import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Toggle from "../components/Toggle";
import { MyPageIcon } from "../assets/icons/NavBar/MyPageIcon";

export default function MyPage() {
  const navigate = useNavigate();

  const [sns, setSns] = useState(true);
  const [marketing, setMarketing] = useState(false);
  const [eventPush, setEventPush] = useState(false);

  return (
    <div className="w-full min-h-screen bg-white px-5 pt-4 pb-20">

      {/* ===== 상단 헤더 (뒤로가기 + 제목) ===== */}
      <div className="flex items-center mb-4">
        <button
          onClick={() => navigate(-1)}
          className="mr-2 text-xl"
        >
          ‹
        </button>
        <h1 className="text-lg font-semibold">마이페이지</h1>
      </div>

      {/* ===== 프로필 요약 영역 ===== */}
      <div
        className="flex items-center justify-between py-4 border-b cursor-pointer"
        onClick={() => navigate("/my/profile")}
      >
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 flex items-center justify-center bg-gray-200 rounded-full">
            <MyPageIcon isActive={false} size={28} />
          </div>

          <div>
            <p className="font-medium">홍길동님</p>
            <p className="text-sm text-[#42BCEB]">hong0123@naver.com</p>
          </div>
        </div>

        <span className="text-gray text-lg">›</span>
      </div>

      {/* ===== 알림 설정 ===== */}
      <div className="mt-6">
        <p className="text-base font-semibold mb-4">알람 설정</p>

        <div className="flex items-center font-semibold justify-between py-3 ">
          <span>SNS 수신 동의</span>
          <Toggle checked={sns} onChange={() => setSns(!sns)} />
        </div>

        <div className="flex items-center font-semibold justify-between py-3 ">
          <span>마케팅 수신 동의</span>
          <Toggle checked={marketing} onChange={() => setMarketing(!marketing)} />
        </div>

        <div className="flex items-center font-bold justify-between py-3">
          <span>이벤트 앱 푸시 수신 동의</span>
          <Toggle checked={eventPush} onChange={() => setEventPush(!eventPush)} />
        </div>
      </div>
    </div>
  );
}
