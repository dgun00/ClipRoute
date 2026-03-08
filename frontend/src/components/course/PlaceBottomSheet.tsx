import { useState } from 'react';
import { DragDropContext, Droppable, Draggable, type DropResult } from '@hello-pangea/dnd';
import PlaceItem from './PlaceItem';
import Checkbox from '../common/Checkbox';

const PlaceBottomSheet = ({
  places = [],
  title = "영상 속 장소 및 코스 정리",
  isEditMode = false,
  setPlaces,
  selectedItems = new Set(),
  onToggleSelect = () => { },
  onDaySelect = () => { },
  onShareClick,
}: any) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleDragEnd = (result: DropResult) => {
    if (!result.destination || !setPlaces) return;

    const sourceDay = Number(result.source.droppableId);
    const destDay = Number(result.destination.droppableId);

    // 같은 자리에 둠
    if (sourceDay === destDay && result.source.index === result.destination.index) return;

    const newPlaces = [...places];

    // 1. 같은 Day 내 이동
    if (sourceDay === destDay) {
      const dayPlaces = newPlaces.filter(p => p.day === sourceDay)
        .sort((a, b) => (a.order || 0) - (b.order || 0));

      const [moved] = dayPlaces.splice(result.source.index, 1);
      dayPlaces.splice(result.destination.index, 0, moved);

      // 순서 재할당
      dayPlaces.forEach((p, idx) => { p.order = idx + 1; });

      // 원본 배열 업데이트: 해당 Day만 교체하고 나머지는 유지
      const otherPlaces = newPlaces.filter(p => p.day !== sourceDay);
      // 병합 시 순서가 섞이지 않도록 주의 (날짜별 정렬이 필요할 수 있음)
      const updatedPlaces = [...otherPlaces, ...dayPlaces].sort((a, b) => a.day - b.day || (a.order || 0) - (b.order || 0));
      setPlaces(updatedPlaces);

    } else {
      // 2. 다른 Day로 이동
      const sourcePlaces = newPlaces.filter(p => p.day === sourceDay)
        .sort((a, b) => (a.order || 0) - (b.order || 0));
      const destPlaces = newPlaces.filter(p => p.day === destDay)
        .sort((a, b) => (a.order || 0) - (b.order || 0));

      const [moved] = sourcePlaces.splice(result.source.index, 1);

      // 이동한 아이템 정보 업데이트
      moved.day = destDay;

      destPlaces.splice(result.destination.index, 0, moved);

      // 순서 재할당
      sourcePlaces.forEach((p, idx) => { p.order = idx + 1; });
      destPlaces.forEach((p, idx) => { p.order = idx + 1; });

      // 전체 병합
      const otherPlaces = newPlaces.filter(p => p.day !== sourceDay && p.day !== destDay);
      const updatedPlaces = [...otherPlaces, ...sourcePlaces, ...destPlaces].sort((a, b) => a.day - b.day || (a.order || 0) - (b.order || 0));
      setPlaces(updatedPlaces);
    }
  };


  return (
    <div
      className="fixed left-0 right-0 z-20 bg-white rounded-t-[30px] shadow-[0_-8px_20px_rgba(0,0,0,0.1)] transition-all duration-500 ease-in-out"
      style={{
        height: '65vh',
        bottom: isOpen ? '0' : 'calc(80px - 65vh)'
      }}
    >
      <div
        className="flex flex-col items-center py-4 cursor-pointer"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="w-[40px] h-[4px] bg-[#E5E5E5] rounded-full mb-3" />
        <h2 className="text-[18px] font-bold text-[#333] px-5 w-full text-left">
          {title}
        </h2>
      </div>

      <div className="px-5 pb-20 overflow-y-auto h-[calc(65vh-80px)] scrollbar-hide">
        {isEditMode ? (
          <DragDropContext onDragEnd={handleDragEnd}>
            {(() => {
              const maxDay = places.length > 0 ? Math.max(...places.map((p: any) => p.day)) : 1;
              const renderElements = [];

              for (let day = 1; day <= maxDay; day++) {
                const dayPlaces = places
                  .filter((p: any) => p.day === day)
                  .sort((a: any, b: any) => (a.order || 0) - (b.order || 0));

                const isDayAllSelected = dayPlaces.length > 0 && dayPlaces.every((p: any) => selectedItems.has(p.id));

                renderElements.push(
                  <div key={`day-section-${day}`} className="mb-2">
                    {/* Day Header */}
                    <div className="flex items-center gap-2 mb-4 mt-6 first:mt-0 text-[#42BCEB] font-bold">
                      {isEditMode && dayPlaces.length > 0 && (
                        <div className="mr-2">
                          <Checkbox
                            checked={isDayAllSelected}
                            onChange={() => onDaySelect(day, !isDayAllSelected)}
                          />
                        </div>
                      )}
                      <span>Day {day}</span>
                      <div className="flex-1 h-[1px] bg-black" />
                    </div>

                    {/* Droppable Area for this Day */}
                    <Droppable droppableId={String(day)}>
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.droppableProps}
                          className={`min-h-[50px] rounded-lg transition-colors ${snapshot.isDraggingOver ? "bg-blue-50" : ""
                            }`}
                        >
                          {dayPlaces.length > 0 ? (
                            dayPlaces.map((place: any, index: number) => {
                              const draggableId = place.id ? `place-${place.id}` : `place-idx-${day}-${index}`;
                              return (
                                <Draggable
                                  key={draggableId}
                                  draggableId={draggableId}
                                  index={index}
                                >
                                  {(dragProvided) => (
                                    <div
                                      ref={dragProvided.innerRef}
                                      {...dragProvided.draggableProps}
                                      className="bg-white mb-2"
                                    >
                                      <PlaceItem
                                        place={place}
                                        isEditMode={isEditMode}
                                        dragHandleProps={dragProvided.dragHandleProps}
                                        isChecked={selectedItems.has(place.id)}
                                        onToggle={() => onToggleSelect(place.id)}
                                      />
                                    </div>
                                  )}
                                </Draggable>
                              );
                            })
                          ) : (
                            <div className="py-8 text-center text-gray-400 text-sm">
                              아직 일정이 없어요
                            </div>
                          )}
                          {provided.placeholder}
                        </div>
                      )}
                    </Droppable>
                  </div>
                );
              }
              return <div>{renderElements}</div>;
            })()}
          </DragDropContext>
        ) : (
          <div>
            {(() => {
              const maxDay = places.length > 0 ? Math.max(...places.map((p: any) => p.day)) : 1;
              const renderList = [];

              for (let day = 1; day <= maxDay; day++) {
                const dayPlaces = places.filter((p: any) => p.day === day);

                // Header
                renderList.push(
                  <div key={`view-header-${day}`} className="flex items-center gap-2 mb-4 mt-6 first:mt-0 text-[#42BCEB] font-bold">
                    <span>Day {day}</span>
                    <div className="flex-1 h-[1px] bg-black" />
                  </div>
                );

                // List
                if (dayPlaces.length > 0) {
                  dayPlaces.forEach((place: any, index: number) => {
                    const uniqueKey = place.id ? `view-place-${place.id}` : `view-place-idx-${day}-${index}`;
                    renderList.push(
                      <PlaceItem
                        key={uniqueKey}
                        place={place}
                        isEditMode={false}
                        onShareClick={(rect: DOMRect) => {
                          if (onShareClick) onShareClick(place, rect);
                        }}
                      />
                    );
                  });
                } else {
                  renderList.push(
                    <div key={`view-empty-${day}`} className="py-8 text-center text-gray-400 text-sm">
                      아직 일정이 없어요
                    </div>
                  );
                }
              }
              return renderList;
            })()}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlaceBottomSheet;