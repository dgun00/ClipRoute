package com.example.cliproute.global.common.converter;

import com.example.cliproute.global.common.dto.SliceInfoDTO;
import org.springframework.data.domain.Slice;

public class SliceConverter {
    // Slice 메타데이터 변환
    public static SliceInfoDTO toSliceInfoDTO(Slice<?> slice) {
        return SliceInfoDTO.builder()
                .currentPage(slice.getNumber())
                .size(slice.getSize())
                .hasNext(slice.hasNext())
                .build();
    }
}
