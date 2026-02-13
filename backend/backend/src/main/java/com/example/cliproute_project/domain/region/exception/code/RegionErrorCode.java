package com.example.cliproute_project.domain.region.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum RegionErrorCode implements BaseErrorCode {
    /* ===============================
     * 400 BAD REQUEST
     * =============================== */

    INVALID_REGION_ID(
            HttpStatus.BAD_REQUEST,
            "REGION400_1",
            "Invalid region id."
    ),

    INVALID_REGION_CONDITION(
            HttpStatus.BAD_REQUEST,
            "REGION400_2",
            "Invalid region query condition."
    ),
    /* ===============================
     * 404 NOT FOUND
     * =============================== */

    REGION_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "REGION404_1",
            "Region not found."
    ),

    REGION_EMPTY(
            HttpStatus.NOT_FOUND,
            "REGION404_2",
            "No regions available."
    );


    private final HttpStatus status;
    private final String code;
    private final String message;
}
