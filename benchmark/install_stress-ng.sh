if ! [ -x "$(command -v stress-ng)" ]; then
    echo "stress-ng가 설치되지 않았습니다. 설치를 진행합니다."

    # 패키지 관리자에 따라 설치 명령을 조정
    if [ -x "$(command -v apt-get)" ]; then
        # Debian/Ubuntu
        sudo apt-get install stress-ng    
    fi

    echo "stress-ng가 성공적으로 설치되었습니다."
fi