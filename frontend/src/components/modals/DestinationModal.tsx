import { useState } from 'react';


export interface RegionData {
  regionId: number;
  regionName: string;
  imageUrl: string;
}

interface DestinationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (region: RegionData) => void;
}

// 목업 데이터
const mockDestinations: RegionData[] = [
  {
    regionId: 1,
    regionName: '강릉',
    imageUrl: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop'
  },
  {
    regionId: 2,
    regionName: '부산',
    imageUrl: 'https://images.unsplash.com/photo-1544781807-28d3c1a41d2d?w=400&h=400&fit=crop'
  },
  {
    regionId: 3,
    regionName: '제주',
    imageUrl: 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=400&fit=crop'
  }
];


const CloseIcon = () => (
  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const ChevronRightIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
  </svg>
);

const DestinationModal = ({ isOpen, onClose, onSelect }: DestinationModalProps) => {
  const [destinations] = useState<RegionData[]>(mockDestinations);

  
  if (!isOpen) return null;

  const handleSelect = (region: RegionData) => {
    onSelect(region);
    onClose();
  };

  return (
    
    <div className="fixed inset-0 z-50 bg-white flex flex-col animate-modal-up">
      
      
      <div className="w-full h-full max-w-md mx-auto flex flex-col">
                                                                        
        
        <div className="relative flex items-center justify-center h-16 shrink-0 border-b border-gray-50">
          <h2 className="text-[18px] font-bold text-black">여행지 선택</h2>
          <button 
            onClick={onClose}
            className="absolute right-5 w-6 h-6 flex items-center justify-center text-gray-800"
          >
            <CloseIcon />
          </button>
        </div>

        
        <div className="px-6 pt-5 pb-3 flex justify-end shrink-0">
          <button className="flex items-center text-[14px] text-black font-medium gap-0.5">
            전체 선택
            <ChevronRightIcon />
          </button>
        </div>

       
        <div className="px-6 pt-4 pb-10 flex-1 overflow-y-auto">
          <div className="grid grid-cols-3 gap-y-10 gap-x-2">
            {destinations.map((region) => (
              <button
                key={region.regionId}
                onClick={() => handleSelect(region)}
                className="flex flex-col items-center group active:scale-95 transition-transform"
              >
                
                <div className="w-[80px] h-[80px] rounded-full overflow-hidden mb-3 border border-gray-100 shadow-sm">
                  <img 
                    src={region.imageUrl} 
                    alt={region.regionName} 
                    className="w-full h-full object-cover"
                  />
                </div>
              
                <span className="text-[14px] font-medium text-gray-700">
                  {region.regionName}
                </span>
              </button>
            ))}
          </div>
        </div>

      </div>

     
      <style>{`
        @keyframes modalUp {
          from { transform: translateY(100%); }
          to { transform: translateY(0); }
        }
        .animate-modal-up {
          animation: modalUp 0.35s cubic-bezier(0.33, 1, 0.68, 1) forwards;
        }
      `}</style>
    </div>
  );
};

export default DestinationModal;