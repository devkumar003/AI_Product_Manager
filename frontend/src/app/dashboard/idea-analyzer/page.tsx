'use client';

import * as React from 'react';

const ENGINES = [
  { name: 'idea_analysis', label: 'Idea Analysis', icon: '💡', description: 'Classify industry, domain, audience, and pain points', placeholder: 'Describe your product idea in detail...' },
  { name: 'idea_validation', label: 'Idea Validation', icon: '✅', description: 'Score feasibility, innovation, competition, and success probability', placeholder: 'Describe the idea to validate...' },
  { name: 'product_discovery', label: 'Product Discovery', icon: '🔭', description: 'Generate vision, personas, KPIs, and North Star metric', placeholder: 'Enter the product concept for discovery...' },
];

export default function IdeaAnalyzerPage() {
  const [selectedEngine, setSelectedEngine] = React.useState(ENGINES[0]);
  const [input, setInput] = React.useState('');
  const [result, setResult] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const handleExecute = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await fetch('/api/v1/ai/engines/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ engine_name: selectedEngine.name, input_data: { idea: input } }),
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
          <h1 className="text-3xl font-bold tracking-tight">Idea Analyzer</h1>
          <p className="text-sm text-zinc-500 mt-1">Transform raw ideas into structured product intelligence</p>
        </div>

        {/* Engine Selector */}
        <div className="flex gap-3">
          {ENGINES.map(e => (
            <button key={e.name} onClick={() => setSelectedEngine(e)}
              className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all ${
                selectedEngine.name === e.name
                  ? 'border-indigo-500/40 bg-indigo-500/10 text-indigo-300'
                  : 'border-zinc-800 bg-zinc-900/40 text-zinc-400 hover:border-zinc-700'
              }`}>
              <span className="text-xl">{e.icon}</span>
              <div className="text-left">
                <div className="text-sm font-medium">{e.label}</div>
                <div className="text-[10px] text-zinc-500">{e.description}</div>
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
            className="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-sm font-medium transition-colors">
            {loading ? 'Analyzing...' : `Run ${selectedEngine.label}`}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6 space-y-4">
            <h2 className="text-lg font-semibold text-zinc-200">Results</h2>
            <pre className="text-xs text-zinc-400 overflow-auto max-h-[600px] whitespace-pre-wrap font-mono bg-zinc-950 border border-zinc-800 rounded-lg p-4">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}
