package com.example.cliproute_project.domain.course.repository;

import com.example.cliproute_project.domain.course.entity.Course;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;

import java.util.Optional;

public interface CourseRepositoryCustom {

    // [2 API] 필터 기준에 따라 코스 리스트 fetch
    Slice<Course> findCoursesByFilter(Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId,  Integer lastValue, Pageable pageable);
    Slice<Course> findCoursesByFilterWithRecommendation(Long regionId, Integer travelDays, String sort, Long seed, Pageable pageable);
    Long countCoursesByFilter(Long regionId, Integer travelDays, Boolean isRep);

    // [4 API] 비로그인 / 로그인 공통, 코스 상세의 itineraries, member-course 외의 데이터 fetch
    Optional<Course> findByIdWithVideoAndRegion(Long courseId);

}

