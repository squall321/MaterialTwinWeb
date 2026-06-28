// 물성 테이블(§14.3.3 TEST RECORDS). 시편별 행 + 재료단위 평균±σ 요약 행(클라 계산, ★C8). low-confidence 경고 배지(★C1).
import { AlertTriangle } from "lucide-react";
import { Badge } from "./ui/badge";
import { cn } from "../lib/utils";
import { paToGPa, paToMPa, ratioToPercent } from "../lib/units";
import type { Properties } from "../api/tests";

/** 한 시편(대표 test)의 물성 행. */
export type PropertyRow = {
  specimenLabel: string;
  geometry?: string;
  strainSource?: string;
  valid?: boolean;
  props: Properties | null; // 미계산이면 null
};

type Props = {
  rows: PropertyRow[];
  /** ISO(Rp0.2/Rm) ↔ ASTM(YS/UTS) 라벨 토글. 기본 ISO. */
  standard?: "iso" | "astm";
};

/** params.confidence 안전 추출(params 가 raw dict 일 수 있음). */
function confidenceOf(p: Properties | null): "high" | "ok" | "low" | null {
  if (!p) return null;
  const c = (p.params as { confidence?: string } | null)?.confidence;
  return c === "high" || c === "ok" || c === "low" ? c : null;
}

function r2Of(p: Properties | null): number | null {
  if (!p) return null;
  const r = (p.params as { r2?: number } | null)?.r2;
  return typeof r === "number" ? r : null;
}

/** 평균·표본표준편차(n-1). 값 2개 미만이면 std=null. */
function meanStd(values: number[]): { mean: number; std: number | null } | null {
  const v = values.filter((x) => Number.isFinite(x));
  if (v.length === 0) return null;
  const mean = v.reduce((a, b) => a + b, 0) / v.length;
  if (v.length < 2) return { mean, std: null };
  const variance = v.reduce((a, b) => a + (b - mean) ** 2, 0) / (v.length - 1);
  return { mean, std: Math.sqrt(variance) };
}

function num(v: number | null | undefined, digits: number): string {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return v.toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

/** 평균±σ 셀 텍스트. */
function summaryCell(
  rows: PropertyRow[],
  pick: (p: Properties) => number | null,
  conv: (x: number) => number,
  digits: number,
): string {
  const vals = rows
    .map((r) => (r.props ? pick(r.props) : null))
    .filter((x): x is number => x !== null && x !== undefined && !Number.isNaN(x))
    .map(conv);
  const ms = meanStd(vals);
  if (!ms) return "—";
  if (ms.std === null) return num(ms.mean, digits);
  return `${num(ms.mean, digits)} ± ${num(ms.std, digits)}`;
}

export function PropertyTable({ rows, standard = "iso" }: Props) {
  const yieldLabel = standard === "astm" ? "YS" : "Rp0.2";
  const utsLabel = standard === "astm" ? "UTS" : "Rm";

  const headCell = "px-3 py-2 text-left text-[0.6875rem] font-semibold uppercase tracking-[0.08em] text-text-tertiary";
  const numHead = cn(headCell, "text-right");
  const cell = "px-3 py-2.5 text-[0.8125rem] text-text-secondary";
  const numCell = cn(cell, "text-right tnum text-text-primary");

  const hasAny = rows.some((r) => r.props);

  return (
    <div className="overflow-x-auto rounded-lg border border-border-subtle">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-border-default">
            <th className={headCell}>Specimen</th>
            <th className={headCell}>Geom</th>
            <th className={numHead}>E (GPa)</th>
            <th className={numHead}>{yieldLabel} (MPa)</th>
            <th className={numHead}>{utsLabel} (MPa)</th>
            <th className={numHead}>A (%)</th>
            <th className={numHead}>R²</th>
            <th className={headCell}>strain</th>
            <th className={headCell}>valid</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => {
            const conf = confidenceOf(r.props);
            const low = conf === "low";
            return (
              <tr key={`${r.specimenLabel}-${i}`} className="border-b border-border-subtle last:border-0">
                <td className={cn(cell, "text-text-primary font-medium")}>{r.specimenLabel}</td>
                <td className={cell}>{r.geometry ?? "—"}</td>
                <td className={numCell}>{r.props ? num(paToGPa(safe(r.props.youngs_modulus_pa)), 1) : "—"}</td>
                <td className={numCell}>{r.props ? num(paToMPa(safe(r.props.yield_strength_pa)), 0) : "—"}</td>
                <td className={numCell}>{r.props ? num(paToMPa(safe(r.props.uts_pa)), 0) : "—"}</td>
                <td className={numCell}>{r.props ? num(ratioToPercent(safe(r.props.fracture_elongation)), 1) : "—"}</td>
                <td className={numCell}>{num(r2Of(r.props), 4)}</td>
                <td className={cell}>{r.strainSource ?? "—"}</td>
                <td className={cell}>
                  {r.valid === false ? (
                    <Badge variant="danger">invalid</Badge>
                  ) : low ? (
                    <Badge variant="warning">
                      <AlertTriangle className="h-3 w-3" aria-hidden />
                      low-conf
                    </Badge>
                  ) : r.props ? (
                    <span className="text-success" aria-label="유효">
                      ✓
                    </span>
                  ) : (
                    <span className="text-text-tertiary">미계산</span>
                  )}
                </td>
              </tr>
            );
          })}

          {hasAny && rows.length > 1 && (
            <tr className="border-t border-border-default bg-surface-2/40">
              <td className={cn(cell, "text-text-primary font-semibold")} colSpan={2}>
                평균 ± σ
              </td>
              <td className={numCell}>{summaryCell(rows, (p) => p.youngs_modulus_pa, paToGPa, 1)}</td>
              <td className={numCell}>{summaryCell(rows, (p) => p.yield_strength_pa, paToMPa, 0)}</td>
              <td className={numCell}>{summaryCell(rows, (p) => p.uts_pa, paToMPa, 0)}</td>
              <td className={numCell}>{summaryCell(rows, (p) => p.fracture_elongation, ratioToPercent, 1)}</td>
              <td className={numCell}>—</td>
              <td className={cell} colSpan={2} />
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}

/** null 을 NaN 으로 환산해 단위변환 시 "—" 로 흐르게. */
function safe(v: number | null): number {
  return v === null ? NaN : v;
}
