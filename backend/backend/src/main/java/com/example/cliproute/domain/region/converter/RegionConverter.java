package com.example.cliproute.domain.region.converter;

import com.example.cliproute.domain.region.dto.res.RegionResDTO;
import com.example.cliproute.domain.region.entity.Region;

import java.util.List;
import java.util.stream.Collectors;

public class RegionConverter {

    // [1 API]
    public static RegionResDTO.RegionSimpleDTO toRegionSimpleDTO(Region region){
        return RegionResDTO.RegionSimpleDTO.builder()
                .regionId(region.getId())
                .regionName(region.getRegionName())
                .imageUrl(region.getImageUrl())
                .build();
    }

    // [1 API]
    public static RegionResDTO.RegionSimpleListDTO toRegionSimpleListDTO(List<Region> regions) {
        List<RegionResDTO.RegionSimpleDTO> regionList = regions.stream()
                .map(RegionConverter::toRegionSimpleDTO)
                .collect(Collectors.toList());

        return RegionResDTO.RegionSimpleListDTO.builder()
                .regions(regionList)
                .build();
}
}
