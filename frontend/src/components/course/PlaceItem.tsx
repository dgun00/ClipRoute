import { useRef } from 'react';
import shareicon from "../../assets/icons/share-icon.svg";
import Checkbox from "../common/Checkbox";
import dragHandleIcon from "../../assets/icons/Bottom/drag_handle-icon.svg";

interface PlaceItemProps {
  place: any;
  isEditMode?: boolean;
  isChecked?: boolean;
  onToggle?: () => void;
  dragHandleProps?: any;
  onShareClick?: (rect: DOMRect) => void;
}

const PlaceItem = ({ place, isEditMode = false, isChecked = false, onToggle = () => { }, dragHandleProps, onShareClick }: PlaceItemProps) => {
  const itemRef = useRef<HTMLDivElement>(null);

  return (
    <div
      ref={itemRef}
      className="flex items-center gap-3 py-4 border-b border-gray-100 last:border-0"
    >
      {/* 편집 모드일 때 체크박스 */}
      {isEditMode && (
        <div className="mr-1">
          <Checkbox checked={isChecked} onChange={onToggle} />
        </div>
      )}

      {/* 순서 번호 */}
      <div className="w-[1.25rem] h-[1.25rem] flex flex-col items-center justify-center gap-[0.625rem] rounded-[6.25rem] bg-white shadow-[0_0_6px_0_#42BCEB] flex-shrink-0">
        <span className="text-[#42BCEB] text-[12px] font-bold">{place.order}</span>
      </div>

      {/* 장소 정보 */}
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="text-[16px] font-bold text-[#333]">{place.name}</span>
          <span className="text-[12px] text-[#42BCEB]">#{place.category}</span>
        </div>
        <p className="text-[13px] text-gray-400 mt-0.5">{place.address || "주소 정보가 없습니다"}</p>
      </div>

      {/* 편집 모드: 핸들바, 일반 모드: 공유 버튼 */}
      <div className="flex gap-3 text-gray-300">
        {isEditMode ? (
          <div
            className="cursor-move p-2"
            {...dragHandleProps}
          >
            <img src={dragHandleIcon} alt="drag handle" />
          </div>
        ) : (
          <button onClick={(e) => {
            e.stopPropagation();
            if (onShareClick && itemRef.current) {
              onShareClick(itemRef.current.getBoundingClientRect());
            }
          }}>
            <img src={shareicon} alt="share" />
          </button>
        )}
      </div>
    </div>
  );
};

export default PlaceItem;