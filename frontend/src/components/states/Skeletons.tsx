// 로딩 스켈레톤(§14.6.2) — 레이아웃 보존 + 시머. 차트는 축 먼저, 영역만 시머. reduced-motion 대응(.skeleton).
import { cn } from "../../lib/utils";

/** 시머 바 1개. */
function Bar({ className }: { className?: string }) {
  return <div className={cn("skeleton h-3", className)} aria-hidden />;
}

/** 차트 스켈레톤 — 축 즉시 렌더 + 곡선 영역만 시머(계측 다이얼 켜지는 느낌). */
export function ChartSkeleton({ height = 380 }: { height?: number }) {
  return (
    <div
      className="relative rounded-lg bg-inset"
      style={{ height }}
      role="status"
      aria-label="차트 로딩 중"
    >
      {/* 좌·하 축선만(데이터잉크↓ §14.4) */}
      <div className="absolute bottom-12 left-16 right-6 top-6 border-b border-l border-border-default">
        <div className="skeleton absolute inset-3 rounded-md opacity-60" />
      </div>
    </div>
  );
}

/** 통계 띠 스켈레톤(overline 짧은 바 + hero 큰 바 + 마이크로) ×4. */
export function StatBandSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg bg-border-subtle md:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="flex flex-col gap-2 bg-surface p-4">
          <Bar className="w-16" />
          <Bar className="h-6 w-20" />
          <Bar className="w-12 opacity-70" />
        </div>
      ))}
    </div>
  );
}

/** 테이블 스켈레톤 — n 행. */
export function TableSkeleton({ rows = 4, cols = 6 }: { rows?: number; cols?: number }) {
  return (
    <div className="rounded-lg border border-border-subtle" role="status" aria-label="테이블 로딩 중">
      <div className="border-b border-border-default px-3 py-2">
        <Bar className="w-24" />
      </div>
      {Array.from({ length: rows }).map((_, r) => (
        <div
          key={r}
          className="flex items-center gap-4 border-b border-border-subtle px-3 py-3 last:border-0"
        >
          {Array.from({ length: cols }).map((_, c) => (
            <Bar key={c} className={cn("flex-1", c === 0 ? "max-w-[6rem]" : "max-w-[4rem]")} />
          ))}
        </div>
      ))}
    </div>
  );
}
