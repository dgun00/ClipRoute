package com.example.cliproute.domain.region.service.query;

import com.example.cliproute_project.domain.region.converter.RegionConverter;
import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;
import com.example.cliproute_project.domain.region.entity.Region;
import com.example.cliproute_project.domain.region.repository.RegionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true) // 조회 전용 트랜잭션 (성능 향상)
public class RegionQueryServiceImpl implements RegionQueryService {
    private final RegionRepository regionRepository;

    @Override
    // [1번 API]
    public RegionResDTO.RegionSimpleListDTO getRegionSimpleList() {
        // 1. DB에서 전체 지역 조회 (Entity List)
        List<Region> regionList = regionRepository.findAll();
        // 2. Converter를 통해 DTO로 변환하여 반환
        return RegionConverter.toRegionSimpleListDTO(regionList);
    }
}
