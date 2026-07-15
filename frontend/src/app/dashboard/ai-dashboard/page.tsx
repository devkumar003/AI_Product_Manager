'use client';

import * as React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Sparkles, Zap, ArrowRight } from 'lucide-react';

const STAT_CARDS = [
  { label: 'AI Agents', value: '24', sub: 'All operational', color: 'text-indigo-400', border: 'border-indigo-500/20', bg: 'bg-indigo-500/5' },
  { label: 'Business Engines', value: '16', sub: 'Ready for execution', color: 'text-emerald-400', border: 'border-emerald-500/20', bg: 'bg-emerald-500/5' },
  { label: 'Workflows', value: '6', sub: 'Pre-built templates', color: 'text-violet-400', border: 'border-violet-500/20', bg: 'bg-violet-500/5' },
  { label: 'Knowledge Docs', value: '0', sub: 'In knowledge base', color: 'text-amber-400', border: 'border-amber-500/20', bg: 'bg-amber-500/5' },
];

const QUICK_ACTIONS = [
  { label: 'Analyze Idea', href: '/dashboard/idea-analyzer', icon: '💡', color: 'bg-amber-500/10 border-amber-500/20 text-amber-300 hover:border-amber-500/40 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)]' },
  { label: 'Generate PRD', href: '/dashboard/prd-generator', icon: '📋', color: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300 hover:border-indigo-500/40 hover:shadow-[0_0_20px_rgba(99,102,241,0.15)]' },
  { label: 'Design Architecture', href: '/dashboard/architecture-generator', icon: '🏗️', color: 'bg-violet-500/10 border-violet-500/20 text-violet-300 hover:border-violet-500/40 hover:shadow-[0_0_20px_rgba(139,92,246,0.15)]' },
  { label: 'Plan Roadmap', href: '/dashboard/roadmap-generator', icon: '🗺️', color: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300 hover:border-emerald-500/40 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]' },
  { label: 'Generate Requirements', href: '/dashboard/requirement-generator', icon: '📝', color: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300 hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)]' },
  { label: 'AI Chat Studio', href: '/dashboard/ai-chat', icon: '💬', color: 'bg-pink-500/10 border-pink-500/20 text-pink-300 hover:border-pink-500/40 hover:shadow-[0_0_20px_rgba(236,72,153,0.15)]' },
  { label: 'Knowledge Base', href: '/dashboard/knowledge-base', icon: '🧠', color: 'bg-orange-500/10 border-orange-500/20 text-orange-300 hover:border-orange-500/40 hover:shadow-[0_0_20px_rgba(249,115,22,0.15)]' },
  { label: 'Agent Catalog', href: '/dashboard/agents', icon: '🤖', color: 'bg-blue-500/10 border-blue-500/20 text-blue-300 hover:border-blue-500/40 hover:shadow-[0_0_20px_rgba(59,130,246,0.15)]' },
  { label: 'Market Research', href: '/dashboard/market-research', icon: '📈', color: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300 hover:border-indigo-500/40 hover:shadow-[0_0_20px_rgba(99,102,241,0.15)]' },
  { label: 'Competitor Intel', href: '/dashboard/competitor-analysis', icon: '🛡️', color: 'bg-violet-500/10 border-violet-500/20 text-violet-300 hover:border-violet-500/40 hover:shadow-[0_0_20px_rgba(139,92,246,0.15)]' },
  { label: 'Cost Estimation', href: '/dashboard/cost-estimation', icon: '💵', color: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300 hover:border-emerald-500/40 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]' },
  { label: 'Risk Analysis', href: '/dashboard/risk-analysis', icon: '⚠️', color: 'bg-amber-500/10 border-amber-500/20 text-amber-300 hover:border-amber-500/40 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)]' },
  { label: 'Tech Stack Creator', href: '/dashboard/tech-stack', icon: '💻', color: 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300 hover:border-cyan-500/40 hover:shadow-[0_0_20px_rgba(6,182,212,0.15)]' },
  { label: 'Testing Plan', href: '/dashboard/testing-strategy', icon: '🧪', color: 'bg-rose-500/10 border-rose-500/20 text-rose-300 hover:border-rose-500/40 hover:shadow-[0_0_20px_rgba(244,63,94,0.15)]' },
  { label: 'CI/CD & Deploy', href: '/dashboard/deployment-guide', icon: '🚀', color: 'bg-blue-500/10 border-blue-500/20 text-blue-300 hover:border-blue-500/40 hover:shadow-[0_0_20px_rgba(59,130,246,0.15)]' },
  { label: 'Wireframe Spec', href: '/dashboard/wireframe-suggestions', icon: '📐', color: 'bg-indigo-500/10 border-indigo-500/20 text-indigo-300 hover:border-indigo-500/40 hover:shadow-[0_0_20px_rgba(99,102,241,0.15)]' },
  { label: 'Acceptance GWT', href: '/dashboard/acceptance-criteria', icon: '✅', color: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300 hover:border-emerald-500/40 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]' },
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
    <AppShell>
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, ease: 'easeOut' }}
        className="space-y-8"
      >
        {/* Header Breadcrumb */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub Command Center' }]} />
          <div className="flex items-center justify-between mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                <Sparkles className="mr-3 text-indigo-400" size={28} /> AI Hub Command Center
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Centralized orchestration of all 24 AI ProductOS specialized agents and multi-agent workflows.
              </p>
            </div>
            <Link
              href="/dashboard/agents"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600/20 border border-indigo-500/30 text-indigo-300 hover:bg-indigo-600/30 hover:text-white transition-all text-xs font-bold uppercase tracking-wider"
            >
              Explore 24-Agent Catalog <ArrowRight size={14} />
            </Link>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {STAT_CARDS.map((s, idx) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.05 }}
              className={`p-5 rounded-2xl border ${s.border} ${s.bg} backdrop-blur-sm`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-zinc-400">{s.label}</span>
                <Zap size={16} className={s.color} />
              </div>
              <div className={`text-3xl font-black mt-2 ${s.color}`}>{s.value}</div>
              <div className="text-[11px] font-medium text-zinc-500 mt-1">{s.sub}</div>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">Multi-Agent Generators & Studio</h2>
            <span className="text-xs text-zinc-500">Select an engine to launch autonomous generation</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            {QUICK_ACTIONS.map((a, idx) => (
              <motion.div
                key={a.label}
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.25, delay: idx * 0.04 }}
              >
                <Link
                  href={a.href}
                  className={`group flex items-center justify-between px-4 py-3.5 rounded-xl border transition-all duration-200 block ${a.color}`}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl group-hover:scale-110 transition-transform duration-200">{a.icon}</span>
                    <span className="text-sm font-bold tracking-tight">{a.label}</span>
                  </div>
                  <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all duration-200" />
                </Link>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Split Telemetry Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent AI Tasks */}
          <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
              <h2 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">Recent Agent Executions</h2>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono">Live Telemetry</span>
            </div>
            <div className="space-y-3">
              {RECENT_ENGINES.map((t, i) => (
                <div key={i} className="flex items-center justify-between text-xs p-3.5 bg-zinc-900/40 border border-zinc-800/60 rounded-xl hover:border-zinc-700 transition-colors">
                  <div>
                    <div className="text-sm text-white font-bold">{t.name}</div>
                    <div className="text-zinc-400 mt-0.5 font-mono text-[11px]">{t.model} · {t.tokens.toLocaleString()} tokens · {t.time}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-emerald-400 font-mono font-bold text-sm">${t.cost.toFixed(3)}</div>
                    <div className="text-[10px] uppercase font-bold tracking-wider text-zinc-500 mt-0.5">{t.status}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Model Usage */}
          <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
              <h2 className="text-sm font-bold text-zinc-300 uppercase tracking-wider">FinOps Model Distribution</h2>
              <span className="text-xs text-zinc-500 font-mono">Last 30 days</span>
            </div>
            <div className="space-y-4 pt-1">
              {POPULAR_MODELS.map((m, i) => (
                <div key={i} className="space-y-1.5">
                  <div className="flex justify-between text-xs">
                    <span className="text-white font-bold">{m.name} <span className="text-zinc-500 font-normal">({m.provider})</span></span>
                    <span className="text-indigo-400 font-mono font-bold">{m.usage}%</span>
                  </div>
                  <div className="w-full bg-zinc-900 rounded-full h-2 overflow-hidden border border-zinc-800/60">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${m.usage}%` }}
                      transition={{ duration: 0.6, ease: 'easeOut', delay: i * 0.1 }}
                      className={`${m.color} h-2 rounded-full`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </AppShell>
  );
}
