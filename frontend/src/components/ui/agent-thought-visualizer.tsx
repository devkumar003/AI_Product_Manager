"use client";

import React, { useState } from "react";
import {
  Brain,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Cpu,
  Layers,
  GitBranch,
  ShieldCheck,
  Terminal,
  Play,
  RotateCcw,
  Wifi,
  WifiOff,
  Zap,
} from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { motion, AnimatePresence } from "framer-motion";

export function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

export interface ThoughtStep {
  id: string;
  agentName: string;
  roleIcon?: "brain" | "cpu" | "layers" | "git" | "shield" | "terminal";
  status: "pending" | "active" | "completed" | "error";
  message: string;
  timestamp?: string;
  details?: string[];
  metrics?: {
    latencyMs?: number;
    tokensUsed?: number;
    model?: string;
  };
}

export interface AgentThoughtVisualizerProps {
  steps: ThoughtStep[];
  isGenerating?: boolean;
  isConnected?: boolean;
  isSimulated?: boolean;
  title?: string;
  subtitle?: string;
  onStepClick?: (step: ThoughtStep) => void;
  onRunPipeline?: () => void;
  onSimulateError?: () => void;
  onResetPipeline?: () => void;
  className?: string;
}

export function AgentThoughtVisualizer({
  steps = [],
  isGenerating = false,
  isConnected = false,
  isSimulated = true,
  title = "AI Executive Hivemind Pipeline",
  subtitle = "Real-time cross-functional reasoning and self-healing JSON synthesis",
  onStepClick,
  onRunPipeline,
  onSimulateError,
  onResetPipeline,
  className,
}: AgentThoughtVisualizerProps) {
  const [expandedSteps, setExpandedSteps] = useState<Record<string, boolean>>({});

  const toggleExpand = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedSteps((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const getRoleIcon = (iconType?: string) => {
    switch (iconType) {
      case "brain":
        return <Brain className="w-5 h-5 text-indigo-400" />;
      case "cpu":
        return <Cpu className="w-5 h-5 text-cyan-400" />;
      case "layers":
        return <Layers className="w-5 h-5 text-purple-400" />;
      case "git":
        return <GitBranch className="w-5 h-5 text-emerald-400" />;
      case "shield":
        return <ShieldCheck className="w-5 h-5 text-amber-400" />;
      case "terminal":
        return <Terminal className="w-5 h-5 text-pink-400" />;
      default:
        return <Sparkles className="w-5 h-5 text-violet-400" />;
    }
  };

  const getStatusBadge = (status: ThoughtStep["status"]) => {
    switch (status) {
      case "active":
        return (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/15 border border-indigo-500/40 text-indigo-300 text-xs font-semibold shadow-[0_0_15px_rgba(99,102,241,0.4)]"
          >
            <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
            <span>Reasoning...</span>
          </motion.div>
        );
      case "completed":
        return (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-emerald-300 text-xs font-semibold shadow-[0_0_12px_rgba(16,185,129,0.3)]"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Verified</span>
          </motion.div>
        );
      case "error":
        return (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/15 border border-rose-500/40 text-rose-300 text-xs font-semibold shadow-[0_0_12px_rgba(244,63,94,0.3)] animate-pulse"
          >
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>Self-Healing Loop</span>
          </motion.div>
        );
      case "pending":
      default:
        return (
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-slate-400 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-slate-600" />
            <span>Queued</span>
          </div>
        );
    }
  };

  const completedCount = steps.filter((s) => s.status === "completed").length;
  const progressPercentage = steps.length > 0 ? Math.round((completedCount / steps.length) * 100) : 0;

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900/95 via-slate-900/98 to-slate-950 p-6 border border-slate-800/90 shadow-2xl backdrop-blur-xl transition-all duration-300",
        className
      )}
    >
      {/* Background ambient glowing spheres */}
      <div className="absolute -top-24 -left-24 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-violet-500/10 rounded-full blur-3xl pointer-events-none animate-pulse" />

      {/* Header section */}
      <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800/80">
        <div className="flex items-center gap-3.5">
          <div className="p-3 rounded-xl bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-pink-500/10 border border-indigo-500/30 shadow-[0_0_20px_rgba(99,102,241,0.25)]">
            <Brain className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <div className="flex items-center gap-2.5 flex-wrap">
              <h3 className="text-lg font-bold bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
                {title}
              </h3>
              {isConnected ? (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-emerald-500/15 border border-emerald-500/40 text-[11px] font-medium text-emerald-300">
                  <Wifi className="w-3 h-3 text-emerald-400" /> Live WebSocket
                </span>
              ) : isSimulated ? (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-cyan-500/15 border border-cyan-500/40 text-[11px] font-medium text-cyan-300">
                  <Zap className="w-3 h-3 text-cyan-400" /> Live Simulation
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[11px] font-medium text-slate-400">
                  <WifiOff className="w-3 h-3 text-slate-500" /> Offline
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
          </div>
        </div>

        {/* Action Controls & Status */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {onRunPipeline && (
            <button
              onClick={onRunPipeline}
              disabled={isGenerating}
              className={cn(
                "flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 shadow-md",
                isGenerating
                  ? "bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed"
                  : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white border border-indigo-400/30 shadow-[0_0_15px_rgba(99,102,241,0.3)] hover:scale-[1.02]"
              )}
            >
              {isGenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
              <span>{isGenerating ? "Pipeline Running..." : "Run AI Pipeline"}</span>
            </button>
          )}

          {onSimulateError && (
            <button
              onClick={onSimulateError}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 hover:bg-rose-950/40 border border-slate-700/80 hover:border-rose-500/50 text-slate-300 hover:text-rose-200 text-xs font-medium transition-all duration-200"
              title="Simulate self-healing error state"
            >
              <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
              <span>Test Self-Healing</span>
            </button>
          )}

          {onResetPipeline && (
            <button
              onClick={onResetPipeline}
              className="p-1.5 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-700/80 text-slate-400 hover:text-white transition-colors"
              title="Reset reasoning chain"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {steps.length > 0 && (
        <div className="relative z-10 mt-5 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2.5">
            <span className="text-xs font-medium text-slate-300">Pipeline Completion:</span>
            <span className="text-xs font-bold text-indigo-300 font-mono">{completedCount} / {steps.length} Steps ({progressPercentage}%)</span>
          </div>
          <div className="flex-1 max-w-md bg-slate-800/80 h-2 rounded-full overflow-hidden border border-slate-700/50">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${progressPercentage}%` }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-emerald-400 rounded-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"
            />
          </div>
        </div>
      )}

      {/* Steps timeline */}
      <div className="relative z-10 mt-5 space-y-3.5">
        <AnimatePresence mode="popLayout">
          {steps.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="text-center py-12 px-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/40"
            >
              <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-2.5 animate-bounce" />
              <p className="text-sm font-semibold text-slate-300">No agent reasoning steps recorded yet.</p>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">Click &ldquo;Run AI Pipeline&rdquo; above to trigger the multi-agent Hivemind and watch real-time reasoning and schema validation.</p>
            </motion.div>
          ) : (
            steps.map((step, index) => {
              const isExpanded = expandedSteps[step.id] || step.status === "active" || step.status === "error";
              const isLast = index === steps.length - 1;

              return (
                <motion.div
                  key={step.id}
                  layout
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  onClick={() => onStepClick && onStepClick(step)}
                  className={cn(
                    "group relative rounded-xl border transition-all duration-300 p-4 cursor-pointer",
                    step.status === "active"
                      ? "bg-slate-800/90 border-indigo-500/60 shadow-[0_0_30px_rgba(99,102,241,0.2)] scale-[1.01]"
                      : step.status === "error"
                      ? "bg-rose-950/25 border-rose-500/50 hover:bg-rose-900/35 shadow-[0_0_20px_rgba(244,63,94,0.15)]"
                      : step.status === "completed"
                      ? "bg-slate-900/70 border-slate-800/90 hover:bg-slate-800/60 hover:border-slate-700/80"
                      : "bg-slate-900/40 border-slate-800/60 opacity-80 hover:opacity-100"
                  )}
                >
                  {/* Connecting timeline line */}
                  {!isLast && (
                    <div className="absolute left-8 top-14 bottom-0 w-0.5 bg-gradient-to-b from-slate-700 via-slate-800 to-transparent -mb-3 z-0" />
                  )}

                  <div className="relative z-10 flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3.5 flex-1 min-w-0">
                      <div
                        className={cn(
                          "p-2.5 rounded-xl border flex-shrink-0 transition-transform duration-300 group-hover:scale-105",
                          step.status === "active"
                            ? "bg-indigo-500/20 border-indigo-500/50 shadow-[0_0_15px_rgba(99,102,241,0.3)]"
                            : step.status === "completed"
                            ? "bg-emerald-500/10 border-emerald-500/30"
                            : step.status === "error"
                            ? "bg-rose-500/20 border-rose-500/50 animate-pulse"
                            : "bg-slate-800 border-slate-700"
                        )}
                      >
                        {getRoleIcon(step.roleIcon)}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-sm font-bold text-white tracking-tight">
                            {step.agentName}
                          </span>
                          {step.timestamp && (
                            <span className="text-[11px] text-slate-500 font-mono">
                              {step.timestamp}
                            </span>
                          )}
                        </div>

                        <p
                          className={cn(
                            "text-sm mt-1 leading-relaxed transition-colors duration-200",
                            step.status === "active"
                              ? "text-indigo-200 font-medium"
                              : step.status === "error"
                              ? "text-rose-200 font-medium"
                              : "text-slate-300"
                          )}
                        >
                          {step.message}
                        </p>

                        {/* Metrics pill bar */}
                        {step.metrics && (
                          <div className="flex items-center gap-2.5 flex-wrap mt-3 pt-2.5 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                            {step.metrics.model && (
                              <span className="bg-slate-950/80 px-2 py-0.5 rounded border border-slate-800 text-indigo-300 flex items-center gap-1">
                                <Cpu className="w-3 h-3 text-indigo-400" /> {step.metrics.model}
                              </span>
                            )}
                            {step.metrics.latencyMs !== undefined && (
                              <span className="bg-slate-950/60 px-2 py-0.5 rounded border border-slate-800/80 text-emerald-300">
                                ⚡ {step.metrics.latencyMs}ms
                              </span>
                            )}
                            {step.metrics.tokensUsed !== undefined && (
                              <span className="bg-slate-950/60 px-2 py-0.5 rounded border border-slate-800/80 text-purple-300">
                                📊 {step.metrics.tokensUsed.toLocaleString()} tokens
                              </span>
                            )}
                          </div>
                        )}

                        {/* Expandable details section */}
                        {step.details && step.details.length > 0 && (
                          <div className="mt-3">
                            <button
                              type="button"
                              onClick={(e) => toggleExpand(step.id, e)}
                              className="flex items-center gap-1.5 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition-colors py-1"
                            >
                              {isExpanded ? (
                                <ChevronDown className="w-3.5 h-3.5" />
                              ) : (
                                <ChevronRight className="w-3.5 h-3.5" />
                              )}
                              <span>
                                {isExpanded ? "Hide reasoning chain" : `View reasoning details (${step.details.length})`}
                              </span>
                            </button>

                            <AnimatePresence>
                              {isExpanded && (
                                <motion.div
                                  initial={{ height: 0, opacity: 0 }}
                                  animate={{ height: "auto", opacity: 1 }}
                                  exit={{ height: 0, opacity: 0 }}
                                  transition={{ duration: 0.25 }}
                                  className="overflow-hidden"
                                >
                                  <div className="mt-2 pl-3 border-l-2 border-indigo-500/40 space-y-1.5 pt-1">
                                    {step.details.map((detail, dIdx) => (
                                      <div
                                        key={dIdx}
                                        className="text-xs text-slate-300 bg-slate-950/70 p-2.5 rounded-lg border border-slate-800/90 font-mono leading-relaxed shadow-sm"
                                      >
                                        {detail}
                                      </div>
                                    ))}
                                  </div>
                                </motion.div>
                              )}
                            </AnimatePresence>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex-shrink-0 ml-2">{getStatusBadge(step.status)}</div>
                  </div>
                </motion.div>
              );
            })
          )}
        </AnimatePresence>
      </div>

      {/* Footer system status */}
      <div className="relative z-10 mt-6 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-medium text-slate-300">Self-Healing JSON Engine:</span>
          <span className="text-emerald-400 font-mono">100% Pydantic Schema Compliant</span>
        </div>
        <div className="flex items-center gap-3 font-mono text-[11px] text-slate-500">
          <span>Failover Matrix: Active</span>
          <span>•</span>
          <span>Topological Scheduler: Kahn&apos;s Engine</span>
        </div>
      </div>
    </div>
  );
}

