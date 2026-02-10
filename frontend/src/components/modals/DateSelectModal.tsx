import { useState } from 'react';
import DatePicker from 'react-datepicker';
import { ko } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';
import './DateSelectModal.css';
import Header from '../common/Header';
import closeicon from "../../assets/icons/close-icon.svg";
import calendaricon from "../../assets/icons/calendar-icon.svg";

interface DateRange {
  startDate: Date | null;
  endDate: Date | null;
}

interface DateSelectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (dateRange: DateRange) => void;
}

const DateSelectModal = ({ isOpen, onClose, onConfirm }: DateSelectModalProps) => {
  const [startDate, setStartDate] = useState<Date | null>(null);
  const [endDate, setEndDate] = useState<Date | null>(null);

  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm({ startDate, endDate });
    onClose();
  };

  const formatDateRange = () => {
    if (!startDate) return '날짜를 선택해주세요';
    
    const format = (date: Date) => {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}.${month}.${day}`;
    };

    if (!endDate) return format(startDate);
    
    const days = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    const nights = days - 1;
    return `${format(startDate)} - ${format(endDate)} [${nights}박 ${days}일]`;
  };

  return (
    <>
      <style>{`
        @keyframes modalUp {
          from { transform: translateY(100%); }
          to { transform: translateY(0); }
        }
        .animate-modal-up {
          animation: modalUp 0.35s cubic-bezier(0.33, 1, 0.68, 1) forwards;
        }
      `}</style>
      
      
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center bg-white"
      >
        <div className="w-full h-full max-w-md bg-white flex flex-col date-select-modal animate-modal-up">
          <Header
            center={<span className='text-[18px] font-bold text-black'>날짜 선택</span>}
            right={
              <button 
                onClick={onClose}
                className="p-2 flex items-center justify-center text-gray-600 active:opacity-50"
              >
                <img src={closeicon} alt="닫기" className='w-4 h-4'/>
              </button>
            }
          />

          {/* 선택된 날짜 표시 */}
          <div className="px-5 pt-6 pb-3 shrink-0">
            <div className="flex items-center gap-2 px-4 py-4 bg-white rounded-2xl border-1 border-[#42BCEB] font-semibold">
              <img src={calendaricon} className='w-6 h-6'/>
              <span className="text-[15px] text-gray-800">{formatDateRange()}</span>
            </div>
          </div>

          
          <div className="px-5 flex-1 overflow-y-auto flex items-start justify-center pt-4">
            <DatePicker
              selected={startDate}
              onChange={(dates) => {
                const [start, end] = dates as [Date | null, Date | null];
                setStartDate(start);
                setEndDate(end);
              }}
              startDate={startDate}
              endDate={endDate}
              selectsRange
              inline
              locale={ko}
              monthsShown={1}
              dateFormat="yyyy.MM.dd"
              minDate={new Date()}
            />
          </div>

         
          <div className="px-5 pb-10 shrink-0">
            <button
              onClick={handleConfirm}
              disabled={!startDate || !endDate}
              className="w-full py-4 bg-[#42BCEB] text-white font-bold rounded-2xl disabled:bg-gray-200 disabled:text-gray-400 active:scale-[0.98] transition-all"
            >
              선택 완료
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default DateSelectModal;