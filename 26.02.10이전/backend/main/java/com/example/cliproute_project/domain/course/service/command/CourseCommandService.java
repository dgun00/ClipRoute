package com.example.cliproute_project.domain.course.service.command;

import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;

public interface CourseCommandService {
    CourseResDTO.ScrapResultDTO scrapCourse(Long memberId, Long courseId);
}
