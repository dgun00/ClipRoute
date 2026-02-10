package com.example.cliproute.domain.place.service.query;

import com.example.cliproute_project.domain.place.dto.res.PlaceResDTO;

public interface PlaceQueryService {

    // [11 API] Available places search
    PlaceResDTO.PlaceSearchResDTO searchPlacesByViewport(
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
