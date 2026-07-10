'use client';

import * as React from 'react';

export default function KnowledgeBasePage() {
  const [title, setTitle] = React.useState('');
  const [content, setContent] = React.useState('');
  const [category, setCategory] = React.useState('general');
  const [tags, setTags] = React.useState('');
  const [searchQuery, setSearchQuery] = React.useState('');
  const [searchResults, setSearchResults] = React.useState<any[]>([]);
  const [stats, setStats] = React.useState<any>(null);
  const [addStatus, setAddStatus] = React.useState('');

  const handleAdd = async () => {
    if (!title.trim() || !content.trim()) return;
    setAddStatus('Adding...');
    try {
      const res = await fetch('/api/v1/ai/knowledge/documents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, category, tags: tags.split(',').map(t => t.trim()).filter(Boolean) }),
      });
      const data = await res.json();
      setAddStatus(`Added: ${data.id}`);
      setTitle('');
      setContent('');
      setTags('');
      handleLoadStats();
    } catch (e: any) {
      setAddStatus(`Error: ${e.message}`);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      const res = await fetch(`/api/v1/ai/knowledge/search?query=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setSearchResults(data);
    } catch (e) {
      setSearchResults([]);
    }
  };

  const handleLoadStats = async () => {
    try {
      const res = await fetch('/api/v1/ai/knowledge/collections');
      const data = await res.json();
      setStats(data);
    } catch (e) { /* */ }
  };

  React.useEffect(() => { handleLoadStats(); }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Knowledge Base</h1>
            <p className="text-sm text-zinc-500 mt-1">Manage documents, search context, and build RAG collections</p>
          </div>
          {stats && (
            <div className="flex gap-4 text-xs text-zinc-500">
              <span className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg">{stats.total_collections ?? 0} collections</span>
              <span className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg">{stats.total_documents ?? 0} documents</span>
            </div>
          )}
        </div>

        <div className="grid grid-cols-2 gap-8">
          {/* Add Document */}
          <div className="space-y-4 p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl">
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Add Document</h2>
            <input value={title} onChange={e => setTitle(e.target.value)} placeholder="Document title"
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 outline-none focus:border-indigo-500/40" />
            <textarea value={content} onChange={e => setContent(e.target.value)} rows={6} placeholder="Document content..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-200 outline-none focus:border-indigo-500/40 resize-none" />
            <div className="flex gap-3">
              <select value={category} onChange={e => setCategory(e.target.value)}
                className="bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-300 outline-none">
                <option value="general">General</option>
                <option value="requirements">Requirements</option>
                <option value="architecture">Architecture</option>
                <option value="research">Research</option>
                <option value="meeting">Meeting</option>
              </select>
              <input value={tags} onChange={e => setTags(e.target.value)} placeholder="Tags (comma separated)"
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 outline-none focus:border-indigo-500/40" />
            </div>
            <button onClick={handleAdd} className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-medium transition-colors">Add to Knowledge Base</button>
            {addStatus && <p className="text-xs text-zinc-500">{addStatus}</p>}
          </div>

          {/* Search */}
          <div className="space-y-4 p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl">
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Search Knowledge</h2>
            <div className="flex gap-2">
              <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Search documents..."
                onKeyDown={e => e.key === 'Enter' && handleSearch()}
                className="flex-1 bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 outline-none focus:border-indigo-500/40" />
              <button onClick={handleSearch} className="px-4 py-2 rounded-lg bg-zinc-800 hover:bg-zinc-700 text-sm transition-colors">Search</button>
            </div>
            <div className="space-y-2 max-h-[400px] overflow-y-auto">
              {searchResults.length === 0 && <p className="text-xs text-zinc-600">No results</p>}
              {searchResults.map((doc, i) => (
                <div key={i} className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-zinc-200">{doc.title}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300">{doc.category}</span>
                  </div>
                  <p className="text-xs text-zinc-500">{doc.preview}</p>
                  {doc.tags?.length > 0 && (
                    <div className="flex gap-1 mt-1">{doc.tags.map((t: string) => <span key={t} className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500">{t}</span>)}</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
