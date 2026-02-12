package com.example.cliproute.domain.course.controller.command;

import com.example.cliproute.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute.domain.course.dto.res.CourseResDTO;
import com.example.cliproute.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;


public interface CourseCommandControllerDocs {
    // [5번 API]
    @Operation(
            summary = "[5번 API] 스크랩",
            description = " (비로그인/로그인이고 내 코스 아닌 코스 상세보기시) 스크랩 버튼 눌럿을때 동작 "
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger에 response 형태 보여주기용"),

            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE201_1", description = "코스 스크랩에 성공했습니다."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "COURSE204_1", description = "코스 스크랩을 취소했습니다."),

    })
    ApiResponse<CourseResDTO.ScrapResultDTO> scrapCourse(
             Long memberId,
             Long courseId,
             CourseReqDTO.CourseDateRequestDTO travelPeriod
    );
}
