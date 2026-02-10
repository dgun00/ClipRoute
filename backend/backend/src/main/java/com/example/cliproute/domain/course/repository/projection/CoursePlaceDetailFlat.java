package com.example.cliproute.domain.course.repository.projection;

import java.time.LocalDateTime;
//[4 API]
// CourseDetailQueryRepository 조회 결과 담는 DTO
public record CoursePlaceDetailFlat(
        Long coursePlaceId,
        Integer visitDay,
        Integer visitOrder,
        Long placeId,
        String placeName,
        String placeCategory,
        String address,
        Double lat,
        Double lng,
        Integer timestamp,
        LocalDateTime deletedAt
) {}