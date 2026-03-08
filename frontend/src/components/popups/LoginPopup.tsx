import { useNavigate } from "react-router-dom";

interface LoginPopupProps {
  isOpen: boolean;
  onClose: () => void;
}


const LoginPopup = ({ isOpen, onClose }: LoginPopupProps) => {
  const navigate = useNavigate();

  if (!isOpen) return null;

  return (

    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/40 backdrop-blur-[1px]">


      <div className="w-[340px] bg-white rounded-[24px] p-7 shadow-xl relative animate-in fade-in zoom-in duration-200">

        {/* 상단 닫기 버튼 */}
        <button
          onClick={onClose}
          className="absolute top-6 right-6 text-black"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        {/* 타이틀 영역 */}
        <div className="pt-2">
          <h3 className="text-[20px] font-bold text-black mb-4">
            로그인이 필요해요
          </h3>
          {/* 회색 구분선 */}
          <div className="w-full h-[1px] bg-[#EEEEEE]"></div>
        </div>

        {/* 본문 텍스트 영역 */}
        <div className="mt-6 mb-10">
          <p className="text-[15px] text-[#333] font-bold leading-[1.6]">
            로그인 시 코스와 장소를 저장하고<br />
            내 코스를 통해 다시 확인할 수 있어요.
          </p>
        </div>

        {/* 버튼 영역 */}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 h-[54px] border border-[#42BCEB] text-[#333] text-[16px] font-bold rounded-[14px] hover:bg-gray-50 transition-colors"
          >
            나중에 할게요
          </button>
          <button
            onClick={() => navigate('/login')}
            className="flex-1 h-[54px] bg-[#42BCEB] text-white text-[16px] font-bold rounded-[14px] shadow-sm active:bg-[#38a6d0] transition-colors"
          >
            로그인하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default LoginPopup;