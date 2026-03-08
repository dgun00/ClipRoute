interface CheckboxProps {
  checked: boolean;
  onChange: () => void;
}

export default function Checkbox({ checked, onChange }: CheckboxProps) {
  return (
    <button
      onClick={(e) => {
        e.stopPropagation();
        onChange();
      }}
      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all ${
        checked
          ? "bg-[#42BCEB] border-[#42BCEB]"
          : "border-gray-300"
      }`}
    >
      {checked && (
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <path d="M11.5 3.5L5 11 2.5 8.5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      )}
    </button>
  );
}