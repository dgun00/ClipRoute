package com.example.cliproute_project.domain.place.controller.query;

import com.example.cliproute_project.domain.place.dto.res.PlaceResDTO;
import com.example.cliproute_project.global.apiPayload.ApiResponse;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponses;

public interface PlaceQueryControllerDocs {

    @Operation(
            summary = "[11 API] Search available places",
            description = "Search available places by region/category and viewport with paging."
    )
    @ApiResponses({
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "200",
                    description = "Success (business code: PLACE200_1)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "400",
                    description = "Bad request (business codes: PLACE400_1, PLACE400_2, PLACE400_3, PLACE400_4, PLACE400_5, PLACE400_6)",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            ),
            @io.swagger.v3.oas.annotations.responses.ApiResponse(
                    responseCode = "401",
                    description = "Unauthorized when the Authorization header is missing or invalid.",
                    content = @Content(schema = @Schema(implementation = ApiResponse.class))
            )
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
