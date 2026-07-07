// Ashby 물성공간 차트 — E(GPa) vs UTS(MPa) 로그-로그 산점, 밀도로 버블·계열로 색상.
import * as React from "react";
import { useNavigate } from "@tanstack/react-router";
import * as echarts from "echarts/core";
import { ScatterChart } from "echarts/charts";
import { GridComponent, TooltipComponent, LegendComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { readChartTheme } from "../lib/echarts";
import type { AshbyPoint } from "../api/insights";

echarts.use([ScatterChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer]);

// 계열별 색(Okabe-Ito 계열 재사용). 재료과학 관례 색감.
const FAMILY_COLOR: Record<string, string> = {
  steel: "#56B4E9",
  aluminum: "#E69F00",
  titanium: "#CC79A7",
  magnesium: "#009E73",
  nickel: "#F0A92C",
  copper: "#D55E00",
  refractory: "#8FA1B3",
  metal: "#9AA7B8",
};

const FAMILY_LABEL: Record<string, string> = {
  steel: "강 (Steel)",
  aluminum: "알루미늄",
  titanium: "티탄",
  magnesium: "마그네슘",
  nickel: "니켈합금",
  copper: "동합금",
  refractory: "내화금속",
  metal: "기타 금속",
};

export function AshbyChart({ points, families }: { points: AshbyPoint[]; families: string[] }) {
  const ref = React.useRef<HTMLDivElement | null>(null);
  const inst = React.useRef<echarts.ECharts | null>(null);
  const navigate = useNavigate();

  React.useEffect(() => {
    if (!ref.current) return;
    const chart = echarts.init(ref.current, undefined, { renderer: "canvas" });
    inst.current = chart;
    chart.on("click", (p: unknown) => {
      const d = (p as { data?: { id?: number } }).data;
      if (d?.id) navigate({ to: "/materials/$id", params: { id: String(d.id) } });
    });
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(ref.current);
    return () => {
      ro.disconnect();
      chart.dispose();
    };
  }, [navigate]);

  React.useEffect(() => {
    if (!inst.current) return;
    const T = readChartTheme();
    const densities = points.map((p) => p.density ?? 3).filter(Boolean);
    const dMin = Math.min(...densities, 1);
    const dMax = Math.max(...densities, 20);
    const bubble = (d: number | null) => {
      const v = d ?? 3;
      return 8 + 22 * Math.sqrt((v - dMin) / (dMax - dMin + 1e-6));
    };

    const series = families.map((fam) => ({
      name: FAMILY_LABEL[fam] ?? fam,
      type: "scatter" as const,
      data: points
        .filter((p) => p.family === fam)
        .map((p) => ({
          value: [p.E_gpa, p.uts_mpa],
          id: p.id,
          name: p.name,
          symbolSize: bubble(p.density),
          extra: p,
        })),
      itemStyle: {
        color: FAMILY_COLOR[fam] ?? "#9AA7B8",
        opacity: 0.82,
        borderColor: "rgba(0,0,0,0.35)",
        borderWidth: 0.5,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: T.text2, borderWidth: 1 } },
    }));

    inst.current.setOption(
      {
        backgroundColor: "transparent",
        textStyle: { fontFamily: "Inter, sans-serif" },
        legend: {
          type: "scroll", top: 4, textStyle: { color: T.text2, fontSize: 11 },
          inactiveColor: T.text3, icon: "circle",
        },
        grid: { left: 62, right: 24, top: 44, bottom: 52 },
        tooltip: {
          backgroundColor: T.surface2, borderColor: T.border,
          textStyle: { color: "#E6EBF2", fontSize: 11 },
          formatter: (p: unknown) => {
            const e = (p as { data: { extra: AshbyPoint } }).data.extra;
            return `<b>${e.name}</b><br/>class: ${e.cls}<br/>` +
              `E = ${e.E_gpa} GPa<br/>UTS = ${e.uts_mpa} MPa<br/>` +
              (e.yield_mpa ? `yield = ${e.yield_mpa} MPa<br/>` : "") +
              (e.density ? `ρ = ${e.density} g/cm³<br/>` : "") +
              `<span style="color:#5E6B7D">클릭 → 상세</span>`;
          },
        },
        xAxis: {
          type: "log", name: "Young's modulus  E (GPa)", nameLocation: "middle", nameGap: 32,
          nameTextStyle: { color: T.text3, fontSize: 12, fontWeight: 500 },
          axisLine: { lineStyle: { color: T.axis } },
          axisLabel: { color: T.text2, fontSize: 10 },
          splitLine: { lineStyle: { color: T.grid } },
          min: 0.05, max: 500,
        },
        yAxis: {
          type: "log", name: "Ultimate tensile strength  σ_UTS (MPa)",
          nameLocation: "middle", nameGap: 44,
          nameTextStyle: { color: T.text3, fontSize: 12, fontWeight: 500 },
          axisLine: { lineStyle: { color: T.axis } },
          axisLabel: { color: T.text2, fontSize: 10 },
          splitLine: { lineStyle: { color: T.grid } },
          min: 20, max: 2000,
        },
        series,
      },
      true,
    );
  }, [points, families]);

  return <div ref={ref} style={{ width: "100%", height: 460 }} />;
}
