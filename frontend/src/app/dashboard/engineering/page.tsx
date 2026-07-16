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
  Cpu,
  Check,
  Copy,
  Download,
  Layers,
  Database,
  Terminal,
  ShieldCheck,
  RefreshCw,
  Server,
  Code2,
  CheckSquare,
  Award,
  Shield
} from 'lucide-react';

const ARCHITECTURE_STEPS: ThoughtStep[] = [
  {
    id: '1',
    agentName: 'System Architecture Swarm',
    roleIcon: 'layers',
    status: 'pending',
    message: 'Analyzing system requirements and drafting topology design...',
    timestamp: 'Just now',
    details: ['Identifying service boundaries', 'Structuring database constraints']
  }
];

export default function UnifiedEngineeringSuitePage() {
  const { activeWorkspace } = useAuth();
  
  // Tab State
  const [activeTab, setActiveTab] = React.useState<'architecture' | 'techstack' | 'sandbox' | 'testing' | 'deployment'>('architecture');
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  
  // Requirement inputs
  const [requirementsInput, setRequirementsInput] = React.useState('');
  
  // Data states
  const [architectureData, setArchitectureData] = React.useState<any>(null);
  const [techStackData, setTechStackData] = React.useState<any>(null);
  const [testingData, setTestingData] = React.useState<any>(null);
  const [deploymentData, setDeploymentData] = React.useState<any>(null);
  const [copied, setCopied] = React.useState(false);

  // Sync tab from URL query param
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tab = params.get('tab');
      if (tab === 'architecture' || tab === 'techstack' || tab === 'sandbox' || tab === 'testing' || tab === 'deployment') {
        setActiveTab(tab);
      }
    }
  }, []);

  React.useEffect(() => {
    if (activeWorkspace) {
      setRequirementsInput(activeWorkspace.description || `A system named ${activeWorkspace.name}`);
    }
  }, [activeWorkspace]);

  // Generators
  const handleGenerateArchitecture = async () => {
    if (!activeWorkspace || !requirementsInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.post<any>('/ai/workflows/execute', {
        workflow_name: 'architecture_design',
        workspace_id: activeWorkspace.id,
        context: { idea: requirementsInput },
      });
      const raw = data.result || data;
      const r = raw.architecture || {};
      const database = raw.database || {};
      const api = raw.api || {};
      
      const mapped = {
        title: activeWorkspace.name + ' System Architecture Spec',
        overview: r.system_architecture || r.application_architecture || 'System architecture overview.',
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
        devopsControls: (r.security_architecture || []).map((sec: string) => ({
          category: 'Security Architecture',
          control: sec
        })).concat([
          { category: 'CI/CD Pipeline', control: 'Automated GitHub Actions pipeline building Docker images and validating unit tests.' },
          { category: 'Containerization', control: 'Docker Compose orchestration mapping database, caching, and core application services.' }
        ])
      };
      setArchitectureData(mapped);
    } catch (e: any) {
      setError(e.message || 'Failed to generate architecture');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTechStack = async () => {
    if (!activeWorkspace || !requirementsInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'architecture_generator',
        workspace_id: activeWorkspace.id,
        input_data: { requirements: requirementsInput }
      });
      setTechStackData(data.result || data);
    } catch (e: any) {
      setError(e.message || 'Failed to generate tech stack blueprint');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTesting = async () => {
    if (!activeWorkspace || !requirementsInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'testing_strategy',
        workspace_id: activeWorkspace.id,
        input_data: { project_description: requirementsInput }
      });
      setTestingData(data.result || data);
    } catch (e: any) {
      setError(e.message || 'Failed to generate testing plan');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateDeployment = async () => {
    if (!activeWorkspace || !requirementsInput.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'deployment_guide',
        workspace_id: activeWorkspace.id,
        input_data: { project_description: requirementsInput }
      });
      setDeploymentData(data.result || data);
    } catch (e: any) {
      setError(e.message || 'Failed to generate deployment configuration');
    } finally {
      setLoading(false);
    }
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
          <Terminal className="text-zinc-600 animate-pulse" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm max-w-sm">
            Choose or create a workspace to view your autonomous engineering suite.
          </p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Section */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Engineering Suite' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center gap-3">
            <Code2 className="text-violet-400" size={28} /> AI Engineering & Architecture Suite
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Synthesize database DDL files, backend OpenAPI interfaces, automated testing plans, and deployment pipeline guides.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex border-b border-zinc-900 pb-px gap-2 overflow-x-auto">
          {(['architecture', 'techstack', 'sandbox', 'testing', 'deployment'] as const).map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 transition-all whitespace-nowrap ${
                activeTab === tab
                  ? 'border-violet-500 text-violet-400'
                  : 'border-transparent text-zinc-500 hover:text-zinc-300'
              }`}
            >
              {tab === 'architecture' ? 'System Topology' : tab === 'techstack' ? 'Tech Stack selection' : tab === 'sandbox' ? 'DDL Sandbox' : tab === 'testing' ? 'QA & Testing' : 'CI/CD deployment'}
            </button>
          ))}
        </div>

        {/* Input Scope section */}
        <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
          <div className="flex justify-between items-center text-xs">
            <span className="font-bold text-zinc-300 uppercase tracking-wider flex items-center gap-2">
              <Sparkles size={14} className="text-violet-400" /> Engineering Specifications
            </span>
          </div>
          <textarea
            value={requirementsInput}
            onChange={e => setRequirementsInput(e.target.value)}
            rows={3}
            className="w-full bg-zinc-900 border border-zinc-850 rounded-xl p-3 text-sm text-zinc-200 focus:outline-none focus:border-violet-500/40"
            placeholder="E.g. A real-time chat gateway needing Redis PubSub queue, Postgres model, and Playwright verification tests..."
          />
          <div className="flex justify-end gap-2">
            {activeTab === 'architecture' && (
              <button onClick={handleGenerateArchitecture} disabled={loading} className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-bold uppercase transition">
                {loading ? 'Synthesizing Spec...' : 'Execute Topology Swarm'}
              </button>
            )}
            {activeTab === 'techstack' && (
              <button onClick={handleGenerateTechStack} disabled={loading} className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-bold uppercase transition">
                {loading ? 'Designing Stack...' : 'Architect Tech Stack'}
              </button>
            )}
            {activeTab === 'testing' && (
              <button onClick={handleGenerateTesting} disabled={loading} className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-bold uppercase transition">
                {loading ? 'Drafting QA plan...' : 'Generate Test Strategy'}
              </button>
            )}
            {activeTab === 'deployment' && (
              <button onClick={handleGenerateDeployment} disabled={loading} className="px-4 py-2 bg-violet-600 hover:bg-violet-500 text-white rounded-lg text-xs font-bold uppercase transition">
                {loading ? 'Building Guides...' : 'Generate Deployment Blueprint'}
              </button>
            )}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-rose-950/20 border border-rose-900/50 rounded-xl text-rose-400 text-xs">
            {error}
          </div>
        )}

        {/* TAB CONTENTS */}
        <div className="space-y-6">
          {/* TAB 1: Architecture topology */}
          {activeTab === 'architecture' && (
            <div className="space-y-6">
              {architectureData ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
                  <div className="lg:col-span-3 p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-violet-400">System Design Overview</h3>
                    <p className="text-xs text-zinc-300 leading-relaxed">{architectureData.overview}</p>
                  </div>

                  <div className="lg:col-span-2 p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                      <Terminal size={14} className="text-emerald-400" /> Rest OpenAPI Endpoints
                    </h3>
                    <div className="space-y-3">
                      {architectureData.apiEndpoints?.map((api: any, idx: number) => (
                        <div key={idx} className="p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg flex items-center justify-between text-xs">
                          <div className="flex items-center gap-3">
                            <span className="px-2 py-0.5 rounded bg-zinc-950 border border-zinc-900 font-mono text-[9px] font-bold text-violet-400">{api.method}</span>
                            <span className="font-mono text-white font-semibold">{api.path}</span>
                          </div>
                          <span className="text-[10px] text-zinc-550">{api.summary}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                      <ShieldCheck size={14} className="text-rose-455" /> Security & Architecture Controls
                    </h3>
                    <div className="space-y-3 text-xs text-zinc-300">
                      {architectureData.devopsControls?.slice(0, 4).map((ctrl: any, idx: number) => (
                        <div key={idx} className="p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg">
                          <strong className="text-[9px] uppercase tracking-wider block text-rose-400 mb-1">{ctrl.category}</strong>
                          {ctrl.control}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                  Execute architecture swarm to view high-level system topology designs.
                </div>
              )}
            </div>
          )}

          {/* TAB 2: Tech stack */}
          {activeTab === 'techstack' && (
            <div className="space-y-6">
              {techStackData ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in duration-200">
                  <CardWrapper title="Architecture Summary">
                    <p className="text-xs text-zinc-300 leading-relaxed">{techStackData.system_architecture}</p>
                  </CardWrapper>

                  <CardWrapper title="Technology Layers">
                    <div className="grid grid-cols-1 gap-3">
                      {(techStackData.microservice_recommendation || []).map((svc: any, idx: number) => (
                        <div key={idx} className="p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg space-y-1">
                          <span className="text-[10px] font-bold text-violet-300 uppercase">{svc.service || svc.layer || 'Service'}</span>
                          <div className="text-xs font-bold text-white">{svc.technology}</div>
                          <p className="text-[11px] text-zinc-400">{svc.rationale}</p>
                        </div>
                      ))}
                    </div>
                  </CardWrapper>
                </div>
              ) : (
                <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                  Run Tech Stack Architect to design project frameworks and microservice boundaries.
                </div>
              )}
            </div>
          )}

          {/* TAB 3: Sandbox/DDL preview */}
          {activeTab === 'sandbox' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-in fade-in duration-200">
              {architectureData?.databaseEntities?.length > 0 ? (
                <>
                  <div className="lg:col-span-1 p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4 max-h-[500px] overflow-y-auto">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Database Entities</h3>
                    <div className="space-y-2">
                      {architectureData.databaseEntities.map((ent: any, idx: number) => (
                        <div key={idx} className="p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg space-y-2 text-xs">
                          <div className="font-bold text-white flex items-center gap-1.5">
                            <Database size={12} className="text-amber-400" />
                            <span>{ent.name}</span>
                          </div>
                          <div className="space-y-1 text-[10px] text-zinc-400 font-mono">
                            {ent.fields.map((f: string, fIdx: number) => (
                              <div key={fIdx}>{f}</div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="lg:col-span-2 p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Generated SQL / DDL Schema Preview</h3>
                    <div className="p-4 bg-zinc-900 border border-zinc-850 rounded-lg text-[11px] font-mono text-zinc-350 leading-relaxed overflow-x-auto whitespace-pre">
                      {architectureData.databaseEntities.map((ent: any) => {
                        return `CREATE TABLE ${ent.name.toLowerCase()} (\n` +
                          `  id SERIAL PRIMARY KEY,\n` +
                          ent.fields.map((f: string) => `  ${f.replace(':', '').toLowerCase()}`).join(',\n') +
                          `\n);\n\n` +
                          ent.indexes.map((idx: string) => `CREATE INDEX ${idx.toLowerCase()} ON ${ent.name.toLowerCase()}(id);`).join('\n') + '\n\n';
                      }).join('')}
                    </div>
                  </div>
                </>
              ) : (
                <div className="lg:col-span-3 text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                  Run system topology swarm first to populate tables and DDL schema previews.
                </div>
              )}
            </div>
          )}

          {/* TAB 4: QA & Testing Strategy */}
          {activeTab === 'testing' && (
            <div className="space-y-6 animate-in fade-in duration-200">
              {testingData ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400 flex items-center gap-2">
                      <CheckSquare size={14} className="text-indigo-400" /> QA Test Suites
                    </h3>
                    <div className="divide-y divide-zinc-900 border border-zinc-900 rounded-lg overflow-hidden bg-zinc-950/40">
                      {testingData.test_suites?.map((suite: any, idx: number) => (
                        <div key={idx} className="p-4 flex items-center justify-between text-xs">
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-[9px] font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded">{suite.test_type}</span>
                              <span className="font-bold text-white">{suite.test_name}</span>
                            </div>
                            <p className="text-[11px] text-zinc-400 mt-1">{suite.description}</p>
                          </div>
                          <span className="text-[9px] uppercase font-bold text-zinc-500">{suite.priority}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Coverage & Tooling Targets</h3>
                    <div className="space-y-4 text-xs">
                      <div>
                        <strong className="text-zinc-400 block mb-1">Recommended Stack</strong>
                        <p className="text-zinc-350">{testingData.tools_recommended?.join(', ')}</p>
                      </div>
                      <div className="border-t border-zinc-900 pt-3">
                        <strong className="text-zinc-400 block mb-2">Coverage Thresholds</strong>
                        {testingData.coverage_targets && Object.entries(testingData.coverage_targets).map(([k, v]: any) => (
                          <div key={k} className="flex justify-between py-1 border-b border-zinc-900/60 text-zinc-300">
                            <span>{k}</span>
                            <span className="font-bold text-indigo-400">{v}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                  Execute Test Strategy Generator to calculate test pyramid metrics and suites.
                </div>
              )}
            </div>
          )}

          {/* TAB 5: Deployment runner */}
          {activeTab === 'deployment' && (
            <div className="space-y-6 animate-in fade-in duration-200">
              {deploymentData ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2 p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">CI/CD Pipeline Stages</h3>
                    <div className="space-y-3">
                      {deploymentData.ci_cd_pipeline?.map((stage: any, idx: number) => (
                        <div key={idx} className="p-3 bg-zinc-900/40 border border-zinc-850 rounded-lg space-y-2 text-xs">
                          <span className="font-bold text-violet-400 uppercase tracking-wider text-[10px]">Stage {idx + 1}: {stage.stage_name}</span>
                          <p className="text-zinc-300">{stage.description}</p>
                          <pre className="p-2.5 bg-zinc-950 border border-zinc-900 rounded font-mono text-[10px] text-zinc-400 overflow-x-auto whitespace-pre">
                            {stage.commands?.join('\n') || '# no command tags'}
                          </pre>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="p-5 rounded-xl bg-zinc-950 border border-zinc-900 space-y-4">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">Security & Zero-Trust Checklist</h3>
                    <ul className="space-y-2 text-xs text-zinc-300 list-disc list-inside">
                      {deploymentData.security_checklist?.map((item: string, idx: number) => (
                        <li key={idx} className="leading-relaxed">{item}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ) : (
                <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                  Run deployment guide pipelines to view dockerfiles and CI/CD targets.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function CardWrapper({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="p-5 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-3">
      <h3 className="text-xs font-bold uppercase tracking-wider text-zinc-400">{title}</h3>
      {children}
    </div>
  );
}
