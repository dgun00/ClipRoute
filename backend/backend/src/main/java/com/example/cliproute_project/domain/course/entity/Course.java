package com.example.cliproute_project.domain.course.entity;

import com.example.cliproute_project.domain.region.entity.Region;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.video.entity.Video;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "COURSES")
public class Course extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    // 원본 영상 ID
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "source_video_id", nullable = false)
    private Video sourceVideo; // 이 코스의 원본이 된 영상
    
    // 코스 지역 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_id", nullable = false)
    private Region region;
    
    // 만든 사람 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id", nullable = false)
    private Member author; // 작성자

    // 원본 코스 id
    @ManyToOne(fetch = FetchType.LAZY) // 자기 참조
    @JoinColumn(name = "original_course_id")
    private Course originalCourse; // 원본 코스면 null

    // 코스 제목
    @Column(nullable = false)
    private String title;
    
    // 코스 설명
    @Column
    private String description;
    
    // 여행 총 일수
    @Column(name = "travel_days", nullable = false)
    private Integer travelDays; // 1박2일 -> 2

    // 커스텀 여부
    @Column(name = "is_customized", nullable = false)
    private Boolean isCustomized = false; // 사용자가 수정,스크랩한 코스인지 여부

    //대표 코스 여부
    @Column(name = "is_rep", nullable = false)
    private Boolean isRep = false;

    // 삭제 일자
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    // [5 API] 스크랩 (static factory)
    // 원본을 커스텀한 코스 정보 생성
    public static Course createScrappedFrom(Course original, Member author) {
        Course c = new Course();
        c.sourceVideo = original.sourceVideo;
        c.region = original.region;
        c.author = author;
        c.originalCourse = original;

        c.title = original.title;
        c.description = original.description;
        c.travelDays = original.travelDays;

        c.isCustomized = true; // 스크랩 직후는 true임, 원본 코스와 구분 실제 수정안했어도 복사본자체가 iscustomized로 간주
        c.deletedAt = null;
        return c;
    }


    // [8 API]
    public void markDeleted(LocalDateTime deletedAt) {
        this.deletedAt = deletedAt;
    }

    // [10 API]
    public void updateTitle(String title) {
        this.title = title;
    }

    // [10 API]
    public void updateTravelDays(Integer travelDays) {
        this.travelDays = travelDays;
    }
}
