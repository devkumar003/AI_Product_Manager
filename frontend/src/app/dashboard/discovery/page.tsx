'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { useRouter } from 'next/navigation';
import {
  Sparkles,
  ArrowRight,
  ArrowLeft,
  Check,
  TrendingUp,
  Search,
  Users,
  Cpu,
  FileText,
  RefreshCw,
  Lightbulb,
  AlertCircle
} from 'lucide-react';

const STEPS = [
  { number: 1, label: 'Idea Validation', description: 'Define and validate the product concept' },
  { number: 2, label: 'Market Research', description: 'Run PESTLE and SWOT analysis' },
  { number: 3, label: 'Competitor Analysis', description: 'Map the competitive landscape' },
  { number: 4, label: 'Discovery Summary', description: 'Consolidate discovery insights' },
  { number: 5, label: 'Requirements Link', description: 'Prepare for PRD generation' },
];

interface MarketData {
  industry: string;
  pestle: string;
  swot: string;
}

interface CompetitorData {
  competitors: string[];
  matrix_markdown: string;
}

export default function DiscoveryDashboard() {
  const { activeWorkspace } = useAuth();
  const router = useRouter();

  const [currentStep, setCurrentStep] = React.useState(1);

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tab = params.get('tab');
      if (tab === 'idea') setCurrentStep(1);
      else if (tab === 'market') setCurrentStep(2);
      else if (tab === 'competitors') setCurrentStep(3);
      else if (tab === 'summary') setCurrentStep(4);
    }
  }, []);

  const [ideaText, setIdeaText] = React.useState('');
  const [validationResult, setValidationResult] = React.useState<any>(null);
  const [marketData, setMarketData] = React.useState<MarketData | null>(null);
  const [competitorData, setCompetitorData] = React.useState<CompetitorData | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  // Sync workspace description when workspace changes
  React.useEffect(() => {
    if (activeWorkspace) {
      setIdeaText(activeWorkspace.description || '');
      setValidationResult(null);
      setMarketData(null);
      setCompetitorData(null);
      setCurrentStep(1);
    }
  }, [activeWorkspace]);

  // Load existing cached workspace insights if they exist
  React.useEffect(() => {
    if (!activeWorkspace) return;
    const loadCachedData = async () => {
      try {
        // We can query market research cache
        const marketRes = await apiService.post<MarketData>(
          `/planning/intelligence/market-research?workspace_id=${activeWorkspace.id}`
        ).catch(() => null);
        if (marketRes) setMarketData(marketRes);

        const compRes = await apiService.post<CompetitorData>(
          `/planning/intelligence/competitor-analysis?workspace_id=${activeWorkspace.id}`
        ).catch(() => null);
        if (compRes) setCompetitorData(compRes);
      } catch (e) {
        console.warn('Failed to load cached insights:', e);
      }
    };
    loadCachedData();
  }, [activeWorkspace]);

  const handleUpdateWorkspaceDesc = async () => {
    if (!activeWorkspace || !ideaText.trim()) return;
    try {
      await apiService.put(`/workspaces/${activeWorkspace.id}`, {
        name: activeWorkspace.name,
        description: ideaText
      });
    } catch (e) {
      console.error('Failed to sync idea with workspace description:', e);
    }
  };

  const runIdeaValidation = async () => {
    if (!activeWorkspace || !ideaText.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      // 1. Sync description to workspace (passes context downstream)
      await handleUpdateWorkspaceDesc();

      // 2. Execute validation engine
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'idea_validation',
        workspace_id: activeWorkspace.id,
        input_data: { idea: ideaText }
      });
      setValidationResult(data.result || data);
    } catch (e: any) {
      setError(e.message || 'Failed to run idea validation');
    } finally {
      setIsLoading(false);
    }
  };

  const runMarketResearch = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    setError(null);
    try {
      // Pass force refresh to backend to capture new workspace description
      const res = await apiService.post<MarketData>(
        `/planning/intelligence/market-research?workspace_id=${activeWorkspace.id}&refresh=true`
      );
      setMarketData(res);
    } catch (e: any) {
      setError(e.message || 'Failed to run market research');
    } finally {
      setIsLoading(false);
    }
  };

  const runCompetitorAnalysis = async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await apiService.post<CompetitorData>(
        `/planning/intelligence/competitor-analysis?workspace_id=${activeWorkspace.id}&refresh=true`
      );
      setCompetitorData(res);
    } catch (e: any) {
      setError(e.message || 'Failed to run competitor analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep < 5) setCurrentStep(currentStep + 1);
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1);
  };

  const navigateToRequirements = () => {
    if (!activeWorkspace) return;
    // Redirect to requirements dashboard, pre-filling idea context if necessary
    router.push(`/dashboard/requirements?tab=prd&workspace_id=${activeWorkspace.id}`);
  };

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
          <Lightbulb className="text-zinc-600 animate-pulse" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm max-w-sm">
            Choose or create a workspace to view your autonomous product discovery workflow.
          </p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Breadcrumbs and Title */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Discovery Dashboard' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-2 flex items-center gap-3">
            <Sparkles className="text-indigo-400" size={28} /> Product Discovery Suite
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            Validate concepts, generate market audits, and establish product direction.
          </p>
        </div>

        {/* Guided Steps Progress Tracker */}
        <div className="bg-zinc-950/80 border border-zinc-900 rounded-2xl p-6">
          <div className="relative flex items-center justify-between">
            {/* Progress line */}
            <div className="absolute left-0 right-0 top-1/2 h-0.5 bg-zinc-900 -translate-y-1/2 z-0" />
            <div
              className="absolute left-0 top-1/2 h-0.5 bg-indigo-600 -translate-y-1/2 transition-all duration-550 z-0"
              style={{ width: `${((currentStep - 1) / 4) * 100}%` }}
            />

            {STEPS.map((step) => {
              const isCompleted = step.number < currentStep;
              const isActive = step.number === currentStep;

              return (
                <div key={step.number} className="relative z-10 flex flex-col items-center">
                  <button
                    onClick={() => {
                      // Allow navigating to previously completed steps or next step if validated
                      if (step.number <= currentStep || (step.number === 2 && validationResult) || (step.number === 3 && marketData) || (step.number === 4 && competitorData)) {
                        setCurrentStep(step.number);
                      }
                    }}
                    className={`w-10 h-10 rounded-full flex items-center justify-center border-2 font-bold text-sm transition-all duration-300 ${
                      isCompleted
                        ? 'border-indigo-600 bg-indigo-600 text-white shadow-[0_0_15px_rgba(99,102,241,0.4)]'
                        : isActive
                        ? 'border-indigo-500 bg-zinc-950 text-indigo-400 shadow-[0_0_10px_rgba(99,102,241,0.2)]Scale-105'
                        : 'border-zinc-800 bg-zinc-950 text-zinc-500'
                    }`}
                  >
                    {isCompleted ? <Check size={16} /> : step.number}
                  </button>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider mt-2.5 hidden md:block transition ${
                      isActive ? 'text-indigo-400' : 'text-zinc-500'
                    }`}
                  >
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Dynamic Step Panels */}
        <div className="min-h-[400px]">
          <AnimatePresence mode="wait">
            {currentStep === 1 && (
              <motion.div
                key="step1"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Lightbulb size={20} className="text-amber-400" /> Describe Your Product Concept
                  </h3>
                  <p className="text-xs text-zinc-400">
                    Input your initial idea or business problem. Running the validator clasifies market positioning, feasibility scores, and generates core product dimensions.
                  </p>
                  <textarea
                    value={ideaText}
                    onChange={(e) => setIdeaText(e.target.value)}
                    rows={6}
                    placeholder="Describe your product idea, target audience, and key pain points to solve..."
                    className="w-full bg-zinc-900/60 border border-zinc-850 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-600 focus:border-indigo-500/40 focus:ring-1 focus:ring-indigo-500/20 outline-none resize-none"
                  />
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-zinc-500">
                      Context will automatically update workspace details to sync downstream.
                    </span>
                    <button
                      onClick={runIdeaValidation}
                      disabled={isLoading || !ideaText.trim()}
                      className="px-6 py-2.5 rounded-lg bg-indigo-650 hover:bg-indigo-600 text-white font-semibold text-sm transition active:scale-95 disabled:bg-zinc-850 disabled:text-zinc-600 flex items-center gap-2"
                    >
                      {isLoading ? (
                        <>
                          <RefreshCw size={14} className="animate-spin" /> Validating Concept...
                        </>
                      ) : (
                        'Validate Concept & Continue'
                      )}
                    </button>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-950/20 border border-red-900/50 rounded-xl p-4 text-red-400 text-xs flex items-center gap-2">
                    <AlertCircle size={16} />
                    {error}
                  </div>
                )}

                {validationResult && (
                  <div className="bg-zinc-950/40 border border-zinc-900 rounded-2xl p-6 space-y-4">
                    <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
                      <h4 className="text-sm font-bold text-white">Validation Assessment Details</h4>
                      <span className="px-2 py-0.5 rounded bg-emerald-950 border border-emerald-900 text-[10px] font-bold text-emerald-400">
                        SUCCESSFULLY ANALYZED
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(validationResult).map(([key, val]: any) => (
                        <div key={key} className="p-4 bg-zinc-950/80 border border-zinc-900 rounded-xl space-y-1">
                          <div className="text-[10px] uppercase font-bold text-zinc-500">
                            {key.replace(/_/g, ' ')}
                          </div>
                          <div className="text-xs text-zinc-250 leading-relaxed">
                            {typeof val === 'object' ? JSON.stringify(val) : String(val)}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="flex justify-end pt-2">
                      <button
                        onClick={handleNext}
                        className="px-5 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white hover:bg-zinc-800 text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition"
                      >
                        Next Step <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {currentStep === 2 && (
              <motion.div
                key="step2"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <TrendingUp size={20} className="text-indigo-400" /> Market Audit & PESTLE/SWOT Analysis
                      </h3>
                      <p className="text-xs text-zinc-400 mt-1">
                        Examine external macroeconomic parameters and internal corporate matrices.
                      </p>
                    </div>
                    <button
                      onClick={runMarketResearch}
                      disabled={isLoading}
                      className="px-4 py-2 bg-indigo-650 hover:bg-indigo-600 text-white rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 disabled:opacity-50 transition"
                    >
                      {isLoading ? (
                        <RefreshCw size={12} className="animate-spin" />
                      ) : (
                        <RefreshCw size={12} />
                      )}
                      Run Market Analysis
                    </button>
                  </div>

                  {marketData ? (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pt-4">
                      <div className="p-5 bg-zinc-950/90 border border-zinc-900 rounded-xl space-y-2">
                        <h4 className="text-xs font-extrabold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                          <TrendingUp size={12} /> PESTLE Analysis
                        </h4>
                        <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-3 bg-zinc-950 border border-zinc-900 rounded-lg max-h-[400px] overflow-y-auto">
                          {marketData.pestle}
                        </div>
                      </div>
                      <div className="p-5 bg-zinc-950/90 border border-zinc-900 rounded-xl space-y-2">
                        <h4 className="text-xs font-extrabold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                          <Search size={12} /> SWOT Matrix
                        </h4>
                        <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-3 bg-zinc-950 border border-zinc-900 rounded-lg max-h-[400px] overflow-y-auto">
                          {marketData.swot}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                      No market research outputs computed yet. Execute the analysis using the button above.
                    </div>
                  )}

                  <div className="flex justify-between items-center pt-4 border-t border-zinc-900/60 mt-6">
                    <button
                      onClick={handleBack}
                      className="px-4 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
                    >
                      <ArrowLeft size={14} /> Back
                    </button>
                    <button
                      onClick={handleNext}
                      disabled={!marketData}
                      className="px-5 py-2 rounded-lg bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition"
                    >
                      Next Step <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {currentStep === 3 && (
              <motion.div
                key="step3"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-white flex items-center gap-2">
                        <Users size={20} className="text-violet-400" /> Competitor Intelligence & Landscape Mapping
                      </h3>
                      <p className="text-xs text-zinc-400 mt-1">
                        Map competitive advantages, features parity, and strategic product gaps.
                      </p>
                    </div>
                    <button
                      onClick={runCompetitorAnalysis}
                      disabled={isLoading}
                      className="px-4 py-2 bg-indigo-650 hover:bg-indigo-600 text-white rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-2 disabled:opacity-50 transition"
                    >
                      {isLoading ? (
                        <RefreshCw size={12} className="animate-spin" />
                      ) : (
                        <RefreshCw size={12} />
                      )}
                      Run Competitor Mapping
                    </button>
                  </div>

                  {competitorData ? (
                    <div className="p-5 bg-zinc-950/90 border border-zinc-900 rounded-xl space-y-4 pt-4">
                      <div className="flex flex-wrap gap-2 pb-2">
                        {competitorData.competitors.map((c) => (
                          <span
                            key={c}
                            className="px-2.5 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-[10px] font-bold text-zinc-400"
                          >
                            {c}
                          </span>
                        ))}
                      </div>
                      <div className="text-xs text-zinc-300 whitespace-pre-wrap leading-relaxed font-mono p-4 bg-zinc-950 border border-zinc-900 rounded-lg max-h-[400px] overflow-y-auto">
                        {competitorData.matrix_markdown}
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-20 text-xs text-zinc-500 border border-dashed border-zinc-900 rounded-xl">
                      No competitive matrices generated yet. Click 'Run Competitor Mapping' to trigger.
                    </div>
                  )}

                  <div className="flex justify-between items-center pt-4 border-t border-zinc-900/60 mt-6">
                    <button
                      onClick={handleBack}
                      className="px-4 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
                    >
                      <ArrowLeft size={14} /> Back
                    </button>
                    <button
                      onClick={handleNext}
                      disabled={!competitorData}
                      className="px-5 py-2 rounded-lg bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition"
                    >
                      Next Step <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {currentStep === 4 && (
              <motion.div
                key="step4"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <FileText size={20} className="text-emerald-400" /> Discovery Phase Summary
                  </h3>
                  <p className="text-xs text-zinc-400">
                    Review and verify the consolidated output of the discovery sprint before generating the requirements document.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4">
                    {/* Val Card */}
                    <div className="p-5 bg-zinc-950/80 border border-zinc-900 rounded-xl space-y-2.5">
                      <span className="text-[9px] uppercase font-bold px-2 py-0.5 rounded bg-indigo-950/30 border border-indigo-900/50 text-indigo-400">
                        Idea Status
                      </span>
                      <h4 className="text-xs font-bold text-white mt-1">Validated Concept</h4>
                      <p className="text-[11px] text-zinc-400 line-clamp-4 leading-relaxed">
                        {ideaText}
                      </p>
                    </div>

                    {/* Market Card */}
                    <div className="p-5 bg-zinc-950/80 border border-zinc-900 rounded-xl space-y-2.5">
                      <span className="text-[9px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-950/30 border border-emerald-900/50 text-emerald-400">
                        Macro Audit
                      </span>
                      <h4 className="text-xs font-bold text-white mt-1">PESTLE / SWOT Metrics</h4>
                      <p className="text-[11px] text-zinc-400 line-clamp-4 leading-relaxed">
                        {marketData ? marketData.pestle : 'Not generated'}
                      </p>
                    </div>

                    {/* Competitors Card */}
                    <div className="p-5 bg-zinc-950/80 border border-zinc-900 rounded-xl space-y-2.5">
                      <span className="text-[9px] uppercase font-bold px-2 py-0.5 rounded bg-violet-950/30 border border-violet-900/50 text-violet-400">
                        Market Position
                      </span>
                      <h4 className="text-xs font-bold text-white mt-1">Competitors parity</h4>
                      <p className="text-[11px] text-zinc-400 line-clamp-4 leading-relaxed">
                        {competitorData ? competitorData.matrix_markdown : 'Not generated'}
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-4 border-t border-zinc-900/60 mt-6">
                    <button
                      onClick={handleBack}
                      className="px-4 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
                    >
                      <ArrowLeft size={14} /> Back
                    </button>
                    <button
                      onClick={handleNext}
                      className="px-5 py-2 rounded-lg bg-indigo-650 hover:bg-indigo-600 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 transition"
                    >
                      Continue to Requirements <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {currentStep === 5 && (
              <motion.div
                key="step5"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="space-y-6"
              >
                <div className="p-8 bg-zinc-950/40 border border-zinc-900 rounded-2xl text-center space-y-6 max-w-xl mx-auto">
                  <div className="w-16 h-16 rounded-full bg-indigo-600/10 border border-indigo-500/30 flex items-center justify-center mx-auto text-indigo-400 animate-bounce">
                    <Cpu size={32} />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-white">Discovery Hand-off Ready</h3>
                    <p className="text-sm text-zinc-400 mt-2 leading-relaxed">
                      All discovery milestones are complete. The context has been synchronized to the active workspace. You are ready to generate a comprehensive Product Requirement Document (PRD) pre-seeded with this information.
                    </p>
                  </div>

                  <div className="flex justify-center gap-3">
                    <button
                      onClick={handleBack}
                      className="px-5 py-2 rounded-lg bg-zinc-900 border border-zinc-800 text-white text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
                    >
                      <ArrowLeft size={14} /> Back
                    </button>
                    <button
                      onClick={navigateToRequirements}
                      className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-extrabold uppercase tracking-wider rounded-lg shadow-[0_0_20px_rgba(99,102,241,0.3)] flex items-center gap-2 transition"
                    >
                      <FileText size={16} /> Generate PRD Specifications
                    </button>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </AppShell>
  );
}
