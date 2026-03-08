import type { CourseItem } from "../types/mycourse";

export const MOCK_COURSES: CourseItem[] = [
  {
    courseId: 1,
    memberCourseId: 1,
    courseTitle: "부산 여행",
    regionName: "부산",
    regionImageUrl: "",
    thumbnailUrl: "https://images.unsplash.com/photo-1634547986064-072d6551069d?q=80&w=200&auto=format&fit=crop",
    startDate: "2026.01.26",
    endDate: "2026.01.28",
    travelDays: 3,
    travelStatus: "ONGOING",
    placeCount: 4,
    createdAt: "2026-01-01T00:00:00Z"
  },
  {
    courseId: 2,
    memberCourseId: 2,
    courseTitle: "제목",
    regionName: "지역명",
    regionImageUrl: "",
    thumbnailUrl: "",
    startDate: "2026.1.20",
    endDate: "2026.1.22",
    travelDays: 3,
    travelStatus: "COMPLETED",
    placeCount: 5,
    createdAt: "2026-12-01T00:00:00Z"
  },
  {
    courseId: 3,
    memberCourseId: 3,
    courseTitle: "제목",
    regionName: "지역명",
    regionImageUrl: "",
    thumbnailUrl: "",
    startDate: "2026.1.15",
    endDate: "2026.1.16",
    travelDays: 2,
    travelStatus: "COMPLETED",
    placeCount: 3,
    createdAt: "2026-12-01T00:00:00Z"
  },
  {
    courseId: 4,
    memberCourseId: 4,
    courseTitle: "제목",
    regionName: "지역명",
    regionImageUrl: "",
    thumbnailUrl: "",
    startDate: "2025.12.10",
    endDate: "2025.12.12",
    travelDays: 3,
    travelStatus: "COMPLETED",
    placeCount: 3,
    createdAt: "2026-12-01T00:00:00Z"
  }
];
