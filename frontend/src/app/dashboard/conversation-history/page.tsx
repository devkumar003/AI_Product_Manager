'use client';

import * as React from 'react';

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  model: string;
  messageCount: number;
  timestamp: string;
  tokens: number;
}

const SAMPLE_CONVERSATIONS: Conversation[] = [
  { id: '1', title: 'Product idea for AI code review tool', lastMessage: 'The architecture should use a microservices pattern...', model: 'gpt-4o', messageCount: 12, timestamp: '10 min ago', tokens: 3420 },
  { id: '2', title: 'Sprint planning for Q3 release', lastMessage: 'Based on the velocity of 30 points per sprint...', model: 'claude-sonnet-4-20250514', messageCount: 8, timestamp: '1 hour ago', tokens: 2180 },
  { id: '3', title: 'Database schema review for e-commerce', lastMessage: 'I recommend adding a composite index on...', model: 'gemini-2.5-pro', messageCount: 15, timestamp: '3 hours ago', tokens: 5640 },
  { id: '4', title: 'Risk assessment for fintech MVP', lastMessage: 'The compliance risks are significant because...', model: 'gpt-4o', messageCount: 6, timestamp: 'Yesterday', tokens: 1890 },
];

export default function ConversationHistoryPage() {
  const [search, setSearch] = React.useState('');
  const [selected, setSelected] = React.useState<Conversation | null>(null);

  const filtered = SAMPLE_CONVERSATIONS.filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase()) || c.lastMessage.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Conversation History</h1>
          <p className="text-sm text-zinc-500 mt-1">Browse and search past AI conversations</p>
        </div>

        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search conversations..."
          className="w-full bg-zinc-900 border border-zinc-800 rounded-xl px-4 py-2.5 text-sm text-zinc-200 placeholder-zinc-600 outline-none focus:border-indigo-500/40" />

        <div className="flex gap-6">
          <div className="flex-1 space-y-2">
            {filtered.map(c => (
              <button key={c.id} onClick={() => setSelected(c)}
                className={`w-full text-left p-4 rounded-xl border transition-all ${
                  selected?.id === c.id ? 'border-indigo-500/40 bg-indigo-500/5' : 'border-zinc-800 bg-zinc-900/30 hover:bg-zinc-900/50'
                }`}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-zinc-200">{c.title}</span>
                  <span className="text-[10px] text-zinc-600">{c.timestamp}</span>
                </div>
                <p className="text-xs text-zinc-500 line-clamp-1">{c.lastMessage}</p>
                <div className="flex gap-3 mt-2 text-[10px] text-zinc-600">
                  <span>{c.model}</span>
                  <span>{c.messageCount} messages</span>
                  <span>{c.tokens} tokens</span>
                </div>
              </button>
            ))}
          </div>

          {selected && (
            <div className="w-80 shrink-0 p-5 bg-zinc-900/40 border border-zinc-800 rounded-xl space-y-4">
              <h3 className="text-sm font-bold text-zinc-200">{selected.title}</h3>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between"><span className="text-zinc-500">Model</span><span className="text-zinc-300 font-mono">{selected.model}</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Messages</span><span className="text-zinc-300">{selected.messageCount}</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Tokens</span><span className="text-zinc-300">{selected.tokens}</span></div>
                <div className="flex justify-between"><span className="text-zinc-500">Last Activity</span><span className="text-zinc-300">{selected.timestamp}</span></div>
              </div>
              <div className="pt-3 border-t border-zinc-800">
                <p className="text-xs text-zinc-400">{selected.lastMessage}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
