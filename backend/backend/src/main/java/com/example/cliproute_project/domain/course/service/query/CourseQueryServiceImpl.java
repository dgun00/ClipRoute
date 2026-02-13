package com.example.cliproute_project.domain.course.service.query;

import com.example.cliproute_project.domain.course.converter.CourseConverter;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.exception.CourseException;
import com.example.cliproute_project.domain.course.exception.code.CourseErrorCode;
import com.example.cliproute_project.domain.course.repository.CourseDetailQueryRepository;
import com.example.cliproute_project.domain.course.repository.CourseRepository;
import com.example.cliproute_project.domain.course.repository.projection.CoursePlaceDetailFlat;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.global.apiPayload.exception.GeneralException;
import com.example.cliproute_project.global.common.dto.SliceInfoDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Slice;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

import static com.example.cliproute_project.global.common.converter.SliceConverter.toSliceInfoDTO;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true) // 조회 성능 최적화
public class CourseQueryServiceImpl implements CourseQueryService {

    private static final String YOUTUBE_WATCH_URL_PREFIX = "https://www.youtube.com/watch?v=";

    private final CourseRepository courseRepository;
    private final CourseDetailQueryRepository courseDetailQueryRepository;
    private final MemberCourseRepository memberCourseRepository;
//    private final CourseDetailConverter courseDetailConverter;

    // [2번 API]
    @Override
    public CourseResDTO.CoursePublicListDTO getCourseList(Long regionId, Integer travelDays, String sort, Long seed, Boolean isRep, Long lastCourseId, Integer lastValue, Integer pageSize) {

        // No-Offset 방식이므로 page 번호는 0으로 고정하고 size만큼 가져옴
        Pageable pageable = PageRequest.of(0, pageSize);

        // 리포지토리 호출하여 슬라이스 데이터 조회
        Long resolvedSeed = resolveSeed(sort, seed); // random logic
        Slice<Course> courseSlice = courseRepository.findCoursesByFilter(
                regionId, travelDays, sort, resolvedSeed, isRep, lastCourseId, lastValue, pageable
        );


        // 첫 페이지 진입 시(lastCourseId == null)에만 전체 개수 조회
        Long totalElements = (lastCourseId == null)
                ? courseRepository.countCoursesByFilter(regionId, travelDays, isRep)
                : null;

        // 엔티티 리스트를 DTO 리스트로 변환 (2번 API는 추천 로직이 없으므로 isRecommended 값은 false)
        List<CourseResDTO.CoursePublicDTO> coursePublicDTOs = courseSlice.stream()
                .map(course -> CourseConverter.toCoursePublicDTO(course, false))
                .toList();

        // Slice DTO 변환
        SliceInfoDTO courseSliceDTOs = toSliceInfoDTO(courseSlice);

        // 최종 응답 DTO 조립 및 반환
        return CourseConverter.toCoursePublicListDTO(coursePublicDTOs, courseSliceDTOs, totalElements, sort, resolvedSeed);
    }

    // [3번 API]
    @Override
    public CourseResDTO.CoursePublicListDTO getCourseListWithRecommendation(Long regionId, Integer travelDays, String sort, Long seed, int page, int size) {

        Pageable pageable = PageRequest.of(page, size);

        // 리포지토리 호출
        Long resolvedSeed = resolveSeed(sort, seed); // random logic
        Slice<Course> courseSlice = courseRepository.findCoursesByFilterWithRecommendation(
                regionId, travelDays, sort, resolvedSeed, pageable
        );

        // 정확히 일치하는 데이터 개수 조회 (첫 페이지만)
        Long totalElements = (page == 0)
                ? courseRepository.countCoursesByFilter(regionId, travelDays, null)
                : null;

        // Course DTO 변환 및 추천 여부(isRecommended) 판별
        List<CourseResDTO.CoursePublicDTO> coursePublicDTOs = courseSlice.stream()
                .map(course -> {
                    // 사용자 정의 입력 조건(regionId, travelDays)과
                    // DB에서 가져온 코스의 실제 데이터가 하나라도 다르면 추천(true)으로 표시
                    boolean isRecommended =
                            (regionId != null && !course.getRegion().getId().equals(regionId)) ||
                                    (travelDays != null && !course.getTravelDays().equals(travelDays));

                    return CourseConverter.toCoursePublicDTO(course, isRecommended);
                })
                .toList();
        // Slice DTO 변환
        SliceInfoDTO courseSliceDTOs = toSliceInfoDTO(courseSlice);

        // 4. 최종 응답 조립
        return CourseConverter.toCoursePublicListDTO(coursePublicDTOs, courseSliceDTOs ,totalElements, sort, resolvedSeed);
    }

    // random logic
    private Long resolveSeed(String sort, Long seed) {
        if (!"random".equals(sort)) {
            return null;
        }
        return seed != null ? seed : ThreadLocalRandom.current().nextLong();
    }

    // [4번 API]
    @Override
    public CourseResDTO.CourseDetailDTO getCourseDetail(Long courseId, Long memberId) {

        // * 비로그인 확인용으로 무엇을 리턴할지 (예외? 혹은 다른 resDTO?)

        // 1) 코스 메타 (Course + Video + Region) 엔티티 조회
        Course course = courseRepository.findByIdWithVideoAndRegion(courseId)
                .orElseThrow(() -> new CourseException(CourseErrorCode.COURSE_NOT_FOUND));

        // 스크랩 여부는 original 코스가 기준
        Long originalId = (course.getOriginalCourse() != null)
                ? course.getOriginalCourse().getId()
                : course.getId();

        // 2) itinerary 정보 (Flat Projection) 조회
        List<CoursePlaceDetailFlat> flats = courseDetailQueryRepository.findCoursePlaceDetails(courseId);

        // 3) Flat -> ItineraryDTO 변환 (visitDay 그룹화 정렬/시간 포맷 등)
        List<CourseResDTO.ItineraryDTO> itineraries = CourseConverter.toItineraries(flats);

        // 4) (비로그인 기본값) + (로그인 시 스크랩 상태 가져오기)
        ScrapState scrapState = resolveScrapState(memberId, originalId);

        // 5) 최종 응답 조립
        return new CourseResDTO.CourseDetailDTO(
                course.getId(),
                course.getSourceVideo().getTitle(),
                buildYoutubeUrl(course.getSourceVideo().getYtVideoId()),
                course.getSourceVideo().getThumbnailUrl(),
                course.getSourceVideo().getChannelName(),
                course.getRegion().getId(),
                course.getRegion().getRegionName(),
                scrapState.isScrapped(),
                scrapState.travelStatus(),
                itineraries
        );
    }

    // 스크랩/여행상태 상태 판단
    private ScrapState resolveScrapState(Long memberId, Long originalCourseId) {
        // 비회원이면 스크랩/여행상태 디폴트값
        if (memberId == null) {
            return ScrapState.defaultState();
        }
        // 회원이면 회원 정보에 맞게 스크랩/여행상태 및 반환
        return memberCourseRepository.findActiveScrapByOriginalCourseId(memberId, originalCourseId)
                //.map(mc -> new ScrapState(true, mc.getTravelStatus()))
                .map(this::toScrapState)
                .orElseGet(ScrapState::defaultState);
    }

    private ScrapState toScrapState(MemberCourse mc) {
        // 비즈니스 룰에 따라:
        return new ScrapState(mc.getIsScrapped(), mc.getTravelStatus());
    }

    // 유튜브 url 생성 메서드
    private String buildYoutubeUrl(String ytVideoId) {
        return YOUTUBE_WATCH_URL_PREFIX + ytVideoId;
    }

    // 스크랩/여행상태 record 정의, 비로그인 시 디폴트값 주는 메서드
    private record ScrapState(boolean isScrapped, TravelStatus travelStatus) {
        static ScrapState defaultState() {
            return new ScrapState(false, TravelStatus.NONE);
        }
    }

}

