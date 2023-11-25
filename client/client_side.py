import requests
import pandas as pd
from client_visualizer import * 

from config_utils import config
server_port = config.get('server')


def connect_db(db_type='postgres', host='dbeda-client', database='test_cli', user='postgres', password='postgres', port='5434', interval ='10'):

    url = f"http://localhost:{server_port}/connect"
    config = {'db_type': db_type,
              'db_host': host,
              'db_name':database,
              'db_user':user,
              'db_password':password,
              'db_port':port,
              'interval':interval}

    response = requests.post(url, json=config)
    # Check the response status code
    if response.status_code == 200:
        print("Configuration data sent successfully.")
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    
    return config

def collect_performance_data(config):

    url = f"http://localhost:{server_port}/collect"

    response = requests.post(url, json=config)
    # Check the response status code
    if response.status_code == 200:
        print("Performance data is being collected.")
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    
    return config

def visualize(config):    
    url = f"http://localhost:{server_port}/"

    response = requests.get(url+"schema", params = config)
    # Check the response status code
    if response.status_code == 200:
        data = response.json() # sidebar_content, schema
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    import time
    schema = data['schema']
    sidebar_content = pd.DataFrame(data['sidebar_content'])
    sidebar = get_sidebar(schema, sidebar_content) # 오래걸림
    main = get_widgets(schema, config)
    display(pn.Row(sidebar, main))


def get_trained_model(config:dict, task:str='anomaly analysis'):
    url = f"http://localhost:{server_port}/trained_model"
    params = {
        'task':task,
        #'config':config
        }
    response = requests.get(url, params ={'params': json.dumps(params)})
    
    # Check the response status code
    if response.status_code == 200:
        data = response.json() # sidebar_content, schema
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")

    print(data)


def train(config:dict, data:pd.DataFrame=pd.DataFrame(), task:str='anomaly detection', pipeline:str='lstm_dynamic_threshold', hyperparameters:dict={}):
    url = f"http://localhost:{server_port}/train"
    data_post = {
        'data':data.to_json(orient='records'),
        'task':task,
        'pipeline':pipeline,
        'hyperparameters':hyperparameters,
        'config':config,
    }


    # POST 요청 보내기
    response = requests.post(url, json=data_post)
    print(response)
    # Check the response status code
    if response.status_code != 200:
        print(f"Error sending configuration data. Status code: {response.status_code}")
        raise NotImplementedError(response.status_code)
    else:
        return response

def predict(config:dict, data:pd.DataFrame, task:str, path:str):
    url = f"http://localhost:{server_port}/predict"
    data_post = {
        'data':data.to_json(orient='records'),
        'task':task,
        'path':path,
        'config':config,
    }

    # POST 요청 보내기
    response = requests.post(url, json=data_post)
    data = pickle.loads(response.content)
    df = pd.DataFrame(data)
    
    return df