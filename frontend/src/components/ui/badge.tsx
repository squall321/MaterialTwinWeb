// 배지 프리미티브 — semantic variant(§14.2 success/warning/danger/info), radius-sm.
import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "../../lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-sm border px-2 py-0.5 text-xs font-medium",
  {
    variants: {
      variant: {
        default: "border-transparent bg-primary-muted text-[var(--primary-hover)]",
        accent: "border-transparent bg-accent-muted text-accent",
        success: "border-transparent bg-[var(--accent-muted)] text-success",
        warning: "border-[color:var(--warning)] bg-transparent text-warning",
        danger: "border-[color:var(--danger)] bg-transparent text-danger",
        info: "border-transparent bg-primary-muted text-info",
        outline: "border-border-default bg-transparent text-text-secondary",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
