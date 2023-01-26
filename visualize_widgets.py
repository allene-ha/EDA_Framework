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
import datetime
from awesome_panel_extensions.models.icon import Icon
from awesome_panel_extensions.widgets.button import AwesomeButton
from panel.pane import HTML, Markdown
from panel.layout.gridstack import GridStack
from panel_modal import Modal



plt.style.use('seaborn-notebook')
DATE_BOUNDS = (datetime.datetime(2023, 1, 19, 12, 30, 0), datetime.datetime(2023, 1, 19, 13, 30, 0)) # default 15


def visualize_panel():    

    import_and_update_data()
    DAT_NAMES = get_dat_names()
    #print(DAT_NAMES)
    STATE = ['active','idle','idle in transaction','idle in transaction (aborted)','fastpath function call', 'disabled']
    WAIT_EVENT_TYPE = ['Activity','BufferPin','Client','Extension','IO','IPC','Lock','LWLock','Timeout']

    css = '''
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
        background-color: transparent;
        box-shadow: inset 0px 0px 0px ;
    }
    .btn .bk-btn-group button:disabled {
        background-color: transparent;
        box-shadow: inset 0px 0px 0px ;
    }
    .btn_round .bk-btn-group button {
        border: 1px maroon solid;
        background-color: white;
        border-radius: 15px;
        height: 30px;
        font-size: 100%;
        text-align: center; 


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
        display: flex;
        
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
    .bk .tile-box{
        background-color: transparent !important;
        border-color: rgba(0,0,0,.12);
        cursor: move;

    }
    '''
    pn.extension('vega','gridstack',comms = 'ipywidgets', sizing_mode = 'stretch_width', raw_css = [css])
    
    pn.config.js_files["fontawesome"]="https://kit.fontawesome.com/121cf5990e.js"

    #pn.config.js_files["fontawesome"]="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.14.0/js/all.min.js"
    
    template = pn.template.MaterialTemplate(title='DB Experimental Data Analysis Framework')
    template.header_background ='maroon'
  
    
    page_name = pn.widgets.RadioButtonGroup(name="Page", options=['🏠 Home','📈 Metrics','🖥️ Dashboard'], css_classes =['btn_radio'], orientation="vertical")
    template.sidebar.append(page_name)
    template.main.append(pn.Column())
    datetime_range_picker = w.DatetimeRangePicker(name='Time range', value=DATE_BOUNDS, width = 400)
    dashboard_chart = []
    template.modal.append(pn.Column()) 
    modal_area = template.modal[0]
    modal = Modal(show_close_button = True)
    modal.style = css
    
    def home():
        return [Markdown("# 🏠"),HTML("<a href='https://bitbucket.org/postech_dblab/eda_framework_visualization/src/main/'>Visit Github!</a>"),]

    def dashboard():
        dashboard_list = []
        top_btn_new = AwesomeButton(name="New Dashboard",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>'))
        top_btn_new.css_classes= ['btn']
        def add_dashboard(clicked_button):
            temp = Dashboard(len(dashboard_list)+1)
            template.main[0].append(temp.get())
            for board in dashboard_list:
                board.update_gridstack()
            dashboard_list.append(temp)
            temp.update_gridstack()

        top_btn_new.on_click(add_dashboard)

        def simple_draw_chart(
                        metric='None', aggregate='Average', # metric
                        type='line', timerange=datetime_range_picker.value):
            
            chart = visualize_metrics_panel([(metric, aggregate)], None, None, type, timerange)
            chart = chart.properties(width = 323, height = 164)
            metric_name = aggregate+' of '+metric.replace('_', ' ') 
            
            
            title = metric_name
            pn.pane.Markdown(f"### {metric_name}", margin = [5,10])

            return [title, pn.panel(chart)]
        

        class Tile:
            def __init__(self, board_obj, title, contents=None):
                self.gstack = board_obj

                         
                self.title = HTML(f"<b><font color='#323130' size='3'>{title}", width = 300)
                
                self.btn_delete = w.Button(name = '🗑', css_classes = ['small-btn'], width = 20, visible = False)

                self.btn_delete.on_click(self.delete_tile)
                self.btn_setting = w.Button(name = '⋯', css_classes = ['small-btn'], width = 20)
                self.btn_setting.on_click(self.open_setting_modal)
                self.bar = pn.Row(self.title, self.btn_delete, self.btn_setting)
                self.content = pn.Column()
                self.content.append(contents)
                self.checkbox = w.Checkbox(name='Override the dashboard time settings at the tile level.',value = False)
                self.s_timespan = w.Select(name='', options=['Past 30 minutes', 'Past hour', 'Past 4 hours'], disabled = True)
                self.s_granularity = w.Select(name='', options=['Automatic', '1 minute', '5 minutes'], disabled = True)
                self.s_tz = w.RadioButtonGroup(name = '', options = ['UTC', "Local"], disabled = True)
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
                #self.setting_modal = Modal(setting_box)
                self.tile = pn.Column(self.bar, self.content, modal, css_classes =['tile-box'], )
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

        class Dashboard:
            def __init__(self, num):
                self.num = num

                self.title = pn.widgets.TextInput(value='New Chart', width = 400, css_classes = ['title'])

                self.top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>"""))
                self.top_btn_refresh.css_classes= ['btn']

                self.top_btn_clone = AwesomeButton(name="Clone",icon=Icon(name="",value="""<i class="fas fa-copy"></i>"""))
                self.top_btn_clone.css_classes= ['btn']

                self.top_btn_edit = AwesomeButton(name="Edit",icon=Icon(name="",value="""<i class="fas fa-pencil"></i>"""))
                self.top_btn_edit.css_classes= ['btn']
                self.top_btn_edit.on_click(self.set_tile_gallery)

                self.metric_charts = pn.Card(title= 'Metric charts', visible = False, collapsible =False)
                #self.tile_gallery = pn.Column(self.metric_charts, visible= False, css_classes= ['float_box_invisible'])
                

                self.top_btn_delete = AwesomeButton(name="Delete",icon=Icon(name="",value="""<i class="fas fa-trash"></i>"""))
                self.top_btn_delete.css_classes= ['btn']
                self.top_bar = pn.Row(self.title, top_btn_new, self.top_btn_edit, self.top_btn_clone, self.top_btn_delete)

                self.top_w = w.RadioButtonGroup(options=['Auto refresh: Off', 'UTC Time: Past 24 hours'], sizing_mode = 'fixed', width = 200, height = 30)
                self.top_space = pn.Row(pn.Spacer(height=100))
                
                self.gstack = GridStack(width = 1250, height = 1000, ncols = 20, height_policy ='min', width_policy = 'min' ,allow_resize = True, allow_drag = True)
                #print("initialize")
                #print(self.gstack)
                self.gstack_objects = self.gstack.objects
                self.gstack_dict = {}

                self.add_tile = w.Button(name = '+ Add tile', css_classes = ['btn'])
                def open_tile_gallery(button):
                    modal.clear()
                    modal.append(self.tile_box)
                    modal.is_open = True
                self.add_tile.on_click(open_tile_gallery)

                self.cached_gstack = None
                self.save_btn = w.Button(name = 'Save', button_type = 'primary', width = 40)
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
                self.add_btn = w.Button(name ='Add', button_type= 'primary', width = 60,align='center')
                self.add_btn.on_click(self.grid_add_tile)
                self.tile_box = pn.Column(Markdown("### Tile Gallery"), self.tile_list, self.add_btn, css_classes = ['modal-box'])
                # self.tile_modal = Modal(pn.Column(Markdown("### Tile Gallery"), self.tile_list, self.add_btn), show_close_button = True)
                # self.tile_modal.style = css
                self.initialize_gstack()
                

                self.box = pn.Column(self.top_bar,self.top_w, self.top_space, self.gstack, modal)
           
            def update_gridstack(self):
                #print("before assigning new obj")
                #print(self.gstack)
                self.gstack = GridStack(objects = self.gstack_objects, width = 1250, height = 1000, ncols = 20, height_policy ='fit', width_policy = 'fit' ,allow_resize = True, allow_drag = True)
                #print("after assigning new obj")
                #print(self.gstack)
                self.box = pn.Column(self.top_bar,self.top_w, self.top_space, self.gstack, modal)
                #print(template.main[0][0])
                template.main[0][self.num-1] = self.box
                #print(self.gstack.grid)
                
            def grid_add_tile(self, clicked_button):
                size = (3, 3)
                #print("add_tile",self.gstack)
                i,j = self.find_empty(size)
                if i == None:
                    print("No space")
                    return
                #print(i,j)
                #print("after find empty",self.gstack)
                key = (i,j,i+size[0],j+size[1])
                #print(key)
                value = self.initialize_tile(self.tile_list.value)# 바로 여기 !!!
                #print("after initialize_tile",self.gstack)
                #print(value) # value 가 none????
                self.gstack_objects[key] = value
                #print("after object",self.gstack)
                #print("대입")
                self.update_gridstack()
                #print("update")
                self.gstack_dict[id(value)] = [key,value]

            
            def grid_delete_tile(self, delete_tile_id):
                delete_position, _ = self.gstack_dict[delete_tile_id]
                self.gstack_objects.pop(delete_position)
                self.update_gridstack()
                del self.gstack_dict[delete_tile_id]

            
            def initialize_tile(self, type):
                #print(type)
                if type == 'Metrics chart':
                    button = w.Button(name = 'Click to set metric charts', sizing_mode = 'stretch_both') 
                    button.on_click(self.initialize_metric_charts)
                    temp = Tile(self, "Test Metric", button)
                    #print("TEMPTILE")
                    #print(temp)
                    #print(temp.tile)
                    return temp.tile

            def initialize_gstack(self):
                temp = Tile(self, "Utilization")
                self.gstack[0:3, 0:2] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(0,0,3,2), temp.tile]

                temp = Tile(self, "Performance")
                self.gstack[3:6, 0:2] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(3,0,6,2), temp.tile]

                temp = Tile(self, "Index") # 바꿔야함
                self.gstack[6:9, 0:2] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(6,0,9,2), temp.tile]


                temp = Tile(self, *simple_draw_chart("Deadlocks"))
                self.gstack[3:6, 2:5] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(3,2,6,5), temp.tile]

                temp = Tile(self, *simple_draw_chart("Backends"))
                self.gstack[0:3, 2:5] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(0,2,3,5), temp.tile]

                temp = Tile(self, *simple_draw_chart("Transactions Committed"))
                self.gstack[3:6, 5:8] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(3,5,6,8), temp.tile]

                temp = Tile(self, *simple_draw_chart("idx_scan"))
                self.gstack[6:9, 2:5] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(6,2,9,5), temp.tile]

                temp = Tile(self, *simple_draw_chart("seq_scan"))
                self.gstack[6:9, 5:8] = temp.tile
                self.gstack_dict[id(temp.tile)] = [(6,5,9,8), temp.tile]

                print(self.gstack.grid)
                self.gstack_objects =  self.gstack.objects 
                print("after initialize")
                print(self.gstack)
                
                

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
                self.top_space.clear()
                self.top_space.append(pn.Row(self.add_tile, self.save_btn, self.clear_btn, None, None, height = 100))
            
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

    class Chart():
        def __init__(self, num, dashboard):
            self.name = ''
            self.num = num         
            charts[self.num-1] = self   
            l = get_metrics_info()
            self.c = None
            self.metrics = AwesomeButton(name="Add metric",icon=Icon(name="",value='<i class="fas fa-plus"></i>'))
            self.metrics.margin = [15,15]
            self.metrics.css_classes= ['btn']
            self.metrics.on_click(self.add_metric)
            self.trigger = pn.widgets.Checkbox(name='', visible = False, value = False)

            self.filter = AwesomeButton(name="Add filter",icon=Icon(name="",value='<i class="fas fa-filter"></i>'), disabled = True)
            self.filter.margin = [15,15]
            self.filter.css_classes= ['btn']
            self.filter.on_click(self.add_filter)

            self.splitting = AwesomeButton(name="Add splitting",icon=Icon(name="",value='<i class="fas fa-wrench"></i>'), disabled = True)
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
            self.chart_list = {'metric':None, 'filter':None, 'split':None, 'type':None}

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

            self.ctop_btn_board = AwesomeButton(name="Pin to dashboard",icon=Icon(name="",value='<i class="fas fa-bookmark"></i>'))
        
            self.ctop_btn_board.margin = [15,15]
            if dashboard:
                self.ctop_btn_board.on_click(self.add_dashboard) ## 다르게
                self.ctop_btn_board.css_classes= ['btn-focus']
            else:
                self.ctop_btn_board.on_click(self.add_dashboard)
                self.ctop_btn_board.css_classes= ['btn']

            self.chart_setting_btn = AwesomeButton(icon=Icon(name="",value='<i class="fas fa-align-justify"></i>'), sizing_mode = "fixed", width = 40, height = 40)
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
            dashboard_chart.append(self.cached_chart)
            print(dashboard_chart)

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
            #self.filter # 라는게 있다고 가정할게 현재 걸려있는 필터, 필터는 property 하나에 밖에 못 걸어.
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
                        type='line', timerange=datetime_range_picker.value, trigger=False, setting = False):
            
            print("DRAW")
            print(self.chart_type.value, type)
        

            if not (metric == 'None' or aggregate == 'None'):
                if len(self.metric_list)==0 or self.metric_list[-1] != (metric,aggregate):
                    self.metric_list.append((metric,aggregate))

            if not (property == 'None' or len(value)==0):
                self.chart_filter = (property, operator, value)
        
                    
            if not (s_value == 'None'):
                self.chart_split = (s_value, limit, sort)
                self.metrics.disabled = True
                

            if trigger == False and self.chart_list['type'] == type and self.chart_list['metric'] != None and set(self.chart_list['metric'])==set(self.metric_list) and self.chart_list['filter'] == self.chart_filter and self.chart_list['split'] == self.chart_split:
                return pn.Column(self.selected_element_bar, pn.panel(self.cached_chart))
            
            
            option_dict = {'y_min':self.y_min.value,
                            'y_max':self.y_max.value,
                            'l_visible':self.l_visible.value,
                            'l_position':self.l_position.value,
                            'l_size':self.l_size.value}
            
            print(option_dict)

            chart = visualize_metrics_panel(self.metric_list, self.chart_filter, self.chart_split, self.chart_type.value, timerange, option_dict)
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
                
            # if not (s_value == 'None'):
            #     self.split_bar.css_classes = ['float_box_invisible']
            #     self.select_split_values.value = "None"
            #     self.select_limit.value = '10'
            #     self.select_sort.value = 'Ascending'

                
            self.set_selected_element_bar()
            self.cached_chart = chart
            self.chart_list['metric'] = copy.deepcopy(self.metric_list)
            self.chart_list['filter'] = self.chart_filter
            self.chart_list['split'] = self.chart_split
            self.chart_list['type'] = type
            

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
            
            return pn.Column(self.selected_element_bar, pn.panel(chart))
        
        def get_title(self, metric, aggregate, trigger):
            if trigger:
                self.trigger = False
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
            self.c = pn.Card(pn.bind(self.get_title, metric = self.select_metrics, aggregate = self.select_agg, trigger = self.trigger), self.chart_top_bar, self.metric_bar, self.filter_bar, self.split_bar, self.selected_element_bar, self.chart_col, collapsible = False, hide_header = True)

            return self.c

    def metrics_dashboard():
        # Top bar
        top_btn_new = AwesomeButton(name="New chart",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>'))
        top_btn_new.css_classes= ['btn']
        top_btn_new.disabled = True
        top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>"""))
        top_btn_refresh.css_classes= ['btn']
        top_bar = pn.Row(top_btn_new,top_btn_refresh,None, datetime_range_picker)    
        
        #template.main.append(
        template.main[0][:] = [
            top_bar,
            Chart(1, True).chart(),    
        ]

        #)
    charts = [None for i in range(5)]
    def metrics():
        # Top bar
        top_btn_new = AwesomeButton(name="New chart",icon=Icon(name="",value='<i class="fas fa-sticky-note"></i>'))
        top_btn_new.css_classes= ['btn']
        

        top_btn_refresh = AwesomeButton(name="Refresh",icon=Icon(name="",value="""<i class="fas fa-sync"></i>"""))
        top_btn_refresh.css_classes= ['btn']
    

        top_bar = pn.Row(top_btn_new,top_btn_refresh,None, datetime_range_picker)

        def new_chart(clicked_button):
            num = len(template.main[0])
            chart = Chart(num, False)
            template.main[0].append(chart.chart())

        def refresh(clicked_button):
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
        
    PAGES = {
        '🏠 Home': home,'📈 Metrics': metrics, '🖥️ Dashboard': dashboard,
    }
    @pn.depends(page_name, watch=True)
    def change_page(page_name):
        page_func = PAGES[page_name]
        template.main[0][:] = page_func()
    
    change_page("🏠 Home")

        #return template
    template.show()

    #display(HTML(style))
    

# def visualize(df = None, user_query = ""):
#     line = HTML('<hr>')
#     style="""
#             <style>
#                 /* enlarges the default jupyter cell outputs, can revert by Cell->Current Outputs->Clear */
#                 .container { width:1020 !important; } 
                
                
#                 /* styles for output widgets */
#                 .o1 {width:180px; border:1px solid #ddd}
#                 .o2 {width:800px; border:1px solid #ddd}
#                 .b1 {background-color:skyblue; }
#                 .o5 span {color:red !important}
                
#                 /* custom styles for testing */
#                 .style_A {background-color:#fafaaa}
#                 .style_B {background-color:#faaafa}
#                 .style_C {background-color:#aafafa}
#             </style>
#         """
    
    
#     display(HTML(style))
#     layout_btn = widgets.Layout(width = '160px')
#     layout_btn2 = widgets.Layout(width = '100px')
#     layout_d = widgets.Layout(width = '100px')
#     style_btn = dict(button_color='white')

#     col_layout = Layout(display='flex',
#                     flex_flow='column',
#                     align_items='center',
#                     #border='solid',
#                     width='100%')
#     row_layout = Layout(display='flex',
#                     flex_flow='row',
#                     align_items='center',
#                     align_content = 'stretch',
#                     justify_content = 'center',


#                     #border='solid',
#                     width='100%')
    
#     head = HTML(value="<b><font size = 5> Visualization Mode</b>")
#     head1 = HTML(value="<font size = 3> General Visualization")
#     head2 = HTML(value="<font size = 3> Specialized Visualization")
#     b11= Button(description="Query and Visualize")
#     df_btn = widgets.Button(description='Dataframe',
#                        tooltip='',
#                        icon='fa-table',
#                        layout=layout_btn,
#                        style = style_btn)
#     #b21= Button(description="Metrics")
#     metric_btn = widgets.Button(description='Metrics',
#                        tooltip='',
#                        icon='fa-line-chart',
#                        layout=layout_btn,
#                        style = style_btn)
    
#     query_performance_btn = widgets.Button(description='Query Performance',
#                        tooltip='',
#                        icon='fa-database',
#                        layout=layout_btn,
#                        style = style_btn)
#     b23= Button(description="Wait Time Viewer")
#     o11 = Output()
#     o12 = Output()
#     o11.add_class('o1')
#     o12.add_class('o1')
#     o21 = Output()
#     o21.add_class('o2')
#     o22 = Output()
#     o22.add_class('o2')
#     o23 = Output()
#     o23.add_class('o2')
#     scene = HBox([VBox([o11,o12]),VBox([o21,o22,o23])])
#     display(scene)

#     def reload():
#         clear_output()
#         display(scene)
    
    
#     status = 'metric'
#     o11.add_class('b1')
#     with o11:
#         display(HTML(' '))
#     with o12:
#         import datetime


#         display(HTML("<b><center><font size = 2>Monitoring<br></center>"),layout = col_layout)
#         display(VBox([metric_btn, query_performance_btn, df_btn],layout = col_layout))
    
#         # chart title
 

#     def b11_on_click_callback(clicked_button: widgets.Button) -> None:
#         b11_head = HTML(value="<b><font size = 3> Query and Visualize")
#         rb = widgets.RadioButtons(
#                     options=['w/ template', 'w/o template'],
#                     description='Query Mode:',
#                     disabled=False
#                 )
#         b11_button = Button(description="Ok", button_style ='primary')
#         def query_on_click_callback(b):
#             if rb.value == 'w/ template':
#                 get_query_template()
#             elif rb.value == 'w/o template':
#                 if user_query != "":
#                     q(user_query)
#                 else:
#                     text = widgets.Text(description='Query:', disabled=False)
#                     text_button = Button(description = "Enter")
#                     display(HBox([text, text_button]))
#                     def text_button_on_click_callback(tb):
#                         if len(text.value)>0:
#                             q(text.value)
#                     text_button.on_click(text_button_on_click_callback)
                
                 
                 
#     def b12_on_click_callback(clicked_button: widgets.Button) -> None:
#         assert df is not None, '[Error] Dataframe input is required to visualize dataframe !'
#         dataframe_visualization(df)

#     #b12.on_click(b12_on_click_callback)
    
#     def metric_on_click_callback(clicked_button: widgets.Button=None) -> None:

#         with o21:
#             clear_output()
#             new_btn = widgets.Button(description='New chart',
#                         tooltip='',
#                         icon='fa-plus',
#                         layout=layout_btn2,
#                         style = style_btn)
#             refresh_btn = widgets.Button(description='Refresh',
#                         tooltip='',
#                         icon='fa-refresh',
#                         layout=layout_btn2,
#                         style = style_btn)
#             display(HBox([new_btn, refresh_btn]))
#         with o22:
#             import panel as pn
#             from panel import widgets as w
#             pn.extension('ipywidgets')
#             o221 = Output()

            

#             datetime_range_picker = w.DatetimeRangePicker(name='Local time', value=values)

            
#             clear_output()
#             #new_m_label = HTML('<i class="fa fa-plus-square-o" aria-hidden="true"></i> New metric')
#             new_m = w.Select(name='Add metric', options=['Biology', 'Chemistry', 'Physics'])
#             new_f = w.Select(name='Add filter', options=['Biology', 'Chemistry', 'Physics'])

#             display(o221)
#             with o221:
#                 display(pn.Row(new_m, new_f, datetime_range_picker))
# #                display(datetime_range_picker)
#         with o23:
#             clear_output()
#             plt.Figure()
#             plt.show()


#     metric_btn.on_click(metric_on_click_callback)

#     metric_on_click_callback()

#     def b22_on_click_callback(clicked_button: widgets.Button) -> None:
#         query_visualizer()

#     #b22.on_click(b22_on_click_callback)
    
#     def b23_on_click_callback(clicked_button: widgets.Button) -> None:
#         wait_visualizer()

#     #b23.on_click(b23_on_click_callback)
    
    
    
#     #display(VBox([head, head1,button_box1, head2, button_box2],layout = col_layout))
