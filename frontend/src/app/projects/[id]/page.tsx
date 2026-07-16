'use client';

import * as React from 'react';
import { useParams } from 'next/navigation';
import { 
  Calendar, FileText, Activity, AlertCircle, RefreshCw, 
  Settings, Users, BarChart3, Database, ShieldAlert, 
  ChevronRight, Play, XOctagon, CheckCircle2, Loader2, Info
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

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
    generation_status?: string | null;
    generation_progress?: number | null;
    workflow_id?: string | null;
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

const STAGES = ["discovery", "requirements", "planning", "roadmap", "engineering", "reports"];

const STAGE_DETAILS = {
  discovery: { label: 'Product Discovery & Audit', desc: 'Analyzing startup feasibility, running SWOT & PESTLE frameworks.' },
  requirements: { label: 'Requirements Engineering', desc: 'Generating Product Requirements Document (PRD) and sprint user stories.' },
  planning: { label: 'Sprint & Resource Planning', desc: 'Estimating backlogs, scheduling allocations, and running simulations.' },
  roadmap: { label: 'Product Roadmap & Budgeting', desc: 'Establishing 12-month release milestones and capital forecasts.' },
  engineering: { label: 'System Design & API Specs', desc: 'Drafting microservices system architecture and OpenAPI endpoint models.' },
  reports: { label: 'Executive Intelligence Reports', desc: 'Assembling strategic advisory reviews for CEO, CTO, and COO.' },
};

export default function ProjectDashboardPage() {
  const { id: projectId } = useParams();
  const { activeWorkspace } = useAuth();
  
  const [data, setData] = React.useState<DashboardStats | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [errorMsg, setErrorMsg] = React.useState('');
  
  // Orchestrator State
  const [workflowDetails, setWorkflowDetails] = React.useState<any>(null);
  const [isTriggering, setIsTriggering] = React.useState(false);
  const [showTelemetryModal, setShowTelemetryModal] = React.useState(false);

  const fetchDashboard = React.useCallback(async () => {
    if (!activeWorkspace || !projectId) return;
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

  const fetchWorkflowDetails = React.useCallback(async (wfId: string) => {
    try {
      const details = await apiService.get<any>(`/orchestrator/status/${wfId}`);
      setWorkflowDetails(details);
    } catch (e) {
      console.error('Failed to load workflow details:', e);
    }
  }, []);

  React.useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  React.useEffect(() => {
    if (data?.project?.workflow_id) {
      fetchWorkflowDetails(data.project.workflow_id);
    }
  }, [data?.project?.workflow_id, fetchWorkflowDetails]);

  // Connect to SSE stream
  React.useEffect(() => {
    if (!data?.project?.id) return;
    const status = data.project.generation_status;
    if (!status || status === 'completed') return;

    const projectId = data.project.id;
    const workflowId = data.project.workflow_id;

    let active = true;
    const controller = new AbortController();

    async function listenToStream() {
      try {
        const token = localStorage.getItem('token') || '';
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/orchestrator/stream/${projectId}`,
          {
            signal: controller.signal,
            headers: {
              'Authorization': `Bearer ${token}`
            }
          }
        );

        if (!response.ok) {
          throw new Error('Failed to connect to stream');
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder('utf-8');
        if (!reader) return;

        while (active) {
          const { value, done } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const payload = JSON.parse(line.slice(6));
                
                // Update local state with real-time progress
                setData(prev => {
                  if (!prev) return prev;
                  return {
                    ...prev,
                    project: {
                      ...prev.project,
                      generation_status: payload.status,
                      generation_progress: payload.progress,
                      current_stage: payload.current_stage
                    }
                  };
                });
                
                if (workflowId) {
                  fetchWorkflowDetails(workflowId);
                }

                // If completed, refresh the whole dashboard to show new documents
                if (payload.status === 'completed') {
                  fetchDashboard();
                }
              } catch (e) {
                // Ignore parsing errors
              }
            }
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          // Fallback to active polling on network/SSE errors
          const interval = setInterval(() => {
            if (active) {
              fetchDashboard();
              if (workflowId) {
                fetchWorkflowDetails(workflowId);
              }
            }
          }, 4000);
          return () => clearInterval(interval);
        }
      }
    }

    listenToStream();

    return () => {
      active = false;
      controller.abort();
    };
  }, [data?.project?.id, data?.project?.generation_status, data?.project?.workflow_id, fetchDashboard, fetchWorkflowDetails]);

  // Handlers
  const handleTriggerOrchestrator = async () => {
    if (!data?.project || !activeWorkspace) return;
    setIsTriggering(true);
    try {
      const payload = {
        project_id: data.project.id,
        workspace_id: activeWorkspace.id,
        name: data.project.name,
        description: data.project.description || '',
      };
      const res = await apiService.post<any>('/orchestrator/trigger', payload);
      setData(prev => prev ? { ...prev, project: { ...prev.project, generation_status: 'processing', workflow_id: res.id } } : null);
      fetchWorkflowDetails(res.id);
    } catch (err: any) {
      alert(err.message || 'Failed to start AI workflow.');
    } finally {
      setIsTriggering(false);
    }
  };

  const handleCancel = async () => {
    if (!data?.project?.workflow_id) return;
    try {
      await apiService.post(`/orchestrator/cancel/${data.project.workflow_id}`, {});
      fetchDashboard();
    } catch (err: any) {
      alert(err.message || 'Failed to cancel workflow.');
    }
  };

  const handleRetry = async () => {
    if (!data?.project?.workflow_id) return;
    try {
      await apiService.post(`/orchestrator/retry/${data.project.workflow_id}`, {});
      fetchDashboard();
    } catch (err: any) {
      alert(err.message || 'Failed to retry workflow.');
    }
  };

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

  // Status mapping helper
  const getStageStatus = (stage: string) => {
    if (workflowDetails?.steps) {
      const step = workflowDetails.steps.find((s: any) => s.agent_name === stage);
      if (step) return step.status; // running, completed, failed, cancelled
    }
    
    // Fallback logic
    const currentIndex = STAGES.indexOf(project.generation_status === 'processing' || project.generation_status === 'pending' ? (project.generation_status || 'discovery') : '');
    const stageIndex = STAGES.indexOf(stage);
    
    if (project.generation_status === 'failed' && stageIndex === currentIndex) return 'failed';
    if (project.generation_status === 'cancelled' && stageIndex === currentIndex) return 'cancelled';
    if (stageIndex < currentIndex) return 'completed';
    if (stageIndex === currentIndex) return 'running';
    return 'pending';
  };

  // Usage telemetry aggregation
  const totalTokens = workflowDetails?.steps?.reduce((acc: number, s: any) => acc + (s.total_tokens || 0), 0) || 0;
  const totalCost = workflowDetails?.steps?.reduce((acc: number, s: any) => acc + (s.estimated_cost || 0), 0) || 0;
  const totalTime = workflowDetails?.steps?.reduce((acc: number, s: any) => acc + (s.execution_time || 0), 0) || 0;

  // Check if orchestrator is currently active/running/failed
  const isGenerationActive = project.generation_status && ['pending', 'processing', 'failed', 'cancelled'].includes(project.generation_status);

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
                project.generation_status === 'processing' ? 'bg-blue-950/40 border border-blue-800 text-blue-400 animate-pulse' :
                project.generation_status === 'failed' ? 'bg-red-950/40 border border-red-900 text-red-400' :
                project.generation_status === 'cancelled' ? 'bg-amber-950/40 border border-amber-900 text-amber-400' :
                project.status === 'Planning' ? 'bg-emerald-950/30 border border-emerald-900/50 text-emerald-400' :
                'bg-zinc-900 border border-zinc-800 text-zinc-400'
              }`}>
                {project.generation_status && project.generation_status !== 'completed' 
                  ? `AI Generating: ${project.generation_status}` 
                  : project.status
                }
              </span>
            </div>
            <p className="text-zinc-400 text-sm mt-2 max-w-2xl">{project.description || 'No description provided.'}</p>
          </div>
          <div className="flex items-center space-x-2">
            {!project.generation_status && (
              <Button variant="primary" onClick={handleTriggerOrchestrator} disabled={isTriggering}>
                {isTriggering ? <Loader2 size={14} className="mr-2 animate-spin" /> : <Play size={14} className="mr-2" />}
                Run Master AI Orchestrator
              </Button>
            )}
            {project.generation_status === 'completed' && (
              <Button variant="outline" onClick={() => setShowTelemetryModal(true)}>
                <BarChart3 size={14} className="mr-2 text-indigo-400" />
                AI Usage Report
              </Button>
            )}
            <Button variant="outline" href={`/projects/${project.id}/settings`}>
              <Settings size={14} className="mr-2" /> Settings
            </Button>
          </div>
        </div>

        {/* Real-time AI Generation HUD console */}
        <AnimatePresence mode="wait">
          {isGenerationActive && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.4 }}
            >
              <Card className="border border-zinc-800 bg-zinc-950/70 backdrop-blur-md overflow-hidden shadow-2xl">
                <div className="p-6 border-b border-zinc-900 flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
                  <div>
                    <h2 className="text-lg font-bold text-white flex items-center">
                      <RefreshCw size={18} className={`mr-2 text-indigo-500 ${project.generation_status === 'processing' ? 'animate-spin' : ''}`} />
                      Autonomous Master AI Product Orchestrator
                    </h2>
                    <p className="text-zinc-400 text-xs mt-1">Executing sequential multi-agent product construction workflows.</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {project.generation_status === 'processing' && (
                      <Button variant="outline" size="sm" onClick={handleCancel} className="border-red-950 bg-red-950/10 text-red-400 hover:bg-red-950/20">
                        <XOctagon size={12} className="mr-1.5" /> Cancel Execution
                      </Button>
                    )}
                    {['failed', 'cancelled'].includes(project.generation_status || '') && (
                      <Button variant="primary" size="sm" onClick={handleRetry}>
                        <RefreshCw size={12} className="mr-1.5" /> Resume From Checkpoint
                      </Button>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 p-6">
                  {/* Progress panel */}
                  <div className="lg:col-span-3 space-y-6">
                    <div>
                      <div className="flex justify-between items-center text-xs mb-2">
                        <span className="text-zinc-400 font-medium">Generation Lifecycle Progress</span>
                        <span className="text-white font-bold">{Math.round((project.generation_progress || 0) * 100)}%</span>
                      </div>
                      <div className="w-full bg-zinc-900 rounded-full h-2 overflow-hidden border border-zinc-800/80">
                        <motion.div 
                          className="bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-500 h-full rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${(project.generation_progress || 0) * 100}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>

                    {/* Step Timeline checklist */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {STAGES.map((stage, idx) => {
                        const status = getStageStatus(stage);
                        const details = STAGE_DETAILS[stage as keyof typeof STAGE_DETAILS];
                        
                        return (
                          <div 
                            key={stage} 
                            className={`p-4 border rounded-xl flex items-start space-x-3 transition duration-300 ${
                              status === 'running' ? 'bg-indigo-950/10 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.05)]' :
                              status === 'completed' ? 'bg-zinc-950/30 border-emerald-900/30' :
                              status === 'failed' ? 'bg-red-950/10 border-red-900/50' :
                              status === 'cancelled' ? 'bg-amber-950/10 border-amber-900/50' :
                              'bg-zinc-950/20 border-zinc-900/50 opacity-60'
                            }`}
                          >
                            <div className="mt-1">
                              {status === 'completed' && <CheckCircle2 size={16} className="text-emerald-500" />}
                              {status === 'running' && <Loader2 size={16} className="text-indigo-400 animate-spin" />}
                              {status === 'pending' && <div className="h-4 w-4 rounded-full border-2 border-zinc-800 flex items-center justify-center text-[10px] text-zinc-500 font-bold">{idx + 1}</div>}
                              {status === 'failed' && <AlertCircle size={16} className="text-red-500" />}
                              {status === 'cancelled' && <XOctagon size={16} className="text-amber-500" />}
                            </div>
                            <div className="flex-1">
                              <h3 className={`text-sm font-bold ${
                                status === 'completed' ? 'text-zinc-200' :
                                status === 'running' ? 'text-indigo-300' :
                                status === 'failed' ? 'text-red-400' :
                                status === 'cancelled' ? 'text-amber-400' :
                                'text-zinc-500'
                              }`}>
                                {details.label}
                              </h3>
                              <p className="text-zinc-400 text-xs mt-0.5 leading-relaxed">{details.desc}</p>
                              
                              {/* Display telemetry metadata for complete stages */}
                              {workflowDetails?.steps?.find((s: any) => s.agent_name === stage) && (
                                <div className="flex items-center space-x-3 text-[10px] text-zinc-500 mt-2 font-mono">
                                  <span>{(workflowDetails.steps.find((s: any) => s.agent_name === stage).total_tokens / 1000).toFixed(1)}k tokens</span>
                                  <span>{workflowDetails.steps.find((s: any) => s.agent_name === stage).execution_time.toFixed(1)}s</span>
                                  <span>${workflowDetails.steps.find((s: any) => s.agent_name === stage).estimated_cost.toFixed(3)}</span>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Telemetry sidebar */}
                  <div className="bg-zinc-950 border border-zinc-900 rounded-xl p-5 space-y-4 flex flex-col justify-between">
                    <div>
                      <h3 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider mb-3">AI Agent Telemetry</h3>
                      <div className="space-y-4">
                        <div>
                          <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Total LLM Tokens</div>
                          <div className="text-xl font-bold text-white mt-0.5">{(totalTokens / 1000).toFixed(1)}k tokens</div>
                        </div>
                        <div>
                          <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Accumulated Budget</div>
                          <div className="text-xl font-bold text-emerald-400 mt-0.5">${totalCost.toFixed(3)} USD</div>
                        </div>
                        <div>
                          <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Total Execution Time</div>
                          <div className="text-xl font-bold text-white mt-0.5">{totalTime.toFixed(1)}s</div>
                        </div>
                      </div>
                    </div>
                    {project.generation_status === 'failed' && workflowDetails?.failure_reason && (
                      <div className="p-3 bg-red-950/20 border border-red-900/50 rounded-lg text-[10px] text-red-400 flex items-start space-x-2">
                        <AlertCircle size={14} className="mt-0.5 shrink-0" />
                        <span className="line-clamp-4">{workflowDetails.failure_reason}</span>
                      </div>
                    )}
                    <div className="text-[10px] text-zinc-500 flex items-center space-x-1.5 p-2 bg-zinc-900/50 rounded-lg">
                      <Info size={12} className="text-indigo-400 shrink-0" />
                      <span>Data becomes visible below as soon as each phase completes.</span>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Stats Grid Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="p-6 bg-zinc-950/40 border-zinc-900 hover:border-zinc-800 transition">
            <div className="flex items-center justify-between text-zinc-500">
              <span className="text-xs font-semibold uppercase tracking-wider">Specifications</span>
              <FileText size={18} className="text-indigo-400" />
            </div>
            <div className="text-3xl font-bold mt-2 text-white">{stats.document_count}</div>
            <div className="text-xs text-zinc-400 mt-1">Total documents generated</div>
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
                  {project.generation_status === 'processing' 
                    ? 'Documents will appear here as soon as their generation stage completes...'
                    : 'No documents linked to this project roadmap.'
                  }
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

      {/* Telemetry Report Modal */}
      {showTelemetryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm">
          <motion.div 
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-full max-w-2xl bg-zinc-950 border border-zinc-900 rounded-2xl p-6 shadow-2xl"
          >
            <div className="flex justify-between items-center pb-4 border-b border-zinc-900">
              <h2 className="text-lg font-bold text-white flex items-center">
                <BarChart3 size={18} className="mr-2 text-indigo-500" />
                AI Generation Telemetry & Usage Report
              </h2>
              <button onClick={() => setShowTelemetryModal(false)} className="text-zinc-500 hover:text-white transition">
                &times;
              </button>
            </div>
            
            <div className="py-6 space-y-6 max-h-[60vh] overflow-y-auto">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-4 bg-zinc-900/40 rounded-xl border border-zinc-900">
                  <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Total LLM Tokens</div>
                  <div className="text-xl font-bold text-white mt-1">{(totalTokens / 1000).toFixed(1)}k</div>
                </div>
                <div className="p-4 bg-zinc-900/40 rounded-xl border border-zinc-900">
                  <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Estimated Cost</div>
                  <div className="text-xl font-bold text-emerald-400 mt-1">${totalCost.toFixed(3)}</div>
                </div>
                <div className="p-4 bg-zinc-900/40 rounded-xl border border-zinc-900">
                  <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">Execution Time</div>
                  <div className="text-xl font-bold text-white mt-1">{totalTime.toFixed(1)}s</div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Agent Breakdown</h3>
                <div className="border border-zinc-900 rounded-xl overflow-hidden divide-y divide-zinc-900">
                  {workflowDetails?.steps?.map((step: any) => (
                    <div key={step.id} className="p-3 flex justify-between items-center text-xs bg-zinc-950">
                      <div>
                        <div className="font-bold text-zinc-200 uppercase tracking-wider">{step.agent_name}</div>
                        <div className="text-zinc-500 text-[10px] mt-0.5">Model: {step.model_used || 'N/A'}</div>
                      </div>
                      <div className="text-right space-y-1 font-mono text-[11px]">
                        <div className="text-zinc-300">{(step.total_tokens / 1000).toFixed(1)}k tokens</div>
                        <div className="text-zinc-500">{step.execution_time.toFixed(1)}s • ${step.estimated_cost.toFixed(3)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4 border-t border-zinc-900/60">
              <Button variant="primary" onClick={() => setShowTelemetryModal(false)}>Close Report</Button>
            </div>
          </motion.div>
        </div>
      )}

    </AppShell>
  );
}
