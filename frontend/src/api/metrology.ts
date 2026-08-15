// 시험장비 API 타입·함수 — metrology.py(summary/instruments/by-property/coverage/catalogs) 정합.
import { request } from "./client";

export type Capability = {
  id: number;
  property_key: string;
  technique: string;
  standard: string | null;
  range_min: number | null;
  range_max: number | null;
  range_unit: string | null;
  resolution: number | null;
  accuracy: string | null;
  temperature_min_k: number | null;
  temperature_max_k: number | null;
  specimen: string | null;
  mapping_confidence: "high" | "medium" | "low";
  source_detail: string | null;
  notes: string | null;
  instrument?: {
    id: number;
    vendor: string;
    model: string;
    category: string;
    doc_path: string | null;
  };
};

export type Instrument = {
  id: number;
  vendor: string;
  model: string;
  category: string;
  technique: string | null;
  description: string | null;
  doc_path: string | null;
  notes: string | null;
  capabilities: Capability[];
};

export type MetrologySummary = {
  instruments: number;
  capabilities: number;
  measurable_properties: number;
  total_properties: number;
  by_category: Record<string, number>;
  by_vendor: Record<string, number>;
};

export type ByProperty = {
  property: {
    key: string;
    name: string;
    domain: string;
    si_unit: string | null;
    test_standard: string | null;
    condition_axes: string[] | null;
  };
  values_in_catalog: number;
  techniques: { technique: string; standards: string[]; instruments: Capability[] }[];
};

export type MetrologyCoverage = {
  measurable: number;
  total: number;
  by_domain: Record<string, { total: number; measurable: number }>;
  /** 잴 수 있는 물성 — 장비 대수 내림차순. */
  covered: {
    key: string;
    name: string;
    domain: string;
    si_unit: string | null;
    instruments: number;
    values_in_catalog: number;
  }[];
  gaps: {
    key: string;
    name: string;
    domain: string;
    si_unit: string | null;
    values_in_catalog: number;
  }[];
};

export const getMetrologySummary = () =>
  request<MetrologySummary>("api/metrology/summary");

export const listInstruments = (p: { category?: string; property_key?: string; q?: string }) => {
  const s = new URLSearchParams();
  if (p.category) s.set("category", p.category);
  if (p.property_key) s.set("property_key", p.property_key);
  if (p.q) s.set("q", p.q);
  const qs = s.toString();
  return request<{ count: number; items: Instrument[] }>(
    `api/metrology/instruments${qs ? `?${qs}` : ""}`,
  );
};

export const getByProperty = (key: string) =>
  request<ByProperty>(`api/metrology/by-property/${key}`);

export const getMetrologyCoverage = () =>
  request<MetrologyCoverage>("api/metrology/coverage");

// 장비 분류 라벨 — 카탈로그 디렉터리 어휘와 같다.
export const CATEGORY_LABEL: Record<string, string> = {
  thermal: "열",
  mechanical: "기계",
  surface: "표면·형상",
  chemical: "화학·조성",
  particle: "입자·유변",
  optical: "광학",
  electrical: "전기",
  ndt: "비파괴",
  reliability: "신뢰성",
};

/** 켈빈 → 섭씨 표기. 없으면 null. */
export function kToC(k: number | null): number | null {
  return k === null || k === undefined ? null : Math.round((k - 273.15) * 10) / 10;
}

/** 측정범위 문자열. **상한만 인쇄된 경우를 그대로 보인다** — 하한을 지어내지 않는다. */
export function rangeText(c: Capability): string | null {
  const { range_min: lo, range_max: hi, range_unit: u } = c;
  if (lo === null && hi === null) return null;
  if (lo !== null && hi !== null) return `${fmt(lo)} ~ ${fmt(hi)} ${u ?? ""}`.trim();
  if (hi !== null) return `≤ ${fmt(hi)} ${u ?? ""}`.trim();
  return `≥ ${fmt(lo as number)} ${u ?? ""}`.trim();
}

function fmt(n: number): string {
  if (n === 0) return "0";
  const a = Math.abs(n);
  if (a >= 1e4 || a < 1e-3) return n.toExponential(2).replace("e", "×10^");
  return String(Number(n.toPrecision(4)));
}
