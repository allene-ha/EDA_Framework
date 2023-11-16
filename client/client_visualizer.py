import pandas as pd
import panel as pn
from panel import widgets as w
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
import datetime as dt
from datetime import datetime, date, timedelta, timezone
import random
import pytz
import plotly.express as px
import pickle
import requests
import json
from functools import partial
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from IPython.display import display, clear_output


import sys
stdout = sys.stdout

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

    .bk.task_box{
        border: 1px solid  lightgray;
    }
    '''
pn.extension('plotly','tabulator',  sizing_mode = 'stretch_width', css_files=[pn.io.resources.CSS_URLS['font-awesome']], raw_css = [css])
ui = None #,
px.defaults.template = "plotly_white"
with open('../port.json', 'r') as json_file:
    data = json.load(json_file)
    server_port = data.get('server')

def get_sidebar(schema, sidebar_content):
    
    df_widgets = []

    bokeh_formatters = {
        #'float': NumberFormatter(format='0.00000'),
        'key': BooleanFormatter(icon = 'check-circle-o'),
    }
    for table_name in schema.keys():
        
        df_filtered = sidebar_content.loc[sidebar_content['table'] == table_name]
        df_filtered = df_filtered.drop('table', axis=1)
        table = pn.widgets.Tabulator(df_filtered,name = "<i class='fa fa-table'></i> "+ table_name.replace("_"," ").capitalize(),show_index=False, formatters = bokeh_formatters)

        df_widgets.append(table)

    accordion = pn.Accordion(*df_widgets)
    return pn.Column("### Performance Tables",accordion, width = 300)

def load_table(conn, measurement, metric = None):
    if metric == None:
        result = conn.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 100')
        df = pd.DataFrame(result.get_points())
        return df
    else:
        df = df[metric]

def query_all_metrics_into_csv(config, save_dir, cause):
    original_df = pd.read_csv(f'../benchmark/log3/{cause}_log.csv')

    # Create a new DataFrame for the results
    results_df = pd.DataFrame(columns=['iteration', 'start_time', 'end_time', 'Anomaly Start Time','Anomaly End Time'])

    # Iterate through the rows of the original DataFrame
    for index, row in original_df.iterrows():
        iteration = row['Iteration']
        start_time = row['Start Time']
        end_time = row['End Time']
        
        # Create a new row for the results DataFrame
        results_df = load_all_metrics(config, start_time, end_time)
        results_df['cause'] = cause
        results_df.to_csv(f'{save_dir}/{cause}_{iteration}.csv', index=False)



def load_all_metrics(config, start_time=None, end_time=None):
    url = f"http://localhost:{server_port}/"
    
    params = {
        'config':config,
    }

    if start_time is not None:
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
        params['start_time'] = start_time
        
    if end_time is not None:
        params['end_time'] = end_time

    response = requests.get(url+"all_metrics", params ={'params': json.dumps(params)})
    # Check the response status code
    data = pickle.loads(response.content)

    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])


    return df

def get_analysis_time(config, table):
    url = f"http://localhost:{server_port}/"
    #print("query_performance_data", config)
    
    params = {
        'table':table,
        'config':config,
    }
    response = requests.get(url+"analysis_time", params ={'params': json.dumps(params)})
    # Check the response status code
    if response.status_code == 200:
        data = response.json() 
        return list(data['analysis_time'])
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
        return ValueError

def query_performance_data(config, table='all', metrics='all', task='metrics', type = None, start_time=None, end_time=None, recent_time_window=None,  order = None, num_of_query = None, split_date=None, analysis_time = None):
    # data
    
    url = f"http://localhost:{server_port}/"
    #print("query_performance_data", config)
    
    params = {
        'table':table,
        'metric':metrics,
        'recent_time_window':recent_time_window,
        'task':task,
        'config':config,
    }
    if task == 'anomaly analysis':
        params['task_type'] = type

    if start_time is not None: # 왜 str ???
        if isinstance(start_time, datetime):
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
        params['start_time'] = start_time
        params['end_time'] = end_time
        
    if order is not None:
        params['order'] = order
        params['num_of_query'] = str(num_of_query)
    
    if analysis_time is not None:
        params['analysis_time'] = analysis_time
    
    print(params)

    response = requests.get(url+"data", params ={'params': json.dumps(params)})
    # Check the response status code
    if response.status_code == 200:
        data = response.json() 
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    return data
        
def load_and_split_performance_data(config, table='all', metrics='all', time_interval=[None,None], split_date=None):
    #
    if table == 'all':
        df = load_all_metrics(config, time_interval[0], time_interval[1])
    else:
        data = query_performance_data(config, table, metrics, start_time=time_interval[0], end_time=time_interval[1], recent_time_window=None, split_date=None)
        df = pd.DataFrame(data['metric'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if split_date != None:
        # 데이터프레임을 기준 시간을 기준으로 분할합니다.
        train_data = df[df['timestamp'] < split_date]
        test_data = df[df['timestamp'] >= split_date]
        return train_data, test_data
    else:
        return df
        

def get_widgets(schema, config):
    for k in schema.keys():
        for c in schema[k]:
            if c[0] == 'timestamp' or c[0] == 'dbid':
                schema[k].remove(c)   
        


    w_table = w.Select(name = 'Tables', options = list(schema.keys()), value = list(schema.keys())[0], width = 220)

    w_title = w.TextInput(name='Title', placeholder='Enter a string for title of visualization', width = 220)
    w_time = w.Select(name = 'Time range', options={'Last 30 minutes':'30 minutes',
                                                    'Last hour':'1 hour',
                                                    'Last 4 hours':'4 hours',
                                                    'Last 12 hours':'12 hours',
                                                    'Last 24 hours':'1 day', 'Custom':''}, width = 220)
    # custom 선택되면 time range 선택하는 위젯 visible하게 변경
    w_time_custom = w.DatetimeRangePicker(name='Custom time', value=(datetime.now() - timedelta(minutes = 30), datetime.now()), width = 220)
    w_time_custom.disabled = True
    w_refresh = w.Select(name = 'Auto refresh', options = {'Off':'None',  'Every 5 minutes':300000, 
                                                                            'Every 10 minutes': 600000, 
                                                                            'Every 15 minutes':900000, 
                                                                           'Every 30 minutes':1800000}, width = 220)

    
    
    class task_widget():
        def __init__(self):
            self.w_task = w.Select(name = 'Task', options = ["Choose a task",
                                                            'metrics', # ok
                                                            'historical comparison', #ok
                                                            'query analysis', #ok
                                                            'distribution', #ok
                                                            'correlation', #ok
                                                            'load prediction', 
                                                            'query ranking', 
                                                            'performance anomaly diagnosis', 
                                                            'anomaly analysis', 
                                                            'delta between predicted and actual value'], width = 250)
            self.w_task_type = w.Select(name = 'Task type', options = ['anomaly time interval', 
                                                'anomaly score', 
                                                'anomaly detection',
                                                'anomaly explanation',
                                                'anomaly detection and explanation'], width = 250)

            self.w_show_bound = w.Select(name = 'Show bounds', options = ['y','n'], width = 300)
            # 중복 허용
            self.w_data_multi = w.MultiSelect(name = 'Data', options = [i[0] for i in schema[w_table.value]], width = 300)
            # 중복 비허용
            self.w_data_x = w.Select(name = 'Data', options = [i[0] for i in schema[w_table.value]], width = 250)
            self.w_data_y = w.Select(name = 'Data', options = [i[0] for i in schema[w_table.value]], width = 250)
            
            self.w_num_of_query = w.IntInput(name='# of queries', value=5, step=1, start=1, end=30, width = 250)
            self.w_color = w.Select(name = 'Color', options = ['None'] + [i[0] for i in schema[w_table.value]], width = 300)
            self.w_shape = w.Select(name = 'Shape', options = ['None'] + [i[0] for i in schema[w_table.value]], width = 300)
            self.w_dis_type = w.Select(name = 'Type', options = ['histogram', 'box', 'violin'], width = 250)
            self.w_analysis_time = w.Select(name = 'Analysis Time', options = [''], width = 250)
            #self.w_dataset = w.Select(name = 'Dataset', options = ['dbsherlock_tpcc_500w'], width = 300)
            
            self.w_cor_type = w.Select(name = 'Type', options = ['scatter', 'kernel density estimation', ], width = 250)
            self.w_type = w.Select(name = 'Type', options = ['line','bar',  'area'], width = 200)
            self.w_order = w.Select(name = 'Order', options = ["ASC", "DESC"], value = 'DESC', width = 200)
            self.w_time_interval = w.Select(name = 'time interval', options = {'10 minutes':[10,'min'],
                                                                                '30 minutes':[30,'min'],
                                                                                '1 hour':[1,'H'],
                                                                                '4 hours':[4,'H'],
                                                                                '12 hours':[12,'H'],
                                                                                '1 day':[1,'D']}, width = 300)

            
            def set_options(event):
                for widget in self.widget[2][0]:
                    widget.options = self.w_data_multi.value
            self.w_data_multi.param.watch(set_options, ['value'], onlychanged=True)
     

            self.widget = pn.Column(pn.Row(self.w_task),pn.Row(), pn.Row(), css_classes = ['task_box'])
            ## color, shape, pattern, size, row, col, tab, legend, label
            def fill_widget(event):
                # table을 한정
                if self.w_task.value == 'query analysis' or self.w_task.value == 'query ranking':
                    w_table.value = 'query_statistics'
                elif self.w_task_type.value == 'anomaly detection and explanation':
                    w_table.options = ['dbsherlock_tpcc_500w','eda']

                self.w_data_multi.options = [i[0] for i in schema[w_table.value]]
                self.w_data_x.options = [i[0] for i in schema[w_table.value]]
                self.w_data_y.options = [i[0] for i in schema[w_table.value]]
                
                if self.w_task.value == 'metrics':
                    self.widget[1].objects = [pn.Row(self.w_data_multi, self.w_type)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                
                elif self.w_task.value == 'distribution':
                    self.widget[1].objects = [pn.Row(self.w_data_x, self.w_dis_type)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                
                elif self.w_task.value == 'correlation':
                    self.widget[1].objects = [pn.Row(self.w_data_y, self.w_data_x, self.w_cor_type)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                
                elif self.w_task.value == 'query analysis':    
                    self.widget[1].objects = [pn.Row(self.w_data_y, self.w_type, self.w_order, self.w_num_of_query)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                    self.w_color.value = 'queryid'

                elif self.w_task.value == 'historical comparison':
                    self.widget[1].objects = [pn.Row(self.w_data_y, self.w_type, self.w_time_interval)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                    
                elif self.w_task.value == 'query ranking':
                    self.widget[1].objects = [pn.Row(self.w_data_x, self.w_num_of_query)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                
                elif self.w_task.value =='anomaly analysis':
                    if self.w_task_type.value == 'anomaly explanation':
                        self.widget[1].objects = [pn.Row(self.w_task_type)]
                        self.widget[2].objects = [pn.Card(pn.Row(),width =800, collapsible = True, collapsed = True, title = 'Options')]
                    elif self.w_task_type.value == 'anomaly detection':
                        self.widget[1].objects = [pn.Row(self.w_type, self.w_task_type)]
                        self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =800, collapsible = True, collapsed = True, title = 'Options')]
                    
                    elif self.w_task_type.value == 'anomaly detection and explanation':
                        analysis_time = get_analysis_time(config, 'anomaly_explanation') # list
                        self.w_analysis_time.options = analysis_time
                        self.widget[0].objects = [pn.Row(self.w_task, self.w_task_type)]
                        self.widget[1].objects = [pn.Row(self.w_analysis_time, self.w_data_y)]
                        self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =800, collapsible = True, collapsed = True, title = 'Options')]
                    
                    else:
                        self.widget[1].objects = [pn.Row(self.w_data_y, self.w_type, self.w_task_type)]
                        self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =800, collapsible = True, collapsed = True, title = 'Options')]

                elif self.w_task.value =='load prediction':
                    self.widget[1].objects = [pn.Row(self.w_data_x)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =800, collapsible = True, collapsed = True, title = 'Options')]


            w_table.param.watch(fill_widget, ['value'], onlychanged=True)
            self.w_task.param.watch(fill_widget, ['value'], onlychanged=True)
            self.w_task_type.param.watch(fill_widget, ['value'], onlychanged=True)
            


    widgets = pn.Row(w_title, w_table, w_time, w_time_custom)#, w_refresh, )
    def custom_time(event):
        if w_time.value == '':
            w_time_custom.disabled = False
        else:
            w_time_custom.disabled = True
    w_time.param.watch(custom_time, ['value'], onlychanged=True)
    
    w_add_task = w.Button(name = 'Add task', width = 100)
    
    tasks = []
    def set_data(event):
        for row in c_task: # row = object의 widget이 담긴 Row
            if len(row[0]) > 1 and len(row[0][1])!=0: #row[0] = widget
                row[0][1][0].options = schema[w_table.value] # data
                for c_row in row[0][2]: # card
                    for widget in c_row:
                        widget.options = schema[w_table.value]
    w_table.param.watch(set_data, ['value'], onlychanged=True)
    
    def add_task(button):
        task = task_widget()
        tasks.append(task)
        task.w_data_multi.param.watch(set_split, ['value'], onlychanged =True)
        c_task.append(pn.Row(task.widget))

    w_add_task.on_click(add_task)
    task = task_widget()
    tasks.append(task)
    c_task = pn.Card(pn.Row(task.widget, w_add_task), title = 'Task', width = 1000)
    w_split = w.Select(name = 'Split', options = ['None','column', 'row', 'tab'], width = 300)
    w_split_basis = w.Select(name = 'Split basis', options = {}, width = 300)
    c_split = pn.Card(pn.Row(w_split, w_split_basis), title = 'Split', width = 1000)
    
    def set_split(event):
        dict = {}
        for task in tasks:
            dict[', '.join(task.w_data_multi.value)] = task.w_data_multi.value
        w_split_basis.options = dict
    
    for task in tasks:
        task.w_data_multi.param.watch(set_split, ['value'], onlychanged =True)

    def tasks_to_charts(clicked_button, tasks):
        for task in tasks:
            if task.w_task.value == "metrics":
                result = query_performance_data(config, w_table.value, task.w_data_multi.value, task.w_task.value, start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value)
                df = pd.DataFrame(result['metric'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dashboard = metrics_task_viz_template(y=task.w_data_multi.value,chart_type = 'line').plot(df)
                main.append(dashboard)
            
            elif task.w_task.value == 'query ranking':
                result = query_performance_data(config, 'query_statistics', task.w_data_x.value, 'query ranking', start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value, order = task.w_order.value, num_of_query = task.w_num_of_query.value)
                df = pd.DataFrame(result['task'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dashboard = w.Tabulator(df)
                main.append(dashboard)
                
            elif task.w_task.value == "query analysis": 
                result = query_performance_data(config, 'query_statistics', task.w_data_y.value, 'query analysis', start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value, order = task.w_order.value, num_of_query = task.w_num_of_query.value)
                df = pd.DataFrame(result['task'])
                df['timestamp'] = pd.to_g(df['timestamp'])
                query_dict = result['query_dict']
                top_queryid = result['top_queryid']
                template = query_analysis_task_viz_template(y=task.w_data_y.value,chart_type = task.w_type.value)#, query_dict = query_dict)
                dashboard = template.plot(df,  query_dict = query_dict, top_queryid = top_queryid)
                main.append(dashboard)

            elif task.w_task.value == "correlation":
                result = query_performance_data(config, w_table.value, task.w_data_x.value+", "+task.w_data_y.value, 'metrics', start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value)
                df = pd.DataFrame(result['metric'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dashboard = correlation_task_viz_template(y=task.w_data_y.value, x= task.w_data_x.value, chart_type = task.w_cor_type.value).plot(df)
                main.append(dashboard)

            elif task.w_task.value == "distribution":
                result = query_performance_data(config, w_table.value, task.w_data_x.value, 'metrics', start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value)
                df = pd.DataFrame(result['metric'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dashboard = distribution_task_viz_template(x=task.w_data_x.value, chart_type = task.w_dis_type.value).plot(df)
                main.append(dashboard)
            
            elif task.w_task.value == "historical comparison":
                result = query_performance_data(config, w_table.value, task.w_data_y.value, 'metrics', start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value)
                df = pd.DataFrame(result['metric'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dashboard = historical_comparison_task_viz_template(y=task.w_data_y.value, chart_type = task.w_dis_type.value, time_interval = task.w_time_interval.value).plot(df)
                main.append(dashboard)    
            
            elif task.w_task.value == 'load prediction':
                result = query_performance_data(config, w_table.value, task.w_data_x.value, task.w_task.value, start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value)
                df = pd.DataFrame(result['metric'])
                df_task = pd.DataFrame(result['task'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_task['timestamp'] = pd.to_datetime(df_task['timestamp'])
                dashboard = load_prediction_task_viz_template(y=task.w_data_x.value,chart_type = 'line').plot(df, derived_df=df_task)
                main.append(dashboard)

            elif task.w_task.value == 'anomaly analysis':

                if task.w_task_type.value == 'anomaly detection and explanation': 
                    result = query_performance_data(config, table = w_table.value, task = task.w_task.value, type = task.w_task_type.value, start_time='-infinity', end_time='infinity', recent_time_window='Custom', analysis_time = task.w_analysis_time.value)
                # else: 
                #     result = query_performance_data(config, w_table.value, task.w_data_y.value, task.w_task.value, type = task.w_task_type.value, start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], recent_time_window=w_time.value)
                
                df = pd.DataFrame(result['metric'])
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                df_task = pd.DataFrame(result['task'])
                df_task['timestamp'] = pd.to_datetime(df_task['timestamp'])
                
                if task.w_task_type.value == 'anomaly score':
                    dashboard = anomaly_score_task_viz_template(y=task.w_data_y.value,chart_type = 'line').plot(df, derived_df=df_task)
                #elif task.w_task_type.value == 'anomaly time interval':
                #    dashboard = anomaly_time_interval_task_viz_template(y=task.w_data_x.value,chart_type = 'line').plot(df, derived_df=df_task)
                elif task.w_task_type.value == 'anomaly explanation':
                    dashboard = anomaly_explanation_task_viz_template().plot(df, derived_df=df_task)
                elif task.w_task_type.value == 'anomaly detection':
                    dashboard = anomaly_detection_task_viz_template(y=task.w_data_y.value,chart_type = 'line').plot(df, derived_df=df_task)
                elif task.w_task_type.value == 'anomaly detection and explanation':
                    dashboard = anomaly_detection_and_explanation_task_viz_template(y=task.w_data_y.value, chart_type = 'line').plot(df, df_task)
                else:
                    raise AssertionError
                main.append(dashboard)
        
    w_draw = w.Button(name='Draw', width = 100)
    import functools
    w_clean = w.Button(name='Clean', width = 100)
    w_draw.on_click(functools.partial(tasks_to_charts, tasks=tasks))
    def clean_output(button):
        main.objects = ["### DB Performance Analysis", widgets, c_task, pn.Row(w_draw,w_clean)]# c_split, pn.Row(w_draw,w_clean)]

    w_clean.on_click(clean_output)
    main = pn.Column("### DB Performance Analysis", widgets, c_task, pn.Row(w_draw,w_clean))# c_split, pn.Row(w_draw,w_clean))
    return main



    



class base_task_viz_template:
    """
    A class representing a template for visualizing chart.

    Attributes:
        y (List[str]): A list of column names to use as the y-axis values.
        chart_type (str): The type of chart to use for visualization.
        color (Optional[str]): The column name to use for coloring the chart.
        shape (Optional[str]): The column name to use for shaping the chart.
        pattern (Optional[str]): The column name to use for patterning the chart.
        size (Optional[str]): The column name to use for sizing the chart.
        row (Optional[str]): The column name to use for creating row facets.
        col (Optional[str]): The column name to use for creating column facets.
        tab (Optional[str]): The column name to use for creating tab facets.
        legend (Optional[str]): The column name to use for creating a legend.
        label (Optional[str]): The column name to use for creating labels.
    """
    def __init__(self, x=None, y=None, chart_type= None, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        self.x = x
        self.y = y
        self.chart_type = chart_type
        self.color = color
        self.shape = shape
        self.pattern = pattern
        self.size = size # only numerical
        self.row = row
        self.col = col
        self.tab = tab  
        #self.legend = legend
        self.label = label
        
    def plot(self, df, derived_df = None, title = ""):
        # implementation of plot method for the base class
        if self.chart_type == 'scatter':
            fig = px.scatter(df, x=self.x, y=self.y, color=self.color, symbol = self.shape, size = self.size, facet_col=self.col, facet_row = self.row)
        elif self.chart_type == 'line':
            fig = px.line(df, x=self.x, y=self.y, color=self.color, facet_col=self.col, facet_row = self.row)
        elif self.chart_type == 'bar':
            fig = px.bar(df, x=self.x, y=self.y, color=self.color, facet_col=self.col, barmode = 'stack')
            
        else:
            raise ValueError("Invalid Chart Type")

        fig.update_layout(
            title=title,
            #xaxis_title='Sepal Length (cm)',
            #yaxis_title='Sepal Width (cm)'
        )
        return pn.pane.Plotly(fig)


class metrics_task_viz_template(base_task_viz_template):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.chart_type = chart_type

class anomaly_score_task_viz_template(base_task_viz_template):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.chart_type = chart_type

    def plot(self, df, derived_df):
        merged_df = pd.merge(df, derived_df, on='timestamp')

        # implementation of plot method for the base class
        if self.chart_type == 'scatter':
            fig = px.scatter(merged_df, x=self.x, y=self.y, color=self.color, symbol = self.shape, size = self.size, facet_col=self.col, facet_row = self.row)
        elif self.chart_type == 'line':
            fig = px.line(merged_df, x=self.x, y=self.y, color=self.color, facet_col=self.col, facet_row = self.row)
        else:
            raise ValueError("Invalid Chart Type")

        custom_colors = [[0.0, 'green'], [0.6, 'yellow'],[0.8, 'orange'], [1.0, 'red']]
        fig.add_trace(go.Scatter(
            x=merged_df['timestamp'],
            y=merged_df[self.y],
            mode='markers',
            marker=dict(
                color=merged_df['anomaly_score'],  # anomaly score에 따라 marker의 진하기 설정
                colorscale=custom_colors,  # 색상 맵 설정
                size=10  # marker의 크기 스케일 설정
            ),
            name='Anomaly'  # trace의 이름 설정
        ))
        fig.update_layout(coloraxis_showscale=True)


#         fig.update_layout(
#             title=title,
#             #xaxis_title='Sepal Length (cm)',
#             #yaxis_title='Sepal Width (cm)'
#         )
        return pn.pane.Plotly(fig)


class anomaly_detection_task_viz_template(base_task_viz_template):
    # anomaly score에 anomaly인 포인트는 마커를 다르게 설정
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.chart_type = chart_type

    def plot(self, df, derived_df):
        merged_df = derived_df

        n = 50
        date_rng = pd.date_range(start="2023-10-27 00:00:00", periods=n, freq="10s")

        # 더미 데이터 생성
        data = {
            "timestamp": date_rng,
            "value": [random.uniform(0, 180) for _ in range(n)],
            "anomaly_score": [random.uniform(0, 1) for _ in range(n)],
            "is_anomaly": [random.choice([False, False,False, False,False, False, True, False,False,False, False, False]) for _ in range(n)],
            "anomaly_cause": [random.choice(["workload spike", "cpu", "memory"]) for _ in range(n)]
        }

        # 데이터프레임 생성
        df = pd.DataFrame(data)

        # 그래프 생성
        fig = go.Figure()

        # 일변수 Anomaly 여부 시각화
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["is_anomaly"], mode="lines", name="Anomaly", line=dict(color="red")))

        # 그래프 레이아웃 설정
        fig.update_layout(legend=dict(orientation="h", y=1.2, x=0)) 
        fig.update_layout(
            title='<b>Anomaly Detection</b>',
            title_font=dict(size=20),
            title_x=0.5,  # 제목의 가로 위치 (0-1),
            width=800
            #template = 'plotly_white'

        )
        fig.update_layout(xaxis_title="Timestamp", yaxis_title="Anomaly (True/False)")

        return pn.pane.Plotly(fig)

class anomaly_detection_and_explanation_task_viz_template(base_task_viz_template):
    # anomaly score에 anomaly인 포인트는 마커를 다르게 설정
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.chart_type = chart_type

    def plot(self, df, df_task):
        df_task['timestamp'] = df_task['timestamp'].dt.tz_localize('Asia/Seoul')
        df['timestamp'] = df['timestamp'].dt.tz_localize('Asia/Seoul')

        # 그래프 생성
        fig = go.Figure()

        # 시계열 데이터를 라인 그래프로 추가
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df[self.y], mode="lines", name="Time Series"))

        df_anomaly = df[df_task['is_anomaly']]
        df_task_anomaly = df_task[df_task['is_anomaly']]

        # anomaly score에 따라 색상 동적 설정
        color_scale = "Reds"  # 원하는 색상 스케일 선택
        colors = df_task_anomaly["anomaly_score"]  # anomaly score에 따라 색상 설정
        colorbar_title = "Anomaly Score"

        # 스캐터 플롯로 추가
        fig.add_trace(go.Scatter(x=df_anomaly["timestamp"], y=df_anomaly[self.y], mode="markers", name="Anomalies",
                                marker=dict(size=10, color=colors, colorscale=color_scale, colorbar_title=colorbar_title, line=dict(width=1, color="black"))))

        # 범례를 차트 위에 추가
        fig.update_layout(legend=dict(orientation="h", y=1.2, x=0))
        fig.update_layout(
            title='<b>Anomaly Detection and Explanation</b>',
            title_font=dict(size=20),
            title_x=0.5,
            width=800
        )

        # is_anomaly가 True인 포인트에 빨간색 배경 표시
        anomaly_indices = df_anomaly.index

        for index in anomaly_indices:
            fig.add_vrect(
                x0=df["timestamp"][index] - pd.Timedelta("5s"),
                x1=df["timestamp"][index] + pd.Timedelta("5s"),
                fillcolor="red",
                opacity=0.2,
                line_width=0
            )

            annotation = go.layout.Annotation(
                x=df["timestamp"][index],
                y=df[self.y][index],
                text=df_task["anomaly_cause"][index],
                showarrow=True,
                arrowhead=4,
                arrowcolor="Red",
                arrowwidth=1,
                bgcolor='lightgray',
                bordercolor="darkgray",
                borderwidth=1,
            )
            fig.add_annotation(annotation)

        return pn.pane.Plotly(fig)



class anomaly_explanation_task_viz_template(base_task_viz_template):
    def __init__(self, y=None, chart_type=None, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__()

    def plot(self, df, derived_df):
        merged_df = derived_df

        n = 50  # 데이터 포인트 수

        # 날짜 범위 생성
        date_rng = pd.date_range(start="2023-10-27 00:00:00", periods=n, freq="10s")

        # 더미 데이터 생성
        data = {
            "timestamp": date_rng,
            "is_anomaly": [random.choice([False, False,False, False,False, False, True, False,False,False, False, False]) for _ in range(n)],
            "primary anomaly cause": [random.choice(["workload spike", "cpu", "memory"]) for _ in range(n)],
            "secondary anomaly cause": [random.choice(["db backup", "poorly written query"]) for _ in range(n)]
        }

        # 데이터프레임 생성
        df = pd.DataFrame(data)
        df_anomaly = df[df['is_anomaly']==True]
        df_anomaly = df_anomaly.drop(columns=["is_anomaly"])

        table = pn.pane.DataFrame(df_anomaly, escape=False, width = 1000, index=False)
        return pn.Column("## Anomaly Explanation", table, height=400, width=1000,align='center')



class load_prediction_task_viz_template(base_task_viz_template):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.predicted_x = 'timestamp'
        self.predicted_y = 'predicted'
        self.lower_bound = 'lower_bound'
        self.upper_bound = 'upper_bound'
        self.chart_type = chart_type

class historical_comparison_task_viz_template(base_task_viz_template):
    def __init__(self, y, chart_type, x = 'timestamp', time_interval = '30 minutes',color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.y = y
        self.chart_type = chart_type
        self.time_interval = time_interval # freq string
    
    def plot(self, df, derived_df = None, title = ""):
        period, freq = self.time_interval
        df = df.set_index('timestamp')

        shifted_df = df.shift(periods = period, freq=freq)
        shifted_df=shifted_df[:max(df.index)]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[self.y], name=self.y))
        fig.add_trace(go.Scatter(x=shifted_df.index, y=shifted_df[self.y], name=self.y+str(period)+" "+freq+" ago"))
        fig.update_layout(title = f"Historical comparison of '{self.y}' ({self.y+str(period)+' '+freq+' ago'})")

        return pn.pane.Plotly(fig)

class distribution_task_viz_template(base_task_viz_template):
    def __init__(self, x, chart_type, y =None, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = x
        self.chart_type = chart_type
    
    def plot(self, df, derived_df = None, title = ""):
        
        if self.chart_type == 'histogram':
            num_bins_widget = pn.widgets.IntSlider(name='Number of Bins', start=1, end=30, value=10)
            # Histogram chart 생성
            @pn.depends(num_bins=num_bins_widget)
            def create_histogram(num_bins):
                fig = px.histogram(df, x=self.x, nbins=num_bins)
                return fig

            
            histogram_chart = pn.Column(create_histogram, num_bins_widget)

            return histogram_chart

        elif self.chart_type == 'box':
            fig = px.box(df, x=self.x)
        elif self.chart_type == 'violin':
            fig = px.violin(df, x=self.x)
    
        return pn.pane.Plotly(fig)

class correlation_task_viz_template(base_task_viz_template):
    def __init__(self, x, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = x
        self.y = y
        self.chart_type = chart_type
    
    def plot(self, df, title = ""): # df에 x, y 데이터가 함께 들어있음
        correlation = df[self.x].corr(df[self.y])
        if self.chart_type == 'scatter':
            fig = px.scatter(df, x=self.x, y=self.y, title=f"Correlation: {correlation}", trendline='ols')
        elif self.chart_type == 'kernel density estimation':
            fig = px.density_contour(df, x=self.x, y=self.y, title=f"Correlation: {correlation}", trendline='ols')

        if title != '':
            fig.update_layout(
                title=title,
                #xaxis_title='Sepal Length (cm)',
                #yaxis_title='Sepal Width (cm)'
            )
        return pn.pane.Plotly(fig)


class query_analysis_task_viz_template(base_task_viz_template):
    def __init__(self, y, chart_type, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        print("log")
        self.y = y
        self.color = 'queryid'
        self.chart_type = chart_type


    def plot(self, df, derived_df = None, title = "", query_dict = {}, top_queryid = []):
        fig = px.bar(df, x=self.x, y=self.y, color=self.color, barmode = 'stack', category_orders = {'queryid':top_queryid}, hover_data = ['query'])
        
        dashboard = pn.pane.Plotly(fig)

        return dashboard

class query_ranking_task_viz_template(base_task_viz_template):
    def __init__(self, y, chart_type=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__()
        self.chart_type = 'table'
        self.y=y
        # Data를 metric과 additional_column으로 분리하는 작업 필요
        # not used to rank
        # ㅇself.metrics = metrics # will be used to rank
    def plot(self, df):
        dashboard = w.Tabulator(df)
        return dashboard