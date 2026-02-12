package com.example.cliproute_project.domain.member.controller.query;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.exception.code.MemberSuccessCode;
import com.example.cliproute_project.domain.member.service.query.MemberQueryService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/members/me/courses")
@Tag(name = "MyCourse", description = "My course APIs")
public class MemberQueryController implements MemberQueryControllerDocs {

    private final MemberQueryService memberQueryService;

    // [6 API] ?�롭?�운 ?�소 fetch
    @GetMapping("/filters")
    public ApiResponse<MemberResDTO.FilterOptionsDTO> getMyCourseFilterOptions(
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId,
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) Integer travelDays,
            @RequestParam(required = false) TravelStatus travelStatus
    ) {
        MemberResDTO.FilterOptionsDTO response = memberQueryService.getMyCourseFilterOptions(
                memberId, regionId, travelDays, travelStatus
        );

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_FILTER_OPTIONS_FETCH_SUCCESS,
                response
        );
    }
    // [7 API]  ??코스 리스??조회
    @GetMapping
    public ApiResponse<MemberResDTO.MyCourseListDTO> getMyCourses(
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId,
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) Integer travelDays,
            @RequestParam(required = false) TravelStatus travelStatus,
            @RequestParam(required = false) Long lastMemberCourseId,
            @RequestParam(required = false, defaultValue = "5") Integer pageSize
    ) {
        MemberResDTO.MyCourseListDTO response = memberQueryService.getMyCourses(
                memberId, regionId, travelDays, travelStatus, lastMemberCourseId, pageSize
        );

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_LIST_FETCH_SUCCESS,
                response
        );
    }
    // [9 API] ??코스 ?�세 조회 (보기 모드)
    @GetMapping("/{courseId}")
    public ApiResponse<MemberResDTO.MyCourseDetailDTO> getMyCourseDetail(
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId,
            @PathVariable Long courseId
    ) {
        MemberResDTO.MyCourseDetailDTO response = memberQueryService.getMyCourseDetail(memberId, courseId);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_DETAIL_FETCH_SUCCESS,
                response
        );
    }
}
