'use client';

import * as React from 'react';

export default function PRDGeneratorPage() {
  const [idea, setIdea] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const handleGenerate = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/v1/ai/workflows/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_name: 'prd_generation', context: { idea } }),
      });
      const data = await res.json();
      setResult(data.result);
    } catch (e: any) {
      setResult({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">PRD Generator</h1>
          <p className="text-sm text-zinc-500 mt-1">Generate a complete Product Requirements Document from an idea</p>
        </div>

        <div className="grid grid-cols-3 gap-3 text-xs text-zinc-500">
          {['Idea Analysis', 'Product Discovery', 'Requirements', 'User Stories', 'PRD Assembly'].map((step, i) => (
            <div key={step} className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${loading && i <= 2 ? 'border-amber-500/30 bg-amber-500/5 text-amber-300' : 'border-zinc-800 bg-zinc-900/30'}`}>
              <span className="w-5 h-5 rounded-full bg-zinc-800 flex items-center justify-center text-[10px] font-bold">{i + 1}</span>
              {step}
            </div>
          ))}
        </div>

        <textarea value={idea} onChange={e => setIdea(e.target.value)} rows={5}
          placeholder="Describe your product idea in detail — the PRD workflow will run analysis, discovery, requirements, stories, and assembly automatically..."
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-600 focus:border-indigo-500/40 focus:ring-1 focus:ring-indigo-500/20 outline-none resize-none" />

        <button onClick={handleGenerate} disabled={loading || !idea.trim()}
          className="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-sm font-medium transition-colors">
          {loading ? 'Generating PRD (multi-step)...' : 'Generate PRD'}
        </button>

        {result && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-zinc-200">Generated PRD</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[700px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
