# [API 7] 내 코스 – 필터 기반 목록 조회 API 지침서

---

## 1. API 목적 (Why)

- **개인화된 목록 제공**  
  사용자가 스크랩하거나 직접 편집한 ‘내 코스’ 목록을 화면에 출력함.

- **연동된 필터링**  
  API 6에서 조회한 옵션 값을 바탕으로 유저가 선택한 조건(지역, 일수, 상태)에 맞는 코스만 선별하여 보여줌.

- **무한 스크롤 지원**  
  데이터 증가를 고려하여 Slice 기반 페이징을 적용, 성능과 UX를 동시에 확보함.

---

## 2. API 역할 정의 (SRP)

- **책임**
    - 필터 조건에 맞는 코스의 요약 정보 리스트 반환
    - (제목, 썸네일, 상태 등)

- **비대상**
    - 드롭다운 옵션 계산 → API 6의 책임
    - 특정 코스의 상세 장소 정보 반환 → API 4 / API 8의 책임

---

## 3. Endpoint
- GET /api/v1/members/me/courses

---

## 4. Query String (선택 파라미터)

| 파라미터 | 타입 | 설명                                 |
|------|------|------------------------------------|
| regionId | Long | 선택된 지역 ID (Optional)               |
| travelDays | Integer | 선택된 여행 일수 (Optional)               |
| travelStatus | String / Enum | 여행 상태 (BEFORE, AFTER, NONE)     |
| lastMemberCourseId | Long | 페이지 커서: 마지막으로 조회한 스크랩 ID (Optional) |
| pageSize | Integer | 한 번에 가져올 데이터 개수 (Default: 5)       |

### 규칙
- 필터 파라미터(`regionId`, `travelDays`, `travelStatus`)는 **AND 조건**으로 적용
- 커서는 정렬 기준(`MemberCourse.id DESC)과 동일하게 동작하며,
  다음 페이지 요청 시 마지막 아이템의 `memberCourseId`과 `memberCourseId`를 함께 전달해야 동일 정렬이 유지됨

---

## 5. 동작 흐름

1. **인증 확인**
    - 헤더의 `X-MEMBER-ID`를 통해 유효한 사용자 확인

2. **동적 쿼리 생성**
    - 전달된 필터 값이 있는 경우에만 `where` 절에 추가

3. **데이터 조회**
    - `MemberCourse`, `Course`, `Region`, `Video`, `Image` 조인
    - Fetch Join 활용하여 1번의 쿼리로 조회, N+1 문제 방지

4. **결과 반환**
    - `Slice` 객체 생성
    - 다음 페이지 존재 여부와 함께 데이터 리스트 반환, 다른 슬라이싱 사용한 API 참고

---

## 6. Response 규격

### result 객체 내 포함 필드

- **courseList**: 코스 정보 객체 배열
    - `courseId`
    - `courseTitle`
    - `regionName`
    - `regionRepImageUrl`
    - `thumbnailUrl`
    - `startDate` 
    - `endDate`
    - `travelDays`
    - `travelStatus`
    - `placeCount`
    - `memberCourseId`
    - `updatedAt`

- **sort** : 정렬기준(default:최신등록순)
- **sliceInfo**: 슬라이싱 메타데이터
    - `currentPage` : 현 페이지
    - `size`: 페이지 사이즈   
    - `hasNext` : 다음 페이지 존재 유무 


### 정렬 규칙
1. 기본: `MemberCourse.id DESC` (최신 스크랩순)
2. 2차: `MemberCourse.id DESC` (동일 시간 대비 순서 보장)

---

## 7. “내 코스” 기준 데이터 범위

API 6과 동일한 무결성 기준을 **엄격히 준수**

- `MemberCourse.memberId = :memberId`
- `MemberCourse.deletedAt IS NULL`
- `MemberCourse.isScrapped = true`
- `Course.deletedAt IS NULL`
- `Course.isCustomized = true`

---

## 8. 아키텍처 규칙

- **Controller**
    - `MemberQueryController` 에 엔드포인트 추가

- **Service**
    - `MemberQueryService`
    - 필터 조건을 조립하여 Repository 호출

- **Repository**
    - `MemberCourseRepositoryImpl`
    - QueryDSL을 사용한 복합 조인 및 페이징 처리

- **Converter**
    - `MemberConverter`
    - `MemberCourse` 엔티티 리스트 → `MyCourseDTO` 리스트 변환

---

## 9. QueryDSL 구현 가이드

- BooleanExpression 도우미 메서드(`eqRegionId`, `eqTravelDays` 등)를  
  기존 API 과 **공유하여 재사용성 극대화**
- N+1 문제 방지를 위해 `fetchJoin()` 적극 사용
- `limit(pageSize + 1)`로 조회하여 `hasNext` 여부 판단

---

## 10. 기존 코드 수정 금지 원칙

- **허용**: 신규 클래스(Controller, Service, RepositoryCustom, DTO, Converter) 추가 및 기존 메서드 재사용.
- **금지**: 기존 API 동작 변경, 주석변경 , 기존 메서드 시그니처 변경, 엔티티/DB 스키마 변경, 수정 필요할시 수정 허락 요청 필수.

---

## 11. SOLID & convention.md 준수

- **LSP / ISP**
    - 기존 인터페이스 구조를 파괴하지 않고 확장
- **SRP**: 옵션 조회 책임에만 집중.
- **OCP**: 필터 옵션 확장이 용이한 구조 설계.
- **Naming**
    - 응답 DTO는 `MemberResDTO.MyCourseListDTO` 형태로 계층화
- **Global Response**
    - 반드시 `ApiResponse.onSuccess` 형식 유지
- **Convention**: 프로젝트 내 `convention.md`에 명시된 네이밍 규칙, 패키지 구조, 응답 포맷 엄수.

---

## 12. 한 줄 요약

> **API 7은 사용자의 스크랩 코스 중 필터 조건에 맞는 데이터를 최신순으로 페이징하여 상세 요약 정보를 제공하는 목록 조회 API이다.**
