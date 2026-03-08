import { useState, useCallback } from 'react';
import {
  APIProvider,
  Map,
  AdvancedMarker,
} from '@vis.gl/react-google-maps';
import MapPin from './map/MapPin';
import MapLabel from './map/MapLabel';
import PlaceBadge from './map/PlaceBadge';
import MapHandler from './map/MapHandler';

interface Place {
  id: number;
  lat: number;
  lng: number;
  order?: number;
  name: string;
  category?: string;
  [key: string]: any;
}

interface GoogleMapProps {
  places: Place[];
  mode?: 'view' | 'add'; // view: 보기 모드일 때 , add: 검색 결과 추가 모드일 때
}

// 실제 지도를 렌더링하고 조작하는 내부 컴포넌트
const MapInner = ({ places, mode = 'view' }: GoogleMapProps) => {
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const handleMarkerClick = useCallback(
    (place: Place) => {
      setSelectedId(place.id);

    },
    []
  );

  return (
    <Map
      defaultCenter={{ lat: 37.5665, lng: 126.9780 }} // 기본값: 서울
      defaultZoom={10}
      mapId="YOUR_MAP_ID"
      disableDefaultUI={true}
      gestureHandling={'greedy'}
      onClick={() => setSelectedId(null)}
    >
      <MapHandler places={places} selectedPlaceId={selectedId} />

      {places.map((place) => (
        <AdvancedMarker
          key={place.id}
          position={{ lat: place.lat, lng: place.lng }}
          onClick={() => handleMarkerClick(place)}
          zIndex={selectedId === place.id ? 10 : 1}
        >
          {mode === 'add' ? (
            <PlaceBadge name={place.name} category={place.category || '기타'} />
          ) : (
            <div className="relative flex flex-col items-center">
              {selectedId === place.id && <MapLabel name={place.name} />}
              <MapPin order={place.order || 0} />
            </div>
          )}
        </AdvancedMarker>
      ))}
    </Map>
  );
};

// GoogleMap 컴포넌트 (Provider 역할)
const GoogleMap = ({ places, mode = 'view' }: GoogleMapProps) => {
  return (
    <APIProvider apiKey={import.meta.env.VITE_GOOGLE_MAPS_API_KEY}>
      <div className="w-full h-full min-h-[500px]">
        <MapInner places={places} mode={mode} />
      </div>
    </APIProvider>
  );
};

export default GoogleMap;