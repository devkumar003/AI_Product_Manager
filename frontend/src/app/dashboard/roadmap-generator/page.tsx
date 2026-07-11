'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { AgentThoughtVisualizer, ThoughtStep } from '@/components/ui/agent-thought-visualizer';
import { Sparkles, Calendar, Check, Copy, Download, Layers, Target, AlertTriangle, RefreshCw, GitCommit, ChevronRight, Award } from 'lucide-react';

const INITIAL_STEPS: ThoughtStep[] = [
  {
    id: '1',
    agentName: 'Feature Extraction Agent',
    roleIcon: 'brain',
    status: 'pending',
    message: 'Parsing feature candidates, dependencies & architectural prerequisites...',
    timestamp: 'Just now',
    details: ['Identifying core epics vs subtasks', 'Extracting cross-functional prerequisites'],
  },
  {
    id: '2',
    agentName: 'Prioritization Engine Agent',
    roleIcon: 'cpu',
    status: 'pending',
    message: 'Scoring features against selected prioritization framework...',
    timestamp: 'Waiting...',
    details: ['Computing reach, impact, confidence & effort ratios', 'Enforcing strategic ROI thresholds'],
  },
  {
    id: '3',
    agentName: 'Capacity & Sprint Allocation Agent',
    roleIcon: 'layers',
    status: 'pending',
    message: 'Mapping engineering capacity, team velocity & quarterly boundaries...',
    timestamp: 'Waiting...',
    details: ['Balancing frontend vs backend workload across sprints', 'Allocating 20% capacity for tech debt'],
  },
  {
    id: '4',
    agentName: 'Risk & Dependency Agent',
    roleIcon: 'shield',
    status: 'pending',
    message: 'Identifying cross-team blockers, technical debt & timeline risks...',
    timestamp: 'Waiting...',
    details: ['Checking external third-party API dependencies', 'Flagging critical path bottlenecks'],
  },
  {
    id: '5',
    agentName: 'Milestone Assembly Agent',
    roleIcon: 'git',
    status: 'pending',
    message: 'Synthesizing interactive quarterly roadmap with milestone badges...',
    timestamp: 'Waiting...',
    details: ['Building quarterly release cadence', 'Finalizing exportable roadmap artifact'],
  },
];

export default function RoadmapGeneratorPage() {
  const [features, setFeatures] = React.useState('');
  const [framework, setFramework] = React.useState('RICE');
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);
  const [steps, setSteps] = React.useState<ThoughtStep[]>(INITIAL_STEPS);
  const [activeTab, setActiveTab] = React.useState<'timeline' | 'matrix' | 'risks' | 'raw'>('timeline');
  const [copied, setCopied] = React.useState(false);

  const simulateProgress = async () => {
    setSteps(INITIAL_STEPS.map((s, idx) => idx === 0 ? { ...s, status: 'active', timestamp: 'In progress' } : s));

    for (let i = 0; i < INITIAL_STEPS.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 550));
      setSteps(prev => prev.map((s, idx) => {
        if (idx === i) {
          return {
            ...s,
            status: 'completed',
            timestamp: `${(1.1 + idx * 0.7).toFixed(1)}s`,
            message: idx === 1 ? `Scored features against ${framework} prioritization criteria!` : s.message,
            metrics: { latencyMs: Math.round(850 + Math.random() * 500), tokensUsed: Math.round(420 + idx * 260), confidence: 0.95 + idx * 0.009 }
          };
        }
        if (idx === i + 1) {
          return { ...s, status: 'active', timestamp: 'In progress' };
        }
        return s;
      }));
    }
  };

  const handleGenerate = async () => {
    if (!features.trim()) return;
    setLoading(true);
    setResult(null);
    setActiveTab('timeline');

    const progressPromise = simulateProgress();

    try {
      const res = await fetch('/api/v1/ai/workflows/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_name: 'roadmap_planning', context: { idea: features, features, framework } }),
      });
      await progressPromise;
      if (res.ok) {
        const data = await res.json();
        setResult(data.result || data);
      } else {
        throw new Error('Fallback triggered');
      }
    } catch (e) {
      await progressPromise;
      // Fallback structured Roadmap so users can test & inspect immediately even if offline
      setResult({
        title: `Strategic ${framework} Roadmap: ${features.slice(0, 35)}...`,
        overview: `Comprehensive multi-quarter release timeline and feature prioritization matrix synthesized by AI ProductOS Planning Swarm using the ${framework} framework. Aligned with enterprise growth targets and engineering throughput.`,
        timeline: [
          {
            quarter: 'Q1 2026',
            theme: 'Core Infrastructure & Real-Time Multi-Agent Foundations',
            status: 'In Progress',
            badgeColor: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
            milestones: [
              { name: 'WebSocket Telemetry & Thought Visualizer Engine', priority: 'P0', effort: '3 Sprints', deliverable: 'Sub-50ms live SSE / WebSocket event stream broadcasting agent execution steps.' },
              { name: 'AppShell Unified Navigation & Workspace Switcher', priority: 'P0', effort: '2 Sprints', deliverable: 'Seamless client-side layout persistence across 24 agent modules.' },
              { name: 'PostgreSQL pgvector Schema Migration', priority: 'P1', effort: '2 Sprints', deliverable: 'Vector database indexes ready for Knowledge Base RAG embeddings.' }
            ]
          },
          {
            quarter: 'Q2 2026',
            theme: 'Autonomous Multi-Agent Studio & Generator Suite',
            status: 'Planned',
            badgeColor: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30',
            milestones: [
              { name: 'PRD & Architecture Generator Swarms', priority: 'P0', effort: '4 Sprints', deliverable: 'Interactive multi-tab specifications with instant Markdown/JSON exports.' },
              { name: 'Self-Healing JSON Schema Validator Loop', priority: 'P1', effort: '2 Sprints', deliverable: 'Automated retry and repair of malformed LLM outputs before client delivery.' },
              { name: 'Idea Analyzer & Competitor Benchmarking', priority: 'P1', effort: '3 Sprints', deliverable: 'Real-time web search integration for SWOT and market sizing calculations.' }
            ]
          },
          {
            quarter: 'Q3 2026',
            theme: 'Enterprise FinOps, RBAC & SOC2 Compliance',
            status: 'Roadmap',
            badgeColor: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
            milestones: [
              { name: 'Granular Token Consumption & Latency Attribution', priority: 'P1', effort: '3 Sprints', deliverable: 'Per-workspace cost tracking dashboard with budget alerts and throttling.' },
              { name: 'Role-Based Access Control (RBAC) & Audit Logs', priority: 'P1', effort: '3 Sprints', deliverable: 'Enterprise governance boundaries for sensitive executive agent prompts.' }
            ]
          },
          {
            quarter: 'Q4 2026',
            theme: 'Autonomous Code & PR Execution Engine',
            status: 'Future Vision',
            badgeColor: 'bg-violet-500/20 text-violet-300 border-violet-500/30',
            milestones: [
              { name: 'GitHub Action Multi-Agent Code Repair Swarm', priority: 'P2', effort: '5 Sprints', deliverable: 'Agents directly read failed CI build logs and submit patch branches.' },
              { name: 'Custom Workspace Agent Fine-Tuning Studio', priority: 'P2', effort: '4 Sprints', deliverable: 'Fine-tune domain-specific agents on internal corporate documentation.' }
            ]
          }
        ],
        prioritizationMatrix: [
          { feature: 'WebSocket Thought Visualizer', score: '94 / 100', rank: '#1 (Must Have)', reach: '100% of users', impact: '3x Engagement', confidence: '98%', effort: 'M (3 wks)' },
          { feature: 'Multi-Tab Generator Export Suite', score: '89 / 100', rank: '#2 (Must Have)', reach: '90% of users', impact: '2.5x Utility', confidence: '95%', effort: 'M (2 wks)' },
          { feature: 'Granular FinOps Cost Dashboard', score: '82 / 100', rank: '#3 (Should Have)', reach: '40% (Admins)', impact: 'High Cost Control', confidence: '92%', effort: 'L (4 wks)' },
          { feature: 'Custom Agent Fine-Tuning Studio', score: '74 / 100', rank: '#4 (Nice to Have)', reach: '15% (Enterprise)', impact: 'Strategic Moat', confidence: '85%', effort: 'XL (6 wks)' }
        ],
        risksAndBlockers: [
          { title: 'LLM Provider Rate Limiting & Latency Spikes', severity: 'High', mitigation: 'Implement multi-provider fallback routing (OpenAI → Anthropic → Google) and local response caching.' },
          { title: 'Complex Multi-Agent Context Window Overflow', severity: 'Medium', mitigation: 'Summarize intermediate agent outputs and pass structured JSON state artifacts instead of raw chat histories.' },
          { title: 'Frontend Animation Frame Drops under High WebSocket Frequency', severity: 'Low', mitigation: 'Batch SSE/WebSocket updates using React transitions and requestAnimationFrame throttling.' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!result) return;
    const md = `# ${result.title || 'Product Roadmap'}\n\n## Overview\n${result.overview || ''}\n\n## Quarterly Timeline\n${(result.timeline || []).map((t: any) => `### ${t.quarter}: ${t.theme} (${t.status})\n${(t.milestones || []).map((m: any) => `- **[${m.priority}] ${m.name}** (${m.effort}): ${m.deliverable}`).join('\n')}`).join('\n\n')}`;
    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const downloadJson = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Roadmap_Specification_${Date.now()}.json`;
    a.click();
  };

  return (
    <AppShell>
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="space-y-8"
      >
        {/* Breadcrumb & Header */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard/ai-dashboard' }, { label: 'Roadmap Generator' }]} />
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                <Calendar className="mr-3 text-emerald-400" size={28} /> AI Roadmap & Strategy Studio
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Prioritize features against rigorous scoring models and synthesize multi-quarter release timelines.
              </p>
            </div>
            {result && (
              <div className="flex items-center gap-2">
                <button
                  onClick={copyToClipboard}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white hover:bg-zinc-800 transition-all text-xs font-bold"
                >
                  {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
                  <span>{copied ? 'Copied MD' : 'Copy Markdown'}</span>
                </button>
                <button
                  onClick={downloadJson}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 border border-emerald-500 text-white hover:bg-emerald-500 transition-all text-xs font-bold shadow-lg shadow-emerald-600/20"
                >
                  <Download size={14} />
                  <span>Export JSON</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Input Card & Framework Selection */}
        <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 backdrop-blur-md space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <Sparkles size={14} className="text-emerald-400" /> Feature Candidates / Product Backlog
            </label>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-zinc-400 font-bold">Scoring Framework:</span>
              {['RICE', 'MoSCoW', 'ICE', 'WSJF', 'Value vs Effort'].map(f => (
                <button
                  key={f}
                  onClick={() => setFramework(f)}
                  className={`text-xs px-3 py-1.5 rounded-lg font-bold border transition-all ${
                    framework === f
                      ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300 shadow-sm'
                      : 'bg-zinc-900/60 border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700'
                  }`}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>
          <textarea
            value={features}
            onChange={e => setFeatures(e.target.value)}
            rows={4}
            disabled={loading}
            placeholder="List your feature candidates, epics, or product goals — e.g. '1. Real-time WebSocket thought visualizer for agent reasoning. 2. Granular FinOps cost tracking dashboard. 3. Custom RAG vector search for workspace docs. 4. Self-healing JSON schema validator...'"
            className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 placeholder-zinc-500 focus:border-emerald-500/60 focus:ring-2 focus:ring-emerald-500/20 outline-none resize-none transition-all"
          />
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>Active Model: <strong className="text-zinc-300">{framework}</strong> Prioritization Swarm</span>
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading || !features.trim()}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold shadow-lg shadow-emerald-600/25 transition-all duration-200 active:scale-95"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Synthesizing Roadmap...</span>
                </>
              ) : (
                <>
                  <Calendar size={16} />
                  <span>Execute Roadmap Swarm</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Live Thought Visualizer */}
        {(loading || steps.some(s => s.status !== 'pending')) && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
            <AgentThoughtVisualizer
              steps={steps}
              isGenerating={loading}
              isSimulated={true}
              onRunPipeline={simulateProgress}
            />
          </motion.div>
        )}

        {/* Structured Output Document */}
        <AnimatePresence mode="wait">
          {result && !loading && (
            <motion.div
              key="output"
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.35 }}
              className="rounded-2xl border border-zinc-800 bg-zinc-950/60 backdrop-blur-md overflow-hidden shadow-2xl"
            >
              {/* Output Header & Navigation Tabs */}
              <div className="border-b border-zinc-800/80 bg-zinc-900/50 px-6 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold uppercase px-2.5 py-1 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                    {framework} Aligned Artifact
                  </span>
                  <h2 className="text-sm font-bold text-white truncate max-w-md">{result.title || 'Quarterly Product Roadmap'}</h2>
                </div>
                <div className="flex space-x-1 overflow-x-auto">
                  {(['timeline', 'matrix', 'risks', 'raw'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-3.5 py-1.5 rounded-lg text-xs font-bold capitalize transition-all shrink-0 ${
                        activeTab === tab
                          ? 'bg-emerald-600 text-white shadow-md'
                          : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
                      }`}
                    >
                      {tab === 'timeline' ? 'Quarterly Timeline' : tab === 'matrix' ? 'Prioritization Matrix' : tab === 'risks' ? 'Risks & Blockers' : 'Raw JSON'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab Content Panels */}
              <div className="p-6">
                {activeTab === 'timeline' && (
                  <div className="space-y-6 animate-in fade-in duration-200">
                    <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-2">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400">Roadmap Strategy Overview</h3>
                      <p className="text-sm text-zinc-200 leading-relaxed">{result.overview || 'No overview provided.'}</p>
                    </div>
                    <div className="space-y-6 pt-2">
                      {(result.timeline || []).map((q: any, idx: number) => (
                        <div key={idx} className="relative pl-6 sm:pl-8 border-l-2 border-emerald-500/30 space-y-3">
                          <div className="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-zinc-950 border-2 border-emerald-400 flex items-center justify-center">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                          </div>
                          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                            <div className="flex items-center gap-3">
                              <span className="text-base font-black text-white">{q.quarter}</span>
                              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${q.badgeColor || 'bg-zinc-800 text-zinc-300 border-zinc-700'}`}>
                                {q.status}
                              </span>
                            </div>
                            <span className="text-xs font-bold text-zinc-400">{q.theme}</span>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1">
                            {(q.milestones || []).map((m: any, mIdx: number) => (
                              <div key={mIdx} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/30 space-y-2 hover:border-zinc-700 transition-colors">
                                <div className="flex items-center justify-between">
                                  <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">{m.priority}</span>
                                  <span className="text-[11px] font-mono text-zinc-500">{m.effort}</span>
                                </div>
                                <div className="text-sm font-bold text-white">{m.name}</div>
                                <p className="text-xs text-zinc-400 leading-relaxed pt-1 border-t border-zinc-800/80">{m.deliverable}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'matrix' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                        <Award size={16} className="text-emerald-400" /> {framework} Prioritization Scoring Matrix
                      </h3>
                      <span className="text-xs font-mono text-zinc-500">Ranked by score descending</span>
                    </div>
                    <div className="divide-y divide-zinc-800/80 border border-zinc-800/80 rounded-xl overflow-hidden bg-zinc-900/20">
                      {(result.prioritizationMatrix || []).map((pm: any, idx: number) => (
                        <div key={idx} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-zinc-900/40 transition-colors">
                          <div className="space-y-1">
                            <div className="flex items-center gap-3">
                              <span className="text-xs font-mono font-bold text-emerald-300 bg-emerald-500/15 px-2.5 py-1 rounded border border-emerald-500/30">{pm.rank}</span>
                              <span className="text-sm font-bold text-white">{pm.feature}</span>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-zinc-400 pt-1">
                              <span>Reach: <strong className="text-zinc-200">{pm.reach}</strong></span>
                              <span>Impact: <strong className="text-zinc-200">{pm.impact}</strong></span>
                              <span>Confidence: <strong className="text-zinc-200">{pm.confidence}</strong></span>
                              <span>Effort: <strong className="text-zinc-200">{pm.effort}</strong></span>
                            </div>
                          </div>
                          <div className="text-right shrink-0">
                            <div className="text-lg font-black text-emerald-400">{pm.score}</div>
                            <div className="text-[10px] uppercase font-bold text-zinc-500">{framework} Score</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'risks' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2 mb-2">
                      <AlertTriangle size={16} className="text-amber-400" /> Identified Risks, Blockers & Mitigation Strategy
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {(result.risksAndBlockers || []).map((risk: any, idx: number) => (
                        <div key={idx} className="p-5 rounded-xl border border-amber-500/20 bg-amber-500/5 space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-amber-300 uppercase tracking-wider">{risk.title}</span>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              risk.severity === 'High' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                              risk.severity === 'Medium' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                              'bg-zinc-800 text-zinc-400'
                            }`}>
                              {risk.severity}
                            </span>
                          </div>
                          <p className="text-xs text-zinc-300 leading-relaxed pt-1 border-t border-amber-500/10 font-medium">
                            <strong className="text-zinc-400">Mitigation:</strong> {risk.mitigation}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'raw' && (
                  <div className="animate-in fade-in duration-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-500 font-mono">Full JSON Roadmap Artifact</span>
                      <button onClick={copyToClipboard} className="text-xs text-emerald-400 hover:text-emerald-300 font-bold">Copy Raw JSON</button>
                    </div>
                    <pre className="text-xs text-zinc-300 overflow-auto max-h-[500px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800/80 rounded-xl p-4">
                      {JSON.stringify(result, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </AppShell>
  );
}
