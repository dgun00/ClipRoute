package com.example.cliproute.domain.member.controller.mypage;

import com.example.cliproute.domain.auth.util.JwtUtil;
import com.example.cliproute.domain.member.dto.req.ProfileUpdateReqDTO;
import com.example.cliproute.domain.member.dto.res.MyPageResDTO;
import com.example.cliproute.domain.member.service.mypage.MyPageService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/members")
@RequiredArgsConstructor
public class MyPageController {
    private final MyPageService myPageService;
    private final JwtUtil jwtUtil; // 토큰 해석을 위해 주입

    @GetMapping("/me")
    public ResponseEntity<MyPageResDTO> getMyPage(@RequestHeader("Authorization") String token) {
        // "Bearer " 접두어 제거 후 이메일 추출
        String jwt = token.substring(7);
        String email = jwtUtil.getUserInfoFromToken(jwt);

        return ResponseEntity.ok(myPageService.getMyInfo(email));
    }

    @PatchMapping("/me")
    public ResponseEntity<String> updateProfile(
            @RequestHeader("Authorization") String token,
            @RequestBody ProfileUpdateReqDTO request) {

        String jwt = token.substring(7);
        String email = jwtUtil.getUserInfoFromToken(jwt);

        myPageService.updateProfile(email, request);
        return ResponseEntity.ok("프로필 정보가 수정되었습니다.");
    }

//    @PostMapping("/logout")
//    public ResponseEntity<String> logout() {
//        return ResponseEntity.ok()
//                .header("Set-Cookie", "accessToken=; Max-Age=0; Path=/; HttpOnly")
//                .body("로그아웃 되었습니다. 저장된 토큰을 삭제해 주세요.");
//    }
    @PostMapping("/logout")
    public ResponseEntity<String> logout() {
        System.out.println("=== 로그아웃 컨트롤러 진입 성공! ==="); // 이 줄이 찍히는지 보세요
        return ResponseEntity.ok("로그아웃 완료");
    }

    @DeleteMapping("/me")
    public ResponseEntity<String> withdraw(@RequestHeader("Authorization") String token) {
        String email = jwtUtil.getEmailFromHeader(token);
        myPageService.withdraw(email);
        return ResponseEntity.ok("회원 탈퇴 완료");
    }
}
