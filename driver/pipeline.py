""" Module containing pipelines (reoccuring function calls) for use with apscheduler. """

from datetime import datetime
import logging
from requests import Session
import json
from apscheduler.schedulers.background import BlockingScheduler
import psycopg2
from driver.driver_config_builder import DriverConfig
from driver.compute_server_client import ComputeServerClient
from driver.database import (
    collect_db_level_observation_for_on_prem,
    collect_table_level_observation_for_on_prem,
)
from datetime import datetime
#from influxdb import InfluxDBClient

TUNE_JOB_ID = "tune_job"
DB_LEVEL_MONITOR_JOB_ID = "db_level_monitor_job"
APPLY_EVENT_JOB_ID = "apply_event_job"
TABLE_LEVEL_MONITOR_JOB_ID = "table_level_monitor_job"


def driver_pipeline(
    config: DriverConfig,
    job_id: str, db_id # pylint: disable=unused-argument
) -> None:
    """
    Run the core pipeline for the driver deployment
    """
    logging.info("Running driver pipeline deployment!")


    #compute_server_client = ComputeServerClient(
    #    config.server_url, Session(), config.api_key
    #)

    if job_id == DB_LEVEL_MONITOR_JOB_ID:
        _db_level_monitor_driver_pipeline_for_on_prem(config, db_id)
    elif job_id == TABLE_LEVEL_MONITOR_JOB_ID:
        _table_level_monitor_driver_pipeline_for_on_prem(config)
    # elif job_id == LINUX


def _db_level_monitor_driver_pipeline_for_on_prem(
    config: DriverConfig, db_id
    #compute_server_client: ComputeServerClient,
) -> None:
    """
    Regular monitoring pipeline that collects database level metrics and configs every minute

    Args:
        config: Driver configuration.
        compute_server_client: Client interacting with server in Ottertune.
    Raises:
        DriverException: Driver error.
        Exception: Other unknown exceptions that are not caught as DriverException.
    """
    logging.debug("Collecting db level observation data.")
    # get metrics from on-premise database
    db_level_observation = collect_db_level_observation_for_on_prem(config) # list
    
    
    # # Connect to the InfluxDB instance
    # client = InfluxDBClient(host='localhost', port=8086)

    # # Choose the database you want to write to
    # client.switch_database('eda')

    # # Write the data to InfluxDB
    # client.write_points(db_level_observation)

    # postgresql
    _insert_db_level_observation_to_postgresql(db_level_observation, db_id)

    now = datetime.now()
    file_name = now.strftime('%Y%m%d_%H%M%S')
    f_path = open('path.txt' , 'r' )
    path = f_path.readline()
    path.rstrip('\n')
    import csv
    server_conn = psycopg2.connect(
    host='localhost',
    database='eda',
    user='postgres',
    password='postgres'
    )
    # 커서 생성
    now = datetime.now()
    cur = server_conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
    table_names = cur.fetchall()
    for table_name in table_names:
        cur.execute(f"SELECT * FROM {table_name[0]}")
        rows = cur.fetchall()
        with open(path+"/" + file_name+ f"{table_name[0]}.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(rows)

    # 커넥션 종료
    cur.close()
    server_conn.close()


    logging.debug("Saving db level observation data to the server.")

    #compute_server_client.post_db_level_observation(db_level_observation)
def _insert_db_level_observation_to_postgresql(db_level_observation, db_id):
    server_conn = psycopg2.connect(
        host='localhost',
        database='eda',
        user='postgres',
        password='postgres'
    )
    # 커서 생성
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    cur = server_conn.cursor()
    def insert_data(data_dict, table_name):
        # 딕셔너리에 저장된 키를 컬럼으로 하여 테이블에 컬럼 추가
        cur.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
        existing_columns = [col[0] for col in cur.fetchall()]

        for col in data_dict.keys():
            if col.lower() not in existing_columns:
                col_type = type(data_dict[col]).__name__
                if col_type == 'str':
                    col_type = 'VARCHAR'
                elif col_type == 'int':
                    col_type = 'numeric'
                print(col, col_type)
                cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type};")
                server_conn.commit()

        # 데이터를 삽입
        keys = data_dict.keys()
        values = [data_dict[k] for k in keys]
        #placeholders = ",".join(["%s"]*len(data_dict))
        #print(values)
        #print(f"INSERT INTO {table_name} ({keys}) VALUES ({placeholders})", values)
        
        
        query = "INSERT INTO {}  ({}) VALUES ({});".format(table_name,
            ','.join(keys),
            ','.join(['%s'] * len(values))
        )
        print(table_name, query, values)
        cur.execute(query, values)

    for observation in db_level_observation:
        #print(observation)
        table_name = observation['table']
        data = observation['data']
        print(data)
        # 테이블이 존재하는지 확인하고 없으면 생성
        cur.execute(f"SELECT EXISTS(SELECT relname FROM pg_class WHERE relname='{table_name}')")
        exists = cur.fetchone()[0]
        if not exists:
            # 새로운 테이블 생성
            cur.execute(f"CREATE TABLE {table_name} (timestamp TIMESTAMP);")
            server_conn.commit()

        if type(data) == list:
            for data_dict in data:
                print(data_dict)
                data_dict['timestamp'] = timestamp
                data_dict['dbid'] = db_id
                insert_data(data_dict, table_name)
        else:
            data['timestamp'] = timestamp
            data['dbid'] = db_id
            insert_data(data, table_name)
        
        
    server_conn.commit()

    # 커넥션 닫기
    cur.close()
    server_conn.close()

def _table_level_monitor_driver_pipeline_for_on_prem(
    config: DriverConfig,
    #compute_server_client: ComputeServerClient,
) -> None:
    """
    Regular monitoring pipeline that collects table level metrics every hour

    Args:
        config: Driver configuration.
        comppute_server_client: Client interacting with server in Ottertune.
    Raises:
        DriverException: Driver error.
        Exception: Other unknown exceptions that are not caught as DriverException.
    """
    logging.debug("Collecting table level observation data")
    table_level_observation = collect_table_level_observation_for_on_prem(config)

    logging.debug("Posting table level observation data to the server.")
    #compute_server_client.post_table_level_observation(table_level_observation)

def _get_interval(config: DriverConfig, job_id: str) -> int:
    """Get the scheduled time interval (sec) based on job id."""

    if job_id == DB_LEVEL_MONITOR_JOB_ID:
        interval_s = int(config['monitor_interval'])
    elif job_id == TABLE_LEVEL_MONITOR_JOB_ID:
        interval_s = int(config['table_level_monitor_interval'])
    else:
        raise ValueError(f"Job {job_id} is not supported")
    return interval_s


def _start_job(
    scheduler: BlockingScheduler, config: DriverConfig, job_id: str, interval: int, db_id
) -> None:
    "Helper to start new job"
    logging.info("Initializing driver pipeline (job %s)...", job_id)

    kwargs = {}
    if job_id in (DB_LEVEL_MONITOR_JOB_ID, TABLE_LEVEL_MONITOR_JOB_ID):
        kwargs["next_run_time"] = datetime.now()

    scheduler.add_job(
        driver_pipeline,
        "interval",
        seconds=interval,
        args=[config, job_id, db_id],
        id=job_id,
        **kwargs,
    )
    logging.info("Running driver pipeline every %d seconds (job %s).", interval, job_id)


def _update_job(
    scheduler: BlockingScheduler,
    old_config: DriverConfig,
    new_config: DriverConfig,
    job_id: str,
    interval: int,
) -> None:
    "Helper to update pre-existing job"
    logging.info("Found new config (job %s)...", job_id)
    # grab old interval before modification
    old_interval = _get_interval(old_config, job_id)
    scheduler.modify_job(job_id, args=[new_config, job_id])
    if old_interval != interval:
        scheduler.reschedule_job(job_id, trigger="interval", seconds=interval)
        logging.info(
            "Running driver pipeline every %d seconds (job %s).", interval, job_id
        )


def schedule_or_update_job(
    scheduler: BlockingScheduler, config: DriverConfig, job_id: str, db_id: int
) -> None:
    """
    Apply configuration change to the job. If the configuration does not change, it will do nothing.
    If the job is not scheduled, it will start a job.

    Args:
        config: Driver configuration.
        job_id: Job ID.
    Raises:
        DriverException: Driver error.
        Exception: Other unknown exceptions that are not caught as DriverException.
    """
    interval = _get_interval(config, job_id)
    job = scheduler.get_job(job_id)

    if not job:
        # NB: first invocation is at current_time + interval
        _start_job(scheduler=scheduler, config=config, job_id=job_id, interval=interval, db_id=0)
    else:
        old_config = job.args[0]
        if old_config != config:
            _update_job(
                scheduler=scheduler,
                old_config=old_config,
                new_config=config,
                job_id=job_id,
                interval=interval,
            )
