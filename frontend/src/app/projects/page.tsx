'use client';

import * as React from 'react';
import { Plus, Search, Calendar, FolderPlus, Copy, Archive, RefreshCw, AlertCircle } from 'lucide-react';

import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Dialog } from '@/components/ui/dialog';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

interface ProjectItem {
  id: string;
  name: string;
  description: string;
  slug: string;
  status: string;
  priority: string;
  color?: string | null;
  icon?: string | null;
  archived: boolean;
  created_at: string;
}

export default function ProjectsPage() {
  const { activeWorkspace } = useAuth();
  const [search, setSearch] = React.useState('');
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [projects, setProjects] = React.useState<ProjectItem[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [apiError, setApiError] = React.useState('');

  // Form states for new project
  const [newName, setNewName] = React.useState('');
  const [newDesc, setNewDesc] = React.useState('');
  const [newPriority, setNewPriority] = React.useState('Medium');
  const [errorName, setErrorName] = React.useState('');

  const fetchProjects = React.useCallback(async () => {
    if (!activeWorkspace) return;
    setIsLoading(true);
    setApiError('');
    try {
      const data = await apiService.get<ProjectItem[]>(`/projects/${activeWorkspace.id}`);
      setProjects(data);
    } catch (err: any) {
      setApiError(err.message || 'Failed to load projects from server.');
    } finally {
      setIsLoading(false);
    }
  }, [activeWorkspace]);

  React.useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeWorkspace) return;
    if (!newName.trim()) {
      setErrorName('Project name is required');
      return;
    }

    try {
      const payload = {
        name: newName,
        description: newDesc,
        status: 'Planning',
        priority: newPriority,
      };
      const newProj = await apiService.post<ProjectItem>(`/projects/${activeWorkspace.id}`, payload);
      setProjects([newProj, ...projects]);
      setIsModalOpen(false);
      setNewName('');
      setNewDesc('');
      setErrorName('');
    } catch (err: any) {
      setErrorName(err.message || 'Failed to create project.');
    }
  };

  const handleDuplicate = async (project_id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!activeWorkspace) return;
    try {
      const duplicated = await apiService.post<ProjectItem>(`/projects/${activeWorkspace.id}/${project_id}/duplicate`);
      setProjects([duplicated, ...projects]);
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleArchive = async (project_id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!activeWorkspace) return;
    try {
      const archived = await apiService.post<ProjectItem>(`/projects/${activeWorkspace.id}/${project_id}/archive`);
      setProjects(projects.map(p => p.id === project_id ? archived : p));
    } catch (err: any) {
      console.error(err);
    }
  };

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.description.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div>
            <Breadcrumb items={[{ label: 'Home', href: '/dashboard' }, { label: 'Projects' }]} />
            <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">
              Projects
            </h1>
          </div>
          <Button variant="primary" onClick={() => setIsModalOpen(true)} disabled={!activeWorkspace}>
            <Plus size={16} className="mr-2" /> New Project
          </Button>
        </div>

        {/* Workspace check alert */}
        {!activeWorkspace && (
          <div className="flex items-center space-x-3 p-4 bg-amber-950/20 border border-amber-900/50 rounded-xl text-amber-400 text-sm">
            <AlertCircle size={18} />
            <span>Please create or switch to an active workspace to view and manage projects.</span>
          </div>
        )}

        {activeWorkspace && (
          <>
            {/* Filter Toolbar */}
            <div className="flex items-center space-x-2 bg-zinc-950 p-1 border border-zinc-900 rounded-lg max-w-md">
              <div className="pl-3 text-zinc-500">
                <Search size={16} />
              </div>
              <input
                type="text"
                placeholder="Search projects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="flex-1 bg-transparent px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 focus:outline-none"
              />
            </div>

            {/* API Errors */}
            {apiError && (
              <div className="p-3 bg-red-950/20 border border-red-900/50 rounded-lg text-red-400 text-xs flex items-center">
                <AlertCircle size={14} className="mr-2" />
                {apiError}
              </div>
            )}

            {/* Loading Indicator */}
            {isLoading ? (
              <div className="flex items-center justify-center py-20 text-zinc-400 space-x-2">
                <RefreshCw size={20} className="animate-spin" />
                <span>Fetching roadmaps...</span>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredProjects.map((project) => (
                  <Card key={project.id} className="hover:border-zinc-800 hover:bg-zinc-950/60 transition duration-300 group">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                          project.status === 'Development' ? 'bg-indigo-950/30 border border-indigo-900/50 text-indigo-400' :
                          project.status === 'Planning' ? 'bg-emerald-950/30 border border-emerald-900/50 text-emerald-400' :
                          project.status === 'Archived' ? 'bg-zinc-900 border border-zinc-800 text-zinc-400' :
                          'bg-amber-950/30 border border-amber-900/50 text-amber-400'
                        }`}>
                          {project.status}
                        </span>
                        <div className="flex items-center text-xs text-zinc-500">
                          <Calendar size={12} className="mr-1" /> {new Date(project.created_at).toLocaleDateString()}
                        </div>
                      </div>
                      <CardTitle className="text-lg font-bold mt-2 text-white">{project.name}</CardTitle>
                      <CardDescription className="text-zinc-400 text-sm mt-1">{project.description || 'No roadmap description provided.'}</CardDescription>
                    </CardHeader>
                    <CardFooter className="flex justify-between items-center text-xs border-zinc-900">
                      <span className="text-zinc-500 font-mono">/{project.slug}</span>
                      <div className="flex items-center space-x-2">
                        <Button variant="outline" size="sm" onClick={(e) => handleDuplicate(project.id, e)} title="Duplicate roadmap">
                          <Copy size={12} />
                        </Button>
                        {!project.archived && (
                          <Button variant="outline" size="sm" onClick={(e) => handleArchive(project.id, e)} title="Archive roadmap">
                            <Archive size={12} />
                          </Button>
                        )}
                        <Button variant="outline" size="sm" href={`/projects/${project.id}`}>
                          Open Roadmap
                        </Button>
                      </div>
                    </CardFooter>
                  </Card>
                ))}
                {filteredProjects.length === 0 && (
                  <div className="col-span-2 py-16 text-center text-zinc-500 bg-zinc-950/30 border border-dashed border-zinc-900 rounded-2xl flex flex-col items-center justify-center space-y-3">
                    <FolderPlus size={36} className="text-zinc-700" />
                    <div>No projects found. Create a new one to start tracking.</div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Dialog Modal Trigger */}
        <Dialog
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Create New Project"
          description="Initialize a new product roadmap workspace"
        >
          <form onSubmit={handleCreateProject} className="space-y-4">
            <Input
              label="Project Name"
              placeholder="e.g. AI Content Writer"
              value={newName}
              onChange={(e) => {
                setNewName(e.target.value);
                if (e.target.value.trim()) setErrorName('');
              }}
              error={errorName}
            />
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Project Description
              </label>
              <textarea
                placeholder="What is this project roadmap about?"
                rows={3}
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                className="flex w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 placeholder:text-zinc-500 transition focus:border-indigo-500 focus:outline-none"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                Priority level
              </label>
              <select
                value={newPriority}
                onChange={(e) => setNewPriority(e.target.value)}
                className="flex h-10 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 transition focus:border-indigo-500 focus:outline-none"
              >
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                Create Project
              </Button>
            </div>
          </form>
        </Dialog>
      </div>
    </AppShell>
  );
}
