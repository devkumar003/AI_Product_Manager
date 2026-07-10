'use client';

import * as React from 'react';
import { FolderKanban, FileText, Users, Activity, CheckCircle2, AlertCircle, RefreshCw, Clock } from 'lucide-react';

import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { checkBackendHealth, HealthStatus, apiService } from '@/lib/api';

import { useAuth } from '@/context/AuthContext';
import { Loading } from '@/components/ui/loading';
import { SetupWizard } from '@/components/layout/SetupWizard';
import { AgentThoughtVisualizer, ThoughtStep } from '@/components/ui/agent-thought-visualizer';

interface ProjectItem {
  id: string;
  name: string;
  status: string;
  slug: string;
}

interface DocItem {
  id: string;
  name: string;
  category: string;
}

interface ActivityItem {
  id: string;
  action: string;
  description: string;
  created_at: string;
}

export default function DashboardPage() {
  const { isLoading, isAuthenticated, organizations, activeWorkspace, refreshUser } = useAuth();
  const [health, setHealth] = React.useState<HealthStatus | null>(null);
  const [healthStatus, setHealthStatus] = React.useState<'loading' | 'healthy' | 'error'>('loading');

  // Dynamic Workspace Data states
  const [projects, setProjects] = React.useState<ProjectItem[]>([]);
  const [docs, setDocs] = React.useState<DocItem[]>([]);
  const [activities, setActivities] = React.useState<ActivityItem[]>([]);
  const [isDataLoading, setIsDataLoading] = React.useState(false);

  // AI Hivemind reasoning steps state
  const [isSimulating, setIsSimulating] = React.useState(true);
  const [aiSteps, setAiSteps] = React.useState<ThoughtStep[]>([
    {
      id: '1',
      agentName: 'AI Product Manager (Chief CPO)',
      roleIcon: 'brain',
      status: 'completed',
      message: 'Decomposed strategic product vision into 4 core epics and 18 user stories.',
      timestamp: 'Just now',
      details: [
        'Epic 1: Autonomous Multi-Agent Routing Engine',
        'Epic 2: Self-Healing JSON Syntax Synthesis',
        'Epic 3: Bi-Directional Git & Code Scaffolding',
        'Epic 4: Enterprise RBAC & Security Audit Logs',
      ],
      metrics: { model: 'gpt-4o', latencyMs: 1240, tokensUsed: 3420 },
    },
    {
      id: '2',
      agentName: 'PRD Formulation Specialist',
      roleIcon: 'layers',
      status: 'completed',
      message: 'Formulated acceptance criteria and Pydantic schema constraints.',
      timestamp: '2s ago',
      details: [
        'Validated 100% Pydantic schema compliance via automated self-healing retry loop.',
        'Generated comprehensive acceptance criteria for each user story.',
      ],
      metrics: { model: 'claude-3-5-sonnet', latencyMs: 890, tokensUsed: 1850 },
    },
    {
      id: '3',
      agentName: 'Technical Architect Agent',
      roleIcon: 'cpu',
      status: 'active',
      message: 'Synthesizing PostgreSQL DDL schemas and SQLAlchemy ORM models...',
      timestamp: 'Active',
      details: [
        'Mapping relational foreign keys for workspace isolation...',
        'Checking index optimization and vector embedding storage...',
      ],
      metrics: { model: 'o1-preview', latencyMs: 3100, tokensUsed: 5120 },
    },
    {
      id: '4',
      agentName: 'PMO Risk & Budget Simulator',
      roleIcon: 'shield',
      status: 'pending',
      message: 'Waiting for schema completion to simulate best/worst case timelines.',
    },
  ]);

  // Fetch health check
  React.useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await checkBackendHealth();
        setHealth(data);
        setHealthStatus('healthy');
      } catch {
        setHealthStatus('error');
      }
    };

    if (isAuthenticated && organizations.length > 0) {
      fetchHealth();
    }
  }, [isAuthenticated, organizations]);

  // Fetch workspace statistics and logs
  const fetchWorkspaceData = React.useCallback(async () => {
    if (!activeWorkspace) return;
    setIsDataLoading(true);
    try {
      const projectsList = await apiService.get<ProjectItem[]>(`/projects/${activeWorkspace.id}`);
      setProjects(projectsList);

      const docsList = await apiService.get<DocItem[]>(`/documents/${activeWorkspace.id}`);
      setDocs(docsList);

      const activitiesList = await apiService.get<ActivityItem[]>(`/activities/${activeWorkspace.id}`);
      setActivities(activitiesList);
    } catch (err) {
      console.warn('Failed to load workspace data for dashboard:', err);
    } finally {
      setIsDataLoading(false);
    }
  }, [activeWorkspace]);

  React.useEffect(() => {
    fetchWorkspaceData();
  }, [fetchWorkspaceData]);

  if (isLoading) {
    return <Loading fullScreen />;
  }

  if (!isAuthenticated) {
    return null;
  }

  if (organizations.length === 0) {
    return <SetupWizard onComplete={refreshUser} />;
  }

  const stats = [
    { name: 'Active Projects', value: String(projects.length), icon: FolderKanban, change: 'From current workspace' },
    { name: 'Spec Documents', value: String(docs.length), icon: FileText, change: 'Across all roadmaps' },
    { name: 'Workspace Activities', value: String(activities.length), icon: Activity, change: 'Timeline actions' },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header section with Breadcrumbs */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Dashboard' }]} />
            <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">
              Workspace Overview
            </h1>
          </div>

          {/* Backend Connection status */}
          <div className="flex items-center space-x-2 bg-zinc-900 border border-zinc-800 rounded-full px-4 py-1.5 text-xs">
            <span className="text-zinc-400">Backend API:</span>
            {healthStatus === 'loading' && (
              <span className="flex items-center text-amber-400 font-semibold animate-pulse">
                <Activity size={12} className="mr-1 animate-spin" /> Checking...
              </span>
            )}
            {healthStatus === 'healthy' && (
              <span className="flex items-center text-emerald-400 font-semibold">
                <CheckCircle2 size={12} className="mr-1" /> Healthy (v{health?.version})
              </span>
            )}
            {healthStatus === 'error' && (
              <span className="flex items-center text-red-400 font-semibold">
                <AlertCircle size={12} className="mr-1" /> Disconnected
              </span>
            )}
          </div>
        </div>

        {/* Workspace Alert */}
        {!activeWorkspace && (
          <div className="flex items-center space-x-3 p-4 bg-amber-950/20 border border-amber-900/50 rounded-xl text-amber-400 text-sm">
            <AlertCircle size={18} />
            <span>Please switch to or configure an active workspace to begin view tracking.</span>
          </div>
        )}

        {activeWorkspace && (
          <>
            {/* Dashboard Widgets */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {stats.map((stat, idx) => {
                const Icon = stat.icon;
                return (
                  <Card key={idx} className="hover:border-zinc-800 transition duration-300">
                    <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                      <CardTitle className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">
                        {stat.name}
                      </CardTitle>
                      <div className="h-8 w-8 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400">
                        <Icon size={16} />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-extrabold text-white">{stat.value}</div>
                      <p className="text-xs text-indigo-400 mt-1 font-medium">{stat.change}</p>
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* AI Hivemind Pipeline Visualizer */}
            <div className="my-6">
              <AgentThoughtVisualizer
                steps={aiSteps}
                isGenerating={isSimulating}
                onStepClick={(step) => {
                  if (step.status === 'active') {
                    setIsSimulating(false);
                    setAiSteps((prev) =>
                      prev.map((s) => (s.id === step.id ? { ...s, status: 'completed', message: 'Schema synthesis completed successfully!' } : s))
                    );
                  } else {
                    setIsSimulating(true);
                    setAiSteps((prev) =>
                      prev.map((s) => (s.id === '3' ? { ...s, status: 'active', message: 'Re-evaluating architecture against new constraints...' } : s))
                    );
                  }
                }}
              />
            </div>

            {/* Recent Work and System Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Projects Card */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle>Recent Projects</CardTitle>
                  <CardDescription>Your roadmap workspaces</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {projects.slice(0, 5).map((proj) => (
                    <div key={proj.id} className="flex items-center justify-between p-3 rounded-lg border border-zinc-900 bg-zinc-950/40 hover:bg-zinc-900/30 transition duration-200">
                      <div className="flex items-center space-x-3">
                        <div className="h-9 w-9 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-indigo-400 text-xs font-bold font-mono">
                          /{proj.slug.substring(0, 4)}
                        </div>
                        <div>
                          <h4 className="text-sm font-bold text-white leading-none">{proj.name}</h4>
                          <span className="text-[10px] text-zinc-500 font-medium">/{proj.slug}</span>
                        </div>
                      </div>
                      <span className={`text-[10px] px-2 py-1 rounded-full font-bold uppercase tracking-wider ${
                        proj.status === 'Completed' ? 'bg-emerald-950/30 border border-emerald-900/50 text-emerald-400' :
                        proj.status === 'Planning' ? 'bg-indigo-950/30 border border-indigo-900/50 text-indigo-400' :
                        'bg-zinc-900 border border-zinc-800 text-zinc-400'
                      }`}>
                        {proj.status}
                      </span>
                    </div>
                  ))}
                  {projects.length === 0 && (
                    <div className="text-center py-8 text-xs text-zinc-500">
                      No roadmaps created yet in this workspace.
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Activity Feed Card */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Clock size={16} className="mr-2 text-rose-400" /> Activity Timeline
                  </CardTitle>
                  <CardDescription>Workspace audit logs</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4 max-h-[350px] overflow-y-auto pr-1">
                  {activities.slice(0, 10).map((act) => (
                    <div key={act.id} className="flex space-x-3 text-xs">
                      <div className="relative flex flex-col items-center">
                        <div className="h-2 w-2 rounded-full bg-rose-500 mt-1.5" />
                        <div className="flex-1 w-px bg-zinc-900 my-1" />
                      </div>
                      <div className="flex-1">
                        <div className="text-zinc-300 leading-tight">{act.description}</div>
                        <div className="text-[10px] text-zinc-500 mt-1">
                          {new Date(act.created_at).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                  {activities.length === 0 && (
                    <div className="text-center py-8 text-xs text-zinc-500">
                      No activities logged yet.
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
