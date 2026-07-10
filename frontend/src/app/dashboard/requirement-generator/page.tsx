'use client';

import * as React from 'react';

export default function RequirementGeneratorPage() {
  const [idea, setIdea] = React.useState('');
  const [activeEngine, setActiveEngine] = React.useState<'requirement_generator' | 'user_story_generator'>('requirement_generator');
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const handleGenerate = async () => {
    if (!idea.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const inputData = activeEngine === 'requirement_generator'
        ? { product_discovery: idea, idea }
        : { requirements: idea };
      const res = await fetch('/api/v1/ai/engines/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine_name: activeEngine, input_data: inputData }),
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
          <h1 className="text-3xl font-bold tracking-tight">Requirement Generator</h1>
          <p className="text-sm text-zinc-500 mt-1">Generate structured requirements and user stories from product specs</p>
        </div>

        <div className="flex gap-3">
          {[
            { key: 'requirement_generator' as const, label: 'Requirements', icon: '📋' },
            { key: 'user_story_generator' as const, label: 'User Stories', icon: '📝' },
          ].map(e => (
            <button key={e.key} onClick={() => setActiveEngine(e.key)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm transition-colors ${
                activeEngine === e.key ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300' : 'border-zinc-800 text-zinc-500 hover:text-zinc-300'
              }`}>
              <span>{e.icon}</span> {e.label}
            </button>
          ))}
        </div>

        <textarea value={idea} onChange={e => setIdea(e.target.value)} rows={6}
          placeholder={activeEngine === 'requirement_generator' ? 'Describe the product features and goals...' : 'Paste the requirements output to decompose into user stories...'}
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-600 focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/20 outline-none resize-none" />

        <button onClick={handleGenerate} disabled={loading || !idea.trim()}
          className="px-6 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-sm font-medium transition-colors">
          {loading ? 'Generating...' : `Generate ${activeEngine === 'requirement_generator' ? 'Requirements' : 'User Stories'}`}
        </button>

        {result && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold text-zinc-200 mb-4">Output</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[600px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
