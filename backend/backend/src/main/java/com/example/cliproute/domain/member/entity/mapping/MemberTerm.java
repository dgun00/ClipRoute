package com.example.cliproute.domain.member.entity.mapping;

import com.example.cliproute.domain.member.entity.Member;
import com.example.cliproute.domain.term.entity.Term;
import com.example.cliproute.global.entity.BaseEntity;
import jakarta.persistence.*;
import lombok.AccessLevel;

import lombok.Getter;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@Table(name = "MEMBER_TERM")
public class MemberTerm extends BaseEntity {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // 멤버 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "member_id", nullable = false)
    private Member member;

    // 약관 id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "term_id", nullable = false)
    private Term term;
    
    // 동의 여부
    @Column(name = "is_agreed", nullable = false)
    private boolean isAgreed;
    
    // 동의 시점
    @Column(name = "agreed_at")
    private LocalDateTime agreedAt;


}