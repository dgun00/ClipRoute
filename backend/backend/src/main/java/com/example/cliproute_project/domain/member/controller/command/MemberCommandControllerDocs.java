package com.example.cliproute_project.domain.member.controller.command;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface MemberCommandControllerDocs {

    // [8 API]
    @Operation(
            summary = "[8 API] Delete my course",
            description = "Soft deletes member course and course places; course is soft deleted only when customized. Returns deletedAt."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: MYCOURSE200_4)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "400",
                    description = "Bad request (business code: MEMBER_COURSE400_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized (business code: MEMBER401_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "404",
                    description = "Not found (business code: MEMBER_COURSE404_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
    })
    ApiResponse<MemberResDTO.MyCourseDeleteResultDTO> deleteMyCourse(
            String token,
            Long courseId
    );

    // [10 API]
    @Operation(
            summary = "[10 API] Edit my course detail",
            description = "Edits my course detail and returns updated detail. Includes yt_video_id."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: MYCOURSE200_5)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "400",
                    description = "Bad request (business codes: MEMBER_COURSE400_1, MEMBER_COURSE400_4, MEMBER_COURSE400_5, MEMBER_COURSE400_6, MEMBER_COURSE400_7, MEMBER_COURSE400_8)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized (business code: MEMBER401_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "403",
                    description = "Forbidden (business codes: MEMBER_COURSE403_1, MEMBER_COURSE403_2)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "404",
                    description = "Not found (business codes: MEMBER_COURSE404_1, MEMBER_COURSE404_2, MEMBER_COURSE404_3)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
    })
    ApiResponse<MemberResDTO.MyCourseDetailDTO> editMyCourseDetail(
            String token,
            Long courseId,
            MemberReqDTO.MyCourseDetailEditDTO request
    );
}
