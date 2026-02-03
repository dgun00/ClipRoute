package com.example.cliproute_project.domain.course.repository.projection;

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
        Integer timestamp
) {}