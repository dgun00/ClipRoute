package com.example.cliproute.domain.region.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum RegionSuccessCode implements BaseSuccessCode {
    /* ===============================
     * 200 OK
     * =============================== */

    REGION_LIST_FETCH_SUCCESS(
            HttpStatus.OK,
            "REGION200_1",
            "지역 목록 조회에 성공했습니다."
    );


    private final HttpStatus status;
    private final String code;
    private final String message;

}