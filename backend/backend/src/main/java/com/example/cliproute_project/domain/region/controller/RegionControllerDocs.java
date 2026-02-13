package com.example.cliproute_project.domain.region.controller;

import com.example.cliproute_project.domain.region.dto.res.RegionResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface RegionControllerDocs {
    @Operation(
            summary = "[1 API] Region list",
            description = "Returns available regions."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "REGION200_1", description = "Region list fetched successfully."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "REGION404_2", description = "No regions available.")
    })
    ApiResponse<RegionResDTO.RegionSimpleListDTO> getSimpleRegions();
}
