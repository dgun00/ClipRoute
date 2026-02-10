package com.example.cliproute.domain.place.exception.code;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum PlaceErrorCode implements BaseErrorCode {
    /* ===============================
     * 400 BAD REQUEST
     * =============================== */

    PLACE_INVALID_VIEWPORT(
            HttpStatus.BAD_REQUEST,
            "PLACE400_1",
            "Invalid viewport parameters."
    ),

    PLACE_INVALID_VIEWPORT_RANGE(
            HttpStatus.BAD_REQUEST,
            "PLACE400_2",
            "Invalid viewport range."
    ),

    PLACE_OUT_OF_SERVICE_AREA(
            HttpStatus.BAD_REQUEST,
            "PLACE400_3",
            "Viewport is out of service area."
    ),

    PLACE_INVALID_PAGE(
            HttpStatus.BAD_REQUEST,
            "PLACE400_4",
            "Invalid page condition."
    ),

    PLACE_INVALID_CATEGORY(
            HttpStatus.BAD_REQUEST,
            "PLACE400_5",
            "Invalid category."
    ),

    PLACE_NO_SEARCH_CONDITION(
            HttpStatus.BAD_REQUEST,
            "PLACE400_6",
            "No search condition."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
