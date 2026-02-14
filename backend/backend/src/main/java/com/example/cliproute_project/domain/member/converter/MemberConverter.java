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

    // [6 API] 생략 (동일)
    public static MemberResDTO.FilterOptionsDTO toFilterOptionsDTO(List<MyCourseRegionOptionFlat> regions, List<Integer> travelDays, List<TravelStatus> travelStatuses) {
        List<MemberResDTO.RegionOptionDTO> regionOptions = (regions == null || regions.isEmpty()) ? List.of() : regions.stream().map(MemberConverter::toRegionOptionDTO).toList();
        List<Integer> travelDaysOptions = (travelDays == null || travelDays.isEmpty()) ? List.of() : List.copyOf(travelDays);
        List<TravelStatus> travelStatusOptions = (travelStatuses == null || travelStatuses.isEmpty()) ? List.of() : List.copyOf(travelStatuses);
        return MemberResDTO.FilterOptionsDTO.builder().regions(regionOptions).travelDays(travelDaysOptions).travelStatuses(travelStatusOptions).build();
    }

    // [7 API] 생략 (동일)
    public static MemberResDTO.MyCourseListDTO toMyCourseListDTO(List<MyCourseListFlat> flats, SliceInfoDTO sliceInfoDTO, String sort) {
        List<MemberResDTO.MyCourseDTO> courses = (flats == null || flats.isEmpty()) ? List.of() : flats.stream().map(MemberConverter::toMyCourseDTO).toList();
        return MemberResDTO.MyCourseListDTO.builder().courseList(courses).sliceInfo(sliceInfoDTO).sort(sort).build();
    }

    private static MemberResDTO.MyCourseDTO toMyCourseDTO(MyCourseListFlat flat) {
        String thumbnailUrl = (flat.courseImageUrl() != null && !flat.courseImageUrl().isBlank()) ? flat.courseImageUrl() : flat.videoThumbnailUrl();
        Integer placeCount = flat.placeCount() != null ? flat.placeCount().intValue() : 0;
        return MemberResDTO.MyCourseDTO.builder().courseId(flat.courseId()).memberCourseId(flat.memberCourseId()).courseTitle(flat.courseTitle()).regionName(flat.regionName()).regionRepImageUrl(flat.regionRepImageUrl()).thumbnailUrl(thumbnailUrl).startDate(flat.startDate()).endDate(flat.endDate()).travelDays(flat.travelDays()).travelStatus(flat.travelStatus()).placeCount(placeCount).createdAt(flat.createdAt()).updatedAt(flat.updatedAt()).build();
    }

    private static MemberResDTO.RegionOptionDTO toRegionOptionDTO(MyCourseRegionOptionFlat flat) {
        return MemberResDTO.RegionOptionDTO.builder().id(flat.id()).name(flat.name()).build();
    }

    // [9 API] 수정한 부분 (필드명 매핑)
    public static MemberResDTO.MyCourseDetailDTO toMyCourseDetailDTO(List<MyCourseDetailFlat> flats) {
        if (flats == null || flats.isEmpty()) {
            return MemberResDTO.MyCourseDetailDTO.builder()
                    .itineraries(List.of())
                    .build();
        }

        MyCourseDetailFlat base = flats.get(0);
        List<MemberResDTO.MyCourseItineraryDTO> itineraries = toMyCourseItineraries(flats);

        return MemberResDTO.MyCourseDetailDTO.builder()
                .courseId(base.courseId())
                .videoTitle(base.courseTitle()) // videoTitle 대신 courseTitle 사용
                .videoUrl(null) // 현재 Flat에 ytVideoId가 없으므로 임시 null
                .thumbnailUrl(base.thumbnailUrl())
                .channelName(base.nickname()) // channelName 대신 닉네임 사용
                .regionId(null) // 현재 Flat에 regionId가 없으므로 임시 null
                .regionName(base.regionName())
                .isScrapped(false) // 임시 처리
                .travelStatus(base.travelStatus())
                .courseTitle(base.courseTitle())
                .startDate(base.startDate())
                .endDate(base.endDate())
                .itineraries(itineraries)
                .build();
    }

    private static List<MemberResDTO.MyCourseItineraryDTO> toMyCourseItineraries(List<MyCourseDetailFlat> flats) {
        List<MyCourseDetailFlat> validFlats = flats.stream()
                .filter(flat -> flat.visitDay() != null)
                .sorted(Comparator
                        .comparing(MyCourseDetailFlat::visitDay, Comparator.nullsLast(Integer::compareTo))
                        .thenComparing(MyCourseDetailFlat::coursePlaceId, Comparator.nullsLast(Long::compareTo)) // visitOrder 대신 ID 순서
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
                .visitOrder(0) // visitOrder 필드가 Flat에 없으므로 임시 0
                .coursePlaceId(flat.coursePlaceId())
                .placeId(0L) // placeId 필드가 Flat에 없으므로 임시 0L
                .placeName(flat.placeName())
                .placeCategory(flat.placeCategory().toString()) // Enum을 String으로 변환
                .address(flat.address())
                .lat(flat.latitude()) // lat -> latitude
                .lng(flat.longitude()) // lng -> longitude
                .timestamp(0) // timestamp 필드 없음
                .deletedAt(null) // deletedAt 필드 없음
                .build();
    }

    public static MemberResDTO.MyCourseDeleteResultDTO toMyCourseDeleteResultDTO(Long courseId, java.time.LocalDateTime deletedAt) {
        return MemberResDTO.MyCourseDeleteResultDTO.builder().courseId(courseId).deletedAt(deletedAt).build();
    }

    private static String buildYoutubeUrl(String ytVideoId) {
        if (ytVideoId == null || ytVideoId.isBlank()) { return null; }
        return YOUTUBE_WATCH_URL_PREFIX + ytVideoId;
    }
}