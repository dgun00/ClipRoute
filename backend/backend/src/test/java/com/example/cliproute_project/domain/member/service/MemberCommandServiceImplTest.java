package com.example.cliproute_project.domain.member.service;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.entity.mapping.CoursePlace;
import com.example.cliproute_project.domain.course.repository.CoursePlaceRepository;
import com.example.cliproute_project.domain.member.dto.req.MemberReqDTO;
import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.exception.MemberException;
import com.example.cliproute_project.domain.member.exception.code.MemberCourseErrorCode;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.member.service.command.MemberCommandServiceImpl;
import com.example.cliproute_project.domain.place.entity.Place;
import com.example.cliproute_project.domain.place.repository.PlaceRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.test.util.ReflectionTestUtils;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
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

    @InjectMocks
    private MemberCommandServiceImpl memberCommandService;

    @Test
    void editMyCourseDetail_success_updates_and_returns_detail() {
        Long memberId = 1L;
        Long courseId = 10L;

        Course course = new Course();
        ReflectionTestUtils.setField(course, "id", courseId);
        ReflectionTestUtils.setField(course, "isCustomized", true);
        ReflectionTestUtils.setField(course, "deletedAt", null);
        ReflectionTestUtils.setField(course, "title", "old-title");
        ReflectionTestUtils.setField(course, "travelDays", 1);

        MemberCourse memberCourse = new MemberCourse();
        ReflectionTestUtils.setField(memberCourse, "course", course);
        ReflectionTestUtils.setField(memberCourse, "deletedAt", null);

        CoursePlace existingPlace = new CoursePlace();
        ReflectionTestUtils.setField(existingPlace, "id", 1001L);
        ReflectionTestUtils.setField(existingPlace, "course", course);

        Place newPlace = new Place();
        ReflectionTestUtils.setField(newPlace, "id", 701L);

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

        MemberResDTO.MyCourseDetailDTO result = memberCommandService.editMyCourseDetail(memberId, courseId, request);

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

        Course course = new Course();
        ReflectionTestUtils.setField(course, "id", courseId);
        ReflectionTestUtils.setField(course, "isCustomized", true);

        MemberCourse memberCourse = new MemberCourse();
        ReflectionTestUtils.setField(memberCourse, "course", course);
        ReflectionTestUtils.setField(memberCourse, "deletedAt", null);

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

        assertThatThrownBy(() -> memberCommandService.editMyCourseDetail(memberId, courseId, request))
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

        Course course = new Course();
        ReflectionTestUtils.setField(course, "id", courseId);
        ReflectionTestUtils.setField(course, "isCustomized", true);

        MemberCourse memberCourse = new MemberCourse();
        ReflectionTestUtils.setField(memberCourse, "course", course);
        ReflectionTestUtils.setField(memberCourse, "deletedAt", null);

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

        assertThatThrownBy(() -> memberCommandService.editMyCourseDetail(memberId, courseId, request))
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
