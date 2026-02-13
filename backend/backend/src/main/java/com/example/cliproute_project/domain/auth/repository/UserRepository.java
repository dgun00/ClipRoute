package com.example.cliproute_project.domain.auth.repository;

import com.example.cliproute_project.domain.auth.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    Optional<User> findByEmail(String email);
}