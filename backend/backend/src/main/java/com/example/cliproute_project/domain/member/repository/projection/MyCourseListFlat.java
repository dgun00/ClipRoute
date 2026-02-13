package com.example.cliproute_project.domain.member.repository.projection;

import com.example.cliproute_project.domain.member.enums.TravelStatus;

import java.time.LocalDate;
import java.time.LocalDateTime;

// [7 API]
public record MyCourseListFlat(
        Long courseId,
        Long memberCourseId,
        String courseTitle,
        String regionName,
        String regionRepImageUrl,
        String courseImageUrl,
        String videoThumbnailUrl,
        LocalDate startDate,
        LocalDate endDate,
        Integer travelDays,
        TravelStatus travelStatus,
        Long placeCount,
        LocalDateTime createdAt,
        LocalDateTime updatedAt
) {
}
