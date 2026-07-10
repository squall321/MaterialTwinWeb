// 재료 계열별 물성 박스플롯 — E는 로그축(범위 큼), 계열 간 분포 차이를 한눈에.
import * as React from "react";
import * as echarts from "echarts/core";
import { BoxplotChart, ScatterChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { useChartTheme } from "../lib/echarts";

echarts.use([BoxplotChart, ScatterChart, GridComponent, TooltipComponent, CanvasRenderer]);

// 계열 색(Ashby와 일치).
const FAMILY_COLOR: Record<string, string> = {
  steel: "#56B4E9", aluminum: "#E69F00", titanium: "#CC79A7", magnesium: "#009E73",
  nickel: "#F0A92C", copper: "#D55E00", refractory: "#8FA1B3", metal: "#9AA7B8",
};

export type FamilyBox = {
  family: string;
  label: string;
  min: number;
  q1: number;
  median: number;
  q3: number;
  max: number;
  mean: number;
  n: number;
};

export function FamilyBoxPlot({
  boxes,
  unit,
  log,
  height = 260,
}: {
  boxes: FamilyBox[];
  unit: string;
  log?: boolean;
  height?: number;
}) {
  const ref = React.useRef<HTMLDivElement | null>(null);
  const inst = React.useRef<echarts.ECharts | null>(null);
  const T = useChartTheme(); // 테마 토글 시 재렌더(§14.4)

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
    const cats = boxes.map((b) => `${b.label}·${b.n}`);
    // boxplot data: [min, q1, median, q3, max]
    const bdata = boxes.map((b) => [b.min, b.q1, b.median, b.q3, b.max]);
    const meanPts = boxes.map((b, i) => [i, b.mean]);

    inst.current.setOption(
      {
        backgroundColor: "transparent",
        textStyle: { fontFamily: "Inter, sans-serif" },
        grid: { left: 64, right: 18, top: 16, bottom: 44 },
        tooltip: {
          trigger: "item",
          backgroundColor: T.surface2, borderColor: T.border,
          textStyle: { color: T.text1, fontSize: 11 },
          formatter: (p: unknown) => {
            const d = p as { seriesType: string; value: number[]; dataIndex: number };
            if (d.seriesType === "boxplot") {
              const b = boxes[d.dataIndex];
              return `<b>${b.label}</b> (n=${b.n})<br/>` +
                `최대 ${b.max}<br/>Q3 ${b.q3}<br/>중앙 ${b.median}<br/>Q1 ${b.q1}<br/>최소 ${b.min}<br/>` +
                `평균 ${b.mean} ${unit}`;
            }
            return "";
          },
        },
        xAxis: {
          type: "category", data: cats,
          axisLine: { lineStyle: { color: T.axis } },
          axisLabel: { color: T.text2, fontSize: 10, interval: 0, rotate: cats.length > 6 ? 22 : 0 },
          axisTick: { show: false },
        },
        yAxis: {
          type: log ? "log" : "value",
          name: unit, nameTextStyle: { color: T.text3, fontSize: 11 },
          axisLine: { lineStyle: { color: T.axis } },
          axisLabel: { color: T.text2, fontSize: 10 },
          splitLine: { lineStyle: { color: T.grid } },
          scale: true,
        },
        series: [
          {
            type: "boxplot", data: bdata,
            itemStyle: {
              color: "transparent",
              borderColor: (p: unknown) => FAMILY_COLOR[boxes[(p as { dataIndex: number }).dataIndex]?.family] ?? "#9AA7B8",
              borderWidth: 1.6,
            },
            boxWidth: [12, 34],
          },
          {
            type: "scatter", data: meanPts, symbolSize: 6,
            itemStyle: { color: T.text1, opacity: 0.9 },
            tooltip: { show: false },
          },
        ],
      },
      true,
    );
  }, [boxes, unit, log, T]);

  return <div ref={ref} style={{ width: "100%", height }} role="img" aria-label="계열별 물성 분포 박스플롯" />;
}
