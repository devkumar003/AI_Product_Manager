'use client';

import * as React from 'react';
import {
  Target,
  Rocket,
  GitBranch,
  Play,
  Plus,
  Trash2,
  RefreshCw,
  CalendarDays,
  Sparkles,
  Zap,
} from 'lucide-react';

import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

// Types aligning with Backend schemas without 'any' to satisfy ESLint
interface Goal {
  id: string;
  name: string;
  description: string;
  type: string;
  status: string;
  progress: number;
  target_date?: string;
}

interface ObjectiveItem {
  name: string;
  metric: string;
  target: string;
}

interface MilestoneItem {
  name: string;
  phase: string;
  estimated_weeks: number;
  deliverables: string[];
}

interface DeliverableItem {
  artifact: string;
  description: string;
  audience: string;
}

interface ExecutionPlanItem {
  steps?: string[];
  risk_mitigation?: string[];
}

interface Mission {
  id: string;
  title: string;
  description: string;
  status: string;
  objectives: ObjectiveItem[];
  milestones: MilestoneItem[];
  deliverables: DeliverableItem[];
  execution_plan: ExecutionPlanItem;
}

interface PlanningItemMetadata {
  scheduled_start?: string;
  scheduled_end?: string;
  acceptance_criteria?: string;
  wireframe_suggestions?: string;
}

interface PlanningItem {
  id: string;
  type: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  estimated_hours: number;
  assigned_roles: string[];
  metadata_fields: PlanningItemMetadata | null;
}

interface Dependency {
  id: string;
  source_item_id: string;
  target_item_id: string;
  dependency_type: string;
}

interface TimelineScenario {
  duration_weeks?: number;
  key_assumptions?: string[];
  key_risks?: string[];
  expected_delivery_date?: string;
}

interface BudgetImpactScenario {
  best_case_cost?: number;
  average_case_cost?: number;
  worst_case_cost?: number;
  cost_breakdown?: string;
}

interface TimelineImpactScenario {
  delay_risk_score?: number;
  critical_path_bottlenecks?: string[];
}

interface Simulation {
  id: string;
  name: string;
  vision: string;
  best_case_timeline?: TimelineScenario;
  worst_case_timeline?: TimelineScenario;
  average_case_timeline?: TimelineScenario;
  budget_impact?: BudgetImpactScenario;
  timeline_impact?: TimelineImpactScenario;
  created_at?: string;
}

interface Analytics {
  accuracy_rate: number;
  completion_rate: number;
  execution_efficiency: number;
  total_delays_hours: number;
}

interface TemplateDefinition {
  name: string;
  description: string;
  items: unknown[];
}

export default function PlanningDashboard() {
  const { activeWorkspace } = useAuth();

  const [activeTab, setActiveTab] = React.useState<'goals' | 'backlog' | 'kanban' | 'dependencies' | 'simulations' | 'compressor' | 'resources' | 'analytics'>('goals');

  // Loading States
  const [isGoalsLoading, setIsGoalsLoading] = React.useState(false);
  const [isActionLoading, setIsActionLoading] = React.useState(false);

  // Data states
  const [goals, setGoals] = React.useState<Goal[]>([]);
  const [missions, setMissions] = React.useState<Mission[]>([]);
  const [backlogItems, setBacklogItems] = React.useState<PlanningItem[]>([]);
  const [dependencies, setDependencies] = React.useState<Dependency[]>([]);
  const [simulations, setSimulations] = React.useState<Simulation[]>([]);
  const [analytics, setAnalytics] = React.useState<Analytics | null>(null);
  const [costData, setCostData] = React.useState<any | null>(null);
  const [templates, setTemplates] = React.useState<Record<string, TemplateDefinition>>({});
  const [expandedItem, setExpandedItem] = React.useState<string | null>(null);
  const [generatingId, setGeneratingId] = React.useState<string | null>(null);

  const handleGenerateAcceptanceCriteria = async (itemId: string) => {
    if (!activeWorkspace) return;
    setGeneratingId(itemId);
    try {
      const data = await apiService.post<{ acceptance_criteria: string }>(
        `/planning/backlog/items/${itemId}/acceptance-criteria?workspace_id=${activeWorkspace.id}`
      );
      setBacklogItems(prev =>
        prev.map(item =>
          item.id === itemId
            ? {
                ...item,
                metadata_fields: {
                  ...item.metadata_fields,
                  acceptance_criteria: data.acceptance_criteria
                }
              }
            : item
        )
      );
    } catch (e) {
      console.error(e);
    } finally {
      setGeneratingId(null);
    }
  };

  const handleGenerateWireframe = async (itemId: string) => {
    if (!activeWorkspace) return;
    setGeneratingId(itemId);
    try {
      const data = await apiService.post<{ wireframe_suggestions: string }>(
        `/planning/backlog/items/${itemId}/wireframe?workspace_id=${activeWorkspace.id}`
      );
      setBacklogItems(prev =>
        prev.map(item =>
          item.id === itemId
            ? {
                ...item,
                metadata_fields: {
                  ...item.metadata_fields,
                  wireframe_suggestions: data.wireframe_suggestions
                }
              }
            : item
        )
      );
    } catch (e) {
      console.error(e);
    } finally {
      setGeneratingId(null);
    }
  };

  // Input states
  const [newGoalName, setNewGoalName] = React.useState('');
  const [newGoalDesc, setNewGoalDesc] = React.useState('');
  const [newGoalType, setNewGoalType] = React.useState('Product');
  const [newGoalTargetDate, setNewGoalTargetDate] = React.useState('');

  const [missionTitle, setMissionTitle] = React.useState('');
  const [selectedGoalIds, setSelectedGoalIds] = React.useState<string[]>([]);

  const [projectVision, setProjectVision] = React.useState('');
  const [simName, setSimName] = React.useState('');
  const [simVision, setSimVision] = React.useState('');

  const [compressText, setCompressText] = React.useState('');
  const [compressedResult, setCompressedResult] = React.useState('');

  // Fetch initial workspace specific planning data
  const loadWorkspaceData = React.useCallback(async () => {
    if (!activeWorkspace) return;
    setIsGoalsLoading(true);

    try {
      // 1. Fetch Goals
      const fetchedGoals = await apiService.get<Goal[]>(`/planning/goals?workspace_id=${activeWorkspace.id}`);
      setGoals(fetchedGoals);

      // 2. Fetch Missions
      const fetchedMissions = await apiService.get<Mission[]>(`/planning/missions?workspace_id=${activeWorkspace.id}`);
      setMissions(fetchedMissions);

      // 3. Fetch Backlog items
      const fetchedBacklog = await apiService.get<PlanningItem[]>(`/planning/backlog/items?workspace_id=${activeWorkspace.id}`);
      setBacklogItems(fetchedBacklog);

      // 4. Fetch Dependencies
      const fetchedDeps = await apiService.get<Dependency[]>(`/planning/dependencies?workspace_id=${activeWorkspace.id}`);
      setDependencies(fetchedDeps);

      // 5. Fetch Simulations
      const fetchedSims = await apiService.get<Simulation[]>(`/planning/simulations?workspace_id=${activeWorkspace.id}`);
      setSimulations(fetchedSims);

      // 6. Fetch Analytics
      const fetchedAnalytics = await apiService.get<Analytics>(`/planning/analytics/latest?workspace_id=${activeWorkspace.id}`);
      setAnalytics(fetchedAnalytics);

      // 7. Fetch Templates
      const fetchedTemplates = await apiService.get<Record<string, TemplateDefinition>>('/planning/intelligence/templates');
      setTemplates(fetchedTemplates);

      // 8. Fetch Cost Estimation
      const fetchedCosts = await apiService.post<any>(`/planning/intelligence/cost-estimation?workspace_id=${activeWorkspace.id}`).catch(() => null);
      if (fetchedCosts) setCostData(fetchedCosts);
    } catch (err) {
      console.warn('Failed to load workspace planning telemetry:', err);
    } finally {
      setIsGoalsLoading(false);
    }
  }, [activeWorkspace]);

  React.useEffect(() => {
    // Avoid synchronous state changes inside effect body
    const timeout = setTimeout(() => {
      loadWorkspaceData();
    }, 100);
    return () => clearTimeout(timeout);
  }, [loadWorkspaceData]);

  // Goal handlers
  const handleCreateGoal = async () => {
    if (!activeWorkspace || !newGoalName.trim()) return;
    setIsActionLoading(true);
    try {
      const payload: Record<string, unknown> = {
        name: newGoalName,
        description: newGoalDesc,
        type: newGoalType,
        progress: 0.0,
        status: 'Open',
      };
      if (newGoalTargetDate) {
        payload.target_date = new Date(newGoalTargetDate).toISOString();
      }
      await apiService.post(`/planning/goals?workspace_id=${activeWorkspace.id}`, payload);
      setNewGoalName('');
      setNewGoalDesc('');
      setNewGoalTargetDate('');
      // Reload
      const freshGoals = await apiService.get<Goal[]>(`/planning/goals?workspace_id=${activeWorkspace.id}`);
      setGoals(freshGoals);
    } catch (err) {
      console.error('Failed to create goal:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  const handleDeleteGoal = async (id: string) => {
    if (!activeWorkspace) return;
    try {
      await apiService.delete(`/planning/goals/${id}?workspace_id=${activeWorkspace.id}`);
      setGoals(goals.filter((g) => g.id !== id));
    } catch (err) {
      console.error('Failed to delete goal:', err);
    }
  };

  // Mission generators
  const handleGenerateMission = async () => {
    if (!activeWorkspace || !missionTitle.trim() || selectedGoalIds.length === 0) return;
    setIsActionLoading(true);
    try {
      await apiService.post(`/planning/missions?workspace_id=${activeWorkspace.id}`, {
        title: missionTitle,
        goal_ids: selectedGoalIds,
      });
      setMissionTitle('');
      setSelectedGoalIds([]);
      const freshMissions = await apiService.get<Mission[]>(`/planning/missions?workspace_id=${activeWorkspace.id}`);
      setMissions(freshMissions);
    } catch (err) {
      console.error('Failed to generate mission plan:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  // Backlog generators
  const handleGenerateBacklog = async () => {
    if (!activeWorkspace || !projectVision.trim()) return;
    setIsActionLoading(true);
    try {
      await apiService.post(`/planning/backlog/generate?workspace_id=${activeWorkspace.id}`, {
        vision: projectVision,
      });
      setProjectVision('');
      // Reload backlog & scheduler
      const freshBacklog = await apiService.get<PlanningItem[]>(`/planning/backlog/items?workspace_id=${activeWorkspace.id}`);
      setBacklogItems(freshBacklog);
      
      // Calculate analytics
      const fetchedAnalytics = await apiService.get<Analytics>(`/planning/analytics/latest?workspace_id=${activeWorkspace.id}`);
      setAnalytics(fetchedAnalytics);
    } catch (err) {
      console.error('Failed to decompose vision:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  // Templates applier
  const handleApplyTemplate = async (key: string) => {
    if (!activeWorkspace) return;
    setIsActionLoading(true);
    try {
      await apiService.post(`/planning/intelligence/templates/apply?workspace_id=${activeWorkspace.id}`, {
        template_key: key,
      });
      const freshBacklog = await apiService.get<PlanningItem[]>(`/planning/backlog/items?workspace_id=${activeWorkspace.id}`);
      setBacklogItems(freshBacklog);
    } catch (err) {
      console.error('Failed to apply template:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  // AI Dependency detectors
  const handleDetectDependencies = async () => {
    if (!activeWorkspace) return;
    setIsActionLoading(true);
    try {
      await apiService.post(`/planning/dependencies/detect?workspace_id=${activeWorkspace.id}`, {});
      const freshDeps = await apiService.get<Dependency[]>(`/planning/dependencies?workspace_id=${activeWorkspace.id}`);
      setDependencies(freshDeps);
    } catch (err) {
      console.error('Failed to detect dependencies:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  // Run AI Scheduler
  const handleRunScheduler = async () => {
    if (!activeWorkspace) return;
    setIsActionLoading(true);
    try {
      await apiService.post(`/planning/scheduler/schedule?workspace_id=${activeWorkspace.id}`, {});
      // Refresh backlog to get dates
      const freshBacklog = await apiService.get<PlanningItem[]>(`/planning/backlog/items?workspace_id=${activeWorkspace.id}`);
      setBacklogItems(freshBacklog);
    } catch (err) {
      console.error('Failed to schedule tasks:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  // Run Scenario simulations
  const handleRunSimulation = async () => {
    if (!activeWorkspace || !simName.trim() || !simVision.trim()) return;
    setIsActionLoading(true);
    try {
      await apiService.post(`/planning/simulations?workspace_id=${activeWorkspace.id}`, {
        name: simName,
        vision: simVision,
      });
      setSimName('');
      setSimVision('');
      const freshSims = await apiService.get<Simulation[]>(`/planning/simulations?workspace_id=${activeWorkspace.id}`);
      setSimulations(freshSims);
    } catch (err) {
      console.error('Failed to run simulation:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  // Semantic compressor
  const handleCompressText = async () => {
    if (!compressText.trim()) return;
    setIsActionLoading(true);
    try {
      const res = await apiService.post<{ compressed: string }>('/planning/compress/text', {
        text: compressText,
        target_summary_words: 200,
      });
      setCompressedResult(res.compressed);
    } catch (err) {
      console.error('Failed to compress text:', err);
    } finally {
      setIsActionLoading(false);
    }
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="text-center py-20">
          <Target className="mx-auto text-zinc-600 mb-4 animate-bounce" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view your autonomous planning engine.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Navigation Breadcrumb and Title */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Autonomous Planning Engine' }]} />
            <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1 flex items-center">
              <Rocket className="mr-2 text-indigo-400" /> Autonomous Planning Engine
            </h1>
          </div>
          <button
            onClick={loadWorkspaceData}
            className="flex items-center space-x-2 bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white px-4 py-2 rounded-lg text-sm transition duration-150"
          >
            <RefreshCw size={16} className={isGoalsLoading ? 'animate-spin' : ''} />
            <span>Reload Telemetry</span>
          </button>
        </div>

        {/* Telemetry Stats Panel */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-zinc-950/40 border border-zinc-900">
            <CardHeader className="pb-2">
              <CardDescription className="text-xs uppercase font-semibold text-zinc-500">Planning Accuracy</CardDescription>
              <CardTitle className="text-2xl font-black text-white">{analytics?.accuracy_rate ? `${analytics.accuracy_rate}%` : '100%'}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-zinc-950/40 border border-zinc-900">
            <CardHeader className="pb-2">
              <CardDescription className="text-xs uppercase font-semibold text-zinc-500">Completion Rate</CardDescription>
              <CardTitle className="text-2xl font-black text-emerald-400">{analytics?.completion_rate ? `${analytics.completion_rate.toFixed(1)}%` : '0.0%'}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-zinc-950/40 border border-zinc-900">
            <CardHeader className="pb-2">
              <CardDescription className="text-xs uppercase font-semibold text-zinc-500">Execution Efficiency</CardDescription>
              <CardTitle className="text-2xl font-black text-indigo-400">{analytics?.execution_efficiency ? `${analytics.execution_efficiency.toFixed(1)}%` : '0.0%'}</CardTitle>
            </CardHeader>
          </Card>
          <Card className="bg-zinc-950/40 border border-zinc-900">
            <CardHeader className="pb-2">
              <CardDescription className="text-xs uppercase font-semibold text-zinc-500">Delays Incurred</CardDescription>
              <CardTitle className="text-2xl font-black text-rose-400">{analytics?.total_delays_hours ? `${analytics.total_delays_hours} hrs` : '0 hrs'}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Tab Controls */}
        <div className="flex space-x-1 border-b border-zinc-900 pb-px">
          {(['goals', 'backlog', 'kanban', 'dependencies', 'simulations', 'compressor', 'resources', 'analytics'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2.5 text-sm font-semibold border-b-2 transition-all duration-200 capitalize ${
                activeTab === tab
                  ? 'border-indigo-500 text-indigo-400 font-bold'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab === 'resources' ? 'Resource Plan' : tab === 'analytics' ? 'Sprint Analytics' : tab}
            </button>
          ))}
        </div>

        {/* TAB 1: Goals and Mission Planner */}
        {activeTab === 'goals' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
            {/* Create Goal Form */}
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Add Workspace Goal</CardTitle>
                <CardDescription>Target objective to steer product planning</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1">
                  <label className="text-xs text-zinc-400 font-semibold">Goal Name</label>
                  <input
                    type="text"
                    value={newGoalName}
                    onChange={(e) => setNewGoalName(e.target.value)}
                    placeholder="e.g. Expand subscription features"
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-zinc-400 font-semibold">Goal Description</label>
                  <textarea
                    value={newGoalDesc}
                    onChange={(e) => setNewGoalDesc(e.target.value)}
                    placeholder="Add details, metrics, or key results..."
                    rows={3}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs text-zinc-400 font-semibold">Type</label>
                    <select
                      value={newGoalType}
                      onChange={(e) => setNewGoalType(e.target.value)}
                      className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                    >
                      <option value="Business">Business</option>
                      <option value="Product">Product</option>
                      <option value="Technical">Technical</option>
                      <option value="Sprint">Sprint</option>
                      <option value="Release">Release</option>
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-zinc-400 font-semibold">Target Date</label>
                    <input
                      type="date"
                      value={newGoalTargetDate}
                      onChange={(e) => setNewGoalTargetDate(e.target.value)}
                      className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                    />
                  </div>
                </div>
                <button
                  onClick={handleCreateGoal}
                  disabled={isActionLoading || !newGoalName.trim()}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg p-2.5 text-sm font-semibold flex items-center justify-center space-x-2 transition active:scale-95 disabled:opacity-50"
                >
                  <Plus size={16} />
                  <span>Create Goal</span>
                </button>
              </CardContent>
            </Card>

            {/* List Goals Board */}
            <Card className="bg-zinc-950/20 border border-zinc-900 lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Goal Board</CardTitle>
                <CardDescription>Track status and progress metrics</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {goals.map((g) => (
                  <div key={g.id} className="p-4 border border-zinc-900 bg-zinc-950/50 rounded-xl flex items-center justify-between">
                    <div className="space-y-1 flex-1 pr-4">
                      <div className="flex items-center space-x-2">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase ${
                          g.type === 'Business' ? 'bg-emerald-950/30 border-emerald-900/50 text-emerald-400' :
                          g.type === 'Technical' ? 'bg-amber-950/30 border-amber-900/50 text-amber-400' :
                          'bg-indigo-950/30 border-indigo-900/50 text-indigo-400'
                        }`}>
                          {g.type}
                        </span>
                        <h4 className="text-sm font-bold text-white leading-none">{g.name}</h4>
                      </div>
                      <p className="text-xs text-zinc-400 line-clamp-1">{g.description}</p>
                      
                      {/* Progress Bar */}
                      <div className="flex items-center space-x-2 mt-2">
                        <div className="flex-1 h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                          <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${g.progress}%` }} />
                        </div>
                        <span className="text-[10px] text-zinc-500 font-bold">{g.progress}%</span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleDeleteGoal(g.id)}
                      className="text-zinc-600 hover:text-red-400 p-2 rounded-lg transition"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
                {goals.length === 0 && (
                  <div className="text-center py-12 text-xs text-zinc-600">No goals added to this workspace.</div>
                )}
              </CardContent>
            </Card>

            {/* Mission Board */}
            <Card className="bg-zinc-950/20 border border-zinc-900 lg:col-span-3">
              <CardHeader>
                <CardTitle className="text-lg">Mission Planner</CardTitle>
                <CardDescription>Synthesize multiple goals into a structured step-by-step Execution Plan</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Generation fields */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
                  <div className="space-y-1">
                    <label className="text-xs text-zinc-400 font-semibold">Mission Plan Title</label>
                    <input
                      type="text"
                      value={missionTitle}
                      onChange={(e) => setMissionTitle(e.target.value)}
                      placeholder="e.g. Q3 Scalability Sprint Plan"
                      className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-xs text-zinc-400 font-semibold">Select Associated Goals</label>
                    <div className="flex flex-wrap gap-1 p-2 border border-zinc-800 rounded-lg bg-zinc-900 min-h-[42px] max-h-24 overflow-y-auto">
                      {goals.map((g) => {
                        const isSelected = selectedGoalIds.includes(g.id);
                        return (
                          <button
                            key={g.id}
                            onClick={() => {
                              if (isSelected) {
                                setSelectedGoalIds(selectedGoalIds.filter(id => id !== g.id));
                              } else {
                                setSelectedGoalIds([...selectedGoalIds, g.id]);
                              }
                            }}
                            className={`text-[10px] px-2 py-0.5 rounded-full border transition ${
                              isSelected
                                ? 'bg-indigo-600/20 border-indigo-500/50 text-indigo-400 font-bold'
                                : 'bg-zinc-950 border-zinc-850 text-zinc-500 hover:text-zinc-300'
                            }`}
                          >
                            {g.name}
                          </button>
                        );
                      })}
                      {goals.length === 0 && <span className="text-[10px] text-zinc-600 italic">No goals to link</span>}
                    </div>
                  </div>
                  <button
                    onClick={handleGenerateMission}
                    disabled={isActionLoading || !missionTitle.trim() || selectedGoalIds.length === 0}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg p-2.5 text-sm font-semibold flex items-center justify-center space-x-2 transition active:scale-95 disabled:opacity-50"
                  >
                    <Sparkles size={16} />
                    <span>Run AI Mission Planner</span>
                  </button>
                </div>

                {/* Generated Missions list */}
                <div className="space-y-6">
                  {missions.map((m) => (
                    <div key={m.id} className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-xl space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-bold text-white text-base">{m.title}</h4>
                        <span className="text-[10px] uppercase font-bold bg-indigo-950/40 border border-indigo-900/50 text-indigo-400 px-3 py-1 rounded-full">{m.status}</span>
                      </div>
                      
                      {/* Milestones grid */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg space-y-2">
                          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Objectives</span>
                          <ul className="text-xs text-zinc-400 space-y-1.5">
                            {m.objectives?.map((o, idx) => (
                              <li key={idx} className="flex items-center space-x-1.5">
                                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
                                <span>{o.name}: <strong>{o.target}</strong></span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg space-y-2">
                          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Milestones</span>
                          <ul className="text-xs text-zinc-400 space-y-1.5">
                            {m.milestones?.map((mi, idx) => (
                              <li key={idx} className="flex items-center space-x-1.5">
                                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                                <span>{mi.name} ({mi.estimated_weeks} wks)</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg space-y-2">
                          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">Execution Steps</span>
                          <ul className="text-xs text-zinc-400 space-y-1.5">
                            {m.execution_plan?.steps?.slice(0, 3).map((st: string, idx: number) => (
                              <li key={idx} className="flex items-center space-x-1.5">
                                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
                                <span className="truncate">{st}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* TAB 2: Backlog Planning & Timeline */}
        {activeTab === 'backlog' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
            {/* Vision Decomposer */}
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Decompose Vision</CardTitle>
                <CardDescription>Input your product vision to automatically generate hierarchical Epics, Features, and Stories</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={projectVision}
                  onChange={(e) => setProjectVision(e.target.value)}
                  placeholder="e.g. Build a healthcare telemedicine app for patients to search doctors, book live consultation calls, and encrypt patient EHR data..."
                  rows={6}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-zinc-700"
                />
                <button
                  onClick={handleGenerateBacklog}
                  disabled={isActionLoading || !projectVision.trim()}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg p-2.5 text-sm font-semibold flex items-center justify-center space-x-2 transition active:scale-95 disabled:opacity-50"
                >
                  <Sparkles size={16} />
                  <span>AI Backlog Decomposer</span>
                </button>
              </CardContent>
            </Card>

            {/* Backlog Hierarchy List */}
            <Card className="bg-zinc-950/20 border border-zinc-900 lg:col-span-2">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div>
                  <CardTitle className="text-lg">Agile Backlog</CardTitle>
                  <CardDescription>Product Epics, Features, and Tasks</CardDescription>
                </div>
                <button
                  onClick={handleRunScheduler}
                  disabled={isActionLoading}
                  className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-500/20 rounded-lg px-3 py-1.5 text-xs font-bold transition flex items-center space-x-1.5"
                >
                  <CalendarDays size={14} />
                  <span>Execute AI Scheduler</span>
                </button>
              </CardHeader>
              <CardContent className="space-y-4 max-h-[500px] overflow-y-auto pr-1">
                {backlogItems.map((item) => {
                  const isExpanded = expandedItem === item.id;
                  const hasCriteria = !!item.metadata_fields?.acceptance_criteria;
                  const hasWireframe = !!item.metadata_fields?.wireframe_suggestions;

                  return (
                    <div key={item.id} className="border border-zinc-900 bg-zinc-950/50 rounded-lg overflow-hidden transition-all">
                      <div 
                        onClick={() => setExpandedItem(isExpanded ? null : item.id)}
                        className="p-3 flex items-center justify-between cursor-pointer hover:bg-zinc-900/20 transition-colors"
                      >
                        <div className="space-y-1">
                          <div className="flex items-center space-x-2">
                            <span className={`text-[9px] font-extrabold px-1.5 py-0.5 rounded uppercase ${
                              item.type === 'Epic' ? 'bg-amber-950 border border-amber-900/50 text-amber-400' :
                              item.type === 'Feature' ? 'bg-blue-950 border border-blue-900/50 text-blue-400' :
                              'bg-zinc-900 border border-zinc-800 text-zinc-400'
                            }`}>
                              {item.type}
                            </span>
                            <h4 className="text-xs font-bold text-white">{item.title}</h4>
                          </div>
                          <p className="text-[11px] text-zinc-400 line-clamp-1">{item.description}</p>
                          
                          {/* Scheduled timeline if existing */}
                          {item.metadata_fields && item.metadata_fields.scheduled_start && item.metadata_fields.scheduled_end && (
                            <div className="text-[10px] text-indigo-400 font-semibold flex items-center space-x-1 mt-1">
                              <CalendarDays size={12} />
                              <span>{new Date(item.metadata_fields.scheduled_start).toLocaleDateString()} - {new Date(item.metadata_fields.scheduled_end).toLocaleDateString()}</span>
                            </div>
                          )}
                        </div>
                        <div className="flex items-center space-x-3 shrink-0">
                          <span className="text-[10px] font-bold text-zinc-400">{item.estimated_hours}h</span>
                          <span className="text-[10px] text-zinc-600">{isExpanded ? '▲' : '▼'}</span>
                        </div>
                      </div>

                      {isExpanded && (
                        <div className="px-3 pb-4 pt-1 border-t border-zinc-900/60 bg-zinc-900/10 space-y-4 text-xs">
                          <div>
                            <div className="text-[10px] font-extrabold text-zinc-500 uppercase tracking-wider mb-1">Description</div>
                            <div className="text-zinc-300 leading-relaxed">{item.description}</div>
                          </div>

                          {/* Given-When-Then Acceptance Criteria */}
                          <div className="p-3 bg-zinc-950/80 border border-zinc-900 rounded-lg space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-extrabold text-zinc-400 uppercase tracking-wider">Acceptance Criteria (Given-When-Then)</span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleGenerateAcceptanceCriteria(item.id);
                                }}
                                disabled={generatingId === item.id}
                                className="text-[10px] px-2.5 py-1 rounded bg-indigo-600/15 border border-indigo-500/30 text-indigo-350 hover:bg-indigo-600/30 transition disabled:opacity-50"
                              >
                                {generatingId === item.id ? 'Generating...' : hasCriteria ? 'Regenerate' : 'Generate via AI'}
                              </button>
                            </div>
                            <pre className="text-[11px] text-zinc-400 whitespace-pre-wrap font-mono leading-relaxed mt-1">
                              {item.metadata_fields?.acceptance_criteria || 'No acceptance criteria generated yet.'}
                            </pre>
                          </div>

                          {/* UX Wireframe layout suggestions */}
                          <div className="p-3 bg-zinc-950/80 border border-zinc-900 rounded-lg space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-extrabold text-zinc-400 uppercase tracking-wider">UX Wireframe Suggestions</span>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleGenerateWireframe(item.id);
                                }}
                                disabled={generatingId === item.id}
                                className="text-[10px] px-2.5 py-1 rounded bg-violet-600/15 border border-violet-500/30 text-violet-350 hover:bg-violet-600/30 transition disabled:opacity-50"
                              >
                                {generatingId === item.id ? 'Generating...' : hasWireframe ? 'Regenerate' : 'Generate via AI'}
                              </button>
                            </div>
                            <pre className="text-[11px] text-zinc-400 whitespace-pre-wrap font-mono leading-relaxed mt-1">
                              {item.metadata_fields?.wireframe_suggestions || 'No wireframe suggestions generated yet.'}
                            </pre>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
                {backlogItems.length === 0 && (
                  <div className="text-center py-16 text-xs text-zinc-600">No backlog items decomposed. Enter a vision or apply a template below.</div>
                )}
              </CardContent>
            </Card>

            {/* Reusable Templates Library */}
            <Card className="bg-zinc-950/20 border border-zinc-900 lg:col-span-3">
              <CardHeader>
                <CardTitle className="text-lg">Industry Planning Templates</CardTitle>
                <CardDescription>Bootstrap your backlog instantly using production templates</CardDescription>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.entries(templates).map(([key, value]) => (
                  <div key={key} className="p-4 border border-zinc-900 bg-zinc-950/40 rounded-xl space-y-3 flex flex-col justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-white">{value.name}</h4>
                      <p className="text-xs text-zinc-400 line-clamp-2 mt-1">{value.description}</p>
                    </div>
                    <button
                      onClick={() => handleApplyTemplate(key)}
                      disabled={isActionLoading}
                      className="w-full bg-zinc-900 hover:bg-zinc-800 text-white rounded-lg p-2 text-xs font-semibold transition active:scale-95"
                    >
                      Apply Template
                    </button>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

        {/* TAB: Kanban Sprint Board */}
        {activeTab === 'kanban' && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-in fade-in duration-200">
            {(['Todo', 'In Progress', 'Blocked', 'Done'] as const).map((colStatus) => {
              const itemsInCol = backlogItems.filter(item => item.status === colStatus);
              return (
                <div key={colStatus} className="flex flex-col h-[700px] border border-zinc-900 bg-zinc-950/20 rounded-2xl p-4 space-y-4">
                  <div className="flex items-center justify-between border-b border-zinc-900 pb-2">
                    <span className="text-xs font-extrabold uppercase tracking-wider text-zinc-300 flex items-center gap-1.5">
                      <span className={`h-2 w-2 rounded-full ${
                        colStatus === 'Todo' ? 'bg-zinc-500' :
                        colStatus === 'In Progress' ? 'bg-indigo-400' :
                        colStatus === 'Blocked' ? 'bg-red-400' :
                        'bg-emerald-400'
                      }`} />
                      {colStatus}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-900 border border-zinc-800 font-bold text-zinc-400">
                      {itemsInCol.length}
                    </span>
                  </div>

                  <div className="flex-1 overflow-y-auto space-y-3 pr-1">
                    {itemsInCol.map((item) => {
                      const isExpanded = expandedItem === item.id;
                      const hasCriteria = !!item.metadata_fields?.acceptance_criteria;
                      const hasWireframe = !!item.metadata_fields?.wireframe_suggestions;

                      return (
                        <div
                          key={item.id}
                          onClick={() => setExpandedItem(isExpanded ? null : item.id)}
                          className={`p-4 border rounded-xl bg-zinc-950/60 cursor-pointer hover:border-zinc-700 transition space-y-3 ${
                            isExpanded ? 'border-indigo-600/80 shadow-[0_0_15px_rgba(99,102,241,0.1)]' : 'border-zinc-900/80'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded ${
                              item.type === 'Epic' ? 'bg-amber-950 border border-amber-900/50 text-amber-450' :
                              item.type === 'Feature' ? 'bg-blue-950 border border-blue-900/50 text-blue-450' :
                              'bg-zinc-900 border border-zinc-800 text-zinc-400'
                            }`}>
                              {item.type}
                            </span>
                            <span className={`text-[9px] font-black uppercase px-1.5 py-0.5 rounded ${
                              item.priority === 'High' ? 'bg-red-950 text-red-400' :
                              item.priority === 'Medium' ? 'bg-amber-950 text-amber-400' :
                              'bg-zinc-900 text-zinc-450'
                            }`}>
                              {item.priority}
                            </span>
                          </div>

                          <h4 className="text-xs font-bold text-white leading-tight">{item.title}</h4>
                          <p className="text-[10px] text-zinc-400 line-clamp-2 leading-relaxed">{item.description}</p>

                          <div className="flex items-center justify-between text-[10px] text-zinc-550 pt-2 border-t border-zinc-900/60">
                            <span>{item.estimated_hours}h</span>
                            <div className="flex gap-1.5" onClick={(e) => e.stopPropagation()}>
                              <select
                                value={item.status}
                                onChange={async (e) => {
                                  const newStatus = e.target.value as 'Todo' | 'In Progress' | 'Blocked' | 'Done';
                                  if (!activeWorkspace) return;
                                  try {
                                    const updated = await apiService.put<PlanningItem>(
                                      `/planning/backlog/items/${item.id}?workspace_id=${activeWorkspace.id}`,
                                      { status: newStatus }
                                    );
                                    setBacklogItems(prev => prev.map(x => x.id === item.id ? updated : x));
                                  } catch (err) {
                                    console.error(err);
                                  }
                                }}
                                className="bg-zinc-900 border border-zinc-800 rounded px-1.5 py-0.5 text-[9px] text-zinc-450 focus:outline-none focus:border-zinc-700 font-bold"
                              >
                                <option value="Todo">Todo</option>
                                <option value="In Progress">In Progress</option>
                                <option value="Blocked">Blocked</option>
                                <option value="Done">Done</option>
                              </select>
                            </div>
                          </div>

                          {isExpanded && (
                            <div className="space-y-3 pt-2 text-[10px] leading-relaxed border-t border-zinc-900/60" onClick={(e) => e.stopPropagation()}>
                              <div className="bg-zinc-950 border border-zinc-900 rounded p-2.5 space-y-1.5">
                                <div className="flex items-center justify-between">
                                  <span className="font-extrabold text-zinc-500 uppercase tracking-wider">Acceptance Criteria</span>
                                  <button
                                    onClick={() => handleGenerateAcceptanceCriteria(item.id)}
                                    disabled={generatingId === item.id}
                                    className="px-1.5 py-0.5 rounded bg-indigo-600/15 border border-indigo-500/30 text-indigo-350 hover:bg-indigo-600/30 transition disabled:opacity-50"
                                  >
                                    {generatingId === item.id ? 'Generating...' : hasCriteria ? 'Regen' : 'AI Gen'}
                                  </button>
                                </div>
                                <pre className="text-[9px] text-zinc-400 whitespace-pre-wrap font-mono leading-relaxed max-h-24 overflow-y-auto">
                                  {item.metadata_fields?.acceptance_criteria || 'No acceptance criteria generated.'}
                                </pre>
                              </div>

                              <div className="bg-zinc-950 border border-zinc-900 rounded p-2.5 space-y-1.5">
                                <div className="flex items-center justify-between">
                                  <span className="font-extrabold text-zinc-500 uppercase tracking-wider">UX Wireframe</span>
                                  <button
                                    onClick={() => handleGenerateWireframe(item.id)}
                                    disabled={generatingId === item.id}
                                    className="px-1.5 py-0.5 rounded bg-violet-600/15 border border-violet-500/30 text-violet-350 hover:bg-violet-600/30 transition disabled:opacity-50"
                                  >
                                    {generatingId === item.id ? 'Generating...' : hasWireframe ? 'Regen' : 'AI Gen'}
                                  </button>
                                </div>
                                <pre className="text-[9px] text-zinc-400 whitespace-pre-wrap font-mono leading-relaxed max-h-24 overflow-y-auto">
                                  {item.metadata_fields?.wireframe_suggestions || 'No wireframe suggestions generated.'}
                                </pre>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                    {itemsInCol.length === 0 && (
                      <div className="text-center py-20 text-[10px] text-zinc-655 italic">No tasks in this column.</div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* TAB 3: Dependency Graph */}
        {activeTab === 'dependencies' && (
          <div className="grid grid-cols-1 gap-6 animate-in fade-in duration-200">
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Technical & Logical Dependencies</CardTitle>
                  <CardDescription>Discover integrations, API requirements, and blockers automatically using AI</CardDescription>
                </div>
                <button
                  onClick={handleDetectDependencies}
                  disabled={isActionLoading || backlogItems.length < 2}
                  className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg px-4 py-2 text-sm font-semibold flex items-center space-x-1.5 transition active:scale-95"
                >
                  <GitBranch size={16} />
                  <span>Run AI Dependency Engine</span>
                </button>
              </CardHeader>
              <CardContent className="space-y-4">
                {dependencies.map((dep) => {
                  const source = backlogItems.find(it => it.id === dep.source_item_id);
                  const target = backlogItems.find(it => it.id === dep.target_item_id);
                  return (
                    <div key={dep.id} className="p-3 border border-zinc-900 bg-zinc-950/50 rounded-lg flex items-center space-x-3 text-xs">
                      <GitBranch size={14} className="text-indigo-400 shrink-0" />
                      <div className="flex-1 flex flex-wrap items-center gap-2">
                        <span className="font-bold text-white">{source?.title || 'Loading item...'}</span>
                        <span className="text-zinc-500 font-medium">is prerequisite for</span>
                        <span className="font-bold text-white">{target?.title || 'Loading item...'}</span>
                      </div>
                      <span className="text-[10px] uppercase font-black bg-rose-950/30 border border-rose-900/50 text-rose-400 px-2 py-0.5 rounded">{dep.dependency_type}</span>
                    </div>
                  );
                })}
                {dependencies.length === 0 && (
                  <div className="text-center py-16 text-xs text-zinc-600">No dependencies detected. Generate a backlog first, then run detection.</div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* TAB 4: Scenario Simulation & Resource Planner */}
        {activeTab === 'simulations' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
            {/* Create Simulation */}
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Simulate Project Delivery</CardTitle>
                <CardDescription>Model optimistic vs pessimistic cases, budget forecasts, and bottleneck risks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-1">
                  <label className="text-xs text-zinc-400 font-semibold">Simulation Title</label>
                  <input
                    type="text"
                    value={simName}
                    onChange={(e) => setSimName(e.target.value)}
                    placeholder="e.g. Q4 MVP Release"
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs text-zinc-400 font-semibold">Simulation Context / Core Scope</label>
                  <textarea
                    value={simVision}
                    onChange={(e) => setSimVision(e.target.value)}
                    placeholder="Specify target requirements, team sizes, and API constraints..."
                    rows={4}
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-2.5 text-sm text-white focus:outline-none focus:border-zinc-700"
                  />
                </div>
                <button
                  onClick={handleRunSimulation}
                  disabled={isActionLoading || !simName.trim() || !simVision.trim()}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg p-2.5 text-sm font-semibold flex items-center justify-center space-x-2 transition active:scale-95 disabled:opacity-50"
                >
                  <Play size={16} />
                  <span>Execute Simulation</span>
                </button>
              </CardContent>
            </Card>

            {/* Simulations Results list */}
            <Card className="bg-zinc-950/20 border border-zinc-900 lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Simulation Results</CardTitle>
                <CardDescription>Modeled timeline, budget impacts, and bottleneck scores</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 max-h-[500px] overflow-y-auto pr-1">
                {simulations.map((sim) => (
                  <div key={sim.id} className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-xl space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-white text-base">{sim.name}</h4>
                      <span className="text-[10px] text-zinc-500">{sim.created_at ? new Date(sim.created_at).toLocaleDateString() : ''}</span>
                    </div>

                    {/* Timeline forecast */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-emerald-400 uppercase">Best Case</span>
                        <div className="text-lg font-black text-white mt-1">{sim.best_case_timeline?.duration_weeks} Weeks</div>
                        <ul className="text-[10px] text-zinc-500 mt-2 list-disc list-inside">
                          {sim.best_case_timeline?.key_assumptions?.slice(0, 2).map((a, idx) => (
                            <li key={idx} className="truncate">{a}</li>
                          ))}
                        </ul>
                      </div>
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-indigo-400 uppercase">Average Case</span>
                        <div className="text-lg font-black text-white mt-1">{sim.average_case_timeline?.duration_weeks} Weeks</div>
                        <span className="text-[10px] text-zinc-500 block mt-2">Target: {sim.average_case_timeline?.expected_delivery_date || 'N/A'}</span>
                      </div>
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-rose-400 uppercase">Worst Case</span>
                        <div className="text-lg font-black text-white mt-1">{sim.worst_case_timeline?.duration_weeks} Weeks</div>
                        <ul className="text-[10px] text-zinc-500 mt-2 list-disc list-inside">
                          {sim.worst_case_timeline?.key_risks?.slice(0, 2).map((r, idx) => (
                            <li key={idx} className="truncate">{r}</li>
                          ))}
                        </ul>
                      </div>
                    </div>

                    {/* Budget & bottleneck impact */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-zinc-400 uppercase">Financial Impact Breakdown</span>
                        <div className="text-xs text-zinc-300 mt-2 space-y-1">
                          <div>Optimistic: <strong>${sim.budget_impact?.best_case_cost?.toLocaleString()}</strong></div>
                          <div>Expected: <strong>${sim.budget_impact?.average_case_cost?.toLocaleString()}</strong></div>
                          <div>Risk: <strong>${sim.budget_impact?.worst_case_cost?.toLocaleString()}</strong></div>
                        </div>
                      </div>
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-zinc-400 uppercase">Bottleneck / Timeline Risks</span>
                        <div className="text-xs text-zinc-300 mt-2 space-y-1">
                          <div>Risk Score: <strong className="text-rose-400">{sim.timeline_impact?.delay_risk_score}/10</strong></div>
                          <div className="truncate">Bottlenecks: <strong>{sim.timeline_impact?.critical_path_bottlenecks?.join(', ') || 'None'}</strong></div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {simulations.length === 0 && (
                  <div className="text-center py-16 text-xs text-zinc-600">No simulations run yet. Enter a context to execute one.</div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {/* TAB 5: Context Compressor */}
        {activeTab === 'compressor' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-200">
            {/* Input Context */}
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Semantic Compressor</CardTitle>
                <CardDescription>Compress long messages, documents, or memory strings to fit context constraints</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <textarea
                  value={compressText}
                  onChange={(e) => setCompressText(e.target.value)}
                  placeholder="Paste long conversations, requirements documents, or transcripts..."
                  rows={8}
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg p-3 text-sm text-white focus:outline-none focus:border-zinc-700"
                />
                <button
                  onClick={handleCompressText}
                  disabled={isActionLoading || !compressText.trim()}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg p-2.5 text-sm font-semibold flex items-center justify-center space-x-2 transition active:scale-95 disabled:opacity-50"
                >
                  <Zap size={16} />
                  <span>Compress Context</span>
                </button>
              </CardContent>
            </Card>

            {/* Compressed Output */}
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Compressed Result</CardTitle>
                <CardDescription>Semantic, condensed equivalent maintaining critical facts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-zinc-900 border border-zinc-800 rounded-xl min-h-[220px] text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed">
                  {compressedResult || 'No compressed output yet. Click compress on the left panel.'}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* TAB 6: Resource Planning */}
        {activeTab === 'resources' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
            {costData ? (
              <>
                <Card className="bg-zinc-950/20 border border-zinc-900">
                  <CardHeader>
                    <CardTitle className="text-lg">FTE Headcount Allocation</CardTitle>
                    <CardDescription>Decomposed staff requirements for the active workspace</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4 text-xs">
                    <div className="flex justify-between items-center p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                      <span className="font-medium text-zinc-300">Software Developers</span>
                      <span className="font-bold text-indigo-400">{costData.total_developers} FTE</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                      <span className="font-medium text-zinc-300">UI/UX Designers</span>
                      <span className="font-bold text-emerald-400">{costData.total_designers} FTE</span>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                      <span className="font-medium text-zinc-300">QA Engineers</span>
                      <span className="font-bold text-amber-400">{costData.total_qa} FTE</span>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-zinc-950/20 border border-zinc-900 lg:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-lg">Operational Budget & Run Rate</CardTitle>
                    <CardDescription>Monthly capital estimations and long range projections</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6 text-xs">
                    <div className="grid grid-cols-3 gap-4">
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase">Monthly Infra</span>
                        <div className="text-base font-black text-white mt-1">${costData.monthly_infra_cost.toLocaleString()}</div>
                      </div>
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase">Monthly AI API</span>
                        <div className="text-base font-black text-indigo-400 mt-1">${costData.monthly_ai_cost.toLocaleString()}</div>
                      </div>
                      <div className="p-3 bg-zinc-950 border border-zinc-900 rounded-lg">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase">Total Monthly Burn</span>
                        <div className="text-base font-black text-rose-450 mt-1">${costData.total_monthly_burn.toLocaleString()}</div>
                      </div>
                    </div>
                    <div className="p-4 bg-zinc-950 border border-zinc-900 rounded-lg">
                      <span className="text-[10px] font-bold text-zinc-400 block mb-2 uppercase">Long Range Growth Projections</span>
                      <div className="text-[11px] text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed max-h-[200px] overflow-y-auto">
                        {costData.forecast_3yr_markdown}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <div className="lg:col-span-3 text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                No resource metadata found. Reload or generate telemetry from the header button.
              </div>
            )}
          </div>
        )}

        {/* TAB 7: Analytics */}
        {activeTab === 'analytics' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 animate-in fade-in duration-200">
            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Velocity & Planning Metrics</CardTitle>
                <CardDescription>Accuracy and efficiency statistics computed over active sprint items</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 text-xs">
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-zinc-350">
                    <span>Task Planning Accuracy</span>
                    <span className="font-bold text-white">{analytics?.accuracy_rate ? `${analytics.accuracy_rate}%` : '100%'}</span>
                  </div>
                  <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500" style={{ width: `${analytics?.accuracy_rate || 100}%` }} />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center text-zinc-350">
                    <span>Active Completion Rate</span>
                    <span className="font-bold text-emerald-400">{analytics?.completion_rate ? `${analytics.completion_rate.toFixed(1)}%` : '0%'}</span>
                  </div>
                  <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500" style={{ width: `${analytics?.completion_rate || 0}%` }} />
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between items-center text-zinc-350">
                    <span>Sprint Execution Efficiency</span>
                    <span className="font-bold text-amber-400">{analytics?.execution_efficiency ? `${analytics.execution_efficiency.toFixed(1)}%` : '0%'}</span>
                  </div>
                  <div className="h-2 bg-zinc-900 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500" style={{ width: `${analytics?.execution_efficiency || 0}%` }} />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-zinc-950/20 border border-zinc-900">
              <CardHeader>
                <CardTitle className="text-lg">Delay & Delay Severity</CardTitle>
                <CardDescription>Telemetry monitoring overdue tickets and active bottleneck blockades</CardDescription>
              </CardHeader>
              <CardContent className="flex flex-col justify-center items-center py-10 space-y-4">
                <div className="text-5xl font-black text-rose-500">
                  {analytics?.total_delays_hours ? `${analytics.total_delays_hours}h` : '0 hrs'}
                </div>
                <div className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Accumulated Project Delay</div>
                <p className="text-[11px] text-zinc-500 text-center max-w-xs">
                  This represents the time sum of overdue sprint tasks relative to target milestone estimates.
                </p>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppShell>
  );
}
