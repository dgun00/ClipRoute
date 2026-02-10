package com.example.cliproute.domain.place.enums;

import java.util.Arrays;
import java.util.Optional;

public enum PlaceCategory {
    맛집,
    카페,
    숙소,
    관광지,
    기타;

    // null/공백이면 empty반환, 앞뒤공백 무시 enum 매칭,
    public static Optional<PlaceCategory> from(String value) {
        if (value == null || value.isBlank()) {
            return Optional.empty();
        }
        String trimmed = value.trim();
        return Arrays.stream(values())
                .filter(v -> v.name().equals(trimmed))
                .findFirst();
    }
}
