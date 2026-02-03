package com.example.cliproute.controller;

import com.example.cliproute.dto.LoginRequestDto;
import com.example.cliproute.dto.SignUpRequestDto;
import com.example.cliproute.service.UserService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/signup")
    public ResponseEntity<String> signUp(@Valid @RequestBody SignUpRequestDto requestDto) {
        try {
            userService.signUp(requestDto);
            return ResponseEntity.ok("회원가입이 완료되었습니다.");
        } catch (IllegalArgumentException e) {
            // 중복 오류 등 비즈니스 로직 예외 처리
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
    @PostMapping("/login")
    public ResponseEntity<String> login(@Valid @RequestBody LoginRequestDto loginDto) {
        // System.out.println 오타 수정 (pringln -> println)
        System.out.println("로그인 요청 들어옴");

        try {
            // 1. 서비스에서 토큰을 생성해서 받아옵니다.
            String token = userService.login(loginDto);
            System.out.println("로그인 성공, 토큰 발급 완료");
            // 2. 헤더에 담아서 보냅니다 (Authorization 헤더 사용)
            // 관례상 JWT는 앞에 "Bearer "를 붙여주는 것이 좋습니다.
            return ResponseEntity.ok()
                    .header("Authorization", "Bearer " + token)
                    .body("로그인 성공!");
        } catch (IllegalArgumentException e) {
            System.out.println("로그인 실패: " + e.getMessage());
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}