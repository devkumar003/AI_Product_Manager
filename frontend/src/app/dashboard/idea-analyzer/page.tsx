'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { Target, Sparkles } from 'lucide-react';

const ENGINES = [
  { name: 'idea_analysis', label: 'Idea Analysis', icon: '💡', description: 'Classify industry, domain, audience, and pain points', placeholder: 'Describe your product idea in detail...' },
  { name: 'idea_validation', label: 'Idea Validation', icon: '✅', description: 'Score feasibility, innovation, competition, and success probability', placeholder: 'Describe the idea to validate...' },
  { name: 'product_discovery', label: 'Product Discovery', icon: '🔭', description: 'Generate vision, personas, KPIs, and North Star metric', placeholder: 'Enter the product concept for discovery...' },
];

export default function IdeaAnalyzerPage() {
  const { activeWorkspace } = useAuth();
  const [selectedEngine, setSelectedEngine] = React.useState(ENGINES[0]);
  const [input, setInput] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  const handleExecute = async () => {
    if (!activeWorkspace || !input.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: selectedEngine.name,
        workspace_id: activeWorkspace.id,
        input_data: { idea: input }
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
          <Target className="mx-auto text-zinc-650 mb-4 animate-bounce" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view your autonomous analysis suite.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'AI Hub', href: '/dashboard/ai-dashboard' }, { label: 'Idea Analyzer' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center">
            <Sparkles className="mr-3 text-indigo-400" size={28} /> Idea Analyzer
          </h1>
          <p className="text-sm text-zinc-400 mt-1">Transform raw ideas into structured product intelligence</p>
        </div>

        {/* Engine Selector */}
        <div className="flex flex-col md:flex-row gap-3">
          {ENGINES.map(e => (
            <button key={e.name} onClick={() => setSelectedEngine(e)}
              className={`flex-1 flex items-center gap-3 p-4 rounded-xl border transition-all text-left ${
                selectedEngine.name === e.name
                  ? 'border-indigo-500/40 bg-indigo-500/10 text-indigo-300'
                  : 'border-zinc-800 bg-zinc-900/40 text-zinc-400 hover:border-zinc-700 hover:bg-zinc-800/20'
              }`}>
              <span className="text-2xl">{e.icon}</span>
              <div>
                <div className="text-sm font-bold text-white">{e.label}</div>
                <div className="text-xs text-zinc-400 mt-0.5">{e.description}</div>
              </div>
            </button>
          ))}
        </div>

        {/* Input Area */}
        <div className="space-y-4">
          <textarea value={input} onChange={e => setInput(e.target.value)} rows={6}
            placeholder={selectedEngine.placeholder}
            className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-600 focus:border-indigo-500/40 focus:ring-1 focus:ring-indigo-500/20 outline-none resize-none" />
          <button onClick={handleExecute} disabled={loading || !input.trim()}
            className="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 disabled:text-zinc-650 text-sm font-semibold transition active:scale-95">
            {loading ? 'Analyzing...' : `Run ${selectedEngine.label}`}
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
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-6 space-y-4">
            <h2 className="text-lg font-bold text-white">Results</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[600px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-900 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </AppShell>
  );
}
