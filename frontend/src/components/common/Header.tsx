interface HeaderProps {
  left?: React.ReactNode;
  center?: React.ReactNode;
  right?: React.ReactNode;
}

const Header = ({ left, center, right }: HeaderProps) => {
  return (
    <header className="relative flex items-center w-full min-h-[3.5rem] h-[3.5rem] px-4 bg-white shrink-0">
    
      <div className="flex items-center justify-start min-w-0">
    {left}
  </div>

  <div className="absolute left-1/2 -translate-x-1/2 flex items-center">
    {center}
  </div>

  <div className="ml-auto flex items-center justify-end gap-2">
    {right}
  </div>
</header>
  );
};

export default Header;
