package com.example.cliproute.domain.course.repository;

import com.example.cliproute_project.domain.course.entity.mapping.CoursePlace;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface CoursePlaceRepository extends JpaRepository<CoursePlace, Long> {
    // [10 API]
    List<CoursePlace> findAllByCourseId(Long courseId);
}
