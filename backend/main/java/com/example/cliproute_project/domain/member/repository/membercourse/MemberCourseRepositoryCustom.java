package com.example.cliproute_project.domain.member.repository.membercourse;

import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;

import java.util.Optional;

public interface MemberCourseRepositoryCustom {
    // [5번 API]
    Optional<MemberCourse> findActiveScrapByCourseId(Long memberId, Long courseId);
    Optional<MemberCourse> findActiveScrapByOriginalCourseId(Long memberId, Long originalCourseId);
    boolean existsActiveScrapByCourseId(Long memberId, Long courseId);
}
