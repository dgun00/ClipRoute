package com.example.cliproute.domain.member.controller.command;

import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.exception.code.MemberSuccessCode;
import com.example.cliproute_project.domain.member.service.command.MemberCommandService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/members/me/courses")
@Tag(name = "MyCourse", description = "My course APIs")
public class MemberCommandController implements MemberCommandControllerDocs {

    private final MemberCommandService memberCommandService;

    // [8번 API]
    @DeleteMapping("/{courseId}")
    public ApiResponse<MemberResDTO.MyCourseDeleteResultDTO> deleteMyCourse(
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId,
            @PathVariable Long courseId
    ) {
        MemberResDTO.MyCourseDeleteResultDTO response = memberCommandService.deleteMyCourse(memberId, courseId);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_DELETE_SUCCESS,
                response
        );
    }

    // [10 API]
    @PatchMapping("/{courseId}")
    public ApiResponse<MemberResDTO.MyCourseDetailDTO> editMyCourseDetail(
            @RequestHeader(value = "X-MEMBER-ID", required = false) Long memberId,
            @PathVariable Long courseId,
            @RequestBody MemberReqDTO.MyCourseDetailEditDTO request
    ) {
        MemberResDTO.MyCourseDetailDTO response = memberCommandService.editMyCourseDetail(memberId, courseId, request);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_DETAIL_EDIT_SUCCESS,
                response
        );
    }
}
