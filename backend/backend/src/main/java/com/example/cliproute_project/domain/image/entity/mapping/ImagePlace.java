package com.example.cliproute_project.domain.image.entity.mapping;

import com.example.cliproute_project.domain.image.entity.Image;
import com.example.cliproute_project.domain.image.enums.ImageType;
import com.example.cliproute_project.domain.place.entity.Place;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;

import lombok.Getter;
import lombok.NoArgsConstructor;


@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "image_place")
public class ImagePlace extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 이미지 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "image_id", nullable = false)
    private Image image;

    // 장소 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "place_id", nullable = false)
    private Place place;
    
    // 이미지 타입 (MENU(메뉴판), EXTERIOR(외관), INTERIOR(내부) 등)
    @Enumerated(EnumType.STRING)
    @Column(name = "image_type", nullable = false)
    private ImageType imageType;

    // 순서 (null 이면 생성 순)
    @Column(name = "sequence")
    private Integer sequence; // 노출 순서 (0번이 대표사진)
    
    // 설명
    @Column(name = "description")
    private String description;

}
