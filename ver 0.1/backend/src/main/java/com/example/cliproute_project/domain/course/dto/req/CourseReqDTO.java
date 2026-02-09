package com.example.cliproute_project.domain.course.dto.req;

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
