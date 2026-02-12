package com.example.cliproute.domain.region.entity;

import com.example.cliproute.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.*;


@Entity
@Getter
@Builder
@AllArgsConstructor
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "REGIONS")
public class Region extends BaseEntity {

    // 디폴트 이미지 링크
    public static final String DEFAULT_REGION_IMAGE = "https://example.com/default.png";

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 지역명
    @Column(name = "region_name", nullable = false, unique = true, length = 50)
    private String regionName;

    // 검색 키워드
    // 연관검색어.(사용자가 입력할 만한 단어들을 모아놓은 컬럼) ( ex, "구마모토, 쿠마모토, kumamoto, 아소산")
    @Column(name= "search_keyword") // 일단 nullable
    private String searchKeyword;

    // 대표 이미지
    @Column(name = "image_url", nullable = false)
    private String imageUrl = DEFAULT_REGION_IMAGE; // 디폴트 이미지 값

    // 지역 노출 순서 (null 이면 맨뒤에서 생성순 정렬)
    @Column(name = "order_index")
    private Integer orderIndex;
    
    // 활성 여부
    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}