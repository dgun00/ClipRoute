package com.example.cliproute_project.domain.course.service.query;

import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;

public interface CourseQueryService  {

    CourseResDTO.CoursePublicListDTO getCourseList(
            Long regionId, Integer travelDays, String sort, Long lastCourseId, Integer lastValue, Integer size
    );
    CourseResDTO.CoursePublicListDTO getCourseListWithRecommendation(
            Long regionId, Integer travelDays, String sort, int page, int size
    );
    CourseResDTO.CourseDetailDTO getCourseDetail(
            Long courseId, Long memberId
    );
}
