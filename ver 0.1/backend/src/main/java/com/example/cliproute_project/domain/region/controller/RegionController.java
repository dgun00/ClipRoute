package com.example.cliproute_project.domain.region.controller;

import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;
import com.example.cliproute_project.domain.region.exception.code.RegionSuccessCode;
import com.example.cliproute_project.domain.region.service.query.RegionQueryService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import com.example.cliproute_project.global.apiPayload.code.GeneralSuccessCode;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;


@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1")
@Tag(name = "Region", description = "지역 관련 API")
public class RegionController implements RegionControllerDocs {
    private final RegionQueryService regionQueryService;

    // [1 API]
    @GetMapping("/regions")
    public ApiResponse<RegionResDTO.RegionSimpleListDTO> getSimpleRegions() {

        RegionResDTO.RegionSimpleListDTO response = regionQueryService.getRegionSimpleList();

        return ApiResponse.onSuccess(
                RegionSuccessCode.REGION_LIST_FETCH_SUCCESS,
                response);
    }
}
