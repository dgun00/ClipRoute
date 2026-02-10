package com.example.cliproute.domain.course.controller.query;


import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface CourseQueryControllerDocs {
    @Operation(
            summary = "[2번 API] 인기/대표 코스 리스트 조회 (임시 처리)",
            description = "인기영상의 코스를 random으로 조회 (random 로직 구현 힘들거같음 -> 될거같음), 무한 스크롤"
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger에 response 형태 보여주기용"),

            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_1", description = "코스 목록 조회에 성공했습니다."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE404_1", description = "코스를 찾을 수 없습니다.")
    })
    ApiResponse<CourseResDTO.CoursePublicListDTO> getCourseList(
            Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId, Integer lastValue, int pageSize
    );


    @Operation(
        summary = "[3번 API] 필터링 및 추천 코스 리스트 조회 (임시 처리)",
        description = "지역/일수 필터링 검색 결과 소진시 추천 코스를 조회, 무한 스크롤, random 로직 구현예정")
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger에 response 형태 보여주기용"),

            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_1", description = "코스 목록 조회에 성공했습니다."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE404_1", description = "코스를 찾을 수 없습니다.")
    })
    ApiResponse<CourseResDTO.CoursePublicListDTO> getCoursesWithRecommendation(
            Long regionId, Integer travelDays, String sort, Long seed, int page, int pageSize
    );

    @Operation(
            summary = "[4번 API] 코스 상세 조회",
            description = "비로그인/로그인(코스 저장 x)용 코스 상세 조회 기능"
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger에 response 형태 보여주기용"),

            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_3", description = "코스 상세 조회에 성공했습니다."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER400_?", description = "AUTH 도메인쪽에서 생성해야함.")
    })
    ApiResponse<CourseResDTO.CourseDetailDTO> getCourseDetail(
            Long courseId,
            Long memberId
    );
}


