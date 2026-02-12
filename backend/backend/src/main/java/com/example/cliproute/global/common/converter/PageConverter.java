package com.example.cliproute.global.common.converter;

import com.example.cliproute.global.common.dto.PageInfoDTO;
import org.springframework.data.domain.Page;

public class PageConverter {
    // 페이지 메타데이터 DTO
    public static PageInfoDTO toPageInfoDTO(Page<?> page) {
        return PageInfoDTO.builder()
                .currentPage(page.getNumber())
                .totalPages(page.getTotalPages())
                .totalElements(page.getTotalElements())
                .isFirst(page.isFirst())
                .isLast(page.isLast())
                .build();
    }
}
