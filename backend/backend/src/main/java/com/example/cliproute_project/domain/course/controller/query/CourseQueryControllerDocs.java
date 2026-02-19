package com.example.cliproute_project.domain.course.controller.query;


import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.constraints.Positive;

public interface CourseQueryControllerDocs {
    @Operation(
            summary = "[2 API] Public course list",
            description = "Returns public courses with filters and cursor pagination."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_1", description = "Course list fetched successfully.")
    })
    ApiResponse<CourseResDTO.CoursePublicListDTO> getCourseList(
            Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId, Integer lastValue, int pageSize
    );


    @Operation(
        summary = "[3 API] Recommended course list",
        description = "Returns public courses with recommendation and pagination."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_1", description = "Course list fetched successfully.")
    })
    ApiResponse<CourseResDTO.CoursePublicListDTO> getCoursesWithRecommendation(
            Long regionId, Integer travelDays, String sort, Long seed, int page, int pageSize
    );

    @Operation(
            summary = "[4 API] Course detail",
            description = "Returns course detail. Authorization token is optional."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_3", description = "Course detail fetched successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE404_1", description = "Course not found.")
    })
    ApiResponse<CourseResDTO.CourseDetailDTO> getCourseDetail(
            @Positive Long courseId,
            String token
    );
}
