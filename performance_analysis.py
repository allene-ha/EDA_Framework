import json
import os
import datetime as dt
from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
import pickle
import numpy as np
import pandas as pd
import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML, Layout
from IPython.display import display, clear_output
import mplcursors
from matplotlib.legend_handler import HandlerLine2D
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates 
import copy
from matplotlib.dates import DateFormatter
plt.style.use('seaborn-notebook')
from query import * 
from dataframe_visualization import *
#import plotly.graph_objects as go
import altair as alt
from bidict import bidict

METRIC_DICT = bidict({
        "num_sessions":"Sessions",
        "num_wait_sessions":"Waiting Sessions",
        "sessions_by_state": "Sessions By State",
        "sessions_by_wait_event_type": "Sessions By WaitEventType",
        "oldest_backend_time_sec": "Oldest Backend",
        "longest_query_time_sec": "Oldest Query",
        "longest_transaction_time_sec": "Oldest Transaction",
        "numbackends": "Backends",
        "deadlocks": "Deadlocks",
        "blks_hit": "Disk Blocks Hit",
        "blks_read": "Disk Blocks Read",
        "temp_files": "Temporary Files",
        "temp_bytes": "Temporary Files Size",
        "xact_total": "Total Transactions",
        "xact_commit": "Transactions Committed",
        "xact_rollback": "Transactions Rolled back",
        "tup_deleted": "Tuples Deleted",
        "tup_fetched": "Tuples Fetched",
        "tup_inserted": "Tuples Inserted",
        "tup_returned": "Tuples Returned",
        "tup_updated": "Tuples Updated",
})


def is_digit(str):
    try:
        tmp = float(str)
        return True
    except ValueError:
        return False

def get_path():
    f = open('path.txt', mode = 'r')
    path = f.readline()
    path.rstrip('\n')
    f.close()
    return path

def get_column_mysql() -> dict: #metric 종류를 담은 dict을 return

    path = get_path()
    file_list = os.listdir(path)
    remove_list = []
    filename = file_list[0]
    file_datetime = dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
    #print(os.path.join(path, filename))
    with open(os.path.join(path, filename), 'r') as f:
        # 파일 내를 탐색
        text = json.load(f)

    metrics_data = text['metrics_data']['global']['global']
    metrics = list(text['metrics_data']['global']['global'].keys())
    # 이상한 metric들 제거
    for me in metrics:
        if is_digit(metrics_data[me]):
            pass
        else:
            remove_list.append(me)

    metrics= [x for x in metrics if x not in remove_list]
    innodb_metrics = list(text['metrics_data']['global']['innodb_metrics'].keys())
    derived_metrics = list(text['metrics_data']['global']['derived'].keys())
    resource_metrics = list(text['metrics_data']['global']['engine']['innodb_status_io'].keys())
    resource_metrics.append('cpu')
    wait_metrics = list(text['metrics_data']['global']['wait'].keys())

    column = {}
    column['metrics'] = metrics
    column['innodb_metrics'] = innodb_metrics
    column['derived_metrics'] = derived_metrics
    column['resource_metrics'] = resource_metrics
    column['wait'] = wait_metrics
    return column

def get_column_pg() -> dict: #metric 종류를 담은 dict을 return

    path = get_path()
    file_list = os.listdir(path)
    filename = file_list[0]
    file_datetime = dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
    #print(os.path.join(path, filename))
    with open(os.path.join(path, filename), 'r') as f:
        # 파일 내를 탐색
        text = json.load(f)

    
    archiver_metrics = list(text['metrics_data']['global']['pg_stat_archiver'].keys())
    remove_list = []
    for me in archiver_metrics:
        if isinstance(text['metrics_data']['global']['pg_stat_archiver'][me], (int, float)) or is_digit(text['metrics_data']['global']['pg_stat_archiver'][me]):
            pass
        else:
            remove_list.append(me)
    archiver_metrics = [x for x in archiver_metrics if x not in remove_list]
    bgwriter_metrics = list(text['metrics_data']['global']['pg_stat_bgwriter'].keys())
    remove_list = []
    for me in bgwriter_metrics:
        if isinstance(text['metrics_data']['global']['pg_stat_bgwriter'][me], (int, float)) or is_digit(text['metrics_data']['global']['pg_stat_bgwriter'][me]):
            pass
        else:
            remove_list.append(me)
    bgwriter_metrics = [x for x in bgwriter_metrics if x not in remove_list]

    agg_database_metrics = list(text['metrics_data']['local']['database']['pg_stat_database']['aggregated'].keys())
    agg_conflicts_metrics = list(text['metrics_data']['local']['database']['pg_stat_database_conflicts']['aggregated'].keys())
    
    agg_user_tables_metrics = list(text['metrics_data']['local']['table']['pg_stat_user_tables']['aggregated'].keys())
    agg_user_tables_io_metrics = list(text['metrics_data']['local']['table']['pg_statio_user_tables']['aggregated'].keys())

    agg_user_indexes_metrics = list(text['metrics_data']['local']['index']['pg_stat_user_indexes']['aggregated'].keys())
    agg_user_indexes_io_metrics = list(text['metrics_data']['local']['index']['pg_statio_user_indexes']['aggregated'].keys())

    raw_database_metrics = copy.deepcopy(agg_database_metrics)
    raw_database_metrics.append('datid')
    raw_database_metrics.append('datname')
    
    raw_conflicts_metrics = copy.deepcopy(agg_conflicts_metrics)
    raw_conflicts_metrics.append('datid')
    raw_conflicts_metrics.append('datname')

    agg_activity_metrics = list(text['metrics_data']['local']['activity']['aggregated'].keys())
    activity_state_metrics = ['active','idle','idle in transaction','idle in transaction (aborted)','fastpath function call', 'disabled']
    activity_wait_event_type_metrics = ['Activity','BufferPin','Client','Extension','IO','IPC','Lock','LWLock','Timeout']
    
    column = {}

    column['archiver_metrics'] = archiver_metrics
    column['bgwriter_metrics'] = bgwriter_metrics
    column['agg_database_metrics'] = agg_database_metrics
    column['agg_conflicts_metrics'] = agg_conflicts_metrics
    column['agg_user_tables_metrics'] = agg_user_tables_metrics
    column['agg_user_tables_io_metrics'] = agg_user_tables_io_metrics
    column['agg_user_indexes_metrics'] = agg_user_indexes_metrics
    column['agg_user_indexes_io_metrics'] = agg_user_indexes_io_metrics
    column['raw_database_metrics'] = raw_database_metrics
    column['raw_conflicts_metrics'] = raw_conflicts_metrics
    column['agg_activity_metrics'] = agg_activity_metrics
    column['activity_state_metrics'] = activity_state_metrics
    column['activity_wait_event_type_metrics'] = activity_wait_event_type_metrics
    
    for c in column.keys():
        column[c].append('timestamp')

    #print(column)

    return column


def create_dataframe(col):
    metrics = {}
    for me in col.keys():
        metrics[me] = pd.DataFrame(columns = col[me])   

    return metrics

def import_metrics_mysql(metrics, text, timestamp,col):
    metrics_data = text['metrics_data']['global']['global']
    new_row = {}
    for m in col['metrics']:
        new_row[m] = metrics_data[m]
    metrics['metrics'] = metrics['metrics'].append(new_row,ignore_index=True)
   
    innodb_metrics_data = text['metrics_data']['global']['innodb_metrics']
    new_row = {}
    for m in col['innodb_metrics']:
        new_row[m] = innodb_metrics_data[m]
    metrics['innodb_metrics'] = metrics['innodb_metrics'].append(new_row,ignore_index=True)
    
    derived_metrics_data = text['metrics_data']['global']['derived']
    new_row = {}
    for m in col['derived_metrics']:
        new_row[m] = derived_metrics_data[m]
    metrics['derived_metrics'] = metrics['derived_metrics'].append(new_row,ignore_index=True)
    
    resource_metrics_data = text['metrics_data']['global']['engine']['innodb_status_io']
    new_row = {}
    new_row['data_io'] = resource_metrics_data['data_io']
    new_row['log_io'] = resource_metrics_data['log_io']
    new_row['cpu'] = text['metrics_data']['global']['cpu']
    metrics['resource_metrics'] = metrics['resource_metrics'].append(new_row,ignore_index=True)
    
    wait_metrics_data = text['metrics_data']['global']['wait']
    
    metrics['wait'] = metrics['wait'].append(wait_metrics_data, ignore_index = True)
    
    
    return metrics

def import_metrics_pg(metrics, text, timestamp,col):
    # Timestamp를 활용하자
    metrics_data = text['metrics_data']

    archiver_metrics_data = metrics_data['global']['pg_stat_archiver']
    archiver_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['archiver_metrics']:
        new_row[m] = archiver_metrics_data[m]
    
    metrics['archiver_metrics'] = metrics['archiver_metrics'].append(new_row,ignore_index=True)
   
    bgwriter_metrics_data = metrics_data['global']['pg_stat_bgwriter']
    bgwriter_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['bgwriter_metrics']:
        new_row[m] = bgwriter_metrics_data[m]
    metrics['bgwriter_metrics'] = metrics['bgwriter_metrics'].append(new_row,ignore_index=True)
    
    agg_database_metrics_data = metrics_data['local']['database']['pg_stat_database']['aggregated']
    agg_database_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_database_metrics']:
        new_row[m] = agg_database_metrics_data[m]
    metrics['agg_database_metrics'] = metrics['agg_database_metrics'].append(new_row,ignore_index=True)

    agg_conflicts_metrics_data = metrics_data['local']['database']['pg_stat_database_conflicts']['aggregated']
    agg_conflicts_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_conflicts_metrics']:
        new_row[m] = agg_conflicts_metrics_data[m]
    metrics['agg_conflicts_metrics'] = metrics['agg_conflicts_metrics'].append(new_row,ignore_index=True)

    agg_user_tables_metrics_data = metrics_data['local']['table']['pg_stat_user_tables']['aggregated']
    agg_user_tables_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_user_tables_metrics']:
        new_row[m] = agg_user_tables_metrics_data[m]
    metrics['agg_user_tables_metrics'] = metrics['agg_user_tables_metrics'].append(new_row,ignore_index=True)

    agg_user_tables_io_metrics_data = metrics_data['local']['table']['pg_statio_user_tables']['aggregated']
    agg_user_tables_io_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_user_tables_io_metrics']:
        new_row[m] = agg_user_tables_io_metrics_data[m]
    metrics['agg_user_tables_io_metrics'] = metrics['agg_user_tables_io_metrics'].append(new_row,ignore_index=True)

    agg_user_indexes_metrics_data = metrics_data['local']['index']['pg_stat_user_indexes']['aggregated']
    agg_user_indexes_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_user_indexes_metrics']:
        new_row[m] = agg_user_indexes_metrics_data[m]
    metrics['agg_user_indexes_metrics'] = metrics['agg_user_indexes_metrics'].append(new_row,ignore_index=True)

    agg_user_indexes_io_metrics_data = metrics_data['local']['index']['pg_statio_user_indexes']['aggregated']
    agg_user_indexes_io_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_user_indexes_io_metrics']:
        new_row[m] = agg_user_indexes_io_metrics_data[m]
    metrics['agg_user_indexes_io_metrics'] = metrics['agg_user_indexes_io_metrics'].append(new_row,ignore_index=True)

    
    raw_database_metrics_data = metrics_data['local']['database']['pg_stat_database']['raw'] 
    for d in raw_database_metrics_data.keys():
        new_row = {}
        for m in col['raw_database_metrics']:
            if m in raw_database_metrics_data[d]:
                new_row[m] = raw_database_metrics_data[d][m]
        new_row['timestamp'] = timestamp
        metrics['raw_database_metrics'] = metrics['raw_database_metrics'].append(new_row,ignore_index=True)

    raw_conflicts_metrics_data = metrics_data['local']['database']['pg_stat_database_conflicts']['raw'] 
    for d in raw_conflicts_metrics_data.keys():
        new_row = {}
        for m in col['raw_conflicts_metrics']:
            if m in raw_conflicts_metrics_data[d]:
                new_row[m] = raw_conflicts_metrics_data[d][m]
        new_row['timestamp'] = timestamp
        metrics['raw_conflicts_metrics'] = metrics['raw_conflicts_metrics'].append(new_row,ignore_index=True)

    agg_activity_metrics_data = metrics_data['local']['activity']['aggregated']
    agg_activity_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['agg_activity_metrics']:
        if m in agg_activity_metrics_data:
            new_row[m] = agg_activity_metrics_data[m]
    metrics['agg_activity_metrics'] = metrics['agg_activity_metrics'].append(new_row,ignore_index=True)

    activity_state_metrics_data = metrics_data['local']['activity']['raw']['state']
    activity_state_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['activity_state_metrics']:
        if m in activity_state_metrics_data:
            new_row[m] = activity_state_metrics_data[m]
    metrics['activity_state_metrics'] = metrics['activity_state_metrics'].append(new_row,ignore_index=True)

    activity_wait_event_type_metrics_data = metrics_data['local']['activity']['raw']['wait_event_type']
    activity_wait_event_type_metrics_data['timestamp'] = timestamp
    new_row = {}
    for m in col['activity_wait_event_type_metrics']:
        if m in activity_wait_event_type_metrics_data:
            new_row[m] = activity_wait_event_type_metrics_data[m]
    metrics['activity_wait_event_type_metrics'] = metrics['activity_wait_event_type_metrics'].append(new_row,ignore_index=True)
    
    
    #print(metrics)
    return metrics


class digest_query:
    def __init__(self, query_id, digest, digest_text, time_ms, cpu_usage=0, io=0, count=0, timestamp=0):
        self.query_id = query_id
        self.digest = digest
        self.digest_text = digest_text
        self.value = [[timestamp, time_ms, cpu_usage, io, count]]
        self.time_ms = []
        self.cpu_usage = []
        self.io = []
        self.count = []
        self.timestamp = []
    
    def add_time(self, time_ms):
        self.value[-1][1]+=time_ms
    
    def add_timestamp(self, time_ms, cpu_usage=0, io=0, count=0, timestamp=0):
        self.value.append([timestamp, time_ms, cpu_usage, io, count])
    
    def print_digest_query(self):
        print(f'query_id={self.query_id}')
        print(f'digest={self.digest}')
        print(f'digest_text={self.digest_text}')
        print(f'time_ms={self.time_ms}')
        print(f'cpu_usage={self.cpu_usage}')
        print(f'io={self.io}')
        print(f'count={self.count}')
    
    def sort_timestamp(self):
        self.value = list(map(lambda x: [x[0], float(x[1]), float(x[2]), int(x[3]), int(x[4])], self.value))
        self.value = sorted(self.value, key=lambda x:x[0])
        for v in self.value:
            #print(v)
            self.time_ms.append(v[1]) 
            self.cpu_usage.append(v[2])
            self.timestamp.append(v[0])
            self.count.append(v[4])
            self.io.append(v[3])

    def add_missing_value(self, all_timestamp):
        new_time_ms = []
        new_cpu_usage = []
        new_count = []
        new_io = []
        for time in all_timestamp:
            if time in self.timestamp: #b에서 val의 index
                
                new_time_ms.append(self.time_ms[self.timestamp.index(time)])
                new_cpu_usage.append(self.cpu_usage[self.timestamp.index(time)])
                new_count.append(self.count[self.timestamp.index(time)])
                new_io.append(self.io[self.timestamp.index(time)])
            else:
                new_time_ms.append(0)
                new_cpu_usage.append(0)
                new_count.append(0)
                new_io.append(0)
        #print(len(all_timestamp), len(new_time_ms), len(new_cpu_usage))
        self.time_ms = new_time_ms
        self.cpu_usage = new_cpu_usage
        self.count = new_count
        self.io = new_io
        
        self.timestamp = copy.deepcopy(all_timestamp)

    
    def merge(self, other_query): #other query가 반드시 더 새로 수집된 데이터로부터 구한 거라고 가정!!
        self.time_ms += other_query.time_ms
        self.cpu_usage += other_query.cpu_usage
        self.io += other_query.io
        self.count += other_query.count
        self.timestamp += other_query.timestamp
        
def update_data_mysql(dic, metrics,all_timestamp, last_import_timestamp, query_num, col):
    new_dic = {}
    new_timestamp =[]
    path = get_path()
    file_list = os.listdir(path)
    
    min_datetime = dt.datetime.now()

    count = 0
    for filename in file_list:
        file_datetime = dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
        if file_datetime <=last_import_timestamp:
            continue
        else:
            count+=1
            if count%10 ==0:
                print(file_datetime)
            if min_datetime > file_datetime:
                min_datetime = file_datetime
        with open(os.path.join(path, filename), 'r') as f:
            # 같은 파일 내를 탐색
            new_timestamp.append(file_datetime)
            text = json.load(f)
            metrics = import_metrics_mysql(metrics, text, file_datetime, col)
            #io = text['metrics_data']["global"]["engine"]["innodb_status_io"]
            performance_schema = text['metrics_data']['global']['performance_schema']

            threads = performance_schema['threads']       
            tid_dic = {i[0]['thread_id']:i[0]['thread_os_id'] for i in threads}
            cpu_usage = performance_schema['cpu_usage'] # thread_os_id : cpu_usage
            io = performance_schema['io'] 
            events_statements_history = performance_schema['events_statements_history'] # list of dic
            digest_list = []
            for event in events_statements_history:
                digest = event['digest']
                if digest is None:
                    continue
                #print(category(digest))
                thread_id = event['thread_id']
                digest_text = event['digest_text']
                count = event['count']
                time = event['time_ms']
                if digest in digest_list: # 같은 쿼리가 같은 시간대에 이미 존재할 경우? time만 합친다.
                    new_dic[digest].add_time(time)
                elif digest in new_dic.keys():
                    if str(tid_dic[thread_id]) in io.keys():
                        #io key에는 있는데 cpu key에는 없을때 ??????? 없을 수도 있음 그러면 0으로 때리자
                        if str(tid_dic[thread_id])  not in cpu_usage.keys():
                            new_dic[digest].add_timestamp(time, 0, io[str(tid_dic[thread_id])], count, file_datetime)
                        else:
                            new_dic[digest].add_timestamp(time, cpu_usage[str(tid_dic[thread_id])], io[str(tid_dic[thread_id])], count, file_datetime)
                    else:
                        if str(tid_dic[thread_id])  not in cpu_usage.keys():
                            new_dic[digest].add_timestamp(time, 0, 0, count, file_datetime)
                        else:
                            new_dic[digest].add_timestamp(time, cpu_usage[str(tid_dic[thread_id])], 0, count, file_datetime)
                else:
                    if str(tid_dic[thread_id]) in io.keys():
                        if str(tid_dic[thread_id]) not in cpu_usage:
                            temp = digest_query(query_num, digest, digest_text, time, 0, io[str(tid_dic[thread_id])], count, file_datetime)
                        else:
                            temp = digest_query(query_num, digest, digest_text, time, cpu_usage[str(tid_dic[thread_id])], io[str(tid_dic[thread_id])], count, file_datetime)
                    else:
                        if str(tid_dic[thread_id]) not in cpu_usage:
                            temp = digest_query(query_num, digest, digest_text, time, 0, 0, count, file_datetime)
                        else:
                            temp = digest_query(query_num, digest, digest_text, time, cpu_usage[str(tid_dic[thread_id])], 0, count, file_datetime)
                    #key error 발생
                    new_dic[digest] = temp
                    query_num+=1

                digest_list.append(digest)
    new_timestamp.sort()
    for query in new_dic:
        query_id = new_dic[query].query_id
        new_dic[query].sort_timestamp()
    #print(len(digest_list))
    
    add_digest_list = copy.deepcopy(digest_list)
    
    for new_query in digest_list: # 새로 추가된 digest = 즉, dict의 key, merge 할때마다 list에서 제거할것
        if new_query in dic.keys():
            dic[new_query].merge(new_dic[new_query])
            add_digest_list.remove(new_query)
    
    #print(len(digest_list))
    for new_digest in add_digest_list:
        dic[new_digest] = new_dic[new_digest]
    #print("all_timestamp before add",len(all_timestamp))
    all_timestamp+=new_timestamp
    #print("all_timestamp aft add",len(all_timestamp))
    for query in dic:
        dic[query].add_missing_value(all_timestamp)
        #print(len(dic[query].time_ms))
    print("MINDT : ",min_datetime)
    return dic, metrics, all_timestamp, query_num

def update_data_pg(dic, metrics,all_timestamp, last_import_timestamp, query_num, col):
    new_dic = {}
    new_timestamp =[]
    path = get_path()
    file_list = os.listdir(path)
    
    min_datetime = dt.datetime.now()

    count = 0
    for filename in file_list:
        file_datetime = dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
        if file_datetime <=last_import_timestamp:
            continue
        else:
            count+=1
            if count%10 ==0:
                print(file_datetime)
            if min_datetime > file_datetime:
                min_datetime = file_datetime
        with open(os.path.join(path, filename), 'r') as f:
            # 같은 파일 내를 탐색
            new_timestamp.append(file_datetime)
            text = json.load(f)
            metrics = import_metrics_pg(metrics, text, file_datetime, col)
            statements = json.loads(text["metrics_data"]['global']['pg_stat_statements']['statements'])

            digest_list = []
            for event in statements:
                digest = event['queryid']
                if digest is None:
                    continue
                #print(category(digest))
                #thread_id = event['thread_id']
                digest_text = event['query']
                count = event['calls']
                time = event['time_ms']
                io = event['io']
                
                if digest in digest_list: # 같은 쿼리가 같은 시간대에 이미 존재할 경우? time만 합친다.
                    new_dic[digest].add_time(time)
                elif digest in new_dic.keys():
                    new_dic[digest].add_timestamp(time, 0, io, count, file_datetime)
                elif digest not in new_dic.keys():
                    new_dic[digest] = digest_query(query_num, digest, digest_text, time, 0, io, count, file_datetime)
                    #dic[digest] = temp
                    query_num+=1
                digest_list.append(digest)                
    new_timestamp.sort()
    for query in new_dic:
        query_id = new_dic[query].query_id
        new_dic[query].sort_timestamp()
    #print(len(digest_list))
    
    add_digest_list = copy.deepcopy(digest_list)
    
    for new_query in digest_list: # 새로 추가된 digest = 즉, dict의 key, merge 할때마다 list에서 제거할것
        if new_query in dic.keys():
            dic[new_query].merge(new_dic[new_query])
            add_digest_list.remove(new_query)
    
    #print(len(digest_list))
    for new_digest in add_digest_list:
        dic[new_digest] = new_dic[new_digest]
    #print("all_timestamp before add",len(all_timestamp))
    all_timestamp+=new_timestamp
    #print("all_timestamp aft add",len(all_timestamp))
    for query in dic:
        dic[query].add_missing_value(all_timestamp)
        #print(len(dic[query].time_ms))
    print("MINDT : ",min_datetime)
    return dic, metrics, all_timestamp, query_num
    



def Average(lst):
        return sum(lst) / len(lst)    


def import_data_pg(time_range=dt.timedelta(hours=4)):
    realtime = False # for debugging
    dic = {}
    path = get_path()
    query_num = 0
    all_timestamp =[]
    file_list = os.listdir(path)#[:10] # for debug
    max_datetime = dt.datetime.min
    
    #col = []
    col = get_column_pg()
    print(col)
    metrics = create_dataframe(col)
    #metrics = {}
    count = 0
    #print(col)
    
    for filename in file_list:
        file_datetime = dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
        if realtime == True and file_datetime <= dt.datetime.now() - time_range:
            print(file_datetime)
            if max_datetime < file_datetime:
                max_datetime = file_datetime
            continue
        else:
            print("imported")
            count+=1
            if count%10 ==0:
                print(file_datetime)
            print(file_datetime)
            if max_datetime < file_datetime:
                max_datetime = file_datetime
        with open(os.path.join(path, filename), 'r') as f:
            # 같은 파일 내를 탐색
            all_timestamp.append(file_datetime)
            text = json.load(f)
        metrics = import_metrics_pg(metrics, text, file_datetime, col)
        statements = json.loads(text["metrics_data"]['global']['pg_stat_statements']['statements'])
        digest_list = []
        for event in statements:
            digest = event['queryid']
            if digest is None:
                continue
            #thread_id = event['thread_id']
            digest_text = event['query']
            count = event['calls']
            time = event['time_ms']
            io = event['io']
            
            if digest in digest_list: # 같은 쿼리가 같은 시간대에 이미 존재할 경우? time만 합친다.
                dic[digest].add_time(time)
            elif digest in dic.keys():
                dic[digest].add_timestamp(time, 0, io, count, file_datetime)
            elif digest not in dic.keys():
                dic[digest] = digest_query(query_num, digest, digest_text, time, 0, io, count, file_datetime)
                #dic[digest] = temp
                query_num+=1
            digest_list.append(digest)
    all_timestamp.sort()
    print("MAXDT : ",max_datetime)
    
    for query in dic:
        query_id = dic[query].query_id
        dic[query].sort_timestamp()
        dic[query].add_missing_value(all_timestamp)
    return dic, metrics, all_timestamp, query_num, col


def import_data_mysql(time_range=dt.timedelta(hours=1)):
    realtime = False # for debugging
    dic = {}
    path = get_path()
    query_num = 0
    all_timestamp =[]
    file_list = os.listdir(path)#[:10] # for debug
    max_datetime = dt.datetime.min
    
    col = get_column_mysql()
    metrics = create_dataframe(col)
    count = 0
    #print(col)
    
    for filename in file_list:
        file_datetime = dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
        if realtime == True and file_datetime <= dt.datetime.now() - time_range:
            print(file_datetime)
            if max_datetime < file_datetime:
                max_datetime = file_datetime
            continue
        else:
            print("imported")
            count+=1
            if count%10 ==0:
                print(file_datetime)
            print(file_datetime)
            if max_datetime < file_datetime:
                max_datetime = file_datetime
        with open(os.path.join(path, filename), 'r') as f:
            # 같은 파일 내를 탐색
            all_timestamp.append(file_datetime)
            text = json.load(f)
        metrics = import_metrics_mysql(metrics, text, file_datetime, col)
        #print(metrics)
        #io = text['metrics_data']["global"]["engine"]["innodb_status_io"]
        performance_schema = text['metrics_data']['global']['performance_schema']
        threads = performance_schema['threads']       
        tid_dic = {i[0]['thread_id']:i[0]['thread_os_id'] for i in threads}
        cpu_usage = performance_schema['cpu_usage'] # thread_os_id : cpu_usage
        io = performance_schema['io'] 
        events_statements_history = performance_schema['events_statements_history'] # list of dic
        digest_list = []
        for event in events_statements_history:
            digest = event['digest']
            if digest is None:
                continue
            thread_id = event['thread_id']
            digest_text = event['digest_text']
            count = event['count']
            time = event['time_ms']
            if thread_id not in tid_dic:
                print(f'{thread_id} is not in tid_dic')
                continue
            if digest in digest_list: # 같은 쿼리가 같은 시간대에 이미 존재할 경우? time만 합친다.
                dic[digest].add_time(time)
            elif digest in dic.keys():
                if str(tid_dic[thread_id]) in io.keys():
                    #io key에는 있는데 cpu key에는 없을때 ??????? 없을 수도 있음 그러면 0으로 때리자
                    if str(tid_dic[thread_id])  not in cpu_usage.keys():
                        dic[digest].add_timestamp(time, 0, io[str(tid_dic[thread_id])], count, file_datetime)
                    else:
                        dic[digest].add_timestamp(time, cpu_usage[str(tid_dic[thread_id])], io[str(tid_dic[thread_id])], count, file_datetime)
                else:
                    if str(tid_dic[thread_id])  not in cpu_usage.keys():
                        dic[digest].add_timestamp(time, 0, 0, count, file_datetime)
                    else:
                        dic[digest].add_timestamp(time, cpu_usage[str(tid_dic[thread_id])], 0, count, file_datetime)
            else:
                if str(tid_dic[thread_id]) in io.keys():
                    if str(tid_dic[thread_id]) not in cpu_usage:
                        temp = digest_query(query_num, digest, digest_text, time, 0, io[str(tid_dic[thread_id])], count, file_datetime)
                    else:
                        temp = digest_query(query_num, digest, digest_text, time, cpu_usage[str(tid_dic[thread_id])], io[str(tid_dic[thread_id])], count, file_datetime)
                else:
                    if str(tid_dic[thread_id]) not in cpu_usage:
                        temp = digest_query(query_num, digest, digest_text, time, 0, 0, count, file_datetime)
                    else:
                        temp = digest_query(query_num, digest, digest_text, time, cpu_usage[str(tid_dic[thread_id])], 0, count, file_datetime)
                #key error 발생
                dic[digest] = temp
                query_num+=1
            digest_list.append(digest)
    all_timestamp.sort()
    
    print("MAXDT : ",max_datetime)
    
    for query in dic:
        query_id = dic[query].query_id
        dic[query].sort_timestamp()
        dic[query].add_missing_value(all_timestamp)
    return dic, metrics, all_timestamp, query_num, col

def rank(dic, category, num, time_range):
    
    rank_list = []
    dic_by_id={}
    for query in dic:
        query_id = dic[query].query_id
        dic_by_id[query_id] = dic[query]
        i=0
        for i, t in enumerate(dic[query].timestamp):
            if t > dic[query].timestamp[-1] - time_range:
                #print(i)
                break
        rank_list.append((dic[query].query_id, Average(dic[query].time_ms[i:]), Average(dic[query].cpu_usage[i:]), Average(dic[query].io[i:]), Average(dic[query].count[i:])))
    
    if category == 'CPU':
        top = sorted(rank_list, key=lambda x:-x[2])[:num]
        print(top)
    elif category == 'Duration':
        top = sorted(rank_list, key=lambda x:-x[1])[:num]
    elif category == 'Disk IO':
        top = sorted(rank_list, key=lambda x:-x[3])[:num]
    elif category == 'Execution Count':
        top = sorted(rank_list, key=lambda x:-x[4])[:num]
    top_qid = [i[0] for i in top]
    return top_qid


def import_and_update_data():
    with open('connect_config.json') as json_file:
        driver_config = json.load(json_file)
    db_type = driver_config['db_type']
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)
    realtime = False
    global dic, metrics, all_timestamp, query_num, col, last_import_time
    all_timestamp =[]
    dic={}
    

    if os.path.isfile('data.pickle'):
        with open('data.pickle','rb') as fr:
            dic, metrics, all_timestamp, query_num, col, last_import_time = pickle.load(fr)
        print("Loaded Data from Pickle")
        if realtime:
            if db_type =='postgres':
                dic, metrics, all_timestamp, query_num = update_data_pg(dic, metrics,all_timestamp,last_import_time, query_num, col)
            
            elif db_type =='mysql':
                dic, metrics, all_timestamp, query_num = update_data_mysql(dic, metrics,all_timestamp,last_import_time, query_num, col)
            else:
                NotImplementedError

        last_import_time = dt.datetime.now()
        print(last_import_time)
        pickle_list = [dic, metrics, all_timestamp, query_num, col, last_import_time]
        with open('data.pickle','wb') as fw:
            pickle.dump(pickle_list,fw)
        print("Data Update Complete!")
        #return dic, metrics, all_timestamp, query_num, last_import_time
    else:
        if db_type == 'postgres':
            dic, metrics, all_timestamp, query_num, col = import_data_pg()
        elif db_type == 'mysql':
            dic, metrics, all_timestamp, query_num, col = import_data_mysql()
        
        last_import_time = dt.datetime.now()
        print(last_import_time)
        print("Data Loading from json Complete!")
        pickle_list = [dic, metrics, all_timestamp, query_num, col, last_import_time]
        with open('data.pickle','wb') as fw:
            pickle.dump(pickle_list,fw)
        print("Saved Data into Pickle")
        #return dic, metrics, all_timestamp, query_num, last_import_time


def resample(inp_array,window_size,how='avg'):
    inp_array = np.asarray(inp_array)
    #print(inp_array)
    #check how many zeros need to be added to the end to make
    #   the array length a multiple of window_size 
    pad = (window_size-(inp_array.size % window_size)) % window_size
    if pad > 0:
        inp_array = np.r_[np.ndarray.flatten(inp_array),np.zeros(pad)]
    else:
        inp_array = np.ndarray.flatten(inp_array)

    #reshape so that the number of columns = window_size
    inp_windows = inp_array.reshape((inp_array.size//window_size,window_size))

    if how == 'max':
       #sum across columns
       return np.max(inp_windows,axis=1)
    elif how == 'avg':
        return np.average(inp_windows,axis=1)
    elif how == 'min':
        return np.min(inp_windows,axis=1)
    else:
        raise NotImplementedError #replace this with other how's you want
#cpu_top_qid = rank(dic, 'CPU', num)

def x_pad(x, window_size):
    x_pad_size = (window_size-(len(x) % window_size)) % window_size
    if x_pad_size >0:
        for i in range(x_pad_size):
            x.append(dt.datetime.now())
    return x


def visualize_multiple_chart_type(category, num, time_range, chart_type, m_agg='avg', col = []):
    global dic, all_timestamp, last_import_time, query_num, metrics
    #print(dic)
    #print(all_timestamp)
    
    ts = [i for i in all_timestamp if i > all_timestamp[-1]-time_range]

    window_size = int(len(ts)/15)
    #print(window_size)
    if window_size ==0:
        window_size = int(len(ts)/5)
        if window_size == 0:
            window_size = 1
    
    def update_prop(handle, orig):
            handle.update_from(orig)
            x,y = handle.get_data()
            handle.set_data([np.mean(x)]*2, [0, 2*y[0]])
    realtime =False # for debugging        
    if realtime:
        if dt.datetime.now()-last_import_time > dt.timedelta(minutes=10):
            with open('connect_config.json') as json_file:
                driver_config = json.load(json_file)
            db_type = driver_config['db_type']
            if db_type =='postgres':
                dic, metrics, all_timestamp, query_num = update_data_pg(dic, metrics,all_timestamp,last_import_time, query_num, col)
        
            elif db_type =='mysql':
                dic, metrics, all_timestamp, query_num = update_data_mysql(dic, metrics,all_timestamp,last_import_time, query_num, col)
            
            else:
                NotImplementedError
            last_import_time = dt.datetime.now()
            print(last_import_time)
            pickle_list = [dic, metrics, all_timestamp, query_num, col, last_import_time]
            with open('data.pickle','wb') as fw:
                pickle.dump(pickle_list,fw)
            print("Data Update Complete!")

    if category == 'CPU':
        figure_num = 1
    elif category == 'Duration':
        figure_num = 2
    elif category == 'Disk IO':
        figure_num = 3
    elif category == 'Execution Count':
        figure_num = 4

    fig = plt.figure(figure_num)
    plt.close(figure_num)    
    bottom = []
    
    top_qid = rank(dic, category, num, time_range)
    #print(top_qid)
    plt.clf()
    for query in dic:
        if dic[query].query_id in top_qid:

            if category == 'CPU':
                y = np.array(dic[query].cpu_usage, dtype=np.float64)
                print(dic[query].cpu_usage)
            elif category == 'Duration':
                y = np.array(dic[query].time_ms, dtype=np.float64)
            elif category == 'Disk IO':
                y = np.array(dic[query].io, dtype=np.float64)
            elif category == 'Execution Count':
                y = np.array(dic[query].count, dtype=np.float64)
            else:
                print("?")
            x = ts
            y = y[len(y)-len(ts):]
            if chart_type != 'bar':
                mask = (y != 0)
                x = [i for indx,i in enumerate(x) if mask[indx] == True]
            y = y[y!=0]
            x = x_pad(x, window_size)
            
            x = x[::window_size]
            y = resample(y, window_size, how=m_agg) # Rollup, Aggregate

            assert len(x) == len(y)
            if chart_type == 'bar':
                if len(bottom)==0:
                    bottom = np.zeros(len(x))
                width = np.min(np.diff(mdates.date2num(x)))
                plt.bar(x, height = y, width = 0.8*width, ec='k' ,label=str(dic[query].query_id) + " "+ dic[query].digest_text[:20], bottom = bottom)
                bottom += y
                
            elif chart_type == 'line':
                plt.plot_date(x, y, xdate = True, ms=0,  ls = '-',label=str(dic[query].query_id) + " "+ dic[query].digest_text[:20])
            

    plt.legend(title = "Query ID + Text", loc=6, bbox_to_anchor=(1, 0.5),handler_map={plt.Line2D:HandlerLine2D(update_func=update_prop)})
    
    if category == 'CPU':
        plt.title(f"CPU usage per query\nfor queries with top {num} CPU usage", size=20, fontweight="bold")
    elif category == 'Duration':
        plt.title(f"Query latency\nfor top {num} slowest queries", size=20, fontweight="bold")
    elif category == 'Disk IO':
        plt.title(f"Disk IO per query\nfor queries with top {num} Disk IO", size=20, fontweight="bold")
    elif category == 'Execution Count':
        plt.title(f"Execution Count for queries\nwith top {num} execution count", size=20, fontweight="bold")


    plt.xlim(x[-1]-time_range,x[-1])
    plt.gcf().autofmt_xdate()
    plt.grid(True, axis='y')
    plt.tight_layout()
    if chart_type =='bar':
        def show_annotation(sel):
            if type(sel.artist) == BarContainer:
                bar = sel.artist[sel.target.index]
                sel.annotation.set_text(f'{sel.artist.get_label()}: {bar.get_height():.1f}')
                sel.annotation.xy = (bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2)
                sel.annotation.get_bbox_patch().set_alpha(0.8)
        cursor = mplcursors.cursor(plt.gcf(), highlight=True, hover = True) 
        cursor.connect('add', show_annotation)        
    else:
        mplcursors.cursor(plt.gcf(), highlight=True, hover = True)  
    plt.show()
    print_raw_data(dic, category, time_range, top_qid)

from matplotlib.widgets import MultiCursor

line = HTML('<hr>')

def print_raw_data_category(category, time_range = dt.timedelta(hours = 1), num = 5):
    global dic, all_timestamp
    top_qid = rank(dic, category, num, time_range)
    data = []
    for query in dic:
        qid = dic[query].query_id
        i=0
        for i, t in enumerate(dic[query].timestamp):
            if t > dic[query].timestamp[-1] - time_range:
                break
    
        if qid in top_qid:
            item = [qid, dic[query].digest_text]
            if category == 'CPU':
                item.append(Average(dic[query].cpu_usage[i:]))
            elif category == 'Duration':
                item.append(Average(dic[query].time_ms[i:]))
            elif category == 'Disk IO':
                item.append(Average(dic[query].io[i:]))
            elif category == 'Execution Count':
                item.append(Average(dic[query].count[i:]))
            data.append(item)
            #data.append([qid, dic[query].digest_text, Average(dic[query].cpu_usage[i:]),Average(dic[query].io[i:]),Average(dic[query].time_ms[i:]),Average(dic[query].count[i:])])

    columns = ['QID', 'Digest Text', category]      
    df = pd.DataFrame(data, columns = columns)
    df = df.set_index('QID')
    df = df.sort_values(by = [category], ascending = False)
    pd.set_option('max_colwidth', None)

    display(df)
    #display(HTML(df.to_html()))
    button_layout = Layout(width = '200px', height = '50px')
    button = Button(description="Visualize", layout = button_layout,
                    style = dict(button_color= 'BlanchedAlmond', font_weight = 'bold'))
    button2 = Button(description="Show Query Plan", layout = button_layout,
                style = dict(button_color= 'BlanchedAlmond', font_weight = 'bold'))
    def print_query_detail(clicked_button):
        dropdown = widgets.Select(
                            options=df.index,
                            description='Select QID',
                            disabled=False,
                            layout={'height':'100px', 'width':'40%'})
        def filter_dataframe(widget):
            global filtered_df
            selection = widget['new'] 
            
            with out:
                clear_output() 
                for digest in dic:
                    if dic[digest].query_id == selection:
                        q = dic[digest]
                        break
                x = q.timestamp
                
                plt.close()
                fig, axes = plt.subplots(nrows=4, sharex = True)
                axes[0].plot(x,q.cpu_usage, label = "cpu usage")

                axes[1].plot(x,q.io, label = 'disk io')
                width = np.min(np.diff(mdates.date2num(x)))
                    
                axes[2].bar(x,q.count, width = width, ec='k',label = 'execution count')
                axes[3].bar(x,q.time_ms,width = width, ec='k', label = 'execution time')
                axes[0].set_title("cpu usage")
                axes[1].set_title("disk io")
                axes[2].set_title('execution count')
                axes[3].set_title('execution time')
                # fig.legend(title = "Query ID + Text", loc=6, bbox_to_anchor=(1, 0.5))
                fig.suptitle(f"Details of query ID {selection}", size=20, fontweight="bold")
                plt.gca().xaxis_date()
                plt.xlim(x[-1]-time_range,x[-1])
                plt.gcf().autofmt_xdate()
                plt.grid(True, axis='y')
                plt.tight_layout()
                multi = MultiCursor(fig.canvas, [axes[0],axes[1],axes[2]], color='r', lw=1)
                cursor = mplcursors.cursor(plt.gcf(), hover = True)
                display(line)
                plt.show()
                def query_plan(clicked_button: widgets.Button) -> None:
                    style = """<style>
                    .box{
                        width : 80%;
                        border : 1px solid black;
                        height : ;
                    }
                    </style>"""
                    display(HTML(style))
                    head = HTML(value="<b><font size = 3> Full Query of Query ID {}".format(selection))
                    q.digest_text = q.digest_text.replace("FROM", " FROM")                    
                    head2 = HTML(value="<b><font size = 3> Query Plan of Query ID {}".format(selection))
                    print(q.digest_text)
                    # num_param = max([int(i.replace('$','')) for i in re.findall(r'\$[0-9]',q.digest_text)])
                    # # #res = q_('Explain '+q.digest_text+';')
                    # #q_wo_fetch(f"""PREPARE stmt(unknown) AS {q.digest_text};""")
                    # #q_wo_fetch("""SET plan_cache_mode = force_generic_plan;""")
                    # res = q_(f"""PREPARE stmt(unknown) AS {q.digest_text};
                    #             EXECUTE stmt({','.join(['NULL']*num_param)});
                    #             DEALLOCATE stmt;""")
                    # #q_wo_fetch("""""")
                    # res = [i[0] for i in res]
                    res = q_prepared(q.digest_text)
                    qp = widgets.HTML('<p style ="margin:10px 20px;"><pre>'+'\n'.join(res))
                    qp.add_class('box')

                    display(line, head)
                    display(HTML('<p style ="margin:10px 20px;">'+q.digest_text).add_class('box'))
                    display(head2, qp)

                    print("... visualize the explained query plan ...")
                    print("... need to integrate typescript code ...")
                    button_layout2 = Layout(width = '400px', height = '50px')
                    button3 = Button(description="""If Query Plan is Not the Problem,
                    
                                                    Database Monitoring""", layout = button_layout2,
                    style = dict(button_color= 'BlanchedAlmond', font_weight = 'bold'))
                    from scenario import db_monitoring
                    button3.on_click(db_monitoring)
                    display(button3)
                    

                
            button2.on_click(query_plan)
            display(button2)

                
               

        out = widgets.Output()
        dropdown.observe(filter_dataframe, names='value')
        display(dropdown)
        display(out)
        #display(button2)
        
    button.on_click(print_query_detail)
    display(button)
    



def print_raw_data(dic, category, time_range,top_qid):
    # category: 어떤 것에 대한 top query들인지
    #df = pd.DataFrame(columns=['QID','Digest Text','CPU usage','Disk IO','Duration(ms)','Execution Count'])
    data = []
    for query in dic:
        qid = dic[query].query_id
        i=0
        for i, t in enumerate(dic[query].timestamp):
            if t > dic[query].timestamp[-1] - time_range:
                break
    
        if qid in top_qid:
            data.append([qid, dic[query].digest_text, Average(dic[query].cpu_usage[i:]),Average(dic[query].io[i:]),Average(dic[query].time_ms[i:]),Average(dic[query].count[i:])])
                
    df = pd.DataFrame(data, columns = ['QID', 'Digest Text','CPU usage','Disk IO','Duration(ms)','Execution Count'])
    df = df.set_index('QID')
    #df = df.sort_values(by = [category], ascending = False)
    
    from IPython.display import display, HTML

    display(HTML(df.to_html()))
    dropdown = widgets.Select(
                        options=df.index,
                        description='Select QID',
                        disabled=False,
                        layout={'height':'100px', 'width':'40%'})
    def filter_dataframe(widget):
        global filtered_df
        selection = widget['new'] 
        
        with out:
            clear_output() 
            for digest in dic:
                if dic[digest].query_id == selection:
                    q = dic[digest]
                    break
            x = q.timestamp
            
            plt.close()
            fig, axes = plt.subplots(nrows=4, sharex = True)
            axes[0].plot(x,q.cpu_usage, label = "cpu usage")

            axes[1].plot(x,q.io, label = 'disk io')
            width = np.min(np.diff(mdates.date2num(x)))
                
            axes[2].bar(x,q.count, width = width, ec='k',label = 'execution count')
            axes[3].bar(x,q.time_ms,width = width, ec='k', label = 'execution time')
            axes[0].set_title("cpu usage")
            axes[0].set_ylim(min(q.cpu_usage)*0.9, max(q.cpu_usage)*1.1)
            axes[1].set_title("disk io")
            axes[1].set_ylim(min(q.io)*0.9, max(q.io)*1.1)
            axes[2].set_ylim(0, max(q.count)*1.1)
            axes[3].set_ylim(0, max(q.time_ms)*1.1)

            axes[2].set_title('execution count')
            axes[3].set_title('execution time')
            fig.legend(title = "Query ID + Text", loc=6, bbox_to_anchor=(1, 0.5))
            fig.suptitle(f"Details of query ID {selection}", size=20, fontweight="bold")
            plt.gca().xaxis_date()
            plt.xlim(x[-1]-time_range,x[-1])
            plt.gcf().autofmt_xdate()
            plt.grid(True, axis='y')
            plt.tight_layout()
            multi = MultiCursor(fig.canvas, [axes[0],axes[1],axes[2]], color='r', lw=1)
            cursor = mplcursors.cursor(plt.gcf(), hover = True)
            plt.draw()
            

    out = widgets.Output()
    dropdown.observe(filter_dataframe, names='value')
    display(dropdown)
    display(out)
    

def query_visualizer():
    style = {'description_width': 'initial'}
    layout = widgets.Layout(
                    align_items='center',
                    width= '80%',
    )

    w1 = widgets.Dropdown(
        options=['CPU', 'Disk IO', 'Duration', 'Execution Count'],
        value='Duration',
        style = style,
        layout = layout,
    )
    w2 = widgets.Dropdown(
        options=['Last 1 min', 'Last 5 min','Last 10 min','Last 1 hr', 'Last 6 hrs', 'Last 24 hrs', 'past week', 'past month', 'custom'],
        value='Last 10 min',
        style = style,
        layout = layout,
    )
    w3 = widgets.Dropdown(
        options=['5','10','15'],
        value='5',
        style = style,
        layout=Layout(flex='1 1 25%', align_items='center', width='80%'),
    )
    w4 = widgets.Dropdown(
        options=['line', 'area','bar'],
        value='line',
        style = style,
        layout = layout,
    )
    w5 = widgets.Dropdown(
        options=['avg','min','max'],
        value='avg',
        style = style,
        layout = layout,
    )

    button = widgets.Button(description='Draw', color = 'blue',
                            layout=Layout(flex='2 1 50%', align_items='center', width='80%'),)



    def on_click_callback(clicked_button: widgets.Button) -> None:
        """버튼이 눌렸을 때 동작하는 이벤트 핸들러"""
        plt.close(1)
        plt.close(2)
        plt.close(3)
        plt.close(4)
        num= int(w3.value)
        if w2.value == 'Last 1 min':
            time_range = dt.timedelta(minutes = 1)
        elif w2.value == 'Last 5 min':
            time_range = dt.timedelta(minutes = 5)
        elif w2.value == 'Last 10 min':
            time_range = dt.timedelta(minutes = 10)
        elif w2.value == 'Last 1 hr':
            time_range = dt.timedelta(hours = 1)
        elif w2.value == 'Last 6 hrs':
            time_range = dt.timedelta(hours = 6)
        elif w2.value == 'Last 24 hrs':
            time_range = dt.timedelta(hours = 24)
        clear_output(wait = True)
        display(HBox(widget_list))
        visualize_multiple_chart_type(w1.value, num, time_range, w4.value, w5.value, col)

    plt.figure(1) # CPU
    plt.figure(2) # Duration
    plt.figure(3) # Disk IO
    plt.figure(4) # Execution Count
    plt.close(1)
    plt.close(2)
    plt.close(3)
    plt.close(4)
    clear_output(wait = True)
    plt.rcParams['figure.figsize'] = [11, 6]
    plt.rcParams["date.autoformatter.minute"] = "%Y-%m-%d %H:%M:%S"
    plt.ion()


    lb1 = widgets.Label('Metrics category:')
    lb2 = widgets.Label('Time period:')
    lb3 = widgets.Label('# of queries:',layout=Layout(flex='1 1 25%', width='auto'))
    lb4 = widgets.Label('Chart type:')
    lb5 = widgets.Label('Metrics aggregation:')


    button.on_click(on_click_callback)
    h1 = VBox([lb1,w1,lb4, w4], layout = layout)
    h2 = VBox([lb2,w2,lb5, w5], layout = layout)
    h3 = VBox([lb3,w3, button], layout=widgets.Layout(flex_flow='column',align_items='center',
                    width= '80%',))
    widget_list = [h1,h2,h3]

    display(HBox(widget_list, layout=Layout( width='auto')))       


from matplotlib.dates import DateFormatter

def visualize_metrics():
    global metrics, all_timestamp, col
    if len(col) ==0:
        col = get_column_mysql()

    def visualize(category, selected_metrics):
        window_size = 30
        plt.close()
        plt.rcParams['figure.figsize'] = [11, 6]
        myFmt = DateFormatter("%Y-%m-%d %H:%M:%S")
        x = all_timestamp
        x = x[::window_size]
        
        if len(selected_metrics) == 1:
            fig, ax1 = plt.subplots()
            
            y = np.array(metrics[category][selected_metrics[0]], dtype=np.float32)
            y = resample(y, window_size) # Rollup, Aggregate
            ln1 = ax1.plot_date(x, y, 'g-', ms=0, label = selected_metrics[0])
            plt.gca().xaxis.set_major_formatter(myFmt)
            ax1.set_ylabel(selected_metrics[0], color='g',fontsize = 10)
            lines = ln1
        elif len(selected_metrics) == 2:
            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()
            y1 = np.array(metrics[category][selected_metrics[0]], dtype=np.float32)
            y1 = resample(y1, window_size)
            ln1 = ax1.plot_date(x, y1, 'g-', ms=0, label = selected_metrics[0])
            plt.gca().xaxis.set_major_formatter(myFmt)
            y2 = np.array(metrics[category][selected_metrics[1]], dtype=np.float32)
            y2 = resample(y2, window_size)
            ln2 = ax2.plot_date(x, y2, 'b-', ms=0, label = selected_metrics[1])
            plt.gca().xaxis.set_major_formatter(myFmt)
            ax1.set_ylabel(selected_metrics[0], color='g',fontsize = 10)
            ax2.set_ylabel(selected_metrics[1], color='b',fontsize = 10)
            lines = ln1+ln2
            
            
            
        else:
            min_metric = selected_metrics[0]
            min_value = max(metrics[category][min_metric].to_numpy(dtype=np.float32))
            max_metric = selected_metrics[0]
            max_value = max(metrics[category][max_metric].to_numpy(dtype=np.float32))
            
            for metric in selected_metrics: #min, max metric을 찾아서 축을 분리할 예정
               
                if max(metrics[category][metric].to_numpy(dtype=np.float32)) > max_value:
                    max_value = max(metrics[category][metric].to_numpy(dtype=np.float32))
                    max_metric = metric
                elif max(metrics[category][metric].to_numpy(dtype=np.float32)) < min_value:
                    min_value = max(metrics[category][metric].to_numpy(dtype=np.float32))
                    min_metric = metric
                        
            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()
            if min_metric == max_metric:
                min_metric = selected_metrics[0]
                min_value = max(metrics[category][min_metric].to_numpy(dtype=np.float32))
                max_metric = selected_metrics[1]
                max_value = max(metrics[category][max_metric].to_numpy(dtype=np.float32))
                
            y1 = np.array(metrics[category][min_metric], dtype=np.float32)
            y1 = resample(y1, window_size)
            ln1 = ax1.plot_date(x, y1, 'g-', ms=0, label = min_metric)
            plt.gca().xaxis.set_major_formatter(myFmt)
            y2 = np.array(metrics[category][max_metric], dtype=np.float32)
            y2 = resample(y2, window_size)
            ln2 = ax2.plot_date(x, y2, 'b-', ms=0, label = max_metric)
            plt.gca().xaxis.set_major_formatter(myFmt)
            ax1.set_ylabel(min_metric, color='g',fontsize = 10)
            ax2.set_ylabel(max_metric, color='b',fontsize = 10)
            lines = ln1+ln2
            
            
            selected_metrics.remove(min_metric)
            selected_metrics.remove(max_metric)
            
            
            for metric in selected_metrics:
                y = np.array(metrics[category][metric], dtype=np.float32)
                y = resample(y, window_size)
              
                if max(metrics[category][metric].to_numpy(dtype=np.float32)) > (min_value+max_value)/2:
                    line = ax2.plot_date(x, y,  ms=0,  ls = '-', label = metric)
                else:
                    line = ax1.plot_date(x, y,  ms=0,  ls = '-', label = metric)
                lines+=line
                plt.gca().xaxis.set_major_formatter(myFmt)
        
        labs = [l.get_label() for l in lines]        
        plt.legend(lines, labs, bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=3)
        plt.gcf().autofmt_xdate()
        plt.gcf().suptitle(f"Metrics Visualization", size=20, fontweight="bold")
        mplcursors.cursor(plt.gcf(), hover = True)   
        plt.grid(True, axis='y')
        plt.tight_layout()
        plt.show()
    options = list(col.keys())
    options.insert(0,"")
    dropdown = widgets.Select(
                            options=options,
                            description='Category:',
                            disabled=False,
                            layout={'height':'100px', 'width':'40%'})



    def filter_dataframe(widget):
        def on_click_callback(widget): # visualize metrics
            visualize(dropdown.value, list(dropdown2.value))
        selection = widget['new'] 
        button = widgets.Button(description='Click me')

        dropdown2 = widgets.SelectMultiple(options=col[selection], description='Metrics:', disabled=False,layout={'height':'100px', 'width':'40%'})
        hbox = HBox ([dropdown, dropdown2,button])
        clear_output()
        display(hbox)
        button.on_click(on_click_callback)


    out = widgets.Output()
    dropdown.observe(filter_dataframe, names='value')
    display(dropdown)

def get_metrics_info():
    global col
    result = {}
    for m in col.keys():
        if 'raw' in m:
            continue
        temp = []
        for c in col[m]:
            if c == 'timestamp':
                continue
            elif c in METRIC_DICT:
                temp.append(METRIC_DICT[c])
            else:
                temp.append(c)
        result[m] = temp
        
    result['options'] = ['None']
    return result

def get_metric_fig():
    global metrics, all_timestamp, col

def visualize_metrics_panel(selected_metrics, filter=None, split=None, type='line', timerange=[]):
    #selected_metrics = [m for (e,m) in selected_element if e == 'metric']
    
    print("filter",filter)
    print("split", split)

    column_dict = {'Database name':'datname',
                    'State':'state',
                    'Wait event type':'wait_event_type'}

    global metrics, all_timestamp, col
    ts = all_timestamp 
    
    df_copy = pd.DataFrame(index = ts)
    #print(df)
    fold = []
    for (metric, agg) in selected_metrics:
        if metric in METRIC_DICT.inverse:
            metric = METRIC_DICT.inverse[metric] # Convert
        for c in col.keys():
            if metric in col[c]:
                category = c
        df_temp = metrics[category].copy()
        df_temp.set_index('timestamp', inplace = True) # column에 없는 경우 발생
        if filter != None:
            print("filter???")
            df_temp = df_temp.loc[df_temp[column_dict[filter[0]]].isin(filter[2])]
        if split != None:
            df_copy = df_copy.join(df_temp[[column_dict[split[0]], metric]], how='outer')
        else:
            df_copy = df_copy.join(df_temp[metric], how='outer')#= df_temp[metric].copy()

    if split == None:
        df_copy = df_copy.groupby(level = 0).agg('mean')

    idx = [i for i in df_copy.index if i >= timerange[0] and i<= timerange[1]]
    df_copy = df_copy.loc[idx]

    
    df_summary = pd.DataFrame()
    for (metric, agg) in selected_metrics:    
        if metric in METRIC_DICT.inverse:
            metric = METRIC_DICT.inverse[metric] # Convert    
        if agg == 'Sum':
            df_summary[metric+'_'+agg] = df_copy[metric].resample('1T').sum()
        elif agg == 'Average':
            df_summary[metric+'_'+agg] = df_copy[metric].resample('1T').mean()
        elif agg == 'Min':
            df_summary[metric+'_'+agg] = df_copy[metric].resample('1T').min()
        elif agg == 'Max':
            df_summary[metric+'_'+agg] = df_copy[metric].resample('1T').max()
        fold.append(metric+'_'+agg)
        

    #display("summary", df_summary)
    #print(fold)
    df_summary.reset_index(inplace=True)

    #print(df_summary)
    chart = alt.Chart(df_summary).transform_fold(fold,)
    if type == 'line':
        chart = chart.mark_line()
    elif type == 'bar':
        chart = chart.mark_bar() # width 지정 필요
    elif type == 'area':
        chart = chart.mark_area()
    elif type == 'scatter':
        chart = chart.mark_circle()

    selection = alt.selection_multi(fields=['key'], bind='legend')
#opacity=alt.condition(selection, alt.value(1), alt.value(0.2))

    chart = chart.encode(
        x = alt.X('index:T', title = '',axis=alt.Axis(grid=False)),
        y = alt.Y('value:Q', title = '', axis=alt.Axis(grid=True)),
        
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=[
        alt.Tooltip('value:Q', title='Value'),
        alt.Tooltip('key:N', title='Metric'),
        alt.Tooltip('index:T', title='Timestamp')
        ]
        ).properties(width='container', height='container'
        ).interactive().configure_legend(orient='bottom',
        ).add_selection(selection)
    if split == None:
        chart = chart.encode(color=alt.Color('key:N', title = ''))
    else:
        if len(selected_metrics)==1:
            chart = chart.encode(color=alt.Color(column_dict[split[0]]+':N'))
        else:
            chart = chart.encode(color=alt.Color('key:N', title = ''),
                                shape=alt.Color(column_dict[split[0]]+':N'))


    return chart

def get_dat_names():
    global metrics
    return list(metrics["raw_database_metrics"].datname.dropna().unique())


def wait_visualizer():
    global metrics, all_timestamp, col
    wait = metrics['wait']
    wait = wait.drop(columns = 'idle')
    wait *= 0.000000001

    def visualize_wait():
        print("BE")
    
    w1 = widgets.Dropdown(
        options=['5','10','15'],
        value='5',
        description='# of queries:',
        
    )
    w2 = widgets.Dropdown(
        options=['Last 1 min', 'Last 5 min','Last 10 min','Last 1 hr', 'Last 6 hrs', 'Last 24 hrs', 'past week', 'past month', 'custom'],
        value='Last 10 min',
        #description='Time Period:',
    )
    w3 = widgets.Dropdown(
        options=['line', 'area','bar'],
        value='line',
        #description='Query aggregation:',
    )
    button = widgets.Button(description='Click me')
    def on_click_callback(widget): # visualize wait
        print(w1.value)#visualize_wait(w.value)
        
        if w2.value == 'Last 1 min':
            time_range = dt.timedelta(minutes = 1)
        elif w2.value == 'Last 5 min':
            time_range = dt.timedelta(minutes = 5)
        elif w2.value == 'Last 10 min':
            time_range = dt.timedelta(minutes = 10)
        elif w2.value == 'Last 1 hr':
            time_range = dt.timedelta(hours = 1)
        elif w2.value == 'Last 6 hrs':
            time_range = dt.timedelta(hours = 6)
        elif w2.value == 'Last 24 hrs':
            time_range = dt.timedelta(hours = 24)
        

        ts = [i for i in all_timestamp if i > all_timestamp[-1]-time_range]
        wait1 = wait.iloc[len(wait.index)-len(ts):]
        
        
        top_index = wait1.sum().sort_values(ascending=False)[:int(w1.value)].index
        
        wait_viz = wait1[top_index]
        wait_viz.index = ts
        
        wait_viz[::5].plot(grid = True, kind = w3.value, title = 'Wait Time Analysis', fontsize= 10, alpha = 0.5)
        plt.title( 'Wait Time Analysis', fontdict = {'weight':'bold','fontsize' : 25})
        clear_output()
        display(HBox([w1,w2,w3, button]))
    button.on_click(on_click_callback)
    display(HBox([w1,w2,w3, button]))

from knob_exploration import *

def change_knob(knob_name):
    knobs = get_knobs()
    knob = knobs[knob_name]
    w_layout = widgets.Layout(
                    align_items='center',
                    width= '80%')

    if knob[3] == 'integer':
        w = widgets.BoundedIntText(
                            value=knob[0],
                            min = knob[1],
                            max = knob[2],
                            disabled=False,
                            layout = w_layout)
    elif knob[3] == 'real':
        w = widgets.BoundedFloatText(
                            value=knob[0],
                            min = knob[1],
                            max = knob[2],
                            disabled=False,
                            layout = w_layout)
    button = Button(description='Set')
    def change(clicked_button):
        q_wo_fetch(f"ALTER SYSTEM SET {knob_name} = {w.value};")
        print(f"set [{knob_name}] to [{w.value}]")
    button.on_click(change)
    display(HBox([VBox([HTML(knob_name), w],layout = Layout(align_items='center')),button], layout = Layout (align_items = 'center')))
    
def read_performance_metric_viz():
    style = """<style>
        .box{
            width : 80%;
            border : 1px solid black;
            height : ;
        }
        </style>"""
    display(HTML(style))

    out1 = widgets.Output()
    out2 = widgets.Output()
    tab = widgets.Tab(children = [out1, out2])
    tab.set_title(0, 'Index scan')
    tab.set_title(1, 'Fetched row')
    #knobs = get_knobs()
    
    
    global metrics
    with out1:
        title = 'Sequential scans vs. index scans'
        visualize_selected_metrics(metrics['agg_user_tables_metrics'][['seq_scan', 'idx_scan']], title)
        display(HTML("""If you believe that the query planner is mistakenly preferring sequential scans over index scans, 
                    you can try tweaking the random_page_cost setting (the estimated cost of randomly accessing a page from disk).
                    lowering this value in proportion to seq_page_cost will encourage the planner to prefer index scans over sequential scans.""").add_class('box'))
        change_knob('random_page_cost')
        change_knob('seq_page_cost')
    with out2:
        title = 'Rows fetched vs. rows returned by queries to the database'
        visualize_selected_metrics(metrics['agg_database_metrics'][['tup_fetched', 'tup_returned']], title)
        display(HTML("""Ideally, the number of rows fetched should be close to the number of rows returned (read/scanned) on the database.
                        This indicates that the database is completing read queries efficiently—it is not scanning through many more rows than it needs to in order to satisfy read queries.
                        If PostgreSQL is scanning through more rows than it is fetching, it indicates that the data may not be properly indexed.
                        Creating indexes on frequently accessed columns can help improve this ratio. """).add_class('box'))
    
    display(tab)
    
def visualize_selected_metrics(df, title = '', scale = 'linear'):
    global all_timestamp
    df.index = all_timestamp
    df.plot()
    myFmt = DateFormatter("%Y-%m-%d %H:%M:%S")
    plt.gca().xaxis.set_major_formatter(myFmt)
    plt.yscale(scale)
    plt.title(title)
    plt.show()

def write_performance_metric_viz():
    style = """<style>
        .box{
            width : 80%;
            border : 1px solid black;
            height : ;
        }
        </style>"""
    display(HTML(style))

    out1 = widgets.Output()
    out2 = widgets.Output()
    out3 = widgets.Output()

    tab = widgets.Tab(children = [out1, out2, out3])
    tab.set_title(0, '# of Rows Written')
    tab.set_title(1, 'HOT update')
    tab.set_title(2, '# of Transactions')

    #knobs = get_knobs()
    
    
    global metrics
    with out1:
        title = 'Rows inserted/updated/deleted per DB'
        visualize_selected_metrics(metrics['agg_database_metrics'][['tup_inserted', 'tup_updated','tup_deleted']], title, 'log')
        display(HTML("""If you see a high rate of updated and deleted rows, 
                        you should also keep a close eye on the number of dead rows, 
                        since an increase in dead rows indicates a problem with VACUUM processes, 
                        which can slow down your queries. 
                        A sudden drop in throughput is concerning and could be due to issues like locks on tables and/or rows that need to be accessed in order to make updates""").add_class('box'))
        
        print("...to add lock-related monitoring...")
        # out1_nest = widgets.Output()
        # accordion = widgets.Accordion(children=[out1_nest])
        # with out1_nest:
        #     title = 'Rows inserted/updated/deleted per DB'
        #     visualize_selected_metrics(metrics['agg_database_metrics'][['tup_inserted', 'tup_updated','tup_deleted']], title, 'log')
        #     display(HTML("""If you see a high rate of updated and deleted rows, 
        #                     you should also keep a close eye on the number of dead rows, 
        #                     since an increase in dead rows indicates a problem with VACUUM processes, 
        #                     which can slow down your queries. 
        #                     A sudden drop in throughput is concerning and could be due to issues like locks on tables and/or rows that need to be accessed in order to make updates""").add_class('box'))
        #     print("...to add lock-related monitoring...")
            



    with out2:
        title = 'Heap Only Tuple update'
        visualize_selected_metrics(metrics['agg_user_tables_metrics'][['n_tup_hot_upd', 'n_tup_upd']], title)
        display(HTML("""PostgreSQL optimizes update through a Heap-Only Tuple (HOT) update. 
                    A HOT update is possible when the transaction does not change any columns that are currently indexed.
                    In comparison with normal updates, a HOT update introduces less I/O load on the database, 
                    since it can update the row without having to update its associated index. """).add_class('box'))
    
    with out3:
        title = 'Total number of transactions executed'
        metrics['agg_database_metrics']['total_transaction'] = metrics['agg_database_metrics']['xact_commit'] + metrics['agg_database_metrics']['xact_rollback']
        visualize_selected_metrics(metrics['agg_database_metrics'][['xact_commit', 'xact_rollback','total_transaction']], title)
        
    display(tab)

def resource_utilization_viz():
    global metrics

    style = """<style>
        .box{
            width : 80%;
            border : 1px solid black;
            height : ;
        }
        </style>"""
    display(HTML(style))

    tab1 = widgets.Tab()
    tab2 = widgets.Tab()
    tab3 = widgets.Tab()
    
    accordion = widgets.Accordion(children=[tab1,tab2,tab3])
    accordion.set_title(0, 'Connection')
    accordion.set_title(1, 'Shared buffer usage')
    accordion.set_title(2, 'Disk and index usage')

    out = [[widgets.Output() for _ in range(3)] for _ in range(3)]

    tab1.children = [out[0][0], out[0][1]]
    tab1.set_title(0, '# of active connections')
    tab1.set_title(1, '% connections in use')
    
    with out[0][0]:
        title = '# of active connections'
        visualize_selected_metrics(metrics['agg_database_metrics'][['numbackends']], title)
        
    
    #with out[0][1]:
        
    display(accordion)