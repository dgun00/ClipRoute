import { useEffect, useState } from 'react';

const CustomSpinner = () => (
  <div 
    className="relative w-14 h-14 animate-spin"
    style={{ animationDuration: '1.2s' }} 
  >
    {[...Array(8)].map((_, i) => (
      <div
        key={i}
        className="absolute left-1/2 top-0 w-[4px] h-[14px] bg-[#42BCEB] rounded-full origin-[2px_28px]"
        style={{
          transform: `translateX(-50%) rotate(${i * 45}deg)`,
          opacity: i === 0 ? 1 : 1 - i * 0.12, 
        }}
      />
    ))}
  </div>
);

const LoadingPage = () => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((prev) => (prev < 100 ? prev + 1 : 100));
    }, 30);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="w-screen h-screen bg-white flex flex-col px-[24px] py-[60px]">
      <div className="flex-1 flex flex-col items-center justify-center">
        <div className="mb-8">
          <CustomSpinner />
        </div>
        
        <h1 className="text-[20px] font-bold text-[#333] mb-2 text-center">
          코스 생성 중...
        </h1>
        <p className="text-[14px] text-gray-400">곧 코스 결과를 보여드릴게요</p>

        <div className="w-full max-w-[280px] h-[6px] bg-[#E5E5E5] rounded-full mt-10 overflow-hidden">
          <div 
            className="h-full bg-[#42BCEB] transition-all duration-300 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};

export default LoadingPage;