package com.example.cliproute_project.domain.course.repository;

import com.example.cliproute_project.domain.course.entity.QCourse;
import com.example.cliproute_project.domain.course.entity.mapping.QCoursePlace;
import com.example.cliproute_project.domain.course.repository.projection.CoursePlaceDetailFlat;
import com.example.cliproute_project.domain.place.entity.QPlace;
import com.example.cliproute_project.domain.video.entity.mapping.QVideoPlace;
import com.querydsl.core.types.Projections;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;

import java.util.List;


@Repository
@RequiredArgsConstructor
public class CourseDetailQueryRepository {

    private final JPAQueryFactory queryFactory;

    /**
     * API4(영상 코스 상세)용: CoursePlace + Place + VideoPlace(timestamp) 조회
     *
     * 3중조인 + 매핑테이블이 포함돼있어 복잡해져서 flat한 projection fetch하는 리포지토리
     */


    public List<CoursePlaceDetailFlat> findCoursePlaceDetails(Long courseId) {
        QCourse c = QCourse.course;
        QCoursePlace cp = QCoursePlace.coursePlace;
        QPlace p = QPlace.place;
        QVideoPlace vp = QVideoPlace.videoPlace;

        return queryFactory
                .select(Projections.constructor( // DB 데이터를 바로 DTO에 넣는 구문
                        CoursePlaceDetailFlat.class,
                        cp.id,
                        cp.visitDay,
                        cp.visitOrder,
                        p.id,
                        p.placeName,
                        // 카테고리 정책은 팀 룰로 확정 필요 (예: aiTag 우선)
                        p.placeCategory,
                        p.address,
                        p.lat,
                        p.lng,
                        vp.timestamp,
                        p.deletedAt
                ))
                .from(cp)
                .join(cp.course, c)
                .join(cp.place, p)
                .leftJoin(vp).on(
                        vp.video.eq(c.sourceVideo)
                                .and(vp.place.eq(p))
                )
                .where(
                        c.id.eq(courseId),
                        c.deletedAt.isNull()
//                        p.deletedAt.isNull(), 아예 안불러오지말고 삭제된 장소라고 알리기
//                        cp.deletedAt.isNull()
                )
                .orderBy(cp.visitDay.asc(), cp.visitOrder.asc())
                .fetch();
    }
}