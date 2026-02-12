package com.example.cliproute.domain.place.service.query;

import com.example.cliproute.domain.place.converter.PlaceConverter;
import com.example.cliproute.domain.place.dto.res.PlaceResDTO;
import com.example.cliproute.domain.place.entity.Place;
import com.example.cliproute.domain.place.enums.PlaceCategory;
import com.example.cliproute.domain.place.exception.PlaceException;
import com.example.cliproute.domain.place.exception.code.PlaceErrorCode;
import com.example.cliproute.domain.place.repository.PlaceRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import com.example.cliproute.domain.member.exception.MemberException;
import com.example.cliproute.domain.member.exception.code.MemberErrorCode;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PlaceQueryServiceImpl implements PlaceQueryService {

    private static final double MIN_LAT = -90.0;
    private static final double MAX_LAT = 90.0;
    private static final double MIN_LNG = -180.0;
    private static final double MAX_LNG = 180.0;

    private final PlaceRepository placeRepository;

    @Override
    public PlaceResDTO.PlaceSearchResDTO searchPlacesByViewport(
            Long memberId,
            Long regionId,
            String category,
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng,
            Integer page,
            Integer size
    ) {
        if (memberId == null) {
            throw new MemberException(MemberErrorCode.UNAUTHORIZED);
        }
        Integer resolvedPage = page != null ? page : 0;
        Integer resolvedSize = size != null ? size : 20;
        if (resolvedPage < 0 || resolvedSize <= 0) {
            throw new PlaceException(PlaceErrorCode.PLACE_INVALID_PAGE);
        }

        boolean hasAnyViewport = minLat != null || maxLat != null || minLng != null || maxLng != null;
        boolean hasAllViewport = minLat != null && maxLat != null && minLng != null && maxLng != null;
        if (hasAnyViewport && !hasAllViewport) {
            throw new PlaceException(PlaceErrorCode.PLACE_INVALID_VIEWPORT);
        }
        if (hasAllViewport) {
            if (minLat > maxLat || minLng > maxLng) {
                throw new PlaceException(PlaceErrorCode.PLACE_INVALID_VIEWPORT_RANGE);
            }
            if (minLat < MIN_LAT || maxLat > MAX_LAT || minLng < MIN_LNG || maxLng > MAX_LNG) {
                throw new PlaceException(PlaceErrorCode.PLACE_OUT_OF_SERVICE_AREA);
            }
        }

        PlaceCategory parsedCategory = null;
        if (category != null && !category.isBlank()) {
            parsedCategory = PlaceCategory.from(category)
                    .orElseThrow(() -> new PlaceException(PlaceErrorCode.PLACE_INVALID_CATEGORY));
        }

        boolean hasCondition = regionId != null || hasAllViewport  || parsedCategory != null;
        if (!hasCondition) {
            throw new PlaceException(PlaceErrorCode.PLACE_NO_SEARCH_CONDITION);
        }

        Pageable pageable = PageRequest.of(resolvedPage, resolvedSize);
        Slice<Place> result = placeRepository.searchPlaces(
                regionId,
                parsedCategory,
                minLat,
                maxLat,
                minLng,
                maxLng,
                pageable
        );

        Long totalInViewport = (resolvedPage == 0)
                ? placeRepository.countPlacesByFilter(
                        regionId,
                        parsedCategory,
                        minLat,
                        maxLat,
                        minLng,
                        maxLng
                )
                : null;

        PlaceResDTO.ViewportDTO viewportDTO = PlaceResDTO.ViewportDTO.builder()
                .minLat(minLat)
                .maxLat(maxLat)
                .minLng(minLng)
                .maxLng(maxLng)
                .build();

        return PlaceConverter.toPlaceSearchResDTO(
                result.getContent(),
                viewportDTO,
                result,
                totalInViewport
        );
    }
}




