package com.example.cliproute.global.common.dto;

import lombok.Builder;

@Builder
public record SliceInfoDTO(
        Integer currentPage,
        Integer size,
        Boolean hasNext // 다음 페이지 존재 여부 (무한 스크롤 핵심)
) {}