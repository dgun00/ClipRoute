package com.example.cliproute.domain.region.exception;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute.global.apiPayload.exception.GeneralException;

public class RegionException extends GeneralException {
    public RegionException(BaseErrorCode code) {
        super(code);
    }
}
