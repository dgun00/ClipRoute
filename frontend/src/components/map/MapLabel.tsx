// src/components/map/MapLabel.tsx
interface MapLabelProps {
  name: string;
}

const MapLabel = ({ name }: MapLabelProps) => {
  return (
    <div className="absolute bottom-[50px] left-1/2 -translate-x-1/2 z-20 pointer-events-none whitespace-nowrap">
     
      <div className="bg-[#42BCEB] text-white text-[14px]  px-3 py-1.5 rounded-2xl shadow-sm">
        {name}
      </div>
    </div>
  );
};

export default MapLabel;