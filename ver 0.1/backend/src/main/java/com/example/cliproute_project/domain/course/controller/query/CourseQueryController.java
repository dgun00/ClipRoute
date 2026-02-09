package com.example.cliproute_project.domain.course.controller.query;

import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.exception.code.CourseSuccessCode;
import com.example.cliproute_project.domain.course.service.query.CourseQueryService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import com.example.cliproute_project.global.apiPayload.code.GeneralSuccessCode;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.constraints.Positive;
import lombok.RequiredArgsConstructor;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/courses")
@RequiredArgsConstructor
@Validated
//@CrossOrigin(origins = "*")
@Tag(name = "Course", description = "코스 관련 API")
public class CourseQueryController implements CourseQueryControllerDocs {

    private final CourseQueryService courseQueryService;

    // [2 API]
    @GetMapping("")
    public ApiResponse<CourseResDTO.CoursePublicListDTO> getCourseList(
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) Integer travelDays,
            @RequestParam(defaultValue = "random") String sort,
            @RequestParam(required = false) Long seed,
            @RequestParam(required = false) Boolean isRep,
            @RequestParam(required = false) Long lastCourseId, // 커서: 마지막 코스 ID
            @RequestParam(required = false) Integer lastValue, // 커서: 마지막 정렬 기준 값 (조회수 등) -> 현재 사용 x
            @RequestParam(required = false, defaultValue = "5") int pageSize
    ) {
        CourseResDTO.CoursePublicListDTO response = courseQueryService.getCourseList(
                regionId, travelDays, sort, seed, isRep, lastCourseId, lastValue, pageSize
        );

        return ApiResponse.onSuccess(
                CourseSuccessCode.COURSE_LIST_FETCH_SUCCESS,
                response);
    }
    // [3 API]
    @GetMapping("/recommendation")
    public ApiResponse<CourseResDTO.CoursePublicListDTO> getCoursesWithRecommendation(
            @RequestParam Long regionId,
            @RequestParam Integer travelDays,
            @RequestParam(defaultValue = "random") String sort, // 정렬 기준값
            @RequestParam(required = false) Long seed,
            @RequestParam(defaultValue = "0") int page, // 현재 위치
            @RequestParam(defaultValue = "5") int pageSize // 페이지 크기
    ) {
        CourseResDTO.CoursePublicListDTO response = courseQueryService.getCourseListWithRecommendation(
                regionId, travelDays, sort, seed, page, pageSize
        );

        return ApiResponse.onSuccess(
                CourseSuccessCode.COURSE_LIST_FETCH_SUCCESS,
                response
        );
    }

    // [4 API]
    @GetMapping("/{courseId}")
    public ApiResponse<CourseResDTO.CourseDetailDTO> getCourseDetail(
            @PathVariable @Positive Long courseId,
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId
    ) {
        CourseResDTO.CourseDetailDTO response = courseQueryService.getCourseDetail(courseId, memberId);
        return ApiResponse.onSuccess(
                CourseSuccessCode.COURSE_DETAIL_FETCH_SUCCESS,
                response);
    }

}
