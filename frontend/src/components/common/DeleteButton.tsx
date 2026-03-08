
interface DeleteButtonProps {
    count: number;
    onClick: () => void;
    isLoading?: boolean;
    className?: string; // 위치 조정
}

export default function DeleteButton({
    count,
    onClick,
    isLoading = false,
    className = "",
}: DeleteButtonProps) {
    if (count === 0 && !isLoading) return null;

    return (
        <button
            onClick={onClick}
            disabled={isLoading || count === 0}
            className={`fixed bottom-5 left-1/2 -translate-x-1/2 w-[22.0625rem] h-[3.125rem] flex items-center justify-center gap-2 rounded-[0.625rem] bg-[#42BCEB] text-white font-bold px-5 py-2 active:opacity-70 disabled:opacity-50 transition-all z-50 shadow-lg ${className}`}
        >
            {isLoading ? "삭제 중..." : "삭제하기"}
        </button>
    );
}
