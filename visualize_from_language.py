# from performance_analysis import *
from influxdb import InfluxDBClient
import pandas as pd
import panel as pn
from panel import widgets as w
from bokeh.models.widgets.tables import NumberFormatter, BooleanFormatter
import datetime as dt
from datetime import datetime, date, timedelta, timezone
import plotly.graph_objs as go
import plotly.express as px

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

def get_sidebar(connector=None, metrics=None):
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
        #print(measurement)
        table = pn.widgets.Tabulator(df,name = "<i class='fa fa-table'></i> "+ measurement.replace("_"," ").capitalize(),show_index=False, formatters = bokeh_formatters)

        df_widgets.append(table)#,button))

    accordion = pn.Accordion(*df_widgets)
    return pn.Column("### Performance Tables",accordion, width = 350)

def get_schema(conn):
    result = conn.get_list_measurements()
    measurements = [m['name'] for m in result]
    #print(measurements)
    schema = {}

    for measurement in measurements:
        schema[measurement] = []

        query = f"SHOW FIELD KEYS from {measurement}"   
        result = conn.query(query)
        result = list(result.get_points())
        #print(result)
        fieldkey = [m['fieldKey'] for m in result]
         
        query = f"SHOW TAG KEYS from {measurement}"   
        result = conn.query(query)
        result = list(result.get_points())
        #print(result)
        tagKey = [m['tagKey'] for m in result]
        
        
        schema[measurement]= fieldkey+tagKey

    return schema


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
def visualize(conn = None, data = None):
    if conn is not None:
    #     # 어떤 데이터를 시각화할지도 결정해야함
        schema = get_schema(conn)
        w_measurement = w.Select(name = 'Measurements', options = list(schema.keys()), value = list(schema.keys())[0], width = 300)
    print(type(schema))
    # elif data is not None:
    #     # 해당 dataframe을 이용하여 시각화
    # else:
    #     NotImplementedError

    w_title = w.TextInput(name='Title', placeholder='Enter a string for title of visualization', width = 300)
    w_time = w.Select(name = 'Time range', options={'Last 30 minutes':30,
                                                    'Last hour':60,
                                                    'Last 4 hours':240,
                                                    'Last 12 hours':720,
                                                    'Last 24 hours':1440, 'Custom':-1}, width = 300)
    # custom 선택되면 time range 선택하는 위젯 visible하게 변경
    w_time_custom = w.DatetimeRangePicker(name='', value=(datetime.now() - timedelta(minutes = 30), datetime.now()), width = 300)
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
                                                'query ranking', 
                                                'cause analysis', 
                                                'anomaly detection', 
                                                'delta between predicted and actual value'], width = 300)
            if conn is not None:
                self.w_data = w.MultiSelect(name = 'Data', options = schema[w_measurement.value], width = 300)
                self.w_color = w.Select(name = 'Color', options = ['None'] + schema[w_measurement.value], width = 300)
                self.w_shape = w.Select(name = 'Shape', options = ['None'] + schema[w_measurement.value], width = 300)
            
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
                self.w_data.options = schema[w_measurement.value]
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
                

            self.w_task.param.watch(fill_widget, ['value'], onlychanged=True)
            


    widgets = pn.Row(w_title, w_measurement, w_time, w_refresh, )
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
        tasks.append(task)
        task.w_data.param.watch(set_split, ['value'], onlychanged =True)
        c_task.append(pn.Row(task.widget))

    w_add_task.on_click(add_task)
    task = task_widget()
    tasks.append(task)
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

    def tasks_to_elements(clicked_button, tasks):
        for task in tasks:
            if task.w_task.value == "metrics":
                df = load_table(conn, w_measurement.value)
                fig = MetricsElement(y=task.w_data.value,chart_type = 'line').plot(df)
                print(fig)
                ui[1].append(pn.pane.Plotly(fig))
        NotImplemented
    w_draw = w.Button(name='Draw', width = 100)
    import functools
    w_draw.on_click(functools.partial(tasks_to_elements, tasks=tasks))
    ui = pn.Row(get_sidebar(conn), pn.Column("### Visualization Language Generation", widgets, c_task, c_split, w_draw))
    display(ui)


    



class Element:
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
        
    def plot(self, df, title = ""):
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


class MetricsElement(Element):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'time'
        self.y = y
        self.chart_type = chart_type

class CorrelationElement(Element):
    def __init__(self, x, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = x
        self.y = y
        self.chart_type = chart_type


class QueryAnalysisElement(Element):
    def __init__(self, y, chart_type, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type)
        self.x = 'time'
        self.y = y
        self.color = 'queryid'
        self.chart_type = chart_type


class DeltaPredictedActualElement(Element):
    def __init__(self, y, chart_type, color=None, shape=None, pattern=None, size=None, row=None, col=None, tab=None, legend=None, label=None):
        super().__init__(chart_type, color=color)
        self.x = 'time'
        self.y = y
        self.chart_type = chart_type


class QueryRankingElement(Element):
    def __init__(self, data, max_row=None):
        super().__init__()
        self.chart_type = 'table'
        self.data = data 
        # Data를 metric과 additional_column으로 분리하는 작업 필요
        # not used to rank
        # ㅇself.metrics = metrics # will be used to rank
        self.max_row = max_row 



    
    



