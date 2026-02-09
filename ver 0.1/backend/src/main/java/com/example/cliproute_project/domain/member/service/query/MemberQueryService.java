package com.example.cliproute_project.domain.member.service.query;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.enums.TravelStatus;


public interface MemberQueryService {

    // [6 API] My course filter options
    MemberResDTO.FilterOptionsDTO getMyCourseFilterOptions(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    // [7 API] My course list
    MemberResDTO.MyCourseListDTO getMyCourses(
            Long memberId,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus,
            Long lastMemberCourseId,
            Integer pageSize
    );

    // [9 API] My course detail
    MemberResDTO.MyCourseDetailDTO getMyCourseDetail(Long memberId, Long courseId);
}

