'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { Target } from 'lucide-react';

interface Message {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tokens?: number;
  cost?: number;
}

interface ModelOption {
  id: string;
  name: string;
  provider: string;
  color: string;
}

export default function AIChatPage() {
  const { activeWorkspace } = useAuth();
  const [selectedModel, setSelectedModel] = React.useState('gemini-1-5');
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
  const [isAgentPanelOpen, setIsAgentPanelOpen] = React.useState(true);
  const [messages, setMessages] = React.useState<Message[]>([
    {
      id: '1',
      sender: 'assistant',
      content: 'Welcome to the AI ProductOS Orchestration environment. I am connected directly to the unified agent router. How can I help you refine your product roadmap today?',
      timestamp: '10:45 AM',
      tokens: 45,
      cost: 0.000675
    }
  ]);

  const [inputMessage, setInputMessage] = React.useState('');
  const [isStreaming, setIsStreaming] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const models: ModelOption[] = [
    { id: 'gemini-1-5', name: 'Gemini 1.5 Pro', provider: 'gemini', color: 'bg-blue-500/20 text-blue-300 border-blue-500/30' },
    { id: 'gpt-4o', name: 'GPT-4o (Standard)', provider: 'openai', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
    { id: 'claude-3-5', name: 'Claude 3.5 Sonnet', provider: 'claude', color: 'bg-orange-500/20 text-orange-300 border-orange-500/30' },
    { id: 'deepseek-chat', name: 'DeepSeek Chat', provider: 'deepseek', color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' },
    { id: 'groq-llama3', name: 'Llama3 8B (Instant)', provider: 'groq', color: 'bg-red-500/20 text-red-300 border-red-500/30' },
    { id: 'ollama-local', name: 'Ollama Local (Offline)', provider: 'ollama', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' }
  ];

  const currentModel = models.find(m => m.id === selectedModel) || models[0];

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !inputMessage.trim()) return;

    const userMessageContent = inputMessage;
    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      content: userMessageContent,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsStreaming(true);
    setError(null);

    try {
      const data = await apiService.post<any>(`/ai/chat`, {
        workspace_id: activeWorkspace.id,
        message: userMessageContent,
        model: selectedModel === 'gemini-1-5' ? 'gemini-1.5-pro' : selectedModel,
        provider: currentModel.provider
      });

      const responseText = data.response || 'No response returned from the agent.';
      const promptLen = Math.max(10, userMessageContent.length / 4);
      const compLen = Math.max(10, responseText.length / 4);
      const tokensCount = Math.round(promptLen + compLen);
      // Average cost is $0.000015 per token
      const calculatedCost = tokensCount * 0.000015;

      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          content: responseText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          tokens: tokensCount,
          cost: calculatedCost
        }
      ]);
    } catch (err: any) {
      setError(err.message || 'Chat routing failed');
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          content: `Error: ${err.message || 'Failed to reach the AI chat backend. Please check your connection.'}`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
      ]);
    } finally {
      setIsStreaming(false);
    }
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="text-center py-20">
          <Target className="mx-auto text-zinc-600 mb-4 animate-bounce" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm mt-2">Choose or create a workspace to view your autonomous chat monitor.</p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="flex h-[calc(100vh-10rem)] border border-zinc-800 rounded-2xl bg-zinc-900/40 backdrop-blur-md overflow-hidden">
        
        {/* CONVERSATION SIDEBAR */}
        <div className={`w-80 bg-zinc-950/60 border-r border-zinc-800 flex flex-col transition-all duration-300 ${isSidebarOpen ? '' : 'hidden'}`}>
          <div className="p-4 border-b border-zinc-800 flex justify-between items-center">
            <h2 className="font-semibold text-sm tracking-wider uppercase text-zinc-400">Agent Sessions</h2>
            <button className="p-1 hover:bg-zinc-800 rounded text-xs text-zinc-500 hover:text-zinc-300">
              New Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            <div className="p-3 bg-zinc-800/40 border border-zinc-700/50 rounded-xl cursor-pointer hover:bg-zinc-800/80 transition-colors">
              <div className="text-sm font-medium text-zinc-200 truncate">Collaborative Workspace specs</div>
              <div className="text-xs text-zinc-500 mt-1 truncate">User: I want to build a real-time...</div>
            </div>
            <div className="p-3 rounded-xl cursor-pointer hover:bg-zinc-800/30 transition-colors text-zinc-400">
              <div className="text-sm font-medium truncate">Database scaling strategies</div>
              <div className="text-xs text-zinc-500 mt-1 truncate">System design specs</div>
            </div>
          </div>
        </div>

        {/* CHAT INTERFACE AREA */}
        <div className="flex-1 flex flex-col bg-zinc-900/20">
          
          {/* TOP ACTION BAR */}
          <div className="p-4 border-b border-zinc-800 flex justify-between items-center bg-zinc-950/20">
            <div className="flex items-center gap-3">
              <button 
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="p-1.5 hover:bg-zinc-800 rounded text-zinc-400 hover:text-zinc-200"
                title="Toggle Sidebar"
              >
                📁
              </button>
              
              {/* MODEL SELECTOR */}
              <div className="relative">
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className="bg-zinc-950 border border-zinc-800 text-zinc-200 text-xs rounded-xl px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-zinc-700 cursor-pointer"
                >
                  {models.map(m => (
                    <option key={m.id} value={m.id}>{m.name} ({m.provider})</option>
                  ))}
                </select>
              </div>

              <span className={`text-xs px-2 py-0.5 border rounded-full ${currentModel.color}`}>
                Active
              </span>
            </div>

            <button 
              onClick={() => setIsAgentPanelOpen(!isAgentPanelOpen)}
              className="text-xs text-zinc-400 hover:text-zinc-200 border border-zinc-800 px-3 py-1.5 rounded-xl hover:bg-zinc-800"
            >
              {isAgentPanelOpen ? 'Hide Controls' : 'Show Controls'}
            </button>
          </div>

          {/* MESSAGES DISPLAY */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 max-w-3xl ${
                  msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''
                }`}
              >
                {/* Sender Avatar */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shrink-0 ${
                  msg.sender === 'user' ? 'bg-zinc-700 text-zinc-200' : 'bg-indigo-600 text-white'
                }`}>
                  {msg.sender === 'user' ? 'U' : 'AI'}
                </div>

                {/* Bubble content */}
                <div className="space-y-1">
                  <div className={`p-4 rounded-2xl border text-sm leading-relaxed ${
                    msg.sender === 'user'
                      ? 'bg-zinc-800/80 border-zinc-700 text-zinc-100'
                      : 'bg-zinc-950/50 border-zinc-800 text-zinc-200'
                  }`}>
                    {/* Render Code block wrapper */}
                    {msg.content.includes('```') ? (
                      <div className="space-y-3">
                        <p>{msg.content.split('```')[0]}</p>
                        <pre className="p-4 bg-zinc-950 border border-zinc-800 rounded-xl overflow-x-auto font-mono text-xs text-emerald-400">
                          {msg.content.split('```')[1].replace('json', '').replace('```', '').trim()}
                        </pre>
                        {msg.content.split('```')[2] && <p>{msg.content.split('```')[2]}</p>}
                      </div>
                    ) : (
                      <p className="whitespace-pre-line">{msg.content}</p>
                    )}
                  </div>

                  {/* Metadata & Cost metrics */}
                  {msg.sender === 'assistant' && msg.tokens && (
                    <div className="flex gap-3 text-[10px] text-zinc-500 px-1">
                      <span>Latency: ~430ms</span>
                      <span>•</span>
                      <span>Tokens: {msg.tokens}</span>
                      <span>•</span>
                      <span>Est. Cost: ${msg.cost?.toFixed(6)}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* TYPING INDICATOR */}
            {isStreaming && (
              <div className="flex gap-4 max-w-3xl">
                <div className="w-8 h-8 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-xs shrink-0">
                  AI
                </div>
                <div className="bg-zinc-950/50 border border-zinc-800 p-4 rounded-2xl flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
          </div>

          {/* INPUT FORM BOX */}
          <form onSubmit={handleSendMessage} className="p-4 border-t border-zinc-800 bg-zinc-950/10">
            <div className="flex gap-3 bg-zinc-950 border border-zinc-800 rounded-2xl p-2 focus-within:ring-1 focus-within:ring-zinc-700">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask AI Orchestrator to execute agents or workflows..."
                className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none px-3"
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isStreaming}
                className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-white font-medium text-xs rounded-xl px-4 py-2 transition-colors shrink-0"
              >
                Send Query
              </button>
            </div>
          </form>

        </div>

        {/* FUTURE AGENT PANEL / MONITOR */}
        <div className={`w-80 bg-zinc-950/60 border-l border-zinc-800 flex flex-col transition-all duration-300 ${isAgentPanelOpen ? '' : 'hidden'}`}>
          <div className="p-4 border-b border-zinc-800">
            <h2 className="font-semibold text-sm tracking-wider uppercase text-zinc-400 font-mono">Agent Monitor</h2>
          </div>
          <div className="p-4 space-y-6 flex-1 overflow-y-auto text-xs">
            
            {/* SECURITY METADATA */}
            <div className="space-y-3">
              <div className="font-medium text-zinc-300">Security Gateways</div>
              <div className="space-y-2">
                <div className="flex justify-between items-center bg-zinc-900/50 p-2 border border-zinc-800 rounded-lg">
                  <span className="text-zinc-500">Injection Protection</span>
                  <span className="text-emerald-400 font-mono">Active</span>
                </div>
                <div className="flex justify-between items-center bg-zinc-900/50 p-2 border border-zinc-800 rounded-lg">
                  <span className="text-zinc-500">Secret Masking Filter</span>
                  <span className="text-emerald-400 font-mono">Active</span>
                </div>
              </div>
            </div>

            {/* TELEMETRY */}
            <div className="space-y-3">
              <div className="font-medium text-zinc-300">Session Telemetry</div>
              <div className="space-y-2 font-mono bg-zinc-950 border border-zinc-800 p-3 rounded-lg space-y-1 text-zinc-400">
                <div className="flex justify-between">
                  <span>Success Rate:</span>
                  <span className="text-zinc-200">100.0%</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Latency:</span>
                  <span className="text-zinc-200">430 ms</span>
                </div>
                <div className="flex justify-between">
                  <span>Cumulative Cost:</span>
                  <span className="text-zinc-200">$0.00311</span>
                </div>
              </div>
            </div>

            {/* CAPABILITIES */}
            <div className="space-y-3">
              <div className="font-medium text-zinc-300">Discovered Tools</div>
              <div className="grid grid-cols-2 gap-2 text-center text-zinc-500 font-mono">
                <div className="p-2 bg-zinc-900/20 border border-zinc-800/80 rounded-lg hover:border-zinc-700/50">
                  🌐 WebSearch
                </div>
                <div className="p-2 bg-zinc-900/20 border border-zinc-800/80 rounded-lg hover:border-zinc-700/50">
                  🗄️ SQL DB
                </div>
                <div className="p-2 bg-zinc-900/20 border border-zinc-800/80 rounded-lg hover:border-zinc-700/50">
                  🧮 Calculator
                </div>
                <div className="p-2 bg-zinc-900/20 border border-zinc-800/80 rounded-lg hover:border-zinc-700/50 text-zinc-600">
                  📁 File System
                </div>
              </div>
            </div>

          </div>
        </div>

      </div>
    </AppShell>
  );
}
