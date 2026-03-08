import useSignup from "../hooks/useSignup";
import Header from "../components/common/Header";
import SignupStep1 from "../components/auth/SignupStep1";
import SignupStep2 from "../components/auth/SignupStep2";
import backicon from "../assets/icons/back-icon.svg";

export default function SignupPage() {
  const {
    navigate,
    step,
    setStep,
    form,
    gender,
    setGender,
    ageRange,
    setAgeRange,
    agreement,
    handleNextStep,
    handleSignup,
  } = useSignup();

  return (
    <div>
      <Header
        left={
          <button onClick={() => navigate(-1)} aria-label="뒤로가기">
            <span className="flex items-center pr-2">
              <img src={backicon} alt="backicon" />
              <div className="pl-2 font-semibold">회원가입</div>
            </span>
          </button>
        }
      />

      <div className="max-w-md mx-auto p-6">
        {step === 1 && (
          <SignupStep1 form={form} onNext={handleNextStep} />
        )}

        {step === 2 && (
          <SignupStep2
            form={form}
            gender={gender}
            setGender={setGender}
            ageRange={ageRange}
            setAgeRange={setAgeRange}
            agreement={agreement}
            onPrevious={() => setStep(1)}
            onSignup={handleSignup}
          />
        )}
      </div>
    </div>
  );
}