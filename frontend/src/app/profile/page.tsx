'use client';

import * as React from 'react';
import { Save } from 'lucide-react';
import { AppShell } from '@/components/layout/shell';
import { Breadcrumb } from '@/components/ui/breadcrumb';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { useAuth } from '@/context/AuthContext';
import { Loading } from '@/components/ui/loading';
import { apiService } from '@/lib/api';

export default function ProfilePage() {
  const { user, refreshUser, isLoading, isAuthenticated } = useAuth();
  const [isSaving, setIsSaving] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  const [fullName, setFullName] = React.useState('');
  const [phone, setPhone] = React.useState('');
  const [timezone, setTimezone] = React.useState('UTC');
  const [language, setLanguage] = React.useState('en');

  // Initialize fields once user is loaded
  React.useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setPhone(user.phone || '');
      setTimezone(user.timezone || 'UTC');
      setLanguage(user.language || 'en');
    }
  }, [user]);

  if (isLoading) {
    return <Loading fullScreen />;
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const initials = fullName
    ? fullName
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2)
    : 'U';

  const handleSave = async () => {
    setIsSaving(true);
    setSuccessMsg(null);
    setErrorMsg(null);
    try {
      await apiService.put('/users/me', {
        full_name: fullName,
        phone: phone || null,
        timezone: timezone,
        language: language,
      });
      await refreshUser();
      setSuccessMsg('Profile updated successfully!');
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setErrorMsg(err?.message || 'Failed to update profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <Breadcrumb items={[{ label: 'Home', href: '/' }, { label: 'Profile' }]} />
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">
            User Profile
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Summary Card */}
          <Card className="flex flex-col items-center p-6 text-center">
            <div className="h-24 w-24 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 border-2 border-zinc-700 flex items-center justify-center text-3xl font-bold text-white shadow-xl shadow-indigo-500/10 mb-4">
              {initials}
            </div>
            <h3 className="text-xl font-bold text-white">{fullName}</h3>
            <p className="text-xs text-indigo-400 font-semibold uppercase tracking-wider mt-1">
              {user.username}
            </p>
            <p className="text-sm text-zinc-500 mt-2">{user.email}</p>
          </Card>

          {/* Right Inputs Card */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Details</CardTitle>
                <CardDescription>Update your personal information and metadata</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {successMsg && (
                  <div className="rounded-lg bg-emerald-950/20 border border-emerald-900/50 p-3 text-xs text-emerald-400 font-medium">
                    {successMsg}
                  </div>
                )}
                {errorMsg && (
                  <div className="rounded-lg bg-red-950/20 border border-red-900/50 p-3 text-xs text-red-400 font-medium">
                    {errorMsg}
                  </div>
                )}

                <Input
                  label="Full Name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="John Doe"
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Phone Number"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+1 (555) 000-0000"
                  />
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                      Language
                    </label>
                    <select
                      value={language}
                      onChange={(e) => setLanguage(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-300 ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="en">English (US)</option>
                      <option value="es">Spanish (ES)</option>
                      <option value="de">German (DE)</option>
                      <option value="fr">French (FR)</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
                      Timezone
                    </label>
                    <select
                      value={timezone}
                      onChange={(e) => setTimezone(e.target.value)}
                      className="flex h-10 w-full rounded-md border border-zinc-800 bg-zinc-950 px-3 py-2 text-sm text-zinc-300 ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-zinc-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time (EST/EDT)</option>
                      <option value="America/Chicago">Central Time (CST/CDT)</option>
                      <option value="America/Denver">Mountain Time (MST/MDT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PST/PDT)</option>
                      <option value="Europe/London">London (GMT/BST)</option>
                      <option value="Europe/Paris">Paris (CET/CEST)</option>
                      <option value="Asia/Tokyo">Tokyo (JST)</option>
                    </select>
                  </div>
                </div>

                <Input
                  label="Email Address"
                  type="email"
                  value={user.email}
                  disabled
                />
                <p className="text-[10px] text-zinc-500">
                  Email modifications require tenant administrator credentials verification.
                </p>
              </CardContent>
              <CardFooter className="flex justify-end border-zinc-900">
                <Button variant="primary" onClick={handleSave} isLoading={isSaving}>
                  <Save size={16} className="mr-2" /> Save Profile
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
