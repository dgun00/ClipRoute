package com.example.cliproute_project.domain.course.controller.command;

import com.example.cliproute_project.domain.auth.util.JwtUtil;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute_project.domain.course.exception.code.CourseSuccessCode;
import com.example.cliproute_project.domain.course.service.command.CourseCommandService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;



@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/courses")
@Tag(name = "Course", description = "Course APIs")
public class CourseCommandController implements CourseCommandControllerDocs {

    private final CourseCommandService courseCommandService;
    private final JwtUtil jwtUtil;
    // [5번 API] 코스 스크랩
    // * 여행 시작일, 끝나는일 넣어서 저장하려면 프론트에서 두 데이터를 받아야함
    @PostMapping("/{courseId}/scrap")
    public ApiResponse<CourseResDTO.ScrapResultDTO> scrapCourse(
            @RequestHeader("Authorization") String token,
            @PathVariable Long courseId,
            @RequestBody (required = false)CourseReqDTO.CourseDateRequestDTO travelPeriod
            ) {
        String jwt = token.substring(7);
        String email = jwtUtil.getUserInfoFromToken(jwt);

        CourseResDTO.ScrapResultDTO response = courseCommandService.scrapCourse(email, courseId, travelPeriod);
        return ApiResponse.onSuccess(
                CourseSuccessCode.COURSE_SCRAP_SUCCESS,
                response);
    }
}
