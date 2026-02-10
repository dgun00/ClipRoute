package com.example.cliproute.global.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(AbstractHttpConfigurer::disable)
                .cors(cors -> cors.configurationSource(request -> {
                    var corsConfiguration = new org.springframework.web.cors.CorsConfiguration();

                    corsConfiguration.setAllowedOriginPatterns(java.util.List.of(
                            "http://localhost:517*",
                            "http://localhost:3000"
                    ));

                    corsConfiguration.setAllowedMethods(java.util.List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
                    corsConfiguration.setAllowedHeaders(java.util.List.of("*"));
                    corsConfiguration.setAllowCredentials(true);
                    return corsConfiguration;
                }))
                .formLogin(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .authorizeHttpRequests(auth -> auth
                        // 누구나 접근 가능한 경로 (로그인 없이 가능)
                        .requestMatchers("/api/auth/**").permitAll()
                        .requestMatchers("/api/v1/regions/**").permitAll()
                        .requestMatchers("/api/v1/courses").permitAll()
                        .requestMatchers("/api/v1/courses/recommendation").permitAll()
                        .requestMatchers("/api/v1/courses/{courseId}").permitAll()
                        .requestMatchers("/api/v1/courses/{courseId}/scrap").permitAll()

                        // Swagger 문서 등 개발 편의를 위한 허용 (필요시)
                        .requestMatchers("/v3/api-docs/**", "/swagger-ui/**").permitAll()

                        // 인증이 필요한 경로 (마이페이지, 내 코스 관련 등)
                        // "me"가 포함된 경로나 특정 검색 서비스는 로그인이 필요함
                        .requestMatchers("/api/v1/members/me/**").authenticated()
                        .requestMatchers("/api/v1/places/search").authenticated()

                        // 그 외 모든 요청은 일단 인증 필요
                        .anyRequest().authenticated()
                );

        return http.build();
    }
}