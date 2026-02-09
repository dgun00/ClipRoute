package com.example.cliproute_project.domain.member.entity.mapping;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "MEMBER_COURSE")
public class MemberCourse extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 멤버 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    // 코스 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "course_id", nullable = false)
    private Course course; //
    
    // 여행 시작일
    @Column(name = "start_date")
    private LocalDate startDate;

    // 여행 종료일
    @Column(name = "end_date")
    private LocalDate endDate;

    // 여행 상태
    @Enumerated(EnumType.STRING)
    @Column(name = "travel_status", nullable = false)
    private TravelStatus travelStatus; // BEFORE, AFTER, PENDING 등

    @Column(name = "is_scrapped", nullable = false)
    private Boolean isScrapped;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    // [5번 API] 스크랩 (static factory)
    public static MemberCourse createScrap(Member member, Course course, TravelStatus status) {
        MemberCourse mc = new MemberCourse();
        mc.member = member;
        mc.course = course;
        mc.travelStatus = status;

        mc.isScrapped = true;
        mc.startDate = null;
        mc.endDate = null;
        mc.deletedAt = null;
        return mc;
    }

}