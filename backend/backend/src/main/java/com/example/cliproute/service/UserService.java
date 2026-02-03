package com.example.cliproute.service;

import com.example.cliproute.dto.LoginRequestDto;
import com.example.cliproute.entity.*;
import com.example.cliproute.dto.SignUpRequestDto;
import com.example.cliproute.repository.UserRepository;
import com.example.cliproute.util.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Transactional
    public void signUp(SignUpRequestDto requestDto) {
        String email = requestDto.getEmail().toLowerCase();

        userRepository.findByEmail(email).ifPresent(user -> {
            throw new IllegalArgumentException("이미 가입된 이메일 입니다. 로그인을 진행해 주세요");
        });

        String encodedPassword = passwordEncoder.encode(requestDto.getPassword());

        User user = User.builder()
                .email(email)
                .password(encodedPassword)
                .nickname(requestDto.getNickname())
                .ageRange(requestDto.getAgeRange())
                .gender(requestDto.getGender())
                .role(Role.USER)
                .status(MemberStatus.ACTIVE)
                .build();

        userRepository.save(user);
    }
    @Transactional(readOnly = true)
    public String login(LoginRequestDto loginDto) {
        // 1. 이메일 확인
        User user = userRepository.findByEmail(loginDto.getEmail().toLowerCase())
                .orElseThrow(() -> new IllegalArgumentException("가입되지 않은 이메일입니다."));

        // 2. 비밀번호 확인 (암호화된 비번과 입력받은 비번 비교)
        if (!passwordEncoder.matches(loginDto.getPassword(), user.getPassword())) {
            throw new IllegalArgumentException("비밀번호가 일치하지 않습니다.");
        }

        // 3. 로그인 성공! (일단은 성공 메시지만 리턴, 나중에 여기서 JWT 토큰을 만듬)
        return jwtUtil.createToken(user.getEmail());
    }
}