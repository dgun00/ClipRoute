interface VideoCardProps {
  title: string;
  region: string;
  duration: string;
  thumbnailUrl?: string;
  onClick?: () => void;
}

const VideoCard = ({ title, region, duration, thumbnailUrl, onClick }: VideoCardProps) => {
  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-3xl border border-gray-200 overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
    >
      {/*썸네일*/}
      <div className="w-full aspect-video bg-gray-100 flex items-center justify-center m-3 rounded-2xl overflow-hidden">
        {thumbnailUrl ? (
          <img 
            src={thumbnailUrl} 
            alt={title}
            className="w-full h-full object-cover"
          />
        ) : (
          <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <rect x="3" y="3" width="18" height="18" rx="3" ry="3" strokeWidth="1.5"/>
            <circle cx="8.5" cy="8.5" r="1.5" fill="currentColor"/>
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M21 15l-5-5L5 21"/>
          </svg>
        )}
      </div>

      {/*영상 정보*/}
      <div className="px-5 pb-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 whitespace-pre-line">
          {title}
        </h3>
        <div className="flex gap-2">
          <span className="text-sm text-[#42BCEB]">#{region}</span>
          <span className="text-sm text-[#42BCEB]">#{duration}</span>
        </div>
      </div>
    </div>
  );
};

export default VideoCard;