# Clirpoute Admin Page

Streamlit 기반의 관리자 페이지입니다. DB 조회/관리와 CSV 업로드(특히 전처리 CSV)를 통해 코스/장소 데이터를 빠르게 적재하는 데 목적이 있습니다.

**핵심 기능**
- 관리자 로그인
- 엔티티 조회/추가/수정/삭제 (regions, places, courses 등)
- 전처리 CSV 업로드로 `courses`, `places`, `course_place` 일괄 저장
- 엔티티별 CSV 업로드

**동작 환경**
- Windows + Python 3.10
- DB: MySQL/MariaDB

## 실행 방법

1. 가상환경 생성/활성화
```bash
python -m venv venv
.\venv\Scripts\activate
```

2. 패키지 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
```bash
copy .env.example .env
```
`.env`에 DB 정보를 입력합니다.

```
DB_HOST=...
DB_PORT=3306
DB_NAME=...
DB_USERNAME=...
DB_PASSWORD=...
```

4. 실행
```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 전처리 CSV 업로드

`CSV 업로드` 페이지에서 `전처리 CSV(코스/장소 일괄)`을 선택하면
CSV 하나로 아래 엔티티를 자동 생성/매핑합니다.

- `places`
- `courses`
- `course_place`

### 샘플 CSV
- 파일명: `Clip Route - 강릉.csv`
- 위치: `utils/Clip Route - 강릉.csv`

### 전처리 CSV 필수 컬럼
다음 컬럼이 있어야 정상 파싱됩니다.

- `코스 제목 (유튜브 명)`
- `일수 분류`
- `일차`
- `전체 순서`
- `장소명`
- `주소`
- `카테고리`
- `조회수`
- `유튜브 링크`

CSV의 헤더가 `Unnamed: 0 ...` 형태로 들어오는 경우에도
첫 유효 헤더 행을 자동 감지하여 정규화합니다.

### 위도/경도 처리
`places.lat/lng`는 NOT NULL입니다.

- CSV에 `위도`, `경도` 컬럼이 있으면 해당 값을 사용합니다.
- 없으면 업로드 화면에서 **기본 위도/경도**를 입력해야 합니다.

## 현재 제한 사항

전처리 CSV 업로드는 아래 엔티티를 **생성하지 않습니다**.

- `videos`
- `images`
- `videos_place`

현재 로직은 `courses.source_video_id`를 기존 `videos` 테이블에서 **조회해 연결**만 합니다.

## 프로젝트 구조
```
Clirpoute_admin_page/
  app.py
  pages/
    4_CSV_업로드.py
    ...
  utils/
    csv_import.py
    db.py
    entities.py
  requirements.txt
```

## 다음 단계 제안
- 전처리 CSV에 `videos/images/videos_place` 필수 컬럼 추가 후 자동 적재 로직 확장
- 이미지 업로드 및 S3 연동 추가
