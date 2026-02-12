package com.example.cliproute_project.domain.course.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
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
            "Invalid course id."
    ),

    INVALID_SORT_CONDITION(
            HttpStatus.BAD_REQUEST,
            "COURSE400_2",
            "Invalid sort condition."
    ),

    INVALID_PAGING_CONDITION(
            HttpStatus.BAD_REQUEST,
            "COURSE400_3",
            "Invalid paging condition."
    ),
    /* ===============================
     * 403 / 401 (authentication / authorization)
     * =============================== */

    COURSE_ACCESS_DENIED(
            HttpStatus.FORBIDDEN,
            "COURSE403_1",
            "Access denied for this course."
    ),
    /* ===============================
     * 404 NOT FOUND
     * =============================== */

    COURSE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_1",
            "Course not found."
    ),

    ORIGINAL_COURSE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_2",
            "Original course not found."
    ),

    COURSE_REGION_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_3",
            "Course region not found."
    ),

    COURSE_VIDEO_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "COURSE404_4",
            "Course video not found."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
