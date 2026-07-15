'use client';

import * as React from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import {
  TrendingUp,
  Activity,
  Users,
  AlertTriangle,
  RefreshCw,
  Clock,
  Terminal,
} from 'lucide-react';

import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

interface EventLog {
  timestamp: string;
  type: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  message: string;
  source: string;
}

export default function AnalyticsDashboardPage() {
  const { activeWorkspace } = useAuth();
  const [dbAnalytics, setDbAnalytics] = React.useState<any>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [logs, setLogs] = React.useState<EventLog[]>([
    { timestamp: '14:24:02', type: 'INFO', message: 'User organization seat capacity upgraded.', source: 'Auth Service' },
    { timestamp: '14:15:10', type: 'WARNING', message: 'Gemini API limit reached. Routed traffic to OpenAI fallback engine.', source: 'LLM Manager' },
    { timestamp: '13:58:44', type: 'ERROR', message: 'Failed to dispatch webhook payload to webhook.site/uuid.', source: 'Integration Pipeline' },
    { timestamp: '13:40:02', type: 'INFO', message: 'Decomposed 15 backlog stories from vision successfully.', source: 'Autonomous Planner' },
    { timestamp: '12:11:15', type: 'CRITICAL', message: 'Database connection pool exhausted. Reset connections active.', source: 'DB Engine' },
  ]);

  const fetchAnalytics = React.useCallback(async () => {
    if (!activeWorkspace) return;
    try {
      const data = await apiService.get<any>(`/planning/analytics/latest?workspace_id=${activeWorkspace.id}`);
      setDbAnalytics(data);
    } catch (err) {
      console.error('Failed to load real planning analytics:', err);
    }
  }, [activeWorkspace]);

  React.useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const handleRefresh = async () => {
    setIsLoading(true);
    await fetchAnalytics();
    
    // Prepend a mock new log
    const types: ('INFO' | 'WARNING' | 'ERROR' | 'CRITICAL')[] = ['INFO', 'WARNING', 'ERROR'];
    const sources = ['AI Engine', 'COO Reporter', 'Auth Manager', 'FinOps'];
    const messages = [
      'Generated CEO strategic SWOT forecast report.',
      'Token quota utilization exceeded 85% for standard tier.',
      'Invalid JWT signature detected from IP 192.168.1.104.',
      'Exported presentation slides to PDF storage archive.',
    ];
    
    const newLog: EventLog = {
      timestamp: new Date().toLocaleTimeString(),
      type: types[Math.floor(Math.random() * types.length)],
      message: messages[Math.floor(Math.random() * messages.length)],
      source: sources[Math.floor(Math.random() * sources.length)],
    };

    setLogs((prev) => [newLog, ...prev.slice(0, 7)]);
    setIsLoading(false);
  };

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Breadcrumbs and Header */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Product Analytics' }]} />
          <div className="flex items-center justify-between mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
                <Activity className="text-indigo-400" /> SaaS Telemetry & Product Analytics
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Real-time dashboard displaying retention grids, active events, and incident console logs.
              </p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-zinc-300 hover:text-white disabled:opacity-50 transition text-xs font-bold uppercase tracking-wider"
            >
              <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
              Refresh Dashboard
            </button>
          </div>
        </div>

        {/* Highlight Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-2">
            <div className="text-[10px] text-zinc-500 uppercase font-black tracking-wider flex items-center gap-1.5">
              <Users size={12} className="text-indigo-400" /> Total Backlog Delays
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {dbAnalytics ? `${dbAnalytics.total_delays_hours}h` : '0h'}
            </div>
            <div className="text-[10px] text-zinc-400 font-bold">Accumulated delay duration</div>
          </div>

          <div className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-2">
            <div className="text-[10px] text-zinc-500 uppercase font-black tracking-wider flex items-center gap-1.5">
              <Activity size={12} className="text-emerald-450" /> Completion Rate
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {dbAnalytics ? `${(dbAnalytics.completion_rate * 100).toFixed(1)}%` : '0.0%'}
            </div>
            <div className="text-[10px] text-emerald-400 font-bold">Active backlog completion</div>
          </div>

          <div className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-2">
            <div className="text-[10px] text-zinc-500 uppercase font-black tracking-wider flex items-center gap-1.5">
              <TrendingUp size={12} className="text-violet-400" /> Backlog Accuracy
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {dbAnalytics ? `${(dbAnalytics.accuracy_rate * 100).toFixed(1)}%` : '0.0%'}
            </div>
            <div className="text-[10px] text-emerald-400 font-bold">Plan feasibility index</div>
          </div>

          <div className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-2">
            <div className="text-[10px] text-zinc-500 uppercase font-black tracking-wider flex items-center gap-1.5">
              <AlertTriangle size={12} className="text-rose-400" /> Execution Efficiency
            </div>
            <div className="text-3xl font-black text-white mt-1">
              {dbAnalytics ? `${(dbAnalytics.execution_efficiency * 100).toFixed(1)}%` : '0.0%'}
            </div>
            <div className="text-[10px] text-emerald-400 font-bold">Velocity telemetry</div>
          </div>
        </div>

        {/* Dashboard Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Daily Active Users Chart & Cohort */}
          <div className="lg:col-span-2 space-y-6">
            {/* Visual Chart Panel */}
            <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-4">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-indigo-400">
                Daily Active Users Trend (Last 14 Days)
              </h3>
              
              {/* Custom SVG/Bar chart for visualization */}
              <div className="h-48 flex items-end justify-between gap-1 pt-6 border-b border-zinc-900/60 pb-1">
                {[65, 70, 68, 75, 80, 82, 78, 85, 90, 88, 92, 98, 102, 110].map((val, idx) => (
                  <div key={idx} className="flex-1 flex flex-col items-center gap-2 group">
                    <div 
                      className="w-full bg-indigo-650 hover:bg-indigo-500 rounded-t transition-all cursor-pointer relative"
                      style={{ height: `${val * 1.2}px` }}
                    >
                      <div className="absolute -top-7 left-1/2 -translate-x-1/2 bg-zinc-900 border border-zinc-800 text-white text-[8px] font-bold py-0.5 px-1.5 rounded opacity-0 group-hover:opacity-100 pointer-events-none transition">
                        {(val * 100).toLocaleString()}
                      </div>
                    </div>
                    <span className="text-[8px] text-zinc-600 font-bold uppercase">
                      Day {idx + 1}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* User Cohort Retention Matrix */}
            <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-4">
              <div>
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-indigo-400">
                  User Cohort Retention (30 Days)
                </h3>
                <p className="text-[10px] text-zinc-500 mt-0.5">
                  Percentage of active user return rate weekly.
                </p>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-zinc-900 text-zinc-500 font-bold uppercase text-[9px] tracking-wider">
                      <th className="pb-3 pr-4">Cohort Start</th>
                      <th className="pb-3 text-center">Size</th>
                      <th className="pb-3 text-center">Week 0</th>
                      <th className="pb-3 text-center">Week 1</th>
                      <th className="pb-3 text-center">Week 2</th>
                      <th className="pb-3 text-center">Week 3</th>
                      <th className="pb-3 text-center">Week 4</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-900 font-mono text-[10px]">
                    {[
                      { date: 'Jun 01 - Jun 07', size: '2,420', w0: '100%', w1: '48.2%', w2: '44.5%', w3: '42.1%', w4: '40.8%' },
                      { date: 'Jun 08 - Jun 14', size: '2,890', w0: '100%', w1: '52.1%', w2: '48.0%', w3: '45.3%', w4: '42.5%' },
                      { date: 'Jun 15 - Jun 21', size: '3,100', w0: '100%', w1: '49.8%', w2: '45.2%', w3: '42.8%', w4: '39.2%' },
                      { date: 'Jun 22 - Jun 28', size: '3,450', w0: '100%', w1: '55.3%', w2: '50.1%', w3: '48.0%', w4: '—' },
                    ].map((row, idx) => (
                      <tr key={idx} className="hover:bg-zinc-900/10">
                        <td className="py-3 text-zinc-300 font-sans">{row.date}</td>
                        <td className="py-3 text-zinc-400 text-center">{row.size}</td>
                        <td className="py-3 text-center bg-indigo-950/20 text-indigo-400 font-bold">{row.w0}</td>
                        <td className="py-3 text-center bg-indigo-950/15 text-indigo-350">{row.w1}</td>
                        <td className="py-3 text-center bg-indigo-950/10 text-indigo-300">{row.w2}</td>
                        <td className="py-3 text-center bg-indigo-950/5 text-indigo-250">{row.w3}</td>
                        <td className="py-3 text-center text-zinc-500">{row.w4}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* System Console / Live Logs console */}
          <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-4 flex flex-col justify-between">
            <div className="space-y-4">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                <Terminal size={14} /> Telemetry Event Logs
              </h3>

              <div className="space-y-3 font-mono text-[10px]">
                {logs.map((log, idx) => (
                  <div key={idx} className="p-3 border border-zinc-900 bg-zinc-950 rounded-xl space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className={`px-1.5 py-0.5 rounded font-black text-[8px] ${
                        log.type === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-900/40' :
                        log.type === 'ERROR' ? 'bg-red-900/20 text-red-300 border border-red-800/20' :
                        log.type === 'WARNING' ? 'bg-amber-900/20 text-amber-300 border border-amber-800/20' :
                        'bg-zinc-900 text-zinc-400'
                      }`}>
                        {log.type}
                      </span>
                      <span className="text-zinc-650 flex items-center gap-1 text-[8px]">
                        <Clock size={10} /> {log.timestamp}
                      </span>
                    </div>
                    <p className="text-zinc-300 leading-relaxed break-words">{log.message}</p>
                    <div className="text-[8px] text-zinc-550">
                      Source: {log.source}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
