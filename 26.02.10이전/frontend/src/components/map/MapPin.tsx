interface MapPinProps {
  order: number;
}

const MapPin = ({ order }: MapPinProps) => {
  return (
    <div className="relative flex justify-center w-[35px] h-[45px]">
      
      {/*물방울 모양 핀*/}
      <svg className="absolute inset-0" xmlns="http://www.w3.org/2000/svg" width="35" height="45" viewBox="0 0 26 30" fill="none">
        <path d="M13 0C20.1797 1.93277e-07 26 5.8203 26 13C26 22.316 16.4933 27.9221 13.7393 29.3506C13.2697 29.5941 12.7303 29.5941 12.2607 29.3506C9.50673 27.9221 2.43317e-07 22.316 0 13C0 5.8203 5.8203 0 13 0Z" fill="#42BCEB"/>
      </svg>

      <div 
        className="absolute z-10 w-[22px] h-[22px] bg-white rounded-full flex items-center justify-center shadow-sm"
        style={{ top: '6px' }} 
      >
        <span className="text-[#42BCEB] font-black text-[12px] leading-none">
          {order}
        </span>
      </div>
    </div>
  );
};

export default MapPin;