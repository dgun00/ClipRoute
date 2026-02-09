package com.example.cliproute_project.domain.member.repository.membercourse;

import com.example.cliproute_project.domain.course.entity.QCourse;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.entity.mapping.QMemberCourse;
import com.querydsl.jpa.impl.JPAQueryFactory;
import lombok.RequiredArgsConstructor;

import java.util.Optional;

@RequiredArgsConstructor
public class MemberCourseRepositoryImpl implements MemberCourseRepositoryCustom {

    private final JPAQueryFactory queryFactory;

    // [4번 API]
    @Override // 비로그인/로그인 상세 조회시 스크랩 여부판단
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
                        // 원본 기준 매칭 (원본 자체 상세도 방어하려면 OR 추가), 커스된 됐을때와 코스가 원본일때
                        c.originalCourse.id.eq(originalCourseId).or(c.id.eq(originalCourseId))
                )
                .orderBy(mc.id.desc()) // 만약 중복이 있다면(의도x)가장 최근 생성 스크랩
                .fetchFirst();

        return Optional.ofNullable(result);
    }

    // --- [5번 API] 스크랩 ---
    @Override // 해당 코스를 스크랩 했는가 확인 메서드(멱등성)
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

    @Override // 현재 떠잇는 코스 기준으로 작성 했던 custom 코스 있는지 확인하는 메서드(원본 코스 기준 2개이상 커스텀코스 생성 막기위함,멱등성)
    public Optional<MemberCourse> findActiveScrapByCourseId(Long memberId, Long courseId) {
        QMemberCourse mc = QMemberCourse.memberCourse;
        QCourse c = QCourse.course;

        // 멤버-코스 엔티티 리턴
        MemberCourse result = queryFactory
                .selectFrom(mc)
                .join(mc.course, c).fetchJoin() // service에서 course 접근할 거면 N+1 방지
                .where(
                        mc.member.id.eq(memberId),
                        mc.deletedAt.isNull(),
                        mc.isScrapped.isTrue(),
                        c.originalCourse.id.eq(courseId)
                )
                .fetchFirst();

        return Optional.ofNullable(result);
    }


}
