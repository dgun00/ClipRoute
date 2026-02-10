package com.example.cliproute.domain.place.converter;

import com.example.cliproute.domain.place.dto.res.PlaceResDTO;
import com.example.cliproute.domain.place.entity.Place;
import com.example.cliproute.global.common.converter.SliceConverter;
import com.example.cliproute.global.common.dto.SliceInfoDTO;
import org.springframework.data.domain.Slice;

import java.util.List;

public class PlaceConverter {

    public static PlaceResDTO.PlaceSearchResDTO toPlaceSearchResDTO(
            List<Place> places,
            PlaceResDTO.ViewportDTO viewportDTO,
            Slice<?> slice,
            Long totalInViewport
    ) {
        List<PlaceResDTO.PlaceDTO> placeDTOs =
                (places == null || places.isEmpty())
                        ? List.of()
                        : places.stream().map(PlaceConverter::toPlaceDTO).toList();

        SliceInfoDTO sliceInfoDTO = SliceConverter.toSliceInfoDTO(slice);

        return PlaceResDTO.PlaceSearchResDTO.builder()
                .places(placeDTOs)
                .viewport(viewportDTO)
                .sliceInfo(sliceInfoDTO)
                .totalInViewport(totalInViewport)
                .build();
    }

    private static PlaceResDTO.PlaceDTO toPlaceDTO(Place place) {
        return PlaceResDTO.PlaceDTO.builder()
                .placeId(place.getId())
                .regionId(place.getRegion() != null ? place.getRegion().getId() : null)
                .placeName(place.getPlaceName())
                .category(place.getPlaceCategory())
                .address(place.getAddress())
                .lat(place.getLat())
                .lng(place.getLng())
                .build();
    }

}
