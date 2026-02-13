package com.example.cliproute_project.domain.member.service.command;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.entity.mapping.CoursePlace;
import com.example.cliproute_project.domain.course.repository.CoursePlaceRepository;
import com.example.cliproute_project.domain.member.converter.MemberConverter;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.exception.MemberException;
import com.example.cliproute_project.domain.member.exception.code.MemberCourseErrorCode;
import com.example.cliproute_project.domain.member.exception.code.MemberErrorCode;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.place.entity.Place;
import com.example.cliproute_project.domain.place.repository.PlaceRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

@Service
@RequiredArgsConstructor
@Transactional
public class MemberCommandServiceImpl implements MemberCommandService {

    private final MemberCourseRepository memberCourseRepository;
    private final CoursePlaceRepository coursePlaceRepository;
    private final PlaceRepository placeRepository;

    // [8 API]
    @Override
    public MemberResDTO.MyCourseDeleteResultDTO deleteMyCourse(Long memberId, Long courseId) {
        if (memberId == null) {
            throw new MemberException(MemberErrorCode.UNAUTHORIZED);
        }
        if (courseId == null || courseId <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_COURSE_ID);
        }

        MemberCourse memberCourse = memberCourseRepository.findByMemberIdAndCourseId(memberId, courseId)
                .orElseThrow(() -> new MemberException(MemberCourseErrorCode.MY_COURSE_NOT_FOUND));

        LocalDateTime deletedAt = memberCourse.getDeletedAt();
        if (deletedAt == null) {
            deletedAt = LocalDateTime.now();
            memberCourse.markDeleted(deletedAt);

            Course course = memberCourse.getCourse();
            if (course == null) {
                throw new MemberException(MemberCourseErrorCode.MY_COURSE_NOT_FOUND);
            }
            if (course != null && Boolean.TRUE.equals(course.getIsCustomized())) {
                course.markDeleted(deletedAt);
            }

            List<CoursePlace> coursePlaces = coursePlaceRepository.findAllByCourseId(course.getId());
            for (CoursePlace coursePlace : coursePlaces) {
                coursePlace.markDeleted(deletedAt);
            }
        }

        return MemberConverter.toMyCourseDeleteResultDTO(courseId, deletedAt);
    }

    // [10 API]
    @Override
    public MemberResDTO.MyCourseDetailDTO editMyCourseDetail(
            Long memberId,
            Long courseId,
            MemberReqDTO.MyCourseDetailEditDTO request
    ) {
        if (memberId == null) {
            throw new MemberException(MemberErrorCode.UNAUTHORIZED);
        }
        if (courseId == null || courseId <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_COURSE_ID);
        }
        if (request == null) {
            throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
        }

        boolean exists = memberCourseRepository.existsMyCourseDetailScope(memberId, courseId);
        if (!exists) {
            throw new MemberException(MemberCourseErrorCode.MY_COURSE_ACCESS_DENIED);
        }

        MemberCourse memberCourse = memberCourseRepository.findByMemberIdAndCourseIdAndDeletedAtIsNull(memberId, courseId)
                .orElseThrow(() -> new MemberException(MemberCourseErrorCode.MY_COURSE_NOT_FOUND));

        Course course = memberCourse.getCourse();
        if (course == null) {
            throw new MemberException(MemberCourseErrorCode.MY_COURSE_NOT_FOUND);
        }
        if (course.getDeletedAt() != null) {
            throw new MemberException(MemberCourseErrorCode.COURSE_ALREADY_DELETED);
        }
        if (!Boolean.TRUE.equals(course.getIsCustomized())) {
            throw new MemberException(MemberCourseErrorCode.COURSE_NOT_EDITABLE);
        }

        if (request.courseTitle() != null) {
            course.updateTitle(request.courseTitle());
        }

        if (request.travelStatus() != null) {
            memberCourse.updateTravelStatus(request.travelStatus());
        }

        if (request.startDate() != null || request.endDate() != null) {
            validateAndApplyTravelPeriod(memberCourse, course, request.startDate(), request.endDate());
        }

        if (request.itineraries() != null) {
            applyItineraries(course, request.itineraries());
        }

        List<MyCourseDetailFlat> flats = memberCourseRepository.findMyCourseDetailFlats(memberId, courseId);
        if (flats == null || flats.isEmpty()) {
            throw new MemberException(MemberCourseErrorCode.MY_COURSE_NOT_FOUND);
        }

        return MemberConverter.toMyCourseDetailDTO(flats);
    }

    // [10 API]
    private void validateAndApplyTravelPeriod(
            MemberCourse memberCourse,
            Course course,
            LocalDate startDate,
            LocalDate endDate
    ) {
        if (startDate == null || endDate == null) {
            throw new MemberException(MemberCourseErrorCode.INVALID_DATE_RANGE);
        }
        if (endDate.isBefore(startDate)) {
            throw new MemberException(MemberCourseErrorCode.INVALID_DATE_RANGE);
        }

        memberCourse.updateTravelPeriod(startDate, endDate);
        int travelDays = Math.toIntExact(ChronoUnit.DAYS.between(startDate, endDate)) + 1;
        course.updateTravelDays(travelDays);
    }

    // [10 API]
    private void applyItineraries(
            Course course,
            List<MemberReqDTO.MyCourseItineraryEditDTO> itineraries
    ) {
        validateVisitDays(itineraries);

        List<CoursePlace> existingPlaces = coursePlaceRepository.findAllByCourseId(course.getId());
        Map<Long, CoursePlace> existingMap = new HashMap<>();
        for (CoursePlace coursePlace : existingPlaces) {
            existingMap.put(coursePlace.getId(), coursePlace);
        }

        Set<Long> requestCoursePlaceIds = new HashSet<>();
        Set<Long> requestPlaceIds = new HashSet<>();
        for (MemberReqDTO.MyCourseItineraryEditDTO itinerary : itineraries) {
            if (itinerary == null) {
                throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
            }
            List<MemberReqDTO.MyCourseItemEditDTO> items = itinerary.items();
            if (items == null) {
                throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
            }
            for (MemberReqDTO.MyCourseItemEditDTO item : items) {
                validateItem(item);
                if (item.coursePlaceId() != null) {
                    requestCoursePlaceIds.add(item.coursePlaceId());
                } else {
                    requestPlaceIds.add(item.placeId());
                }
            }
        }

        for (Long coursePlaceId : requestCoursePlaceIds) {
            if (!existingMap.containsKey(coursePlaceId)) {
                throw new MemberException(MemberCourseErrorCode.COURSE_PLACE_NOT_FOUND);
            }
        }

        Map<Long, Place> placeMap = fetchPlaces(requestPlaceIds);

        Set<Long> keptCoursePlaceIds = new HashSet<>();
        List<CoursePlace> newCoursePlaces = new ArrayList<>();

        for (MemberReqDTO.MyCourseItineraryEditDTO itinerary : itineraries) {
            if (itinerary == null) {
                throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
            }
            Integer visitDay = itinerary.visitDay();
            List<MemberReqDTO.MyCourseItemEditDTO> items = itinerary.items();
            if (items == null) {
                throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
            }

            int visitOrder = 1;
            for (MemberReqDTO.MyCourseItemEditDTO item : items) {
                if (item.coursePlaceId() != null) {
                    if (!keptCoursePlaceIds.add(item.coursePlaceId())) {
                        throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
                    }
                    CoursePlace coursePlace = existingMap.get(item.coursePlaceId());
                    coursePlace.updateVisitInfo(visitDay, visitOrder);
                } else {
                    Place place = placeMap.get(item.placeId());
                    CoursePlace coursePlace = CoursePlace.create(course, place, visitDay, visitOrder);
                    newCoursePlaces.add(coursePlace);
                }
                visitOrder++;
            }
        }

        Set<Long> toDeleteIds = new HashSet<>();
        for (Long existingId : existingMap.keySet()) {
            if (!keptCoursePlaceIds.contains(existingId)) {
                toDeleteIds.add(existingId);
            }
        }

        if (!toDeleteIds.isEmpty()) {
            coursePlaceRepository.deleteAllByIdInBatch(toDeleteIds);
        }
        if (!newCoursePlaces.isEmpty()) {
            coursePlaceRepository.saveAll(newCoursePlaces);
        }
    }

    // [10 API]
    private void validateVisitDays(List<MemberReqDTO.MyCourseItineraryEditDTO> itineraries) {
        if (itineraries == null || itineraries.isEmpty()) {
            return;
        }

        Set<Integer> uniqueDays = new HashSet<>();
        for (MemberReqDTO.MyCourseItineraryEditDTO itinerary : itineraries) {
            if (itinerary == null) {
                throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
            }
            Integer visitDay = itinerary.visitDay();
            if (visitDay == null || visitDay <= 0) {
                throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
            }
            if (!uniqueDays.add(visitDay)) {
                throw new MemberException(MemberCourseErrorCode.DUPLICATE_VISIT_DAY);
            }
        }

        List<Integer> sortedDays = new ArrayList<>(uniqueDays);
        sortedDays.sort(Integer::compareTo);
        if (sortedDays.get(0) != 1) {
            throw new MemberException(MemberCourseErrorCode.INVALID_VISIT_DAY_SEQUENCE);
        }
        for (int i = 1; i < sortedDays.size(); i++) {
            if (sortedDays.get(i) != sortedDays.get(i - 1) + 1) {
                throw new MemberException(MemberCourseErrorCode.INVALID_VISIT_DAY_SEQUENCE);
            }
        }
    }

    // [10 API]
    private void validateItem(MemberReqDTO.MyCourseItemEditDTO item) {
        if (item == null) {
            throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
        }
        boolean hasCoursePlaceId = item.coursePlaceId() != null;
        boolean hasPlaceId = item.placeId() != null;
        if (hasCoursePlaceId == hasPlaceId) {
            throw new MemberException(MemberCourseErrorCode.INVALID_REQUEST);
        }
    }

    // [10 API]
    private Map<Long, Place> fetchPlaces(Set<Long> placeIds) {
        if (placeIds == null || placeIds.isEmpty()) {
            return Map.of();
        }

        List<Place> places = placeRepository.findAllByIdInAndDeletedAtIsNull(placeIds);
        if (places.size() != placeIds.size()) {
            throw new MemberException(MemberCourseErrorCode.PLACE_NOT_FOUND);
        }

        Map<Long, Place> placeMap = new HashMap<>();
        for (Place place : places) {
            placeMap.put(place.getId(), place);
        }
        return placeMap;
    }
}
