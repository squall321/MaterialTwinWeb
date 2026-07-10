// ECharts core+line 전용 모듈 등록 + CSS변수 테마 브리지(§14.4). 필요한 컴포넌트만 import.
import * as React from "react";
import * as echarts from "echarts/core";
import { LineChart } from "echarts/charts";
import {
  GridComponent,
  TooltipComponent,
  AxisPointerComponent,
  MarkLineComponent,
  MarkPointComponent,
  DataZoomComponent,
  BrushComponent,
} from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";

echarts.use([
  LineChart,
  GridComponent,
  TooltipComponent,
  AxisPointerComponent,
  MarkLineComponent,
  MarkPointComponent,
  DataZoomComponent,
  BrushComponent,
  CanvasRenderer,
]);

export { echarts };

/** :root 의 CSS 변수 1개를 읽어 trim. ECharts canvas 는 CSS변수를 못 읽으므로 런타임 주입에 사용. */
export function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

/** 차트에 주입할 테마 색 묶음(§14.4 테마 브리지). data-theme 변경 시 재호출해 setOption. */
export function readChartTheme() {
  return {
    inset: cssVar("--bg-inset"),
    grid: cssVar("--chart-grid"),
    gridMinor: cssVar("--chart-grid-minor"),
    axis: cssVar("--chart-axis"),
    text1: cssVar("--text-primary"),
    text2: cssVar("--text-secondary"),
    text3: cssVar("--text-tertiary"),
    primary: cssVar("--primary"),
    primaryHover: cssVar("--primary-hover"),
    crosshair: cssVar("--chart-crosshair"),
    surface2: cssVar("--bg-surface-2"),
    border: cssVar("--border-default"),
    markUts: cssVar("--chart-marker-uts"),
    markYield: cssVar("--chart-marker-yield"),
    regression: cssVar("--chart-regression"),
    brushFill: cssVar("--chart-brush-fill"),
    brushStroke: cssVar("--chart-brush-stroke"),
    toeGhost: cssVar("--chart-toe-ghost"),
    series: Array.from({ length: 8 }, (_, i) => cssVar(`--chart-${i + 1}`)),
  };
}

export type ChartTheme = ReturnType<typeof readChartTheme>;

/** 문서 루트 data-theme/클래스 변경을 감지해 최신 차트 테마를 돌려주는 공용 훅(§14.4). setOption effect 의존성에 넣으면 토글 시 재렌더된다. */
export function useChartTheme(): ChartTheme {
  const [theme, setTheme] = React.useState<ChartTheme>(readChartTheme);
  React.useEffect(() => {
    const mo = new MutationObserver(() => setTheme(readChartTheme()));
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });
    return () => mo.disconnect();
  }, []);
  return theme;
}

/** prefers-reduced-motion 가드 — ECharts animation 비활성 판단용(§14.7). */
export function reducedMotion(): boolean {
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}
