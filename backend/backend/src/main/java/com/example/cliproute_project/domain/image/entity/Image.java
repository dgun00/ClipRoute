package com.example.cliproute_project.domain.image.entity;

import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "images")
public class Image extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 이미지 url
    @Column(name = "image_url", nullable = false)
    private String imageUrl;

    // 파일 이름 (사용자 지정 파일 이름)
    @Column(name = "original_name", nullable = false)
    private String originalName; // 원본 파일명

//    // 저장 이름 (저장소에 저장된 파일 이름)
//    @Column(name = "stored_name", nullable = false, unique = true)
//    private String storedName; // 저장소 파일명 (UUID)
//
//    // 이미지 파일 크기(byte)
//    @Column(name = "file_size", nullable = false)
//    private Long fileSize;

    // 삭제일시
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

//    @Column(name = "s3_key")
//    private String s3Key; // S3 삭제용 키
}
