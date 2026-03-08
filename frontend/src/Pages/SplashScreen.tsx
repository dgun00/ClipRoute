import { useEffect, useState } from 'react';
import logoSymbol from '../assets/icons/Splash/splash-logo-icon.svg';
import logoText from '../assets/icons/Splash/logo-text-white-icon.svg';

interface SplashScreenProps {
    onFinish: () => void;
}

const SplashScreen = ({ onFinish }: SplashScreenProps) => {
    const [isFadingOut, setIsFadingOut] = useState(false);

    useEffect(() => {
        // 1.5초 뒤에 페이드 아웃 시작
        const fadeTimer = setTimeout(() => {
            setIsFadingOut(true);
        }, 1500);

        // 페이드 아웃(1초) 끝난 뒤 onFinish 호출
        const finishTimer = setTimeout(() => {
            onFinish();
        }, 2500);

        return () => {
            clearTimeout(fadeTimer);
            clearTimeout(finishTimer);
        };
    }, [onFinish]);

    return (
        <div
            className={`fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#42BCEB] transition-opacity duration-1000 ${isFadingOut ? 'opacity-0 pointer-events-none' : 'opacity-100'
                }`}
        >
            <div className="flex flex-col items-center gap-4">
                <img
                    src={logoSymbol}
                    alt="ClipRoute Logo Symbol"
                    className="w-[2.5rem]"
                />
                <img
                    src={logoText}
                    alt="ClipRoute Text"
                    className="w-[10rem]"
                />
            </div>
        </div>
    );
};

export default SplashScreen;
