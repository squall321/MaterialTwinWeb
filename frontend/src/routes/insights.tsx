// 재료 인사이트 대시보드(/insights) — Ashby 물성공간·클래스 분포·물성 통계·커버리지 갭·지식그래프.
import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import { Boxes, Sigma, Layers, TriangleAlert, Feather, Dumbbell, Gauge, Zap, Weight } from "lucide-react";
import { insightsApi, type StatCell, type AutoInsight } from "../api/insights";
import { AshbyChart } from "../components/AshbyChart";
import { TaxonomyGraph } from "../components/TaxonomyGraph";
import { FamilyBoxPlot } from "../components/FamilyBoxPlot";
import { Card } from "../components/ui/card";
import { ChartSkeleton } from "../components/states/Skeletons";
import { cn } from "../lib/utils";

export function InsightsScreen() {
  const overviewQ = useQuery({ queryKey: ["insights", "overview"], queryFn: insightsApi.overview });
  const spaceQ = useQuery({ queryKey: ["insights", "space"], queryFn: insightsApi.propertySpace });
  const statsQ = useQuery({ queryKey: ["insights", "stats"], queryFn: insightsApi.propertyStats });
  const coverageQ = useQuery({ queryKey: ["insights", "coverage"], queryFn: insightsApi.coverage });
  const familyQ = useQuery({ queryKey: ["insights", "family"], queryFn: insightsApi.familyStats });

  const ov = overviewQ.data;
  const [boxMetric, setBoxMetric] = React.useState("E_gpa");
  const activeMetric = familyQ.data?.metrics.find((m) => m.key === boxMetric) ?? familyQ.data?.metrics[0];

  return (
    <div className="flex flex-col gap-8">
      <header>
        <p className="text-overline">재료 인사이트</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
          재료 데이터베이스 개요
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-text-secondary">
          시험 데이터에서 도출한 물성으로 재료 공간을 탐색합니다. 클래스별 분포, 물성 통계,
          Ashby 물성공간, 그리고 어떤 계열이 부족한지 커버리지를 한눈에 봅니다.
        </p>
      </header>

      {/* KPI 리드아웃 */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <Kpi icon={<Boxes className="size-4" />} label="총 재료" value={ov?.total_materials ?? "—"} />
        <Kpi icon={<Layers className="size-4" />} label="재료 클래스" value={ov ? Object.keys(ov.by_class).length : "—"} />
        <Kpi icon={<Sigma className="size-4" />} label="탄소성 / 점탄성"
          value={ov ? `${ov.by_kind.elastoplastic ?? 0} / ${ov.by_kind.viscoelastic ?? 0}` : "—"} />
        <Kpi icon={<Boxes className="size-4" />} label="분석 완료" value={ov?.total_analyzed ?? "—"} accent />
      </div>

      {/* Ashby 물성공간 — 히어로 */}
      <Card className="p-4">
        <div className="mb-2 flex items-baseline justify-between">
          <div>
            <p className="text-overline">Ashby 물성공간</p>
            <p className="mt-0.5 text-xs text-text-tertiary">
              E–UTS 로그-로그 · 버블 크기 = 밀도 · 색 = 계열 · 클릭하면 상세로 이동
            </p>
          </div>
        </div>
        {spaceQ.isPending ? (
          <ChartSkeleton height={460} />
        ) : spaceQ.data && spaceQ.data.points.length > 0 ? (
          <AshbyChart points={spaceQ.data.points} families={spaceQ.data.families} />
        ) : (
          <p className="py-16 text-center text-sm text-text-tertiary">물성공간 데이터가 없습니다.</p>
        )}
      </Card>

      {/* 자동 인사이트 — 재료군 비교의 핵심 결론 */}
      {familyQ.data && familyQ.data.insights.length > 0 && (
        <div>
          <p className="text-overline mb-3">핵심 인사이트 · 재료군 비교</p>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {familyQ.data.insights.map((ins) => (
              <InsightCard key={ins.metric} ins={ins} />
            ))}
          </div>
        </div>
      )}

      {/* 재료군별 물성 분포(박스플롯) — E는 log축, 그룹 차이가 직접 보임 */}
      <Card className="p-4">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <p className="text-overline">재료군별 물성 분포</p>
            <p className="mt-0.5 text-xs text-text-tertiary">
              계열별 5수치 박스 · 흰 점 = 평균 {activeMetric?.log_scale && "· 로그축(범위 큼)"}
            </p>
          </div>
          <div className="flex flex-wrap gap-1">
            {familyQ.data?.metrics.map((m) => (
              <button
                key={m.key}
                onClick={() => setBoxMetric(m.key)}
                className={cn(
                  "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                  boxMetric === m.key
                    ? "bg-primary-muted text-[var(--primary-hover)]"
                    : "text-text-tertiary hover:text-text-secondary",
                )}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>
        {activeMetric ? (
          <FamilyBoxPlot boxes={activeMetric.boxes} unit={activeMetric.unit} log={activeMetric.log_scale} height={300} />
        ) : (
          <ChartSkeleton height={300} />
        )}
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 클래스 분포 */}
        <Card className="p-4">
          <p className="text-overline mb-3">재료 클래스 분포</p>
          {ov ? <ClassBars data={ov.by_class} /> : <ChartSkeleton height={280} />}
        </Card>

        {/* 물성 통계 */}
        <Card className="p-4">
          <p className="text-overline mb-3">물성 분포 통계</p>
          {statsQ.data ? (
            <div className="flex flex-col gap-4">
              <StatHistogram title="탄성계수 E" cell={statsQ.data.E_gpa} color="var(--chart-1)" />
              <StatHistogram title="인장강도 UTS" cell={statsQ.data.uts_mpa} color="var(--chart-2)" />
              <StatHistogram title="항복강도 Rp0.2" cell={statsQ.data.yield_mpa} color="var(--accent)" />
            </div>
          ) : (
            <ChartSkeleton height={280} />
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* 지식그래프 */}
        <Card className="p-4">
          <p className="text-overline mb-1">Taxonomy 지식그래프</p>
          <p className="mb-2 text-xs text-text-tertiary">root → 카테고리 → 계열 (드래그·확대 가능)</p>
          {coverageQ.data ? (
            <TaxonomyGraph nodes={coverageQ.data.graph.nodes} edges={coverageQ.data.graph.edges} />
          ) : (
            <ChartSkeleton height={360} />
          )}
        </Card>

        {/* 커버리지 갭 */}
        <Card className="p-4">
          <div className="mb-3 flex items-center gap-2">
            <TriangleAlert className="size-4 text-warning" />
            <p className="text-overline">커버리지 갭 분석</p>
          </div>
          {coverageQ.data ? <CoverageMatrix rows={coverageQ.data.coverage} /> : <ChartSkeleton height={280} />}
        </Card>
      </div>
    </div>
  );
}

// 자동 인사이트 카드 — 지표별 선두 재료군을 결론으로.
const INSIGHT_ICON: Record<string, React.ReactNode> = {
  "비강도(경량 대비 강도)": <Feather className="size-4" />,
  "비강성(경량 대비 강성)": <Gauge className="size-4" />,
  "절대 인장강도": <Dumbbell className="size-4" />,
  "밀도(가벼움)": <Weight className="size-4" />,
  "탄성계수(강성)": <Zap className="size-4" />,
};

function InsightCard({ ins }: { ins: AutoInsight }) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-2 text-primary">
        {INSIGHT_ICON[ins.metric] ?? <Sigma className="size-4" />}
        <span className="text-xs font-medium text-text-secondary">{ins.metric}</span>
      </div>
      <p className="mt-2 text-lg font-semibold text-text-primary">
        {ins.leader} <span className="tnum text-sm font-normal text-accent">1위</span>
      </p>
      <p className="tnum text-sm text-text-secondary">
        {ins.value} <span className="text-xs text-text-tertiary">{ins.unit}</span>
      </p>
      <p className="mt-1.5 text-xs text-text-tertiary">{ins.why} · 2위 {ins.runner_up}</p>
    </Card>
  );
}

function Kpi({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: React.ReactNode; accent?: boolean }) {
  return (
    <Card className="p-3.5">
      <div className="flex items-center gap-2 text-text-tertiary">
        {icon}
        <span className="text-[0.62rem] uppercase tracking-[0.08em]">{label}</span>
      </div>
      <p className={cn("tnum mt-1.5 text-2xl font-semibold", accent ? "text-accent" : "text-text-primary")}>{value}</p>
    </Card>
  );
}

function ClassBars({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data);
  const max = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <div className="flex flex-col gap-1.5">
      {entries.map(([cls, n]) => (
        <div key={cls} className="flex items-center gap-3">
          <span className="w-40 shrink-0 truncate text-xs text-text-secondary">{cls}</span>
          <div className="relative h-5 flex-1 overflow-hidden rounded bg-surface-2">
            <div
              className="absolute inset-y-0 left-0 rounded bg-primary/70"
              style={{ width: `${(n / max) * 100}%` }}
            />
          </div>
          <span className="tnum w-6 text-right text-xs text-text-primary">{n}</span>
        </div>
      ))}
    </div>
  );
}

function StatHistogram({ title, cell, color }: { title: string; cell: StatCell | null; color: string }) {
  if (!cell) return null;
  const max = Math.max(...cell.hist, 1);
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <span className="text-sm text-text-secondary">{title}</span>
        <span className="tnum text-xs text-text-tertiary">
          {cell.min}–{cell.max} {cell.unit} · 평균 {cell.mean}
        </span>
      </div>
      <div className="mt-1.5 flex h-14 items-end gap-0.5">
        {cell.hist.map((h, i) => (
          <div
            key={i}
            className="flex-1 rounded-t"
            style={{ height: `${(h / max) * 100}%`, minHeight: h > 0 ? 2 : 0, background: color, opacity: 0.75 }}
            title={`${cell.edges[i]}–${cell.edges[i + 1]}: ${h}`}
          />
        ))}
      </div>
    </div>
  );
}

const STATUS_STYLE: Record<string, string> = {
  rich: "text-accent bg-accent-muted",
  sparse: "text-warning bg-[color-mix(in_srgb,var(--warning)_14%,transparent)]",
  missing: "text-danger bg-[color-mix(in_srgb,var(--danger)_12%,transparent)]",
};
const STATUS_LABEL: Record<string, string> = { rich: "충실", sparse: "부족", missing: "없음" };

function CoverageMatrix({ rows }: { rows: { group: string; family: string; count: number; status: string }[] }) {
  const groups = [...new Set(rows.map((r) => r.group))];
  return (
    <div className="flex flex-col gap-4">
      {groups.map((g) => (
        <div key={g}>
          <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-text-tertiary">{g}</p>
          <div className="flex flex-wrap gap-1.5">
            {rows.filter((r) => r.group === g).map((r) => (
              <div
                key={r.family}
                className={cn("flex items-center gap-1.5 rounded-md px-2 py-1 text-xs", STATUS_STYLE[r.status])}
              >
                <span className="font-medium">{r.family}</span>
                <span className="tnum opacity-80">{r.count}</span>
                <span className="opacity-70">· {STATUS_LABEL[r.status]}</span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
