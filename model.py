import datetime
import json
from DBAnomTransformer.detector import DBAnomDector
import numpy as np
import pandas as pd

eda_training_path = '/root/DBEDA/benchmark/dataset'
dbsherlock_path = '/root/Anomaly_Explanation/dataset/dbsherlock/converted' 

from omegaconf import OmegaConf

from DBAnomTransformer.config.utils import default_config
from DBAnomTransformer.detector import DBAnomDector
from config_utils import config
dataset_name = "DBS"
#dataset_name = "EDA"

# Create config
eda_config = default_config
dbsherlock_config = OmegaConf.create(
    config.get('dbsherlock')
)


# Create dummy data
if dataset_name == "EDA":
    feature_num = 29
elif dataset_name == "DBS":
    feature_num = 200 # 92
dummy_data = np.random.rand(130, feature_num)
dummy_data = pd.DataFrame(dummy_data, columns=[f"attr_{i}" for i in range(feature_num)])


# Initialize and train model
if dataset_name == "EDA":
    detector = DBAnomDector()
    detector.train(dataset_path="dataset/EDA/")
elif dataset_name == "DBS":
    detector = DBAnomDector(override_config=dbsherlock_config)
    detector.train(
        dataset_path="/root/Anomaly_Explanation/dataset/dbsherlock/converted/tpcc_500w_test.json",
        dataset_name="DBS",
    )

# Run inference (detect anomaly)
anomaly_score, is_anomaly, anomaly_cause = detector.infer(data=dummy_data)

# # Create dummy data
# dummy_data = np.random.rand(130, 29)
# dummy_data = pd.DataFrame(dummy_data, columns=[f"attr_{i}" for i in range(29)])

# # Load model
# detector = DBAnomDector()
# # Train model
# detector.train(dataset_path=eda_training_path)
# # Run inference (detect anomaly
# anomaly_score, is_anomaly, anomaly_cause = detector.infer(data=dummy_data)
print(anomaly_score, is_anomaly, anomaly_cause)