package com.example.cliproute_project.domain.course.service.command;

import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.exception.CourseException;
import com.example.cliproute_project.domain.course.exception.code.CourseErrorCode;
import com.example.cliproute_project.domain.course.repository.CourseRepository;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.domain.member.repository.member.MemberRepository;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import com.example.cliproute_project.global.apiPayload.code.GeneralErrorCode;
import com.example.cliproute_project.global.apiPayload.exception.GeneralException;
import lombok.RequiredArgsConstructor;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import static com.example.cliproute_project.domain.course.converter.CourseConverter.toScrapResult;

@Service
@RequiredArgsConstructor
public class CourseCommandServiceImpl implements CourseCommandService{

    private final CourseRepository courseRepository;
    private final MemberRepository memberRepository;
    private final MemberCourseRepository memberCourseRepository;

    @Transactional
    public CourseResDTO.ScrapResultDTO scrapCourse(Long memberId, Long courseId) {
        // auth 도메인에서 예외코드 생성해야함.
        if (memberId == null){
            throw new GeneralException(GeneralErrorCode.UNAUTHORIZED);
        }
        if (courseId == null || courseId <= 0) {
            throw new CourseException(CourseErrorCode.INVALID_COURSE_ID);
        }

        // 1) 대상 코스 로딩 (repo에 있는 fetchJoin 메서드 재사용)
        Course target = courseRepository.findByIdWithVideoAndRegion(courseId)
                .orElseThrow(() -> new CourseException(CourseErrorCode.COURSE_NOT_FOUND));

        // 2) original normalize (커스텀 코스 들어와도 원본 기준으로 멱등 처리)
        // originalCourse가 null이면 이 코스가 원본코스
        Course original = (target.getOriginalCourse() != null) ? target.getOriginalCourse() : target;
        Long originalId = original.getId();

        // 3) 멱등성: 이미 스크랩된게 있으면 그대로 반환
        //    (네 MemberCourseRepositoryImpl이 c.originalCourse.id.eq(courseId) 기준이라
        //     여기서 반드시 originalId로 호출해야 함)
        return memberCourseRepository.findActiveScrapByCourseId(memberId, originalId)
                .map(existing -> toScrapResult(existing.getCourse().getId(), originalId, existing))
                .orElseGet(() -> createScrap(memberId, original));
    }


    private CourseResDTO.ScrapResultDTO createScrap(Long memberId, Course original) {

        // Member 엔티티를 "프록시 참조" 형태로 가져온다. "연관관계(FK)"만 맺으면 되기 때문에 getReferenceById 사용
        Member memberRef = memberRepository.getReferenceById(memberId);

        // 새 Course 생성 (원본 복제 + originalCourse 세팅)
        Course newCourse = Course.createScrappedFrom(original, memberRef);
        courseRepository.save(newCourse);

        // MemberCourse 생성
        MemberCourse memberCourse = MemberCourse.createScrap(memberRef, newCourse, TravelStatus.PENDING);
        memberCourseRepository.save(memberCourse);

        return toScrapResult(newCourse.getId(), original.getId(), memberCourse);
    }


}
