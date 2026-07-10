import * as React from 'react';
import { twMerge } from 'tailwind-merge';
import { Button } from './button';

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}

export const EmptyState = ({
  title,
  description,
  actionText,
  onAction,
  icon,
  className,
  ...props
}: EmptyStateProps) => {
  return (
    <div
      className={twMerge(
        'flex flex-col items-center justify-center rounded-xl border border-dashed border-zinc-800 bg-zinc-950/20 p-8 text-center backdrop-blur-md',
        className
      )}
      {...props}
    >
      <div className="mb-4 flex items-center justify-center rounded-full bg-zinc-900/80 p-4 text-zinc-400 border border-zinc-800">
        {icon ? (
          icon
        ) : (
          <svg
            className="h-8 w-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="1.5"
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
            />
          </svg>
        )}
      </div>
      <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
      <p className="max-w-xs text-sm text-zinc-400 mb-6">{description}</p>
      {actionText && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionText}
        </Button>
      )}
    </div>
  );
};
