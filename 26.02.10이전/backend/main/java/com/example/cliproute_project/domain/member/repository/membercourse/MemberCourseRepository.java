package com.example.cliproute_project.domain.member.repository.membercourse;

import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface MemberCourseRepository extends JpaRepository<MemberCourse,Long>, MemberCourseRepositoryCustom {
    /**
     * 로그인 시 코스 상세에서
     * 찜 여부 / 여행 상태 조회
     */
    Optional<MemberCourse> findByMemberIdAndCourseId(Long memberId,Long courseId);
    Optional<MemberCourse> findByMemberIdAndCourseIdAndDeletedAtIsNull(Long memberId, Long courseId);
}
