package com.example.cliproute.domain.member.dto.req;

import com.example.cliproute_project.domain.member.enums.TravelStatus;

import java.time.LocalDate;
import java.util.List;

public class MemberReqDTO {

    // [10 API] My course detail edit
    public record MyCourseDetailEditDTO(
            String courseTitle,
            LocalDate startDate,
            LocalDate endDate,
            TravelStatus travelStatus,
            List<MyCourseItineraryEditDTO> itineraries
    ) {}

    // [10 API]
    public record MyCourseItineraryEditDTO(
            Integer visitDay,
            List<MyCourseItemEditDTO> items
    ) {}

    // [10 API] 두 요소중 하나만 기입
    public record MyCourseItemEditDTO(
            Long coursePlaceId,
            Long placeId
    ) {}
}
