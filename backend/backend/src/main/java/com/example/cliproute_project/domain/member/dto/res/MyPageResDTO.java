package com.example.cliproute_project.domain.member.dto.res;

import lombok.Builder;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Builder
public class MyPageResDTO {
    private String email;
    private String nickname;
    private String gender;
    private String ageRange;
}