package com.example.cliproute_project.domain.course.dto.res;

import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.global.common.dto.SliceInfoDTO;
import lombok.Builder;

import java.time.LocalDateTime;
import java.util.List;

public class CourseResDTO {

    // --- 2,3번 API ---
    @Builder
    public record CoursePublicListDTO( // 비로그인 or 저장 x 코스 리스트 (2번 API)
            List<CoursePublicDTO> courseList,
            Long totalElements,
            String sort,
            SliceInfoDTO sliceInfo
    ) {}

    @Builder
    public record CoursePublicDTO( // 비로그인 or 저장 x 코스 데이터 (2번 API)
            Long courseId,
            String thumbnailUrl,
            String channelName,
            String videoTitle,
            Integer travelDays,
            Long regionId,
            String regionName,
            Boolean isRecommended
    ) {}
    // --- 4번 API ---
    @Builder
    public record CourseDetailDTO(
            Long courseId,
            String videoTitle,
            String videoUrl,
            String thumbnailUrl,
            String channelName,
            Long regionId,
            String regionName,
            Boolean isScrapped,
            TravelStatus travelStatus, // BEFORE, AFTER, NONE
            List<ItineraryDTO> itineraries
    ) {}

    @Builder
    public record ItineraryDTO(
            Integer visitDay,
            List<PlaceInItineraryDTO> places
    ) {}

    @Builder
    public record PlaceInItineraryDTO(
            Long coursePlaceId,
            Integer visitOrder,
            Long placeId,
            String placeName,
            String placeCategory,
            String address,
            Double lat,
            Double lng,
            Integer timestamp
    ) {}

    // --- 5번 API --- (스크랩 결과)
    public record ScrapResultDTO(
            Long newCourseId,
            Long originalCourseId,
            boolean isScrapped,
            TravelStatus travelStatus,
            LocalDateTime createdAt
    ) {}
}

