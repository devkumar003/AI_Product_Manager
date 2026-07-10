'use client';

import * as React from 'react';

/**
 * Task 12 — Skeleton UI components for loading states.
 */

export function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-xl border border-zinc-800 bg-zinc-900/30 p-5 space-y-3">
      <div className="h-4 w-1/3 rounded bg-zinc-800" />
      <div className="h-3 w-2/3 rounded bg-zinc-800/50" />
      <div className="h-3 w-1/2 rounded bg-zinc-800/30" />
    </div>
  );
}

export function SkeletonLine({ width = '100%' }: { width?: string }) {
  return <div className="animate-pulse h-3 rounded bg-zinc-800/60" style={{ width }} />;
}

export function SkeletonGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}

export function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClasses = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-10 h-10' };
  return (
    <div className={`${sizeClasses[size]} border-2 border-zinc-700 border-t-indigo-400 rounded-full animate-spin`} />
  );
}

export function PageLoader({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-3">
      <LoadingSpinner size="lg" />
      <span className="text-sm text-zinc-500">{message}</span>
    </div>
  );
}

export function EmptyState({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 text-center">
      <span className="text-4xl mb-3">{icon}</span>
      <h3 className="text-lg font-semibold text-zinc-300">{title}</h3>
      <p className="text-sm text-zinc-500 mt-1 max-w-sm">{description}</p>
    </div>
  );
}

export function SkeletonTable({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-xl border border-zinc-800 overflow-hidden">
      <div className="bg-zinc-900/60 p-3 flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="animate-pulse h-3 flex-1 rounded bg-zinc-700" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, ri) => (
        <div key={ri} className="p-3 flex gap-4 border-t border-zinc-800/50">
          {Array.from({ length: cols }).map((_, ci) => (
            <div key={ci} className="animate-pulse h-3 flex-1 rounded bg-zinc-800/40" />
          ))}
        </div>
      ))}
    </div>
  );
}
