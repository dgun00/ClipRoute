package com.example.cliproute_project.domain.region.converter;

import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;
import com.example.cliproute_project.domain.region.entity.Region;

import java.util.List;
import java.util.stream.Collectors;

public class RegionConverter {

    public static RegionResDTO.RegionSimpleDTO toRegionSimpleDTO(Region region){
        return RegionResDTO.RegionSimpleDTO.builder()
                .regionId(region.getId())
                .regionName(region.getRegionName())
                .imageUrl(region.getImageUrl())
                .build();
    }

    public static RegionResDTO.RegionSimpleListDTO toRegionSimpleListDTO(List<Region> regions) {
        List<RegionResDTO.RegionSimpleDTO> regionList = regions.stream()
                .map(RegionConverter::toRegionSimpleDTO)
                .collect(Collectors.toList());

        return RegionResDTO.RegionSimpleListDTO.builder()
                .regions(regionList)
                .build();
}
}
