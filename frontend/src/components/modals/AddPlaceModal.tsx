import { useState, useEffect } from 'react';
import GoogleMap from '../GoogleMap';
import backIcon from '../../assets/icons/back-icon.svg';
import { fetchPlaceSearch } from '../../api/searchPlace';
import CategoryFilter from '../common/CategoryFilter';
import SearchPlaceBottomSheet from './SearchPlaceBottomSheet';

interface AddPlaceModalProps {
    isOpen: boolean;
    onClose: () => void;
    onPlaceSelect?: (place: any) => void;
    regionId?: number;
    regionName?: string;
}

const AddPlaceModal = ({ isOpen, onClose, onPlaceSelect, regionId, regionName }: AddPlaceModalProps) => {
    const [tempPlaces, setTempPlaces] = useState<any[]>([]);
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [selectedPlace, setSelectedPlace] = useState<any | null>(null);

    useEffect(() => {
        setSelectedPlace(null);
    }, [tempPlaces, isOpen]);

    useEffect(() => {
        if (isOpen && regionId) {
            const loadPlaces = async () => {
                const params: any = {
                    regionId: regionId,
                    page: 0,
                    pageSize: 20
                };

                if (selectedCategory !== "all") {
                    params.category = selectedCategory;
                }

                console.log(`[AddPlaceModal] 장소 검색 (Category: ${selectedCategory})`);
                const response = await fetchPlaceSearch(params);

                if (response?.result) {
                    setTempPlaces(response.result.places);
                }
            };
            loadPlaces();
        }
    }, [isOpen, regionId, selectedCategory]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 bg-white flex flex-col animate-modal-up">
            {/* 전체 지도 영역 */}
            <div className="absolute inset-0 w-full h-full">
                <GoogleMap
                    places={tempPlaces.map(p => ({
                        ...p,
                        id: p.placeId,
                        name: p.placeName,
                    }))}
                    mode="add"
                />
            </div>

            {/* 상단 플로팅 헤더 (카드 형태) */}
            <div className="absolute top-5 left-4 right-4 z-10 flex flex-col gap-3">
                <div className="bg-white rounded-xl border border-[#42BCEB] p-3 flex items-center gap-3">
                    <button onClick={onClose} className="p-1 -ml-1">
                        <img src={backIcon} alt="뒤로가기" className="w-4 h-4" />
                    </button>
                    <span className="font-bold text-lg">{regionName ? `${regionName} 장소 리스트` : "장소 리스트"}</span>
                </div>

                {/* 카테고리 필터 */}
                <CategoryFilter
                    selectedCategory={selectedCategory}
                    onSelectCategory={setSelectedCategory}
                />
            </div>

            {/* 하단 장소 검색 시트 (분리된 컴포넌트) */}
            <SearchPlaceBottomSheet
                places={tempPlaces}
                selectedPlace={selectedPlace}
                onSelect={(place) => {
                    if (selectedPlace?.placeId === place.placeId) {
                        setSelectedPlace(null);
                    } else {
                        setSelectedPlace(place);
                    }
                }}
                onAdd={() => {
                    if (onPlaceSelect && selectedPlace) {
                        onPlaceSelect(selectedPlace);
                    }
                }}
                regionName={regionName}
            />

            <style>{`
                @keyframes modalUp { 
                  from { transform: translateY(100%); } 
                  to { transform: translateY(0); } 
                }
                .animate-modal-up { 
                  animation: modalUp 0.3s cubic-bezier(0.33, 1, 0.68, 1) forwards; 
                }
                @keyframes slideUp {
                    from { transform: translateY(100%); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                .animate-slide-up {
                    animation: slideUp 0.4s ease-out 0.2s forwards;
                    opacity: 0; /* 초기 상태 숨김 */
                }
            `}</style>
        </div>
    );
};

export default AddPlaceModal;
