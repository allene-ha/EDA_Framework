#!/bin/bash

# CSV 파일 이름 및 헤더 작성
csv_file="index_log.csv"
echo "Iteration,Start Time,End Time,Anomaly Start Time,Anomaly End Time" > $csv_file

normal="sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=16 --time=1300 --report-interval=60 oltp_read_write run"

# 총 실행 시간 (초)
total_time=1300

# PostgreSQL 데이터베이스 백업 디렉토리 설정

# 10번의 실험 반복
for i in $(seq 1 10)
do
    # Random한 시간 설정
    random_time=$((200 + $RANDOM % 401))
    # 현재 시간 기록
    start_time=$(date +"%Y-%m-%d %H:%M:%S")

    # Random한 시간만큼 "normal" 명령어 실행
    echo "[$start_time] Running normal for $random_time seconds: $normal"
    $normal > output.log 2>&1 &

    sleep $random_time

    # 현재 시간 다시 기록
    anomaly_start_time=$(date +"%Y-%m-%d %H:%M:%S")

    echo "[$anomaly_start_time] Start creating index"    
    #!/bin/bash

    # Open SQL script file for writing
    echo "" > create_indexes.sql

    for j in $(seq 1 150)
    do
        table="sbtest$j"
        index_name="redundant_idx_$table"

        # Append SQL commands to the script file
        echo "CREATE INDEX ${index_name}_1 ON public.$table USING btree (k);" >> create_indexes.sql
        echo "CREATE INDEX ${index_name}_2 ON public.$table USING btree (id);" >> create_indexes.sql
        #echo "CREATE INDEX ${index_name}_3 ON public.$table USING btree (pad);" >> create_indexes.sql
        #echo "CREATE INDEX ${index_name}_4 ON public.$table USING btree (c);" >> create_indexes.sql

        echo "Index creation statements added for $table"
    done

    psql --host localhost --port 5434 --username postgres --dbname oltpbench -w -f create_indexes.sql


    # Wait for 3 minutes
    sleep 180

    #!/bin/bash

    # Open SQL script file for writing
    echo "" > drop_indexes.sql

    for j in $(seq 1 150)
    do
        table="sbtest$j"
        index_name="redundant_idx_$table"

        # Append SQL commands to the script file
        echo "DROP INDEX IF EXISTS ${index_name}_1, ${index_name}_2;" >> drop_indexes.sql
        # , ${index_name}_3, ${index_name}_4
        echo "Index drop statements added for $table"
    done

    psql --host localhost --port 5434 --username postgres --dbname oltpbench -w -f drop_indexes.sql

    # 현재 시간 다시 기록
    anomaly_end_time=$(date +"%Y-%m-%d %H:%M:%S")

    echo "[$anomaly_end_time] Finished adding index"
    wait
    end_time=$(date +"%Y-%m-%d %H:%M:%S")

    # CSV 파일에 로그 추가
    echo "$i,$start_time,$end_time,$anomaly_start_time,$anomaly_end_time" >> $csv_file

done
