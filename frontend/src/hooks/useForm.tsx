import { useEffect, useState } from "react";
import type { ChangeEvent } from "react";

interface UseFormProps<T> {
  initialValue: T; // { email: "", password: ""}
  validate: (value: T) => Record<keyof T, string>;
}

function useForm<T>({initialValue, validate}: UseFormProps<T>) {
  const [ values, setValues ] = useState(initialValue);
  const [ touched, setTouched] = useState<Record<string, boolean>>({});
  const [ errors, setErrors ] = useState<Record<string, string>>({});

  // 사용자가 입력값 변경 시 실행되는 함수
  const handlechange = (name: keyof T, text: string) => {
    setValues({
      ...values, // 기존값 유지
      [name]: text,
    });
  };

  const handleBlur = ( name: keyof T) => {
    setTouched({
      ...touched,
      [name]: true,
    });
  };
  
  // 이메일, 비밀번호 입력 속성 가져오기
  const getInputProps = ( name: keyof T) => {
    const value: T[keyof T] = values[name];
    const onChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => handlechange(name, e.target.value);
    const onBlur = () => handleBlur(name);
    return { value, onChange, onBlur};
  };
  
  // values 변경 시 에러 검증 로직 실행
  useEffect(() =>{
    const newsErrors = validate(values);
    setErrors(newsErrors); // 오류 메시지 업뎃
  }, [validate, values]);

  return { values, errors, touched, getInputProps };
}

export default useForm; 


