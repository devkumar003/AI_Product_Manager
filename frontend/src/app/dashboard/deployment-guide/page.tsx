'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { Target, Sparkles, Terminal, Shield } from 'lucide-react';
import { motion } from 'framer-motion';

export default function DeploymentGuidePage() {
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
        engine_name: 'deployment_guide',
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
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view deployment guide.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard' }, { label: 'Deployment Guide' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center">
            <Terminal className="mr-3 text-indigo-400" size={28} /> CI/CD & Deployment Guide
          </h1>
          <p className="text-sm text-zinc-400 mt-1">Generate deployable Docker structures, Github Action pipelines, and zero-trust security checklists</p>
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
            {loading ? 'Generating Guide...' : 'Generate Deployment Guide'}
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
              <h3 className="text-lg font-bold text-white">Deployment Summary</h3>
              <div className="text-sm text-zinc-300 leading-relaxed bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                {result.deployment_summary}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
              <h3 className="text-lg font-bold text-white">Docker Configuration</h3>
              <pre className="text-xs text-zinc-300 overflow-auto max-h-[500px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800/80 rounded-xl p-4">
                {result.docker_configuration}
              </pre>
            </div>

            <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
              <h3 className="text-lg font-bold text-white">CI/CD Pipeline Stages</h3>
              <div className="space-y-4">
                {(result.ci_cd_pipeline || []).map((stage: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl border border-zinc-800 bg-zinc-900/30 space-y-2">
                    <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Stage {idx + 1}: {stage.stage_name}</span>
                    <p className="text-xs text-zinc-300">{stage.description}</p>
                    <div className="text-xs text-zinc-400 mt-2">
                      <span className="font-bold text-zinc-300 block mb-1">Commands</span>
                      <pre className="text-[11px] font-mono bg-zinc-950 p-2.5 rounded border border-zinc-900 overflow-x-auto text-zinc-300">
                        {stage.commands?.join('\n') || '# no commands specified'}
                      </pre>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Shield size={16} className="text-emerald-400" /> Security Checklist
                </h3>
                <ul className="list-disc list-inside text-xs text-zinc-300 space-y-1">
                  {(result.security_checklist || []).map((item: any, idx: number) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 space-y-4">
                <h3 className="text-base font-bold text-white">Disaster Recovery & Rollback</h3>
                <p className="text-xs text-zinc-350 leading-relaxed bg-zinc-900/40 p-4 rounded-xl border border-zinc-800">
                  {result.rollback_plan}
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </AppShell>
  );
}
