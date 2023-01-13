import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML, Dropdown
from ipywidgets import interact, interact_manual, Layout
from IPython.display import display, clear_output
from query import q_, q_wo_fetch
import numpy as np
import seaborn as sns
import pandas as pd
import subprocess

import matplotlib.pyplot as plt

class knob:
    def __init__(self):
        self.knobs = get_knobs()
        w_layout = widgets.Layout(
                    align_items='center',
                    width= '80%')
        knob_list = list(get_knobs().keys())
        self.w = {}
        self.w['knob'] = Dropdown(options=knob_list,
                            value=knob_list[0],
                            layout = w_layout)
        self.w['min'] = widgets.BoundedFloatText(
                            value=None,
                            disabled=True,
                            layout = w_layout)
        self.w['max'] = widgets.BoundedFloatText(
                            value=None,
                            disabled=True,
                            layout = w_layout)
        self.w['num'] = widgets.IntText(
                            value=None,
                            disabled=True,
                            layout = w_layout)
        
        self.w['knob'].observe(self.set_min_max, names='value')
        

    def set_min_max(self, widget):
        self.w['min'].min = 0
        self.w['min'].max = 0
        self.w['max'].min = 0
        self.w['max'].max = 0
        self.w['num'].min = 0
        self.w['num'].max = 0

        selection = widget['new']
        knob = self.knobs[selection]
        self.type = knob[3]
        if self.type == 'integer':
            self.w['min'].step = 1
            self.w['max'].step = 1
        elif self.type =='real':
            self.w['min'].step = 0.1 # 더 낮추어야하는 knob도 있음 cpu 관련 knob들 따로 처리 필요
            self.w['max'].step = 0.1
        else:
            raise NotImplementedError

        self.w['min'].disabled = False
        self.w['min'].max = knob[2]
        self.w['min'].min = knob[1]
        
        self.w['min'].value = knob[0]

        self.w['max'].disabled = False
        self.w['max'].max = knob[2]
        self.w['max'].min = knob[1]
        
        self.w['max'].value = knob[0]

        self.w['num'].disabled = False
        self.w['num'].min = 2
        self.w['num'].max = 100
        self.w['num'].value = 5
    
    def get_box(self):
        layout = widgets.Layout(
                    align_items='center',
                    width= '100%')
        return HBox([
        VBox([HTML('Knob'), self.w['knob']], layout=layout),
        VBox([HTML('Min'), self.w['min']], layout=layout),
        VBox([HTML('Max'), self.w['max']], layout=layout),
        VBox([HTML('Num'), self.w['num']], layout=layout)
        ], layout = Layout(width = '100%'))
    
    def set_disabled(self, status = True):
        self.w['knob'].disabled = status
        self.w['min'].disabled = status
        self.w['max'].disabled = status
        self.w['num'].disabled = status
        


def get_knobs():
    res = q_("SELECT name, setting, min_val, max_val, vartype From pg_settings where pending_restart = False and (vartype = 'integer' or vartype = 'real');")
    #res = [i for i in res if is_digit(i[1])]
    
    return {a:[b,c,d,e] for a,b,c,d,e in res}

def set_knob(name, val):
    q_wo_fetch(f"ALTER SYSTEM SET {name} = {val};")
    print(f"set [{name}] to [{val}]")

def run():
    tpcc_command = './tpcc.lua --db-driver=pgsql --pgsql-host=localhost --pgsql-port=5432 --pgsql-user=postgres --pgsql-password=postgres --pgsql-db=sbt --time=10 --threads=16 --report-interval=10 --tables=10 --scale=10 run'
    def run_tpcc_1d(knob1_val, time = 60):
        knob1_name =  knob1.w['knob'].value
        result = {}
        result['TPS'] = np.zeros(len(knob1_val))
        result['QPS'] = np.zeros(len(knob1_val))
        result['latency'] = np.zeros(len(knob1_val))
        
        print(f"====================== Start Running TPC-C =======================")
        for i, val in enumerate(knob1_val):
            # knob1의 값을 val으로 설정한다.
            set_knob(knob1_name, val)

            # tpcc를 일정 시간 돌린다.
            
            output = subprocess.check_output(tpcc_command,shell=True, cwd="sysbench-tpcc", universal_newlines=True)


            temp = output.split('\n')
            temp = temp[-25:]

            s = [i.replace("  ","").split(':') for i in temp]
            d = {i[0].lstrip():i[1].lstrip() for i in s if len(i)>1}
            txn = float(d['transactions'].replace("("," ").split(" ")[0])
            query = float(d['queries'].replace("("," ").split(" ")[0])
            latency = float(d['95th percentile'].replace("("," "))
            time = float(d['total time'].replace("("," ").replace("s",''))
            print(f"Complete running TPC-C ({knob1_name}: {val})| TPS: {txn/time} QPS: {query/time} 95th latency: {latency}")
            result['TPS'][i] = txn/time
            result['QPS'][i] = query/time
            result['latency'][i] = latency
        print(f"====================== END Running TPC-C =======================")
        

        # 결과를 저장한다.
        fig, axes = plt.subplots(ncols=3, figsize=(13,5))
        axes[0].plot(knob1_val, result['TPS'])
        axes[0].set_title("TPS")
        axes[1].plot(knob1_val, result['QPS'])
        axes[1].set_title("QPS")
        axes[2].plot(knob1_val, result['latency'])
        axes[2].set_title("95th percentile latency")
        axes[0].grid(True, axis='y')
        axes[1].grid(True, axis='y')
        axes[2].grid(True, axis='y')
        fig.suptitle(f"Performance by values of {knob1_name}", size=20, fontweight="bold")
        axes[1].set_xlabel(knob1_name)
       
        plt.tight_layout()
        plt.show()
        

        
    def run_tpcc_2d(knob1_val, knob2_val):
        # 결과 2차 배열을 초기화한다.
        knob1_name = knob1.w['knob'].value
        knob2_name = knob2.w['knob'].value
        result = {}
        result['TPS'] = np.zeros((len(knob1_val),len(knob2_val)))
        result['QPS'] = np.zeros((len(knob1_val),len(knob2_val)))
        result['latency'] = np.zeros((len(knob1_val),len(knob2_val)))

        print(f"====================== Start Running TPC-C =======================")
        for i, val1 in enumerate(knob1_val):
            for j, val2 in enumerate(knob2_val):
                # knob1의 값을 val1로, knob2의 값을 val2로 설정한다.
                set_knob(knob1_name, val1)
                set_knob(knob2_name, val2)
                # tpcc를 일정 시간 돌린다.

                output = subprocess.check_output(tpcc_command,shell=True, cwd="sysbench-tpcc", universal_newlines=True)


                temp = output.split('\n')
                temp = temp[-25:]

                s = [i.replace("  ","").split(':') for i in temp]
                d = {i[0].lstrip():i[1].lstrip().replace("("," ") for i in s if len(i)>1}
                txn = float(d['transactions'].split(" ")[0])
                query = float(d['queries'].split(" ")[0])
                latency = float(d['95th percentile'])
                time = float(d['total time'].replace("s",''))
                print(f"Complete running TPC-C ({knob1_name}: {val1}/ {knob2_name}: {val2})| TPS: {txn/time} QPS: {query/time} 95th latency: {latency}")
                result['TPS'][i][j] = txn/time
                result['QPS'][i][j] = query/time
                result['latency'][i][j] = latency
                # 결과를 저장한다.
        print(f"====================== END Running TPC-C =======================")

        tps_df = pd.DataFrame(result['TPS'], columns = knob2_val, index = knob1_val)
        qps_df = pd.DataFrame(result['QPS'], columns = knob2_val, index = knob1_val)
        latency_df = pd.DataFrame(result['latency'], columns = knob2_val, index = knob1_val)

        fig, axes = plt.subplots(ncols=3, figsize=(13,5))
        sns.heatmap(tps_df, ax = axes[0])
        sns.heatmap(qps_df, ax = axes[1])
        sns.heatmap(latency_df, ax = axes[2])
        axes[0].set_title("TPS")
        axes[1].set_title("QPS")
        axes[2].set_title("95th percentile latency")
        fig.suptitle(f"Performance by values of {knob1_name} and {knob2_name}", size=20, fontweight="bold")
        
        axes[1].set_xlabel(knob2_name)
        axes[0].set_ylabel(knob1_name)
       

        plt.tight_layout()
        plt.show()



    def run_experiment(button):
        if knob1.w['min'].disabled:
            raise AssertionError
        if not knob2.w['knob'].disabled and knob2.w['min'].disabled:
            raise AssertionError
        if knob1.w['min'].value > knob1.w['max'].value:
            raise ValueError
        if not knob2.w['knob'].disabled and knob2.w['min'].value > knob2.w['max'].value:
            raise ValueError


        knob1_val = np.linspace(knob1.w['min'].value, knob1.w['max'].value, knob1.w['num'].value)
        if knob1.type == 'integer':
            knob1_val = np.asarray(knob1_val, dtype = int)
        print(knob1_val)
        if not knob2.w['knob'].disabled:
            knob2_val = np.linspace(knob2.w['min'].value, knob2.w['max'].value, knob2.w['num'].value)
            if knob2.type == 'integer':
                knob2_val = np.asarray(knob2_val, dtype = int)
            print(knob2_val) # get configuration
        
        if not knob2.w['knob'].disabled: # Two knobs
            run_tpcc_2d(knob1_val, knob2_val)
        else: # One 
            run_tpcc_1d(knob1_val)

        



    button_layout = Layout(height = '50px', width ='100px')
     
    knob1 = knob()
    knob2 = knob()
    knob2.set_disabled()
    
    add1 = Button(description="Add",  layout = button_layout)
    run = Button(description="Run", button_style = 'primary', layout = button_layout)
    add2 = Button(disabled = True, style = dict(button_color = 'white'), layout =button_layout)
    def add_knob(button):
        display(HBox([knob2.get_box(), add2, add2], layout = Layout (align_items = 'center')))
        knob2.w['knob'].disabled = False
        add1.disabled = True
    add1.on_click(add_knob)
    run.on_click(run_experiment)
    display(HBox([knob1.get_box(),add1, run], layout = Layout (align_items = 'center')))

