package com.example.cliproute.domain.member.repository.membercourse;

import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseListFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseRegionOptionFlat;

import java.util.List;
import java.util.Optional;

public interface MemberCourseRepositoryCustom {
    // [5 API]
    Optional<MemberCourse> findActiveScrapByCourseId(Long memberId, Long courseId);
    Optional<MemberCourse> findActiveScrapByOriginalCourseId(Long memberId, Long originalCourseId);
    boolean existsActiveScrapByCourseId(Long memberId, Long courseId);

    // [6 API]
    // [6 API] Filter option: regions
    List<MyCourseRegionOptionFlat> findDistinctRegionsForMyCourseFilters(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    // [6 API] Filter option: travel days
    List<Integer> findDistinctTravelDaysForMyCourseFilters(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    // [6 API] Filter option: travel status
    List<TravelStatus> findDistinctTravelStatusesForMyCourseFilters(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    // [7 API]
    List<MyCourseListFlat> findMyCoursesByFilter(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus,
            Long lastMemberCourseId,
            Integer pageSize
    );

    // [9 API]
    boolean existsMyCourseDetailScope(Long memberId, Long courseId);
    List<MyCourseDetailFlat> findMyCourseDetailFlats(Long memberId, Long courseId);
}

