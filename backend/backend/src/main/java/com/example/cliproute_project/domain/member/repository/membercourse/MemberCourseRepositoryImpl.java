package com.example.cliproute_project.domain.member.repository.membercourse;

import com.example.cliproute_project.domain.course.entity.QCourse;
import com.example.cliproute_project.domain.course.entity.mapping.QCoursePlace;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.entity.mapping.QMemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseListFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseRegionOptionFlat;
import com.example.cliproute_project.domain.place.entity.QPlace;
import com.example.cliproute_project.domain.region.entity.QRegion;
import com.example.cliproute_project.domain.video.entity.QVideo;
import com.example.cliproute_project.domain.video.entity.mapping.QVideoPlace;
import com.querydsl.core.types.Projections;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;

import java.util.List;
import java.util.Optional;

@RequiredArgsConstructor
public class MemberCourseRepositoryImpl implements MemberCourseRepositoryCustom {

    private final JPAQueryFactory queryFactory;

    // [4 API]
    @Override
    public Optional<MemberCourse> findActiveScrapByOriginalCourseId(Long memberId, Long originalCourseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        MemberCourse result = queryFactory
                .selectFrom(mc)
                .join(mc.course, c)
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.originalCourse.id.eq(originalCourseId).or(c.id.eq(originalCourseId))
                )
                .orderBy(mc.id.desc())
                .fetchFirst();

        return Optional.ofNullable(result);
    }

    // --- [5 API] scrap ---
    @Override
    public boolean existsActiveScrapByCourseId(Long memberId, Long courseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        Integer found = queryFactory
                .selectOne()
                .from(mc)
                .join(mc.course, c)
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.originalCourse.id.eq(courseId)
                )
                .fetchFirst();

        return found != null;
    }

    @Override
    public Optional<MemberCourse> findActiveScrapByCourseId(Long memberId, Long courseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        MemberCourse result = queryFactory
                .selectFrom(mc)
                .join(mc.course, c).fetchJoin()
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.originalCourse.id.eq(courseId)
                )
                .fetchFirst();

        return Optional.ofNullable(result);
    }

    // --- [6 API] filter options ---
    @Override
    public List<MyCourseRegionOptionFlat> findDistinctRegionsForMyCourseFilters(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    ) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;
        QRegion r = QRegion.region;

        return queryFactory
                .select(Projections.constructor(
                        MyCourseRegionOptionFlat.class,
                        r.id,
                        r.regionName
                ))
                .from(mc)
                .join(mc.course, c)
                .join(c.region, r)
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.deletedAt.isNull(),
                        c.isCustomized.isTrue(),
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        eqTravelStatus(travelStatus)
                )
                .distinct()
                .orderBy(r.id.asc())
                .fetch();
    }

    @Override
    public List<Integer> findDistinctTravelDaysForMyCourseFilters(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    ) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        return queryFactory
                .select(c.travelDays)
                .from(mc)
                .join(mc.course, c)
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.deletedAt.isNull(),
                        c.isCustomized.isTrue(),
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        eqTravelStatus(travelStatus)
                )
                .distinct()
                .orderBy(c.travelDays.asc())
                .fetch();
    }

    @Override
    public List<TravelStatus> findDistinctTravelStatusesForMyCourseFilters(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    ) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        return queryFactory
                .select(mc.travelStatus)
                .from(mc)
                .join(mc.course, c)
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.deletedAt.isNull(),
                        c.isCustomized.isTrue(),
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        eqTravelStatus(travelStatus)
                )
                .distinct()
                .orderBy(mc.travelStatus.asc())
                .fetch();
    }

    // --- [7 API] my courses list ---
    @Override
    public List<MyCourseListFlat> findMyCoursesByFilter(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus,
            Long lastMemberCourseId,
            Integer pageSize
    ) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;
        QRegion r = QRegion.region;
        QVideo v = QVideo.video;
        QCoursePlace cp = QCoursePlace.coursePlace;

        return queryFactory
                .select(Projections.constructor(
                        MyCourseListFlat.class,
                        c.id,
                        c.originalCourse.id,
                        mc.id,
                        c.title,
                        r.regionName,
                        v.ytVideoId,
                        mc.startDate,
                        mc.endDate,
                        c.travelDays,
                        mc.travelStatus,
                        cp.id.countDistinct(),
                        mc.createdAt,
                        mc.updatedAt
                ))
                .from(mc)
                .join(mc.course, c)
                .join(c.region, r)
                .join(c.sourceVideo, v)
                .leftJoin(cp).on(cp.course.eq(c).and(cp.deletedAt.isNull()))
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.deletedAt.isNull(),
                        c.isCustomized.isTrue(),
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        eqTravelStatus(travelStatus),
                        cursorCondition(lastMemberCourseId)
                )
                .groupBy(
                        c.id,
                        c.originalCourse.id,
                        c.title,
                        r.regionName,
                        v.ytVideoId,
                        mc.startDate,
                        mc.endDate,
                        c.travelDays,
                        mc.travelStatus,
                        mc.createdAt,
                        mc.updatedAt,
                        mc.id
                )
                .orderBy(mc.id.desc())
                .limit(pageSize + 1L)
                .fetch();
    }

    // --- [9 API] my course detail ---
    @Override
    public boolean existsMyCourseDetailScope(Long memberId, Long courseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        Integer found = queryFactory
                .selectOne()
                .from(mc)
                .join(mc.course, c)
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.deletedAt.isNull(),
                        c.isCustomized.isTrue(),
                        c.id.eq(courseId)
                )
                .fetchFirst();

        return found != null;
    }

    // [9,10 API]
    @Override
    public List<MyCourseDetailFlat> findMyCourseDetailFlats(Long memberId, Long courseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;
        QRegion r = QRegion.region;
        QVideo v = QVideo.video;
        QCoursePlace cp = QCoursePlace.coursePlace;
        QPlace p = QPlace.place;

        return queryFactory
                .select(Projections.constructor(
                        MyCourseDetailFlat.class,
                        c.id,                        // 1. courseId (Long)
                        c.title,                     // 2. courseTitle (String)
                        r.id,                        // 3. regionId (Long)
                        r.regionName,                // 4. regionName (String)
                        v.ytVideoId,                 // 5. ytVideoId (String)
                        mc.id,                       // 6. memberCourseId (Long)
                        v.channelName,               // 7. channelName (String)
                        mc.member.id.eq(memberId),   // 8. isMine (Boolean)
                        mc.isScrapped,               // 9. isScrapped (Boolean)
                        mc.travelStatus,             // 10. travelStatus (Enum)
                        c.description,               // 11. memo (String)
                        mc.startDate,                // 12. startDate (LocalDate)
                        mc.endDate,                  // 13. endDate (LocalDate)
                        c.travelDays,                // 14. travelDays (Integer)
//                        com.querydsl.core.types.dsl.Expressions.asNumber(0).as("likeCount"),  // 14. Integer
//                        com.querydsl.core.types.dsl.Expressions.asNumber(0L).as("scrapCount"), // 15. Long

                        cp.id,                       // 16. coursePlaceId (Long)
                        p.id,                        // 17. placeId (Long)
                        cp.visitOrder,               // 18. visitOrder (Integer)
                        p.placeName,                 // 19. placeName (String)
                        p.placeCategory,             // 20. placeCategory (Enum)
                        p.address,                   // 21. address (String)
                        p.lat,                       // 22. latitude (Double)
                        p.lng,                       // 23. longitude (Double)
                        cp.visitDay,                 // 24. visitDay (Integer)
//                        vp.timestamp,                // 25. timestamp (Integer)
                        p.updatedAt                  // 26. updatedAt (LocalDateTime)
                ))
                .from(c)
                .join(c.region, r)
                .join(c.sourceVideo, v)
                .join(mc).on(
                        mc.course.eq(c),
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue()
                )
                .leftJoin(cp).on(cp.course.eq(c).and(cp.deletedAt.isNull())) // 삭제된 장소 제외
                .leftJoin(p).on(cp.place.eq(p))
                .where(
                        c.id.eq(courseId),
                        c.deletedAt.isNull()
                )
                .orderBy(cp.visitDay.asc(), cp.visitOrder.asc())
                .fetch();
    }

    private BooleanExpression eqRegionId(Long regionId) {
        QCourse c = QCourse.course;
        return regionId != null ? c.region.id.eq(regionId) : null;
    }

    private BooleanExpression eqTravelDays(Integer travelDays) {
        QCourse c = QCourse.course;
        return travelDays != null ? c.travelDays.eq(travelDays) : null;
    }

    private BooleanExpression eqTravelStatus(TravelStatus travelStatus) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        return travelStatus != null ? mc.travelStatus.eq(travelStatus) : null;
    }

    private BooleanExpression cursorCondition(Long lastMemberCourseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        if (lastMemberCourseId == null) {
            return null;
        }
        return mc.id.lt(lastMemberCourseId);
    }
}

