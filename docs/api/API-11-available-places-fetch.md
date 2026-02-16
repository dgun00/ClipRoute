# [API 11] 장소 – 여행 지역(지도) 기반 장소 조회 API 지침서

---

## 1. API 목적 (Why)

- **장소 추가 UX 지원(편집 모드 연계)**  
  사용자가 코스 편집 화면에서 "장소 추가"를 눌렀을 때, 추가 후보 장소 리스트를 빠르게 조회할 수 있어야 한다.

- **지도 앱 표준 패턴(현재 화면 내 장소만 조회)**  
  사용자가 보고 있는 지도 화면(Viewport) 범위 내 장소만 조회하도록 지원한다. (Bounding Box 기반)

- **CQRS(Command / Query 분리)**  
  본 API는 장소 **탐색(Query)** 전용이며, 선택된 장소의 실제 추가/저장은 **API 10(내 코스 상세 편집 저장)**에서 최종 커밋한다.

---

## 2. API 역할 정의 (SRP)

### 책임
- 지도/검색 조건에 맞는 **장소 후보 리스트 조회**
- (선택) regionId 기반 1차 필터 + viewport 기반 2차 필터링
- Soft Delete 정합성 기준을 만족하는 Place만 노출
- Slice 기반 페이징으로 대량 데이터 효율 제공

### 비대상
- 코스에 장소를 실제로 추가하는 행위(CoursePlace 생성)
- 내 코스/코스 목록 필터 옵션 계산
- UI 메시지 생성 (프론트엔드에서 totalInViewport 기반 처리)

---

## 3. Endpoint

- **GET** `/api/v1/places/search`

---

## 4. Query String

### 4-1. 기본 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| regionId | Long | X | 지역 ID (초기 진입 / 성능 최적화용) |
| category | String / Enum | X | 장소 카테고리 (예: 관광명소, 맛집, 카페, 자연) |
| page | Integer | X | 페이지 번호 (default: 0) |
| size | Integer | X | 페이지 크기 (default: 20) |

### 4-2. 지도 Viewport(Bounding Box) 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---|---|---|---|
| minLat | Double | O | 화면 남쪽 위도  |
| maxLat | Double | O | 화면 북쪽 위도  |
| minLng | Double | O | 화면 서쪽 경도 |
| maxLng | Double | O | 화면 동쪽 경도  |

- 위도(Latitude): 90.0 <= lat <= 90.0
- 경도(Longitude): 180.0 <= lng <= 180

### 4-3. 파라미터 규칙

- Viewport 파라미터는 **4개 모두 전달되어야 유효**
- 일부만 전달된 경우 `BAD_REQUEST` (PLACE_INVALID_VIEWPORT)
- `regionId + viewport` 조합 사용 권장
- 최소 하나의 조건 필요: `regionId` 또는 `viewport` 또는 `category`

### 4-4. 대한민국 좌표 범위 검증

**유효 범위**:
- 위도(Latitude): 90.0 <= lat <= 90.0
- 경도(Longitude): 180.0 <= lng <= 180.0
- 
**검증 로직**:
```java
if (minLat < 90.0 || maxLat > 90.0 ||
    minLng < 180.0 || maxLng > 180.0) {
    throw new PlaceInvalidViewportRangeException();
}
```

---

## 5. 파라미터 우선순위 테이블

| 케이스 | regionId | viewport | category | 주요 시나리오 | 조회 조건 | 허용 |
|------|----------|----------|----------|--------------|----------|------|
| 1 | O | O | X | 지도 화면 내 전체 장소 | region + viewport | O |
| 2 | O | O | O | 카테고리 필터 검색 | region + viewport + category | O |
| 3 | O | X | O | 지역 + 카테고리 | region + category | O |
| 4 | O | X | X | 초기 검색(리스트 진입) | region | O |
| 5 | X | O | X | 지도 이동 후 검색 | viewport | O |
| 6 | X | X | X | 조건 없음 | - | X (400) |

---

## 6. API 호출 전략 (프론트엔드 기준)

### 6-1. 초기 로딩 전략 (3단계 Fallback)

1. Geolocation API로 현재 위치 획득
2. 실패 시 사용자 최근 선택 regionId 중심
3. 최종 fallback: 서울 중심 좌표 (37.5665, 126.9780)

---

## 7. 동작 흐름

1. 요청 파라미터 검증
2. Soft Delete 필터 적용
3. QueryDSL 동적 쿼리 생성
4. Slice 페이징 처리
5. DTO 변환 후 반환

---

## 8. Response 규격

### 8-1. 전체 구조

```json
{
  "isSuccess": true,
  "code": "PLACE200_1",
  "message": "장소 조회에 성공했습니다.",
  "result": {
    "places": [],
    "viewport": {},
    "sliceInfo": {},
    "totalInViewport": 150
  }
}
```

### 8-2. places 배열

| 필드 | 타입 | 설명 |
|---|---|---|
| placeId | Long | 장소 ID |
| regionId | Long | 지역 ID |
| placeName | String | 장소명 |
| category | String | 장소 카테고리 |
| address | String | 주소 |
| lat | Double | 위도 |
| lng | Double | 경도 |

### 8-3. sliceInfo 객체

| 필드 | 타입 | 설명 |
|---|---|---|
| currentPage | Integer | 현재 페이지 번호 (0부터 시작) |
| size | Integer | 페이지 크기 |
| hasNext | Boolean | 다음 페이지 존재 여부 |

### 8-4. viewport 객체(Echo)

| 필드 | 타입 | 설명 |
|---|---|---|
| minLat | Double | 요청한 남쪽 위도 |
| maxLat | Double | 요청한 북쪽 위도 |
| minLng | Double | 요청한 서쪽 경도 |
| maxLng | Double | 요청한 동쪽 경도 |

### 8-5. totalInViewport

- **첫 조회(page=0)일 때만 계산**해서 내려줌
- page > 0인 경우 `null`

---

## 9. 페이징 & 무한 스크롤

- viewport 또는 category 변경 시 page=0 초기화
- page 증가 시 기존 마커 유지 + 추가 표시

---

## 10. 데이터 범위 / 정합성 기준

- Place.deletedAt IS NULL
- lat, lng NULL 데이터 제외

---

## 11. 아키텍처 규칙

- Controller: PlaceQueryController
- Service: PlaceQueryService
- Repository: QueryDSL 기반 Custom Repository
- DTO: record + @Builder

---

## 12. 예외 처리

| 상황 | 에러 코드 | HTTP |
|---|---|---|
| viewport 누락 | PLACE_INVALID_VIEWPORT | 400 |
| 좌표 범위 오류 | PLACE_INVALID_VIEWPORT_RANGE | 400 |
| 서비스 범위 외 | PLACE_OUT_OF_SERVICE_AREA | 400 |
| page 음수 | PLACE_INVALID_PAGE | 400 |
| category 오류 | PLACE_INVALID_CATEGORY | 400 |
| 조건 없음 | PLACE_NO_SEARCH_CONDITION | 400 |

---

## 13. SOLID & Convention

- CQRS 준수
- SRP 준수
- DTO 직접 노출 금지
- Global ApiResponse 사용

---

## 14. 테스트 체크리스트

- viewport 조합 조회
- category 필터링
- 페이징 / 무한 스크롤
- 좌표 범위 검증
- 성능 테스트

---

## 15. 요약

> **API 11은 지도 Viewport, regionId, category 조건을 조합하여 Soft Delete 정합성을 만족하는 장소 후보 리스트를 Slice 방식으로 조회하는 Query 전용 API이다.**
