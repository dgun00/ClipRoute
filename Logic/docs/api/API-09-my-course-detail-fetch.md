# API 9 – 내 코스 상세 조회

## 1. API 목적 (Why)

### 내 코스 상세 화면 구성 데이터 제공

사용자가 스크랩/편집해 보유한 **“내 코스” 단건**에 대해, 화면 구성에 필요한 **마스터 정보 + 일차별 장소 리스트**를 한 번에 반환한다.

### 일정 구조화(그룹/정렬) 보장

* `visitDay` 기준으로 **그룹화**
* 각 일차 내 장소는 `visitOrder` 기준으로 **정렬**

클라이언트가 추가 가공 없이 그대로 렌더링할 수 있도록 구조를 보장한다.

### Soft Delete 정합성 유지 (보기 모드)

내 코스에 포함된 장소가 삭제(Soft Delete)된 경우에도 **응답에 포함**하되, `deletedAt` 값을 함께 내려 클라이언트가 “삭제됨” 상태를 인지/표시할 수 있게 한다.

---

## 2. API 역할 정의 (SRP)

### 책임

* 특정 `courseId`에 대한 **“내 코스” 상세** (마스터 정보 + itinerary) 반환
* `visitDay` 그룹화 / `visitOrder` 정렬 규칙 보장
* 삭제된 장소도 포함하여 반환 (`deletedAt`으로 상태 노출)

### 비대상

* 드롭다운 옵션 계산 → **API 6**의 책임
* 내 코스 목록 페이징 조회 → **API 7**의 책임
* 편집(수정/재정렬/삭제) → 별도 **Command API** 책임

---

## 3. Endpoint

```
GET /api/v1/members/me/courses/{courseId}
```

---

## 4. Path Variable

| 파라미터     | 타입   | 설명                    |
| -------- | ---- | --------------------- |
| courseId | Long | 내 코스 ID (`Course.id`) |

---

## 5. 동작 흐름

### 1) 인증 확인

* 헤더 `X-MEMBER-ID`로 사용자 식별
* 누락/비정상 값이면 즉시 예외

### 2) 소유권(내 코스 여부) 검증

* 7번 **“내 코스 기준 데이터 범위”** 조건으로 `MemberCourse` 존재 여부 확인
* 불일치 시 타인의 코스 접근이므로 예외 처리

### 3) 코스 마스터 조회

* `Course.deletedAt IS NULL`
* `Course.isCustomized = true`
* 지역 / 영상 / 썸네일 등 화면에 필요한 마스터 정보 함께 조회

### 4) 장소(일정) Flat 조회

* 코스에 포함된 `CoursePlace`를 `visitDay`, `visitOrder` 기준으로 정렬 조회
* **삭제된 장소도 포함** (`CoursePlace.deletedAt` 필터링 금지)
* 조회 결과를 **Flat 리스트**로 수신

### 5) DTO 변환 및 응답

* Converter에서 Flat → `visitDay` 그룹화 → `visitOrder` 정렬된 DTO 생성
* `ApiResponse.onSuccess(...)` 규격 유지

---

## 6. Response 규격

### result 객체 내 포함 필드 (권장)

#### courseInfo (코스 마스터)

* `courseId`
* `videoTitle`
* `videoUrl`
* `thumbnailUrl`
* `channelName`
* `regionId`
* `regionName`
* `isScrapped`
* `travelStatus`
* `courseTitle`
* `startDate`
* `endDate`

#### itineraries (일차별 장소 리스트)

```
[
  { visitDay, places[] }
]
```

##### places[] 내부 (권장)

* `visitOrder`
* `coursePlaceId`
* `placeId`
* `placeName`
* `category`
* `address`
* `lat`
* `lng`
* `timestamp`
* `deletedAt` ✅ (Soft Delete 반영)

### 규칙

* `itineraries`는 반드시 **visitDay ASC**
* 각 `places`는 반드시 **visitOrder ASC**
* 삭제된 장소도 포함 반환하되 `deletedAt` 값으로 상태 명시
* 일정/장소가 없는 경우도 **에러가 아닌 빈 배열 [] 반환**

    * 단, 코스 자체가 없거나 권한이 없으면 예외

---

## 7. “내 코스” 기준 데이터 범위 (API 6 / 7 동일)

API 9은 단건 조회이지만, **내 코스 범위 필터 기준은 API 6/7과 완전히 동일**해야 한다.

* `MemberCourse.memberId = :memberId`
* `MemberCourse.deletedAt IS NULL`
* `MemberCourse.isScrapped = true`
* `Course.deletedAt IS NULL`
* `Course.isCustomized = true`

> Note: 이미 위 조건을 만족하는 공용 `QueryDSL` 메서드 / `BooleanExpression`이 있다면 반드시 재사용할 것

---

## 8. 아키텍처 규칙 (CQRS / 패키지 분리)

### CQRS 원칙

* API 9은 **Query(Read) 전용**
* Command(편집/삭제/재정렬)는 별도 API로 분리

### 구조

```
Controller (Query)
 → QueryService
   → Repository (QueryDSL)
     → DB
```

* Converter: **DTO 변환만 담당** (비즈니스 판단 금지)
* Service: 권한/정합성 검증 + 유스케이스 오케스트레이션 담당 (QueryDSL 작성 금지)

### DTO 컨벤션

* `record + @Builder` 형태 준수
* 응답 DTO 네이밍: `MemberResDTO.MyCourseDetailDTO` 처럼 계층화

---

## 9. QueryDSL 구현 가이드 (조인 전략 / Fetch Join)

### 핵심 전략: **Flat 조회 + Converter 그룹화**

* 일정/장소는 1:N 구조 → 엔티티 그래프 fetchJoin 시 row 중복/비대해짐
* 단건 상세라도 **Projection(Flat DTO)** 조회 후 Converter 그룹화 권장

### 권장 쿼리 분리

#### 1) 소유권 검증 쿼리

* `MemberCourse`에서 다음 조건 확인

    * `memberId`
    * `courseId`
    * `deletedAt IS NULL`
    * `isScrapped = true`

#### 2) 코스 마스터 + 일정 Flat 조회

* 기준: `Course`
* 조인

    * `join course.region` (fetchJoin 가능)
    * `join course.video / sourceVideo` (fetchJoin 가능)
    * `leftJoin course.coursePlaces`
    * `leftJoin coursePlace.place`
* where

    * `course.id = :courseId`
    * `course.deletedAt IS NULL`
    * `course.isCustomized = true`
* ⚠️ `coursePlace.deletedAt` 조건은 **걸지 않는다** (삭제 포함 목적)
* orderBy

    * `coursePlace.visitDay.asc()`
    * `coursePlace.visitOrder.asc()`

### N+1 방지

* `region`, `video` 등 1:1 / ManyToOne 관계는 fetchJoin
* 장소/일정은 Flat projection으로 방지

---

## 10. 비즈니스 예외 처리 (도메인 예외)

| 케이스                | 예외 코드(예시)              | 처리 기준                          |
| ------------------ | ---------------------- | ------------------------------ |
| X-MEMBER-ID 누락/비정상 | INVALID_MEMBER_ID      | Controller / Service 초입 검증     |
| 내 코스 소유권 불일치       | FORBIDDEN_MY_COURSE    | MemberCourse 조건 불만족            |
| 코스 없음              | COURSE_NOT_FOUND       | courseId 조회 불가                 |
| 삭제된 코스 접근          | COURSE_DELETED         | `Course.deletedAt IS NOT NULL` |
| 내 코스 아님            | NOT_CUSTOMIZED_COURSE  | `Course.isCustomized = false`  |
| 일정 데이터 정합성 위반      | INVALID_ITINERARY_DATA | 로깅 후 제외 or 에러 (정책 선택)          |

> 보안 정책 팁: “존재하지만 내 코스 아님”을 숨기고 싶으면, 소유권 불일치 시에도 `COURSE_NOT_FOUND`로 마스킹 가능 (프로젝트 방침에 맞춰 통일)

---

## 11. Request / Response 예시

### Request

```
GET /api/v1/members/me/courses/5002
X-MEMBER-ID: 100
```

### Response (성공 예시)

```json
{
  "isSuccess": true,
  "code": "COURSE200_3",
  "message": "코스 상세 조회에 성공했습니다.",
  "result": {
    "courseId": 15,
    "videoTitle": "서울 여행 브이로그 11",
    "videoUrl": "https://www.youtube.com/watch?v=yt_idx_1353",
    "thumbnailUrl": "https://img.youtube.com/vi/sample/hqdefault.jpg",
    "channelName": "채널_마루",
    "regionId": 2,
    "regionName": "부산",
    "isScrapped": false,
    "travelStatus": "BEFORE",
    
    "courseTitle" : "여행1",
    "startDate" : null,
    "endDate" : null,
    
    "itineraries": [
      {
        "visitDay": 1,
        "places": [
          {
            "visitOrder": 1,
            "coursePlaceId": 764,
            "placeId": 23,
            "placeName": "핫플_23",
            "placeCategory": "카페",
            "address": "도로명 주소 23번길",
            "lat": 37.25630281684576,
            "lng": 128.37273059680382,
            "timestamp": null,
            "deletedAt": "2026-01-26T23:30:43"
          },
          {
            "visitOrder": 2,
            "coursePlaceId": 765,
            "placeId": 3,
            "placeName": "해운대해수욕장",
            "placeCategory": "해변",
            "address": "부산광역시 해운대구 우동",
            "lat": 35.158,
            "lng": 129.158,
            "timestamp": null,
            "deletedAt": null
          }
        ]
      },
      {
        "visitDay": 2,
        "places": [
          {
            "visitOrder": 1,
            "coursePlaceId": 766,
            "placeId": 21,
            "placeName": "핫플_21",
            "placeCategory": "음식점",
            "address": "도로명 주소 21번길",
            "lat": 37.585699437079676,
            "lng": 126.88337459124939,
            "timestamp": null,
            "deletedAt": null
          },
          {
            "visitOrder": 2,
            "coursePlaceId": 767,
            "placeId": 27,
            "placeName": "핫플_27",
            "placeCategory": "음식점",
            "address": "도로명 주소 27번길",
            "lat": 35.29044311734889,
            "lng": 127.7044267460745,
            "timestamp": null,
            "deletedAt": "2026-01-27T23:30:43"
          }
        ]
      }
    ]
  }
}
```

---

## 12. 한 줄 요약

> API 9는 사용자의 “내 코스” 단건을 조회하여 코스 마스터 정보와 일차별 장소 목록을 `visitDay`로 그룹화하고 `visitOrder`로 정렬해 반환하며, 삭제된 장소도 `deletedAt`과 함께 포함하는 상세 조회 API이다.
