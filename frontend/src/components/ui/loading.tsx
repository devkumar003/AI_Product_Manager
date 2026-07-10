import * as React from 'react';
import { twMerge } from 'tailwind-merge';

export interface LoadingProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
}

export const Loading = ({ size = 'md', fullScreen = false, className, ...props }: LoadingProps) => {
  const sizeClasses = {
    sm: 'h-6 w-6 border-2',
    md: 'h-10 w-10 border-3',
    lg: 'h-16 w-16 border-4',
  };

  const containerStyles = fullScreen
    ? 'fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/80 backdrop-blur-sm'
    : 'flex items-center justify-center p-6';

  return (
    <div className={twMerge(containerStyles, className)} {...props}>
      <div
        className={twMerge(
          'animate-spin rounded-full border-zinc-800 border-t-indigo-500',
          sizeClasses[size]
        )}
      />
    </div>
  );
};
