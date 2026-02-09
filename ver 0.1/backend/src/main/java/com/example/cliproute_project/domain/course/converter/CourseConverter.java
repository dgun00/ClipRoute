package com.example.cliproute_project.domain.course.converter;

import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.entity.Course;

import com.example.cliproute_project.domain.course.repository.projection.CoursePlaceDetailFlat;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.global.common.dto.SliceInfoDTO;

import java.util.*;
import java.util.stream.Collectors;

public class CourseConverter {

    // [2,3 API]
    public static CourseResDTO.CoursePublicDTO toCoursePublicDTO(Course course, boolean isRecommended) {
        return CourseResDTO.CoursePublicDTO.builder()
                .courseId(course.getId())
                .thumbnailUrl(course.getSourceVideo().getThumbnailUrl())
                .channelName(course.getSourceVideo().getChannelName())
                .videoTitle(course.getSourceVideo().getTitle())
                .travelDays(course.getTravelDays())
                .regionId(course.getRegion().getId())
                .regionName(course.getRegion().getRegionName())
                .isRecommended(isRecommended)
                .isRep(course.getIsRep())
                .isCustomized(course.getIsCustomized())
                .deletedAt(course.getDeletedAt())
                .build();
    }


    // [2,3 API]
    public static CourseResDTO.CoursePublicListDTO toCoursePublicListDTO(
            List<CourseResDTO.CoursePublicDTO> courses, SliceInfoDTO courseInfoDTO, Long totalElements, String sort, Long seed
    ) {

        return CourseResDTO.CoursePublicListDTO.builder()
                .courseList(courses)
                .sliceInfo(courseInfoDTO)
                .totalElements(totalElements)
                .sort(sort)
                .seed(seed)
                .build();
    }

    // [4 API]
    public static List<CourseResDTO.ItineraryDTO> toItineraries(List<CoursePlaceDetailFlat> flats) { // Flat 리스트 -> 일차별 Itinerary 리스트
        if (flats == null || flats.isEmpty()) { // 입력이 null/빈값이면
            return List.of(); // 빈 리스트 반환
        }

        List<CoursePlaceDetailFlat> sorted = flats.stream() // 입력 리스트를 스트림으로 변환
                .sorted(Comparator // 정렬 기준 정의
                        .comparing(CoursePlaceDetailFlat::visitDay, Comparator.nullsLast(Integer::compareTo)) // visitDay 오름차순 (null은 뒤로)
                        .thenComparing(CoursePlaceDetailFlat::visitOrder, Comparator.nullsLast(Integer::compareTo)) // visitOrder 오름차순 (null은 뒤로)
                )
                .toList(); // 정렬된 리스트로 수집

        Map<Integer, List<CoursePlaceDetailFlat>> byDay = sorted.stream() // 정렬된 리스트를 다시 스트림으로
                .collect(Collectors.groupingBy( // visitDay 기준으로 그룹핑
                        CoursePlaceDetailFlat::visitDay, // 그룹 키: visitDay
                        LinkedHashMap::new, // 입력 순서(visitDay 정렬 순서)를 보존하기 위해 LinkedHashMap 사용
                        Collectors.toList() // 각 day별로 리스트로 모음
                ));

        List<CourseResDTO.ItineraryDTO> itineraries = new ArrayList<>(byDay.size()); // 최종 결과 빈 리스트(일차 수만큼) 생성

        for (Map.Entry<Integer, List<CoursePlaceDetailFlat>> entry : byDay.entrySet()) { // day 그룹을 순회
            Integer visitDay = entry.getKey(); // 현재 일차(visitDay)
            List<CoursePlaceDetailFlat> dayFlats = entry.getValue(); // 해당 일차의 place 목록(flat)

            List<CourseResDTO.PlaceInItineraryDTO> places = dayFlats.stream() // 해당 일차의 flat 리스트를 스트림으로
                    .map(CourseConverter::toPlaceInItinerary) // flat 1개를 PlaceInItineraryDTO로 변환
                    .toList(); // 변환 결과를 리스트로 수집

            itineraries.add(new CourseResDTO.ItineraryDTO(visitDay, places)); // (visitDay, places)로 ItineraryDTO 생성 후 결과에 추가
        }

        return itineraries; // 최종 ItineraryDTO 리스트 반환
    }

    // [4 API]
    private static CourseResDTO.PlaceInItineraryDTO toPlaceInItinerary(CoursePlaceDetailFlat flat) { // Flat 1개 -> PlaceInItineraryDTO 1개
        return new CourseResDTO.PlaceInItineraryDTO( // 응답 DTO 생성(Flat에서 필요한 필드만 추출)
                flat.coursePlaceId(),// coursePlaceId
                flat.visitOrder(), // visitOrder
                flat.placeId(), // placeId
                flat.placeName(), // placeName
                flat.placeCategory(), // category
                flat.address(), // address
                flat.lat(), // lat
                flat.lng(), // lng
                flat.timestamp(), // 초 반환
                flat.deletedAt()
        );
    }

    // [5 API]
    public static CourseResDTO.ScrapResultDTO toScrapResult(
            Long newCourseId, Long originalCourseId, MemberCourse mc, CourseReqDTO.CourseDateRequestDTO travelPeriod
    ) {
        return new CourseResDTO.ScrapResultDTO(
                newCourseId,
                originalCourseId,
                mc.getIsScrapped(),
                mc.getTravelStatus(),
                travelPeriod.startDate(),
                travelPeriod.endDate(),
                mc.getCreatedAt()
        );
    }

}


