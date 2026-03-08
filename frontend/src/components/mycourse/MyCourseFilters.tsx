import { useState, useRef, useEffect } from "react";
import chevronDown from "../../assets/icons/chevrondown-icon.svg";
import chevronUp from "../../assets/icons/chevronup-icon.svg";

import type { FilterOptionResult } from "../../types/mycourse";

interface MyCourseFiltersProps {
    filterOptions: FilterOptionResult | null;
    selectedRegionId: number | null;
    setSelectedRegionId: (id: number | null) => void;
    selectedTravelDay: number | null;
    setSelectedTravelDay: (day: number | null) => void;
}

export default function MyCourseFilters({
    filterOptions,
    selectedRegionId,
    setSelectedRegionId,
    selectedTravelDay,
    setSelectedTravelDay,
}: MyCourseFiltersProps) {
    const [isRegionOpen, setIsRegionOpen] = useState(false);
    const [isSortOpen, setIsSortOpen] = useState(false);

    const regionRef = useRef<HTMLDivElement>(null);
    const sortRef = useRef<HTMLDivElement>(null);

    // 외부 클릭 시 드롭다운 닫기
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (regionRef.current && !regionRef.current.contains(event.target as Node)) {
                setIsRegionOpen(false);
            }
            if (sortRef.current && !sortRef.current.contains(event.target as Node)) {
                setIsSortOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="px-5 py-4 flex justify-end gap-[0.94rem] items-center bg-white">
            {/* 지역 필터 */}
            {/* 지역 필터 (Custom Dropdown) */}
            {/* 지역 필터 (Custom Dropdown) */}
            <div
                ref={regionRef}
                className="relative inline-flex items-center gap-[0.41rem] cursor-pointer"
                onClick={() => setIsRegionOpen(!isRegionOpen)}
            >
                <span className="text-[#606060] font-medium text-[0.875rem] leading-[1.5rem]">
                    {selectedRegionId
                        ? filterOptions?.regions.find(r => r.id === selectedRegionId)?.name || '지역'
                        : '지역'}
                </span>
                <img
                    src={isRegionOpen ? chevronUp : chevronDown}
                    alt="toggle"
                    className="w-3 h-3"
                />

                {isRegionOpen && (
                    <ul className="absolute top-full right-0 mt-1 flex flex-col items-start gap-[0.9375rem] w-[6.25rem] p-[0.625rem_0.9375rem] bg-white border border-[#D2D2D2] rounded-[0.625rem] shadow-sm z-20 max-h-[200px] overflow-y-auto scrollbar-hide">
                        <li
                            className={`text-[0.875rem] font-medium leading-[0.875rem] cursor-pointer ${selectedRegionId === null ? 'text-[#606060]' : 'text-black'}`}
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedRegionId(null);
                                setIsRegionOpen(false);
                            }}
                        >
                            전체
                        </li>
                        {filterOptions?.regions.map((region) => (
                            <li
                                key={region.id}
                                className={`text-[0.875rem] font-medium leading-[0.875rem] cursor-pointer ${selectedRegionId === region.id ? 'text-[#606060]' : 'text-black'}`}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedRegionId(region.id);
                                    setIsRegionOpen(false);
                                }}
                            >
                                {region.name}
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            {/* 여행 기간 필터 */}
            <div
                ref={sortRef}
                className="relative inline-flex items-center gap-[0.31rem] cursor-pointer"
                onClick={() => setIsSortOpen(!isSortOpen)}
            >
                <span className="text-[#606060] font-medium text-[0.875rem] leading-[1.5rem]">
                    {selectedTravelDay ? `${selectedTravelDay}일` : '여행 기간'}
                </span>
                <img
                    src={isSortOpen ? chevronUp : chevronDown}
                    alt="toggle"
                    className="w-3 h-3"
                />

                {isSortOpen && (
                    <ul className="absolute top-full right-0 mt-1 flex flex-col items-start gap-[0.9375rem] w-[6.25rem] p-[0.625rem_0.9375rem] bg-white border border-[#D2D2D2] rounded-[0.625rem] shadow-sm z-20 max-h-[200px] overflow-y-auto scrollbar-hide">
                        <li
                            className={`text-[0.875rem] font-medium leading-[0.875rem] cursor-pointer whitespace-nowrap ${selectedTravelDay === null ? 'text-[#606060]' : 'text-black'}`}
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedTravelDay(null);
                                setIsSortOpen(false);
                            }}
                        >
                            전체
                        </li>
                        {filterOptions?.travelDays.map((days) => (
                            <li
                                key={days}
                                className={`text-[0.875rem] font-medium leading-[0.875rem] cursor-pointer whitespace-nowrap ${selectedTravelDay === days ? 'text-[#606060]' : 'text-black'}`}
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setSelectedTravelDay(days);
                                    setIsSortOpen(false);
                                }}
                            >
                                {days}일
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
}