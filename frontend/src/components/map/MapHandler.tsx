import { useEffect } from 'react';
import { useMap, useMapsLibrary } from '@vis.gl/react-google-maps';

interface Place {
    id: number; //지도 위 표시된 Marker 고유 식별자
    lat: number;
    lng: number;
    [key: string]: any;
}

interface MapHandlerProps {
    places: Place[];
    selectedPlaceId?: number | null;
}

const MapHandler = ({ places, selectedPlaceId }: MapHandlerProps) => {
    const map = useMap();
    const coreLib = useMapsLibrary('core'); // google.maps 로딩 대기

    // 장소 목록이 변경되면 모든 장소가 보이도록 fitBounds
    useEffect(() => {
        if (!map || !coreLib || places.length === 0) return;

        // 이미 선택된 장소가 있다면 그쪽으로 이동하는 로직이 우선
        if (selectedPlaceId) return;

        const bounds = new google.maps.LatLngBounds();
        places.forEach((place) => {
            bounds.extend({ lat: place.lat, lng: place.lng });
        });

        map.fitBounds(bounds);

        const listener = google.maps.event.addListener(map, "idle", () => {
            if (map.getZoom()! > 16) map.setZoom(16);
            google.maps.event.removeListener(listener);
        });

    }, [map, coreLib, places]);

    // 선택된 장소가 변경되면 해당 장소로 이동 (panTo & zoom)
    useEffect(() => {
        if (!map || !selectedPlaceId) return;

        const selectedPlace = places.find(p => p.id === selectedPlaceId);
        if (selectedPlace) {
            map.panTo({ lat: selectedPlace.lat, lng: selectedPlace.lng });
            map.setZoom(15);
        }
    }, [map, selectedPlaceId, places]);

    return null;
};

export default MapHandler;
