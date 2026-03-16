package com.example.cliproute_project.domain.course.controller.command;

import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;


public interface CourseCommandControllerDocs {
    // [5 API]
    @Operation(
            summary = "[5 API] Scrap course",
            description = "Creates or returns a scrapped course for the authenticated member."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success. The current implementation returns 200 OK with business code COURSE201_1.",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "400",
                    description = "Bad request (business codes: MEMBER400_1, COURSE400_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized (business code: MEMBER401_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "404",
                    description = "Not found (business code: COURSE404_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
    })
    ApiResponse<CourseResDTO.ScrapResultDTO> scrapCourse(
             String email,
             Long courseId,
             CourseReqDTO.CourseDateRequestDTO travelPeriod
    );
}
