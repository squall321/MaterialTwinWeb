// 물성 카탈로그 API 타입·함수 — catalog.py(summary/materials/detail/coverage) 정합.
import { request } from "./client";

export type Facet = { value: string; count: number; materials?: number };

export type CatalogSummary = {
  totals: {
    materials: number;
    values: number;
    sources: number;
    definitions: number;
    covered: number;
    domains: number;
  };
  facets: {
    subsystem: Facet[];
    category: Facet[];
    manufacturer: Facet[];
    material_class: Facet[];
    domain: Facet[];
  };
};

export type CatalogMaterial = {
  id: number;
  name: string;
  material_code: string | null;
  category: string | null;
  n_properties: number;
  domains: string[];
  manufacturer?: string | null;
  grade?: string | null;
  trade_name?: string | null;
  material_class?: string | null;
  process?: string | null;
  subsystem?: string | null;
};

export type PropertySource = {
  title: string | null;
  url: string | null;
  doi: string | null;
  manufacturer: string | null;
  kind: string | null;
  detail: string | null;
};

export type PropertyValueRow = {
  key: string;
  name: string;
  symbol: string | null;
  value: number | null;
  value_text: string | null;
  unit: string | null;
  uncertainty: number | null;
  conditions: Record<string, unknown> | null;
  method: string;
  tier: number;
  standard: string | null;
  notes: string | null;
  source: PropertySource | null;
};

export type CatalogMaterialDetail = {
  id: number;
  name: string;
  material_code: string | null;
  category: string | null;
  description: string | null;
  metadata: Record<string, string | null>;
  attributes: Record<string, unknown>;
  n_values: number;
  domains: Record<string, PropertyValueRow[]>;
};

export type CatalogFilters = {
  q?: string;
  subsystem?: string;
  category?: string;
  manufacturer?: string;
  material_class?: string;
  domain?: string;
  sort?: string;
};

export function getCatalogSummary() {
  return request<CatalogSummary>("api/catalog/summary");
}

export function listCatalogMaterials(f: CatalogFilters = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(f)) if (v) qs.set(k, String(v));
  const s = qs.toString();
  return request<{ items: CatalogMaterial[]; total: number }>(
    `api/catalog/materials${s ? `?${s}` : ""}`,
  );
}

export function getCatalogMaterial(id: number) {
  return request<CatalogMaterialDetail>(`api/catalog/materials/${id}`);
}

export type Coverage = {
  subsystems: string[];
  domains: string[];
  matrix: { subsystem: string; cells: { domain: string; count: number }[] }[];
};

export function getCoverage() {
  return request<Coverage>("api/catalog/coverage");
}

// ── 재료 비교(/compare) — 물성별 대표값 정렬 매트릭스 ──
export type CompareCell = {
  material_id: number;
  value: number | null;
  value_text: string | null;
  unit: string | null;
  tier: number;
  method: string;
  conditions: Record<string, unknown> | null;
  source: PropertySource | null;
  rel?: number;
};

export type CompareProperty = {
  key: string;
  name: string;
  symbol: string | null;
  unit: string | null;
  standard: string | null;
  domain: string;
  present: number;
  numeric: boolean;
  min_material_id: number | null;
  max_material_id: number | null;
  cells: (CompareCell | null)[];
};

export type CompareMaterialMeta = {
  id: number;
  name: string;
  material_code: string | null;
  category: string | null;
  manufacturer?: string | null;
  grade?: string | null;
  trade_name?: string | null;
  material_class?: string | null;
  process?: string | null;
  subsystem?: string | null;
};

export type CatalogComparison = {
  materials: CompareMaterialMeta[];
  domains: { domain: string; properties: CompareProperty[] }[];
  n_properties: number;
  n_shared: number;
  rule: string;
};

export function compareMaterials(ids: number[]) {
  return request<CatalogComparison>(`api/catalog/compare?ids=${ids.join(",")}`);
}

// ── Ashby 물성공간 산점도 ──
export type AxisOption = {
  key: string;
  name: string;
  symbol: string | null;
  unit: string | null;
  domain: string;
  n_materials: number;
};

export type AshbyAxis = {
  key: string;
  name: string;
  symbol: string | null;
  unit: string | null;
  domain: string;
};

export type AshbyPoint = {
  material_id: number;
  name: string;
  category: string | null;
  subsystem: string | null;
  manufacturer: string | null;
  material_class: string | null;
  x: number;
  y: number;
};

export type AshbyData = {
  x: AshbyAxis;
  y: AshbyAxis;
  points: AshbyPoint[];
  rule: string;
};

export function getAxes() {
  return request<{ options: AxisOption[] }>("api/catalog/axes");
}

export function getAshby(x: string, y: string) {
  return request<AshbyData>(`api/catalog/ashby?x=${encodeURIComponent(x)}&y=${encodeURIComponent(y)}`);
}
