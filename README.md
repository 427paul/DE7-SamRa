# 🚀 날씨 대시보드 & 날씨 알림 챗봇

> End-to-End 데이터 파이프라인 실습을 위해 날씨 도메인의 데이터를 데이터 파이프라인(Airflow, Docker)을 통해 분석하고 시각화(Superset)해본다.

## 💡 개요 (Overview)

본 프로젝트는 날씨 데이터를 Airflow를 활용해 데이터 추출(Extract), 정제(Transform), 적재(Load) 작업을 스케줄링하고, 적재된 데이터를 Superset에서 시각화하여 사용자에게 직관적인 기상 분석 환경을 제공한다.

또한 주요 기상 변화나 예보 등을 Slack 알림으로 전달하여 신속한 정보 확인이 가능하도록 설계하였다.

## 프로젝트 구성도
```text
.
├── .github/                       # GitHub Actions (CI/CD) 및 템플릿 관련 파일
│   ├── workflows/                 # GitHub Actions 관련 파일
│   │   ├── CD.yml                 # DAG 코드에 대한 CD 자동화
│   │   └── ruff.yml               # Ruff Linting 자동화
│   └── pull_request_template.md   # Pull Request 템플릿
├── airflow_project/               # Airflow 관련 파일
│   ├── dags/                      # DAGs 정의 폴더
│   │   ├── config/                # DAGs config 폴더
│   │   │   └── region.json        # ASOS에 사용되는 지역별 정보 json
│   │   ├── ASOS.py                # 기상청 raw 데이터 적재 DAG
│   │   ├── ASOS_ETL.py            # 기상청 데이터 모델링 및 ETL DAG
│   │   ├── mise_EL.py             # 한국환경공단 대기오염정보 API 데이터 추출 및 변환과 검증
│   │   ├── mois_report_slack.py   # 행정안전부 안전관리일일상황 보고서 기상 정보 Slack 알림
│   │   └── wwarn_dag.py           # 기상청 기상 특보 현황, 이미지 데이터 ETL DAG
│   ├── config/                    # Airflow 설정 파일 (선택적)
│   └── plugins/                   # 커스텀 Airflow 플러그인 (선택적)
├── README.md                      # 현재 파일
├── install-setup.md               # 서버 설정 및 docker, airflow 설치 가이드
└── install_airflow.sh             # docker, airflow 설치 shell 코드
```
## 🛠️ 기술 스택 (Tech Stack)

### 워크플로우
![Airflow](https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=apache-airflow&logoColor=white)

### 인프라
![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazon-ec2&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

### 데이터 레이크하우스
![AWS S3](https://img.shields.io/badge/AWS_S3-569A31?style=for-the-badge&logo=amazon-s3&logoColor=white)
![Snowflake](https://img.shields.io/badge/Snowflake-2A9DF2?style=for-the-badge&logo=snowflake&logoColor=white)

### 프로그래밍 언어
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

### 커뮤니케이션
![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)

### 시각화
![Superset](https://img.shields.io/badge/Superset-4E4E63?style=for-the-badge&logo=apache-superset&logoColor=white)


## 🖼️ 데모 및 결과물 (Demo & Results)


### 대시보드
![Image](https://github.com/user-attachments/assets/866098a3-b095-4f16-b328-a09e3a673075)

### Slack 알림
![Image](https://github.com/user-attachments/assets/8055e8da-b365-47ba-8e5a-f6a8745ee0e9)

## ⚙️ 시작하기 (Getting Started)

[initial-setup.md](https://github.com/DE7-SamRa/samra-airflow/blob/main/initial-setup.md)를 참고하여 로컬에 설치
