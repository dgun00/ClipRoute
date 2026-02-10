package com.example.cliproute.domain.member.exception;

import com.example.cliproute.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute.global.apiPayload.exception.GeneralException;

public class MemberException extends GeneralException {
    public MemberException(BaseErrorCode code) {
        super(code);
    }
}
