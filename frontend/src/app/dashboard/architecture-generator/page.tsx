'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { AgentThoughtVisualizer, ThoughtStep } from '@/components/ui/agent-thought-visualizer';
import { Sparkles, Cpu, Check, Copy, Download, Layers, Database, Terminal, ShieldCheck, RefreshCw, Server, GitBranch, Target } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

const INITIAL_STEPS: ThoughtStep[] = [
  {
    id: '1',
    agentName: 'Technical Architect Agent',
    roleIcon: 'layers',
    status: 'pending',
    message: 'Evaluating stack tradeoffs, cloud providers & high-level design patterns...',
    timestamp: 'Just now',
    details: ['Evaluating monolithic vs microservice boundaries', 'Selecting primary language & framework ecosystem'],
  },
  {
    id: '2',
    agentName: 'Database Architect Agent',
    roleIcon: 'cpu',
    status: 'pending',
    message: 'Structuring entity-relationship schemas, indexing models, and migrations...',
    timestamp: 'Waiting...',
    details: ['Defining relational table keys & foreign constraints', 'Optimizing query paths & caching strategy'],
  },
  {
    id: '3',
    agentName: 'API & Microservice Architect Agent',
    roleIcon: 'terminal',
    status: 'pending',
    message: 'Synthesizing OpenAPI REST endpoints, authentication protocols & rate limits...',
    timestamp: 'Waiting...',
    details: ['Drafting request/response JSON payloads', 'Setting up JWT & OAuth2 middleware patterns'],
  },
  {
    id: '4',
    agentName: 'DevOps & Security Agent',
    roleIcon: 'brain',
    status: 'pending',
    message: 'Designing CI/CD pipelines, Docker container topology & OWASP compliance...',
    timestamp: 'Waiting...',
    details: ['Configuring Docker multi-stage builds', 'Applying zero-trust network boundaries'],
  },
  {
    id: '5',
    agentName: 'Cross-System Validation Agent',
    roleIcon: 'shield',
    status: 'pending',
    message: 'Cross-validating system scalability, latency budget & resilience targets...',
    timestamp: 'Waiting...',
    details: ['Verifying horizontal scale limits', 'Finalizing exportable architecture specification'],
  },
];

export default function ArchitectureGeneratorPage() {
  const { activeWorkspace } = useAuth();
  const [requirements, setRequirements] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [steps, setSteps] = React.useState<ThoughtStep[]>(INITIAL_STEPS);
  const [activeTab, setActiveTab] = React.useState<'topology' | 'database' | 'api' | 'devops' | 'raw'>('topology');
  const [copied, setCopied] = React.useState(false);

  const simulateProgress = async () => {
    setSteps(INITIAL_STEPS.map((s, idx) => idx === 0 ? { ...s, status: 'active', timestamp: 'In progress' } : s));

    for (let i = 0; i < INITIAL_STEPS.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 850 + Math.random() * 600));
      setSteps(prev => prev.map((s, idx) => {
        if (idx === i) {
          return {
            ...s,
            status: 'completed',
            timestamp: `${(1.2 + idx * 0.8).toFixed(1)}s`,
            metrics: { latencyMs: Math.round(950 + Math.random() * 600), tokensUsed: Math.round(520 + idx * 310), confidence: 0.97 + idx * 0.005 }
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
    if (!activeWorkspace || !requirements.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    setActiveTab('topology');

    const progressPromise = simulateProgress();

    try {
      const data = await apiService.post<any>('/ai/workflows/execute', {
        workflow_name: 'architecture_design',
        workspace_id: activeWorkspace.id,
        context: { idea: requirements },
      });
      const rawResult = data.result || data;
      const architecture = rawResult.architecture || {};
      const database = rawResult.database || {};
      const api = rawResult.api || {};
      
      const mapped = {
        title: activeWorkspace.name + ' System Architecture Spec',
        overview: architecture.system_architecture || architecture.application_architecture || 'System architecture overview.',
        techStack: [
          { layer: 'Application Framework', technology: 'FastAPI (Python)', rationale: 'High performance asynchronous web framework with native Pydantic validation.' },
          { layer: 'Frontend client', technology: 'Next.js (React & TypeScript)', rationale: 'Server-side rendering, robust component ecosystem, and static generation.' },
          { layer: 'Primary Database', technology: 'PostgreSQL', rationale: 'ACID compliant relational storage with powerful indexing and JSONB support.' },
          { layer: 'Cache / Queue', technology: 'Redis', rationale: 'In-memory cache for distributed session handling and background task queues.' }
        ],
        databaseEntities: (database.entities || []).map((e: any) => ({
          name: e.name || 'Entity',
          fields: (e.attributes || []).map((attr: any) => `${attr.name || attr.field}: ${attr.type || 'string'}`),
          indexes: (database.indexes || [])
            .filter((idx: any) => idx.entity === e.name || idx.table === e.name)
            .map((idx: any) => idx.name || 'IDX_' + e.name)
        })),
        apiEndpoints: (api.endpoints || []).map((ep: any) => ({
          method: ep.method || 'GET',
          path: ep.path || '/api/v1',
          auth: ep.auth_required ? 'JWT Bearer' : 'Public',
          summary: ep.summary || 'REST API Endpoint',
          latencyTarget: '200ms'
        })),
        devopsControls: (architecture.security_architecture || []).map((sec: string) => ({
          category: 'Security Architecture',
          control: sec
        })).concat([
          { category: 'CI/CD Pipeline', control: 'Automated GitHub Actions pipeline building Docker images and validating unit tests.' },
          { category: 'Containerization', control: 'Docker Compose orchestration mapping database, caching, and core application services.' }
        ])
      };
      await progressPromise;
      setResult(mapped);
    } catch (e: any) {
      await progressPromise;
      setError(e.message || 'An error occurred during architecture generation');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    if (!result) return;
    const md = `# ${result.title || 'System Architecture Document'}\n\n## Overview\n${result.overview || ''}\n\n## Tech Stack\n${(result.techStack || []).map((t: any) => `- **${t.layer}**: ${t.technology} (${t.rationale})`).join('\n')}`;
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
    a.download = `Architecture_Specification_${Date.now()}.json`;
    a.click();
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="text-center py-20">
          <Target className="mx-auto text-zinc-600 mb-4 animate-bounce" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view your autonomous architecture studio.</p>
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
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard/ai-dashboard' }, { label: 'Architecture Generator' }]} />
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                <Cpu className="mr-3 text-violet-400" size={28} /> AI Architecture Generator Studio
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Autonomous system design, database schema modeling, and OpenAPI endpoint synthesis.
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
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-violet-600 border border-violet-500 text-white hover:bg-violet-500 transition-all text-xs font-bold shadow-lg shadow-violet-600/20"
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

        {/* Requirements Input Card */}
        <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <Sparkles size={14} className="text-violet-400" /> System Specs / PRD Requirements
            </label>
            <span className="text-[11px] text-zinc-500 font-mono">Input technical constraints or feature lists</span>
          </div>
          <textarea
            value={requirements}
            onChange={e => setRequirements(e.target.value)}
            rows={4}
            disabled={loading}
            placeholder="Describe the technical requirements or system goals — e.g. 'A real-time multi-agent AI product management platform requiring high-concurrency WebSocket telemetry, PostgreSQL vector search for document RAG, and strict RBAC authorization boundaries across 24 autonomous agents...'"
            className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 placeholder-zinc-500 focus:border-violet-500/60 focus:ring-2 focus:ring-violet-500/20 outline-none resize-none transition-all"
          />
          <div className="flex items-center justify-between pt-1">
            <div className="flex items-center gap-2 text-xs text-zinc-500">
              <span className="w-2 h-2 rounded-full bg-violet-500" />
              <span>Pipeline: Tech Stack → Database Schema → API Endpoints → DevOps → Cross-Validation</span>
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading || !requirements.trim()}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-bold shadow-lg shadow-violet-600/25 transition-all duration-200 active:scale-95"
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="animate-spin" />
                  <span>Synthesizing Architecture...</span>
                </>
              ) : (
                <>
                  <Cpu size={16} />
                  <span>Execute Architecture Swarm</span>
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
                  <span className="text-xs font-mono font-bold uppercase px-2.5 py-1 rounded bg-violet-500/10 border border-violet-500/20 text-violet-400">
                    Validated Architecture Artifact
                  </span>
                  <h2 className="text-sm font-bold text-white truncate max-w-md">{result.title || 'System Architecture Document'}</h2>
                </div>
                <div className="flex space-x-1 overflow-x-auto">
                  {(['topology', 'database', 'api', 'devops', 'raw'] as const).map(tab => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`px-3.5 py-1.5 rounded-lg text-xs font-bold capitalize transition-all shrink-0 ${
                        activeTab === tab
                          ? 'bg-violet-600 text-white shadow-md'
                          : 'text-zinc-400 hover:text-white hover:bg-zinc-800/60'
                      }`}
                    >
                      {tab === 'topology' ? 'Tech Stack & Topology' : tab === 'database' ? 'Database Schema' : tab === 'api' ? 'OpenAPI Endpoints' : tab === 'devops' ? 'DevOps & Security' : 'Raw JSON'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tab Content Panels */}
              <div className="p-6">
                {activeTab === 'topology' && (
                  <div className="space-y-6 animate-in fade-in duration-200">
                    <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800/80 space-y-2">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-violet-400">System Design Overview</h3>
                      <p className="text-sm text-zinc-200 leading-relaxed">{result.overview || 'No overview provided.'}</p>
                    </div>
                    <div className="space-y-3">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                        <Server size={16} className="text-indigo-400" /> Technology Layers & Rationale
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {(result.techStack || []).map((t: any, idx: number) => (
                          <div key={idx} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/30 space-y-2 hover:border-zinc-700 transition-colors">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-violet-300 bg-violet-500/10 px-2.5 py-1 rounded border border-violet-500/20">{t.layer}</span>
                            </div>
                            <div className="text-sm font-extrabold text-white">{t.technology}</div>
                            <p className="text-xs text-zinc-400 leading-relaxed pt-1 border-t border-zinc-800/80">{t.rationale}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'database' && (
                  <div className="space-y-4 animate-in fade-in duration-200">
                    <div className="flex items-center justify-between">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                        <Database size={16} className="text-amber-400" /> Relational Entity Models & Indexes
                      </h3>
                      <span className="text-xs font-mono text-zinc-500">{(result.databaseEntities || []).length} tables defined</span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {(result.databaseEntities || []).map((ent: any, idx: number) => (
                        <div key={idx} className="p-5 rounded-xl border border-amber-500/20 bg-amber-500/5 space-y-3 flex flex-col justify-between">
                          <div className="space-y-2">
                            <div className="text-sm font-bold text-white flex items-center gap-2">
                              <Database size={14} className="text-amber-400" />
                              <span>{ent.name}</span>
                            </div>
                            <div className="space-y-1 pt-2 border-t border-amber-500/10">
                              {(ent.fields || []).map((f: string, fIdx: number) => (
                                <div key={fIdx} className="text-[11px] font-mono text-zinc-300 bg-zinc-950/60 px-2.5 py-1 rounded border border-zinc-800/60">
                                  {f}
                                </div>
                              ))}
                            </div>
                          </div>
                          <div className="pt-2 border-t border-amber-500/10 text-[10px] font-mono text-amber-400/80">
                            Indexes: {(ent.indexes || []).join(', ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'api' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                        <Terminal size={16} className="text-emerald-400" /> REST & OpenAPI Endpoint Matrix
                      </h3>
                      <span className="text-xs font-mono text-zinc-500">{(result.apiEndpoints || []).length} endpoints synthesized</span>
                    </div>
                    <div className="divide-y divide-zinc-800/80 border border-zinc-800/80 rounded-xl overflow-hidden bg-zinc-900/20">
                      {(result.apiEndpoints || []).map((api: any, idx: number) => (
                        <div key={idx} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-zinc-900/40 transition-colors">
                          <div className="space-y-1.5 flex-1">
                            <div className="flex items-center gap-3">
                              <span className={`px-2.5 py-0.5 rounded text-xs font-mono font-bold ${
                                api.method === 'POST' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                                api.method === 'GET' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                                'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              }`}>
                                {api.method}
                              </span>
                              <span className="text-sm font-mono font-bold text-white">{api.path}</span>
                              <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">{api.auth}</span>
                            </div>
                            <p className="text-xs text-zinc-400 leading-relaxed max-w-2xl">{api.summary}</p>
                          </div>
                          <div className="text-right shrink-0">
                            <span className="text-[11px] font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
                              Target: {api.latencyTarget}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'devops' && (
                  <div className="space-y-3 animate-in fade-in duration-200">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2 mb-2">
                      <ShieldCheck size={16} className="text-rose-400" /> DevOps & Zero-Trust Security Controls
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {(result.devopsControls || []).map((ctrl: any, idx: number) => (
                        <div key={idx} className="p-5 rounded-xl border border-rose-500/20 bg-rose-500/5 space-y-2">
                          <div className="text-xs font-bold text-rose-300 uppercase tracking-wider">{ctrl.category}</div>
                          <p className="text-xs text-zinc-300 leading-relaxed pt-1 border-t border-rose-500/10">{ctrl.control}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {activeTab === 'raw' && (
                  <div className="animate-in fade-in duration-200 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-zinc-500 font-mono">Full JSON Architecture Artifact</span>
                      <button onClick={copyToClipboard} className="text-xs text-violet-400 hover:text-violet-300 font-bold">Copy Raw JSON</button>
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
