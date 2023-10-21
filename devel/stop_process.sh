#!/bin/bash

# 주어진 포트번호
port=80

# 해당 포트번호를 사용하는 프로세스의 PID 추출
pid=$(lsof -t -i:$port)

# PID가 존재하는 경우에만 프로세스 종료
if [[ -n $pid ]]; then
    echo "Stopping process with PID $pid"
    kill -9 $pid
else
    echo "No process found running on port $port"
fi