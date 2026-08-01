// Ashby 물성공간(/catalog/ashby) — 물성 X–Y 산점도(로그축·계열별 색). 재료 선택·아웃라이어 탐색용.
import * as React from "react";
import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ScatterChart as ScatterIcon, ArrowLeftRight, Info } from "lucide-react";
import { getAxes, getAshby, type AxisOption, type AshbyData, type AshbyPoint } from "../api/catalog";
import { echarts, useChartTheme, reducedMotion } from "../lib/echarts";
import { domainMeta, subsystemLabel, formatValue, prettyUnit } from "../lib/catalog-ui";
import { ErrorState } from "../components/states/ErrorState";
import { ChartSkeleton } from "../components/states/Skeletons";
import { cn } from "../lib/utils";

type AshbySearch = { x?: string; y?: string; color?: string; logx?: string; logy?: string };

const COLOR_FACETS = [
  { key: "category", label: "분류" },
  { key: "subsystem", label: "서브시스템" },
  { key: "material_class", label: "재료계열" },
  { key: "manufacturer", label: "제조사" },
] as const;

const DEFAULT_X = "physical.density";
const DEFAULT_Y = "mechanical.youngs_modulus";

export function CatalogAshbyScreen() {
  const search = useSearch({ from: "/catalog/ashby" }) as AshbySearch;
  const navigate = useNavigate();
  const set = (patch: Partial<AshbySearch>) =>
    navigate({ to: "/catalog/ashby", search: (p: AshbySearch) => {
      const n = { ...p, ...patch };
      for (const k of Object.keys(n) as (keyof AshbySearch)[]) if (!n[k]) delete n[k];
      return n;
    }, replace: true });

  const x = search.x ?? DEFAULT_X;
  const y = search.y ?? DEFAULT_Y;
  const colorBy = search.color ?? "category";
  const logx = search.logx !== "0";
  const logy = search.logy !== "0";

  const axesQ = useQuery({ queryKey: ["catalog", "axes"], queryFn: getAxes });
  const dataQ = useQuery({ queryKey: ["catalog", "ashby", x, y], queryFn: () => getAshby(x, y) });

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link to="/catalog" className="inline-flex items-center gap-1 text-sm text-text-secondary transition-colors hover:text-text-primary">
          <ChevronLeft className="size-4" /> 물성 카탈로그
        </Link>
      </div>

      <header className="flex flex-col gap-1">
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.08em] text-text-tertiary">
          <ScatterIcon className="size-3.5 text-primary" /> Ashby Property Space
        </div>
        <h1 className="text-2xl font-semibold tracking-[-0.01em] text-text-primary">Ashby 차트</h1>
        <p className="text-sm text-text-secondary">
          두 물성을 축으로 전체 재료를 한 평면에 흩어 봅니다. 재료 선택·아웃라이어 판별에 씁니다.
        </p>
      </header>

      {/* ── 컨트롤 ── */}
      <div className="flex flex-col gap-3 rounded-lg border border-border-subtle bg-surface p-4 md:flex-row md:flex-wrap md:items-end">
        <AxisPicker label="Y축 (세로)" value={y} options={axesQ.data?.options} onChange={(k) => set({ y: k })} />
        <button
          onClick={() => set({ x: y, y: x })}
          title="축 교환"
          className="mb-0.5 hidden size-9 items-center justify-center rounded-md border border-border-default text-text-secondary transition-colors hover:bg-surface-2 hover:text-text-primary md:inline-flex"
        >
          <ArrowLeftRight className="size-4" />
        </button>
        <AxisPicker label="X축 (가로)" value={x} options={axesQ.data?.options} onChange={(k) => set({ x: k })} />

        <div className="flex flex-col gap-1">
          <span className="text-xs font-medium text-text-tertiary">색상 기준</span>
          <select
            value={colorBy}
            onChange={(e) => set({ color: e.target.value })}
            className="h-9 rounded-md border border-border-default bg-surface px-2 text-sm text-text-primary"
          >
            {COLOR_FACETS.map((f) => <option key={f.key} value={f.key}>{f.label}</option>)}
          </select>
        </div>

        <div className="flex items-center gap-3 md:ml-auto md:self-center">
          <label className="inline-flex cursor-pointer items-center gap-1.5 text-xs text-text-secondary">
            <input type="checkbox" checked={logx} onChange={(e) => set({ logx: e.target.checked ? undefined : "0" })} className="accent-[var(--primary)]" />
            X 로그
          </label>
          <label className="inline-flex cursor-pointer items-center gap-1.5 text-xs text-text-secondary">
            <input type="checkbox" checked={logy} onChange={(e) => set({ logy: e.target.checked ? undefined : "0" })} className="accent-[var(--primary)]" />
            Y 로그
          </label>
        </div>
      </div>

      {/* ── 차트 ── */}
      {dataQ.isError ? (
        <ErrorState onRetry={() => dataQ.refetch()} />
      ) : dataQ.isPending ? (
        <ChartSkeleton height={520} />
      ) : dataQ.data ? (
        <AshbyChart data={dataQ.data} colorBy={colorBy} logx={logx} logy={logy} />
      ) : null}
    </div>
  );
}

function AxisPicker({
  label, value, options, onChange,
}: { label: string; value: string; options?: AxisOption[]; onChange: (k: string) => void }) {
  // 도메인별 optgroup(재료 수 내림차순).
  const byDomain = React.useMemo(() => {
    const m = new Map<string, AxisOption[]>();
    for (const o of options ?? []) {
      const arr = m.get(o.domain) ?? [];
      arr.push(o);
      m.set(o.domain, arr);
    }
    return [...m.entries()].sort((a, b) => a[0].localeCompare(b[0]));
  }, [options]);
  return (
    <div className="flex min-w-0 flex-1 flex-col gap-1 md:max-w-[15rem]">
      <span className="text-xs font-medium text-text-tertiary">{label}</span>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 truncate rounded-md border border-border-default bg-surface px-2 text-sm text-text-primary"
      >
        {byDomain.map(([dom, opts]) => (
          <optgroup key={dom} label={domainMeta(dom).label}>
            {opts.map((o) => (
              <option key={o.key} value={o.key}>
                {o.name}{o.unit && o.unit !== "1" ? ` (${prettyUnit(o.unit)})` : ""} · {o.n_materials}종
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}

const FALLBACK = "미분류";

function facetValue(p: AshbyPoint, key: string): string {
  const v = (p as unknown as Record<string, unknown>)[key];
  if (!v) return FALLBACK;
  return key === "subsystem" ? subsystemLabel(String(v)) : String(v);
}

function AshbyChart({
  data, colorBy, logx, logy,
}: { data: AshbyData; colorBy: string; logx: boolean; logy: boolean }) {
  const elRef = React.useRef<HTMLDivElement | null>(null);
  const chartRef = React.useRef<echarts.ECharts | null>(null);
  const navigate = useNavigate();
  const T = useChartTheme();

  // 로그축이면 비양수 좌표는 제외(로그 정의역).
  const points = React.useMemo(
    () => data.points.filter((p) => (!logx || p.x > 0) && (!logy || p.y > 0)),
    [data.points, logx, logy],
  );

  // 색상 그룹(크기 내림차순) → 팔레트 배정.
  const groups = React.useMemo(() => {
    const m = new Map<string, AshbyPoint[]>();
    for (const p of points) {
      const g = facetValue(p, colorBy);
      const arr = m.get(g) ?? [];
      arr.push(p);
      m.set(g, arr);
    }
    return [...m.entries()].sort((a, b) => b[1].length - a[1].length);
  }, [points, colorBy]);

  // 차트 1회 생성 + 리사이즈 + 클릭 네비.
  React.useEffect(() => {
    if (!elRef.current) return;
    const chart = echarts.init(elRef.current, undefined, { renderer: "canvas" });
    chartRef.current = chart;
    const ro = new ResizeObserver(() => chart.resize());
    ro.observe(elRef.current);
    return () => { ro.disconnect(); chart.dispose(); chartRef.current = null; };
  }, []);

  const navRef = React.useRef(navigate);
  navRef.current = navigate;

  React.useEffect(() => {
    const chart = chartRef.current;
    if (!chart) return;
    const palette = T.series;
    const grayed = T.text3;
    const xUnit = data.x.unit && data.x.unit !== "1" ? ` (${prettyUnit(data.x.unit)})` : "";
    const yUnit = data.y.unit && data.y.unit !== "1" ? ` (${prettyUnit(data.y.unit)})` : "";

    const series = groups.map(([g, pts], i) => ({
      name: g,
      type: "scatter" as const,
      data: pts.map((p) => ({ value: [p.x, p.y], mid: p.material_id, nm: p.name })),
      symbolSize: 11,
      itemStyle: {
        color: g === FALLBACK ? grayed : palette[i % palette.length],
        opacity: 0.85,
        borderColor: T.inset,
        borderWidth: 0.6,
      },
      emphasis: { focus: "series", scale: 1.4 },
    }));

    chart.setOption({
      animation: !reducedMotion(),
      grid: { left: 64, right: 20, top: 16, bottom: 78 },
      legend: {
        type: "scroll", bottom: 0, left: "center",
        textStyle: { color: T.text2, fontSize: 11 },
        inactiveColor: T.text3, pageIconColor: T.text2, pageTextStyle: { color: T.text3 },
      },
      tooltip: {
        trigger: "item",
        backgroundColor: T.surface2, borderColor: T.border, borderWidth: 1,
        textStyle: { color: T.text1, fontSize: 12 },
        formatter: (pr: { data: { nm: string; value: [number, number] }; seriesName: string }) => {
          const [vx, vy] = pr.data.value;
          return `<b>${pr.data.nm}</b><br/>${data.y.name}: ${formatValue(vy, data.y.unit)}`
            + `<br/>${data.x.name}: ${formatValue(vx, data.x.unit)}`
            + `<br/><span style="color:${T.text3}">${pr.seriesName}</span>`;
        },
      },
      xAxis: {
        type: logx ? "log" : "value", name: `${data.x.name}${xUnit}`,
        nameLocation: "middle", nameGap: 40, nameTextStyle: { color: T.text2, fontSize: 12 },
        axisLine: { lineStyle: { color: T.axis } }, axisLabel: { color: T.text3, fontSize: 10 },
        splitLine: { lineStyle: { color: T.gridMinor } }, scale: true,
      },
      yAxis: {
        type: logy ? "log" : "value", name: `${data.y.name}${yUnit}`,
        nameLocation: "middle", nameGap: 48, nameTextStyle: { color: T.text2, fontSize: 12 },
        axisLine: { lineStyle: { color: T.axis } }, axisLabel: { color: T.text3, fontSize: 10 },
        splitLine: { lineStyle: { color: T.gridMinor } }, scale: true,
      },
      series,
    }, { notMerge: true });

    chart.off("click");
    chart.on("click", (pr) => {
      const mid = (pr as { data?: { mid?: number } }).data?.mid;
      if (mid) navRef.current({ to: "/catalog/$mid", params: { mid: String(mid) } });
    });
  }, [groups, data, logx, logy, T]);

  return (
    <div className="flex flex-col gap-2">
      <div className="rounded-lg border border-border-subtle bg-surface p-3">
        <div ref={elRef} style={{ height: 520, width: "100%" }} role="img" aria-label="Ashby 산점도" />
      </div>
      <div className="flex flex-wrap items-center justify-between gap-2 px-1 text-[0.6875rem] text-text-tertiary">
        <span className="inline-flex items-center gap-1"><Info className="size-3" /> {data.rule}. 점 클릭 → 재료 상세.</span>
        <span className={cn("tnum", points.length < data.points.length && "text-warning")}>
          {points.length}종 표시{points.length < data.points.length ? ` (로그축 제외 ${data.points.length - points.length})` : ""}
        </span>
      </div>
    </div>
  );
}
