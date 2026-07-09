// 점탄성 재료 뷰 — 완화탄성률 E(t) 로그곡선 + Prony 물성 카드 + MAT_VISCOELASTIC 카드.
import * as React from "react";
import * as echarts from "echarts/core";
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent, MarkLineComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { Download } from "lucide-react";
import {
  getCurve, getProperties, viscoCardUrl,
  UNIT_SYSTEMS, DEFAULT_UNITS, type UnitSystemKey, type Properties,
} from "../api/tests";
import { useQuery } from "@tanstack/react-query";
import { Card } from "./ui/card";
import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { ChartSkeleton } from "./states/Skeletons";
import { readChartTheme, cssVar } from "../lib/echarts";

echarts.use([LineChart, GridComponent, TooltipComponent, MarkLineComponent, CanvasRenderer]);

type Props = { testId: number };

export function ViscoelasticView({ testId }: Props) {
  const [units, setUnits] = React.useState<UnitSystemKey>(DEFAULT_UNITS);
  const curveQ = useQuery({
    queryKey: ["curve", testId, "relaxation"],
    queryFn: () => getCurve(testId, { kind: "relaxation", max_points: 300 }),
  });
  const propsQ = useQuery({
    queryKey: ["properties", testId],
    queryFn: () => getProperties(testId),
    retry: false,
  });

  const vm = viscoMetrics(propsQ.data);

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-4">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-overline">점탄성 완화곡선 · E(t)</p>
          <span className="text-xs text-text-tertiary">시간-완화탄성률 (로그 시간축)</span>
        </div>
        {curveQ.isPending ? (
          <ChartSkeleton />
        ) : curveQ.isError ? (
          <p className="py-8 text-center text-sm text-danger">완화곡선을 불러오지 못했습니다.</p>
        ) : (
          <RelaxationChart x={curveQ.data.x} y={curveQ.data.y} einf={vm?.einfPa ?? null} e0={vm?.e0Pa ?? null} />
        )}
      </Card>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Metric label="순간 탄성률 E₀" value={vm ? mpa(vm.e0Pa) : "—"} unit="MPa" />
        <Metric label="평형 탄성률 E∞" value={vm ? mpa(vm.einfPa) : "—"} unit="MPa" />
        <Metric label="완화시간 τ" value={vm ? sci(vm.tauS) : "—"} unit="s" />
        <Metric label="Prony R²" value={vm?.pronyR2 != null ? vm.pronyR2.toFixed(3) : "—"} />
      </div>

      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle px-4 py-3">
          <p className="text-overline">Prony 급수 · 일반화 Maxwell</p>
          <div className="flex flex-wrap items-center gap-2">
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
            <a href={viscoCardUrl(testId, units)} download>
              <Button variant="ghost" size="sm">
                <Download className="size-4" />
                MAT_VISCOELASTIC 카드
              </Button>
            </a>
          </div>
        </div>
        {vm && vm.terms.length > 0 ? (
          <div className="flex flex-col divide-y divide-border-subtle">
            <div className="flex px-4 py-2 text-xs text-text-tertiary">
              <span className="w-16">항</span>
              <span className="flex-1">Eᵢ (MPa)</span>
              <span className="flex-1">τᵢ (s)</span>
            </div>
            {vm.terms.map(([Ei, tau], i) => (
              <div key={i} className="tnum flex px-4 py-2 text-sm text-text-secondary">
                <span className="w-16 text-text-tertiary">#{i + 1}</span>
                <span className="flex-1 text-text-primary">{(Ei / 1e6).toFixed(3)}</span>
                <span className="flex-1">{sci(tau)}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="px-4 py-6 text-center text-sm text-text-tertiary">Prony 항이 없습니다.</p>
        )}
      </Card>
    </div>
  );
}

function RelaxationChart({
  x, y, einf, e0,
}: {
  x: number[];
  y: number[];
  einf: number | null;
  e0: number | null;
}) {
  const ref = React.useRef<HTMLDivElement | null>(null);
  const inst = React.useRef<echarts.ECharts | null>(null);

  React.useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current, undefined, { renderer: "canvas" });
    inst.current = chart;
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(ref.current);
    return () => {
      ro.disconnect();
      chart.dispose();
    };
  }, []);

  React.useEffect(() => {
    if (!inst.current) return;
    const T = readChartTheme();
    const accent = cssVar("--accent");
    const text1 = cssVar("--text-primary");
    const data = x.map((xi, i) => [xi, y[i] / 1e6]); // Pa→MPa
    const marks: Record<string, unknown>[] = [];
    if (einf != null) marks.push({ yAxis: einf / 1e6, label: { formatter: `E∞ ${(einf / 1e6).toFixed(2)}` } });
    if (e0 != null) marks.push({ yAxis: e0 / 1e6, label: { formatter: `E₀ ${(e0 / 1e6).toFixed(2)}` } });
    inst.current.setOption({
      backgroundColor: "transparent",
      grid: { left: 60, right: 20, top: 18, bottom: 44, containLabel: false },
      textStyle: { fontFamily: "Inter, sans-serif" },
      xAxis: {
        type: "log", name: "time  t (s)", nameLocation: "middle", nameGap: 30,
        nameTextStyle: { color: T.text3, fontSize: 11 },
        axisLine: { lineStyle: { color: T.axis } },
        axisLabel: { color: T.text2, fontSize: 10 },
        splitLine: { lineStyle: { color: T.grid } },
      },
      yAxis: {
        type: "value", name: "E(t) (MPa)",
        nameTextStyle: { color: T.text3, fontSize: 11 },
        axisLine: { lineStyle: { color: T.axis } },
        axisLabel: { color: T.text2, fontSize: 10 },
        splitLine: { lineStyle: { color: T.grid } },
      },
      tooltip: {
        trigger: "axis",
        backgroundColor: T.surface2, borderColor: T.border,
        textStyle: { color: text1, fontSize: 11 },
      },
      series: [
        {
          type: "line", data, showSymbol: false, smooth: false,
          lineStyle: { color: accent, width: 2 },
          areaStyle: { color: accent + "18" },
          markLine: marks.length
            ? {
                silent: true, symbol: "none",
                lineStyle: { color: T.text3, type: "dashed", width: 1 },
                label: { color: T.text2, fontSize: 10, position: "insideEndTop" },
                data: marks,
              }
            : undefined,
        },
      ],
    });
  }, [x, y, einf, e0]);

  return <div ref={ref} style={{ width: "100%", height: 340 }} />;
}

function Metric({ label, value, unit }: { label: string; value: string; unit?: string }) {
  return (
    <Card className="p-3">
      <p className="text-[0.62rem] uppercase tracking-[0.08em] text-text-tertiary">{label}</p>
      <p className="tnum mt-1 text-lg font-semibold text-text-primary">
        {value}
        {unit && <span className="ml-1 text-xs font-normal text-text-tertiary">{unit}</span>}
      </p>
    </Card>
  );
}

// extra_metrics(viscoelastic)에서 지표 추출.
type VM = { e0Pa: number; einfPa: number; tauS: number; pronyR2: number | null; terms: [number, number][] };
function viscoMetrics(p: Properties | undefined): VM | null {
  const em = p?.extra_metrics as Record<string, unknown> | null | undefined;
  if (!em || em.kind !== "viscoelastic") return null;
  const fit = (em.prony_fit ?? {}) as { r2?: number; terms?: [number, number][] };
  return {
    e0Pa: Number(em.E0_pa), einfPa: Number(em.Einf_pa), tauS: Number(em.tau_s),
    pronyR2: fit.r2 ?? null, terms: fit.terms ?? [],
  };
}

function mpa(pa: number): string {
  return (pa / 1e6).toFixed(pa / 1e6 < 1 ? 3 : 1);
}
function sci(v: number): string {
  return v < 0.01 || v >= 1000 ? v.toExponential(2) : v.toFixed(3);
}
