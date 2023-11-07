-- metric table creation
CREATE TABLE bgwriter (
    timestamp TIMESTAMP,
    dbid varchar(36),
   
    PRIMARY KEY (timestamp)
);
CREATE TABLE access (
    timestamp TIMESTAMP,
    dbid varchar(36),
    PRIMARY KEY (timestamp)
);
CREATE TABLE io (
    timestamp TIMESTAMP,
    dbid varchar(36),
    PRIMARY KEY (timestamp)
);
CREATE TABLE os_metric (
    timestamp TIMESTAMP,
    dbid varchar(36),
    PRIMARY KEY (timestamp)
);
CREATE TABLE sessions (
    timestamp TIMESTAMP,
    dbid varchar(36),
    PRIMARY KEY (timestamp)
);
CREATE TABLE active_sessions (
    timestamp TIMESTAMP,
    dbid varchar(36),
    PRIMARY KEY (timestamp)
);
CREATE TABLE waiting_sessions (
    timestamp TIMESTAMP,
    dbid varchar(36),
    PRIMARY KEY (timestamp)
);
CREATE TABLE database_statistics (
    timestamp TIMESTAMP,
    dbid varchar(36),
    datid int,
   
    PRIMARY KEY (timestamp, datid)
);
CREATE TABLE conflicts (
    timestamp TIMESTAMP,
    dbid varchar(36),
    datid int,
   
    PRIMARY KEY (timestamp, datid)
);
CREATE TABLE query_statistics (
    timestamp TIMESTAMP,
    dbid varchar(36),
    queryid varchar,
   
    PRIMARY KEY (timestamp, queryid)
);
-- custom table creation

CREATE TABLE performance (
    timestamp TIMESTAMP,
    dbid varchar(36), 
    PRIMARY KEY (timestamp, queryid)
);


-- derived metric table creation
CREATE TABLE load_prediction (
    dbid varchar(36) NOT NULL,
    analysis_time TIMESTAMP NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metric varchar(200),
    predicted FLOAT NOT NULL,
    upper_bound FLOAT,
    lower_bound FLOAT,
    PRIMARY KEY (dbid, timestamp, analysis_time)
);
CREATE TABLE anomaly_time_interval (
    dbid varchar(36) NOT NULL,
    analysis_time TIMESTAMP NOT NULL,
    metric varchar(200),
    start TIMESTAMP NOT NULL,
    "end" TIMESTAMP NOT NULL,
    severity FLOAT,
    PRIMARY KEY (dbid, analysis_time)
);
CREATE TABLE anomaly_explanation (
    dbid varchar(36) NOT NULL,
    analysis_time TIMESTAMP NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    anomaly_score FLOAT NOT NULL,
    is_anomaly BOOLEAN NOT NULL,
    anomaly_cause varchar(200),
    dataset varchar(36),
    metric varchar(200),
    PRIMARY KEY (dbid, timestamp, analysis_time)
);
CREATE TABLE anomaly_scorer (
    dbid varchar(36) NOT NULL,
    analysis_time TIMESTAMP NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metric varchar(200),
    anomaly_score FLOAT NOT NULL,
    PRIMARY KEY (dbid, timestamp, analysis_time)
);
CREATE TABLE anomaly_detector (
    dbid varchar(36) NOT NULL,
    analysis_time TIMESTAMP NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    metric varchar(200),
    anomaly_label FLOAT NOT NULL,
    PRIMARY KEY (dbid, timestamp)
);
