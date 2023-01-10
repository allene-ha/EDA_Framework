
import datetime as dt
from matplotlib import pyplot as plt
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


from query import * 
from dataframe_visualization import *

from performance_analysis import import_and_update_data, print_raw_data_category

button_layout = Layout(width = '200px', height = '50px')

def scenario():

    import_and_update_data()
    qm = Button(description="Query Monitoring", 
                layout = button_layout,  
                style = dict(button_color= 'LightBlue', font_weight = 'bold', font_size="18px"))

    dm = Button(description="Database Monitoring", 
                layout = button_layout,  
                style = dict(button_color= 'LightBlue', font_weight = 'bold',  font_size="18px"))
    qm.on_click(query_monitoring)
    dm.on_click(db_monitoring)
    display(VBox([qm, dm]))#, layout = Layout(justify_content = 'center')))


line = HTML('<hr>')


def query_monitoring(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Query Monitoring")
    display(line, head)

    b1 = Button(description="Long Running Queries", layout = button_layout)
    b2 = Button(description="IO Consuming Queries", layout = button_layout)
    b3 = Button(description="CPU Consuming Queries", layout = button_layout)
    b4 = Button(description="Frequent Queries", layout = button_layout)
    b1.on_click(long_running_query)
    b2.on_click(io_consuming_query)
    b4.on_click(frequent_query)
    display(VBox([b1,b2,b3,b4]))

def db_monitoring(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Database Monitoring")
    display(head)

def long_running_query(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Longest Running Queries" )
    display(line, head)
    print_raw_data_category('Duration')

def io_consuming_query(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> IO Consuming Queries" )
    display(line, head)
    print_raw_data_category('Disk IO')

def frequent_query(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Frequent Queries" )
    display(line, head)
    print_raw_data_category('Execution Count')

    