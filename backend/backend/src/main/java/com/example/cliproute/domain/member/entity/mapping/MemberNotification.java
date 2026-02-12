package com.example.cliproute.domain.member.entity.mapping;

import com.example.cliproute.domain.member.entity.Member;
import com.example.cliproute.domain.notification.entity.Notification;
import com.example.cliproute.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "MEMBER_NOTIFICATION")
public class MemberNotification extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 멤버 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    // 알림 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "notification_id", nullable = false)
    private Notification notification;

    // 읽음 여부
    @Column(name = "is_read", nullable = false)
    private boolean isRead = false;

    // 읽은 시간
    @Column(name = "read_at")
    private LocalDateTime readAt;

    // 보낸 시간
    @Column(name = "sent_at") // 일단 null 가능
    private LocalDateTime sentAt;

    // 삭제 시간
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt; // 유저가 알림 삭제 시 Soft Delete

}