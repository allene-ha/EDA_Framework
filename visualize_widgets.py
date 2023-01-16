from query import * 
from dataframe_visualization import *
from performance_analysis import *
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML, Output, Layout
import panel as pn
from panel import widgets as w
#import holoviews as hv
import datetime
from awesome_panel_extensions.models.icon import Icon
from awesome_panel_extensions.widgets.button import AwesomeButton
from panel.pane import HTML, HoloViews, Markdown


plt.style.use('seaborn-notebook')
DATE_BOUNDS = (datetime.datetime(2023, 1, 11, 23, 0, 0), datetime.datetime(2023, 1, 12, 5, 0, 0)) # default 15

def visualize_panel():    
    import_and_update_data()

    css = '''
    .btn .bk-btn-group button {
        cursor: default;
        border: 0px;
        background-color: transparent;
        border-radius: 0px;
        height: 30px;
        width: 100px;
        margin-top: 0;
        font-size: 100%;
        text-align: left; 
    }
    .btn .bk-btn-group button:hover {
        background-color: transparent;
    }
    .btn .bk-btn-group button:focus {
        background-color: transparent;
        box-shadow: inset 0px 0px 0px ;
    }
    .picker {
        width: 300px;
    }
    '''
    pn.extension(comms = 'ipywidgets', sizing_mode = 'stretch_width', raw_css = [css])
    pn.config.js_files["fontawesome"]="https://kit.fontawesome.com/121cf5990e.js"

    #pn.config.js_files["fontawesome"]="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.14.0/js/all.min.js"
    
    def icon(name):
        return pn.pane.HTML(f"<i class='fa fa-{name}'></i>", width = 50)

    template = pn.template.MaterialTemplate(title='DB Experimental Data Analysis Framework')

    # menu_items = [('Metrics', 'a'), ('Dashboard', 'b'), None, ('Help', 'help')]
    # menu_button = w.MenuButton(name='Monitoring', items=menu_items, split = True)
    
    template.sidebar.append(Markdown("""## Monitoring"""))
    
    
    # Side bar

    #side_btn_metrics = w.Button(name='Metrics', css_classes = ['btn'])
    #side_btn_board = w.Button(name='Dashboard', css_classes = ['btn'])
    side_btn_metrics = AwesomeButton(name="Metrics",icon=Icon(name="",value="""<i class="fa fa-chart-line"></i>"""))
    side_btn_metrics.css_classes= ['btn']

    side_btn_board = AwesomeButton(name="Dashboard",icon=Icon(name="",value="""<i class="fa fa-th"></i>"""))
    side_btn_board.css_classes= ['btn']
    template.sidebar.append(side_btn_metrics)
    template.sidebar.append(side_btn_board)

    # Top bar
    top_btn_new = AwesomeButton(name="New chart",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>'))
    top_btn_new.css_classes= ['btn']
    

    top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>"""))
    top_btn_refresh.css_classes= ['btn']
    datetime_range_picker = w.DatetimeRangePicker(name='Time range', value=DATE_BOUNDS, width = 400)

    top_bar = pn.Row(top_btn_new,top_btn_refresh,None, datetime_range_picker)


    class Chart():
        def __init__(self, name, num):
            self.name = name
            self.num = num
            #self.ctop_btn_add = AwesomeButton(name="Add metric",icon=Icon(name="",value='<i class="fas fa-plus"></i>'))
            #self.ctop_btn_add.css_classes= ['btn']
            l = get_metrics_info()
            self.metrics = pn.widgets.MultiChoice(name='➕ Add metric', options=l, solid = False, value = [l[0]], height = 150, width = 400)
            

            self.agg = w.Select(name = '📊 Aggregation', options=['average','min','max','sum'], margin = [10,10])
            self.agg.css_classes= ['btn']
            self.ctop_btn_board = AwesomeButton(name="Add to dashboard",icon=Icon(name="",value='<i class="fas fa-bookmark"></i>'))
            self.ctop_btn_board.css_classes= ['btn']
            self.chart_type = w.Select(name = '📈 Chart type', options={'Line chart':'line', 'Bar chart':'bar', 'Area chart':'area', 'Scatter chart':'scatter'}, margin = [10,10])
            self.chart_top_bar = pn.Row(self.metrics, self.agg, None, self.chart_type, self.ctop_btn_board, background='WhiteSmoke')
            self.chart_col = pn.Column()
            self.aggregate = []
            
            
            
        def _get_metrics(self):
            return get_metrics_info(self.metrics)
        def draw_chart(self, metrics=[], aggregate='average', type = 'line', timerange = datetime_range_picker.value):
            chart = visualize_metrics_panel(metrics, aggregate, type, timerange)
            metrics = [m.replace('_', ' ') for m in metrics]
            if len(metrics) == 1:
                self.name = metrics[0]
            elif len(metrics) >= 2:
                self.name = ', '.join(metrics[0:3])
                if len(metrics) > 4:
                    self.name += f", and {len(metrics)-3} other metrics" 
            #print(self.num)
            if self.num>1 or len(metrics)>1:
                template.main[0][self.num-1].title = self.name
            #print(len(template.main))
            #[self.num].title = self.name
            return pn.panel(chart)

        def get_title(self, metrics = []):
            return pn.pane.Markdown(f"### {self.name}")

        def chart(self):
            self.chart_col = pn.Column(pn.bind(self.draw_chart, metrics = self.metrics, aggregate = self.agg, type = self.chart_type, timerange = datetime_range_picker))
            return pn.Card(pn.bind(self.get_title, metrics = self.metrics), self.chart_top_bar, self.chart_col, collapsible = False, hide_header = True)
    def new_chart(clicked_button):
        num = len(template.main[0])-1
        chart = Chart('name', num)
        template.main[0].append(chart.chart())
    
    top_btn_new.on_click(new_chart)
    


    template.main.append(
        pn.Column(
            top_bar,
            Chart('First Chart', 1).chart(),    
        ),
    )
    

    
    #template.servable()
    template.show()

    #display(HTML(style))
    

def visualize(df = None, user_query = ""):
    line = HTML('<hr>')
    style="""
            <style>
                /* enlarges the default jupyter cell outputs, can revert by Cell->Current Outputs->Clear */
                .container { width:1020 !important; } 
                
                
                /* styles for output widgets */
                .o1 {width:180px; border:1px solid #ddd}
                .o2 {width:800px; border:1px solid #ddd}
                .b1 {background-color:skyblue; }
                .o5 span {color:red !important}
                
                /* custom styles for testing */
                .style_A {background-color:#fafaaa}
                .style_B {background-color:#faaafa}
                .style_C {background-color:#aafafa}
            </style>
        """
    
    
    display(HTML(style))
    layout_btn = widgets.Layout(width = '160px')
    layout_btn2 = widgets.Layout(width = '100px')
    layout_d = widgets.Layout(width = '100px')
    style_btn = dict(button_color='white')

    col_layout = Layout(display='flex',
                    flex_flow='column',
                    align_items='center',
                    #border='solid',
                    width='100%')
    row_layout = Layout(display='flex',
                    flex_flow='row',
                    align_items='center',
                    align_content = 'stretch',
                    justify_content = 'center',


                    #border='solid',
                    width='100%')
    
    head = HTML(value="<b><font size = 5> Visualization Mode</b>")
    head1 = HTML(value="<font size = 3> General Visualization")
    head2 = HTML(value="<font size = 3> Specialized Visualization")
    b11= Button(description="Query and Visualize")
    df_btn = widgets.Button(description='Dataframe',
                       tooltip='',
                       icon='fa-table',
                       layout=layout_btn,
                       style = style_btn)
    #b21= Button(description="Metrics")
    metric_btn = widgets.Button(description='Metrics',
                       tooltip='',
                       icon='fa-line-chart',
                       layout=layout_btn,
                       style = style_btn)
    
    query_performance_btn = widgets.Button(description='Query Performance',
                       tooltip='',
                       icon='fa-database',
                       layout=layout_btn,
                       style = style_btn)
    b23= Button(description="Wait Time Viewer")
    o11 = Output()
    o12 = Output()
    o11.add_class('o1')
    o12.add_class('o1')
    o21 = Output()
    o21.add_class('o2')
    o22 = Output()
    o22.add_class('o2')
    o23 = Output()
    o23.add_class('o2')
    scene = HBox([VBox([o11,o12]),VBox([o21,o22,o23])])
    display(scene)

    def reload():
        clear_output()
        display(scene)
    
    
    status = 'metric'
    o11.add_class('b1')
    with o11:
        display(HTML(' '))
    with o12:
        import datetime


        display(HTML("<b><center><font size = 2>Monitoring<br></center>"),layout = col_layout)
        display(VBox([metric_btn, query_performance_btn, df_btn],layout = col_layout))
    
        # chart title
 

    def b11_on_click_callback(clicked_button: widgets.Button) -> None:
        b11_head = HTML(value="<b><font size = 3> Query and Visualize")
        rb = widgets.RadioButtons(
                    options=['w/ template', 'w/o template'],
                    description='Query Mode:',
                    disabled=False
                )
        b11_button = Button(description="Ok", button_style ='primary')
        def query_on_click_callback(b):
            if rb.value == 'w/ template':
                get_query_template()
            elif rb.value == 'w/o template':
                if user_query != "":
                    q(user_query)
                else:
                    text = widgets.Text(description='Query:', disabled=False)
                    text_button = Button(description = "Enter")
                    display(HBox([text, text_button]))
                    def text_button_on_click_callback(tb):
                        if len(text.value)>0:
                            q(text.value)
                    text_button.on_click(text_button_on_click_callback)
                
                 
                 
    def b12_on_click_callback(clicked_button: widgets.Button) -> None:
        assert df is not None, '[Error] Dataframe input is required to visualize dataframe !'
        dataframe_visualization(df)

    #b12.on_click(b12_on_click_callback)
    
    def metric_on_click_callback(clicked_button: widgets.Button=None) -> None:

        with o21:
            clear_output()
            new_btn = widgets.Button(description='New chart',
                        tooltip='',
                        icon='fa-plus',
                        layout=layout_btn2,
                        style = style_btn)
            refresh_btn = widgets.Button(description='Refresh',
                        tooltip='',
                        icon='fa-refresh',
                        layout=layout_btn2,
                        style = style_btn)
            display(HBox([new_btn, refresh_btn]))
        with o22:
            import panel as pn
            from panel import widgets as w
            pn.extension('ipywidgets')
            o221 = Output()

            

            datetime_range_picker = w.DatetimeRangePicker(name='Local time', value=values)

            
            clear_output()
            #new_m_label = HTML('<i class="fa fa-plus-square-o" aria-hidden="true"></i> New metric')
            new_m = w.Select(name='Add metric', options=['Biology', 'Chemistry', 'Physics'])
            new_f = w.Select(name='Add filter', options=['Biology', 'Chemistry', 'Physics'])

            display(o221)
            with o221:
                display(pn.Row(new_m, new_f, datetime_range_picker))
#                display(datetime_range_picker)
        with o23:
            clear_output()
            plt.Figure()
            plt.show()


    metric_btn.on_click(metric_on_click_callback)

    metric_on_click_callback()

    def b22_on_click_callback(clicked_button: widgets.Button) -> None:
        query_visualizer()

    #b22.on_click(b22_on_click_callback)
    
    def b23_on_click_callback(clicked_button: widgets.Button) -> None:
        wait_visualizer()

    #b23.on_click(b23_on_click_callback)
    
    
    
    #display(VBox([head, head1,button_box1, head2, button_box2],layout = col_layout))