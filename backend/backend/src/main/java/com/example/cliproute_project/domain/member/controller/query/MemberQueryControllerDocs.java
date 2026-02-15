package com.example.cliproute_project.domain.member.controller.query;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;


public interface MemberQueryControllerDocs {

    @Operation(
            summary = "[6 API] My course filter options",
            description = "Returns distinct filter options based on selected filters (AND)."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MYCOURSE200_1", description = "My course filter options fetched successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER401_1", description = "Authentication required."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_2", description = "Invalid region id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_3", description = "Invalid travel days.")
    })
    ApiResponse<MemberResDTO.FilterOptionsDTO> getMyCourseFilterOptions(
            String token,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    @Operation(
            summary = "[7 API] My course list",
            description = "Returns my course list with filters and no-offset pagination."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MYCOURSE200_2", description = "My course list fetched successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER401_1", description = "Authentication required."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_2", description = "Invalid region id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_3", description = "Invalid travel days.")
    })
    ApiResponse<MemberResDTO.MyCourseListDTO> getMyCourses(
            String token,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus,
            Long lastMemberCourseId,
            Integer pageSize
    );

    @Operation(
            summary = "[9 API] My course detail",
            description = "Returns my course detail with course info and itineraries."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MYCOURSE200_3", description = "My course detail fetched successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER401_1", description = "Authentication required."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_1", description = "Invalid course id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE403_1", description = "Access denied for this course."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE404_1", description = "My course not found.")
    })
    ApiResponse<MemberResDTO.MyCourseDetailDTO> getMyCourseDetail(
            String token,
            Long courseId
    );
}