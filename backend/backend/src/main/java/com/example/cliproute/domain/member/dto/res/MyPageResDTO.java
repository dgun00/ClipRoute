package com.example.cliproute.domain.member.dto.res;

import lombok.Builder;
import lombok.Getter;

@Getter
@Builder
public class MyPageResDTO {
    private String email;
    private String nickname;
    private String gender;
    private String ageRange;
}
