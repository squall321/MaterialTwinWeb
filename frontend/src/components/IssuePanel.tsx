// 파서 이슈 패널(§14.6.3). ERROR/WARN/INFO 등급별·인라인·실행가능. 파일별 부분실패·계산게이트 노출(★C9).
import { CircleAlert, TriangleAlert, Info } from "lucide-react";
import { cn } from "../lib/utils";
import type { Issue } from "../api/uploads";

type Props = {
  issues: Issue[];
  /** 파일명(파일별 부분실패 헤더). */
  filename?: string;
  /** 계산게이트 결과 — 물성 산출이 실제로 이뤄졌는지(★C9). */
  computed?: boolean;
  /** ERROR 이슈의 액션(예: 매핑 열기). */
  onResolveError?: () => void;
  className?: string;
};

const LEVEL_RANK: Record<string, number> = { ERROR: 0, WARN: 1, INFO: 2 };

function levelMeta(level: string) {
  switch (level) {
    case "ERROR":
      return { Icon: CircleAlert, color: "text-danger", label: "ERROR", blocking: true };
    case "WARN":
      return { Icon: TriangleAlert, color: "text-warning", label: "WARN", blocking: false };
    default:
      return { Icon: Info, color: "text-info", label: "INFO", blocking: false };
  }
}

export function IssuePanel({ issues, filename, computed, onResolveError, className }: Props) {
  if (issues.length === 0 && computed !== false) return null;

  const sorted = [...issues].sort(
    (a, b) => (LEVEL_RANK[a.level] ?? 9) - (LEVEL_RANK[b.level] ?? 9),
  );
  const errorCount = issues.filter((i) => i.level === "ERROR").length;
  const blocked = errorCount > 0;

  // 헤더 톤 — 차단(ERROR)이면 danger, 아니면 warning/안내.
  const headerTone = blocked ? "text-danger" : issues.length > 0 ? "text-warning" : "text-text-secondary";

  return (
    <div
      className={cn("rounded-lg border border-border-default bg-surface", className)}
      role="region"
      aria-label="파싱 이슈"
    >
      <div className="flex items-center justify-between border-b border-border-subtle px-3 py-2">
        <span className={cn("text-[0.8125rem] font-medium", headerTone)}>
          {filename ? `${filename} · ` : ""}
          {issues.length > 0
            ? `${issues.length} issue${issues.length > 1 ? "s" : ""} · ${blocked ? "차단됨" : "진행 가능"}`
            : "처리 완료"}
        </span>
        {computed !== undefined && (
          <span
            className={cn(
              "text-[0.6875rem] uppercase tracking-[0.04em]",
              computed ? "text-success" : "text-text-tertiary",
            )}
          >
            {computed ? "물성 산출됨" : "물성 미산출"}
          </span>
        )}
      </div>

      <ul className="divide-y divide-border-subtle">
        {sorted.map((issue, idx) => {
          const { Icon, color, label, blocking } = levelMeta(issue.level);
          return (
            <li key={`${issue.code}-${idx}`} className="flex items-start gap-2.5 px-3 py-2.5">
              <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", color)} aria-hidden />
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className={cn("text-[0.6875rem] font-semibold uppercase tracking-[0.04em]", color)}>
                    {label}
                  </span>
                  <span className="font-mono text-[0.6875rem] text-text-tertiary">{issue.code}</span>
                </div>
                <p className="mt-0.5 text-[0.8125rem] text-text-secondary">{issue.message}</p>
              </div>
              {blocking && onResolveError && (
                <button
                  type="button"
                  onClick={onResolveError}
                  className="shrink-0 rounded-sm border border-border-default px-2 py-1 text-[0.75rem] text-text-secondary transition-colors hover:border-border-strong hover:text-text-primary"
                >
                  매핑 열기
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
