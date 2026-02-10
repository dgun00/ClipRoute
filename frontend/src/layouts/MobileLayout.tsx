import { Outlet } from 'react-router-dom';
import type { ReactNode } from 'react';

interface MobileLayoutProps {
  children?: ReactNode;
}

export default function MobileLayout({ children }: MobileLayoutProps) {
  return (
    <div className="w-full h-dvh bg-white">
      {children || <Outlet />}
    </div>
  );
}