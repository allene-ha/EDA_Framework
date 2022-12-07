import datetime as dt
from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
import matplotlib
import numpy as np
import pandas as pd
import copy
import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML, FloatText, Text
from ipywidgets import Layout
import IPython.display
from IPython.display import display, clear_output


import seaborn as sns

plt.style.use('seaborn-notebook')

def dataframe_visualization(df):
    class Chart(object):
        def __init__(self, type, df):
            self.type = type
            self.df = df
            self.detail = None

            # axis
            self.x = dropdown_x.dropdown.value
            self.y = dropdown_y.dropdown.value
            self.z = dropdown_z.dropdown.value
            
            # other properties
            self.color = dropdown_color.dropdown.value
            self.marker = dropdown_marker.dropdown.value

            # # of charts
            self.row = dropdown_row.dropdown.value
            self.column = dropdown_column.dropdown.value

        def type_to_property(self):
            df_numerics_only = df.select_dtypes(include=np.number)
            col_date = list(df.select_dtypes(include=[np.datetime64]).columns)
            col_num = list(df_numerics_only.columns)
            col_cat = [x for x in df.columns if x not in col_num]
            col_tot = list(df.columns)
            
            def type_to_x(self): #candidate column의 list
                candidate = []
                if self.type == "Line":
                    if len(col_date)>0:
                        for col in col_date:
                            if df[col].nunique()>5:
                                candidate.append(col)
                elif self.type == "Bar":
                    if len(col_cat) == 1:
                        candidate.append(col_cat[0])
                    elif len(col_cat)>1:
                        for col in col_cat:
                            if df[col].nunique()<20 and df[col].nunique()>=5:
                                candidate.append(col)
                        if len(candidate)==0:
                            for col in col_cat:
                                if df[col].nunique()<20:
                                    candidate.append(col)
                else:
                    if len(col_num) == 1:
                        candidate.append(col_num[0])
                    elif len(col_num) >1:
                        for col in col_num:
                            if df[col].nunique()>=5:
                                candidate.append(col)
                return candidate
            def type_to_y(self):
                candidate = []
                for col in col_num:
                    if df[col].nunique()>3:
                        candidate.append(col)
                return 
            def # 조합 짜는 함수

                    





            # 'Bar':
            #     self.draw_bar_chart()
            # elif self.type =='Scatter':
            #     self.draw_scatter_chart()
            # elif self.type == 'Line':
            #     self.draw_line_chart()
            # elif self.type == 'Heatmap':
            #     self.draw_heatmap_chart()
            # elif self.type == 'Surface':

        
        def set_property(self):
            self.x = dropdown_x.dropdown.value
            self.y = dropdown_y.dropdown.value
            self.z = dropdown_z.dropdown.value
            
            # other properties
            self.color = dropdown_color.dropdown.value
            self.marker = dropdown_marker.dropdown.value

            # # of charts
            self.row = dropdown_row.dropdown.value
            self.column = dropdown_column.dropdown.value


        def set_detail(self, detail):
            self.detail = detail
        
        def set_type(self, type):
            self.type = type
        
        def draw(self):
            if self.type == 'Bar':
                self.draw_bar_chart()
            elif self.type =='Scatter':
                self.draw_scatter_chart()
            elif self.type == 'Line':
                self.draw_line_chart()
            elif self.type == 'Heatmap':
                self.draw_heatmap_chart()
            elif self.type == 'Surface':
                self.draw_surface_chart()

        def draw_surface_chart(self):
            title = self.z + ' by ' + self.y + ' and '+ self.x
            plt.clf()
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d')
            df_pivot_mean = pd.pivot_table(self.df, index = self.y, columns = self.x, values = self.z, aggfunc = 'mean')
            # #index = y, colunns = x, vlaues = color

            X_ = df_pivot_mean.columns.tolist()
            Y_ = df_pivot_mean.index.tolist()
            X = [X_ for _ in range(len(Y_))]
            Y = [[y_]*len(X_) for y_ in Y_]
            Z = df_pivot_mean.values
            if self.detail is not None:
                min, max, interval, scale = self.detail['X-axis']
                if min == 'None':
                    min, _ = ax.get_xlim()
                if max == 'None':
                    _, max = ax.get_xlim()
                if interval == 'None':
                    ax.set_xlim(min, max)
                else:
                    ax.xaxis.set_ticks(np.arange(min, max, interval))
                ax.set_xscale(scale)

                min, max, interval, scale = self.detail['Y-axis']
                if min == 'None':
                    min, _ = ax.get_ylim()
                if max == 'None':
                    _, max = ax.get_ylim()
                if interval == 'None':
                    ax.set_ylim(min, max)
                else:
                    ax.yaxis.set_ticks(np.arange(min, max, interval))
                ax.set_yscale(scale)
   
                min, max, interval, scale = self.detail['Z-axis']
                if min == 'None':
                    min, _ = ax.get_zlim()
                if max == 'None':
                    _, max = ax.get_zlim()
                if interval == 'None':
                    ax.set_zlim(min, max)
                else:
                    ax.zaxis.set_ticks(np.arange(min, max, interval))
                ax.set_zscale(scale)
            ax.plot_surface(X,Y,Z, cmap="inferno")
            plt.title(title)

            clear_output(wait=True)
            display_df(self.df)
            display_widgets()
            plt.show()

        def draw_heatmap_chart(self):
            #sns.set(rc={'figure.figsize':(12,12)})
            title = self.color + ' by ' + self.y + ' and '+ self.x
            plt.clf()
            #temp = df.pivot("sepal_length", "sepal_width", "petal_width")
            df_pivot_mean = pd.pivot_table(self.df, index = self.y, columns = self.x, values = self.color, aggfunc = 'mean')
            #index = y, colunns = x, vlaues = color
            sns.heatmap(df_pivot_mean, cbar_kws={'label': self.color}).set(title = title)
            ax = plt.gca()
            if self.detail is not None:
                min, max, interval, scale = self.detail['X-axis']
                if min == 'None':
                    min, _ = ax.get_xlim()
                if max == 'None':
                    _, max = ax.get_xlim()
                if interval == 'None':
                    ax.set_xlim(min, max)
                else:
                    ax.xaxis.set_ticks(np.arange(min, max, interval))
                ax.set_xscale(scale)

                min, max, interval, scale = self.detail['Y-axis']
                if min == 'None':
                    min, _ = ax.get_ylim()
                if max == 'None':
                    _, max = ax.get_ylim()
                if interval == 'None':
                    ax.set_ylim(min, max)
                else:
                    ax.yaxis.set_ticks(np.arange(min, max, interval))
                ax.set_yscale(scale)
   
            clear_output(wait=True)
            display_df(self.df)
            display_widgets()
            plt.show()

        def draw_line_chart(self):
            title = self.y + ' by ' + self.x
            d = {}
            if self.color != 'None':
                d['hue'] = self.color
            if self.marker != 'None':
                d['style'] = self.marker
            if self.row != 'None':
                d['row'] = self.row
            if self.column != 'None':
                d['col'] = self.column
            plt.clf()
            sns.set(rc={'figure.figsize':(12,9)})
            sns.relplot(x=self.x, y=self.y, ci=None, legend = 'full', kind = 'line', **d, data=df).set(title = title)
            
            ax = plt.gca()
            if self.detail is not None:
                min, max, interval, scale = self.detail['X-axis']
                if min == 'None':
                    min, _ = ax.get_xlim()
                if max == 'None':
                    _, max = ax.get_xlim()
                if interval == 'None':
                    ax.set_xlim(min, max)
                else:
                    ax.xaxis.set_ticks(np.arange(min, max, interval))
                ax.set_xscale(scale)

                min, max, interval, scale = self.detail['Y-axis']
                if min == 'None':
                    min, _ = ax.get_ylim()
                if max == 'None':
                    _, max = ax.get_ylim()
                if interval == 'None':
                    ax.set_ylim(min, max)
                else:
                    ax.yaxis.set_ticks(np.arange(min, max, interval))
                ax.set_yscale(scale)
              
            
            clear_output(wait=True)
            display_df(self.df)
            display_widgets()
            plt.show()

        def draw_scatter_chart(self):
            title = self.y + ' by ' + self.x
            d = {}
            if self.color != 'None':
                d['hue'] = self.color
            if self.marker != 'None':
                d['style'] = self.marker
            if self.row != 'None':
                d['row'] = self.row
            if self.column != 'None':
                d['col'] = self.column

            plt.clf()
            sns.set(rc={'figure.figsize':(12,9)})
            sns.relplot(x=self.x, y=self.y, **d, data=self.df, legend = 'full').set(title = title)

            ax = plt.gca()
            if self.detail is not None:
                min, max, interval, scale = self.detail['X-axis']
                if min == 'None':
                    min, _ = ax.get_xlim()
                if max == 'None':
                    _, max = ax.get_xlim()
                if interval == 'None':
                    ax.set_xlim(min, max)
                else:
                    ax.xaxis.set_ticks(np.arange(min, max, interval))
                ax.set_xscale(scale)

                min, max, interval, scale = self.detail['Y-axis']
                if min == 'None':
                    min, _ = ax.get_ylim()
                if max == 'None':
                    _, max = ax.get_ylim()
                if interval == 'None':
                    ax.set_ylim(min, max)
                else:
                    ax.yaxis.set_ticks(np.arange(min, max, interval))
                ax.set_yscale(scale)

            # if dropdown_marker.dropdown.value == True and dropdown_color.dropdown.value != 'None':
            #     m = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
            #     m = m[0:df.nunique(dropna=True)]
            #     sns.lmplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, fit_reg = False, markers = m, **d, data=df)
            # else:
            #     sns.lmplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, fit_reg = False, **d, data=df)
            clear_output(wait=True)
            display_df(self.df)
            display_widgets()
            plt.show()
    
        def draw_bar_chart(self):
            title = self.y + ' by ' + self.x
            d = {}
            g = {}
            if self.color != 'None':
                d['hue'] = self.color
            if self.row != 'None':
                g['row'] = self.row
            if self.column != 'None':
                g['col'] = self.column
            plt.clf()
            sns.set(rc={'figure.figsize':(12,9)})
            
            # Form a facetgrid using columns with a hue
            if self.row != 'None' or self.column != 'None':
                if self.color != 'None':
                    grid = sns.FacetGrid(self.df, **g, hue = d['hue'], margin_titles = True, legend_out = True)
                else: 
                    grid = sns.FacetGrid(self.df, **g, margin_titles = True)
                grid.map(sns.barplot, self.x, self.y)
                grid.add_legend()
                grid.fig.suptitle(title)
                #plt.legend(loc = 2, bbox_to_anchor = (1,1))
            else:
                bar = sns.barplot(x=self.x, y=self.y, **d, data=df).set(title = title)
                plt.legend(loc = 2, bbox_to_anchor = (1,1))
    
            if self.pattern != 'False':
                if self.row != 'None' or self.column != 'None':
                    for ax in grid.axes_dict.values():
                        bars = [rect for rect in ax.get_children() if isinstance(rect, matplotlib.patches.Rectangle)]
                        hatches = ['-', '+', 'x', '\\', '*', 'o']
                        for i,thisbar in enumerate(bars):
                            # Set a different hatch for each bar
                            thisbar.set_hatch(hatches[i%len(hatches)])
                        
                else:
                    # Define some hatches
                    hatches = ['-', '+', 'x', '\\', '*', 'o']

                    # Loop over the bars
                    for i,thisbar in enumerate(bar.patches):
                        # Set a different hatch for each bar
                        thisbar.set_hatch(hatches[i%len(hatches)])

            if self.detail is not None:

                min, max, interval, scale = self.detail['Y-axis']
                if min == 'None':
                    min, _ = ax.get_ylim()
                if max == 'None':
                    _, max = ax.get_ylim()
                if interval == 'None':
                    ax.set_ylim(min, max)
                else:
                    ax.yaxis.set_ticks(np.arange(min, max, interval))
                ax.set_yscale(scale)


            clear_output(wait=True)
            display_df(self.df)
            display_widgets()
            plt.show()
    chart = Chart('line', df)

    def display_df(df):
        display(HTML(df.head().to_html()))

    display_df(df)
    class dropdown(object):
        def __init__(self, description, option):
            self.label = HTML(value=description)
            self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            self.d = VBox([self.label, self.dropdown], layout = Layout(width = '100%', align_items='center'))#, layout = Layout(flex='stretch', align_items='center'))
        def set_option(self, option):
            self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            self.d = VBox([self.label, self.dropdown], layout = Layout(width = '100%', align_items='center'))

    #toggle_label = HTML(value="<font size = 2> Recommendation", layout = Layout(margin ='0 30px'))
    #toggle = widgets.Checkbox(value=True, indent=False)


    # def toggle_changed(b):
    #     if b['type'] =='change' and b['name']=='value':
    #         clear_output(wait=True)
    #         display(HBox([toggle_label, toggle]))

    #         if b['new'] == True:
    #             right_box.layout.width = '70%'
    #             display(widgets.HBox([left_box, right_box]))
    #         if b['new'] == False:
    #             right_box.layout.width = '100%'
    #             display(right_box)



    #toggle.observe(toggle_changed)

    #display(HBox([toggle_label, toggle]))

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
                        options=['Line','Bar', 'Scatter', 'Heatmap','Surface'],
                        value = 'Line',
                        disabled=False,
                        layout=Layout(width='90%'))

    

    def display_widgets():
        if dropdown_type.value =='Line' or dropdown_type.value== 'Scatter':
            dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d, dropdown_y.d, dropdown_marker.d, dropdown_column.d]
        elif dropdown_type.value == 'Bar': 
            dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d, dropdown_y.d, dropdown_pattern.d, dropdown_column.d]
        elif dropdown_type.value == 'Pie': 
            dropdowns = [dropdown_label.d, dropdown_size.d, dropdown_row.d, dropdown_column.d]
        elif dropdown_type.value == 'Heatmap': 
            dropdowns = [dropdown_x.d, dropdown_y.d, dropdown_color.d]
        elif dropdown_type.value == 'Surface': 
            dropdowns = [dropdown_x.d, dropdown_y.d, dropdown_z.d]
        else:
            print("Undefined Type")
        clear_output(wait=True)
        #display(HBox([toggle_label, toggle]))
        right_box2 = compose_box(dropdowns)
        detail, detail_widgets = compose_detail_tab() # dict, widgets
        accordion = widgets.Accordion(children=[detail_widgets], selected_index = None, layout=Layout(margin = '10px',width='90%'))
        accordion.set_title(0, 'Detail')        #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
        right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                            width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
        right_box = VBox([right_label, right_box1, accordion, draw_button], layout = col_layout_r) 
        display(right_box)
        # if toggle.value == True:
        #     display(widgets.HBox([left_box, right_box]))
        # if toggle.value == False:
        #     display(right_box)

    
    def type_changed(d):
        if d['type'] =='change' and d['name']=='value':
            display_widgets()
            chart.set_type(d['new'])

    dropdown_type.observe(type_changed)






    # option은 그때그때 변경

    def compose_box(dropdowns):
        if len(dropdowns) <=3:
            row1 = HBox(dropdowns, layout=row_layout)
            return VBox([row1], layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
        elif len(dropdowns)==4:
            row1 = HBox(dropdowns[0:2], layout=row_layout)
            row2 = HBox(dropdowns[2:], layout = row_layout)
        else:
            row1 = HBox(dropdowns[0:3], layout=row_layout)
            row2 = HBox(dropdowns[3:], layout = row_layout)


        return VBox([row1,row2], layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
    df_numerics_only = df.select_dtypes(include=np.number)

    col_num = list(df_numerics_only.columns)
    col_cat = [x for x in df.columns if x not in col_num]
    col_tot = list(df.columns)
    col_num_none = copy.deepcopy(col_num)
    col_cat_none = copy.deepcopy(col_cat)
    col_tot_none = copy.deepcopy(col_tot)

    col_num_none.insert(0,'None')
    col_cat_none.insert(0,'None')
    col_tot_none.insert(0,'None')

    dropdown_x = dropdown('X-axis',col_tot)
    dropdown_y = dropdown('Y-axis',col_num)
    dropdown_z = dropdown('Z-axis',col_num)

    dropdown_label = dropdown('Label',col_tot)
    dropdown_size = dropdown('Size',col_tot_none)


    dropdown_color = dropdown('Color',col_tot_none)
    dropdown_pattern = dropdown('Pattern',['True', 'False'])
    dropdown_marker = dropdown('marker',col_cat_none)
    dropdown_row = dropdown('Row',col_cat_none)
    dropdown_column = dropdown('Column',col_cat_none)

    output = widgets.Output(layout=Layout(width='100%'))
    left_box = VBox([left_label, output], layout = col_layout_l)

    class axis(object):
        def __init__(self, description):
            self.description = description
            self.label = HTML(value='<b>'+description)
            self.min_label = HTML(value='Minimum axis value')
            self.min = Text(disabled=False, value ='auto', layout = Layout(width = '90%'))
            self.max_label = HTML(value='Max axis value')
            self.max = Text(disabled=False, value ='auto', layout = Layout(width = '90%'))
            self.interval_label = HTML(value='Interval')
            self.interval = Text(disabled=False,  value ='auto',layout = Layout(width = '90%'))
            self.scale_label = HTML(value='Scale')
            self.scale = widgets.Dropdown(options=["linear", "log", "symlog", "logit"],value='linear',  layout = Layout(width = '90%'))
            box_layout = Layout(display = 'flex', flex_flow='column', align_items='center', width='25%')
            self.box = VBox([self.label, HBox([VBox([self.min_label, self.min], layout =box_layout), 
                                                VBox([self.max_label, self.max], layout =box_layout), 
                                                VBox([self.interval_label, self.interval], layout =box_layout), 
                                                VBox([self.scale_label, self.scale], layout =box_layout)], layout = Layout (justify_content = 'space-around'))])
        def get_info(self):
            return self.description, [self.min, self.max, self.interval, self.scale]

    ## Accordian Box # chart drawing 함수들이 여기서 얻은 정보들을 갖고실행될 수 있도록
    def compose_detail_tab():
                #print(dropdown_type.value)
        results = {}
        boxes = []
        if dropdown_type.value == 'Line' or dropdown_type.value == 'Scatter' or dropdown_type.value == 'Heatmap'or dropdown_type.value == 'Surface': # xticks
            x_tick = axis('X-axis')
            x_tick.get_info()
            result = x_tick.get_info()
            results[result[0]] = result[1]
            boxes.append(x_tick.box)
        
        y_tick = axis('Y-axis')
        result = y_tick.get_info()
        results[result[0]] = result[1]
        boxes.append(y_tick.box)
        
        if dropdown_type.value == 'Surface':
            z_tick = axis('Z-axis')
            result = z_tick.get_info()
            results[result[0]] = result[1]
            boxes.append(z_tick.box)
        
        return results, VBox(boxes)

    detail, detail_widgets = compose_detail_tab() # dict, widgets
    detail_button = Button(description = "Apply")
    def detail_on_click_callback(clicked_button: widgets.Button) -> None:
        chart.set_detail(detail)
    detail_button.on_click(detail_on_click_callback)
    accordion = widgets.Accordion(children=[detail_widgets], selected_index = None, layout=Layout(margin = '10px',width='90%'))
    accordion.set_title(0, 'Detail')
  

    def draw_on_click_callback(clicked_button: widgets.Button) -> None:
        #chart.set_detail(detail)
        chart.draw()
 

    
            

    draw_button = Button(description = "Draw", button_style='primary', layout = Layout(flex = '0 0 auto', align_self='flex-end', width = '20%', margin ='10px 30px'))
    draw_button.on_click(draw_on_click_callback)





    dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d,dropdown_y.d, dropdown_marker.d, dropdown_column.d]
    right_box2 = compose_box(dropdowns)
    #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
    right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
    right_box = VBox([right_label, right_box1, accordion, draw_button], layout = col_layout_r) 

    with output: # drawing recommended Chart. only activated when recommendation toggle is on.
        plt.close()
        plt.figure(figsize = (4,3))

        plt.plot([1,2,3,4,5],[1,3,5,7,9])
        plt.show() 

    display(right_box)
