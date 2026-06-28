// 입력 프리미티브 — inset well 결의 입력 필드(§14.2 토큰).
import * as React from "react";
import { cn } from "../../lib/utils";

const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        ref={ref}
        className={cn(
          "flex h-9 w-full rounded-md border border-border-default bg-inset px-3 py-1 text-sm text-text-primary",
          "shadow-[var(--inset-well)] transition-colors duration-[130ms]",
          "placeholder:text-text-tertiary",
          "focus-visible:outline-none focus-visible:border-primary",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className,
        )}
        {...props}
      />
    );
  },
);
Input.displayName = "Input";

export { Input };
