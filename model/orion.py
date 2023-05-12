from typing import List, Union

import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from datetime import datetime
from orion import Orion


def train_with_orion_pipeline(df, pipeline, hyperparameters = {}):
    print("HERE")
    if hyperparameters == {}:
        hyperparameters = {
        "mlprimitives.custom.timeseries_preprocessing.time_segments_aggregate#1": {
            "interval": 300
        },
        "mlprimitives.custom.timeseries_preprocessing.rolling_window_sequences#1": {
            "window_size": 100
        },
        "keras.Sequential.LSTMTimeSeriesRegressor#1": {
            "epochs": 5,
            "verbose": True
        }
    }
    orion = Orion(
        pipeline=pipeline,
        hyperparameters=hyperparameters
    ) # tensoflow open

    if df.shape[1] != 2:
        transformed_dfs = []
        print(df.columns[1:])
        # timestamp 컬럼과 각 메트릭 컬럼으로 이루어진 데이터프레임 생성
        for metric_col in df.columns[1:]:  # metric 컬럼들만 선택
            transformed_df = df[['timestamp', metric_col]].copy()  # timestamp와 해당 metric 컬럼 선택
            transformed_df.columns = ['timestamp','value']
            print(metric_col)
            # 특정 컬럼의 데이터 타입 확인
            if pd.api.types.is_datetime64_any_dtype(transformed_df['value']):
                transformed_df['value'] = transformed_df['value'].astype(int) / 10**9

            #transformed_df['value'] = transformed_df['value'].astype(float)
           
            # transformed_dfs.append(transformed_df)  # 변형된 데이터프레임 리스트에 추가
            orion.fit(transformed_df)

        # # 결과 확인
        # for transformed_df in transformed_dfs:
        #     print(transformed_df)
            
    else:
        orion.fit(df)

    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline}_{timestamp}.pickle"
    orion.save('/home/eda_framework_visualization/model/trained_model/'+filename)
    print(f"saved the trained model at /home/eda_framework_visualization/model/trained_model/{filename}")
    # orion.fit(train_data)

    # anomalies = orion.detect(test_data)

    # print(anomalies) # DataFrame


def detect_with_orion_pipeline(server_conn, db_id, df, path):
    print("detect_with_orion_pipeline")
    orion = Orion.load(path)
    print(orion)
    print(orion._fitted)
    anomaly_dict = {}
    if df.shape[1] != 2:
        #transformed_dfs = []

        # timestamp 컬럼과 각 메트릭 컬럼으로 이루어진 데이터프레임 생성
        for metric_col in df.columns[1:]:  # metric 컬럼들만 선택
            transformed_df = df[['timestamp', metric_col]].copy()  # timestamp와 해당 metric 컬럼 선택
            transformed_df.columns = ['timestamp','value']
            #transformed_dfs.append(transformed_df)  # 변형된 데이터프레임 리스트에 추가
            print(metric_col)
            if pd.api.types.is_datetime64_any_dtype(transformed_df['value']):
                transformed_df['value'] = transformed_df['value'].astype(int) / 10**9
            transformed_df['value'] = transformed_df['value'].astype(float)
            print(transformed_df)
            anomalies = orion.detect(transformed_df)
            anomaly_dict[metric_col] = anomalies
            print(anomalies)
            print(type(anomalies))
            
            
    else:
        anomalies = orion.detect(df)

    

    print(anomaly_dict)
    # start, end, severity를 담은 Dataframe
    # 
    # Server에 저장
    # 현재 시간 가져오기
    current_time = datetime.now()
    cur = server_conn.cursor()
    for metric in anomaly_dict:
        anomalies = anomaly_dict[metric]
        for index, row in anomalies.iterrows():
            start = datetime.strptime(row['start'], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(row['end'], '%Y-%m-%d %H:%M:%S')
            severity = row['severity']
            
            # SQL 쿼리
            query = "INSERT INTO anomaly_time_interval (dbid, metric, analysis_time, start, end, severity) VALUES (%s, %s, %s, %s, %s, %s)"
            values = (db_id, metric, current_time, start, end, severity)
            print(values)
            # 쿼리 실행
            cur.execute(query, values)


#     CREATE TABLE anomaly_time_interval (
#     dbid varchar(36) NOT NULL,
#     analysis_time TIMESTAMP NOT NULL,
#     metric varchar(200),
#     start TIMESTAMP NOT NULL,
#     end TIMESTAMP NOT NULL,
#     severity FLOAT,
#     PRIMARY KEY (dbid, timestamp)
# );