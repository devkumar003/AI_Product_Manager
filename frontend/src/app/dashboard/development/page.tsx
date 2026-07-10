'use client';

import React, { useState, useEffect } from 'react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import { 
  Code2, 
  Play, 
  Terminal, 
  GitBranch, 
  GitCommit, 
  GitPullRequest, 
  Sparkles, 
  Layers, 
  CheckCircle2, 
  RefreshCw, 
  AlertCircle,
  Plus,
  Send,
  Sliders,
  Database,
  Layout,
  FileText,
  FileCode,
  Check,
  UserCheck,
  Flag,
  LineChart,
  Activity,
  History,
  Rocket
} from 'lucide-react';

interface CodePlan {
  id: string;
  title: string;
  description: string;
  steps: string[];
  status: string;
}

interface GitBranchObj {
  id: string;
  branch_name: string;
  source_branch: string;
  status: string;
}

interface GitPRObj {
  id: string;
  title: string;
  description: string;
  source_branch: string;
  target_branch: string;
  status: string;
  merge_recommendation: string;
}

interface ReleasePlan {
  id: string;
  version: string;
  name: string;
  description: string;
  status: string;
}

interface DevAnalytics {
  total_lines_generated: number;
  quality_score_avg: number;
  coverage_rate_avg: number;
  bug_fix_ratio: number;
  commits_count: number;
  pull_requests_count: number;
  active_branches: string[];
}

export default function DevelopmentWorkspacePage() {
  const { activeWorkspace } = useAuth();
  
  // Tab states
  const [activeTab, setActiveTab] = useState<'workspace' | 'git' | 'management' | 'analytics'>('workspace');
  
  // Pipeline form states
  const [pipelineType, setPipelineType] = useState<string>('backend');
  const [targetName, setTargetName] = useState<string>('BillingModule');
  const [promptContent, setPromptContent] = useState<string>('Create standard subscription billing handlers with webhook validations.');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Pipeline output code state
  const [generatedFilePath, setGeneratedFilePath] = useState<string>('backend/app/controllers/billing.py');
  const [generatedCode, setGeneratedCode] = useState<string>(
    "# AI ProductOS Autonomous Code Generation Sandbox\n" +
    "# Select a pipeline and click 'Trigger Autonomous Generation Pipeline' to execute."
  );
  
  // Mock console log outputs
  const [consoleLogs, setConsoleLogs] = useState<string[]>(['Workspace IDE Sandbox initialized... Ready.']);
  
  // Code Plans
  const [plans, setPlans] = useState<CodePlan[]>([]);
  const [newPlanTitle, setNewPlanTitle] = useState<string>('');
  const [newPlanDesc, setNewPlanDesc] = useState<string>('');

  // Git states
  const [branches, setBranches] = useState<GitBranchObj[]>([]);
  const [prs, setPrs] = useState<GitPRObj[]>([]);
  const [activeBranch, setActiveBranch] = useState<string>('main');
  const [activeBranchId, setActiveBranchId] = useState<string>('');
  const [newBranchName, setNewBranchName] = useState<string>('feature/billing-hooks');
  const [commitMsg, setCommitMsg] = useState<string>('feat: implement stripe customer subscriptions webhook');
  const [prTitle, setPrTitle] = useState<string>('Integrate stripe customer billing');
  const [prDesc, setPrDesc] = useState<string>('Handles charge.succeeded payloads.');

  // Release/Sprint states
  const [releases, setReleases] = useState<ReleasePlan[]>([]);
  const [newVersion, setNewVersion] = useState<string>('v1.3.0');
  const [newReleaseName, setNewReleaseName] = useState<string>('Payments Launch');
  const [newReleaseDesc, setNewReleaseDesc] = useState<string>('Includes full subscription billing options.');
  
  const [sprintName, setSprintName] = useState<string>('Sprint 5 - Billing Integrations');
  const [sprintSummary, setSprintSummary] = useState<string>('Completed basic controller routes, initializing UI integrations.');
  const [sprintStatus, setSprintStatus] = useState<string>('');

  // Dev Analytics state
  const [analytics, setAnalytics] = useState<DevAnalytics | null>(null);

  // Load all initial dev status
  const loadWorkspaceData = async () => {
    if (!activeWorkspace) return;
    try {
      // 1. Fetch plans
      const plansList = await apiService.get<CodePlan[]>(`/development/plans?workspace_id=${activeWorkspace.id}`);
      setPlans(plansList);

      // 2. Fetch Analytics
      const analyticsData = await apiService.get<DevAnalytics>(`/development/analytics?workspace_id=${activeWorkspace.id}`);
      setAnalytics(analyticsData);
      if (analyticsData.active_branches && analyticsData.active_branches.length > 0) {
        setActiveBranch(analyticsData.active_branches[0]);
      }
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadWorkspaceData();
  }, [activeWorkspace]);

  // Trigger generator pipelines
  const handleTriggerPipeline = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) return;
    setIsLoading(true);
    setErrorMsg(null);
    setConsoleLogs(prev => [...prev, `[PIPELINE] Launching autonomous ${pipelineType} generator pipeline for ${targetName}...`]);
    try {
      const res = await apiService.post<any>(
        `/development/pipelines/execute?workspace_id=${activeWorkspace.id}&pipeline_type=${pipelineType}`,
        {
          target_name: targetName,
          prompt: promptContent,
          options: {
            code_content: generatedCode,
            requirements: promptContent
          }
        }
      );
      if (res.success) {
        const fileData = res.outputs;
        if (fileData.file_path) setGeneratedFilePath(fileData.file_path);
        if (fileData.content) setGeneratedCode(fileData.content);
        setConsoleLogs(prev => [
          ...prev, 
          `[SUCCESS] Generated ${fileData.file_path || 'plan'} successfully!`,
          `[STATS] lines generated: ${fileData.content ? fileData.content.split('\n').length : 0}`
        ]);
        loadWorkspaceData();
      } else {
        setErrorMsg(res.message);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Error occurred during pipeline execution.');
    } finally {
      setIsLoading(false);
    }
  };

  // Run Sandbox IDE actions
  const runIDEAction = async (action: 'lint' | 'format' | 'test') => {
    if (!activeWorkspace) return;
    setConsoleLogs(prev => [...prev, `[IDE] Running ${action} checking on ${generatedFilePath}...`]);
    try {
      const res = await apiService.post<any>(
        `/development/workspace/action?workspace_id=${activeWorkspace.id}&file_path=${generatedFilePath}&action=${action}`
      );
      if (res.success) {
        setConsoleLogs(prev => [
          ...prev, 
          `[${action.toUpperCase()} OUT] ${res.message}`,
          ...(res.findings ? res.findings.map((f: string) => `  - ${f}`) : []),
          res.changes ? `  - ${res.changes}` : '',
          res.outcome ? `  - Outcome: ${res.outcome} | Passed: ${res.stats?.passed}` : ''
        ].filter(Boolean));
      }
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Create Code Plan
  const handleCreatePlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !newPlanTitle || !newPlanDesc) return;
    try {
      await apiService.post(
        `/development/plans?workspace_id=${activeWorkspace.id}&title=${encodeURIComponent(newPlanTitle)}&description=${encodeURIComponent(newPlanDesc)}&requirements=${encodeURIComponent(newPlanDesc)}`
      );
      setNewPlanTitle('');
      setNewPlanDesc('');
      loadWorkspaceData();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Create Git Branch
  const handleCreateBranch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !newBranchName) return;
    try {
      const res = await apiService.post<GitBranchObj>(
        `/development/git/branch?workspace_id=${activeWorkspace.id}`,
        {
          branch_name: newBranchName,
          source_branch: activeBranch
        }
      );
      setBranches(prev => [...prev, res]);
      setActiveBranch(res.branch_name);
      setActiveBranchId(res.id);
      setConsoleLogs(prev => [...prev, `[GIT] Checked out to new branch: ${res.branch_name}`]);
      setNewBranchName('');
      loadWorkspaceData();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Simulate Git Commit
  const handleCommit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !commitMsg || !activeBranchId) {
      setErrorMsg('Ensure you have created and checked out a custom branch first.');
      return;
    }
    try {
      const res = await apiService.post<any>(
        `/development/git/commit?workspace_id=${activeWorkspace.id}`,
        {
          branch_id: activeBranchId,
          commit_message: commitMsg,
          files_changed: [generatedFilePath]
        }
      );
      setConsoleLogs(prev => [...prev, `[GIT] Committed changes. Hash: ${res.commit_hash.slice(0, 7)}`]);
      setCommitMsg('');
      loadWorkspaceData();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Create PR
  const handleCreatePR = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !prTitle) return;
    try {
      const res = await apiService.post<GitPRObj>(
        `/development/git/pr?workspace_id=${activeWorkspace.id}`,
        {
          title: prTitle,
          description: prDesc,
          source_branch: activeBranch,
          target_branch: 'main'
        }
      );
      setPrs(prev => [...prev, res]);
      setConsoleLogs(prev => [
        ...prev, 
        `[GIT] Pull Request #${prs.length + 1} generated! Merge recommendation: ${res.merge_recommendation}`
      ]);
      setPrTitle('');
      setPrDesc('');
      loadWorkspaceData();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Merge PR
  const handleMergePR = async (prId: string) => {
    if (!activeWorkspace) return;
    try {
      const res = await apiService.post<any>(
        `/development/git/pr/${prId}/merge?workspace_id=${activeWorkspace.id}`
      );
      setPrs(prev => prev.map(p => p.id === prId ? { ...p, status: 'Merged' } : p));
      setConsoleLogs(prev => [...prev, `[GIT] Successfully merged PR into main branch.`]);
      setActiveBranch('main');
      loadWorkspaceData();
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Create Release plan
  const handleCreateRelease = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !newVersion || !newReleaseName) return;
    try {
      const res = await apiService.post<ReleasePlan>(
        `/development/releases?workspace_id=${activeWorkspace.id}`,
        {
          version: newVersion,
          name: newReleaseName,
          description: newReleaseDesc,
          scope: []
        }
      );
      setReleases(prev => [...prev, res]);
      setNewVersion('');
      setNewReleaseName('');
      setNewReleaseDesc('');
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  // Create Sprint update
  const handleSprintUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace || !sprintName || !sprintSummary) return;
    try {
      await apiService.post(
        `/development/sprints/update?workspace_id=${activeWorkspace.id}`,
        {
          sprint_name: sprintName,
          progress_summary: sprintSummary
        }
      );
      setSprintStatus(`Successfully published update for ${sprintName}!`);
      setTimeout(() => setSprintStatus(''), 4000);
    } catch (err: any) {
      setErrorMsg(err.message);
    }
  };

  return (
    <AppShell>
      <div className="p-6 text-zinc-100 bg-zinc-950 min-h-screen">
        <Breadcrumb items={[{ label: 'Dashboard', href: '/dashboard' }, { label: 'Development Workspace' }]} />
        
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between border-b border-zinc-900 pb-5 mt-4 mb-6">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-medium text-xs tracking-wider uppercase mb-1">
              <Code2 size={14} />
              <span>Automated Programming Environment</span>
            </div>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center">
              AI Development Workspace
              <span className="ml-3 rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-400 border border-emerald-500/20">
                Sandbox Mode
              </span>
            </h1>
            <p className="text-zinc-500 text-sm mt-1">
              Generate features, test suites, database schema migrations, and review code quality inside the workspace.
            </p>
          </div>
          
          <button
            onClick={loadWorkspaceData}
            className="mt-4 md:mt-0 flex items-center space-x-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-700 px-4 py-2 text-xs font-medium text-zinc-300 transition duration-200"
          >
            <RefreshCw size={12} />
            <span>Sync Workspace State</span>
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
        <div className="flex border-b border-zinc-900 space-x-6 mb-6 overflow-x-auto pb-px">
          {[
            { key: 'workspace', label: 'AI Code Workspace', icon: Code2 },
            { key: 'git', label: 'Simulated Git Flow', icon: GitBranch },
            { key: 'management', label: 'Sprint & Release Plans', icon: Rocket },
            { key: 'analytics', label: 'Development KPIs', icon: LineChart },
          ].map(tab => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => {
                  setActiveTab(tab.key as any);
                  setErrorMsg(null);
                }}
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

        {/* Tab 1: AI Code Workspace */}
        {activeTab === 'workspace' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Form Panel */}
            <div className="lg:col-span-1 space-y-6">
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-4 flex items-center">
                  <Sliders size={16} className="text-indigo-400 mr-2" />
                  Configure Code Generator
                </h2>
                <form onSubmit={handleTriggerPipeline} className="space-y-4">
                  <div>
                    <label className="text-xs text-zinc-400 block mb-1">Pipeline Action</label>
                    <select
                      value={pipelineType}
                      onChange={e => setPipelineType(e.target.value)}
                      className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-indigo-500"
                    >
                      <option value="prd">Product Requirement Doc (PRD)</option>
                      <option value="requirement">Requirement Analysis Doc</option>
                      <option value="architecture">Architecture Design Doc</option>
                      <option value="database">Database SQL Schema DDL</option>
                      <option value="backend">FastAPI Backend Code</option>
                      <option value="frontend">Next.js React Frontend View</option>
                      <option value="api">OpenAPI Yaml Specs</option>
                      <option value="unittest">Generate Pytest Unit Tests</option>
                      <option value="integrationtest">Generate Integration Tests</option>
                      <option value="documentation">Write Technical Markdown Docs</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-xs text-zinc-400 block mb-1">Target Name</label>
                    <input
                      type="text"
                      value={targetName}
                      onChange={e => setTargetName(e.target.value)}
                      className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-indigo-500"
                      placeholder="e.g. StripeWebhookHandler"
                      required
                    />
                  </div>

                  <div>
                    <label className="text-xs text-zinc-400 block mb-1">Prompt / Context Instructions</label>
                    <textarea
                      value={promptContent}
                      onChange={e => setPromptContent(e.target.value)}
                      rows={4}
                      className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-2 px-3 text-xs text-white outline-none focus:border-indigo-500 resize-none"
                      placeholder="What should the AI developer agent build? Provide files context, endpoints logic, or styling specifications."
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full flex items-center justify-center space-x-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold text-xs py-2.5 transition duration-200"
                  >
                    <Sparkles size={14} />
                    <span>{isLoading ? 'Processing Pipeline...' : 'Run Autonomous Generator'}</span>
                  </button>
                </form>
              </div>

              {/* Development Code Plans */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <FileText size={16} className="text-indigo-400 mr-2" />
                  Technical Roadmaps & Plans
                </h2>
                <p className="text-[10px] text-zinc-500 mb-4">
                  Create code planning specifications which outline coding steps before programming.
                </p>

                <form onSubmit={handleCreatePlan} className="space-y-3 mb-4">
                  <input
                    type="text"
                    placeholder="Plan Title"
                    value={newPlanTitle}
                    onChange={e => setNewPlanTitle(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                    required
                  />
                  <input
                    type="text"
                    placeholder="Brief description / scope target"
                    value={newPlanDesc}
                    onChange={e => setNewPlanDesc(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                    required
                  />
                  <button
                    type="submit"
                    className="w-full rounded bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-1 text-[11px] font-semibold text-zinc-300 transition duration-150"
                  >
                    Generate Steps
                  </button>
                </form>

                <div className="space-y-3 max-h-56 overflow-y-auto pr-1">
                  {plans.map(p => (
                    <div key={p.id} className="bg-zinc-900/40 border border-zinc-900 p-3 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div className="font-bold text-xs text-white">{p.title}</div>
                        <span className="text-[9px] bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-1.5 py-0.5 rounded-full">
                          {p.status}
                        </span>
                      </div>
                      <div className="text-[10px] text-zinc-500 mt-1">{p.description}</div>
                      {p.steps.length > 0 && (
                        <div className="mt-2 space-y-1 pl-2 border-l border-zinc-800">
                          {p.steps.slice(0, 3).map((st, idx) => (
                            <div key={idx} className="text-[9px] text-zinc-400 truncate">
                              {idx + 1}. {st}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Sandbox IDE Panel */}
            <div className="lg:col-span-2 space-y-6">
              {/* Code editor view */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 overflow-hidden flex flex-col h-[520px]">
                <div className="bg-zinc-900/80 px-4 py-2 border-b border-zinc-900 flex justify-between items-center">
                  <div className="flex items-center space-x-2">
                    <FileCode size={14} className="text-yellow-500" />
                    <span className="font-mono text-xs text-zinc-300 font-semibold">{generatedFilePath}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => runIDEAction('lint')}
                      className="px-2.5 py-1 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 rounded text-[10px] text-zinc-400 hover:text-white transition duration-150"
                    >
                      Lint Code
                    </button>
                    <button
                      onClick={() => runIDEAction('format')}
                      className="px-2.5 py-1 bg-zinc-950 border border-zinc-800 hover:border-zinc-700 rounded text-[10px] text-zinc-400 hover:text-white transition duration-150"
                    >
                      Format Code
                    </button>
                    <button
                      onClick={() => runIDEAction('test')}
                      className="px-2.5 py-1 bg-indigo-600/20 border border-indigo-500/30 hover:bg-indigo-600/30 text-indigo-400 rounded text-[10px] font-semibold transition duration-150 flex items-center space-x-1"
                    >
                      <Play size={8} /> <span>Simulate Tests</span>
                    </button>
                  </div>
                </div>

                <div className="flex-1 p-4 bg-zinc-950 font-mono text-xs overflow-auto text-zinc-300">
                  <pre className="whitespace-pre-wrap">{generatedCode}</pre>
                </div>
              </div>

              {/* Terminal Logs Panel */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 overflow-hidden">
                <div className="bg-zinc-900/60 px-4 py-2 border-b border-zinc-900 flex items-center space-x-2">
                  <Terminal size={14} className="text-indigo-400" />
                  <span className="text-xs font-bold text-zinc-400">Sandbox Console Output</span>
                </div>
                <div className="p-4 bg-zinc-950/80 font-mono text-[10px] h-32 overflow-y-auto space-y-1 text-zinc-400">
                  {consoleLogs.map((log, index) => (
                    <div key={index} className="leading-relaxed">
                      <span className="text-zinc-600 mr-2">[{new Date().toLocaleTimeString()}]</span>
                      <span>{log}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Simulated Git Flow */}
        {activeTab === 'git' && (
          <div className="max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Branches & Commits */}
            <div className="space-y-6">
              {/* Branch Setup */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <GitBranch size={16} className="text-indigo-400 mr-2" />
                  Simulate Git Branches
                </h2>
                <div className="text-xs text-zinc-400 mb-4 flex items-center">
                  Active Branch: 
                  <span className="ml-2 bg-indigo-500/10 border border-indigo-500/25 text-indigo-400 px-2 py-0.5 rounded font-mono text-[10px]">
                    {activeBranch}
                  </span>
                </div>

                <form onSubmit={handleCreateBranch} className="flex space-x-2">
                  <input
                    type="text"
                    placeholder="New branch name (e.g. feature/stripe)"
                    value={newBranchName}
                    onChange={e => setNewBranchName(e.target.value)}
                    className="flex-1 rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                    required
                  />
                  <button
                    type="submit"
                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold px-3 py-1.5 rounded-lg transition duration-150"
                  >
                    Branch
                  </button>
                </form>
              </div>

              {/* Commit changes */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <GitCommit size={16} className="text-indigo-400 mr-2" />
                  Commit Sandbox File changes
                </h2>
                <p className="text-[10px] text-zinc-500 mb-4">
                  Saves the current code sandbox file changes to the local branch.
                </p>

                <form onSubmit={handleCommit} className="space-y-3">
                  <div>
                    <label className="text-[10px] text-zinc-500 block mb-1">Target File to Commit</label>
                    <input
                      type="text"
                      value={generatedFilePath}
                      disabled
                      className="w-full rounded-lg border border-zinc-900 bg-zinc-950/50 py-1.5 px-3 text-xs text-zinc-400 font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] text-zinc-500 block mb-1">Commit Message</label>
                    <input
                      type="text"
                      placeholder="Commit message details"
                      value={commitMsg}
                      onChange={e => setCommitMsg(e.target.value)}
                      className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                      required
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-2 rounded-lg text-xs font-semibold text-zinc-300 transition duration-150"
                  >
                    Commit Changes
                  </button>
                </form>
              </div>
            </div>

            {/* Pull Requests & Merges */}
            <div className="space-y-6">
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <GitPullRequest size={16} className="text-indigo-400 mr-2" />
                  Generate Pull Request
                </h2>
                <p className="text-[10px] text-zinc-500 mb-4">
                  Submits active commits to a PR, running automated conflict & merge safety analysis.
                </p>

                <form onSubmit={handleCreatePR} className="space-y-3">
                  <input
                    type="text"
                    placeholder="PR Title"
                    value={prTitle}
                    onChange={e => setPrTitle(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                    required
                  />
                  <textarea
                    placeholder="Describe implementation details"
                    value={prDesc}
                    onChange={e => setPrDesc(e.target.value)}
                    rows={2}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500 resize-none"
                  />
                  <button
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-500 py-2 rounded-lg text-xs font-semibold text-white transition duration-150"
                  >
                    Submit Pull Request
                  </button>
                </form>
              </div>

              {/* Active PRs List */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Active Pull Requests</h3>
                {prs.length === 0 ? (
                  <div className="rounded-xl border border-dashed border-zinc-900 p-8 text-center text-zinc-655 text-xs">
                    No active pull requests open.
                  </div>
                ) : (
                  prs.map(pr => (
                    <div key={pr.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-bold text-sm text-white">{pr.title}</h4>
                          <code className="text-[10px] text-zinc-500 block mt-0.5">
                            {pr.source_branch} &rarr; {pr.target_branch}
                          </code>
                        </div>
                        <span className={`text-[9px] px-2 py-0.5 rounded-full border font-bold ${
                          pr.status === 'Merged'
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                            : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20'
                        }`}>
                          {pr.status}
                        </span>
                      </div>
                      
                      {pr.status === 'Open' && (
                        <div className="mt-4 pt-3 border-t border-zinc-900/60 flex items-center justify-between">
                          <span className={`text-[10px] flex items-center ${
                            pr.merge_recommendation === 'Ready' 
                              ? 'text-emerald-400' 
                              : pr.merge_recommendation === 'Conflicts'
                              ? 'text-red-400'
                              : 'text-amber-400'
                          }`}>
                            <CheckCircle2 size={10} className="mr-1" />
                            Merge safety: {pr.merge_recommendation}
                          </span>
                          
                          <button
                            onClick={() => handleMergePR(pr.id)}
                            className="bg-emerald-600 hover:bg-emerald-500 text-white text-[10px] font-bold px-2.5 py-1 rounded transition duration-150"
                          >
                            Merge Pull Request
                          </button>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Sprint & Release Plans */}
        {activeTab === 'management' && (
          <div className="max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Release Plans */}
            <div className="space-y-6">
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <Flag size={16} className="text-indigo-400 mr-2" />
                  Release Planning Engine
                </h2>
                <p className="text-[10px] text-zinc-500 mb-4">
                  Schedule deployment versions, outline changelogs, and prepare cloud deployment compose scripts.
                </p>

                <form onSubmit={handleCreateRelease} className="space-y-3">
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="text"
                      placeholder="v1.0.0"
                      value={newVersion}
                      onChange={e => setNewVersion(e.target.value)}
                      className="rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500 col-span-1"
                      required
                    />
                    <input
                      type="text"
                      placeholder="Release Name"
                      value={newReleaseName}
                      onChange={e => setNewReleaseName(e.target.value)}
                      className="rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500 col-span-2"
                      required
                    />
                  </div>
                  <input
                    type="text"
                    placeholder="Changelog details summary"
                    value={newReleaseDesc}
                    onChange={e => setNewReleaseDesc(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                  />
                  <button
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-500 py-2 rounded-lg text-xs font-semibold text-white transition duration-150"
                  >
                    Draft Release Plan
                  </button>
                </form>
              </div>

              {/* Active Release list */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Scheduled Release Tracks</h3>
                {releases.length === 0 ? (
                  <div className="rounded-xl bg-zinc-900/30 border border-zinc-900 p-4 text-xs text-zinc-500">
                    No release versions drafted yet.
                  </div>
                ) : (
                  releases.map(rel => (
                    <div key={rel.id} className="rounded-xl border border-zinc-900 bg-zinc-950 p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="text-xs bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded font-mono font-bold mr-2">
                            {rel.version}
                          </span>
                          <span className="font-bold text-sm text-white">{rel.name}</span>
                        </div>
                        <span className="text-[10px] text-zinc-500">{rel.status}</span>
                      </div>
                      <p className="text-[10px] text-zinc-400 mt-2">{rel.description}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Sprints & Assignments */}
            <div className="space-y-6">
              {/* Sprint Updates */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <Activity size={16} className="text-indigo-400 mr-2" />
                  Sprint Update Engine
                </h2>
                <p className="text-[10px] text-zinc-500 mb-4">
                  Log active sprint progress, compile burn-down velocity logs, and resolve blockers.
                </p>

                <form onSubmit={handleSprintUpdate} className="space-y-3">
                  <input
                    type="text"
                    value={sprintName}
                    onChange={e => setSprintName(e.target.value)}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500"
                    placeholder="Sprint Name"
                    required
                  />
                  <textarea
                    value={sprintSummary}
                    onChange={e => setSprintSummary(e.target.value)}
                    rows={2}
                    className="w-full rounded-lg border border-zinc-800 bg-zinc-900 py-1.5 px-3 text-xs text-white outline-none focus:border-indigo-500 resize-none"
                    placeholder="Sprint progress summary..."
                    required
                  />
                  <button
                    type="submit"
                    className="w-full bg-zinc-900 border border-zinc-800 hover:border-zinc-700 py-2 rounded-lg text-xs font-semibold text-zinc-300 transition duration-150"
                  >
                    Publish Sprint Status
                  </button>
                </form>

                {sprintStatus && (
                  <div className="mt-3 text-[10px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 p-2 rounded-lg">
                    {sprintStatus}
                  </div>
                )}
              </div>

              {/* Developer Assignments */}
              <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
                <h2 className="text-md font-bold text-white mb-2 flex items-center">
                  <UserCheck size={16} className="text-indigo-400 mr-2" />
                  Task Assignment Matrix
                </h2>
                <div className="space-y-3">
                  {[
                    { dev: 'AI Architect Agent', role: 'System Spec Design', hours: 12 },
                    { dev: 'AI Backend Agent', role: 'Database DDL & API routes', hours: 24 },
                    { dev: 'AI Frontend Agent', role: 'Responsive TSX Component', hours: 20 },
                  ].map((assign, idx) => (
                    <div key={idx} className="flex justify-between items-center bg-zinc-900/30 p-2.5 rounded-lg border border-zinc-900">
                      <div>
                        <div className="text-xs font-bold text-white">{assign.dev}</div>
                        <div className="text-[9px] text-zinc-500">{assign.role}</div>
                      </div>
                      <span className="text-[10px] font-mono text-indigo-400 bg-indigo-500/5 px-2 py-0.5 rounded border border-indigo-500/10">
                        {assign.hours} hours
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Development KPIs */}
        {activeTab === 'analytics' && (
          <div className="max-w-4xl space-y-6">
            <h2 className="text-lg font-bold text-white flex items-center">
              <LineChart size={18} className="text-indigo-400 mr-2" />
              Autonomous Programming Analytics
            </h2>

            {/* Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Lines Code Generated', value: analytics?.total_lines_generated || 0, change: '100% Correct Diffs', icon: FileCode },
                { label: 'Average Quality Rating', value: `${analytics?.quality_score_avg.toFixed(1) || '0.0'}/100`, change: 'Security approved', icon: CheckCircle2 },
                { label: 'Estimated Test Coverage', value: `${analytics?.coverage_rate_avg.toFixed(1) || '0.0'}%`, change: 'Pytest suite standard', icon: Play },
                { label: 'Commits Count', value: analytics?.commits_count || 0, change: 'Push trigger integration', icon: GitCommit },
              ].map((card, idx) => {
                const Icon = card.icon;
                return (
                  <div key={idx} className="rounded-xl border border-zinc-900 bg-zinc-950 p-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">{card.label}</span>
                      <Icon size={14} className="text-indigo-400" />
                    </div>
                    <div className="text-xl font-bold text-white tracking-tight">{card.value}</div>
                    <span className="text-[8px] text-zinc-650 font-bold block mt-1">{card.change}</span>
                  </div>
                );
              })}
            </div>

            {/* Execution logs overview */}
            <div className="rounded-xl border border-zinc-900 bg-zinc-950 p-5">
              <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-3">Workspace Activity Trail</h3>
              <div className="space-y-3 max-h-[300px] overflow-y-auto">
                {[
                  { event: 'Autonomous Code Execution completed', user: 'AI Developer Agent', time: '10 mins ago', desc: 'Wrote frontend view components' },
                  { event: 'Commit created: Stripe Billing', user: 'AI Developer Agent', time: '40 mins ago', desc: 'Saved billing routes' },
                  { event: 'Linter run complete', user: 'Workspace IDE Sandbox', time: '2 hours ago', desc: 'Valid formatting check' },
                ].map((act, idx) => (
                  <div key={idx} className="flex justify-between items-start p-3 bg-zinc-900/20 border border-zinc-900 rounded-lg">
                    <div>
                      <div className="text-xs font-semibold text-white">{act.event}</div>
                      <div className="text-[10px] text-zinc-500 mt-0.5">{act.desc}</div>
                    </div>
                    <div className="text-right">
                      <span className="text-[9px] text-zinc-550 block">{act.time}</span>
                      <span className="text-[8px] bg-zinc-800 text-zinc-400 px-1 py-0.5 rounded font-bold mt-1 inline-block">
                        {act.user}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
