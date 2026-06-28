// 시편(Specimen) API 타입과 함수 — schemas.py SpecimenOut/SpecimenIn 정합.
import { request } from "./client";

export type GeometryType = "flat" | "round";

export type Specimen = {
  id: number;
  material_id: number;
  label: string;
  geometry_type: string;
  gauge_length_m: number;
  width_m: number | null;
  thickness_m: number | null;
  diameter_m: number | null;
  area0_m2: number;
  orientation: string | null;
  standard: string | null;
};

export type SpecimenIn = {
  label: string;
  geometry_type: GeometryType;
  gauge_length_m: number;
  width_m?: number | null;
  thickness_m?: number | null;
  diameter_m?: number | null;
  area0_m2?: number | null;
  orientation?: string | null;
  standard?: string | null;
};

export function listSpecimens(mid: number): Promise<Specimen[]> {
  return request<Specimen[]>(`api/materials/${mid}/specimens`);
}

export function createSpecimen(
  mid: number,
  payload: SpecimenIn,
): Promise<Specimen> {
  return request<Specimen>(`api/materials/${mid}/specimens`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getSpecimen(sid: number): Promise<Specimen> {
  return request<Specimen>(`api/specimens/${sid}`);
}

export function patchSpecimen(
  sid: number,
  payload: SpecimenIn,
): Promise<Specimen> {
  return request<Specimen>(`api/specimens/${sid}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteSpecimen(sid: number): Promise<void> {
  return request<void>(`api/specimens/${sid}`, { method: "DELETE" });
}
