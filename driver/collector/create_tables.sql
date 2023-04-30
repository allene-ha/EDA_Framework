CREATE TABLE bgwriter (
    timestamp TIMESTAMP,
    dbid int,
   
    PRIMARY KEY (timestamp)
);
CREATE TABLE access (
    timestamp TIMESTAMP,
    dbid int,
    PRIMARY KEY (timestamp)
);
CREATE TABLE io (
    timestamp TIMESTAMP,
    dbid int,
    PRIMARY KEY (timestamp)
);
CREATE TABLE os_metric (
    timestamp TIMESTAMP,
    dbid int,
    PRIMARY KEY (timestamp)
);
CREATE TABLE sessions (
    timestamp TIMESTAMP,
    dbid int,
    PRIMARY KEY (timestamp)
);
CREATE TABLE active_sessions (
    timestamp TIMESTAMP,
    dbid int,
    PRIMARY KEY (timestamp)
);
CREATE TABLE waiting_sessions (
    timestamp TIMESTAMP,
    dbid int,
    PRIMARY KEY (timestamp)
);
CREATE TABLE database_statistics (
    timestamp TIMESTAMP,
    dbid int,
    datid int,
   
    PRIMARY KEY (timestamp, datid)
);
CREATE TABLE conflicts (
    timestamp TIMESTAMP,
    dbid int,
    datid int,
   
    PRIMARY KEY (timestamp, datid)
);
CREATE TABLE query_statistics (
    timestamp TIMESTAMP,
    dbid int,
    queryid varchar,
   
    PRIMARY KEY (timestamp, queryid)
);
