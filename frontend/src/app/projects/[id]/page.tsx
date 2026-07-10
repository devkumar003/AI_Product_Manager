'use client';

import * as React from 'react';
import { useParams } from 'next/navigation';
import { 
  Calendar, FileText, Activity, AlertCircle, RefreshCw, 
  Settings, Users, BarChart3, Database, ShieldAlert, ChevronRight
} from 'lucide-react';

import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

interface DashboardStats {
  project: {
    id: string;
    name: string;
    description: string;
    status: string;
    priority: string;
    color: string | null;
    icon: string | null;
    archived: boolean;
  };
  recent_activity: Array<{
    id: string;
    action: string;
    description: string;
    created_at: string;
  }>;
  recent_documents: Array<{
    id: string;
    name: string;
    category: string;
    file_size: number;
    updated_at: string;
  }>;
  stats: {
    document_count: number;
    storage_used_bytes: number;
  };
}

export default function ProjectDashboardPage() {
  const { id: projectId } = useParams();
  const { activeWorkspace } = useAuth();
  
  const [data, setData] = React.useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMsg, setErrorMsg] = React.useState('');

  const fetchDashboard = React.useCallback(async () => {
    if (!activeWorkspace || !projectId) return;
    setIsLoading(true);
    setErrorMsg('');
    try {
      const result = await apiService.get<DashboardStats>(
        `/projects/${activeWorkspace.id}/${projectId}/dashboard`
      );
      setData(result);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to fetch project dashboard.');
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspace, projectId]);

  React.useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="p-6 text-zinc-500 text-center">
          Please select an active workspace to view this project dashboard.
        </div>
      </AppShell>
    );
  }

  if (isLoading) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center py-32 space-y-4">
          <RefreshCw size={32} className="animate-spin text-indigo-500" />
          <span className="text-zinc-400 text-sm">Aggregating roadmap metrics...</span>
        </div>
      </AppShell>
    );
  }

  if (errorMsg || !data) {
    return (
      <AppShell>
        <div className="max-w-md mx-auto my-12 p-6 bg-red-950/20 border border-red-900/50 rounded-2xl text-center space-y-4">
          <ShieldAlert size={48} className="text-red-500 mx-auto" />
          <h2 className="text-lg font-bold text-white">Dashboard Error</h2>
          <p className="text-zinc-400 text-sm">{errorMsg || 'Project not found.'}</p>
          <Button variant="outline" href="/projects">Back to Projects</Button>
        </div>
      </AppShell>
    );
  }

  const { project, recent_activity, recent_documents, stats } = data;
  const storageMB = (stats.storage_used_bytes / (1024 * 1024)).toFixed(2);

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Breadcrumbs */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <Breadcrumb 
              items={[
                { label: 'Home', href: '/dashboard' }, 
                { label: 'Projects', href: '/projects' },
                { label: project.name }
              ]} 
            />
            <div className="flex items-center space-x-3 mt-1">
              <h1 className="text-3xl font-extrabold tracking-tight text-white">
                {project.name}
              </h1>
              <span className={`text-xs px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                project.status === 'Planning' ? 'bg-emerald-950/30 border border-emerald-900/50 text-emerald-400' :
                project.status === 'Development' ? 'bg-indigo-950/30 border border-indigo-900/50 text-indigo-400' :
                'bg-zinc-900 border border-zinc-800 text-zinc-400'
              }`}>
                {project.status}
              </span>
            </div>
            <p className="text-zinc-400 text-sm mt-2 max-w-2xl">{project.description || 'No description provided.'}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" href={`/projects/${project.id}/settings`}>
              <Settings size={14} className="mr-2" /> Settings
            </Button>
            <Button variant="primary" href="/documents">
              <FileText size={14} className="mr-2" /> Upload Spec
            </Button>
          </div>
        </div>

        {/* Stats Grid Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="p-6 bg-zinc-950/40 border-zinc-900 hover:border-zinc-800 transition">
            <div className="flex items-center justify-between text-zinc-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Specifications</span>
              <FileText size={18} className="text-indigo-400" />
            </div>
            <div className="text-3xl font-bold mt-2 text-white">{stats.document_count}</div>
            <div className="text-xs text-zinc-400 mt-1">Total documents uploaded</div>
          </Card>

          <Card className="p-6 bg-zinc-950/40 border-zinc-900 hover:border-zinc-800 transition">
            <div className="flex items-center justify-between text-zinc-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Storage Capacity</span>
              <Database size={18} className="text-emerald-400" />
            </div>
            <div className="text-3xl font-bold mt-2 text-white">{storageMB} MB</div>
            <div className="text-xs text-zinc-400 mt-1">Roadmap file space consumed</div>
          </Card>

          <Card className="p-6 bg-zinc-950/40 border-zinc-900 hover:border-zinc-800 transition">
            <div className="flex items-center justify-between text-zinc-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Priority Level</span>
              <BarChart3 size={18} className="text-amber-400" />
            </div>
            <div className="text-3xl font-bold mt-2 text-white">{project.priority}</div>
            <div className="text-xs text-zinc-400 mt-1">Milestone delivery speed</div>
          </Card>

          <Card className="p-6 bg-zinc-950/40 border-zinc-900 hover:border-zinc-800 transition">
            <div className="flex items-center justify-between text-zinc-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Collaboration</span>
              <Users size={18} className="text-rose-400" />
            </div>
            <div className="text-3xl font-bold mt-2 text-white">Active</div>
            <div className="text-xs text-zinc-400 mt-1">Shared workspace scope</div>
          </Card>
        </div>

        {/* Dashboard Split Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Recent Documents Column */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center">
              <FileText size={18} className="mr-2 text-indigo-400" /> Project Specifications
            </h2>
            <div className="bg-zinc-950/40 border border-zinc-900 rounded-xl divide-y divide-zinc-900">
              {recent_documents.map((doc) => (
                <div key={doc.id} className="p-4 flex items-center justify-between hover:bg-zinc-900/30 transition">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-indigo-950/30 border border-indigo-900/50 rounded-lg text-indigo-400">
                      <FileText size={16} />
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white">{doc.name}</div>
                      <div className="text-xs text-zinc-500 mt-0.5">{doc.category} • {(doc.file_size / 1024).toFixed(1)} KB</div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" href="/documents">
                    Manage
                  </Button>
                </div>
              ))}
              {recent_documents.length === 0 && (
                <div className="p-8 text-center text-zinc-500 text-sm">
                  No documents linked to this project roadmap.
                </div>
              )}
            </div>
          </div>

          {/* Activity Timeline Column */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-white flex items-center">
              <Activity size={18} className="mr-2 text-rose-400" /> Recent Activity
            </h2>
            <div className="bg-zinc-950/40 border border-zinc-900 rounded-xl p-4 space-y-4">
              {recent_activity.map((act) => (
                <div key={act.id} className="flex space-x-3 text-xs">
                  <div className="relative flex flex-col items-center">
                    <div className="h-2 w-2 rounded-full bg-rose-500 mt-1.5" />
                    <div className="flex-1 w-px bg-zinc-900 my-1" />
                  </div>
                  <div className="flex-1">
                    <div className="text-zinc-200">{act.description}</div>
                    <div className="text-[10px] text-zinc-500 mt-1">
                      {new Date(act.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
              {recent_activity.length === 0 && (
                <div className="py-8 text-center text-zinc-500 text-sm">
                  No activities logged yet.
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
