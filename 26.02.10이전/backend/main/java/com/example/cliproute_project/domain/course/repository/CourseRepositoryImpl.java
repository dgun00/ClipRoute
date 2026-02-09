package com.example.cliproute_project.domain.course.repository;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.entity.QCourse;
import com.example.cliproute_project.domain.region.entity.QRegion;
import com.example.cliproute_project.domain.video.entity.QVideo;
import com.querydsl.core.types.OrderSpecifier;
import com.querydsl.core.types.dsl.BooleanExpression;
import com.querydsl.core.types.dsl.CaseBuilder;
import com.querydsl.core.types.dsl.NumberExpression;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static com.example.cliproute_project.domain.course.entity.QCourse.course;
import static com.example.cliproute_project.domain.video.entity.QVideo.video;
import static com.example.cliproute_project.domain.region.entity.QRegion.region;


@RequiredArgsConstructor
public class CourseRepositoryImpl implements CourseRepositoryCustom {
    private final JPAQueryFactory queryFactory;

    // [2번 API] 무한 스크롤 데이터 조회 (No-Offset 방식)
    @Override
    public Slice<Course> findCoursesByFilter(Long regionId, Integer travelDays, String sort, Long lastCourseId, Integer lastValue, Pageable pageable) {

        List<Course> content = queryFactory
                .selectFrom(course)
                .join(course.sourceVideo, video).fetchJoin() // N+1 방지
                .join(course.region, region).fetchJoin()    // N+1 방지
                .where(
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        // 정렬 기준에 따른 No-Offset 커서 조건
                        cursorCondition(sort, lastCourseId, lastValue),
                        course.deletedAt.isNull(),
                        course.isCustomized.isFalse() // 커스텀된 코스는 추천 안함
                )
                .orderBy(
                        // 정렬 기준에 따른 OrderSpecifier 적용
                        dynamicOrderBy(sort)
                )
                .limit(pageable.getPageSize() + 1) // 다음 페이지 확인용 (+1)
                .fetch();

        boolean hasNext = false;
        if (content.size() > pageable.getPageSize()) { // 다음 페이지 확인용(-1)
            content.remove(pageable.getPageSize());
            hasNext = true;
        }

        return new SliceImpl<>(content, pageable, hasNext);
    }

    // [3번 API] 필터링 + 추천 (정확도 우선, 소진 시 추천 코스 연속 노출)
    @Override
    public Slice<Course> findCoursesByFilterWithRecommendation(Long regionId, Integer travelDays, String sort, Pageable pageable) {

        // 1순위: 지역&일수 일치 / 2순위: 지역만 / 3순위: 일수만 / 4순위: 나머지
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
                        // 추천을 위해 조건을 OR로 확장하거나, 전체에서 랭킹순으로 가져옴
                       // filter,
                        course.deletedAt.isNull(),
                        course.isCustomized.isFalse() // 커스텀된 코스는 추천 안함
                )
                // 모든 정렬 조건을 합쳐주는 헬퍼 메서드 호출
                .orderBy(
                        getAllOrderSpecifiers(rankPath.asc(), sort)
                )
                .offset(pageable.getOffset()) // 추천 시스템은 복합 정렬이라 Offset 방식이 안전함
                .limit(pageable.getPageSize() + 1)
                .fetch();

        boolean hasNext = false;
        if (content.size() > pageable.getPageSize()) {
            content.remove(pageable.getPageSize());
            hasNext = true;
        }

        return new SliceImpl<>(content, pageable, hasNext);
    }


    // [2,3번 API] 첫 조회시 데이터수 카운트
    @Override
    public Long countCoursesByFilter(Long regionId, Integer travelDays) {
        Long count = queryFactory
                .select(course.count())
                .from(course)
                .where(
                        eqRegionId(regionId),
                        eqTravelDays(travelDays),
                        course.deletedAt.isNull(), // soft delete 된건 제외
                        course.isCustomized.isFalse() // 커스텀된 코스는 추천 안함
                )
                .fetchOne();
        // 조회된거 없으면 0 반환
        return count != null ? count : 0L;
    }



    // --- No-Offset 동적 커서 생성 로직 ---
    // [2번 API]
    private BooleanExpression cursorCondition(String sort, Long lastId, Integer lastValue) {
        if (lastId == null) return null; // 첫 페이지면 조건 없음

        if ("인기".equals(sort)) {
            // 인기순 커서: (조회수 < lastValue) OR (조회수 == lastValue AND id < lastId)
            // ※ 현재 엔티티에 조회수(viewCount) 필드가 없으므로 패턴만 참고
            // return course.viewCount.lt(lastValue).or(course.viewCount.eq(lastValue).and(course.id.lt(lastId)));
            return ltCourseId(lastId); // 임시
        }

        // 기본값 (최신순): id < lastId
        return ltCourseId(lastId);
    }

    // [3번 API] 랭킹과 동적 정렬을 하나로 합치는 헬퍼 메서드
    private OrderSpecifier<?>[] getAllOrderSpecifiers(OrderSpecifier<Integer> rankOrder, String sort) {
        List<OrderSpecifier<?>> orders = new ArrayList<>();

        // 1순위: 무조건 랭킹 점수
        orders.add(rankOrder);

        // 2순위 & 3순위: 사용자 선택 정렬 (배열을 리스트로 변환해서 추가)
        orders.addAll(Arrays.asList(dynamicOrderBy(sort)));

        return orders.toArray(new OrderSpecifier[0]);
    }

    // --- 동적 정렬 생성 로직 ---
    //[2,3번 API]
    private OrderSpecifier<?>[] dynamicOrderBy(String sort) {
        List<OrderSpecifier<?>> orders = new ArrayList<>();

        if ("인기".equals(sort)) {
            // 1차: 인기순 (조회수 등)
            // orders.add(course.viewCount.desc());
            // 2차: ID순 (인기 점수가 같을 때 순서 보장)
            orders.add(course.id.desc());
        } else {
            // 최신순 (기본) id 내림차순이 거의 최신순임
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

    // [4번 API]
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

        return Optional.ofNullable(resCourse); // 반환값 null 가능성
    }

}