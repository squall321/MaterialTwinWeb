// API 호출 캡슐화 — JSON request 헬퍼와 FormData uploadFiles 헬퍼(상대경로 전용).
// 모든 경로는 선행 슬래시 없는 상대경로("api/...")로 호출한다(Vite base:"./" 불변).

/** 백엔드 에러 — status + detail 보존. */
export class ApiError extends Error {
  status: number;
  detail: string;
  constructor(status: number, detail: string) {
    super(`${status} ${detail}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

async function extractError(res: Response): Promise<never> {
  let detail = res.statusText;
  try {
    const body = await res.json();
    if (body && typeof body.detail === "string") detail = body.detail;
    else if (body && body.detail) detail = JSON.stringify(body.detail);
  } catch {
    // 본문이 JSON 이 아니면 statusText 유지.
  }
  throw new ApiError(res.status, detail);
}

/** JSON request — application/json 직렬화/역직렬화. 204 는 undefined 반환. */
export async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) await extractError(res);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/**
 * 멀티파트 업로드 전용 — Content-Type 미지정(브라우저가 boundary 설정).
 * fields 는 추가 form 필드(예: mapping JSON 문자열).
 */
export async function uploadFiles<T>(
  path: string,
  file: File,
  fields?: Record<string, string>,
): Promise<T> {
  const form = new FormData();
  form.append("file", file);
  if (fields) {
    for (const [key, value] of Object.entries(fields)) {
      form.append(key, value);
    }
  }
  const res = await fetch(path, { method: "POST", body: form });
  if (!res.ok) await extractError(res);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}
