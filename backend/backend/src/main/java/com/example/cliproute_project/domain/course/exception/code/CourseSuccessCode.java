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
            "Course list fetched successfully."
    ),


    COURSE_DETAIL_FETCH_SUCCESS(
            HttpStatus.OK,
            "COURSE200_3",
            "Course detail fetched successfully."
    ),

    /* ===============================
     * 201 CREATED
     * =============================== */

    COURSE_SCRAP_SUCCESS(
            HttpStatus.CREATED,
            "COURSE201_1",
            "Course scrapped successfully."
    ),

    /* ===============================
     * 204 NO CONTENT
     * =============================== */

    COURSE_SCRAP_CANCEL_SUCCESS(
            HttpStatus.NO_CONTENT,
            "COURSE204_1",
            "Course scrap canceled."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;

}
