export interface ApiResponse<T> {
  isSuccess: boolean;
  code: string;
  message: string;
  result: T;
}

/**
 * JWT 토큰 Payload 구조
 */
export interface TokenPayload {
  sub: number;  // 사용자 ID
  iat: number;  // 발급 시간 (timestamp)
  exp: number;  // 만료 시간 (timestamp)
}

/**
 * 인증 데이터 (localStorage/sessionStorage에 저장)
 */
export interface AuthData {
  accessToken: string;
  refreshToken?: string;  // 나중에 추가될 수 있음
}
