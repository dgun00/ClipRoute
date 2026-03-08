import type { ApiResponse } from '../types/common';
import type { RegionListResult } from '../types/region';

export const MOCK_REGIONS_RESPONSE: ApiResponse<RegionListResult> = {
  isSuccess: true,
  code: "200",
  message: "지역 목록 조회 성공",
  result: {
    regions: [
      {
        regionId: 1,
        regionName: "강릉",
        imageUrl: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200&h=200&fit=crop"
      },
      {
        regionId: 2,
        regionName: "부산",
        imageUrl: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200&h=200&fit=crop"
      },
      {
        regionId: 3,
        regionName: "제주",
        imageUrl: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=200&h=200&fit=crop"
      }

    ]
  }
};