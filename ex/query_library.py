def get_query_library(table_name='', limit=5):

    
    query_library = {}

    # 1 Data

    query_library['data'] = {}
    data = query_library['data']

    data['Data_Types'] = """SELECT
    DATA_TYPE AS Data_Type,
    COUNT(1) AS Number
    FROM
    information_schema.COLUMNS
    WHERE TABLE_SCHEMA NOT IN ('information_schema', 'mysql','performance_schema')
    GROUP BY Data_Type
    ORDER BY Number""" # 테이블별 데이터 타입의 개수

    data['Database_Size'] = f"""SELECT
    TABLE_SCHEMA  AS Database,
    SUM(
        (data_length + index_length) / (1024 * 1024)
    ) AS Database_Size
    FROM
    information_schema.TABLES
    GROUP BY table_schema
    ORDER BY Database_Size DESC
    LIMIT {limit};""" # Top 5 데이터베이스의 사이즈

    data['Diskinfo'] = """SELECT
    TABLE_SCHEMA AS Database,
    TABLE_NAME AS Table,
    TABLE_ROWS AS Rows
    FROM
    information_schema.TABLES;""" # 테이블명 및 보유한 레코드 수

    # 2 Index
    query_library['index'] = {}
    index = query_library['index']

    index['FullText_Index'] = """SELECT
    TABLE_SCHEMA AS Table_Schema,
    TABLE_NAME AS Table_Name,
    INDEX_NAME AS Index_Name,
    SEQ_IN_INDEX AS Seq_In_Index,
    COLUMN_NAME AS Column_Name,
    CARDINALITY AS Cardinality,
    NULLABLE AS Nullable
    FROM
    information_schema.STATISTICS
    WHERE INDEX_TYPE LIKE 'FULLTEXT%'
    ORDER BY TABLE_SCHEMA,
    TABLE_NAME;""" # FULLTEXT 인덱스 목록

    index['Schema_Redundant_Index'] = f"""SELECT *
    FROM sys.schema_redundant_indexes LIMIT {limit};""" # 불필요한 중복되는 인덱스

    index['Unused_Indexes_In_Schema'] = f"""SELECT *
    FROM sys.schema_unused_indexes LIMIT {limit};""" # 테이블에서 사용되지 않은 인덱스

    index['WorstIndex'] = f"""SELECT
    t.TABLE_SCHEMA AS Db,
    t.TABLE_NAME AS Table,
    s.INDEX_NAME AS Index_Name,
    s.COLUMN_NAME AS Field_Name,
    s.SEQ_IN_INDEX Seq_In_Index,
    s2.max_columns AS Max_Cols,
    s.CARDINALITY AS Card,
    t.TABLE_ROWS AS Est_rows,
    ROUND(
        (
        (
            s.CARDINALITY / IFNULL(t.TABLE_ROWS, 0.01)
        ) * 100
        ),
        2
    ) AS Sel %
    FROM
    INFORMATION_SCHEMA.STATISTICS s
    INNER JOIN INFORMATION_SCHEMA.TABLES t
        ON s.TABLE_SCHEMA = t.TABLE_SCHEMA
        AND s.TABLE_NAME = t.TABLE_NAME
    INNER JOIN
        (SELECT
        TABLE_SCHEMA,
        TABLE_NAME,
        INDEX_NAME,
        MAX(SEQ_IN_INDEX) AS max_columns
        FROM
        INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA != 'mysql'
        GROUP BY TABLE_SCHEMA,
        TABLE_NAME,
        INDEX_NAME) AS s2
        ON s.TABLE_SCHEMA = s2.TABLE_SCHEMA
        AND s.TABLE_NAME = s2.TABLE_NAME
        AND s.INDEX_NAME = s2.INDEX_NAME
    WHERE t.TABLE_SCHEMA != 'mysql'
    LIMIT {limit} ;""" # 성능이 가장 떨어지는 상위 10개 인덱스


    # 3 Host

    query_library['Host'] = {}
    host = query_library['Host']
    host['Host_Hitting_by_File_io'] = f"""SELECT host
    FROM sys.x$host_summary
    ORDER BY file_ios DESC LIMIT {limit};""" # 총 파일 I/O를 기반으로 서버에 도달한 호스트

    host['Host_Hitting_by_Tablescans'] = f"""SELECT host
    FROM sys.x$host_summary
    ORDER BY table_scans DESC LIMIT {limit};""" # 테이블 스캔을 통해 서버에 도달한 호스트

    # 4 User

    query_library['User'] = {}
    user = query_library['User']
    user['Users_Connected'] = """SELECT
    SUBSTRING_INDEX(HOST, ':', 1) AS Host_Name,
    GROUP_CONCAT(DISTINCT USER) AS Users,
    COUNT(*) AS No_Of_Connections
    FROM
    information_schema.PROCESSLIST
    WHERE user != 'system user'
    GROUP BY Host_Name
    ORDER BY No_Of_connections DESC ;""" # 현재 연결된 사용자

    user['Users_Hitting_by_File_io'] = f"""SELECT user
    FROM sys.x$user_summary
    ORDER BY file_ios DESC LIMIT {limit};""" # 총 파일 I/O를 기준으로 서버에 접속한 사용자

    user['Users_Hitting_by_Tablescans'] = f"""SELECT user
    FROM sys.x$user_summary
    ORDER BY table_scans DESC LIMIT {limit};""" # 테이블 스캔으로 서버에 접속한 사용자

    user['Users_statements_executed'] = f"""SELECT *
    FROM sys.x$user_summary_by_statement_latency
    ORDER BY total_latency DESC LIMIT {limit};""" # 사용자가 실행한 총 명령문 수를 기반으로 한 사용자

    # 5 Object

    query_library['Object'] = {}
    object = query_library['Object']
    object['Non-InnoDB_Tables_Count'] = """SELECT
    COUNT(*) as count
    FROM
    INFORMATION_SCHEMA.TABLES
    WHERE
    ENGINE != 'InnoDB'
    AND TABLE_SCHEMA NOT IN ('mysql','performance_schema',
    'information_schema');""" # Innodb가 아닌 테이블 수	

    object['Object_accessed_the_most'] = f"""SELECT table_schema,table_name
    FROM sys.x$schema_table_statistics
    ORDER BY io_read_latency DESC LIMIT {limit};""" # 가장 많이 엑세스한 테이블

    object['Storage_Engine'] = """SELECT
    ENGINE AS Engine,
    COUNT(*) AS Tables,
    CONCAT(
        ROUND(SUM(table_rows) / 1000000, 2),
        'M'
    ) AS Rows,
    CONCAT(
        ROUND(
        SUM(data_length) / (1024 * 1024 * 1024),
        2
        ),
        'G'
    ) AS Data,
    CONCAT(
        ROUND(
        SUM(index_length) / (1024 * 1024 * 1024),
        2
        ),
        'G'
    ) AS Index,
    CONCAT(
        ROUND(
        SUM(data_length + index_length) / (1024 * 1024 * 1024),
        2
        ),
        'G'
    ) AS Total_Size,
    ROUND(
        SUM(index_length) / SUM(data_length),
        2
    ) AS Index_Frac
    FROM
    information_schema.TABLES
    WHERE ENGINE != 'NULL'
    GROUP BY ENGINE
    ORDER BY SUM(data_length + index_length) DESC ;""" # 테이블별 엔진 타입

    object['Table_InnoDB_Buffer_Pool'] = f"""SELECT object_schema,object_name
    FROM sys.x$innodb_buffer_stats_by_table
    ORDER BY pages DESC LIMIT {limit};""" # InnoDB 버퍼 풀에 가장 많은 페이지를 저장하는 테이블

    object['Tables_Size'] = """SELECT
    COUNT(*) AS Tables,
    CONCAT(
        ROUND(SUM(table_rows) / 1000000, 2),
        'M'
    ) AS Rows,
    CONCAT(
        ROUND(
        SUM(data_length) / (1024 * 1024 * 1024),
        2
        ),
        'G'
    ) AS Data,
    CONCAT(
        ROUND(
        SUM(index_length) / (1024 * 1024 * 1024),
        2
        ),
        'G'
    ) AS Index,
    CONCAT(
        ROUND(
        SUM(data_length + index_length) / (1024 * 1024 * 1024),
        2
        ),
        'G'
    ) AS Total_Size,
    ROUND(
        SUM(index_length) / SUM(data_length),
        2
    ) AS Index_Frac
    FROM
    information_schema.TABLES ;""" # 총 테이블 수와 크기

    object['Tables_Without_PK_UK'] = """SELECT DISTINCT
        t.TABLE_SCHEMA,
        t.TABLE_NAME,
        ENGINE
    FROM
        information_schema.TABLES t
        INNER JOIN information_schema.COLUMNS c
                ON t.TABLE_SCHEMA = c.TABLE_SCHEMA
                AND t.TABLE_NAME = c.TABLE_NAME
                AND t.TABLE_SCHEMA NOT IN (
                    'performance_schema',
                    'information_schema',
                    'mysql'
                );""" # Primary Key / Unique Key가 없는 테이블

    object['Tables_Without_Constraints'] = """SELECT
    COUNT(1) AS COUNT
    FROM INFORMATION_SCHEMA.TABLES A
    LEFT JOIN INFORMATION_SCHEMA.TABLE_CONSTRAINTS B
        ON A.TABLE_NAME=B.TABLE_NAME
        AND A.TABLE_SCHEMA =B.TABLE_SCHEMA
    WHERE A.TABLE_SCHEMA NOT IN ('mysql','information_schema','performance_schema')
        AND B.TABLE_NAME IS NULL
        AND B.TABLE_SCHEMA is NULL;"""

    object['Tables_FK_Constraints'] = """SELECT referenced_table_name parent, table_name child, constraint_name
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE referenced_table_name IS NOT NULL
    ORDER BY referenced_table_name;""" # FK 제약 조건 테이블 찾기

    object['Hot_Tables'] = f"""select * from sys.io_global_by_file_by_bytes where file like '%.ibd' LIMIT {limit};""" 

    object['Hot_Schemas'] = f"""`select SUBSTRING_INDEX(SUBSTRING_INDEX(file,'/', 5),'/',-1) AS d, format_bytes(sum(total)) as bytes from x$io_global_by_file_by_bytes where file like '%.ibd' group by d order by sum(total) desc LIMIT {limit};`"""

    # 6 Performance

    query_library['Performance'] = {}
    performance = query_library['Performance']
    performance['Performance_Schema_Events'] = """SELECT
    EVENT_NAME,
    MAX_TIMER_READ,
    AVG_TIMER_READ,
    MAX_TIMER_WRITE,
    AVG_TIMER_WRITE,
    MAX_TIMER_MISC,
    AVG_TIMER_MISC
    FROM performance_schema.file_summary_by_event_name;""" # Performance_Schema 메트릭

    performance['Primary_Key_Ratio'] = """SELECT
    @tblWithoutPk :=
    (SELECT
        COUNT()
        FROM     information_schema.TABLES AS t     
        LEFT JOIN information_schema.KEY_COLUMN_USAGE AS c       
        ON t.TABLE_NAME = c.TABLE_NAME       
        AND c.CONSTRAINT_SCHEMA = t.TABLE_SCHEMA   
        WHERE t.TABLE_SCHEMA NOT IN ('information_schema', 'mysql','performance_schema')     
        AND constraint_name IS NULL) AS Tables_Without_PK,   @tblwithPk :=   (SELECT     COUNT()
    FROM
        information_schema.TABLES AS t
        LEFT JOIN information_schema.KEY_COLUMN_USAGE AS c
        ON t.TABLE_NAME = c.TABLE_NAME
        AND c.CONSTRAINT_SCHEMA = t.TABLE_SCHEMA
    WHERE t.TABLE_SCHEMA NOT IN ('information_schema', 'mysql','performance_schema')
        AND constraint_name = 'PRIMARY') AS Tables_With_PK,
    @tblwithPk / (@tblWithoutPk + @tblwithPk) * 100 AS Ratio ;""" # Primary Key Ratio

    performance['Tables_with_full_table_scans'] = f"""SELECT *
    FROM sys.x$schema_tables_with_full_table_scans
    ORDER BY rows_full_scanned DESC,latency DESC LIMIT {limit};""" # 쿼리 실행 시 전체 테이블 스캔을 수행하는 테이블 확인

    performance['Tables_Fragmentation'] = """SELECT TABLE_NAME, (DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024 AS sizeMb,DATA_FREE / 1024 / 1024 AS data_free_MB
    FROM information_schema.TABLES
    WHERE ENGINE LIKE 'InnoDB'
    AND TABLE_SCHEMA = 'db_name'
    AND DATA_FREE > 100 * 1024 * 1024;""" # 테이블 Fragmentation 확인


    # 7 Cluster 
    # Only MySQL Cluster v7.1.3	

    query_library['Cluster'] = {}
    cluster = query_library['Cluster']
    cluster['Cluster_Data_Free'] = """SELECT
        @ total_data_memory : = (
        SELECT
            SUM(total) AS Total_Memory
            FROM
            ndbinfo.memoryusage
            WHERE
            memory_type = 'Data memory'
        ) AS Total_Data_Memory
        ,@ used_data_memory : = (
        SELECT
            SUM(used) Used_Memory
            FROM
            ndbinfo.memoryusage
            WHERE
            memory_type = 'Data memory'
        ) AS Used_Data_Memory
        ,(@ total_data_memory - @ used_data_memory) / (@ total_data_memory) * 100 AS Percentage_Of_Free_Data_Memory;""" # 사용 가능한 데이터 메모리의 백분율

    cluster['Cluster_Nodes'] = """SELECT
    @total :=
    (SELECT
        VARIABLE_VALUE
    FROM
        information_schema.GLOBAL_STATUS
    WHERE VARIABLE_NAME = 'NDB_NUMBER_OF_DATA_NODES') AS Total,
    @running :=
    (SELECT
        VARIABLE_VALUE
    FROM
        information_schema.GLOBAL_STATUS
    WHERE VARIABLE_NAME = 'NDB_NUMBER_OF_READY_DATA_NODES') AS Running,
    @total - @running AS Nodes_Not_Running ;""" # 실행되지 않는 노드의 수를 반환하고 모든 노드가 실행 중인 경우 0을 반환

    cluster['Cluster_RedoBuffer'] = """SELECT
    @total :=
    (SELECT
        SUM(total)
    FROM
        ndbinfo.logbuffers) AS Total,
    @used :=
    (SELECT
        SUM(used)
    FROM
        ndbinfo.logbuffers) AS Used,
    ((@total - @used) / @total) * 100 AS Free_Redo_Buffer;""" # 사용 가능한 로그 버퍼 크기의 백분율

    cluster['Cluster_RedoLogspace'] = """SELECT
    @total :=
    (SELECT
        SUM(total)
    FROM
        ndbinfo.logspaces) AS Total,
    @used :=
    (SELECT
        SUM(used)
    FROM
        ndbinfo.logspaces) AS Used,
    ((@total - @used) / @total) * 100 AS Free_Redo_Log_Space ;""" # 사용 가능한 로그 공간 크기의 백분율	

    # 8 Statements

    query_library['Statements'] = {}
    statements = query_library['Statements']

    statements['most frequent query'] = f"""select * from sys.statement_analysis where query is not NULL and query <> 'COMMIT' order by exec_count desc LIMIT {limit};"""


    statements['statements with temp table'] = f"""select * from sys.statements_with_temp_tables where query like '%select%' order by exec_count desc LIMIT {limit};"""

    statements['statements with sorting'] = f"""select * from sys.statements_with_sorting where query is not null order by exec_count desc LIMIT {limit};"""
    
    statements['time consuming query'] = f"""SELECT (100 * SUM_TIMER_WAIT / sum(SUM_TIMER_WAIT) OVER ()) percent, 
        sum_timer_wait as total, 
        count_star as calls, 
        avg_timer_wait as mean,
        substring(digest_text,1,75)
FROM 
performance_schema.events_statements_summary_by_digest 
        ORDER BY sum_timer_wait DESC
        LIMIT {limit};"""
    
    
    

    # 9 Table Statistics
    # Table name 받아야 함

    table_name = 'sbtest'

    query_library['Table_Statistics'] = {}
    table_statistics = query_library['Table_Statistics']

    table_statistics['table_statistics'] = f"""select * from sys.schema_table_statistics where table_schema = {table_name} LIMIT {limit};"""

    table_statistics['table_statistics_with_buffer'] = f"""select * from sys.schema_table_statistics_with_buffer where table_schema = {table_name} LIMIT {limit};"""


    # 10

    query_library['etc'] = {}
    etc = query_library['etc']

    etc['latest_file_io'] = f"""select * from sys.latest_file_io LIMIT {limit};"""
    etc['Unclosed connections not closed properly'] = """SELECT ess.user, ess.host, (a.total_connections - a.current_connections) -ess.count_star as not_colsed, ((a.total_connections - a.current_connections)-ess.count_star)*100 / (a.total_connections - a.current_connections) as pct_not_closed 
    from performance_schema.events_statements_summary_by_account_by_event_name ess 
    JOIN performance_schema.accounts a 
    on(ess.user = a.user and ess.host = a.host) 
    where ess.event_name = 'statement/com/quit' AND (a.total_connections - a.current_connections) > ess.count_star;"""
    
    return query_library