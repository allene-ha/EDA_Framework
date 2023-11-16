import numpy as np
import pandas as pd
from omegaconf import OmegaConf
from DBAnomTransformer.config.utils import default_config
from DBAnomTransformer.detector import DBAnomDector
import json
import pytz
import random
from sqlalchemy import create_engine
from datetime import datetime
import pickle
CAUSES_DBSHERLOCK = ['Poorly Written Query', 
                     'Poor Physical Design', 
                     'Workload Spike', 
                     'I/O Saturation', 
                     'DB Backup', 
                     'Table Restore', 
                     'CPU Saturation', 
                     'Flush Log/Table', 
                     'Network Congestion', 
                     'Lock Contention']
CAUSES_EDA = [  'CPU Saturation', 
                'DB Backup', 
                'Poor Physical Design', 
                'Memory Saturation', 
                'Poorly Written Query', 
                'Workload Spike']

with open('../port.json', 'r') as json_file:
    data = json.load(json_file)
    server_db_port = data.get('serverdb')
    server_port = data.get('server')

def ade_train_anomaly_transformer_from_dbsherlock(pipeline, hyperparameters):
    # DB Sherlock 데이터 불러오기
    dataset_name = "DBS"
    
    dbsherlock_config = OmegaConf.create(
        {
            "model": {"num_anomaly_cause": 11, "num_feature": 200},
            "model_path": "checkpoints/DBS_checkpoint.pth",
            "scaler_path": "checkpoints/DBS_scaler.pkl",
            "stats_path": "checkpoints/DBS_stats.json",
        }
    )

    detector = DBAnomDector(override_config=dbsherlock_config)
    detector.train(
        dataset_path="/root/Anomaly_Explanation/dataset/dbsherlock/converted/tpcc_500w_test.json",
        dataset_name="DBS",
    )
    

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"DBAT_{pipeline}_{timestamp}.pickle"
    with open(f'model/trained_model/ade/{filename}', 'wb+') as file:
        pickle.dump(detector, file)
        print(f"saved model {filename}")


def ade_train_anomaly_transformer(train_df, pipeline, hyperparameters):
    train_df.fillna(method='ffill', inplace = True)
    detector = DBAnomDector()
    detector.train(dataset_path="dataset/EDA/")

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"DBAT_{pipeline}_{timestamp}.pickle"
    with open(f'model/trained_model/ade/{filename}', 'wb') as file:
        pickle.dump(detector, file)
        print(f"saved model {filename}")


def ade_predict_anomaly_transformer(server_conn, db_id, test_df, path):
    with open('/root/DBEDA/server/model/trained_model/ade/'+path, 'rb') as file:
        detector = pickle.load(file)
    # test_df.columns = ['timestamp', 'metric1', ...]
    test_data = test_df.drop(columns=['timestamp'])
    if 'combined_avg_latency' in test_data.columns:
        test_data = test_data.drop(columns=['combined_avg_latency'])


    if len(test_data.columns) == 200: # DBSHERLOCK
        dataset = 'dbsherlock_tpcc_500w'
        CAUSES = CAUSES_DBSHERLOCK
    else:
        dataset = 'eda'
        CAUSES = CAUSES_EDA

    anomaly_score, is_anomaly, anomaly_cause = detector.infer(data=test_data)
    anomaly_cause = list(map(lambda x: CAUSES[x], anomaly_cause)) # String으로 변환
    data = {
        "timestamp": list(test_df['timestamp']),
        "anomaly_score": anomaly_score,
        "is_anomaly": is_anomaly,
        "anomaly_cause": anomaly_cause
        }

    # 데이터프레임 생성
    anomaly_df = pd.DataFrame(data)
    
    #anomaly_df.reset_index(inplace=True)
    
    result_df = anomaly_df.copy()
    # Server에 저장
    
    # 현재 시간 가져오기
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = server_conn.cursor()
    anomaly_df = anomaly_df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)

    anomaly_df['analysis_time'] = current_time
    anomaly_df['dbid'] = db_id
    anomaly_df['dataset'] = dataset
    anomaly_df = anomaly_df[['dbid','analysis_time','timestamp','anomaly_score','is_anomaly','anomaly_cause','dataset']]
    columns = anomaly_df.columns.tolist()
    
    # Generate the placeholders for the INSERT query
    placeholders = ', '.join(['%s'] * len(columns))
    # Convert the DataFrame to a list of tuples
    values = [tuple(row) for row in anomaly_df.values]
    # Execute the INSERT query
    cur.executemany(f"INSERT INTO anomaly_explanation VALUES ({placeholders})", values)

    #test_df['analysis_time'] = current_time
    #test_df['dbid'] = db_id
    #server_engine = create_engine(f'postgresql://postgres:postgres@localhost:{server_db_port}/dbeda')

    #test_df.to_sql(dataset, server_engine, if_exists='append', index=False)
    
    # Commit the changes
    server_conn.commit()

    # Close the cursor and connection
    cur.close()
    
    import time
    time.sleep(1)
    
    return result_df
   