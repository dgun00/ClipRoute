import { useState } from "react";
import { useNavigate } from "react-router-dom";
import useForm from "../hooks/useForm";
import { validateSignup, type SignupInformation } from "../utils/validate";
import Header from "../components/common/Header";
import backicon from "../assets/icons/back-icon.svg";
import { signup } from "../api/auth";

export default function SignupPage() {
  const navigate = useNavigate();

  const { values, errors, touched, getInputProps } =
    useForm<SignupInformation>({
      initialValue: {
        email: "",
        password: "",
        passwordConfirm: "",
        nickname: "",
      },
      validate: validateSignup,
    });

  const [gender, setGender] =
    useState<"FEMALE" | "MALE" | "OTHER">("FEMALE");

  const [ageRange, setAgeRange] = useState<
    | "AGE_10S"
    | "AGE_20S"
    | "AGE_30S"
    | "AGE_40S"
    | "AGE_50S"
    | "AGE_60S_OVER"
    | "UNKNOWN"
  >("AGE_20S");

  const [agreements, setAgreements] = useState({
    all: false,
    terms: false,
    privacy: false,
    email: false,
    sns: false,
    push: false,
  });

  const handleAllAgree = (checked: boolean) => {
    setAgreements({
      all: checked,
      terms: checked,
      privacy: checked,
      email: checked,
      sns: checked,
      push: checked,
    });
  };

  const updateAgreement = (key: keyof typeof agreements, checked: boolean) => {
    setAgreements(prev => {
      const updated = { ...prev, [key]: checked };
      const allChecked =
        updated.terms &&
        updated.privacy &&
        updated.email &&
        updated.sns &&
        updated.push;

      return { ...updated, all: allChecked };
    });
  };

  const handleSignup = async () => {
    const noErrors = !Object.values(errors).some(e => e !== "");

    if (!noErrors) {
      alert("입력 정보를 다시 확인해주세요.");
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

      console.log("회원가입 요청 전송 완료");
    } catch (err) {
      console.error("회원가입 요청 실패", err);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white px-6 pt-12 pb-8">
      <Header
        left={
          <button onClick={() => navigate(-1)} aria-label="뒤로가기">
            <img src={backicon} alt="backicon" />
          </button>
        }
      />

      <div className="flex-1 space-y-8 overflow-y-auto">
       
        <section className="space-y-4">
          <div>
            <label className="block text-sm font-bold mb-2">이메일</label>
            <input
              type="email"
              placeholder="이메일을 입력해주세요."
              {...getInputProps("email")}
              className="w-full h-12 px-4 bg-[#F4F4F4] rounded-lg outline-none"
            />
            {touched.email && errors.email && (
              <p className="text-red-500 text-xs mt-1">{errors.email}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-bold mb-2">비밀번호</label>
            <input
              type="password"
              placeholder="비밀번호를 입력해주세요."
              {...getInputProps("password")}
              className="w-full h-12 px-4 bg-[#F4F4F4] rounded-lg outline-none"
            />
            {touched.password && errors.password && (
              <p className="text-red-500 text-xs mt-1">{errors.password}</p>
            )}
          </div>

         
          <div>
            <label className="block text-sm font-bold mb-2">
              비밀번호 재확인
            </label>
            <input
              type="password"
              placeholder="비밀번호를 다시 입력해주세요."
              {...getInputProps("passwordConfirm")}
              className="w-full h-12 px-4 bg-[#F4F4F4] rounded-lg outline-none"
            />
            {touched.passwordConfirm && errors.passwordConfirm && (
              <p className="text-red-500 text-xs mt-1">
                {errors.passwordConfirm}
              </p>
            )}
          </div>
        </section>

        {/* 닉네임 */}
        <section>
          <label className="block text-sm font-bold mb-2">닉네임</label>
          <input
            type="text"
            placeholder="닉네임을 입력해주세요."
            {...getInputProps("nickname")}
            className="w-full h-12 px-4 border border-[#42BCEB] rounded-lg"
          />
        </section>

        {/* 성별 */}
        <section>
          <label className="block text-sm font-bold mb-3">성별</label>
          <div className="flex gap-2">
            {[
              { label: "남성", value: "MALE" },
              { label: "여성", value: "FEMALE" },
              { label: "기타", value: "OTHER" },
            ].map(item => (
              <button
                key={item.value}
                type="button"
                onClick={() => setGender(item.value as any)}
                className={`flex-1 h-12 rounded-lg border ${
                  gender === item.value
                    ? "border-[#42BCEB] text-black"
                    : "bg-[#F4F4F4] text-gray-400"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </section>

        {/* 연령 */}
        <section>
          <label className="block text-sm font-bold mb-3">연령</label>
          <div className="flex bg-[#F4F4F4] rounded-lg p-1">
            {[
              { label: "10대", value: "AGE_10S" },
              { label: "20대", value: "AGE_20S" },
              { label: "30대", value: "AGE_30S" },
              { label: "40대", value: "AGE_40S" },
              { label: "50대+", value: "AGE_50S" },
            ].map(item => (
              <button
                key={item.value}
                type="button"
                onClick={() => setAgeRange(item.value as any)}
                className={`flex-1 h-10 rounded-md text-xs ${
                  ageRange === item.value
                    ? "bg-white border border-[#42BCEB]"
                    : "text-gray-400"
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </section>

        {/* 약관 */}
        <section className="pt-4 border-t space-y-4">
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={agreements.all}
              onChange={e => handleAllAgree(e.target.checked)}
            />
            <span className="font-bold text-sm">전체 동의</span>
          </div>

          {[
            { key: "terms", label: "[필수] 이용약관 동의" },
            { key: "privacy", label: "[필수] 개인정보 처리방침 동의" },
            { key: "email", label: "[선택] 이메일 수신 동의" },
            { key: "sns", label: "[선택] SNS 수신 동의" },
            { key: "push", label: "[선택] 앱 푸시 수신 동의" },
          ].map(item => (
            <div key={item.key} className="flex items-center gap-3 text-sm">
              <input
                type="checkbox"
                checked={(agreements as any)[item.key]}
                onChange={e =>
                  updateAgreement(item.key as any, e.target.checked)
                }
              />
              <span>{item.label}</span>
            </div>
          ))}
        </section>
      </div>

      <div className="mt-8">
        <button
          onClick={handleSignup}
          className="w-full h-14 bg-[#42BCEB] text-white text-lg font-bold rounded-xl"
        >
          회원가입
        </button>
      </div>
    </div>
  );
}
