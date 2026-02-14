package com.example.cliproute_project.domain.member.service;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.entity.mapping.CoursePlace;
import com.example.cliproute_project.domain.course.repository.CoursePlaceRepository;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.exception.MemberException;
import com.example.cliproute_project.domain.member.exception.code.MemberCourseErrorCode;
import com.example.cliproute_project.domain.member.repository.member.MemberRepository;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.member.service.command.MemberCommandServiceImpl;
import com.example.cliproute_project.domain.place.entity.Place;
import com.example.cliproute_project.domain.place.repository.PlaceRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.lang.reflect.Constructor;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class MemberCommandServiceImplTest {

    @Mock
    private MemberCourseRepository memberCourseRepository;

    @Mock
    private CoursePlaceRepository coursePlaceRepository;

    @Mock
    private PlaceRepository placeRepository;

    @Mock
    private MemberRepository memberRepository; // 추가된 부분

    @InjectMocks
    private MemberCommandServiceImpl memberCommandService; // 이름 확인

    private <T> T createInstance(Class<T> clazz) {
        try {
            Constructor<T> constructor = clazz.getDeclaredConstructor();
            constructor.setAccessible(true);
            return constructor.newInstance();
        } catch (Exception e) {
            throw new RuntimeException("테스트 객체 생성 실패: " + clazz.getName(), e);
        }
    }

    private Member testMember;
    private final String testEmail = "test@example.com";

    @BeforeEach
    void setUp() {
        testMember = createInstance(Member.class);
        ReflectionTestUtils.setField(testMember, "id", 1L);
        ReflectionTestUtils.setField(testMember, "email", testEmail);
    }

    @Test
    void editMyCourseDetail_success_updates_and_returns_detail() {
        Long memberId = 1L;
        Long courseId = 10L;

        Course course = createInstance(Course.class);
        ReflectionTestUtils.setField(course, "id", courseId);
        ReflectionTestUtils.setField(course, "isCustomized", true);
        ReflectionTestUtils.setField(course, "deletedAt", null);
        ReflectionTestUtils.setField(course, "title", "old-title");
        ReflectionTestUtils.setField(course, "travelDays", 1);

        MemberCourse memberCourse = createInstance(MemberCourse.class);
        ReflectionTestUtils.setField(memberCourse, "course", course);
        ReflectionTestUtils.setField(memberCourse, "deletedAt", null);

        CoursePlace existingPlace = createInstance(CoursePlace.class);
        ReflectionTestUtils.setField(existingPlace, "id", 1001L);
        ReflectionTestUtils.setField(existingPlace, "course", course);

        Place newPlace = createInstance(Place.class);
        ReflectionTestUtils.setField(newPlace, "id", 701L);

        // Mock 설정 변경: 이메일로 멤버 찾기 추가
        when(memberRepository.findByEmail(testEmail)).thenReturn(Optional.of(testMember));
        when(memberCourseRepository.existsMyCourseDetailScope(memberId, courseId)).thenReturn(true);
        when(memberCourseRepository.findByMemberIdAndCourseIdAndDeletedAtIsNull(memberId, courseId))
                .thenReturn(Optional.of(memberCourse));
        when(coursePlaceRepository.findAllByCourseId(courseId)).thenReturn(List.of(existingPlace));
        when(placeRepository.findAllByIdInAndDeletedAtIsNull(any())).thenReturn(List.of(newPlace));
        when(memberCourseRepository.findMyCourseDetailFlats(memberId, courseId))
                .thenReturn(List.of(sampleFlat(courseId)));

        MemberReqDTO.MyCourseDetailEditDTO request = new MemberReqDTO.MyCourseDetailEditDTO(
                "new-title",
                LocalDate.of(2026, 1, 26),
                LocalDate.of(2026, 1, 27),
                TravelStatus.AFTER,
                List.of(
                        new MemberReqDTO.MyCourseItineraryEditDTO(
                                1,
                                List.of(
                                        new MemberReqDTO.MyCourseItemEditDTO(1001L, null),
                                        new MemberReqDTO.MyCourseItemEditDTO(null, 701L)
                                )
                        )
                )
        );

        // 이메일 파라미터로 호출
        MemberResDTO.MyCourseDetailDTO result = memberCommandService.editMyCourseDetail(testEmail, courseId, request);

        assertThat(result).isNotNull();
        assertThat(result.courseId()).isEqualTo(courseId);
        assertThat(course.getTitle()).isEqualTo("new-title");
        assertThat(course.getTravelDays()).isEqualTo(2);

        verify(coursePlaceRepository).saveAll(any());
        verify(memberCourseRepository).findMyCourseDetailFlats(memberId, courseId);
    }

    @Test
    void editMyCourseDetail_invalid_date_range_throws() {
        Long memberId = 1L;
        Long courseId = 10L;

        Course course = createInstance(Course.class);
        ReflectionTestUtils.setField(course, "id", courseId);
        ReflectionTestUtils.setField(course, "isCustomized", true);

        MemberCourse memberCourse = createInstance(MemberCourse.class);
        ReflectionTestUtils.setField(memberCourse, "course", course);
        ReflectionTestUtils.setField(memberCourse, "deletedAt", null);

        // 추가
        when(memberRepository.findByEmail(testEmail)).thenReturn(Optional.of(testMember));
        when(memberCourseRepository.existsMyCourseDetailScope(memberId, courseId)).thenReturn(true);
        when(memberCourseRepository.findByMemberIdAndCourseIdAndDeletedAtIsNull(memberId, courseId))
                .thenReturn(Optional.of(memberCourse));

        MemberReqDTO.MyCourseDetailEditDTO request = new MemberReqDTO.MyCourseDetailEditDTO(
                null,
                LocalDate.of(2026, 1, 26),
                null,
                null,
                null
        );

        // 이메일로 호출
        assertThatThrownBy(() -> memberCommandService.editMyCourseDetail(testEmail, courseId, request))
                .isInstanceOf(MemberException.class)
                .satisfies(ex -> {
                    MemberException me = (MemberException) ex;
                    assertThat(me.getCode()).isEqualTo(MemberCourseErrorCode.INVALID_DATE_RANGE);
                });
    }

    @Test
    void editMyCourseDetail_invalid_visit_day_sequence_throws() {
        Long memberId = 1L;
        Long courseId = 10L;

        Course course = createInstance(Course.class);
        ReflectionTestUtils.setField(course, "id", courseId);
        ReflectionTestUtils.setField(course, "isCustomized", true);

        MemberCourse memberCourse = createInstance(MemberCourse.class);
        ReflectionTestUtils.setField(memberCourse, "course", course);
        ReflectionTestUtils.setField(memberCourse, "deletedAt", null);

        // 추가
        when(memberRepository.findByEmail(testEmail)).thenReturn(Optional.of(testMember));
        when(memberCourseRepository.existsMyCourseDetailScope(memberId, courseId)).thenReturn(true);
        when(memberCourseRepository.findByMemberIdAndCourseIdAndDeletedAtIsNull(memberId, courseId))
                .thenReturn(Optional.of(memberCourse));

        MemberReqDTO.MyCourseDetailEditDTO request = new MemberReqDTO.MyCourseDetailEditDTO(
                null,
                null,
                null,
                null,
                List.of(
                        new MemberReqDTO.MyCourseItineraryEditDTO(
                                2,
                                List.of(new MemberReqDTO.MyCourseItemEditDTO(1001L, null))
                        )
                )
        );

        // 이메일로 호출
        assertThatThrownBy(() -> memberCommandService.editMyCourseDetail(testEmail, courseId, request))
                .isInstanceOf(MemberException.class)
                .satisfies(ex -> {
                    MemberException me = (MemberException) ex;
                    assertThat(me.getCode()).isEqualTo(MemberCourseErrorCode.INVALID_VISIT_DAY_SEQUENCE);
                });
    }

    private MyCourseDetailFlat sampleFlat(Long courseId) {
        return new MyCourseDetailFlat(
                courseId,
                "video-title",
                "yt-id",
                "thumb",
                "channel",
                1L,
                "region",
                true,
                TravelStatus.AFTER,
                "new-title",
                LocalDate.of(2026, 1, 26),
                LocalDate.of(2026, 1, 27),
                1,
                1,
                1001L,
                701L,
                "place",
                "category",
                "address",
                37.0,
                127.0,
                100,
                LocalDateTime.now()
        );
    }
}