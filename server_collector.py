import os
import psycopg2
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
import uuid

import json

from typing import Dict, Any, Union

from driver.collector.collector_factory import get_collector
from driver.database import (
    collect_db_level_data_from_database,
    collect_table_level_data_from_database,
)



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



def schedule_db_level_monitor_job(config, db_id) -> None:
    """
    The outer polling loop for the driver
    """
    schedule_or_update_job(scheduler, config, DB_LEVEL_MONITOR_JOB_ID, db_id)


def schedule_table_level_monitor_job(config) -> None:
    """
    The polling loop for table level statistics
    """
    schedule_or_update_job(scheduler, config, TABLE_LEVEL_MONITOR_JOB_ID)




app = Flask(__name__)
scheduler = BackgroundScheduler()

@app.route('/config', methods=['POST'])
def get_config():
    # Get database configuration data from the client request
    data = request.get_json()
    db_type = data['db_type']
    db_host = data['db_host']
    db_port = data['db_port']
    db_name = data['db_name']
    db_user = data['db_user']
    db_password = data['db_password']
    
    server_conn = psycopg2.connect(
        host='localhost',
        database='eda',
        user='postgres',
        password='postgres'
    )
    
    # Add collect_metrics function to the scheduler
    # Check if the input DB configuration already exists in the database
    cur = server_conn.cursor()
    cur.execute("""
        SELECT id
        FROM db_config
        WHERE db_type = %s AND db_host = %s AND db_port = %s AND db_name = %s AND db_user = %s;
    """, (db_type, db_host, db_port, db_name, db_user))
    result = cur.fetchone()

    if result:
        # If the input DB configuration already exists in the database, use the existing ID
        db_id = result[0]
    else:
        # If the input DB configuration does not exist in the database, generate a new ID
        db_id = str(uuid.uuid4())
        print(db_id, db_type, db_host, db_port, db_name, db_user, db_password)
        # Store the new DB ID and configuration in the database
        cur.execute("""
            INSERT INTO db_config (id, db_type, db_host, db_port, db_name, db_user, db_password)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (db_id, db_type, db_host, db_port, db_name, db_user, db_password))
        server_conn.commit()

    # Return the DB ID to the client
    collect_metrics(db_id, db_type, db_host, db_port, db_name, db_user, db_password)

    # Return a success response
    return f"{db_id}Database configuration data received successfully!"

def collect_metrics(db_id, db_type, db_host, db_port, db_name, db_user, db_password):

    

    driver_config = {
        "db_host":db_host,
        "db_port":db_port,
        "db_name":db_name,
        "db_user":db_user,
        "db_password":db_password,
        "db_type":"postgres",
        "monitor_interval":"10",
        "table_level_monitor_interval":"5000",
        "db_provider": "on_premise",
        "db_key": "test_key",
        "organization_id": "test_organization"
    }

    print(driver_config)
    schedule_db_level_monitor_job(driver_config, db_id)
    #if not config.disable_table_level_stats or not config.disable_index_stats:
    #    schedule_table_level_monitor_job(config)
    scheduler.start()
    # Run queries to collect metrics and store them in a file or database

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)