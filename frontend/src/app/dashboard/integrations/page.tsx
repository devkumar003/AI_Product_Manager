'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { 
  Puzzle, 
  Plus, 
  Trash2, 
  RefreshCw, 
  ExternalLink, 
  Settings2, 
  Activity, 
  Check, 
  Search, 
  Terminal, 
  Sparkles, 
  Mail, 
  FolderGit2, 
  Send,
  Lock,
  Layers,
  AlertCircle,
  Plug
} from 'lucide-react';

interface Plugin {
  id: string;
  name: string;
  slug: string;
  description: string;
  plugin_version: string;
  plugin_type: string;
  category: string;
  is_active: boolean;
  settings_schema?: Record<string, any>;
}

interface Connection {
  id: string;
  plugin_id: string;
  workspace_id: string;
  config: Record<string, any>;
  status: string;
  last_sync_at?: string;
  error_message?: string;
  plugin?: Plugin;
}

interface MCPServer {
  id: string;
  name: string;
  url: string;
  headers: Record<string, string>;
  is_active: boolean;
}

interface Webhook {
  id: string;
  name: string;
  target_url: string;
  events: string[];
  is_active: boolean;
  secret_token?: string;
}

interface AuditLog {
  id: string;
  action: string;
  status: string;
  payload: Record<string, any>;
  error_message?: string;
  created_at: string;
}

export default function IntegrationsPage() {
  const { activeWorkspace } = useAuth();
  const [activeTab, setActiveTab] = useState<'marketplace' | 'mcp' | 'webhooks' | 'logs'>('marketplace');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Data States
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [mcpServers, setMcpServers] = useState<MCPServer[]>([]);
  const [webhooks, setWebhooks] = useState<Webhook[]>([]);
  const [logs, setLogs] = useState<AuditLog[]>([]);
  
  // Loading & Action States
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Modal / Input Forms States
  const [mcpName, setMcpName] = useState('');
  const [mcpUrl, setMcpUrl] = useState('');
  const [webhookName, setWebhookName] = useState('');
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookEvents, setWebhookEvents] = useState<string[]>(['*']);
  
  // Interactive Action responses (GitHub Repos, Slack message status etc.)
  const [actionOutput, setActionOutput] = useState<Record<string, any>>({});
  const [runningAction, setRunningAction] = useState<string | null>(null);

  // Fetch all basic data
  const fetchData = async () => {
    if (!activeWorkspace) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      // Fetch Plugins
      const pluginsData = await apiService.get<Plugin[]>('/integration/plugins');
      setPlugins(pluginsData);
      
      // Fetch Active Connections
      const connsData = await apiService.get<Connection[]>(`/integration/connections?workspace_id=${activeWorkspace.id}`);
      setConnections(connsData);

      // Fetch MCP Servers
      const mcpData = await apiService.get<MCPServer[]>(`/integration/mcp?workspace_id=${activeWorkspace.id}`);
      setMcpServers(mcpData);

      // Fetch Webhooks
      const whData = await apiService.get<Webhook[]>(`/integration/webhooks?workspace_id=${activeWorkspace.id}`);
      setWebhooks(whData);

      // Fetch Logs
      const logsData = await apiService.get<AuditLog[]>(`/integration/logs?workspace_id=${activeWorkspace.id}`);
      setLogs(logsData);
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || 'Failed to sync integration framework data from backend API server.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeWorkspace]);

  // Connect integration (Mock OAuth exchange flow)
  const handleConnect = async (plugin: Plugin) => {
    if (!activeWorkspace) return;
    setRunningAction(`connect-${plugin.slug}`);
    try {
      await apiService.post<Connection>(`/integration/oauth/exchange?workspace_id=${activeWorkspace.id}`, {
        provider: plugin.slug,
        code: 'auth_flow_sandbox_code_99',
        redirect_uri: 'http://localhost:3000/dashboard/integrations'
      });
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || `Failed to authenticate ${plugin.name}`);
    } finally {
      setRunningAction(null);
    }
  };

  // Disconnect connection
  const handleDisconnect = async (connectionId: string) => {
    if (!activeWorkspace) return;
    try {
      await apiService.delete(`/integration/connections/${connectionId}?workspace_id=${activeWorkspace.id}`);
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to delete integration connection.');
    }
  };

  // Register MCP Server
  const handleRegisterMcp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !mcpName || !mcpUrl) return;
    try {
      await apiService.post(`/integration/mcp?workspace_id=${activeWorkspace.id}`, {
        name: mcpName,
        url: mcpUrl,
        headers: {}
      });
      setMcpName('');
      setMcpUrl('');
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to register MCP server.');
    }
  };

  // Delete MCP Server
  const handleDeleteMcp = async (id: string) => {
    if (!activeWorkspace) return;
    try {
      await apiService.delete(`/integration/mcp/${id}?workspace_id=${activeWorkspace.id}`);
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to delete MCP server.');
    }
  };

  // Discover tools for an MCP server
  const handleDiscoverMcpTools = async (serverId: string) => {
    if (!activeWorkspace) return;
    setRunningAction(`mcp-discover-${serverId}`);
    try {
      const data = await apiService.get<{ tools: Record<string, any>[] }>(`/integration/mcp/${serverId}/tools?workspace_id=${activeWorkspace.id}`);
      setActionOutput(prev => ({
        ...prev,
        [serverId]: data.tools
      }));
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to query MCP tools list.');
    } finally {
      setRunningAction(null);
    }
  };

  // Register Webhook
  const handleRegisterWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !webhookName || !webhookUrl) return;
    try {
      await apiService.post(`/integration/webhooks?workspace_id=${activeWorkspace.id}`, {
        name: webhookName,
        target_url: webhookUrl,
        events: webhookEvents
      });
      setWebhookName('');
      setWebhookUrl('');
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to register webhook.');
    }
  };

  // Delete Webhook
  const handleDeleteWebhook = async (id: string) => {
    if (!activeWorkspace) return;
    try {
      await apiService.delete(`/integration/webhooks/${id}?workspace_id=${activeWorkspace.id}`);
      fetchData();
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to delete webhook configuration.');
    }
  };

  // Run Provider actions (interactive sandbox integrations)
  const handleRunProviderAction = async (provider: string, actionKey: string, endpoint: string) => {
    if (!activeWorkspace) return;
    const cacheKey = `${provider}-${actionKey}`;
    setRunningAction(cacheKey);
    try {
      const data = await apiService.get<any>(`${endpoint}workspace_id=${activeWorkspace.id}`);
      setActionOutput(prev => ({
        ...prev,
        [cacheKey]: data
      }));
    } catch (err: any) {
      setErrorMsg(err.message || `Failed to query provider: ${provider}`);
    } finally {
      setRunningAction(null);
    }
  };

  // Filter plugins by search input
  const filteredPlugins = plugins.filter(p => 
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-zinc-950 p-6 text-zinc-100 font-sans">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-5 mb-8">
        <div>
          <div className="flex items-center space-x-2 text-indigo-400 font-medium text-sm tracking-wider uppercase mb-1">
            <Layers size={14} />
            <span>Workspace Sync</span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center">
            Integration Dashboard
            <span className="ml-3 rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
              Active OS
            </span>
          </h1>
          <p className="text-zinc-500 text-sm mt-1">
            Manage your external OAuth providers, Model Context Protocol (MCP) servers, outbound webhooks, and event logs.
          </p>
        </div>
        <button
          onClick={fetchData}
          disabled={loading}
          className="mt-4 md:mt-0 flex items-center space-x-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 px-4 py-2 text-sm font-medium text-zinc-200 transition duration-200 hover:text-white active:scale-95 disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          <span>{loading ? 'Syncing...' : 'Sync Status'}</span>
        </button>
      </div>

      {/* Global Error Banner */}
      {errorMsg && (
        <div className="mb-6 flex items-center space-x-3 rounded-lg border border-red-500/25 bg-red-500/10 p-4 text-sm text-red-400">
          <AlertCircle size={18} className="shrink-0" />
          <div className="flex-1">{errorMsg}</div>
          <button onClick={() => setErrorMsg(null)} className="text-red-400 hover:text-white font-bold text-xs uppercase">Dismiss</button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex border-b border-zinc-900 space-x-6 mb-8 overflow-x-auto pb-px">
        {[
          { key: 'marketplace', label: 'Plugin Marketplace', icon: Puzzle },
          { key: 'mcp', label: 'MCP Servers', icon: Terminal },
          { key: 'webhooks', label: 'Outbound Webhooks', icon: Send },
          { key: 'logs', label: 'Audit Trail Logs', icon: Activity },
        ].map(tab => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center space-x-2 pb-4 text-sm font-medium transition duration-200 border-b-2 -mb-px outline-none ${
                isActive 
                  ? 'border-indigo-500 text-indigo-400' 
                  : 'border-transparent text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Contents: Marketplace */}
      {activeTab === 'marketplace' && (
        <div>
          {/* Search bar */}
          <div className="relative max-w-md mb-8">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-zinc-500" />
            <input
              type="text"
              placeholder="Search plugins by name, category, or features..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-zinc-800 bg-zinc-900/60 py-2.5 pl-10 pr-4 text-sm text-white placeholder-zinc-500 outline-none focus:border-indigo-500 focus:bg-zinc-900 transition-colors"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPlugins.map(plugin => {
              const connection = connections.find(c => c.plugin_id === plugin.id);
              const isConnected = connection && connection.status === 'Connected';
              const showActions = isConnected && ['github', 'jira', 'notion', 'slack'].includes(plugin.slug);

              return (
                <div 
                  key={plugin.id}
                  className={`rounded-xl border bg-zinc-950 p-5 transition duration-300 flex flex-col justify-between group hover:shadow-[0_8px_30px_rgb(0,0,0,0.4)] ${
                    isConnected 
                      ? 'border-indigo-500/40 bg-zinc-950/90 shadow-[0_0_15px_rgba(99,102,241,0.05)]' 
                      : 'border-zinc-900 hover:border-zinc-800'
                  }`}
                >
                  <div>
                    {/* Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <div className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1">
                          {plugin.category}
                        </div>
                        <h3 className="text-lg font-bold text-white group-hover:text-indigo-400 transition-colors duration-200">
                          {plugin.name}
                        </h3>
                      </div>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full border font-semibold ${
                        plugin.plugin_type === 'OAuth' 
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
                          : plugin.plugin_type === 'APIKey'
                          ? 'bg-blue-500/10 text-blue-400 border-blue-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                        {plugin.plugin_type}
                      </span>
                    </div>

                    {/* Description */}
                    <p className="text-zinc-400 text-xs leading-relaxed mb-5">
                      {plugin.description}
                    </p>
                  </div>

                  <div>
                    {/* Connected action drawer */}
                    {showActions && (
                      <div className="mb-4 rounded-lg bg-zinc-900/50 border border-zinc-800 p-3 text-xs">
                        <div className="font-bold text-zinc-300 mb-2 flex items-center space-x-1.5">
                          <Settings2 size={12} className="text-indigo-400" />
                          <span>Quick Actions</span>
                        </div>
                        <div className="space-y-2">
                          {plugin.slug === 'github' && (
                            <>
                              <button
                                onClick={() => handleRunProviderAction('github', 'repos', '/integration/github/repos?')}
                                disabled={runningAction !== null}
                                className="w-full text-left bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-1.5 px-2 rounded hover:text-white text-zinc-300 transition duration-150 flex items-center justify-between"
                              >
                                <span className="flex items-center space-x-1"><FolderGit2 size={12} /> <span>Fetch Repositories</span></span>
                                <ExternalLink size={10} />
                              </button>
                              {actionOutput['github-repos'] && (
                                <div className="mt-2 space-y-1 bg-zinc-950 p-2 rounded max-h-32 overflow-y-auto">
                                  {actionOutput['github-repos'].map((r: any) => (
                                    <div key={r.id} className="text-[10px] text-zinc-400 flex items-center justify-between">
                                      <span className="truncate">{r.full_name}</span>
                                      <span className="text-[8px] text-zinc-650 font-bold">Active</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </>
                          )}

                          {plugin.slug === 'slack' && (
                            <>
                              <button
                                onClick={() => handleRunProviderAction('slack', 'post', '/integration/slack/post?channel=general&text=Hello%20from%20AI%20ProductOS!')}
                                disabled={runningAction !== null}
                                className="w-full text-left bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-1.5 px-2 rounded hover:text-white text-zinc-300 transition duration-150 flex items-center justify-between"
                              >
                                <span className="flex items-center space-x-1"><Send size={12} /> <span>Post Sandbox Greeting</span></span>
                                <ExternalLink size={10} />
                              </button>
                              {actionOutput['slack-post'] && (
                                <div className="mt-2 text-[10px] text-emerald-400 bg-emerald-500/5 p-2 rounded border border-emerald-500/10">
                                  Message Sent! TS: {actionOutput['slack-post'].ts}
                                </div>
                              )}
                            </>
                          )}

                          {plugin.slug === 'jira' && (
                            <>
                              <button
                                onClick={() => handleRunProviderAction('jira', 'projects', '/integration/jira/projects?')}
                                disabled={runningAction !== null}
                                className="w-full text-left bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-1.5 px-2 rounded hover:text-white text-zinc-300 transition duration-150 flex items-center justify-between"
                              >
                                <span className="flex items-center space-x-1"><Plus size={12} /> <span>View Jira Projects</span></span>
                                <ExternalLink size={10} />
                              </button>
                              {actionOutput['jira-projects'] && (
                                <div className="mt-2 space-y-1 bg-zinc-950 p-2 rounded max-h-32 overflow-y-auto">
                                  {actionOutput['jira-projects'].map((p: any) => (
                                    <div key={p.id} className="text-[10px] text-zinc-400 flex justify-between">
                                      <span>{p.name}</span>
                                      <span className="font-semibold text-indigo-400">{p.key}</span>
                                    </div>
                                  ))}
                                </div>
                              )}
                            </>
                          )}

                          {plugin.slug === 'notion' && (
                            <>
                              <button
                                onClick={() => handleRunProviderAction('notion', 'dbs', '/integration/notion/databases?')}
                                disabled={runningAction !== null}
                                className="w-full text-left bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-1.5 px-2 rounded hover:text-white text-zinc-300 transition duration-150 flex items-center justify-between"
                              >
                                <span className="flex items-center space-x-1"><Layers size={12} /> <span>Fetch Databases</span></span>
                                <ExternalLink size={10} />
                              </button>
                              {actionOutput['notion-dbs'] && (
                                <div className="mt-2 space-y-1 bg-zinc-950 p-2 rounded">
                                  {actionOutput['notion-dbs'].map((db: any) => (
                                    <div key={db.id} className="text-[10px] text-zinc-400 truncate">
                                      {db.title[0]?.text?.content || 'Roadmap Database'}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Action buttons */}
                    <div className="flex items-center justify-between border-t border-zinc-900/60 pt-4 mt-2">
                      <span className="text-[10px] text-zinc-650">v{plugin.plugin_version}</span>
                      
                      {isConnected ? (
                        <div className="flex items-center space-x-2">
                          <span className="text-xs text-emerald-400 flex items-center mr-2">
                            <Check size={12} className="mr-1" /> Connected
                          </span>
                          <button
                            onClick={() => handleDisconnect(connection.id)}
                            className="rounded-lg bg-red-950/20 hover:bg-red-900/30 text-red-400 border border-red-500/20 hover:border-red-500/30 px-3 py-1.5 text-xs font-semibold transition duration-200"
                          >
                            Disconnect
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => handleConnect(plugin)}
                          disabled={runningAction !== null}
                          className="rounded-lg bg-indigo-600 hover:bg-indigo-500 hover:shadow-[0_0_15px_rgba(99,102,241,0.3)] text-white px-3 py-1.5 text-xs font-semibold transition duration-200 active:scale-95 disabled:opacity-50"
                        >
                          {runningAction === `connect-${plugin.slug}` ? 'Connecting...' : 'Authorize'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab Contents: MCP Servers */}
      {activeTab === 'mcp' && (
        <div className="max-w-4xl">
          {/* Register new Form */}
          <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-6 mb-8">
            <h2 className="text-lg font-bold text-white mb-2 flex items-center">
              <Plus size={16} className="text-indigo-400 mr-2" />
              Register Model Context Protocol (MCP) Server
            </h2>
            <p className="text-xs text-zinc-500 mb-6">
              Connect external agent environments containing tools, prompts, or custom document systems.
            </p>
            <form onSubmit={handleRegisterMcp} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Server Name (e.g. filesystem-tools)"
                value={mcpName}
                onChange={e => setMcpName(e.target.value)}
                className="rounded-lg border border-zinc-800 bg-zinc-900/60 py-2 px-3 text-sm text-white outline-none focus:border-indigo-500 transition-colors"
                required
              />
              <input
                type="url"
                placeholder="Server HTTP Endpoint URL (e.g. http://localhost:8080)"
                value={mcpUrl}
                onChange={e => setMcpUrl(e.target.value)}
                className="rounded-lg border border-zinc-800 bg-zinc-900/60 py-2 px-3 text-sm text-white outline-none focus:border-indigo-500 transition-colors"
                required
              />
              <button
                type="submit"
                className="md:col-span-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm py-2 transition duration-200"
              >
                Register MCP Host
              </button>
            </form>
          </div>

          {/* Servers list */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white mb-2">Registered MCP Hosts</h2>
            {mcpServers.length === 0 ? (
              <div className="rounded-xl border border-dashed border-zinc-850 p-8 text-center text-zinc-650 text-sm">
                No MCP servers configured for this workspace.
              </div>
            ) : (
              mcpServers.map(server => (
                <div key={server.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-5 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-md font-bold text-white">{server.name}</h3>
                      <code className="text-zinc-550 text-[10px] block mt-1">{server.url}</code>
                    </div>
                    <button
                      onClick={() => handleDeleteMcp(server.id)}
                      className="text-zinc-600 hover:text-red-400 p-1.5 transition duration-150"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                  
                  <div className="mt-4 border-t border-zinc-900/60 pt-4 flex items-center justify-between">
                    <button
                      onClick={() => handleDiscoverMcpTools(server.id)}
                      disabled={runningAction !== null}
                      className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center"
                    >
                      <Terminal size={12} className="mr-1.5" />
                      {runningAction === `mcp-discover-${server.id}` ? 'Discovering...' : 'Discover Available Tools'}
                    </button>
                    <span className="text-[10px] text-emerald-400 flex items-center font-semibold">
                      <Check size={10} className="mr-1" /> Active
                    </span>
                  </div>

                  {actionOutput[server.id] && (
                    <div className="mt-4 bg-zinc-900/50 border border-zinc-800 rounded-lg p-3 space-y-2 animate-in fade-in slide-in-from-top-1 duration-200">
                      <div className="text-[10px] font-bold text-zinc-400 uppercase tracking-wider">
                        Available Remote Tools
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {actionOutput[server.id].map((t: any) => (
                          <div key={t.name} className="bg-zinc-950 border border-zinc-850 p-2 rounded">
                            <div className="font-bold text-xs text-white">{t.name}</div>
                            <div className="text-[10px] text-zinc-500 mt-0.5">{t.description}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab Contents: Webhooks */}
      {activeTab === 'webhooks' && (
        <div className="max-w-4xl">
          {/* Register Outbound Webhook */}
          <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-6 mb-8">
            <h2 className="text-lg font-bold text-white mb-2 flex items-center">
              <Plus size={16} className="text-indigo-400 mr-2" />
              Register Outbound Webhook Subscriber
            </h2>
            <p className="text-xs text-zinc-500 mb-6">
              Send real-time JSON events to your systems whenever milestones are completed, tasks are updated, or plans simulation ends.
            </p>
            <form onSubmit={handleRegisterWebhook} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                placeholder="Subscriber Name (e.g. Analytics Pipeline)"
                value={webhookName}
                onChange={e => setWebhookName(e.target.value)}
                className="rounded-lg border border-zinc-800 bg-zinc-900/60 py-2 px-3 text-sm text-white outline-none focus:border-indigo-500 transition-colors"
                required
              />
              <input
                type="url"
                placeholder="Target Dispatch URL (e.g. https://api.mycompany.com/webhook)"
                value={webhookUrl}
                onChange={e => setWebhookUrl(e.target.value)}
                className="rounded-lg border border-zinc-800 bg-zinc-900/60 py-2 px-3 text-sm text-white outline-none focus:border-indigo-500 transition-colors"
                required
              />
              <div className="md:col-span-2">
                <label className="text-xs text-zinc-400 block mb-1">Subscribed Events</label>
                <div className="flex space-x-4 text-xs">
                  <label className="flex items-center space-x-2">
                    <input 
                      type="radio" 
                      name="events" 
                      checked={webhookEvents.includes('*')} 
                      onChange={() => setWebhookEvents(['*'])} 
                    />
                    <span>All Events (*)</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input 
                      type="radio" 
                      name="events" 
                      checked={!webhookEvents.includes('*')} 
                      onChange={() => setWebhookEvents(['document.created', 'planning.milestone_completed'])} 
                    />
                    <span>Custom Events Selection</span>
                  </label>
                </div>
              </div>
              <button
                type="submit"
                className="md:col-span-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm py-2 transition duration-200"
              >
                Create Subscriber Webhook
              </button>
            </form>
          </div>

          {/* Webhooks list */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-white mb-2">Active Webhooks</h2>
            {webhooks.length === 0 ? (
              <div className="rounded-xl border border-dashed border-zinc-850 p-8 text-center text-zinc-650 text-sm">
                No webhooks registered for this workspace.
              </div>
            ) : (
              webhooks.map(wh => (
                <div key={wh.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-5 flex flex-col justify-between">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-md font-bold text-white">{wh.name}</h3>
                      <code className="text-zinc-555 text-[10px] block mt-1">{wh.target_url}</code>
                    </div>
                    <button
                      onClick={() => handleDeleteWebhook(wh.id)}
                      className="text-zinc-600 hover:text-red-400 p-1.5 transition duration-150"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                  
                  <div className="mt-4 border-t border-zinc-900/60 pt-4 flex items-center justify-between">
                    <div className="flex items-center space-x-1.5 text-xs text-zinc-400">
                      <span>Events:</span>
                      {wh.events.map(ev => (
                        <span key={ev} className="bg-zinc-900 px-2 py-0.5 rounded border border-zinc-800 text-[10px] text-zinc-300">
                          {ev}
                        </span>
                      ))}
                    </div>
                    <span className="text-[10px] text-emerald-400 flex items-center font-semibold">
                      <Check size={10} className="mr-1" /> Listening
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Tab Contents: Logs */}
      {activeTab === 'logs' && (
        <div className="max-w-5xl">
          <h2 className="text-lg font-bold text-white mb-4">Workspace Sync History Logs</h2>
          {logs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-zinc-850 p-8 text-center text-zinc-650 text-sm">
              No synchronization events have been recorded.
            </div>
          ) : (
            <div className="rounded-xl border border-zinc-900 bg-zinc-950 overflow-hidden">
              <div className="max-h-[500px] overflow-y-auto">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-zinc-900 bg-zinc-900/30 text-zinc-400 uppercase tracking-wider text-[10px] font-bold">
                      <th className="p-4">Action Event</th>
                      <th className="p-4">Status</th>
                      <th className="p-4">Payload Summary</th>
                      <th className="p-4">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-900/50">
                    {logs.map(log => (
                      <tr key={log.id} className="hover:bg-zinc-900/25 transition duration-150">
                        <td className="p-4 font-semibold text-zinc-200">
                          {log.action}
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            log.status === 'Success' 
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                              : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="p-4 text-zinc-400 truncate max-w-xs">
                          {log.error_message ? (
                            <span className="text-red-400">{log.error_message}</span>
                          ) : (
                            <span>{JSON.stringify(log.payload)}</span>
                          )}
                        </td>
                        <td className="p-4 text-zinc-500 font-mono">
                          {new Date(log.created_at).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
