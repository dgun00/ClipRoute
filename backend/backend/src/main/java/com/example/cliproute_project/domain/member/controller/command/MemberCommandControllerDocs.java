package com.example.cliproute_project.domain.member.controller.command;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface MemberCommandControllerDocs {

    // [8 API]
    @Operation(
            summary = "[8 API] My course delete",
            description = "Soft deletes member course and course places; course is soft deleted only when customized. Returns deletedAt."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MYCOURSE200_4", description = "My course deleted successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER401_1", description = "Unauthorized"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_1", description = "Invalid course id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE404_1", description = "My course not found.")
    })
    ApiResponse<MemberResDTO.MyCourseDeleteResultDTO> deleteMyCourse(
            Long memberId,
            Long courseId
    );

    // [10 API]
    @Operation(
            summary = "[10 API] My course detail edit",
            description = "Edits my course detail and returns updated detail."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MYCOURSE200_5", description = "My course detail edited successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER401_1", description = "Unauthorized"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_1", description = "Invalid course id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_4", description = "Invalid date range."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_5", description = "Duplicate visit day."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_6", description = "Invalid visit day sequence."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_7", description = "Invalid request."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE400_8", description = "Course already deleted."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE403_1", description = "Access denied for this course."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE403_2", description = "Course is not editable."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE404_1", description = "My course not found."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE404_2", description = "Course place not found."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER_COURSE404_3", description = "Place not found.")
    })
    ApiResponse<MemberResDTO.MyCourseDetailDTO> editMyCourseDetail(
            Long memberId,
            Long courseId,
            MemberReqDTO.MyCourseDetailEditDTO request
    );
}
