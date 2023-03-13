# from performance_analysis import *
from influxdb import InfluxDBClient
import pandas as pd
import panel as pn
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
import datetime as dt
from functools import partial

from IPython.display import display, clear_output

css = '''
    .bk.row {
      display: flex !;
      
    }

    .bk.row > * {
      flex: 1;
    }

    .bk.row > :first-child {
      flex-basis: 20%;
    }

    .bk.row > :nth-child(n+2) {
      flex-basis: 80%;
    }

    .bk .side {
        flex: 1 1 0;
    }


    .bk .main {
        flex: 5 1 0;
    }
    .bk .card-button{
        color: transparent;
    }
    .bk.bk-clearfix{
        font-weight: normal;
        text-align: left;
        font-size: 16px !important;
        background: transparent;
    }
    .bk.accordion button.bk.accordion-header{
        background: white;
        
    }
    .bk.accordion{
        border: 0px;
    }
    '''
pn.extension('tabulator',sizing_mode = 'stretch_width', css_files=[pn.io.resources.CSS_URLS['font-awesome']], raw_css = [css])

def connect(dbtype = 'posgres', host = 'localhost', port = '5432', dbname = 'eda', user = 'username', password = None):
    NotImplemented
    # schema, metrics = import_data_influx()
    client = InfluxDBClient(host='localhost', port=8086)

    # Switch to a specific database
    client.switch_database('eda')
    return client

def collect(connector, metrics=None):
    dic = {}
    query_num = 0
    schema = {}
    
    # Get all measurements
    result = connector.get_list_measurements()
    measurements = [m['name'] for m in result]
    now = dt.datetime.now()
    try:
        metrics
#        dt.datetime.strptime(filename,'%Y%m%d_%H%M%S') 
        for measurement in measurements:
            query = f"SELECT * FROM {measurement} WHERE time > '{last_import_time.strftime('%Y-%m-%dT%H:%M:%SZ')}'"
            
            result = connector.query(query)#, bind_params = bind_params)
            metrics[measurement] = pd.concat([metrics[measurement], pd.DataFrame(list(result.get_points()))])   
            metrics[measurement]['time'] = pd.to_datetime(metrics[measurement]['time'])
            col[measurement] = list(metrics[measurement].columns)
            col[measurement].remove('time')
        print('update complete')
        print(f'time: {dt.datetime.now()-now}') 
    except NameError:
        metrics = {}
        col = {}
        for measurement in measurements:
            schema[measurement] = {}
            #Get the measurement's structure
            query = f'SHOW TAG KEYS FROM {measurement}'
            tags_result = connector.query(query)
            tags = [tag['tagKey'] for tag in tags_result.get_points()]
            
            #query = f'SHOW FIELD KEYS FROM {measurement}'
            fields_result = connector.query(query)
            fields = [field['fieldKey'] for field in fields_result.get_points()]
            query = f'SELECT * FROM {measurement}'
            result = connector.query(query)
            metrics[measurement] = pd.DataFrame(list(result.get_points()))
            metrics[measurement]['time'] = pd.to_datetime(metrics[measurement]['time'])

            col[measurement] = list(metrics[measurement].columns)
            col[measurement].remove('time')
        print('import complete') 
        print(f'time: {dt.datetime.now()-now}') # 4000 건 2초
    last_import_time = metrics[measurement]['time'].max()
    all_timestamp = list(metrics[measurement]['time'])

    return metrics

def show_schema(connector=None, metrics=None):
    # Get all measurements
    result = connector.get_list_measurements()
    measurements = [m['name'] for m in result]
    #print(measurements)
    schema = {}
    df_widgets = []

    bokeh_formatters = {
        #'float': NumberFormatter(format='0.00000'),
        'key': BooleanFormatter(icon = 'check-circle-o'),
    }

    for measurement in measurements:
        schema[measurement] = {}

        query = f"SHOW FIELD KEYS from {measurement}"   
        result = connector.query(query)
        res_field = pd.DataFrame(list(result.get_points()))
        res_field.columns = ['column','type']
        res_field['key'] = False
         
        query = f"SHOW TAG KEYS from {measurement}"   
        result = connector.query(query)
        res_tag = pd.DataFrame(list(result.get_points()))
        if len(res_tag)>0:
            res_tag.columns = ['column']
            res_tag['type'] = 'string'
            res_tag['key'] = True
        df = pd.concat([res_field, res_tag], axis = 0)
        table = pn.widgets.Tabulator(df,name = "<i class='fa fa-table'></i> "+ measurement.replace("_"," ").capitalize(),show_index=False, formatters = bokeh_formatters)
        #, buttons={'Search': "<i class='fa fa-search'></i>"}
        #button = pn.widgets.Button(name='Load Table', button_type='primary')
        #button.message = measurement
        #button.on_click(partial(load_table, conn = connector, measurement = measurement))
        #table.on_click(partial(show_table, conn = connector, measurement = measurement))
        df_widgets.append(pn.Column(table))#,button))

    accordion = pn.Accordion(*df_widgets, sizing_mode = 'stretch_width' )
    
    display(pn.Column(accordion))


def load_table(conn, measurement, metric = None):
    
    
    if metric == None:
        result = conn.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 100')
        df = pd.DataFrame(result.get_points())
        return df
    else:
        df = df[metric]

    #print(clicked['row'])
        #print(clicked)

#main = pn.Column("""### Language generation part""",pn.Spacer(height = 300),"""### Visualization part""", pn.Spacer(height = 300), background = 'white', css_classes = ['main'])
#side = pn.Column(accordion, css_classes = ['side'], width = 400)
#pn.Row(side, main, css_classes = ['row'])




