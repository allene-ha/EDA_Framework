# 데이터베이스 이름
db_name="oltpbench"

# 데이터베이스가 이미 존재하는지 확인
if psql -lqt | cut -d \| -f 1 | grep -qw $db_name; then
    echo "Database $db_name already exists."
else
    # 데이터베이스 생성
    su - postgres -c "psql -c 'CREATE DATABASE $db_name;'"
    #CREATE DATABASE $db_name
    echo "Database $db_name created."
fi

echo "Prepare OLTP Benchmark"
sysbench --db-driver=pgsql --pgsql-user=postgres --pgsql-port=5434 --pgsql-password=postgres --pgsql-db=oltpbench --table_size=800000 --tables=150 --threads=64 --time=1800 --report-interval=60 oltp_read_write prepare

