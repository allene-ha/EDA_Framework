
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

def scenario():

    import_and_update_data()
    qm = Button(description="Query Monitoring", layout = Layout(width = '80%'))
    dm = Button(description="Database Monitoring", layout = Layout(width = '80%'))
    qm.on_click(query_monitoring)
    dm.on_click(db_monitoring)
    display(HBox([qm, dm], layout = Layout(justify_content = 'center')))
    


def query_monitoring(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Query Monitoring")
    display(head)

    b1 = Button(description="Long Running Queries", layout = Layout(width = '80%'))
    b2 = Button(description="IO Consuming Queries", layout = Layout(width = '80%'))
    b1.on_click(long_running_query)
    display(b1)

def db_monitoring(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Database Monitoring")
    display(head)

def long_running_query(clicked_button: widgets.Button) -> None:
    head = HTML(value="<b><font size = 3> Longest Running Queries" )
    display(head)
    print_raw_data_category('Duration')
    

    