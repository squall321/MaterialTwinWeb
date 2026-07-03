// 구성방정식 피팅 패널(§6.3) — Hollomon/Swift/Voce/JC 피팅 계산·표시 + LS-DYNA 카드 export.
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Sigma, Download, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { computeFits, getFits, cardUrl, type Fit } from "../api/tests";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

// 모델 표시명.
const MODEL_LABEL: Record<string, string> = {
  hollomon: "Hollomon",
  swift: "Swift",
  voce: "Voce",
  johnson_cook: "Johnson-Cook",
};

// 파라미터 표시(Pa→MPa 변환, 무차원은 그대로).
function fmtParam(key: string, v: number): string {
  if (key.endsWith("_pa")) return `${(v / 1e6).toFixed(1)} MPa`;
  return v.toFixed(4);
}

type Props = {
  testId: number;
  /** 물성 계산 완료 여부(카드 export 전제). */
  hasProperties: boolean;
};

export function FitPanel({ testId, hasProperties }: Props) {
  const qc = useQueryClient();
  const fitsQ = useQuery({
    queryKey: ["fits", testId],
    queryFn: () => getFits(testId),
  });

  const computeMut = useMutation({
    mutationFn: () => computeFits(testId),
    onSuccess: (r) => {
      qc.setQueryData(["fits", testId], r);
      const best = r.fits.find((f) => f.params);
      toast.success(
        best ? `피팅 완료 — 최적 ${MODEL_LABEL[best.model] ?? best.model}` : "피팅 완료",
      );
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : "피팅 실패"),
  });

  const fits = fitsQ.data?.fits ?? [];
  const fitted = fits.filter((f) => f.params);

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-border-subtle px-4 py-3">
        <p className="text-overline">구성방정식 피팅</p>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => computeMut.mutate()}
            disabled={computeMut.isPending}
          >
            {computeMut.isPending ? (
              <Loader2 className="size-4 animate-spin" />
            ) : (
              <Sigma className="size-4" />
            )}
            피팅 계산
          </Button>
          <a href={hasProperties ? cardUrl(testId) : undefined} download>
            <Button variant="ghost" size="sm" disabled={!hasProperties}>
              <Download className="size-4" />
              LS-DYNA 카드
            </Button>
          </a>
        </div>
      </div>

      {fitted.length === 0 ? (
        <div className="px-4 py-6 text-center text-sm text-text-tertiary">
          아직 피팅이 없습니다. "피팅 계산"을 눌러 Hollomon·Swift·Voce·Johnson-Cook을 적합하세요.
        </div>
      ) : (
        <div className="flex flex-col divide-y divide-border-subtle">
          {fitted.map((f) => (
            <FitRow key={f.model} fit={f} />
          ))}
        </div>
      )}
    </Card>
  );
}

function FitRow({ fit }: { fit: Fit }) {
  const r2 = fit.r2 ?? 0;
  return (
    <div className="flex items-center gap-3 px-4 py-2.5">
      <span className="w-28 shrink-0 text-sm font-medium text-text-primary">
        {MODEL_LABEL[fit.model] ?? fit.model}
      </span>
      <Badge variant={r2 >= 0.99 ? "success" : r2 >= 0.95 ? "warning" : "default"}>
        R² {r2.toFixed(4)}
      </Badge>
      <span className="tnum min-w-0 flex-1 truncate text-xs text-text-secondary">
        {fit.params
          ? Object.entries(fit.params)
              .map(([k, v]) => `${k}=${fmtParam(k, v)}`)
              .join("  ")
          : "—"}
      </span>
    </div>
  );
}
