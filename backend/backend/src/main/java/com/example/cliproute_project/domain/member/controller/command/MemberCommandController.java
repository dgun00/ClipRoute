package com.example.cliproute_project.domain.member.controller.command;

import com.example.cliproute_project.domain.auth.util.JwtUtil;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.exception.code.MemberSuccessCode;
import com.example.cliproute_project.domain.member.service.command.MemberCommandService;
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
    private final JwtUtil jwtUtil;

    // [8번 API] 내 코스 삭제
    @DeleteMapping("/{courseId}")
    public ApiResponse<MemberResDTO.MyCourseDeleteResultDTO> deleteMyCourse(
            @RequestHeader("Authorization") String token,
            @PathVariable Long courseId
    ) {
        String email = jwtUtil.getUserInfoFromToken(token.substring(7));
        MemberResDTO.MyCourseDeleteResultDTO response = memberCommandService.deleteMyCourse(email, courseId);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_DELETE_SUCCESS,
                response
        );
    }

    // [10 API] 내 코스 수정
    @PatchMapping("/{courseId}")
    public ApiResponse<MemberResDTO.MyCourseDetailDTO> editMyCourseDetail(
            @RequestHeader("Authorization") String token,
            @PathVariable Long courseId,
            @RequestBody MemberReqDTO.MyCourseDetailEditDTO request
    ) {
        String email = jwtUtil.getUserInfoFromToken(token.substring(7));
        MemberResDTO.MyCourseDetailDTO response = memberCommandService.editMyCourseDetail(email, courseId, request);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MY_COURSE_DETAIL_EDIT_SUCCESS,
                response
        );
    }
}
