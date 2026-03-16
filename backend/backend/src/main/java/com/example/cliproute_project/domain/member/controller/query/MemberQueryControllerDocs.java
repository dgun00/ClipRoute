package com.example.cliproute_project.domain.member.controller.query;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;


public interface MemberQueryControllerDocs {

    @Operation(
            summary = "[6 API] My course filter options",
            description = "Returns distinct filter options based on selected filters (AND)."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: MYCOURSE200_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "400",
                    description = "Bad request (business codes: MEMBER_COURSE400_2, MEMBER_COURSE400_3)",
                    content = @Content(
                            schema = @Schema(implementation = ApiResponse.class),
                            examples = {
                                    @ExampleObject(
                                            name = "Invalid Region Id",
                                            value = """
                                                    {
                                                      "isSuccess": false,
                                                      "code": "MEMBER_COURSE400_2",
                                                      "message": "Invalid region id.",
                                                      "result": null
                                                    }
                                                    """
                                    ),
                                    @ExampleObject(
                                            name = "Invalid Travel Days",
                                            value = """
                                                    {
                                                      "isSuccess": false,
                                                      "code": "MEMBER_COURSE400_3",
                                                      "message": "Invalid travel days.",
                                                      "result": null
                                                    }
                                                    """
                                    )
                            }
                    )
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized (business code: MEMBER401_1)",
                    content = @Content(
                            schema = @Schema(implementation = ApiResponse.class),
                            examples = @ExampleObject(
                                    name = "Unauthorized",
                                    value = """
                                            {
                                              "isSuccess": false,
                                              "code": "MEMBER401_1",
                                              "message": "Authentication required.",
                                              "result": null
                                            }
                                            """
                            )
                    )
            )
    })
    ApiResponse<MemberResDTO.FilterOptionsDTO> getMyCourseFilterOptions(
            String token,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    @Operation(
            summary = "[7 API] My course list",
            description = "Returns my course list with filters and no-offset pagination. Includes yt_video_id."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: MYCOURSE200_2)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "400",
                    description = "Bad request (business codes: MEMBER_COURSE400_2, MEMBER_COURSE400_3)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized (business code: MEMBER401_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
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
            description = "Returns my course detail with course info and itineraries. Includes yt_video_id."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: MYCOURSE200_3)",
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
                    responseCode = "403",
                    description = "Forbidden (business code: MEMBER_COURSE403_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "404",
                    description = "Not found (business code: MEMBER_COURSE404_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
    })
    ApiResponse<MemberResDTO.MyCourseDetailDTO> getMyCourseDetail(
            String token,
            Long courseId
    );
}
