package com.example.cliproute_project.domain.place.controller.query;

import com.example.cliproute_project.domain.place.dto.res.PlaceResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter; // 추가됨
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface PlaceQueryControllerDocs {

    @Operation(
            summary = "[11 API] Available places search",
            description = "Search available places by region/category and viewport with paging."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "200", description = "Swagger response"),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE200_1", description = "Place search succeeded."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE400_1", description = "Invalid viewport parameters."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE400_2", description = "Invalid viewport range."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE400_3", description = "Viewport out of service area."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE400_4", description = "Invalid page condition."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE400_5", description = "Invalid category."),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(responseCode = "PLACE400_6", description = "No search condition.")
    })
    ApiResponse<PlaceResDTO.PlaceSearchResDTO> searchPlaces(
            String token,
            Long regionId,
            String category,
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng,
            Integer page,
            Integer size
    );
}