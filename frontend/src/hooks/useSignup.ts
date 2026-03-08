import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useForm from "./useForm";
import { useAgreement } from "./useAgreement";
import { validateSignup, type SignupInformation } from "../utils/validate";
import { signup } from "../api/auth";

export type AgeRange =
    | "AGE_10S"
    | "AGE_20S"
    | "AGE_30S"
    | "AGE_40S"
    | "AGE_50S"
    | "AGE_60S_OVER"
    | "UNKNOWN";

export type Gender = "FEMALE" | "MALE" | "OTHER";

export default function useSignup() {
    const navigate = useNavigate();
    const [step, setStep] = useState<1 | 2>(1);

    const { values, errors, touched, getInputProps } = useForm<SignupInformation>({
        initialValue: {
            email: "",
            password: "",
            passwordConfirm: "",
            nickname: "",
        },
        validate: validateSignup,
    });

    const [gender, setGender] = useState<Gender>("FEMALE");
    const [ageRange, setAgeRange] = useState<AgeRange>("AGE_20S");

    const { agreements, handleAllAgree, updateAgreement } = useAgreement();

    const handleNextStep = () => {
        const emailError = errors.email;
        const passwordError = errors.password;
        const passwordConfirmError = errors.passwordConfirm;

        if (!touched.email || !touched.password || !touched.passwordConfirm) {
            alert("모든 필드를 입력해주세요.");
            return;
        }

        if (emailError || passwordError || passwordConfirmError) {
            alert("입력 정보를 다시 확인해주세요.");
            return;
        }

        setStep(2);
    };

    const handleSignup = async () => {
        if (!touched.nickname) {
            alert("닉네임을 입력해주세요.");
            return;
        }

        if (errors.nickname) {
            alert("닉네임을 다시 확인해주세요.");
            return;
        }

        if (!agreements.terms || !agreements.privacy) {
            alert("필수 약관에 동의해주세요.");
            return;
        }

        try {
            await signup({
                email: values.email,
                password: values.password,
                nickname: values.nickname,
                gender,
                ageRange,
            });
            alert("회원가입이 완료되었습니다! 로그인 해주세요.");
            navigate("/login");
        } catch (err) {
            console.log(err);
            alert("회원가입에 실패했습니다.");
        }
    };

    return {
        navigate,
        step,
        setStep,
        form: { values, errors, touched, getInputProps },
        gender,
        setGender,
        ageRange,
        setAgeRange,
        agreement: { agreements, handleAllAgree, updateAgreement },
        handleNextStep,
        handleSignup,
    };
}
