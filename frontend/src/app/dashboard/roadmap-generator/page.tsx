'use client';

import * as React from 'react';

export default function RoadmapGeneratorPage() {
  const [features, setFeatures] = React.useState('');
  const [framework, setFramework] = React.useState('RICE');
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const handleGenerate = async () => {
    if (!features.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/v1/ai/workflows/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_name: 'roadmap_planning', context: { idea: features, features, framework } }),
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
          <h1 className="text-3xl font-bold tracking-tight">Roadmap Generator</h1>
          <p className="text-sm text-zinc-500 mt-1">Prioritize features and generate quarterly/monthly roadmaps</p>
        </div>

        <div className="flex gap-3">
          <label className="text-sm text-zinc-400 self-center">Framework:</label>
          {['MoSCoW', 'RICE', 'ICE', 'WSJF', 'value_vs_effort'].map(f => (
            <button key={f} onClick={() => setFramework(f)}
              className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                framework === f ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300' : 'bg-zinc-900/40 border-zinc-800 text-zinc-500 hover:text-zinc-300'
              }`}>{f}</button>
          ))}
        </div>

        <textarea value={features} onChange={e => setFeatures(e.target.value)} rows={6}
          placeholder="List your product features, one per line or as a description..."
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-600 focus:border-emerald-500/40 focus:ring-1 focus:ring-emerald-500/20 outline-none resize-none" />

        <button onClick={handleGenerate} disabled={loading || !features.trim()}
          className="px-6 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-sm font-medium transition-colors">
          {loading ? 'Generating Roadmap...' : 'Generate Roadmap'}
        </button>

        {result && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-zinc-200 mb-4">Roadmap Output</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[600px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
