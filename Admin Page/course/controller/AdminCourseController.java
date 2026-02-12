package umc.cliproute.domain.course.controller;

import umc.cliproute.dto.CourseSaveDto; 
import umc.cliproute.service.AdminCourseService; 
import lombok.RequiredArgsConstructor; 
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/admin/courses")
@RequiredArgsConstructor /
public class AdminCourseController {

    private final AdminCourseService adminCourseService; 

    @PostMapping("/bulk")
    public ResponseEntity<String> saveBulkCourses(@RequestBody List<CourseSaveDto> dtos) {
      
        adminCourseService.saveBulkCourses(dtos);
        
        return ResponseEntity.ok("총 " + dtos.size() + "건의 데이터가 엔티티 매핑 및 DB 저장이 완료되었습니다!");
    }
}