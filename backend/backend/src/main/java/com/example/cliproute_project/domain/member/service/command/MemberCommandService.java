package com.example.cliproute_project.domain.member.service.command;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;

public interface MemberCommandService {
    // [8 API]
    MemberResDTO.MyCourseDeleteResultDTO deleteMyCourse(Long memberId, Long courseId);

    // [10 API]
    MemberResDTO.MyCourseDetailDTO editMyCourseDetail(
            Long memberId,
            Long courseId,
            MemberReqDTO.MyCourseDetailEditDTO request
    );
}
