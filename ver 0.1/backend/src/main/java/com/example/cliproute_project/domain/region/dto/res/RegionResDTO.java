package com.example.cliproute_project.domain.region.dto.res;

import lombok.Builder;

import java.util.List;


public class RegionResDTO {

    // [1 API]
    @Builder
    public record RegionSimpleListDTO(// 여행지 선택옵션때 나오는 데이터 리스트
            List<RegionSimpleDTO> regions
    ) {}
    //[1 API]
    @Builder
    public record RegionSimpleDTO(// 여행지 선택옵션때 나오는 데이터
            Long regionId,
            String regionName,
            String imageUrl
    ){}

}
