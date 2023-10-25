# DBEDA - Database Experimental Data Analysis Framework

DBEDA is an experimental data analysis framework designed for database performance monitoring in a Jupyter environment. This framework combines server and client components to collect, visualize, and analyze performance data from integrated databases.

![DBEDA Logo](https://github.com/jeha-dblab/dbeda_framework/assets/80744377/a4f7cfe8-7dba-455e-ba89-43b74791fd84)

## Environment Setup
- Start the DBEDA server and client using Docker Compose:
```docker compose up```

### Server
To set up the server component, follow these steps:
- Run these commands to set up the server:
   ```
   service postgresql start
   cd /root/DBEDA/server
   pip install -r server_requirements.txt
   python3 server_collector.py
   ```
### Client
To set up the client component, follow these steps:
- Run these commands to set up the client:
   ```
   service postgresql start
   cd /root/DBEDA/client
   pip install -r client_requirements.txt
   jupyter-notebook --allow-root
   ```

## Example Usage
Click `client_tutorial.ipynb`

### Register Database Configuration

Register the configuration of the database for collecting performance data:

```python
from client_side import *
config = connect_db(db_type='postgres', host='dbeda-client', database='test_cli', user='postgres', password='postgres', port='5434')
collect_performance_data(config)
```
### Data Visualization
Execute a widget to visualize the collected performance data:

```python
visualize(config)
```
### Data Extraction
Extract the desired performance data:
```python
data = query_performance_data(config, table='os_metric', metrics='cpu_percent', task='load prediction', recent_time_window='1 day')
```
### Model Traning and Prediction
Train a model, retrieve the trained model, and make predictions:

```python
response = train(config, train_df, 'load prediction', pipeline='RNN')
get_trained_model(config, 'load prediction')
predicted = predict(config, 'load prediction', metric='tps', path="darts_TCN_20230523_150814.pickle")
```
## Contributing
Contributions to the DBEDA framework are welcome. If you have suggestions or improvements, please feel free to open issues or submit pull requests.
