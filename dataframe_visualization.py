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
import itertools
import IPython.display
from IPython.display import display, clear_output
import math
import time
from matplotlib import rcParams


import seaborn as sns

#plt.style.use('seaborn-notebook')

def dataframe_visualization(df):
    class Chart(object):
        def __init__(self, type, df):
            self.type = type
            self.df = df
            self.detail = None
            self.option = {}

            # axis
            if self.type == 'Bar':
                self.x = dropdown_x_cat.dropdown.value
            else:
                self.x = dropdown_x.dropdown.value

            self.y = dropdown_y.dropdown.value # tuple
            self.z = dropdown_z.dropdown.value
            
            # other properties
            self.color = dropdown_color.dropdown.value
            self.marker = dropdown_marker.dropdown.value
            self.pattern = dropdown_pattern.dropdown.value

            # # of charts
            self.row = dropdown_row.dropdown.value
            self.column = dropdown_column.dropdown.value

        def type_to_property(self):
            df_numerics_only = self.df.select_dtypes(include=np.number)
            col_date = list(self.df.select_dtypes(include=[np.datetime64]).columns)
            col_num = list(df_numerics_only.columns)
            col_cat = [x for x in self.df.columns if x not in col_num]
            col_tot = list(self.df.columns)
            
            def type_to_x(): #candidate column의 list
                candidate = []
                if self.type == "Line":
                    if len(col_date)>0:
                        for col in col_date:
                            if self.df[col].nunique()>5:
                                candidate.append(col)
                elif self.type == "Bar":
                    if len(col_cat) == 1:
                        candidate.append(col_cat[0])
                    elif len(col_cat)>1:
                        for col in col_cat:
                            if self.df[col].nunique()<20 and self.df[col].nunique()>=5:
                                candidate.append(col)
                        if len(candidate)==0:
                            for col in col_cat:
                                if self.df[col].nunique()<20:
                                    candidate.append(col)
                else:
                    if len(col_num) == 1:
                        candidate.append(col_num[0])
                    elif len(col_num) >1:
                        for col in col_num:
                            if df[col].nunique()>=5:
                                candidate.append(col)
                return candidate
            def type_to_y_z():
                candidate = []
                for col in col_num:
                    if self.df[col].nunique()>3:
                        candidate.append(col)
                return candidate
            def candidate_to_data(cand_x, cand_y, cand_z = None):# 조합 짜는 함수
                lists = [cand_x, cand_y]
                result = []
                coeff = []
                if cand_z != None:
                    lists.append(cand_z)
                for element in itertools.product(*lists):
                    if len(element) == len(set(element)):
                        result.append(element)
                        
                        #print(self.df[element])
                        #print(self.df[element].corr())
                        if self.type == 'Scatter' or  self.type == 'Line':
                            c = self.df[list(element)].corr().iat[0,1]
                            coeff.append(c)
                
                if self.type == 'Scatter' or  self.type == 'Line':
                    coeff = list(np.abs(coeff))
            

                    #= [x for _,x in sorted(zip(coeff,result), reverse=True)]
                    sorted_result = [x for _, x in sorted(zip(coeff, result),reverse=True, key=lambda pair: pair[0])]

                    return sorted_result
                else:
                    return result
            
            def type_data_to_option(data): # dict를 return{'color':'attr', ...}
                # 처음 몇개를 순회하면서 각각 데이터를 제외하고 카테고리컬 데이터를 담은 어트리뷰트가 남았는지 검사
                # 각 어트리뷰터의 card 검사
                # 1개일 때 => 컬러,하지만 카디날리티 너무 많으면 버려
                # 2개이면 => line scatter 면 marker 추가, card 더 높은것이 컬러 적은것이 마커
                # 그 이상인데 나머지 카디날리티가 3 이하일때 row, col에 할당. 먼저 col하고 다음에 row, 
                result = []
                for element in data[:4]:
                    option = self.option
                    cat_cand = [x for x in col_cat if x not in element and self.df[x].nunique()>1] # 데이터를 제외하고 카테고리컬 데이터 컬럼이 남았는지 검사
                    if len(cat_cand) == 0:
                        result.append([element, option])
                    elif len(cat_cand) == 1:
                        option['hue'] = cat_cand[0]
                        result.append([element, option]) # tuple and dict for options
                    elif len(cat_cand)>1:
                        nunique = [self.df[x].nunique() for x in cat_cand]
                        
                        f = lambda i: nunique[i]
                        argmax = max(range(len(nunique)), key=f)
                        option['hue'] = cat_cand[argmax]
                        cat_cand.remove(argmax)
                        if len(cat_cand) ==1:
                            option['marker'] = cat_cand[0]
                            result.append([element, option])
                        else: # 총 cat이 3개 이상인 경우
                            nunique = [self.df[x].nunique() for x in cat_cand] # 두번째 max 찾기
                            
                            argmax = max(range(len(nunique)), key=f)
                            option['marker'] = cat_cand[argmax]
                            cat_cand.remove(argmax) 

                            nunique = [self.df[x].nunique() for x in cat_cand] # 세번째 max 찾기
                            argmax = max(range(len(nunique)), key=f)
                            if nunique[argmax] == 2 or nunique[argmax] == 3:
                                if 'col' not in option.keys():
                                    option['col'] = cat_cand[argmax]
                                    result.append([element, option])
                                elif 'row' not in option.keys():
                                    option['row'] = cat_cand[argmax]
                                    result.append([element, option])
                            
                #print(result)
                return result # element와 option(dict)의 ordered list


            if self.x == 'None':
                x_cand = type_to_x()
            else:
                x_cand = [self.x]
            if self.y[0] == 'None':
                y_cand = type_to_y_z()
            else:
                y_cand = [self.y[0]] # this can be tuple

            if self.type =='Surface' or self.type == 'Heatmap':
                if self.z == 'None':
                    z_cand = type_to_y_z()
                else:
                    z_cand = [self.z]
                comb = candidate_to_data(x_cand, y_cand, z_cand)
            else:
                comb = candidate_to_data(x_cand, y_cand)
            
            return type_data_to_option(comb)

        def recommend_drawing(self):
            data = self.type_to_property()
            elements = []
            #print(len(axes_data))
            #print(axes_data)
            for axes_data, d in data[:4]: # 반복문 하나에 차트 하나type_data_to_option(self.type, comb)
                #out = widgets.Output(layout = Layout(width = '45%'))
                plt.close()
                out = widgets.Output()#layout = Layout(width = '50%', height='50%'))
                with out:
                    plt.close()      
                    
                    if self.type =='Scatter' or self.type == 'Line' or self.type == 'Bar':
                        x,y = axes_data
                        
                        if type(y) == tuple:

                            plots = []
                            for y_ in y:
                                title = "X: " + x + " / Y: "+ y_
                                if self.type == 'Scatter':
                                    plot = sns.relplot(x=x, y=y_, legend = 'full', **d, data=self.df).set(title = title)
                                elif self.type == 'Line':
                                    plot = sns.relplot(x=x, y=y_, ci=None, legend = 'full', kind = 'line', **d, data=self.df).set(title = title)
                                elif self.type == 'Bar':
                                    plot = sns.catplot(data = self.df, kind = 'bar', x = x, y=y_, **d, legend = True, dodge = False, capsize=.15,  errwidth=1.5, facet_kws={"legend_out": True}).set(title=title)
                
                                    #if len(self.y)>1:
                                        #plt.figure()
                                plots.append(plot)
                        else:
                                
                            title = "X: " + x + " / Y: "+ y
                            if self.type == 'Scatter':
                                sns.relplot(x=x, y=y, **d, data=self.df, legend = 'full').set(title = title)
                                #plt.show()
                            elif self.type == 'Line':
                                sns.relplot(x=x, y=y,ci = None, kind = 'line', data=self.df).set(title = title)
                            elif self.type == 'Bar':
                                sns.barplot(x=x, y=y, **d, data=self.df).set(title = title)
                    elif self.type == 'Heatmap' or self.type =='Surface':
                        x, y, z = axes_data
                        title = "X: " + x + " / Y: "+ y + " / Z: "+ z
                        if self.type == "Heatmap":
                            df_pivot_mean = pd.pivot_table(self.df, index = y, columns = x, values = z, aggfunc = 'mean')
                            sns.heatmap(df_pivot_mean, cbar_kws={'label': self.z}).set(title = title)
                        if self.type == 'Surface':
                            fig = plt.gcf()
                            ax = fig.add_subplot(projection='3d')
                            df_pivot_mean = pd.pivot_table(self.df, index = y, columns = x, values = z, aggfunc = 'mean')
                            X_ = df_pivot_mean.columns.tolist()
                            Y_ = df_pivot_mean.index.tolist()
                            X = [X_ for _ in range(len(Y_))]
                            Y = [[y_]*len(X_) for y_ in Y_]
                            Z = df_pivot_mean.values
                            ax.plot_surface(X,Y,Z, cmap="inferno")
                            plt.title(title)
                    plt.gcf().tight_layout()
                    plt.ioff()
                    plt.gcf().set_size_inches(5, 3.5)

                    plt.show()
                elements.append(out)
            return HBox(elements, layout = Layout(display ='flex', flex_flow ='row wrap', justify_content='space-around'))
        
        def set_property(self):
            if self.type !='Bar':
                self.x = dropdown_x.dropdown.value
            else:
                self.x = dropdown_x_cat.dropdown.value
            self.y = dropdown_y.dropdown.value
            self.z = dropdown_z.dropdown.value
            
            # other properties
            self.color = dropdown_color.dropdown.value
            self.marker = dropdown_marker.dropdown.value
            self.pattern = dropdown_pattern.dropdown.value

            # # of charts
            self.row = dropdown_row.dropdown.value
            self.column = dropdown_column.dropdown.value

        def set_detail(self, detail):
            self.detail = detail
        
        def set_type(self, type):
            self.type = type
        
        def draw(self):
            self.set_type(dropdown_type.value)
            self.set_property()
            #print(self.x, self.y, self.z)
            if self.type == 'Bar':
                if self.x == 'None' or self.y == ('None'):
                    print("Select X, Y")
                elif self.x in self.y:
                    print("Select different columns for each axis")
                else:
                    print("HERE")
                    self.draw_bar_chart()
            elif self.type =='Scatter':
                if self.x == 'None' or self.y == ('None'):
                    print("Select X, Y")
                elif self.x in self.y:
                    print("Select different columns for each axis")
                else:
                    self.draw_scatter_chart()
            elif self.type == 'Line':
                if self.x == 'None' or self.y == ('None'):
                    print("Select X, Y")
                elif self.x in self.y:
                    print("Select different columns for each axis")
                else:
                    self.draw_line_chart()
            elif self.type == 'Heatmap':
                # if self.x == 'None' or self.y == 'None' or self.z == 'None':
                #     print("Select X, Y, color")
                # elif self.x == self.y or self.x == self.z or self.y == self.z:
                #     print("Select different columns for each axis")
                # else:
                self.draw_heatmap_chart()
            elif self.type == 'Surface':
                # if self.x == 'None' or self.y == 'None' or self.z == 'None':
                #     print("Select X, Y, Z")
                # elif self.x == self.y or self.x == self.z or self.y == self.z:
                #     print("Select different columns for each axis")
                # else:
                self.draw_surface_chart()

        def draw_surface_chart(self):

            title = self.z + ' by ' + self.y[0] + ' and '+ self.x
            plt.clf()
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d')
            df_pivot_mean = pd.pivot_table(self.df, index = self.y[0], columns = self.x, values = self.z, aggfunc = 'mean')
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
            title = self.z + ' by ' + self.y[0] + ' and '+ self.x
            plt.clf()
            #temp = df.pivot("sepal_length", "sepal_width", "petal_width")
            df_pivot_mean = pd.pivot_table(self.df, index = self.y[0], columns = self.x, values = self.z, aggfunc = 'mean')
            #index = y, colunns = x, vlaues = color
            sns.heatmap(df_pivot_mean, cbar_kws={'label': self.z}).set(title = title)
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
            #title = self.y + ' by ' + self.x
            d = {}
            if self.color != 'None':
                d['hue'] = self.color
            if self.marker != 'None':
                d['style'] = self.marker
            if self.row != 'None':
                d['row'] = self.row
            if self.column != 'None':
                d['col'] = self.column
            plt.close()
            sns.set(rc={'figure.figsize':(15,9)})

            plots = []
            for y in self.y:
                title = y +  ' by ' + self.x
                plot = sns.relplot(x=self.x, y=y, ci=None, legend = 'full', kind = 'line', **d, data=self.df).set(title = title)
                #if len(self.y)>1:
                    #plt.figure()
                plots.append(plot)



            #sns.relplot(x=self.x, y=self.y, ci=None, legend = 'full', kind = 'line', **d, data=df).set(title = title)
            if self.detail is not None:
                for plot in plots:
                    for ax in plot.axes.flat:
                        
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
            #title = self.y + ' by ' + self.x
            d = {}
            if self.color != 'None':
                d['hue'] = self.color
            if self.marker != 'None':
                d['style'] = self.marker
            if self.row != 'None':
                d['row'] = self.row
            if self.column != 'None':
                d['col'] = self.column

            plt.close()
        
            sns.set(rc={'figure.figsize':(15,9)})
            #sns.relplot(x=self.x, y=self.y, **d, data=self.df, legend = 'full').set(title = title)
            plots = []
            for y in self.y:
                title = y +  ' by ' + self.x
                plot = sns.relplot(x=self.x, y=y, legend = 'full', **d, data=self.df).set(title = title)
                #if len(self.y)>1:
                    #plt.figure()
                plots.append(plot)


            if self.detail is not None:
                for plot in plots:
                    for ax in plot.axes.flat:
                        
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
            clear_output(wait=True)
            display_df(self.df)
            display_widgets()
            d = {}
            #g = {}
            if self.color != 'None':
                d['hue'] = self.color
            if self.row != 'None':
                d['row'] = self.row
            if self.column != 'None':
                d['col'] = self.column
            plt.figure()
        
            sns.set(rc={'figure.figsize':(15,9)})
            plots = []
            for y in self.y:
                title = y +  ' by ' + self.x
                plot = sns.catplot(data = self.df, kind = 'bar', x = self.x, y=y, **d, legend = True, dodge = False, capsize=.15,  errwidth=1.5, facet_kws={"legend_out": True}).set(title=title)
                #if len(self.y)>1:
                    #plt.figure()
                plot.add_legend()
                plots.append(plot)
            
            if self.pattern !='False':
                for plot in plots:
                    for ax in plot.axes.flat:
                        bars = [rect for rect in ax.get_children() if isinstance(rect, matplotlib.patches.Rectangle)]
                        hatches = ['//', '.','+', 'o', 'x','\\']
                        bars = [rect for rect in bars if not math.isnan(rect.get_height())]
                        for i,thisbar in enumerate(bars):
                            # Set a different hatch for each bar
                            thisbar.set_hatch(hatches[i%len(hatches)])
                        ax.grid(axis='y',linestyle = 'dashed')
                        ax.set_axisbelow(True)


            # # Form a facetgrid using columns with a hue
            # if self.row != 'None' or self.column != 'None':
            #     if self.color != 'None':
            #         grid = sns.FacetGrid(self.df, **g, hue = d['hue'], margin_titles = True, legend_out = True)
            #     else: 
            #         grid = sns.FacetGrid(self.df, **g, margin_titles = True)
            #     grid.map(sns.barplot, self.x, self.y)
            #     grid.add_legend()
            #     grid.fig.suptitle(title)
            #     #plt.legend(loc = 2, bbox_to_anchor = (1,1))
            # else:
            #     bar = sns.barplot(x=self.x, y=self.y, **d, data=df).set(title = title)
            #     plt.legend(loc = 2, bbox_to_anchor = (1,1))
    
            # # if self.pattern != 'False':
            # #     if self.row != 'None' or self.column != 'None':
            # #         for ax in grid.axes_dict.values():
            # #             bars = [rect for rect in ax.get_children() if isinstance(rect, matplotlib.patches.Rectangle)]
            # #             hatches = ['-', '+', 'x', '\\', '*', 'o']
            # #             for i,thisbar in enumerate(bars):
            # #                 # Set a different hatch for each bar
            # #                 thisbar.set_hatch(hatches[i%len(hatches)])
                        
            # #     else:
            # #         # Define some hatches
            # #         hatches = ['-', '+', 'x', '\\', '*', 'o']

            # #         # Loop over the bars
            # #         for i,thisbar in enumerate(bar.patches):
            # #             # Set a different hatch for each bar
            # #             thisbar.set_hatch(hatches[i%len(hatches)])

            if self.detail is not None:
                for plot in plots:
                    for ax in plot.axes.flat:
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

            
            
            plt.show()
   

    def display_df(df):
        display(HTML(df.head().to_html()))

    display_df(df)
    class dropdown(object):
        def __init__(self, description, option, multiselect = False):
            self.label = HTML(value=description)
            self.multiselect = multiselect
            if multiselect:
                self.dropdown = widgets.SelectMultiple(
                    options=option,
                    value=(option[0],),
                    rows=3,
                    disabled=False,
                    layout = Layout(width = '90%')
                    )
            else:
                self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            self.d = VBox([self.label, self.dropdown], layout = Layout(width = '100%', align_items='center'))#, layout = Layout(flex='stretch', align_items='center'))
        def set_option(self, option):
            if self.multiselect:
                self.dropdown = widgets.SelectMultiple(
                    options=option,
                    value= (option[0],),
                    rows=3,
                    disabled=False,
                    layout = Layout(width = '90%')
                    )
            else:
                self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            #self.dropdown = widgets.Dropdown(options=option,value=option[0], layout = Layout(width = '90%'))
            self.d = VBox([self.label, self.dropdown], layout = Layout(width = '100%', align_items='center'))

    toggle_label = HTML(value="<font size = 2> Recommendation", layout = Layout(margin ='0 30px'))
    toggle = widgets.Checkbox(value=False, indent=False)


    def toggle_changed(b):
        if b['type'] =='change' and b['name']=='value':
            chart.set_type(dropdown_type.value)
            display_widgets()




    toggle.observe(toggle_changed)
    display(HBox([toggle_label, toggle]))

    col_layout = Layout(display='flex',
                        flex_flow='column wrap',
                        align_items='center',
                        border='1px solid',
                        width='100%')
    
    row_layout = Layout(display='flex',
                        flex_flow='row',
                        align_items='center',
                        align_content = 'stretch',
                        justify_content = 'center',
                        #border='solid',
                        width='90%')

    rec_label = HTML(value="<b><font size = 3> Recommended Chart")
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
            dropdowns = [dropdown_x_cat.d, dropdown_color.d, dropdown_row.d, dropdown_y.d, dropdown_pattern.d, dropdown_column.d]
        elif dropdown_type.value == 'Pie': 
            dropdowns = [dropdown_label.d, dropdown_size.d, dropdown_row.d, dropdown_column.d]
        elif dropdown_type.value == 'Heatmap': 
            dropdowns = [dropdown_x.d, dropdown_y.d, dropdown_z.d]
        elif dropdown_type.value == 'Surface': 
            dropdowns = [dropdown_x.d, dropdown_y.d, dropdown_z.d]
        else:
            print("Undefined Type")
        clear_output(wait=True)
        display(HBox([toggle_label, toggle]))
        
        right_box2 = compose_box(dropdowns)
        detail, detail_widgets = compose_detail_tab() # dict, widgets
        accordion = widgets.Accordion(children=[detail_widgets], selected_index = None, layout=Layout(margin = '10px',width='90%'))
        accordion.set_title(0, 'Detail')        #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
        right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                            width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
        right_box = VBox([right_label, right_box1, accordion, draw_button], layout = col_layout) 
        if toggle.value == True:
            recommendation = chart.recommend_drawing()
            rec_box = VBox([rec_label, recommendation], layout = col_layout)
            display(widgets.VBox([right_box, rec_box]))
        if toggle.value == False:
            display(right_box)
            

    
    def type_changed(d):
        if d['type'] =='change' and d['name']=='value':
            chart.set_type(d['new'])
            display_widgets()

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

    dropdown_x = dropdown('X-axis',col_tot_none)
    dropdown_x_cat = dropdown('X-axis',col_cat_none)
    dropdown_y = dropdown('Y-axis',col_num_none, True)
    dropdown_z = dropdown('Z-axis',col_num_none)

    dropdown_label = dropdown('Label',col_tot)
    dropdown_size = dropdown('Size',col_tot_none)


    dropdown_color = dropdown('Color',col_tot_none)
    dropdown_pattern = dropdown('Pattern',['True', 'False'])
    dropdown_marker = dropdown('marker',col_cat_none)
    dropdown_row = dropdown('Row',col_cat_none)
    dropdown_column = dropdown('Column',col_cat_none)
    chart = Chart('Line', df)

    
    def dropdown_changed(d):
        if d['type'] == 'change' and d['name'] == 'value':
            if toggle.value == True:
                chart.set_property()
                display_widgets()

    dropdown_x.dropdown.observe(dropdown_changed)
    dropdown_y.dropdown.observe(dropdown_changed)
    dropdown_z.dropdown.observe(dropdown_changed)



    output = widgets.Output(layout=Layout(width='100%'))
    rec_box = VBox([rec_label, output], layout = col_layout)
    
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
        #display_widgets()
        chart.draw()
 

    
            

    draw_button = Button(description = "Draw", button_style='primary', layout = Layout(flex = '0 0 auto', align_self='flex-end', width = '20%', margin ='10px 30px'))
    draw_button.on_click(draw_on_click_callback)





    dropdowns = [dropdown_x.d, dropdown_color.d, dropdown_row.d,dropdown_y.d, dropdown_marker.d, dropdown_column.d]
    right_box2 = compose_box(dropdowns)
    #VBox ([right_box3,right_box4, accordion], layout = Layout(display='flex', flex_flow='column', align_items='center', width='80%'))#col_layout_r2)# , layout=Layout(width='100%'))
    right_box1 = HBox([VBox([type_label, dropdown_type],layout = Layout(display='flex', flex_flow='column', align_items='center',
                        width='25%')), right_box2], layout = Layout(align_items = 'center',width = '100%')) # 비율이 1:3 정도
    right_box = VBox([right_label, right_box1, accordion, draw_button], layout = col_layout) 

    # with output: # drawing recommended Chart. only activated when recommendation toggle is on.
    #     plt.close()
    #     plt.figure(figsize = (4,3))

    #     plt.show() 

    display(HBox([right_box]))
