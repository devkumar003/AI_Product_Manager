import Link from 'next/link';
import { ArrowRight, Sparkles, FolderKanban, FileText, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-zinc-950 text-zinc-100 flex flex-col overflow-hidden">
      {/* Background radial overlays */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-indigo-600/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute bottom-0 right-10 w-[600px] h-[600px] bg-purple-600/5 rounded-full blur-[160px] pointer-events-none" />

      {/* Header */}
      <header className="z-10 flex h-20 items-center justify-between px-6 lg:px-16 border-b border-zinc-900/50 backdrop-blur-md sticky top-0">
        <div className="flex items-center space-x-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-lg shadow-indigo-500/20">
            <Sparkles size={20} />
          </div>
          <span className="text-lg font-bold tracking-tight text-white">
            AI Product<span className="text-indigo-500">OS</span>
          </span>
        </div>
        <div className="flex items-center space-x-4">
          <Link href="/login">
            <Button variant="ghost">Sign In</Button>
          </Link>
          <Link href="/signup">
            <Button variant="primary">Get Started</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center items-center text-center px-6 py-20 lg:py-32 z-10 space-y-8 max-w-4xl mx-auto">
        <div className="inline-flex items-center space-x-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3.5 py-1 text-xs font-semibold text-indigo-400 backdrop-blur-md">
          <Sparkles size={12} />
          <span>Next-Gen Product Management is Here</span>
        </div>
        
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-zinc-200 to-zinc-500 leading-tight">
          The Operating System for AI-First Product Managers
        </h1>

        <p className="max-w-2xl text-md md:text-lg text-zinc-400 leading-relaxed">
          Plan projects, compose dynamic product specification documents, orchestrate team milestones, and supercharge workflows using context-aware assistant tools.
        </p>

        <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4 pt-4">
          <Link href="/signup">
            <Button variant="primary" size="lg" className="w-full sm:w-auto text-md px-8 py-6">
              Start Free Trial <ArrowRight size={18} className="ml-2" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="glass" size="lg" className="w-full sm:w-auto text-md px-8 py-6">
              Launch Console
            </Button>
          </Link>
        </div>
      </section>

      {/* Features Grid */}
      <section className="px-6 lg:px-16 py-16 z-10 max-w-7xl mx-auto w-full border-t border-zinc-900/50">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <Card className="hover:border-indigo-500/40 transition duration-300">
            <CardContent className="p-8 space-y-4">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center">
                <FolderKanban size={24} />
              </div>
              <h3 className="text-xl font-bold text-white">Dynamic Roadmaps</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Orchestrate project phases, tasks, and dependencies with smooth visual interfaces designed for agility.
              </p>
            </CardContent>
          </Card>

          <Card className="hover:border-indigo-500/40 transition duration-300">
            <CardContent className="p-8 space-y-4">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center">
                <FileText size={24} />
              </div>
              <h3 className="text-xl font-bold text-white">Doc Workspace</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Compose, link, and format requirements documents, features lists, and user stories in a rich text interface.
              </p>
            </CardContent>
          </Card>

          <Card className="hover:border-indigo-500/40 transition duration-300">
            <CardContent className="p-8 space-y-4">
              <div className="h-12 w-12 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center">
                <Shield size={24} />
              </div>
              <h3 className="text-xl font-bold text-white">Enterprise Security</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Roles-based access control, encrypted data stores, and verified JSON-token authenticated requests.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="z-10 border-t border-zinc-900 bg-zinc-950/50 py-8 px-6 lg:px-16 text-center text-xs text-zinc-500 flex flex-col sm:flex-row items-center justify-between max-w-7xl mx-auto w-full">
        <p>© 2026 AI ProductOS Technologies Inc. All rights reserved.</p>
        <div className="flex space-x-6 mt-4 sm:mt-0">
          <a href="#" className="hover:text-zinc-300 transition">Terms of Service</a>
          <a href="#" className="hover:text-zinc-300 transition">Privacy Policy</a>
          <a href="#" className="hover:text-zinc-300 transition">Contact</a>
        </div>
      </footer>
    </div>
  );
}
