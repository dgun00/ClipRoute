package com.example.cliproute_project.domain.member.service.query;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.enums.TravelStatus;

public interface MemberQueryService {

    // [6 API] 내 코스 필터 옵션 조회
    MemberResDTO.FilterOptionsDTO getMyCourseFilterOptions(
            String email,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    );

    // [7 API] 내 코스 리스트 조회
    MemberResDTO.MyCourseListDTO getMyCourses(
            String email,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus,
            Long lastMemberCourseId,
            Integer pageSize
    );

    // [9 API] 내 코스 상세 조회
    MemberResDTO.MyCourseDetailDTO getMyCourseDetail(String email, Long courseId);
}