'use client';

import * as React from 'react';

export default function AISettingsPage() {
  const [settings, setSettings] = React.useState({
    provider: 'openai',
    model: 'gpt-4o',
    temperature: 0.7,
    top_p: 1.0,
    streaming_enabled: true,
    memory_enabled: true,
    embeddings_enabled: false,
    max_tokens: 4096,
    prompt_template: '',
  });
  const [saved, setSaved] = React.useState(false);

  const providers = [
    { value: 'openai', label: 'OpenAI', models: ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'o1-preview'] },
    { value: 'anthropic', label: 'Anthropic', models: ['claude-sonnet-4-20250514', 'claude-3.5-sonnet', 'claude-3-haiku'] },
    { value: 'google', label: 'Google Gemini', models: ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.0-flash'] },
    { value: 'groq', label: 'Groq', models: ['llama-3.3-70b-versatile', 'mixtral-8x7b-32768'] },
    { value: 'deepseek', label: 'DeepSeek', models: ['deepseek-chat', 'deepseek-coder'] },
    { value: 'ollama', label: 'Ollama (Local)', models: ['llama3', 'codellama', 'mistral'] },
  ];

  const selectedProvider = providers.find(p => p.value === settings.provider) || providers[0];

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">AI Settings</h1>
          <p className="text-sm text-zinc-500 mt-1">Configure AI providers, models, and inference parameters</p>
        </div>

        <div className="space-y-6">
          {/* Provider Selection */}
          <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Provider & Model</h2>
            <div className="grid grid-cols-3 gap-3">
              {providers.map(p => (
                <button key={p.value} onClick={() => setSettings(s => ({ ...s, provider: p.value, model: p.models[0] }))}
                  className={`text-left px-4 py-3 rounded-xl border text-sm transition-all ${
                    settings.provider === p.value ? 'border-indigo-500/40 bg-indigo-500/10 text-indigo-300' : 'border-zinc-800 text-zinc-400 hover:border-zinc-700'
                  }`}>
                  <div className="font-medium">{p.label}</div>
                  <div className="text-[10px] text-zinc-500 mt-0.5">{p.models.length} models</div>
                </button>
              ))}
            </div>
            <div>
              <label className="text-xs text-zinc-500 mb-1 block">Model</label>
              <select value={settings.model} onChange={e => setSettings(s => ({ ...s, model: e.target.value }))}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 outline-none">
                {selectedProvider.models.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
          </div>

          {/* Parameters */}
          <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Inference Parameters</h2>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">Temperature: {settings.temperature}</label>
                <input type="range" min="0" max="2" step="0.1" value={settings.temperature}
                  onChange={e => setSettings(s => ({ ...s, temperature: parseFloat(e.target.value) }))}
                  className="w-full accent-indigo-500" />
              </div>
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">Top P: {settings.top_p}</label>
                <input type="range" min="0" max="1" step="0.05" value={settings.top_p}
                  onChange={e => setSettings(s => ({ ...s, top_p: parseFloat(e.target.value) }))}
                  className="w-full accent-indigo-500" />
              </div>
              <div>
                <label className="text-xs text-zinc-500 mb-1 block">Max Tokens</label>
                <input type="number" value={settings.max_tokens} onChange={e => setSettings(s => ({ ...s, max_tokens: parseInt(e.target.value) || 4096 }))}
                  className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-sm text-zinc-200 outline-none" />
              </div>
            </div>
          </div>

          {/* Toggles */}
          <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Features</h2>
            {[
              { key: 'streaming_enabled' as const, label: 'Streaming Responses', desc: 'Stream tokens in real-time' },
              { key: 'memory_enabled' as const, label: 'Memory', desc: 'Persist conversation context across sessions' },
              { key: 'embeddings_enabled' as const, label: 'Embeddings & RAG', desc: 'Enable vector search for knowledge retrieval' },
            ].map(toggle => (
              <div key={toggle.key} className="flex items-center justify-between">
                <div>
                  <div className="text-sm text-zinc-200">{toggle.label}</div>
                  <div className="text-[10px] text-zinc-500">{toggle.desc}</div>
                </div>
                <button onClick={() => setSettings(s => ({ ...s, [toggle.key]: !s[toggle.key] }))}
                  className={`w-11 h-6 rounded-full transition-colors relative ${settings[toggle.key] ? 'bg-indigo-600' : 'bg-zinc-700'}`}>
                  <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full transition-transform ${settings[toggle.key] ? 'left-[22px]' : 'left-0.5'}`} />
                </button>
              </div>
            ))}
          </div>

          {/* Prompt Template */}
          <div className="p-6 bg-zinc-900/40 border border-zinc-800 rounded-xl space-y-4">
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Custom System Prompt</h2>
            <textarea value={settings.prompt_template} onChange={e => setSettings(s => ({ ...s, prompt_template: e.target.value }))}
              rows={4} placeholder="Override the default system prompt for all AI interactions..."
              className="w-full bg-zinc-950 border border-zinc-800 rounded-lg p-3 text-sm text-zinc-200 placeholder-zinc-600 outline-none resize-none" />
          </div>

          <button onClick={handleSave}
            className="px-6 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-sm font-medium transition-colors">
            {saved ? '✓ Saved' : 'Save Settings'}
          </button>
        </div>
      </div>
    </div>
  );
}
