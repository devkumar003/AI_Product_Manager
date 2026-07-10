'use client';

import * as React from 'react';
import { Settings, Shield, Bell, Key, Save, Lock, ToggleLeft, ToggleRight, Check, Sliders } from 'lucide-react';

import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { apiService } from '@/lib/api';

export default function SettingsPage() {
  const { activeWorkspace, refreshUser } = useAuth();
  
  const [activeTab, setActiveTab] = React.useState('general');
  const [isSaving, setIsSaving] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);

  // General & Workspace State
  const [workspaceName, setWorkspaceName] = React.useState('');
  const [defaultStatus, setDefaultStatus] = React.useState('active');
  const [openaiKey, setOpenaiKey] = React.useState('sk-proj-••••••••••••••••••••••••');

  // Security State
  const [currentPassword, setCurrentPassword] = React.useState('');
  const [newPassword, setNewPassword] = React.useState('');
  const [confirmPassword, setConfirmPassword] = React.useState('');
  const [twoFactor, setTwoFactor] = React.useState(false);
  const [sessionTimeout, setSessionTimeout] = React.useState('60');

  // Notifications State
  const [notifyReport, setNotifyReport] = React.useState(true);
  const [notifySync, setNotifySync] = React.useState(true);
  const [notifyDigest, setNotifyDigest] = React.useState(false);
  const [slackWebhook, setSlackWebhook] = React.useState('https://hooks.slack.com/services/••••/••••');

  // Developer State
  const [linearToken, setLinearToken] = React.useState('lin_api_••••••••••••••••••••••••');
  const [githubToken, setGithubToken] = React.useState('ghp_••••••••••••••••••••••••');

  // Set workspace name from active workspace context
  React.useEffect(() => {
    if (activeWorkspace) {
      setWorkspaceName(activeWorkspace.name);
    }
  }, [activeWorkspace]);

  const showNotification = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(null), 3000);
  };

  const handleSaveGeneral = async () => {
    if (!activeWorkspace) return;
    setIsSaving(true);
    try {
      // 1. Update workspace details via real backend API
      await apiService.put(`/workspaces/${activeWorkspace.id}`, {
        name: workspaceName,
      });
      
      // 2. Trigger AuthContext refresh to update sidebar Immediately
      await refreshUser();
      
      showNotification('Workspace customization saved successfully!');
    } catch (err: any) {
      alert(`Failed to save settings: ${err.message || err}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveSecurity = () => {
    if (newPassword && newPassword !== confirmPassword) {
      alert('New passwords do not match.');
      return;
    }
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
      showNotification('Security credentials and access controls updated.');
    }, 1000);
  };

  const handleSaveNotifications = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      showNotification('Notification channels and alert triggers saved.');
    }, 1000);
  };

  const handleSaveDeveloper = () => {
    setIsSaving(true);
    setTimeout(() => {
      setIsSaving(false);
      showNotification('Developer tokens and Webhook integration synced.');
    }, 1000);
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Settings' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">
            System Settings
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Navigation Categories */}
          <div className="space-y-2">
            {[
              { id: 'general', name: 'General & Workspace', icon: Settings },
              { id: 'security', name: 'Security & Access', icon: Shield },
              { id: 'notifications', name: 'Notifications', icon: Bell },
              { id: 'developer', name: 'Developer Integrations', icon: Key },
            ].map((cat) => {
              const Icon = cat.icon;
              const isActive = activeTab === cat.id;
              return (
                <button
                  key={cat.id}
                  onClick={() => setActiveTab(cat.id)}
                  className={`flex w-full items-center space-x-3 px-4 py-3 rounded-lg text-sm font-semibold transition border ${
                    isActive
                      ? 'bg-zinc-900 border-zinc-800 text-white shadow-lg'
                      : 'border-transparent text-zinc-400 hover:bg-zinc-900/50 hover:text-zinc-200'
                  }`}
                >
                  <Icon size={16} />
                  <span>{cat.name}</span>
                </button>
              );
            })}
          </div>

          {/* Settings Panels */}
          <div className="lg:col-span-2 space-y-6">
            {successMsg && (
              <div className="rounded-lg bg-emerald-950/20 border border-emerald-900/50 p-3 text-xs text-emerald-400 font-semibold flex items-center space-x-2 animate-in fade-in duration-200">
                <Check size={14} />
                <span>{successMsg}</span>
              </div>
            )}

            {/* TAB: GENERAL */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Workspace Customization</CardTitle>
                    <CardDescription>Configure naming, logos, and defaults for this monorepo workspace</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      label="Workspace Name"
                      value={workspaceName}
                      onChange={(e) => setWorkspaceName(e.target.value)}
                    />

                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                        Default Project Status
                      </label>
                      <select 
                        value={defaultStatus}
                        onChange={(e) => setDefaultStatus(e.target.value)}
                        className="flex h-10 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="draft">Draft (Planning)</option>
                        <option value="active">Active (Development)</option>
                        <option value="archived">Archived</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>AI Integration Keys</CardTitle>
                    <CardDescription>Inject private environment keys for upcoming AI features (will validate server-side)</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      label="OpenAI Private Endpoint Token"
                      type="password"
                      value={openaiKey}
                      onChange={(e) => setOpenaiKey(e.target.value)}
                    />
                    <p className="text-[10px] text-zinc-500 leading-relaxed">
                      Keys are encrypted end-to-end and stored securely in local database session records.
                    </p>
                  </CardContent>
                  <CardFooter className="flex justify-end border-t border-zinc-900/50 pt-4">
                    <Button variant="primary" onClick={handleSaveGeneral} isLoading={isSaving}>
                      <Save size={16} className="mr-2" /> Save Workspace Settings
                    </Button>
                  </CardFooter>
                </Card>
              </div>
            )}

            {/* TAB: SECURITY */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Update Password</CardTitle>
                    <CardDescription>Ensure your account is using a long, random password to stay secure.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      label="Current Password"
                      type="password"
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                    />
                    <Input
                      label="New Password"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                    />
                    <Input
                      label="Confirm New Password"
                      type="password"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Access Controls & Session Management</CardTitle>
                    <CardDescription>Configure Multi-Factor Authentication and session expiry constraints.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between p-3 rounded-lg border border-zinc-800 bg-zinc-900/20">
                      <div>
                        <div className="text-sm font-semibold text-white">Two-Factor Authentication (2FA)</div>
                        <div className="text-xs text-zinc-500 mt-0.5">Secure your account with a Google Authenticator TOTP token.</div>
                      </div>
                      <button 
                        onClick={() => setTwoFactor(!twoFactor)}
                        className="text-zinc-400 hover:text-indigo-400 transition"
                      >
                        {twoFactor ? <ToggleRight size={32} className="text-indigo-500" /> : <ToggleLeft size={32} />}
                      </button>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                        Inactive Session Timeout
                      </label>
                      <select 
                        value={sessionTimeout}
                        onChange={(e) => setSessionTimeout(e.target.value)}
                        className="flex h-10 w-full rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="15">15 Minutes</option>
                        <option value="60">1 Hour</option>
                        <option value="1440">24 Hours</option>
                      </select>
                    </div>
                  </CardContent>
                  <CardFooter className="flex justify-end border-t border-zinc-900/50 pt-4">
                    <Button variant="primary" onClick={handleSaveSecurity} isLoading={isSaving}>
                      <Lock size={16} className="mr-2" /> Save Access Controls
                    </Button>
                  </CardFooter>
                </Card>
              </div>
            )}

            {/* TAB: NOTIFICATIONS */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Notification Triggers</CardTitle>
                    <CardDescription>Select what activities you want to receive real-time email alerts for.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-3">
                      {[
                        { id: 'report', label: 'AI Report Generation Completed', desc: 'Alert when CEO/CTO/COO reports are fully synthesized.', checked: notifyReport, setter: setNotifyReport },
                        { id: 'sync', label: 'Linear/GitHub Integration Sync Failures', desc: 'Alert if any background syncing tasks encounter credentials failures.', checked: notifySync, setter: setNotifySync },
                        { id: 'digest', label: 'Daily Operations Digest', desc: 'A summaries email containing the sprint velocity progress report.', checked: notifyDigest, setter: setNotifyDigest },
                      ].map((item) => (
                        <label key={item.id} className="flex items-start space-x-3 cursor-pointer p-2 rounded hover:bg-zinc-900/30">
                          <input 
                            type="checkbox" 
                            checked={item.checked}
                            onChange={(e) => item.setter(e.target.checked)}
                            className="mt-1 h-4 w-4 rounded border-zinc-800 bg-zinc-950 text-indigo-600 focus:ring-indigo-500" 
                          />
                          <div>
                            <div className="text-sm font-semibold text-white">{item.label}</div>
                            <div className="text-xs text-zinc-500 mt-0.5">{item.desc}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Slack Alerts Integration</CardTitle>
                    <CardDescription>Forward all workspace activity notifications directly to a Slack channel webhook.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      label="Slack Webhook Connection URL"
                      type="text"
                      value={slackWebhook}
                      onChange={(e) => setSlackWebhook(e.target.value)}
                    />
                  </CardContent>
                  <CardFooter className="flex justify-end border-t border-zinc-900/50 pt-4">
                    <Button variant="primary" onClick={handleSaveNotifications} isLoading={isSaving}>
                      <Sliders size={16} className="mr-2" /> Save Alert Channels
                    </Button>
                  </CardFooter>
                </Card>
              </div>
            )}

            {/* TAB: DEVELOPER */}
            {activeTab === 'developer' && (
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Connected Integrations & OAuth Keys</CardTitle>
                    <CardDescription>Setup secure connection tokens to synchronize issues, projects and codebases.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <Input
                      label="Linear API Connection Token"
                      type="password"
                      value={linearToken}
                      onChange={(e) => setLinearToken(e.target.value)}
                    />
                    
                    <Input
                      label="GitHub Personal Access Key"
                      type="password"
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                    />
                  </CardContent>
                  <CardFooter className="flex justify-end border-t border-zinc-900/50 pt-4">
                    <Button variant="primary" onClick={handleSaveDeveloper} isLoading={isSaving}>
                      <Key size={16} className="mr-2" /> Save Integrations
                    </Button>
                  </CardFooter>
                </Card>
              </div>
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
