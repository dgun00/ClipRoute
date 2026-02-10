import { useState } from 'react';
import PlaceItem from './PlaceItem';

const PlaceBottomSheet = ({ places }: any) => {
  const [isOpen, setIsOpen] = useState(false);
  const days = Array.from(new Set(places.map((p: any) => p.day))).sort();

  return (
    <div 
      className="fixed bottom-0 left-0 right-0 z-20 bg-white rounded-t-[30px] shadow-[0_-8px_20px_rgba(0,0,0,0.1)] transition-transform duration-500 ease-in-out"
      style={{ height: '65vh', transform: isOpen ? 'translateY(0)' : 'translateY(calc(65vh - 80px))' }}
    >
      <div className="flex flex-col items-center py-4 cursor-pointer" onClick={() => setIsOpen(!isOpen)}>
        <div className="w-[40px] h-[4px] bg-[#E5E5E5] rounded-full mb-3" />
        <h2 className="text-[18px] font-bold text-[#333] px-5 w-full text-left">영상 속 장소 및 코스 정리</h2>
      </div>
      <div className="px-5 pb-10 overflow-y-auto h-full scrollbar-hide">
        {days.map((day: any) => (
          <div key={day} className="mb-6">
            <div className="flex items-center gap-2 mb-2 text-[#42BCEB] font-bold italic">
              <span>Day {day}</span>
              <div className="flex-1 h-[1px] bg-gray-100" />
            </div>
            {places.filter((p: any) => p.day === day).map((place: any) => (
              <PlaceItem key={place.id} place={place} />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PlaceBottomSheet;