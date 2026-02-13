package com.example.cliproute_project.domain.place.exception;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute_project.global.apiPayload.exception.GeneralException;

public class PlaceException extends GeneralException {
    public PlaceException(BaseErrorCode code) {
        super(code);
    }
}
