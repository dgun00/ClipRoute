import closeIcon from "../../assets/icons/close-icon.svg";

interface DeleteConfirmModalProps {
    isOpen: boolean;
    onClose: () => void;
    onConfirm: () => void;
    title?: string;
    description?: string;
}

export default function DeleteConfirmModal({
    isOpen,
    onClose,
    onConfirm,
    title = "정말 삭제할까요?",
    description = "선택한 장소는 삭제 후 복구할 수 없어요.",
}: DeleteConfirmModalProps) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4">
            <div className="relative w-full max-w-[20rem] bg-white rounded-[1.25rem] p-6 shadow-lg animate-fade-in">
                {/* 닫기 버튼 */}
                <button
                    onClick={onClose}
                    className="absolute top-5 right-5 w-6 h-6 flex items-center justify-center"
                >
                    <img src={closeIcon} alt="close" />
                </button>

                {/* 제목 */}
                <h2 className="text-[1.125rem] font-bold text-[#333] mb-4 mt-2 text-left">
                    {title}
                </h2>

                <div className="w-full h-[1px] bg-[#EEEEEE] mb-4" />

                {/* 설명 */}
                <p className="text-[0.9375rem] text-[#333] mb-8 text-left whitespace-pre-line leading-relaxed">
                    {description}
                </p>

                {/* 버튼 영역 */}
                <div className="flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 h-[3rem] border border-[#CCCCCC] rounded-[0.625rem] text-[#333] font-medium active:bg-gray-50 transition-colors"
                    >
                        취소
                    </button>
                    <button
                        onClick={onConfirm}
                        className="flex-1 h-[3rem] bg-[#42BCEB] rounded-[0.625rem] text-white font-bold active:bg-[#3aa8d4] transition-colors"
                    >
                        삭제
                    </button>
                </div>
            </div>
        </div>
    );
}
