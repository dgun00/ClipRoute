package com.example.cliproute.domain.course.exception;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute.global.apiPayload.exception.GeneralException;

public class CourseException extends GeneralException {
    public CourseException(BaseErrorCode code) {
        super(code);
    }
}
