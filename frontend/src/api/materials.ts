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
