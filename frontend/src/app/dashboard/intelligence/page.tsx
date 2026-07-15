'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { apiService } from '@/lib/api';
import { useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import {
  Sparkles,
  TrendingUp,
  ShieldAlert,
  DollarSign,
  Briefcase,
  Users,
  HardDrive,
  Cpu,
  RefreshCw,
  Search,
  CheckCircle,
} from 'lucide-react';

interface MarketData {
  industry: string;
  pestle: string;
  swot: string;
}

interface CompetitorData {
  competitors: string[];
  matrix_markdown: string;
}

interface CostData {
  total_developers: number;
  total_qa: number;
  total_designers: number;
  monthly_infra_cost: number;
  monthly_ai_cost: number;
  total_monthly_burn: number;
  forecast_3yr_markdown: string;
}

interface RiskItem {
  category: string;
  severity: string;
  description: string;
  mitigation: string;
}

interface RiskData {
  overall_status: string;
  risks: RiskItem[];
}

function IntelligenceSuiteContent() {
  const { activeWorkspace } = useAuth();
  const searchParams = useSearchParams();
  const tabParam = searchParams.get('tab');
  
  const [activeTab, setActiveTab] = React.useState<'market' | 'competitors' | 'costs' | 'risks'>('market');
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    if (tabParam === 'market' || tabParam === 'competitors' || tabParam === 'costs' || tabParam === 'risks') {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  // States for each category
  const [marketData, setMarketData] = React.useState<MarketData | null>(null);
  const [competitorData, setCompetitorData] = React.useState<CompetitorData | null>(null);
  const [costData, setCostData] = React.useState<CostData | null>(null);
  const [riskData, setRiskData] = React.useState<RiskData | null>(null);

  const fetchMarketResearch = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    try {
      const res = await apiService.post<MarketData>(
        `/planning/intelligence/market-research?workspace_id=${activeWorkspace.id}`
      );
      setMarketData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCompetitorAnalysis = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    try {
      const res = await apiService.post<CompetitorData>(
        `/planning/intelligence/competitor-analysis?workspace_id=${activeWorkspace.id}`
      );
      setCompetitorData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCostEstimation = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    try {
      const res = await apiService.post<CostData>(
        `/planning/intelligence/cost-estimation?workspace_id=${activeWorkspace.id}`
      );
      setCostData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRiskAnalysis = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    try {
      const res = await apiService.post<RiskData>(
        `/planning/intelligence/risk-analysis?workspace_id=${activeWorkspace.id}`
      );
      setRiskData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto load when tab changes or active workspace changes
  React.useEffect(() => {
    if (!activeWorkspace) return;
    if (activeTab === 'market' && !marketData) fetchMarketResearch();
    if (activeTab === 'competitors' && !competitorData) fetchCompetitorAnalysis();
    if (activeTab === 'costs' && !costData) fetchCostEstimation();
    if (activeTab === 'risks' && !riskData) fetchRiskAnalysis();
  }, [activeTab, activeWorkspace]);

  const handleRunAnalysis = () => {
    if (activeTab === 'market') fetchMarketResearch();
    if (activeTab === 'competitors') fetchCompetitorAnalysis();
    if (activeTab === 'costs') fetchCostEstimation();
    if (activeTab === 'risks') fetchRiskAnalysis();
  };

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Header Breadcrumb */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Intelligence Suite' }]} />
          <div className="flex items-center justify-between mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center">
                <Sparkles className="mr-3 text-indigo-400" size={28} /> Dedicated Intelligence Suite
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Run deep market intelligence, SWOT/PESTLE audits, and aggregated risk and cost matrices.
              </p>
            </div>
            {activeWorkspace && (
              <button
                onClick={handleRunAnalysis}
                disabled={isLoading}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 border border-indigo-500 text-white hover:bg-indigo-700 disabled:opacity-50 transition-all text-xs font-bold uppercase tracking-wider shadow-[0_0_15px_rgba(99,102,241,0.2)]"
              >
                {isLoading ? (
                  <RefreshCw size={14} className="animate-spin" />
                ) : (
                  <RefreshCw size={14} />
                )}
                Run Analysis
              </button>
            )}
          </div>
        </div>

        {/* Workspace Block Check */}
        {!activeWorkspace ? (
          <div className="p-8 border border-zinc-900 bg-zinc-950/40 rounded-2xl text-center space-y-3">
            <div className="text-3xl">⚠️</div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">No Active Workspace</h3>
            <p className="text-xs text-zinc-500 max-w-xs mx-auto">
              Please select or create an active workspace from the sidebar menu to execute strategic intelligence modules.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Tab Selection Row */}
            <div className="flex border-b border-zinc-900 pb-px gap-2">
              <button
                onClick={() => setActiveTab('market')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'market'
                    ? 'border-indigo-500 text-indigo-400'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Market Research
              </button>
              <button
                onClick={() => setActiveTab('competitors')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'competitors'
                    ? 'border-indigo-500 text-indigo-400'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Competitor Analysis
              </button>
              <button
                onClick={() => setActiveTab('costs')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'costs'
                    ? 'border-indigo-500 text-indigo-400'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Cost Estimation
              </button>
              <button
                onClick={() => setActiveTab('risks')}
                className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all ${
                  activeTab === 'risks'
                    ? 'border-indigo-500 text-indigo-400'
                    : 'border-transparent text-zinc-400 hover:text-zinc-200'
                }`}
              >
                Risk Analysis
              </button>
            </div>

            {/* Content Switcher */}
            <div className="min-h-[300px]">
              {isLoading && (
                <div className="flex flex-col items-center justify-center py-20 space-y-4">
                  <RefreshCw size={28} className="text-indigo-500 animate-spin" />
                  <p className="text-xs text-zinc-500 animate-pulse uppercase tracking-wider font-extrabold">
                    AI Agent executing deep audits...
                  </p>
                </div>
              )}

              {!isLoading && (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeTab}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                  >
                    {/* Tab 1: Market Research */}
                    {activeTab === 'market' && (
                      <div className="space-y-6">
                        {marketData ? (
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-3">
                              <h3 className="text-xs font-extrabold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                                <TrendingUp size={14} /> PESTLE Analysis
                              </h3>
                              <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-3 bg-zinc-950 border border-zinc-900 rounded-xl max-h-[500px] overflow-y-auto">
                                {marketData.pestle}
                              </div>
                            </div>
                            <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-3">
                              <h3 className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                                <Search size={14} /> SWOT Profile
                              </h3>
                              <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-3 bg-zinc-950 border border-zinc-900 rounded-xl max-h-[500px] overflow-y-auto">
                                {marketData.swot}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-16 text-xs text-zinc-500">
                            No market research details generated. Click 'Run Analysis' to query.
                          </div>
                        )}
                      </div>
                    )}

                    {/* Tab 2: Competitor Analysis */}
                    {activeTab === 'competitors' && (
                      <div className="space-y-6">
                        {competitorData ? (
                          <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-4">
                            <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
                              <h3 className="text-xs font-extrabold uppercase tracking-wider text-violet-400">
                                Competitive Landscape Mapping
                              </h3>
                              <div className="flex gap-2">
                                {competitorData.competitors.map((c) => (
                                  <span
                                    key={c}
                                    className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] text-zinc-400"
                                  >
                                    {c}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-4 bg-zinc-950 border border-zinc-900 rounded-xl">
                              {competitorData.matrix_markdown}
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-16 text-xs text-zinc-500">
                            No competitive analysis records found. Click 'Run Analysis' to fetch.
                          </div>
                        )}
                      </div>
                    )}

                    {/* Tab 3: Cost Estimation */}
                    {activeTab === 'costs' && (
                      <div className="space-y-6">
                        {costData ? (
                          <div className="space-y-6">
                            {/* Aggregated Cost Stats */}
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                              <div className="p-4 border border-zinc-900 bg-zinc-950/50 rounded-2xl">
                                <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">
                                  Engineering Headcount
                                </div>
                                <div className="text-2xl font-black text-white mt-1 flex items-center gap-2">
                                  <Users className="text-indigo-400" size={20} />
                                  {costData.total_developers + costData.total_qa + costData.total_designers}
                                </div>
                                <div className="text-[9px] text-zinc-400 mt-0.5">
                                  {costData.total_developers} Devs · {costData.total_qa} QA · {costData.total_designers} Designers
                                </div>
                              </div>

                              <div className="p-4 border border-zinc-900 bg-zinc-950/50 rounded-2xl">
                                <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">
                                  Monthly Hosting Est.
                                </div>
                                <div className="text-2xl font-black text-white mt-1 flex items-center gap-2">
                                  <HardDrive className="text-emerald-400" size={20} />
                                  ${costData.monthly_infra_cost.toFixed(1)}
                                </div>
                                <div className="text-[9px] text-zinc-400 mt-0.5">
                                  Cloud servers, DB clusters, cache
                                </div>
                              </div>

                              <div className="p-4 border border-zinc-900 bg-zinc-950/50 rounded-2xl">
                                <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">
                                  Monthly AI/API Costs
                                </div>
                                <div className="text-2xl font-black text-white mt-1 flex items-center gap-2">
                                  <Cpu className="text-violet-400" size={20} />
                                  ${costData.monthly_ai_cost.toFixed(1)}
                                </div>
                                <div className="text-[9px] text-zinc-400 mt-0.5">
                                  LLM prompts, generation API tokens
                                </div>
                              </div>

                              <div className="p-4 border border-zinc-900 bg-zinc-950/50 rounded-2xl">
                                <div className="text-zinc-500 text-[10px] uppercase font-bold tracking-wider">
                                  Estimated Burn Rate
                                </div>
                                <div className="text-2xl font-black text-white mt-1 flex items-center gap-2">
                                  <DollarSign className="text-amber-400" size={20} />
                                  ${costData.total_monthly_burn.toLocaleString(undefined, { maximumFractionDigits: 0 })}/mo
                                </div>
                                <div className="text-[9px] text-zinc-400 mt-0.5">
                                  Fully loaded operational burn
                                </div>
                              </div>
                            </div>

                            {/* 3-Year Projection Details */}
                            <div className="p-6 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-3">
                              <h3 className="text-xs font-extrabold uppercase tracking-wider text-amber-400">
                                3-Year Budget Forecast & Financial Strategy
                              </h3>
                              <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-4 bg-zinc-950 border border-zinc-900 rounded-xl">
                                {costData.forecast_3yr_markdown}
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-16 text-xs text-zinc-500">
                            No resource cost estimates mapped. Click 'Run Analysis' to generate budget charts.
                          </div>
                        )}
                      </div>
                    )}

                    {/* Tab 4: Risk Analysis */}
                    {activeTab === 'risks' && (
                      <div className="space-y-6">
                        {riskData ? (
                          <div className="space-y-6">
                            {/* Operational Status Banner */}
                            <div className="p-4 rounded-xl border border-zinc-900 bg-zinc-950/80 flex items-center justify-between">
                              <div>
                                <div className="text-[10px] uppercase font-extrabold text-zinc-500">
                                  Workspace Risk Assessment
                                </div>
                                <div className="text-sm font-bold text-white mt-0.5">
                                  Current Status:{' '}
                                  <span
                                    className={
                                      riskData.overall_status === 'Critical Risk'
                                        ? 'text-red-400'
                                        : riskData.overall_status === 'Elevated Risk'
                                        ? 'text-amber-400'
                                        : 'text-emerald-400'
                                    }
                                  >
                                    {riskData.overall_status}
                                  </span>
                                </div>
                              </div>
                              <CheckCircle
                                className={
                                  riskData.overall_status === 'Normal Operations'
                                    ? 'text-emerald-400'
                                    : 'text-amber-400'
                                }
                                size={22}
                              />
                            </div>

                            {/* Risks Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              {riskData.risks.map((r, idx) => (
                                <div
                                  key={idx}
                                  className="p-5 border border-zinc-900 bg-zinc-950/40 rounded-2xl space-y-3"
                                >
                                  <div className="flex items-center justify-between">
                                    <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
                                      {r.category}
                                    </span>
                                    <span
                                      className={`text-[9px] font-black uppercase px-2 py-0.5 rounded ${
                                        r.severity === 'High'
                                          ? 'bg-red-950 border border-red-900/50 text-red-450'
                                          : r.severity === 'Medium'
                                          ? 'bg-amber-950 border border-amber-900/50 text-amber-450'
                                          : 'bg-zinc-900 border border-zinc-800 text-zinc-400'
                                      }`}
                                    >
                                      {r.severity}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="text-[10px] text-zinc-550 font-bold uppercase tracking-wider">
                                      Risk Description
                                    </div>
                                    <p className="text-xs text-zinc-300 leading-relaxed mt-1">
                                      {r.description}
                                    </p>
                                  </div>
                                  <div className="pt-2 border-t border-zinc-900/60">
                                    <div className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider">
                                      Mitigation Plan
                                    </div>
                                    <p className="text-xs text-zinc-400 leading-relaxed mt-1">
                                      {r.mitigation}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div className="text-center py-16 text-xs text-zinc-500">
                            No risk registers generated. Click 'Run Analysis' to audit workspace metrics.
                          </div>
                        )}
                      </div>
                    )}
                  </motion.div>
                </AnimatePresence>
              )}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}

export default function IntelligenceSuitePage() {
  return (
    <React.Suspense fallback={
      <div className="flex items-center justify-center min-h-[400px] text-zinc-500 animate-pulse text-xs">
        Loading...
      </div>
    }>
      <IntelligenceSuiteContent />
    </React.Suspense>
  );
}
