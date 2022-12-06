import datetime as dt
from matplotlib import pyplot as plt
from matplotlib.container import BarContainer
import matplotlib
import numpy as np
import pandas as pd
import copy
import ipywidgets as widgets
from ipywidgets import Label, HBox, VBox, Button, HTML, FloatText
from ipywidgets import Layout
import IPython.display
from IPython.display import display, clear_output


import seaborn as sns

plt.style.use('seaborn-notebook')



def dataframe_visualization(df):
    def draw_surface_chart(df):

        title = dropdown_z.dropdown.value + ' by ' + dropdown_y.dropdown.value + ' and '+ dropdown_x.dropdown.value
        plt.clf()
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        df_pivot_mean = pd.pivot_table(df, index = dropdown_y.dropdown.value, columns =  dropdown_x.dropdown.value, values = dropdown_z.dropdown.value, aggfunc = 'mean')
        # #index = y, colunns = x, vlaues = color

        X_ = df_pivot_mean.columns.tolist()
        Y_ = df_pivot_mean.index.tolist()
        X = [X_ for _ in range(len(Y_))]
        Y = [[y_]*len(X_) for y_ in Y_]
        Z = df_pivot_mean.values

        ax.plot_surface(X,Y,Z, cmap="inferno")
        plt.title(title)

        clear_output(wait=True)
        display_df(df)
        display_widgets()
        plt.show()

    def draw_heatmap_chart(df):
        #sns.set(rc={'figure.figsize':(12,12)})
        title = dropdown_color.dropdown.value + ' by ' + dropdown_y.dropdown.value + ' and '+ dropdown_x.dropdown.value
        plt.clf()
        #temp = df.pivot("sepal_length", "sepal_width", "petal_width")
        df_pivot_mean = pd.pivot_table(df, index = dropdown_y.dropdown.value, columns = dropdown_x.dropdown.value, values = dropdown_color.dropdown.value, aggfunc = 'mean')
        #index = y, colunns = x, vlaues = color
        sns.heatmap(df_pivot_mean, cbar_kws={'label': dropdown_color.dropdown.value}).set(title = title)
        clear_output(wait=True)
        display_df(df)
        display_widgets()
        plt.show()


    def draw_line_chart(df):
        title = dropdown_y.dropdown.value + ' by ' + dropdown_x.dropdown.value
        d = {}
        if dropdown_color.dropdown.value != 'None':
            d['hue'] = dropdown_color.dropdown.value
        if dropdown_marker.dropdown.value != 'None':
            d['style'] = dropdown_marker.dropdown.value
        if dropdown_row.dropdown.value != 'None':
            d['row'] = dropdown_row.dropdown.value
        if dropdown_column.dropdown.value != 'None':
            d['col'] = dropdown_column.dropdown.value
        plt.clf()
        sns.set(rc={'figure.figsize':(12,9)})
        sns.relplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, ci=None, legend = 'full', kind = 'line', **d, data=df).set(title = title)
        clear_output(wait=True)
        display_df(df)
        display_widgets()
        plt.show()

    def draw_scatter_chart(df):
        title = dropdown_y.dropdown.value + ' by ' + dropdown_x.dropdown.value
        d = {}
        if dropdown_color.dropdown.value != 'None':
            d['hue'] = dropdown_color.dropdown.value
        if dropdown_marker.dropdown.value != 'None':
            d['style'] = dropdown_marker.dropdown.value
        if dropdown_row.dropdown.value != 'None':
            d['row'] = dropdown_row.dropdown.value
        if dropdown_column.dropdown.value != 'None':
            d['col'] = dropdown_column.dropdown.value

        plt.clf()
        sns.set(rc={'figure.figsize':(12,9)})
        sns.relplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, **d, data=df, legend = 'full').set(title = title)

        # if dropdown_marker.dropdown.value == True and dropdown_color.dropdown.value != 'None':
        #     m = ['o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X']
        #     m = m[0:df.nunique(dropna=True)]
        #     sns.lmplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, fit_reg = False, markers = m, **d, data=df)
        # else:
        #     sns.lmplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, fit_reg = False, **d, data=df)
        clear_output(wait=True)
        display_df(df)
        display_widgets()
        plt.show()
 
    def draw_bar_chart(df):
        title = dropdown_y.dropdown.value + ' by ' + dropdown_x.dropdown.value
        d = {}
        g = {}
        if dropdown_color.dropdown.value != 'None':
            d['hue'] = dropdown_color.dropdown.value
        if dropdown_row.dropdown.value != 'None':
            g['row'] = dropdown_row.dropdown.value
        if dropdown_column.dropdown.value != 'None':
            g['col'] = dropdown_column.dropdown.value
        plt.clf()
        sns.set(rc={'figure.figsize':(12,9)})
        
        # Form a facetgrid using columns with a hue
        if dropdown_row.dropdown.value != 'None' or dropdown_column.dropdown.value != 'None':
            if dropdown_color.dropdown.value != 'None':
                grid = sns.FacetGrid(df, **g, hue = d['hue'], margin_titles = True, legend_out = True)
            else: 
                grid = sns.FacetGrid(df, **g, margin_titles = True)
            grid.map(sns.barplot, dropdown_x.dropdown.value, dropdown_y.dropdown.value)
            grid.add_legend()
            grid.fig.suptitle(title)
            #plt.legend(loc = 2, bbox_to_anchor = (1,1))
        else:
            bar = sns.barplot(x=dropdown_x.dropdown.value, y=dropdown_y.dropdown.value, **d, data=df).set(title = title)
            plt.legend(loc = 2, bbox_to_anchor = (1,1))
 
        if dropdown_pattern.dropdown.value != 'False':
            if dropdown_row.dropdown.value != 'None' or dropdown_column.dropdown.value != 'None':
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
        clear_output(wait=True)
        display_df(df)
        display_widgets()
        plt.show()

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
        #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
        right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                            width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
        right_box = VBox([right_label, right_box1, draw_button], layout = col_layout_r) 
        display(right_box)
        # if toggle.value == True:
        #     display(widgets.HBox([left_box, right_box]))
        # if toggle.value == False:
        #     display(right_box)

    
    def type_changed(d):
        if d['type'] =='change' and d['name']=='value':
            display_widgets()

    dropdown_type.observe(type_changed)






    # option은 그때그때 변경

    def compose_box(dropdowns):
        if len(dropdowns) <=3:
            row1 = HBox(dropdowns, layout=row_layout)
            return VBox([row1, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
        elif len(dropdowns)==4:
            row1 = HBox(dropdowns[0:2], layout=row_layout)
            row2 = HBox(dropdowns[2:], layout = row_layout)
        else:
            row1 = HBox(dropdowns[0:3], layout=row_layout)
            row2 = HBox(dropdowns[3:], layout = row_layout)


        return VBox([row1,row2, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center',
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

    accordion = widgets.Accordion(children=[widgets.IntSlider()], selected_index = None, layout=Layout(margin = '10px',width='90%'))
    accordion.set_title(0, 'Detail')

    ## Accordian Box # chart drawing 함수들이 여기서 얻은 정보들을 갖고실행될 수 있도록
    def compose_detail_tab():
        class tick(object):
            def __init__(self, description):
                self.label = HTML(value=description)
                self.min = FloatText(description='Min:',disabled=False)
                self.max = FloatText(description='Max:',disabled=False)
                self.interval = FloatText(description='Interval:',disabled=False)
                self.box = VBox([self.label, HBox([self.min, self.max, self.interval])])
        
        boxes = []
        if dropdown_type.value == 'Line' or dropdown_type.value == 'Scatter' or dropdown_type.value == 'Heatmap'or dropdown_type.value == 'Surface': # xticks
            x_tick = tick('X-tick')
            boxes.append(x_tick.box)
        
        y_tick = tick('Y-tick')
        boxes.append(y_tick)
        
        if dropdown_type.value == 'Surface':
            z_tick = tick('Z-tick')
            boxes.append(z_tick)
        

    # X ticks 
    # 조건 numeric할 것
    # 최소값, 최댓값, 간격
    # plt.xticks(np.arange(min(x), max(x)+1, 1.0))
    # xlabel
    # xscale
    # Y ticks
    
    # Z ticks

    # x scale
    ##

    def draw_on_click_callback(clicked_button: widgets.Button) -> None:
        if dropdown_type.value == 'Bar':
            draw_bar_chart(df)
        elif dropdown_type.value =='Scatter':
            draw_scatter_chart(df)
        elif dropdown_type.value == 'Line':
            draw_line_chart(df)
        # elif dropdown_type.value == 'Box':
        #     draw_box_chart(df)
        elif dropdown_type.value == 'Heatmap':
            draw_heatmap_chart(df)
        elif dropdown_type.value == 'Surface':
            draw_surface_chart(df)
        """버튼이 눌렸을 때 동작하는 이벤트 핸들러"""

    draw_button = Button(description = "Draw", button_style='primary', layout = Layout(flex = '0 0 auto', align_self='flex-end', width = '20%', margin ='10px 30px'))
    draw_button.on_click(draw_on_click_callback)





    dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d,dropdown_y.d, dropdown_marker.d, dropdown_column.d]
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

    display(right_box)
