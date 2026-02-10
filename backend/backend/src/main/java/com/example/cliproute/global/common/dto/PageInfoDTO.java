package com.example.cliproute.global.common.dto;

import lombok.Builder;

@Builder
public record PageInfoDTO(
        Integer currentPage,
        Integer totalPages,
        Long totalElements,
        Boolean isFirst,
        Boolean isLast
){}