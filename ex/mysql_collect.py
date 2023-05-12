import json

from typing import Dict, Any, Union
import mysql.connector

from driver.collector.collector_factory import get_mysql_version, connect_mysql
from driver.database import (
    collect_db_level_data_from_database,
    collect_table_level_data_from_database,
)
#from tests.useful_literals import TABLE_LEVEL_MYSQL_COLUMNS

# pylint: disable=ungrouped-imports
from driver.collector.mysql_collector import MysqlCollector

# pylint: disable=missing-function-docstring

def _get_driver_conf(
    db_type: str,
    mysql_user: str,
    mysql_password: str,
    mysql_host: str,
    mysql_port: str,
    mysql_database: str,
    num_table_to_collect_stats: int,
    num_index_to_collect_stats: int,
    monitor_interval: int,
    table_level_monitor_interval: int
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
        "monitor_interval": monitor_interval,
        "table_level_monitor_interval": table_level_monitor_interval,
    }
    return conf

"""
The main entrypoint for the driver. The driver will poll for new configurations and schedule
executions of monitoring and tuning pipeline.
"""
import logging

from apscheduler.schedulers.background import BlockingScheduler

from driver.driver_config_builder import DriverConfigBuilder, Overrides
from driver.pipeline import (
    schedule_or_update_job,
    DB_LEVEL_MONITOR_JOB_ID,
    TABLE_LEVEL_MONITOR_JOB_ID,
)

# Setup the scheduler that will poll for new configs and run the core pipeline
scheduler = BlockingScheduler()



def schedule_db_level_monitor_job(config) -> None:
    """
    The outer polling loop for the driver
    """
    schedule_or_update_job(scheduler, config, DB_LEVEL_MONITOR_JOB_ID)


def schedule_table_level_monitor_job(config) -> None:
    """
    The polling loop for table level statistics
    """
    schedule_or_update_job(scheduler, config, TABLE_LEVEL_MONITOR_JOB_ID)


def get_config(args):
    """
    Build configuration from file, command line overrides, rds info,
    """
    config_builder = DriverConfigBuilder()
    overrides = Overrides(
        monitor_interval=args.override_monitor_interval,
        server_url=args.override_server_url,
        num_table_to_collect_stats=args.override_num_table_to_collect_stats,
        table_level_monitor_interval=args.override_table_level_monitor_interval,
        num_index_to_collect_stats=args.override_num_index_to_collect_stats,
    )
    config = config_builder.get_config()

    return config

def connect_config():
    with open('connect_config.json') as json_file:
        data = json.load(json_file)

    db_type=data["db_type"]
    host=data["host"]
    port=data["port"]
    user=data["user"]
    password=data["password"]
    if db_type =='mysql':
        mysql_database=data["mysql_database"]   
    monitor_interval=10
    table_level_monitor_interval=5000


    config = _get_driver_conf(
            db_type, 
            user, 
            password, 
            host, 
            port, 
            mysql_database, 
            10, 
            100, 
            monitor_interval,
            table_level_monitor_interval,
        )
    loglevel = 'INFO'
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {loglevel}")
    logging.basicConfig(level=numeric_level)
    return config

def run() -> None:
    """
    The main entrypoint for the driver
    """

    with open('connect_config.json') as json_file:
        config = json.load(json_file)

    end_time = str(0) # initialize
    with open('end_time', 'w') as outfile:
        outfile.write(end_time)
    schedule_db_level_monitor_job(config)
    #if not config.disable_table_level_stats or not config.disable_index_stats:
    #    schedule_table_level_monitor_job(config)
    scheduler.start()


if __name__ == "__main__":
    run()

