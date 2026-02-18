package com.example.cliproute_project.domain.video.entity;

import com.example.cliproute_project.domain.region.entity.Region;
import com.example.cliproute_project.domain.video.enums.VideoFormat;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "videos")
public class Video extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 지역 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_id", nullable = false)
    private Region region;

    // 유튜브 영상 id
    @Column(name = "yt_video_id", unique = true, nullable = false)
    private String ytVideoId;

    // 영상 제목
    @Column(nullable = false)
    private String title;
    
    // 채널명
    @Column(name = "channel_name", nullable = false, length = 100)
    private String channelName;

    // 업로드일
    @Column(name = "upload_date")
    private LocalDateTime uploadDate;

    // 썸네일 url
    @Column(name = "thumbnail_url", nullable = false)
    private String thumbnailUrl;

    // 영상 길이 (sec)
    @Column(name = "duration")
    private Integer duration;
    
    // 자막 여부
    @Column(name = "has_caption")
    private Boolean hasCaption;
    
    // 영상 포맷
    @Enumerated(EnumType.STRING)
    @Column(name = "video_format")
    private VideoFormat videoFormat;
    
    // 삭제 일시
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;
    
}
