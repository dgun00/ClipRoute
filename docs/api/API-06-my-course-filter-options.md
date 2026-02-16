# [API 6] 내 코스 – 동적 드롭다운 옵션 조회 API 지침서

## 1. API 목적 (Why)
- **사용자 경험 최적화**: 내 코스 화면의 드롭다운 필터(지역 / 여행일수 / 여행상태)는 유저가 실제로 보유한 코스 데이터에 존재하는 값만 노출되어야 함.
- **동적 필터링**: 필터를 하나 이상 선택했을 경우, 선택된 조건을 모두 만족하는 코스 집합(**AND 조건**)을 기준으로 유효한 드롭다운 옵션을 다시 계산하여 반환함.

## 2. API 역할 정의 (SRP)
- **책임**: 드롭다운에 사용할 유일한 옵션 값(`distinct`) 목록 제공.
- **비대상**: 코스 리스트 반환, 코스 ID/상세 데이터 반환 (해당 기능은 **API 7**의 책임임).

## 3. Endpoint
- **GET** `/api/v1/members/me/courses/filters`

## 4. Query String (선택 파라미터)
| 파라미터 | 타입 | 설명                                                  |
| :--- | :--- |:----------------------------------------------------|
| `regionId` | Long | 선택된 지역 ID (Optional)                                |
| `travelDays` | Integer | 선택된 여행 일수 (Optional)                                |
| `travelStatus` | String/Enum | 선택된 여행 상태 ( BEFORE, AFTER,PENDING,default = BEFORE) |

- **규칙**:
    - 모든 파라미터는 선택 사항임.
    - 전달된 파라미터들은 **AND 조건**으로 적용됨.
    - 파라미터 전달 순서는 결과에 영향을 주지 않음.

## 5. 동작 흐름
1. **최초 진입 (필터 미선택)**: `memberId` 기준 유저의 전체 코스 집합에서 `distinct` 옵션 계산.
2. **필터 선택 후**: `memberId` + 선택된 필터 조건을 만족하는 코스 집합에서 `region`, `travelDays`, `travelStatus`를 다시 `distinct` 계산.
3. **복수 필터 선택**: 모든 선택 조건을 만족하는 코스 집합을 기준으로 유효 옵션 도출.

## 6. Response 규격
`result` 객체 내 다음 세 가지 필드를 포함:

- `regions`: `{ id, name }` 객체 배열
- `travelDays`: Integer 배열
- `travelStatuses`: String(Enum) 배열

**[규칙]**
- 항상 `distinct` 값만 반환.
- **정렬**:
    - `regions`: `id` ASC (또는 `name` ASC 고정)
    - `travelDays`: ASC
- **빈 데이터**: 조건에 맞는 값이 없는 경우 에러가 아닌 **빈 배열 `[]`** 반환.

## 7. “내 코스” 기준 데이터 범위
옵션 계산 시 **API 7(내 코스 조회)**과 동일한 데이터 필터링 기준을 유지해야 함.

- `MemberCourse.memberId = :memberId`
- `MemberCourse.deletedAt IS NULL`
- `MemberCourse.isScrapped = true`
- `Course.deletedAt IS NULL`
- `Course.isCustomized = true` (스크랩 시 복사 코스 구조인 경우)

> **Note**: 기존 코드에 위 조건이 구현된 메서드가 있다면 반드시 재사용할 것.

## 8. 아키텍처 규칙
**[구조]**
`Controller` → `Service` → `Repository (QueryDSL)` → `DB`

**[역할 분리]**
- **Controller**: 요청 수신, Query String 파싱, Service 호출.
- **Service**: 비즈니스 로직 판단, 조건 조합, Converter 호출.
- **Repository**: QueryDSL을 활용한 `distinct` 쿼리 및 `orderBy` 처리.
- **Converter**: Entity/Raw Data를 DTO로 변환하는 역할만 수행.
- **금지 사항**: Service 내 QueryDSL 작성 금지, Converter 내 비즈니스 로직 금지.

## 9. QueryDSL 구현 가이드
- Query String으로 받은 값들을 `BooleanExpression`으로 모듈화.
- `null`이 아닌 조건만 `where` 절에 추가 (`where(cond1, cond2, ...)`).
- **전략**: 가독성과 유지보수를 위해 각 옵션(Region, Days, Status)별로 쿼리를 분리하거나, 하나의 공통 서브쿼리를 활용.

## 10. 기존 코드 수정 금지 원칙
- **허용**: 신규 클래스(Controller, Service, RepositoryCustom, DTO, Converter) 추가 및 기존 메서드 재사용.
- **금지**: 기존 API(1~5) 동작 변경, 주석변경 , 기존 메서드 시그니처 변경, 엔티티/DB 스키마 변경, 수정 필요할시 수정 허락 요청 필수.

## 11. SOLID & convention.md 준수
- **SRP**: 옵션 조회 책임에만 집중.
- **OCP**: 필터 옵션 확장이 용이한 구조 설계.
- **Convention**: 프로젝트 내 `convention.md`에 명시된 네이밍 규칙, 패키지 구조, 응답 포맷 엄수.

## 12. 한 줄 요약
> **API 6**은 현재 선택된 필터 조건(AND)을 적용한 코스 집합을 기반으로, 드롭다운에 표시할 유효한 **`distinct` 옵션 목록**만 반환하는 API이다.
