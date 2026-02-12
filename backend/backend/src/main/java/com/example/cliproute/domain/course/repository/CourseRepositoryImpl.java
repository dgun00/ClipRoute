package com.example.cliproute.domain.course.repository;

import com.example.cliproute.domain.course.entity.Course;
import com.example.cliproute.domain.course.entity.QCourse;
import com.example.cliproute.domain.region.entity.QRegion;
import com.example.cliproute.domain.video.entity.QVideo;
import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.core.types.dsl.CaseBuilder;
import com.querydsl.core.types.dsl.Expressions;
import com.querydsl.core.types.dsl.NumberExpression;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static com.example.cliproute.domain.course.entity.QCourse.course;
import static com.example.cliproute.domain.video.entity.QVideo.video;
import static com.example.cliproute.domain.region.entity.QRegion.region;


@RequiredArgsConstructor
public class CourseRepositoryImpl implements CourseRepositoryCustom {
    private final JPAQueryFactory queryFactory;

    // [2 API] 무한 스크롤 페이지 조회 (No-Offset 방식)
    @Override
    public Slice<Course> findCoursesByFilter(
            Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId,  Integer lastCourseValue, Pageable pageable
    ) {

        List<Course> content = queryFactory
                .selectFrom(course)
                .join(course.sourceVideo, video).fetchJoin() // N+1 방지
                .join(course.region, region).fetchJoin()    // N+1 방지
                .where(
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        eqIsRepresentative(isRep),
                        // 정렬 기준에 따른 No-Offset 커서 조건
                        cursorCondition(sort, seed, lastCourseId, lastCourseValue),
                        course.deletedAt.isNull(),
                        course.isCustomized.isFalse() // 다음 페이지 존재 확인 (+1)
                )
                .orderBy(
                        // 정렬 기준에 따른 OrderSpecifier 적용
                        dynamicOrderBy(sort, seed)
                )
                .limit(pageable.getPageSize() + 1) // 다음 페이지 존재 여부 확인 (+1)
                .fetch();

        boolean hasNext = false;
        if (content.size() > pageable.getPageSize()) { // 다음 페이지 존재 여부 확인 (+1)
            content.remove(pageable.getPageSize());
            hasNext = true;
        }

        return new SliceImpl<>(content, pageable, hasNext);
    }

    // [3 API] 커스텀 필터 + 추천 (필터 우선순위 적용, 위치 기반 추천 코스 데이터 조회)
    @Override
    public Slice<Course> findCoursesByFilterWithRecommendation(Long regionId, Integer travelDays, String sort, Long seed, Pageable pageable) {

        // 1우선순위: 지역&일정 일치 / 2우선순위: 지역 일치 / 3우선순위: 일정 일치 / 4우선순위: 나머지
        NumberExpression<Integer> rankPath = new CaseBuilder()
                .when(eqRegionId(regionId).and(eqTravelDays(travelDays))).then(1)
                .when(eqRegionId(regionId)).then(2)
                .when(eqTravelDays(travelDays)).then(3)
                .otherwise(4);


        List<Course> content = queryFactory
                .selectFrom(course)
                .join(course.sourceVideo, video).fetchJoin()
                .join(course.region, region).fetchJoin()
                .where(
                        // 추천 로직에서는 조건을 OR로 묶기보다는 전체 데이터를 가져와서 정렬로 처리
                        // filter,
                        course.deletedAt.isNull(),
                        course.isCustomized.isFalse() // 커스텀 코스는 추천 제외
                )
                // 모든 정렬 조건을 합쳐주는 헬퍼 메서드 사용
                .orderBy(
                        getAllOrderSpecifiers(rankPath.asc(), sort, seed)
                )
                // 추천 데이터는 정렬이 복잡하므로 Offset 방식을 유지함
                .offset(pageable.getOffset())
                .limit(pageable.getPageSize() + 1)
                .fetch();

        boolean hasNext = false;
        if (content.size() > pageable.getPageSize()) {
            content.remove(pageable.getPageSize());
            hasNext = true;
        }

        return new SliceImpl<>(content, pageable, hasNext);
    }


    // [2,3 API] 첫 조회 시 전체 데이터 카운트    @Override
    public Long countCoursesByFilter(Long regionId, Integer travelDays, Boolean isRep) {
        Long count = queryFactory
                .select(course.count())
                .from(course)
                .where(
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        eqIsRepresentative(isRep),
                        course.deletedAt.isNull(),
                        course.isCustomized.isFalse()
                )
                .fetchOne();

        return count != null ? count : 0L;
    }



    // random logic
    private NumberExpression<Integer> randomKey(Long seed) {
        return Expressions.numberTemplate(
                Integer.class,
                "MOD(ABS(CRC32(CONCAT({0}, '::', {1}))), 2147483647)",
                course.id, seed
        );
    }

    // --- No-Offset 커서 생성 로직 ---
    // [2 API]
    private BooleanExpression cursorCondition(String sort, Long seed, Long lastCourseId, Integer lastCourseValue) {
        if (lastCourseId == null) return null;

        if ("random".equals(sort)) {
            NumberExpression<Integer> currentKey = randomKey(seed);
            NumberExpression<Integer> lastKey = Expressions.numberTemplate(
                    Integer.class,
                    "MOD(ABS(CRC32(CONCAT({0}, '::', {1}))), 2147483647)",
                    Expressions.constant(lastCourseId), seed
            );
            // random logic
            return currentKey.gt(lastKey).or(currentKey.eq(lastKey).and(course.id.gt(lastCourseId)));
        }
        else
            // 최신순: id < lastCourseId
            return ltCourseId(lastCourseId);

//        if ("popular".equals(sort)) { -> 다른 정렬기준은 미구현
//            // 인기순 커서: (조회수 < lastCourseValue) OR (조회수 == lastValue AND id < lastId)
//            // 현재 엔티티에 조회수(viewCount) 필드가 없으므로 최신순(ID) 로직 참고용으로만 유지
//            // return course.viewCount.lt(lastValue).or(course.viewCount.eq(lastValue).and(course.id.lt(lastId)))
//        }


    }

    // [3 API] 추천 랭킹과 사용자 정의 정렬을 합쳐주는 메서드
    private OrderSpecifier<?>[] getAllOrderSpecifiers(OrderSpecifier<Integer> rankOrder, String sort, Long seed) {
        List<OrderSpecifier<?>> orders = new ArrayList<>();

        // 1순위: 무조건 추천 순위가 먼저
        orders.add(rankOrder);

        // 2순위 & 3순위: 사용자 정의 정렬 (배열을 리스트로 변환 후 추가)
        orders.addAll(Arrays.asList(dynamicOrderBy(sort, seed)));

        return orders.toArray(new OrderSpecifier[0]);
    }

    // --- 동적 정렬 조건 로직 ---
    // [2,3 API]
    private OrderSpecifier<?>[] dynamicOrderBy(String sort, Long seed) {
        List<OrderSpecifier<?>> orders = new ArrayList<>();

        if ("random".equals(sort)) {
            // random logic
            orders.add(randomKey(seed).asc());
            orders.add(course.id.asc());
//        } else if ("popular".equals(sort)) {
//            // 1차 인기순 (조회수 기준 - 필드 추가 시 활성화)
//            // orders.add(course.viewCount.desc());
//            // 2차 ID순 (동일 인기수일 때 일관성 보장)
//            orders.add(course.id.desc());
        } else {
            // 최신순: ID 내림차순
            orders.add(course.id.desc());
        }

        return orders.toArray(new OrderSpecifier[0]);
    }

    // --- BooleanExpression ---
    private BooleanExpression eqRegionId(Long regionId) {
        return regionId != null ? course.region.id.eq(regionId) : null;
    }

    private BooleanExpression eqTravelDays(Integer travelDays) {
        return travelDays != null ? course.travelDays.eq(travelDays) : null;
    }

    private BooleanExpression ltCourseId(Long lastCourseId) {
        // 첫 페이지(null)면 조건 무시, 아니면 id < lastCourseId 적용
        return lastCourseId != null ? course.id.lt(lastCourseId) : null;
    }
    private BooleanExpression eqIsRepresentative(Boolean isRep) {
        // 파라미터가 null이면 조건을 걸지 않음 (전체 조회)
         return isRep != null ? course.isRep.eq(isRep) : null;
    }
    // [4 API]
    @Override
    public Optional<Course> findByIdWithVideoAndRegion(Long courseId) {

//        QCourse c = QCourse.course;
//        QVideo v = QVideo.video;
//        QRegion r = QRegion.region;

        Course resCourse = queryFactory
                .selectFrom(course)
                .join(course.sourceVideo, video).fetchJoin()
                .join(course.region, region).fetchJoin()
                .where(
                        course.id.eq(courseId),
                        course.deletedAt.isNull(),
                        course.isCustomized.isFalse()
                )
                .fetchOne();

        return Optional.ofNullable(resCourse); // 반환값이 null일 가능성 있음
    }

}
