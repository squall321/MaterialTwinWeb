// 시험(Test) + 곡선 + 물성 API 타입과 함수 — schemas.py TestOut/PropertiesOut/properties.py 정합.
import { request } from "./client";

export type Test = {
  id: number;
  specimen_id: number;
  test_type: string;
  machine: string | null;
  software: string | null;
  source_format: string | null;
  strain_source: string;
  test_speed_m_s: number | null;
  temperature_k: number | null;
  tested_at: string | null;
  valid: boolean;
  invalid_reason: string | null;
};

export type TestPatch = {
  valid?: boolean | null;
  invalid_reason?: string | null;
};

export type CurveKind = "nominal" | "force_disp" | "true" | "relaxation";

/** Considère 넥킹점(진응력 곡선에만). 값 없으면 strain=null. */
export type Necking = {
  strain: number | null;
  stress: number | null;
  index: number | null;
  reason: string | null;
};

export type Curve = {
  kind: string;
  x_label: string;
  y_label: string;
  n_total: number;
  n_returned: number;
  x: number[];
  y: number[];
  necking?: Necking | null;
};

/** 구성방정식 피팅 1건. params는 모델별 파라미터 dict(SI). */
export type Fit = {
  model: "hollomon" | "swift" | "voce" | "johnson_cook" | string;
  params: Record<string, number> | null;
  r2?: number | null;
  rmse_pa?: number | null;
  n_points?: number | null;
  reason?: string | null;
};

export type Confidence = "high" | "ok" | "low";

export type ProcessingParams = {
  schema_version: number;
  e_range: [number, number];
  offset: number;
  toe: boolean;
  r2: number;
  confidence: Confidence;
  n_points: number;
};

export type Properties = {
  test_id: number;
  youngs_modulus_pa: number | null;
  yield_strength_pa: number | null;
  uts_pa: number | null;
  uniform_elongation: number | null;
  fracture_elongation: number | null;
  reduction_of_area: number | null;
  strain_hardening_n: number | null;
  strength_coeff_k_pa: number | null;
  params: ProcessingParams | Record<string, unknown>;
  extra_metrics: Record<string, unknown> | null;
  computed_at: string;
};

export type ComputePropertiesArgs = {
  e_range?: [number, number] | null;
  offset?: number;
  toe?: boolean;
};

export function getTest(tid: number): Promise<Test> {
  return request<Test>(`api/tests/${tid}`);
}

export function patchTest(tid: number, payload: TestPatch): Promise<Test> {
  return request<Test>(`api/tests/${tid}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function deleteTest(tid: number): Promise<void> {
  return request<void>(`api/tests/${tid}`, { method: "DELETE" });
}

export function listTests(sid: number): Promise<Test[]> {
  return request<Test[]>(`api/specimens/${sid}/tests`);
}

export function getCurve(
  tid: number,
  params?: { kind?: CurveKind; max_points?: number },
): Promise<Curve> {
  const sp = new URLSearchParams();
  if (params?.kind) sp.set("kind", params.kind);
  if (params?.max_points) sp.set("max_points", String(params.max_points));
  const qs = sp.toString();
  return request<Curve>(`api/tests/${tid}/curve${qs ? `?${qs}` : ""}`);
}

/** 풀해상도 CSV 다운로드 URL(상대경로). 브라우저 네비게이션/링크용. */
export function curveCsvUrl(tid: number): string {
  return `api/tests/${tid}/curve.csv`;
}

export function getProperties(tid: number): Promise<Properties> {
  return request<Properties>(`api/tests/${tid}/properties`);
}

export function computeProperties(
  tid: number,
  args?: ComputePropertiesArgs,
): Promise<Properties> {
  return request<Properties>(`api/tests/${tid}/properties:compute`, {
    method: "POST",
    body: JSON.stringify(args ?? {}),
  });
}

/** 구성방정식 피팅 계산(교체). Hollomon/Swift/Voce/JC. */
export function computeFits(tid: number): Promise<{ test_id: number; fits: Fit[] }> {
  return request<{ test_id: number; fits: Fit[] }>(`api/tests/${tid}/fits:compute`, {
    method: "POST",
  });
}

export function getFits(tid: number): Promise<{ test_id: number; fits: Fit[] }> {
  return request<{ test_id: number; fits: Fit[] }>(`api/tests/${tid}/fits`);
}

/** LS-DYNA *MAT_024 카드 다운로드 URL(상대경로). */
export function cardUrl(tid: number): string {
  return `api/tests/${tid}/card.k`;
}

/** LS-DYNA *MAT_VISCOELASTIC 카드 다운로드 URL(점탄성). */
export function viscoCardUrl(tid: number): string {
  return `api/tests/${tid}/viscocard.k`;
}
