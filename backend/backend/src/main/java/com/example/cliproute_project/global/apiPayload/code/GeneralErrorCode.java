package com.example.cliproute_project.global.apiPayload.code;


import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum GeneralErrorCode implements BaseErrorCode{

    BAD_REQUEST(HttpStatus.BAD_REQUEST,
            "COMMON400_1",
            "Invalid request."),
    UNAUTHORIZED(HttpStatus.UNAUTHORIZED,
            "AUTH401_1",
            "Authentication required."),
    FORBIDDEN(HttpStatus.FORBIDDEN,
            "AUTH403_1",
            "Access denied."),
    NOT_FOUND(HttpStatus.NOT_FOUND,
            "COMMON404_1",
            "Resource not found."),
    INTERNAL_SERVER_ERROR(HttpStatus.INTERNAL_SERVER_ERROR,
            "COMMON500_1",
            "Internal server error."),
    ;

    private final HttpStatus status;
    private final String code;
    private final String message;
}
