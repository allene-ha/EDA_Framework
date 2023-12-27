import copy
import logging
from typing import *

import hkkang_utils.file as file_utils
import numpy as np
import pandas as pd
import tqdm
from omegaconf import OmegaConf
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from DBAnomTransformer.config.utils import default_config
from DBAnomTransformer.detector import DBAnomDector
from config_utils import config
from DBAnomTransformer.solver import detect_adjustment

dataset_name = "DBS"
# dataset_name = "EDA"

# Create config
eda_config = default_config
dbsherlock_config = OmegaConf.create(
    config.get('dbsherlock')
)


def dbsherlock_data_to_dataframe() -> pd.DataFrame:
    pass


def eval_ab_regions(
    gold: List[bool], pred: List[bool], do_adjustment: bool = False
) -> float:
    gold = copy.deepcopy(gold)
    pred = copy.deepcopy(pred)
    assert len(gold) == len(pred), f"len(gold): {len(gold)} != len(pred): {len(pred)}"
    # Preprocess
    if do_adjustment:
        pred = detect_adjustment(pred, gold)
    # Evaluate
    cnt = 0
    for i in range(len(gold)):
        if gold[i] == pred[i]:
            cnt += 1
    return cnt / len(gold)


def eval_precision_recall_fscore_support(
    gold: List[bool], pred: List[bool], do_adjustment: bool = False
) -> Tuple[float, float, float, float]:
    gold = copy.deepcopy(gold)
    pred = copy.deepcopy(pred)
    if do_adjustment:
        pred = detect_adjustment(pred, gold)
    return precision_recall_fscore_support(gold, pred, average="binary")


def read_in_dbsherlock_data() -> np.ndarray:
    file_path = (
        "/root/Anomaly_Explanation/dataset/dbsherlock/converted/tpcc_500w_test.json"
    )
    detector = DBAnomDector(override_config=dbsherlock_config)
    do_train = False
    if do_train:
        detector.train(
            dataset_path="dataset/dbsherlock/converted/tpcc_500w_test.json",
            dataset_name="DBS",
        )

    dataset = file_utils.read_json_file(file_path)["data"]
    # for data in tqdm.tqdm(dataset):
    # dataset = dataset[15:16]
    for idx, data in enumerate(dataset):
        values = np.array(data["values"])[:, 2:]
        values_as_df = pd.DataFrame(values, columns=data["attributes"][2:])

        # Run inference (detect anomaly)
        anomaly_score, is_anomaly, anomaly_cause = detector.infer(data=values_as_df)

        ab_regions = data["abnormal_regions"]
        assert (
            max(ab_regions) <= values_as_df.shape[0]
        ), f"ab_regions: {max(ab_regions)} > values_as_df.shape[0]: {values_as_df.shape[0]}"
        ab_regions = [i + 1 in ab_regions for i in range(values_as_df.shape[0])]

        acc = eval_ab_regions(ab_regions, is_anomaly, do_adjustment=True)

        precision, recall, f_score, support = eval_precision_recall_fscore_support(
            ab_regions, is_anomaly, do_adjustment=False
        )

        print(f"\nidx: {idx}")
        print(
            f"Before acc: {acc} precision: {precision} recall: {recall} f_score: {f_score}"
        )

        precision, recall, f_score, support = eval_precision_recall_fscore_support(
            ab_regions, is_anomaly, do_adjustment=True
        )

        print(
            f"After acc: {acc} precision: {precision} recall: {recall} f_score: {f_score}"
        )


def main():
    # Create dummy data
    if dataset_name == "EDA":
        feature_num = 29
    elif dataset_name == "DBS":
        feature_num = 200
    dummy_data = np.random.rand(130, feature_num)
    dummy_data = pd.DataFrame(
        dummy_data, columns=[f"attr_{i}" for i in range(feature_num)]
    )

    # Initialize and train model
    if dataset_name == "EDA":
        detector = DBAnomDector()
        # detector.train(dataset_path="dataset/EDA2/")
    elif dataset_name == "DBS":
        detector = DBAnomDector(override_config=dbsherlock_config)
        # detector.train(
        #     dataset_path="dataset/dbsherlock/converted/tpcc_500w_test.json",
        #     dataset_name="DBS",
        # )

    # Run inference (detect anomaly)
    anomaly_score, is_anomaly, anomaly_cause = detector.infer(data=dummy_data)

    # Evaluate the result


if __name__ == "__main__":
    logging.basicConfig(
        format="[%(asctime)s %(levelname)s %(name)s] %(message)s",
        datefmt="%m/%d %H:%M:%S",
        level=logging.INFO,
    )
    read_in_dbsherlock_data()
    # main()
    print("Done!")
