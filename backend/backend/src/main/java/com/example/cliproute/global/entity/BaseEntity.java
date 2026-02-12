package com.example.cliproute.global.entity;

import jakarta.persistence.Column;
import jakarta.persistence.EntityListeners;
import jakarta.persistence.MappedSuperclass;
import lombok.Getter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;

@Getter
@MappedSuperclass // 상속받는 엔티티들이 이 클래스의 필드(created_at 등)를 컬럼으로 인식하도록 함
@EntityListeners(AuditingEntityListener.class) // 시간에 대한 값을 자동으로 넣어주는 리스너 적용
public abstract class BaseEntity {

    @CreatedDate
    @Column(name = "created_at", updatable = false) // 생성 시간은 수정되지 않도록 막음
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;


}