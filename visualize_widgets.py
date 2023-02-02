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
import holoviews as hv
from datetime import datetime, date, timedelta
from awesome_panel_extensions.models.icon import Icon
from awesome_panel_extensions.widgets.button import AwesomeButton
from panel.pane import HTML, Markdown
from panel.layout.gridstack import GridStack
from panel_modal import Modal
import pytz

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
plt.style.use('seaborn-notebook')
#DATE_BOUNDS = (datetime(2023, 1, 19, 12, 30, 0), datetime(2023, 1, 19, 13, 30, 0)) # default 15
pc = {}

def visualize_panel():    
    print('start')
    #pc['update'] = pn.state.add_periodic_callback


    import_and_update_data()
    DAT_NAMES = get_dat_names()
    #print(DAT_NAMES)
    STATE = ['active','idle','idle in transaction','idle in transaction (aborted)','fastpath function call', 'disabled']
    WAIT_EVENT_TYPE = ['Activity','BufferPin','Client','Extension','IO','IPC','Lock','LWLock','Timeout']

    css = '''
    .modebar { display: none !important; }
    i {
    color: #800000;
    }

    .mdc-top-app-bar__section{
        padding: 0px 12px;
    }
    #header {
        height: 55px;
      
    }
    .pn-busy-container {
    visibility: hidden;
    }
    .title{
        font-size: 1em !important;
        font-weight: 550 !important;
    }

    .none {
        display: none;
    }
    .small-btn .bk-btn-group button {
        border: 0px;
        background-color: transparent;
        border-radius: 10px;
        height: 20px;
        width: 20px;
        font-size: 100%;
    }
    .btn .bk-btn-group button, .btn-focus .bk-btn-group button:hover, .btn-focus .bk-btn-group button:focus {

        border: 0px;
        background-color: transparent;
        border-radius: 10px;
        height: 30px;
        width: 100px;
        box-shadow: inset 0px 0px 0px ;
        font-size: 100%;
        text-align: left; 
    }
    .btn-focus .bk-btn-group button {

        border: 0px;
        background-color: rgba(255, 0, 0, 0.2);
        border-radius: 10px;
        height: 30px;
        width: 100px;

        font-size: 100%;
        text-align: left; 
    }
    .small-btn .bk-btn-group button:hover {
        background-color: transparent;
    }
    .small-btn .bk-btn-group button:focus {
        background-color: transparent;
        box-shadow: inset 0px 0px 0px ;
    }
    .btn .bk-btn-group button {

        border: 0px;
        background-color: transparent;
        border-radius: 10px;
        height: 30px;
        width: 100px;

        font-size: 100%;
        text-align: left; 
    }
    .btn .bk-btn-group button:hover {
        background-color: transparent;
    }
    .btn .bk-btn-group button:focus {
        background-color: rgba(255, 0, 0, 0.2);
        box-shadow: inset 0px 0px 0px ;
    }
    .btn .bk-btn-group button:disabled {
        background-color: transparent;
        box-shadow: inset 0px 0px 0px ;
    }
    .btn_round .bk-btn-group button {
        border: 1px maroon solid !important;
        background-color: white !important;
        border-radius: 15px !important;
        height: 35px;
        margin: 15px 0 0 0;
        font-size: 100%;
        text-align: center !important; 
    }
    .btn-board .bk-btn-group button {
        border: 1px maroon solid !important;
        background-color: white !important;
        border-radius: 0px !important;
        height: 50px !important;
        width: 100px !important;
        text-align: center !important;
        font-size: 100%;
    }
    .btn_round .bk-btn-group button:hover {
        background-color: white;
        border: 1px maroon solid;

    }
    .bk.bk-btn.bk-btn-default{
        display: inline-block;
        background-color: transparent;
        border: 0px;
        text-align: start;
        vertical-align: middle;
        white-space: nowrap;
        padding: 6px 12px;
        font-size: 15px;
        border: 0px;
        border-radius: 0px;
        outline: 0;
        box-shadow: none;
    }
    .bk.bk-btn.bk-btn-default.bk-active{
        display: inline-block;
        background-color: lightgray;
        border: 0px;
        text-align: start;
        vertical-align: middle;
        white-space: nowrap;
        padding: 6px 12px;
        font-size: 15px;
        border: 0px;
        border-radius: 0px;
        outline: 0;
        box-shadow: none;
    }
    .bk.bk-radio.bk-btn-default.bk-active{
        display: inline-block;
        background-color: lightgray;
        border: 0px;
        text-align: start;
        vertical-align: middle;
        white-space: nowrap;
        padding: 6px 12px;
        font-size: 15px;
        border: 0px;
        border-radius: 0px;
        outline: 0;
        box-shadow: none;
    }
    .bk.modal-box {
    
        justify-content: center;
        border: 0px;
        background: white;
        
        }
    .bk.box {
        background: WhiteSmoke;
        border-radius: 10px;
        border: 0px;
        height: 40px;
        }
    .bk.float_box {
        display: flex;
        align-items: center;
        justify-content: center;
        align: center;
        align-self: start;
        background: white;
        border-radius: 15px;
        border: 1px maroon solid;
        height: 40px;
        margin-right: 30px;
        margin-bottom: 10px;
        margin-top: -10px;
        
        }
    .bk.float_box_invisible {
        display: none;
        }

    .bk.menu_box {
        justify-content: space-around;
                    }

    .picker {
        width: 300px;
    }
    
    .bk-root .bk-btn-group:not(.bk-vertical) > .bk-btn:first-child:not(:last-child), .bk-root .bk-btn-group:not(.bk-vertical) > .bk-btn:not(:first-child):last-child {
        border-radius: 15px;
        margin: 10px;
    }
    .bk-root .bk-btn-success, .bk-root .bk-btn-success.bk-active, .bk-root .bk-btn-success:hover{
        background-color: transparent;
        border: 0px;
        border-color: transparent;
        color: black;
        font-size: 14px;
        text-align: start;
        box-shadow: none;
    }
    .title .bk-input, .title .bk-input:focus{
        border: 0px;
        border-radious: 0px;
        font-size: 16px;
        font-weight : bold;
        outline: none;
        box-shadow: none;
    }
    .title .bk-input:hover{
        text-decoration : underline;
    }
    .dialog-content{
        background: white;
        margin: auto;
        z-index: 100002;
        padding: 0px;
        padding-bottom: 0px;
        position: fixed;
        top: 9%;
        left: 80%;
        bottom: 100%;
        right: 100%;
        
    }
    .dialog-container[aria-hidden='true'] {
        display: none;
    }
    .pnx-dialog-close {
        position: absolute;
        top: 0.5em;
        right: 0.5em;
        border: 0;
        padding: 0.25em;
        background-color: transparent;
        font-size: 1.5em;
        width: 1.5em;
        height: 1.5em;
        text-align: center;
        cursor: pointer;
        transition: 0.15s;
        border-radius: 50%;
        z-index: 10003;
    }
    .dialog-overlay{
        background-color: transparent !important;

    }
    .mdc-card{
        box-shadow: -1px -1px 1px -1px rgb(0 0 0 / 20%), -1px -1px 1px 0px rgb(0 0 0 / 14%), 0px -1px 3px 0px rgb(0 0 0 / 12%) !important;
        border: lightgray 1px solid !important;
    }
    .bk .tile-box{
        background-color: transparent !important;
        border-color: rgba(0,0,0,.12);
        cursor: move;

    }
    '''
    pn.extension('plotly','gridstack','ace',comms = 'ipywidgets', sizing_mode = 'stretch_width', raw_css = [css], notifications = True)
    
    pn.config.js_files["fontawesome"]="https://kit.fontawesome.com/121cf5990e.js"

    #pn.config.js_files["fontawesome"]="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.14.0/js/all.min.js"
    
    template = pn.template.MaterialTemplate(title='DB Experimental Data Analysis Framework')
    template.header_background ='maroon'
  
    icon1 = Icon(
            name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24" width="512" height="512"><path d="M22.849,7.68l-.869-.68h.021V2h-2v3.451L13.849,.637c-1.088-.852-2.609-.852-3.697,0L1.151,7.68c-.731,.572-1.151,1.434-1.151,2.363v13.957H9V15c0-.551,.448-1,1-1h4c.552,0,1,.449,1,1v9h9V10.043c0-.929-.42-1.791-1.151-2.363Zm-.849,14.32h-5v-7c0-1.654-1.346-3-3-3h-4c-1.654,0-3,1.346-3,3v7H2V10.043c0-.31,.14-.597,.384-.788L11.384,2.212c.363-.284,.869-.284,1.232,0l9,7.043c.244,.191,.384,.478,.384,.788v11.957Z"/></svg>
    """,#"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><!--! Font Awesome Pro 6.2.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M64 64c0-17.7-14.3-32-32-32S0 46.3 0 64V400c0 44.2 35.8 80 80 80H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H80c-8.8 0-16-7.2-16-16V64zm406.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L320 210.7l-57.4-57.4c-12.5-12.5-32.8-12.5-45.3 0l-112 112c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L240 221.3l57.4 57.4c12.5 12.5 32.8 12.5 45.3 0l128-128z"/></svg>""",
            fill_color="#800000",
        )
    btn1 = AwesomeButton(name=" Home", icon=icon1)

    icon2 = Icon(
            name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24" width="512" height="512"><title>03-Diagram</title><path d="M3,21.976a1,1,0,0,1-1-1V0H0V20.976a3,3,0,0,0,3,3H24v-2Z"/><rect x="5" y="12" width="2" height="7"/><rect x="10" y="10" width="2" height="9"/><rect x="15" y="13" width="2" height="6"/><rect x="20" y="9" width="2" height="10"/><polygon points="11 4.414 16 9.414 23.707 1.707 22.293 0.293 16 6.586 11 1.586 5.293 7.293 6.707 8.707 11 4.414"/></svg>
    """,#"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Pro 6.2.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M64 0C28.7 0 0 28.7 0 64V352c0 35.3 28.7 64 64 64H240l-10.7 32H160c-17.7 0-32 14.3-32 32s14.3 32 32 32H416c17.7 0 32-14.3 32-32s-14.3-32-32-32H346.7L336 416H512c35.3 0 64-28.7 64-64V64c0-35.3-28.7-64-64-64H64zM512 64V288H64V64H512z"/></svg>""",
            fill_color="#800000",
        )
    btn2 = AwesomeButton(name=" Metrics", icon=icon2)


    icon3 = Icon(
            name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 24 24" width="512" height="512"><path d="M5,6.5c0-.83,.67-1.5,1.5-1.5s1.5,.67,1.5,1.5-.67,1.5-1.5,1.5-1.5-.67-1.5-1.5Zm8,12.5v2h5v2H6v-2h5v-2H0V4C0,2.35,1.35,1,3,1H21c1.65,0,3,1.35,3,3v15H13Zm9-2V7.41l-7,7-4-4-6.59,6.59H22ZM2,4v12.59L11,7.59l4,4,7-7v-.59c0-.55-.45-1-1-1H3c-.55,0-1,.45-1,1Z"/></svg>
    """,#"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"><!--! Font Awesome Pro 6.2.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2022 Fonticons, Inc. --><path d="M543.8 287.6c17 0 32-14 32-32.1c1-9-3-17-11-24L512 185V64c0-17.7-14.3-32-32-32H448c-17.7 0-32 14.3-32 32v36.7L309.5 7c-6-5-14-7-21-7s-15 1-22 8L10 231.5c-7 7-10 15-10 24c0 18 14 32.1 32 32.1h32v69.7c-.1 .9-.1 1.8-.1 2.8V472c0 22.1 17.9 40 40 40h16c1.2 0 2.4-.1 3.6-.2c1.5 .1 3 .2 4.5 .2H160h24c22.1 0 40-17.9 40-40V448 384c0-17.7 14.3-32 32-32h64c17.7 0 32 14.3 32 32v64 24c0 22.1 17.9 40 40 40h24 32.5c1.4 0 2.8 0 4.2-.1c1.1 .1 2.2 .1 3.3 .1h16c22.1 0 40-17.9 40-40V455.8c.3-2.6 .5-5.3 .5-8.1l-.7-160.2h32z"/></svg>""",
            fill_color="#800000",
        )
    btn3 = AwesomeButton(name=" Dashboard", icon=icon3)
    #page_name = pn.widgets.RadioButtonGroup(name="Page", options=['🏠 Home','📈 Metrics','🖥️ Dashboard'], css_classes =['btn_radio'], orientation="vertical")
    template.sidebar.append(btn1)
    template.sidebar.append(btn2)
    template.sidebar.append(btn3)
    template.main.append(pn.Column())
    datetime_range_picker = w.DatetimeRangePicker(name='', value=(datetime.now() - timedelta(minutes = 30), datetime.now()), width = 300)
    dashboard_chart = []
    template.modal.append(pn.Column()) 
    modal_area = template.modal[0]
    modal = Modal(show_close_button = True)
    modal.style = css
    
    def home():
        m = pn.pane.image.PNG(
            'https://cdn-icons-png.flaticon.com/512/2821/2821637.png',
            width=500,
        )
        t =pn.pane.HTML("""<html>
        <head>
            <link href="https://fonts.googleapis.com/css2?family=Open+Sans&display=swap" rel="stylesheet">
            <style>
            body {
                font-family: 'Open Sans', sans-serif;
            
            }
            </style>
        </head>
        <body>
            <h2>Streamline your database monitoring and tuning</h2>
            <h3>within the comfort of your favorite data analytics platform: Jupyter Notebook!</h3></center>
        </body>
        </html>""")
        return [t,m]
    def get_time_range(tr):
                now = datetime.now()
                if tr == 'Last 30 minutes':
                    return (now - timedelta(minutes = 30), now)
                elif tr == 'Last hour':
                    return (now - timedelta(hours = 30), now)
                elif tr == 'Last 4 hours':
                    return (now - timedelta(hours = 4), now)
                elif tr == 'Last 12 hours':
                    return (now - timedelta(hours = 12), now)
                elif tr == 'Last 24 hours':
                    return (now - timedelta(hours = 24), now)
                elif tr == 'Custom':
                    return datetime_range_picker.value
    def dashboard():
        dashboard_list = []
        # top_btn_new = AwesomeButton(name="New Dashboard",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>'))
        # top_btn_new.css_classes= ['btn']
        # def add_dashboard(clicked_button):
        #     temp = Dashboard(len(dashboard_list)+1)
        #     template.main[0].append(temp.get())
        #     for board in dashboard_list:
        #         board.update_gridstack()
        #     dashboard_list.append(temp)
        #     temp.update_gridstack()

        # top_btn_new.on_click(add_dashboard)

        def simple_draw_chart(
                        metric='None', aggregate='Average', # metric
                        type='line', timerange = 'Custom', l = None):
            if l != None:
                chart = visualize_metrics_panel_plotly(l['metric'], l['filter'], l['split'], l['type'], get_time_range(timerange))
            else:
                chart = visualize_metrics_panel_plotly([(metric, aggregate)], None, None, type, get_time_range(timerange))
            #chart = chart.properties(width = 280, height = 120)
            metric_name = aggregate+' of '+metric.replace('_', ' ') 

            # showing the plot
            chart.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                autosize=False,
                width=300,
                height=150,
                showlegend=False,
            )

            title = metric_name
            #pn.pane.Markdown(f"### {metric_name}", margin = [5,10])

            return pn.pane.Plotly(chart)
        
        class Tile:
            def __init__(self, board_obj, title, contents=None):
                self.board_obj = board_obj                         
                self.title = HTML(f"<b><font color='#323130' size='3'>{title}")
                if len(title)==0:
                    self.title.width = 150
                self.btn_delete = AwesomeButton(name="",icon=Icon(name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="512" height="512"><g id="_01_align_center" data-name="01 align center"><path d="M22,4H17V2a2,2,0,0,0-2-2H9A2,2,0,0,0,7,2V4H2V6H4V21a3,3,0,0,0,3,3H17a3,3,0,0,0,3-3V6h2ZM9,2h6V4H9Zm9,19a1,1,0,0,1-1,1H7a1,1,0,0,1-1-1V6H18Z"/><rect x="9" y="10" width="2" height="8"/><rect x="13" y="10" width="2" height="8"/></g></svg>""", fill_color="#800000",), width = 20, visible = False, css_classes = ['small-btn'])
                self.btn_setting = AwesomeButton(name="",icon=Icon(name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" id="Outline" viewBox="0 0 24 24" width="512" height="512"><circle cx="2" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="22" cy="12" r="2"/></svg>""", fill_color="#800000",), width = 20, visible = False, css_classes = ['small-btn'])
                self.btn_delete.on_click(self.delete_tile)
                #self.btn_setting = w.Button(name = '⋯', css_classes = ['small-btn'], width = 20)
                self.btn_setting.on_click(self.open_setting_modal)
                self.bar = pn.Row(self.title, self.btn_delete, self.btn_setting, css_classes =['menu_box'])
                self.content = pn.Column(contents)
                self.setting_box = None
                
                #self.setting_modal = Modal(setting_box)
                self.tile = pn.Column(self.bar, self.content, modal, css_classes =['tile-box'], width_policy = 'fit', height_policy='fit')
            def delete_tile(self, clicked_button):
                self.board_obj.grid_delete_tile(id(self))
            def open_setting_modal(self, clicked_button):
                modal.clear()
                modal.append(self.setting_box)

                if modal.is_open:
                    modal.is_open= False
                else:
                    modal.is_open= True
            # def get_tile(self):
            #     return self.tile

        class MarkdownTile(Tile):
            def __init__(self, board_obj, title, contents = None):
                super().__init__(board_obj, title, contents)
                
                self.wtitle = w.TextInput(name='Title', placeholder='My title', value=title)
                self.wsubtitle = w.TextInput(name='subtitle', placeholder='My subtitle')
                self.editor = w.Ace(value="", language='markdown', height=300)
                self.done = w.Button(name='Done')
                self.reset = w.Button(name='Reset')
                self.done.on_click(self.update)
                self.reset.on_click(self.reset_value)
                
                self.bar = pn.Row(self.title, self.btn_delete, self.btn_setting, css_classes =['menu_box'])

                self.set_setting_box()
                #w.input.TextAreaInput(name = 'Content', )
            def update(self, clicked_button=None):
                if len(self.wtitle.value)>0 and len(self.wsubtitle.value)>0:
                    self.bar[0].object = f"<b><font color='#323130' size='3'>{self.wtitle.value}</b></font><br><font size='1'>{self.wsubtitle.value}</font>"
                elif len(self.wtitle.value)>0 and len(self.wsubtitle.value)==0:
                    self.bar[0].object =f"<b><font color='#323130' size='3'>{self.wtitle.value}"
                elif len(self.wtitle.value)==0 and len(self.wsubtitle.value)>0:                    
                    self.bar[0].object =f"<b><font color='#323130' size='3'>{self.wsubtitle.value}"
                
                self.content.clear()
                self.content.append(Markdown(self.editor.value))
              
            
            def reset_value(self, clicked_button):
                self.editor.value = ''


            def set_setting_box(self):
                print("Set markdown setting")
                self.setting_box = pn.Column(HTML("<h3><b>Edit Markdown"), 
                                        self.wtitle,
                                        self.wsubtitle,
                                        self.editor,
                                        pn.Row(self.done, self.reset),
                                        css_classes = ['modal-box'])
            
            
        
        class MetricTile(Tile):
            def __init__(self, board_obj, title, contents=None, dashboard = None):
                super().__init__(board_obj, title, contents)
                self.l = None
                if dashboard != None:
                    self.l = dashboard
                    contents = simple_draw_chart(l=dashboard_chart[dashboard])
                    self.content.clear()
                    self.content.append(contents)
                    
             
                
                self.metric = title
                
                if contents == None and dashboard == None:
                    contents = simple_draw_chart(self.metric, timerange = board_obj.time_range.value)
                    self.content.clear()
                    self.content.append(contents)
                    #self.title = HTML(f"<b><font color='#323130' size='3'>{contents[0]}")
                    
                self.checkbox = w.Checkbox(name='Override the dashboard time settings at the tile level.',value = False)
                self.s_timespan = w.Select(name='', options=['Last 30 minutes', 'Last hour', 'Last 4 hours'], disabled = True)
                self.s_granularity = w.Select(name='', options=['Automatic', '1 minute', '5 minutes'], disabled = True)
                self.s_tz = w.RadioButtonGroup(name = '', options = ['UTC', "Local"], disabled = True)
                self.set_setting_box()

            def update(self):
                contents = simple_draw_chart(self.metric, timerange = self.board_obj.time_range.value, l=dashboard_chart[self.l])
                self.content.clear()
                self.content.append(contents)



            def set_setting_box(self):
                def time_setting_widget(checkbox = self.checkbox):
                    if checkbox: 
                        self.s_timespan.disabled = False
                        self.s_granularity.disabled = False
                        self.s_tz.disabled = False
                        return pn.GridBox("Timespan", self.s_timespan, "Time granularity", self.s_granularity, "Show time as", self.s_tz, ncols =2)
                    else:
                        self.s_timespan.disabled = True
                        self.s_granularity.disabled = True
                        self.s_tz.disabled = True
                        return pn.GridBox("Timespan", self.s_timespan, "Time granularity", self.s_granularity, "Show time as", self.s_tz, ncols =2)

                self.setting_box = pn.Column(HTML("<h3><b>Configure tile settings"), 
                                        HTML("<b>Time settings"), 
                                        self.checkbox,
                                        pn.bind(time_setting_widget, checkbox = self.checkbox),
                                        HTML("<b>Resize"),
                                        w.Button(name = 'Copy'),
                                        w.Button(name = 'Remove'),
                                        css_classes = ['modal-box'])

        
        class ClockTile(Tile):
            def __init__(self, board_obj, title, contents=None):
                super().__init__(board_obj, title, contents)
                self.tz = w.Select(name='Location', options = pytz.all_timezones, value = "Asia/Seoul")
                self.tf = pn.widgets.Checkbox(name='Use 24 hours format', value = False)
                self.contents = self.initialize_clock(self.tz.value, self.tf.value)
                self.done = w.Button(name='Done')
                self.reset = w.Button(name='Reset')
                self.done.on_click(self.update)
                self.set_setting_box()
                self.content.clear()
                self.content.append(self.contents)

                pn.state.add_periodic_callback(self.update, period=60000, count=200)
                self.tile = pn.Column(self.bar, self.content, modal, css_classes =['tile-box'], width_policy = 'fit', height_policy='fit')
            

            def update(self, clicked_button=None):
                self.content.clear()
                self.content.append(self.initialize_clock(self.tz.value, self.tf.value))

            def initialize_clock(self, location, time_format):
                today = datetime.today()
                tz = pytz.timezone(location)
                utcnow = datetime.utcnow() 
                local_now = pytz.utc.localize(utcnow, is_dst=None).astimezone(tz)

                def day(date):
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    day = date.weekday()
                    return days[day]
                
                ampm = 'AM'
                hour = local_now.hour
                min = local_now.minute
                if time_format == True:
                    ampm = ''
                elif local_now.hour >= 12:
                    ampm = 'PM'
                    if local_now.hour > 12:
                        hour -= 12
                if location == "Asia/Seoul":
                    tz_full = 'Korea Standard Time'
                else:
                    tz_full = location
                clock = HTML(f"""<center>{tz_full}<br>
                            <b><font size="5em">{hour} : {min} {ampm}</font></b><br>
                            {day(today)}, {today.strftime("%B %d, %Y")}</center>""", width = 200, height = 100, margin=0, )
                return clock

            def set_setting_box(self):                
                self.setting_box = pn.Column(HTML("<h3><b>Edit clock"), 
                                        self.tz,
                                        self.tf,
                                        HTML("<hr>"),
                                        pn.Row(self.done, self.reset),
                                        css_classes = ['modal-box'])


            #def clock_widget(self, ):
                



        

        class Dashboard:
            def __init__(self, num):
                self.num = num
                self.title = pn.widgets.TextInput(value='New Chart', width = 400, css_classes = ['title'])
                self.top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>"""))
                self.top_btn_refresh.css_classes= ['btn']
                
                self.top_btn_edit = AwesomeButton(name="Edit",icon=Icon(name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="512" height="512"><g id="_01_align_center" data-name="01 align center"><path d="M5,19H9.414L23.057,5.357a3.125,3.125,0,0,0,0-4.414,3.194,3.194,0,0,0-4.414,0L5,14.586Zm2-3.586L20.057,2.357a1.148,1.148,0,0,1,1.586,0,1.123,1.123,0,0,1,0,1.586L8.586,17H7Z"/><path d="M23.621,7.622,22,9.243V16H16v6H2V3A1,1,0,0,1,3,2H14.758L16.379.379A5.013,5.013,0,0,1,16.84,0H3A3,3,0,0,0,0,3V24H18.414L24,18.414V7.161A5.15,5.15,0,0,1,23.621,7.622ZM18,21.586V18h3.586Z"/></g></svg>""", fill_color="#800000",))
                self.top_btn_edit.css_classes= ['btn']
                self.top_btn_edit.on_click(self.set_tile_gallery)

                self.metric_charts = pn.Card(title= 'Metric charts', visible = False, collapsible =False)
                #self.tile_gallery = pn.Column(self.metric_charts, visible= False, css_classes= ['float_box_invisible'])
                

                self.top_btn_delete = AwesomeButton(name="Delete",icon=Icon(name="icon",
            value="""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="512" height="512"><g id="_01_align_center" data-name="01 align center"><path d="M22,4H17V2a2,2,0,0,0-2-2H9A2,2,0,0,0,7,2V4H2V6H4V21a3,3,0,0,0,3,3H17a3,3,0,0,0,3-3V6h2ZM9,2h6V4H9Zm9,19a1,1,0,0,1-1,1H7a1,1,0,0,1-1-1V6H18Z"/><rect x="9" y="10" width="2" height="8"/><rect x="13" y="10" width="2" height="8"/></g></svg>""", fill_color="#800000",))
                self.top_btn_delete.css_classes= ['btn']
                self.top_bar = pn.Row(self.title, self.top_btn_edit, self.top_btn_delete, pn.layout.HSpacer(),pn.layout.HSpacer())

                self.auto_refresh = w.Select(name = 'Auto refresh', options = {'Off':'None',  'Every 5 minutes':300000, 
                                                                            'Every 10 minutes': 600000, 
                                                                            'Every 15 minutes':900000, 
                                                                           'Every 30 minutes':1800000}, width = 250)
                
                self.time = w.Button(name = 'Local Time: Custom', margin = [5,5], css_classes = ['btn_round'], width = 250)
                # self.time이 클릭되면 top_space에 box를 표시할거임
                                                                                   
                def set_auto_refresh(event):
                    if self.auto_refresh.value != 'None':
                        if 'dashboard_pc' in pc:
                            pc['dashboard_pc'].stop()                
                        pc['dashboard_pc'] = pn.state.add_periodic_callback(self.update_objects, period=self.auto_refresh.value, count=200)

                self.auto_refresh.param.watch(set_auto_refresh, 'value')            

                self.time_range = w.Select(name = 'Time range', options=['Last 30 minutes',
                                                                    'Last hour',
                                                                    'Last 4 hours',
                                                                    'Last 12 hours',
                                                                    'Last 24 hours', 'Custom'], value = 'Custom', width = 300)

                self.time_granularity = w.Select(name = 'Time granularity', options = ['Automatic', 
                                                                                    '1 minutes', 
                                                                                    '5 minutes', 
                                                                                    '15 minutes', 
                                                                                    '30 minutes', 
                                                                                    '1 hour', 
                                                                                    '6 hours',
                                                                                    '12 hours', 
                                                                                    '1 day'], width = 200)
                self.tz = w.RadioBoxGroup(name = 'Show time as', options = ['UTC','Local'], value='Local')
                def update_button(event):
                    self.box[1][1].name = f'{self.tz.value} Time: {self.time_range.value}'
                    if self.time_range.value == 'Custom' and len(self.time_setting[0]) == 1:
                        self.time_setting[0].append(datetime_range_picker)
                    elif self.time_range.value != 'Custom' and len(self.time_setting[0]) > 1:
                        del self.time_setting[0][1:]
                
                self.time_range.param.watch(update_button, 'value')
                self.tz.param.watch(update_button, 'value')
                
                self.top_space = pn.Row(pn.Row(pn.Spacer(height=99)))
                self.time_setting = pn.Row(pn.Column(self.time_range), pn.Column(self.time_granularity, self.tz), css_classes = ['float_box'], margin = [10,0])
                def show_time_setting(cb):
                    if len(self.top_space[0]) == 1: # spacer만 있을 경우?
                        #self.top_space.clear()
                        self.top_space[0] = self.time_setting
                    else:
                        #self.top_space.clear()
                        self.top_space[0] = pn.Row(pn.Spacer(height=99))
                self.time.on_click(show_time_setting)
                
                
                
                
                
                self.gstack = GridStack(width = 1500, height = 1500, ncols = 20, nrows = 16, sizing_mode = 'fixed',allow_resize = True, allow_drag = True)
              
                self.gstack_objects = self.gstack.objects
                self.gstack_dict = {}

                self.add_tile = w.Button(name = '+ Add tile', css_classes = ['btn'])
                def open_tile_gallery(button):
                    modal.clear()
                    modal.append(self.tile_box)
                    modal.is_open = True
                self.add_tile.on_click(open_tile_gallery)

                self.cached_gstack = None
                self.save_btn = w.Button(name = 'Save', width = 40, css_classes = ['btn-board'])
                self.clear_btn = w.Button(name = 'Clear', button_type = 'danger', width = 40)
                
                def clear(button):
                    self.update_gridstack()
                    
                    self.top_space[0] = pn.Spacer(height=100)
                    for i in self.gstack.objects:
                        self.gstack.objects[i][0][1].visible = False
                
                def save(button):
                    self.update_gridstack()

                    self.top_space[0] = pn.Spacer(height=100)
                    for i in self.gstack.objects:
                        self.gstack.objects[i][0][1].visible = False
                
                self.save_btn.on_click(save)
                self.clear_btn.on_click(clear)


                
                self.tile_list = w.RadioButtonGroup(name='', options={'🏠 Metrics chart':'Metrics chart', '⏰ Clock':'Clock', '📝 Markdown':'Markdown'},css_classes = ['btn_radio'], orientation='vertical',sizing_mode = 'fixed', height = 600, width = 300)
                self.add_btn = w.Button(name ='Add', css_classes = ['btn-board'], width = 100)
                self.add_btn.on_click(self.grid_add_tile)
                self.tile_box = pn.Column(Markdown("### Tile Gallery"), self.tile_list, self.add_btn, css_classes = ['modal-box'])
                self.initialize_gstack()
                

                self.box = pn.Column(self.top_bar,pn.Row(self.auto_refresh, self.time, pn.layout.HSpacer(width=1500)), self.top_space, pn.layout.VSpacer(height = 20), modal, self.gstack)

            def update_objects(self):
                update_data_pg_test()
                for i in self.gstack_dict:
                    self.gstack_dict[i][1].update()

            def update_gridstack(self):
                self.gstack = GridStack(objects = self.gstack_objects, width = 1500, height = 1500, ncols = 20, nrows = 16, sizing_mode = 'fixed',allow_resize = True, allow_drag = True)
                self.box = pn.Column(self.top_bar,pn.Row(self.auto_refresh, self.time, pn.layout.HSpacer(width=1500)), self.top_space, pn.layout.VSpacer(height = 20), modal, self.gstack)
                template.main[0][self.num-1] = self.box
                for i in self.gstack.objects:
                    self.gstack.objects[i][0][1].visible = True
                
            def grid_add_tile(self, clicked_button):
                type = self.tile_list.value 
                if type =='Metrics chart':
                    size = (3, 3)
                elif type == 'Clock':
                    size = (2, 2)
                elif type == 'Markdown':
                    size = (3, 2)
                else:
                    size = (1,1)
                #print("add_tile",self.gstack)
                i,j = self.find_empty(size)
                if i == None:
                    pn.state.notifications.send('There is no space left in the dashboard!', type='error', duration=3000)
                    print("No space")
                    return
                
                key = (i,j,i+size[0],j+size[1])
                value, id, tile_obj = self.initialize_tile(type)

                self.gstack_objects[key] = value
                self.update_gridstack()
                self.gstack_dict[id] = [key,tile_obj]

            
            def grid_delete_tile(self, delete_tile_id):
                delete_position, _ = self.gstack_dict[delete_tile_id]
                self.gstack_objects.pop(delete_position)
               
                self.update_gridstack()
                modal.is_open = False
                del self.gstack_dict[delete_tile_id]


            
            def initialize_tile(self, type):
                #print(type)
                if type == 'Metrics chart':
                    button = w.Button(name = 'Click to set metric charts', sizing_mode = 'stretch_both') 
                    button.on_click(self.initialize_metric_charts)
                    temp = MetricTile(self, "New metric", button)
                    return temp.tile, id(temp), temp
                elif type == 'Clock':        
                    temp = ClockTile(self, "")
                    return temp.tile, id(temp), temp
                elif type == 'Markdown':
                    temp = MarkdownTile(self, "Markdown")
                    return temp.tile, id(temp), temp
                   

            def initialize_gstack(self):
                temp = MarkdownTile(self, "Utilization")
                self.gstack[0:3, 0:2] = temp.tile
                self.gstack_dict[id(temp)] = [(0,0,3,2), temp]

                temp = MarkdownTile(self, "Performance")
                self.gstack[3:6, 0:2] = temp.tile
                self.gstack_dict[id(temp)] = [(3,0,6,2), temp]

                temp = MarkdownTile(self, "Index") 
                self.gstack[6:9, 0:2] = temp.tile
                self.gstack_dict[id(temp)] = [(6,0,9,2), temp]


                temp = MetricTile(self, "Deadlocks")
                self.gstack[3:6, 2:5] = temp.tile
                self.gstack_dict[id(temp)] = [(3,2,6,5), temp]

                temp = MetricTile(self, "Backends")
                self.gstack[0:3, 2:5] = temp.tile
                self.gstack_dict[id(temp)] = [(0,2,3,5), temp]

                temp = MetricTile(self, "Transactions Committed")
                self.gstack[3:6, 5:8] = temp.tile
                self.gstack_dict[id(temp)] = [(3,5,6,8), temp]

                temp = MetricTile(self, "idx_scan")
                self.gstack[6:9, 2:5] = temp.tile
                self.gstack_dict[id(temp)] = [(6,2,9,5), temp]

                temp = MetricTile(self, "seq_scan")
                self.gstack[6:9, 5:8] = temp.tile
                self.gstack_dict[id(temp)] = [(6,5,9,8), temp]
                size = (3,3)
                for i in range(len(dashboard_chart)):
                    i,j = self.find_empty(size)                
                    key = (i,j,i+size[0],j+size[1])
                    temp = MetricTile(self, dashboard_chart[i]['name'], dashboard = i)
                    self.gstack[key[0]:key[2], key[1]:key[3]] = temp.tile
                    self.gstack_dict[id(temp)] = [key, temp]



                #print(self.gstack.grid)
                self.gstack_objects =  self.gstack.objects 
                #print("after initialize")
                #print(self.gstack)
                
                

            def initialize_metric_charts(self, button):
                print("HELLO")

            def set_tile_gallery(self, clicked_button):
                #self.cached_gstack = self.gstack.clone()
                modal.clear()
                modal.append(self.tile_box)
               
                if modal.is_open:
                    modal.is_open = False
                else:
                    modal.is_open = True
                
                for i in self.gstack.objects:
                    self.gstack.objects[i][0][1].visible = True
                    self.gstack.objects[i][0][2].visible = True
                self.top_space.clear()
                self.top_space.append(pn.Row(self.add_tile, None, None, self.save_btn, None, height = 100))
            
            def find_empty(self, size):
                grid = self.gstack.grid
                #print(grid)
                r,c = grid.shape
                for i in range(r-size[0]+1):
                    for j in range(c-size[1]+1):
                        print(i,j)
                        if np.sum(grid[i:i+size[0], j:j+size[1]], axis=None) == 0:
                            return i, j
                return None, None

                
            def get(self):
                return self.box

        temp = Dashboard(1)
        dashboard_list.append(temp)
        return [
            temp.box 
        ]
        #)

    

    # def metrics_dashboard():
    #     # Top bar
    #     top_btn_new = AwesomeButton(name="New chart",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>'))
    #     top_btn_new.css_classes= ['btn']
    #     top_btn_new.disabled = True
    #     top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>"""))
    #     top_btn_refresh.css_classes= ['btn']
    #     top_bar = pn.Row(top_btn_new,top_btn_refresh,pn.layout.HSpacer(), None, datetime_range_picker)    
        
    #     #template.main.append(
    #     template.main[0][:] = [
    #         top_bar,
    #         Chart(1, True).chart(),    
    #     ]

    #     #)
    charts = [None for i in range(5)]
    def metrics():
        class Chart():
            def __init__(self, num, dashboard):
                self.name = ''
                self.num = num         
                charts[self.num-1] = self   
                l = get_metrics_info()
                self.c = None
                self.metrics = AwesomeButton(name="Add metric",icon=Icon(name="",value='<i class="fas fa-plus"></i>' ,fill_color="#800000",))
                self.metrics.margin = [15,15]
                self.metrics.css_classes= ['btn']
                self.metrics.on_click(self.add_metric)
                self.trigger = pn.widgets.Checkbox(name='', visible = False, value = False)

                self.filter = AwesomeButton(name="Add filter",icon=Icon(name="",value='<i class="fas fa-filter"></i>', fill_color="#800000",), disabled = True)
                self.filter.margin = [15,15]
                self.filter.css_classes= ['btn']
                self.filter.on_click(self.add_filter)

                self.splitting = AwesomeButton(name="Add splitting",icon=Icon(name="",value='<i class="fas fa-wrench"></i>', fill_color="#800000",), disabled = True)
                self.splitting.margin = [15,15]
                self.splitting.css_classes= ['btn']
                self.splitting.on_click(self.add_splitting)
                #self.splitting.on_click(self.add_metric)


                self.select_metrics =  w.Select(name = 'Metric', groups=l, value = 'None', sizing_mode = 'fixed')
                self.select_agg = w.Select(name = 'Aggregation', value = 'None', options=['None','Average','Min','Max','Sum'], sizing_mode = 'fixed')
                self.select_agg.css_classes= ['btn']
                self.metric_bar = pn.Row(self.select_metrics, self.select_agg, css_classes = ['float_box_invisible'])
                self.metric_bar[0].visible = False
                self.metric_bar[1].visible = False
                self.metric_list = []
                self.chart_dict = {'metric':None, 'filter':None, 'split':None, 'type':None}

                self.select_property = w.Select(name = 'Property', value = 'None', options=['None'], sizing_mode = 'fixed', width = 250)
                self.select_operator = w.Select(name = 'Operator', value = '=', options=['='], sizing_mode = 'fixed', width = 100)
                self.select_values = w.CheckBoxGroup( inline = False, width = 250)
                self.select_values_name = pn.pane.HTML("values", visible = False)
                self.filter_bar = pn.Row(self.select_property, self.select_operator, pn.Column(self.select_values_name,self.select_values), css_classes = ['float_box_invisible'])
                self.select_property.visible = False
                self.select_operator.visible = False
                self.select_values_name.vislbie = False
                self.select_values.visible = False
                
                self.select_split_values = w.Select(name = 'Values', value = 'None', options=['None'], sizing_mode = 'fixed')
                self.select_limit = w.input.NumberInput(name = 'Limit', value = 10, start = 1, stop = 50, step = 1, width = 100, sizing_mode = 'fixed', disabled = True)
                self.select_sort = w.Select(name = 'Sort', value = 'Ascending', options=['Ascending', 'Descending'], sizing_mode = 'fixed', width = 200, disabled = True)

                self.split_bar = pn.Row(self.select_split_values, self.select_limit, self.select_sort, css_classes = ['float_box_invisible'])
                self.select_split_values.visible = False
                self.select_limit.visible = False
                self.select_sort.visible = False
                
                self.chart_filter = None
                self.chart_split = None

                self.ctop_btn_board = AwesomeButton(name="Pin to dashboard",icon=Icon(name="",value='<i class="fas fa-bookmark"></i>', fill_color="#800000",))
            
                self.ctop_btn_board.margin = [15,15]
                if dashboard:
                    self.ctop_btn_board.on_click(self.add_dashboard) ## 다르게
                    self.ctop_btn_board.css_classes= ['btn-focus']
                else:
                    self.ctop_btn_board.on_click(self.add_dashboard)
                    self.ctop_btn_board.css_classes= ['btn']

                self.chart_setting_btn = AwesomeButton(icon=Icon(name="",value='<i class="fas fa-align-justify"></i>', fill_color="#800000",), sizing_mode = "fixed", width = 40, height = 40)
                self.chart_setting_btn.css_classes= ['btn']
                self.chart_setting_btn.margin = [15,15]
                self.chart_setting_btn.on_click(self.set_chart_setting)

                self.chart_type = w.Select(name = '', options={'Line chart':'line', 'Bar chart':'bar', 'Area chart':'area', 'Scatter chart':'scatter'}, margin = [15,15])
                self.chart_top_bar = pn.Row(self.metrics, self.filter, self.splitting, self.chart_type, self.ctop_btn_board, self.chart_setting_btn, background='WhiteSmoke', css_classes = ['box'])
                self.chart_col = pn.Column()
                self.aggregate = []
                self.metric_container = pn.Row()
                self.filter_container = pn.Row()
                self.split_container = pn.Row()
                self.selected_element_bar = pn.Row(self.metric_container, self.filter_container, self.split_container) # metric, filter, split
                self.cached_chart = None
            #     self.initialize_chart_setting()
                
            # def initialize_chart_setting(self):
                self.y_min = w.FloatInput(name = 'Min value', placeholder='Enter your value...', width = 200)
                self.y_max = w.FloatInput(name = 'Max value', placeholder='Enter your value...', width = 200)
                self.b_min = w.Button(name = 'Reset ', button_type = 'light', width = 60, align = 'center')
                self.b_max = w.Button(name = 'Reset ', button_type = 'light', width = 60, align = 'center')

                self.r_type = w.RadioButtonGroup(
                    name='Chart type', options=['line', 'area', 'bar', 'scatter', 'table'], button_type='primary')

                self.r_title = w.RadioButtonGroup(
                    name='Chart title', options=['Auto', 'Custom', 'None'], button_type='primary')

                self.l_visible = w.RadioButtonGroup(options=['Visible', 'Hidden'], button_type='primary', width = 150, value = 'Visible')
                self.l_position = w.RadioButtonGroup(options=['Bottom', 'Right'], button_type='primary', width = 150, value = 'Bottom')
                self.l_size = w.RadioButtonGroup(options=['Compact', 'Full'], button_type='primary', width = 150, value = 'Full')
                self.l_grid = pn.GridBox(
                    'Visibility',self.l_visible,
                    'Position',self.l_position,
                    'Size',self.l_size,
                    ncols=2, align = 'center')
                self.btn_apply = w.Button(name = 'Apply', button_type = 'default', width = 90)
                self.btn_apply.on_click(self.apply_chart_setting)
                self.box = pn.WidgetBox('<font size="5em">⚙️ Chart settings</font>',
                                #'<hr width="300px"><b>Chart type<b/>', 
                                #r_type, 
                                '<hr width="300px"><b>Chart title<b/>',
                                self.r_title,
                                '<div style="margin: 0px 0px 0px 10px;">Title created from your selection of metrics, filters, and grouping.</div><hr width="300px">',
                                '<b>Y-axis range<b/>',
                                pn.Row(self.y_min, self.b_min), pn.Row(self.y_max, self.b_max),
                                '<hr width="300px"><b>Legends<b/>',
                                self.l_grid, self.btn_apply, width = 300)
            
            def add_dashboard(self, clicked_button):
                dashboard_chart.append(self.chart_dict)
                

            def apply_chart_setting(self, clicked_button):
                #print("APPLY")
                self.trigger.value = True

        

            def set_chart_setting(self, clicked_button):
                
                modal_area.clear()
                modal_area.append(self.box)
                template.open_modal()
                #print("set se")

            def add_metric(self, clicked_button):
            
                if self.metric_bar[0].visible:
                    self.metric_bar.css_classes = ['float_box_invisible']
                    for i in self.metric_bar:
                        i.visible = False
                else:
                    self.metric_bar.css_classes = ['float_box']
                    
                    for i in self.metric_bar:
                        i.visible = True
                        i.value = 'None'
            
            def add_filter(self, clicked_button):
                print("ADD filter")
                if self.filter_bar[0].visible:
                    self.filter_bar.css_classes = ['float_box_invisible']
                    for i in self.filter_bar:
                        i.visible = False
                    self.select_values_name.vislbie = False
                    self.select_values.visible = False
                else:
                    print("ADD filter visible?")
                    self.filter_bar.css_classes = ['float_box']
                    for i in self.filter_bar:
                        i.visible = True
                    self.select_values.value = self.select_values.options
                    self.select_values_name.vislbie = True
                    self.select_values.visible = True
            
            def add_splitting(self, clicked_button):
                if self.split_bar[0].visible:
                    self.split_bar.css_classes = ['float_box_invisible']
                    for i in self.split_bar:
                        i.visible = False
                else:
                    self.split_bar.css_classes = ['float_box']
                    for i in self.split_bar:
                        i.visible = True

            def _get_metrics(self):
                return get_metrics_info(self.metrics)
            
            def set_selected_element_bar(self): #for visualize
                #self.selected_element_bar.clear()
                self.metric_container.clear()
                self.filter_container.clear()
                self.split_container.clear()

                for metric in self.metric_list:
                    name = pn.pane.HTML("<center>"+metric[1]+' of '+metric[0], align = 'center',width=200)
                    temp = w.Button(name = '✖', message = (0,metric), css_classes = ['small-btn'], width = 20, margin=[-3,0])
                    temp.on_click(self.remove_metric)
                    self.metric_container.append(pn.Row(name,temp, sizing_mode = 'fixed', width=250, css_classes = ['float_box']))
                    
                if self.chart_filter != None:
                    name = pn.pane.HTML("<center>"+self.chart_filter[0]+self.chart_filter[1]+', '.join(self.chart_filter[2]), align = 'center',width=200)
                    temp = w.Button(name = '✖', message = (1,copy.deepcopy(self.chart_filter)), css_classes = ['small-btn'], width = 20, margin=[-3,0])
                    temp.on_click(self.remove_metric)        
                    self.filter_container.append(pn.Row(name,temp, sizing_mode = 'fixed', width=250, css_classes = ['float_box']))
                
                if self.chart_split != None:
                    name = pn.pane.HTML("<center>split by "+self.chart_split[0], align = 'center', width=150)
                    temp = w.Button(name = '✖', message = (2,copy.deepcopy(self.chart_split)), css_classes = ['small-btn'], width = 20, margin=[-3,0])
                    temp.on_click(self.remove_metric)        
                    self.split_container.append(pn.Row(name,temp, sizing_mode = 'fixed', width=200, css_classes = ['float_box']))

            def remove_metric(self, event):
                print("REMOVE")
                e = event.obj.message # (숫자, metric or filter or split)
                if e[0] == 0:
                    for m in self.metric_container: # Row
                        print("Remove metric")
                        print("m",m)
                        print("e",e)
                        print(m[1].message)
                        if m[1].message == e:
                            print("RERE")
                            print(m)
                            print(self.metric_container)
                            self.metric_container.remove(m)
                            self.metric_list.remove(e[1])
                elif e[0] == 1:
                    self.filter_container.clear()
                    self.chart_filter = None
                    self.select_property.value = 'None'
                elif e[0] == 2:
                    self.split_container.clear()
                    self.chart_split = None
                    self.select_split_values.value = 'None'
                    self.metrics.disabled = False
                
                self.trigger.value = True

            def draw_chart(self,
                            metric='None', aggregate='None', # metric
                            property = 'None', operator = '=', value =[], # filter
                            s_value = 'None', limit = 0, sort = 'Ascending', # split
                            type='line', timerange='Custom', trigger=False, setting = False):
                
                print("DRAW")
               
                #timerange = get_time_range(timerange)
                
                if not (metric == 'None' or aggregate == 'None'):
                    if len(self.metric_list)==0 or self.metric_list[-1] != (metric,aggregate):
                        self.metric_list.append((metric,aggregate))

                if not (property == 'None' or len(value)==0):
                    self.chart_filter = (property, operator, value)
            
                        
                if not (s_value == 'None'):
                    self.chart_split = (s_value, limit, sort)
                    self.metrics.disabled = True
                    

                if trigger == False and self.chart_dict['type'] == type and self.chart_dict['metric'] != None and set(self.chart_dict['metric'])==set(self.metric_list) and self.chart_dict['filter'] == self.chart_filter and self.chart_dict['split'] == self.chart_split and auto_refresh.value =='None':
                    return pn.Column(self.selected_element_bar, pn.panel(self.cached_chart))
                
                if len(self.metric_list) == 0:
                    return pn.Spacer(height = 1000)
                
                option_dict = {'y_min':self.y_min.value,
                                'y_max':self.y_max.value,
                                'l_visible':self.l_visible.value,
                                'l_position':self.l_position.value,
                                'l_size':self.l_size.value}
                
                print(option_dict)

                chart = visualize_metrics_panel_plotly(self.metric_list, self.chart_filter, self.chart_split, self.chart_type.value, timerange, option_dict)
                self.trigger.value = False
                # Chart setting widget value 설정해야함!!!
                

                metric_names = [a+' of '+m.replace('_', ' ') for (m,a) in self.metric_list]
                if len(metric_names) == 1:
                    self.name = metric_names[0]
                elif len(metric_names) >= 2:
                    self.name = ', '.join(metric_names[0:3])
                    if len(metric_names) > 4:
                        self.name += f", and {len(metric_names)-3} other metrics" 
                #print(self.num)
                if self.num>1 or len(metric_names)>=1:
                    template.main[0][self.num-1].title = self.name
            

                if not (metric == 'None' or aggregate == 'None'): 
                # initialize
                    self.metric_bar.css_classes = ['float_box_invisible']
                    self.select_metrics.visible = False
                    self.select_agg.visible = False
                    self.select_metrics.value = 'None'
                    self.select_agg.value = 'None'
                    
                if not (property == 'None' or operator == '=' or value ==[]):
                    self.filter_bar.css_classes = ['float_box_invisible']
                    self.select_property.value = "None"
                    self.select_operator.value = '='
                    self.select_value.value = ()
                    
                    
                self.set_selected_element_bar()
                self.cached_chart = chart
                self.chart_dict['metric'] = copy.deepcopy(self.metric_list)
                self.chart_dict['filter'] = self.chart_filter
                self.chart_dict['split'] = self.chart_split
                self.chart_dict['type'] = type
                self.chart_dict['name'] = self.name
                

                ml = [m for (m,a) in self.metric_list]
                if len(ml)>0:
                    MULTI_DIM_METRICS = [
                        ["Sessions"], ["Waiting Sessions"],
                        ["Backends", 
                        "Deadlocks",
                        "Disk Blocks Hit",
                        "Disk Blocks Read",
                        "Temporary Files",
                        "Temporary Files Size", 
                        "Total Transactions", 
                        "Transactions Committed", 
                        "Transactions Rolled back",
                        "Tuples Deleted",
                        "Tuples Fetched", 
                        "Tuples Inserted", 
                        "Tuples Returned", 
                        "Tuples Updated",]
                    ]
                    for i,c in enumerate(MULTI_DIM_METRICS):  
                        if len(set(ml)-set(c))==0:
                            if i == 0:
                                self.select_property.options = ['None','State']
                                self.select_values.options = STATE
                                self.select_split_values.options = ['None','State']
                            elif i == 1:
                                self.select_property.options = ['None','Wait event type']
                                self.select_values.options = WAIT_EVENT_TYPE
                                self.select_split_values.options = ['None','Wait event type']
                            elif i == 2:
                                self.select_property.options = ['None','Database name']
                                self.select_values.options = DAT_NAMES
                                self.select_split_values.options= ['None','Database name']
                                
                            self.filter.disabled =False
                            self.splitting.disabled = False
                            self.select_values.disabled = False
                            break
                        else:
                            self.filter.disabled =True
                            self.splitting.disabled =True
                
                return pn.Column(self.selected_element_bar, pn.pane.Plotly(chart))
            
            def get_title(self, metric, aggregate, trigger):
                if trigger:
                    self.trigger.value = False
                if not (metric == 'None' or aggregate == 'None'):
                    return pn.pane.Markdown(f"### {self.name}", margin = [5,10])

                if len(self.metric_list) == 0:
                    return pn.pane.Markdown(f"### Empty Chart", margin = [5,10])
                else:
                    metric_names = [a+' of '+m.replace('_', ' ') for (m,a) in self.metric_list]
                    if len(metric_names) == 1:
                        self.name = metric_names[0]
                    elif len(metric_names) >= 2:
                        self.name = ', '.join(metric_names[0:3])
                        if len(metric_names) > 4:
                            self.name += f", and {len(metric_names)-3} other metrics" 
                    return pn.pane.Markdown(f"### {self.name}", margin = [5,10])

            def chart(self):
                self.chart_col = pn.Column(pn.bind(self.draw_chart, 
                                                    metric = self.select_metrics, aggregate = self.select_agg, 
                                                    property = self.select_property, operator = '=', value = self.select_values,
                                                    s_value = self.select_split_values, limit = 10, sort = 'Ascending',
                                                    type = self.chart_type, 
                                                    timerange = datetime_range_picker, 
                                                    trigger = self.trigger, setting = self.btn_apply))
                self.c = pn.Card(pn.bind(self.get_title, metric = self.select_metrics, aggregate = self.select_agg, trigger = self.trigger), self.chart_top_bar, self.metric_bar, self.filter_bar, self.split_bar, self.chart_col, collapsible = False, hide_header = True)

                return self.c
        # Top bar
        top_btn_new = AwesomeButton(name="New chart",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>', fill_color="#800000",))
        top_btn_new.css_classes= ['btn']
        

        top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>""", fill_color="#800000",))
        top_btn_refresh.css_classes= ['btn']

        time_range = w.Select(name = 'Time range', options=['Last 30 minutes',
                                                            'Last hour',
                                                            'Last 4 hours',
                                                            'Last 12 hours',
                                                            'Last 24 hours', 'Custom'], value = 'Custom', width = 300)

        time_granularity = w.Select(name = 'Time granularity', options = ['Automatic', 
                                                                            '1 minutes', 
                                                                            '5 minutes', 
                                                                            '15 minutes', 
                                                                            '30 minutes', 
                                                                            '1 hour', 
                                                                            '6 hours',
                                                                            '12 hours', 
                                                                            '1 day'], width = 200)
        tz = w.RadioBoxGroup(name = 'Show time as', options = ['UTC/GMT','Local'], value='Local')

        auto_refresh = w.Select(name = 'Auto refresh', options = {'Off':'None',  '1 minutes':60000, 
                                                                            '5 minutes':300000, 
                                                                            '15 minutes':900000, 
                                                                           '30 minutes':1800000}, width = 200)
        #update_func = update_data_pg_test()
      
                                                                           
        def set_auto_refresh(event):
            if auto_refresh.value != 'None':
                if 'metrics_refresh' in pc:
                    pc['metrics_refresh'].stop()                
                pc['metrics_refresh'] = pn.state.add_periodic_callback(refresh, start = True, period=auto_refresh.value, count=200)
                print('set refresh')
            else:
                if 'metrics_refresh' in pc:
                    pc['metrics_refresh'].stop()
                    del pc['metrics_refresh'] 
        auto_refresh.param.watch(set_auto_refresh, 'value')


        def custom_time(event):
            if time_range.value != 'Custom':
                datetime_range_picker.disabled = True
                datetime_range_picker.value = get_time_range(time_range.value)
            else:
                datetime_range_picker.disabled = False
        
        time_range.param.watch(custom_time, 'value')



        top_bar = pn.Row(top_btn_new,pn.Column(top_btn_refresh, auto_refresh),pn.layout.HSpacer(), pn.layout.HSpacer(), pn.Column(time_granularity, tz),pn.Column(time_range,datetime_range_picker))

        def new_chart(clicked_button):
            num = len(template.main[0])
            chart = Chart(num, False)
            template.main[0].append(chart.chart())

        def refresh(clicked_button=None):
            print('refresh')
            #asyncio.run(update_func)
            print("before update", datetime.now())
            update_data_pg_test()
            print("after update", datetime.now())
            if time_range.value != 'Custom':
                datetime_range_picker.value = get_time_range(time_range.value)
            charts_copy = [i for i in charts if i != None]
            for chart in charts_copy:
                chart.trigger.value = True

        top_btn_new.on_click(new_chart)
        top_btn_refresh.on_click(refresh)
        


        #template.main.append(
        return [
            top_bar,
            Chart(1, False).chart(),    
        ]
        #)
    

    from functools import partial


   


    PAGES = {
        'home': home,'metrics': metrics, 'dashboard': dashboard,
    }
    #@pn.depends(page_name, watch=True)
    def change_page(event=None, page_name='home'):
        page_func = PAGES[page_name]
        template.main[0][:] = page_func()
    
    btn1.on_click(partial(change_page, page_name = 'home'))
    btn2.on_click(partial(change_page, page_name = 'metrics'))
    btn3.on_click(partial(change_page, page_name = 'dashboard'))
    
    change_page(page_name = "home")

        #return template
    template.show()

