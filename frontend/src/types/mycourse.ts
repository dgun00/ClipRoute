import type { ApiResponse } from "../types/common";

// --- 기존 타입 유지 ---
export interface CourseItem {
    courseId: number;
    memberCourseId: number;
    courseTitle: string;
    regionName: string;
    regionImageUrl: string;
    thumbnailUrl: string;
    startDate: string | null;
    endDate: string | null;
    travelDays: number;
    travelStatus: "BEFORE" | "ONGOING" | "COMPLETED" | "AFTER";
    placeCount: number;
    createdAt: string;
    yt_video_id?: string; // 유튜브 비디오 ID (썸네일 생성용)
}

export interface MyCoursesResult {
    courseList: CourseItem[];
    sort: string;
    sliceInfo: {
        currentPage: number;
        size: number;
        hasNext: boolean;
    };
}

export type FetchMyCoursesResponse = ApiResponse<MyCoursesResult>;

export interface DeleteMyCoursesResponse {
    isSuccess: boolean;
    code: string;
    message: string;
}

// --- 나의 코스 상세 조회 (Response) ---
export interface MyCoursePlace {
    visitOrder: number;
    coursePlaceId: number;
    placeId: number;
    placeName: string;
    placeCategory: string;
    address: string;
    lat: number;
    lng: number;
    timestamp: number | null;
    deletedAt: string | null;
}

export interface MyCourseItinerary {
    visitDay: number;
    places: MyCoursePlace[];
}

export interface MyCourseDetail {
    courseId: number;
    videoTitle: string;
    yt_video_id: string;
    channelName: string;
    regionId: number;
    regionName: string;
    isScrapped: boolean;
    travelStatus: "BEFORE" | "ONGOING" | "COMPLETED" | "AFTER";
    courseTitle: string;
    startDate: string;
    endDate: string;
    itineraries: MyCourseItinerary[];
}

export type MyCourseDetailResponse = ApiResponse<MyCourseDetail>;


// --- 나의 코스 수정 (Request) ---
// 편집 모드 저장 시 사용되는 타입 정의

export interface UpdateMyCourseItem {
    coursePlaceId?: number; // 기존 장소일 경우 필수 (placeId는 생략 가능하거나 무시됨)
    placeId?: number;       // 새로 추가된 장소일 경우 필수 (coursePlaceId 없음)
    // visitOrder?: number;    // 서버에서 배열 순서로 자동 매핑하므로 제거
}

export interface UpdateMyCourseItinerary {
    visitDay: number;
    items: UpdateMyCourseItem[]; // places가 아니라 items임
}

export interface UpdateMyCourseDetailRequest {
    courseTitle: string;
    startDate: string | null;
    endDate: string | null;
    travelStatus: "BEFORE" | "ONGOING" | "COMPLETED" | "AFTER";
    itineraries: UpdateMyCourseItinerary[];
}


// --- 필터 옵션 ---
export interface FilterOptionResult {
    regions: {
        id: number;
        name: string;
    }[];
    travelDays: number[];
    travelStatuses: string[];
}

export type FilterOptionResponse = ApiResponse<FilterOptionResult>;