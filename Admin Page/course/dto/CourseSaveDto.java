package umc.cliproute.domain.course.dto;

import lombok.Data;
import java.util.List;

@Data
public class CourseSaveDto {
    // 1. 코스 정보
    private String title;
    private String duration;
    private String region;

    // 2. 영상 정보
    private String videoUrl;
    private String youtubeVideoId; 
    private Long viewCount;

    // 3. 장소 리스트
    private List<PlaceDto> places;

    @Data
    public static class PlaceDto {
        private String name;
        private String address;
        private String category;
        private Integer sequence; 
    }
}