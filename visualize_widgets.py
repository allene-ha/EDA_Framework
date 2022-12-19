from query import * 
from dataframe_visualization import *
from performance_analysis import *
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML
from ipywidgets import Layout

plt.style.use('seaborn-notebook')



def visualize(df = None, user_query = ""):
    line = HTML('<hr>')
    col_layout = Layout(display='flex',
                    flex_flow='column',
                    align_items='center',
                    #border='solid',
                    width='50%')
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
    b12= Button(description="Dataframe Visualizer")
    b21= Button(description="Metric Viewer")
    b22= Button(description="Query Performance Viewer")
    b23= Button(description="Wait Time Viewer")
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
                
        b11_button.on_click(query_on_click_callback)
        display(VBox([line, b11_head, HBox([rb, b11_button])]))
        
    button_box1 = HBox([b11,b12], layout = row_layout)
    button_box2 = HBox([b21,b22,b23],  layout = row_layout)
    #Label("Visualization Mode", style = dict(font_weight='bold',font_size="18px"))
    
    b11.on_click(b11_on_click_callback)
                 
                 
    def b12_on_click_callback(clicked_button: widgets.Button) -> None:
        assert df is not None, '[Error] Dataframe input is required to visualize dataframe !'
        dataframe_visualization(df)

    b12.on_click(b12_on_click_callback)
    
    def b21_on_click_callback(clicked_button: widgets.Button) -> None:
        visualize_metrics()

    b21.on_click(b21_on_click_callback)


    def b22_on_click_callback(clicked_button: widgets.Button) -> None:
        query_visualizer()

    b22.on_click(b22_on_click_callback)
    
    def b23_on_click_callback(clicked_button: widgets.Button) -> None:
        wait_visualizer()

    b23.on_click(b23_on_click_callback)
    
    
    
    display(VBox([head, head1,button_box1, head2, button_box2],layout = col_layout))