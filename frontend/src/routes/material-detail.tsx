// 재료 상세(/materials/$id, §14.3.3) — 시편 레전드 + 응력-변형률 곡선(오버레이) + 영률 picker + 물성 테이블.
import * as React from "react";
import { Link, useParams } from "@tanstack/react-router";
import { useQuery, useQueries, useMutation, useQueryClient } from "@tanstack/react-query";
import { ChevronLeft, Upload, Download, FlaskConical } from "lucide-react";
import { toast } from "sonner";
import { getMaterial } from "../api/materials";
import { listSpecimens, type Specimen } from "../api/specimens";
import {
  listTests,
  getCurve,
  getProperties,
  computeProperties,
  curveCsvUrl,
  type Test,
  type Curve,
  type Properties,
} from "../api/tests";
import {
  StressStrainChart,
  type ChartSeries,
  type ChartMarkers,
} from "../components/StressStrainChart";
import { PropertyTable, type PropertyRow } from "../components/PropertyTable";
import { RegressionRangePicker } from "../components/RegressionRangePicker";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { ChartSkeleton, TableSkeleton } from "../components/states/Skeletons";
import { cn } from "../lib/utils";

// 시편의 대표 test(첫 valid) + 곡선 + 물성을 묶은 뷰 모델.
type SpecimenView = {
  specimen: Specimen;
  test: Test | null;
  curve: Curve | null;
  props: Properties | null;
};

export function MaterialDetailScreen() {
  const { id } = useParams({ from: "/materials/$id" });
  const mid = Number(id);
  const qc = useQueryClient();

  const materialQ = useQuery({ queryKey: ["material", mid], queryFn: () => getMaterial(mid) });
  const specimensQ = useQuery({ queryKey: ["specimens", mid], queryFn: () => listSpecimens(mid) });

  const specimens = specimensQ.data ?? [];

  // 각 시편의 대표 test 목록(첫 valid). 시편 수만큼 병렬 쿼리.
  const testQueries = useQueries({
    queries: specimens.map((s) => ({
      queryKey: ["tests", s.id],
      queryFn: () => listTests(s.id),
      enabled: specimens.length > 0,
    })),
  });

  const reps = specimens.map((s, i) => {
    const tests = (testQueries[i]?.data ?? []) as Test[];
    return { specimen: s, test: tests.find((t) => t.valid) ?? tests[0] ?? null };
  });

  // 대표 test 들의 곡선·물성 병렬 쿼리.
  const curveQueries = useQueries({
    queries: reps.map((r) => ({
      queryKey: ["curve", r.test?.id],
      queryFn: () => getCurve(r.test!.id, { kind: "nominal", max_points: 2000 }),
      enabled: !!r.test,
    })),
  });
  const propsQueries = useQueries({
    queries: reps.map((r) => ({
      queryKey: ["properties", r.test?.id],
      queryFn: () => getProperties(r.test!.id),
      enabled: !!r.test,
      retry: false,
    })),
  });

  const views: SpecimenView[] = reps.map((r, i) => ({
    specimen: r.specimen,
    test: r.test,
    curve: (curveQueries[i]?.data as Curve | undefined) ?? null,
    props: (propsQueries[i]?.data as Properties | undefined) ?? null,
  }));

  // 활성 시편(차트 마커·회귀 picker 대상). 기본 첫 시편.
  const [activeId, setActiveId] = React.useState<number | null>(null);
  React.useEffect(() => {
    if (activeId == null && specimens.length > 0) setActiveId(specimens[0].id);
  }, [specimens, activeId]);

  const active = views.find((v) => v.specimen.id === activeId) ?? null;
  const [range, setRange] = React.useState<[number, number] | null>(null);

  const recompute = useMutation({
    mutationFn: (r: [number, number]) =>
      computeProperties(active!.test!.id, { e_range: r }),
    onSuccess: (p) => {
      qc.setQueryData(["properties", active!.test!.id], p);
      const conf = (p.params as { confidence?: string })?.confidence;
      toast.success(
        conf === "low"
          ? "재계산 완료 — 신뢰도 낮음(low) 확인 필요"
          : "영률 재계산 완료",
      );
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : "재계산 실패"),
  });

  const series: ChartSeries[] = views
    .filter((v) => v.curve && v.test)
    .map((v) => ({
      testId: v.test!.id,
      name: v.specimen.label,
      x: v.curve!.x,
      y: v.curve!.y,
      active: v.specimen.id === activeId,
      markers: v.specimen.id === activeId ? markersFrom(v.props) : undefined,
    }));

  const rows: PropertyRow[] = views.map((v) => ({
    specimenLabel: v.specimen.label,
    geometry: v.specimen.geometry_type,
    strainSource: v.test?.strain_source,
    valid: v.test?.valid,
    props: v.props,
  }));

  const loading = materialQ.isPending || specimensQ.isPending;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link
          to="/materials"
          className="inline-flex items-center gap-1 text-sm text-text-secondary transition-colors hover:text-text-primary"
        >
          <ChevronLeft className="size-4" />
          재료 라이브러리
        </Link>
      </div>

      {materialQ.isError ? (
        <ErrorState onRetry={() => materialQ.refetch()} />
      ) : (
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-overline">재료 상세</p>
            <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
              {materialQ.data?.name ?? "—"}
            </h1>
            {materialQ.data?.material_code && (
              <p className="tnum mt-1 text-xs text-text-tertiary">
                {materialQ.data.material_code}
              </p>
            )}
          </div>
          <Link to="/upload" search={{ material: mid }}>
            <Button variant="outline">
              <Upload className="size-4" />
              시험 데이터 업로드
            </Button>
          </Link>
        </header>
      )}

      {loading ? (
        <div className="flex flex-col gap-6">
          <ChartSkeleton />
          <TableSkeleton />
        </div>
      ) : specimens.length === 0 ? (
        <EmptyState
          icon={<FlaskConical className="size-6" />}
          title="시험 데이터가 없습니다"
          description="이 재료에 인장 시험 파일을 업로드하면 곡선과 물성이 표시됩니다."
          action={
            <Link to="/upload" search={{ material: mid }}>
              <Button>
                <Upload className="size-4" />
                업로드
              </Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[200px_minmax(0,1fr)]">
          {/* 시편 레전드 — 활성 선택 */}
          <aside className="flex flex-col gap-1">
            <p className="text-overline mb-1">시편</p>
            {views.map((v, i) => (
              <button
                key={v.specimen.id}
                onClick={() => {
                  setActiveId(v.specimen.id);
                  setRange(null);
                }}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition-colors",
                  v.specimen.id === activeId
                    ? "bg-primary-muted text-text-primary"
                    : "text-text-secondary hover:bg-surface-2",
                )}
              >
                <span
                  className="size-2.5 shrink-0 rounded-full"
                  style={{ background: `var(--chart-${(i % 8) + 1})` }}
                />
                <span className="truncate">{v.specimen.label}</span>
              </button>
            ))}
          </aside>

          <div className="flex min-w-0 flex-col gap-6">
            <Card className="p-4">
              {series.length === 0 ? (
                <EmptyState title="곡선 없음" description="대표 시험의 곡선을 불러올 수 없습니다." />
              ) : (
                <StressStrainChart
                  series={series}
                  onRangeSelect={(r) => setRange(r)}
                />
              )}
            </Card>

            {active?.curve && active.test && (
              <RegressionRangePicker
                x={active.curve.x}
                y={active.curve.y}
                range={range}
                onRangeChange={setRange}
                onCommit={(r) => recompute.mutate(r)}
                committing={recompute.isPending}
              />
            )}

            <Card className="overflow-hidden">
              <div className="flex items-center justify-between border-b border-border-subtle px-4 py-3">
                <p className="text-overline">시험 기록</p>
                {active?.test && (
                  <a href={curveCsvUrl(active.test.id)} download>
                    <Button variant="ghost" size="sm">
                      <Download className="size-4" />
                      CSV
                    </Button>
                  </a>
                )}
              </div>
              <PropertyTable rows={rows} />
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}

// 서버 확정 물성 → 차트 마커 좌표(argmax 금지 — 스칼라 기반 근사 좌표).
function markersFrom(p: Properties | null): ChartMarkers | undefined {
  if (!p) return undefined;
  const m: ChartMarkers = {};
  if (p.uts_pa != null && p.uniform_elongation != null)
    m.uts = { strain: p.uniform_elongation, stressPa: p.uts_pa };
  if (p.yield_strength_pa != null) {
    const params = p.params as { offset?: number } | null;
    const e = p.youngs_modulus_pa;
    const off = params?.offset ?? 0.002;
    // Rp0.2 변형률 ≈ offset + σy/E (offset 직선 교점의 근사 x).
    const strain = e ? off + p.yield_strength_pa / e : off;
    m.yield = { strain, stressPa: p.yield_strength_pa };
  }
  const params = p.params as { e_range?: [number, number]; r2?: number } | null;
  if (p.youngs_modulus_pa != null && params?.e_range) {
    m.regression = {
      e1: params.e_range[0],
      e2: params.e_range[1],
      ePa: p.youngs_modulus_pa,
      intercept: 0,
      r2: params.r2 ?? 1,
    };
  }
  return m;
}
