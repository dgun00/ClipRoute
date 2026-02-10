package com.example.cliproute.domain.course.service.query;

import com.example.cliproute.domain.course.dto.res.CourseResDTO;

public interface CourseQueryService  {

    // [2 API]
    CourseResDTO.CoursePublicListDTO getCourseList(
            Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId, Integer lastValue, Integer size
    );
    // [3 API]
    CourseResDTO.CoursePublicListDTO getCourseListWithRecommendation(
            Long regionId, Integer travelDays, String sort, Long seed, int page, int size
    );
    // [4 API]
    CourseResDTO.CourseDetailDTO getCourseDetail(
            Long courseId, Long memberId
    );
}

