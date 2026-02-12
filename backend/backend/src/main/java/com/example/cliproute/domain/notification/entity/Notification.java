package com.example.cliproute.domain.notification.entity;

import com.example.cliproute.domain.notification.enums.NotiType;
import com.example.cliproute.domain.notification.enums.TargetGroup;
import com.example.cliproute.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "NOTIFICATIONS")
public class Notification extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 알림 제목
    @Column(nullable = false, length = 50)
    private String title;

    // 알림 내용
    @Column(nullable = false)
    private String content;

    // 알림 링크
    @Column(name = "link_url", nullable = false)
    private String linkUrl; // 클릭 시 이동할 링크
    
    // 발송 타켓
    @Enumerated(EnumType.STRING)
    @Column(name = "target_group", nullable = false)
    private TargetGroup targetGroup; // GLOBAL(유저 전체), PERSONAL(개인) 등
    
    // 알림 유형
    @Enumerated(EnumType.STRING)
    @Column(name = "noti_type", nullable = false)
    private NotiType notiType; // (NOTICE, EVENT 등)
}