// 스켈레톤 프리미티브 — pulse 로딩 플레이스홀더(surface-2 결).
import * as React from "react";
import { cn } from "../../lib/utils";

function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-surface-2", className)}
      {...props}
    />
  );
}

export { Skeleton };
