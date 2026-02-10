import api from './axios';

export interface SignUpRequest {
  email: string;
  password: string;
  nickname: string;
  gender: 'FEMALE' | 'MALE' | 'OTHER';
  ageRange:
    | 'AGE_10S'
    | 'AGE_20S'
    | 'AGE_30S'
    | 'AGE_40S'
    | 'AGE_50S'
    | 'AGE_60S_OVER'
    | 'UNKNOWN';
}

export const signup = (data: SignUpRequest) => {
  return api.post('/api/auth/signup', data);
};
