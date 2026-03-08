import { useState, useEffect } from "react";
import mappinIcon from "../../assets/icons/mappin-icon.svg";
import calendarIcon from "../../assets/icons/calendar-icon.svg";

interface CourseInfoEditModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSave: (newTitle: string, newDate: string) => void;
    initialTitle: string;
    initialDate: string;
    onDateClick?: () => void;
}

export default function CourseInfoEditModal({
    isOpen,
    onClose,
    onSave,
    initialTitle,
    initialDate,
    onDateClick,
}: CourseInfoEditModalProps) {
    const [title, setTitle] = useState(initialTitle);
    const [date, setDate] = useState(initialDate);

    // 모달이 열릴 때마다 초기값 동기화
    useEffect(() => {
        if (isOpen) {
            setTitle(initialTitle);
            setDate(initialDate);
        }
    }, [isOpen, initialTitle, initialDate]);

    // Note: 외부 클릭 자동 저장은 제거하고, 하단 버튼으로 명시적 저장 수행.
    // Enter 키 저장은 편의를 위해 유지.

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex flex-col items-center pt-[12px] bg-black/50">
            {/* 배경 클릭 시 닫기 (취소) */}
            <div className="absolute inset-0 z-0" onClick={onClose} />

            {/* 상단 팝업 카드 */}
            <div className="relative z-10 flex flex-col justify-center items-center gap-[0.625rem] w-[22.0625rem] px-[0.9375rem] py-[0.875rem] bg-white rounded-[0.9375rem] border border-[#42BCEB] shadow-sm animate-fade-in">
                {/* 제목 입력 */}
                <div className="w-full flex items-center gap-[0.625rem]">
                    <img src={mappinIcon} alt="location" className="w-5 h-5 flex-shrink-0" />
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="flex-1 text-[15px] font-bold text-[#333] outline-none placeholder-gray-300 bg-transparent truncate"
                        placeholder="코스 제목"
                        autoFocus
                        onKeyDown={(e) => {
                            if (e.key === "Enter") {
                                onSave(title, date);
                                onClose(); // 모달 닫기
                            }
                        }}
                    />
                </div>

                {/* 구분선 */}
                <div className="w-full h-[1px] bg-[#EEEEEE]" />

                {/* 날짜 입력 (읽기 전용, 클릭 시 달력 모달 호출) */}
                <div
                    className="w-full flex items-center gap-[0.625rem] cursor-pointer"
                    onClick={onDateClick}
                >
                    <img src={calendarIcon} alt="calendar" className="w-5 h-5 flex-shrink-0" />
                    <input
                        type="text"
                        value={date}
                        readOnly
                        className="flex-1 text-[13px] font-medium text-[#333] outline-none placeholder-gray-300 bg-transparent truncate cursor-pointer pointer-events-none"
                        placeholder="YYYY.MM.DD - MM.DD"
                    />
                </div>
            </div>

            {/* 하단 저장하기 버튼 */}
            <div className="absolute bottom-8 w-[90%] max-w-[22rem] z-10">
                <button
                    onClick={() => onSave(title, date)} // 버튼 클릭 시 저장
                    className="w-full h-[3.25rem] bg-[#42BCEB] rounded-[0.625rem] text-white text-[1.125rem] font-bold shadow-md active:bg-[#3aa8d4] transition-colors"
                >
                    저장하기
                </button>
            </div>
        </div>
    );
}
