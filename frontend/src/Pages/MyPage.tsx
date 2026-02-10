export default function MyPage() {
  return (
    <div className="p-8 space-y-4">
      <h1 className="text-4xl font-bold text-primary-dark">
        Pretendard 폰트 테스트
      </h1>
      
      <div className="space-y-2">
        <p className="text-xl font-light text-gray-5">
          가벼운 텍스트 (font-light)
        </p>
        <p className="text-xl font-normal text-gray-2">
          보통 텍스트 (font-normal)
        </p>
        <p className="text-xl font-medium text-gray-2">
          중간 텍스트 (font-medium)
        </p>
        <p className="text-xl font-semibold text-gray-1">
          세미볼드 텍스트 (font-semibold)
        </p>
        <p className="text-xl font-bold text-gray-1">
          굵은 텍스트 (font-bold)
        </p>
        <p className="text-xl font-extrabold text-primary-dark">
          아주 굵은 텍스트 (font-extrabold)
        </p>
      </div>

      <div className="mt-8 p-4 bg-gray-8 rounded">
        <p className="text-gray-3">
          한글과 English 123 !@# 모두 테스트
        </p>
      </div>
    </div>
  )
}