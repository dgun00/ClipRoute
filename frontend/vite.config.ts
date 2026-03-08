import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 현재 작업 디렉토리에서 .env 파일 로드 (VITE_ prefix가 없어도 로드 가능하도록 설정해도 되지만 보통 VITE_만 쓴다)
  // loadEnv(mode, process.cwd(), '') -> 세 번째 인자가 prefix인데 ''로 주면 모든 변수 로드
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      react(),
      tailwindcss()
    ],
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_TARGET, // .env에 정의된 주소 사용 (하드코딩 제거)
          changeOrigin: true,
          secure: false, // http 사용 시 필수
          // rewrite: (path) => path.replace(/^\/api/, ''), // 만약 백엔드가 /api를 안 쓴다면 이거 필요함. 
          // 하지만 사용자님의 vercel.json 설정("/api/:path*")을 보니 백엔드도 /api 경로를 쓰는 것 같아서 주석 처리.
        },
      },
    },
  }
})
