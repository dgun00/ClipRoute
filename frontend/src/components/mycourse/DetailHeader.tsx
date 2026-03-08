
import backicon from "../../assets/icons/back-icon.svg";

interface DetailHeaderProps {
    region: string;
    title: string;
    date: string;
    onBack: () => void;
    onEdit: () => void;
    isEditMode?: boolean;
    onTitleClick?: () => void;
}

export default function DetailHeader({ region, title, date, onBack, onEdit, isEditMode = false, onTitleClick }: DetailHeaderProps) {
    return (
        <div className="absolute top-0 left-0 right-0 z-10 px-[16px] pt-[12px]">
            <div className="w-full h-[48px] bg-white rounded-[13px] border border-[#42BCEB] flex items-center px-3 shadow-sm">
                {/* 뒤로 가기 버튼 */}
                <button
                    onClick={onBack}
                    className="p-1 -ml-1 hover:bg-gray-100 rounded-full transition-colors mr-2"
                >
                    <img src={backicon} className="w-4 h-4" alt="뒤로가기" />
                </button>

                {/* 지역 뱃지 */}
                <span className="bg-[#42BCEB] text-white text-[12px] font-bold px-3 py-1 rounded-full mr-2 whitespace-nowrap">
                    {region}
                </span>

                {/* 제목 및 날짜 */}
                <div
                    className={`flex-1 truncate flex items-center gap-1 min-w-0 transition-colors ${isEditMode ? "cursor-pointer active:opacity-70" : ""
                        }`}
                    onClick={() => isEditMode && onTitleClick?.()}
                >
                    <span className="text-[15px] font-bold text-gray-900 truncate">
                        {title}
                    </span>
                    <span className="text-[13px] font-semibold text-black whitespace-nowrap">
                        · {date}
                    </span>
                </div>

                {/* 편집 버튼 */}
                <button
                    onClick={onEdit}
                    className={`text-[13px] font-bold px-2 whitespace-nowrap ${isEditMode ? "text-[#42BCEB]" : "text-gray-900 hover:text-gray-600"}`}
                >
                    {isEditMode ? "완료" : "편집"}
                </button>
            </div>
        </div>
    );
}
