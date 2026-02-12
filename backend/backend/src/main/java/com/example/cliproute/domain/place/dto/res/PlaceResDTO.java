package com.example.cliproute.domain.place.dto.res;

import com.example.cliproute.domain.place.enums.PlaceCategory;
import com.example.cliproute.global.common.dto.SliceInfoDTO;
import lombok.Builder;

import java.util.List;

public class PlaceResDTO {

    @Builder
    public record PlaceSearchResDTO(
            List<PlaceDTO> places,
            ViewportDTO viewport,
            SliceInfoDTO sliceInfo,
            Long totalInViewport

    ) {}

    @Builder
    public record PlaceDTO(
            Long placeId,
            Long regionId,
            String placeName,
            PlaceCategory category,
            String address,
            Double lat,
            Double lng
    ) {}

    @Builder
    public record ViewportDTO(
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng
    ) {}

}
