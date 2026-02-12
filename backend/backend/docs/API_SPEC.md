# API Specification

## 개요
- Base URL: `/api/v1`
- 인증: `X-MEMBER-ID` 헤더(타입: `Long`). 코드 기준으로 일부 엔드포인트는 옵션이지만, 미인증 시 `401`이 반환될 수 있습니다.
- 응답 포맷: 모든 API는 `ApiResponse<T>` 래퍼를 사용합니다.
  - `isSuccess` (Boolean)
  - `code` (String)
  - `message` (String)
  - `result` (T)
- 날짜/시간 형식
  - `LocalDate`: `YYYY-MM-DD`
  - `LocalDateTime`: ISO-8601 (`YYYY-MM-DDTHH:MM:SS`)
- 공통 enum
  - `TravelStatus`: `BEFORE`, `AFTER`, `NONE`

---

## Region

### GET `/api/v1/regions`
**기능**: 지역(장소) 선택용 간단 리스트 조회

**Request Parameters/Body**
- 없음

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "REGION200_1",
  "message": "지역 목록 조회에 성공했습니다.",
  "result": {
    "regions": [
      {
        "regionId": 1,
        "regionName": "Seoul",
        "imageUrl": "https://..."
      }
    ]
  }
}
```

**필드 설명**
- `regions`: 지역 목록
- `regionId`: 지역 ID
- `regionName`: 지역명
- `imageUrl`: 대표 이미지 URL

**Error Codes**
- 404 `REGION404_1` 지역 정보를 찾을 수 없음
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

## Course

### GET `/api/v1/courses`
**기능**: 코스 리스트 조회 (필터/정렬/무한스크롤)

**Request Parameters**

| 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|
| regionId | Long | N | 지역 ID 필터 |
| travelDays | Integer | N | 여행 일수 필터 |
| sort | String | N | 정렬 기준 (default: `latest`) |
| lastCourseId | Long | N | 무한스크롤 커서: 마지막 코스 ID |
| lastValue | Integer | N | 무한스크롤 커서: 마지막 정렬 값 |
| pageSize | Integer | N | 페이지 크기 (default: 5) |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "COURSE200_1",
  "message": "코스 목록 조회에 성공했습니다.",
  "result": {
    "courseList": [
      {
        "courseId": 10,
        "thumbnailUrl": "https://...",
        "channelName": "Channel",
        "videoTitle": "Video",
        "travelDays": 3,
        "regionId": 1,
        "regionName": "Seoul",
        "isRecommended": false
      }
    ],
    "totalElements": 100,
    "sort": "latest",
    "sliceInfo": {
      "currentPage": 0,
      "size": 5,
      "hasNext": true
    }
  }
}
```

**필드 설명**
- `courseList`: 코스 목록
- `totalElements`: 전체 개수(첫 페이지일 때만 반환될 수 있음)
- `sliceInfo`: 무한스크롤 정보

**Error Codes**
- 404 `COURSE404_1` 코스를 찾을 수 없음
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

### GET `/api/v1/courses/recommendation`
**기능**: 필터 조건 + 추천 코스 리스트 조회

**Request Parameters**

| 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|
| regionId | Long | Y | 지역 ID |
| travelDays | Integer | Y | 여행 일수 |
| sort | String | N | 정렬 기준 (default: `latest`) |
| page | Integer | N | 페이지 번호 (default: 0) |
| pageSize | Integer | N | 페이지 크기 (default: 5) |

**Response Body**
- `CoursePublicListDTO`와 동일

**Error Codes**
- 404 `COURSE404_1` 코스를 찾을 수 없음
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

### GET `/api/v1/courses/{courseId}`
**기능**: 코스 상세 조회

**Request Parameters**

| 위치 | 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|---|
| Path | courseId | Long | Y | 코스 ID |
| Header | X-MEMBER-ID | Long | N | 로그인 사용자 ID |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "COURSE200_3",
  "message": "코스 상세 조회에 성공했습니다.",
  "result": {
    "courseId": 10,
    "videoTitle": "Video",
    "videoUrl": "https://www.youtube.com/watch?v=...",
    "thumbnailUrl": "https://...",
    "channelName": "Channel",
    "regionId": 1,
    "regionName": "Seoul",
    "isScrapped": true,
    "travelStatus": "BEFORE",
    "itineraries": [
      {
        "visitDay": 1,
        "places": [
          {
            "coursePlaceId": 100,
            "visitOrder": 1,
            "placeId": 999,
            "placeName": "Place",
            "placeCategory": "Category",
            "address": "Address",
            "lat": 37.0,
            "lng": 127.0,
            "timestamp": 120,
            "deletedAt": null
          }
        ]
      }
    ]
  }
}
```

**Error Codes**
- 400 `MEMBER400_?` (Auth 도메인에서 생성 예정)
- 404 `COURSE404_1` 코스를 찾을 수 없음
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

### POST `/api/v1/courses/{courseId}/scrap`
**기능**: 코스 스크랩(또는 스크랩 취소)

**Request Parameters**
| 위치 | 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|---|
| Path | courseId | Long | Y | 코스 ID |
| Header | X-MEMBER-ID | Long | N | 로그인 사용자 ID |

**Request Body**
| 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|
| startDate | LocalDate | N | 여행 시작일 |
| endDate | LocalDate | N | 여행 종료일 |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "COURSE201_1",
  "message": "코스 스크랩에 성공했습니다.",
  "result": {
    "newCourseId": 20,
    "originalCourseId": 10,
    "isScrapped": true,
    "travelStatus": "BEFORE",
    "startDate": "2026-02-01",
    "endtDate": "2026-02-03",
    "createdAt": "2026-02-06T12:00:00"
  }
}
```

**Error Codes**
- 401 `MEMBER401_1` Unauthorized
- 404 `COURSE404_1` 코스를 찾을 수 없음
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

## MyCourse (Member)

### GET `/api/v1/members/me/courses/filters`
**기능**: 내 코스 필터 옵션 조회

**Request Parameters**

| 위치 | 필드명 | 타입 | 필수 | 설명 | 
| :--- | :--- | :--- | :---: | :--- |
| Header | X-MEMBER-ID | Long | Y | 로그인 사용자 ID |
| Query | regionId | Long | N | 지역 필터 |
| Query | travelDays | Integer | N | 여행 일수 필터 |
| Query | travelStatus | TravelStatus | N | 여행 상태 필터 (`BEFORE`/`AFTER`/`NONE`) |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "MYCOURSE200_1",
  "message": "My course filter options fetched successfully.",
  "result": {
    "regions": [
      { "id": 1, "name": "Seoul" }
    ],
    "travelDays": [1, 2, 3],
    "travelStatuses": ["BEFORE", "AFTER", "NONE"]
  }
}
```

**Error Codes**
- 401 `AUTH401_1` Unauthorized
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

### GET `/api/v1/members/me/courses`
**기능**: 내 코스 리스트 조회 (필터/무한스크롤)

**Request Parameters**

| 위치 | 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|---|
| Header | X-MEMBER-ID | Long | Y | 로그인 사용자 ID |
| Query | regionId | Long | N | 지역 필터 |
| Query | travelDays | Integer | N | 여행 일수 필터 |
| Query | travelStatus | TravelStatus | N | 여행 상태 필터 |
| Query | lastMemberCourseId | Long | N | 무한스크롤 커서: 마지막 내 코스 ID |
| Query | pageSize | Integer | N | 페이지 크기 (default: 5) |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "MYCOURSE200_2",
  "message": "My course list fetched successfully.",
  "result": {
    "courseList": [
      {
        "courseId": 10,
        "memberCourseId": 100,
        "courseTitle": "Title",
        "regionName": "Seoul",
        "regionRepImageUrl": "https://...",
        "thumbnailUrl": "https://...",
        "startDate": "2026-02-01",
        "endDate": "2026-02-03",
        "travelDays": 3,
        "travelStatus": "BEFORE",
        "placeCount": 5,
        "createdAt": "2026-02-06T12:00:00",
        "updatedAt": "2026-02-06T12:00:00"
      }
    ],
    "sort": "latest",
    "sliceInfo": {
      "currentPage": 0,
      "size": 5,
      "hasNext": true
    }
  }
}
```

**Error Codes**
- 401 `AUTH401_1` Unauthorized
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

### GET `/api/v1/members/me/courses/{courseId}`
**기능**: 내 코스 상세 조회

**Request Parameters**

| 위치 | 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|---|
| Header | X-MEMBER-ID | Long | Y | 로그인 사용자 ID |
| Path | courseId | Long | Y | 코스 ID |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "COURSE200_3",
  "message": "코스 상세 조회에 성공했습니다.",
  "result": {
    "courseId": 10,
    "videoTitle": "Video",
    "videoUrl": "https://www.youtube.com/watch?v=...",
    "thumbnailUrl": "https://...",
    "channelName": "Channel",
    "regionId": 1,
    "regionName": "Seoul",
    "isScrapped": true,
    "travelStatus": "BEFORE",
    "courseTitle": "Title",
    "startDate": "2026-02-01",
    "endDate": "2026-02-03",
    "itineraries": [
      {
        "visitDay": 1,
        "places": [
          {
            "visitOrder": 1,
            "coursePlaceId": 100,
            "placeId": 999,
            "placeName": "Place",
            "placeCategory": "Category",
            "address": "Address",
            "lat": 37.0,
            "lng": 127.0,
            "timestamp": 120,
            "deletedAt": null
          }
        ]
      }
    ]
  }
}
```

**Error Codes**
- 401 `AUTH401_1` Unauthorized
- 403 `AUTH403_1` Forbidden
- 404 `MEMBER_COURSE404_1` My course not found
- 500 `INTERNAL_SERVER_ERROR` 서버 오류

---

### DELETE `/api/v1/members/me/courses/{courseId}`
**기능**: 내 코스 삭제(Soft delete)

**Request Parameters**

| 위치 | 필드명 | 타입 | 필수 | 설명 |
|---|---|---|---|---|
| Header | X-MEMBER-ID | Long | Y | 로그인 사용자 ID |
| Path | courseId | Long | Y | 코스 ID |

**Response Body (성공 예시)**
```json
{
  "isSuccess": true,
  "code": "MYCOURSE200_4",
  "message": "My course deleted successfully.",
  "result": {
    "courseId": 10,
    "deletedAt": "2026-02-06T12:00:00"
  }
}
```

**Error Codes**
- 400 `MEMBER_COURSE400_1` Invalid course id
- 401 `MEMBER401_1` Unauthorized
- 404 `MEMBER_COURSE404_1` My course not found
- 500 `INTERNAL_SERVER_ERROR` 서버 오류
