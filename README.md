# DBEDA - Database Experimental Data Analysis Framework

DBEDA is an experimental data analysis framework designed for database performance monitoring in a Jupyter environment. This framework combines server and client components to collect, visualize, and analyze performance data from integrated databases.

![DBEDA Logo](https://github.com/jeha-dblab/dbeda_framework/assets/80744377/a4f7cfe8-7dba-455e-ba89-43b74791fd84)

## Environment Setup

### Server

To set up the server component, follow these steps:

- Pull the Docker container for the server:
```docker pull nvidia/cuda:11.7.0-cudnn8-runtime-ubuntu20.04```

- Start the DBEDA server using Docker Compose:
```docker-compose up```

- Run these commands to set up the server:
   ```
   service postgresql start
   cd /root/DBEDA/server
   pip install -r server_requirements.txt
   python3 server_collector.py
   ```

### Client

To set up the client component, follow these steps:

1. **Client Container**:
   - Run a Docker container for the client:

     ```bash
     docker run -it --name dbeda-client --network dbeda-network ubuntu:20.04 /bin/bash
     ```

2. **Database Setup**:
   - Install [PostgreSQL](https://www.postgresql.org/download/linux/ubuntu/).
   - Modify the configuration file of the client's database (e.g., /etc/postgresql/14/main/postgresql.conf) to allow data collection:

     ```ini
     listen_address = '*'

     # For collecting query statistics
     shared_preload_libraries = 'pg_stat_statements'
     pg_stat_statements.track = all
     ```

   - Run the PostgreSQL DB and execute the command:

     ```sql
     CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
     ```

   - Register the IP address that is allowed to connect in pg_hba.conf (e.g., host all all dbeda.dbeda-network trust).

## Example Usage

### Register Database Configuration

Register the configuration of the database for collecting performance data:

```python
from client_side import *
config = connect_db(db_type='postgres', host='dbeda-client', database='test_cli', user='postgres', password='postgres', port='5432')
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
