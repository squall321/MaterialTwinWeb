// 응력-변형률 차트(ECharts core+line, §14.4). 다중 시편 오버레이·markPoint(UTS/Rp0.2)·markLine(회귀선)·brush 영률 구간 선택.
import * as React from "react";
import { echarts, readChartTheme, reducedMotion, type ChartTheme } from "../lib/echarts";
import { paToMPa } from "../lib/units";

/** 한 시편 곡선 + (활성 시편이면) 서버 확정 마커/회귀선 좌표(SI). */
export type ChartSeries = {
  testId: number;
  name: string;
  /** strain(무차원) 오름차순. */
  x: number[];
  /** stress(Pa). */
  y: number[];
  active?: boolean; // 활성 시편에만 markPoint/markLine 표시(레전드 토글)
  visible?: boolean; // false 면 곡선 숨김
  markers?: ChartMarkers; // 활성 시편의 서버 확정 물성 좌표
};

/** 서버 확정 물성에서 파생한 마커/회귀 좌표(argmax 금지 — 서버 스칼라 기반). */
export type ChartMarkers = {
  uts?: { strain: number; stressPa: number } | null; // Rm 좌표
  yield?: { strain: number; stressPa: number } | null; // Rp0.2 좌표
  necking?: { strain: number; stressPa: number } | null; // Considère 넥킹점(진곡선)
  regression?: { e1: number; e2: number; ePa: number; intercept: number; r2: number } | null;
  toeIntercept?: number | null; // toe 보정 전 절편(고스트 외삽 표시용, strain)
};

type Props = {
  series: ChartSeries[];
  /** brush 로 [ε1,ε2] 선택 시 호출(없으면 brush 비활성 표시). */
  onRangeSelect?: (range: [number, number]) => void;
  height?: number;
};

/** [ε,σMPa] 쌍 배열로 변환(ECharts data). */
function toPairs(x: number[], y: number[]): [number, number][] {
  const out: [number, number][] = new Array(x.length);
  for (let i = 0; i < x.length; i++) out[i] = [x[i], paToMPa(y[i])];
  return out;
}

function buildOption(series: ChartSeries[], T: ChartTheme, anim: boolean): echarts.EChartsCoreOption {
  const numCss = "'tnum' 1,'cv01' 1,'cv02' 1";

  const lineSeries = series
    .filter((s) => s.visible !== false)
    .map((s, idx) => {
      const color = T.series[idx % 8];
      const dash = idx >= 8 ? ([6, 4] as number[]) : undefined; // 8개 초과 시 dash 2차 분리
      const m = s.active ? s.markers : undefined;

      const base: Record<string, unknown> = {
        name: s.name,
        type: "line",
        data: toPairs(s.x, s.y),
        showSymbol: false,
        smooth: false, // 평활 금지(진짜 데이터)
        sampling: "lttb",
        large: true,
        largeThreshold: 2000,
        lineStyle: { color, width: 1.75, cap: "round", join: "round", type: dash ?? "solid" },
        emphasis: { focus: "series", lineStyle: { width: 2.25 } },
      };

      if (m?.regression) {
        const { e1, e2, ePa, intercept, r2 } = m.regression;
        const p0: [number, number] = [e1, paToMPa(ePa * e1 + intercept)];
        const p1: [number, number] = [e2, paToMPa(ePa * e2 + intercept)];
        base.markLine = {
          silent: true,
          symbol: "none",
          lineStyle: { color: T.regression, width: 1.25, type: [5, 4], opacity: 0.9 },
          label: {
            show: true,
            position: "insideEndTop",
            color: T.primaryHover,
            fontSize: 11,
            fontWeight: 500,
            formatter: `E ${(ePa / 1e9).toFixed(1)} GPa · R² ${r2.toFixed(4)}`,
          },
          data: [[{ coord: p0 }, { coord: p1 }]],
        };
      }

      if (m?.uts || m?.yield || m?.necking) {
        const pts: Record<string, unknown>[] = [];
        if (m.uts) {
          pts.push({
            name: "UTS",
            coord: [m.uts.strain, paToMPa(m.uts.stressPa)],
            symbol: "diamond",
            symbolSize: 9,
            itemStyle: { color: "transparent", borderColor: T.markUts, borderWidth: 1.75 },
            label: { formatter: `Rm ${paToMPa(m.uts.stressPa).toFixed(0)} MPa` },
          });
        }
        if (m.yield) {
          pts.push({
            name: "Rp0.2",
            coord: [m.yield.strain, paToMPa(m.yield.stressPa)],
            symbol: "circle",
            symbolSize: 7,
            itemStyle: { color: T.markYield, borderColor: T.inset, borderWidth: 1.5 },
            label: { formatter: `Rp0.2 ${paToMPa(m.yield.stressPa).toFixed(0)} MPa` },
          });
        }
        if (m.necking) {
          pts.push({
            name: "Necking",
            coord: [m.necking.strain, paToMPa(m.necking.stressPa)],
            symbol: "triangle",
            symbolSize: 9,
            itemStyle: { color: "transparent", borderColor: T.markUts, borderWidth: 1.75 },
            label: { formatter: `넥킹 ${paToMPa(m.necking.stressPa).toFixed(0)} MPa` },
          });
        }
        base.markPoint = {
          symbolSize: 1,
          label: {
            show: true,
            position: "top",
            distance: 8,
            color: "#E6EBF2",
            fontSize: 11,
            fontWeight: 500,
            backgroundColor: T.surface2,
            borderColor: T.border,
            borderWidth: 1,
            padding: [3, 6],
            borderRadius: 4,
          },
          data: pts,
        };
      }
      return base;
    });

  return {
    animation: anim,
    animationDuration: 360,
    animationEasing: "cubicOut",
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, sans-serif" },
    grid: { left: 64, right: 22, top: 22, bottom: 52, containLabel: false },
    xAxis: {
      type: "value",
      name: "Strain  ε",
      nameLocation: "middle",
      nameGap: 32,
      nameTextStyle: { color: T.text3, fontSize: 11, fontWeight: 500 },
      min: 0,
      axisLine: { lineStyle: { color: T.axis, width: 1 } },
      axisTick: { show: true, length: 3, lineStyle: { color: T.axis } },
      axisLabel: { color: T.text2, fontSize: 11, fontWeight: 500, formatter: (v: number) => v.toFixed(3) },
      splitLine: { show: true, lineStyle: { color: T.grid, width: 1, type: [2, 4] } },
      minorTick: { show: true, splitNumber: 2, length: 2, lineStyle: { color: T.axis } },
      minorSplitLine: { show: true, lineStyle: { color: T.gridMinor, width: 1 } },
    },
    yAxis: {
      type: "value",
      name: "Stress  σ  (MPa)",
      nameLocation: "end",
      nameGap: 12,
      nameTextStyle: { color: T.text3, fontSize: 11, fontWeight: 500, align: "left" },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: T.text2, fontSize: 11, fontWeight: 500, formatter: (v: number) => v.toFixed(0), margin: 12 },
      splitLine: { show: true, lineStyle: { color: T.grid, width: 1, type: [2, 4] } },
      minorSplitLine: { show: true, lineStyle: { color: T.gridMinor, width: 1 } },
    },
    axisPointer: {
      show: true,
      link: [{ xAxisIndex: "all" }],
      snap: true,
      triggerTooltip: true,
      lineStyle: { color: T.crosshair, width: 1, type: [3, 3], opacity: 0.55 },
      label: {
        backgroundColor: T.surface2,
        borderColor: T.border,
        borderWidth: 1,
        color: "#E6EBF2",
        fontSize: 11,
        padding: [3, 6],
        borderRadius: 4,
        shadowBlur: 0,
      },
    },
    tooltip: {
      trigger: "axis",
      confine: true,
      backgroundColor: T.surface2,
      borderColor: T.border,
      borderWidth: 1,
      padding: [8, 10],
      extraCssText: "border-radius:6px;box-shadow:0 4px 12px -2px rgba(0,0,0,.55);",
      textStyle: { color: "#E6EBF2", fontSize: 12 },
      formatter: (p: unknown) => {
        const a = (Array.isArray(p) ? p[0] : p) as { data: [number, number]; seriesName: string; color: string };
        const [eps, sig] = a.data;
        return `<div style="font-feature-settings:${numCss};letter-spacing:.01em">
          <span style="display:inline-block;width:7px;height:7px;border-radius:1px;background:${a.color};margin-right:6px"></span>
          <b>${a.seriesName}</b><br/>
          <span style="color:${T.text2}">ε</span>&nbsp;${eps.toFixed(4)}<br/>
          <span style="color:${T.text2}">σ</span>&nbsp;${sig.toFixed(1)} <span style="color:${T.text3}">MPa</span>
        </div>`;
      },
    },
    brush: {
      toolbox: [],
      xAxisIndex: 0,
      brushType: "lineX",
      brushMode: "single",
      transformable: true,
      throttleType: "debounce",
      throttleDelay: 60,
      brushStyle: { color: T.brushFill, borderColor: T.brushStroke, borderWidth: 1 },
      outOfBrush: { colorAlpha: 0.28 },
    },
    dataZoom: [
      { type: "inside", filterMode: "none", zoomOnMouseWheel: "shift" },
      {
        type: "slider",
        height: 16,
        bottom: 6,
        filterMode: "none",
        backgroundColor: "transparent",
        borderColor: T.border,
        fillerColor: T.brushFill,
        handleStyle: { color: T.primary, borderColor: T.primaryHover },
        moveHandleSize: 4,
        dataBackground: { lineStyle: { color: T.axis, width: 1 }, areaStyle: { opacity: 0 } },
        textStyle: { color: T.text3, fontSize: 10 },
      },
    ],
    series: lineSeries,
  };
}

export function StressStrainChart({ series, onRangeSelect, height = 380 }: Props) {
  const elRef = React.useRef<HTMLDivElement | null>(null);
  const chartRef = React.useRef<echarts.ECharts | null>(null);
  // 콜백 ref — 차트 이벤트 핸들러를 1회만 묶고 최신 콜백 참조.
  const onRangeRef = React.useRef(onRangeSelect);
  onRangeRef.current = onRangeSelect;

  // 차트 인스턴스 1회 생성 + ResizeObserver + 테마 MutationObserver.
  React.useEffect(() => {
    if (!elRef.current) return;
    const chart = echarts.init(elRef.current, undefined, { renderer: "canvas" });
    chartRef.current = chart;

    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(elRef.current);

    // brush 선택 → [ε1,ε2] 콜백.
    chart.on("brushEnd", (params: unknown) => {
      const areas = (params as { areas?: { coordRange?: number[] }[] }).areas;
      const range = areas?.[0]?.coordRange;
      if (range && range.length === 2 && onRangeRef.current) {
        onRangeRef.current([range[0], range[1]]);
      }
    });

    // data-theme 변경 시 색 재주입(§14.4).
    const mo = new MutationObserver(() => {
      const T = readChartTheme();
      chart.setOption(buildOption(seriesRef.current, T, !reducedMotion()));
    });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });

    return () => {
      ro.disconnect();
      mo.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  // series 최신값을 MutationObserver 콜백에서 참조하기 위한 ref.
  const seriesRef = React.useRef(series);
  seriesRef.current = series;

  // series 변경 시 옵션 재계산(notMerge 로 잔여 markPoint 제거).
  React.useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    const T = readChartTheme();
    chart.setOption(buildOption(series, T, !reducedMotion()), { notMerge: true });
  }, [series]);

  return <div ref={elRef} style={{ width: "100%", height }} role="img" aria-label="응력-변형률 곡선" />;
}
