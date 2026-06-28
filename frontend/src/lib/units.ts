// 백엔드 SI 값을 표시 단위(MPa/GPa/mm/%)로 변환하는 헬퍼. 저장은 항상 SI.

/** Pa → MPa. */
export function paToMPa(pa: number): number {
  return pa / 1e6;
}

/** Pa → GPa. */
export function paToGPa(pa: number): number {
  return pa / 1e9;
}

/** m → mm. */
export function mToMm(m: number): number {
  return m * 1e3;
}

/** m² → mm². */
export function m2ToMm2(m2: number): number {
  return m2 * 1e6;
}

/** 무차원 비율 → %. */
export function ratioToPercent(ratio: number): number {
  return ratio * 100;
}

/** null/undefined 안전 숫자 포맷(고정 소수). 값 없으면 dash. */
export function fmt(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return value.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}

/** 영률 표시 — Pa → GPa 문자열(단위 제외). */
export function youngsModulusGPa(pa: number | null | undefined): string {
  if (pa === null || pa === undefined) return "—";
  return fmt(paToGPa(pa), 1);
}

/** 응력 표시 — Pa → MPa 문자열(단위 제외). */
export function stressMPa(pa: number | null | undefined): string {
  if (pa === null || pa === undefined) return "—";
  return fmt(paToMPa(pa), 1);
}

/** 변형/연신 표시 — 비율 → % 문자열(단위 제외). */
export function elongationPercent(ratio: number | null | undefined): string {
  if (ratio === null || ratio === undefined) return "—";
  return fmt(ratioToPercent(ratio), 1);
}
