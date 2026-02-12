# AI Agent Code Convention

## Package / Folder Structure
- Keep domain packages under `domain/{domain}/{controller|service|repository|dto|exception}`.
- Split controllers into `command` and `query` subpackages.
- Split services into `interface` and `impl` (`*Service`, `*ServiceImpl`).
- Keep DTOs under `dto/req` and `dto/res`.

## Controller Rules
- Always return `ApiResponse.onSuccess(code, result)` for success responses.
- Base route is `/api/v1` plus resource path.
- Swagger docs live in `*ControllerDocs` interface; controller `implements` it.
- Member identification uses `X-MEMBER-ID` header; service validates null or invalid values.

## Service Rules
- Read operations use `@Transactional(readOnly = true)`.
- Business logic belongs in services; controllers orchestrate only.
- Validate parameters in service; throw domain exceptions when invalid.

## Repository Rules
- Use `JpaRepository` for CRUD.
- Use QueryDSL for complex queries via `*RepositoryCustom` + `*RepositoryImpl`.
- Use `fetchJoin` to avoid N+1 where appropriate.

## DTO Rules
- Response DTOs use `record` + `@Builder`.
- Wrap list responses in list DTOs.
- Group related response DTOs as nested records in a single file.

## Exception / Code Rules
- Domain-Specific Exceptions: Each domain must have its own Exception class (e.g., CourseException, MemberException) located in its exception package.

- Error/Success Codes: Utilize or add domain-specific ErrorCode and SuccessCode enums within the domain's exception package.

- Error Code Standard: All error codes must implement the BaseErrorCode interface.

## Exception Convention
- Message language is English.
- Domain codes use domain-specific prefixes (e.g., COURSE, PLACE, REGION, MEMBER_COURSE).
- Common/Auth codes remain in global (`COMMON*`, `AUTH*`) and are reused by domains when applicable.
- Code format is `PREFIX + HTTP_STATUS + _ + SEQ` (e.g., `PLACE400_1`, `COURSE404_2`).

## Soft Delete Policy
- `MemberCourse`: always soft delete on my-course delete.
- `CoursePlace`: always soft delete on my-course delete.
- `Course`: soft delete only when `isCustomized == true`.

## Swagger Rules
- Use `@Operation` and `@ApiResponses` with actual `SuccessCode`/`ErrorCode` values.
- Keep controller docs synced with implementation.

## Coding Style
- Use `@RequiredArgsConstructor` for DI.
- Use clear verb-based method names: `get*`, `create*`, `update*`, `delete*`, `find*`.
- Prefer expressive names over noisy comments.
