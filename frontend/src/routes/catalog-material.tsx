// 물성 카탈로그 재료 상세(/catalog/$mid) — 메타데이터 헤더 + 도메인별 물성표(값·조건·신뢰등급·출처).
import { Link, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  ChevronLeft, ExternalLink, Factory, FileText, Beaker, SearchX, Info, GitCompare, FlaskConical,
  Ruler, Layers, TriangleAlert,
} from "lucide-react";
import { getCatalogMaterial, type PropertyValueRow, type PropertySource } from "../api/catalog";
import { ApiError } from "../api/client";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import {
  domainMeta, tierMeta, tierBadge, METHOD_LABEL, formatValue, formatConditions, subsystemLabel,
  separatedByLabel, tieMessage, conditionDelta, condValue,
} from "../lib/catalog-ui";
import { cn } from "../lib/utils";

// 도메인 표시 순서(기계→열→전기→물리→광학→…). 정의 외 도메인은 뒤에 알파벳순.
const DOMAIN_ORDER = [
  "mechanical", "interface", "thermal", "electrical", "physical", "optical",
  "magnetic", "chemical", "acoustic", "rheological", "structure",
];

export function CatalogMaterialScreen() {
  const { mid } = useParams({ from: "/catalog/$mid" });
  const id = Number(mid);
  const invalid = !Number.isInteger(id) || id <= 0;

  const q = useQuery({
    queryKey: ["catalog", "material", id],
    queryFn: () => getCatalogMaterial(id),
    enabled: !invalid,
    retry: (n, e) => !(e instanceof ApiError && e.status === 404) && n < 2,
  });

  const notFound =
    invalid || (q.isError && q.error instanceof ApiError && q.error.status === 404);
  if (notFound) {
    return (
      <div className="flex flex-col gap-6">
        <BackLink />
        <EmptyState
          icon={<SearchX className="size-6" />}
          title="재료를 찾을 수 없습니다"
          description="삭제되었거나 존재하지 않는 재료입니다."
          action={<Link to="/catalog"><Button>카탈로그로</Button></Link>}
        />
      </div>
    );
  }

  const d = q.data;
  const meta = d?.metadata ?? {};
  const domainKeys = d
    ? Object.keys(d.domains).sort(
        (a, b) => orderIdx(a) - orderIdx(b) || a.localeCompare(b),
      )
    : [];
  const nSources = d
    ? new Set(
        Object.values(d.domains).flat()
          .map((r) => r.source?.title || r.source?.manufacturer)
          .filter(Boolean),
      ).size
    : 0;

  return (
    <div className="flex flex-col gap-6">
      <BackLink />

      {q.isError ? (
        <ErrorState onRetry={() => q.refetch()} />
      ) : (
        <>
          {/* ── 메타데이터 헤더 ── */}
          <header className="flex flex-col gap-4">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div className="min-w-0">
                <p className="text-overline">물성 카탈로그</p>
                {q.isPending ? (
                  <Skeleton className="mt-2 h-8 w-64" />
                ) : (
                  <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
                    {d?.name}
                  </h1>
                )}
                <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-text-tertiary">
                  {d?.material_code && <span className="tnum">{d.material_code}</span>}
                  {meta.trade_name && <span>상품명 {meta.trade_name}</span>}
                  {meta.composition && <span className="tnum">{meta.composition}</span>}
                </div>
              </div>
              {!q.isPending && (
                <div className="flex shrink-0 flex-col items-end gap-3">
                  <div className="flex gap-2">
                    {/* 재료 상세는 시험 곡선까지 함께 보여준다 — 두 화면을 오갈 수 있게 연결. */}
                    <Link to="/materials/$id" params={{ id: String(id) }}>
                      <Button variant="ghost" size="sm">
                        <FlaskConical className="size-4" /> 시험 데이터
                      </Button>
                    </Link>
                    <Link to="/catalog/compare" search={{ ids: String(id) }}>
                      <Button variant="outline" size="sm">
                        <GitCompare className="size-4" /> 비교에 추가
                      </Button>
                    </Link>
                  </div>
                  <div className="flex items-center gap-4 rounded-md border border-border-subtle bg-surface px-4 py-2">
                    <Stat label="물성값" value={d?.n_values} />
                    <div className="h-8 w-px bg-border-subtle" />
                    <Stat label="도메인" value={domainKeys.length} />
                    <div className="h-8 w-px bg-border-subtle" />
                    <Stat label="출처" value={nSources} />
                    {/* 대표값 하나만 세면 "후보가 더 있다" 가 화면 어디에도 안 남는다. */}
                    <div className="h-8 w-px bg-border-subtle" />
                    <Stat
                      label="대안 있음"
                      value={d?.alternatives?.keys}
                      hint={`후보가 둘 이상인 물성 ${d?.alternatives?.keys ?? 0}개 · 그중 순위가 동률인 것 ${d?.alternatives?.ties ?? 0}개`}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* 메타데이터 배지 행 */}
            {q.isPending ? (
              <Skeleton className="h-6 w-96" />
            ) : (
              <div className="flex flex-wrap items-center gap-1.5">
                {meta.manufacturer && (
                  <Badge variant="outline" className="gap-1">
                    <Factory className="size-3" /> {meta.manufacturer}
                  </Badge>
                )}
                {meta.grade && <Badge variant="info">grade {meta.grade}</Badge>}
                {meta.material_class && <Badge variant="default">{meta.material_class}</Badge>}
                {meta.subsystem && <Badge variant="accent">{subsystemLabel(meta.subsystem)}</Badge>}
                {d?.category && <Badge variant="outline">{d.category}</Badge>}
                {meta.process && <Badge variant="outline">{meta.process}</Badge>}
                {meta.standard && (
                  <Badge variant="outline" className="gap-1">
                    <FileText className="size-3" /> {meta.standard}
                  </Badge>
                )}
              </div>
            )}

            {d?.description && (
              <p className="max-w-[70ch] text-sm leading-relaxed text-text-secondary">
                {d.description}
              </p>
            )}
          </header>

          {/* ── 도메인 점프 + 신뢰등급 레전드 ── */}
          {!q.isPending && domainKeys.length > 0 && (
            <div className="flex flex-wrap items-center justify-between gap-3 border-y border-border-subtle py-2.5">
              <div className="flex flex-wrap items-center gap-1.5">
                {domainKeys.map((dk) => {
                  const dm = domainMeta(dk);
                  return (
                    <a
                      key={dk}
                      href={`#dom-${dk}`}
                      className="inline-flex items-center gap-1.5 rounded-sm px-2 py-1 text-xs font-medium text-text-secondary transition-colors hover:bg-surface-2 hover:text-text-primary"
                    >
                      <span className="size-2 rounded-full" style={{ background: dm.color }} />
                      {dm.label}
                      <span className="tnum text-text-tertiary">{d!.domains[dk].length}</span>
                    </a>
                  );
                })}
              </div>
              <TierLegend />
            </div>
          )}

          {/* ── 도메인별 물성표 ── */}
          {q.isPending ? (
            <div className="flex flex-col gap-6">
              {[0, 1].map((i) => <Skeleton key={i} className="h-64 w-full" />)}
            </div>
          ) : domainKeys.length === 0 ? (
            <EmptyState
              icon={<Beaker className="size-6" />}
              title="등록된 물성이 없습니다"
              description="이 재료에는 아직 화·물리 물성값이 없습니다."
            />
          ) : (
            <div className="flex flex-col gap-6">
              {domainKeys.map((dk) => (
                <DomainSection key={dk} domain={dk} rows={d!.domains[dk]} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}

function orderIdx(d: string): number {
  const i = DOMAIN_ORDER.indexOf(d);
  return i === -1 ? DOMAIN_ORDER.length : i;
}

function Stat({ label, value, hint }: { label: string; value?: number; hint?: string }) {
  return (
    <div className="flex flex-col" title={hint}>
      <span className="text-[0.6875rem] font-medium text-text-tertiary">{label}</span>
      <span className="font-mono text-lg font-semibold leading-tight tabular-nums text-text-primary">
        {value ?? "—"}
      </span>
    </div>
  );
}

function TierLegend() {
  return (
    <div className="flex items-center gap-2 text-[0.6875rem] text-text-tertiary">
      <Info className="size-3" />
      <span>신뢰등급</span>
      {[1, 2, 3, 4, 5].map((t) => {
        const tm = tierMeta(t);
        return (
          <span key={t} className="inline-flex items-center gap-1">
            <span className={cn("inline-block size-2 rounded-full", tm.cls.replace(/text-\S+/g, ""))} />
            <span>{t} {tm.label}</span>
          </span>
        );
      })}
    </div>
  );
}

function DomainSection({ domain, rows }: { domain: string; rows: PropertyValueRow[] }) {
  const dm = domainMeta(domain);
  return (
    <section id={`dom-${domain}`} className="scroll-mt-6">
      <Card className="overflow-hidden">
        {/* 도메인 헤더 */}
        <div className="flex items-center gap-2 border-b border-border-subtle px-4 py-3">
          <span className="size-2.5 rounded-full" style={{ background: dm.color }} />
          <h2 className="text-sm font-semibold text-text-primary">{dm.label} 물성</h2>
          <span className="tnum text-xs text-text-tertiary">{rows.length}</span>
          <span className="ml-2 rounded-sm bg-surface-2 px-1.5 py-0.5 font-mono text-[0.625rem] uppercase tracking-wide text-text-tertiary">
            {dm.abbr}
          </span>
        </div>

        {/* 컬럼 헤더(md+) */}
        <div className="hidden border-b border-border-subtle px-4 py-2 text-[0.6875rem] font-medium uppercase tracking-[0.04em] text-text-tertiary md:grid md:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)_minmax(0,1.1fr)_minmax(0,1.2fr)] md:gap-4">
          <span>물성</span>
          <span className="text-right">값</span>
          <span>조건</span>
          <span>신뢰 · 출처</span>
        </div>

        <div className="divide-y divide-border-subtle">
          {groupByKey(rows).map((g) => (
            <PropGroup key={g.key} rows={g.rows} />
          ))}
        </div>
      </Card>
    </section>
  );
}

/** 같은 물성키의 행을 한 덩어리로 묶는다 — 응답은 이미 인접해 있지만 순서에 기대지 않는다. */
function groupByKey(rows: PropertyValueRow[]): { key: string; rows: PropertyValueRow[] }[] {
  const out: { key: string; rows: PropertyValueRow[] }[] = [];
  const at = new Map<string, PropertyValueRow[]>();
  for (const r of rows) {
    let bucket = at.get(r.key);
    if (!bucket) {
      bucket = [];
      at.set(r.key, bucket);
      out.push({ key: r.key, rows: bucket });
    }
    bucket.push(r);
  }
  // 대표값을 덩어리 맨 앞으로. 진 행은 뒤에 그대로 남는다 — 감추지 않는다.
  for (const g of out) g.rows.sort((a, b) => Number(b.representative) - Number(a.representative));
  return out;
}

/**
 * 한 물성키의 후보 전부. 대표값을 표시하고, 진 행에는 **대표값과 무엇이 다른지**를 적는다.
 *
 * 행을 접지 않는다(§ "값을 숨기지 마라"). 원래도 상세는 전 행을 보여 주고 있었다 —
 * 빠져 있던 것은 "이 중 어느 것이 카드·비교·Ashby 로 나가는 값인가" 였다.
 */
function PropGroup({ rows }: { rows: PropertyValueRow[] }) {
  const rep = rows.find((r) => r.representative) ?? rows[0];
  const multi = rows.length > 1 || (rep?.n_candidates ?? 1) > 1;
  return (
    <div>
      {rows.map((r, i) => (
        <PropRow
          key={`${r.key}-${i}`}
          r={r}
          multi={multi}
          repConditions={r.representative ? null : (rep?.conditions ?? null)}
        />
      ))}
    </div>
  );
}

function PropRow({
  r, multi = false, repConditions = null,
}: {
  r: PropertyValueRow;
  multi?: boolean;
  repConditions?: Record<string, unknown> | null;
}) {
  const tm = tierBadge(r.tier, r.conditions);
  const cond = formatConditions(r.conditions);
  const valueText =
    r.value !== null ? formatValue(r.value, r.unit) : (r.value_text ?? "—");
  return (
    <div className="px-4 py-3 transition-colors hover:bg-surface-2/40">
      <div className="grid grid-cols-1 gap-x-4 gap-y-2 md:grid-cols-[minmax(0,1.6fr)_minmax(0,1fr)_minmax(0,1.1fr)_minmax(0,1.2fr)]">
        {/* 물성 이름 + 기호 + 표준 */}
        <div className="min-w-0">
          <div className="flex flex-wrap items-baseline gap-1.5">
            <span className="text-sm font-medium text-text-primary">{r.name}</span>
            {r.symbol && <span className="font-mono text-xs text-text-tertiary">{r.symbol}</span>}
            {/* 후보가 둘 이상일 때만 표시한다 — 대부분의 물성에는 후보가 하나뿐이다. */}
            {multi && r.representative && (
              <span
                title={`목록·비교·Ashby·DYNA 카드가 쓰는 값이다. 이 재료·물성의 후보는 ${r.n_candidates}개.`}
                className="inline-flex items-center gap-1 rounded-sm border border-[color:var(--accent)] px-1.5 py-0.5 text-[0.625rem] font-medium text-accent"
              >
                <Layers className="size-3" /> 대표값 · 후보 {r.n_candidates}
              </span>
            )}
            {multi && !r.representative && (
              <span
                title="이 값도 그대로 쓸 수 있다 — 대표값으로 뽑히지 않았을 뿐이다."
                className="rounded-sm border border-border-default px-1.5 py-0.5 text-[0.625rem] text-text-tertiary"
              >
                대안값{r.separated_by ? ` · ${separatedByLabel(r.separated_by)}` : ""}
              </span>
            )}
          </div>
          {r.standard && (
            <div className="mt-0.5 text-[0.6875rem] text-text-tertiary">{r.standard}</div>
          )}
          {/* 값을 보고 "이걸 어떻게 재나" 로 넘어가는 통로. */}
          <Link
            to="/metrology"
            search={{ key: r.key }}
            className="mt-0.5 inline-flex items-center gap-1 text-[0.6875rem] text-text-tertiary transition-colors hover:text-primary"
          >
            <Ruler className="size-3" />
            측정법
          </Link>
        </div>

        {/* 값 + 불확도 */}
        <div className="md:text-right">
          <span className="font-mono text-sm font-semibold tabular-nums text-text-primary">
            {valueText}
          </span>
          {r.uncertainty != null && r.value !== null && (
            <span className="ml-1 font-mono text-xs text-text-tertiary">
              ± {formatValue(r.uncertainty, null)}
            </span>
          )}
          {r.value !== null && r.value_text && (
            <div className="text-[0.6875rem] text-text-tertiary md:text-right">{r.value_text}</div>
          )}
        </div>

        {/* 조건 */}
        <div className="min-w-0 text-xs text-text-secondary">
          {cond || <span className="text-text-disabled">—</span>}
        </div>

        {/* 신뢰 + 출처 */}
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-1.5">
            <span className={cn("inline-flex items-center rounded-sm border px-1.5 py-0.5 text-[0.6875rem] font-medium", tm.cls)}>
              {r.tier} · {tm.label}
            </span>
            <span className="text-[0.6875rem] text-text-tertiary">
              {METHOD_LABEL[r.method] ?? r.method}
            </span>
          </div>
          <SourceLink source={r.source} />
        </div>
      </div>

      {/* 동률 안내 — 대표행에만. 값이 1% 넘게 갈릴 때만 서버가 붙인다(반올림 쌍둥이 제외). */}
      {r.tie && (
        <p className="mt-2 flex max-w-[80ch] items-start gap-1.5 border-l-2 border-[color:var(--warning)] pl-2.5 text-[0.6875rem] leading-relaxed text-text-secondary">
          <TriangleAlert className="mt-0.5 size-3 shrink-0 text-warning" />
          <span>
            {tieMessage(r.tie.kind, r.tie.n_tied, r.tie.condition_keys)}
            {r.tie.max_rel_diff != null && (
              <span className="text-text-tertiary">
                {" "}(값 차이 최대 {Math.round(r.tie.max_rel_diff * 100)}%)
              </span>
            )}
            . 아래 후보를 보고 직접 고를 수 있다.
          </span>
        </p>
      )}

      {/* 대표값과 무엇이 다른가 — 진 행에만. 조건이 안 보이면 대안이 무의미하다. */}
      {!r.representative && repConditions !== null && (
        <ConditionDelta rep={repConditions} alt={r.conditions} />
      )}

      {/* 근거 노트(전폭) */}
      {r.notes && (
        <p className="mt-2 max-w-[80ch] border-l-2 border-border-default pl-2.5 text-[0.6875rem] leading-relaxed text-text-tertiary">
          {r.notes}
        </p>
      )}
    </div>
  );
}

/** 대표값 행과의 조건 차이. 응답에 전 행이 있으므로 화면이 직접 견준다(서버 응답을 안 불린다). */
function ConditionDelta({
  rep, alt,
}: {
  rep: Record<string, unknown> | null;
  alt: Record<string, unknown> | null;
}) {
  const delta = conditionDelta(rep, alt);
  if (delta.length === 0) return null;
  return (
    <p className="mt-1.5 max-w-[80ch] border-l-2 border-border-default pl-2.5 text-[0.6875rem] leading-relaxed text-text-tertiary">
      <span className="text-text-secondary">대표값과 다른 조건</span>{" "}
      {delta.map((d, i) => (
        <span key={d.key}>
          {i > 0 && " · "}
          <span className="font-mono">{d.key}</span> {condValue(d.rep)} →{" "}
          <span className="text-text-secondary">{condValue(d.alt)}</span>
        </span>
      ))}
    </p>
  );
}

function SourceLink({ source }: { source: PropertySource | null }) {
  if (!source) return <span className="text-[0.6875rem] text-text-disabled">출처 미상</span>;
  const href = source.url || (source.doi ? `https://doi.org/${source.doi}` : null);
  const label = source.manufacturer || source.title || source.doi || "출처";
  const inner = (
    <>
      <span className="truncate">{label}</span>
      {href && <ExternalLink className="size-3 shrink-0" />}
    </>
  );
  const title = [source.title, source.detail, source.kind].filter(Boolean).join(" — ");
  if (href) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        title={title || undefined}
        className="inline-flex max-w-full items-center gap-1 text-[0.6875rem] text-text-secondary transition-colors hover:text-info hover:underline"
      >
        {inner}
      </a>
    );
  }
  return (
    <span
      title={title || undefined}
      className="inline-flex max-w-full items-center gap-1 text-[0.6875rem] text-text-tertiary"
    >
      {inner}
    </span>
  );
}

function BackLink() {
  return (
    <div>
      <Link
        to="/catalog"
        className="inline-flex items-center gap-1 text-sm text-text-secondary transition-colors hover:text-text-primary"
      >
        <ChevronLeft className="size-4" />
        물성 카탈로그
      </Link>
    </div>
  );
}
