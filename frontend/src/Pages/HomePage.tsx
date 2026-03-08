import { useState } from 'react';
import NavigationLayout from '../layouts/NavigationLayout';
import Header from '../components/common/Header';
import { CourseInputCard } from '../components/CourseInputCard';
import DestinationModal from '../components/modals/DestinationModal';
import DateSelectModal from '../components/modals/DateSelectModal';
import VideoSection from '../components/VideoSection';
import bellicon from "../assets/icons/bell-icon.svg";
import logoicon from "../assets/icons/logo-icon.svg";
import backicon from "../assets/icons/back-icon.svg";
import { useNavigate } from "react-router-dom";


interface Destination {
  regionId: number;
  regionName: string;
  imageUrl: string;
}

interface DateRange {
  startDate: Date | null;
  endDate: Date | null;
}

const HomePage = () => {
  const [isDestinationModalOpen, setIsDestinationModalOpen] = useState(false);
  const [isDateModalOpen, setIsDateModalOpen] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState<Destination | null>(null);
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange | null>(null);
  const [shouldFilter, setShouldFilter] = useState(false);

  const calculateTravelDays = (dateRange: DateRange | null): number | null => {
    if (!dateRange?.startDate || !dateRange?.endDate) return null;
    const days = Math.ceil(
      (dateRange.endDate.getTime() - dateRange.startDate.getTime()) / (1000 * 60 * 60 * 24)
    );
    return days;
  };

  const navigate = useNavigate();


  const handleGenerateCourse = () => {
    if (!selectedDestination) return;

    const params = new URLSearchParams();
    params.append("regionId", String(selectedDestination.regionId));

    if (travelDays !== null) {
      params.append("travelDays", String(travelDays));
    }

    if (selectedDateRange?.startDate && selectedDateRange?.endDate) {
      // 날짜 포맷 (YYYY-MM-DD)
      const formatDate = (date: Date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };

      params.append("startDate", formatDate(selectedDateRange.startDate));
      params.append("endDate", formatDate(selectedDateRange.endDate));
    }

    console.log("이동 경로:", `/courses?${params.toString()}`);
    navigate(`/courses?${params.toString()}`);
  };

  const handleBackToMain = () => {
    setShouldFilter(false);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const isFilterMode = shouldFilter && (selectedDestination !== null || selectedDateRange !== null);
  const isAnyModalOpen = isDestinationModalOpen || isDateModalOpen;
  const travelDays = calculateTravelDays(selectedDateRange);


  const getFilterTitle = () => {
    const parts: string[] = [];
    if (selectedDestination) parts.push(selectedDestination.regionName);
    if (travelDays) parts.push(`${travelDays}박 ${travelDays + 1}일`);
    return parts.join(' ') + ' 여행 코스';
  };

  return (
    <NavigationLayout activeTab="home" hideNavigation={isAnyModalOpen}>
      <div className="bg-white min-h-screen">
        {/* 조건부 헤더 렌더링 */}
        {isFilterMode ? (
          <Header
            left={
              <div className="flex items-center gap-3">
                <button onClick={handleBackToMain}>
                  <img src={backicon} alt="back" className="w-4 h-4" />
                </button>
                <h1 className="font-bold text-base">{getFilterTitle()}</h1>
              </div>}

          />
        ) : (
          <Header
            left={<img src={logoicon} alt="logo" />}
            right={<img src={bellicon} alt="notifications" className='w-5 h-5' />}
          />
        )}

        <main className='px-5 pt-6 pb-24'>

          {!isFilterMode && (
            <h1 className="font-sans font-[700] text-[1rem] pb-[15px]">
              대표 여행 유튜버들의 국내 여행 코스를 한 눈에!
            </h1>
          )}


          <CourseInputCard
            region={selectedDestination}
            dateRange={selectedDateRange}
            onLocationClick={() => setIsDestinationModalOpen(true)}
            onDateClick={() => setIsDateModalOpen(true)}
          />


          {!isFilterMode && (
            <div className="flex justify-end mt-4">
              <button
                className="px-5 py-3 rounded-xl font-bold bg-[#42BCEB] text-white active:opacity-80 transition-all"
                onClick={handleGenerateCourse}
              >
                코스 생성하기
              </button>
            </div>
          )}

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

          {/* VideoSection */}
          <div id="video-section" className={isFilterMode ? 'mt-6' : ''}>
            <VideoSection
              destination={selectedDestination}
              travelDays={travelDays}
              shouldFilter={shouldFilter}
            />
          </div>
        </main>
      </div>
    </NavigationLayout>
  );
};

export default HomePage;