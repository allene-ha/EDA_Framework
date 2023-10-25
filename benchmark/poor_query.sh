#!/bin/bash

# CSV 파일 이름 및 헤더 작성
csv_file="poor_query_log.csv"
echo "Iteration,Start Time,End Time,Anomaly Start Time,Anomaly End Time" > $csv_file

normal="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=16 --time=513 --report-interval=60 oltp_read_write run"

# 총 실행 시간 (초)
total_time=1300

# PostgreSQL 데이터베이스 백업 디렉토리 설정

# 10번의 실험 반복
for i in $(seq 1 1)
do
    # Random한 시간 설정 (1에서 300 사이의 랜덤한 값)
    random_time=$((30 + $RANDOM % 40))
    # 현재 시간 기록
    start_time=$(date +"%Y-%m-%d %H:%M:%S")

    # Random한 시간만큼 "normal" 명령어 실행
    echo "[$start_time] Running normal for $random_time seconds: $normal"
    $normal > output.log 2>&1 &

    sleep $random_time

    # 현재 시간 다시 기록
    anomaly_start_time=$(date +"%Y-%m-%d %H:%M:%S")

    echo "[$anomaly_start_time] Start poorly designed join query"    
    #!/bin/bash
        
    psql --host localhost --port 5434 --username postgres --dbname oltpbench -w -c "SELECT a.*, b.* FROM sbtest1 a INNER JOIN sbtest2 b ON a.id = b.id WHERE a.k > (SELECT AVG(k) FROM sbtest3);" > poor_query_result.txt

    # 현재 시간 다시 기록
    anomaly_end_time=$(date +"%Y-%m-%d %H:%M:%S")

    echo "[$anomaly_end_time] Finished poorly designed join query"
    wait
    end_time=$(date +"%Y-%m-%d %H:%M:%S")

    # CSV 파일에 로그 추가
    echo "$i,$start_time,$end_time,$anomaly_start_time,$anomaly_end_time" >> $csv_file

done
