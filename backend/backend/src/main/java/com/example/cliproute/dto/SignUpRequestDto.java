package com.example.cliproute.dto;

import com.example.cliproute.entity.AgeRange;
import com.example.cliproute.entity.Gender;
import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class SignUpRequestDto {

    @NotBlank(message = "올바른 이메일 형식을 입력해 주세요")
    @Email(regexp = "^[a-z0-9._-]+@[a-z0-9.-]+\\.[a-z]{2,}$", message = "올바른 이메일 형식을 입력해 주세요")
    private String email;

    @NotBlank(message = "비밀번호는 8자 이상 입력해주세요")
    @Size(min = 8, max = 20, message = "비밀번호는 8자 이상 입력해주세요")
    @Pattern(regexp = "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d!@#$%^&*]*$",
            message = "비밀번호는 영문과 숫자를 포함해야 합니다.")
    private String password;

    @NotBlank(message = "닉네임은 2~10자 이내로 입력해 주세요")
    @Size(min = 2, max = 10, message = "닉네임은 2~10자 이내로 입력해 주세요")
    @Pattern(regexp = "^[가-힣a-zA-Z0-9\\s]*$", message = "특수문자는 사용할 수 없습니다.")
    private String nickname;


    @NotNull(message = "성별을 선택해 주세요")
    private Gender gender;

    @NotNull(message = "연령대를 선택해 주세요")
    private AgeRange ageRange;
}