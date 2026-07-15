'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { FileCode, Target, ClipboardList } from 'lucide-react';

export default function RequirementGeneratorPage() {
  const { activeWorkspace } = useAuth();
  const [idea, setIdea] = React.useState('');
  const [activeEngine, setActiveEngine] = React.useState<'requirement_generator' | 'user_story_generator'>('requirement_generator');
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const handleGenerate = async () => {
    if (!activeWorkspace || !idea.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const inputData = activeEngine === 'requirement_generator'
        ? { product_discovery: idea, idea }
        : { requirements: idea };
      
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: activeEngine,
        workspace_id: activeWorkspace.id,
        input_data: inputData,
      });
      setResult(data.result || data);
    } catch (e: any) {
      setError(e.message || 'An error occurred during generation');
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
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view your autonomous requirements suite.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard/ai-dashboard' }, { label: 'Requirement Generator' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center">
            <ClipboardList className="mr-3 text-cyan-400" size={28} /> Requirement Generator
          </h1>
          <p className="text-sm text-zinc-400 mt-1">Generate structured requirements and user stories from product specs</p>
        </div>

        <div className="flex gap-3">
          {[
            { key: 'requirement_generator' as const, label: 'Requirements Spec', icon: '📋' },
            { key: 'user_story_generator' as const, label: 'User Stories Decomposition', icon: '📝' },
          ].map(e => (
            <button key={e.key} onClick={() => { setActiveEngine(e.key); setResult(null); setError(null); }}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-semibold transition-all ${
                activeEngine === e.key ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300' : 'border-zinc-800 text-zinc-500 hover:text-zinc-350 hover:bg-zinc-900/40'
              }`}>
              <span>{e.icon}</span> {e.label}
            </button>
          ))}
        </div>

        <textarea value={idea} onChange={e => setIdea(e.target.value)} rows={6}
          placeholder={activeEngine === 'requirement_generator' ? 'Describe the product features and goals...' : 'Paste the requirements output to decompose into user stories...'}
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-650 focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/25 outline-none resize-none" />

        <button onClick={handleGenerate} disabled={loading || !idea.trim()}
          className="px-6 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-zinc-800 disabled:text-zinc-650 text-sm font-semibold transition active:scale-95">
          {loading ? 'Generating...' : `Generate ${activeEngine === 'requirement_generator' ? 'Requirements' : 'User Stories'}`}
        </button>

        {error && (
          <div className="bg-rose-950/20 border border-rose-900/50 rounded-xl p-4 text-rose-300 text-sm">
            {error}
          </div>
        )}

        {result && (
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-6 space-y-3">
            <h2 className="text-lg font-bold text-white">Generated Spec Output</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[600px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-900 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </AppShell>
  );
}
