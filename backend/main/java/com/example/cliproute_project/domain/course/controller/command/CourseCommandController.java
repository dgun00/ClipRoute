package com.example.cliproute_project.domain.course.controller.command;

import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.exception.code.CourseSuccessCode;
import com.example.cliproute_project.domain.course.service.command.CourseCommandService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import com.example.cliproute_project.global.apiPayload.code.GeneralSuccessCode;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/courses")
@Tag(name = "Course", description = "코스 관련 API")
public class CourseCommandController implements CourseCommandControllerDocs {

    private final CourseCommandService courseCommandService;

    // [5번 API] 코스 스크랩
    // POST /api/v1/courses/{courseId}/scrap
    @PostMapping("/{courseId}/scrap")
    public ApiResponse<CourseResDTO.ScrapResultDTO> scrapCourse(
            // 프로젝트의 인증 Principal 타입에 맞게 바꿔야함
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId, // <-- 임시/대체안
            @PathVariable Long courseId
    ) {
        CourseResDTO.ScrapResultDTO response = courseCommandService.scrapCourse(memberId, courseId);
        return ApiResponse.onSuccess(
                CourseSuccessCode.COURSE_SCRAP_SUCCESS,
                response);
    }
}