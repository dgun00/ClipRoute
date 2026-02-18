package com.example.cliproute_project.domain.member.repository.projection;

import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.place.enums.PlaceCategory;

import java.time.LocalDate;
import java.time.LocalDateTime;

public record MyCourseDetailFlat(
        Long courseId,
        String courseTitle,
        Long regionId,
        String regionName,
        String ytVideoId,
        Long memberCourseId,
        String channelName,
        Boolean isMine,
        Boolean isScrapped,
        TravelStatus travelStatus,
        String memo,
        LocalDate startDate,
        LocalDate endDate,
        Integer travelDays,
//        Integer likeCount,
//        Long scrapCount,
        Long coursePlaceId,
        Long placeId,
        Integer visitOrder,
        String placeName,
        PlaceCategory placeCategory,
        String address,
        Double latitude,
        Double longitude,
        Integer visitDay,
//        Integer timestamp,
        LocalDateTime updatedAt
) {
}
