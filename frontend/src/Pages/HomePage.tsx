import { useState } from 'react';
import Header from '../components/common/Header';
import { CourseInputCard } from '../components/CourseInputCard';
import DestinationModal from '../components/modals/DestinationModal';
import DateSelectModal from '../components/modals/DateSelectModal';
import VideoCard from '../components/VideoCard';
import bellicon from "../assets/icons/bell-icon.svg";
import logoicon from "../assets/icons/logo-icon.svg";

interface Destination {
  regionId: number;
  regionName: string;
  imageUrl: string;
}

interface DateRange {
  startDate: Date | null;
  endDate: Date | null;
}

const mockVideos = [
  {
    id: 1,
    title: '[제날멍]\n영상 제목이 들어갑니다.',
    region: '여행지',
    duration: '1박 2일'
  },
  {
    id: 2,
    title: '[제날멍]\n영상 제목이 들어갑니다.',
    region: '여행지',
    duration: '2박 3일'
  },
  {
    id: 3,
    title: '[제날멍]\n영상 제목이 들어갑니다.',
    region: '여행지',
    duration: '2박 3일'
  },
  {
    id: 4,
    title: '[제날멍]\n영상 제목이 들어갑니다.',
    region: '여행지',
    duration: '2박 3일'
  }
];

const HomePage = () => {
  const [isDestinationModalOpen, setIsDestinationModalOpen] = useState(false);
  const [isDateModalOpen, setIsDateModalOpen] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null);
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange | null>(null);

  // 여행 일수 계산 함수
  const calculateTravelDays = (dateRange: DateRange | null): number | null => {
    if (!dateRange?.startDate || !dateRange?.endDate) return null;
    const days = Math.ceil(
      (dateRange.endDate.getTime() - dateRange.startDate.getTime()) / (1000 * 60 * 60 * 24)
    ) + 1;
    return days;
  };

  return (
    <div className="bg-white min-h-screen">
      <Header
        left={<img src={logoicon} alt="logo"/>}
        right={<img src={bellicon} alt="notifications" className='w-5 h-5'/>}
      />

      <main className='px-5 pt-6'>
        <h1 className="font-sans font-[700] text-[1rem] pb-[15px]">
  대표 여행 유튜버들의 국내 여행 코스를 한 눈에!
</h1>

        <CourseInputCard 
          region={selectedDestination} 
          dateRange={selectedDateRange}
          onLocationClick={() => setIsDestinationModalOpen(true)}
          onDateClick={() => setIsDateModalOpen(true)}
        />

        <div className="flex justify-end mt-4">
          <button 
            className="px-5 py-3 rounded-xl font-bold bg-[#42BCEB] text-white active:opacity-80 transition-all"
            onClick={() => {
              console.log("선택된 여행지:", selectedDestination);
              console.log("선택된 날짜:", selectedDateRange);
              console.log("여행 일수:", calculateTravelDays(selectedDateRange));
            }}>
            코스 생성하기
          </button>
        </div>

        <DestinationModal 
          isOpen={isDestinationModalOpen}
          onClose={() => setIsDestinationModalOpen(false)}
          onSelect={(dest) => {
            setSelectedDestination(dest);
            setIsDestinationModalOpen(false);
          }} 
        />

        <DateSelectModal
          isOpen={isDateModalOpen}
          onClose={() => setIsDateModalOpen(false)}
          onConfirm={(dateRange) => {
            setSelectedDateRange(dateRange);
          }}
        />

        
        <div className="mt-12 pt-8 border-t border-gray-100">
          <h2 className="font-bold text-[18px]">대표 지역 / 인기 영상 속 코스</h2>
          <p className="text-[14px] text-gray-400 mt-1 mb-5">
            현재 가장 인기 있는 대표 지역은 제주, 부산입니다.
          </p>

         
          <div className="grid grid-cols-1 gap-4 pb-8">
            {mockVideos.map((video) => (
              <VideoCard
                key={video.id}
                title={video.title}
                region={video.region}
                duration={video.duration}
                onClick={() => console.log('영상 클릭:', video.id)}
              />
            ))}
          </div>
        </div>
      </main>
    </div>
  );
};

export default HomePage;