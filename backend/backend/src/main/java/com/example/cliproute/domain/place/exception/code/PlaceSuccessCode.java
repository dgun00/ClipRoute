package com.example.cliproute.domain.place.exception.code;

import com.example.cliproute.global.apiPayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum PlaceSuccessCode implements BaseSuccessCode {
    /* ===============================
     * 200 OK
     * =============================== */

    PLACE_SEARCH_SUCCESS(
            HttpStatus.OK,
            "PLACE200_1",
            "장소 조회에 성공했습니다."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
