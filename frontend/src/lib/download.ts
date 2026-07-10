// 파일 다운로드 헬퍼 — fetch로 받아 HTTP 에러를 잡고(422 등) Blob으로 저장한다.
// <a href download> 직링크는 에러 응답이 파일로 저장되는 문제가 있어 이 헬퍼로 대체.
import { ApiError } from "../api/client";

/** Content-Disposition에서 파일명 추출(filename* 우선, 없으면 filename). */
function filenameFrom(res: Response, fallback: string): string {
  const cd = res.headers.get("content-disposition") ?? "";
  const star = /filename\*=UTF-8''([^;]+)/i.exec(cd);
  if (star) return decodeURIComponent(star[1]);
  const plain = /filename="?([^";]+)"?/i.exec(cd);
  return plain ? plain[1] : fallback;
}

/**
 * url을 fetch해 성공 시 브라우저 다운로드를 트리거한다.
 * 실패 시 ApiError를 던진다 — 호출부에서 toast.error 처리.
 */
export async function downloadFile(url: string, fallbackName = "download"): Promise<void> {
  const res = await fetch(url);
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      if (body && typeof body.detail === "string") detail = body.detail;
    } catch {
      // 본문이 JSON이 아니면 statusText 유지.
    }
    throw new ApiError(res.status, detail);
  }
  const blob = await res.blob();
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filenameFrom(res, fallbackName);
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(a.href);
}

/** 백엔드 영어 detail → 사용자용 한국어 메시지. 매핑 없으면 원문 유지. */
export function errorMessage(e: unknown): string {
  if (e instanceof ApiError) {
    const d = e.detail;
    if (d.includes("material_code already exists")) return "재료 코드가 이미 존재합니다.";
    if (d.includes("valid Young's modulus required")) return "유효한 영률이 없어 카드를 만들 수 없습니다 — 물성을 다시 계산하세요.";
    if (d.includes("viscoelastic relaxation result required")) return "점탄성 완화 결과가 없어 카드를 만들 수 없습니다.";
    if (d.includes("material not found")) return "재료를 찾을 수 없습니다.";
    if (d.includes("specimen not found")) return "시편을 찾을 수 없습니다.";
    if (d.includes("test not found")) return "시험을 찾을 수 없습니다.";
    if (d.includes("upload exceeds")) return "파일이 업로드 용량 한도를 초과했습니다.";
    if (d.includes("specimen constraint")) return "시편 정보가 제약을 위반했습니다 — 치수·형상을 확인하세요.";
    return d;
  }
  return e instanceof Error ? e.message : "알 수 없는 오류가 발생했습니다.";
}
