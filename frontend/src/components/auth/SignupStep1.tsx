import AuthInput from "./AuthInput";
import { type ChangeEvent } from "react";

interface SignupStep1Props {
    form: {
        values: { email: string; nickname: string };
        errors: Record<string, string>;
        touched: Record<string, boolean>;
        getInputProps: (name: any) => {
            value: any;
            onChange: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
            onBlur: () => void;
        };
    };
    onNext: () => void;
}

export default function SignupStep1({ form, onNext }: SignupStep1Props) {
    const { errors, touched, getInputProps } = form;

    return (
        <div className="space-y-6">
            <AuthInput
                label="이메일"
                type="email"
                placeholder="이메일을 입력해주세요."
                {...getInputProps("email")}
                error={errors.email}
                touched={touched.email}
                successMessage={
                    touched.email && !errors.email ? "사용 가능한 이메일입니다." : undefined
                }
            />

            <AuthInput
                label="비밀번호"
                type="password"
                placeholder="비밀번호를 입력해주세요."
                {...getInputProps("password")}
                error={errors.password}
                touched={touched.password}
            />

            <AuthInput
                label="비밀번호 재확인"
                type="password"
                placeholder="비밀번호를 재입력해주세요."
                {...getInputProps("passwordConfirm")}
                error={errors.passwordConfirm}
                touched={touched.passwordConfirm}
            />

            <button
                onClick={onNext}
                className="w-full bg-[#42BCEB] text-white py-3 rounded-lg font-medium hover:bg-[#38A5D0] transition mt-8"
            >
                다음
            </button>
        </div>
    );
}
