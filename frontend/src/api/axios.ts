import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: 토큰 자동 추가
api.interceptors.request.use(
  (config) => {
    // 인증 불필요 엔드포인트 (로그인, 회원가입)
    const publicEndpoints = ['/api/auth/login', '/api/auth/signup'];
    const isPublicEndpoint = publicEndpoints.some(endpoint => config.url?.includes(endpoint));

    // 토큰 가져오기 (localStorage 우선, 없으면 sessionStorage)
    const localToken = localStorage.getItem('accessToken');
    const sessionToken = sessionStorage.getItem('accessToken');
    const token = localToken || sessionToken;

    console.log('🔍 [Request Interceptor]', {
      'URL': config.url,
      'isPublicEndpoint': isPublicEndpoint,
      'localStorage 토큰': localToken ? `있음 (${localToken.substring(0, 20)}...)` : 'null',
      'sessionStorage 토큰': sessionToken ? `있음 (${sessionToken.substring(0, 20)}...)` : 'null',
      '최종 토큰': token ? `있음 (${token.substring(0, 20)}...)` : 'null',
      '토큰 추가 여부': !isPublicEndpoint && !!token,
    });

    // 공개 엔드포인트가 아니고 토큰이 있으면 Authorization 헤더에 추가
    if (!isPublicEndpoint && token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('✅ Authorization 헤더 추가됨!');
    } else {
      console.log('⚠️ Authorization 헤더 추가 안 됨 (공개 엔드포인트 또는 토큰 없음)');
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor: 에러 처리
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 401 에러 처리 (인증 실패)
    if (error.response?.status === 401) {
      console.error('❌ 인증 실패: 로그인이 필요합니다.');
      // 필요시 로그인 페이지로 리다이렉트
      // window.location.href = '/login';
    }

    // 403 에러 처리 (권한 없음)
    if (error.response?.status === 403) {
      console.error('❌ 권한 없음: 접근이 거부되었습니다.');
    }

    return Promise.reject(error);
  }
);

export default api;
