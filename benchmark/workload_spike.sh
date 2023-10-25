#!/bin/bash

# CSV 파일 이름 및 헤더 작성
csv_file="benchmark_logs.csv"
echo "Iteration,Start Time,End Time,Anomaly Start Time,Anomaly End Time" > $csv_file

normal="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=16 --time=1800 --report-interval=60 oltp_read_write run"

# 총 실행 시간 (초)
total_time=1300

# 10번의 실험 반복
for i in $(seq 1 10)
do
    # Random한 시간 설정 (1에서 300 사이의 랜덤한 값)
    random_time=$((300 + $RANDOM % 401))
    # 현재 시간 기록
    start_time=$(date +"%Y-%m-%d %H:%M:%S")

    # Anomaly 명령어 설정, 실행 시간을 30초에서 300초까지 증가
    anomaly_time=$((30 * i))
    anomaly="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=64 --time=$anomaly_time --report-interval=60 oltp_read_write run"

    # Random한 시간만큼 "normal" 명령어 실행
    echo "[$start_time] Running normal for $random_time seconds: $normal"
    timeout $random_time $normal

    # 현재 시간 다시 기록
    anomaly_start_time=$(date +"%Y-%m-%d %H:%M:%S")

    # Anomaly 명령어 실행
    echo "[$anomaly_start_time] Running anomaly (time: $anomaly_time seconds): $anomaly"
    $anomaly

    # 현재 시간 다시 기록
    anomaly_end_time=$(date +"%Y-%m-%d %H:%M:%S")

    # 남은 시간 동안 "normal" 명령어 실행
    remaining_time=$((total_time - random_time - anomaly_time))
    if [ $remaining_time -gt 0 ]; then
        remaining_start_time=$(date +"%Y-%m-%d %H:%M:%S")
        echo "[$remaining_start_time] Running normal for remaining $remaining_time seconds: $normal"
        timeout $remaining_time $normal
    fi
    end_time=$(date +"%Y-%m-%d %H:%M:%S")

    # CSV 파일에 로그 추가
    echo "$i,$start_time,$end_time,$anomaly_start_time,$anomaly_end_time" >> $csv_file
    
done