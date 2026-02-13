package com.example.cliproute_project.global.apiPayload.code;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum GeneralSuccessCode implements BaseSuccessCode {

    OK(HttpStatus.OK,
            "COMMON200",
            "Request processed successfully."),

    CREATED(HttpStatus.CREATED,
            "COMMON201",
            "Resource created successfully."),

    NO_CONTENT(HttpStatus.NO_CONTENT,
            "COMMON204",
            "Request processed successfully, but no response content."),
    ;

    private final HttpStatus status;
    private final String code;
    private final String message;
}
