// 수동 컬럼 매핑(§5.2·C5) — sniff 컬럼별 역할을 사용자가 재지정. {header: role} 매핑 산출.
import { ArrowRight, CircleAlert, Wand2 } from "lucide-react";
import type { SniffColumn } from "../api/uploads";
import { cn } from "../lib/utils";

// 역할 표시 라벨(한국어). backend roles vocabulary와 값 일치.
const ROLE_LABEL: Record<string, string> = {
  time: "시간",
  force: "힘",
  displacement: "변위(crosshead)",
  extension: "신율계",
  strain: "변형률",
  stress: "응력",
  unknown: "무시",
};

type Props = {
  columns: SniffColumn[];
  /** backend /api/parsers 의 roles vocabulary. 빈 배열이면 로드 실패로 간주. */
  roles: string[];
  /** 현재 매핑 {header: role}. 비어있으면 자동감지값 사용. */
  value: Record<string, string>;
  onChange: (mapping: Record<string, string>) => void;
  /** roles 로드 실패 시 재시도 콜백(parsers 쿼리 refetch 등). */
  onRetryRoles?: () => void;
};

/**
 * 매핑 유효성 — 응력 축(stress 또는 force)과 변형률 축(strain·extension·displacement)이
 * 각각 하나 이상 있어야 backend가 물성을 계산할 수 있다(ingest.py 정규화 규칙과 동일).
 */
export function hasAxisPair(
  columns: SniffColumn[],
  value: Record<string, string>,
): boolean {
  const effective = new Set(columns.map((c) => value[c.header] ?? c.role));
  return (
    (effective.has("stress") || effective.has("force")) &&
    (effective.has("strain") || effective.has("extension") || effective.has("displacement"))
  );
}

export function ColumnMapper({ columns, roles, value, onChange, onRetryRoles }: Props) {
  // 각 컬럼의 현재 역할: 매핑 오버라이드 우선, 없으면 감지값.
  const roleOf = (c: SniffColumn) => value[c.header] ?? c.role;

  const setRole = (header: string, role: string) => {
    onChange({ ...value, [header]: role });
  };

  const rolesMissing = roles.length === 0;
  const pairOk = hasAxisPair(columns, value);

  return (
    <div className="flex flex-col gap-3">
      {rolesMissing && (
        <div
          className="flex items-center justify-between gap-3 rounded-md border border-border-default bg-surface-2 px-3 py-2"
          role="alert"
        >
          <span className="flex items-center gap-2 text-sm text-danger">
            <CircleAlert className="size-4 shrink-0" aria-hidden />
            역할 목록을 불러오지 못해 매핑을 지정할 수 없습니다.
          </span>
          {onRetryRoles && (
            <button
              type="button"
              onClick={onRetryRoles}
              className="shrink-0 rounded-sm border border-border-default px-2 py-1 text-xs text-text-secondary transition-colors hover:border-border-strong hover:text-text-primary"
            >
              다시 시도
            </button>
          )}
        </div>
      )}
      <div className="flex items-center gap-2 text-sm text-text-secondary">
        <Wand2 className="size-4 text-primary" />
        컬럼 역할을 확인하고 필요하면 직접 지정하세요.
      </div>
      <div className="flex flex-col gap-1.5">
        {columns.map((c) => {
          const current = roleOf(c);
          const overridden = value[c.header] != null && value[c.header] !== c.role;
          return (
            <div
              key={c.index}
              className="flex items-center gap-3 rounded-md border border-border-subtle bg-surface px-3 py-2"
            >
              <div className="min-w-0 flex-1">
                <span className="tnum block truncate text-sm text-text-primary">
                  {c.header}
                </span>
                {c.unit && (
                  <span className="text-xs text-text-tertiary">단위 {c.unit}</span>
                )}
              </div>
              <ArrowRight className="size-3.5 shrink-0 text-text-tertiary" />
              <select
                aria-label={`${c.header} 역할`}
                value={current}
                disabled={rolesMissing}
                onChange={(e) => setRole(c.header, e.target.value)}
                className={cn(
                  "h-8 shrink-0 rounded-md border bg-surface-2 px-2 text-sm text-text-primary",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)]",
                  "disabled:cursor-not-allowed disabled:opacity-50",
                  overridden ? "border-primary" : "border-border-default",
                )}
              >
                {(rolesMissing ? [current] : roles).map((r) => (
                  <option key={r} value={r}>
                    {ROLE_LABEL[r] ?? r}
                  </option>
                ))}
              </select>
            </div>
          );
        })}
      </div>
      {!rolesMissing && !pairOk && (
        <p className="text-xs text-warning" role="status">
          응력·변형률(또는 힘·변위) 축 쌍이 없습니다 — 물성을 계산하려면 두 축을 모두 지정하세요.
        </p>
      )}
    </div>
  );
}
