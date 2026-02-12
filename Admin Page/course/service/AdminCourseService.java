package umc.cliproute.domain.course.service;

@Service
@Transactional
@RequiredArgsConstructor
public class AdminCourseService {

    private final CourseRepository courseRepository;
    private final RegionRepository regionRepository; // 지역 확인용
    private final VideoRepository videoRepository;   // 영상 저장용
    private final MemberRepository memberRepository; // 관리자 확인용

    public void saveBulkCourses(List<CourseSaveDto> dtos) {
        // 1. 관리자 정보 가져오기 (작성자 매핑을 위해 필요)
        // 실제로는 로그인된 관리자 ID를 써야 하지만, 테스트용으로 1번 멤버를 관리자로 가정
        Member admin = memberRepository.findById(1L).orElseThrow();

        for (CourseSaveDto dto : dtos) {
            // 2. 지역 매핑 (CSV의 "제주" 등을 Region 엔티티에서 찾음)
            Region region = regionRepository.findByName(dto.getRegion()).orElseThrow();

            // 3. 영상 엔티티 먼저 생성 및 저장
            Video video = Video.createVideo(dto.getVideoUrl(), dto.getYoutubeVideoId());
            videoRepository.save(video);

            Integer days = parseTravelDays(dto.getDuration()); 
            
            Course course = Course.createAdminCourse(
                dto.getTitle(), 
                days, 
                region, 
                video, 
                admin
            );

            courseRepository.save(course);
        }
    }

    private Integer parseTravelDays(String duration) {
        if (duration.contains("당일")) return 1;
        if (duration.contains("1박")) return 2;
        return 1; // 기본값
    }
}