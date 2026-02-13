package com.example.cliproute_project.domain.member.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum MemberErrorCode implements BaseErrorCode {
    /* ===============================
     * 400 BAD REQUEST
     * =============================== */

    INVALID_MEMBER_ID(
            HttpStatus.BAD_REQUEST,
            "MEMBER400_1",
            "Invalid member id."
    ),

    /* ===============================
     * 401 UNAUTHORIZED
     * =============================== */
    MEMBER_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "MEMBER404_1",
            "사용자를 찾을 수 없습니다."),

    UNAUTHORIZED(
            HttpStatus.UNAUTHORIZED,
            "MEMBER401_1",
            "Authentication required."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
