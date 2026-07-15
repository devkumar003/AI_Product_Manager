'use client';

import * as React from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { api, apiService } from '../lib/api';

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url?: string | null;
  phone?: string | null;
  timezone: string;
  language: string;
  preferences: Record<string, any>;
  is_verified: boolean;
  is_active: boolean;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string | null;
  logo?: string | null;
  owner_id: string;
  plan: string;
  status: string;
}

export interface Workspace {
  id: string;
  organization_id: string;
  name: string;
  description?: string | null;
  icon?: string | null;
  color?: string | null;
  visibility: string;
  archived: boolean;
}

interface AuthContextType {
  user: UserResponse | null;
  organizations: Organization[];
  workspaces: Workspace[];
  activeWorkspace: Workspace | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  signup: (payload: Record<string, any>) => Promise<void>;
  logout: () => Promise<void>;
  switchWorkspace: (workspaceId: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = React.createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = React.useState<UserResponse | null>(null);
  const [organizations, setOrganizations] = React.useState<Organization[]>([]);
  const [workspaces, setWorkspaces] = React.useState<Workspace[]>([]);
  const [activeWorkspace, setActiveWorkspace] = React.useState<Workspace | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  
  const router = useRouter();
  const pathname = usePathname();

  // Helper to fetch user details and context state
  const loadContextData = React.useCallback(async () => {
    try {
      // 1. Fetch user profile
      const userData = await apiService.get<UserResponse>('/users/me');
      setUser(userData);

      // 2. Fetch User Organizations
      const orgsData = await apiService.get<Organization[]>('/organizations/');
      setOrganizations(orgsData);

      // 3. Determine active workspace
      const activeWsId = userData.preferences?.active_workspace_id;
      
      let wsList: Workspace[] = [];
      let currentWs: Workspace | null = null;

      // If user belongs to an organization, load workspaces
      if (orgsData.length > 0) {
        // Load workspaces from the first organization as default, or from active workspace organization
        const targetOrgId = orgsData[0].id;
        wsList = await apiService.get<Workspace[]>(`/workspaces/organization/${targetOrgId}`);
        setWorkspaces(wsList);

        if (activeWsId) {
          currentWs = wsList.find(w => w.id === activeWsId) || wsList[0] || null;
        } else if (wsList.length > 0) {
          currentWs = wsList[0];
          // Try to set default active workspace on backend
          await apiService.post(`/workspaces/${currentWs.id}/switch`);
        }
      }
      
      setActiveWorkspace(currentWs);
    } catch (err) {
      console.error('Failed to load user profile or workspace context:', err);
      // Token is likely invalid or expired
      localStorage.removeItem('auth_token');
      setUser(null);
      setOrganizations([]);
      setWorkspaces([]);
      setActiveWorkspace(null);
      
      // If we're on a protected page, redirect
      if (pathname !== '/login' && pathname !== '/signup' && pathname !== '/forgot-password' && pathname !== '/') {
        router.replace('/login');
      }
    } finally {
      setIsLoading(false);
    }
  }, [router, pathname]);

  // Handle initial load / refresh state
  React.useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      loadContextData();
    } else {
      setIsLoading(false);
      // Redirect if not on public route
      if (pathname !== '/login' && pathname !== '/signup' && pathname !== '/forgot-password' && pathname !== '/') {
        router.replace('/login');
      }
    }
  }, [loadContextData, pathname, router]);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post<{ access_token: string }>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const token = response.data.access_token;
      localStorage.setItem('auth_token', token);
      await loadContextData();
      
      router.push('/dashboard');
    } catch (err) {
      setIsLoading(false);
      throw err;
    }
  };

  const signup = async (payload: Record<string, any>) => {
    setIsLoading(true);
    try {
      // Register
      await apiService.post('/auth/signup', payload);
      
      // Automatically login
      await login(payload.email, payload.password);
    } catch (err) {
      setIsLoading(false);
      throw err;
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await api.post('/auth/logout');
    } catch (err) {
      console.warn('Backend logout failed or not implemented:', err);
    } finally {
      localStorage.removeItem('auth_token');
      setUser(null);
      setOrganizations([]);
      setWorkspaces([]);
      setActiveWorkspace(null);
      setIsLoading(false);
      router.replace('/login');
    }
  };

  const switchWorkspace = async (workspaceId: string) => {
    try {
      const result = await apiService.post<{ active_workspace_id: string }>(`/workspaces/${workspaceId}/switch`);
      
      // Update local state active workspace
      if (user) {
        setUser({
          ...user,
          preferences: {
            ...user.preferences,
            active_workspace_id: result.active_workspace_id,
          },
        });
      }

      // Fetch workspaces list for the new organization if workspace belongs to a different org
      // For now, we find workspace in the current list
      const targetWs = workspaces.find(w => w.id === workspaceId);
      if (targetWs) {
        setActiveWorkspace(targetWs);
      } else {
        // If workspace is not in current list (maybe user switched orgs), reload context data
        const token = localStorage.getItem('auth_token');
        if (token) {
          await loadContextData();
        }
      }
    } catch (err) {
      console.error('Failed to switch workspace:', err);
      throw err;
    }
  };

  const refreshUser = async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        await loadContextData();
      }
    } catch (err) {
      console.error('Failed to refresh user context:', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        organizations,
        workspaces,
        activeWorkspace,
        isAuthenticated: !!user,
        isLoading,
        login,
        signup,
        logout,
        switchWorkspace,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
