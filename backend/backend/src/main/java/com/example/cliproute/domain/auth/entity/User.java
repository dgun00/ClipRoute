package com.example.cliproute.domain.auth.entity;
import com.example.cliproute.domain.auth.enums.AgeRange;
import com.example.cliproute.domain.auth.enums.Gender;
import com.example.cliproute.domain.auth.enums.MemberStatus;
import com.example.cliproute.domain.auth.enums.Role;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import java.time.LocalDateTime;

@Entity
@Table(name = "members")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
@AllArgsConstructor
@Builder
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true, length = 50)
    private String email;

    @Column(nullable = false, length = 255)
    private String password;

    @Column(nullable = false, unique = true, length = 20)
    private String nickname;

    @Enumerated(EnumType.STRING)
    @Column(name = "age_range", nullable = false)
    private AgeRange ageRange;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Gender gender;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private MemberStatus status;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    public void updateProfile(String nickname, String email, Gender gender, AgeRange ageRange) {
        if (nickname != null) this.nickname = nickname;
        if (email != null) this.email = email;
        if (gender != null) this.gender = gender;
        if (ageRange != null) this.ageRange = ageRange;
    }

    public void updatePassword(String password) {
        this.password = password;
    }
    public void updateStatus(MemberStatus status) {
        this.status = status;
        // 만약 상태가 DELETED로 변경되면 탈퇴 시간을 현재로 기록
        if (status == MemberStatus.DELETED) {
            this.deletedAt = LocalDateTime.now();
        }
    }
}