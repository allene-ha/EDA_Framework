import json

from typing import Dict, Any, Union
#import mysql.connector

from driver.collector.collector_factory import get_collector
from driver.database import (
    collect_db_level_data_from_database,
    collect_table_level_data_from_database,
)
#from tests.useful_literals import TABLE_LEVEL_MYSQL_COLUMNS

# pylint: disable=ungrouped-imports
from driver.collector.mysql_collector import MysqlCollector

# pylint: disable=missing-function-docstring


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
        driver_config = json.load(json_file)

    return config

def run() -> None:
    """
    The main entrypoint for the driver
    """

    with open('connect_config.json') as json_file:
        driver_config = json.load(json_file)

    end_time = str(0) # initialize
    with open('end_time', 'w') as outfile:
        outfile.write(end_time)
    schedule_db_level_monitor_job(driver_config)
    #if not config.disable_table_level_stats or not config.disable_index_stats:
    #    schedule_table_level_monitor_job(config)
    scheduler.start()


if __name__ == "__main__":
    run()