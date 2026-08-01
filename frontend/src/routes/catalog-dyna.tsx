// LS-DYNA 카드 내보내기(/catalog/dyna) — 'MID, 재료명' 행 붙여넣기 → 후보 리스트박스 선택 → 덱 일괄 생성.
import * as React from "react";
import { Link } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import {
  ChevronLeft, FileCode2, Wand2, Copy, Download, Check, AlertTriangle, X,
} from "lucide-react";
import {
  matchDynaRows, buildDynaDeck, type DynaMatch, type DynaDeck, type DynaRow,
} from "../api/catalog";
import { Button } from "../components/ui/button";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { EmptyState } from "../components/states/EmptyState";
import { cn } from "../lib/utils";

const SAMPLE = `101, SUS304
102, 전해동박
103, Kapton
104, Al6061`;

// MID, PID, 재료명 3열 예시 — PID를 주면 CTE 카드까지 생성된다.
const SAMPLE_PID = `101, 5, SUS304
102, 11;12, 전해동박
103, 7, Kapton`;

const UNITS = [
  { key: "ton_mm_s", label: "ton, mm, s (MPa)" },
  { key: "kg_m_s", label: "kg, m, s (Pa, SI)" },
  { key: "g_mm_ms", label: "g, mm, ms (MPa)" },
  { key: "kg_mm_ms", label: "kg, mm, ms (GPa)" },
];

export function CatalogDynaScreen() {
  const [rows, setRows] = React.useState(SAMPLE);
  const [midStart, setMidStart] = React.useState(1);
  const [card, setCard] = React.useState("mechanical");
  const [units, setUnits] = React.useState("ton_mm_s");
  // 행별 선택된 재료 id(리스트박스 선택). key=행 인덱스.
  const [picked, setPicked] = React.useState<Record<number, number | null>>({});
  const [match, setMatch] = React.useState<DynaMatch | null>(null);
  const [deck, setDeck] = React.useState<DynaDeck | null>(null);
  const [copied, setCopied] = React.useState(false);

  const matchMut = useMutation({
    mutationFn: () => matchDynaRows(rows, midStart),
    onSuccess: (d) => {
      setMatch(d);
      setDeck(null);
      // 최상위 후보를 기본 선택.
      const init: Record<number, number | null> = {};
      d.rows.forEach((r, i) => { init[i] = r.candidates[0]?.material_id ?? null; });
      setPicked(init);
    },
  });

  const buildMut = useMutation({
    mutationFn: () => {
      const picks = (match?.rows ?? [])
        .map((r, i) => ({ mid: r.mid, material_id: picked[i] as number, pids: r.pids }))
        .filter((p) => p.material_id != null);
      return buildDynaDeck(picks, card, units);
    },
    onSuccess: setDeck,
  });

  const nPicked = Object.values(picked).filter((v) => v != null).length;

  const copy = async () => {
    if (!deck) return;
    await navigator.clipboard.writeText(deck.keyword);
    setCopied(true);
    setTimeout(() => setCopied(false), 1600);
  };
  const download = () => {
    if (!deck) return;
    const blob = new Blob([deck.keyword], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `materialtwin_${deck.card}_${deck.units.key}.k`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <Link to="/catalog" className="inline-flex items-center gap-1 text-sm text-text-secondary transition-colors hover:text-text-primary">
          <ChevronLeft className="size-4" /> 물성 카탈로그
        </Link>
      </div>

      <header className="flex flex-col gap-1">
        <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.08em] text-text-tertiary">
          <FileCode2 className="size-3.5 text-primary" /> LS-DYNA Card Export
        </div>
        <h1 className="text-2xl font-semibold tracking-[-0.01em] text-text-primary">LS-DYNA 카드 내보내기</h1>
        <p className="text-sm text-text-secondary">
          <span className="font-mono text-xs">MID, 재료명</span> 형식으로 여러 행을 붙여넣으면 재료를 매칭합니다.
          행마다 후보 중 하나를 고르고 확인하면 키워드 덱이 한 번에 생성됩니다.
        </p>
      </header>

      {/* ── 1단계: 입력 ── */}
      <Card className="flex flex-col gap-3 p-4">
        <div className="flex items-center gap-2">
          <span className="flex size-5 items-center justify-center rounded-full bg-primary-muted text-[0.6875rem] font-semibold text-[var(--primary-hover)]">1</span>
          <span className="text-sm font-semibold text-text-primary">재료 행 붙여넣기</span>
        </div>
        <textarea
          value={rows}
          onChange={(e) => setRows(e.target.value)}
          rows={7}
          spellCheck={false}
          className="w-full resize-y rounded-md border border-border-default bg-inset p-3 font-mono text-xs text-text-primary focus:outline-none focus:ring-1 focus:ring-[color:var(--focus-ring)]"
          placeholder={"101, SUS304\n102, 전해동박\n(MID 생략 시 자동 배정)"}
        />
        <div className="flex flex-wrap items-center gap-2 text-[0.6875rem] text-text-tertiary">
          <span>형식:</span>
          <code className="rounded-sm bg-surface-2 px-1.5 py-0.5 font-mono">MID, 재료명</code>
          <span>또는</span>
          <code className="rounded-sm bg-surface-2 px-1.5 py-0.5 font-mono">MID, PID, 재료명</code>
          <span>— PID를 주면 CTE(*MAT_ADD_THERMAL_EXPANSION)까지 생성. 여러 PART는 <code className="font-mono">5;6;7</code></span>
          <button onClick={() => setRows(SAMPLE_PID)}
                  className="ml-auto text-text-secondary underline-offset-2 hover:text-text-primary hover:underline">
            PID 예시 넣기
          </button>
        </div>
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1">
            <span className="text-xs font-medium text-text-tertiary">MID 시작(자동 배정분)</span>
            <input
              type="number" min={1} value={midStart}
              onChange={(e) => setMidStart(Math.max(1, Number(e.target.value) || 1))}
              className="h-9 w-28 rounded-md border border-border-default bg-surface px-2 text-sm text-text-primary"
            />
          </label>
          <Button onClick={() => matchMut.mutate()} disabled={matchMut.isPending || !rows.trim()}>
            <Wand2 className="size-4" />
            {matchMut.isPending ? "매칭 중…" : "재료 매칭"}
          </Button>
          {matchMut.isError && <span className="text-xs text-danger">매칭 실패 — 입력을 확인하세요.</span>}
        </div>
      </Card>

      {/* ── 2단계: 매칭 선택 ── */}
      {match && (
        <Card className="flex flex-col gap-3 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex size-5 items-center justify-center rounded-full bg-primary-muted text-[0.6875rem] font-semibold text-[var(--primary-hover)]">2</span>
            <span className="text-sm font-semibold text-text-primary">매칭 확인 · 재료 선택</span>
            <span className="text-xs text-text-tertiary">
              {match.rows.length}행 중 {nPicked}개 선택됨
            </span>
          </div>

          {match.mid_warnings?.length > 0 && (
            <div className="flex items-start gap-2 rounded-md border border-[color:var(--warning)] bg-transparent px-3 py-2 text-xs text-warning">
              <AlertTriangle className="mt-0.5 size-3.5 shrink-0" />
              <div>{match.mid_warnings.join(" · ")}</div>
            </div>
          )}

          <div className="flex flex-col gap-2">
            {match.rows.map((r, i) => (
              <RowPicker
                key={i}
                row={r}
                value={picked[i] ?? null}
                onChange={(v) => setPicked((p) => ({ ...p, [i]: v }))}
              />
            ))}
          </div>

          <div className="flex flex-wrap items-end gap-3 border-t border-border-subtle pt-3">
            <label className="flex flex-col gap-1">
              <span className="text-xs font-medium text-text-tertiary">카드 종류</span>
              <select value={card} onChange={(e) => setCard(e.target.value)}
                      className="h-9 rounded-md border border-border-default bg-surface px-2 text-sm text-text-primary">
                <option value="mechanical">기계 (*MAT_ELASTIC / *MAT_024)</option>
                <option value="thermal">열 (*MAT_THERMAL_ISOTROPIC)</option>
                <option value="both">둘 다</option>
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs font-medium text-text-tertiary">단위계</span>
              <select value={units} onChange={(e) => setUnits(e.target.value)}
                      className="h-9 rounded-md border border-border-default bg-surface px-2 text-sm text-text-primary">
                {UNITS.map((u) => <option key={u.key} value={u.key}>{u.label}</option>)}
              </select>
            </label>
            <Button onClick={() => buildMut.mutate()} disabled={buildMut.isPending || nPicked === 0}>
              <FileCode2 className="size-4" />
              {buildMut.isPending ? "생성 중…" : `키워드 생성 (${nPicked}종)`}
            </Button>
          </div>
        </Card>
      )}

      {/* ── 3단계: 결과 덱 ── */}
      {deck && (
        <Card className="flex flex-col gap-3 p-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex size-5 items-center justify-center rounded-full bg-accent-muted text-[0.6875rem] font-semibold text-accent">3</span>
            <span className="text-sm font-semibold text-text-primary">LS-DYNA 덱</span>
            <Badge variant="accent">{deck.n_materials}종</Badge>
            <Badge variant="outline">{deck.units.label}</Badge>
            <div className="ml-auto flex gap-2">
              <Button variant="outline" size="sm" onClick={copy}>
                {copied ? <Check className="size-4 text-accent" /> : <Copy className="size-4" />}
                {copied ? "복사됨" : "복사"}
              </Button>
              <Button variant="outline" size="sm" onClick={download}>
                <Download className="size-4" /> .k 저장
              </Button>
            </div>
          </div>

          {deck.skipped.length > 0 && (
            <div className="flex flex-col gap-1 rounded-md border border-[color:var(--warning)] px-3 py-2 text-xs text-warning">
              <div className="flex items-center gap-1.5 font-medium">
                <AlertTriangle className="size-3.5" /> 물성 부족으로 생성하지 못한 카드 {deck.skipped.length}건
              </div>
              {deck.skipped.slice(0, 6).map((s, i) => (
                <div key={i} className="pl-5 text-text-tertiary">
                  {s.material} · {s.card} — {s.reason}
                </div>
              ))}
            </div>
          )}

          <pre className="max-h-[520px] overflow-auto rounded-md bg-inset p-3 font-mono text-[0.6875rem] leading-relaxed text-text-secondary">
            {deck.keyword}
          </pre>
        </Card>
      )}

      {!match && !matchMut.isPending && (
        <EmptyState
          icon={<FileCode2 className="size-6" />}
          title="재료 행을 붙여넣고 매칭하세요"
          description="MID를 지정하면 그대로 사용하고, 생략하면 자동으로 번호를 매깁니다."
        />
      )}
    </div>
  );
}

// 한 행 — 좌측에 MID·질의, 우측에 후보 리스트박스(매칭도 순).
function RowPicker({
  row, value, onChange,
}: { row: DynaRow; value: number | null; onChange: (v: number | null) => void }) {
  return (
    <div className="grid grid-cols-1 gap-2 rounded-md border border-border-subtle p-2.5 md:grid-cols-[150px_minmax(0,1fr)]">
      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-1.5">
          <span className="font-mono text-sm font-semibold tabular-nums text-text-primary">
            MID {row.mid}
          </span>
          <Badge variant={row.mid_source === "지정" ? "info" : "outline"} className="text-[0.625rem]">
            {row.mid_source}
          </Badge>
        </div>
        {row.pids?.length > 0 && (
          <span className="font-mono text-[0.625rem] text-accent" title="PART 지정 — CTE 카드 생성">
            PID {row.pids.join(", ")} · CTE
          </span>
        )}
        <span className="truncate font-mono text-[0.6875rem] text-text-tertiary" title={row.query}>
          "{row.query}"
        </span>
      </div>

      {row.unmatched ? (
        <div className="flex items-center gap-1.5 text-xs text-danger">
          <X className="size-3.5" /> 일치하는 재료가 없습니다 — 이 행은 제외됩니다.
        </div>
      ) : (
        <select
          size={Math.min(row.candidates.length, 4)}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value ? Number(e.target.value) : null)}
          className={cn(
            "w-full rounded-md border border-border-default bg-surface px-1 py-1 font-mono text-xs text-text-primary",
            "focus:outline-none focus:ring-1 focus:ring-[color:var(--focus-ring)]",
          )}
        >
          {row.candidates.map((c) => (
            <option key={c.material_id} value={c.material_id} className="py-0.5">
              {`${(c.score * 100).toFixed(0)}%  ${c.name}`}
              {c.manufacturer ? ` · ${c.manufacturer}` : ""}
              {`  [${c.has_mechanical ? "기계" : "기계✗"}/${c.has_thermal ? "열" : "열✗"}] 물성${c.n_properties}`}
            </option>
          ))}
        </select>
      )}
    </div>
  );
}
