// 재료 taxonomy 지식그래프 — root→category→family 노드를 힘-방향 그래프로.
import * as React from "react";
import * as echarts from "echarts/core";
import { GraphChart } from "echarts/charts";
import { TooltipComponent } from "echarts/components";
import { CanvasRenderer } from "echarts/renderers";
import { useChartTheme } from "../lib/echarts";
import type { GraphNode, GraphEdge } from "../api/insights";

echarts.use([GraphChart, TooltipComponent, CanvasRenderer]);

export function TaxonomyGraph({ nodes, edges }: { nodes: GraphNode[]; edges: GraphEdge[] }) {
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
    // 노드 타입별 색 — 테마 토큰에서 파생(root=본문색, category=프라이머리, family=녹색 마커).
    const typeColor: Record<string, string> = {
      root: T.text1,
      category: T.primary,
      family: T.markUts,
    };
    const maxVal = Math.max(...nodes.map((n) => n.value), 1);
    inst.current.setOption(
      {
        backgroundColor: "transparent",
        tooltip: {
          backgroundColor: T.surface2, borderColor: T.border,
          textStyle: { color: T.text1, fontSize: 11 },
          formatter: (p: unknown) => {
            const d = p as { dataType?: string; data: { label?: string; value?: number } };
            return d.dataType === "node" ? `${d.data.label}: ${d.data.value}개` : "";
          },
        },
        series: [
          {
            type: "graph",
            layout: "force",
            roam: true,
            draggable: true,
            force: { repulsion: 240, edgeLength: [40, 120], gravity: 0.12 },
            label: {
              show: true, color: T.text2, fontSize: 11,
              formatter: (p: unknown) => (p as { data: { label: string } }).data.label,
            },
            lineStyle: { color: T.grid, width: 1, curveness: 0.08 },
            emphasis: { focus: "adjacency", lineStyle: { color: T.primary, width: 2 } },
            data: nodes.map((n) => ({
              id: n.id, label: n.label, value: n.value,
              symbolSize: 12 + 34 * Math.sqrt(n.value / maxVal),
              itemStyle: { color: typeColor[n.type] ?? T.text2 },
              category: n.type,
            })),
            links: edges.map((e) => ({ source: e.source, target: e.target })),
          },
        ],
      },
      true,
    );
  }, [nodes, edges, T]);

  return <div ref={ref} style={{ width: "100%", height: 360 }} role="img" aria-label="재료 분류 지식그래프" />;
}
