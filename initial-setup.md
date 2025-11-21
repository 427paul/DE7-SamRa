# Initial-Setup
본 페이지에서는 AWS EC2에 설치된 과정을 설명한다.

## EC2 인스턴스
- OS : Ubuntu
- Amazon Machine Image(AMI) : Ubuntu Server 24.04 LTS
- Instance : m7i-flex.large (프리 티어 기준 사용 가능한 고성능 인스턴스)
- Storage : 10GiB
- Inbound Rules : 0.0.0.0:8080 (Airflow 사용을 위한 8080 포트 개방)

## install_airflow.sh
두 공식 홈페이지의 설명에 따라 install_airflow.sh 작성
- Docker : https://docs.docker.com/engine/install/ubuntu/#upgrade-docker-engine-1
- Airflow : https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html

## Docker & Airflow 설치

### 1. sh 파일 실행
로컬에 git clone을 하였다면, install_airflow.sh의 ```Installing Airflow``` 단계는 주석처리 후 진행
```
sh install_airflow.sh
```
### 2. 설정 추가
./airflow_project/.env 파일에 airflow 아이디와 비밀번호 추가
```
_AIRFLOW_WWW_USER_USERNAME=your_id
_AIRFLOW_WWW_USER_PASSWORD=your_password
```
./airflow_project/docker-compose.yml 파일에 examples를 false로 설정
```
environment:
    ...
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
```
./airflow_project/dags/mois_report_slack.py 에서 사용되는 라이브러리 추가
```
environment:
    ...
    _PIP_ADDITIONAL_REQUIREMENTS: ${_PIP_ADDITIONAL_REQUIREMENTS:- bs4 gradio_client PyPDF2}
```

### 3. Docker 실행
docker compose 명령어들을 통해 airflow 실행
```
sudo docker compose run airflow-cli airflow config list
sudo docker compose up airflow-init
sudo docker compose up -d
```
