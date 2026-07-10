'use client';

import React, { useState, useEffect } from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService, API_URL } from '@/lib/api';
import { 
  Building2, 
  Cpu, 
  Briefcase, 
  Sparkles, 
  FileText, 
  Download, 
  Plus, 
  Activity, 
  AlertTriangle, 
  ShieldCheck, 
  TrendingUp, 
  Users, 
  Wallet,
  Clock,
  Layers,
  LineChart,
  HardDrive,
  CheckCircle2,
  RefreshCw
} from 'lucide-react';

interface CEOReport {
  id: string;
  title: string;
  strategy_data: {
    business_strategy: string;
    swot: { swot_markdown: string };
    pestle: { pestle_markdown: string };
    gtm: { gtm_plan_markdown: string };
  };
  financials: {
    initial_budget: number;
    forecast: {
      forecast_markdown: string;
      projected_break_even_months: number;
      suggested_tiers: string[];
    };
  };
  market_intelligence: {
    competitors: {
      competitor_matrix_markdown: string;
      competitor_names: string[];
    };
    market_risk_score: string;
  };
  recommendations: Array<{ title: string; details: string }>;
  marketing_sales: {
    journey: { journey_map_markdown: string };
  };
  created_at: string;
}

interface CTOReport {
  id: string;
  title: string;
  architecture_review: {
    tech_stack: string[];
    cloud_infra: {
      specs_review_markdown: string;
      architecture_pattern: string;
      cloud_provider: string;
    };
  };
  optimization_plans: {
    cost_optimization_target: string;
    perf_plans: {
      optimizations_markdown: string;
      db_indexing_strategy: string;
      api_cache_strategy: string;
    };
  };
  security_devops: {
    compliance: {
      compliance_markdown: string;
      standards: string[];
      monitoring: string;
    };
  };
  technical_debt: {
    tech_debt_score: string;
    details: { debt_markdown: string };
  };
  health_metrics: {
    uptime_target: string;
    api_latency_target: string;
    db_pool_status: string;
  };
  created_at: string;
}

interface COOReport {
  id: string;
  title: string;
  resource_capacity: {
    team_size: number;
    roster: string[];
    capacity_hours_weekly: number;
    utilization_rate_est: number;
  };
  delivery_monitoring: {
    active_sprint: string;
    status: string;
    risk_mitigation_actions: string[];
    release_target_date: string;
  };
  incidents_risks: {
    open_severity_1_incidents: number;
    critical_system_alerts: string[];
    risk_status: string;
  };
  operations_analytics: {
    allocated_budget: number;
    burn_rate_monthly: number;
    estimated_months_runway: number;
    infra_cost_pct: number;
    engineering_headcount_cost_pct: number;
  };
  notification_center: Array<{ type: string; message: string }>;
  created_at: string;
}

export default function ExecutiveBoardroomPage() {
  const { activeWorkspace } = useAuth();
  const [activeRole, setActiveRole] = useState<'ceo' | 'cto' | 'coo'>('ceo');
  
  // Lists
  const [ceoReports, setCeoReports] = useState<CEOReport[]>([]);
  const [ctoReports, setCtoReports] = useState<CTOReport[]>([]);
  const [cooReports, setCooReports] = useState<COOReport[]>([]);
  
  // Generators Loading
  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  // CEO input forms
  const [ceoIdea, setCeoIdea] = useState('An automated supply chain logistics coordination SaaS using AI agents.');
  const [ceoIndustry, setCeoIndustry] = useState('Logistics & SaaS');
  const [ceoCompetitors, setCeoCompetitors] = useState('Flexport, Convoy');
  const [ceoBudget, setCeoBudget] = useState(150000);

  // CTO input forms
  const [ctoSpec, setCtoSpec] = useState('FastAPI backend, React frontend, PostgreSQL database, microservices deployed to ECS.');
  const [ctoCloud, setCtoCloud] = useState('AWS');
  const [ctoCompliance, setCtoCompliance] = useState('SOC2, GDPR');

  // COO input forms
  const [cooSprint, setCooSprint] = useState('Sprint 9 - Logistics Routing Logic');
  const [cooTeam, setCooTeam] = useState('Alice (Backend), Bob (Frontend), Charlie (QA)');
  const [cooBudget, setCooBudget] = useState(60000);

  const fetchReports = async () => {
    if (!activeWorkspace) return;
    try {
      const ceoList = await apiService.get<CEOReport[]>(`/executive/ceo/reports?workspace_id=${activeWorkspace.id}`);
      setCeoReports(ceoList);
      
      const ctoList = await apiService.get<CTOReport[]>(`/executive/cto/reports?workspace_id=${activeWorkspace.id}`);
      setCtoReports(ctoList);

      const cooList = await apiService.get<COOReport[]>(`/executive/coo/reports?workspace_id=${activeWorkspace.id}`);
      setCooReports(cooList);
    } catch (err) {
      console.warn('Failed to load executive reports:', err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [activeWorkspace]);

  // CEO generator trigger
  const handleGenerateCEO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) return;
    setIsLoading(true);
    setStatusMsg(null);
    try {
      await apiService.post(`/executive/ceo/report?workspace_id=${activeWorkspace.id}`, {
        product_idea: ceoIdea,
        target_industry: ceoIndustry,
        competitors: ceoCompetitors.split(',').map(c => c.trim()),
        budget: ceoBudget
      });
      setStatusMsg('Successfully generated CEO corporate strategy suite!');
      fetchReports();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // CTO generator trigger
  const handleGenerateCTO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) return;
    setIsLoading(true);
    setStatusMsg(null);
    try {
      await apiService.post(`/executive/cto/report?workspace_id=${activeWorkspace.id}`, {
        product_spec: ctoSpec,
        preferred_cloud: ctoCloud,
        compliance_needs: ctoCompliance.split(',').map(c => c.trim())
      });
      setStatusMsg('Successfully generated CTO architecture audit!');
      fetchReports();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // COO generator trigger
  const handleGenerateCOO = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) return;
    setIsLoading(true);
    setStatusMsg(null);
    try {
      await apiService.post(`/executive/coo/report?workspace_id=${activeWorkspace.id}`, {
        sprint_name: cooSprint,
        team_members: cooTeam.split(',').map(c => c.trim()),
        total_budget: cooBudget
      });
      setStatusMsg('Successfully published COO operations review!');
      fetchReports();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Download files
  const handleDownload = async (id: string, type: 'ceo' | 'cto' | 'coo', format: 'pdf' | 'ppt') => {
    if (!activeWorkspace) return;
    try {
      const res = await apiService.get<{ success: boolean; message: string; download_url: string }>(
        `/executive/export/${format}?report_id=${id}&report_type=${type}&workspace_id=${activeWorkspace.id}`
      );
      
      if (res.download_url) {
        const token = localStorage.getItem('auth_token');
        const headers: Record<string, string> = {};
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const baseUrl = API_URL.replace(/\/api\/v1$/, '');
        const response = await fetch(`${baseUrl}${res.download_url}`, {
          headers,
        });
        
        if (!response.ok) {
          throw new Error(`Failed to download: ${response.statusText}`);
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_report_${id.substring(0, 8)}_${format}.txt`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      } else {
        alert(res.message);
      }
    } catch (err: any) {
      alert(`Export error: ${err.message}`);
    }
  };

  return (
    <AppShell>
      <div className="p-6 text-zinc-100 bg-zinc-950 min-h-screen">
        <Breadcrumb items={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Executive Boardroom' }]} />
        
        {/* Title */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-5 mt-4 mb-6">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-medium text-xs tracking-wider uppercase mb-1">
              <Building2 size={14} />
              <span>Enterprise Advisor Workspace</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center">
              Executive AI Boardroom
            </h1>
            <p className="text-zinc-500 text-sm mt-1">
              Leverage CEO, CTO, and COO intelligence agents to structure strategy, optimize stacks, and analyze burn rates.
            </p>
          </div>
          
          <button
            onClick={fetchReports}
            className="mt-4 md:mt-0 flex items-center space-x-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 px-4 py-2 text-xs font-medium text-zinc-300 transition duration-200"
          >
            <RefreshCw size={12} />
            <span>Sync Executive Status</span>
          </button>
        </div>

        {/* Global Action feedback banner */}
        {statusMsg && (
          <div className="mb-6 flex items-center justify-between rounded-lg border border-indigo-500/25 bg-indigo-500/10 p-4 text-sm text-indigo-400">
            <div className="flex items-center space-x-2">
              <Sparkles size={16} />
              <span>{statusMsg}</span>
            </div>
            <button onClick={() => setStatusMsg(null)} className="text-xs uppercase font-bold hover:text-white">Dismiss</button>
          </div>
        )}

        {/* Executive Roles Tabs */}
        <div className="flex border-b border-zinc-900 space-x-6 mb-6">
          {[
            { key: 'ceo', label: 'AI CEO Workspace', icon: Briefcase, color: 'text-emerald-400 border-emerald-500' },
            { key: 'cto', label: 'AI CTO Tech Audits', icon: Cpu, color: 'text-indigo-400 border-indigo-500' },
            { key: 'coo', label: 'AI COO Operations', icon: Activity, color: 'text-purple-400 border-purple-500' }
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeRole === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => {
                  setActiveRole(tab.key as any);
                  setStatusMsg(null);
                }}
                className={`flex items-center space-x-2 pb-4 text-sm font-medium transition duration-200 border-b-2 -mb-px outline-none ${
                  isActive 
                    ? `${tab.color} text-zinc-100` 
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* -------------------------------------------------------------
            TAB 1: AI CEO
           ------------------------------------------------------------- */}
        {activeRole === 'ceo' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Config Form */}
            <div className="lg:col-span-1 rounded-xl border border-zinc-900 bg-zinc-950 p-5 h-fit">
              <h2 className="text-md font-bold text-white mb-4 flex items-center">
                <Plus size={16} className="text-emerald-400 mr-2" />
                Launch Strategy Suite
              </h2>
              <form onSubmit={handleGenerateCEO} className="space-y-4">
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Product Idea</label>
                  <textarea
                    value={ceoIdea}
                    onChange={e => setCeoIdea(e.target.value)}
                    rows={3}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-emerald-500 resize-none"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Target Vertical</label>
                  <input
                    type="text"
                    value={ceoIndustry}
                    onChange={e => setCeoIndustry(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Competitors (comma separated)</label>
                  <input
                    type="text"
                    value={ceoCompetitors}
                    onChange={e => setCeoCompetitors(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Financial Budget ($)</label>
                  <input
                    type="number"
                    value={ceoBudget}
                    onChange={e => setCeoBudget(Number(e.target.value))}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-emerald-500"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-semibold text-xs py-2.5 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
                >
                  <Sparkles size={14} />
                  <span>{isLoading ? 'Running Strategy Engines...' : 'Synthesize CEO Report'}</span>
                </button>
              </form>
            </div>

            {/* Strategy Reports Output */}
            <div className="lg:col-span-2 space-y-6">
              {ceoReports.length === 0 ? (
                <div className="rounded-xl border border-dashed border-zinc-900 p-12 text-center text-zinc-500 text-xs">
                  No CEO strategy suites generated yet. Use the config panel to synthesize corporate advice.
                </div>
              ) : (
                ceoReports.map(report => (
                  <div key={report.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-6 space-y-6">
                    {/* Header */}
                    <div className="flex justify-between items-start border-b border-zinc-900 pb-4">
                      <div>
                        <h3 className="font-bold text-lg text-white">{report.title}</h3>
                        <div className="text-[10px] text-zinc-500 mt-0.5">
                          Synthesized on {new Date(report.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleDownload(report.id, 'ceo', 'pdf')}
                          className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300"
                        >
                          <Download size={12} />
                          <span>PDF</span>
                        </button>
                        <button
                          onClick={() => handleDownload(report.id, 'ceo', 'ppt')}
                          className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300"
                        >
                          <Download size={12} />
                          <span>PPT</span>
                        </button>
                      </div>
                    </div>

                    {/* SWOT & PESTLE Columns */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">SWOT Analysis</h4>
                        <pre className="font-sans text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed">
                          {report.strategy_data.swot?.swot_markdown}
                        </pre>
                      </div>
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">PESTLE Market Outlook</h4>
                        <pre className="font-sans text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed">
                          {report.strategy_data.pestle?.pestle_markdown}
                        </pre>
                      </div>
                    </div>

                    {/* Financials & Market opportunity */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-3">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                          <Wallet size={12} className="mr-1.5" /> Financial Revenue Forecasts
                        </h4>
                        <div className="text-xs text-zinc-300">
                          Initial Budget Pool: <strong className="text-white">${report.financials.initial_budget.toLocaleString()}</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Break-even Forecast: <strong className="text-white">{report.financials.forecast?.projected_break_even_months} Months</strong>
                        </div>
                        <div className="mt-2 space-y-1">
                          <span className="text-[10px] text-zinc-500 uppercase tracking-wider block">Suggested Pricing Models:</span>
                          {report.financials.forecast?.suggested_tiers?.map((tier, idx) => (
                            <div key={idx} className="text-xs text-zinc-300 flex items-center space-x-2">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                              <span>{tier}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-3">
                        <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center">
                          <TrendingUp size={12} className="mr-1.5" /> Market Competitors & GTM
                        </h4>
                        <div className="text-xs text-zinc-300">
                          Competitors Matrix: 
                          <pre className="font-sans text-[11px] text-zinc-400 mt-1 whitespace-pre-wrap">
                            {report.market_intelligence.competitors?.competitor_matrix_markdown}
                          </pre>
                        </div>
                      </div>
                    </div>

                    {/* Recommendations */}
                    <div className="bg-zinc-900/20 border border-zinc-900 p-4 rounded-lg">
                      <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3">CEO Strategic Directives</h4>
                      <div className="space-y-2">
                        {report.recommendations.map((rec, idx) => (
                          <div key={idx} className="text-xs text-zinc-300 leading-relaxed border-l-2 border-emerald-500/40 pl-3">
                            <strong className="text-white block">{rec.title}</strong>
                            <span>{rec.details}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------
            TAB 2: AI CTO
           ------------------------------------------------------------- */}
        {activeRole === 'cto' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Config Form */}
            <div className="lg:col-span-1 rounded-xl border border-zinc-900 bg-zinc-950 p-5 h-fit">
              <h2 className="text-md font-bold text-white mb-4 flex items-center">
                <Plus size={16} className="text-indigo-400 mr-2" />
                Trigger Tech Review
              </h2>
              <form onSubmit={handleGenerateCTO} className="space-y-4">
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Product Technical Scope</label>
                  <textarea
                    value={ctoSpec}
                    onChange={e => setCtoSpec(e.target.value)}
                    rows={4}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-indigo-500 resize-none"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Preferred Cloud Platform</label>
                  <select
                    value={ctoCloud}
                    onChange={e => setCtoCloud(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-indigo-500"
                  >
                    <option value="AWS">Amazon Web Services (AWS)</option>
                    <option value="GCP">Google Cloud Platform (GCP)</option>
                    <option value="Azure">Microsoft Azure</option>
                    <option value="Vercel">Vercel Serverless Platform</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Compliance Needs (comma separated)</label>
                  <input
                    type="text"
                    value={ctoCompliance}
                    onChange={e => setCtoCompliance(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-indigo-500"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs py-2.5 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
                >
                  <Sparkles size={14} />
                  <span>{isLoading ? 'Running Tech Scanners...' : 'Analyze Architecture'}</span>
                </button>
              </form>
            </div>

            {/* Architecture Reports Output */}
            <div className="lg:col-span-2 space-y-6">
              {ctoReports.length === 0 ? (
                <div className="rounded-xl border border-dashed border-zinc-900 p-12 text-center text-zinc-500 text-xs">
                  No CTO architecture audits generated yet. Build a review via the configurator.
                </div>
              ) : (
                ctoReports.map(report => (
                  <div key={report.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-6 space-y-6">
                    {/* Header */}
                    <div className="flex justify-between items-start border-b border-zinc-900 pb-4">
                      <div>
                        <h3 className="font-bold text-lg text-white">{report.title}</h3>
                        <div className="text-[10px] text-zinc-500 mt-0.5">
                          Synthesized on {new Date(report.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleDownload(report.id, 'cto', 'pdf')}
                          className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300"
                        >
                          <Download size={12} />
                          <span>PDF</span>
                        </button>
                        <button
                          onClick={() => handleDownload(report.id, 'cto', 'ppt')}
                          className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300"
                        >
                          <Download size={12} />
                          <span>PPT</span>
                        </button>
                      </div>
                    </div>

                    {/* Stacks & Health metrics */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg md:col-span-1 space-y-2">
                        <h4 className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider">Recommended Stack</h4>
                        <div className="flex flex-wrap gap-1.5">
                          {report.architecture_review.tech_stack?.map((tech, idx) => (
                            <span key={idx} className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-mono px-2 py-0.5 rounded">
                              {tech}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg md:col-span-2 grid grid-cols-3 gap-2">
                        <div>
                          <span className="text-[9px] text-zinc-500 uppercase tracking-wider block">Target Uptime</span>
                          <span className="text-sm font-bold text-white">{report.health_metrics?.uptime_target}</span>
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-500 uppercase tracking-wider block">Target Latency</span>
                          <span className="text-sm font-bold text-white">{report.health_metrics?.api_latency_target}</span>
                        </div>
                        <div>
                          <span className="text-[9px] text-zinc-500 uppercase tracking-wider block">DB Pool status</span>
                          <span className="text-sm font-bold text-emerald-400">{report.health_metrics?.db_pool_status}</span>
                        </div>
                      </div>
                    </div>

                    {/* Cloud specifications */}
                    <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg">
                      <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center mb-2">
                        <HardDrive size={12} className="mr-1.5" /> Infrastructure & Cloud Planner ({report.architecture_review.cloud_infra?.cloud_provider})
                      </h4>
                      <pre className="font-sans text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed">
                        {report.architecture_review.cloud_infra?.specs_review_markdown}
                      </pre>
                    </div>

                    {/* Security Compliance & Technical debt */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center">
                          <ShieldCheck size={12} className="mr-1.5" /> Security & CI/CD Pipelines
                        </h4>
                        <div className="text-xs text-zinc-400">
                          Monitoring System: <strong className="text-white">{report.security_devops.compliance?.monitoring}</strong>
                        </div>
                        <pre className="font-sans text-[11px] text-zinc-300 mt-2 whitespace-pre-wrap">
                          {report.security_devops.compliance?.compliance_markdown}
                        </pre>
                      </div>

                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider flex items-center">
                          <AlertTriangle size={12} className="mr-1.5" /> Quality & Tech Debt Analysis
                        </h4>
                        <div className="text-xs text-zinc-400">
                          Quality Rating: <strong className="text-white">{report.technical_debt?.tech_debt_score}</strong>
                        </div>
                        <pre className="font-sans text-[11px] text-zinc-300 mt-2 whitespace-pre-wrap">
                          {report.technical_debt?.details?.debt_markdown}
                        </pre>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------
            TAB 3: AI COO
           ------------------------------------------------------------- */}
        {activeRole === 'coo' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Config Form */}
            <div className="lg:col-span-1 rounded-xl border border-zinc-900 bg-zinc-950 p-5 h-fit">
              <h2 className="text-md font-bold text-white mb-4 flex items-center">
                <Plus size={16} className="text-purple-400 mr-2" />
                Track Capacity & Sprint
              </h2>
              <form onSubmit={handleGenerateCOO} className="space-y-4">
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Active Sprint Name</label>
                  <input
                    type="text"
                    value={cooSprint}
                    onChange={e => setCooSprint(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-purple-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Team Roster (comma separated)</label>
                  <input
                    type="text"
                    value={cooTeam}
                    onChange={e => setCooTeam(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-purple-500"
                    required
                  />
                </div>
                <div>
                  <label className="text-xs text-zinc-400 block mb-1">Allocated Budget ($)</label>
                  <input
                    type="number"
                    value={cooBudget}
                    onChange={e => setCooBudget(Number(e.target.value))}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-purple-500"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white font-semibold text-xs py-2.5 rounded-lg transition duration-200 flex items-center justify-center space-x-2"
                >
                  <Sparkles size={14} />
                  <span>{isLoading ? 'Running Operations Audits...' : 'Log Operations Review'}</span>
                </button>
              </form>
            </div>

            {/* COO Reports Output */}
            <div className="lg:col-span-2 space-y-6">
              {cooReports.length === 0 ? (
                <div className="rounded-xl border border-dashed border-zinc-900 p-12 text-center text-zinc-500 text-xs">
                  No COO operations report generated yet. Compile logs via the configuration setup.
                </div>
              ) : (
                cooReports.map(report => (
                  <div key={report.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-6 space-y-6">
                    {/* Header */}
                    <div className="flex justify-between items-start border-b border-zinc-900 pb-4">
                      <div>
                        <h3 className="font-bold text-lg text-white">{report.title}</h3>
                        <div className="text-[10px] text-zinc-500 mt-0.5">
                          Synthesized on {new Date(report.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleDownload(report.id, 'coo', 'pdf')}
                          className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300"
                        >
                          <Download size={12} />
                          <span>PDF</span>
                        </button>
                        <button
                          onClick={() => handleDownload(report.id, 'coo', 'ppt')}
                          className="flex items-center space-x-1.5 px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 rounded-lg text-xs font-semibold text-zinc-300"
                        >
                          <Download size={12} />
                          <span>PPT</span>
                        </button>
                      </div>
                    </div>

                    {/* Team & Resources allocation */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-3">
                        <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center">
                          <Users size={12} className="mr-1.5" /> Resource Capacity Planning
                        </h4>
                        <div className="text-xs text-zinc-300">
                          Active Team Size: <strong className="text-white">{report.resource_capacity.team_size} members</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Weekly Productive Capacity: <strong className="text-white">{report.resource_capacity.capacity_hours_weekly} Hours</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Estimated Resource Utilization: <strong className="text-white">{(report.resource_capacity.utilization_rate_est * 100).toFixed(0)}%</strong>
                        </div>
                        <div className="mt-2 space-y-1">
                          <span className="text-[10px] text-zinc-500 uppercase tracking-wider block">Roster Details:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {report.resource_capacity.roster?.map((member, idx) => (
                              <span key={idx} className="bg-purple-500/10 border border-purple-500/20 text-purple-400 text-[10px] px-2 py-0.5 rounded-full">
                                {member}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Delivery & Sprint tracking */}
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-3">
                        <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider flex items-center">
                          <Clock size={12} className="mr-1.5" /> Delivery Track & Sprint Health
                        </h4>
                        <div className="text-xs text-zinc-300">
                          Active Sprint: <strong className="text-white">{report.delivery_monitoring.active_sprint}</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Sprint Delivery Target: <strong className="text-white">{report.delivery_monitoring.release_target_date}</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Risk Mitigation Actions:
                          <ul className="list-disc pl-4 text-zinc-400 text-[11px] mt-1 space-y-1">
                            {report.delivery_monitoring.risk_mitigation_actions?.map((action, idx) => (
                              <li key={idx}>{action}</li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>

                    {/* Operational risks & incidents notifications */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider">Operational Incidents & Risks</h4>
                        <div className="text-xs text-zinc-300">
                          S1 Incidents Open: <strong className="text-white">{report.incidents_risks.open_severity_1_incidents}</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          System Security Risk Rating: <strong className="text-white">{report.incidents_risks.risk_status}</strong>
                        </div>
                      </div>

                      <div className="bg-zinc-900/40 border border-zinc-900 p-4 rounded-lg space-y-2">
                        <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider">Financial runway analysis</h4>
                        <div className="text-xs text-zinc-300">
                          Allocated Budget pool: <strong className="text-white">${report.operations_analytics.allocated_budget.toLocaleString()}</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Burn Rate / Month: <strong className="text-white">${report.operations_analytics.burn_rate_monthly.toLocaleString()}</strong>
                        </div>
                        <div className="text-xs text-zinc-300">
                          Calculated Runway: <strong className="text-white">{report.operations_analytics.estimated_months_runway} Months</strong>
                        </div>
                      </div>
                    </div>

                    {/* Notification logs list */}
                    <div className="bg-zinc-900/20 border border-zinc-900 p-4 rounded-lg space-y-2">
                      <h4 className="text-[10px] font-bold text-purple-400 uppercase tracking-wider">Executive Notification Center</h4>
                      <div className="space-y-1">
                        {report.notification_center?.map((notif, idx) => (
                          <div key={idx} className="text-xs text-zinc-300 flex items-center space-x-2 leading-relaxed">
                            <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                            <span>{notif.message}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
