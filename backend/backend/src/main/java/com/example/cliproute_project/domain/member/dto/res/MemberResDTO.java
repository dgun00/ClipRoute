package com.example.cliproute_project.domain.member.dto.res;

import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.global.common.dto.SliceInfoDTO;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

public class MemberResDTO {
    // [6 API]
    @Builder
    public record FilterOptionsDTO(
            List<RegionOptionDTO> regions,
            List<Integer> travelDays,
            List<TravelStatus> travelStatuses
    ) {}

    @Builder
    public record RegionOptionDTO(
            Long id,
            String name
    ) {}

    // [7 API]
    @Builder
    public record MyCourseListDTO(
            List<MyCourseDTO> courseList,
            String sort,
            SliceInfoDTO sliceInfo
    ) {}

    @Builder
    public record MyCourseDTO(
            Long courseId,
            Long originalCourseId,
            Long memberCourseId,
            String courseTitle,
            String regionName,
            @JsonProperty("yt_video_id") String ytVideoId,
            LocalDate startDate,
            LocalDate endDate,
            Integer travelDays,
            TravelStatus travelStatus,
            Integer placeCount,
            LocalDateTime createdAt,
            LocalDateTime updatedAt
    ) {}

    // [9,10 API]
    @Builder
    public record MyCourseDetailDTO(
            Long courseId,
            String videoTitle,
            @JsonProperty("yt_video_id") String ytVideoId,
            String channelName,
            Long regionId,
            String regionName,
            Boolean isScrapped,
            TravelStatus travelStatus,
            String courseTitle,
            LocalDate startDate,
            LocalDate endDate,
            List<MyCourseItineraryDTO> itineraries
    ) {}

    @Builder
    public record MyCourseItineraryDTO(
            Integer visitDay,
            List<MyCoursePlaceDTO> places
    ) {}

    @Builder
    public record MyCoursePlaceDTO(
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
    ) {}

    // [8 API] My course delete
    @Builder
    public record MyCourseDeleteResultDTO(
            Long courseId,
            LocalDateTime deletedAt
    ) {}
}

