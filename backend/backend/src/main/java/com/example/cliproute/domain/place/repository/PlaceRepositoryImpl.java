package com.example.cliproute.domain.place.repository;

import com.example.cliproute.domain.place.entity.Place;
import com.example.cliproute.domain.place.entity.QPlace;
import com.example.cliproute.domain.place.enums.PlaceCategory;
import com.example.cliproute.domain.region.entity.QRegion;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.data.domain.SliceImpl;

import java.util.List;

@RequiredArgsConstructor
public class PlaceRepositoryImpl implements PlaceRepositoryCustom {

    private final JPAQueryFactory queryFactory;

    @Override
    public Slice<Place> searchPlaces(
            Long regionId,
            PlaceCategory category,
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng,
            Pageable pageable
    ) {
        QPlace p = QPlace.place;
        QRegion r = QRegion.region;

        List<Place> content = queryFactory
                .selectFrom(p)
                .join(p.region, r).fetchJoin()
                .where(
                        p.deletedAt.isNull(),
                        p.lat.isNotNull(),
                        p.lng.isNotNull(),
                        eqRegionId(regionId),
                        eqCategory(category),
                        withinViewport(minLat, maxLat, minLng, maxLng)
                )
                .orderBy(p.id.desc())
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize() + 1L)
                .fetch();

        boolean hasNext = false;
        if (content.size() > pageable.getPageSize()) {
            content = content.subList(0, pageable.getPageSize());
            hasNext = true;
        }

        return new SliceImpl<>(content, pageable, hasNext);
    }

    @Override
    public Long countPlacesByFilter(
            Long regionId,
            PlaceCategory category,
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng
    ) {
        QPlace p = QPlace.place;
        Long total = queryFactory
                .select(p.count())
                .from(p)
                .where(
                        p.deletedAt.isNull(),
                        p.lat.isNotNull(),
                        p.lng.isNotNull(),
                        eqRegionId(regionId),
                        eqCategory(category),
                        withinViewport(minLat, maxLat, minLng, maxLng)
                )
                .fetchOne();

        return total != null ? total : 0L;
    }

    private BooleanExpression eqRegionId(Long regionId) {
        QPlace p = QPlace.place;
        return regionId != null ? p.region.id.eq(regionId) : null;
    }


    private BooleanExpression eqCategory(PlaceCategory category) {
        QPlace p = QPlace.place;
        if (category == null) {
            return null;
        }
        return p.placeCategory.eq(category);
    }

    private BooleanExpression withinViewport(
            Double minLat,
            Double maxLat,
            Double minLng,
            Double maxLng
    ) {
        QPlace p = QPlace.place;
        if (minLat == null || maxLat == null || minLng == null || maxLng == null) {
            return null;
        }
        return p.lat.between(minLat, maxLat)
                .and(p.lng.between(minLng, maxLng));
    }
}
