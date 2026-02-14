package com.example.cliproute_project.domain.member.service.query;

import com.example.cliproute_project.domain.member.converter.MemberConverter;
import com.example.cliproute_project.domain.member.dto.res.MemberResDTO;
import com.example.cliproute_project.domain.member.entity.Member;
import com.example.cliproute_project.domain.member.enums.TravelStatus;
import com.example.cliproute_project.domain.member.exception.MemberException;
import com.example.cliproute_project.domain.member.exception.code.MemberCourseErrorCode;
import com.example.cliproute_project.domain.member.exception.code.MemberErrorCode;
import com.example.cliproute_project.domain.member.repository.member.MemberRepository;
import com.example.cliproute_project.domain.member.repository.membercourse.MemberCourseRepository;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseDetailFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseListFlat;
import com.example.cliproute_project.domain.member.repository.projection.MyCourseRegionOptionFlat;
import com.example.cliproute_project.global.common.converter.SliceConverter;
import com.example.cliproute_project.global.common.dto.SliceInfoDTO;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Slice;
import org.springframework.data.domain.SliceImpl;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class MemberQueryServiceImpl implements MemberQueryService {

    private final MemberCourseRepository memberCourseRepository;
    private final MemberRepository memberRepository;

    @Override
    // [6 API] My course filter options
    public MemberResDTO.FilterOptionsDTO getMyCourseFilterOptions(
            String email,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus
    ) {
        // 이메일로 회원 조회
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new MemberException(MemberErrorCode.MEMBER_NOT_FOUND));
        Long memberId = member.getId();

        if (regionId != null && regionId <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_REGION_ID);
        }
        if (travelDays != null && travelDays <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_TRAVEL_DAYS);
        }

        List<MyCourseRegionOptionFlat> regions = memberCourseRepository.findDistinctRegionsForMyCourseFilters(
                memberId, regionId, travelDays, travelStatus
        );
        List<Integer> travelDaysOptions = memberCourseRepository.findDistinctTravelDaysForMyCourseFilters(
                memberId, regionId, travelDays, travelStatus
        );
        List<TravelStatus> travelStatusOptions = memberCourseRepository.findDistinctTravelStatusesForMyCourseFilters(
                memberId, regionId, travelDays, travelStatus
        );

        return MemberConverter.toFilterOptionsDTO(regions, travelDaysOptions, travelStatusOptions);
    }

    @Override
    // [7 API] My course list
    public MemberResDTO.MyCourseListDTO getMyCourses(
            String email,
            Long regionId,
            Integer travelDays,
            TravelStatus travelStatus,
            Long lastMemberCourseId,
            Integer pageSize
    ) {
        // 이메일로 회원 조회
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new MemberException(MemberErrorCode.MEMBER_NOT_FOUND));
        Long memberId = member.getId();

        if (regionId != null && regionId <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_REGION_ID);
        }
        if (travelDays != null && travelDays <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_TRAVEL_DAYS);
        }
        if (pageSize == null || pageSize <= 0) {
            pageSize = 5;
        }

        List<MyCourseListFlat> flats = memberCourseRepository.findMyCoursesByFilter(
                memberId, regionId, travelDays, travelStatus, lastMemberCourseId, pageSize
        );

        boolean hasNext = false;
        if (flats.size() > pageSize) {
            flats = flats.subList(0, pageSize);
            hasNext = true;
        }

        Slice<MyCourseListFlat> slice = new SliceImpl<>(
                flats,
                PageRequest.of(0, pageSize),
                hasNext
        );

        SliceInfoDTO sliceInfoDTO = SliceConverter.toSliceInfoDTO(slice);
        return MemberConverter.toMyCourseListDTO(flats, sliceInfoDTO, "latest");
    }

    @Override
    // [9 API] My course detail
    public MemberResDTO.MyCourseDetailDTO getMyCourseDetail(String email, Long courseId) {
        // 이메일로 회원 조회
        Member member = memberRepository.findByEmail(email)
                .orElseThrow(() -> new MemberException(MemberErrorCode.MEMBER_NOT_FOUND));
        Long memberId = member.getId();

        if (courseId == null || courseId <= 0) {
            throw new MemberException(MemberCourseErrorCode.INVALID_COURSE_ID);
        }

        boolean exists = memberCourseRepository.existsMyCourseDetailScope(memberId, courseId);
        if (!exists) {
            throw new MemberException(MemberCourseErrorCode.MY_COURSE_ACCESS_DENIED);
        }

        List<MyCourseDetailFlat> flats = memberCourseRepository.findMyCourseDetailFlats(memberId, courseId);
        if (flats == null || flats.isEmpty()) {
            throw new MemberException(MemberCourseErrorCode.MY_COURSE_NOT_FOUND);
        }

        return MemberConverter.toMyCourseDetailDTO(flats);
    }
}