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

export interface LoginRequest {
  email: string;
  password: string;
}

export const signup = (data: SignUpRequest) => {
  return api.post('/api/auth/signup', data);
};

export interface LoginResponse {
  status?: number;
  message?: string;
  data?: {
    accessToken?: string;
    refreshToken?: string;
    nickname?: string;
  };
}

export interface LoginOptions {
  /** localStorage 사용 여부 (false면 sessionStorage) */
  keepLogin?: boolean;
}

/**
 * 로그인 API 호출 및 토큰 저장
 * @param body 로그인 요청 데이터
 * @param options 로그인 옵션 (keepLogin 등)
 * @returns 로그인 응답 데이터
 */
export const login = async (
  body: LoginRequest,
  options: LoginOptions = { keepLogin: true }
) => {
  const res = await api.post<LoginResponse>("/api/auth/login", body);

  const storage = options.keepLogin ? localStorage : sessionStorage;

  // 기존 토큰 제거 (충돌 방지)
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("nickname");
  sessionStorage.removeItem("accessToken");
  sessionStorage.removeItem("refreshToken");
  sessionStorage.removeItem("nickname");

  // 🔍 전체 응답 구조 확인
  console.log('🔍 [백엔드 응답 전체 구조]', {
    '응답 전체': res,
    'res.data': res.data,
    'res.headers 전체': res.headers,
    'res.headers.authorization': res.headers['authorization'],
    'res.headers.Authorization': res.headers['Authorization'],
  });

  // 방법 1: 응답 바디에서 토큰 추출 (우선순위)
  let accessToken = res.data?.data?.accessToken;
  let refreshToken = res.data?.data?.refreshToken;
  let nickname = res.data?.data?.nickname;

  console.log('🔍 [로그인 응답 디버깅]', {
    'body에 토큰 있음': !!accessToken,
    'body에 refreshToken 있음': !!refreshToken,
    'nickname': nickname,
  });

  // 방법 2: 응답 헤더에서 토큰 추출 (바디에 없을 경우)
  if (!accessToken) {
    const headerToken = res.headers["authorization"] || res.headers["Authorization"];
    console.log('🔍 [헤더에서 토큰 찾기]', {
      'authorization 헤더 있음': !!res.headers["authorization"],
      'Authorization 헤더 있음': !!res.headers["Authorization"],
      'Bearer 형식 확인': headerToken?.startsWith("Bearer "),
    });

    if (headerToken?.startsWith("Bearer ")) {
      accessToken = headerToken.substring(7).trim();
      console.log('✅ [헤더에서 토큰 추출 성공]', {
        '토큰 길이': accessToken?.length || 0,
        '토큰 앞 10자': accessToken ? accessToken.substring(0, 10) + '...' : 'N/A',
      });
    }
  }

  // 토큰 검증
  if (!accessToken) {
    console.error('❌ [로그인 실패] 토큰을 받지 못했습니다.');
    console.error('📋 백엔드 개발자에게 전달 필요:');
    console.error('1. CORS 설정에 다음 추가 필요:');
    console.error('   Access-Control-Expose-Headers: Authorization');
    console.error('2. 로그인 응답 헤더에 토큰 포함 확인:');
    console.error('   Authorization: Bearer <token>');
    throw new Error("로그인 응답에 토큰이 없습니다. 백엔드 CORS 설정을 확인하세요.");
  }

  // 토큰 저장 (있을 경우만)
  if (accessToken) {
    storage.setItem("accessToken", accessToken);
  }

  if (refreshToken) {
    storage.setItem("refreshToken", refreshToken);
  }

  if (nickname) {
    storage.setItem("nickname", nickname);
  }

  console.log('✅ [로그인 성공] 토큰 저장 완료', {
    storage: options.keepLogin ? 'localStorage' : 'sessionStorage',
    hasAccessToken: !!accessToken,
    hasRefreshToken: !!refreshToken,
    nickname,
  });

  return res.data;
};

/**
 * 로그아웃 (토큰 삭제)
 */
export const logout = () => {
  // localStorage와 sessionStorage 모두 정리
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
  localStorage.removeItem("nickname");

  sessionStorage.removeItem("accessToken");
  sessionStorage.removeItem("refreshToken");
  sessionStorage.removeItem("nickname");

  console.log('✅ [로그아웃] 토큰 삭제 완료');
};

