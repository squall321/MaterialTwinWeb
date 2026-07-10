// 영률 회귀구간 선택(§14.5.1). brush [ε1,ε2] → 클라 실시간 회귀 프리뷰(E·R²·n), 확정 시 computeProperties 콜백.
// 저장은 서버 확정값(★E1) — 여기선 프리뷰만. 키보드 대안: ε 숫자입력 2칸.
import * as React from "react";
import { Check } from "lucide-react";
import { cn } from "../lib/utils";
import { linearRegression, r2Confidence } from "../lib/regression";

type Props = {
  /** 활성 시편 곡선(SI). x=strain, y=stress(Pa). */
  x: number[];
  y: number[];
  /** brush 로 외부에서 선택된 구간([ε1,ε2]). 없으면 기본 0.0005~0.0025. */
  range: [number, number] | null;
  /** ε 숫자입력 변경 시(brush 와 양방향). */
  onRangeChange: (range: [number, number]) => void;
  /** 확정 — 서버 재계산. 진행 중 disabled. */
  onCommit: (range: [number, number]) => void;
  committing?: boolean;
  className?: string;
};

const DEFAULT_RANGE: [number, number] = [0.0005, 0.0025];

export function RegressionRangePicker({
  x,
  y,
  range,
  onRangeChange,
  onCommit,
  committing,
  className,
}: Props) {
  const active = range ?? DEFAULT_RANGE;
  const [lo, hi] = active[0] <= active[1] ? active : [active[1], active[0]];

  // 라이브 회귀 — 구간/곡선 변경 시 재계산(<2ms, 메모).
  const reg = React.useMemo(() => linearRegression(x, y, lo, hi), [x, y, lo, hi]);

  const eGPa = reg ? reg.slope / 1e9 : null;
  const conf = reg ? r2Confidence(reg.r2) : null;
  // R² 색 보간(§14.5.1: ≥0.99 accent / 0.97~0.99 primary / <0.97 warning).
  const r2Color =
    reg === null
      ? "var(--text-tertiary)"
      : reg.r2 >= 0.99
        ? "var(--accent)"
        : reg.r2 >= 0.97
          ? "var(--primary)"
          : "var(--warning)";

  const setLo = (v: number) => onRangeChange([v, hi]);
  const setHi = (v: number) => onRangeChange([lo, v]);

  const inputCls =
    "tnum w-24 rounded-sm border border-border-default bg-inset px-2 py-1 text-[0.8125rem] text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)]";

  return (
    <div className={cn("rounded-lg border border-border-default bg-surface p-3", className)}>
      <div className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-text-tertiary">
        Regression
      </div>

      {/* 부동 readout 칩 — 80ms opacity micro-fade(카운트업 없음, §14.5.1). */}
      <div
        className="mt-2 flex items-baseline gap-2 transition-opacity"
        style={{ transitionDuration: "80ms" }}
      >
        <span className="tnum text-[1.625rem] font-medium leading-none" style={{ color: r2Color }}>
          {eGPa === null ? "—" : eGPa.toFixed(1)}
        </span>
        <span className="text-[0.6875rem] text-text-tertiary">GPa · E</span>
      </div>
      <div className="mt-1 tnum text-[0.6875rem] text-text-tertiary">
        {reg ? (
          <>
            R² {reg.r2.toFixed(4)} · n={reg.nPoints}
            {conf === "low" && <span className="ml-1 text-warning">· ⚠ low-confidence</span>}
            {reg.nPoints < 5 && <span className="ml-1 text-warning">· n&lt;5 부족</span>}
          </>
        ) : (
          "구간 내 점이 부족합니다."
        )}
      </div>

      {/* 키보드 대안 — ε 구간 숫자입력 2칸(동일 compute 경로). */}
      <div className="mt-3 flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-[0.6875rem] text-text-tertiary">ε₁</span>
          <input
            type="number"
            step={0.0005}
            min={0}
            value={lo}
            onChange={(e) => setLo(Number(e.target.value))}
            className={inputCls}
            aria-label="회귀 시작 변형률"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-[0.6875rem] text-text-tertiary">ε₂</span>
          <input
            type="number"
            step={0.0005}
            min={0}
            value={hi}
            onChange={(e) => setHi(Number(e.target.value))}
            className={inputCls}
            aria-label="회귀 종료 변형률"
          />
        </label>
        <button
          type="button"
          disabled={!reg || committing}
          onClick={() => onCommit([lo, hi])}
          className={cn(
            "ml-auto inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-[0.8125rem] font-medium text-[var(--accent-muted)] transition-[background,transform] active:scale-[0.97]",
            "hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50",
          )}
          style={{ transitionDuration: "var(--mo-dur-fast)" }}
        >
          <Check className="h-3.5 w-3.5" aria-hidden />
          {committing ? "확정 중…" : "Commit E"}
        </button>
      </div>
    </div>
  );
}
