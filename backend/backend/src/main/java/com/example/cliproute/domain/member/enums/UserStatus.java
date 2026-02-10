package com.example.cliproute.domain.member.enums;

public enum UserStatus {
    ACTIVE,     // 정상 활동 중인 유저
    INACTIVE,   // 휴면 계정 (장기 미접속)
    SUSPENDED,  // 정지 계정 (신고나 운영 정책 위반)
    DELETED     // 탈퇴한 유저 (Soft Delete)
}
