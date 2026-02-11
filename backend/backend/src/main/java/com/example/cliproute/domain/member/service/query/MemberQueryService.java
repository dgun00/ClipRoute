package com.example.cliproute.domain.member.service.query;

import com.example.cliproute.domain.member.dto.res.MemberResDTO;
import com.example.cliproute.domain.member.enums.TravelStatus;


public interface MemberQueryService {

    // 이메일로 멤버 ID 조회
    Long findIdByEmail(String email);

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

