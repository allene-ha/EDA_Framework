import datetime as dt
from matplotlib import pyplot as plt
from matplotlib.container import BarContainer

import numpy as np
import math
import pandas as pd
import textwrap

import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML
from ipywidgets import interact, interact_manual, Layout
import IPython.display
from IPython.display import display, clear_output
import mplcursors
from matplotlib.legend_handler import HandlerLine2D
from collections import Counter
from matplotlib.animation import FuncAnimation
import matplotlib.dates as mdates 
import copy
from matplotlib.dates import DateFormatter
plt.style.use('seaborn-notebook')



def dataframe_visualization(df):
    def display_df(df):
        display(HTML(df.to_html()))

    display_df(df)
    class dropdown(object):
        def __init__(self, description, option):
            self.label = HTML(value=description)
            self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            self.d = VBox([self.label, self.dropdown], layout = Layout(width = '100%', align_items='center'))#, layout = Layout(flex='stretch', align_items='center'))
        def set_option(self, option):
            self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            self.d = VBox([self.label, self.dropdown], layout = Layout(width = '100%', align_items='center'))

    toggle_label = HTML(value="<font size = 2> Recommendation", layout = Layout(margin ='0 30px'))
    toggle = widgets.Checkbox(value=True, indent=False)


    def toggle_changed(b):
        if b['type'] =='change' and b['name']=='value':
            clear_output(wait=True)
            display(HBox([toggle_label, toggle]))

            if b['new'] == True:
                right_box.layout.width = '70%'
                display(widgets.HBox([left_box, right_box]))
            if b['new'] == False:
                right_box.layout.width = '100%'
                display(right_box)



    toggle.observe(toggle_changed)

    display(HBox([toggle_label, toggle]))

    col_layout_l = Layout(display='flex',
                        flex_flow='column',
                        align_items='center',
                        border='1px solid',
                        width='30%')
    col_layout_r = Layout(display='flex',
                        flex_flow='column',
                        align_items='center',
                        border='1px solid',
                        width='70%')
    col_layout_r2 = Layout(display='flex',
                        flex_flow='column',
                        align_items='center',
                        width='100%')
    row_layout = Layout(display='flex',
                        flex_flow='row',
                        align_items='center',
                        align_content = 'stretch',
                        justify_content = 'center',
                        #border='solid',
                        width='90%')

    left_label = HTML(value="<b><font size = 3> Recommended Chart")
    right_label = HTML(value="<b><font size = 3> Chart Drawing", layout = Layout(flex = '0 0 auto', align_self='center'))
    type_label = HTML(value="<font size = > Type")


    dropdown_type =  widgets.Select(
                        options=['Line','Bar', 'Pie', 'Scatter', 'Heatmap','Surface'],
                        disabled=False,
                        layout=Layout(width='90%'))

    

    def display_widgets(dropdowns):
        clear_output(wait=True)
        display(HBox([toggle_label, toggle]))
        right_box2 = compose_box(dropdowns)
        #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
        right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                            width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
        right_box = VBox([right_label, right_box1, draw_button], layout = col_layout_r) 
        if toggle.value == True:
            display(widgets.HBox([left_box, right_box]))
        if toggle.value == False:
            display(right_box)


    def type_changed(d):
        if d['type'] =='change' and d['name']=='value':
            print(d['new']) # type
            if d['new'] =='Line' or d['new'] == 'Scatter':
                dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d, dropdown_y.d, dropdown_marker.d, dropdown_column.d]
            elif d['new'] == 'Bar': 
                dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d, dropdown_height.d, dropdown_pattern.d, dropdown_column.d]
            elif d['new'] == 'Pie': 
                dropdowns = [dropdown_label.d, dropdown_size.d, dropdown_row.d, dropdown_column.d]
            elif d['new'] == 'Heatmap': 
                dropdowns = [dropdown_x.d, dropdown_y.d, dropdown_color.d, dropdown_row.d, dropdown_column.d]
            elif d['new'] == 'Surface': 
                dropdowns = [dropdown_x.d, dropdown_y.d, dropdown_z.d, dropdown_row.d, dropdown_column.d]
            else:
                print("Undefined Type")
            display_widgets(dropdowns)

    dropdown_type.observe(type_changed)






    # option은 그때그때 변경

    def compose_box(dropdowns):
        if len(dropdowns)==4:
            row1 = HBox(dropdowns[0:2], layout=row_layout)
            row2 = HBox(dropdowns[2:], layout = row_layout)
        else:
            row1 = HBox(dropdowns[0:3], layout=row_layout)
            row2 = HBox(dropdowns[3:], layout = row_layout)


        return VBox([row1,row2, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))

    example_num = ['1','2','3','4','5']
    example_cat = ['girl','boys']
    example = example_num + example_cat

    dropdown_x = dropdown('X-axis',example)
    dropdown_y = dropdown('Y-axis',example)
    dropdown_z = dropdown('Z-axis',example)

    dropdown_height = dropdown('Height',example)
    dropdown_label = dropdown('Label',example)
    dropdown_size = dropdown('Size',example)


    dropdown_color = dropdown('Color',example)
    dropdown_pattern = dropdown('Pattern',example)
    dropdown_marker = dropdown('marker',example)
    dropdown_row = dropdown('Row',example)
    dropdown_column = dropdown('Column',example)

    output = widgets.Output(layout=Layout(width='100%'))
    left_box = VBox([left_label, output], layout = col_layout_l)

    accordion = widgets.Accordion(children=[widgets.IntSlider()], selected_index = None, layout=Layout(margin = '10px',width='90%'))
    accordion.set_title(0, 'Detail')

    def draw_on_click_callback(clicked_button: widgets.Button) -> None:
        print("Hello")
        """버튼이 눌렸을 때 동작하는 이벤트 핸들러"""

    draw_button = Button(description = "Draw", button_style='primary', layout = Layout(flex = '0 0 auto', align_self='flex-end', width = '20%', margin ='10px 30px'))
    draw_button.on_click(draw_on_click_callback)





    dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d,dropdown_y.d, dropdown_pattern.d, dropdown_column.d]
    right_box2 = compose_box(dropdowns)
    #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
    right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
    right_box = VBox([right_label, right_box1, draw_button], layout = col_layout_r) 

    with output: # drawing recommended Chart. only activated when recommendation toggle is on.
        plt.close()
        plt.figure(figsize = (4,3))

        plt.plot([1,2,3,4,5],[1,3,5,7,9])
        plt.show() 

    display(widgets.HBox([left_box, right_box]))
