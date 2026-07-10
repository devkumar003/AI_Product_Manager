import * as React from 'react';
import { twMerge } from 'tailwind-merge';
import { Button } from './button';

export interface ErrorStateProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  retryText?: string;
  onRetry?: () => void;
}

export const ErrorState = ({
  title = 'Something went wrong',
  message,
  retryText,
  onRetry,
  className,
  ...props
}: ErrorStateProps) => {
  return (
    <div
      className={twMerge(
        'flex flex-col items-center justify-center rounded-xl border border-red-950/30 bg-red-950/10 p-8 text-center backdrop-blur-md max-w-lg mx-auto border-t-red-600/50',
        className
      )}
      {...props}
    >
      <div className="mb-4 flex items-center justify-center rounded-full bg-red-950/40 p-4 text-red-500 border border-red-900/50">
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
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      </div>
      <h3 className="text-lg font-bold text-white mb-1">{title}</h3>
      <p className="text-sm text-zinc-300 mb-6">{message}</p>
      {retryText && onRetry && (
        <Button variant="danger" onClick={onRetry}>
          {retryText}
        </Button>
      )}
    </div>
  );
};
