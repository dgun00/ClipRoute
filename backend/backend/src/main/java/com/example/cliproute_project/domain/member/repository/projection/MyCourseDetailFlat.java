package com.example.cliproute_project.domain.member.repository.projection;

import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.place.enums.PlaceCategory; // 카테고리 Enum 확인 필요

import java.time.LocalDate;
import java.time.LocalDateTime;

public record MyCourseDetailFlat(
        Long courseId,               // 1. Long
        String courseTitle,          // 2. String
        String regionName,           // 3. String
        String regionRepImageUrl,    // 4. String
        String thumbnailUrl,         // 5. String
        Long memberCourseId,         // 6. Long
        String nickname,             // 7. String
        Boolean isMine,              // 8. Boolean
        TravelStatus travelStatus,   // 9. TravelStatus (Enum)
        String memo,                 // 10. String
        LocalDate startDate,         // 11. LocalDate
        LocalDate endDate,           // 12. LocalDate
        Integer travelDays,          // 13. Integer
        Integer likeCount,           // 14. Integer
        Long scrapCount,             // 15. Long
        Long coursePlaceId,          // 16. Long
        String placeName,            // 17. String
        PlaceCategory placeCategory, // 18. PlaceCategory (Enum) - String에서 변경됨
        String address,              // 19. String
        Double latitude,             // 20. Double
        Double longitude,            // 21. Double
        Integer visitDay,            // 22. Integer
        LocalDateTime updatedAt      // 23. LocalDateTime
) {
}