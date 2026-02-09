package com.example.cliproute_project.domain.place.entity;

import com.example.cliproute_project.domain.place.enums.PlaceCategory;
import com.example.cliproute_project.domain.region.entity.Region;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "PLACES")
public class Place extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 지역 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "region_id", nullable = false)
    private Region region;
    
    // 장소명
    @Column(name = "place_name", nullable = false)
    private String placeName;
    
    // ai 태그
    @Column(name = "ai_tag") // 일단 nullable
    private String aiTag; // "식당", "카페" 등
    
    // 지도 카테고리
    @Enumerated(EnumType.STRING)
    @Column(name = "place_category", nullable = false) // 일단 nullable
    private PlaceCategory placeCategory;
    
    // 주소
    @Column // 일단 nullable
    private String address;

    // 위도
    @Column(nullable = false)
    private Double lat;

    // 경도
    @Column(nullable = false)
    private Double lng;

    // 외부 지도 id
    @Column(name = "external_id") // 일단 nullable
    private String externalId;

    // 외부 링크(지도 or 검색엔진)
    @Column(name = "external_link")
    private String externalLink; // 외부 지도 링크

    // 삭제 일시
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

}
