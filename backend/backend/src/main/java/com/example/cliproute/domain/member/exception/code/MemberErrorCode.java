package com.example.cliproute.domain.member.exception.code;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
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
    UNAUTHORIZED(
            HttpStatus.UNAUTHORIZED,
            "MEMBER401_1",
            "Authentication required."
    ),

    /* ===============================
     * 404 NOT FOUND
     * =============================== */
    // 이 부분을 추가하세요!
    MEMBER_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "MEMBER404_1",
            "Member not found."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
