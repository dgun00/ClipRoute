package com.example.cliproute_project.domain.member.dto.req;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@NoArgsConstructor
public class ProfileUpdateReqDTO {
    private String nickname;
    private String email;
    private String password;
    private String gender;
    private String ageRange;
}
