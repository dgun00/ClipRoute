package com.example.cliproute_project.domain.course.service.command;

import com.example.cliproute_project.domain.course.dto.req.CourseReqDTO;
import com.example.cliproute_project.domain.course.entity.Course;
import com.example.cliproute_project.domain.course.exception.CourseException;
import com.example.cliproute_project.domain.course.exception.code.CourseErrorCode;
import com.example.cliproute_project.domain.course.repository.CourseRepository;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.member.entity.mapping.MemberCourse;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.exception.MemberException;
import com.example.cliproute_project.domain.member.exception.code.MemberErrorCode;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.domain.member.repository.member.MemberRepository;
import com.example.cliproute_project.domain.course.dto.res.CourseResDTO;
import lombok.RequiredArgsConstructor;
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
    // [5 API]
    public CourseResDTO.ScrapResultDTO scrapCourse(Long memberId, Long courseId, CourseReqDTO.CourseDateRequestDTO travelPeriod) {

//        // 만약 travelPeriod가 null이면 기본 객체 생성해서 사용
//        if (travelPeriod == null) {
//            CourseReqDTO.CourseDateRequestDTO TravelPeriod = new CourseReqDTO.CourseDateRequestDTO(
//                    null,null
//            );
//        }

        final CourseReqDTO.CourseDateRequestDTO effectiveTravelPeriod = (travelPeriod == null)
                ? new CourseReqDTO.CourseDateRequestDTO(null, null)
                : travelPeriod;

        // auth 미인증 예외 처리
        if (memberId == null){
            throw new MemberException(MemberErrorCode.UNAUTHORIZED);
        }
        if (courseId == null || courseId <= 0) {
            throw new CourseException(CourseErrorCode.INVALID_COURSE_ID);
        }

        // 1) 대상 코스 로딩 (repo에서는 fetchJoin 메서드 사용)
        Course target = courseRepository.findByIdWithVideoAndRegion(courseId)
                .orElseThrow(() -> new CourseException(CourseErrorCode.COURSE_NOT_FOUND));

        // 2) original normalize (커스텀 코스가 들어와도 원본 기준으로 멱등 처리)
        // originalCourse가 null이면 해당 코스가 원본 코스
        Course original = (target.getOriginalCourse() != null) ? target.getOriginalCourse() : target;
        Long originalId = original.getId();

        // 3) 멱등 처리: 이미 스크랩된 코스가 있으면 그대로 반환
        //    (MemberCourseRepositoryImpl의 c.originalCourse.id.eq(courseId) 기준이라
        //     여기서 반드시 originalId를 넘겨야 함)
        return memberCourseRepository.findActiveScrapByCourseId(memberId, originalId)
                .map(existing -> toScrapResult(existing.getCourse().getId(), originalId, existing,effectiveTravelPeriod))
                .orElseGet(() -> createScrap(memberId, original, effectiveTravelPeriod));
    }


    // [5 API]
    private CourseResDTO.ScrapResultDTO createScrap(Long memberId, Course original,CourseReqDTO.CourseDateRequestDTO travelPeriod) {

        // Member 존재 확인 (없으면 예외로 변환)
        Member memberRef = memberRepository.findById(memberId)
                .orElseThrow(() -> new MemberException(MemberErrorCode.INVALID_MEMBER_ID));

        // Course 생성 (원본 복제 + originalCourse 설정)
        Course newCourse = Course.createScrappedFrom(original, memberRef);
        courseRepository.save(newCourse);

        // MemberCourse 생성
        MemberCourse memberCourse = MemberCourse.createScrap(memberRef, newCourse, TravelStatus.BEFORE, travelPeriod);
        memberCourseRepository.save(memberCourse);

        return toScrapResult(newCourse.getId(), original.getId(), memberCourse, travelPeriod );
    }


}
