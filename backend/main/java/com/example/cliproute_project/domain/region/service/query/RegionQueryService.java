package com.example.cliproute_project.domain.region.service.query;

import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;

public interface RegionQueryService {

    // 1번 API: 여행지 리스트 조회
    RegionResDTO.RegionSimpleListDTO getRegionSimpleList();
}
