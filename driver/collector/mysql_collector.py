"""MySQL database collector to get knob and metric data from the target database"""
import json
from decimal import Decimal
from token import TILDE
from typing import Dict, List, Any, Tuple
import logging
import mysql.connector
import mysql.connector.connection as mysql_conn
from mysql.connector import errorcode
import pandas as pd
from IPython.display import display, clear_output

import subprocess
from driver.exceptions import MysqlCollectorException
from driver.collector.base_collector import BaseDbCollector, PermissionInfo

TABLE_LEVEL_STATS_SQL_TEMPLATE = """
SELECT
  TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE,
  ENGINE, ROW_FORMAT, TABLE_ROWS,
  AVG_ROW_LENGTH, DATA_LENGTH, INDEX_LENGTH,
  DATA_FREE
FROM
  information_schema.TABLES
WHERE 
  TABLE_SCHEMA
NOT IN
  ('information_schema', 'performance_schema', 'mysql', 'sys')
AND
  TABLE_ROWS > 0
ORDER BY 
  TABLE_ROWS DESC
LIMIT
  {n};
"""

INDEX_SIZE_SQL_TEMPLATE = """
SELECT
    DATABASE_NAME, TABLE_NAME, INDEX_NAME, STAT_VALUE,
    STAT_VALUE * @@innodb_page_size AS SIZE_IN_BYTE
FROM
    mysql.innodb_index_stats
WHERE
    stat_name='size'
AND
    (DATABASE_NAME,TABLE_NAME) IN {schema_table_list}
ORDER BY
    SIZE_IN_BYTE DESC
LIMIT
    {n};
"""

INDEX_STATS_SQL_TEMPLATE = """
SELECT 
    TABLE_SCHEMA,TABLE_NAME,NON_UNIQUE,
    INDEX_SCHEMA,INDEX_NAME,SEQ_IN_INDEX,COLUMN_NAME,
    COLLATION,CARDINALITY,SUB_PART,NULLABLE,INDEX_TYPE 
FROM
    information_schema.STATISTICS
WHERE
    (TABLE_SCHEMA,TABLE_NAME,INDEX_NAME) IN {schema_table_index_list};
"""

INDEX_USAGE_SQL_TEMPLATE = """
SELECT
    OBJECT_TYPE,OBJECT_SCHEMA,OBJECT_NAME,INDEX_NAME,COUNT_STAR,
    SUM_TIMER_WAIT,COUNT_READ,SUM_TIMER_READ,COUNT_WRITE,SUM_TIMER_WRITE,
    COUNT_FETCH,SUM_TIMER_FETCH,COUNT_INSERT,SUM_TIMER_INSERT,
    COUNT_UPDATE,SUM_TIMER_UPDATE,COUNT_DELETE,SUM_TIMER_DELETE 
FROM
    performance_schema.table_io_waits_summary_by_index_usage 
WHERE
    OBJECT_TYPE='TABLE'
AND
    (OBJECT_SCHEMA,OBJECT_NAME,INDEX_NAME) IN {schema_table_index_list};
"""


class MysqlCollector(BaseDbCollector):  # pylint: disable=too-many-instance-attributes
    """Mysql connector to collect knobs/metrics from the MySQL database"""
    VERSION_SQL = "SELECT VERSION();"
    KNOBS_SQL = "SHOW GLOBAL VARIABLES;"
    METRICS_SQL = "SHOW GLOBAL STATUS;"
    METRICS_INNODB_SQL = (
        "SELECT name, count FROM information_schema.innodb_metrics "
        "WHERE subsystem = 'transaction';"
    )

    # convert the time unit from ps to ms by dividing 1,000,000,000
    METRICS_LATENCY_HIST_SQL = (
        "SELECT bucket_number, bucket_timer_low / 1000000000 as bucket_timer_low, "
        "bucket_timer_high / 1000000000 as bucket_timer_high, count_bucket, "
        "count_bucket_and_lower, bucket_quantile FROM "
        "performance_schema.events_statements_histogram_global;"
    )
    QUERY_DIGEST_TIME = (
        "SELECT CONCAT(IFNULL(schema_name, 'NULL'), '_', digest) as queryid, "
        "count_star as calls, "
        "round(avg_timer_wait/1000000000, 6) as avg_time_ms "
        "FROM performance_schema.events_statements_summary_by_digest;"
    )
    WAIT_SUMMARY_SQL = "select event_name, sum_timer_wait from performance_schema.events_waits_summary_global_by_event_name;"

    ENGINE_INNODB_SQL = "SHOW ENGINE INNODB STATUS;"
    ENGINE_MASTER_SQL = "SHOW MASTER STATUS;"

    def __init__(self, conn: mysql_conn.MySQLConnection, version: str) -> None:
        """
        Callers should make sure that the connection object is closed after using
        the collector. This likely means that callers should not insantiate this class
        directly and instead use the collector_factory.get_collector method instead.
        Args:
            conn: The connection to the database
            version: DB version (e.g. 5.7.3)
        """
        self._conn = conn
        self._version_str = version
        self._version = float(".".join(version.split(".")[:2]))
        self._innodb_status: str = ""
        self._global_status: Dict[str, Any] = {}
        # From MySQL 8.0.22, SHOW REPLICA STATUS is available to use.
        if self._version > 8.0:
            # pylint: disable=invalid-name
            self.ENGINE_REPLICA_SQL: str = "SHOW REPLICA STATUS;"
        else:
            self.ENGINE_REPLICA_SQL: str = "SHOW SLAVE STATUS;"
        #self.end_time
    
    def get_conn(self):
        return self._conn

    def _cmd(self, sql: str):  # type: ignore
        """Run the command line (sql query), and fetch the returned results.
        Args:
            sql: Sql query which is executed
        Returns:
            Fetched results of the query, as well as table meta data
        Raises:
            MysqlCollectorException: Failed to execute the sql query
        """
        try:
            cursor = self._conn.cursor(dictionary=False)
            cursor.execute(sql)
            res = cursor.fetchall()
            columns = cursor.description
            meta = [col[0] for col in columns]
            return res, meta
        except Exception as ex:  # pylint: disable=broad-except
            msg = f"Failed to execute sql {sql}"
            raise MysqlCollectorException(msg, ex) from ex

    def _cmd_wo_fetch(self, sql: str):  # type: ignore
        try:
            cursor = self._conn.cursor(dictionary=False)
            cursor.execute(sql)
        except Exception as ex:  # pylint: disable=broad-except
            msg = f"Failed to execute sql {sql}"
            raise MysqlCollectorException(msg, ex) from ex

    def get_version(self) -> str:
        """Get database version"""

        return self._version_str

    def check_permission(self) -> Tuple[bool, List[PermissionInfo], str]:
        """Check the permissions of running all collector queries.
        Returns:
            True if the user has all expected permissions. If errors appear, return False,
            as well as the information about how to grant corresponding permissions.
        Raises:
            MysqlCollectorException: Failed to connect to the database
        """
        success = True
        # The SHOW STATUS and SHOW VARIABLES statements do not need any privileges
        sql_priv_map = {
            self.ENGINE_INNODB_SQL: "PROCESS",
            self.KNOBS_SQL: "",
            self.ENGINE_MASTER_SQL: "REPLICATION CLIENT",
            self.ENGINE_REPLICA_SQL: "REPLICATION CLIENT",
            self.METRICS_INNODB_SQL: "PROCESS",
            self.METRICS_SQL: "",
            self.VERSION_SQL: "",
        }
        if self._version >= 8.0:
            sql_priv_map[
                self.METRICS_LATENCY_HIST_SQL
            ] = "performance_schema.events_statements_histogram_global"

        results = []
        for sql, priv in sql_priv_map.items():
            try:
                cursor = self._conn.cursor(dictionary=False)
                cursor.execute(sql)
                cursor.fetchall()
            except mysql.connector.Error as err:
                example = "unknown"
                if err.errno in (
                    errorcode.ER_SPECIFIC_ACCESS_DENIED_ERROR,
                    errorcode.ER_ACCESS_DENIED_ERROR,
                ):
                    example = f"GRANT {priv} ON *.* TO <user>@<host>;"
                elif err.errno == errorcode.ER_TABLEACCESS_DENIED_ERROR:
                    example = f"GRANT SELECT ON {priv} TO <user>@<'host'>;"
                info = {}
                info["query"] = sql
                info["success"] = False
                # example of how to grant the privilege
                info["example"] = example
                results.append(info)
                success = False
        # debug info
        # TODO(bohan) (from nappelson) I think debug information like this should be
        # propgated in a different way For instance, this kind of information
        # should be pushed somewhere. For now, we can leave as is.
        text_lines = []
        for res in results:
            text_lines.append("-----------------------------------------------\n")
            text_lines.append(f"Permissions check failed for SQL: {res['query']}\n")
            text_lines.append(
                f"Please grant the privilege. For example: {res['example']}\n"
            )
        text = "".join(text_lines)
        return success, results, text

    def collect_knobs(self) -> Dict[str, Any]:
        """Collect database knobs informationß
        Returns:
            Database knob data
        Raises:
            MysqlCollectorException: Failed to execute the sql query to get knob data
        """

        knobs: Dict[str, Any] = {"global": {"global": {}}, "local": None}

        #knobs["global"]["global"] = dict(self._cmd(self.KNOBS_SQL)[0])
        return knobs

    def collect_thread(self): 
        
        with open('end_time', 'r') as infile:
            end_time = infile.read()
        #print("before",end_time)
        QUERY_DIGEST_SQL = f"select round(history.timer_wait/1000000000,6) as time_ms, history.digest, history.digest_text, history.thread_id, summary.count_star as count, history.timer_end from performance_schema.events_statements_history history inner join performance_schema.events_statements_summary_by_digest summary on history.digest=summary.digest where history.timer_end>{end_time};"
        #events_statements_history 에서 count 관련 정보는 없지만 digest를 얻을 수 있음
        #이 digest를 기준으로 이 테이블과 events_statements_summary_by_digest를 digest로 inner join해서
        #events_statements_summary_by_digest 테이블에 count_star
        # select round(history.timer_wait/1000000000,6) as time_ms, history.digest, history.digest_text, history.thread_id, summary.count_star as count, history.timer_end from performance_schema.events_statements_history history inner join performance_schema.events_statements_summary_by_digest summary on history.digest=summary.digest where history.timer_end>0;
        # digest랑 Count_star는 중복제거 해야함
        try:
            query_digest_data, query_digest_meta = self._cmd(QUERY_DIGEST_SQL)
            self._cmd_wo_fetch("truncate table performance_schema.events_statements_summary_by_digest;")
            end_time = str(query_digest_data[-1][-1])
            #print("after",end_time)
            with open('end_time', 'w') as outfile:
                outfile.write(end_time)
            query_digest = self._make_list(query_digest_data, query_digest_meta)
            #print(query_digest[0])
        except Exception as ex:
            logging.error("Failed to collect query digest: %s", ex)
            query_digest = []

        TID = []
        for i in query_digest_data:
            #print(i)
            TID.append(i[3])
        TID = set(TID)
        thread_data = []
        thread_meta = []
        thread_result = []
        #print(TID)
        for i in TID:
            THREAD_SQL = f"select thread_id, thread_os_id from performance_schema.threads  where thread_id={i};"
            thread_data = self._cmd(THREAD_SQL)[0]
            thread_meta = self._cmd(THREAD_SQL)[1]
            thread_result.append(self._make_list(thread_data, thread_meta))
            
        result = {}

        result['threads'] = thread_result # json.dumps 해제
        result['events_statements_history'] = query_digest # json.dumps(query_digest)

        ps_result = subprocess.check_output(['ps -ef | grep mysql'], shell=True).decode()
        ps_lines = ps_result.splitlines()
        TID = []
        for ps_line in ps_lines:
            ps_line=ps_line.replace("  ",' ').replace("  ",' ').replace("  ",' ').replace("  ",' ').replace("  ",' ')
            ps = ps_line.split(' ')
            if 'mysql' in ps[0]:
                TID.append(ps[1])
        #print(TID)
        pidstat_cpu_result = subprocess.check_output(['pidstat -t'], shell=True).decode()
        lines = pidstat_cpu_result.splitlines()[3:]
        dict={}
        collect = False
        for line in lines:
            line=line.replace("     ",' ').replace("    ",' ').replace("   ",' ').replace("  ",' ').replace("  ",' ')
            words = line.split(' ')
            if words[2] in TID:
                collect = True
                continue
            elif collect == True and words[2] !='-':
                collect = False
                continue
            elif collect == False:
                continue
            dict[words[3]] = words[8]
        sorted(dict.items(),key=lambda x:x[1],reverse=True)
        result['cpu_usage'] = dict

        pidstat_io_result = subprocess.check_output(['pidstat -d -t'], shell=True).decode()
        lines = pidstat_io_result.splitlines()[3:]
        dict={}
        collect = False
        for line in lines:
            line=line.replace("     ",' ').replace("    ",' ').replace("   ",' ').replace("  ",' ').replace("  ",' ')
            words = line.split(' ')
            if words[2] in TID:
                collect = True
                continue
            elif collect == True and words[2] !='-':
                collect = False
                continue
            elif collect == False:
                continue
            dict[words[3]] = words[7]# float(words[4])+float(words[5]) # clock ticks
        sorted(dict.items(),key=lambda x:x[1],reverse=True)
        result['io'] = dict
        #print(dict)

        return result

    def collect_waits(self):
        self._cmd_wo_fetch("truncate table performance_schema.events_waits_summary_global_by_event_name;")
        temp = dict(self._cmd(self.WAIT_SUMMARY_SQL)[0])
        print(temp)
        #temp= list(map(list, zip(*temp)))     
        return temp
       
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect database metrics information
        Returns:
            Database metric data
        Raises:
            MysqlCollectorException: Failed to execute the sql query to get metric data
        """

        metrics: Dict[str, Any] = {
            "global": {
                "global": {},
                "innodb_metrics": {},
                "performance_schema": {},
                "engine": {},
                "derived": {},
            },
            "local": None,
        }
        self._global_status = {
            x[0].lower(): x[1] for x in self._cmd(self.METRICS_SQL)[0]
        }
        metrics["global"]["global"] = self._global_status
        metrics["global"]["innodb_metrics"] = dict(
            self._cmd(self.METRICS_INNODB_SQL)[0]
        )
        status_raw = self._cmd(self.ENGINE_INNODB_SQL)[0]
        if len(status_raw) > 0:
            self._innodb_status = self._truncate_innodb_status(status_raw[0][-1])
        metrics["global"]["engine"]["innodb_status"] = self._innodb_status
        metrics["global"]["engine"]["innodb_status_io"] = self._extract_from_innodb_status(self._innodb_status)
        metrics["global"]["derived"] = self._collect_derived_metrics()
        metrics["global"]["wait"] = self.collect_waits() # dict
        
        # CPU
        pidstat_cpu_usage = subprocess.check_output(['pidstat -C mysql'], shell=True).decode()
        lines = pidstat_cpu_usage.splitlines()[3:]
        temp = 0

        for line in lines:
            line=line.replace("     ",' ').replace("    ",' ').replace("   ",' ').replace("  ",' ').replace("  ",' ')
            words = line.split(' ')
            
            temp += float(words[7])# float(words[4])+float(words[5]) # clock ticks
        metrics["global"]["cpu"] = temp
        
        # # replica status and master status
        # replica_metrics, replica_meta = self._cmd(self.ENGINE_REPLICA_SQL)
        # if len(replica_metrics) > 0:
        #     replica_metrics = replica_metrics[0]
        #     replica_json = dict(zip(replica_meta, replica_metrics))
        #     metrics["global"]["engine"]["replica_status"] = json.dumps(replica_json)
        # else:
        #     metrics["global"]["engine"]["replica_status"] = ""

        # master_metrics, master_meta = self._cmd(self.ENGINE_MASTER_SQL)
        # if len(master_metrics) > 0:
        #     master_metrics = master_metrics[0]
        #     master_json = dict(zip(master_meta, master_metrics))
        #     metrics["global"]["engine"]["master_status"] = json.dumps(master_json)
        # else:
        #     metrics["global"]["engine"]["master_status"] = ""

        # try:
        #     digest_data, digest_meta = self._cmd(self.QUERY_DIGEST_TIME)
        #     summary_by_digest = self._make_list(digest_data, digest_meta)
        # except Exception as ex:  # pylint: disable=broad-except
        #     logging.error("Failed to collect query latency metrics: %s", ex)
        #     summary_by_digest = []

        # metrics["global"]["performance_schema"][
        #     "events_statements_summary_by_digest"
        # ] = json.dumps(summary_by_digest)

        # if self._version >= 8.0:
        #     # latency histogram
        #     histogram_data, histogram_meta = self._cmd(self.METRICS_LATENCY_HIST_SQL)
        #     metrics["global"]["performance_schema"][
        #         "events_statements_histogram_global"
        #     ] = json.dumps(self._make_list(histogram_data, histogram_meta))

        thread_metrics = self.collect_thread()
        metrics['global']["performance_schema"].update(thread_metrics)
        return metrics

    def collect_table_row_number_stats(self) -> Dict[str, Any]:
        """Collect statistics about the number of rows of different tables"""
        return {}

    def get_target_table_info(self,
                          num_table_to_collect_stats: int) -> Dict[str, Any]:
        """Get the information of tables to collect table and index stats"""
        table_values, table_columns = self._cmd(
            TABLE_LEVEL_STATS_SQL_TEMPLATE.format(n=num_table_to_collect_stats))
        table_rows = [list(row) for row in table_values]
        schema_table_string_list = [
            "(\"{schema}\", \"{table}\")".format(schema=item[0], table=item[1])
            for item in self._find_columns(
                table_columns, table_rows, ["TABLE_SCHEMA", "TABLE_NAME"])
        ]
        return {
            "table_columns": table_columns,
            "table_rows": table_rows,
            "schema_table_string_list": schema_table_string_list
        }

    def collect_table_level_metrics(self,
                                    target_table_info: Dict[str, Any]) -> Dict[str, Any]:
        """Collect table level statistics

        Returns:
        {
            "information_schema_TABLES": {
                "columns": [
                    "TABLE_SCHEMA",
                    "TABLE_NAME",
                    "TABLE_TYPE",
                    "ENGINE",
                    "ROW_FORMAT",
                    "TABLE_ROWS",
                    "AVG_ROW_LENGTH",
                    "DATA_LENGTH",
                    "INDEX_LENGTH",
                    "DATA_FREE",
                ],
                "rows": List[List[Any]],
            },
            "information_schema_STATISTICS": {
                "columns": [...],
                "rows": [[...], [...]]
            },
        }
        """

        return {
            "information_schema_TABLES": {
                "columns": target_table_info.get("table_columns"),
                "rows": target_table_info.get("table_rows"),
            },
        }

    def collect_index_metrics(self,
                              target_table_info: Dict[str, Any],
                              num_index_to_collect_stats: int) -> Dict[str, Any]:
        """Collect index statistics

        Returns:
        {
            "information_schema_STATISTICS": {
                "columns": [...],
                "rows": [[...], [...]]
            },
            "performance_schema_table_io_waits_summary_by_index_usage": {
                "columns": [...],
                "rows": [[...], [...]]
            },
            "indexes_size": {
                "columns": [...],
                "rows": [[...], [...]]
            }
        }
        """
        # pylint: disable=too-many-locals
        schema_table_string_list = target_table_info.get("schema_table_string_list")

        if not schema_table_string_list:
            schema_table_string = "((NULL,NULL))"
        else:
            schema_table_string = "(" + ",".join(schema_table_string_list) + ")"

        index_size_values, index_size_columns = self._cmd(
            INDEX_SIZE_SQL_TEMPLATE.format(schema_table_list=schema_table_string,
                                           n=num_index_to_collect_stats))

        index_size_rows = [list(row) for row in index_size_values]

        schema_table_index_string_list = [
            "(\"{schema}\", \"{table}\", \"{index}\")".format(
                schema=item[0], table=item[1], index=item[2])
            for item in self._find_columns(
                index_size_columns, index_size_values,
                ["DATABASE_NAME", "TABLE_NAME", "INDEX_NAME"])
        ]

        if not schema_table_index_string_list:
            schema_table_index_string = "((NULL,NULL,NULL))"
        else:
            schema_table_index_string = "(" + ",".join(schema_table_index_string_list) + ")"

        index_stats_values, index_stats_columns = self._cmd(
            INDEX_STATS_SQL_TEMPLATE.format(
                schema_table_index_list=schema_table_index_string))
        index_stats_rows = [list(row) for row in index_stats_values]

        index_usage_values, index_usage_columns = self._cmd(
            INDEX_USAGE_SQL_TEMPLATE.format(
                schema_table_index_list=schema_table_index_string))
        index_usage_rows = [list(row) for row in index_usage_values]

        return {
            "information_schema_STATISTICS": {
                "columns": index_stats_columns,
                "rows": index_stats_rows,
            },
            "performance_schema_table_io_waits_summary_by_index_usage": {
                "columns": index_usage_columns,
                "rows": index_usage_rows,
            },
            "indexes_size": {
                "columns": index_size_columns,
                "rows": index_size_rows,
            }
        }

    def _find_columns(self,
                      columns: List[str],
                      rows: List[List[Any]],
                      target_columns: List[str]) -> List[List[Any]]:
        indices = [columns.index(target_col) for target_col in target_columns]
        result = []

        for row in rows:
            result.append([row[idx] for idx in indices])

        return result

    def _collect_derived_metrics(self) -> Dict[str, Any]:
        """Collect metrics derived from base metrics
        Calculate derived metrics from collected base metrics. We may want to move it to the server
        side to calculate derived metrics. We can revisit this when saas server is implemented
        Returns:
            Database calculated derived metrics
        """

        # buffer pool miss ratio
        innodb_buffer_pool_reads = int(
            self._global_status.get("innodb_buffer_pool_reads", 0)
        )
        innodb_buffer_pool_read_requests = int(
            self._global_status.get("innodb_buffer_pool_read_requests", 0)
        )
        if innodb_buffer_pool_read_requests == 0:
            buffer_miss_ratio = 0.0
        else:
            buffer_miss_ratio = (
                round(innodb_buffer_pool_reads / innodb_buffer_pool_read_requests, 4)
                * 100
            )

        # read write query ratio
        read_counts = int(self._global_status.get("com_select", 0))
        write_counts = (
            int(self._global_status.get("com_insert", 0))
            + int(self._global_status.get("com_update", 0))
            + int(self._global_status.get("com_delete", 0))
            + int(self._global_status.get("com_replace", 0))
        )
        read_counts = 1 if read_counts == 0 else read_counts
        write_counts = 1 if write_counts == 0 else write_counts
        read_write_ratio = round(read_counts / write_counts, 4)  # keep 4 decimals here

        # merge metrics
        derived_metrics = dict(
            buffer_miss_ratio=buffer_miss_ratio, read_write_ratio=read_write_ratio
        )
        return derived_metrics

    @staticmethod
    def _truncate_innodb_status(status: str) -> str:
        """
        If the innodb status has too many lines, we truncate it and keep a limited number of lines.
        Currently, we keep the first 50 lines and the last 100 lines.
        """

        lines = status.splitlines()
        size = len(lines)
        if size <= 150:
            return status
        new_lines = lines[:50]
        new_lines.append(f"...ignore {size-150} lines here...")
        new_lines.extend(lines[-100:])
        truncated_status = "\n".join(new_lines)
        return truncated_status

    @staticmethod
    def _extract_from_innodb_status(status: str) -> dict:
        """
        extract data i/o and log i/o from innodb status
        """
        file_io = ''
        log_io = ''
        lines = status.splitlines()
        for line in lines:
            if 'OS file reads,' in line:
                file_io = line
            elif 'log i/o' in line:
                log_io = line
        
        import re
        file_io_number = re.findall(r'\d+', file_io)
        log_io_number = re.findall(r'\d+', log_io)
        #print(file_io_number)        
        #print(log_io_number)
        dict = {}
        dict['data_io'] = int(file_io_number[0]) + int(file_io_number[1])
        dict['log_io'] = int(log_io_number[0])
        #print(dict)
        return dict 

    @staticmethod
    def _make_list(data, meta: List[str]) -> List[Dict[str, Any]]:  # type: ignore
        """
        Convert fetched data to a list.
        Args:
            data: row values, e.g., [(val1_1, val1_2), (val2_1, val2_2)]
            meta: column names, e.g., [col1, col2]
        Returns:
            converted data, e.g., [{"col1": val1_1, "col2": val1_2},
                                   {"col1": val2_1, "col2": val2_2}]
        """

        res = []
        for row in data:
            row_new = [
                float(elem) if isinstance(elem, Decimal) else elem for elem in row
            ]
            res.append(dict(zip(meta, row_new)))
        return res
