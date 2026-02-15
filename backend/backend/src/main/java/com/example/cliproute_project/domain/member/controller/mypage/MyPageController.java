package com.example.cliproute_project.domain.member.controller.mypage;

import com.example.cliproute_project.domain.auth.util.JwtUtil;
import com.example.cliproute_project.domain.member.dto.req.ProfileUpdateReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MyPageResDTO;
import com.example.cliproute_project.domain.member.exception.code.MemberSuccessCode;
import com.example.cliproute_project.domain.member.service.mypage.MyPageService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/members")
@RequiredArgsConstructor
public class MyPageController {
    private final MyPageService myPageService;
    private final JwtUtil jwtUtil;

    @GetMapping("/me")
    public ApiResponse<MyPageResDTO> getMyPage(@RequestHeader("Authorization") String token) {
        String email = jwtUtil.getUserInfoFromToken(token.substring(7));
        MyPageResDTO response = myPageService.getMyInfo(email);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MEMBER_INFO_FETCH_SUCCESS,
                response
        );
    }

    @PatchMapping("/me")
    public ApiResponse<MyPageResDTO> updateProfile(
            @RequestHeader("Authorization") String token,
            @RequestBody ProfileUpdateReqDTO request) {

        String email = jwtUtil.getUserInfoFromToken(token.substring(7));

        MyPageResDTO result = myPageService.updateProfile(email, request);

        return ApiResponse.onSuccess(
                MemberSuccessCode.MEMBER_UPDATE_SUCCESS,
                result
        );
    }

//    @PostMapping("/logout")
//    public ResponseEntity<String> logout() {
//        return ResponseEntity.ok()
//                .header("Set-Cookie", "accessToken=; Max-Age=0; Path=/; HttpOnly")
//                .body("로그아웃 되었습니다. 저장된 토큰을 삭제해 주세요.");
//    }
    @PostMapping("/logout")
    public ResponseEntity<String> logout() {
        return ResponseEntity.ok("로그아웃 완료");
    }

    @DeleteMapping("/me")
    public ResponseEntity<String> withdraw(@RequestHeader("Authorization") String token) {
        String email = jwtUtil.getEmailFromHeader(token);
        myPageService.withdraw(email);
        return ResponseEntity.ok("회원 탈퇴 완료");
    }
}
