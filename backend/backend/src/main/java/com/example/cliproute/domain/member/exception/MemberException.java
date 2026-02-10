package com.example.cliproute.domain.member.exception;

import com.example.cliproute_project.global.apiPayload.code.BaseErrorCode;
import com.example.cliproute_project.global.apiPayload.exception.GeneralException;

public class MemberException extends GeneralException {
    public MemberException(BaseErrorCode code) {
        super(code);
    }
}
