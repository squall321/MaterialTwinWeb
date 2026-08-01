// 재료 비교(/catalog/compare) — CPU 스펙 비교식. 재료 컬럼 picker + 물성별 정렬표(상대막대·최대/최소).
import * as React from "react";
import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import {
  ChevronLeft, Plus, X, Search, Factory, Info, ChevronUp, ChevronDown, ExternalLink, GitCompare,
} from "lucide-react";
import {
  compareMaterials, listCatalogMaterials,
  type CatalogComparison, type CompareProperty, type CompareCell,
  type CatalogMaterial, type CompareMaterialMeta,
} from "../api/catalog";
import { cn } from "../lib/utils";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from "../components/ui/dialog";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { Skeleton } from "../components/ui/skeleton";
import {
  domainMeta, tierMeta, formatValue, formatConditions, subsystemLabel,
} from "../lib/catalog-ui";

const MAX_COLS = 4;
// 재료 컬럼 색(막대·헤더 액센트).
const COL_COLORS = ["var(--chart-1)", "var(--chart-2)", "var(--chart-4)", "var(--chart-6)"];

type CompareSearch = { ids?: string; shared?: string };

export function CatalogCompareScreen() {
  const search = useSearch({ from: "/catalog/compare" }) as CompareSearch;
  const navigate = useNavigate();

  const ids = React.useMemo(
    () => (search.ids ?? "").split(",").map((s) => Number(s)).filter((n) => Number.isInteger(n) && n > 0).slice(0, MAX_COLS),
    [search.ids],
  );
  const sharedOnly = search.shared === "1";

  // 선택 재료 메타 캐시(슬롯 표시용 — 2개 미만이라 compare 쿼리가 없을 때도 이름 표시).
  const [cache, setCache] = React.useState<Record<number, CompareMaterialMeta | CatalogMaterial>>({});
  const [addOpen, setAddOpen] = React.useState(false);

  const setIds = React.useCallback(
    (next: number[]) =>
      navigate({
        to: "/catalog/compare",
        search: (p: CompareSearch) => ({ ...p, ids: next.join(",") || undefined }),
        replace: true,
      }),
    [navigate],
  );
  const addId = (m: CatalogMaterial) => {
    setCache((c) => ({ ...c, [m.id]: m }));
    if (!ids.includes(m.id) && ids.length < MAX_COLS) setIds([...ids, m.id]);
    setAddOpen(false);
  };
  const removeId = (id: number) => setIds(ids.filter((x) => x !== id));

  const cmpQ = useQuery({
    queryKey: ["catalog", "compare", ids],
    queryFn: () => compareMaterials(ids),
    enabled: ids.length >= 2,
    placeholderData: keepPreviousData,
  });

  // compare 응답의 권위 메타를 캐시에 반영(이름·제조사 등).
  React.useEffect(() => {
    if (cmpQ.data) setCache((c) => {
      const n = { ...c };
      for (const m of cmpQ.data.materials) n[m.id] = m;
      return n;
    });
  }, [cmpQ.data]);

  const colOf = (id: number) => COL_COLORS[Math.max(0, ids.indexOf(id)) % COL_COLORS.length];
  const slots: (CompareMaterialMeta | CatalogMaterial)[] = ids.map(
    (id) => cache[id] ?? ({ id, name: `#${id}` } as CompareMaterialMeta),
  );

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link to="/catalog" className="inline-flex items-center gap-1 text-sm text-text-secondary transition-colors hover:text-text-primary">
          <ChevronLeft className="size-4" /> 물성 카탈로그
        </Link>
      </div>

      <header className="flex flex-col gap-1">
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.08em] text-text-tertiary">
          <GitCompare className="size-3.5 text-primary" /> Material Comparison
        </div>
        <h1 className="text-2xl font-semibold tracking-[-0.01em] text-text-primary">재료 비교</h1>
        <p className="text-sm text-text-secondary">
          재료를 최대 4종까지 골라 물성별로 나란히 비교합니다. 각 값은 신뢰등급 최상의 대표값입니다.
        </p>
      </header>

      {/* ── 재료 슬롯(컬럼 picker) ── */}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {slots.map((m, i) => (
          <SlotCard key={m.id} m={m} color={COL_COLORS[i % COL_COLORS.length]} onRemove={() => removeId(m.id)} />
        ))}
        {ids.length < MAX_COLS && (
          <button
            onClick={() => setAddOpen(true)}
            className="flex min-h-[92px] flex-col items-center justify-center gap-1.5 rounded-lg border border-dashed border-border-default bg-surface/40 text-text-tertiary transition-colors hover:border-primary hover:text-text-secondary"
          >
            <Plus className="size-5" />
            <span className="text-xs font-medium">재료 추가</span>
          </button>
        )}
      </div>

      {/* ── 본문 ── */}
      {ids.length < 2 ? (
        <EmptyState
          icon={<GitCompare className="size-6" />}
          title="비교할 재료를 2개 이상 선택하세요"
          description="위 '재료 추가'로 재료를 골라 물성별 비교표를 확인합니다."
          action={<Button onClick={() => setAddOpen(true)}><Plus className="size-4" /> 재료 추가</Button>}
        />
      ) : cmpQ.isError ? (
        <ErrorState onRetry={() => cmpQ.refetch()} />
      ) : cmpQ.isPending ? (
        <Skeleton className="h-96 w-full" />
      ) : cmpQ.data ? (
        <CompareTable
          data={cmpQ.data}
          ids={ids}
          colOf={colOf}
          sharedOnly={sharedOnly}
          onToggleShared={() =>
            navigate({ to: "/catalog/compare", search: (p: CompareSearch) => ({ ...p, shared: sharedOnly ? undefined : "1" }), replace: true })
          }
        />
      ) : null}

      <AddDialog open={addOpen} onOpenChange={setAddOpen} exclude={ids} onPick={addId} />
    </div>
  );
}

function SlotCard({
  m, color, onRemove,
}: { m: CompareMaterialMeta | CatalogMaterial; color: string; onRemove: () => void }) {
  return (
    <div className="relative flex min-h-[92px] flex-col gap-1.5 rounded-lg border-t-2 bg-surface p-3 shadow-[var(--elev-1)]" style={{ borderTopColor: color }}>
      <button
        onClick={onRemove}
        aria-label="제거"
        className="absolute right-2 top-2 text-text-tertiary transition-colors hover:text-danger"
      >
        <X className="size-3.5" />
      </button>
      <div className="pr-5 text-sm font-semibold leading-tight text-text-primary">{m.name}</div>
      <div className="mt-auto flex flex-wrap items-center gap-1">
        {m.manufacturer && (
          <span className="inline-flex items-center gap-0.5 text-[0.6875rem] text-text-tertiary">
            <Factory className="size-3" /> {m.manufacturer}
          </span>
        )}
        {m.material_class && <span className="text-[0.6875rem] text-text-tertiary">· {m.material_class}</span>}
      </div>
    </div>
  );
}

function CompareTable({
  data, ids, colOf, sharedOnly, onToggleShared,
}: {
  data: CatalogComparison;
  ids: number[];
  colOf: (id: number) => string;
  sharedOnly: boolean;
  onToggleShared: () => void;
}) {
  const n = data.materials.length;
  const byId = React.useMemo(
    () => Object.fromEntries(data.materials.map((m) => [m.id, m])),
    [data.materials],
  );
  // 요청(ids) 순서대로 컬럼 정렬.
  const cols = ids.map((id) => byId[id]).filter(Boolean) as CompareMaterialMeta[];
  const colIndex = React.useMemo(() => {
    // cells 배열은 data.materials 순서 → id로 셀 찾기용 매핑.
    return data.materials.map((m) => m.id);
  }, [data.materials]);

  const domains = data.domains
    .map((d) => ({
      ...d,
      properties: sharedOnly ? d.properties.filter((p) => p.present === n) : d.properties,
    }))
    .filter((d) => d.properties.length > 0);

  return (
    <div className="flex flex-col gap-3">
      {/* 컨트롤 바 */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm text-text-secondary">
          공통 <span className="tnum font-semibold text-text-primary">{data.n_shared}</span> · 전체{" "}
          <span className="tnum font-semibold text-text-primary">{data.n_properties}</span> 물성
        </span>
        <label className="inline-flex cursor-pointer items-center gap-1.5 text-xs text-text-secondary">
          <input type="checkbox" checked={sharedOnly} onChange={onToggleShared} className="accent-[var(--primary)]" />
          공통 물성만
        </label>
        <span className="ml-auto inline-flex items-center gap-1 text-[0.6875rem] text-text-tertiary" title={data.rule}>
          <Info className="size-3" /> 대표값 기준
        </span>
      </div>

      {/* 비교표(가로 스크롤, 라벨 컬럼 sticky) */}
      <div className="overflow-x-auto rounded-lg border border-border-subtle">
        <table className="w-full min-w-[640px] border-collapse">
          <thead>
            <tr className="border-b border-border-default bg-surface">
              <th className="sticky left-0 z-10 w-52 min-w-[13rem] bg-surface px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.04em] text-text-tertiary">
                물성
              </th>
              {cols.map((m) => (
                <th key={m.id} className="border-l border-border-subtle px-4 py-3 text-left align-top" style={{ borderTopColor: colOf(m.id) }}>
                  <div className="flex items-start gap-1.5">
                    <span className="mt-1 size-2 shrink-0 rounded-full" style={{ background: colOf(m.id) }} />
                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold text-text-primary" title={m.name}>{m.name}</div>
                      <div className="mt-0.5 flex flex-wrap items-center gap-1 text-[0.6875rem] text-text-tertiary">
                        {m.manufacturer && <span>{m.manufacturer}</span>}
                        {m.grade && <span>· {m.grade}</span>}
                        {m.material_class && <span>· {m.material_class}</span>}
                      </div>
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {domains.map((d) => (
              <React.Fragment key={d.domain}>
                <tr>
                  <td colSpan={cols.length + 1} className="border-y border-border-subtle bg-surface-2/60 px-4 py-1.5">
                    <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-text-secondary">
                      <span className="size-2 rounded-full" style={{ background: domainMeta(d.domain).color }} />
                      {domainMeta(d.domain).label} 물성
                    </span>
                  </td>
                </tr>
                {d.properties.map((p) => (
                  <PropRow key={p.key} p={p} colIndex={colIndex} cols={cols} colOf={colOf} />
                ))}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function PropRow({
  p, colIndex, cols, colOf,
}: {
  p: CompareProperty;
  colIndex: number[];
  cols: CompareMaterialMeta[];
  colOf: (id: number) => string;
}) {
  const cellById = (id: number): CompareCell | null => {
    const i = colIndex.indexOf(id);
    return i >= 0 ? p.cells[i] ?? null : null;
  };
  return (
    <tr className="border-b border-border-subtle transition-colors hover:bg-surface-2/30">
      <th scope="row" className="sticky left-0 z-10 bg-surface px-4 py-2.5 text-left align-top">
        <div className="flex items-baseline gap-1.5">
          <span className="text-sm font-medium text-text-primary">{p.name}</span>
          {p.symbol && <span className="font-mono text-xs text-text-tertiary">{p.symbol}</span>}
        </div>
        <div className="mt-0.5 flex flex-wrap items-center gap-x-2 text-[0.6875rem] text-text-tertiary">
          {p.unit && p.unit !== "1" && <span className="font-mono">{p.unit.replace(/\*/g, "·")}</span>}
          {p.standard && <span>{p.standard}</span>}
        </div>
      </th>
      {cols.map((m) => (
        <td key={m.id} className="border-l border-border-subtle px-4 py-2.5 align-top">
          <Cell
            cell={cellById(m.id)}
            row={p}
            color={colOf(m.id)}
            isMax={p.max_material_id === m.id}
            isMin={p.min_material_id === m.id}
          />
        </td>
      ))}
    </tr>
  );
}

function Cell({
  cell, row, color, isMax, isMin,
}: { cell: CompareCell | null; row: CompareProperty; color: string; isMax: boolean; isMin: boolean }) {
  if (!cell || (cell.value === null && !cell.value_text)) {
    return <span className="text-sm text-text-disabled">—</span>;
  }
  const disp = cell.value !== null ? formatValue(cell.value, null) : cell.value_text;
  const cond = formatConditions(cell.conditions);
  const tm = tierMeta(cell.tier);
  const href = cell.source?.url || (cell.source?.doi ? `https://doi.org/${cell.source.doi}` : null);
  const srcLabel = cell.source?.manufacturer || cell.source?.title;
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline gap-1">
        <span className="font-mono text-sm font-semibold tabular-nums text-text-primary">{disp}</span>
        {isMax && row.present > 1 && <ChevronUp className="size-3 text-accent" aria-label="이 행에서 최대" />}
        {isMin && row.present > 1 && <ChevronDown className="size-3 text-text-tertiary" aria-label="이 행에서 최소" />}
      </div>
      {/* 상대 막대(전부 비음수일 때만 rel 존재) */}
      {typeof cell.rel === "number" && (
        <div className="h-1 w-full max-w-[120px] overflow-hidden rounded-full bg-surface-2">
          <div className="h-full rounded-full" style={{ width: `${Math.max(2, cell.rel * 100)}%`, background: color }} />
        </div>
      )}
      <div className="flex flex-wrap items-center gap-x-1.5 gap-y-0.5 text-[0.625rem] text-text-tertiary">
        <span className={cn("inline-flex items-center rounded-sm border px-1 py-px font-medium", tm.cls)}>
          {cell.tier}·{tm.label}
        </span>
        {cond && <span title={cond} className="max-w-[110px] truncate">{cond}</span>}
        {srcLabel && (
          href ? (
            <a href={href} target="_blank" rel="noopener noreferrer" title={cell.source?.title || undefined}
               className="inline-flex max-w-[110px] items-center gap-0.5 truncate transition-colors hover:text-info hover:underline">
              <span className="truncate">{srcLabel}</span><ExternalLink className="size-2.5 shrink-0" />
            </a>
          ) : (
            <span title={cell.source?.title || undefined} className="max-w-[110px] truncate">{srcLabel}</span>
          )
        )}
      </div>
    </div>
  );
}

// 재료 추가 다이얼로그 — 검색 → 결과 리스트(제조사·계열·물성수). 이미 선택된 건 제외.
function AddDialog({
  open, onOpenChange, exclude, onPick,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  exclude: number[];
  onPick: (m: CatalogMaterial) => void;
}) {
  const [q, setQ] = React.useState("");
  const [dq, setDq] = React.useState("");
  React.useEffect(() => {
    const t = setTimeout(() => setDq(q), 200);
    return () => clearTimeout(t);
  }, [q]);
  const listQ = useQuery({
    queryKey: ["catalog", "materials", { q: dq, sort: "properties" }],
    queryFn: () => listCatalogMaterials({ q: dq || undefined, sort: "properties" }),
    enabled: open,
    placeholderData: keepPreviousData,
  });
  const items = (listQ.data?.items ?? []).filter((m) => !exclude.includes(m.id)).slice(0, 40);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>재료 추가</DialogTitle>
          <DialogDescription>비교에 추가할 재료를 검색해 고르세요.</DialogDescription>
        </DialogHeader>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-text-tertiary" />
          <Input autoFocus value={q} onChange={(e) => setQ(e.target.value)} placeholder="재료·코드 검색" className="pl-8" />
        </div>
        <div className="max-h-[50vh] overflow-y-auto">
          {items.length === 0 ? (
            <p className="px-1 py-6 text-center text-sm text-text-tertiary">
              {listQ.isPending ? "불러오는 중…" : "결과 없음"}
            </p>
          ) : (
            <ul className="flex flex-col gap-0.5">
              {items.map((m) => (
                <li key={m.id}>
                  <button
                    onClick={() => onPick(m)}
                    className="flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-left transition-colors hover:bg-surface-2"
                  >
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium text-text-primary">{m.name}</div>
                      <div className="flex flex-wrap items-center gap-1.5 text-[0.6875rem] text-text-tertiary">
                        {m.manufacturer && <span>{m.manufacturer}</span>}
                        {m.material_class && <span>· {m.material_class}</span>}
                        {m.subsystem && <span>· {subsystemLabel(m.subsystem)}</span>}
                      </div>
                    </div>
                    <span className="tnum shrink-0 text-xs text-text-tertiary">물성 {m.n_properties}</span>
                    <Plus className="size-4 shrink-0 text-text-tertiary" />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
