import requests
from client_visualizer import * 


def connect_db(db_type='postgres', host='eda-client', database='test_cli', user='postgres', password='postgres', port='5432', interval ='10'):

    url = "http://eda:80/connect"
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

    url = "http://eda:80/collect"
    # config = {'db_type': db_type,
    #           'db_host': host,
    #           'db_name':database,
    #           'db_user':user,
    #           'db_password':password,
    #           'db_port':port,
    #           'interval':interval}

    response = requests.post(url, json=config)
    # Check the response status code
    if response.status_code == 200:
        print("Performance data is being collected.")
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    
    return config

def visualize(config):    
    url = "http://eda:80/"

    response = requests.get(url+"schema", params = config)
    # Check the response status code
    if response.status_code == 200:
        data = response.json() # sidebar_content, schema
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    schema = data['schema']
    #print(data['sidebar_content'])
    sidebar_content = pd.DataFrame(data['sidebar_content'])
    sidebar = get_sidebar(schema, sidebar_content)
    main = get_widgets(schema, config)
    display(pn.Row(sidebar, main))

def train(config:dict, data:pd.DataFrame, task:str, pipeline:str='lstm_dynamic_threshold', hyperparameters:dict={}):
    url = "http://eda:80/train"
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
    url = "http://eda:80/predict"
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
    if 'start' in df:
        df['start'] = pd.to_datetime(df['start'])
        df['end'] = pd.to_datetime(df['end'])
        return df
    else:
        print("no anomaly")
        return None
