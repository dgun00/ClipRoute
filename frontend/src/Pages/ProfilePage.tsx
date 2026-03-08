import { useNavigate } from "react-router-dom";
import { MyPageIcon } from "../assets/icons/NavBar/MyPageIcon";
import Header from "../components/common/Header";

export default function ProfilePage() {
  const navigate = useNavigate();

  return (
    <div className="w-full min-h-screen bg-white px-5 pt-4 pb-20">

      <Header>
        
      </Header>

      {/* ===== 상단 헤더 ===== */}
      <div className="flex items-center mb-6">
        <button
          onClick={() => navigate(-1)}
          className="mr-2 text-xl"
        >
          ‹
        </button>
        <h1 className="text-lg font-semibold">프로필 관리</h1>
      </div>

      {/* ===== 프로필 영역 ===== */}
      <div className="flex flex-col items-center mb-6">
        <div className="relative mb-3">
          <div className="w-20 h-20 bg-gray-200 rounded-full flex items-center justify-center">
            <MyPageIcon isActive={false} size={36} />
          </div>

          {/* 카메라 아이콘 자리 */}
          <div className="absolute bottom-0 right-0 w-7 h-7 bg-white border border-gray-300 rounded-full flex items-center justify-center">
            ㅁ
          </div>
        </div>

        <p className="font-medium">홍길동</p>
        <p className="text-sm text-[#42BCEB]">hong0123@naver.com</p>
      </div>

      <hr className="border-gray-200" />

      {/* ===== 계정 정보 ===== */}
      <p className="mt-4 mb-2 font-semibold">계정 정보</p>

      <div className="flex justify-between py-3">
        <span>닉네임</span>
        <span className="text-[#42BCEB]">홍길동 ›</span>
      </div>

      <div className="flex justify-between py-3 ">
        <span>이메일</span>
        <span className="text-[#42BCEB]">hong0123@naver.com ›</span>
      </div>

      <div className="flex justify-between py-3 ">
        <span>비밀번호</span>
        <span className="text-gray-500">변경 ›</span>
      </div>

      <div className="flex justify-between py-3">
        <span>성별</span>
        <span className="text-[#42BCEB]">남성 ›</span>
      </div>

      <div className="flex justify-between py-3">
        <span>나이</span>
        <span className="text-[#42BCEB]">20대 ›</span>
      </div>

      <hr className="border-gray-200 mt-6" />

      {/* ===== 하단 로그아웃 / 회원탈퇴 ===== */}
      <div className="flex justify-left gap-4 mt-4 text-sm text-gray-500">
         <div className="flex justify-between border-b">
          <span className="cursor-pointer">로그아웃</span>
         </div>
        
       <div className="flex justify-between border-b">
        <span className="cursor-pointer">회원탈퇴</span>
       </div>
      </div>
    </div>
  );
}
