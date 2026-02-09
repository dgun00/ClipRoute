package com.example.cliproute_project.domain.course.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum CourseSuccessCode implements BaseSuccessCode {
    /* ===============================
     * 200 OK
     * =============================== */

    COURSE_LIST_FETCH_SUCCESS(
            HttpStatus.OK,
            "COURSE200_1",
            "코스 목록 조회에 성공했습니다."
    ),


    COURSE_DETAIL_FETCH_SUCCESS(
            HttpStatus.OK,
            "COURSE200_3",
            "코스 상세 조회에 성공했습니다."
    ),

    /* ===============================
     * 201 CREATED
     * =============================== */

    COURSE_SCRAP_SUCCESS(
            HttpStatus.CREATED,
            "COURSE201_1",
            "코스 스크랩에 성공했습니다."
    ),

    /* ===============================
     * 204 NO CONTENT
     * =============================== */

    COURSE_SCRAP_CANCEL_SUCCESS(
            HttpStatus.NO_CONTENT,
            "COURSE204_1",
            "코스 스크랩을 취소했습니다."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;

}
