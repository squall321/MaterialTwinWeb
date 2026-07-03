// 재료(Material) API 타입과 함수 — schemas.py MaterialOut/MaterialIn/MaterialPatch 정합.
import { request } from "./client";

export type Material = {
  id: number;
  name: string;
  material_code: string | null;
  category: string | null;
  description: string | null;
  attributes: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type MaterialIn = {
  name: string;
  material_code?: string | null;
  category?: string | null;
  description?: string | null;
  attributes?: Record<string, unknown>;
};

export type MaterialPatch = Partial<MaterialIn>;

export type MaterialList = {
  items: Material[];
  total: number;
  page: number;
  size: number;
};

export function listMaterials(params?: {
  q?: string;
  page?: number;
  size?: number;
}): Promise<MaterialList> {
  const sp = new URLSearchParams();
  if (params?.q) sp.set("q", params.q);
  if (params?.page) sp.set("page", String(params.page));
  if (params?.size) sp.set("size", String(params.size));
  const qs = sp.toString();
  return request<MaterialList>(`api/materials${qs ? `?${qs}` : ""}`);
}

export function createMaterial(payload: MaterialIn): Promise<Material> {
  return request<Material>("api/materials", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getMaterial(mid: number): Promise<Material> {
  return request<Material>(`api/materials/${mid}`);
}

export function patchMaterial(
  mid: number,
  payload: MaterialPatch,
): Promise<Material> {
  return request<Material>(`api/materials/${mid}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteMaterial(mid: number): Promise<void> {
  return request<void>(`api/materials/${mid}`, { method: "DELETE" });
}

/** 물성 필드별 평균±σ. n은 유효 시편 수. */
export type StatCell = { mean: number | null; std: number | null; n: number };

export type MaterialStats = {
  material_id: number;
  n_specimens: number;
  per_specimen: Array<Record<string, unknown>>;
  stats: Record<string, StatCell>;
};

/** 재료 단위 물성 평균±σ 집계(★C8). */
export function getMaterialStats(mid: number): Promise<MaterialStats> {
  return request<MaterialStats>(`api/materials/${mid}/stats`);
}
