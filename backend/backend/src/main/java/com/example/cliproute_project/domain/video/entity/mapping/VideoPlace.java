package com.example.cliproute_project.domain.video.entity.mapping;


import com.example.cliproute_project.domain.place.entity.Place;
import com.example.cliproute_project.domain.video.entity.Video;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;

import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "VIDEOS_PLACE")
public class VideoPlace extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 영상 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "video_id", nullable = false)
    private Video video;

    // 장소 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "place_id", nullable = false)
    private Place place;
    
    // 타임 스탬프 (sec)
//    @Column(nullable = false)
//    private Integer timestamp;

}
