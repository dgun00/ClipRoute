import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useInfiniteQuery } from '@tanstack/react-query';
import VideoCard from './VideoCard';
import { fetchCourses } from '../api/courses';

interface VideoSectionProps {
  destination: { regionId: number; regionName: string } | null;
  travelDays: number | null;
  shouldFilter: boolean;
}

export default function VideoSection({
  destination,
  travelDays,
  shouldFilter,
}: VideoSectionProps) {
  const observerTarget = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  // 필터 모드 여부
  const isFilterMode =
    shouldFilter && (destination !== null || travelDays !== null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    status,
  } = useInfiniteQuery({
    queryKey: ['courses', destination?.regionId, travelDays, isFilterMode],
    queryFn: ({ pageParam = 0 }) =>
      fetchCourses({
        pageParam,
        destination,
        travelDays,
        isFilterMode,
        isRep: true
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => {
      const { hasNext, currentPage } = lastPage.result.sliceInfo;
      return hasNext ? currentPage + 1 : undefined;
    },
  });

  useEffect(() => {
    if (!observerTarget.current || !hasNextPage) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.5 }
    );

    observer.observe(observerTarget.current);
    return () => observer.disconnect();
  }, [hasNextPage, fetchNextPage, isFetchingNextPage]);

  const allCourses =
    data?.pages.flatMap((page) => page.result.courseList) ?? [];

  const handleCourseClick = (courseId: number) => {
    navigate(`/courses/${courseId}`);
  };

  const getSectionTitle = () => {
    if (isFilterMode && destination) {
      return `${destination.regionName} 여행 추천`;
    }
    return '대표 지역 / 인기 영상 속 코스';
  };

  const getSectionDescription = () => {
    if (isFilterMode) {
      const parts: string[] = [];
      if (destination) parts.push(destination.regionName);
      if (travelDays) parts.push(`${travelDays}박 ${travelDays + 1}일`);
      return '조건에 맞는 여행 코스를 찾았어요!';
    }
    return '현재 가장 인기 있는 대표 지역은 제주, 부산입니다.';
  };

  return (
    <div className="mt-12 pt-8 border-t border-gray-100">
      <h2 className="font-bold text-[18px]">{getSectionTitle()}</h2>
      <p className="text-[14px] text-gray-400 mt-1 mb-5">
        {getSectionDescription()}
      </p>

      <div className="grid grid-cols-1 gap-4">
        {allCourses.length > 0 ? (
          allCourses.map((course) => (
            <VideoCard
              key={course.courseId}
              course={course}
              onClick={() => handleCourseClick(course.courseId)}
            />
          ))
        ) : (
          status === 'success' && (
            <p className="text-center text-gray-400 py-10">
              {isFilterMode
                ? '조건에 맞는 코스가 모두 소진되었습니다.'
                : '코스를 불러오는 중입니다...'}
            </p>
          )
        )}
      </div>

      {status === 'error' && (
        <p className="text-center text-red-500 py-10">
          데이터 로드 중 오류가 발생했습니다.
        </p>
      )}

      <div
        ref={observerTarget}
        className="h-24 flex justify-center items-center"
      >
        {isFetchingNextPage ? (
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#42BCEB]" />
        ) : (
          !hasNextPage &&
          allCourses.length > 0 && (
            <p className="text-gray-400 text-[13px]">
              조건에 맞는 코스가 모두 소진되었습니다.
            </p>
          )
        )}
      </div>
    </div>
  );
}