'use client';

import * as React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { twMerge } from 'tailwind-merge';
import {
  LayoutDashboard,
  FolderKanban,
  FileText,
  Settings,
  User,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ChevronDown,
  Calendar,
  Plug,
  Code2,
  Building2,
  Cpu,
  MessageSquare,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export const Sidebar = ({ isOpen, setIsOpen }: SidebarProps) => {
  const pathname = usePathname();
  const { workspaces, activeWorkspace, switchWorkspace, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = React.useState(false);

  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Projects', href: '/projects', icon: FolderKanban },
    { name: 'AI Hub', href: '/dashboard/ai-dashboard', icon: Sparkles },
    { name: 'AI Agents', href: '/dashboard/agents', icon: Cpu },
    { name: 'AI Chat', href: '/dashboard/ai-chat', icon: MessageSquare },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Planning', href: '/dashboard/planning', icon: Calendar },
    { name: 'Integrations', href: '/dashboard/integrations', icon: Plug },
    { name: 'Development', href: '/dashboard/development', icon: Code2 },
    { name: 'Executive', href: '/dashboard/executive', icon: Building2 },
    { name: 'Profile', href: '/profile', icon: User },
    { name: 'Settings', href: '/settings', icon: Settings },
  ];

  const handleWorkspaceSelect = async (workspaceId: string) => {
    try {
      await switchWorkspace(workspaceId);
      setDropdownOpen(false);
    } catch (err) {
      console.error('Failed to switch workspace:', err);
    }
  };

  return (
    <aside
      className={twMerge(
        'fixed bottom-0 top-16 z-30 flex flex-col border-r border-zinc-900 bg-zinc-950/80 backdrop-blur-md transition-all duration-300',
        isOpen ? 'w-64' : 'w-16'
      )}
    >
      {/* Sidebar Toggle Handle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute -right-3 top-4 z-40 rounded-full border border-zinc-800 bg-zinc-950 p-1 text-zinc-400 hover:text-white transition duration-200 shadow-md active:scale-90"
      >
        {isOpen ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
      </button>

      {/* Workspace Brand / Selector */}
      <div className="relative border-b border-zinc-900/50 p-4">
        <button
          onClick={() => isOpen && setDropdownOpen(!dropdownOpen)}
          className={twMerge(
            'flex w-full items-center space-x-3 rounded-lg p-2 transition-all duration-200',
            isOpen ? 'hover:bg-zinc-900/40 cursor-pointer' : 'justify-center cursor-default'
          )}
        >
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white border"
            style={{
              backgroundColor: `${activeWorkspace?.color || '#6366f1'}15`,
              borderColor: `${activeWorkspace?.color || '#6366f1'}40`,
              color: activeWorkspace?.color || '#6366f1',
            }}
          >
            <Sparkles size={16} />
          </div>
          {isOpen && (
            <div className="flex flex-1 items-center justify-between min-w-0">
              <div className="text-left min-w-0">
                <h2 className="text-sm font-bold text-white truncate leading-none">
                  {activeWorkspace?.name || 'Loading...'}
                </h2>
                <span className="text-[10px] text-zinc-500 font-medium truncate block mt-0.5">
                  Workspace Active
                </span>
              </div>
              <ChevronDown
                size={14}
                className={twMerge(
                  'text-zinc-500 transition-transform duration-200 shrink-0 ml-1',
                  dropdownOpen && 'rotate-180'
                )}
              />
            </div>
          )}
        </button>

        {/* Workspace Selector Dropdown */}
        {dropdownOpen && isOpen && (
          <div className="absolute left-4 right-4 top-16 z-50 rounded-xl border border-zinc-800 bg-zinc-900/95 p-2 shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150">
            <div className="mb-1.5 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-zinc-500">
              Switch Workspace ({workspaces.length})
            </div>
            <div className="max-h-48 overflow-y-auto space-y-1 pr-1">
              {workspaces.map((ws) => (
                <button
                  key={ws.id}
                  onClick={() => handleWorkspaceSelect(ws.id)}
                  className={twMerge(
                    'flex w-full items-center space-x-2.5 rounded-lg px-2.5 py-2 text-xs font-medium transition-colors',
                    activeWorkspace?.id === ws.id
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30 font-semibold'
                      : 'text-zinc-400 hover:bg-zinc-800/60 hover:text-white'
                  )}
                >
                  <div
                    className="h-2 w-2 rounded-full shrink-0"
                    style={{ backgroundColor: ws.color || '#6366f1' }}
                  />
                  <span className="truncate">{ws.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Menu Links */}
      <nav className="flex-1 space-y-1 px-3 py-6 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isGeneratorRoute = pathname.includes('-generator') || pathname.includes('idea-analyzer') || pathname.includes('knowledge-base');
          const isActive =
            item.href === '/dashboard'
              ? pathname === '/dashboard'
              : item.href === '/dashboard/ai-dashboard'
              ? pathname === '/dashboard/ai-dashboard' || isGeneratorRoute
              : pathname.startsWith(item.href);

          return (
            <Link
              key={item.name}
              href={item.href}
              className={twMerge(
                'group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-300 relative',
                isActive
                  ? 'bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-[0_0_15px_rgba(99,102,241,0.12)]'
                  : 'text-zinc-400 hover:bg-zinc-900/40 hover:text-zinc-100 border border-transparent'
              )}
            >
              <Icon
                size={18}
                className={twMerge(
                  'transition duration-300 shrink-0',
                  isActive ? 'text-indigo-400' : 'text-zinc-400 group-hover:text-zinc-100',
                  isOpen ? 'mr-3' : 'mr-0'
                )}
              />
              {isOpen && <span>{item.name}</span>}
              {!isOpen && (
                <div className="absolute left-14 rounded bg-zinc-950 border border-zinc-800 px-2 py-1 text-xs text-white opacity-0 group-hover:opacity-100 pointer-events-none transition duration-200 whitespace-nowrap shadow-xl">
                  {item.name}
                </div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Logout Footer */}
      <div className="border-t border-zinc-900/50 p-3">
        <button
          onClick={logout}
          className={twMerge(
            'group flex w-full items-center rounded-lg px-3 py-2.5 text-sm font-medium text-zinc-500 hover:bg-red-950/10 hover:text-red-400 transition-all duration-300 border border-transparent',
            !isOpen && 'justify-center'
          )}
        >
          <LogOut
            size={18}
            className={twMerge('transition duration-300', isOpen ? 'mr-3' : 'mr-0')}
          />
          {isOpen && <span>Logout</span>}
          {!isOpen && (
            <div className="absolute left-14 rounded bg-zinc-950 border border-zinc-800 px-2 py-1 text-xs text-red-400 opacity-0 group-hover:opacity-100 pointer-events-none transition duration-200 whitespace-nowrap shadow-xl">
              Logout
            </div>
          )}
        </button>
      </div>
    </aside>
  );
};
