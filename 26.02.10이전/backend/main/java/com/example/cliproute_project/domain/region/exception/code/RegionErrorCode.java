package com.example.cliproute_project.domain.region.exception.code;

import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum RegionErrorCode {
    /* ===============================
     * 400 BAD REQUEST
     * =============================== */

    INVALID_REGION_ID(
            HttpStatus.BAD_REQUEST,
            "REGION400_1",
            "유효하지 않은 지역 ID입니다."
    ),

    INVALID_REGION_CONDITION(
            HttpStatus.BAD_REQUEST,
            "REGION400_2",
            "유효하지 않은 지역 조회 조건입니다."
    ),
    /* ===============================
     * 404 NOT FOUND
     * =============================== */

    REGION_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "REGION404_1",
            "지역 정보를 찾을 수 없습니다."
    ),

    REGION_EMPTY(
            HttpStatus.NOT_FOUND,
            "REGION404_2",
            "등록된 지역 정보가 없습니다."
    );


    private final HttpStatus status;
    private final String code;
    private final String message;
}
