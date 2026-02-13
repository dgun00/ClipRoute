package com.example.cliproute_project.domain.course.service.command;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;

public interface CourseCommandService {
    // [5 API]
    CourseResDTO.ScrapResultDTO scrapCourse(String email, Long courseId, CourseReqDTO.CourseDateRequestDTO travelPeriod);
}
