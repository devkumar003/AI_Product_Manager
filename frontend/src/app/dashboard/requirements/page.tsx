'use client';

import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';
import {
  FileText,
  Layers,
  Users,
  Sparkles,
  Save,
  Clock,
  History,
  RotateCcw,
  CheckCircle,
  AlertCircle,
  Plus,
  ArrowRight,
  RefreshCw,
  Search,
  CheckSquare,
  Award,
  Monitor,
  AppWindow,
  X,
  FileDown
} from 'lucide-react';
import { AgentThoughtVisualizer, ThoughtStep } from '@/components/ui/agent-thought-visualizer';

interface DocItem {
  id: string;
  name: string;
  category: string;
  current_version_number: number;
  filename: string;
  is_editable: boolean;
  updated_at: string;
  versions_list: any[];
}

const INITIAL_STEPS: ThoughtStep[] = [
  { id: '1', agentName: 'Market Research Agent', roleIcon: 'brain', status: 'pending', message: 'Analyzing domain viability...', timestamp: 'Waiting...' },
  { id: '2', agentName: 'Product Discovery Agent', roleIcon: 'layers', status: 'pending', message: 'Structuring value prop...', timestamp: 'Waiting...' },
  { id: '3', agentName: 'Business Analyst Agent', status: 'pending', message: 'Drafting specs...', timestamp: 'Waiting...' },
  { id: '4', agentName: 'UX & Story Agent', status: 'pending', message: 'Decomposing user journeys...', timestamp: 'Waiting...' },
  { id: '5', agentName: 'Executive Review Agent', status: 'pending', message: 'Validating PRD artifact...', timestamp: 'Waiting...' }
];

export default function RequirementsDashboard() {
  const { activeWorkspace } = useAuth();

  const [activeTab, setActiveTab] = React.useState<'prd' | 'catalog' | 'stories'>('prd');

  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const tab = params.get('tab');
      if (tab === 'prd' || tab === 'catalog' || tab === 'stories') {
        setActiveTab(tab);
      }
    }
  }, []);

  const [documents, setDocuments] = React.useState<DocItem[]>([]);
  const [selectedDoc, setSelectedDoc] = React.useState<DocItem | null>(null);
  
  // Editor States
  const [editorContent, setEditorContent] = React.useState('');
  const [originalContent, setOriginalContent] = React.useState('');
  const [isSaving, setIsSaving] = React.useState(false);
  const [saveStatus, setSaveStatus] = React.useState<'idle' | 'draft-saved' | 'published'>('idle');
  
  // Version History States
  const [versions, setVersions] = React.useState<any[]>([]);
  const [previewVersion, setPreviewVersion] = React.useState<number | null>(null);
  const [previewContent, setPreviewContent] = React.useState<string | null>(null);

  // Swarm States
  const [swarmInput, setSwarmInput] = React.useState('');
  const [swarmOpen, setSwarmOpen] = React.useState(false);
  const [swarmLoading, setSwarmLoading] = React.useState(false);
  const [swarmSteps, setSwarmSteps] = React.useState<ThoughtStep[]>(INITIAL_STEPS);
  const [swarmResult, setSwarmResult] = React.useState<any>(null);

  // Requirements Catalog States
  const [reqSearch, setReqSearch] = React.useState('');
  
  // User Stories & Drawer
  const [selectedStory, setSelectedStory] = React.useState<any | null>(null);
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const [drawerTab, setDrawerTab] = React.useState<'criteria' | 'wireframe'>('criteria');
  const [criteriaLoading, setCriteriaLoading] = React.useState(false);
  const [criteriaResult, setCriteriaResult] = React.useState<any>(null);
  const [wireframeLoading, setWireframeLoading] = React.useState(false);
  const [wireframeResult, setWireframeResult] = React.useState<any>(null);

  // Load requirements documents on workspace load
  const loadDocuments = async () => {
    if (!activeWorkspace) return;
    try {
      const docs = await apiService.get<DocItem[]>(`/documents/${activeWorkspace.id}`);
      // Filter for Requirements / PRD or editable docs
      const reqDocs = docs.filter(d => d.category === 'Requirements' || d.category === 'PRD' || d.is_editable);
      setDocuments(reqDocs);
      if (reqDocs.length > 0 && !selectedDoc) {
        setSelectedDoc(reqDocs[0]);
      }
    } catch (e) {
      console.error('Failed to load documents:', e);
    }
  };

  React.useEffect(() => {
    loadDocuments();
  }, [activeWorkspace]);

  // Load selected document content
  React.useEffect(() => {
    if (!activeWorkspace || !selectedDoc) {
      setEditorContent('');
      setOriginalContent('');
      setVersions([]);
      setPreviewVersion(null);
      setPreviewContent(null);
      return;
    }
    const loadContent = async () => {
      try {
        const data = await apiService.get<any>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/content`);
        setEditorContent(data.content || '');
        setOriginalContent(data.content || '');
        
        // Fetch versions
        const vers = await apiService.get<any[]>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/versions`);
        setVersions(vers);
      } catch (e) {
        console.error('Failed to load document content:', e);
      }
    };
    loadContent();
  }, [selectedDoc, activeWorkspace]);

  // Auto-save draft debouncing
  React.useEffect(() => {
    if (!selectedDoc || editorContent === originalContent || !editorContent.trim()) return;

    const timer = setTimeout(async () => {
      try {
        await apiService.put(`/documents/${activeWorkspace?.id}/${selectedDoc.id}/content`, {
          content: editorContent,
          is_draft: true
        });
        setOriginalContent(editorContent);
        setSaveStatus('draft-saved');
        setTimeout(() => setSaveStatus('idle'), 2500);
      } catch (e) {
        console.error('Failed to auto-save draft:', e);
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [editorContent]);

  // Manual save/publish version
  const handlePublish = async () => {
    if (!activeWorkspace || !selectedDoc) return;
    setIsSaving(true);
    try {
      const updated = await apiService.put(`/documents/${activeWorkspace.id}/${selectedDoc.id}/content`, {
        content: editorContent,
        is_draft: false
      });
      setOriginalContent(editorContent);
      setSaveStatus('published');
      // Refresh version list
      const vers = await apiService.get<any[]>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/versions`);
      setVersions(vers);
      setTimeout(() => setSaveStatus('idle'), 2500);
    } catch (e) {
      console.error('Failed to publish version:', e);
    } finally {
      setIsSaving(false);
    }
  };

  // Preview historical version content
  const handlePreviewVersion = async (versionNum: number) => {
    if (!activeWorkspace || !selectedDoc) return;
    setPreviewVersion(versionNum);
    try {
      const data = await apiService.get<any>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/version/${versionNum}/content`);
      setPreviewContent(data.content);
    } catch (e) {
      console.error('Failed to fetch historical version content:', e);
    }
  };

  // Restore historical version
  const handleRestoreVersion = async (versionNum: number) => {
    if (!activeWorkspace || !selectedDoc) return;
    setIsSaving(true);
    try {
      const restored = await apiService.post<any>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/version/${versionNum}/restore`);
      // Update editor text
      const data = await apiService.get<any>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/content`);
      setEditorContent(data.content);
      setOriginalContent(data.content);
      setPreviewVersion(null);
      setPreviewContent(null);
      
      // Update version list
      const vers = await apiService.get<any[]>(`/documents/${activeWorkspace.id}/${selectedDoc.id}/versions`);
      setVersions(vers);
    } catch (e) {
      console.error('Failed to restore version:', e);
    } finally {
      setIsSaving(false);
    }
  };

  // Create Blank Document
  const handleCreateBlankDoc = async () => {
    if (!activeWorkspace) return;
    const name = prompt('Enter document name:', 'Requirements Specification');
    if (!name) return;
    try {
      const formData = new FormData();
      const blob = new Blob(['# Requirements Specification\n\nDescribe the requirements details here...'], { type: 'text/markdown' });
      formData.append('file', blob, `${name.replace(/\s+/g, '_')}.md`);
      formData.append('name', name);
      formData.append('category', 'Requirements');
      formData.append('tags_json', JSON.stringify(['editable']));

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/documents/${activeWorkspace.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      if (res.ok) {
        const newDoc = await res.json();
        await loadDocuments();
        setSelectedDoc(newDoc);
      }
    } catch (e) {
      console.error('Failed to create blank document:', e);
    }
  };

  // Execute Multi-Agent Swarm
  const simulateSwarmProgress = async () => {
    setSwarmSteps(INITIAL_STEPS.map((s, idx) => idx === 0 ? { ...s, status: 'active', timestamp: 'In progress' } : s));
    for (let i = 0; i < INITIAL_STEPS.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 550));
      setSwarmSteps(prev => prev.map((s, idx) => {
        if (idx === i) {
          return {
            ...s,
            status: 'completed',
            timestamp: `${(1.0 + idx * 0.6).toFixed(1)}s`,
            metrics: { latencyMs: Math.round(800 + Math.random() * 400), tokensUsed: Math.round(300 + idx * 200), confidence: 0.95 + idx * 0.01 }
          };
        }
        if (idx === i + 1) {
          return { ...s, status: 'active', timestamp: 'In progress' };
        }
        return s;
      }));
    }
  };

  const handleRunSwarm = async () => {
    if (!activeWorkspace || !swarmInput.trim()) return;
    setSwarmLoading(true);
    setSwarmResult(null);
    const progressPromise = simulateSwarmProgress();

    try {
      const data = await apiService.post<any>('/ai/workflows/execute', {
        workflow_name: 'prd_generation',
        workspace_id: activeWorkspace.id,
        context: { idea: swarmInput },
      });
      const rawResult = data.result || data;
      await progressPromise;
      setSwarmResult(rawResult);
      
      // Save it into documents automatically
      const name = `${activeWorkspace.name} PRD`;
      const prdMarkdown = `# ${name}\n\n## Executive Summary\n${rawResult.prd?.executive_summary || 'Generated by Agent Swarm.'}\n\n## Personas\n${(rawResult.prd?.personas || []).map((p: any) => `### ${p.name || p.segment}\n- Pain Point: ${p.pain_points || p.description}\n`).join('\n')}\n\n## Functional Requirements\n${(rawResult.prd?.functional_requirements || []).map((f: any) => `- **[${f.id || 'FR'}] ${f.title || f.name}** (${f.priority}): ${f.description}`).join('\n')}\n\n## Success Metrics\n${(rawResult.prd?.success_metrics || []).map((m: any) => `- ${m.metric || m.name || m}: ${m.target || '100%'}`).join('\n')}`;
      
      const formData = new FormData();
      const blob = new Blob([prdMarkdown], { type: 'text/markdown' });
      formData.append('file', blob, `${name.replace(/\s+/g, '_')}.md`);
      formData.append('name', name);
      formData.append('category', 'Requirements');
      formData.append('tags_json', JSON.stringify(['editable', 'agent-generated']));

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/documents/${activeWorkspace.id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      if (res.ok) {
        const newDoc = await res.json();
        await loadDocuments();
        setSelectedDoc(newDoc);
        setSwarmOpen(false);
      }
    } catch (e) {
      console.error('Swarm PRD generation failed:', e);
    } finally {
      setSwarmLoading(false);
    }
  };

  // Open Story sliding side drawer
  const handleOpenStoryDrawer = (story: any) => {
    setSelectedStory(story);
    setDrawerOpen(true);
    setCriteriaResult(null);
    setWireframeResult(null);
    setDrawerTab('criteria');
  };

  // Generate GWT Acceptance Criteria
  const handleGenerateCriteria = async () => {
    if (!activeWorkspace || !selectedStory) return;
    setCriteriaLoading(true);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'acceptance_criteria',
        workspace_id: activeWorkspace.id,
        input_data: { user_story: `As a ${selectedStory.asA}, I want to ${selectedStory.iWantTo}, so that ${selectedStory.soThat}` }
      });
      setCriteriaResult(data.result || data);
    } catch (e) {
      console.error(e);
    } finally {
      setCriteriaLoading(false);
    }
  };

  // Generate Wireframe Blueprints
  const handleGenerateWireframe = async () => {
    if (!activeWorkspace || !selectedStory) return;
    setWireframeLoading(true);
    try {
      const data = await apiService.post<any>('/ai/engines/execute', {
        engine_name: 'wireframe_suggestions',
        workspace_id: activeWorkspace.id,
        input_data: { feature_description: selectedStory.iWantTo }
      });
      setWireframeResult(data.result || data);
    } catch (e) {
      console.error(e);
    } finally {
      setWireframeLoading(false);
    }
  };

  // Hardcoded story items if no PRD generated yet for demo/parity
  const demoStories = [
    { id: 'US-1', asA: 'Product Manager', iWantTo: 'view and edit requirements document online', soThat: 'I can collaborate with engineers on live specs.' },
    { id: 'US-2', asA: 'Developer', iWantTo: 'browse story backlog details with criteria', soThat: 'I know exactly what to build and how it looks.' },
    { id: 'US-3', asA: 'QA Lead', iWantTo: 'extract DoD checklists', soThat: 'I can verify requirements compliance systematically.' }
  ];

  const demoRequirements = [
    { id: 'FR-1', title: 'Requirements Version Control', description: 'Store edits in database and track complete version sequence history with recovery option.', priority: 'Must Have' },
    { id: 'FR-2', title: 'Interactive Backlog Drawer', description: 'Expose story detail card drawer containing GWT scenarios and wireframe suggest tabs.', priority: 'Must Have' },
    { id: 'FR-3', title: 'Auto-save debouncing', description: 'Automatically sync and save local changes as drafts to prevent state losses.', priority: 'Should Have' }
  ];

  if (!activeWorkspace) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
          <FileText className="text-zinc-600 animate-pulse" size={48} />
          <h2 className="text-xl font-bold text-white">Select a Workspace</h2>
          <p className="text-zinc-400 text-sm max-w-sm">
            Choose or create a workspace to view your requirements studio and story backlog.
          </p>
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Requirements Dashboard' }]} />
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mt-2">
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
                <FileText className="text-indigo-400" size={28} /> Requirements & PRD Suite
              </h1>
              <p className="text-sm text-zinc-400 mt-1">
                Author specification PRDs, manage version logs, and decompose features into backlog user stories.
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => { setSwarmInput(activeWorkspace.description || ''); setSwarmOpen(true); }}
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl text-xs font-bold uppercase tracking-wider flex items-center gap-2 shadow-lg"
              >
                <Sparkles size={14} /> Execute AI Swarm
              </button>
              <button
                onClick={handleCreateBlankDoc}
                className="px-4 py-2 bg-zinc-900 border border-zinc-800 text-white rounded-xl text-xs font-bold uppercase tracking-wider flex items-center gap-2"
              >
                <Plus size={14} /> New Document
              </button>
            </div>
          </div>
        </div>

        {/* Tab Row */}
        <div className="flex border-b border-zinc-900 pb-px gap-2">
          <button
            onClick={() => setActiveTab('prd')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'prd'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <FileText size={14} /> PRD Studio
          </button>
          <button
            onClick={() => setActiveTab('catalog')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'catalog'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Layers size={14} /> Requirements Catalog
          </button>
          <button
            onClick={() => setActiveTab('stories')}
            className={`px-4 py-2 text-xs font-bold uppercase tracking-wider border-b-2 transition-all flex items-center gap-2 ${
              activeTab === 'stories'
                ? 'border-indigo-500 text-indigo-400'
                : 'border-transparent text-zinc-400 hover:text-zinc-200'
            }`}
          >
            <Users size={14} /> Backlog User Stories
          </button>
        </div>

        {/* Tab Panel contents */}
        <div className="min-h-[450px]">
          {activeTab === 'prd' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Left sidebar: documents list */}
              <div className="lg:col-span-1 p-5 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4">
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-zinc-400">Specifications</h3>
                <div className="space-y-2">
                  {documents.length === 0 ? (
                    <div className="text-center py-8 text-xs text-zinc-500">
                      No requirements docs found. Create one to begin.
                    </div>
                  ) : (
                    documents.map((doc) => (
                      <button
                        key={doc.id}
                        onClick={() => { setSelectedDoc(doc); setPreviewVersion(null); }}
                        className={`w-full text-left p-3 rounded-xl border text-xs transition-all ${
                          selectedDoc?.id === doc.id
                            ? 'border-indigo-500/40 bg-indigo-500/10 text-indigo-300'
                            : 'border-zinc-805 bg-zinc-900/20 text-zinc-400 hover:bg-zinc-900/60'
                        }`}
                      >
                        <div className="font-bold truncate text-white">{doc.name}</div>
                        <div className="text-[10px] text-zinc-550 mt-1">Version v{doc.current_version_number}</div>
                      </button>
                    ))
                  )}
                </div>
              </div>

              {/* Main Panel: Text Editor */}
              <div className="lg:col-span-3 space-y-4">
                {selectedDoc ? (
                  <div className="p-6 bg-zinc-950/40 border border-zinc-900 rounded-2xl space-y-4 relative">
                    {/* Toolbar */}
                    <div className="flex items-center justify-between border-b border-zinc-900 pb-3.5">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h2 className="text-base font-bold text-white">{selectedDoc.name}</h2>
                          {previewVersion && (
                            <span className="px-2 py-0.5 rounded bg-amber-950/50 border border-amber-900 text-[10px] font-bold text-amber-450">
                              PREVIEWING V{previewVersion}
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-zinc-500">
                          Active version: v{selectedDoc.current_version_number}
                        </div>
                      </div>
                      
                      {/* Save Status & Buttons */}
                      <div className="flex items-center gap-3">
                        {saveStatus === 'draft-saved' && (
                          <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                            <CheckCircle size={10} /> Auto-saved draft
                          </span>
                        )}
                        {saveStatus === 'published' && (
                          <span className="text-[10px] text-indigo-400 flex items-center gap-1">
                            <CheckCircle size={10} /> Version published!
                          </span>
                        )}
                        
                        {/* Version selector dropdown */}
                        {versions.length > 0 && (
                          <div className="relative group">
                            <button className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-300 hover:text-white flex items-center gap-1.5">
                              <History size={12} /> Versions
                            </button>
                            <div className="absolute right-0 top-full mt-1.5 w-44 bg-zinc-950 border border-zinc-900 rounded-xl shadow-2xl overflow-hidden hidden group-hover:block z-20">
                              {versions.map((ver) => (
                                <button
                                  key={ver.id}
                                  onClick={() => handlePreviewVersion(ver.version_number)}
                                  className="w-full text-left px-4 py-2 hover:bg-zinc-900 text-[11px] text-zinc-400 hover:text-white border-b border-zinc-900/60 last:border-0 flex justify-between"
                                >
                                  <span>Version {ver.version_number}</span>
                                  <span className="text-[9px] text-zinc-600">v{ver.version_number}</span>
                                </button>
                              ))}
                            </div>
                          </div>
                        )}

                        {previewVersion ? (
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => { setPreviewVersion(null); setPreviewContent(null); }}
                              className="px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-xs text-zinc-400 hover:text-white"
                            >
                              Exit Preview
                            </button>
                            <button
                              onClick={() => handleRestoreVersion(previewVersion)}
                              disabled={isSaving}
                              className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 rounded-lg text-xs font-bold text-white flex items-center gap-1 shadow-lg shadow-amber-600/10"
                            >
                              <RotateCcw size={12} /> Restore
                            </button>
                          </div>
                        ) : (
                          <button
                            onClick={handlePublish}
                            disabled={isSaving || editorContent === originalContent}
                            className="px-4 py-1.5 bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-white rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 shadow-md"
                          >
                            <Save size={12} /> Publish version
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Text Area Editor */}
                    <div className="pt-2">
                      {previewVersion && previewContent !== null ? (
                        <div className="w-full min-h-[350px] bg-zinc-900/40 border border-zinc-800/80 rounded-xl p-4 text-sm text-zinc-400 font-mono overflow-y-auto whitespace-pre-wrap select-none leading-relaxed">
                          {previewContent}
                        </div>
                      ) : (
                        <textarea
                          value={editorContent}
                          onChange={(e) => setEditorContent(e.target.value)}
                          rows={16}
                          placeholder="Write requirements in Markdown format..."
                          className="w-full bg-zinc-900/50 border border-zinc-850 rounded-xl p-4 text-sm text-zinc-200 placeholder-zinc-650 focus:border-indigo-500/40 focus:ring-1 focus:ring-indigo-500/20 outline-none resize-none leading-relaxed font-mono"
                        />
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="p-12 border border-dashed border-zinc-900 bg-zinc-950/20 rounded-2xl text-center space-y-4">
                    <FileText size={48} className="text-zinc-700 mx-auto" />
                    <h3 className="text-sm font-bold text-white">No active specification document</h3>
                    <p className="text-xs text-zinc-550 max-w-sm mx-auto">
                      Generate a detailed spec using the Multi-Agent Swarm or create a blank one to begin editing.
                    </p>
                    <button
                      onClick={handleCreateBlankDoc}
                      className="px-4 py-2 bg-indigo-650 hover:bg-indigo-600 rounded-lg text-xs font-bold text-white"
                    >
                      Create document
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'catalog' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center bg-zinc-950/40 border border-zinc-900 rounded-xl p-4">
                <div className="relative max-w-sm w-full">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                  <input
                    type="text"
                    value={reqSearch}
                    onChange={(e) => setReqSearch(e.target.value)}
                    placeholder="Filter requirements catalog..."
                    className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-indigo-500/40"
                  />
                </div>
                <span className="text-xs text-zinc-500 font-mono">
                  {demoRequirements.length} functional requirements
                </span>
              </div>

              <div className="border border-zinc-900 bg-zinc-950/20 rounded-2xl divide-y divide-zinc-900/60 overflow-hidden">
                {demoRequirements
                  .filter(r => r.title.toLowerCase().includes(reqSearch.toLowerCase()) || r.description.toLowerCase().includes(reqSearch.toLowerCase()))
                  .map((fr) => (
                    <div key={fr.id} className="p-5 flex flex-col sm:flex-row justify-between gap-4 hover:bg-zinc-900/20 transition-all">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] font-mono font-bold bg-indigo-550/10 border border-indigo-500/25 px-2 py-0.5 rounded text-indigo-400">
                            {fr.id}
                          </span>
                          <span className="text-sm font-bold text-white">{fr.title}</span>
                        </div>
                        <p className="text-xs text-zinc-400 leading-relaxed pt-1 max-w-3xl">
                          {fr.description}
                        </p>
                      </div>
                      <span className="px-2.5 py-0.5 rounded bg-indigo-950 border border-indigo-900 text-[10px] font-bold text-indigo-400 self-start">
                        {fr.priority}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {activeTab === 'stories' && (
            <div className="space-y-4">
              <div className="text-xs text-zinc-550 pb-2">
                Click a user story card below to open the details side drawer and generate acceptance criteria or screen blueprints.
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {demoStories.map((story) => (
                  <button
                    key={story.id}
                    onClick={() => handleOpenStoryDrawer(story)}
                    className="p-5 rounded-2xl border border-zinc-900 bg-zinc-950/30 hover:border-indigo-500/40 text-left space-y-3 transition-all hover:shadow-[0_0_15px_rgba(99,102,241,0.05)]"
                  >
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-mono font-bold text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/20">
                        {story.id}
                      </span>
                      <span className="text-[10px] text-zinc-500">As a {story.asA}</span>
                    </div>
                    <p className="text-xs text-zinc-200 font-bold leading-relaxed line-clamp-2">
                      I want to {story.iWantTo}
                    </p>
                    <div className="pt-2 border-t border-zinc-900/60 text-[10px] text-emerald-400 font-mono">
                      So that {story.soThat}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Swarm Modal Dialouge */}
        {swarmOpen && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-zinc-950 border border-zinc-900 w-full max-w-2xl rounded-2xl overflow-hidden shadow-2xl p-6 space-y-6">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="text-indigo-400" size={18} /> Execute 5-Agent PRD Swarm
                </h3>
                <button onClick={() => setSwarmOpen(false)} className="text-zinc-500 hover:text-white">
                  <X size={18} />
                </button>
              </div>

              <div className="space-y-4">
                <label className="text-[11px] font-bold uppercase tracking-wider text-zinc-400">
                  Configure vision inputs (seeded from active workspace context)
                </label>
                <textarea
                  value={swarmInput}
                  onChange={(e) => setSwarmInput(e.target.value)}
                  rows={4}
                  className="w-full bg-zinc-905 border border-zinc-800 rounded-xl p-3 text-xs text-zinc-200 placeholder-zinc-600 focus:outline-none"
                />
              </div>

              {/* Progress Agent thought */}
              {(swarmLoading || swarmSteps.some(s => s.status !== 'pending')) && (
                <div className="max-h-[220px] overflow-y-auto border border-zinc-900 rounded-xl p-3 bg-zinc-950/80">
                  <AgentThoughtVisualizer steps={swarmSteps} isGenerating={swarmLoading} isSimulated={true} />
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">
                <button
                  onClick={() => setSwarmOpen(false)}
                  className="px-4 py-2 border border-zinc-850 hover:bg-zinc-900 text-zinc-300 rounded-lg text-xs font-bold uppercase tracking-wider"
                >
                  Cancel
                </button>
                <button
                  onClick={handleRunSwarm}
                  disabled={swarmLoading || !swarmInput.trim()}
                  className="px-5 py-2 bg-indigo-650 hover:bg-indigo-600 text-white rounded-lg text-xs font-bold uppercase tracking-wider flex items-center gap-1.5"
                >
                  {swarmLoading ? <RefreshCw size={12} className="animate-spin" /> : <Sparkles size={12} />}
                  Run Swarm & Create Spec
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Story Sliding Side Drawer */}
        {drawerOpen && selectedStory && (
          <div className="fixed inset-y-0 right-0 w-full md:w-[480px] bg-zinc-950 border-l border-zinc-900 shadow-2xl p-6 space-y-6 z-55 flex flex-col justify-between overflow-y-auto">
            <div className="space-y-6">
              {/* Drawer Header */}
              <div className="flex justify-between items-start border-b border-zinc-900 pb-4">
                <div className="space-y-1">
                  <span className="text-[10px] font-mono font-bold text-violet-400 bg-violet-500/10 px-2 py-0.5 rounded border border-violet-500/20">
                    {selectedStory.id}
                  </span>
                  <h3 className="text-sm font-bold text-white mt-2">
                    As a {selectedStory.asA}
                  </h3>
                  <p className="text-xs text-zinc-400 leading-relaxed pt-1">
                    I want to {selectedStory.iWantTo}
                  </p>
                </div>
                <button onClick={() => setDrawerOpen(false)} className="text-zinc-500 hover:text-white p-1">
                  <X size={18} />
                </button>
              </div>

              {/* Drawer Tabs */}
              <div className="flex border-b border-zinc-900 pb-px gap-2">
                <button
                  onClick={() => setDrawerTab('criteria')}
                  className={`px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider border-b-2 transition-all flex items-center gap-1.5 ${
                    drawerTab === 'criteria'
                      ? 'border-indigo-500 text-indigo-400'
                      : 'border-transparent text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  <CheckSquare size={12} /> Acceptance Criteria
                </button>
                <button
                  onClick={() => setDrawerTab('wireframe')}
                  className={`px-3 py-1.5 text-[10px] font-extrabold uppercase tracking-wider border-b-2 transition-all flex items-center gap-1.5 ${
                    drawerTab === 'wireframe'
                      ? 'border-indigo-500 text-indigo-400'
                      : 'border-transparent text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  <Monitor size={12} /> Wireframe blueprints
                </button>
              </div>

              {/* Drawer content switcher */}
              <div className="min-h-[250px]">
                {drawerTab === 'criteria' && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] text-zinc-550">GWT Scenarios</span>
                      <button
                        onClick={handleGenerateCriteria}
                        disabled={criteriaLoading}
                        className="px-3 py-1 bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-[10px] font-bold uppercase tracking-wider text-white rounded flex items-center gap-1 transition"
                      >
                        {criteriaLoading ? <RefreshCw size={10} className="animate-spin" /> : <Sparkles size={10} />}
                        Generate
                      </button>
                    </div>

                    {criteriaLoading && (
                      <div className="text-center py-12 text-zinc-650 text-xs animate-pulse">
                        Analyzing user journeys and negative edge scenarios...
                      </div>
                    )}

                    {!criteriaLoading && criteriaResult && (
                      <div className="space-y-4">
                        <div className="space-y-3">
                          {(criteriaResult.criteria || []).map((c: any, idx: number) => (
                            <div key={idx} className="p-4 rounded-xl bg-zinc-900/30 border border-zinc-850 space-y-1.5">
                              <div className="text-xs font-bold text-white">{c.scenario}</div>
                              <div className="text-[11px] text-zinc-400"><span className="text-indigo-400 font-bold uppercase mr-1">Given</span> {c.given}</div>
                              <div className="text-[11px] text-zinc-400"><span className="text-indigo-400 font-bold uppercase mr-1">When</span> {c.when}</div>
                              <div className="text-[11px] text-zinc-400"><span className="text-emerald-400 font-bold uppercase mr-1">Then</span> {c.then}</div>
                            </div>
                          ))}
                        </div>

                        {criteriaResult.edge_cases && (
                          <div className="p-4 rounded-xl bg-zinc-900/20 border border-zinc-900 space-y-2">
                            <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider flex items-center gap-1">
                              <Award size={10} /> Edge Cases
                            </span>
                            <ul className="list-disc list-inside text-[11px] text-zinc-400 space-y-1">
                              {criteriaResult.edge_cases.map((e: any, idx: number) => (
                                <li key={idx}>{e}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}

                    {!criteriaLoading && !criteriaResult && (
                      <div className="text-center py-12 text-[11px] text-zinc-550 border border-dashed border-zinc-900 rounded-xl">
                        Click 'Generate' to query the AI BA Agent.
                      </div>
                    )}
                  </div>
                )}

                {drawerTab === 'wireframe' && (
                  <div className="space-y-4">
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] text-zinc-550 font-mono">UI Recommendation matrix</span>
                      <button
                        onClick={handleGenerateWireframe}
                        disabled={wireframeLoading}
                        className="px-3 py-1 bg-indigo-650 hover:bg-indigo-600 disabled:opacity-50 text-[10px] font-bold uppercase tracking-wider text-white rounded flex items-center gap-1 transition"
                      >
                        {wireframeLoading ? <RefreshCw size={10} className="animate-spin" /> : <Sparkles size={10} />}
                        Generate blueprints
                      </button>
                    </div>

                    {wireframeLoading && (
                      <div className="text-center py-12 text-zinc-650 text-xs animate-pulse">
                        Calculating accessibility and component grids...
                      </div>
                    )}

                    {!wireframeLoading && wireframeResult && (
                      <div className="space-y-4">
                        {(wireframeResult.screens || []).map((screen: any, idx: number) => (
                          <div key={idx} className="p-4 rounded-xl bg-zinc-900/30 border border-zinc-850 space-y-2">
                            <div className="flex justify-between border-b border-zinc-900 pb-1">
                              <span className="text-xs font-bold text-white">{screen.screen_name}</span>
                              <span className="text-[9px] text-zinc-550 uppercase">{screen.purpose}</span>
                            </div>
                            <div className="text-[11px] text-zinc-400">
                              <strong className="text-zinc-300 block mb-0.5">Layout Structure</strong>
                              {screen.layout_structure}
                            </div>
                            <div className="text-[11px] text-zinc-400">
                              <strong className="text-zinc-300 block mb-0.5">Components</strong>
                              {screen.components?.join(', ')}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {!wireframeLoading && !wireframeResult && (
                      <div className="text-center py-12 text-[11px] text-zinc-550 border border-dashed border-zinc-900 rounded-xl">
                        Click 'Generate blueprints' to request wireframe structural guidelines.
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="pt-4 border-t border-zinc-900/60 mt-6 flex justify-end">
              <button
                onClick={() => setDrawerOpen(false)}
                className="px-4 py-2 bg-zinc-900 border border-zinc-850 hover:bg-zinc-800 text-white rounded-lg text-xs font-bold uppercase tracking-wider"
              >
                Close Details
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
