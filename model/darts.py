from typing import Sequence
from datetime import datetime
import numpy as np
import pandas as pd
from pyod.models.knn import KNN
from scipy.stats import cauchy, expon, gamma, laplace, norm, poisson
import pickle
from darts import TimeSeries
from darts.ad.scorers import CauchyNLLScorer
from darts.ad.scorers import DifferenceScorer as Difference
from darts.ad.scorers import (
    ExponentialNLLScorer,
    GammaNLLScorer,
    GaussianNLLScorer,
    KMeansScorer,
    LaplaceNLLScorer,
)
from darts.ad.scorers import NormScorer as Norm
from darts.ad.scorers import PoissonNLLScorer, PyODScorer, WassersteinScorer
from darts.models import MovingAverageFilter
from darts.tests.base_test_class import DartsBaseTestClass

list_NonFittableAnomalyScorer = [
    Norm(),
    Difference(),
    GaussianNLLScorer(),
    ExponentialNLLScorer(),
    PoissonNLLScorer(),
    LaplaceNLLScorer(),
    CauchyNLLScorer(),
    GammaNLLScorer(),
]

list_FittableAnomalyScorer = [
    PyODScorer(model=KNN()),
    KMeansScorer(),
    WassersteinScorer(),
]

list_NLLScorer = [
    GaussianNLLScorer(),
    ExponentialNLLScorer(),
    PoissonNLLScorer(),
    LaplaceNLLScorer(),
    CauchyNLLScorer(),
    GammaNLLScorer(),
]

def lp_train_with_darts(train_df, pipeline, hyperparameters={}):
    train_df.fillna(method='ffill', inplace = True)
    train_series = TimeSeries.from_dataframe(train_df, "timestamp", train_df.columns[1])
    if pipeline == 'FFT':
        model = FFT(required_matches=set(), nr_freqs_to_keep=None, **hyperparameters)




def ad_train_with_darts(train_df, pipeline, hyperparameters = {}):
    train_df.fillna(method='ffill', inplace = True)
    train_series = TimeSeries.from_dataframe(train_df, "timestamp", train_df.columns[1])

    if pipeline == 'kmeans_scorer':
        model = KMeansScorer(**hyperparameters)
    
    model.fit(train_series)
    
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"darts_{pipeline}_{timestamp}.pickle"
    with open(f'model/trained_model/{filename}', 'wb') as file:
        pickle.dump(model, file)
        print(f"saved model {filename}")


def ad_predict_with_darts(server_conn, db_id, test_df, path):
    metric =  test_df.columns[1]
    test_series = TimeSeries.from_dataframe(test_df, "timestamp", metric)

    with open('/home/eda_framework_visualization/model/trained_model/'+path, 'rb') as file:
        model = pickle.load(file)

    anom_score = model.score(test_series)

    anom_df = anom_score.pd_dataframe() # timeseries # score
    anom_df.reset_index(inplace=True)
    
    print(anom_df)
    print(anom_df.columns)
    print(anom_df.index)
    
    anom_df.columns = ['timestamp','anomaly_score']
    result_df = anom_df.copy()
    #return anom_df
    # Server에 저장
    # 현재 시간 가져오기
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = server_conn.cursor()
    anom_df = anom_df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)

    anom_df['metric'] = metric
    anom_df['analysis_time'] = current_time
    anom_df['dbid'] = db_id
    print(anom_df)
    columns = anom_df.columns.tolist()

    anom_df = anom_df[['dbid', 'analysis_time','timestamp','metric','anomaly_score']]

    # Generate the placeholders for the INSERT query
    placeholders = ', '.join(['%s'] * len(columns))

    # Convert the DataFrame to a list of tuples
    values = [tuple(row) for row in anom_df.values]

    # Execute the INSERT query
    cur.executemany(f"INSERT INTO anomaly_scorer VALUES ({placeholders})", values)

    # Commit the changes
    server_conn.commit()

    # Close the cursor and connection
    cur.close()
    
    return result_df
   