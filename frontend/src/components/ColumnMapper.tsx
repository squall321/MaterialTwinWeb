// 수동 컬럼 매핑(§5.2·C5) — sniff 컬럼별 역할을 사용자가 재지정. {header: role} 매핑 산출.
import { ArrowRight, Wand2 } from "lucide-react";
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
  /** backend /api/parsers 의 roles vocabulary. */
  roles: string[];
  /** 현재 매핑 {header: role}. 비어있으면 자동감지값 사용. */
  value: Record<string, string>;
  onChange: (mapping: Record<string, string>) => void;
};

export function ColumnMapper({ columns, roles, value, onChange }: Props) {
  // 각 컬럼의 현재 역할: 매핑 오버라이드 우선, 없으면 감지값.
  const roleOf = (c: SniffColumn) => value[c.header] ?? c.role;

  const setRole = (header: string, role: string) => {
    onChange({ ...value, [header]: role });
  };

  return (
    <div className="flex flex-col gap-3">
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
                onChange={(e) => setRole(c.header, e.target.value)}
                className={cn(
                  "h-8 shrink-0 rounded-md border bg-surface-2 px-2 text-sm text-text-primary",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)]",
                  overridden ? "border-primary" : "border-border-default",
                )}
              >
                {roles.map((r) => (
                  <option key={r} value={r}>
                    {ROLE_LABEL[r] ?? r}
                  </option>
                ))}
              </select>
            </div>
          );
        })}
      </div>
    </div>
  );
}
