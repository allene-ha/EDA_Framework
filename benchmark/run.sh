#!/bin/bash

normal_thread_count=16
#anomaly_thread_count="$2"

# normal 명령어 생성
normal="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=$normal_thread_count --time=600 --report-interval=10 oltp_read_write run"

# anomaly 명령어 생성
anomaly="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=$anomaly_thread_count --time=300 --report-interval=60 oltp_read_write run"

# "normal" 명령어 실행
echo "Running normal: $normal"
$normal

# "anomaly" 명령어 실행
#echo "Running anomaly: $anomaly"
#$anomaly
