# [API 10] 내 코스 – 상세 편집 API 지침서 (최종)

---

## 1. API 목적 (Why)

- **내 코스 편집 기능 제공**
  사용자가 보유한 ‘내 코스’의 메타 정보와 일정(일차별 장소 구성)을 편집할 수 있도록 한다.

- **스냅샷 기반 저장**
  편집 화면에서 구성된 최종 상태를 한 번의 요청으로 서버에 커밋한다.

- **부분 업데이트(PATCH) 지원**
  Request Body에 포함된 필드만 수정하며, 포함되지 않은 필드는 기존 값을 유지한다.

---

## 2. API 역할 정의 (SRP)

- **책임**
    - 코스 기본 정보 수정
    - 여행 상태(travelStatus) 변경
    - 일정(itineraries) 전체 스냅샷 저장
    - 일정 내 장소 추가 / 삭제(soft delete) / 재정렬 처리

- **비대상**
    - 코스 생성 → API 5
    - 코스 삭제 → API 8
    - 보기 전용 상세 조회 → API 9
    - 장소 검색 → API 11

---

## 3. Endpoint

- **PATCH** `/api/v1/members/me/courses/{courseId}`

---

## 4. Path Variable

| 파라미터 | 타입 | 설명 |
|------|------|------|
| courseId | Long | 수정 대상 내 코스 ID |

---

## 5. Request Body (Partial Update + Snapshot)

```json
{
  "courseTitle": "제주도 힐링 여행",
  "startDate": "2026-01-26",
  "endDate": "2026-01-27",
  "travelStatus": "AFTER",
  "itineraries": [
    {
      "visitDay": 1,
      "items": [
        { "coursePlaceId": 1001 },
        { "placeId": 701 }
      ]
    },
    {
      "visitDay": 2,
      "items": [
        { "placeId": 702 }
      ]
    }
  ]
}
```

---

## 6. 필드별 수정 규칙

### 6-1. 기본 필드

| 필드 | 규칙 |
|---|---|
| courseTitle | 포함 시 수정, 미포함 시 유지 |
| startDate / endDate | 포함 시 수정, 미포함 시 유지 |
| travelStatus | 포함 시 즉시 수정 |

### 6-2. itineraries 필드

- Request Body에 `itineraries`가 **포함된 경우**
    - 해당 값은 **최종 일정 스냅샷**으로 간주한다.
- Request Body에 `itineraries`가 **없는 경우**
    - 기존 일정은 **변경하지 않는다.**

---

## 7. itineraries 스냅샷 정책 (A)

### 7-1. 기본 원칙

- `visitDay` + `items[]`는 해당 일차의 **최종 상태**를 의미한다.
- `items` 배열의 **순서(index)** 가 곧 `visitOrder`이다.
- 드래그앤드롭에 따른 순서 변경은 **프론트엔드 책임**이다.

---

### 7-2. items 구조 규칙

- `items` 배열에는 **기존 항목과 신규 항목이 섞여 있을 수 있다.**
- 단, **하나의 item은 반드시 아래 둘 중 하나만 포함해야 한다.**

| item 형태 | 의미 |
|---|---|
| `{ "coursePlaceId": Long }` | 기존 방문 인스턴스 |
| `{ "placeId": Long }` | 신규 방문 인스턴스 |

#### 금지 규칙
- 하나의 item에 `coursePlaceId`와 `placeId`를 **동시에 포함하는 경우** → INVALID_REQUEST
- 둘 다 없는 item → INVALID_REQUEST

---

### 7-3. 서버 처리 방식

1. **기존 CoursePlace 조회**
    - `courseId` 기준 전체 조회 (Fetch Join)

2. **Request Body itineraries 순회**
    - `coursePlaceId` 존재 → UPDATE (visitDay, visitOrder)
    - `placeId` 존재 → INSERT (새 CoursePlace 생성)

3. **Request Body에 포함되지 않은 CoursePlace**
    - **즉시 삭제 (Hard Delete)**
    - 사용자가 명시적으로 제거한 것으로 간주
    - `DELETE FROM course_place WHERE id IN (...)`

### 7-4. Place 폐점 처리 (별도 시나리오)

**Admin의 Place 삭제 (폐점)**
- Place.deletedAt = now() (Soft Delete)
- 기존 CoursePlace는 유지 (FK 관계 보존)

**사용자 응답 시**
- Place.deletedAt != null → 프론트엔드가 "폐점됨" 표시
- 별도 status 필드 없음 (deletedAt으로 충분)

**폐점 장소 제거**
- 사용자가 편집 시 해당 coursePlaceId를 itineraries에서 제외
- CoursePlace Hard Delete (일반 제거와 동일)

---

## 8. 중복 placeId 정책

- **동일 placeId의 중복 방문을 허용한다.**
- 동일한 `placeId`가 여러 번 요청될 경우,
  요청 순서대로 각각 **독립적인 CoursePlace 엔티티**를 생성한다.


---

## 9. 데이터 정합성 및 보안 검증

### 9-1. 기본 검증

- 요청자(memberId)와 코스 소유자 일치 여부
- `Course.deletedAt IS NULL`
- `Course.isCustomized = true`
- `MemberCourse.deletedAt IS NULL`
- 
### 9-2. Request Body 검증

**날짜 검증**
- startDate, endDate는 필수 (null 불가)
- endDate >= startDate (같은 날 당일치기 허용)
- 위반 시 → `INVALID_DATE_RANGE`

**visitDay 검증**
- Request Body 내 visitDay 중복 불가 → `DUPLICATE_VISIT_DAY`
- visitDay는 1부터 시작하며 연속되어야 함 (1, 2, 3...)
    - 예: [1, 3] (2 건너뜀) → `INVALID_VISIT_DAY_SEQUENCE`
    - 예: [2, 3] (1부터 시작 안 함) → `INVALID_VISIT_DAY_SEQUENCE`

**ID 검증**
- `coursePlaceId` 검증
    - 존재 여부
    - 해당 courseId 소속 여부
- `placeId` 존재 여부 검증

---
## 10. 예외 처리 정책

| 상황 | ErrorCode |
|---|---|
| 존재하지 않는 courseId | COURSE_NOT_FOUND |
| 내 코스 아님 | COURSE_ACCESS_DENIED |
| 삭제된 코스 | COURSE_ALREADY_DELETED |
| 커스터마이즈 불가 코스 | COURSE_NOT_EDITABLE |
| 날짜 범위 오류 | INVALID_DATE_RANGE |
| visitDay 중복 | DUPLICATE_VISIT_DAY |
| visitDay 연속성 오류 | INVALID_VISIT_DAY_SEQUENCE |
| coursePlaceId 없음 | COURSE_PLACE_NOT_FOUND |
| placeId 없음 | PLACE_NOT_FOUND |
| item 구조 오류 | INVALID_REQUEST |
---

## 11. Response 규격

- **API 9 (내 코스 상세 조회)와 동일한 응답 구조 반환**
- 수정 완료 직후의 최신 상태 기준
### 응답 예시 (폐점 장소 포함)
```json
{
  "isSuccess": true,
  "code": "COMMON200",
  "message": "성공입니다.",
  "result": {
    "courseId": 5002,
    "videoTitle": "[Vlog] 제주도 서쪽 일주일 살기",
    "itineraries": [
      {
        "visitDay": 1,
        "places": [
          {
            "coursePlaceId": 1001,
            "placeId": 501,
            "placeName": "성산일출봉",
            "visitOrder": 1,
            "deletedAt": null
          },
          {
            "coursePlaceId": 1002,
            "placeId": 505,
            "placeName": "곰막식당",
            "visitOrder": 2,
            "deletedAt": "2026-02-06T10:00:00"  // 폐점됨
          }
        ]
      }
    ]
  }
}
```


---

**폐점 장소 표시:**
- Place.deletedAt 필드로 구분
- `deletedAt != null` → 프론트가 폐점 UI 표시
- 별도 status 필드 사용 안 함

**CoursePlace 포함 규칙:**
- Hard Delete된 CoursePlace는 응답에 포함되지 않음
- Place가 Soft Delete된 CoursePlace는 포함됨 (deletedAt 필드 있음)
---

## 12. 아키텍처 및 구현 규칙

### 12-1. 기본 구조
- **Controller**
    - `MemberCommandController`

- **Service**
    - `MemberCommandService`
    - 스냅샷 기반 저장 로직 구현
    - 부분 업데이트 분기 처리

- **Repository**
    - QueryDSL + Fetch Join
    - 일정 조회 시 N+1 방지

- **Transaction**
    - 단일 `@Transactional`
    - 모든 수정은 원자적으로 처리

---
### 12-2. N+1 문제 방지 전략

**문제 상황:**
- Request Body의 itineraries를 순회하며 각 coursePlaceId를 개별 조회하면 N번의 SELECT 발생
- 100개 장소 편집 시 100번의 DB 왕복 → 성능 저하

**해결 방법:**

1. **일괄 조회 (Fetch Join)**
```java
   // CoursePlace + Place를 한 번에 로드
   List existingPlaces = coursePlaceRepository
       .findAllByCourseIdWithPlace(courseId);
```

2. **메모리 캐싱 (Map 활용)**
```java
   // coursePlaceId를 키로 하는 Map 생성
   Map placeMap = existingPlaces.stream()
       .collect(Collectors.toMap(
           CoursePlace::getId,
           Function.identity()
       ));
   
   // Request Body 순회하며 Map에서 O(1) 조회
   for (ItemDto item : items) {
       if (item.getCoursePlaceId() != null) {
           CoursePlace place = placeMap.get(item.getCoursePlaceId());
           place.setVisitOrder(index++);  // 변경 감지
       }
   }
```

3. **Dirty Checking 활용**
    - 엔티티 필드를 직접 수정하면 트랜잭션 종료 시 자동 UPDATE
    - 명시적 `save()` 호출 불필요
    - JPA가 변경된 엔티티만 일괄 UPDATE

**QueryDSL 예시:**
```java
public List findAllByCourseIdWithPlace(Long courseId) {
    return queryFactory
        .selectFrom(coursePlace)
        .leftJoin(coursePlace.place, place).fetchJoin()
        .where(coursePlace.course.id.eq(courseId))
        .fetch();
}
```

**효과:**
- 기존: N+1번 쿼리 (1 + 100)
- 개선: 2번 쿼리 (1 조회 + 1 일괄 UPDATE)
---

### 12-3. 트랜잭션 실행 순서

1. **검증 단계**
    - 모든 coursePlaceId, placeId 존재 여부 확인
    - 날짜, visitDay 유효성 검증
    - 검증 실패 시 즉시 예외 발생 (DB 변경 전)

2. **변경 단계**
    - 기존 CoursePlace UPDATE (visitDay, visitOrder)
    - 신규 CoursePlace INSERT
    - 미포함 CoursePlace DELETE

3. **조회 단계**
    - 최신 상태 조회 (API 9 로직 재사용)
    - 응답 DTO 변환 및 반환
---
## 13. 한 줄 요약

> **API 10은 내 코스 편집 화면의 최종 상태를 스냅샷으로 저장하는 PATCH API이며, 기존(coursePlaceId)과 신규(placeId) 항목을 혼합 처리하고 배열 순서로 visitOrder를 결정한다.**
````

---