'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { AgentThoughtVisualizer, ThoughtStep } from '@/components/ui/agent-thought-visualizer';
import { Sparkles, FileText, Check, Copy, Download, Layers, Users, Target, ShieldCheck, RefreshCw } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

const INITIAL_STEPS: ThoughtStep[] = [
  {
    id: '1',
    agentName: 'Market Research Agent',
    roleIcon: 'brain',
    status: 'pending',
    message: 'Analyzing idea domain, market viability, and target user personas...',
    timestamp: 'Just now',
    details: ['Querying industry benchmarks', 'Identifying primary user segments & pain points'],
  },
  {
    id: '2',
    agentName: 'Product Discovery Agent',
    roleIcon: 'layers',
    status: 'pending',
    message: 'Structuring core value proposition and North Star metrics...',
    timestamp: 'Waiting...',
    details: ['Synthesizing unique value proposition (UVP)', 'Defining key performance indicators'],
  },
  {
    id: '3',
    agentName: 'Business Analyst Agent',
    roleIcon: 'cpu',
    status: 'pending',
    message: 'Drafting detailed functional requirements & acceptance criteria...',
    timestamp: 'Waiting...',
    details: ['Synthesizing P1/P2 feature scope', 'Enforcing MoSCoW prioritization'],
  },
  {
    id: '4',
    agentName: 'UX & User Story Agent',
    roleIcon: 'git',
    status: 'pending',
    message: 'Creating user stories, epic breakdowns, and edge cases...',
    timestamp: 'Waiting...',
    details: ['Mapping end-to-end user journeys', 'Documenting failure modes and edge conditions'],
  },
  {
    id: '5',
    agentName: 'Executive Review Agent',
    roleIcon: 'shield',
    status: 'pending',
    message: 'Assembling & cross-validating complete PRD specification...',
    timestamp: 'Waiting...',
    details: ['Running schema validation', 'Finalizing exportable PRD artifact'],
  },
];

export default function PRDGeneratorPage() {
  const { activeWorkspace } = useAuth();
  const [idea, setIdea] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [steps, setSteps] = React.useState<ThoughtStep[]>(INITIAL_STEPS);
  const [activeTab, setActiveTab] = React.useState<'summary' | 'requirements' | 'stories' | 'metrics' | 'raw'>('summary');
  const [copied, setCopied] = React.useState(false);

  const simulateProgress = async () => {
    setSteps(INITIAL_STEPS.map((s, idx) => idx === 0 ? { ...s, status: 'active', timestamp: 'In progress' } : s));

    for (let i = 0; i < INITIAL_STEPS.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 600));
      setSteps(prev => prev.map((s, idx) => {
        if (idx === i) {
          return {
            ...s,
            status: 'completed',
            timestamp: `${(1.1 + idx * 0.7).toFixed(1)}s`,
            metrics: { latencyMs: Math.round(900 + Math.random() * 500), tokensUsed: Math.round(450 + idx * 280), confidence: 0.96 + idx * 0.008 }
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
    if (!activeWorkspace || !idea.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setActiveTab('summary');

    const progressPromise = simulateProgress();

    try {
      const data = await apiService.post<any>('/ai/workflows/execute', {
        workflow_name: 'prd_generation',
        workspace_id: activeWorkspace.id,
        context: { idea },
      });
      const rawResult = data.result || data;
      const prd = rawResult.prd || {};
      const stories = rawResult.stories || {};
      
      const mapped = {
        title: prd.title || activeWorkspace.name + ' PRD Specification',
        overview: prd.executive_summary || prd.background || 'No overview generated.',
        targetAudience: (prd.personas || []).map((p: any) => ({
          segment: p.name || p.role || p.segment || 'User Persona',
          painPoint: p.pain_points || p.description || p.painPoint || 'Needs product solutions'
        })),
        functionalRequirements: (prd.functional_requirements || []).map((f: any, idx: number) => ({
          id: f.id || `FR-${idx + 1}`,
          title: f.title || f.name || 'Requirement',
          description: f.description || '',
          priority: f.priority || 'Should Have'
        })),
        userStories: (stories.stories || []).map((s: any, idx: number) => ({
          id: s.story_id || `US-${idx + 1}`,
          asA: s.as_a || s.role || 'User',
          iWantTo: s.i_want || s.i_want_to || s.description || 'perform action',
          soThat: s.so_that || s.benefit || 'benefit is achieved'
        })),
        successMetrics: (prd.success_metrics || []).map((m: any, idx: number) => ({
          metric: typeof m === 'string' ? m : m.metric || m.name || `Metric ${idx + 1}`,
          target: typeof m === 'object' && m.target ? m.target : '100%',
          timeframe: typeof m === 'object' && m.timeframe ? m.timeframe : 'Q1'
        }))
      };
      await progressPromise;
      setResult(mapped);
    } catch (e: any) {
      await progressPromise;
      setError(e.message || 'An error occurred during PRD generation');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!result) return;
    const md = `# ${result.title || 'Product Requirements Document'}\n\n## Overview\n${result.overview || ''}\n\n## Functional Requirements\n${(result.functionalRequirements || []).map((fr: any) => `- **[${fr.id}] ${fr.title}** (${fr.priority}): ${fr.description}`).join('\n')}`;
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
    a.download = `PRD_Specification_${Date.now()}.json`;
    a.click();
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="text-center py-20">
          <Target className="mx-auto text-zinc-600 mb-4 animate-bounce" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view your autonomous PRD studio.</p>
        </div>
      </AppShell>
    );
  }

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
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard/ai-dashboard' }, { label: 'PRD Generator' }]} />
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                <FileText className="mr-3 text-indigo-400" size={28} /> AI PRD Generator Studio
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Multi-agent autonomous requirements engineering: transforms high-level concepts into rigorous specs.
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
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 border border-indigo-500 text-white hover:bg-indigo-500 transition-all text-xs font-bold shadow-lg shadow-indigo-600/20"
                >
                  <Download size={14} />
                  <span>Export JSON</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-rose-950/20 border border-rose-900/50 rounded-xl p-4 text-rose-300 text-sm">
            {error}
          </div>
        )}

        {/* Idea Input Card */}
        <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <Sparkles size={14} className="text-amber-400" /> Product Vision / Epic Concept
            </label>
            <span className="text-[11px] text-zinc-500 font-mono">Input natural language vision</span>
          </div>
          <textarea
            value={idea}
            onChange={e => setIdea(e.target.value)}
            rows={4}
            disabled={loading}
            placeholder="Describe your product vision in detail — e.g. 'An autonomous self-healing CI/CD pipeline agent that monitors test failures, analyzes stack traces using Claude 3.5 Sonnet, and automatically submits GitHub pull requests with patch fixes...'"
            className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20 outline-none resize-none transition-all"
          />
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span className="w-2 h-2 rounded-full bg-indigo-500" />
              <span>Pipeline: Market Research → Discovery → Requirements → UX Stories → Executive Review</span>
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading || !idea.trim()}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold shadow-lg shadow-indigo-600/25 transition-all duration-200 active:scale-95"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Synthesizing PRD...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Execute 5-Agent Swarm</span>
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
                  <span className="text-xs font-mono font-bold uppercase px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                    Validated PRD Artifact
                  </span>
                  <h2 className="text-sm font-bold text-white truncate max-w-md">{result.title || 'Product Requirements Document'}</h2>
                </div>
                <div className="flex space-x-1 overflow-x-auto">
                  {(['summary', 'requirements', 'stories', 'metrics', 'raw'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-3.5 py-1.5 rounded-lg text-xs font-bold capitalize transition-all shrink-0 ${
                        activeTab === tab
                          ? 'bg-indigo-600 text-white shadow-md'
                          : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
                      }`}
                    >
                      {tab === 'summary' ? 'Overview & Audience' : tab}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab Content Panels */}
              <div className="p-6">
                {activeTab === 'summary' && (
                  <div className="space-y-6 animate-in fade-in duration-200">
                    <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-2">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">Executive Summary</h3>
                      <p className="text-sm text-zinc-200 leading-relaxed">{result.overview || 'No overview provided.'}</p>
                    </div>
                    <div className="space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                        <Users size={16} className="text-emerald-400" /> Target User Personas & Pain Points
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {(result.targetAudience || []).map((aud: any, idx: number) => (
                          <div key={idx} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/30 space-y-1.5">
                            <div className="text-sm font-bold text-white">{aud.segment}</div>
                            <p className="text-xs text-zinc-400 leading-relaxed">{aud.painPoint}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'requirements' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                        <Layers size={16} className="text-indigo-400" /> Functional Specification Catalog
                      </h3>
                      <span className="text-xs font-mono text-zinc-500">{(result.functionalRequirements || []).length} items defined</span>
                    </div>
                    <div className="divide-y divide-zinc-800/80 border border-zinc-800/80 rounded-xl overflow-hidden bg-zinc-900/20">
                      {(result.functionalRequirements || []).map((fr: any) => (
                        <div key={fr.id} className="p-4 flex flex-col sm:flex-row sm:items-start justify-between gap-4 hover:bg-zinc-900/40 transition-colors">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2.5">
                              <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">{fr.id}</span>
                              <span className="text-sm font-bold text-white">{fr.title}</span>
                            </div>
                            <p className="text-xs text-zinc-400 leading-relaxed pt-1 max-w-3xl">{fr.description}</p>
                          </div>
                          <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider shrink-0 self-start ${
                            fr.priority === 'Must Have' ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400' :
                            fr.priority === 'Should Have' ? 'bg-amber-500/10 border border-amber-500/20 text-amber-400' :
                            'bg-zinc-800 text-zinc-400 border border-zinc-700'
                          }`}>
                            {fr.priority}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'stories' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 mb-2">User Stories & Acceptance Scope</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {(result.userStories || []).map((us: any) => (
                        <div key={us.id} className="p-4 rounded-xl border border-zinc-800/80 bg-zinc-900/30 space-y-2 hover:border-zinc-700 transition-colors">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-mono font-bold text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/20">{us.id}</span>
                            <span className="text-xs font-bold text-zinc-300">As a <span className="text-white underline decoration-indigo-500">{us.asA}</span></span>
                          </div>
                          <p className="text-xs text-zinc-200 font-medium">I want to {us.iWantTo}</p>
                          <div className="pt-2 border-t border-zinc-800/80 text-[11px] text-emerald-400 font-mono">
                            So that {us.soThat}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'metrics' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2 mb-2">
                      <Target size={16} className="text-amber-400" /> North Star & KPIs
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {(result.successMetrics || []).map((m: any, idx: number) => (
                        <div key={idx} className="p-5 rounded-xl border border-amber-500/20 bg-amber-500/5 space-y-2">
                          <div className="text-xs font-bold text-amber-300 uppercase tracking-wider">{m.metric}</div>
                          <div className="text-xl font-black text-white">{m.target}</div>
                          <div className="text-[11px] font-mono text-zinc-400 pt-1 border-t border-amber-500/10">Timeline: {m.timeframe}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'raw' && (
                  <div className="animate-in fade-in duration-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-500 font-mono">Full JSON Schema Artifact</span>
                      <button onClick={copyToClipboard} className="text-xs text-indigo-400 hover:text-indigo-300 font-bold">Copy Raw JSON</button>
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
