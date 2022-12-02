# **Database Experimental Data Analysis Framework - framework For DB monitoring and tuning on jupyter notebook**

---

## **주요 기능**

데이터베이스로부터 데이터를 수집하고 전처리하여 시각화하여 데이터베이스로부터 얻은 실험 데이터를 분석하는데 활용할 수 있습니다.

---

## **설치**

### **사전 준비 사항**

Python 3.8 이상의 환경과 연결할 MySQL Database 설치가 필요합니다.

### **다운로드**

```
git clone https://Jeongeun_Ha@bitbucket.org/postech_dblab/eda_framework_visualization.git
cd eda_framework_visualization
pip install -r requirements.txt

```

---

## **데이터 수집**

### **Configuration for MySQL Connection**

`connect_config.json` 파일에 아래 예시와 같이 MySQL 연결 정보를 입력합니다. 

```
{
    "db_type":"mysql",
    "mysql_host":"localhost",
    "mysql_port":"3306",
    "mysql_user":"root",
    "mysql_password":"",
    "mysql_database":""
}
```
### **스크립트 실행을 통한 데이터 수집**

MySQL 연결을 위한 configuration 설정 이후 아래 커맨드를 터미널에 입력하면 데이터베이스로부터 데이터가 수집됩니다.

`python3 mysql_collect.py` 

파일 저장 경로를 `path.txt`를 수정하여 변경할 수 있습니다.

`CTRL+Z`로 스크립트를 종료하기 전까지 데이터가 수집됩니다.

---

## **실행**

`jupyter notebook --ip='0.0.0.0' --port=8888 --allow-root`

`EDA.ipynb` 파일을 실행합니다.

### **Import collected data**

`import_and_update_data()`

### **Visualize**

`visualize()`는 총 다섯 가지의 시각화 모드로 구성되어있습니다.

**General Visualization** : 데이터 수집 과정 없이 원하는 쿼리로 질의하고 이 질의 결과 혹은 임의의 데이터프레임을 시각화

 * Query and Visualize: 데이터베이스에 질의하고 그 결과를 시각화 할 수 있는 모드
 * Dataframe Visualizer: `visualize()` method 실행 시 dataframe input이 반드시 필요한 모드

**Specialized Visualization** : 데이터베이스 모니터링에 특화된 시각화 모드로 데이터 수집과 `import_and_update_data()`를 사전 수행해야 가능함

 * Metric Viewer: 수집된 메트릭을 시간에 따라 시각화하는 모드
 * Query Performance Viewer: 가장 리소스 소모량이 많거나 실행시간이 긴 쿼리들의 시간에 따른 퍼포먼스를 시각화하는 모드
 * Wait Time Viewer: 대기 시간을 발생시킨 요소 별로 시간에 따른 대기 시간을 시각화하는 모드

---

## **Reference**
이 프레임워크의 데이터 수집부는 OtterTune의 [ot-agent](https://github.com/ottertune/ot-agent) 코드를 기반으로 작성되었습니다.