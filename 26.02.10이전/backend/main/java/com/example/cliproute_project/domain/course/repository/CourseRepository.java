package com.example.cliproute_project.domain.course.repository;

import com.example.cliproute_project.domain.course.entity.Course;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CourseRepository extends JpaRepository<Course,Long>, CourseRepositoryCustom  {


}
