export interface Place {
  coursePlaceId: number;
  visitOrder: number;
  placeId: number;
  placeName: string;
  placeCategory: string;
  address: string;
  lat: number;
  lng: number;
  timestamp: number;
}

export interface Itinerary {
  visitDay: number;
  places: Place[];
}

export interface CourseDetailResult {
  courseId: number;
  videoTitle: string;
  videoUrl: string;
  thumbnailUrl: string;
  channelName: string;
  regionId: number;
  regionName: string;
  isScrapped: boolean;
  travelStatus: 'BEFORE' | 'DURING' | 'AFTER';
  itineraries: Itinerary[];
}

export interface CourseDetailResponse {
  isSuccess: boolean;
  code: string;
  message: string;
  result: CourseDetailResult;
}


export interface MapPlace {
  id: number;
  day: number;
  order: number;
  name: string;
  category: string;
  address: string;
  lat: number;
  lng: number;
  timestamp?: number;
}


export interface ScrapResult {
  newCourseId: number; // 스크랩 시 생성된 내 코스 ID
  originalCourseId: number;
  isScrapped: boolean;
  travelStatus: "BEFORE" | "AFTER";
  startDate: string | null;  //여행 시작, 종료 날짜 null 디폴트
  endtDate: string | null;
  createdAt: string;
}
