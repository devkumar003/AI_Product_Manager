'use client';

import * as React from 'react';
import { Plus, Search, Calendar, FileText, Download, Tag, AlertCircle, RefreshCw, Layers } from 'lucide-react';

import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Dialog } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/context/AuthContext';
import { api, apiService, API_URL } from '@/lib/api';

interface DocItem {
  id: string;
  name: string;
  filename: string;
  mime_type: string;
  file_size: number;
  current_version_number: number;
  category: string;
  tags: string[];
  status: string;
  project_id?: string | null;
  created_at: string;
  updated_at: string;
}

interface ProjectItem {
  id: string;
  name: string;
}

export default function DocumentsPage() {
  const { activeWorkspace } = useAuth();
  const [search, setSearch] = React.useState('');
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [docs, setDocs] = React.useState<DocItem[]>([]);
  const [projects, setProjects] = React.useState<ProjectItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [apiError, setApiError] = React.useState('');

  // Form states
  const [newName, setNewName] = React.useState('');
  const [newProject, setNewProject] = React.useState('');
  const [newCategory, setNewCategory] = React.useState('General');
  const [newTagsStr, setNewTagsStr] = React.useState('');
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [errorName, setErrorName] = React.useState('');

  const fetchDocs = React.useCallback(async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    setApiError('');
    try {
      const docsData = await apiService.get<DocItem[]>(`/documents/${activeWorkspace.id}`);
      setDocs(docsData);
      
      const projectsData = await apiService.get<ProjectItem[]>(`/projects/${activeWorkspace.id}`);
      setProjects(projectsData);
    } catch (err: any) {
      setApiError(err.message || 'Failed to fetch specifications.');
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspace]);

  React.useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      if (!newName) {
        // Pre-fill name from file name
        const baseName = e.target.files[0].name.replace(/\.[^/.]+$/, "");
        setNewName(baseName);
      }
    }
  };

  const handleCreateDoc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) return;
    if (!newName.trim()) {
      setErrorName('Document title is required');
      return;
    }
    if (!selectedFile) {
      setErrorName('Please select a file to upload');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('name', newName);
      if (newProject) {
        formData.append('project_id', newProject);
      }
      formData.append('category', newCategory);
      
      // Parse tags
      const tagsList = newTagsStr.split(',').map(t => t.trim()).filter(Boolean);
      formData.append('tags_json', JSON.stringify(tagsList));

      const newDoc = await api.post<DocItem>(`/documents/${activeWorkspace.id}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setDocs([newDoc.data, ...docs]);
      setIsModalOpen(false);
      setNewName('');
      setNewProject('');
      setNewCategory('General');
      setNewTagsStr('');
      setSelectedFile(null);
      setErrorName('');
    } catch (err: any) {
      setErrorName(err.message || 'Upload failed.');
    }
  };

  const handleDownload = (doc: DocItem) => {
    if (!activeWorkspace) return;
    // Direct link to streaming download endpoint
    const token = localStorage.getItem('auth_token');
    const downloadUrl = `${API_URL}/documents/${activeWorkspace.id}/${doc.id}/download?token=${token}`;
    window.open(downloadUrl, '_blank');
  };

  const filteredDocs = docs.filter((d) =>
    d.name.toLowerCase().includes(search.toLowerCase()) ||
    d.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Documents' }]} />
            <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">
              Specification Documents
            </h1>
          </div>
          <Button variant="primary" onClick={() => setIsModalOpen(true)} disabled={!activeWorkspace}>
            <Plus size={16} className="mr-2" /> New Document
          </Button>
        </div>

        {/* Workspace check alert */}
        {!activeWorkspace && (
          <div className="flex items-center space-x-3 p-4 bg-amber-950/20 border border-amber-900/50 rounded-xl text-amber-400 text-sm">
            <AlertCircle size={18} />
            <span>Please switch to an active workspace to manage specification documents.</span>
          </div>
        )}

        {activeWorkspace && (
          <>
            {/* Toolbar */}
            <div className="flex items-center space-x-2 bg-zinc-950 p-1 border border-zinc-900 rounded-lg max-w-md">
              <div className="pl-3 text-zinc-500">
                <Search size={16} />
              </div>
              <input
                type="text"
                placeholder="Search documents..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="flex-1 bg-transparent px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none"
              />
            </div>

            {/* Error notifications */}
            {apiError && (
              <div className="p-3 bg-red-950/20 border border-red-900/50 rounded-lg text-red-400 text-xs flex items-center">
                <AlertCircle size={14} className="mr-2" />
                {apiError}
              </div>
            )}

            {/* Documents Grid / Empty State */}
            {isLoading ? (
              <div className="flex items-center justify-center py-20 text-zinc-400 space-x-2">
                <RefreshCw size={20} className="animate-spin" />
                <span>Downloading document lists...</span>
              </div>
            ) : filteredDocs.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredDocs.map((doc) => (
                  <Card key={doc.id} className="hover:border-zinc-800 hover:bg-zinc-950/60 transition duration-300 flex flex-col justify-between group">
                    <CardHeader className="pb-4">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] bg-zinc-900 border border-zinc-800 rounded-full px-2.5 py-0.5 font-bold uppercase tracking-wider text-zinc-400">
                          {doc.category}
                        </span>
                        <div className="flex items-center text-[10px] text-zinc-500 font-medium">
                          <Layers size={10} className="mr-1" /> V{doc.current_version_number}
                        </div>
                      </div>
                      <CardTitle className="text-base font-bold mt-2 text-white group-hover:text-indigo-400 transition">
                        {doc.name}
                      </CardTitle>
                      <CardDescription className="text-zinc-500 text-xs mt-1">
                        Size: {(doc.file_size / 1024).toFixed(1)} KB • {new Date(doc.updated_at).toLocaleDateString()}
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="pt-0 pb-4">
                      <div className="flex flex-wrap gap-1.5 mt-2">
                        {doc.tags && doc.tags.map((tag, idx) => (
                          <span key={idx} className="flex items-center text-[9px] bg-zinc-900 text-zinc-400 px-2 py-0.5 rounded border border-zinc-850">
                            <Tag size={8} className="mr-1" /> {tag}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                    <div className="border-t border-zinc-900 p-3 flex justify-end bg-zinc-950/30 rounded-b-xl">
                      <Button variant="outline" size="sm" onClick={() => handleDownload(doc)}>
                        <Download size={12} className="mr-1.5" /> Download
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="py-20 text-center text-zinc-500 bg-zinc-950/30 border border-dashed border-zinc-900 rounded-2xl flex flex-col items-center justify-center space-y-3">
                <FileText size={42} className="text-zinc-700" />
                <div>No specification documents found. Add roadmap spec files to start.</div>
              </div>
            )}
          </>
        )}

        {/* Dialog Modal Trigger */}
        <Dialog
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Upload New Document"
          description="Support formats: PDF, DOCX, TXT, CSV, MD specification files"
        >
          <form onSubmit={handleCreateDoc} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Roadmap Spec File
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                className="flex w-full rounded-lg border border-zinc-850 bg-zinc-950 px-3 py-2 text-xs text-zinc-300 focus:outline-none"
              />
            </div>
            <Input
              label="Document Name"
              placeholder="e.g. AI Engine PRD"
              value={newName}
              onChange={(e) => {
                setNewName(e.target.value);
                if (e.target.value.trim()) setErrorName('');
              }}
              error={errorName}
            />
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Link to Project Roadmap
              </label>
              <select
                value={newProject}
                onChange={(e) => setNewProject(e.target.value)}
                className="flex h-10 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 focus:outline-none"
              >
                <option value="">General (No project mapping)</option>
                {projects.map((p) => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Classification Category
              </label>
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="flex h-10 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 focus:outline-none"
              >
                <option value="Requirements">Requirements</option>
                <option value="Design">Design</option>
                <option value="Architecture">Architecture</option>
                <option value="Retrospective">Retrospective</option>
                <option value="General">General</option>
              </select>
            </div>
            <Input
              label="Tags (Comma separated)"
              placeholder="e.g. v1, marketing, security"
              value={newTagsStr}
              onChange={(e) => setNewTagsStr(e.target.value)}
            />
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Upload File
              </Button>
            </div>
          </form>
        </Dialog>
      </div>
    </AppShell>
  );
}
