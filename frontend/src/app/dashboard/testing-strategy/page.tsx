'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { Target, Sparkles, CheckSquare, Award } from 'lucide-react';
import { motion } from 'framer-motion';

export default function TestingStrategyPage() {
  const { activeWorkspace } = useAuth();
  const [input, setInput] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (activeWorkspace) {
      setInput(activeWorkspace.description || `A product named ${activeWorkspace.name}`);
    }
  }, [activeWorkspace]);

  const handleExecute = async () => {
    if (!activeWorkspace || !input.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'testing_strategy',
        workspace_id: activeWorkspace.id,
        input_data: { project_description: input }
      });
      setResult(data.result || data);
    } catch (e: any) {
      setError(e.message || 'An error occurred during execution');
    } finally {
      setLoading(false);
    }
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="text-center py-20">
          <Target className="mx-auto text-zinc-600 mb-4 animate-bounce" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view testing strategy.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard' }, { label: 'Testing Strategy' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center">
            <CheckSquare className="mr-3 text-indigo-400" size={28} /> Testing Strategy Generator
          </h1>
          <p className="text-sm text-zinc-400 mt-1">Generate comprehensive QA plans, test cases, and coverage recommendations</p>
        </div>

        {/* Input Area */}
        <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 backdrop-blur-md space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold uppercase tracking-wider text-zinc-300 flex items-center gap-2">
              <Sparkles size={14} className="text-amber-400" /> Target Concept / Vision
            </label>
          </div>
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            rows={4}
            disabled={loading}
            className="w-full bg-zinc-900/80 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-100 placeholder-zinc-500 focus:border-indigo-500/60 focus:ring-2 focus:ring-indigo-500/20 outline-none resize-none transition-all"
          />
          <button
            onClick={handleExecute}
            disabled={loading || !input.trim()}
            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-50 text-white text-sm font-bold shadow-lg transition-all duration-200 active:scale-95"
          >
            {loading ? 'Generating Testing Plan...' : 'Generate Testing Strategy'}
          </button>
        </div>

        {/* Errors */}
        {error && (
          <div className="bg-rose-950/20 border border-rose-900/50 rounded-xl p-4 text-rose-300 text-sm">
            {error}
          </div>
        )}

        {/* Results */}
        {result && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
              <h3 className="text-lg font-bold text-white">Strategy Summary</h3>
              <div className="text-sm text-zinc-300 leading-relaxed bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                {result.strategy_summary}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
                <h3 className="text-base font-bold text-white">Test Pyramid Recommendations</h3>
                <div className="space-y-3">
                  {Object.entries(result.test_pyramid_breakdown || {}).map(([key, val]: any) => (
                    <div key={key} className="flex items-center justify-between border-b border-zinc-900 pb-2 text-sm text-zinc-300">
                      <span className="capitalize">{key} Tests</span>
                      <strong className="text-indigo-400">{val} Cases</strong>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
                <h3 className="text-base font-bold text-white">Testing Tools & Coverage Targets</h3>
                <div className="space-y-3">
                  <div className="text-xs text-zinc-400">
                    <span className="font-bold text-zinc-300 block mb-1">Recommended Tools</span>
                    {(result.tools_recommended || []).join(', ')}
                  </div>
                  <div className="text-xs text-zinc-400 pt-2 border-t border-zinc-900">
                    <span className="font-bold text-zinc-300 block mb-1">Coverage Targets</span>
                    {Object.entries(result.coverage_targets || {}).map(([k, v]: any) => (
                      <div key={k} className="flex justify-between">{k}: <strong>{v}</strong></div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Award size={18} className="text-indigo-400" /> Detailed Test Suites
              </h3>
              <div className="divide-y divide-zinc-900 border border-zinc-900 rounded-xl overflow-hidden">
                {(result.test_suites || []).map((suite: any, idx: number) => (
                  <div key={idx} className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 bg-zinc-950/20">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">{suite.test_type}</span>
                        <h4 className="text-sm font-bold text-white">{suite.test_name}</h4>
                      </div>
                      <p className="text-xs text-zinc-400 mt-1">{suite.description}</p>
                    </div>
                    <span className="text-[10px] uppercase font-extrabold px-2 py-0.5 rounded bg-zinc-800 text-zinc-400 self-start md:self-auto">{suite.priority}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </AppShell>
  );
}
