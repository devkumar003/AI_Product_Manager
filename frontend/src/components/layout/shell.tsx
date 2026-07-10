'use client';

import * as React from 'react';
import { Navbar } from '../ui/navbar';
import { Sidebar } from '../ui/sidebar';
import { twMerge } from 'tailwind-merge';

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell = ({ children }: AppShellProps) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  // Sync initial sidebar state based on screen width
  React.useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      } else {
        setSidebarOpen(true);
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <Navbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex flex-1 relative">
        {/* Collapsible Sidebar */}
        <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />

        {/* Content Area */}
        <main
          className={twMerge(
            'flex-1 p-6 md:p-8 transition-all duration-300 min-h-[calc(100vh-4rem)]',
            sidebarOpen ? 'md:pl-[17rem]' : 'md:pl-[5rem]'
          )}
        >
          <div className="max-w-7xl mx-auto space-y-6">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
