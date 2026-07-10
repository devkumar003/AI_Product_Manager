import Link from 'next/link';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function NotFound() {
  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center bg-zinc-950 px-4 text-center overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-600/5 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-1/3 w-[400px] h-[400px] bg-indigo-600/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="z-10 space-y-6 max-w-md">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-xl bg-red-950/20 border border-red-900/50 text-red-500 shadow-xl shadow-red-900/5">
          <AlertCircle size={28} />
        </div>
        
        <div className="space-y-2">
          <h1 className="text-4xl font-extrabold tracking-tight text-white">404 - Page Not Found</h1>
          <p className="text-sm text-zinc-400 leading-relaxed">
            The workspace section or product specification page you are trying to access does not exist or has been relocated.
          </p>
        </div>

        <div className="pt-4">
          <Link href="/dashboard">
            <Button variant="outline" className="w-full">
              <ArrowLeft size={16} className="mr-2" /> Return to Dashboard
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
