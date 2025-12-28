import { ReactNode } from 'react';
import { cn } from "../../utils/cn"

export const Card = ({
  className,
  children,
  ...props
}: {
  className?: string;
  children: ReactNode;
  [key: string]: any;
}) => (
  <div
    className={cn(
      'bg-white rounded-md border border-gray-200 shadow-sm',
      className
    )}
    {...props}
  >
    {children}
  </div>
);

export const CardHeader = ({
  className,
  children,
  ...props
}: {
  className?: string;
  children: ReactNode;
  [key: string]: any;
}) => (
  <div className={cn('px-4 py-3 border-b border-gray-200', className)} {...props}>
    {children}
  </div>
);

export const CardContent = ({
  className,
  children,
  ...props
}: {
  className?: string;
  children: ReactNode;
  [key: string]: any;
}) => (
  <div className={cn('px-4 py-3', className)} {...props}>
    {children}
  </div>
);

export const CardFooter = ({
  className,
  children,
  ...props
}: {
  className?: string;
  children: ReactNode;
  [key: string]: any;
}) => (
  <div className={cn('px-4 py-3 border-t border-gray-200', className)} {...props}>
    {children}
  </div>
);
