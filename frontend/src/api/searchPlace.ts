import api from "./axios";
import type { PlaceSearchResponse } from "../types/searchPlace";

export interface PlaceSearchParams {
    regionId?: number;
    category?: string;
    minLat?: number;
    maxLat?: number;
    minLng?: number;
    maxLng?: number;
    page?: number;
    pageSize?: number;
}

// 장소 추가 API (필터 및 뷰포트 기반)
// GET /api/v1/places/search
export const fetchPlaceSearch = async (params: PlaceSearchParams): Promise<PlaceSearchResponse | null> => {
    try {
        const {
            regionId,
            category,
            minLat, maxLat, minLng, maxLng,
            page = 0,
            pageSize = 10
        } = params;

        // 유효한 파라미터만 전송
        const queryParams: any = {
            page,
            pageSize
        };

        if (regionId) queryParams.regionId = regionId;
        if (category) queryParams.category = category;
        if (minLat) queryParams.minLat = minLat;
        if (maxLat) queryParams.maxLat = maxLat;
        if (minLng) queryParams.minLng = minLng;
        if (maxLng) queryParams.maxLng = maxLng;

        const response = await api.get<PlaceSearchResponse>('/api/v1/places/search', {
            params: queryParams
        });

        console.log('✅ [장소 검색 성공]', response.data);
        return response.data;
    } catch (error) {
        console.error('❌ 장소 검색 실패:', error);
        return null;
    }
};
