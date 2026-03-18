
# 폴더 구조 및 사용 규칙
backend/   - 백엔드 서버 소스 코드 (API, DB 연동, 인증, 비즈니스 로직)

frontend/  - 프론트엔드 소스 코드 (화면, 라우팅, API 호출)

Logic/     - 서비스 로직 문서, 로직 검토 및 API 흐름 정리

docs/      - ERD, API 명세서, 회의록 등 문서 자료

infra/     - 인프라 관련 문서 (AWS, DB 세팅 메모, 배포 가이드)

# 커밋 메세지 규칙
CHORE: 코드 수정, 내부 파일 수정

FEAT: 추가 기능 추가

FIX: 버그, 오류 수정

DOCS: README 등의 문서 수정

REFACTOR: 전면수정(코드 리펙토링)

TEST: 테스트 코드 추가 및 수정

Clip Route Logic Architecture

본 프로젝트는 비정형 여행 데이터를 정제하고, 지능형 분석을 통해 유의미한 정보를 추출하는 3단계 아키텍처로 구성되어 있습니다.

1. Data Pipeline Layer (pipeline/)
    Normalization: 결측치를 보정하고(ffill), 영상 제목과 코스명을 동기화하여 데이터 무결성을 확보합니다.
    Validation: 누적 방문 순서(visit_order)의 연속성을 검증하여 경로 데이터의 논리적 오류를 제거합니다.
    Extraction: 비즈니스 로직(맛집/카페 필터링)에 따라 핵심 데이터를 선별합니다.

2. Intelligent Layer (llm/)
    Data Enrichment: LLM을 활용하여 단순 장소 정보에 지능형 설명을 추가하거나 데이터 품질을 높입니다.
    Verification: 좌표 오차나 주소 불일치 등 정형 로직으로 잡기 어려운 오류를 검토합니다.

3. Output Layer
    사용자의 필요에 따라 CSV(데이터용)와 Excel(보고용)형태의 다중 포맷 결과물을 생성합니다.

