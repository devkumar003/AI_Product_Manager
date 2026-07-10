'use client';

import * as React from 'react';

export default function ArchitectureGeneratorPage() {
  const [requirements, setRequirements] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const handleGenerate = async () => {
    if (!requirements.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/v1/ai/workflows/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ workflow_name: 'architecture_design', context: { idea: requirements } }),
      });
      const data = await res.json();
      setResult(data.result);
    } catch (e: any) {
      setResult({ error: e.message });
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    { key: 'requirements', label: '1. Requirements', color: 'text-blue-400' },
    { key: 'architecture', label: '2. Architecture', color: 'text-violet-400' },
    { key: 'database', label: '3. Database', color: 'text-amber-400' },
    { key: 'api', label: '4. API Design', color: 'text-emerald-400' },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Architecture Generator</h1>
          <p className="text-sm text-zinc-500 mt-1">Generate system architecture, database schema, and API spec from requirements</p>
        </div>

        <div className="flex gap-3">
          {sections.map(s => (
            <div key={s.key} className={`text-xs px-3 py-2 rounded-lg border border-zinc-800 bg-zinc-900/30 ${s.color}`}>
              {s.label}
            </div>
          ))}
        </div>

        <textarea value={requirements} onChange={e => setRequirements(e.target.value)} rows={6}
          placeholder="Describe the product requirements or paste feature specifications..."
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-600 focus:border-violet-500/40 focus:ring-1 focus:ring-violet-500/20 outline-none resize-none" />

        <button onClick={handleGenerate} disabled={loading || !requirements.trim()}
          className="px-6 py-2.5 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-sm font-medium transition-colors">
          {loading ? 'Generating Architecture...' : 'Generate Architecture'}
        </button>

        {result && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-zinc-200 mb-4">Architecture Output</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[700px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
