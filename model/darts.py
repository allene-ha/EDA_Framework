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
from darts.models import (
    FFT,
    RNNModel,
    TCNModel,
    TransformerModel,
    NBEATSModel,
    BlockRNNModel,
    VARIMA,
)
from darts.models.forecasting.arima import ARIMA
from darts.models.forecasting.auto_arima import AutoARIMA
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

def merge_dicts(original_dict, new_dict):
    for key, value in new_dict.items():
        if key not in original_dict:
            original_dict[key] = value
    return original_dict


def lp_train_with_darts(train_df, pipeline, hyperparameters={}):
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    train_df.fillna(method='ffill', inplace = True)
    train_series = TimeSeries.from_dataframe(train_df, "timestamp", train_df.columns[1])
    if pipeline in ['RNN','LSTM']:
        rnn_hyperparameters = {"input_chunk_length": 24}
        hyperparameters = merge_dicts(hyperparameters, rnn_hyperparameters)                        
        model = RNNModel(**hyperparameters)
    elif pipeline in ['ARIMA']:                      
        model = ARIMA(**hyperparameters)
        print("HERE")
    elif pipeline in ['AutoARIMA']:                      
        model = AutoARIMA(**hyperparameters)
    elif pipeline in ['TCN']:                      
        tcn_hyperparameters = { "input_chunk_length":13,
                                "output_chunk_length":12,}
        hyperparameters = merge_dicts(hyperparameters, tcn_hyperparameters)    
        model = TCNModel(**hyperparameters)
    elif pipeline in ['Transformer']:        
        tf_hyperparameters = { "input_chunk_length":13,
                                "output_chunk_length":12,} 
        hyperparameters = merge_dicts(hyperparameters, tf_hyperparameters)    
        model = TransformerModel(**hyperparameters)
    elif pipeline in ['FFT']:    
        fft_hyperparameters = {"required_matches":set(), "nr_freqs_to_keep":None} 
        hyperparameters = merge_dicts(hyperparameters, fft_hyperparameters)    
        model = FFT(**hyperparameters)
    elif pipeline in ['NBEATS']:    
        nbeats_hyperparameters = {"input_chunk_length":30, "output_chunk_length":7} 
        hyperparameters = merge_dicts(hyperparameters, nbeats_hyperparameters)    
        model = NBEATSModel(**hyperparameters)
    

    model.fit(train_series)
    
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"darts_{pipeline}_{timestamp}.pickle"
    path = '/home/eda_framework_visualization/model/trained_model/lp/'+filename
    model.save(path)
    print(f"saved model {filename}")

def lp_predict_with_darts(server_conn, db_id, filename, metric,  n):
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

   
    path = '/home/eda_framework_visualization/model/trained_model/lp/'+filename
    if filename.split('_')[1] == 'RNN':
        model = RNNModel.load(path)
    elif filename.split('_')[1] == 'ARIMA':                      
        model = ARIMA.load(path)
    elif filename.split('_')[1] == 'AutoARIMA':                      
        model = AutoARIMA.load(path)
    elif filename.split('_')[1] == 'TCN':                          
        model = TCNModel.load(path)
    elif filename.split('_')[1] == 'Transformer':            
        model = TransformerModel.load(path)
    elif filename.split('_')[1] == 'FFT':    
        model = FFT.load(path)
    elif filename.split('_')[1] == 'NBEATS':    
        model = NBEATSModel.load(path)

    predicted_series = model.predict(n=n)

    pred_df = predicted_series.pd_dataframe() # timeseries # score
    pred_df.reset_index(inplace=True)
    
    pred_df.columns = ['timestamp','predicted']
    result_df = pred_df.copy()
    # Server에 저장
    # 현재 시간 가져오기
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur = server_conn.cursor()
    pred_df = pred_df.applymap(lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if isinstance(x, pd.Timestamp) else x)

    pred_df['metric'] = metric
    pred_df['analysis_time'] = current_time
    pred_df['dbid'] = db_id

    columns = pred_df.columns.tolist()

    pred_df = pred_df[['dbid', 'analysis_time','timestamp','metric','predicted']]

    # Generate the placeholders for the INSERT query
    placeholders = ', '.join(['%s'] * len(columns))

    # Convert the DataFrame to a list of tuples
    values = [tuple(row) for row in pred_df.values]

    # Execute the INSERT query
    cur.executemany(f"INSERT INTO load_prediction VALUES ({placeholders})", values)

    # Commit the changes
    server_conn.commit()

    # Close the cursor and connection
    cur.close()
    
    return result_df



def ad_train_with_darts(train_df, pipeline, hyperparameters = {}):
    train_df.fillna(method='ffill', inplace = True)
    train_series = TimeSeries.from_dataframe(train_df, "timestamp", train_df.columns[1])

    if 'kmeans_scorer' in pipeline:
        model = KMeansScorer(**hyperparameters)
    elif 'pyod' in pipeline:
        pyod_hyperparameters = {"model": KNN()}
        hyperparameters = merge_dicts(hyperparameters, pyod_hyperparameters)     
        model = PyODScorer(**hyperparameters)
    elif 'wasserstein' in pipeline:
        model = WassersteinScorer(**hyperparameters)
    
    model.fit(train_series)
    
    current_time = datetime.now()
    timestamp = current_time.strftime("%Y%m%d_%H%M%S")
    filename = f"darts_{pipeline}_{timestamp}.pickle"
    with open(f'model/trained_model/ad/{filename}', 'wb') as file:
        pickle.dump(model, file)
        print(f"saved model {filename}")


def ad_predict_with_darts(server_conn, db_id, test_df, path):
    metric =  test_df.columns[1]
    test_series = TimeSeries.from_dataframe(test_df, "timestamp", metric)

    with open('/home/eda_framework_visualization/model/trained_model/ad/'+path, 'rb') as file:
        model = pickle.load(file)

    anom_score = model.score(test_series)

    anom_df = anom_score.pd_dataframe() # timeseries # score
    anom_df.reset_index(inplace=True)
    
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
   