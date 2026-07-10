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
} from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

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
  title?: string;
  subtitle?: string;
  onStepClick?: (step: ThoughtStep) => void;
  className?: string;
}

export function AgentThoughtVisualizer({
  steps = [],
  isGenerating = false,
  title = "AI Executive Hivemind Pipeline",
  subtitle = "Real-time cross-functional reasoning and self-healing JSON synthesis",
  onStepClick,
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
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-medium animate-pulse shadow-[0_0_12px_rgba(99,102,241,0.3)]">
            <Loader2 className="w-3.5 h-3.5 animate-spin text-indigo-400" />
            <span>Reasoning...</span>
          </div>
        );
      case "completed":
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-medium shadow-[0_0_10px_rgba(16,185,129,0.2)]">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Verified</span>
          </div>
        );
      case "error":
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-medium shadow-[0_0_10px_rgba(244,63,94,0.2)]">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>Self-Healing</span>
          </div>
        );
      case "pending":
      default:
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800/60 border border-slate-700/50 text-slate-400 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-slate-600" />
            <span>Queued</span>
          </div>
        );
    }
  };

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900/90 via-slate-900/95 to-slate-950/90 p-6 border border-slate-800/80 shadow-2xl backdrop-blur-xl transition-all duration-300",
        className
      )}
    >
      {/* Background ambient glowing spheres */}
      <div className="absolute -top-24 -left-24 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none animate-pulse" />
      <div className="absolute -bottom-24 -right-24 w-64 h-64 bg-violet-500/10 rounded-full blur-3xl pointer-events-none animate-pulse" />

      {/* Header section */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 border border-indigo-500/30 shadow-[0_0_15px_rgba(99,102,241,0.2)]">
            <Brain className="w-6 h-6 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold bg-gradient-to-r from-white via-slate-100 to-slate-300 bg-clip-text text-transparent">
              {title}
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isGenerating ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-pink-500/20 border border-indigo-500/40 text-indigo-200 text-xs font-semibold tracking-wide uppercase shadow-[0_0_20px_rgba(99,102,241,0.3)]">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
              <span>Pipeline Active</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300 text-xs font-medium">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Ready for Synthesis</span>
            </div>
          )}
        </div>
      </div>

      {/* Steps timeline */}
      <div className="relative z-10 mt-6 space-y-3">
        {steps.length === 0 ? (
          <div className="text-center py-12 px-4 rounded-xl border border-dashed border-slate-800 bg-slate-900/40">
            <Sparkles className="w-8 h-8 text-slate-600 mx-auto mb-2 animate-bounce" />
            <p className="text-sm font-medium text-slate-400">No agent reasoning steps recorded yet.</p>
            <p className="text-xs text-slate-500 mt-1">Initiate a product vision or backlog synthesis to watch the hivemind think.</p>
          </div>
        ) : (
          steps.map((step, index) => {
            const isExpanded = expandedSteps[step.id] || step.status === "active";
            const isLast = index === steps.length - 1;

            return (
              <div
                key={step.id}
                onClick={() => onStepClick && onStepClick(step)}
                className={cn(
                  "group relative rounded-xl border transition-all duration-300 p-4 cursor-pointer",
                  step.status === "active"
                    ? "bg-slate-800/80 border-indigo-500/50 shadow-[0_0_25px_rgba(99,102,241,0.15)] scale-[1.01]"
                    : step.status === "error"
                    ? "bg-rose-950/20 border-rose-500/40 hover:bg-rose-900/30"
                    : "bg-slate-900/60 border-slate-800 hover:bg-slate-800/50 hover:border-slate-700/80"
                )}
              >
                {/* Connecting timeline line */}
                {!isLast && (
                  <div className="absolute left-8 top-14 bottom-0 w-0.5 bg-gradient-to-b from-slate-700 via-slate-800 to-transparent -mb-3 z-0" />
                )}

                <div className="relative z-10 flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <div
                      className={cn(
                        "p-2 rounded-lg border flex-shrink-0 transition-transform duration-300 group-hover:scale-105",
                        step.status === "active"
                          ? "bg-indigo-500/20 border-indigo-500/40 shadow-inner"
                          : step.status === "completed"
                          ? "bg-emerald-500/10 border-emerald-500/30"
                          : step.status === "error"
                          ? "bg-rose-500/20 border-rose-500/40"
                          : "bg-slate-800 border-slate-700"
                      )}
                    >
                      {getRoleIcon(step.roleIcon)}
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-semibold text-white tracking-tight">
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
                          "text-sm mt-1 transition-colors duration-200",
                          step.status === "active"
                            ? "text-indigo-200 font-medium"
                            : step.status === "error"
                            ? "text-rose-200"
                            : "text-slate-300"
                        )}
                      >
                        {step.message}
                      </p>

                      {/* Metrics pill bar */}
                      {step.metrics && (
                        <div className="flex items-center gap-3 mt-2.5 pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-400">
                          {step.metrics.model && (
                            <span className="bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700/60 text-slate-300">
                              🤖 {step.metrics.model}
                            </span>
                          )}
                          {step.metrics.latencyMs !== undefined && (
                            <span>⚡ {step.metrics.latencyMs}ms</span>
                          )}
                          {step.metrics.tokensUsed !== undefined && (
                            <span>📊 {step.metrics.tokensUsed.toLocaleString()} tokens</span>
                          )}
                        </div>
                      )}

                      {/* Expandable details section */}
                      {step.details && step.details.length > 0 && (
                        <div className="mt-3">
                          <button
                            type="button"
                            onClick={(e) => toggleExpand(step.id, e)}
                            className="flex items-center gap-1.5 text-xs font-medium text-indigo-400 hover:text-indigo-300 transition-colors py-1"
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

                          {isExpanded && (
                            <div className="mt-2 pl-3 border-l-2 border-indigo-500/30 space-y-1.5 animate-fadeIn">
                              {step.details.map((detail, dIdx) => (
                                <div
                                  key={dIdx}
                                  className="text-xs text-slate-300 bg-slate-950/50 p-2 rounded border border-slate-800/80 font-mono leading-relaxed"
                                >
                                  {detail}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex-shrink-0 ml-2">{getStatusBadge(step.status)}</div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer system status */}
      <div className="relative z-10 mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Self-Healing JSON Engine: Enabled</span>
        </div>
        <div>
          <span>Cross-Provider Failover Matrix: Active</span>
        </div>
      </div>
    </div>
  );
}
