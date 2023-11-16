#!/bin/bash

source_dir="/root/DBEDA/benchmark/data"  # 원본 파일이 있는 폴더
destination_dir="/root/DBEDA/benchmark/dataset/raw_data"  # 복사할 폴더
name="cpu"  # 파일 이름에서 추출할 이름 부분

# 최댓값에 1을 더함
new_number=24

# 원본 폴더에서 "${name}_number.csv" 파일 찾아 이름 변경하고 복사
for file in "$source_dir"/"${name}"_*.csv; do
  if [ -f "$file" ]; then
    # 파일 이름에서 숫자 부분 추출
    numeric_part=${file##*_}
    numeric_part=${numeric_part%.csv}
    
    # 새로운 파일 이름 생성
    new_numeric_part=$((numeric_part + new_number))
    new_file_name="${name}_${new_numeric_part}.csv"

    # 파일 복사
    cp "$file" "$destination_dir/$new_file_name"
  fi
done
