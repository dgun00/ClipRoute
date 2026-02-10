package com.example.cliproute.domain.member.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum MemberCourseErrorCode implements BaseErrorCode {
    /* ===============================
     * 400 BAD REQUEST
     * =============================== */

    INVALID_COURSE_ID(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_1",
            "Invalid course id."
    ),

    INVALID_REGION_ID(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_2",
            "Invalid region id."
    ),

    INVALID_TRAVEL_DAYS(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_3",
            "Invalid travel days."
    ),

    // [10 API]
    INVALID_DATE_RANGE(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_4",
            "Invalid date range."
    ),

    // [10 API]
    DUPLICATE_VISIT_DAY(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_5",
            "Duplicate visit day."
    ),

    // [10 API]
    INVALID_VISIT_DAY_SEQUENCE(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_6",
            "Invalid visit day sequence."
    ),

    // [10 API]
    INVALID_REQUEST(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_7",
            "Invalid request."
    ),

    // [10 API]
    COURSE_ALREADY_DELETED(
            HttpStatus.BAD_REQUEST,
            "MEMBER_COURSE400_8",
            "Course already deleted."
    ),

    /* ===============================
     * 403 FORBIDDEN
     * =============================== */

    MY_COURSE_ACCESS_DENIED(
            HttpStatus.FORBIDDEN,
            "MEMBER_COURSE403_1",
            "Access denied for this course."
    ),

    // [10 API]
    COURSE_NOT_EDITABLE(
            HttpStatus.FORBIDDEN,
            "MEMBER_COURSE403_2",
            "Course is not editable."
    ),

    /* ===============================
     * 404 NOT FOUND
     * =============================== */

    MY_COURSE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "MEMBER_COURSE404_1",
            "My course not found."
    ),

    // [10 API]
    COURSE_PLACE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "MEMBER_COURSE404_2",
            "Course place not found."
    ),

    // [10 API]
    PLACE_NOT_FOUND(
            HttpStatus.NOT_FOUND,
            "MEMBER_COURSE404_3",
            "Place not found."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}
