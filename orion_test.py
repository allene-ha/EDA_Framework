from typing import List, Union

import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np

from orion import Orion

hyperparameters = {
    'keras.Sequential.LSTMTimeSeriesRegressor#1': {
        'epochs': 30,
        'verbose': True
    }
}

orion = Orion(
    pipeline='lstm_dynamic_threshold',
    hyperparameters=hyperparameters
)

# 2022년 5월 1일 0시부터 24시까지 1초 간격으로 timestamp 생성
timestamp = pd.date_range(start='2022-05-01', end='2022-05-02', freq='S')[:-1]

# 0부터 1까지의 랜덤한 값을 생성하여 value로 설정
value = np.random.rand(len(timestamp))

# 간헐적으로 발생하는 anomaly 추가
for i in range(0, len(timestamp), 500):
    value[i:i+50] += np.random.normal(loc=2, scale=0.5, size=50)
    
# timestamp와 value로 이루어진 데이터프레임 생성
df = pd.DataFrame({'timestamp': timestamp, 'value': value})

# 데이터셋을 train과 test 데이터셋으로 나눔 (train : test = 7 : 3)
train_data, test_data = train_test_split(df, test_size=0.3, random_state=42)

orion.fit(train_data)

anomalies = orion.detect(test_data)

print(anomalies) # DataFrame
