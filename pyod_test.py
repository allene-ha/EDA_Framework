
import numpy as np
import pandas as pd
from pyod.models.auto_encoder import AutoEncoder
df = pd.read_csv('./CurrentVoltage.csv', parse_dates = ['DeviceTimeStamp'])
df = df.dropna(how = 'any', axis = 0) #remove empty rows in any
df.info() #minutes granularity
# Set up model
clf1 = AutoEncoder(hidden_neurons =[10, 10, 2, 10, 10])
data = df.iloc[:,1:]
clf1.fit(data)
# Get the outlier scores for the train data
y_train_scores = clf1.decision_scores_
df['score'] = y_train_scores

# Visualization
import plotly.graph_objects as go
from plotly.subplots import make_subplots
fig = make_subplots(rows=2, cols=1)
fig.add_trace(
    go.Scatter(x=df['Date'], y=df['INUT'], name="INUT"),
    row=1, col=1
)
fig.add_trace(
    go.Scatter(x=df['Date'], y=df['score'], name="Score"),
    row=2, col=1
)