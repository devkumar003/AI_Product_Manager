'use client';

import * as React from 'react';

interface PromptEntry {
  id: string;
  engine: string;
  timestamp: string;
  inputPreview: string;
  outputPreview: string;
  model: string;
  tokens: number;
  latencyMs: number;
}

const SAMPLE_PROMPTS: PromptEntry[] = [
  { id: '1', engine: 'idea_analysis', timestamp: '10:41 AM', inputPreview: 'An AI-powered code review platform...', outputPreview: '{"industry": "Software Development", "domain": "DevTools"...}', model: 'gpt-4o', tokens: 1890, latencyMs: 2140 },
  { id: '2', engine: 'prd_generator', timestamp: '10:38 AM', inputPreview: 'E-commerce marketplace for handmade goods...', outputPreview: '{"executive_summary": "A curated marketplace..."...}', model: 'claude-sonnet-4-20250514', tokens: 6420, latencyMs: 11200 },
  { id: '3', engine: 'architecture_generator', timestamp: '10:32 AM', inputPreview: 'Real-time collaborative document editor...', outputPreview: '{"system_architecture": "Event-driven microservices..."...}', model: 'gpt-4o', tokens: 4210, latencyMs: 7800 },
  { id: '4', engine: 'risk_analysis', timestamp: '10:25 AM', inputPreview: 'Healthcare appointment scheduling SaaS...', outputPreview: '{"technical_risks": [{"risk": "HIPAA compliance..."...}]...}', model: 'gemini-2.5-pro', tokens: 3150, latencyMs: 5400 },
];

export default function PromptHistoryPage() {
  const [selected, setSelected] = React.useState<PromptEntry | null>(null);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Prompt History</h1>
          <p className="text-sm text-zinc-500 mt-1">Review all engine and agent prompt executions</p>
        </div>

        <div className="flex gap-6">
          <div className="flex-1 space-y-2">
            {SAMPLE_PROMPTS.map(p => (
              <button key={p.id} onClick={() => setSelected(p)}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  selected?.id === p.id ? 'border-indigo-500/40 bg-indigo-500/5' : 'border-zinc-800 bg-zinc-900/30 hover:bg-zinc-900/50'
                }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-mono px-2 py-0.5 rounded bg-zinc-800 text-zinc-400">{p.engine}</span>
                  <span className="text-[10px] text-zinc-600">{p.timestamp}</span>
                </div>
                <p className="text-xs text-zinc-500 mt-1 line-clamp-1">{p.inputPreview}</p>
                <div className="flex gap-3 mt-2 text-[10px] text-zinc-600">
                  <span>{p.model}</span>
                  <span>{p.tokens} tokens</span>
                  <span>{p.latencyMs}ms</span>
                </div>
              </button>
            ))}
          </div>

          {selected && (
            <div className="w-96 shrink-0 p-5 bg-zinc-900/40 border border-zinc-800 rounded-xl space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">{selected.engine}</span>
                <span className="text-[10px] text-zinc-600">{selected.timestamp}</span>
              </div>
              <div>
                <h4 className="text-[10px] text-zinc-500 uppercase mb-1">Input</h4>
                <p className="text-xs text-zinc-300 bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono">{selected.inputPreview}</p>
              </div>
              <div>
                <h4 className="text-[10px] text-zinc-500 uppercase mb-1">Output</h4>
                <p className="text-xs text-zinc-300 bg-zinc-950 border border-zinc-800 rounded-lg p-3 font-mono max-h-40 overflow-y-auto">{selected.outputPreview}</p>
              </div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between"><span className="text-zinc-500">Model</span><span className="text-zinc-300 font-mono">{selected.model}</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Tokens</span><span className="text-zinc-300">{selected.tokens}</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Latency</span><span className="text-zinc-300">{selected.latencyMs}ms</span></div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
