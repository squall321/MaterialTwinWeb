// 측정 방법(/metrology) — 물성을 고르면 기법별로 묶인 장비·측정범위를 낸다 + 측정공백 목록.
import * as React from "react";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import { Search, Ruler, CircleAlert, Thermometer, FileText, Microscope } from "lucide-react";
import {
  getMetrologySummary,
  getMetrologyCoverage,
  getByProperty,
  kToC,
  rangeText,
  type Capability,
} from "../api/metrology";
import { cn } from "../lib/utils";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { TableSkeleton } from "../components/states/Skeletons";
import { domainMeta } from "../lib/catalog-ui";

export function MetrologyScreen() {
  const [sel, setSel] = React.useState<string | null>(null);
  const [q, setQ] = React.useState("");

  const summary = useQuery({ queryKey: ["metro", "summary"], queryFn: getMetrologySummary });
  const coverage = useQuery({ queryKey: ["metro", "cov"], queryFn: getMetrologyCoverage });
  const detail = useQuery({
    queryKey: ["metro", "prop", sel],
    queryFn: () => getByProperty(sel as string),
    enabled: !!sel,
    placeholderData: keepPreviousData,
  });

  if (summary.isError) return <ErrorState detail={String(summary.error)} onRetry={() => summary.refetch()} />;

  const s = summary.data;
  const empty = s && s.instruments === 0;

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-xl font-medium tracking-[-0.01em]">측정 방법</h1>
        <p className="text-sm text-text-secondary">
          물성 카탈로그가 <span className="text-text-primary">무엇이 얼마인가</span>에 답한다면,
          여기서는 <span className="text-text-primary">그걸 무엇으로 어떻게 재는가</span>에 답한다.
          장비 사양은 제조사 카탈로그에 <span className="text-text-primary">인쇄된 것만</span> 싣는다.
        </p>
      </header>

      {s && (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          <Tile icon={<Microscope className="size-4" />} label="장비" value={s.instruments} />
          <Tile icon={<Ruler className="size-4" />} label="측정 능력" value={s.capabilities} />
          <Tile
            icon={<FileText className="size-4" />}
            label="측정 가능 물성"
            value={`${s.measurable_properties} / ${s.total_properties}`}
          />
          <Tile
            icon={<CircleAlert className="size-4" />}
            label="장비 없는 물성"
            value={s.total_properties - s.measurable_properties}
            tone="warn"
          />
        </div>
      )}

      {empty ? (
        <EmptyState
          title="아직 편입된 장비가 없다"
          description="카탈로그 PDF 추출이 끝나면 여기에 장비와 측정범위가 실린다."
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[300px_1fr]">
          {/* 좌: 물성 고르기 — 장비가 있는 것과 없는 것을 한 목록에서 구분해 보인다 */}
          <div className="flex flex-col gap-3">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-tertiary" />
              <Input
                value={q}
                onChange={(e) => setQ(e.target.value)}
                placeholder="물성 이름·키로 찾기"
                className="pl-9"
              />
            </div>
            <PropertyPicker
              q={q}
              selected={sel}
              onSelect={setSel}
              coverage={coverage.data}
              loading={coverage.isLoading}
            />
          </div>

          {/* 우: 고른 물성의 측정법 */}
          <div className="min-w-0">
            {!sel ? (
              <EmptyState
                title="물성을 고르면 측정법이 나온다"
                description="같은 물성을 여러 기법으로 재는 경우, 기법으로 묶어서 보인다 — 장비 목록이 아니라 방법이 답이다."
              />
            ) : detail.isLoading ? (
              <TableSkeleton />
            ) : detail.isError ? (
              <ErrorState detail={String(detail.error)} onRetry={() => detail.refetch()} />
            ) : detail.data ? (
              <PropertyMethods data={detail.data} />
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
}

function Tile({
  icon,
  label,
  value,
  tone,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
  tone?: "warn";
}) {
  return (
    <Card className="flex flex-col gap-1 p-4">
      <div className="flex items-center gap-1.5 text-xs text-text-tertiary">
        {icon}
        {label}
      </div>
      <div
        className={cn(
          "text-lg font-medium tabular-nums",
          tone === "warn" && "text-warning",
        )}
      >
        {value}
      </div>
    </Card>
  );
}

function PropertyPicker({
  q,
  selected,
  onSelect,
  coverage,
  loading,
}: {
  q: string;
  selected: string | null;
  onSelect: (k: string) => void;
  coverage?: import("../api/metrology").MetrologyCoverage;
  loading: boolean;
}) {
  if (loading) return <TableSkeleton />;

  const match = (k: string, n: string) =>
    !q || k.toLowerCase().includes(q.toLowerCase()) || n.toLowerCase().includes(q.toLowerCase());
  const filtered = (coverage?.covered ?? []).filter((r) => match(r.key, r.name));

  const gapRows = (coverage?.gaps ?? []).filter(
    (g) => match(g.key, g.name),
  );

  return (
    <div className="flex max-h-[70vh] flex-col gap-4 overflow-y-auto pr-1">
      <Section title={`잴 수 있다 (${filtered.length})`}>
        {filtered.map((r) => (
          <PickRow
            key={r.key}
            label={r.name}
            domain={r.domain}
            right={`장비 ${r.instruments}`}
            active={selected === r.key}
            onClick={() => onSelect(r.key)}
          />
        ))}
      </Section>
      <Section title={`장비 없음 (${gapRows.length})`} muted>
        {gapRows.slice(0, 60).map((g) => (
          <PickRow
            key={g.key}
            label={g.name}
            domain={g.domain}
            right={g.values_in_catalog > 0 ? `값 ${g.values_in_catalog}` : "—"}
            active={selected === g.key}
            onClick={() => onSelect(g.key)}
            muted
          />
        ))}
        {gapRows.length > 60 && (
          <p className="px-2 py-1 text-xs text-text-tertiary">
            …외 {gapRows.length - 60}종. 검색으로 좁혀라.
          </p>
        )}
      </Section>
    </div>
  );
}

function Section({
  title,
  muted,
  children,
}: {
  title: string;
  muted?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1">
      <div
        className={cn(
          "px-2 text-xs font-medium uppercase tracking-wide",
          muted ? "text-text-tertiary" : "text-text-secondary",
        )}
      >
        {title}
      </div>
      <div className="flex flex-col gap-0.5">{children}</div>
    </div>
  );
}

function PickRow({
  label,
  domain,
  right,
  active,
  onClick,
  muted,
}: {
  label: string;
  domain: string;
  right: string;
  active: boolean;
  onClick: () => void;
  muted?: boolean;
}) {
  const dm = domainMeta(domain);
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm transition-colors",
        active ? "bg-primary-muted text-text-primary" : "hover:bg-surface-hover",
        muted && !active && "text-text-secondary",
      )}
    >
      <span
        className="size-1.5 shrink-0 rounded-full"
        style={{ background: dm.color }}
        aria-hidden
      />
      <span className="min-w-0 flex-1 truncate">{label}</span>
      <span className="shrink-0 text-xs tabular-nums text-text-tertiary">{right}</span>
    </button>
  );
}

function PropertyMethods({ data }: { data: import("../api/metrology").ByProperty }) {
  const { property: p, techniques, values_in_catalog } = data;
  const dm = domainMeta(p.domain);

  return (
    <div className="flex flex-col gap-4">
      <Card className="flex flex-col gap-2 p-4">
        <div className="flex flex-wrap items-center gap-2">
          <Badge style={{ background: dm.color, color: "white", border: "none" }}>{dm.label}</Badge>
          <h2 className="text-md font-medium">{p.name}</h2>
          <code className="text-xs text-text-tertiary">{p.key}</code>
          {p.si_unit && (
            <span className="text-xs text-text-secondary">SI · {p.si_unit}</span>
          )}
        </div>
        <div className="flex flex-wrap gap-4 text-xs text-text-secondary">
          <span>카탈로그 값 {values_in_catalog.toLocaleString()}개</span>
          {p.test_standard && <span>기준 규격 {p.test_standard}</span>}
          {p.condition_axes?.length ? (
            <span>필수 조건 · {p.condition_axes.join(" · ")}</span>
          ) : null}
        </div>
      </Card>

      {techniques.length === 0 ? (
        <EmptyState
          title="이 물성을 재는 장비가 카탈로그에 없다"
          description={
            values_in_catalog > 0
              ? `카탈로그에 값은 ${values_in_catalog}개 있다 — 문헌에서만 얻은 물성이다. 직접 재려면 장비 카탈로그를 더 넣어야 한다.`
              : "값도 장비도 없다. 이 칸은 지금 구조로는 못 채운다."
          }
        />
      ) : (
        techniques.map((t) => (
          <Card key={t.technique} className="flex flex-col gap-3 p-4">
            <div className="flex flex-wrap items-baseline gap-2">
              <h3 className="text-sm font-medium">{t.technique}</h3>
              {t.standards.map((s) => (
                <Badge key={s} variant="outline" className="text-xs">
                  {s}
                </Badge>
              ))}
              <span className="ml-auto text-xs text-text-tertiary">
                장비 {t.instruments.length}대
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[640px] text-sm">
                <thead>
                  <tr className="border-b border-border-subtle text-left text-xs text-text-tertiary">
                    <th className="py-1.5 pr-3 font-normal">장비</th>
                    <th className="py-1.5 pr-3 font-normal">측정범위</th>
                    <th className="py-1.5 pr-3 font-normal">시편 온도</th>
                    <th className="py-1.5 pr-3 font-normal">정확도</th>
                    <th className="py-1.5 font-normal">시편</th>
                  </tr>
                </thead>
                <tbody>
                  {t.instruments.map((c) => (
                    <CapRow key={c.id} c={c} />
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        ))
      )}
    </div>
  );
}

function CapRow({ c }: { c: Capability }) {
  const lo = kToC(c.temperature_min_k);
  const hi = kToC(c.temperature_max_k);
  const temp =
    lo === null && hi === null
      ? null
      : lo !== null && hi !== null
        ? `${lo} ~ ${hi} °C`
        : hi !== null
          ? `≤ ${hi} °C`
          : `≥ ${lo} °C`;
  return (
    <tr className="border-b border-border-subtle/60 last:border-0 align-top">
      <td className="py-2 pr-3">
        <div className="flex flex-col">
          <span className="font-medium">
            {c.instrument?.vendor} {c.instrument?.model}
          </span>
          {c.mapping_confidence !== "high" && (
            <span className="text-xs text-warning">
              매핑 신뢰도 {c.mapping_confidence} — 우리 키와 정확히 같은 물리량인지 확인이 필요하다
            </span>
          )}
          {c.notes && <span className="text-xs text-text-tertiary">{c.notes}</span>}
        </div>
      </td>
      <td className="py-2 pr-3 tabular-nums">{rangeText(c) ?? <Dash />}</td>
      <td className="py-2 pr-3 tabular-nums">
        {temp ? (
          <span className="inline-flex items-center gap-1">
            <Thermometer className="size-3 text-text-tertiary" />
            {temp}
          </span>
        ) : (
          <Dash />
        )}
      </td>
      <td className="py-2 pr-3">{c.accuracy ?? <Dash />}</td>
      <td className="py-2 text-xs text-text-secondary">{c.specimen ?? <Dash />}</td>
    </tr>
  );
}

/** 안 적힌 것은 안 적혔다고 보인다 — 빈 칸이 틀린 값보다 낫다. */
function Dash() {
  return <span className="text-text-tertiary">—</span>;
}
