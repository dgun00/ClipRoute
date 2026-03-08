export interface SearchedPlace {
    placeId: number;
    regionId: number;
    placeName: string;
    category: string;
    address: string;
    lat: number;
    lng: number;
}

export interface Viewport {
    minLat: number;
    maxLat: number;
    minLng: number;
    maxLng: number;
}

export interface SliceInfo {
    currentPage: number;
    size: number;
    hasNext: boolean;
}

export interface PlaceSearchResult {
    places: SearchedPlace[];
    viewport: Viewport;
    sliceInfo: SliceInfo;
    totalInViewport: number;
}

export interface PlaceSearchResponse {
    isSuccess: boolean;
    code: string;
    message: string;
    result: PlaceSearchResult;
}
