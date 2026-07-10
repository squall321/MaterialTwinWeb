// 구성방정식 피팅 패널(§6.3) — Hollomon/Swift/Voce/JC 피팅 계산·표시 + LS-DYNA 카드 export.
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Sigma, Download, Loader2, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import {
  computeFits, getFits, cardUrl,
  UNIT_SYSTEMS, DEFAULT_UNITS, type UnitSystemKey, type Fit,
} from "../api/tests";
import { downloadFile, errorMessage } from "../lib/download";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";
import { Skeleton } from "./ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";

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
  const [units, setUnits] = useState<UnitSystemKey>(DEFAULT_UNITS);
  const [downloading, setDownloading] = useState(false);
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
    onError: (e) => toast.error(errorMessage(e)),
  });

  const download = async (model: "piecewise" | "johnson_cook") => {
    setDownloading(true);
    try {
      await downloadFile(cardUrl(testId, units, model), `test_${testId}.k`);
    } catch (e) {
      toast.error(errorMessage(e));
    } finally {
      setDownloading(false);
    }
  };

  const fits = fitsQ.data?.fits ?? [];
  const fitted = fits.filter((f) => f.params);
  const cardHint = hasProperties ? undefined : "물성 계산 후 다운로드할 수 있습니다";

  return (
    <Card className="overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle px-4 py-3">
        <p className="text-overline">구성방정식 피팅</p>
        <div className="flex flex-wrap items-center gap-2">
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
          <Select value={units} onValueChange={(v) => setUnits(v as UnitSystemKey)}>
            <SelectTrigger className="h-8 w-auto gap-1.5 text-xs" aria-label="단위계">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {UNIT_SYSTEMS.map((u) => (
                <SelectItem key={u.key} value={u.key} className="text-xs">
                  {u.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="ghost"
            size="sm"
            disabled={!hasProperties || downloading}
            title={cardHint}
            onClick={() => download("piecewise")}
          >
            <Download className="size-4" />
            *MAT_024
          </Button>
          <Button
            variant="ghost"
            size="sm"
            disabled={!hasProperties || downloading}
            title={cardHint}
            onClick={() => download("johnson_cook")}
          >
            <Download className="size-4" />
            Johnson-Cook
          </Button>
        </div>
      </div>

      {fitsQ.isPending ? (
        <div className="flex flex-col gap-2 px-4 py-4">
          <Skeleton className="h-5 w-full" />
          <Skeleton className="h-5 w-4/5" />
          <Skeleton className="h-5 w-3/5" />
        </div>
      ) : fitsQ.isError ? (
        <div className="flex items-center justify-center gap-3 px-4 py-6 text-sm text-text-tertiary">
          피팅 정보를 불러오지 못했습니다.
          <Button variant="ghost" size="sm" onClick={() => fitsQ.refetch()}>
            <RefreshCw className="size-3.5" />
            다시 시도
          </Button>
        </div>
      ) : fitted.length === 0 ? (
        <div className="px-4 py-6 text-center text-sm text-text-tertiary">
          아직 피팅이 없습니다. "피팅 계산"으로 Hollomon·Swift·Voce·Johnson-Cook 피팅을 실행하세요.
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
