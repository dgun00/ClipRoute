package com.example.cliproute.domain.member.controller.query;

import com.example.cliproute.domain.member.dto.res.MemberResDTO;
import com.example.cliproute.domain.member.enums.TravelStatus;
import com.example.cliproute.global.apiPayload.ApiResponse;
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
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "AUTH401_1", description = "Unauthorized")
    })
    ApiResponse<MemberResDTO.FilterOptionsDTO> getMyCourseFilterOptions(
            Long memberId,
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
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "AUTH401_1", description = "Unauthorized")
    })
    ApiResponse<MemberResDTO.MyCourseListDTO> getMyCourses(
            Long memberId,
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
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE200_3", description = "Course details fetch success."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "AUTH401_1", description = "Unauthorized"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "AUTH403_1", description = "Forbidden")
    })
    ApiResponse<MemberResDTO.MyCourseDetailDTO> getMyCourseDetail(
            Long memberId,
            Long courseId
    );
}

