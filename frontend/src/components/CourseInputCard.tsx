import mappinicon from '../assets/icons/mappin-icon.svg';
import calendaricon from '../assets/icons/calendar-icon.svg';

interface RegionData {
  regionId: number;
  regionName: string;
  imageUrl: string;
}

interface DateRange {
  startDate: Date | null;
  endDate: Date | null;
}

interface Props {
  region: RegionData | null;
  dateRange: DateRange | null;
  onLocationClick: () => void;
  onDateClick: () => void;
}

export const CourseInputCard = ({ region, dateRange, onLocationClick, onDateClick }: Props) => {

  const formatDateRange = (dateRange: DateRange | null): string => {
    if (!dateRange?.startDate || !dateRange?.endDate) {
      return '여행 날짜를 선택해주세요';
    }

    const format = (d: Date) => `${d.getFullYear()}.${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;
    const formatShort = (d: Date) => `${String(d.getMonth() + 1).padStart(2, '0')}.${String(d.getDate()).padStart(2, '0')}`;

    const days = Math.ceil((dateRange.endDate.getTime() - dateRange.startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    const nights = days - 1;

    return `${format(dateRange.startDate)} - ${formatShort(dateRange.endDate)} [${nights}박 ${days}일]`;
  };

  return (
    <div className="border-[1px] border-[#42BCEB] rounded-2xl py-1 px-[15px] bg-white">

      {/*여행지 선택*/}
      <div
        onClick={onLocationClick}
        className="flex items-center gap-3 py-4 border-b border-[#D2D2D2] cursor-pointer"
      >
        <img src={mappinicon} alt="location" className="w-6 h-6" />
        <span className={`text-sm ${region ? 'text-gray-900' : 'text-[#999]'}`}>
          {region ? region.regionName : '여행지를 선택해 주세요'}
        </span>
      </div>

      {/*여행 날짜 선택*/}
      <div
        onClick={onDateClick}
        className="flex items-center gap-3 py-4 cursor-pointer"
      >
        <img src={calendaricon} alt="calendar" className="w-6 h-6" />
        <span className={`text-sm ${dateRange?.startDate ? 'text-gray-900' : 'text-[#999]'}`}>
          {formatDateRange(dateRange)}
        </span>
      </div>

    </div>
  );
};