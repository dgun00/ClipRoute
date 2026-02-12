# [API 8] 내 코스 – 삭제 API 지침서

---

## 1. API 목적 (Why)

- 사용자가 더 이상 필요로 하지 않는 **내 코스(My Course)** 를 목록에서 제거한다.
- 데이터의 완전 삭제를 방지하기 위해 **Soft Delete 방식**을 사용하며, 실제 레코드는 유지하고 `deletedAt` 필드만 갱신한다.
- 삭제 이후에도 통계, 로그, 추적 목적의 데이터 정합성을 유지한다.

---

## 2. API 역할 정의 (SRP)

### 책임 (Responsibility)

- 특정 `courseId`에 대해, **요청 사용자와 연결된 내 코스 관계를 논리적으로 삭제**한다.
- 커스텀 코스(`isCustomized = true`)의 경우, 사용자 단독 소유 리소스이므로 **연관된 Course 엔티티까지 함께 Soft Delete** 처리한다.

### 비대상 (Out of Scope)

- 원본 코스(`isCustomized = false`) 삭제
- 장소(`Place`), 지역(`Region`) 등 공용 마스터 데이터 삭제
- 타 사용자의 내 코스에 대한 변경

---

## 3. Endpoint

```http
DELETE /api/v1/members/me/courses/{courseId}
```

---

## 4. Parameters

### Path Variable

| 이름 | 타입 | 설명 |
|---|---|---|
| courseId | Long | 삭제할 내 코스 ID |

### Header

| 이름 | 타입 | 설명 |
|---|---|---|
| X-MEMBER-ID | Long | 요청 사용자 식별자 |

---

## 5. 핵심 도메인 전제 (중요)

- `isCustomized = true` 인 코스는 **사용자 단독 소유(1:1 대응)** 리소스이다.
- 커스텀 코스는 다른 사용자가 스크랩하거나 공유할 수 없다.
- 따라서 커스텀 코스 삭제 시, 해당 `Course` 엔티티는 고아 데이터 방지를 위해 함께 Soft Delete 처리한다.

---

## 6. 동작 흐름

1. **인증 및 사용자 식별**
    - `X-MEMBER-ID` 헤더를 통해 요청 사용자 식별

2. **소유권 검증**
    - `MemberCourse.memberId = X-MEMBER-ID`
    - `MemberCourse.courseId = courseId`
    - 위 조건을 만족하지 않으면 접근 불가

3. **상태 검증**
    - 이미 `deletedAt != null` 인 경우에도 요청은 허용 (Idempotent)

4. **Soft Delete 처리**
    - `deletedAt`이 `null`인 경우에만 `MemberCourse.deletedAt = now()` 설정
    - 이미 삭제된 경우 기존 `deletedAt` 값 유지
    - 연관된 커스텀 코스(`Course.isCustomized = true`)인 경우
        - `Course.deletedAt = now()`

5. **응답 반환**
    - 삭제 성공 여부와 관계없이 정상 처리 시 성공 응답 반환

---

## 7. Response 규격

```json
{
  "isSuccess": true,
  "code": "COMMON200",
  "message": "성공입니다.",
  "result": {
    "courseId": 15,
    "deletedAt": "2026-02-06T14:30:00Z"
  }
}
```

---

## 8. 아키텍처 규칙

### Controller
- `MemberCommandController`
- 상태 변경(Command) 전용 컨트롤러 사용

### Service
- `MemberCommandService`
- 소유권 검증, 삭제 대상 판별, Soft Delete 로직 수행
- `@Transactional` 필수

### Repository
- `MemberCourseRepository`
- `CourseRepository`
- Dirty Checking 기반 엔티티 업데이트 또는 `@Modifying` 쿼리 사용 가능

---

## 9. 구현 가이드

- **보안**
    - 반드시 `WHERE member_id = :memberId` 조건을 포함하여 타 사용자 데이터 삭제 방지
- **Idempotent 보장**
    - 이미 삭제된 리소스에 대한 DELETE 요청도 성공 응답 반환
- **CQRS 준수**
    - 본 API는 Command API로, Query API와 책임 분리

---

## 10. 예외 처리 정책

| 상황 | 예외 코드 |
|---|---|
| courseId가 유효하지 않음 | INVALID_COURSE_ID |
| 내 코스가 아님 | MY_COURSE_NOT_FOUND |


- 모든 예외는 `MemberException` 또는 `CourseException` 사용
- Global Exception Handler를 통해 공통 응답 포맷 유지

---

## 11. 기존 코드 수정 금지 원칙

- API 6, API 7, API 9(상세 조회/편집) 동작 변경 ❌
- Entity 구조 및 DB 스키마 변경 ❌
- 기존 비즈니스 규칙 우회 ❌

---

## 12. 한 줄 요약

> **API 8은 사용자 소유의 내 코스를 Soft Delete 방식으로 제거하며, 커스텀 코스의 경우 연관된 Course까지 함께 논리 삭제하는 Command API이다.**
