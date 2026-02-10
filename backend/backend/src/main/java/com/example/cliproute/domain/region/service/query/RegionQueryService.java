package com.example.cliproute.domain.region.service.query;

import com.example.cliproute.domain.region.dto.res.RegionResDTO;

public interface RegionQueryService {

    // 1번 API: 여행지 리스트 조회
    RegionResDTO.RegionSimpleListDTO getRegionSimpleList();
}
