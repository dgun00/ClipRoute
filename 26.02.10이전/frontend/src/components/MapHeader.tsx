const MapHeader = () => {
  return (
    <div className="absolute top-0 left-0 right-0 z-10 px-[16px] pt-[12px]">
      {/*  헤더 */}
      <div className="w-full h-[48px] bg-white rounded-[13px] border border-[#42BCEB] flex items-center px-3 shadow-sm">
        
        {/* 뒤로가기 아이콘 */}
        <button className="text-gray-600">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>

        {/* 수정 필요 */}
        <span className="flex-1 text-[15px] font-bold truncate text-[#333] px-1">
          [영상 제목..] 코스 정리
        </span>

        
        <div className="relative flex flex-col items-center">
          {/* 북마크 아이콘 */}
          <button className="text-black p-1">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/></svg>
          </button>

          
          <div className="absolute top-full mt-1 flex flex-col items-center">
           
            <svg width="10" height="6" viewBox="0 0 10 6" className="text-[#42BCEB] fill-current">
              <path d="M5 0L10 6H0L5 0Z" />
            </svg>

            {/* 말풍선 몸통 */}
            <div className="bg-[#42BCEB] text-white px-3 py-1 rounded-full shadow-md whitespace-nowrap">
              <span className="text-[11px] font-bold leading-none">저장하기</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MapHeader;