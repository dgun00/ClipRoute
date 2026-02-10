package com.example.cliproute.domain.member.entity;

import com.example.cliproute_project.domain.member.enums.*;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "MEMBERS")
public class Member extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 이메일
    @Column(nullable = false, unique = true, length = 50)
    private String email;

    // 비밀번호
    @Column(nullable = false)
    private String password; // 소셜 로그인이면 null일 수 있음

    // 닉네임
    @Column(nullable = false, unique = true, length = 20)
    private String nickname;

//    @Column(name = "profile_image_url")
//    private String profileImageUrl;

    // 성별
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Gender gender;
    
    // 연령대
    @Enumerated(EnumType.STRING)
    @Column(name = "age_range", nullable = false)
    private AgeRange ageRange;


    // 상태
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private UserStatus status;

    // 권한
    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false)
    private Role role = Role.USER;
    
    // 삭제일시
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
}