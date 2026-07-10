'use client';

import * as React from 'react';
import { Sparkles, ArrowRight, Building2, Briefcase, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '../ui/card';
import { apiService } from '../../lib/api';

interface SetupWizardProps {
  onComplete: () => Promise<void>;
}

export const SetupWizard = ({ onComplete }: SetupWizardProps) => {
  const [step, setStep] = React.useState(1);
  const [isLoading, setIsLoading] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  // Step 1: Org details
  const [orgName, setOrgName] = React.useState('');
  const [orgSlug, setOrgSlug] = React.useState('');
  const [orgDesc, setOrgDesc] = React.useState('');

  // Step 2: Workspace details
  const [wsName, setWsName] = React.useState('');
  const [wsDesc, setWsDesc] = React.useState('');
  const [wsColor, setWsColor] = React.useState('#6366f1');
  const [wsVisibility, setWsVisibility] = React.useState('private');

  // Auto-generate slug from organization name
  React.useEffect(() => {
    setOrgSlug(
      orgName
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/(^-|-$)+/g, '')
    );
  }, [orgName]);

  const handleNextStep = () => {
    if (step === 1) {
      if (!orgName.trim()) {
        setErrorMsg('Organization name is required');
        return;
      }
      setErrorMsg(null);
      setWsName(`${orgName} Team`); // Default workspace name
      setStep(2);
    }
  };

  const handleBackStep = () => {
    setStep(1);
    setErrorMsg(null);
  };

  const handleSubmit = async () => {
    if (!wsName.trim()) {
      setErrorMsg('Workspace name is required');
      return;
    }

    setIsLoading(true);
    setErrorMsg(null);

    try {
      // 1. Create Organization
      const org = await apiService.post<{ id: string }>('/organizations/', {
        name: orgName,
        slug: orgSlug,
        description: orgDesc || null,
      });

      // 2. Create Workspace
      await apiService.post(`/workspaces/?org_id=${org.id}`, {
        name: wsName,
        description: wsDesc || null,
        color: wsColor,
        visibility: wsVisibility,
        icon: 'briefcase',
      });

      // 3. Mark setup complete
      setStep(3);
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to complete setup wizard. Please try again.');
      setIsLoading(false);
    }
  };

  const handleFinalize = async () => {
    setIsLoading(true);
    try {
      await onComplete();
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to load dashboard context.');
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950 px-4 py-12 overflow-hidden">
      {/* Premium Glassmorphic Gradients */}
      <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none" />

      <div className="w-full max-w-lg z-10 space-y-6">
        {/* Logo and Progress Tracker */}
        <div className="flex flex-col items-center text-center space-y-2">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-xl shadow-indigo-500/20">
            <Sparkles size={24} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-4">
            Setting up AI ProductOS
          </h1>
          <p className="text-sm text-zinc-400">
            Create your organization and team workspace to get started.
          </p>

          {/* Step Indicator */}
          <div className="flex items-center space-x-2 mt-4">
            <span
              className={`h-2 w-12 rounded-full transition-all duration-300 ${
                step >= 1 ? 'bg-indigo-500' : 'bg-zinc-800'
              }`}
            />
            <span
              className={`h-2 w-12 rounded-full transition-all duration-300 ${
                step >= 2 ? 'bg-indigo-500' : 'bg-zinc-800'
              }`}
            />
            <span
              className={`h-2 w-12 rounded-full transition-all duration-300 ${
                step >= 3 ? 'bg-indigo-500' : 'bg-zinc-800'
              }`}
            />
          </div>
        </div>

        <Card className="border border-zinc-800/80 bg-zinc-950/60 backdrop-blur-md transition-all duration-300">
          {errorMsg && (
            <div className="mx-6 mt-6 rounded-lg bg-red-950/20 border border-red-900/50 p-3 text-xs text-red-500 font-medium">
              {errorMsg}
            </div>
          )}

          {step === 1 && (
            <>
              <CardHeader>
                <div className="flex items-center space-x-2 text-indigo-400">
                  <Building2 size={20} />
                  <CardTitle className="text-lg">Create Your Organization</CardTitle>
                </div>
                <CardDescription>
                  Organizations represent your company or tenant account.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  label="Organization Name"
                  placeholder="e.g. Acme Corp"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                />
                <Input
                  label="URL Slug"
                  placeholder="acme-corp"
                  value={orgSlug}
                  onChange={(e) => setOrgSlug(e.target.value)}
                />
                <div className="space-y-1">
                  <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                    Description (Optional)
                  </label>
                  <textarea
                    placeholder="Describe your organization's purpose"
                    value={orgDesc}
                    onChange={(e) => setOrgDesc(e.target.value)}
                    className="flex min-h-[80px] w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-300 placeholder:text-zinc-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  />
                </div>
              </CardContent>
              <CardFooter className="flex justify-end">
                <Button onClick={handleNextStep}>
                  Next Step <ArrowRight size={16} className="ml-2" />
                </Button>
              </CardFooter>
            </>
          )}

          {step === 2 && (
            <>
              <CardHeader>
                <div className="flex items-center space-x-2 text-indigo-400">
                  <Briefcase size={20} />
                  <CardTitle className="text-lg">Create Your First Workspace</CardTitle>
                </div>
                <CardDescription>
                  Workspaces group projects, roadmaps, and PRD specifications.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  label="Workspace Name"
                  placeholder="e.g. Engineering Team"
                  value={wsName}
                  onChange={(e) => setWsName(e.target.value)}
                />
                <div className="space-y-1">
                  <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                    Description (Optional)
                  </label>
                  <textarea
                    placeholder="Describe this workspace's projects"
                    value={wsDesc}
                    onChange={(e) => setWsDesc(e.target.value)}
                    className="flex min-h-[80px] w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-300 placeholder:text-zinc-600 focus-visible:outline-none"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                      Visibility
                    </label>
                    <select
                      value={wsVisibility}
                      onChange={(e) => setWsVisibility(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-300"
                    >
                      <option value="private">Private (Only invited members)</option>
                      <option value="public">Public (Everyone in organization)</option>
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400 font-sans">
                      Workspace Accent Color
                    </label>
                    <div className="flex items-center space-x-2 mt-1">
                      {['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'].map((color) => (
                        <button
                          key={color}
                          type="button"
                          onClick={() => setWsColor(color)}
                          className={`h-6 w-6 rounded-full border transition duration-150 ${
                            wsColor === color ? 'border-white scale-110' : 'border-transparent'
                          }`}
                          style={{ backgroundColor: color }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="ghost" onClick={handleBackStep} disabled={isLoading}>
                  Back
                </Button>
                <Button onClick={handleSubmit} isLoading={isLoading}>
                  Finish Setup <ArrowRight size={16} className="ml-2" />
                </Button>
              </CardFooter>
            </>
          )}

          {step === 3 && (
            <div className="flex flex-col items-center justify-center p-8 text-center space-y-4">
              <CheckCircle2 size={48} className="text-emerald-500 animate-bounce" />
              <h2 className="text-lg font-bold text-white">Your Workspace is Ready!</h2>
              <p className="text-sm text-zinc-400 max-w-sm">
                Successfully set up <strong>{orgName}</strong> organization and{' '}
                <strong>{wsName}</strong> workspace. Let&apos;s open your dashboard.
              </p>
              <Button onClick={handleFinalize} className="w-full mt-4" isLoading={isLoading}>
                Go to Dashboard
              </Button>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};
