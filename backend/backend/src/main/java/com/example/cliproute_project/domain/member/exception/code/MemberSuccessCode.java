package com.example.cliproute_project.domain.member.exception.code;

import com.example.cliproute_project.global.apiPayload.code.BaseSuccessCode;
import lombok.AllArgsConstructor;
import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
@AllArgsConstructor
public enum MemberSuccessCode implements BaseSuccessCode {
    MY_COURSE_FILTER_OPTIONS_FETCH_SUCCESS(
            HttpStatus.OK,
            "MYCOURSE200_1",
            "My course filter options fetched successfully."
    ),
    MY_COURSE_LIST_FETCH_SUCCESS(
            HttpStatus.OK,
            "MYCOURSE200_2",
            "My course list fetched successfully."
    ),
    MY_COURSE_DETAIL_FETCH_SUCCESS(
            HttpStatus.OK,
            "MYCOURSE200_3",
            "My course detail fetched successfully."
    ),
    MY_COURSE_DELETE_SUCCESS(
            HttpStatus.OK,
            "MYCOURSE200_4",
            "My course deleted successfully."
    ),
    MY_COURSE_DETAIL_EDIT_SUCCESS(
            HttpStatus.OK,
            "MYCOURSE200_5",
            "My course detail edited successfully."
    ), 


    MEMBER_UPDATE_SUCCESS(
            HttpStatus.OK,
            "MEMBER200_1",
            "Member profile updated successfully."
    ),
    MEMBER_INFO_FETCH_SUCCESS(
            HttpStatus.OK,
            "MEMBER200_2",
            "Member info fetched successfully."
    );

    private final HttpStatus status;
    private final String code;
    private final String message;
}