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
  /** prop 필터를 걸었을 때만 실린다 — 그 물성의 대표값. */
  prop_value?: number | null;
  /** 목록은 **수만** 낸다(값은 상세·비교에서). 후보 수와 동률 여부. */
  prop_candidates?: number;
  prop_tie?: boolean;
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

// ── 대표값의 "다른 후보" (51차 MB) ──────────────────────────────────────────
// 선택기는 (재료,물성키)당 한 행만 낸다. 라이브 41,368행에서 후보가 둘 이상인 쌍이 6,330개이고
// 그중 3,642쌍은 **순위가 같은데 값이 1% 넘게 다르다**. 그 사실을 화면이 감추면 안 된다.

/** 대표값과 이 후보의 순위가 **처음 어긋난 자리**. `load_order` 면 순위가 못 갈랐다는 뜻이다. */
export type SeparatedBy =
  | "state"
  | "tier"
  | "numeric"
  | "temperature"
  | "wavelength"
  | "n_conditions"
  | "load_order";

/** 대표값과 순위가 완전히 같은데 값이 다른 후보가 있을 때만 붙는다. */
export type RepTie = {
  /**
   * `condition_axis` 조건이 다른데 선택기에 그 축이 없다(라이브 3,213건) ·
   * `multi_term` 한 키에 여러 항이 산다(394건) ·
   * `indistinguishable` 구분할 조건조차 없다(35건) — **이때만 "적재 순서" 가 맞는 말이다.**
   */
  kind: "condition_axis" | "multi_term" | "indistinguishable";
  n_tied: number;
  max_rel_diff: number | null;
  condition_keys: string[];
};

export type ConditionDiff = Record<string, { rep: unknown; alt: unknown }>;

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
  /** 이 행이 목록·비교·Ashby·DYNA 카드가 쓰는 그 값인가. */
  representative: boolean;
  /** 이 재료·물성키의 후보 행 수(자기 자신 포함). */
  n_candidates: number;
  /** 대표행에만 붙는다 — 형제 행마다 반복하면 소음이 된다. */
  tie: RepTie | null;
  /** 진 행에만 붙는다. 조건 차이는 응답에 이미 전 행이 있으므로 화면이 직접 견준다. */
  separated_by: SeparatedBy | null;
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
  /** 후보가 둘 이상인 물성 수 · 그중 동률로 갈린 수. */
  alternatives: { keys: number; ties: number };
};

export type CatalogFilters = {
  q?: string;
  subsystem?: string;
  category?: string;
  manufacturer?: string;
  material_class?: string;
  domain?: string;
  /** 물성 값 범위 검색 — 이름에 없는 조건(유리섬유 함량 등)을 거를 때 쓴다. */
  prop?: string;
  prop_min?: number;
  prop_max?: number;
  sort?: string;
};

export function getCatalogSummary() {
  return request<CatalogSummary>("api/catalog/summary");
}

export function listCatalogMaterials(f: CatalogFilters = {}) {
  const qs = new URLSearchParams();
  for (const [k, v] of Object.entries(f))
    if (v !== undefined && v !== null && v !== "") qs.set(k, String(v));
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
  /** 후보가 둘 이상일 때만 붙는다. 없으면 1개로 본다. */
  n_candidates?: number;
  /** 값이 실질적으로 다른 후보만, 최대 2건. */
  alternatives?: CompareAlternative[];
  tie?: RepTie;
};

/** 비교표의 진 후보 한 건. 조건 dict 전체가 아니라 **다른 칸만** 실린다. */
export type CompareAlternative = {
  value: number | null;
  value_text: string | null;
  unit: string | null;
  tier: number;
  method: string;
  separated_by: SeparatedBy;
  condition_diff: ConditionDiff;
  source_title: string | null;
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
  /** 점이 738개라 후보가 둘 이상일 때만 붙는다. 없으면 1개·동률 없음. */
  x_candidates?: number;
  y_candidates?: number;
  x_tie?: boolean;
  y_tie?: boolean;
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

// ── LS-DYNA 카드 내보내기(붙여넣기 → 매칭 선택 → 덱 생성) ──
export type DynaCandidate = {
  material_id: number;
  name: string;
  score: number;
  matched_by: string;
  manufacturer: string | null;
  grade: string | null;
  category: string | null;
  n_properties: number;
  has_mechanical: boolean;
  has_thermal: boolean;
};

export type DynaRow = {
  mid: number;
  mid_source: string;
  pids: number[];
  query: string;
  candidates: DynaCandidate[];
  unmatched: boolean;
};

export type DynaMatch = { rows: DynaRow[]; errors: string[]; mid_warnings: string[] };

export type DynaDeck = {
  keyword: string;
  units: { key: string; label: string; stress: string; density: string };
  card: string;
  materials: { mid: number; material_id: number; name: string; matched_by: string;
               query: string; mid_source?: string; pids?: number[]; cards: string[] }[];
  parts: { pid: number; mid: number; lcid: number; material: string; cte: number }[];
  n_materials: number;
  skipped: { material: string; card: string; reason: string }[];
  resolution_errors: string[];
  mid_warnings?: string[];
};

export function matchDynaRows(rows: string, mid_start = 1) {
  return request<DynaMatch>("api/catalog/dyna/match", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rows, mid_start }),
  });
}

export function buildDynaDeck(
  picks: { mid: number; material_id: number; pids?: number[] }[],
  card: string,
  units: string,
) {
  return request<DynaDeck>("api/catalog/dyna/build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ picks, card, units }),
  });
}

// 재료의 σ-ε 곡선 — 인장시험이 있으면 실측, 없으면 스칼라에서 합성한 곡선.
export type MaterialCurve = {
  material_id: number;
  name: string;
  kind: "measured" | "synthetic";
  test_id: number | null;
  strain: number[];
  stress_pa: number[];
  model: string;
  note: string | null;
  inconsistent?: boolean;
  inputs?: Record<string, number | null> | null;
  sources?: Record<string, string> | null;
  provenance?: string | null;
};

export function getMaterialCurve(id: number, nPoints = 80) {
  return request<MaterialCurve>(`api/catalog/materials/${id}/curve?n_points=${nPoints}`);
}
