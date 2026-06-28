// brush 구간 [ε1,ε2]에서 클라 실시간 선형회귀(E·R²) — 절편 포함 polyfit(1). 영속은 서버(★E1).
// 단위: 입력 x=strain(무차원), y=stress(Pa). slope(=E)는 Pa.

export type Regression = {
  slope: number; // E (Pa)
  intercept: number; // Pa
  r2: number;
  nPoints: number;
};

/**
 * x,y 배열에서 [lo,hi] 구간 점만 골라 절편 포함 1차 회귀.
 * 점이 2개 미만이면 null(회귀 불가).
 */
export function linearRegression(
  x: number[],
  y: number[],
  lo: number,
  hi: number,
): Regression | null {
  const xs: number[] = [];
  const ys: number[] = [];
  for (let i = 0; i < x.length; i++) {
    if (x[i] >= lo && x[i] <= hi) {
      xs.push(x[i]);
      ys.push(y[i]);
    }
  }
  const n = xs.length;
  if (n < 2) return null;

  let sx = 0;
  let sy = 0;
  for (let i = 0; i < n; i++) {
    sx += xs[i];
    sy += ys[i];
  }
  const mx = sx / n;
  const my = sy / n;

  let sxx = 0;
  let sxy = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - mx;
    sxx += dx * dx;
    sxy += dx * (ys[i] - my);
  }
  if (sxx === 0) return null;

  const slope = sxy / sxx;
  const intercept = my - slope * mx;

  let ssRes = 0;
  let ssTot = 0;
  for (let i = 0; i < n; i++) {
    const pred = slope * xs[i] + intercept;
    ssRes += (ys[i] - pred) ** 2;
    ssTot += (ys[i] - my) ** 2;
  }
  const r2 = ssTot === 0 ? 1 : 1 - ssRes / ssTot;

  return { slope, intercept, r2, nPoints: n };
}

/** R² → confidence 등급(§6.1: ≥0.999 high, ≥0.99 ok, 그 외 low). 거부 아님. */
export function r2Confidence(r2: number): "high" | "ok" | "low" {
  if (r2 >= 0.999) return "high";
  if (r2 >= 0.99) return "ok";
  return "low";
}
