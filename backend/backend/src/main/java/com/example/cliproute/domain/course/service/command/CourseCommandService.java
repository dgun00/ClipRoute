package com.example.cliproute.domain.course.service.command;

import com.example.cliproute.domain.course.dto.res.CourseResDTO;
import com.example.cliproute.domain.course.dto.req.CourseReqDTO;

public interface CourseCommandService {
    // [5 API]
    CourseResDTO.ScrapResultDTO scrapCourse(Long memberId, Long courseId, CourseReqDTO.CourseDateRequestDTO travelPeriod);
}
