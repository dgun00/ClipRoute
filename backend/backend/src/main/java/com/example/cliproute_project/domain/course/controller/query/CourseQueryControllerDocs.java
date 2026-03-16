package com.example.cliproute_project.domain.course.controller.query;


import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.ExampleObject;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.constraints.Positive;

public interface CourseQueryControllerDocs {
    @Operation(
            summary = "[2 API] Public course list",
            description = "Returns public courses with filters and cursor pagination."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: COURSE200_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
    })
    ApiResponse<CourseResDTO.CoursePublicListDTO> getCourseList(
            Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId, Integer lastValue, int pageSize
    );


    @Operation(
        summary = "[3 API] Recommended course list",
        description = "Returns public courses with recommendation and pagination."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: COURSE200_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
    })
    ApiResponse<CourseResDTO.CoursePublicListDTO> getCoursesWithRecommendation(
            Long regionId, Integer travelDays, String sort, Long seed, int page, int pageSize
    );

    @Operation(
            summary = "[4 API] Course detail",
            description = "Returns course detail. The Authorization header is optional."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: COURSE200_3)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
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
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "404",
                    description = "Not found (business codes: COURSE404_1, MEMBER404_1)",
                    content = @Content(
                            schema = @Schema(implementation = ApiResponse.class),
                            examples = {
                                    @ExampleObject(
                                            name = "Course Not Found",
                                            value = """
                                                    {
                                                      "isSuccess": false,
                                                      "code": "COURSE404_1",
                                                      "message": "Course not found.",
                                                      "result": null
                                                    }
                                                    """
                                    ),
                                    @ExampleObject(
                                            name = "Member Not Found",
                                            value = """
                                                    {
                                                      "isSuccess": false,
                                                      "code": "MEMBER404_1",
                                                      "message": "Member not found.",
                                                      "result": null
                                                    }
                                                    """
                                    )
                            }
                    )
            )
    })
    ApiResponse<CourseResDTO.CourseDetailDTO> getCourseDetail(
            @Positive Long courseId,
            String token
    );
}
