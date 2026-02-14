package com.example.cliproute_project.domain.member.service.command;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;

public interface MemberCommandService {
    // [8 API]
    MemberResDTO.MyCourseDeleteResultDTO deleteMyCourse(String email, Long courseId);

    // [10 API]
    MemberResDTO.MyCourseDetailDTO editMyCourseDetail(
            String email,
            Long courseId,
            MemberReqDTO.MyCourseDetailEditDTO request
    );
}
