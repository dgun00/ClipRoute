import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Pretendard', 'system-ui', 'Apple SD Gothic Neo', 'sans-serif'],
      },
      colors: {
        primary: '#42BCEB',        // Main_Point
        'primary-dark': '#000000', // Main_Dark
        white: '#FFFFFF',          // Main_White
        'gray-1': '#333333',       // Main_Dark Gray
        'gray-2': '#606060',       // Text_Dark Gray
        'gray-3': '#999999',       // Text_Gray
        'gray-4': '#B5B5B5',       // Blur_Gray 80%
        'gray-5': '#D2D2D2',       // Main_Gray
        'gray-6': '#D9D9D9',       // Sheet_Gray 80%
        'gray-7': '#E4E4E4',       // Main_Low Gray
        'gray-8': '#F4F4F4',       // Light Gray
        pink: '#FF9999',           // Point
        blue: '#9999FF',           // Point
      },
    },
  },
  plugins: [],
}

export default config
