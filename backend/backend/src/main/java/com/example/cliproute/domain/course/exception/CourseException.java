package com.example.cliproute.domain.course.exception;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute_project.global.apiPayload.exception.GeneralException;

public class CourseException extends GeneralException {
    public CourseException(BaseErrorCode code) {
        super(code);
    }
}
