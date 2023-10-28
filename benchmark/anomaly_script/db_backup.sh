#!/bin/bash

# CSV 파일 이름 및 헤더 작성
csv_file="../log3/db_backup_log.csv"
echo "Iteration,Start Time,End Time,Anomaly Start Time,Anomaly End Time" > $csv_file

normal="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=32 --time=1300 --report-interval=60 oltp_read_write run"

# 총 실행 시간 (초)
total_time=600

# PostgreSQL 데이터베이스 백업 디렉토리 설정

# 10번의 실험 반복
for i in $(seq 1 10)
do
    # Random한 시간 설정 (1에서 300 사이의 랜덤한 값)
    random_time=$((100 + $RANDOM % 150))
    # 현재 시간 기록
    start_time=$(date +"%Y-%m-%d %H:%M:%S")

    # Random한 시간만큼 "normal" 명령어 실행
    echo "[$start_time] Running normal for $random_time seconds: $normal"
    $normal > output.log 2>&1 &

    sleep $random_time

    # 현재 시간 다시 기록
    anomaly_start_time=$(date +"%Y-%m-%d %H:%M:%S")
    # 데이터베이스 백업
    echo "[$anomaly_start_time] Start backup"
    backup_file="../backup.sql"
    pg_dump --host localhost --port 5434 --username postgres --dbname oltpbench -w --file $backup_file
    
    # 현재 시간 다시 기록
    anomaly_end_time=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$anomaly_end_time] Finished backup"
    wait
    end_time=$(date +"%Y-%m-%d %H:%M:%S")

    # CSV 파일에 로그 추가
    echo "$i,$start_time,$end_time,$anomaly_start_time,$anomaly_end_time" >> $csv_file

done
