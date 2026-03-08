import type { Course } from '../types/video';

interface VideoCardProps {
  course: Course;
  onClick?: () => void;
}

const VideoCard = ({ course, onClick }: VideoCardProps) => {
  const displayThumbnailUrl = course.yt_video_id
    ? `https://cliproute-images.s3.ap-northeast-2.amazonaws.com/images/courses/${course.yt_video_id}.jpg`
    : course.thumbnailUrl;

  return (
    <div
      onClick={onClick}
      className="flex flex-col items-start w-[22.0625rem] px-[0.9375rem] py-[0.75rem] gap-[0.625rem] bg-white rounded-2xl border border-[#E4E4E4] cursor-pointer"
    >
      {/* 썸네일 */}
      <div className="h-[10rem] self-stretch rounded-xl overflow-hidden">
        {displayThumbnailUrl ? (
          <img
            src={displayThumbnailUrl}
            alt={course.videoTitle}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gray-100">
            <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <rect x="3" y="3" width="18" height="18" rx="3" ry="3" strokeWidth="1.5" />
              <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 15l-5-5L5 21" />
            </svg>
          </div>
        )}
      </div>

      {/* 영상 정보 */}
      <div className="px-1 pb-1 w-full">
        <h3 className="text-sm font-semibold text-black mt-2">{course.channelName}</h3>
        <h3 className="text-sm font-semibold text-gray-900 mb-2 whitespace-pre-line line-clamp-2">
          {course.videoTitle}
        </h3>

        <div className="flex gap-2">
          <span className="text-sm text-[#42BCEB] font-semibold">#{course.regionName}</span>
          <span className="text-sm text-[#42BCEB] font-semibold">#{course.travelDays === 1 ? "당일치기" : `${Math.max(0, course.travelDays - 1)}박 ${course.travelDays}일`}</span>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;