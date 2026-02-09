package com.example.cliproute_project.domain.region.exception;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute_project.global.apiPayload.exception.GeneralException;

public class RegionException extends GeneralException {
    public RegionException(BaseErrorCode code) {
        super(code);
    }
}
