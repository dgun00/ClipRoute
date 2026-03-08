import api from "./axios";
import type { FetchMyCoursesResponse, DeleteMyCoursesResponse, MyCourseDetail, MyCourseDetailResponse, FilterOptionResult, FilterOptionResponse, UpdateMyCourseDetailRequest } from "../types/mycourse";
import axios from 'axios';

// --- 나의 코스 목록 조회 (GET) ---
// /api/v1/members/me/courses
export const fetchMyCourses = async (
  sortBy: "recent" | "progress" = "recent",
  lastMemberCourseId?: number | null,
  size: number = 5,
  regionId?: number | null,
  travelDays?: number | null
): Promise<any> => {
  console.log(`🚀 [fetchMyCourses] API 요청: lastId=${lastMemberCourseId}, size=${size}, sort=${sortBy}, regionId=${regionId}, travelDays=${travelDays}`);

  try {
    const sortParam = sortBy === "recent" ? "latest" : sortBy;

    // 커서 기반 페이지네이션 적용
    const params: any = {
      sort: sortParam,
      pageSize: size
    };

    // lastMemberCourseId가 있을 때만 파라미터에 추가 (첫 페이지는 없음)
    if (lastMemberCourseId) {
      params.lastMemberCourseId = lastMemberCourseId;
    }

    if (regionId) {
      params.regionId = regionId;
    }
    if (travelDays) {
      params.travelDays = travelDays;
    }

    const responseData = await api.get<FetchMyCoursesResponse>('/api/v1/members/me/courses', {
      params
    });
    const response = responseData.data;

    console.log(`✅ [API 응답 전체]`, response);

    if (response.result?.courseList?.length > 0) {
      console.log(`📌 [첫 번째 코스 ID] ${response.result.courseList[0].courseId} (중복 여부 확인용)`);
    }

    if (response.isSuccess && response.result) {
      // 무한 스크롤을 위해 result 전체(sliceInfo 포함) 반환
      return response.result;
    }

    throw new Error("데이터 형식이 올바르지 않습니다.");
  } catch (error: unknown) {
    console.error('❌ 나의 코스 목록 조회 실패:', error);
    throw error;
  }
};

// --- 나의 코스 삭제 
// /api/v1/members/me/courses/{courseId} 반복 호출
export const deleteMyCourses = async (courseIds: number[]): Promise<DeleteMyCoursesResponse> => {

  try {
    // 현재 코스 1개씩 삭제(백엔드와 상의)
    for (const courseId of courseIds) {
      await api.delete(`/api/v1/members/me/courses/${courseId}`);
    }

    return {
      isSuccess: true,
      code: "COMMON200",
      message: `${courseIds.length}개의 코스가 삭제되었습니다.`,
    };
  } catch (error: unknown) {
    console.error('❌ 나의 코스 삭제 실패:', error);
    return {
      isSuccess: false,
      code: "FAIL",
      message: "코스 삭제 중 오류가 발생했습니다."
    };
  }
};

// --- 나의 코스 상세 조회 (GET) ---
// /api/v1/members/me/courses/{courseId}
export const fetchMyCourseDetail = async (courseId: string): Promise<MyCourseDetail | null> => {
  console.log('🚀 [fetchMyCourseDetail] 호출됨', courseId);

  try {
    const responseData = await api.get<MyCourseDetailResponse>(`/api/v1/members/me/courses/${courseId}`);
    const response = responseData.data;

    console.log('✅ [나의 코스 상세 조회 성공]', response);

    if (response.isSuccess && response.result) {
      return response.result;
    }
    return null;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.message ?? '상세 조회 실패';
      console.error('❌ 상세 조회 실패:', { status, message });
    } else {
      console.error('❌ 알 수 없는 에러:', error);
    }
    throw error;
  }
};

// --- 나의 코스 수정/저장 (PATCH) ---
// /api/v1/members/me/courses/{courseId}
export const updateMyCourseDetail = async (courseId: string, data: UpdateMyCourseDetailRequest): Promise<MyCourseDetailResponse> => {
  console.log('🚀 [updateMyCourseDetail] 호출됨', { courseId, data });

  try {
    const responseData = await api.patch<MyCourseDetailResponse>(`/api/v1/members/me/courses/${courseId}`, data);
    const response = responseData.data;

    console.log('✅ [나의 코스 수정 성공]', response);
    return response;
  } catch (error: unknown) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const message = error.response?.data?.message ?? '수정 실패';
      console.error('❌ 수정 요청 실패:', { status, message, detail: error.response?.data });
      throw new Error(`Error ${status}: ${message}`);
    } else {
      console.error('❌ 알 수 없는 에러:', error);
      throw new Error('수정 요청 중 오류 발생');
    }
  }
};

// --- 나의 코스 필터 옵션 조회 (GET) ---
export const fetchMyCourseFilterOptions = async (): Promise<FilterOptionResult | null> => {
  try {
    const responseData = await api.get<FilterOptionResponse>('/api/v1/members/me/courses/filters');
    const response = responseData.data;

    console.log('✅ [필터 옵션 조회 성공]', response);

    if (response.isSuccess && response.result) {
      return response.result;
    }
    return null;
  } catch (error: unknown) {
    console.error('❌ 필터 옵션 조회 실패:', error);
    return null;
  }
};