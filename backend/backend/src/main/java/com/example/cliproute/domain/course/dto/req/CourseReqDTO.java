package com.example.cliproute.domain.course.dto.req;

import lombok.Builder;

import java.time.LocalDate;

public class CourseReqDTO {

    @Builder
    // [5 API]
    public record CourseDateRequestDTO(
            LocalDate startDate,
            LocalDate endDate
    ){}

}
