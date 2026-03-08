type ToggleProps = {
  checked: boolean;
  onChange: () => void;
};

export default function Toggle({ checked, onChange }: ToggleProps) {
  return (
    <button
      onClick={onChange}
      className={`
        w-11 h-6 rounded-full relative transition-colors
        ${checked ? "bg-[#42BCEB]" : "bg-gray-300"}
      `}
    >
      <div
        className={`
          w-5 h-5 bg-white rounded-full absolute top-0.5 left-0.5
          transition-transform
          ${checked ? "translate-x-5" : "translate-x-0"}
        `}
      />
    </button>
  );
}
