// 재료 상세(/materials/$id, §14.3.3) — 시편 레전드 + 응력-변형률 곡선(오버레이) + 영률 picker + 물성 테이블.
import * as React from "react";
import { Link, useParams, useNavigate } from "@tanstack/react-router";
import { useQuery, useQueries, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ChevronLeft,
  Upload,
  Download,
  FlaskConical,
  Pencil,
  Trash2,
  AlertTriangle,
  SearchX,
} from "lucide-react";
import { toast } from "sonner";
import { getMaterial, patchMaterial, deleteMaterial } from "../api/materials";
import { listSpecimens, type Specimen } from "../api/specimens";
import {
  listTests,
  getCurve,
  getProperties,
  computeProperties,
  patchTest,
  curveCsvUrl,
  type Test,
  type Curve,
  type Properties,
} from "../api/tests";
import { ApiError } from "../api/client";
import {
  StressStrainChart,
  type ChartSeries,
  type ChartMarkers,
} from "../components/StressStrainChart";
import { PropertyTable, type PropertyRow } from "../components/PropertyTable";
import { RegressionRangePicker } from "../components/RegressionRangePicker";
import { FitPanel } from "../components/FitPanel";
import { ViscoelasticView } from "../components/ViscoelasticView";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Skeleton } from "../components/ui/skeleton";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { ChartSkeleton, TableSkeleton } from "../components/states/Skeletons";
import { downloadFile, errorMessage } from "../lib/download";
import { cssVar } from "../lib/echarts";
import { cn } from "../lib/utils";

// 시편의 대표 test(첫 valid) + 곡선 + 물성을 묶은 뷰 모델.
type SpecimenView = {
  specimen: Specimen;
  test: Test | null;
  curve: Curve | null;
  props: Properties | null;
  curveError: boolean;
};

const CATEGORY_OPTIONS = ["metal", "polymer", "rubber", "composite", "ceramic", "foam"] as const;

/** 테마 토글 시 재렌더 신호(레전드·시리즈 색 재계산용). */
function useThemeVersion(): number {
  const [v, setV] = React.useState(0);
  React.useEffect(() => {
    const ob = new MutationObserver(() => setV((x) => x + 1));
    ob.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });
    return () => ob.disconnect();
  }, []);
  return v;
}

export function MaterialDetailScreen() {
  const { id } = useParams({ from: "/materials/$id" });
  const mid = Number(id);
  const idInvalid = !Number.isInteger(mid) || mid <= 0;
  const qc = useQueryClient();
  const navigate = useNavigate();
  const themeVersion = useThemeVersion();

  const materialQ = useQuery({
    queryKey: ["material", mid],
    queryFn: () => getMaterial(mid),
    enabled: !idInvalid,
    retry: (count, e) => !(e instanceof ApiError && e.status === 404) && count < 2,
  });
  const specimensQ = useQuery({
    queryKey: ["specimens", mid],
    queryFn: () => listSpecimens(mid),
    enabled: !idInvalid && materialQ.isSuccess,
  });

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

  // 공칭↔진 응력 토글(§6.2). 진곡선은 넥킹 마커, 공칭은 UTS/Rp0.2 마커.
  const [curveKind, setCurveKind] = React.useState<"nominal" | "true">("nominal");

  // 대표 test 들의 곡선·물성 병렬 쿼리. 완화시험은 인장 곡선이 없으므로 제외(500 방지).
  const curveQueries = useQueries({
    queries: reps.map((r) => ({
      queryKey: ["curve", r.test?.id, curveKind],
      queryFn: () => getCurve(r.test!.id, { kind: curveKind, max_points: 2000 }),
      enabled: !!r.test && r.test.test_type !== "relaxation",
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
    curveError: curveQueries[i]?.isError ?? false,
  }));

  // 활성 시편(차트 마커·회귀 picker 대상). 기본 첫 시편.
  // 파생 effect는 paint 후 실행돼 activeId=null 창이 생기므로, 유효 activeId를
  // 첫 시편으로 즉시 폴백해 렌더한다(점탄성 클라 네비 시 1프레임 빈 화면 방지).
  const [activeId, setActiveId] = React.useState<number | null>(null);
  const effectiveActiveId =
    activeId != null && views.some((v) => v.specimen.id === activeId)
      ? activeId
      : specimens[0]?.id ?? null;
  React.useEffect(() => {
    if (activeId == null && specimens.length > 0) setActiveId(specimens[0].id);
  }, [specimens, activeId]);

  const active = views.find((v) => v.specimen.id === effectiveActiveId) ?? null;
  const [range, setRange] = React.useState<[number, number] | null>(null);

  // 클라 네비로 다른 재료에 오면(같은 컴포넌트 재사용) 시편·토글 상태 초기화.
  // 이전 재료의 activeId/curveKind가 유출되면 점탄성 뷰가 빈 화면이 되는 버그 방지.
  React.useEffect(() => {
    setActiveId(null);
    setRange(null);
    setCurveKind("nominal");
  }, [mid]);

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
    onError: (e) => toast.error(errorMessage(e)),
  });

  // 재료 편집·삭제(파괴적 액션은 확인 다이얼로그).
  const [editOpen, setEditOpen] = React.useState(false);
  const [deleteOpen, setDeleteOpen] = React.useState(false);
  const editMut = useMutation({
    mutationFn: (p: { name: string; material_code: string | null; category: string | null; description: string | null }) =>
      patchMaterial(mid, p),
    onSuccess: (m) => {
      qc.setQueryData(["material", mid], m);
      qc.invalidateQueries({ queryKey: ["materials"] });
      setEditOpen(false);
      toast.success("재료 정보를 수정했습니다.");
    },
    onError: (e) => toast.error(errorMessage(e)),
  });
  const deleteMut = useMutation({
    mutationFn: () => deleteMaterial(mid),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["materials"] });
      toast.success("재료를 삭제했습니다.");
      navigate({ to: "/materials" });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  // 시험 valid 토글(이상치 수동 제외, PropertyTable 액션).
  const toggleValid = useMutation({
    mutationFn: (t: Test) =>
      patchTest(t.id, {
        valid: !t.valid,
        invalid_reason: t.valid ? "수동 제외" : null,
      }),
    onSuccess: (_r, t) => {
      qc.invalidateQueries({ queryKey: ["tests", t.specimen_id] });
      toast.success(t.valid ? "시험을 제외했습니다." : "시험을 복원했습니다.");
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  // 시리즈 색: 전체 시편 인덱스 기준으로 한 번 계산해 레전드·차트가 항상 일치.
  // themeVersion 의존으로 테마 토글 시 재계산.
  const seriesColor = React.useMemo(
    () => views.map((_v, i) => cssVar(`--chart-${(i % 8) + 1}`)),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [views.length, themeVersion],
  );

  const series: ChartSeries[] = views
    .map((v, i) => ({ v, i }))
    .filter(({ v }) => v.curve && v.test)
    .map(({ v, i }) => ({
      testId: v.test!.id,
      name: v.specimen.label,
      x: v.curve!.x,
      y: v.curve!.y,
      active: v.specimen.id === effectiveActiveId,
      color: seriesColor[i],
      // 진곡선이면 넥킹 마커, 공칭이면 UTS/Rp0.2/회귀 마커.
      markers:
        v.specimen.id === effectiveActiveId
          ? curveKind === "true"
            ? neckingMarker(v.curve)
            : markersFrom(v.props)
          : undefined,
    }));

  const rows: PropertyRow[] = views.map((v) => ({
    specimenLabel: v.specimen.label,
    geometry: v.specimen.geometry_type,
    strainSource: v.test?.strain_source,
    valid: v.test?.valid,
    props: v.props,
    test: v.test,
  }));

  const loading = materialQ.isPending || specimensQ.isPending;
  // 점탄성 재료면 전용 뷰로 분기. test_type이 우선, 로딩 중엔 카테고리를 폴백 신호로
  // 써서 인장 뷰로 깜빡이는 레이스를 방지(클라 네비 시).
  const repTestType = reps.find((r) => r.test)?.test?.test_type;
  const cat = materialQ.data?.category;
  const isViscoelastic =
    repTestType === "relaxation" ||
    (repTestType == null && (cat === "polymer" || cat === "rubber"));

  // ── 잘못된 id / 404 — 전용 화면으로 종료(아래 콘텐츠 렌더 중단) ──
  const notFound =
    idInvalid ||
    (materialQ.isError && materialQ.error instanceof ApiError && materialQ.error.status === 404);
  if (notFound) {
    return (
      <div className="flex flex-col gap-6">
        <BackLink />
        <EmptyState
          icon={<SearchX className="size-6" />}
          title="재료를 찾을 수 없습니다"
          description="삭제되었거나 존재하지 않는 재료입니다."
          action={
            <Link to="/materials">
              <Button>재료 라이브러리로</Button>
            </Link>
          }
        />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <BackLink />

      {materialQ.isError ? (
        <ErrorState onRetry={() => materialQ.refetch()} />
      ) : (
        <header className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-overline">재료 상세</p>
            {materialQ.isPending ? (
              <Skeleton className="mt-2 h-7 w-56" />
            ) : (
              <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
                {materialQ.data?.name}
              </h1>
            )}
            {materialQ.data?.material_code && (
              <p className="tnum mt-1 text-xs text-text-tertiary">
                {materialQ.data.material_code}
              </p>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="ghost" size="sm" onClick={() => setEditOpen(true)} disabled={!materialQ.data}>
              <Pencil className="size-4" />
              편집
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-danger hover:text-danger"
              onClick={() => setDeleteOpen(true)}
              disabled={!materialQ.data}
            >
              <Trash2 className="size-4" />
              삭제
            </Button>
            <Link to="/upload" search={{ material: mid }}>
              <Button variant="outline">
                <Upload className="size-4" />
                시험 데이터 업로드
              </Button>
            </Link>
          </div>
        </header>
      )}

      {loading && !materialQ.isError ? (
        <div className="flex flex-col gap-6">
          <ChartSkeleton />
          <TableSkeleton />
        </div>
      ) : specimensQ.isError ? (
        <ErrorState
          title="시편 목록을 불러오지 못했습니다"
          onRetry={() => specimensQ.refetch()}
        />
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
      ) : isViscoelastic && active?.test ? (
        <ViscoelasticView testId={active.test.id} />
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
                aria-pressed={v.specimen.id === effectiveActiveId}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-sm transition-colors",
                  v.specimen.id === effectiveActiveId
                    ? "bg-primary-muted text-text-primary"
                    : "text-text-secondary hover:bg-surface-2",
                )}
              >
                <span
                  className="size-2.5 shrink-0 rounded-full"
                  style={{ background: seriesColor[i] }}
                />
                <span className="truncate">{v.specimen.label}</span>
                {v.curveError && (
                  <AlertTriangle
                    className="ml-auto size-3.5 shrink-0 text-warning"
                    aria-label="곡선 로드 실패"
                  />
                )}
              </button>
            ))}
          </aside>

          <div className="flex min-w-0 flex-col gap-6">
            <Card className="p-4">
              <div className="mb-3 flex items-center justify-between">
                <p className="text-overline">응력-변형률</p>
                <div className="flex rounded-md border border-border-default p-0.5">
                  {(["nominal", "true"] as const).map((k) => (
                    <button
                      key={k}
                      onClick={() => setCurveKind(k)}
                      aria-pressed={curveKind === k}
                      className={cn(
                        "rounded px-2.5 py-1 text-xs font-medium transition-colors",
                        curveKind === k
                          ? "bg-primary-muted text-[var(--primary-hover)]"
                          : "text-text-tertiary hover:text-text-secondary",
                      )}
                    >
                      {k === "nominal" ? "공칭" : "진응력"}
                    </button>
                  ))}
                </div>
              </div>
              {series.length === 0 ? (
                views.some((v) => v.curveError) ? (
                  <ErrorState
                    title="곡선을 불러오지 못했습니다"
                    onRetry={() => curveQueries.forEach((q) => q.refetch())}
                  />
                ) : (
                  <EmptyState title="곡선 없음" description="대표 시험의 곡선을 불러올 수 없습니다." />
                )
              ) : (
                <StressStrainChart
                  series={series}
                  onRangeSelect={curveKind === "nominal" ? (r) => setRange(r) : undefined}
                />
              )}
            </Card>

            {/* 영률 회귀는 공칭-탄성 개념 → 진응력 뷰에서는 안내 배너로 대체. */}
            {curveKind === "nominal" && active?.curve && active.test ? (
              <RegressionRangePicker
                x={active.curve.x}
                y={active.curve.y}
                range={range}
                onRangeChange={setRange}
                onCommit={(r) => recompute.mutate(r)}
                committing={recompute.isPending}
              />
            ) : curveKind === "true" ? (
              <p className="rounded-md border border-border-subtle bg-surface-2/50 px-4 py-2.5 text-xs text-text-tertiary">
                영률 회귀 구간 선택은 공칭 곡선에서 수행합니다 — 진응력 뷰는 넥킹(Considère) 마커를 표시합니다.
              </p>
            ) : null}

            <Card className="overflow-hidden">
              <div className="flex items-center justify-between border-b border-border-subtle px-4 py-3">
                <p className="text-overline">시험 기록</p>
                {active?.test && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      downloadFile(curveCsvUrl(active.test!.id), "curve.csv").catch((e) =>
                        toast.error(errorMessage(e)),
                      )
                    }
                  >
                    <Download className="size-4" />
                    CSV
                  </Button>
                )}
              </div>
              <PropertyTable
                rows={rows}
                onToggleValid={(t) => toggleValid.mutate(t)}
              />
            </Card>

            {/* 구성방정식 피팅 + LS-DYNA 카드(활성 시편 기준, §6.3). */}
            {active?.test && (
              <FitPanel testId={active.test.id} hasProperties={active.props != null} />
            )}
          </div>
        </div>
      )}

      {/* ── 편집 다이얼로그 ── */}
      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>재료 정보 편집</DialogTitle>
            <DialogDescription>이름·코드·분류·설명을 수정합니다.</DialogDescription>
          </DialogHeader>
          {materialQ.data && (
            <EditForm
              material={materialQ.data}
              pending={editMut.isPending}
              onSubmit={(p) => editMut.mutate(p)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* ── 삭제 확인 다이얼로그 ── */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>재료 삭제</DialogTitle>
            <DialogDescription>
              "{materialQ.data?.name}"을(를) 삭제합니다. 시편 {specimens.length}개와 모든
              시험·곡선·물성이 함께 삭제되며 되돌릴 수 없습니다.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setDeleteOpen(false)}>
              취소
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteMut.mutate()}
              disabled={deleteMut.isPending}
            >
              <Trash2 className="size-4" />
              {deleteMut.isPending ? "삭제 중…" : "삭제"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function BackLink() {
  return (
    <div>
      <Link
        to="/materials"
        className="inline-flex items-center gap-1 text-sm text-text-secondary transition-colors hover:text-text-primary"
      >
        <ChevronLeft className="size-4" />
        재료 라이브러리
      </Link>
    </div>
  );
}

// 편집 폼 — 다이얼로그 열릴 때의 재료 값으로 초기화.
function EditForm({
  material,
  pending,
  onSubmit,
}: {
  material: { name: string; material_code: string | null; category: string | null; description: string | null };
  pending: boolean;
  onSubmit: (p: { name: string; material_code: string | null; category: string | null; description: string | null }) => void;
}) {
  const [name, setName] = React.useState(material.name);
  const [code, setCode] = React.useState(material.material_code ?? "");
  // 분류 없음(null)을 'none' 센티널로 표현 — 이름만 고쳐도 category가 metal로 굳는 것 방지.
  const [category, setCategory] = React.useState(material.category ?? "none");
  const [desc, setDesc] = React.useState(material.description ?? "");
  const nameInvalid = !name.trim();

  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={(e) => {
        e.preventDefault();
        if (nameInvalid) return;
        onSubmit({
          name: name.trim(),
          material_code: code.trim() || null,
          category: category === "none" ? null : category,
          description: desc.trim() || null,
        });
      }}
    >
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="edit-name">이름 *</Label>
        <Input id="edit-name" value={name} onChange={(e) => setName(e.target.value)} />
        {nameInvalid && <p className="text-xs text-danger">이름은 필수입니다.</p>}
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="edit-code">재료 코드</Label>
        <Input id="edit-code" value={code} onChange={(e) => setCode(e.target.value)} />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label>분류</Label>
        <Select value={category} onValueChange={setCategory}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">미분류</SelectItem>
            {CATEGORY_OPTIONS.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="edit-desc">설명</Label>
        <Input id="edit-desc" value={desc} onChange={(e) => setDesc(e.target.value)} />
      </div>
      <DialogFooter>
        <Button type="submit" disabled={pending || nameInvalid}>
          {pending ? "저장 중…" : "저장"}
        </Button>
      </DialogFooter>
    </form>
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

// 진곡선 넥킹점(Considère) → 차트 마커. 곡선 응답의 necking 좌표 사용(§6.2).
function neckingMarker(curve: Curve | null): ChartMarkers | undefined {
  const n = curve?.necking;
  if (!n || n.strain == null || n.stress == null) return undefined;
  return { necking: { strain: n.strain, stressPa: n.stress } };
}
