'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';

interface AgentInfo {
  name: string;
  displayName: string;
  description: string;
  status: 'active' | 'inactive' | 'deprecated';
  health: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  category: string;
  icon: string;
}

const AGENT_CATALOG: AgentInfo[] = [
  { name: 'ceo', displayName: 'CEO Agent', description: 'Business vision, SWOT, revenue strategy, KPIs', status: 'active', health: 'healthy', version: '1.0.0', category: 'Strategy', icon: '👔' },
  { name: 'product_manager', displayName: 'Product Manager', description: 'Feature planning, scoping, roadmap phases, prioritization', status: 'active', health: 'healthy', version: '1.0.0', category: 'Strategy', icon: '📋' },
  { name: 'business_analyst', displayName: 'Business Analyst', description: 'Requirements, business rules, acceptance criteria', status: 'active', health: 'healthy', version: '1.0.0', category: 'Strategy', icon: '📊' },
  { name: 'market_research', displayName: 'Market Research', description: 'Competitor analysis, market sizing, pricing benchmarks', status: 'active', health: 'healthy', version: '1.0.0', category: 'Strategy', icon: '🔍' },
  { name: 'ux_designer', displayName: 'UX Designer', description: 'User flows, screen catalogs, design system', status: 'active', health: 'healthy', version: '1.0.0', category: 'Design', icon: '🎨' },
  { name: 'technical_architect', displayName: 'Technical Architect', description: 'Stack selection, architecture patterns, scalability', status: 'active', health: 'healthy', version: '1.0.0', category: 'Architecture', icon: '🏗️' },
  { name: 'database_architect', displayName: 'Database Architect', description: 'Entity schemas, relationships, indexes, migrations', status: 'active', health: 'healthy', version: '1.0.0', category: 'Architecture', icon: '🗄️' },
  { name: 'api_architect', displayName: 'API Architect', description: 'REST endpoints, auth, pagination, error schemas', status: 'active', health: 'healthy', version: '1.0.0', category: 'Architecture', icon: '🔌' },
  { name: 'backend_architect', displayName: 'Backend Architect', description: 'FastAPI modules, services, dependency injection', status: 'active', health: 'healthy', version: '1.0.0', category: 'Architecture', icon: '⚙️' },
  { name: 'frontend_architect', displayName: 'Frontend Architect', description: 'Next.js layouts, components, state stores, hooks', status: 'active', health: 'healthy', version: '1.0.0', category: 'Architecture', icon: '🖥️' },
  { name: 'roadmap', displayName: 'Roadmap Agent', description: 'Quarterly/monthly milestones, release timeline', status: 'active', health: 'healthy', version: '1.0.0', category: 'Planning', icon: '🗺️' },
  { name: 'sprint', displayName: 'Sprint Agent', description: 'Sprint goals, capacity, velocity, backlog selection', status: 'active', health: 'healthy', version: '1.0.0', category: 'Planning', icon: '🏃' },
  { name: 'task_generator', displayName: 'Task Generator', description: 'Epics, stories, subtasks, developer assignments', status: 'active', health: 'healthy', version: '1.0.0', category: 'Planning', icon: '📝' },
  { name: 'qa', displayName: 'QA Agent', description: 'Test suites, edge cases, performance targets', status: 'active', health: 'healthy', version: '1.0.0', category: 'Quality', icon: '🧪' },
  { name: 'security', displayName: 'Security Agent', description: 'OWASP, auth review, dependency scanning', status: 'active', health: 'healthy', version: '1.0.0', category: 'Quality', icon: '🔒' },
  { name: 'devops', displayName: 'DevOps Agent', description: 'Docker, CI/CD, monitoring, backup, HA', status: 'active', health: 'healthy', version: '1.0.0', category: 'Operations', icon: '🚀' },
  { name: 'analytics', displayName: 'Analytics Agent', description: 'North Star metric, KPIs, retention, adoption', status: 'active', health: 'healthy', version: '1.0.0', category: 'Operations', icon: '📈' },
  { name: 'meeting', displayName: 'Meeting Agent', description: 'Transcript parsing, action items, decisions', status: 'active', health: 'healthy', version: '1.0.0', category: 'Collaboration', icon: '🤝' },
  { name: 'documentation', displayName: 'Documentation Agent', description: 'README, API docs, architecture docs, changelogs', status: 'active', health: 'healthy', version: '1.0.0', category: 'Collaboration', icon: '📖' },
  { name: 'knowledge', displayName: 'Knowledge Agent', description: 'Document indexing, retrieval, future RAG', status: 'active', health: 'healthy', version: '1.0.0', category: 'Collaboration', icon: '🧠' },
  { name: 'review', displayName: 'Review Agent', description: 'Cross-validates all agent outputs for consistency', status: 'active', health: 'healthy', version: '1.0.0', category: 'Validation', icon: '✅' },
  { name: 'estimation', displayName: 'Estimation Agent', description: 'Time, cost, resources, complexity scoring', status: 'active', health: 'healthy', version: '1.0.0', category: 'Validation', icon: '⏱️' },
  { name: 'risk', displayName: 'Risk Agent', description: 'Technical, business, schedule, budget risks', status: 'active', health: 'healthy', version: '1.0.0', category: 'Validation', icon: '⚠️' },
  { name: 'priority', displayName: 'Priority Agent', description: 'MoSCoW, RICE, ICE, Value vs Effort scoring', status: 'active', health: 'healthy', version: '1.0.0', category: 'Validation', icon: '🎯' },
];

const CATEGORIES = ['Strategy', 'Design', 'Architecture', 'Planning', 'Quality', 'Operations', 'Collaboration', 'Validation'];

const CATEGORY_COLORS: Record<string, string> = {
  Strategy: 'border-amber-500/30 bg-amber-500/5',
  Design: 'border-pink-500/30 bg-pink-500/5',
  Architecture: 'border-blue-500/30 bg-blue-500/5',
  Planning: 'border-emerald-500/30 bg-emerald-500/5',
  Quality: 'border-red-500/30 bg-red-500/5',
  Operations: 'border-violet-500/30 bg-violet-500/5',
  Collaboration: 'border-cyan-500/30 bg-cyan-500/5',
  Validation: 'border-orange-500/30 bg-orange-500/5',
};

const CATEGORY_TAG_COLORS: Record<string, string> = {
  Strategy: 'bg-amber-500/20 text-amber-300',
  Design: 'bg-pink-500/20 text-pink-300',
  Architecture: 'bg-blue-500/20 text-blue-300',
  Planning: 'bg-emerald-500/20 text-emerald-300',
  Quality: 'bg-red-500/20 text-red-300',
  Operations: 'bg-violet-500/20 text-violet-300',
  Collaboration: 'bg-cyan-500/20 text-cyan-300',
  Validation: 'bg-orange-500/20 text-orange-300',
};

interface AgentExecution {
  agentName: string;
  timestamp: string;
  status: 'completed' | 'running' | 'failed';
  latencyMs: number;
}

export default function AgentDashboardPage() {
  const [selectedCategory, setSelectedCategory] = React.useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = React.useState<AgentInfo | null>(null);

  const [executionTimeline] = React.useState<AgentExecution[]>([
    { agentName: 'ceo', timestamp: '10:41:12', status: 'completed', latencyMs: 1240 },
    { agentName: 'product_manager', timestamp: '10:41:14', status: 'completed', latencyMs: 1890 },
    { agentName: 'business_analyst', timestamp: '10:41:16', status: 'completed', latencyMs: 2110 },
    { agentName: 'market_research', timestamp: '10:41:19', status: 'completed', latencyMs: 3420 },
    { agentName: 'technical_architect', timestamp: '10:41:22', status: 'running', latencyMs: 0 },
  ]);

  const filteredAgents = selectedCategory
    ? AGENT_CATALOG.filter(a => a.category === selectedCategory)
    : AGENT_CATALOG;

  return (
    <AppShell>
      <div className="space-y-6">

        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-zinc-100">Agent Dashboard</h1>
            <p className="text-sm text-zinc-500 mt-1">
              {AGENT_CATALOG.length} agents registered &middot; All systems operational
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-full px-3 py-1">
              <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
              Registry Online
            </span>
          </div>
        </div>

        {/* Category Filter Bar */}
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
              !selectedCategory
                ? 'bg-zinc-700/60 border-zinc-600 text-zinc-100'
                : 'bg-zinc-900/40 border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700'
            }`}
          >
            All ({AGENT_CATALOG.length})
          </button>
          {CATEGORIES.map(cat => {
            const count = AGENT_CATALOG.filter(a => a.category === cat).length;
            return (
              <button
                key={cat}
                onClick={() => setSelectedCategory(selectedCategory === cat ? null : cat)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                  selectedCategory === cat
                    ? 'bg-zinc-700/60 border-zinc-600 text-zinc-100'
                    : 'bg-zinc-900/40 border-zinc-800 text-zinc-500 hover:text-zinc-300 hover:border-zinc-700'
                }`}
              >
                {cat} ({count})
              </button>
            );
          })}
        </div>

        {/* Main Layout: Agent Grid + Sidebar */}
        <div className="flex gap-6">

          {/* Agent Cards Grid */}
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredAgents.map(agent => (
              <button
                key={agent.name}
                onClick={() => setSelectedAgent(agent)}
                className={`text-left p-4 rounded-xl border transition-all duration-200 hover:scale-[1.01] ${
                  selectedAgent?.name === agent.name
                    ? 'border-indigo-500/40 bg-indigo-500/5 ring-1 ring-indigo-500/20'
                    : `${CATEGORY_COLORS[agent.category]} hover:bg-zinc-800/30`
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-2xl">{agent.icon}</span>
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />
                    <span className="text-[10px] text-zinc-500 font-mono">v{agent.version}</span>
                  </div>
                </div>
                <h3 className="text-sm font-semibold text-zinc-200 mb-1">{agent.displayName}</h3>
                <p className="text-xs text-zinc-500 leading-relaxed line-clamp-2">{agent.description}</p>
                <div className="mt-3">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${CATEGORY_TAG_COLORS[agent.category]}`}>
                    {agent.category}
                  </span>
                </div>
              </button>
            ))}
          </div>

          {/* Agent Detail Sidebar */}
          <div className="w-80 shrink-0 space-y-4">

            {/* Selected Agent Detail */}
            {selectedAgent ? (
              <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{selectedAgent.icon}</span>
                  <div>
                    <h3 className="text-sm font-bold text-zinc-100">{selectedAgent.displayName}</h3>
                    <p className="text-[10px] text-zinc-500 font-mono">{selectedAgent.name} &middot; v{selectedAgent.version}</p>
                  </div>
                </div>
                <p className="text-xs text-zinc-400 leading-relaxed">{selectedAgent.description}</p>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-500">Status</span>
                    <span className="text-emerald-400 font-mono capitalize">{selectedAgent.status}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-500">Health</span>
                    <span className="text-emerald-400 font-mono capitalize">{selectedAgent.health}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-zinc-500">Category</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] ${CATEGORY_TAG_COLORS[selectedAgent.category]}`}>
                      {selectedAgent.category}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/30 text-center text-zinc-600 text-xs">
                Select an agent to inspect
              </div>
            )}

            {/* Execution Timeline */}
            <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 space-y-3">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">Execution Timeline</h4>
              <div className="space-y-2">
                {executionTimeline.map((exec, i) => {
                  const agent = AGENT_CATALOG.find(a => a.name === exec.agentName);
                  return (
                    <div key={i} className="flex items-center gap-3 text-xs">
                      <span className="text-zinc-600 font-mono w-14 text-right shrink-0">{exec.timestamp}</span>
                      <div className={`w-2 h-2 rounded-full shrink-0 ${
                        exec.status === 'completed' ? 'bg-emerald-400' :
                        exec.status === 'running' ? 'bg-amber-400 animate-pulse' :
                        'bg-red-400'
                      }`} />
                      <span className="text-zinc-300 truncate">{agent?.displayName || exec.agentName}</span>
                      {exec.status === 'completed' && (
                        <span className="text-zinc-600 font-mono ml-auto shrink-0">{exec.latencyMs}ms</span>
                      )}
                      {exec.status === 'running' && (
                        <span className="text-amber-400 font-mono ml-auto shrink-0 animate-pulse">running</span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Agent Logs Panel */}
            <div className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/50 space-y-3">
              <h4 className="text-xs font-semibold text-zinc-400 uppercase tracking-wider">System Logs</h4>
              <div className="bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono text-[10px] text-zinc-500 leading-relaxed max-h-40 overflow-y-auto">
                <div><span className="text-zinc-600">[10:41:12]</span> <span className="text-emerald-400">INFO</span> Registered 24 agents in registry</div>
                <div><span className="text-zinc-600">[10:41:12]</span> <span className="text-emerald-400">INFO</span> CEO Agent executing...</div>
                <div><span className="text-zinc-600">[10:41:13]</span> <span className="text-emerald-400">INFO</span> LLM generate via openai (gpt-4o)</div>
                <div><span className="text-zinc-600">[10:41:14]</span> <span className="text-emerald-400">INFO</span> CEO Agent completed (1240ms)</div>
                <div><span className="text-zinc-600">[10:41:14]</span> <span className="text-emerald-400">INFO</span> PM Agent executing...</div>
                <div><span className="text-zinc-600">[10:41:16]</span> <span className="text-emerald-400">INFO</span> PM Agent completed (1890ms)</div>
                <div><span className="text-zinc-600">[10:41:16]</span> <span className="text-emerald-400">INFO</span> BA Agent executing...</div>
                <div><span className="text-zinc-600">[10:41:19]</span> <span className="text-emerald-400">INFO</span> BA Agent completed (2110ms)</div>
                <div><span className="text-zinc-600">[10:41:22]</span> <span className="text-amber-400">INFO</span> Tech Architect running...</div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </AppShell>
  );
}
