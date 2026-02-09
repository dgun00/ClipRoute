export type LoginInformation = {
  email: string;
  password: string;
};

export type SignupInformation = {
  email: string;
  password: string;
  passwordConfirm: string;
  nickname: string;
};

// 로그인 검증 함수
function validateSignin(values: LoginInformation) {
  const errors: Record<keyof LoginInformation, string> = {
    email: "",
    password: "",
  };

  if (!values.email) {
    errors.email = "이메일을 입력해주세요.";
  } else if (!/^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i.test(values.email)) {
    errors.email = "올바른 이메일 형식이 아닙니다.";
  }

  if (!values.password) {
    errors.password = "비밀번호를 입력해주세요.";
  } else if (!(values.password.length >= 8 && values.password.length <= 20)) {
    errors.password = "비밀번호는 8~20자 사이로 입력해주세요.";
  }

  return errors;
}

// 회원가입 검증 함수
function validateSignup(values: SignupInformation) {
  const errors: Record<keyof SignupInformation, string> = {
    email: "",
    password: "",
    passwordConfirm: "",
    nickname: "",
  };

  if (!values.email) {
    errors.email = "이메일을 입력해주세요.";
  } else if (!/^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*\.[a-zA-Z]{2,3}$/i.test(values.email)) {
    errors.email = "올바른 이메일 형식이 아닙니다.";
  }

  if (!values.nickname) {
    errors.nickname = "닉네임을 입력해주세요.";
  } else if (values.nickname.length < 2 || values.nickname.length > 10) {
    errors.nickname = "닉네임은 2자 이상 10자 이하여야 합니다.";
  }

  if (!values.password) {
    errors.password = "비밀번호를 입력해주세요.";
  } else if (!(values.password.length >= 8 && values.password.length <= 20)) {
    errors.password = "비밀번호는 8~20자 사이로 입력해주세요.";
  } else if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(values.password)) {
    errors.password = "비밀번호는 영문자와 숫자를 포함해야 합니다.";
  }

  if (!values.passwordConfirm) {
    errors.passwordConfirm = "비밀번호를 다시 입력해주세요.";
  } else if (values.password !== values.passwordConfirm) {
    errors.passwordConfirm = "비밀번호가 일치하지 않습니다.";
  }

  return errors;
}

export { validateSignin, validateSignup };