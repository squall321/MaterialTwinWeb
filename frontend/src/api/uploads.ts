// 업로드 API 타입과 함수 — uploads.py sniff/parsers/시편적재/수동매핑 정합. FormData 전용 헬퍼 사용.
import { request, uploadFiles } from "./client";

export type IssueLevel = "INFO" | "WARN" | "ERROR" | string;

export type Issue = {
  level: IssueLevel;
  code: string;
  message: string;
};

export type SniffColumn = {
  index: number;
  header: string;
  role: string;
  unit: string | null;
  confidence: number;
};

export type SniffSpecimen = {
  n_rows?: number;
  columns?: SniffColumn[];
  meta?: Record<string, unknown>;
};

export type SniffResult = {
  filename: string;
  parser: string;
  confidence: number;
  needs_manual_mapping: boolean;
  raw_preview: string;
  issues: Issue[];
  specimen: SniffSpecimen;
};

export type ParsersInfo = {
  parsers: { name: string }[];
  roles: string[];
};

export type IngestResult = {
  test_id: number;
  valid: boolean;
  invalid_reason: string | null;
  computed: boolean;
  issues: Issue[];
};

/** 파일을 파싱만 해보고 파서 후보/신뢰도/컬럼 매핑 반환(미커밋). */
export function sniff(file: File): Promise<SniffResult> {
  return uploadFiles<SniffResult>("api/uploads/sniff", file);
}

/** 등록 파서 목록 + 역할 vocabulary. */
export function getParsers(): Promise<ParsersInfo> {
  return request<ParsersInfo>("api/parsers");
}

/** 시편에 원본 업로드 → 파싱 → 적재. test 는 항상 생성. */
export function uploadToSpecimen(
  sid: number,
  file: File,
): Promise<IngestResult> {
  return uploadFiles<IngestResult>(`api/specimens/${sid}/uploads`, file);
}

/** 수동 매핑 재파싱. mapping 은 {header: role} 객체. */
export function remapUpload(
  tid: number,
  file: File,
  mapping: Record<string, string>,
): Promise<IngestResult> {
  return uploadFiles<IngestResult>(`api/uploads/${tid}/mapping`, file, {
    mapping: JSON.stringify(mapping),
  });
}
