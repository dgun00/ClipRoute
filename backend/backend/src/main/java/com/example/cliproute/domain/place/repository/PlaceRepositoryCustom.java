package com.example.cliproute.domain.place.repository;

import com.example.cliproute.domain.place.entity.Place;
import com.example.cliproute.domain.place.enums.PlaceCategory;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;

public interface PlaceRepositoryCustom {
    Slice<Place> searchPlaces(
            Long regionId,
            PlaceCategory category,
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng,
            Pageable pageable
    );

    Long countPlacesByFilter(
            Long regionId,
            PlaceCategory category,
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng
    );
}
