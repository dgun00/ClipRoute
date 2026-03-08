import { type ChangeEvent } from "react";
import AuthInput from "./AuthInput";
import { type AgeRange, type Gender } from "../../hooks/useSignup";
import { type AgreementState } from "../../hooks/useAgreement";

interface SignupStep2Props {
    form: {
        values: { nickname: string };
        errors: Record<string, string>;
        touched: Record<string, boolean>;
        getInputProps: (name: any) => {
            value: any;
            onChange: (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => void;
            onBlur: () => void;
        };
    };
    gender: Gender;
    setGender: (gender: Gender) => void;
    ageRange: AgeRange;
    setAgeRange: (age: AgeRange) => void;
    agreement: {
        agreements: AgreementState;
        handleAllAgree: (checked: boolean) => void;
        updateAgreement: (key: any, checked: boolean) => void;
    };
    onPrevious: () => void;
    onSignup: () => void;
}

export default function SignupStep2({
    form,
    gender,
    setGender,
    ageRange,
    setAgeRange,
    agreement,
    onPrevious,
    onSignup,
}: SignupStep2Props) {
    const { errors, touched, getInputProps } = form;
    const { agreements, handleAllAgree, updateAgreement } = agreement;

    return (
        <div className="space-y-6">
            <AuthInput
                label="닉네임"
                type="text"
                placeholder="닉네임을 입력해주세요."
                {...getInputProps("nickname")}
                error={errors.nickname}
                touched={touched.nickname}
                successMessage={
                    touched.nickname && !errors.nickname ? "✓" : undefined
                }
            />

            {/* 성별 */}
            <div>
                <label className="block text-sm font-medium mb-3">성별</label>
                <div className="flex gap-3">
                    {[
                        { label: "남성", value: "MALE" as const },
                        { label: "여성", value: "FEMALE" as const },
                        { label: "기타", value: "OTHER" as const },
                    ].map((item) => (
                        <button
                            key={item.value}
                            onClick={() => setGender(item.value)}
                            className={`flex-1 h-12 rounded-lg border ${gender === item.value
                                ? "border-[#42BCEB] text-black bg-white"
                                : "bg-gray-100 text-gray-400 border-transparent"
                                }`}
                        >
                            {item.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* 연령 */}
            <div>
                <label className="block text-sm font-medium mb-3">연령</label>
                <div className="flex gap-2">
                    {[
                        { label: "10대", value: "AGE_10S" as const },
                        { label: "20대", value: "AGE_20S" as const },
                        { label: "30대", value: "AGE_30S" as const },
                        { label: "40대", value: "AGE_40S" as const },
                        { label: "50대+", value: "AGE_50S" as const },
                    ].map((item) => (
                        <button
                            key={item.value}
                            onClick={() => setAgeRange(item.value)}
                            className={`flex-1 h-10 rounded-md text-xs ${ageRange === item.value
                                ? "bg-white border-[#42BCEB] text-black"
                                : "bg-gray-100 text-gray-400 border-transparent"
                                }`}
                        >
                            {item.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* 약관 동의 */}
            <div>
                <label className="block text-sm font-medium mb-4">약관</label>

                {/* 전체 동의 */}
                <div className="flex items-center gap-2 mb-4 pb-4 border-b">
                    <input
                        type="checkbox"
                        id="all-agree"
                        checked={agreements.all}
                        onChange={(e) => handleAllAgree(e.target.checked)}
                        className="w-4 h-4"
                    />
                    <label htmlFor="all-agree" className="font-medium">
                        전체 동의
                    </label>
                </div>

                {/* 개별 약관 */}
                <div className="space-y-3">
                    {[
                        { key: "terms" as const, label: "[필수] 이용약관 동의" },
                        { key: "privacy" as const, label: "[필수] 개인정보 처리방침 동의" },
                        { key: "email" as const, label: "[선택] 이메일 수신 동의" },
                        { key: "sns" as const, label: "[선택] SNS 수신 동의" },
                        { key: "push" as const, label: "[선택] 앱 푸시 수신 동의" },
                    ].map((item) => (
                        <div key={item.key} className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id={item.key}
                                checked={agreements[item.key]}
                                onChange={(e) =>
                                    updateAgreement(item.key, e.target.checked)
                                }
                                className="w-4 h-4"
                            />
                            <label htmlFor={item.key} className="text-sm">
                                {item.label}
                            </label>
                        </div>
                    ))}
                </div>
            </div>

            {/* 버튼 그룹 */}
            <div className="flex gap-3 mt-8">
                <button
                    onClick={onPrevious}
                    className="flex-1 border border-gray-300 text-gray-700 py-3 rounded-lg font-medium hover:bg-gray-50 transition"
                >
                    이전
                </button>
                <button
                    onClick={onSignup}
                    className="flex-1 bg-[#42BCEB] text-white py-3 rounded-lg font-medium hover:bg-[#38A5D0] transition"
                >
                    회원가입
                </button>
            </div>
        </div>
    );
}
