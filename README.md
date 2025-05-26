# 🌍 RestCountries API to Redshift ETL with Apache Airflow

## 📝 프로젝트 개요

- [restcountries.com](https://restcountries.com/v3/all) API를 호출하여 전 세계 국가들의 정보를 수집합니다.
- 수집된 데이터에서 `공식 국가명`, `인구수`, `면적` 정보를 추출합니다.
- 추출한 데이터를 **Redshift**의 `ryanp3.country_info` 테이블에 Full Refresh 방식으로 저장합니다.
- 이 과정은 **Apache Airflow DAG**으로 작성되어 **매주 토요일 오전 6시 30분 (UTC)** 에 자동 실행됩니다.

---

## 🛠️ 사용 기술 스택

- **Apache Airflow**
- **Amazon Redshift**
- **Python Requests**
- **PostgresHook** (`airflow.providers.postgres`)
- **REST API**: https://restcountries.com/v3/all

---

## 🗂️ DAG 구성

### DAG ID : country_info_to_redshift

### 태스크 구성

1. `fetch_country_data`  
   - REST API 호출
   - JSON 응답 파싱 및 필요한 필드 추출

2. `load_to_redshift`  
   - Redshift 연결
   - `ryanp3.country_info` 테이블 생성 (없을 시)
   - 기존 데이터 삭제 후 새로 삽입 (Full Replace)

---

## 📊 Redshift 테이블 구조

| 컬럼명      | 타입        | 설명              |
|-------------|-------------|-------------------|
| `name`      | VARCHAR     | 국가명 (공식명칭) |
| `population`| BIGINT      | 인구 수           |
| `area`      | FLOAT       | 면적 (제곱킬로미터) |

---

## 🧪 DAG 테스트 방법

```bash
# 특정 날짜로 DAG 테스트 실행
airflow dags test country_info_to_redshift 2025-05-26

![스크린샷 2025-05-26 175445](https://github.com/user-attachments/assets/d69240fc-b96f-4999-a910-73af98a0b664)





