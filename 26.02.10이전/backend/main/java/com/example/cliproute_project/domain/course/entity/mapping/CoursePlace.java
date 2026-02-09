package com.example.cliproute_project.domain.course.entity.mapping;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.place.entity.Place;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;


@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "COURSE_PLACE")
public class CoursePlace extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 코스 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "course_id", nullable = false)
    private Course course;

    // 장소 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "place_id", nullable = false)
    private Place place;

    // 방문 일차
    @Column(name = "visit_day")
    private Integer visitDay; // 몇 일차인지 (1일차, 2일차...)

    // 방문 순서
    @Column(name = "visit_order")
    private Integer visitOrder; // 그 날짜 내에서의 순서 (1, 2, 3...)

    // 삭제 일자
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;


}