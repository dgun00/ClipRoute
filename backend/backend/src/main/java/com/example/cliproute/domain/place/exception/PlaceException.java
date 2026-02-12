package com.example.cliproute.domain.place.exception;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute.global.apiPayload.exception.GeneralException;

public class PlaceException extends GeneralException {
    public PlaceException(BaseErrorCode code) {
        super(code);
    }
}
