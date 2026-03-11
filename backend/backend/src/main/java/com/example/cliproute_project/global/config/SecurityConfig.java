package com.example.cliproute_project.global.config;

import com.example.cliproute_project.domain.auth.util.JwtAuthenticationFilter;
import com.example.cliproute_project.domain.auth.util.JwtUtil;
import lombok.RequiredArgsConstructor;
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
@RequiredArgsConstructor // 1. jwtUtil 주입을 위해 추가 필수!
public class SecurityConfig {

    private final JwtUtil jwtUtil; // 2. final이므로 생성자 주입이 필요함

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
                            "http://localhost:3000",
                            "https://cliproute.vercel.app",
                            "https://frontend-five-theta-26.vercel.app"
                    ));
                    corsConfiguration.setAllowedMethods(java.util.List.of("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"));
                    corsConfiguration.setAllowedHeaders(java.util.List.of("*"));
                    corsConfiguration.setExposedHeaders(java.util.List.of("Authorization"));
                    corsConfiguration.setAllowCredentials(true);
                    return corsConfiguration;
                }))
                .formLogin(AbstractHttpConfigurer::disable)
                .httpBasic(AbstractHttpConfigurer::disable)
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/**").permitAll()
                        .requestMatchers("/api/v1/regions/**").permitAll()
                        .requestMatchers("/api/v1/courses/**").permitAll()
                        .requestMatchers("/v3/api-docs/**", "/swagger-ui/**").permitAll()
                        .requestMatchers("/api/v1/members/**").authenticated()
                        .requestMatchers("/api/v1/places/search").authenticated()
                        .anyRequest().authenticated()
                )

                // JWT 검사를 먼저 하도록 설정
                .addFilterBefore(new JwtAuthenticationFilter(jwtUtil),
                        org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }
}