package com.example.cliproute.global.apiPayload.code;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum GeneralSuccessCode implements BaseSuccessCode {

    // 200 OK: 요청 성공, 데이터 반환이 있을 때 사용
    OK(HttpStatus.OK,
            "COMMON200",
            "요청이 성공적으로 처리되었습니다."),

    // 201 CREATED: 새로운 리소스 생성 성공 시 사용
    CREATED(HttpStatus.CREATED,
            "COMMON201",
            "리소스 생성에 성공했습니다."),

    // 204 NO_CONTENT: 요청 성공했으나, 응답 본문에 보낼 데이터가 없을 때 (주로 삭제, 업데이트 후)
    NO_CONTENT(HttpStatus.NO_CONTENT,
            "COMMON204",
            "요청이 성공적으로 처리되었으나, 응답 데이터가 없습니다."),
    ;

    private final HttpStatus status;
    private final String code;
    private final String message;
}