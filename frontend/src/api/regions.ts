import api from './axios';
import type { ApiResponse } from '../types/common';
import type { RegionListResult } from '../types/region';

export const fetchRegions = async (): Promise<ApiResponse<RegionListResult>> => {
  const response = await api.get<ApiResponse<RegionListResult>>('/api/v1/regions');
  return response.data;
};
