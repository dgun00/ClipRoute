package com.example.cliproute_project.domain.term.entity;

import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "terms")
public class Term extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 약관 제목
    @Column(nullable = false, length = 100)
    private String title;

    // 약관 내용(간단)
    @Column
    private String content;

    // 약관 내용 링크(자세히)
    @Column(name = "content_url", nullable = false)
    private String contentUrl;

    // 필수 여부
    @Column(name = "is_required", nullable = false)
    private Boolean isRequired;

    // 약관 버전 (ex. ver 1.3.2)
    @Column(nullable = false)
    private String version;

    // 활성화 여부
    @Column(name = "is_active", nullable = false)
    private Boolean isActive;
}
