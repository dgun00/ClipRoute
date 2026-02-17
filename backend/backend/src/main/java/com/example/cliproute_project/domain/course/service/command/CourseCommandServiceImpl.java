package com.example.cliproute_project.domain.course.service.command;

import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.entity.mapping.CoursePlace;
import com.example.cliproute_project.domain.course.exception.CourseException;
import com.example.cliproute_project.domain.course.exception.code.CourseErrorCode;
import com.example.cliproute_project.domain.course.repository.CoursePlaceRepository;
import com.example.cliproute_project.domain.course.repository.CourseRepository;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.exception.MemberException;
import com.example.cliproute_project.domain.member.exception.code.MemberErrorCode;
import com.example.cliproute_project.domain.member.repository.member.MemberRepository;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

import static com.example.cliproute_project.domain.course.converter.CourseConverter.toScrapResult;

@Service
@RequiredArgsConstructor
public class CourseCommandServiceImpl implements CourseCommandService {

    private final CourseRepository courseRepository;
    private final CoursePlaceRepository coursePlaceRepository;
    private final MemberRepository memberRepository;
    private final MemberCourseRepository memberCourseRepository;

    @Transactional
    // [5 API]
    public CourseResDTO.ScrapResultDTO scrapCourse(String email, Long courseId, CourseReqDTO.CourseDateRequestDTO travelPeriod) {
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new MemberException(MemberErrorCode.MEMBER_NOT_FOUND));
        Long memberId = member.getId();

        final CourseReqDTO.CourseDateRequestDTO effectiveTravelPeriod = (travelPeriod == null)
                ? new CourseReqDTO.CourseDateRequestDTO(null, null)
                : travelPeriod;

        if (courseId == null || courseId <= 0) {
            throw new CourseException(CourseErrorCode.INVALID_COURSE_ID);
        }

        Course target = courseRepository.findByIdWithVideoAndRegion(courseId)
                .orElseThrow(() -> new CourseException(CourseErrorCode.COURSE_NOT_FOUND));

        Course original = (target.getOriginalCourse() != null) ? target.getOriginalCourse() : target;
        Long originalId = original.getId();

        return memberCourseRepository.findActiveScrapByCourseId(memberId, originalId)
                .map(existing -> {
                    ensureItinerariesCopied(existing.getCourse(), original);
                    return toScrapResult(existing.getCourse().getId(), originalId, existing, effectiveTravelPeriod);
                })
                .orElseGet(() -> createScrap(member, original, effectiveTravelPeriod));
    }

    // [5 API]
    private CourseResDTO.ScrapResultDTO createScrap(Member member, Course original, CourseReqDTO.CourseDateRequestDTO travelPeriod) {
        Course newCourse = Course.createScrappedFrom(original, member);
        courseRepository.save(newCourse);

        copyItineraries(original, newCourse);

        MemberCourse memberCourse = MemberCourse.createScrap(member, newCourse, TravelStatus.BEFORE, travelPeriod);
        memberCourseRepository.save(memberCourse);

        return toScrapResult(newCourse.getId(), original.getId(), memberCourse, travelPeriod);
    }

    private void ensureItinerariesCopied(Course targetCourse, Course original) {
        List<CoursePlace> existingPlaces = coursePlaceRepository.findAllByCourseId(targetCourse.getId());
        if (!existingPlaces.isEmpty()) {
            return;
        }
        copyItineraries(original, targetCourse);
    }

    private void copyItineraries(Course original, Course targetCourse) {
        List<CoursePlace> originalPlaces = coursePlaceRepository.findAllByCourseId(original.getId());
        if (originalPlaces.isEmpty()) {
            return;
        }
        List<CoursePlace> copiedPlaces = originalPlaces.stream()
                .map(cp -> CoursePlace.create(
                        targetCourse,
                        cp.getPlace(),
                        cp.getVisitDay(),
                        cp.getVisitOrder()
                ))
                .toList();
        coursePlaceRepository.saveAll(copiedPlaces);
    }
}
