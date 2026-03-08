
import { useEffect } from "react";

interface DeleteModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title?: string;
    description?: string;
}

export default function DeleteModal({
    isOpen,
    onClose,
    onConfirm,
    title = "정말 삭제할까요?",
    description = "선택한 코스는 다시 찾아서 저장할 수 있어요.",
}: DeleteModalProps) {

    useEffect(() => {
        if (isOpen) {
            document.body.style.overflow = "hidden";
        } else {
            document.body.style.overflow = "unset";
        }
        return () => {
            document.body.style.overflow = "unset";
        };
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center px-4">

            <div
                className="absolute inset-0 bg-black/40 backdrop-blur-[2px]"
                onClick={onClose}
            />

            {/* 모달 컨텐츠 */}
            <div className="relative w-full max-w-[320px] bg-white rounded-[1.25rem] p-6 shadow-xl animate-scale-up">
                {/* 헤더 */}
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-[1.125rem] font-bold text-gray-900 leading-tight">
                        {title}
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-1 -mr-2 text-gray-400 hover:text-gray-600 active:opacity-70"
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 6L6 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <path d="M6 6L18 18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </button>
                </div>

                {/* 구분선 */}
                <div className="h-[1px] bg-gray-100 w-full mb-5" />

                {/* 설명 텍스트 */}
                <div className="mb-8">
                    <p className="text-[0.9375rem] text-gray-800 font-medium leading-relaxed break-keep">
                        {description}
                    </p>
                </div>

                {/* 버튼 영역 */}
                <div className="flex gap-2.5">
                    <button
                        onClick={onClose}
                        className="flex-1 py-3 rounded-xl border border-[#42BCEB] text-[#42BCEB] font-bold text-[1rem] active:bg-blue-50 transition-colors"
                    >
                        취소
                    </button>
                    <button
                        onClick={onConfirm}
                        className="flex-1 py-3 rounded-xl bg-[#42BCEB] text-white font-bold text-[1rem] shadow-sm active:bg-[#34a3ce] transition-colors"
                    >
                        삭제
                    </button>
                </div>
            </div>
        </div>
    );
}
