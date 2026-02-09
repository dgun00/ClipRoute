package com.example.cliproute_project.domain.region.controller;

import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface RegionControllerDocs {
    @Operation(
            summary = "[1번 API] 장소 데이터들 조회",
            description = "장소 선택시 장소 리스트 조회"
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger에 response 형태 보여주기용"),

            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "REGION200_1", description = "지역 목록 조회에 성공했습니다."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "REGION404_1", description = "지역 정보를 찾을 수 없습니다.")
    })
    ApiResponse<RegionResDTO.RegionSimpleListDTO> getSimpleRegions();
}
