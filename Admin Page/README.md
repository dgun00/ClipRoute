# ClipRoute Admin Page

Streamlit 기반 관리자 페이지입니다. DB 엔티티 조회/관리와 전처리 CSV 업로드를 통해
코스/장소/이미지 등 데이터를 빠르게 적재·관리할 수 있습니다.

**주요 기능**

- 관리자 로그인
- 엔티티 조회/추가/수정/삭제
    - 코스/멤버/지역/이미지/장소 등 관리 페이지 제공
    - 일부 엔티티는 삭제 탭 대신 수정 탭 내 삭제 버튼 제공
- 전처리 CSV 업로드
    - `videos`, `images`, `courses`, `places`, `course_place` 자동 적재
    - YouTube 썸네일을 S3으로 스트리밍 업로드

**현재 동작 요약**

- 대시보드 통계: DB 실데이터 기반(코스/멤버 등)
- 최근 활동: 미구현
- CSV 업로드
    - 업로드 완료/실패 팝업 제공
    - 업로드 중 버튼 비활성화 및 안내 문구 표시

---

## 실행 환경

- Windows + Python 3.10
- DB: MySQL/MariaDB

## 설치 및 실행

1. 가상환경 생성/활성화

```bash
python -m venv venv
.\venv\Scripts\activate
```

2. 패키지 설치

```bash
pip install -r requirements.txt
```

3. 환경변수 설정

```bash
copy .env.example .env
```

`.env`에 아래 값을 설정합니다.

```
DB_HOST=...
DB_PORT=3306
DB_NAME=...
DB_USERNAME=...
DB_PASSWORD=...

AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=ap-northeast-2
S3_BUCKET=cliproute-images
```

4. 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## 전처리 CSV 업로드

`pages/4_CSV_업로드.py`에서 전처리 CSV 업로드를 수행합니다.

**필수 컬럼**

- `video_title`
- `channel_name`
- `course_title`
- `travel_day`
- `visit_day`
- `visit_order`
- `place_name`
- `address`
- `place_category`
- `yt_video_id`
- `original_name`
- `region_id`
- `lat`
- `lng`

**이미지 업로드 흐름**

- YouTube 썸네일 URL 생성
    - `https://img.youtube.com/vi/{yt_video_id}/maxresdefault.jpg`
    - 실패 시 `sddefault.jpg` → `hqdefault.jpg` 순으로 fallback
- S3 업로드 키: `images/courses/{yt_video_id}.jpg`
- `images.image_url`에 S3 URL 저장

---

## 프로젝트 구조

```
Admin Page/
  app.py
  pages/
    4_CSV_업로드.py
    5_코스_관리.py
    6_멤버_관리.py
    7_지역_관리.py
    8_이미지_관리.py
    9_장소_관리.py
  utils/
    admin_ui.py
    csv_import.py
    db.py
    entities.py
  requirements.txt
```

---

## 참고

- 최근 활동 로그는 미구현입니다.
- CSV 업로드는 S3 연동 설정이 되어 있어야 이미지 업로드가 가능합니다.