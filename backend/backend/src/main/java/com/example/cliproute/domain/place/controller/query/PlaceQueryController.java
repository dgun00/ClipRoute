package com.example.cliproute.domain.place.controller.query;

import com.example.cliproute.domain.place.dto.res.PlaceResDTO;
import com.example.cliproute.domain.place.exception.code.PlaceSuccessCode;
import com.example.cliproute.domain.place.service.query.PlaceQueryService;
import com.example.cliproute.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/places")
@Tag(name = "Place", description = "Place APIs")
public class PlaceQueryController implements PlaceQueryControllerDocs {

    private final PlaceQueryService placeQueryService;

    // [11 API] Available places search
    @GetMapping("/search")
    public ApiResponse<PlaceResDTO.PlaceSearchResDTO> searchPlaces(
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) Double minLat,
            @RequestParam(required = false) Double maxLat,
            @RequestParam(required = false) Double minLng,
            @RequestParam(required = false) Double maxLng,
            @RequestParam(required = false, defaultValue = "0") Integer page,
            @RequestParam(required = false, defaultValue = "10") Integer pageSize
    ) {
        PlaceResDTO.PlaceSearchResDTO response = placeQueryService.searchPlacesByViewport(
                regionId, category, minLat, maxLat, minLng, maxLng, page, pageSize
        );

        return ApiResponse.onSuccess(
                PlaceSuccessCode.PLACE_SEARCH_SUCCESS,
                response
        );
    }
}
