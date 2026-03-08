import { useRef, useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useInfiniteQuery } from "@tanstack/react-query";
import NavigationLayout from "../layouts/NavigationLayout";
import Header from "../components/common/Header";
import backicon from "../assets/icons/back-icon.svg";
import mappinicon from "../assets/icons/mappin-icon.svg";
import calendaricon from "../assets/icons/calendar-icon.svg";
import VideoCard from "../components/VideoCard";
import { fetchRecommendedCourses } from "../api/courses";
import LoadingPage from "./LoadingPage";

const CourseListPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const startDateStr = searchParams.get("startDate");
  const endDateStr = searchParams.get("endDate");
  const regionIdParam = searchParams.get("regionId");
  const travelDaysParam = searchParams.get("travelDays");

  const regionId = regionIdParam ? Number(regionIdParam) : null;
  const travelDays = travelDaysParam !== null ? Number(travelDaysParam) : null;

  // 무한 스크롤 관찰용 ref
  const observerRef = useRef<HTMLDivElement | null>(null);

  const {
    data,
    isLoading,
    isError,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ["courseList", regionId, travelDays],
    queryFn: ({ pageParam }) =>
      fetchRecommendedCourses({
        pageParam,
        regionId: regionId!,
        travelDays: travelDays !== null ? travelDays + 1 : null,
      }),
    initialPageParam: 0,
    getNextPageParam: (lastPage) => {
      if (!lastPage || !lastPage.result) return undefined;
      const { sliceInfo } = lastPage.result;
      return sliceInfo.hasNext ? sliceInfo.currentPage + 1 : undefined;
    },
    enabled: regionId !== null,
  });

  // IntersectionObserver로 스크롤 감지
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 1.0 }
    );

    if (observerRef.current) observer.observe(observerRef.current);

    return () => {
      if (observerRef.current) observer.unobserve(observerRef.current);
    };
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  if (regionId === null) {
    return (
      <div className="p-10 text-center text-gray-500 font-medium">
        잘못된 접근입니다. 여행지를 선택해주세요.
      </div>
    );
  }

  // 최소 로딩 시간 관리
  const [isMinTimeElapsed, setIsMinTimeElapsed] = useState(false);

  useEffect(() => {
    // 2.5초 후에 최소 로딩 시간이 지난 것으로 설정
    const timer = setTimeout(() => {
      setIsMinTimeElapsed(true);
    }, 2700);

    return () => clearTimeout(timer);
  }, []);

  // API 로딩 중이거나 최소 시간이 지나지 않았으면 로딩 페이지 표시
  if (isLoading || !isMinTimeElapsed) return <LoadingPage />;

  if (isError)
    return (
      <div className="p-10 text-center text-red-500 font-medium whitespace-pre-line">
        코스를 추천하는 중 오류가 발생했습니다.{"\n"}
        잠시 후 다시 시도해주세요.
      </div>
    );

  // 모든 페이지의 데이터를 하나로 합침 (Safety Check 추가)
  const courseList = data?.pages.flatMap((page) => page?.result?.courseList || []) || [];

  // 맞춤 코스와 추천 코스 분리 (isRecommended: false -> 맞춤, true -> 추천)
  const customizedCourses = courseList.filter(course => !course.isRecommended);
  const recommendedCourses = courseList.filter(course => course.isRecommended);

  // 지역 이름
  const displayRegionName =
    courseList.length > 0
      ? courseList[0].regionName
      : regionId
        ? `${regionId}번 지역`
        : "전체 지역";

  // 헤더용 일정 문구
  const headerDaysText =
    travelDays === 0
      ? "당일치기"
      : travelDays === null
        ? ""
        : `${travelDays}박 ${travelDays + 1}일`;

  const headerTitle = `${displayRegionName} ${headerDaysText} 여행 코스`.trim();

  // 날짜 포맷 함수
  function formatDate(dateStr: string | null) {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(
      2,
      "0"
    )}.${String(d.getDate()).padStart(2, "0")}`;
  }

  // 입력 카드용 날짜 문구
  const getFormattedDateRange = () => {
    if (travelDays === null) return "날짜 미지정 (전체 일정)";
    if (travelDays === 0) return "당일치기 여행";

    if (startDateStr && endDateStr) {
      const start = formatDate(startDateStr);
      const end = formatDate(endDateStr).slice(5);
      return `${start} - ${end} [${travelDays}박 ${travelDays + 1
        }일]`;
    }

    return `${travelDays}박 ${travelDays + 1}일`;
  };

  const handleScrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <NavigationLayout activeTab="home">
      <div className="bg-white min-h-screen">
        <Header
          left={
            <div className="flex items-center gap-3">
              <button onClick={() => navigate(-1)}>
                <img src={backicon} alt="back" className="w-4 h-4" />
              </button>
              <h1 className="font-bold text-base">{headerTitle}</h1>
            </div>
          }
        />

        <main className="px-5 pt-6 pb-24">
          {/* 입력 정보 카드 */}
          <div className="border border-[#42BCEB] rounded-2xl py-1 px-[15px] bg-white mb-8">
            <div className="flex items-center gap-3 py-4 border-b border-gray-100">
              <img src={mappinicon} alt="location" className="w-6 h-6" />
              <span className="text-sm text-gray-900 font-medium">
                {displayRegionName}
              </span>
            </div>
            <div className="flex items-center gap-3 py-4">
              <img src={calendaricon} alt="calendar" className="w-6 h-6" />
              <span className="text-sm text-gray-900 font-medium">
                {getFormattedDateRange()}
              </span>
            </div>
          </div>

          {/* 1. 조건에 맞는 맞춤 코스 섹션 */}
          {customizedCourses.length > 0 && (
            <div className="mb-10 animate-fade-in">
              <div className="mb-4">
                <h2 className="font-bold text-lg mb-1 text-[#333]">
                  {displayRegionName} 여행 추천
                </h2>
                <p className="text-sm text-gray-400">
                  조건에 맞는 여행 코스를 추천했어요!
                </p>
              </div>
              <div className="space-y-4">
                {customizedCourses.map((course) => (
                  <VideoCard
                    key={`custom-${course.courseId}`}
                    course={course}
                    onClick={() => navigate(`/courses/${course.courseId}?${searchParams.toString()}`)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 2. 비슷한 여행 코스 추천 섹션 (무한 스크롤) */}
          {(recommendedCourses.length > 0 || customizedCourses.length === 0) && (
            <div className={`mb-2 animate-fade-in ${customizedCourses.length > 0 ? "pt-4 border-t border-gray-100" : ""}`}>
              {/* 추천 섹션 헤더 (조건에 맞는 게 있으면 구분 목적) */}
              {(customizedCourses.length > 0 || recommendedCourses.length > 0) && (
                <div className="mb-4">
                  <h2 className="font-bold text-lg mb-1 text-[#333]">
                    비슷한 여행 코스 추천
                  </h2>
                  <p className="text-xs text-gray-400">
                    조건에 맞는 여행 코스가 소진되어 비슷한 여행 코스를 추천해드려요!
                  </p>
                </div>
              )}

              <div className="space-y-4">
                {recommendedCourses.map((course) => (
                  <VideoCard
                    key={`rec-${course.courseId}`}
                    course={course}
                    onClick={() => navigate(`/courses/${course.courseId}?${searchParams.toString()}`)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* 코스가 아예 없을 경우 */}
          {customizedCourses.length === 0 && recommendedCourses.length === 0 && !isLoading && !isFetchingNextPage && (
            <div className="text-center text-gray-500 py-20 bg-gray-50 rounded-xl mt-4">
              <p className="mb-2">조건에 맞는 여행 코스가 없습니다.</p>
              <p className="text-sm">다른 지역이나 날짜로 검색해보세요.</p>
            </div>
          )}

          {/* 무한 스크롤 감지용 태그 및 로딩바 */}
          <div ref={observerRef} className="h-10 mt-4 flex justify-center items-center">
            {isFetchingNextPage && <span className="text-gray-400 text-sm">더 불러오는 중...</span>}
          </div>

          {/* 더 이상 불러올 데이터가 없을 때 완료 메시지 */}
          {!hasNextPage && (customizedCourses.length > 0 || recommendedCourses.length > 0) && (
            <div className="text-center mt-6 pt-8 pb-10 border-t border-gray-200">
              <p className="text-xs text-gray-400">조건에 맞는 코스가 모두 소진되었습니다..</p>
            </div>
          )}

        </main>

        {/* Top 버튼 */}
        <button
          onClick={handleScrollToTop}
          className="fixed bottom-24 right-5 bg-white border border-[#42BCEB] rounded-full p-3 shadow-lg z-50 w-12 h-12 flex items-center justify-center"
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M5 15L12 8L19 15"
              stroke="#42BCEB"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>
    </NavigationLayout>
  );
};

export default CourseListPage;
