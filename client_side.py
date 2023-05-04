import requests
from client_visualizer import * 
import json

def connect_db(db_type='postgres', host='eda-client', database='test_cli', user='postgres', password='postgres', port='5432', interval ='10'):

    url = "http://eda:80/config"
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

    

    
