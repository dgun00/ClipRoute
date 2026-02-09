import likeicon from "../../assets/icons/like-icon.svg";
import shareicon from "../../assets/icons/share-icon.svg";

const PlaceItem = ({ place }: any) => (
  <div className="flex items-start gap-3 py-4 border-b border-gray-100 last:border-0">
    <div className="w-6 h-6 rounded-full border border-[#42BCEB] bg-white flex items-center justify-center flex-shrink-0 mt-1">
      <span className="text-[#42BCEB] text-[12px] font-bold">{place.order}</span>
    </div>
    <div className="flex-1">
      <div className="flex items-center gap-2">
        <span className="text-[16px] font-bold text-[#333]">{place.name}</span>
        <span className="text-[12px] text-[#42BCEB]">#{place.category}</span>
      </div>
      <p className="text-[13px] text-gray-400 mt-0.5">{place.address || "주소 정보가 없습니다"}</p>
    </div>
    <div className="flex gap-3 text-gray-300 mt-1">
      <button>
        <img src={likeicon}/>
      </button>
      <button>
        <img src={shareicon}/>
      </button>
    </div>
  </div>
);

export default PlaceItem;