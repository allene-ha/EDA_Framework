import pandas as pd
import datetime

json_file_path = 'workload_spike_1_result.json'
df = pd.read_json(json_file_path)
df['analysis_time'] = datetime.datetime.now()
df['timestamp'] = df.index
df['dbid'] = '323dc0c5-6c1a-4bfa-b34a-398ade69251d'

print(df)

import psycopg2
from sqlalchemy import create_engine

# 데이터베이스 연결 정보
# db_connection = psycopg2.connect(
#     host="localhost",
#     database="dbeda",
#     user="postgres",
#     password="postgres"
# )
df['is_anomaly'] = df['is_anomaly'].astype(bool)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# 데이터베이스 연결을 열고 데이터를 테이블에 삽입
engine = create_engine('postgresql://postgres:postgres@localhost:5433/dbeda')
df.to_sql('anomaly_explanation', engine, if_exists='append', index=False)
