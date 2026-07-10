// 업로드 4단계 마법사(/upload, §14.3.1·§8.2) — Drop → Detect&Map → Specimen Meta → Preview&Commit.
import * as React from "react";
import { useNavigate, useSearch } from "@tanstack/react-router";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Check, ChevronRight, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { listMaterials, createMaterial } from "../api/materials";
import { createSpecimen, type GeometryType } from "../api/specimens";
import {
  sniff,
  uploadToSpecimen,
  remapUpload,
  getParsers,
  type SniffResult,
  type IngestResult,
} from "../api/uploads";
import { UploadDropzone } from "../components/UploadDropzone";
import { IssuePanel } from "../components/IssuePanel";
import { ColumnMapper, hasAxisPair } from "../components/ColumnMapper";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { errorMessage } from "../lib/download";
import { cn } from "../lib/utils";

type Step = 0 | 1 | 2 | 3;
const STEP_LABELS = ["파일 선택", "감지·매핑", "시편 정보", "미리보기·등록"];

// 시편 메타 폼 상태(SI 변환은 커밋 시).
type MetaForm = {
  materialId: number | null;
  newMaterialName: string;
  label: string;
  geometry: GeometryType;
  L0_mm: string;
  w0_mm: string;
  t0_mm: string;
  d0_mm: string;
};

const EMPTY_META: MetaForm = {
  materialId: null,
  newMaterialName: "",
  label: "S1",
  geometry: "flat",
  L0_mm: "50",
  w0_mm: "12.5",
  t0_mm: "2",
  d0_mm: "10",
};

export function UploadScreen() {
  const search = useSearch({ from: "/upload" }) as { material?: number };
  const navigate = useNavigate();

  const [step, setStep] = React.useState<Step>(0);
  const [file, setFile] = React.useState<File | null>(null);
  const [sniffResult, setSniffResult] = React.useState<SniffResult | null>(null);
  const [meta, setMeta] = React.useState<MetaForm>({
    ...EMPTY_META,
    materialId: search.material ?? null,
  });
  const [result, setResult] = React.useState<IngestResult | null>(null);
  // 커밋으로 확정된 재료 id(신규 생성 포함) — "재료 보기" 네비게이션용(★BUG-2).
  const [committedMaterialId, setCommittedMaterialId] = React.useState<number | null>(null);
  // 수동 컬럼 매핑 {header: role}. 비어있으면 자동감지. 열림 여부 별도(★C5·수동매핑).
  const [mapping, setMapping] = React.useState<Record<string, string>>({});
  const [showMapper, setShowMapper] = React.useState(false);
  // 등록 중 생성된 재료/시편/시험 id — 중간 단계 실패 후 재시도 시 재사용해 중복 생성을 막는다.
  const [createdIds, setCreatedIds] = React.useState<{
    materialId: number | null;
    specimenId: number | null;
    testId: number | null;
  }>({ materialId: null, specimenId: null, testId: null });
  // 결과 화면(computed=false)에서 매핑 수정 패널 열림 여부.
  const [showResultMapper, setShowResultMapper] = React.useState(false);

  // 재료 정체성(기존 선택 or 새 이름)이 바뀌면 생성해둔 재료 재사용을 취소한다.
  // 시편/시험은 재료 하위이므로 함께 무효화.
  React.useEffect(() => {
    setCreatedIds({ materialId: null, specimenId: null, testId: null });
  }, [meta.materialId, meta.newMaterialName]);

  // 시편 메타(치수·라벨·형상)나 파일이 바뀌면 시편·시험만 재생성 대상(재료 id는 유지).
  // 이전엔 재료 id까지 초기화해, 새 재료로 커밋 중간 실패 후 시편 정보만 고쳐 재시도하면
  // createMaterial이 재실행돼 중복 재료 + 고아 시편이 생겼다.
  React.useEffect(() => {
    setCreatedIds((c) => ({ ...c, specimenId: null, testId: null }));
  }, [meta.label, meta.geometry, meta.L0_mm, meta.w0_mm, meta.t0_mm, meta.d0_mm, file]);

  const materialsQ = useQuery({ queryKey: ["materials", ""], queryFn: () => listMaterials({ size: 100 }) });
  const parsersQ = useQuery({ queryKey: ["parsers"], queryFn: getParsers });

  const sniffMut = useMutation({
    mutationFn: (f: File) => sniff(f),
    onSuccess: (r) => {
      setSniffResult(r);
      setMapping({});
      // 미인식(수동매핑 필요)이면 매퍼를 자동으로 펼친다(★C5).
      setShowMapper(r.needs_manual_mapping);
      setStep(1);
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : "감지 실패"),
  });

  const commitMut = useMutation({
    mutationFn: async () => {
      // 1) 재료 결정(기존 선택 or 새로 생성). 재시도 시 이전 생성분 재사용.
      let mid = meta.materialId ?? createdIds.materialId;
      if (!mid) {
        const m = await stage("재료 생성", () =>
          createMaterial({ name: meta.newMaterialName.trim() }),
        );
        mid = m.id;
        setCreatedIds((s) => ({ ...s, materialId: m.id }));
      }
      const materialId = mid;
      // 2) 시편 생성(mm → m SI 변환). 재시도 시 이전 생성분 재사용.
      let sid = createdIds.specimenId;
      if (!sid) {
        const sp = await stage("시편 생성", () =>
          createSpecimen(materialId, {
            label: meta.label.trim(),
            geometry_type: meta.geometry,
            gauge_length_m: mm(meta.L0_mm),
            width_m: meta.geometry === "flat" ? mm(meta.w0_mm) : null,
            thickness_m: meta.geometry === "flat" ? mm(meta.t0_mm) : null,
            diameter_m: meta.geometry === "round" ? mm(meta.d0_mm) : null,
          }),
        );
        sid = sp.id;
        setCreatedIds((c) => ({ ...c, materialId, specimenId: sp.id }));
      }
      const specimenId = sid;
      // 3) 업로드 → 파싱 → 적재. 이미 만든 test가 있으면(재시도·매핑 수정 재등록)
      //    remap 경로로 기존 test를 대체해 같은 시편에 중복 test가 쌓이지 않게 한다.
      const manual = effectiveMapping(mapping);
      let ingest: IngestResult;
      if (createdIds.testId != null) {
        ingest = await stage("재적재", () => remapUpload(createdIds.testId!, file!, manual));
      } else {
        ingest = await stage("업로드", () => uploadToSpecimen(specimenId, file!));
        setCreatedIds((c) => ({ ...c, testId: ingest.test_id }));
        // 3b) 수동 매핑이 있으면 재파싱(4·5단계만 재실행, ★C5).
        if (Object.keys(manual).length > 0) {
          const tid = ingest.test_id;
          ingest = await stage("매핑 재적재", () => remapUpload(tid, file!, manual));
        }
      }
      return { materialId, ingest };
    },
    onSuccess: ({ materialId, ingest }) => {
      setResult(ingest);
      setCommittedMaterialId(materialId);
      setCreatedIds((c) => ({ ...c, testId: ingest.test_id })); // remap 후 최종 test id로 갱신.
      setStep(3);
      if (ingest.computed) toast.success("등록·물성 계산 완료");
      else toast.warning("등록됨 — 확인이 필요합니다");
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : "등록 실패"),
  });

  // 결과 화면에서 매핑을 고쳐 같은 test에 재적재(computed=false 복구 경로).
  const remapMut = useMutation({
    mutationFn: (m: Record<string, string>) => remapUpload(result!.test_id, file!, m),
    onSuccess: (r) => {
      setResult(r);
      setCreatedIds((c) => ({ ...c, testId: r.test_id })); // 대체된 test id 추적.
      setShowResultMapper(false);
      if (r.computed) toast.success("재적재 완료 — 물성 계산됨");
      else toast.warning("재적재됨 — 여전히 확인이 필요합니다");
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const a0 = computeA0(meta);
  // 1단계 게이트 — ERROR 이슈(하드 파싱 실패)는 매핑으로 못 고치므로 진행을 막는다.
  const sniffHasError = (sniffResult?.issues ?? []).some((i) => i.level === "ERROR");
  const metaReason = metaInvalidReason(meta);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <header>
        <p className="text-overline">업로드</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
          시험 데이터 업로드
        </h1>
      </header>

      {/* 결과 화면에서 되돌아가면 stale 결과를 비워 재등록 dead-end를 막는다(createdIds는
          유지 — 재등록 시 remap 경로로 기존 test를 대체). */}
      <Stepper
        step={step}
        onStepClick={(s) => {
          if (result) {
            setResult(null);
            setCommittedMaterialId(null);
            setShowResultMapper(false);
          }
          setStep(s);
        }}
      />

      {/* 단계 0 — 파일 선택 */}
      {step === 0 && (
        <div className="flex flex-col gap-4">
          <UploadDropzone
            multiple={false}
            files={file ? [file] : []}
            onFiles={(fs) => setFile(fs[0] ?? null)}
            onRemove={() => setFile(null)}
            accept={{ "text/*": [".csv", ".txt", ".tsv"] }}
          />
          <div className="flex justify-end">
            <Button
              disabled={!file || sniffMut.isPending}
              onClick={() => file && sniffMut.mutate(file)}
            >
              {sniffMut.isPending ? (
                <Loader2 className="size-4 animate-spin" />
              ) : (
                <ChevronRight className="size-4" />
              )}
              감지
            </Button>
          </div>
        </div>
      )}

      {/* 단계 1 — 감지·매핑 */}
      {step === 1 && sniffResult && (
        <div className="flex flex-col gap-4">
          <Card className="p-4">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant={sniffResult.needs_manual_mapping ? "warning" : "success"}>
                {sniffResult.needs_manual_mapping ? "수동 매핑 필요" : "자동 감지됨"}
              </Badge>
              <span className="text-sm text-text-secondary">
                파서 <span className="tnum">{sniffResult.parser}</span> · 신뢰도{" "}
                <span className="tnum">{(sniffResult.confidence * 100).toFixed(0)}%</span>
              </span>
            </div>
            {sniffResult.specimen.columns && !showMapper && (
              <div className="mt-3 flex flex-col gap-1.5">
                {sniffResult.specimen.columns.map((c) => (
                  <div key={c.index} className="flex items-center gap-2 text-sm">
                    <span className="tnum w-40 truncate text-text-secondary">{c.header}</span>
                    <ChevronRight className="size-3 text-text-tertiary" />
                    <Badge>{c.role}</Badge>
                    {c.unit && <span className="text-xs text-text-tertiary">{c.unit}</span>}
                  </div>
                ))}
                <button
                  type="button"
                  onClick={() => setShowMapper(true)}
                  className="mt-1 self-start text-sm text-[var(--primary-hover)] hover:underline"
                >
                  직접 매핑하기
                </button>
              </div>
            )}
            {sniffResult.specimen.columns && showMapper && (
              <div className="mt-3">
                <ColumnMapper
                  columns={sniffResult.specimen.columns}
                  roles={parsersQ.data?.roles ?? []}
                  value={mapping}
                  onChange={setMapping}
                  onRetryRoles={() => parsersQ.refetch()}
                />
              </div>
            )}
          </Card>
          {sniffResult.issues.length > 0 && (
            <IssuePanel
              issues={sniffResult.issues}
              filename={file?.name}
              onResolveError={() => setShowMapper(true)}
            />
          )}
          <StepNav
            onBack={() => setStep(0)}
            onNext={() => setStep(2)}
            nextLabel="시편 정보"
            nextDisabled={sniffHasError}
            nextReason={sniffHasError ? "오류 이슈를 해결해야 진행할 수 있습니다" : undefined}
          />
        </div>
      )}

      {/* 단계 2 — 시편 정보 */}
      {step === 2 && (
        <div className="flex flex-col gap-4">
          <Card className="flex flex-col gap-4 p-4">
            <Field label="재료">
              <select
                className="h-9 rounded-md border border-border-default bg-surface px-3 text-sm text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--focus-ring)]"
                value={meta.materialId ?? "new"}
                onChange={(e) =>
                  setMeta((m) => ({
                    ...m,
                    materialId: e.target.value === "new" ? null : Number(e.target.value),
                  }))
                }
              >
                <option value="new">+ 새 재료 생성</option>
                {materialsQ.data?.items.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
              {materialsQ.isError && (
                <p className="flex items-center gap-2 text-xs text-danger" role="alert">
                  재료 목록을 불러오지 못했습니다.
                  <button
                    type="button"
                    onClick={() => materialsQ.refetch()}
                    className="underline underline-offset-2 hover:text-text-primary"
                  >
                    다시 시도
                  </button>
                </p>
              )}
            </Field>
            {meta.materialId == null && (
              <Field label="새 재료명" required>
                <Input
                  value={meta.newMaterialName}
                  onChange={(e) => setMeta((m) => ({ ...m, newMaterialName: e.target.value }))}
                  placeholder="예: AL6061-T6"
                />
              </Field>
            )}
            <Field label="시편 라벨" required>
              <Input value={meta.label} onChange={(e) => setMeta((m) => ({ ...m, label: e.target.value }))} />
            </Field>

            <Field label="형상">
              <div className="flex gap-2">
                {(["flat", "round"] as GeometryType[]).map((g) => (
                  <button
                    key={g}
                    type="button"
                    aria-pressed={meta.geometry === g}
                    onClick={() => setMeta((m) => ({ ...m, geometry: g }))}
                    className={cn(
                      "rounded-md border px-3 py-1.5 text-sm transition-colors",
                      meta.geometry === g
                        ? "border-primary bg-primary-muted text-text-primary"
                        : "border-border-default text-text-secondary hover:bg-surface-2",
                    )}
                  >
                    {g === "flat" ? "평판" : "봉상"}
                  </button>
                ))}
              </div>
            </Field>

            <div className="grid grid-cols-2 gap-3">
              <Field label="게이지 길이 L₀ (mm)" required error={dimError(meta.L0_mm)}>
                <Input type="number" min={0} step="any" aria-invalid={dimError(meta.L0_mm) ? true : undefined} value={meta.L0_mm} onChange={(e) => setMeta((m) => ({ ...m, L0_mm: e.target.value }))} className="tnum" />
              </Field>
              {meta.geometry === "flat" ? (
                <>
                  <Field label="폭 w₀ (mm)" required error={dimError(meta.w0_mm)}>
                    <Input type="number" min={0} step="any" aria-invalid={dimError(meta.w0_mm) ? true : undefined} value={meta.w0_mm} onChange={(e) => setMeta((m) => ({ ...m, w0_mm: e.target.value }))} className="tnum" />
                  </Field>
                  <Field label="두께 t₀ (mm)" required error={dimError(meta.t0_mm)}>
                    <Input type="number" min={0} step="any" aria-invalid={dimError(meta.t0_mm) ? true : undefined} value={meta.t0_mm} onChange={(e) => setMeta((m) => ({ ...m, t0_mm: e.target.value }))} className="tnum" />
                  </Field>
                </>
              ) : (
                <Field label="지름 d₀ (mm)" required error={dimError(meta.d0_mm)}>
                  <Input type="number" min={0} step="any" aria-invalid={dimError(meta.d0_mm) ? true : undefined} value={meta.d0_mm} onChange={(e) => setMeta((m) => ({ ...m, d0_mm: e.target.value }))} className="tnum" />
                </Field>
              )}
            </div>

            <div className="rounded-md bg-surface-2 px-3 py-2 text-sm text-text-secondary">
              초기 단면적 A₀ ={" "}
              <span className="tnum text-text-primary">{a0 != null ? a0.toFixed(3) : "—"}</span> mm²
            </div>
          </Card>
          <StepNav
            onBack={() => setStep(1)}
            onNext={() => setStep(3)}
            nextLabel="미리보기"
            nextDisabled={metaReason != null}
            nextReason={metaReason ?? undefined}
          />
        </div>
      )}

      {/* 단계 3 — 미리보기·등록 / 결과 */}
      {step === 3 && (
        <div className="flex flex-col gap-4">
          {!result ? (
            <>
              <Card className="flex flex-col gap-2 p-4 text-sm">
                <Row k="파일" v={file?.name ?? "—"} />
                <Row k="재료" v={meta.materialId ? materialName(materialsQ.data?.items, meta.materialId) : `신규: ${meta.newMaterialName}`} />
                <Row k="시편" v={meta.label} />
                <Row k="형상" v={meta.geometry === "flat" ? "평판" : "봉상"} />
                <Row k="A₀" v={`${a0?.toFixed(3) ?? "—"} mm²`} />
              </Card>
              <StepNav
                onBack={() => setStep(2)}
                onNext={() => commitMut.mutate()}
                nextLabel={commitMut.isPending ? "등록 중…" : "등록"}
                nextDisabled={commitMut.isPending}
                nextLoading={commitMut.isPending}
              />
            </>
          ) : (
            <div className="flex flex-col gap-4">
              <Card className="flex items-center gap-3 p-4">
                <span
                  className={cn(
                    "flex size-9 items-center justify-center rounded-full",
                    result.computed ? "bg-accent-muted text-accent" : "bg-[var(--warning-muted,transparent)] text-warning",
                  )}
                >
                  <Check className="size-5" />
                </span>
                <div>
                  <p className="font-medium text-text-primary">
                    {result.computed ? "물성 계산 완료" : "업로드됨 — 확인 필요"}
                  </p>
                  <p className="tnum text-xs text-text-tertiary">test #{result.test_id}</p>
                </div>
              </Card>
              {result.issues.length > 0 && (
                <IssuePanel issues={result.issues} filename={file?.name} computed={result.computed} />
              )}
              {/* 물성 미산출이면 매핑을 고쳐 같은 test에 재적재할 수 있다. */}
              {!result.computed && file && sniffResult?.specimen.columns && (
                <Card className="flex flex-col gap-3 p-4">
                  {!showResultMapper ? (
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="text-sm text-text-secondary">
                        컬럼 매핑을 고쳐 다시 적재하면 물성이 계산될 수 있습니다.
                      </span>
                      <Button variant="outline" onClick={() => setShowResultMapper(true)}>
                        매핑 수정
                      </Button>
                    </div>
                  ) : (
                    <>
                      <ColumnMapper
                        columns={sniffResult.specimen.columns}
                        roles={parsersQ.data?.roles ?? []}
                        value={mapping}
                        onChange={setMapping}
                        onRetryRoles={() => parsersQ.refetch()}
                      />
                      <div className="flex flex-wrap items-center justify-end gap-3">
                        {!hasAxisPair(sniffResult.specimen.columns, mapping) && (
                          <span className="text-xs text-text-tertiary">
                            응력·변형률(또는 힘·변위) 축 쌍이 있어야 재적재할 수 있습니다
                          </span>
                        )}
                        <Button variant="ghost" onClick={() => setShowResultMapper(false)}>
                          취소
                        </Button>
                        <Button
                          onClick={() => remapMut.mutate(effectiveMapping(mapping))}
                          disabled={
                            remapMut.isPending ||
                            !hasAxisPair(sniffResult.specimen.columns, mapping)
                          }
                        >
                          {remapMut.isPending && <Loader2 className="size-4 animate-spin" />}
                          재적재
                        </Button>
                      </div>
                    </>
                  )}
                </Card>
              )}
              <div className="flex justify-end gap-2">
                <Button variant="ghost" onClick={resetWizard}>
                  새 업로드
                </Button>
                <Button
                  onClick={() =>
                    committedMaterialId != null &&
                    navigate({ to: "/materials/$id", params: { id: String(committedMaterialId) } })
                  }
                  disabled={committedMaterialId == null}
                >
                  재료 보기
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  function resetWizard() {
    setStep(0);
    setFile(null);
    setSniffResult(null);
    setResult(null);
    setCommittedMaterialId(null);
    setMapping({});
    setShowMapper(false);
    setCreatedIds({ materialId: null, specimenId: null, testId: null });
    setShowResultMapper(false);
  }
}

// ── 보조 컴포넌트 ──────────────────────────────────────────────────────
function Stepper({ step, onStepClick }: { step: Step; onStepClick: (s: Step) => void }) {
  return (
    <div className="flex items-center gap-2">
      {STEP_LABELS.map((label, i) => {
        const done = i < step;
        return (
          <React.Fragment key={i}>
            {/* 완료된 단계는 클릭해 되돌아갈 수 있다. 진행 중/미래 단계는 비활성. */}
            <button
              type="button"
              disabled={!done}
              onClick={() => onStepClick(i as Step)}
              aria-current={i === step ? "step" : undefined}
              aria-label={done ? `${label} 단계로 돌아가기` : label}
              className={cn(
                "flex items-center gap-2",
                done ? "cursor-pointer transition-opacity hover:opacity-75" : "cursor-default",
              )}
            >
              <span
                className={cn(
                  "tnum flex size-6 items-center justify-center rounded-full text-xs font-medium transition-colors duration-200",
                  done
                    ? "bg-accent text-[var(--primary-fg)]"
                    : i === step
                      ? "bg-primary text-[var(--primary-fg)]"
                      : "bg-surface-2 text-text-tertiary",
                )}
              >
                {done ? <Check className="size-3.5" /> : i + 1}
              </span>
              <span className={cn("text-sm", i === step ? "text-text-primary" : "text-text-tertiary")}>
                {label}
              </span>
            </button>
            {i < STEP_LABELS.length - 1 && <div className="h-px w-4 bg-border-default" />}
          </React.Fragment>
        );
      })}
    </div>
  );
}

function StepNav({
  onBack,
  onNext,
  nextLabel,
  nextDisabled,
  nextLoading,
  nextReason,
}: {
  onBack: () => void;
  onNext: () => void;
  nextLabel: string;
  nextDisabled?: boolean;
  nextLoading?: boolean;
  /** 다음 버튼이 비활성인 이유 — 버튼 옆에 표시. */
  nextReason?: string;
}) {
  return (
    <div className="flex items-center justify-between gap-3">
      <Button variant="ghost" onClick={onBack}>
        뒤로
      </Button>
      <div className="flex items-center gap-3">
        {nextDisabled && nextReason && (
          <span className="text-xs text-text-tertiary" role="status">
            {nextReason}
          </span>
        )}
        <Button onClick={onNext} disabled={nextDisabled}>
          {nextLoading ? <Loader2 className="size-4 animate-spin" /> : <ChevronRight className="size-4" />}
          {nextLabel}
        </Button>
      </div>
    </div>
  );
}

function Field({
  label,
  required,
  error,
  children,
}: {
  label: string;
  required?: boolean;
  /** 필드별 인라인 에러 문구(입력 아래 표시). */
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label>
        {label}
        {required && <span className="ml-0.5 text-danger">*</span>}
      </Label>
      {children}
      {error && (
        <p className="text-xs text-danger" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-text-tertiary">{k}</span>
      <span className="text-text-primary">{v}</span>
    </div>
  );
}

// ── 유틸 ───────────────────────────────────────────────────────────────
function mm(s: string): number {
  return Number(s) / 1000;
}

/** 등록 단계 실행 래퍼 — 실패 시 어느 단계에서 실패했는지 메시지에 명시한다. */
async function stage<T>(label: string, fn: () => Promise<T>): Promise<T> {
  try {
    return await fn();
  } catch (e) {
    throw new Error(`${label} 실패 — ${errorMessage(e)}`);
  }
}

/** 수동 매핑에서 미지정(unknown)·빈 값을 제거한 실제 오버라이드만 남긴다. */
function effectiveMapping(mapping: Record<string, string>): Record<string, string> {
  // '무시'(unknown)도 유효한 오버라이드 — 백엔드 _apply_mapping이 해당 컬럼을 배제한다.
  // 이를 걸러내면 오검출 컬럼을 무시로 지정해도 서버에 반영되지 않는다.
  return Object.fromEntries(Object.entries(mapping).filter(([, role]) => role));
}

/** 치수 문자열 검증 — 0보다 큰 숫자가 아니면 인라인 에러 문구 반환. */
function dimError(s: string): string | undefined {
  return Number(s) > 0 ? undefined : "0보다 큰 숫자여야 합니다";
}

function computeA0(m: MetaForm): number | null {
  if (m.geometry === "flat") {
    const w = Number(m.w0_mm);
    const t = Number(m.t0_mm);
    return w > 0 && t > 0 ? w * t : null;
  }
  const d = Number(m.d0_mm);
  return d > 0 ? (Math.PI * d * d) / 4 : null;
}

/** 시편 메타 검증 — 유효하면 null, 아니면 미리보기 버튼 옆에 보여줄 사유. */
function metaInvalidReason(m: MetaForm): string | null {
  if (m.materialId == null && !m.newMaterialName.trim()) return "새 재료명을 입력해야 진행할 수 있습니다";
  if (!m.label.trim()) return "시편 라벨을 입력해야 진행할 수 있습니다";
  if (Number(m.L0_mm) <= 0 || computeA0(m) == null) return "치수는 0보다 큰 숫자여야 합니다";
  return null;
}

function materialName(
  items: { id: number; name: string }[] | undefined,
  id: number,
): string {
  return items?.find((m) => m.id === id)?.name ?? `#${id}`;
}
