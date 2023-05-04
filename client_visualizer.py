# from performance_analysis import *
#from influxdb import InfluxDBClient
import pandas as pd
import panel as pn
from panel import widgets as w
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
import datetime as dt
from datetime import datetime, date, timedelta, timezone
import plotly.graph_objs as go
import plotly.express as px
import requests
import json
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

    .bk.task_box{
        border: 1px solid  lightgray;
    }
    '''
pn.extension('plotly','tabulator',sizing_mode = 'stretch_width', css_files=[pn.io.resources.CSS_URLS['font-awesome']], raw_css = [css])
ui = None


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
    return pn.Column("### Performance Tables",accordion, width = 350)

def load_table(conn, measurement, metric = None):
    if metric == None:
        result = conn.query(f'SELECT * FROM {measurement} ORDER BY time DESC LIMIT 100')
        df = pd.DataFrame(result.get_points())
        return df
    else:
        df = df[metric]

def load_all_metrics(config):
    url = "http://eda:80/"
  
    params = {
        'config':config
    }


    response = requests.get(url+"all_metrics", params ={'params': json.dumps(params)})
    # Check the response status code
    if response.status_code == 200:
        data = response.json() 
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    
    df = pd.DataFrame(data['metric'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])


    return df

def query_performance_data(config, table='all', metrics='all', task='metrics', type = None, start_time=None, end_time=None, interval=None):
    url = "http://eda:80/"
    print("query_performance_data", config)
    
    params = {
        'table':table,
        'metric':metrics,
        'start_time':start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'end_time':end_time.strftime("%Y-%m-%d %H:%M:%S"),
        'interval':interval,
        'task':task,
        'config':config
    }

    # if start_time == None and end_time == None:
    #     params['start_time'] = None
    #     params['end_time'] = None
    # if interval == None:
    #     params['interval'] = None
    


    response = requests.get(url+"data", params ={'params': json.dumps(params)})
    # Check the response status code
    if response.status_code == 200:
        data = response.json() 
    else:
        print(f"Error sending configuration data. Status code: {response.status_code}")
    
    
    return data

   
def get_widgets(schema, config):
    for k in schema.keys():
        for c in schema[k]:
            if c[0] == 'timestamp' or c[0] == 'dbid':
                schema[k].remove(c)   
        


    w_measurement = w.Select(name = 'Measurements', options = list(schema.keys()), value = list(schema.keys())[0], width = 300)
    #print(type(schema))
    # elif data is not None:
    #     # 해당 dataframe을 이용하여 시각화
    # else:
    #     NotImplementedError

    w_title = w.TextInput(name='Title', placeholder='Enter a string for title of visualization', width = 300)
    w_time = w.Select(name = 'Time range', options={'Last 30 minutes':'30 minutes',
                                                    'Last hour':'1 hour',
                                                    'Last 4 hours':'4 hours',
                                                    'Last 12 hours':'12 hours',
                                                    'Last 24 hours':'1 day', 'Custom':''}, width = 300)
    # custom 선택되면 time range 선택하는 위젯 visible하게 변경
    w_time_custom = w.DatetimeRangePicker(name='', value=(datetime.now() - timedelta(minutes = 30), datetime.now()), width = 300)
    w_time_custom.disabled = True
    w_refresh = w.Select(name = 'Auto refresh', options = {'Off':'None',  'Every 5 minutes':300000, 
                                                                            'Every 10 minutes': 600000, 
                                                                            'Every 15 minutes':900000, 
                                                                           'Every 30 minutes':1800000}, width = 300)

    
    
    class task_widget():
        def __init__(self):
            self.w_task = w.Select(name = 'Task', options = ["Choose a task",'metrics', 
                                                'historical comparisons', 
                                                'query analysis', 
                                                'distribution', 
                                                'correlation', 
                                                'load prediction',
                                                'query ranking', 
                                                'performance anomaly diagnosis', 
                                                'anomaly detection', 
                                                'delta between predicted and actual value'], width = 300)
            self.w_task_type = w.Select(name = 'Task type', options = ['anomaly time interval', 
                                                'anomaly scorer', 
                                                'anomaly detector'], width = 300)
            self.w_show_bound = w.Select(name = 'Show bounds', options = ['y','n'], width = 300)
            self.w_data = w.MultiSelect(name = 'Data', options = [i[0] for i in schema[w_measurement.value]], width = 300)
            self.w_color = w.Select(name = 'Color', options = ['None'] + [i[0] for i in schema[w_measurement.value]], width = 300)
            self.w_shape = w.Select(name = 'Shape', options = ['None'] + [i[0] for i in schema[w_measurement.value]], width = 300)
        
            self.w_type = w.Select(name = 'Type', options = ['stacked bar', 'bar', 'line', 'area'], width = 300)
            self.w_order = w.Select(name = 'Order', options = ["ASC", "DESC"], width = 300)

            def set_options(event):
                for widget in self.widget[2][0]:
                    widget.options = self.w_data.value
                #self.w_shape.options = self.w_data.value
            self.w_data.param.watch(set_options, ['value'], onlychanged=True)
     
            
            self.widget = pn.Column(pn.Row(self.w_task),pn.Row(), pn.Row(), css_classes = ['task_box'])
            ## color, shape, pattern, size, row, col, tab, legend, label
            def fill_widget(event):
                self.w_data.options = [i[0] for i in schema[w_measurement.value]]
                if self.w_task.value == 'metrics':
                    self.widget[1].objects = [pn.Row(self.w_data, self.w_type, self.w_order)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]

                elif self.w_task.value == 'query analysis':
                    
                    self.widget[1].objects = [pn.Row(self.w_data, self.w_type, self.w_order)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                    self.w_color.value = 'queryid'
                
                elif self.w_task.value == 'query ranking':
                    
                    self.widget[1].objects = [pn.Row(self.w_data)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]
                
                elif self.w_task.value =='anomaly detection':
                    self.widget[1].objects = [pn.Row(self.w_data, self.w_type, self.w_task_type)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]

                elif self.w_task.value =='load prediction':
                    self.widget[1].objects = [pn.Row(self.w_data)]
                    self.widget[2].objects = [pn.Card(pn.Row(self.w_color, self.w_shape),width =1000, collapsible = True, collapsed = True, title = 'Options')]



            self.w_task.param.watch(fill_widget, ['value'], onlychanged=True)
            


    widgets = pn.Row(w_title, w_measurement, pn.Column(w_time, w_time_custom), w_refresh, )
    def custom_time(event):
        if w_time.value == '':
            w_time_custom.disabled = False
        else:
            w_time_custom.disabled = True
    w_time.param.watch(custom_time, ['value'], onlychanged=True)
    
    w_add_task = w.Button(name = 'Add task', width = 100)
    
    # task = pn.Row(w_task, w_data, w_type, w_add_task)
    tasks = []
    def set_data(event):
        for row in c_task: # row = object의 widget이 담긴 Row
            if len(row[0]) > 1 and len(row[0][1])!=0: #row[0] = widget
                row[0][1][0].options = schema[w_measurement.value] # data
                for c_row in row[0][2]: # card
                    for widget in c_row:
                        widget.options = schema[w_measurement.value]
    w_measurement.param.watch(set_data, ['value'], onlychanged=True)
    
    def add_task(button):
        task = task_widget()
        tasks.append(base_task)
        task.w_data.param.watch(set_split, ['value'], onlychanged =True)
        c_task.append(pn.Row(task.widget))

    w_add_task.on_click(add_task)
    task = task_widget()
    tasks.append(base_task)
    c_task = pn.Card(pn.Row(task.widget, w_add_task), title = 'Task', width = 1200)
    w_split = w.Select(name = 'Split', options = ['None','column', 'row', 'tab'], width = 300)
    w_split_basis = w.Select(name = 'Split basis', options = {}, width = 300)
    c_split = pn.Card(pn.Row(w_split, w_split_basis), title = 'Split', width = 1200)
    def set_split(event):
        dict = {}
        for task in tasks:
            dict[', '.join(task.w_data.value)] = task.w_data.value
        w_split_basis.options = dict
    for task in tasks:
        task.w_data.param.watch(set_split, ['value'], onlychanged =True)

    def tasks_to_charts(clicked_button, tasks):
        for task in tasks:
            if task.w_task.value == "metrics":
                result = query_performance_data(config, w_measurement.value, task.w_data.value, task.w_task.value, start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], interval=w_time.value)
                df = pd.DataFrame(result['metric'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])

                #df = load_table(conn, w_measurement.value)
                fig = metrics_task(y=task.w_data.value,chart_type = 'line').plot(df)
                #print(fig)
                main.append(pn.pane.Plotly(fig))
            elif task.w_task.value == 'load prediction':
                result = query_performance_data(config, w_measurement.value, task.w_data.value, task.w_task.value, start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], interval=w_time.value)
                
                df = pd.DataFrame(result['metric'])
                df_task = pd.DataFrame(result['task'])

                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_task['timestamp'] = pd.to_datetime(df_task['timestamp'])
                fig = load_prediction_task(y=task.w_data.value,chart_type = 'line').plot(df, derived_df=df_task)
                #print(fig)
                main.append(pn.pane.Plotly(fig))
            elif task.w_task.value == 'anomaly detection':
                result = query_performance_data(config, w_measurement.value, task.w_data.value, task.w_task.value, type = task.w_task_type.value, start_time=w_time_custom.value[0], end_time=w_time_custom.value[1], interval=w_time.value)
                
                df = pd.DataFrame(result['metric'])
                df_task = pd.DataFrame(result['task'])

                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df_task['timestamp'] = pd.to_datetime(df_task['timestamp'])

                if task.w_task_type.value == 'anomaly scorer':
                    fig = anomaly_scorer_task(y=task.w_data.value,chart_type = 'line').plot(df, derived_df=df_task)
                elif task.w_task_type.value == 'anomaly time interval':
                    fig = anomaly_time_interval_task(y=task.w_data.value,chart_type = 'line').plot(df, derived_df=df_task)
                elif task.w_task_type.value == 'anomaly detector':
                    fig = anomaly_detector_task(y=task.w_data.value,chart_type = 'line').plot(df, derived_df=df_task)
                else:
                    raise AssertionError
                
                #print(fig)
                main.append(pn.pane.Plotly(fig))
        NotImplemented
    w_draw = w.Button(name='Draw', width = 100)
    import functools
    w_draw.on_click(functools.partial(tasks_to_charts, tasks=tasks))
    main = pn.Column("### Visualization Language Generation", widgets, c_task, c_split, w_draw)
    return main
    #display(ui)


    



class base_task:
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
            fig = px.bar(df, x=self.x, y=self.y, color=self.color, facet_col=self.col)
        else:
            raise ValueError("Invalid Chart Type")

        fig.update_layout(
            title=title,
            #xaxis_title='Sepal Length (cm)',
            #yaxis_title='Sepal Width (cm)'
        )
        fig.show()
        return fig


class metrics_task(base_task):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.chart_type = chart_type

class anomaly_scorer_task(base_task):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
       
class anomaly_detector_task(base_task):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)

class anomaly_time_interval_task(base_task):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)

class load_prediction_task(base_task):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'timestamp'
        self.y = y
        self.predicted_x = 'timestamp'
        self.predicted_y = 'predicted'
        self.lower_bound = 'lower_bound'
        self.upper_bound = 'upper_bound'
        self.chart_type = chart_type

class correlation_task(base_task):
    def __init__(self, x, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = x
        self.y = y
        self.chart_type = chart_type


class query_analysis_task(base_task):
    def __init__(self, y, chart_type, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'time'
        self.y = y
        self.color = 'queryid'
        self.chart_type = chart_type


class query_ranking_task(base_task):
    def __init__(self, data, max_row=None):
        super().__init__()
        self.chart_type = 'table'
        self.data = data 
        # Data를 metric과 additional_column으로 분리하는 작업 필요
        # not used to rank
        # ㅇself.metrics = metrics # will be used to rank
        self.max_row = max_row 



    
    



