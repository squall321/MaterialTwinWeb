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
import { ColumnMapper } from "../components/ColumnMapper";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Card } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { cn } from "../lib/utils";

type Step = 0 | 1 | 2 | 3;
const STEP_LABELS = ["파일 선택", "감지·매핑", "시편 정보", "미리보기·커밋"];

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
      // 1) 재료 결정(기존 선택 or 새로 생성).
      let mid = meta.materialId;
      if (!mid) {
        const m = await createMaterial({ name: meta.newMaterialName.trim() });
        mid = m.id;
      }
      // 2) 시편 생성(mm → m SI 변환).
      const sp = await createSpecimen(mid, {
        label: meta.label.trim(),
        geometry_type: meta.geometry,
        gauge_length_m: mm(meta.L0_mm),
        width_m: meta.geometry === "flat" ? mm(meta.w0_mm) : null,
        thickness_m: meta.geometry === "flat" ? mm(meta.t0_mm) : null,
        diameter_m: meta.geometry === "round" ? mm(meta.d0_mm) : null,
      });
      // 3) 업로드 → 파싱 → 적재. 재료 id를 함께 반환(★BUG-2).
      let ingest = await uploadToSpecimen(sp.id, file!);
      // 3b) 수동 매핑이 있으면 재파싱(4·5단계만 재실행, ★C5).
      const effectiveMapping = Object.fromEntries(
        Object.entries(mapping).filter(([, role]) => role && role !== "unknown"),
      );
      if (Object.keys(effectiveMapping).length > 0) {
        ingest = await remapUpload(ingest.test_id, file!, effectiveMapping);
      }
      return { materialId: mid, ingest };
    },
    onSuccess: ({ materialId, ingest }) => {
      setResult(ingest);
      setCommittedMaterialId(materialId);
      setStep(3);
      if (ingest.computed) toast.success("업로드·물성 계산 완료");
      else toast.warning("업로드됨 — 확인이 필요합니다");
    },
    onError: (e) => toast.error(e instanceof Error ? e.message : "커밋 실패"),
  });

  const a0 = computeA0(meta);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <header>
        <p className="text-overline">업로드</p>
        <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
          시험 데이터 업로드
        </h1>
      </header>

      <Stepper step={step} />

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
                />
              </div>
            )}
          </Card>
          {sniffResult.issues.length > 0 && <IssuePanel issues={sniffResult.issues} filename={file?.name} />}
          <StepNav onBack={() => setStep(0)} onNext={() => setStep(2)} nextLabel="시편 정보" />
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
              <Field label="게이지 길이 L₀ (mm)" required>
                <Input value={meta.L0_mm} onChange={(e) => setMeta((m) => ({ ...m, L0_mm: e.target.value }))} className="tnum" />
              </Field>
              {meta.geometry === "flat" ? (
                <>
                  <Field label="폭 w₀ (mm)" required>
                    <Input value={meta.w0_mm} onChange={(e) => setMeta((m) => ({ ...m, w0_mm: e.target.value }))} className="tnum" />
                  </Field>
                  <Field label="두께 t₀ (mm)" required>
                    <Input value={meta.t0_mm} onChange={(e) => setMeta((m) => ({ ...m, t0_mm: e.target.value }))} className="tnum" />
                  </Field>
                </>
              ) : (
                <Field label="지름 d₀ (mm)" required>
                  <Input value={meta.d0_mm} onChange={(e) => setMeta((m) => ({ ...m, d0_mm: e.target.value }))} className="tnum" />
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
            nextDisabled={!metaValid(meta)}
          />
        </div>
      )}

      {/* 단계 3 — 미리보기·커밋 / 결과 */}
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
                nextLabel={commitMut.isPending ? "커밋 중…" : "커밋"}
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
  }
}

// ── 보조 컴포넌트 ──────────────────────────────────────────────────────
function Stepper({ step }: { step: Step }) {
  return (
    <div className="flex items-center gap-2">
      {STEP_LABELS.map((label, i) => (
        <React.Fragment key={i}>
          <div className="flex items-center gap-2">
            <span
              className={cn(
                "tnum flex size-6 items-center justify-center rounded-full text-xs font-medium transition-colors duration-200",
                i < step
                  ? "bg-accent text-[var(--primary-fg)]"
                  : i === step
                    ? "bg-primary text-[var(--primary-fg)]"
                    : "bg-surface-2 text-text-tertiary",
              )}
            >
              {i < step ? <Check className="size-3.5" /> : i + 1}
            </span>
            <span className={cn("text-sm", i === step ? "text-text-primary" : "text-text-tertiary")}>
              {label}
            </span>
          </div>
          {i < STEP_LABELS.length - 1 && <div className="h-px w-4 bg-border-default" />}
        </React.Fragment>
      ))}
    </div>
  );
}

function StepNav({
  onBack,
  onNext,
  nextLabel,
  nextDisabled,
  nextLoading,
}: {
  onBack: () => void;
  onNext: () => void;
  nextLabel: string;
  nextDisabled?: boolean;
  nextLoading?: boolean;
}) {
  return (
    <div className="flex justify-between">
      <Button variant="ghost" onClick={onBack}>
        뒤로
      </Button>
      <Button onClick={onNext} disabled={nextDisabled}>
        {nextLoading ? <Loader2 className="size-4 animate-spin" /> : <ChevronRight className="size-4" />}
        {nextLabel}
      </Button>
    </div>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label>
        {label}
        {required && <span className="ml-0.5 text-danger">*</span>}
      </Label>
      {children}
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

function computeA0(m: MetaForm): number | null {
  if (m.geometry === "flat") {
    const w = Number(m.w0_mm);
    const t = Number(m.t0_mm);
    return w > 0 && t > 0 ? w * t : null;
  }
  const d = Number(m.d0_mm);
  return d > 0 ? (Math.PI * d * d) / 4 : null;
}

function metaValid(m: MetaForm): boolean {
  if (!m.label.trim()) return false;
  if (m.materialId == null && !m.newMaterialName.trim()) return false;
  if (Number(m.L0_mm) <= 0) return false;
  return computeA0(m) != null;
}

function materialName(
  items: { id: number; name: string }[] | undefined,
  id: number,
): string {
  return items?.find((m) => m.id === id)?.name ?? `#${id}`;
}
