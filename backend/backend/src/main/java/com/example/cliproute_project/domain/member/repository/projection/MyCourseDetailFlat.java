package com.example.cliproute_project.domain.member.repository.projection;

import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.place.enums.PlaceCategory;

import java.time.LocalDate;
import java.time.LocalDateTime;

public record MyCourseDetailFlat(
        Long courseId,
        String courseTitle,
        Long regionId,             // 추가
        String regionName,
        String regionRepImageUrl,
        String videoUrl,           // 추가
        String thumbnailUrl,
        Long memberCourseId,
        String nickname,
        Boolean isMine,
        Boolean isScrapped,        // 추가
        TravelStatus travelStatus,
        String memo,
        LocalDate startDate,
        LocalDate endDate,
        Integer travelDays,
        Long coursePlaceId,
        Long placeId,
        Integer visitOrder,
        String placeName,
        PlaceCategory placeCategory,
        String address,
        Double latitude,
        Double longitude,
        Integer visitDay,
        Integer timestamp,         // 추가
        LocalDateTime updatedAt
) {
}
