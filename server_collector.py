import os
import psycopg2
from flask import Flask, request, Response
from apscheduler.schedulers.background import BackgroundScheduler
import uuid

import json
import pandas as pd
from typing import Dict, Any, Union
#import simplejson as json
import pickle

#from driver.collector.collector_factory import get_collector
# from driver.database import (
#     collect_db_level_data_from_database,
#     collect_table_level_data_from_database,
# )

metric_tables = ['bgwriter', 'access', 'io', 'os_metric', 'sessions', 'active_sessions', 'waiting_sessions', 'database_statistics', 'conflicts', 'query_statistics']
non_default_table = ['sessions', 'active_sessions', 'waiting_sessions','query_statistics']
derived_metric_tables = ['load_prediction', 'anomaly_time_interval', 'anomaly_scorer', 'anomaly_detector']
db_statistics_tables = ['database_statistics', 'conflicts']

"""
The main entrypoint for the driver. The driver will poll for new configurations and schedule
executions of monitoring and tuning pipeline.
"""
import logging

from apscheduler.schedulers.background import BlockingScheduler

#from driver.driver_config_builder import DriverConfigBuilder, Overrides
from driver.pipeline import (
    schedule_or_update_job,
    DB_LEVEL_MONITOR_JOB_ID,
    TABLE_LEVEL_MONITOR_JOB_ID,
)

# Setup the scheduler that will poll for new configs and run the core pipeline
scheduler = BlockingScheduler()

server_conn = psycopg2.connect(
        host='localhost',
        database='eda',
        user='postgres',
        password='postgres'
    )

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
        #print(db_id, db_type, db_host, db_port, db_name, db_user, db_password)
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

def get_dbid(config):
    
    cur = server_conn.cursor()
    cur.execute("""
        SELECT id
        FROM db_config
        WHERE db_type = %s AND db_host = %s AND db_port = %s AND db_name = %s AND db_user = %s;
    """, (config['db_type'],config['db_host'], config['db_port'], config['db_name'], config['db_user']))
    result = cur.fetchone()

    if result:
        # If the input DB configuration already exists in the database, use the existing ID
        db_id = result[0]
    else:
        raise KeyError("Cannot find database configuration. Connect is first.")
    
    return db_id
        
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
    schedule_db_level_monitor_job(driver_config, db_id)
    #if not config.disable_table_level_stats or not config.disable_index_stats:
    #    schedule_table_level_monitor_job(config)
    scheduler.start()
    # Run queries to collect metrics and store them in a file or database


@app.route('/data', methods=['GET'])
def perform_data_query():
    
    params_json = request.args.get('params')
    args = json.loads(params_json)

    # print(args)

    table = args['table']
    metrics = args['metric']
    start_time = args['start_time']
    end_time = args['end_time']
    interval = args['interval']
    task = args['task']
    #subtask = args['subtask']
    print("server",args)
    db_id = get_dbid(args['config'])
    

    data = {}
    # SQL 쿼리문 작성
    if interval == '':
        sql_query = f"""SELECT timestamp, {','.join(metrics)} FROM {table} 
                        WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                        AND dbid = '{db_id}'
                        ORDER BY timestamp ASC;"""
    else:
        sql_query = f"""SELECT timestamp, {','.join(metrics)} FROM {table}  
                        WHERE timestamp BETWEEN NOW() - INTERVAL '{interval}' AND NOW()
                        AND dbid = '{db_id}'
                        ORDER BY timestamp ASC;"""

        # Pandas DataFrame으로 변환
    df_metrics = pd.read_sql_query(sql_query, server_conn)
    df_metrics['timestamp'] = df_metrics['timestamp'].astype(str)

    if task == 'metrics':
        data['metrics'] = df_metrics.to_dict()
        return json.dumps(data)
    elif task == 'load prediction':
        
        assert len(metrics) == 1
        data['metrics'] = df_metrics.to_dict()

        metric = metrics[0]
        sql_query = f"""SELECT timestamp, predicted, lower_bound, upper_bound, analysis_time FROM load_prediction """
        
        if interval == '':
            sql_query += f"""WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                            AND dbid = '{db_id}'
                            AND metric = '{metric}'
                            ORDER BY timestamp ASC;"""
        else:
            sql_query += f"""WHERE timestamp BETWEEN NOW() - INTERVAL '{interval}' AND NOW()
                            AND dbid = '{db_id}'
                            AND metric = '{metric}'
                            ORDER BY timestamp ASC;"""

        df_task = pd.read_sql_query(sql_query, server_conn)
        #df = df_metrics[['timestamp', metric]]
        #df_result = pd.merge(df, df_task, on='timestamp', how='outer')
        data['task'] = df_task.to_dict()
    elif task == 'anomaly time interval':
        assert len(metrics) == 1

        data['metrics'] = df_metrics.to_dict()
        metric = metrics[0]
        sql_query = f"""SELECT analysis_time, start, end, severity FROM anomaly_time_interval"""
        
        if interval == '':
            sql_query += f"""WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                            AND dbid = '{db_id}'
                            AND (metric = '{metric}' OR metric IS NULL)
                            ORDER BY timestamp ASC;"""
        else:
            sql_query += f"""WHERE timestamp BETWEEN NOW() - INTERVAL '{interval}' AND NOW()
                            AND dbid = '{db_id}'
                            AND metric = '{metric}'
                            ORDER BY timestamp ASC;"""

        df_task = pd.read_sql_query(sql_query, server_conn)
        data['task'] = df_task.to_dict()
    elif task == 'anomaly scorer':
        assert len(metrics) == 1

        data['metrics'] = df_metrics.to_dict()
        metric = metrics[0]
        sql_query = f"""SELECT timestamp, anomaly_score, analysis_time FROM anomaly_scorer"""
        
        if interval == '':
            sql_query += f"""WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                            AND dbid = '{db_id}'
                            AND (metric = '{metric}' OR metric IS NULL)
                            ORDER BY timestamp ASC;"""
        else:
            sql_query += f"""WHERE timestamp BETWEEN NOW() - INTERVAL '{interval}' AND NOW()
                            AND dbid = '{db_id}'
                            AND metric = '{metric}'
                            ORDER BY timestamp ASC;"""

        df_task = pd.read_sql_query(sql_query, server_conn)
        data['task'] = df_task.to_dict()
    elif task == 'anomaly detector':
        assert len(metrics) == 1

        data['metrics'] = df_metrics.to_dict()
        metric = metrics[0]
        sql_query = f"""SELECT timestamp, anomaly_label, analysis_time FROM anomaly_scorer"""
        
        if interval == '':
            sql_query += f"""WHERE timestamp BETWEEN '{start_time}' AND '{end_time}'
                            AND dbid = '{db_id}'
                            AND (metric = '{metric}' OR metric IS NULL)
                            ORDER BY timestamp ASC;"""
        else:
            sql_query += f"""WHERE timestamp BETWEEN NOW() - INTERVAL '{interval}' AND NOW()
                            AND dbid = '{db_id}'
                            AND metric = '{metric}'
                            ORDER BY timestamp ASC;"""

        df_task = pd.read_sql_query(sql_query, server_conn)
        data['task'] = df_task.to_dict()

    return json.dumps(data)


@app.route('/schema', methods=['GET'])
def get_schema():
    config = request.args.to_dict()
    db_id = get_dbid(config)
    # 커서 생성
    cur = server_conn.cursor()
    schema = {}
    # 모든 테이블 가져오기
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_catalog = 'eda' 
        AND table_schema = 'public' 
        AND table_type = 'BASE TABLE'
    """)

    # 결과 가져오기
    rows = cur.fetchall()

    result = pd.DataFrame(columns=['table','column','type','key'])
    # dbid 열의 값이 db_id인 테이블들 찾기
    for row in rows:
        table_name = row[0]
        if table_name == 'db_config':
            continue
        cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
        table_columns = cur.fetchall()
        #print(table_columns)
        # primary key 확인
        cur.execute(f"""
            SELECT CC.COLUMN_NAME AS COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS       TC
                ,INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE CC
            WHERE TC.TABLE_CATALOG   = 'eda'
            AND TC.TABLE_NAME      = '{table_name}'
            AND TC.CONSTRAINT_TYPE = 'PRIMARY KEY'
            AND TC.TABLE_CATALOG   = CC.TABLE_CATALOG
            AND TC.TABLE_SCHEMA    = CC.TABLE_SCHEMA
            AND TC.TABLE_NAME      = CC.TABLE_NAME
            AND TC.CONSTRAINT_NAME = CC.CONSTRAINT_NAME
            ;
        """)
        primary_key_columns = cur.fetchall()
        #print(primary_key_columns)

        if 'dbid' in [column[0] for column in table_columns]:
            cur.execute(f"SELECT * FROM public.{table_name} WHERE dbid = '{db_id}'")
            
            if cur.fetchone():
                #print(f"Table Name: {table_name}")
                for column in table_columns:
                    #print(f"Column Name: {column[0]}, Data Type: {column[1]}")
                    key = False
                    if column in primary_key_columns:
                        key = True
                    new_df = pd.DataFrame({'table': [table_name], 'column':[column[0]], 'type':[column[1]], 'key':[key]})
                    result = pd.concat([result, new_df],ignore_index=True)
                schema[table_name] = table_columns

    # 커서와 연결 닫기
    cur.close()
    response = {}
    response['sidebar_content'] = result.to_dict()
    response['schema'] =  schema
    #print(response)
    return json.dumps(response)


@app.route('/all_metrics', methods=['GET'])
def fetch_metrics_within_time_range(config=None, start_time='-infinity', end_time='infinity'):
    if request.args:
        print("HHHHHHHHHHHHHHH")
        params_json = request.args.get('params')
        args = json.loads(params_json)
        config = args['config']
    print(config)
    db_id = get_dbid(config)

    # 조회된 결과를 저장할 빈 DataFrame 생성
    result_df = pd.DataFrame()

    # DB 쿼리문
    db_statistics_query = """
    SELECT 
        timestamp, {} 
    FROM 
        {} 
    WHERE 
        dbid = %s
    AND timestamp BETWEEN '{}' AND '{}'
    GROUP BY timestamp;
    """

    # 모든 컬럼 이름 가져오기
    columns_query = """
    SELECT 
        COLUMN_NAME 
    FROM 
        INFORMATION_SCHEMA.COLUMNS 
    WHERE 
        TABLE_NAME = '{}' ;
    """
    
    cur = server_conn.cursor()
    # metric table들을 순회하며 조회 쿼리를 실행하고 결과를 DataFrame에 추가
    for table_name in metric_tables:
        if table_name in db_statistics_tables:
            continue
            cur.execute(columns_query.format(table_name))
            column_names = [row[0] for row in cur.fetchall()]
            column_names = [col for col in column_names if col not in ['timestamp', 'dbid', 'datid','datname']]
            
            # 컬럼들의 합을 계산하고 datid로 groupby
            query = db_statistics_query.format(", ".join(["SUM({}) AS {}".format(col, col) for col in column_names]), table_name, start_time, end_time)
        elif table_name in non_default_table:
            continue
        else:
            cur.execute(columns_query.format(table_name))
            column_names = [row[0] for row in cur.fetchall()]
            column_names = [col for col in column_names if col not in ['timestamp', 'dbid', 'datid','datname']]
            
            query = f"""
                SELECT timestamp, {", ".join([col for col in column_names])}
                FROM {table_name}
                WHERE dbid = %s
            """
            if start_time is not None and end_time is not None:
                query += f"AND timestamp BETWEEN '{start_time}' AND '{end_time}'"
        cur.execute(query, (db_id,))
        results = cur.fetchall()
        #result_df.set_index('timestamp', inplace=True)
        

        temp_df = pd.DataFrame(results, columns=['timestamp'] + column_names)
        temp_df.set_index('timestamp', inplace=True)
        result_df = pd.concat([result_df, temp_df], axis=1)
        print(result_df.head)
        print(result_df.columns)
    result_df = result_df.reset_index()

    result_df['timestamp'] = result_df['timestamp'].astype(str)
    # DataFrame을 pickle로 직렬화
    serialized_df = pickle.dumps(result_df)

    # Response 객체에 직렬화된 데이터와 MIME 타입을 지정하여 담기
    response = Response(serialized_df, mimetype='application/octet-stream')

    return response

        
def run_anomaly_detector(config, model_name, metric=''):

    # 모델 초기화
    model = IsolationForest()

    # 데이터 전처리
    # ...

    # 학습 데이터와 테스트 데이터 분리
    train_data, test_data = train_test_split(data, test_size=0.2)

    # 모델 학습
    model.fit(train_data)

    # 이상치 검출
    results = pd.DataFrame(model.predict(test_data))
    results['dbid'] = get_dbid(config)

    # 결과 데이터베이스에 저장
    results.to_sql(name='anomaly_detector', con=server_conn, if_exists='append')



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)