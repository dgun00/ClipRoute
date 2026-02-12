package com.example.cliproute.domain.member.repository.member;

import com.example.cliproute.domain.member.entity.Member;
import org.springframework.data.jpa.repository.JpaRepository;

public interface MemberRepository extends JpaRepository<Member, Long> {
}
