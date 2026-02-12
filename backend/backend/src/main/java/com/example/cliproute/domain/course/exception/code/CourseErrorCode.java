package com.example.cliproute.domain.course.exception.code;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum CourseErrorCode implements BaseErrorCode {
    /* ===============================
     * 400 BAD REQUEST
     * =============================== */

    INVALID_COURSE_ID(
            HttpStatus.BAD_REQUEST,
            "COURSE400_1",
            "유효하지 않은 코스 ID입니다."
    ),

    INVALID_SORT_CONDITION(
            HttpStatus.BAD_REQUEST,
            "COURSE400_2",
            "유효하지 않은 정렬 조건입니다."
    ),

    INVALID_PAGING_CONDITION(
            HttpStatus.BAD_REQUEST,
            "COURSE400_3",
            "페이지 조건이 올바르지 않습니다."
    ),
    /* ===============================
     * 403 / 401 (확장 대비)
     * =============================== */

    COURSE_ACCESS_DENIED(
            HttpStatus.FORBIDDEN,
            "COURSE403_1",
            "해당 코스에 대한 접근 권한이 없습니다."
    ),
    /* ===============================
     * 404 NOT FOUND
     * =============================== */

    COURSE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_1",
                    "코스를 찾을 수 없습니다."
    ),

    ORIGINAL_COURSE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_2",
                    "원본 코스를 찾을 수 없습니다."
    ),

    COURSE_REGION_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_3",
                    "코스의 지역 정보를 찾을 수 없습니다."
    ),

    COURSE_VIDEO_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_4",
                    "코스의 영상 정보를 찾을 수 없습니다."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
