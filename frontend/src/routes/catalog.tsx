// 물성 카탈로그(/catalog) — 요약 타일 + 패싯 필터 레일 + 재료 그리드(도메인·제조사·물성수).
import * as React from "react";
import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { Search, X, Factory, Layers, Boxes, Database, FlaskConical, ChevronRight } from "lucide-react";
import {
  getCatalogSummary,
  listCatalogMaterials,
  type CatalogMaterial,
  type Facet,
} from "../api/catalog";
import { cn } from "../lib/utils";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { TableSkeleton } from "../components/states/Skeletons";
import { domainMeta, subsystemLabel } from "../lib/catalog-ui";

type CatSearch = {
  q?: string; subsystem?: string; category?: string;
  manufacturer?: string; class?: string; domain?: string; sort?: string;
};

export function CatalogScreen() {
  const search = useSearch({ from: "/catalog" }) as CatSearch;
  const navigate = useNavigate();
  const [q, setQ] = React.useState(search.q ?? "");

  const setFilter = React.useCallback(
    (patch: Partial<CatSearch>) =>
      navigate({
        to: "/catalog",
        search: (prev: CatSearch) => {
          const next = { ...prev, ...patch };
          for (const k of Object.keys(next) as (keyof CatSearch)[])
            if (!next[k]) delete next[k];
          return next;
        },
        replace: true,
      }),
    [navigate],
  );

  React.useEffect(() => {
    if ((q || "") === (search.q ?? "")) return;
    const t = setTimeout(() => setFilter({ q: q || undefined }), 250);
    return () => clearTimeout(t);
  }, [q, search.q, setFilter]);

  const summaryQ = useQuery({ queryKey: ["catalog", "summary"], queryFn: getCatalogSummary });
  const filters = {
    q: search.q, subsystem: search.subsystem, category: search.category,
    manufacturer: search.manufacturer, material_class: search.class,
    domain: search.domain, sort: search.sort,
  };
  const matsQ = useQuery({
    queryKey: ["catalog", "materials", filters],
    queryFn: () => listCatalogMaterials(filters),
    placeholderData: keepPreviousData,
  });

  const activeFilters = (
    [
      ["subsystem", search.subsystem, subsystemLabel(search.subsystem)],
      ["category", search.category, search.category],
      ["manufacturer", search.manufacturer, search.manufacturer],
      ["class", search.class, search.class],
      ["domain", search.domain, domainMeta(search.domain ?? "").label],
    ] as const
  ).filter(([, v]) => v);

  const t = summaryQ.data?.totals;

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.08em] text-text-tertiary">
          <FlaskConical className="size-3.5 text-primary" /> Material Property Catalog
        </div>
        <h1 className="text-2xl font-semibold tracking-[-0.01em] text-text-primary">물성 카탈로그</h1>
        <p className="text-sm text-text-secondary">
          스마트폰 내부 재질의 화·물리 물성을 근거(출처·조건·신뢰등급)와 함께 조회합니다.
        </p>
      </header>

      {/* 요약 스탯 타일 */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <StatTile icon={<Boxes className="size-4" />} label="재료" value={t?.materials} />
        <StatTile icon={<Database className="size-4" />} label="물성값" value={t?.values} accent />
        <StatTile icon={<Layers className="size-4" />} label="도메인" value={t?.domains} />
        <StatTile
          icon={<Boxes className="size-4" />}
          label="커버리지"
          value={t ? `${t.covered}/${t.materials}` : undefined}
        />
        <StatTile icon={<Factory className="size-4" />} label="출처" value={t?.sources} />
      </div>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        {/* 패싯 레일 */}
        <aside className="flex w-full shrink-0 flex-col gap-5 lg:w-60">
          <div className="relative">
            <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-text-tertiary" />
            <Input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="재료·코드 검색"
              className="pl-8"
            />
          </div>
          <FacetGroup
            title="서브시스템"
            facets={summaryQ.data?.facets.subsystem}
            active={search.subsystem}
            label={(v) => subsystemLabel(v)}
            onPick={(v) => setFilter({ subsystem: v === search.subsystem ? undefined : v })}
          />
          <FacetGroup
            title="도메인"
            facets={summaryQ.data?.facets.domain}
            active={search.domain}
            label={(v) => domainMeta(v).label}
            dot={(v) => domainMeta(v).color}
            onPick={(v) => setFilter({ domain: v === search.domain ? undefined : v })}
          />
          <FacetGroup
            title="제조사"
            facets={summaryQ.data?.facets.manufacturer}
            active={search.manufacturer}
            max={12}
            onPick={(v) => setFilter({ manufacturer: v === search.manufacturer ? undefined : v })}
          />
          <FacetGroup
            title="카테고리"
            facets={summaryQ.data?.facets.category}
            active={search.category}
            onPick={(v) => setFilter({ category: v === search.category ? undefined : v })}
          />
        </aside>

        {/* 메인: 활성 필터 + 그리드 */}
        <section className="flex min-w-0 flex-1 flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-sm text-text-secondary">
              {matsQ.data ? `${matsQ.data.total}종` : "…"}
            </span>
            {activeFilters.map(([k, , lbl]) => (
              <button
                key={k}
                onClick={() => setFilter({ [k]: undefined } as Partial<CatSearch>)}
                className="inline-flex items-center gap-1 rounded-sm border border-border-default bg-surface-2 px-2 py-0.5 text-xs text-text-secondary transition-colors hover:text-text-primary"
              >
                {lbl}
                <X className="size-3" />
              </button>
            ))}
            {activeFilters.length > 0 && (
              <button
                onClick={() =>
                  navigate({ to: "/catalog", search: search.q ? { q: search.q } : {}, replace: true })
                }
                className="text-xs text-text-tertiary underline-offset-2 hover:text-text-secondary hover:underline"
              >
                모두 지우기
              </button>
            )}
            <div className="ml-auto">
              <select
                value={search.sort ?? "properties"}
                onChange={(e) => setFilter({ sort: e.target.value })}
                className="rounded-sm border border-border-default bg-surface px-2 py-1 text-xs text-text-secondary focus:outline-none focus:ring-1 focus:ring-[color:var(--focus-ring)]"
              >
                <option value="properties">물성 많은 순</option>
                <option value="name">이름순</option>
                <option value="id">등록순</option>
              </select>
            </div>
          </div>

          {matsQ.isError ? (
            <ErrorState onRetry={() => matsQ.refetch()} />
          ) : matsQ.isLoading ? (
            <TableSkeleton rows={6} />
          ) : matsQ.data && matsQ.data.items.length === 0 ? (
            <EmptyState title="해당 재료 없음" description="필터를 조정해 보세요." />
          ) : (
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {matsQ.data?.items.map((m) => <MaterialCard key={m.id} m={m} />)}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function StatTile({
  icon, label, value, accent,
}: { icon: React.ReactNode; label: string; value?: number | string; accent?: boolean }) {
  return (
    <Card className="flex flex-col gap-1 px-4 py-3">
      <div className="flex items-center gap-1.5 text-xs font-medium text-text-tertiary">
        <span className={accent ? "text-accent" : "text-text-tertiary"}>{icon}</span>
        {label}
      </div>
      <div
        className={cn(
          "font-mono text-xl font-semibold tabular-nums tracking-tight",
          accent ? "text-accent" : "text-text-primary",
        )}
      >
        {value ?? "—"}
      </div>
    </Card>
  );
}

function FacetGroup({
  title, facets, active, onPick, label, dot, max = 8,
}: {
  title: string;
  facets?: Facet[];
  active?: string;
  onPick: (v: string) => void;
  label?: (v: string) => string;
  dot?: (v: string) => string;
  max?: number;
}) {
  const [expanded, setExpanded] = React.useState(false);
  if (!facets || facets.length === 0) return null;
  const shown = expanded ? facets : facets.slice(0, max);
  return (
    <div className="flex flex-col gap-1.5">
      <div className="text-xs font-semibold uppercase tracking-[0.06em] text-text-tertiary">{title}</div>
      <div className="flex flex-col gap-0.5">
        {shown.map((f) => {
          const on = active === f.value;
          return (
            <button
              key={f.value}
              onClick={() => onPick(f.value)}
              className={cn(
                "group flex items-center gap-2 rounded-sm px-2 py-1 text-left text-sm transition-colors",
                on ? "bg-primary-muted text-text-primary" : "text-text-secondary hover:bg-surface-2 hover:text-text-primary",
              )}
            >
              {dot && (
                <span className="size-2 shrink-0 rounded-full" style={{ background: dot(f.value) }} />
              )}
              <span className="min-w-0 flex-1 truncate">{label ? label(f.value) : f.value}</span>
              <span className="shrink-0 font-mono text-xs tabular-nums text-text-tertiary">{f.count}</span>
            </button>
          );
        })}
        {facets.length > max && (
          <button
            onClick={() => setExpanded((e) => !e)}
            className="px-2 py-0.5 text-left text-xs text-text-tertiary hover:text-text-secondary"
          >
            {expanded ? "접기" : `+${facets.length - max}개 더`}
          </button>
        )}
      </div>
    </div>
  );
}

function MaterialCard({ m }: { m: CatalogMaterial }) {
  return (
    <Link to="/catalog/$mid" params={{ mid: String(m.id) }} className="group block">
      <Card className="flex h-full flex-col gap-3 p-4 transition-colors hover:border-border-strong">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <div className="truncate text-sm font-semibold text-text-primary">{m.name}</div>
            {m.material_class && (
              <div className="truncate text-xs text-text-tertiary">{m.material_class}</div>
            )}
          </div>
          <ChevronRight className="mt-0.5 size-4 shrink-0 text-text-disabled transition-colors group-hover:text-text-secondary" />
        </div>

        <div className="flex flex-wrap items-center gap-1.5">
          {m.manufacturer && (
            <Badge variant="outline" className="gap-1">
              <Factory className="size-3" /> {m.manufacturer}
            </Badge>
          )}
          {m.grade && <Badge variant="info">{m.grade}</Badge>}
          {m.subsystem && <Badge variant="accent">{subsystemLabel(m.subsystem)}</Badge>}
          {m.category && !m.subsystem && <Badge variant="outline">{m.category}</Badge>}
        </div>

        <div className="mt-auto flex items-center justify-between gap-2 border-t border-border-subtle pt-2.5">
          <div className="flex items-center gap-1">
            {m.domains.map((d) => {
              const dm = domainMeta(d);
              return (
                <span
                  key={d}
                  title={dm.label}
                  className="size-2.5 rounded-full"
                  style={{ background: dm.color }}
                />
              );
            })}
          </div>
          <span className="font-mono text-xs tabular-nums text-text-secondary">
            물성 {m.n_properties}
          </span>
        </div>
      </Card>
    </Link>
  );
}
