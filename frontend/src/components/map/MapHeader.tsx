import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import backIcon from "../../assets/icons/back-icon.svg";
import saveIcon from "../../assets/icons/save-icon.svg";
import LoginPopup from "../popups/LoginPopup";
import { useScrapCourse } from "../../hooks/useScrapCourse";

interface MapHeaderProps {
  courseId?: number;
  videoTitle?: string;
}

const MapHeader = ({ courseId, videoTitle }: MapHeaderProps) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const startDate = searchParams.get("startDate");
  const endDate = searchParams.get("endDate");
  const [showSaveTooltip, setShowSaveTooltip] = useState(true);
  const [isLoginPopupOpen, setIsLoginPopupOpen] = useState(false);
  const { mutate: scrap, isPending } = useScrapCourse();

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowSaveTooltip(false);
    }, 3000);
    return () => clearTimeout(timer);
  }, []);

  const handleSaveClick = () => {
    setShowSaveTooltip(false);

    // 로그인 확인
    const token = localStorage.getItem('accessToken') || sessionStorage.getItem('accessToken');

    if (!token) {
      // 로그인 안 되어 있으면 팝업
      setIsLoginPopupOpen(true);
      return;
    }

    // 로그인 되어 있으면 스크랩
    if (courseId) {
      scrap(
        { courseId, startDate, endDate },
        {
          onSuccess: () => {
            alert('✅ 내 코스에 저장되었어요!');
            // TODO: UX 개선 필요 
          },
          onError: () => {
            alert('❌ 스크랩에 실패했습니다. 다시 시도해주세요.');
          }
        }
      );
    }
  };

  return (
    <>
      <div className="absolute top-0 left-0 right-0 z-10 px-[16px] pt-[12px]">
        <div className="w-full h-[48px] bg-white rounded-[13px] border border-[#42BCEB] flex items-center px-3 shadow-sm">
          {/* 뒤로 가기 버튼 */}
          <button
            onClick={() => navigate(-1)}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors">
            <img src={backIcon} className="w-4 h-4" alt="뒤로가기" />
          </button>

          {/* 영상 제목  */}
          <span className="flex-1 text-[15px] font-bold truncate text-[#333] px-2">
            {videoTitle || '[영상 제목..] 코스 정리'}
          </span>

          <div className="relative flex items-center">
            {/* 스크랩 버튼 */}
            <button
              onClick={handleSaveClick}
              disabled={isPending}
              className="p-1 hover:bg-gray-100 rounded-full transition-colors disabled:opacity-50"
            >
              <img src={saveIcon} className="w-5 h-5" alt="저장하기" />
            </button>

            {/* 툴팁 (3초 후 자동 소멸) */}
            {showSaveTooltip && (
              <div className="absolute top-full right-0 mt-3 flex flex-col items-end pointer-events-none animate-bounce-subtle">
                <div className="bg-[#42BCEB] text-white text-[12px] font-semibold px-3 py-2 rounded-full whitespace-nowrap shadow-lg">
                  저장하기
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 로그인 유도 팝업 연동 */}
      <LoginPopup
        isOpen={isLoginPopupOpen}
        onClose={() => setIsLoginPopupOpen(false)}
      />
    </>
  );
};

export default MapHeader;