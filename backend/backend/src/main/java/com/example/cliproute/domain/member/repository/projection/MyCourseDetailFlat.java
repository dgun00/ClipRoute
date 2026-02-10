package com.example.cliproute.domain.member.repository.projection;

import com.example.cliproute_project.domain.member.enums.TravelStatus;

import java.time.LocalDate;
import java.time.LocalDateTime;

// [9 API]
public record MyCourseDetailFlat(
        Long courseId,
        String videoTitle,
        String ytVideoId,
        String thumbnailUrl,
        String channelName,
        Long regionId,
        String regionName,
        Boolean isScrapped,
        TravelStatus travelStatus,
        String courseTitle,
        LocalDate startDate,
        LocalDate endDate,
        Integer visitDay,
        Integer visitOrder,
        Long coursePlaceId,
        Long placeId,
        String placeName,
        String placeCategory,
        String address,
        Double lat,
        Double lng,
        Integer timestamp,
        LocalDateTime deletedAt
) {
}
