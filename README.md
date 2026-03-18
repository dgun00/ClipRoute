# CLIPROUTE

유튜브 여행 브이로그를 실제 여행 코스로 바꿔 주는 국내 여행 추천 서비스입니다.  
사용자는 지역과 여행 기간만 선택하면 인기 여행 유튜버의 동선을 기반으로 코스를 추천받고, 지도로 확인하고, 내 일정으로 스크랩해 다시 편집할 수 있습니다.

포트폴리오 관점에서는 "비정형 콘텐츠를 구조화된 여행 데이터로 전환하고, 추천과 편집 경험까지 연결한 서비스"라는 점이 가장 큰 특징입니다.

## Overview

- 여행 정보가 유튜브 영상, 자막, 댓글처럼 흩어져 있어 실제 일정으로 옮기기 어렵다는 문제를 해결하려고 했습니다.
- CLIPROUTE는 영상 속 여행 동선을 코스 데이터로 정리해 추천하고, 사용자가 내 여행 일정으로 저장해 직접 수정할 수 있게 만들었습니다.
- 일반 사용자용 여행 앱, Spring Boot API 서버, Streamlit 관리자 페이지, AI 기반 데이터 정제 파이프라인으로 구성되어 있습니다.

## Key Features

### 1. 조건 기반 여행 코스 추천

- 지역과 여행 기간을 선택하면 조건에 맞는 여행 코스를 추천합니다.
- 조건에 정확히 맞는 코스가 부족할 때는 유사한 여행 코스를 함께 제안합니다.
- 대표 지역과 인기 영상 기반 코스를 홈 화면에서 탐색할 수 있습니다.

### 2. 지도 중심 코스 상세 탐색

- 코스 상세 화면에서 여행 동선을 지도 위에 표시합니다.
- Day 단위 일정과 방문 순서를 함께 보여줘 실제 이동 흐름을 이해하기 쉽습니다.
- 장소 정보와 영상 기반 코스를 함께 연결해 탐색 경험을 강화했습니다.

### 3. 내 코스 스크랩 및 편집

- 마음에 드는 코스를 내 일정으로 스크랩할 수 있습니다.
- 스크랩한 코스는 날짜 수정, 제목 수정, 장소 추가/삭제 등 후편집이 가능합니다.
- 내 코스 목록은 필터링과 무한 스크롤 기반으로 관리할 수 있습니다.

### 4. 관리자 데이터 운영 환경

- Streamlit 기반 관리자 페이지에서 코스, 장소, 이미지, 지역, 멤버 데이터를 관리할 수 있습니다.
- 전처리된 CSV를 업로드해 여행 코스 데이터를 빠르게 적재할 수 있습니다.
- 유튜브 썸네일을 S3로 업로드해 이미지 자산 관리 흐름도 함께 구성했습니다.

### 5. AI 기반 여행 데이터 정제 파이프라인

- 유튜브 검색 결과에서 여행 영상을 수집합니다.
- 자막, 설명, 댓글을 모아 여행 맥락 데이터를 구성합니다.
- LLM으로 일정 후보를 복원하고, Naver Local API로 장소를 검증합니다.
- 최종적으로 Day, 방문 순서, 좌표가 포함된 코스 데이터로 정리합니다.

## User Flow

1. 사용자가 지역과 날짜를 선택합니다.
2. 추천 API가 조건에 맞는 여행 코스를 조회합니다.
3. 사용자는 코스 상세 화면에서 지도와 동선을 확인합니다.
4. 원하는 코스를 스크랩해 내 일정으로 저장합니다.
5. 저장한 코스에서 날짜와 장소를 편집해 실제 여행 계획으로 다듬습니다.

## Tech Stack

### Frontend

- React 19
- TypeScript
- Vite
- Tailwind CSS
- TanStack Query
- React Router
- Google Maps / Kakao Maps 연동

### Backend

- Java 17
- Spring Boot 3
- Spring Web
- Spring Data JPA
- Spring Security
- QueryDSL
- MySQL
- JWT Authentication
- Swagger

### Admin / Data

- Python
- Streamlit
- yt-dlp
- Gemini API 연동
- Naver Local API
- AWS S3

## Architecture

### Frontend App

- 홈 화면에서 지역/일정 입력 후 추천 코스를 탐색합니다.
- 코스 상세와 내 코스 상세에서 지도 기반 사용자 경험을 제공합니다.
- React Query를 사용해 목록 조회, 상세 조회, 스크랩/수정 흐름을 관리합니다.

### Backend API

- `GET /api/v1/courses`: 대표 코스 및 공개 코스 목록 조회
- `GET /api/v1/courses/recommendation`: 조건 기반 추천 코스 조회
- `GET /api/v1/courses/{courseId}`: 코스 상세 조회
- `POST /api/v1/courses/{courseId}/scrap`: 코스 스크랩
- `GET /api/v1/members/me/courses`: 내 코스 목록 조회
- `PATCH /api/v1/members/me/courses/{courseId}`: 내 코스 수정
- `DELETE /api/v1/members/me/courses/{courseId}`: 내 코스 삭제
- `GET/PATCH /api/v1/members/me`: 마이페이지 조회 및 수정
- `POST /api/auth/signup`, `POST /api/auth/login`: 인증 처리

### AI Pipeline

- Step 0: 유튜브 여행 영상 수집 및 점수화
- Step 1: 자막, 설명, 댓글 수집 및 정제
- Step 2: LLM 기반 일정 복원
- Step 3: Naver API 기반 장소 검증
- Step 4: 방문 순서 및 좌표 정렬

## Project Structure

```text
CLIPROUTE/
├─ frontend/            # 사용자용 여행 앱
├─ backend/backend/     # Spring Boot API 서버
├─ admin_page/          # Streamlit 관리자 페이지
├─ AI_logic/            # 여행 데이터 정제 및 추천용 파이프라인
├─ Logic/               # API/서비스 로직 문서
├─ docs/                # 이미지, 스웨거 정적 문서 등
└─ swagger.html         # API 문서 진입 파일
```

## What Makes This Project Strong

- 비정형 유튜브 콘텐츠를 실제 여행 코스로 구조화했다는 점
- 추천, 지도 시각화, 스크랩, 후편집까지 사용자 흐름이 완결되어 있다는 점
- 서비스 화면뿐 아니라 관리자 운영 도구와 데이터 적재 파이프라인까지 함께 설계했다는 점
- LLM과 외부 장소 검증 API를 결합해 데이터 품질을 높이려 했다는 점

## Local Setup

### 1. Frontend

```bash
cd frontend
npm install
npm run dev
```

기본적으로 Vite 개발 서버에서 실행됩니다.

### 2. Backend

```bash
cd backend/backend
export DB_URL=jdbc:mysql://localhost:3306/cliproute
export DB_USERNAME=YOUR_DB_USERNAME
export DB_PASSWORD=YOUR_DB_PASSWORD
export JWT_SECRET=YOUR_JWT_SECRET
./gradlew bootRun
```

Spring Boot 기본 포트는 `8080`입니다.

### 3. Admin Page

```bash
cd admin_page
pip install -r requirements.txt
streamlit run app.py
```

기본적으로 `http://localhost:8501`에서 확인할 수 있습니다.

## Notes

- `backend/backend/src/main/resources/application.yml` 기준으로 DB와 JWT 값은 환경변수로 주입됩니다.
- 관리자 페이지의 CSV 업로드 기능은 S3 및 DB 설정이 필요합니다.
- AI 파이프라인은 외부 API와 크롤링/수집 환경 설정이 선행되어야 합니다.

## Portfolio Summary

CLIPROUTE는 단순한 여행 정보 조회 앱이 아니라, 콘텐츠 수집부터 데이터 정제, 추천, 사용자 편집, 관리자 운영까지 하나의 서비스 사이클을 담은 프로젝트입니다.  
포트폴리오에서는 "사용자 경험을 만드는 프론트엔드", "추천과 데이터 처리를 담당하는 백엔드", "운영을 위한 관리자 도구", "비정형 데이터를 다루는 AI 파이프라인"이 함께 맞물린 프로젝트로 소개하기 좋습니다.
