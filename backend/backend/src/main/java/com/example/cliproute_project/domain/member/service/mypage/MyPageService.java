package com.example.cliproute_project.domain.member.service.mypage;
import com.example.cliproute_project.domain.auth.entity.User;
import com.example.cliproute_project.domain.auth.enums.AgeRange;
import com.example.cliproute_project.domain.auth.enums.Gender;
import com.example.cliproute_project.domain.auth.enums.MemberStatus;
import com.example.cliproute_project.domain.auth.repository.UserRepository;
import com.example.cliproute_project.domain.member.dto.req.ProfileUpdateReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MyPageResDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class MyPageService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @Transactional(readOnly = true)
    public MyPageResDTO getMyInfo(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

        return MyPageResDTO.builder()
                .email(user.getEmail())
                .nickname(user.getNickname())
                .gender(user.getGender().name())
                .ageRange(user.getAgeRange().name())
                .build();
    }

    @Transactional
    public void updateProfile(String currentEmail, ProfileUpdateReqDTO request) {
        User user = userRepository.findByEmail(currentEmail)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));

        // 비밀번호 수정
        if (request.getPassword() != null && !request.getPassword().isEmpty()) {
            String encodedPassword = passwordEncoder.encode(request.getPassword());
            user.updatePassword(encodedPassword);
        }

        // 프로필 정보 업데이트
        user.updateProfile(
                request.getNickname(),
                request.getEmail(),
                request.getGender() != null ? Gender.valueOf(request.getGender()) : null,
                request.getAgeRange() != null ? AgeRange.valueOf(request.getAgeRange()) : null
        );
    }
    @Transactional
    public void withdraw(String email) {
        User user = findUserByEmail(email);
        user.updateStatus(MemberStatus.DELETED);
    }

    private User findUserByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new IllegalArgumentException("사용자를 찾을 수 없습니다."));
    }
}
