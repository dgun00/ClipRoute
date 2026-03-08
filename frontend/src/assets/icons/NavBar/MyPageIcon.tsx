interface IconProps {
  isActive: boolean;
  size?: number;
}

export const MyPageIcon = ({ isActive, size = 24 }: IconProps) => {
  const ACTIVE_COLOR = "#42BCEB";

  // 활성화 상태 
  if (isActive) {
    return (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path 
          d="M19.6515 19.4054C20.2043 19.2902 20.5336 18.7117 20.2589 18.2183C19.6533 17.1307 18.6993 16.1749 17.4788 15.4465C15.907 14.5085 13.9812 14 12 14C10.0188 14 8.09292 14.5085 6.52112 15.4465C5.30069 16.1749 4.34666 17.1307 3.74108 18.2183C3.46638 18.7117 3.79562 19.2902 4.34843 19.4054C9.39524 20.4572 14.6047 20.4572 19.6515 19.4054Z" 
          fill={ACTIVE_COLOR} 
        />
        <circle cx="12" cy="8" r="5" fill={ACTIVE_COLOR} />
      </svg>
    );
  }

  // 비활성화 상태
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path 
        d="M19 21C19 18.2386 15.4183 16 11 16C6.58172 16 3 18.2386 3 21M11 13C8.23858 13 6 10.7614 6 8C6 5.23858 8.23858 3 11 3C13.7614 3 16 5.23858 16 8C16 10.7614 13.7614 13 11 13Z" 
        stroke="black" 
        strokeWidth="1.5" 
        strokeLinecap="round" 
        strokeLinejoin="round" 
      />
    </svg>
  );
};