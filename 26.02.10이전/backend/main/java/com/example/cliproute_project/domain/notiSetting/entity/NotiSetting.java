package com.example.cliproute_project.domain.notiSetting.entity;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "NOTI_SETTINGS")
public class NotiSetting extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 멤버 id
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;
    
    // 알림 여부
    @Column(name = "is_push_enabled", nullable = false)
    private Boolean isPushEnabled;
    
    // 마케팅 동의 여부
    @Column(name = "is_marketing_agreed", nullable = false)
    private Boolean isMarketingAgreed;
    
    // 야간 알림 여부
    @Column(name = "is_night_push_enabled", nullable = false)
    private Boolean isNightPushEnabled;
}