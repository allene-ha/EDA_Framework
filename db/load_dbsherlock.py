from sqlalchemy import create_engine
import json
import pandas as pd
from config_utils import config

server_db_port = config.get('serverdb')
server_port = config.get('server')

# Replace the placeholder values with your actual database connection details
server_engine = create_engine(f'postgresql://postgres:postgres@localhost:{server_db_port}/dbeda')
csv_file_path = '/root/DBEDA/db/test_1.csv'
df = pd.read_csv(csv_file_path)

from datetime import datetime
date_string = "2023-11-17"
date_object = datetime.strptime(date_string, "%Y-%m-%d")

# timestamp로 변환
timestamp = int(date_object.timestamp()) * 1000000000
df['timestamp'] = pd.to_datetime(df['Epoch']*(10000000000)+timestamp)
df.drop(columns = ['Epoch'], inplace=True)
df.columns = list(map(lambda x: x.replace(" ","_").replace("(","").replace(")","").replace("_#","").lower(), df.columns))
df.to_sql('dbsherlock', con=server_engine, if_exists='replace', index=False)


