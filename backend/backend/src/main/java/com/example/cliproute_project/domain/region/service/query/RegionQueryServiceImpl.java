package com.example.cliproute_project.domain.region.service.query;

import com.example.cliproute_project.domain.region.converter.RegionConverter;
import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;
import com.example.cliproute_project.domain.region.entity.Region;
import com.example.cliproute_project.domain.region.exception.RegionException;
import com.example.cliproute_project.domain.region.exception.code.RegionErrorCode;
import com.example.cliproute_project.domain.region.repository.RegionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class RegionQueryServiceImpl implements RegionQueryService {
    private final RegionRepository regionRepository;

    @Override
    // [1 API]
    public RegionResDTO.RegionSimpleListDTO getRegionSimpleList() {
        List<Region> regionList = regionRepository.findAll();
        if (regionList == null || regionList.isEmpty()) {
            throw new RegionException(RegionErrorCode.REGION_EMPTY);
        }
        return RegionConverter.toRegionSimpleListDTO(regionList);
    }
}
