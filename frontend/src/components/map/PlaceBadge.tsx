import { CATEGORIES } from "../../constants/categories";

interface PlaceBadgeProps {
    name: string;
    category: string;
}

const PlaceBadge = ({ name, category }: PlaceBadgeProps) => {
    // 카테고리 아이콘 찾기
    const catInfo = CATEGORIES.find(c => c.id === category || c.name === category) || CATEGORIES.find(c => c.id === "기타");
    const icon = catInfo?.icon;

    return (
        <div className="relative flex items-center bg-[#42BCEB] text-white rounded-full pl-[0.25rem] pr-3 gap-2 min-w-max cursor-pointer hover:bg-[#3aaad6] transition-colors h-[2rem] shadow-md border border-transparent">
            {/* 둥근 아이콘 배경 */}
            <div className="grid place-items-center w-[1.6rem] h-[1.6rem] bg-white rounded-full text-[#42BCEB] flex-shrink-0 shadow-sm p-[0.25rem]">
                {icon ? (
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" className="block">
                        {icon}
                    </svg>
                ) : (
                    <div className="w-3 h-3 bg-[#42BCEB] rounded-full" />
                )}
            </div>

            {/* 장소명 */}
            <span className="text-[0.875rem] font-bold truncate max-w-[140px] leading-none pt-[1px]">{name}</span>

            {/* 하단 꼬리 */}
            {/* <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-0 h-0 border-l-[3px] border-l-transparent border-r-[3px] border-r-transparent border-t-[4px] border-t-[#42BCEB]" /> */}
        </div>
    );
};

export default PlaceBadge;
