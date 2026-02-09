package com.example.cliproute_project.global.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        // 모든 경로(/**)에 대해 CORS 설정을 적용합니다.
        registry.addMapping("/**")
                // 신분증 검사 통과 대상: 모든 도메인 패턴을 허용합니다. (localhost:5174 등 포함)
                .allowedOriginPatterns("*")
                // 허용할 HTTP 메서드들을 지정합니다.
                .allowedMethods("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
                // 모든 헤더 정보를 허용합니다.
                .allowedHeaders("*")
                // 쿠키나 인증 정보를 포함한 요청도 허용합니다.
                .allowCredentials(true)
                // 브라우저가 이 설정값을 기억할 시간(초)을 정합니다. (1시간)
                .maxAge(3600);
    }
}