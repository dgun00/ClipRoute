package com.example.cliproute.domain.member.controller.query;

import com.example.cliproute.domain.auth.util.JwtUtil;
import com.example.cliproute.domain.member.dto.res.MemberResDTO;
import com.example.cliproute.domain.member.enums.TravelStatus;
import com.example.cliproute.domain.member.exception.code.MemberSuccessCode;
import com.example.cliproute.domain.member.service.query.MemberQueryService;
import com.example.cliproute.domain.course.exception.code.CourseSuccessCode;
import com.example.cliproute.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/members/me/courses")
@Tag(name = "MyCourse", description = "My course APIs")
public class MemberQueryController implements MemberQueryControllerDocs {

    private final MemberQueryService memberQueryService;
    private final JwtUtil jwtUtil;

    // [6 API] 드롭다운 요소 fetch
    @Override
    @GetMapping("/filters")
    public ApiResponse<MemberResDTO.FilterOptionsDTO> getMyCourseFilterOptions(
            @RequestHeader("Authorization") String token, // Long memberId에서 변경
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) Integer travelDays,
            @RequestParam(required = false) TravelStatus travelStatus
    ) {
        Long memberId = memberQueryService.findIdByEmail(jwtUtil.getEmailFromHeader(token));

        MemberResDTO.FilterOptionsDTO response = memberQueryService.getMyCourseFilterOptions(
                memberId, regionId, travelDays, travelStatus
        );

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_FILTER_OPTIONS_FETCH_SUCCESS,
                response
        );
    }

    // [7 API] 내 코스 리스트 조회
    @Override
    @GetMapping
    public ApiResponse<MemberResDTO.MyCourseListDTO> getMyCourses(
            @RequestHeader("Authorization") String token, // Long memberId에서 변경
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) Integer travelDays,
            @RequestParam(required = false) TravelStatus travelStatus,
            @RequestParam(required = false) Long lastMemberCourseId,
            @RequestParam(required = false, defaultValue = "5") Integer pageSize
    ) {
        Long memberId = memberQueryService.findIdByEmail(jwtUtil.getEmailFromHeader(token));

        MemberResDTO.MyCourseListDTO response = memberQueryService.getMyCourses(
                memberId, regionId, travelDays, travelStatus, lastMemberCourseId, pageSize
        );

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_LIST_FETCH_SUCCESS,
                response
        );
    }

    // [9 API] 내 코스 상세 조회 (보기 모드)
    @Override
    @GetMapping("/{courseId}")
    public ApiResponse<MemberResDTO.MyCourseDetailDTO> getMyCourseDetail(
            @RequestHeader("Authorization") String token,
            @PathVariable Long courseId
    ) {
        // memberService 대신 memberQueryService를 사용하도록 수정
        Long memberId = memberQueryService.findIdByEmail(jwtUtil.getEmailFromHeader(token));

        MemberResDTO.MyCourseDetailDTO response = memberQueryService.getMyCourseDetail(memberId, courseId);

        return ApiResponse.onSuccess(
                CourseSuccessCode.COURSE_DETAIL_FETCH_SUCCESS,
                response
        );
    }
}