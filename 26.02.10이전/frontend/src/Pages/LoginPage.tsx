import { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import usericon from "../assets/icons/user-icon.svg";
import passwordicon from "../assets/icons/password-icon.svg";
import useForm from "../hooks/useForm";
import { validateSignin, type LoginInformation } from "../utils/validate";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [keepLogin, setKeepLogin] = useState(false);
  
  const navigate = useNavigate(); 

  const { values, errors, touched, getInputProps } = useForm<LoginInformation>({
    initialValue: { 
      email: "", 
      password: "" 
    },
    validate: validateSignin, 
  });

  const handleLogin = () => {
    const noErrors = !errors.email && !errors.password;
    const isSubmitted = values.email && values.password;

    if (noErrors && isSubmitted) {
      console.log("로그인 시도:", { 
        email: values.email, 
        password: values.password,
        keepLogin 
      });
      alert("로그인 성공");
    } else {
      alert("입력 정보를 다시 확인해주세요.");
    }
  };

  return (
    <div className="flex flex-col h-full px-8 pt-24 pb-12">
      <div className="flex justify-center mb-16">
        <h1 className="text-[26px] font-extrabold text-[#42BCEB] tracking-tight">
          ClipRoute
        </h1>
      </div>

      
      <div className="space-y-4 mb-10">
        {/* 이메일 입력 */}
        <div>
          <div className="relative w-full">
            <span className="absolute left-[15px] top-1/2 -translate-y-1/2 flex items-center">
              <img src={usericon} alt="usericon" className="w-6 h-6" />
            </span>
            <input
              type="email"
              placeholder="이메일"
              {...getInputProps("email")} 
              className="w-full h-[55px] pl-[45px] pr-[15px] bg-[#F4F4F4] border-none focus:ring-2 focus:ring-[#42BCEB] outline-none transition-all placeholder:text-[#606060]"
            />
          </div>
          {touched.email && errors.email && (
            <p className="text-red-500 text-xs mt-1 ml-1">{errors.email}</p>
          )}
        </div>

        {/* 비밀번호 입력 */}
        <div>
          <div className="relative w-full">
            <span className="absolute left-[15px] top-1/2 -translate-y-1/2 flex items-center">
              <img src={passwordicon} alt="passwordicon" className="w-5 h-5" />
            </span>
            <input
              type={showPassword ? "text" : "password"}
              placeholder="비밀번호"
              {...getInputProps("password")} 
              className="w-full h-[55px] pl-[45px] pr-[45px] bg-[#F4F4F4] border-none focus:ring-2 focus:ring-[#42BCEB] outline-none transition-all placeholder:text-[#606060]"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-[15px] top-1/2 -translate-y-1/2 text-[#606060] transition-colors hover:text-[#42BCEB]"
            >
              {showPassword ? "o" : "x"}
            </button>
          </div>
          {touched.password && errors.password && (
            <p className="text-red-500 text-xs mt-1 ml-1">{errors.password}</p>
          )}
        </div>

        {/* 로그인 상태 유지 */}
        <div className="flex items-center gap-2 py-2">
          <input
            type="checkbox"
            id="keep"
            checked={keepLogin}
            onChange={(e) => setKeepLogin(e.target.checked)}
            className="w-5 h-5 rounded border-gray-300 text-[#42BCEB] focus:ring-[#42BCEB] cursor-pointer"
          />
          <label htmlFor="keep" className="text-sm text-gray-600 font-medium cursor-pointer select-none">
            로그인 상태 유지
          </label>
        </div>
      </div>


      <div className="space-y-6">
        <button
          onClick={handleLogin}
          className="w-full h-14 bg-[#42BCEB] text-white text-lg font-bold rounded-xl hover:bg-[#3ba8d4] active:scale-[0.98] transition-all shadow-md shadow-blue-50"
        >
          로그인
        </button>

        <div className="flex justify-center items-center gap-4 text-[13px] text-gray-500 font-medium">
          <button 
            onClick={() => navigate("/signup")} 
            className="hover:text-gray-800 transition-colors"
          >
            회원가입
          </button>
          <span className="w-[1px] h-3 bg-gray-300"></span>
          <button className="hover:text-gray-800 transition-colors">ID 찾기</button>
          <span className="w-[1px] h-3 bg-gray-300"></span>
          <button className="hover:text-gray-800 transition-colors">비밀번호 찾기</button>
        </div>
      </div>
    </div>
  );
}