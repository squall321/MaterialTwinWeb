// 인사이트 API — 대시보드용 집계(overview·Ashby 물성공간·통계·커버리지 갭).
import { request } from "./client";

export type Overview = {
  total_materials: number;
  total_analyzed: number;
  by_category: Record<string, number>;
  by_class: Record<string, number>;
  by_family: Record<string, number>;
  by_kind: Record<string, number>;
};

export type AshbyPoint = {
  name: string;
  id: number;
  cls: string;
  family: string;
  E_gpa: number;
  uts_mpa: number;
  yield_mpa: number | null;
  density: number | null;
  elong_pct: number | null;
  spec_strength: number | null;
  spec_stiffness: number | null;
  test_id: number;
};

export type PropertySpace = { points: AshbyPoint[]; families: string[] };

export type StatCell = {
  unit: string;
  n: number;
  min: number;
  max: number;
  mean: number;
  median: number;
  hist: number[];
  edges: number[];
};

export type PropertyStats = {
  E_gpa: StatCell | null;
  uts_mpa: StatCell | null;
  yield_mpa: StatCell | null;
  elong_pct: StatCell | null;
  viscoelastic_count: number;
};

export type FamilyBoxData = {
  family: string; label: string;
  min: number; q1: number; median: number; q3: number; max: number; mean: number; n: number;
};
export type MetricBoxes = { key: string; label: string; unit: string; log_scale: boolean; boxes: FamilyBoxData[] };
export type AutoInsight = { metric: string; unit: string; leader: string; value: number; why: string; runner_up: string };
export type FamilyStats = {
  families: { key: string; label: string; n: number }[];
  metrics: MetricBoxes[];
  insights: AutoInsight[];
};

export type CoverageRow = { group: string; family: string; count: number; status: "rich" | "sparse" | "missing" };
export type GraphNode = { id: string; label: string; type: string; value: number };
export type GraphEdge = { source: string; target: string };
export type Coverage = { coverage: CoverageRow[]; graph: { nodes: GraphNode[]; edges: GraphEdge[] } };

export const insightsApi = {
  overview: () => request<Overview>("api/insights/overview"),
  propertySpace: () => request<PropertySpace>("api/insights/property-space"),
  propertyStats: () => request<PropertyStats>("api/insights/property-stats"),
  coverage: () => request<Coverage>("api/insights/coverage"),
  familyStats: () => request<FamilyStats>("api/insights/family-stats"),
};
