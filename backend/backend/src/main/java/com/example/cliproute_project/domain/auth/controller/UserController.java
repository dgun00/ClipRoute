package com.example.cliproute_project.domain.auth.controller;

import com.example.cliproute_project.domain.auth.dto.req.LoginRequestDto;
import com.example.cliproute_project.domain.auth.dto.req.SignUpRequestDto;
import com.example.cliproute_project.domain.auth.service.UserService;
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
        System.out.println("로그인 요청 들어옴");

        try {
            String token = userService.login(loginDto);
            System.out.println("\n================ [JWT TOKEN 발급] ================");
            System.out.println("Bearer " + token);
            System.out.println("==================================================\n");
            return ResponseEntity.ok()

                    .header("Authorization", "Bearer " + token)
                    .body("로그인 성공!");
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }
}