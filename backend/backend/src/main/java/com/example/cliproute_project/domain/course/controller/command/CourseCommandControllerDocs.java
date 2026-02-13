package com.example.cliproute_project.domain.course.controller.command;

import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;


public interface CourseCommandControllerDocs {
    // [5 API]
    @Operation(
            summary = "[5 API] Scrap course",
            description = "Scraps or cancels scrap for a course."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE201_1", description = "Course scrapped successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE204_1", description = "Course scrap canceled."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER401_1", description = "Authentication required."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "MEMBER400_1", description = "Invalid member id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE400_1", description = "Invalid course id."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE404_1", description = "Course not found.")
    })
    ApiResponse<CourseResDTO.ScrapResultDTO> scrapCourse(
             String email,
             Long courseId,
             CourseReqDTO.CourseDateRequestDTO travelPeriod
    );
}
