"""Util functions for retrieving from different metric source """

from typing import Any, Callable, Dict

#from driver.aws.cloudwatch import cloudwatch_collector
from driver.collector import mysql_collector

METRIC_SOURCE_COLLECTOR: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    #"mysql": mysql_collector,
    #"linux": linux_collector,
}