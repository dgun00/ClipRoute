package com.example.cliproute_project.domain.member.converter;

import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseListFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseRegionOptionFlat;
import com.example.cliproute_project.global.common.dto.SliceInfoDTO;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class MemberConverter {

    private static final String YOUTUBE_WATCH_URL_PREFIX = "https://www.youtube.com/watch?v=";

    public static MemberResDTO.FilterOptionsDTO toFilterOptionsDTO(
            List<MyCourseRegionOptionFlat> regions,
            List<Integer> travelDays,
            List<TravelStatus> travelStatuses
    ) {
        List<MemberResDTO.RegionOptionDTO> regionOptions =
                (regions == null || regions.isEmpty()) ? List.of() : regions.stream().map(MemberConverter::toRegionOptionDTO).toList();
        List<Integer> travelDaysOptions = (travelDays == null || travelDays.isEmpty()) ? List.of() : List.copyOf(travelDays);
        List<TravelStatus> travelStatusOptions =
                (travelStatuses == null || travelStatuses.isEmpty()) ? List.of() : List.copyOf(travelStatuses);

        return MemberResDTO.FilterOptionsDTO.builder()
                .regions(regionOptions)
                .travelDays(travelDaysOptions)
                .travelStatuses(travelStatusOptions)
                .build();
    }

    public static MemberResDTO.MyCourseListDTO toMyCourseListDTO(
            List<MyCourseListFlat> flats,
            SliceInfoDTO sliceInfoDTO,
            String sort
    ) {
        List<MemberResDTO.MyCourseDTO> courses =
                (flats == null || flats.isEmpty()) ? List.of() : flats.stream().map(MemberConverter::toMyCourseDTO).toList();

        return MemberResDTO.MyCourseListDTO.builder()
                .courseList(courses)
                .sliceInfo(sliceInfoDTO)
                .sort(sort)
                .build();
    }

    private static MemberResDTO.MyCourseDTO toMyCourseDTO(MyCourseListFlat flat) {
        Integer placeCount = flat.placeCount() != null ? flat.placeCount().intValue() : 0;

        return MemberResDTO.MyCourseDTO.builder()
                .courseId(flat.courseId())
                .originalCourseId(flat.originalCourseId())
                .memberCourseId(flat.memberCourseId())
                .courseTitle(flat.courseTitle())
                .regionName(flat.regionName())
                .ytVideoId(flat.ytVideoId())
                .startDate(flat.startDate())
                .endDate(flat.endDate())
                .travelDays(flat.travelDays())
                .travelStatus(flat.travelStatus())
                .placeCount(placeCount)
                .createdAt(flat.createdAt())
                .updatedAt(flat.updatedAt())
                .build();
    }

    private static MemberResDTO.RegionOptionDTO toRegionOptionDTO(MyCourseRegionOptionFlat flat) {
        return MemberResDTO.RegionOptionDTO.builder()
                .id(flat.id())
                .name(flat.name())
                .build();
    }

    public static MemberResDTO.MyCourseDetailDTO toMyCourseDetailDTO(List<MyCourseDetailFlat> flats) {
        if (flats == null || flats.isEmpty()) {
            return MemberResDTO.MyCourseDetailDTO.builder()
                    .itineraries(List.of())
                    .build();
        }

        MyCourseDetailFlat base = flats.get(0);
//        List<MemberResDTO.MyCourseItineraryDTO> itineraries = toMyCourseItineraries(flats);

        return MemberResDTO.MyCourseDetailDTO.builder()
                .courseId(base.courseId())
                .videoTitle(base.courseTitle())
                .ytVideoId(base.ytVideoId())
                .channelName(base.channelName())
                .regionId(base.regionId())
                .regionName(base.regionName())
                .isScrapped(base.isScrapped())
                .travelStatus(base.travelStatus())
                .courseTitle(base.courseTitle())
                .startDate(base.startDate())
                .endDate(base.endDate())
                .itineraries(toMyCourseItineraries(flats))
                .build();
    }

    private static List<MemberResDTO.MyCourseItineraryDTO> toMyCourseItineraries(List<MyCourseDetailFlat> flats) {
        List<MyCourseDetailFlat> validFlats = flats.stream()
                .filter(flat -> flat.visitDay() != null)
                .sorted(Comparator
                        .comparing(MyCourseDetailFlat::visitDay, Comparator.nullsLast(Integer::compareTo))
                        .thenComparing(MyCourseDetailFlat::coursePlaceId, Comparator.nullsLast(Long::compareTo))
                )
                .toList();

        if (validFlats.isEmpty()) {
            return List.of();
        }

        Map<Integer, List<MyCourseDetailFlat>> byDay = validFlats.stream()
                .collect(Collectors.groupingBy(
                        MyCourseDetailFlat::visitDay,
                        LinkedHashMap::new,
                        Collectors.toList()
                ));

        List<MemberResDTO.MyCourseItineraryDTO> itineraries = new ArrayList<>(byDay.size());

        for (Map.Entry<Integer, List<MyCourseDetailFlat>> entry : byDay.entrySet()) {
            Integer visitDay = entry.getKey();
            List<MyCourseDetailFlat> dayFlats = entry.getValue();

            List<MemberResDTO.MyCoursePlaceDTO> places = dayFlats.stream()
                    .map(MemberConverter::toMyCoursePlaceDTO)
                    .toList();

            itineraries.add(MemberResDTO.MyCourseItineraryDTO.builder()
                    .visitDay(visitDay)
                    .places(places)
                    .build());
        }

        return itineraries;
    }

    private static MemberResDTO.MyCoursePlaceDTO toMyCoursePlaceDTO(MyCourseDetailFlat flat) {
        return MemberResDTO.MyCoursePlaceDTO.builder()
                .visitOrder(flat.visitOrder())   // 0 대신 flat 값
                .coursePlaceId(flat.coursePlaceId())
                .placeId(flat.placeId())         // 0 대신 flat 값
                .placeName(flat.placeName())
                .placeCategory(flat.placeCategory().toString())
                .address(flat.address())
                .lat(flat.latitude())
                .lng(flat.longitude())
//                .timestamp(flat.timestamp())     // flat 값 연결
                .deletedAt(null)
                .build();
    }

    public static MemberResDTO.MyCourseDeleteResultDTO toMyCourseDeleteResultDTO(
            Long courseId,
            java.time.LocalDateTime deletedAt
    ) {
        return MemberResDTO.MyCourseDeleteResultDTO.builder()
                .courseId(courseId)
                .deletedAt(deletedAt)
                .build();
    }

    private static String buildYoutubeUrl(String ytVideoId) {
        if (ytVideoId == null || ytVideoId.isBlank()) {
            return null;
        }
        return YOUTUBE_WATCH_URL_PREFIX + ytVideoId;
    }
}
