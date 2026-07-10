'use client';

import * as React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Menu, Bell, Moon, Sun, Sparkles, Search, Check, Archive, FileText, Folder } from 'lucide-react';
import { Button } from './button';

import { useAuth } from '../../context/AuthContext';
import { apiService } from '../../lib/api';

interface NavbarProps {
  onMenuToggle?: () => void;
}

interface NotificationItem {
  id: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  archived: boolean;
}

interface SearchResults {
  projects: Array<{ id: string; name: string }>;
  documents: Array<{ id: string; name: string; category: string }>;
  workspaces: Array<{ id: string; name: string }>;
}

export const Navbar = ({ onMenuToggle }: NavbarProps) => {
  const router = useRouter();
  const [isDarkMode, setIsDarkMode] = React.useState(true);
  const { user, activeWorkspace, switchWorkspace } = useAuth();
  
  // Notification dropdown states
  const [showNotifDropdown, setShowNotifDropdown] = React.useState(false);
  const [notifications, setNotifications] = React.useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = React.useState(0);

  // Search states
  const [searchQuery, setSearchQuery] = React.useState('');
  const [searchResults, setSearchResults] = React.useState<SearchResults | null>(null);
  const [showSearchDropdown, setShowSearchDropdown] = React.useState(false);

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    : 'U';

  const toggleTheme = () => {
    setIsDarkMode(!isDarkMode);
    if (typeof window !== 'undefined') {
      const root = window.document.documentElement;
      if (isDarkMode) {
        root.classList.remove('dark');
      } else {
        root.classList.add('dark');
      }
    }
  };

  // Fetch notifications
  const fetchNotifications = React.useCallback(async () => {
    if (!user) return;
    try {
      const list = await apiService.get<NotificationItem[]>('/notifications/?unread_only=true');
      setNotifications(list);
      setUnreadCount(list.filter(n => !n.read).length);
    } catch (err) {
      console.warn('Failed to load notifications:', err);
    }
  }, [user]);

  React.useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 15000); // refresh every 15s
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  // Handle marking read
  const handleMarkRead = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiService.post(`/notifications/${id}/read`);
      setNotifications(notifications.filter(n => n.id !== id));
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (err) {
      console.error(err);
    }
  };

  // Handle mark all read
  const handleMarkAllRead = async () => {
    try {
      await apiService.post('/notifications/read-all');
      setNotifications([]);
      setUnreadCount(0);
    } catch (err) {
      console.error(err);
    }
  };

  // Live search handler
  React.useEffect(() => {
    const delayDebounce = setTimeout(async () => {
      if (searchQuery.trim().length >= 2 && activeWorkspace) {
        try {
          const results = await apiService.get<SearchResults>(
            `/search/?q=${searchQuery}&workspace_id=${activeWorkspace.id}`
          );
          setSearchResults(results);
          setShowSearchDropdown(true);
        } catch (err) {
          console.warn('Search query failed:', err);
        }
      } else {
        setSearchResults(null);
        setShowSearchDropdown(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounce);
  }, [searchQuery, activeWorkspace]);

  return (
    <header className="sticky top-0 z-40 flex h-16 w-full items-center justify-between border-b border-zinc-900 bg-zinc-950/80 px-6 backdrop-blur-md">
      <div className="flex items-center space-x-4 flex-1">
        {/* Mobile menu trigger */}
        <button
          onClick={onMenuToggle}
          className="block rounded-lg p-1.5 text-zinc-400 hover:bg-zinc-900 hover:text-white transition md:hidden"
        >
          <Menu size={20} />
        </button>

        {/* Brand logo */}
        <Link href="/dashboard" className="flex items-center space-x-2 mr-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/20">
            <Sparkles size={18} />
          </div>
          <span className="text-md font-bold tracking-tight text-white hidden sm:block">
            AI Product<span className="text-indigo-500">OS</span>
          </span>
        </Link>

        {/* Global Search Input */}
        {activeWorkspace && (
          <div className="relative max-w-md w-full hidden md:block">
            <div className="flex items-center space-x-2 bg-zinc-900 px-3 py-1.5 border border-zinc-800 rounded-lg focus-within:border-indigo-500 transition">
              <Search size={14} className="text-zinc-500" />
              <input
                type="text"
                placeholder="Global workspace search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-transparent text-xs text-zinc-100 placeholder:text-zinc-500 focus:outline-none w-full"
              />
            </div>

            {/* Search Dropdown Results */}
            {showSearchDropdown && searchResults && (
              <div className="absolute top-11 left-0 w-full bg-zinc-950 border border-zinc-900 rounded-xl p-3 shadow-2xl space-y-3 z-50">
                {searchResults.projects.length > 0 && (
                  <div>
                    <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1 flex items-center">
                      <Folder size={10} className="mr-1" /> Roadmaps
                    </div>
                    {searchResults.projects.map(p => (
                      <div
                        key={p.id}
                        onClick={() => {
                          router.push(`/projects/${p.id}`);
                          setShowSearchDropdown(false);
                          setSearchQuery('');
                        }}
                        className="text-xs text-zinc-300 hover:text-white p-1 hover:bg-zinc-900 rounded cursor-pointer transition"
                      >
                        {p.name}
                      </div>
                    ))}
                  </div>
                )}

                {searchResults.documents.length > 0 && (
                  <div>
                    <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1 flex items-center">
                      <FileText size={10} className="mr-1" /> Documents
                    </div>
                    {searchResults.documents.map(d => (
                      <div
                        key={d.id}
                        onClick={() => {
                          router.push('/documents');
                          setShowSearchDropdown(false);
                          setSearchQuery('');
                        }}
                        className="text-xs text-zinc-300 hover:text-white p-1 hover:bg-zinc-900 rounded cursor-pointer transition"
                      >
                        {d.name} <span className="text-[9px] text-zinc-650">({d.category})</span>
                      </div>
                    ))}
                  </div>
                )}

                {searchResults.projects.length === 0 && searchResults.documents.length === 0 && (
                  <div className="text-xs text-zinc-500 text-center py-2">
                    No results match "{searchQuery}"
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center space-x-3">
        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleTheme}
          className="rounded-full p-2 h-9 w-9 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/60"
        >
          {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
        </Button>

        {/* Notification center */}
        <div className="relative">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowNotifDropdown(!showNotifDropdown)}
            className="relative rounded-full p-2 h-9 w-9 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900/60"
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-indigo-500" />
            )}
          </Button>

          {/* Notifications Dropdown list */}
          {showNotifDropdown && (
            <div className="absolute right-0 top-11 w-80 bg-zinc-950 border border-zinc-900 rounded-xl p-4 shadow-2xl z-50 space-y-3">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-2">
                <span className="text-xs font-bold text-white">Notifications</span>
                {unreadCount > 0 && (
                  <button onClick={handleMarkAllRead} className="text-[10px] text-indigo-400 hover:underline">
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-60 overflow-y-auto space-y-2.5">
                {notifications.map((notif) => (
                  <div key={notif.id} className="p-2 bg-zinc-900/30 border border-zinc-900 rounded-lg flex items-start justify-between">
                    <div className="space-y-0.5 pr-2">
                      <div className="text-xs font-bold text-white">{notif.title}</div>
                      <div className="text-[10px] text-zinc-400 leading-tight">{notif.message}</div>
                    </div>
                    <button
                      onClick={(e) => handleMarkRead(notif.id, e)}
                      className="p-1 hover:bg-zinc-800 rounded text-zinc-500 hover:text-zinc-200"
                      title="Mark read"
                    >
                      <Check size={12} />
                    </button>
                  </div>
                ))}

                {notifications.length === 0 && (
                  <div className="text-center text-xs text-zinc-500 py-6">
                    You have no unread notifications.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* User Profile Avatar */}
        <div className="flex items-center space-x-2 border-l border-zinc-800 pl-3">
          <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 border border-zinc-700 flex items-center justify-center text-xs font-bold text-white shadow-md">
            {initials}
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-bold text-zinc-200">{user?.full_name || 'Loading...'}</p>
            <p className="text-[10px] text-zinc-500 leading-none">{user?.email || ''}</p>
          </div>
        </div>
      </div>
    </header>
  );
};
