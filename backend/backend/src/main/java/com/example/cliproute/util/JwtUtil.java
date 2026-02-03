package com.example.cliproute.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Component;
import java.security.Key;
import java.util.Base64;
import java.util.Date;

@Component
public class JwtUtil {
    @org.springframework.beans.factory.annotation.Value("${jwt.secret}")
    private String secretKey;

    private Key key;
    private final long TOKEN_TIME = 60 * 60 * 1000L; // 1시간

    @PostConstruct
    public void init() {
        byte[] bytes = Base64.getDecoder().decode(Base64.getEncoder().encodeToString(secretKey.getBytes()));
        key = Keys.hmacShaKeyFor(bytes);
    }

    // 토큰 생성
    public String createToken(String email) {
        Date date = new Date();

        return Jwts.builder()
                .setSubject(email)
                .setExpiration(new Date(date.getTime() + TOKEN_TIME))
                .setIssuedAt(date)
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    // 1. 토큰 유효성 검증
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token);
            return true;
        } catch (SecurityException | MalformedJwtException e) {
            System.out.println("Invalid JWT signature, 유효하지 않는 JWT 서명 입니다.");
        } catch (ExpiredJwtException e) {
            System.out.println("Expired JWT token, 만료된 JWT token 입니다.");
        } catch (UnsupportedJwtException e) {
            System.out.println("Unsupported JWT token, 지원되지 않는 JWT 토큰 입니다.");
        } catch (IllegalArgumentException e) {
            System.out.println("JWT claims is empty, 잘못된 JWT 토큰 입니다.");
        }
        return false;
    }

    // 2. 토큰에서 사용자 정보(Email) 가져오기
    public String getUserInfoFromToken(String token) {
        return Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token).getBody().getSubject();
    }
}