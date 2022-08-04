import pprint

"""Tests for interacting with MySQL database"""
import json
import time

from typing import Dict, Any, Union
import mysql.connector

from driver.collector.collector_factory import get_mysql_version, connect_mysql
from driver.database import (
    collect_db_level_data_from_database,
    collect_table_level_data_from_database,
)
from tests.useful_literals import TABLE_LEVEL_MYSQL_COLUMNS

# pylint: disable=ungrouped-imports
from driver.collector.mysql_collector import MysqlCollector

# pylint: disable=missing-function-docstring
def _db_query(conn: mysql.connector.MySQLConnection, sql: str) -> None:
    conn.cursor().execute(sql)


def _create_user(
    conn: mysql.connector.MySQLConnection, user: str, password: str
) -> None:
    sql = f"CREATE USER IF NOT EXISTS '{user}' IDENTIFIED BY '{password}';"
    _db_query(conn, sql)


def _drop_user(conn: mysql.connector.MySQLConnection, user: str) -> None:
    sql = f" DROP USER IF EXISTS '{user}';"
    _db_query(conn, sql)


def _get_conf(
    mysql_user: str,
    mysql_password: str,
    mysql_host: str,
    mysql_port: str,
    mysql_database: str,
) -> Dict[str, str]:
    conf = {
        "user": mysql_user,
        "password": mysql_password,
        "host": mysql_host,
        "port": mysql_port,
        "database": mysql_database,
    }
    return conf


def _get_driver_conf(
    db_type: str,
    mysql_user: str,
    mysql_password: str,
    mysql_host: str,
    mysql_port: str,
    mysql_database: str,
    num_table_to_collect_stats: int,
    num_index_to_collect_stats: int,
) -> Dict[str, Union[int, str]]:
    # pylint: disable=too-many-arguments
    conf = {
        "db_user": mysql_user,
        "db_password": mysql_password,
        "db_host": mysql_host,
        "db_port": mysql_port,
        "db_name": mysql_database,
        "db_type": db_type,
        "db_provider": "on_premise",
        "db_key": "test_key",
        "organization_id": "test_organization",
        "num_table_to_collect_stats": num_table_to_collect_stats,
        "num_index_to_collect_stats": num_index_to_collect_stats,
    }
    return conf

db_type='mysql'
mysql_host='127.0.0.1'
mysql_port='3306'
mysql_user='root'
mysql_password='1234'
mysql_database=''

driver_conf = _get_driver_conf(
        db_type, mysql_user, mysql_password, mysql_host, mysql_port, mysql_database, 10, 100
    )
observation = collect_db_level_data_from_database(driver_conf)
knobs = observation["knobs_data"]
metrics = observation["metrics_data"]
summary = observation["summary"]
row_num_stats = observation["row_num_stats"]
version_str = summary["version"]

#pprint.pprint(observation)

conf = _get_conf(mysql_user, mysql_password, mysql_host, mysql_port, mysql_database)
conn = connect_mysql(conf)
version = get_mysql_version(conn)
collector = MysqlCollector(conn, version)
collector.collect_test()