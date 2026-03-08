import { useQuery } from '@tanstack/react-query';
import { fetchRegions } from '../../api/regions';
import type { Region } from '../../types/region';
import Header from '../common/Header';
import closeIcon from '../../assets/icons/close-icon.svg';


interface DestinationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (region: Region) => void;
}

const DestinationModal = ({ isOpen, onClose, onSelect }: DestinationModalProps) => {
  const { data } = useQuery({
    queryKey: ['regions'],
    queryFn: fetchRegions,
    enabled: isOpen,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });

  if (!isOpen) return null;

  const regions = data?.result.regions || [];


  regions.forEach(r => {
    if (!r.imageUrl) console.warn(`[Region ${r.regionId}] Image URL is missing!`);
    else console.log(`[Region ${r.regionId}] Image URL:`, r.imageUrl);
  });

  const handleSelectRegion = (region: Region) => {
    onSelect(region);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-white flex flex-col animate-modal-up">
      <div className="w-full h-full max-w-md mx-auto flex flex-col">
        <Header
          center={
            <h2 className="text-[1.125rem] font-bold">
              여행지 선택
            </h2>
          }
          right={
            <button
              onClick={onClose}
              className="p-2 rounded-full hover:bg-gray-100"
              aria-label="닫기"
            >
              <img
                src={closeIcon}
                className="w-[1.5rem] h-[1.5rem]"
                alt=""
              />
            </button>
          }
        />



        <div className="px-6 pt-4 pb-10 flex-1 overflow-y-auto">
          <div className="grid grid-cols-3 gap-y-10 gap-x-2">
            {regions.map((region) => (
              <button
                key={region.regionId}
                onClick={() => handleSelectRegion(region)}
                className="flex flex-col items-center group active:scale-95 transition-transform"
              >
                <div className="w-[4.6875rem] h-[4.6875rem] rounded-full overflow-hidden mb-3 border border-gray-100 shadow-sm">
                  <img
                    // S3 URL 구조: https://cliproute-images.s3.ap-northeast-2.amazonaws.com/images/regions/{region_name}.jpg
                    src={`https://cliproute-images.s3.ap-northeast-2.amazonaws.com/images/regions/${region.regionName}.jpg`}
                    alt={region.regionName}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.onerror = null;
                      e.currentTarget.src = "https://placehold.co/80?text=No+Image";
                    }}
                  />
                </div>
                <span className="text-sm font-semibold text-black">
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