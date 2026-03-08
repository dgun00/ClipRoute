export interface CourseListResult {
  courseList: Course[];
  totalElements: number;
  sort: string;
  seed: number;
  sliceInfo: {
    currentPage: number;
    size: number;
    hasNext: boolean;
  };
}

export interface Course {
  courseId: number;
  yt_video_id: string;
  channelName: string;
  videoTitle: string;
  travelDays: number;
  regionId: number;
  regionName: string;
  isRecommended: boolean;
  isRep: boolean;
  isCustomized: boolean;
  deletedAt: string | null;
  thumbnailUrl?: string; // API 응답에는 없지만 호환성을 위해 유지 (optional)
}

export interface CourseQueryParams {
  regionId?: number | null;
  travelDays?: number | null;
  sort?: string;
  pageSize?: number;
  lastCourseId?: number;
  lastValue?: string;
}