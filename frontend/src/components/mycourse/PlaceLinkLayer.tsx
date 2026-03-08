import { useEffect } from 'react';
import PlaceItem from '../course/PlaceItem';
import youtubeIcon from '../../assets/icons/social/youtube-icon.svg';
import naverIcon from '../../assets/icons/social/naver-icon.svg';

interface PlaceLinkLayerProps {
    place: any;
    rect: DOMRect | null;
    onClose: () => void;
    showYoutube?: boolean; // 유튜브 버튼 표시 여부 (기본값: true)
    showNaver?: boolean;   // 네이버 버튼 표시 여부 (기본값: true)
}

const PlaceLinkLayer = ({ place, rect, onClose, showYoutube = true, showNaver = true }: PlaceLinkLayerProps) => {
    useEffect(() => {
        // Esc 키로 닫기 및 스크롤 방지
        const handleEsc = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };

        document.body.style.overflow = 'hidden';
        window.addEventListener('keydown', handleEsc);

        return () => {
            document.body.style.overflow = '';
            window.removeEventListener('keydown', handleEsc);
        };
    }, [onClose]);

    if (!place || !rect) return null;

    // 외부 링크 연결 핸들러
    const handleLink = (type: 'youtube' | 'naver') => {
        let url = '';
        // 검색어: 장소 이름 + (주소 or 카테고리)
        const query = encodeURIComponent(`${place.name} ${place.address || ''}`);

        if (type === 'youtube') {
            // 유튜브: 비디오 ID가 있으면 해당 영상으로 이동, 없으면 검색 결과
            if (place.yt_video_id) {
                url = `https://www.youtube.com/watch?v=${place.yt_video_id}`;
            } else {
                url = `https://m.youtube.com/results?search_query=${query}`;
            }
        } else {
            // 네이버 지도 (기존 로직 유지)
            if (place.lat && place.lng) {
                const lat = place.lat;
                const lng = place.lng;
                const name = encodeURIComponent(place.name);

                // 1. 앱 실행 스키마
                const appUrl = `nmap://place?lat=${lat}&lng=${lng}&name=${name}&appname=ClipRoute`;

                // 2. 웹 폴백 URL
                const webUrl = `https://map.naver.com/v5/search/${name}?c=${lng},${lat},15,0,0,0,dh`;

                // 모바일 기기인지 확인
                const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

                if (isMobile) {
                    // 앱 실행 시도 (Deep Link)
                    const clickedAt = +new Date();

                    // iframe을 통한 앱 실행 시도
                    const iframe = document.createElement('iframe');
                    iframe.style.visibility = 'hidden';
                    iframe.src = appUrl;
                    document.body.appendChild(iframe);

                    // 1.5초 후에도 앱으로 이동하지 않았다면 웹으로 이동
                    setTimeout(() => {
                        document.body.removeChild(iframe);
                        if (+new Date() - clickedAt < 2000) {
                            window.open(webUrl, '_blank');
                        }
                    }, 1500);
                } else {
                    // 데스크탑에서는 바로 웹으로 이동
                    window.open(webUrl, '_blank');
                }

                return; // 여기서 함수 종료 (window.open 중복 방지)
            } else {
                // 좌표 없는 경우 단순 검색
                url = `https://m.map.naver.com/search2/search.naver?query=${query}`;
            }
        }

        window.open(url, '_blank');
    };

    return (
        <div
            className="fixed inset-0 z-[60] flex flex-col"
            onClick={onClose}
        >
            {/* 배경 Dim 처리 */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-[1px] animate-fade-in transition-opacity" />

            {/* 아이템 위치에 복제되어 띄워질 컨테이너 */}
            <div
                className="absolute z-10"
                style={{
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    // 높이는 내용물에 따라 자동 조절
                }}
                onClick={(e) => e.stopPropagation()} // 아이템 영역 클릭 시 닫히지 않음
            >
                {/* 하이라이트된 PlaceItem */}
                <div className="flex flex-col items-start gap-[0.625rem] pt-[0.025rem] pb-[0.625rem] pl-[0.375rem] pr-0 rounded-[0.3125rem] bg-white w-full h-[4.5rem] shadow-2xl scale-[1.02] transition-transform duration-200">
                    <div className="w-full">
                        <PlaceItem place={place} isEditMode={false} />
                    </div>
                </div>

                {/* 링크 연결 버튼들 (우측 상단 배치) */}
                <div className={`absolute right-0 flex flex-col items-end gap-3 pointer-events-auto pb-4 
                    ${!showYoutube ? '-top-[3.5rem]' : '-top-[7.5rem]'}`}
                >
                    {/* YouTube Button */}
                    {showYoutube && (
                        <div
                            className="flex items-center gap-3 group cursor-pointer hover:opacity-90 active:scale-95 transition-all"
                            onClick={() => handleLink('youtube')}
                        >
                            <span className="text-white text-[0.75rem] font-normal drop-shadow-md">유튜브로 연결하기</span>
                            <img src={youtubeIcon} alt="YouTube" className="w-[2.8125rem] h-[2.8125rem] shadow-lg rounded-full" />
                        </div>
                    )}

                    {/* Naver Button */}
                    {showNaver && (
                        <div
                            className="flex items-center gap-3 group cursor-pointer hover:opacity-90 active:scale-95 transition-all"
                            onClick={() => handleLink('naver')}
                        >
                            <span className="text-white text-[0.75rem] font-normal drop-shadow-md">네이버로 연결하기</span>
                            <img src={naverIcon} alt="Naver" className="w-[2.8125rem] h-[2.8125rem] rounded-full" />
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default PlaceLinkLayer;
