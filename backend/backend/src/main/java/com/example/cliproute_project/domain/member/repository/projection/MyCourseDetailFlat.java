package com.example.cliproute_project.domain.member.repository.projection;

import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.place.enums.PlaceCategory; // 카테고리 Enum 확인 필요

import java.time.LocalDate;
import java.time.LocalDateTime;

public record MyCourseDetailFlat(
        Long courseId,               // 1
        String videoTitle,           // 2. 추가 (영상 제목)
        String ytVideoId,            // 3. 추가 (URL 생성용)
        String channelName,          // 4. 추가 (채널명)
        Long regionId,               // 5. 추가 (지역 ID)
        String regionName,           // 6
        String regionRepImageUrl,    // 7
        String thumbnailUrl,         // 8
        Long memberCourseId,         // 9
        String nickname,             // 10
        Boolean isMine,              // 11
        Boolean isScrapped,          // 12. 추가 (스크랩 여부)
        TravelStatus travelStatus,   // 13
        String courseTitle,          // 14
        String memo,                 // 15
        LocalDate startDate,         // 16
        LocalDate endDate,           // 17
        Integer travelDays,          // 18
        Integer likeCount,           // 19
        Long scrapCount,             // 20
        Long coursePlaceId,          // 21
        Long placeId,                // 22. 추가 (장소 PK)
        String placeName,            // 23
        PlaceCategory placeCategory, // 24
        String address,              // 25
        Double latitude,             // 26
        Double longitude,            // 27
        Integer visitDay,            // 28
        Integer visitOrder,          // 29. 추가 (방문 순서)
        LocalDateTime updatedAt      // 30
) {}