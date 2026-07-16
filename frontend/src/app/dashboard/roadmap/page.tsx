'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { AgentThoughtVisualizer, ThoughtStep } from '@/components/ui/agent-thought-visualizer';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import {
  Sparkles,
  Calendar,
  Check,
  Copy,
  Download,
  Target,
  AlertTriangle,
  RefreshCw,
  Award,
  DollarSign,
  Briefcase,
  Users,
  HardDrive,
  Cpu,
  ShieldAlert,
  ChevronRight
} from 'lucide-react';

interface CostData {
  total_developers: number;
  total_qa: number;
  total_designers: number;
  monthly_infra_cost: number;
  monthly_ai_cost: number;
  total_monthly_burn: number;
  forecast_3yr_markdown: string;
}

interface RiskItem {
  category: string;
  severity: string;
  description: string;
  mitigation: string;
}

interface RiskData {
  overall_status: string;
  risks: RiskItem[];
}

const INITIAL_THOUGHTS: ThoughtStep[] = [
  {
    id: '1',
    agentName: 'Feature Roadmap Planner',
    roleIcon: 'brain',
    status: 'pending',
    message: 'Analyzing backlog structure & planning release timeline...',
    timestamp: 'Just now',
    details: ['Mapping stories to sprints', 'Allocating quarters and defining milestone targets'],
  },
  {
    id: '2',
    agentName: 'Cost Optimization Agent',
    roleIcon: 'cpu',
    status: 'pending',
    message: 'Calculating headcount burn rate and AI token resource allocation...',
    timestamp: 'Waiting...',
    details: ['Evaluating dev resources', 'Synthesizing infrastructure vs API cost estimations'],
  },
  {
    id: '3',
    agentName: 'Risk Mitigation Agent',
    roleIcon: 'shield',
    status: 'pending',
    message: 'Analyzing compliance hurdles, operational blockers, and mitigation plans...',
    timestamp: 'Waiting...',
    details: ['Formulating response playbooks', 'Assembling probability heatmaps'],
  }
];

export default function UnifiedRoadmapPage() {
  const { activeWorkspace } = useAuth();
  
  // Tab control
  const [activeTab, setActiveTab] = React.useState<'timeline' | 'costs' | 'risks'>('timeline');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [thoughts, setThoughts] = React.useState<ThoughtStep[]>(INITIAL_THOUGHTS);
  
  // Data states
  const [roadmapData, setRoadmapData] = React.useState<any>(null);
  const [costData, setCostData] = React.useState<CostData | null>(null);
  const [riskData, setRiskData] = React.useState<RiskData | null>(null);
  const [featuresInput, setFeaturesInput] = React.useState('');
  const [framework, setFramework] = React.useState('RICE');
  const [copied, setCopied] = React.useState(false);

  // Sync tab from URL query param
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tab = params.get('tab');
      if (tab === 'timeline' || tab === 'costs' || tab === 'risks') {
        setActiveTab(tab);
      }
    }
  }, []);

  // Fetch / Cache loader
  const loadWorkspaceRoadmapData = React.useCallback(async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      // Load cost estimation and risk analysis caches if they exist
      const costs = await apiService.post<CostData>(`/planning/intelligence/cost-estimation?workspace_id=${activeWorkspace.id}`).catch(() => null);
      if (costs) setCostData(costs);

      const risks = await apiService.post<RiskData>(`/planning/intelligence/risk-analysis?workspace_id=${activeWorkspace.id}`).catch(() => null);
      if (risks) setRiskData(risks);
    } catch (e: any) {
      console.warn('Failed to pre-fetch roadmap elements:', e);
    } finally {
      setLoading(false);
    }
  }, [activeWorkspace]);

  React.useEffect(() => {
    loadWorkspaceRoadmapData();
  }, [loadWorkspaceRoadmapData]);

  const simulateProgress = async () => {
    setThoughts(INITIAL_THOUGHTS.map((t, idx) => idx === 0 ? { ...t, status: 'active', timestamp: 'In progress' } : t));
    for (let i = 0; i < INITIAL_THOUGHTS.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 600));
      setThoughts(prev => prev.map((t, idx) => {
        if (idx === i) {
          return {
            ...t,
            status: 'completed',
            timestamp: `${(0.8 + idx * 0.5).toFixed(1)}s`,
            metrics: { latencyMs: 400, tokensUsed: 350, confidence: 0.98 }
          };
        }
        if (idx === i + 1) {
          return { ...t, status: 'active', timestamp: 'In progress' };
        }
        return t;
      }));
    }
  };

  const handleGenerateRoadmap = async () => {
    if (!activeWorkspace || !featuresInput.trim()) return;
    setLoading(true);
    setError(null);
    const progress = simulateProgress();
    try {
      const data = await apiService.post<any>('/ai/workflows/execute', {
        workflow_name: 'roadmap_planning',
        workspace_id: activeWorkspace.id,
        context: { idea: featuresInput, features: featuresInput, framework },
      });
      const raw = data.result || data;
      const r = raw.roadmap || {};
      const prioritization = raw.prioritization || {};
      
      const mapped = {
        title: activeWorkspace.name + ' Product Roadmap',
        overview: r.vision_roadmap || 'Roadmap strategy overview.',
        timeline: (r.quarterly_roadmap || []).map((q: any) => ({
          quarter: q.quarter || q.name || 'Q1',
          status: q.status || 'Planned',
          badgeColor: q.status === 'In Progress' ? 'bg-emerald-950 border-emerald-900/50 text-emerald-450' : 'bg-zinc-800 border-zinc-700 text-zinc-300',
          theme: q.theme || 'Focus Theme',
          milestones: (q.milestones || []).map((m: any) => ({
            priority: m.priority || 'Medium',
            effort: m.effort || 'Medium',
            name: m.name || m.title || 'Milestone Item',
            deliverable: m.deliverable || m.description || ''
          }))
        })),
        prioritizationMatrix: (prioritization.ranked_features || []).map((f: any, idx: number) => ({
          rank: idx + 1,
          feature: f.feature_name || 'Feature',
          reach: f.framework_breakdown?.reach || 'High',
          impact: f.framework_breakdown?.impact || 'Medium',
          confidence: f.framework_breakdown?.confidence || 'High',
          effort: f.framework_breakdown?.effort || 'Low',
          score: f.score || 0
        }))
      };
      await progress;
      setRoadmapData(mapped);
    } catch (e: any) {
      setError(e.message || 'Failed to synthesize roadmap');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCosts = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const costs = await apiService.post<CostData>(`/planning/intelligence/cost-estimation?workspace_id=${activeWorkspace.id}&refresh=true`);
      setCostData(costs);
    } catch (e: any) {
      setError(e.message || 'Failed to generate cost projections');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRisks = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setError(null);
    try {
      const risks = await apiService.post<RiskData>(`/planning/intelligence/risk-analysis?workspace_id=${activeWorkspace.id}&refresh=true`);
      setRiskData(risks);
    } catch (e: any) {
      setError(e.message || 'Failed to generate risk registers');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!roadmapData) return;
    const md = `# ${roadmapData.title}\n\n## Overview\n${roadmapData.overview}\n\n## Quarterly Timeline\n` + 
      roadmapData.timeline.map((t: any) => `### ${t.quarter} - ${t.theme} (${t.status})\n` +
        t.milestones.map((m: any) => `* **[${m.priority}] ${m.name}** - ${m.deliverable} (${m.effort})`).join('\n')
      ).join('\n\n');
    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
          <Calendar className="text-zinc-600 animate-pulse" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm max-w-sm">
            Choose or create a workspace to view your autonomous roadmap and strategy deck.
          </p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Breadcrumb & Title */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Roadmap & Strategy' }]} />
            <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center gap-3">
              <Calendar className="text-emerald-400" size={28} /> AI Roadmap & Financials Studio
            </h1>
            <p className="text-sm text-zinc-400 mt-1">
              Analyze product timelines, prioritize features, and manage operational cost & risk budgets.
            </p>
          </div>
          {roadmapData && (
            <button
              onClick={copyToClipboard}
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-xl text-zinc-300 hover:text-white text-xs font-bold transition"
            >
              {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
              <span>{copied ? 'Copied' : 'Copy Markdown'}</span>
            </button>
          )}
        </div>

        {/* Tab Controls */}
        <div className="flex border-b border-zinc-900 pb-px gap-2">
          {(['timeline', 'costs', 'risks'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
                activeTab === tab
                  ? 'border-emerald-500 text-emerald-400'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab === 'timeline' ? 'Quarterly Timeline' : tab === 'costs' ? 'Cost & Budgeting' : 'Risk registers'}
            </button>
          ))}
        </div>

        {error && (
          <div className="p-4 bg-rose-950/20 border border-rose-900/50 rounded-xl text-rose-400 text-xs">
            {error}
          </div>
        )}

        {/* TAB 1: TIMELINE / ROADMAP TIMELINE */}
        {activeTab === 'timeline' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            {/* Input form */}
            <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
                  <Sparkles size={14} className="text-emerald-400" /> Feature Candidates / Scope Outline
                </label>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs text-zinc-500 font-bold">Framework:</span>
                  {['RICE', 'MoSCoW', 'Value vs Effort'].map(f => (
                    <button
                      key={f}
                      onClick={() => setFramework(f)}
                      className={`text-xs px-2.5 py-1 rounded-lg font-bold border transition ${
                        framework === f
                          ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                          : 'bg-zinc-900 border-zinc-850 text-zinc-400'
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>
              <textarea
                value={featuresInput}
                onChange={e => setFeaturesInput(e.target.value)}
                rows={3}
                placeholder="E.g. 1. Multi-tenant workspace database sharing. 2. Real-time Slack/Teams alerts. 3. Interactive Gantt roadmap timeline visualizer..."
                className="w-full bg-zinc-900 border border-zinc-850 rounded-xl p-3 text-sm text-zinc-200 focus:outline-none focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/20"
              />
              <div className="flex justify-end">
                <button
                  onClick={handleGenerateRoadmap}
                  disabled={loading || !featuresInput.trim()}
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold uppercase tracking-wider disabled:opacity-50 transition"
                >
                  {loading ? 'Synthesizing...' : 'Execute Roadmap Swarm'}
                </button>
              </div>
            </div>

            {/* Thoughts visualizer */}
            {loading && (
              <AgentThoughtVisualizer steps={thoughts} isGenerating={loading} isSimulated={true} />
            )}

            {/* Timeline Outputs */}
            {roadmapData && (
              <div className="space-y-6">
                <div className="p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400">Roadmap Strategy Overview</h3>
                  <p className="text-xs text-zinc-300 leading-relaxed">{roadmapData.overview}</p>
                </div>
                
                <div className="grid grid-cols-1 gap-6">
                  {roadmapData.timeline?.map((q: any, idx: number) => (
                    <div key={idx} className="relative pl-6 border-l-2 border-emerald-500/30 space-y-3">
                      <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-zinc-950 border-2 border-emerald-400" />
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-base font-bold text-white">{q.quarter}</span>
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${q.badgeColor}`}>
                            {q.status}
                          </span>
                        </div>
                        <span className="text-xs text-zinc-500">{q.theme}</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        {q.milestones?.map((m: any, mIdx: number) => (
                          <div key={mIdx} className="p-4 rounded-xl border border-zinc-900 bg-zinc-950/40 space-y-2">
                            <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500">
                              <span>Priority: {m.priority}</span>
                              <span>Effort: {m.effort}</span>
                            </div>
                            <h4 className="text-xs font-bold text-white">{m.name}</h4>
                            <p className="text-xs text-zinc-400 leading-relaxed border-t border-zinc-900/60 pt-2">{m.deliverable}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Prioritization matrix list */}
                <div className="p-6 rounded-2xl bg-zinc-950/20 border border-zinc-900 space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Award size={18} className="text-emerald-400" /> Prioritization Scoring Matrix ({framework})
                  </h3>
                  <div className="divide-y divide-zinc-900 border border-zinc-900 rounded-xl overflow-hidden bg-zinc-950/40">
                    {roadmapData.prioritizationMatrix?.map((pm: any) => (
                      <div key={pm.rank} className="p-4 flex items-center justify-between text-xs hover:bg-zinc-900/10">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-400 font-mono font-bold">{pm.rank}</span>
                            <span className="font-bold text-white">{pm.feature}</span>
                          </div>
                          <div className="text-[10px] text-zinc-500 flex gap-3">
                            <span>Reach: {pm.reach}</span>
                            <span>Impact: {pm.impact}</span>
                            <span>Confidence: {pm.confidence}</span>
                            <span>Effort: {pm.effort}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-bold text-emerald-400">{pm.score}</div>
                          <span className="text-[9px] uppercase font-bold text-zinc-500">Aggregate Score</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            {!roadmapData && (
              <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                No roadmap generated yet. Use the prompt studio above to trigger.
              </div>
            )}
          </div>
        )}

        {/* TAB 2: COST ESTIMATION & BUDGET */}
        {activeTab === 'costs' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-base font-bold text-white">Resource, Headcount & Operating Budget</h3>
                <p className="text-xs text-zinc-500">Calculates monthly human capital run rate and infrastructure scale costs</p>
              </div>
              <button
                onClick={handleGenerateCosts}
                disabled={loading}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 transition"
              >
                <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                <span>Re-estimate Costs</span>
              </button>
            </div>

            {costData ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Stats Panel */}
                <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="p-4 bg-zinc-950/40 border border-zinc-900 rounded-xl space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase">Monthly Dev Burn</span>
                    <div className="text-2xl font-black text-white">${((costData.total_developers * 8000) + (costData.total_qa * 6000) + (costData.total_designers * 7000)).toLocaleString()}</div>
                    <span className="text-[9px] text-zinc-500">Standard market rates applied</span>
                  </div>
                  <div className="p-4 bg-zinc-950/40 border border-zinc-900 rounded-xl space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase">Monthly Infra Cost</span>
                    <div className="text-2xl font-black text-emerald-450">${costData.monthly_infra_cost.toLocaleString()}</div>
                    <span className="text-[9px] text-zinc-500">Hosting and DB resources</span>
                  </div>
                  <div className="p-4 bg-zinc-950/40 border border-zinc-900 rounded-xl space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase">Monthly AI & LLM Costs</span>
                    <div className="text-2xl font-black text-indigo-400">${costData.monthly_ai_cost.toLocaleString()}</div>
                    <span className="text-[9px] text-zinc-500">API queries & prompt loads</span>
                  </div>
                  <div className="p-4 bg-zinc-950/40 border border-zinc-900 rounded-xl space-y-1">
                    <span className="text-[10px] font-bold text-zinc-500 uppercase">Total Monthly Burn</span>
                    <div className="text-2xl font-black text-rose-400">${costData.total_monthly_burn.toLocaleString()}</div>
                    <span className="text-[9px] text-zinc-500">Aggregate burn forecast</span>
                  </div>
                </div>

                {/* Team allocation cards */}
                <div className="p-5 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Headcount Allocations</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-xs p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Cpu className="text-indigo-400" size={16} />
                        <span>Developers</span>
                      </div>
                      <span className="font-bold text-white">{costData.total_developers} FTE</span>
                    </div>
                    <div className="flex justify-between items-center text-xs p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Users className="text-emerald-450" size={16} />
                        <span>Designers</span>
                      </div>
                      <span className="font-bold text-white">{costData.total_designers} FTE</span>
                    </div>
                    <div className="flex justify-between items-center text-xs p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                      <div className="flex items-center gap-2">
                        <Briefcase className="text-amber-400" size={16} />
                        <span>QA Engineers</span>
                      </div>
                      <span className="font-bold text-white">{costData.total_qa} FTE</span>
                    </div>
                  </div>
                </div>

                {/* 3yr Forecast */}
                <div className="lg:col-span-2 p-5 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-zinc-400">3-Year Long Range Projection</h4>
                  <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-4 bg-zinc-950 border border-zinc-900 rounded-lg max-h-[300px] overflow-y-auto">
                    {costData.forecast_3yr_markdown}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                No cost estimates generated. Click "Re-estimate Costs" above to run computation.
              </div>
            )}
          </div>
        )}

        {/* TAB 3: RISK ANALYSIS */}
        {activeTab === 'risks' && (
          <div className="space-y-6 animate-in fade-in duration-200">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-base font-bold text-white">Risk Register & Mitigation Protocols</h3>
                <p className="text-xs text-zinc-500">Maps compliance, integration, and team velocity risks</p>
              </div>
              <button
                onClick={handleGenerateRisks}
                disabled={loading}
                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 transition"
              >
                <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
                <span>Run Risk Audit</span>
              </button>
            </div>

            {riskData ? (
              <div className="space-y-6">
                <div className="p-4 bg-zinc-950 border border-zinc-900 rounded-xl flex items-center justify-between text-xs">
                  <span className="font-bold text-zinc-400">Workspace Health & Security Audit Status:</span>
                  <span className={`px-3 py-1 rounded-full font-bold uppercase text-[9px] ${
                    riskData.overall_status === 'Healthy' || riskData.overall_status === 'Low Risk' ? 'bg-emerald-950 text-emerald-450 border border-emerald-900' :
                    riskData.overall_status === 'Medium Risk' ? 'bg-amber-950 text-amber-450 border border-amber-900' :
                    'bg-red-950 text-red-400 border border-red-900'
                  }`}>
                    {riskData.overall_status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {riskData.risks?.map((r, idx) => (
                    <div key={idx} className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-xl space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] uppercase font-bold text-zinc-500 bg-zinc-900 border border-zinc-800 px-2.5 py-0.5 rounded">{r.category}</span>
                        <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                          r.severity === 'High' ? 'bg-rose-950 text-rose-400 border border-rose-900' :
                          r.severity === 'Medium' ? 'bg-amber-950 text-amber-400 border border-amber-900' :
                          'bg-zinc-850 text-zinc-400'
                        }`}>
                          Severity: {r.severity}
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-white leading-tight">{r.description}</h4>
                      <div className="p-3 bg-zinc-900/60 border border-zinc-850 rounded-lg text-xs text-zinc-300">
                        <strong className="text-zinc-550 block text-[9px] uppercase tracking-wider mb-1">Mitigation playbook</strong>
                        {r.mitigation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                No risk audit generated yet. Click "Run Risk Audit" to analyze workspace security vulnerabilities.
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
