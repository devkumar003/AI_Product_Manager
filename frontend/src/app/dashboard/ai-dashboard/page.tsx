'use client';

import * as React from 'react';

const STAT_CARDS = [
  { label: 'AI Agents', value: '24', sub: 'All operational', color: 'text-indigo-400', border: 'border-indigo-500/20', bg: 'bg-indigo-500/5' },
  { label: 'Business Engines', value: '16', sub: 'Ready for execution', color: 'text-emerald-400', border: 'border-emerald-500/20', bg: 'bg-emerald-500/5' },
  { label: 'Workflows', value: '6', sub: 'Pre-built templates', color: 'text-violet-400', border: 'border-violet-500/20', bg: 'bg-violet-500/5' },
  { label: 'Knowledge Docs', value: '0', sub: 'In knowledge base', color: 'text-amber-400', border: 'border-amber-500/20', bg: 'bg-amber-500/5' },
];

const QUICK_ACTIONS = [
  { label: 'Analyze Idea', href: '/dashboard/idea-analyzer', icon: '💡', color: 'bg-amber-500/10 border-amber-500/20 text-amber-300' },
  { label: 'Generate PRD', href: '/dashboard/prd-generator', icon: '📋', color: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300' },
  { label: 'Design Architecture', href: '/dashboard/architecture-generator', icon: '🏗️', color: 'bg-violet-500/10 border-violet-500/20 text-violet-300' },
  { label: 'Plan Roadmap', href: '/dashboard/roadmap-generator', icon: '🗺️', color: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300' },
  { label: 'Generate Requirements', href: '/dashboard/requirement-generator', icon: '📝', color: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300' },
  { label: 'AI Chat', href: '/dashboard/ai-chat', icon: '💬', color: 'bg-pink-500/10 border-pink-500/20 text-pink-300' },
  { label: 'Knowledge Base', href: '/dashboard/knowledge-base', icon: '🧠', color: 'bg-orange-500/10 border-orange-500/20 text-orange-300' },
  { label: 'Agent Dashboard', href: '/dashboard/agents', icon: '🤖', color: 'bg-blue-500/10 border-blue-500/20 text-blue-300' },
];

const RECENT_ENGINES = [
  { name: 'Idea Analysis', model: 'gpt-4o', tokens: 2340, cost: 0.047, time: '2.1s', status: 'completed' },
  { name: 'PRD Generation', model: 'claude-sonnet-4-20250514', tokens: 8920, cost: 0.134, time: '12.4s', status: 'completed' },
  { name: 'Architecture Design', model: 'gemini-2.5-pro', tokens: 6510, cost: 0.098, time: '8.7s', status: 'completed' },
];

const POPULAR_MODELS = [
  { name: 'GPT-4o', provider: 'OpenAI', usage: 67, color: 'bg-emerald-500' },
  { name: 'Claude Sonnet 4', provider: 'Anthropic', usage: 18, color: 'bg-violet-500' },
  { name: 'Gemini 2.5 Pro', provider: 'Google', usage: 10, color: 'bg-blue-500' },
  { name: 'Llama 3.3 70B', provider: 'Groq', usage: 5, color: 'bg-amber-500' },
];

export default function AIDashboardPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Dashboard</h1>
          <p className="text-sm text-zinc-500 mt-1">AI ProductOS intelligence overview</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-4 gap-4">
          {STAT_CARDS.map(s => (
            <div key={s.label} className={`p-5 rounded-xl border ${s.border} ${s.bg}`}>
              <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-sm text-zinc-300 mt-1">{s.label}</div>
              <div className="text-[10px] text-zinc-500 mt-0.5">{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div>
          <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-3">Quick Actions</h2>
          <div className="grid grid-cols-4 gap-3">
            {QUICK_ACTIONS.map(a => (
              <a key={a.label} href={a.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all hover:scale-[1.02] ${a.color}`}>
                <span className="text-xl">{a.icon}</span>
                <span className="text-sm font-medium">{a.label}</span>
              </a>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Recent AI Tasks */}
          <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">Recent AI Tasks</h2>
            <div className="space-y-3">
              {RECENT_ENGINES.map((t, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-3 bg-zinc-950 border border-zinc-800 rounded-lg">
                  <div>
                    <div className="text-sm text-zinc-200 font-medium">{t.name}</div>
                    <div className="text-zinc-500 mt-0.5">{t.model} · {t.tokens} tokens · {t.time}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-emerald-400 font-mono">${t.cost.toFixed(3)}</div>
                    <div className="text-zinc-600 mt-0.5">{t.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Model Usage */}
          <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl">
            <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider mb-4">Popular Models</h2>
            <div className="space-y-3">
              {POPULAR_MODELS.map((m, i) => (
                <div key={i} className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-zinc-200">{m.name} <span className="text-zinc-600">({m.provider})</span></span>
                    <span className="text-zinc-400 font-mono">{m.usage}%</span>
                  </div>
                  <div className="w-full bg-zinc-800 rounded-full h-1.5">
                    <div className={`${m.color} h-1.5 rounded-full transition-all`} style={{ width: `${m.usage}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
