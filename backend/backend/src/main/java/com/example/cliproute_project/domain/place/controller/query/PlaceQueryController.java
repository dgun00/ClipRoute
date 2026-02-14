package com.example.cliproute_project.domain.place.controller.query;

import com.example.cliproute_project.domain.auth.util.JwtUtil;
import com.example.cliproute_project.domain.place.dto.res.PlaceResDTO;
import com.example.cliproute_project.domain.place.exception.code.PlaceSuccessCode;
import com.example.cliproute_project.domain.place.service.query.PlaceQueryService;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/places")
@Tag(name = "Place", description = "Place APIs")
public class PlaceQueryController implements PlaceQueryControllerDocs {

    private final PlaceQueryService placeQueryService;
    private final JwtUtil jwtUtil;
    // [11 API] Available places search
    @GetMapping("/search")
    public ApiResponse<PlaceResDTO.PlaceSearchResDTO> searchPlaces(
            @RequestHeader("Authorization") String token,
            @RequestParam(required = false) Long regionId,
            @RequestParam(required = false) String category,
            @RequestParam(required = false) Double minLat,
            @RequestParam(required = false) Double maxLat,
            @RequestParam(required = false) Double minLng,
            @RequestParam(required = false) Double maxLng,
            @RequestParam(required = false, defaultValue = "0") Integer page,
            @RequestParam(required = false, defaultValue = "10") Integer pageSize
    ) {

        String email = jwtUtil.getUserInfoFromToken(token.substring(7));

        PlaceResDTO.PlaceSearchResDTO response = placeQueryService.searchPlacesByViewport(
                email, regionId, category, minLat, maxLat, minLng, maxLng, page, pageSize
        );

        return ApiResponse.onSuccess(
                PlaceSuccessCode.PLACE_SEARCH_SUCCESS,
                response
        );
    }
}
