import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML, Dropdown
from ipywidgets import interact, interact_manual, Layout
import IPython.display
from IPython.display import display, clear_output
from query import q_

class knob:
    def __init__(self):
        knobs = get_knobs()
        knob_list = list(get_knobs().keys())
        self.w = {}
        self.w['knob'] = Dropdown(options=knob_list,
                            value=knob_list[0])
        self.w['min'] = widgets.BoundedFloatText(
                            value=None,
                            disabled=True)
        self.w['max'] = widgets.BoundedFloatText(
                            value=None,
                            disabled=True)
        self.w['num'] = widgets.IntText(
                            value=None,
                            disabled=True)
        
        self.w['knob'].observe(self.set_min_max, names='value')
        

    def set_min_max(self, widget):
        selection = widget['new']
        
        self.w['min'].disabled = False
        self.w['min'].
        self.w['max'].disabled = False
        self.w['num'].disabled = False

        NotImplemented
    
    def get_box(self):
        layout = widgets.Layout(
                    align_items='center',
                    width= '80%')
        return HBox([
        VBox(HTML('Knob'), self.w['knob'], layout=layout),
        VBox(HTML('Min'), self.w['min'], layout=layout),
        VBox(HTML('Max'), self.w['max'], layout=layout),
        VBox(HTML('Num'), self.w['num'], layout=layout)
        ])
        


def get_knobs():
    res = q_("SELECT name, setting, min_val, max_val From pg_settings where pending_restart = False and (vartype = 'integer' or vartype = 'real');")
    #res = [i for i in res if is_digit(i[1])]
    
    return {a:[b,c,d] for a,b,c,d in res}