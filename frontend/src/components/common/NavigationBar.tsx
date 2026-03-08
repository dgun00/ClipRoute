import { useNavigate, useLocation } from "react-router-dom";
import { HomeIcon } from "../../assets/icons/NavBar/HomeIcon";
import { MycourseIcon } from "../../assets/icons/NavBar/MycourseIcon";
import { MyPageIcon } from "../../assets/icons/NavBar/MyPageIcon";

interface NavItem {
  id: 'home' | 'course' | 'mypage';
  label: string;
  path: string;
  Icon: React.ComponentType<{ isActive: boolean; size?: number }>;
}


const NAV_MENU: NavItem[] = [
  { id: 'home', label: '홈', path: '/', Icon: HomeIcon },
  { id: 'course', label: '내 코스', path: '/mycourse', Icon: MycourseIcon },
  { id: 'mypage', label: '마이페이지', path: '/my', Icon: MyPageIcon },
];

export default function NavigationBar() {
  const navigate = useNavigate();
  const location = useLocation();


  const handleNavigation = (path: string) => {
    const token = localStorage.getItem("accessToken") || sessionStorage.getItem("accessToken");

    // 내 코스, 마이페이지는 로그인 필요
    if ((path === '/mycourse' || path === '/my') && !token) {
      // 토큰이 없으면 로그인 페이지로 이동
      navigate('/login');
      return;
    }

    navigate(path);
  };

  return (
    <nav className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 flex w-[22.0625rem] h-[4.0625rem] max-w-[calc(100%-2rem)] items-center justify-center gap-x-[3.44rem] rounded-full bg-white shadow-[0_0_10px_0_rgba(0,0,0,0.1)] border border-gray-50 px-2">
      {NAV_MENU.map((item) => {
        // 현재 경로가 item.path와 일치하는지 확인하여 활성화 상태 결정
        const isActive = location.pathname === item.path;

        return (
          <button
            key={item.id}
            onClick={() => handleNavigation(item.path)}
            className="flex flex-col items-center justify-center gap-1 transition-all duration-200 active:scale-90 h-full w-auto min-w-[3rem] whitespace-nowrap"
          >
            <item.Icon isActive={isActive} size={24} />
            <span
              className={`text-sm transition-colors duration-200 ${isActive ? 'text-[#42BCEB] font-bold' : 'text-black'
                }`}
            >
              {item.label}
            </span>
          </button>
        );
      })}
    </nav>
  );
}