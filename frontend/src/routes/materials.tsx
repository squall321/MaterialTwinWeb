// 재료 라이브러리(/materials, §14.3.2) — 검색·재료 카드 그리드·새 재료 생성 다이얼로그.
import * as React from "react";
import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import {
  useQuery,
  useMutation,
  useQueryClient,
  keepPreviousData,
} from "@tanstack/react-query";
import { Library, Plus, Search, ArrowRight, X } from "lucide-react";
import { toast } from "sonner";
import {
  listMaterials,
  createMaterial,
  type Material,
  type MaterialIn,
} from "../api/materials";
import { errorMessage } from "../lib/download";
import { cn } from "../lib/utils";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Card } from "../components/ui/card";
import { Badge, badgeVariants } from "../components/ui/badge";
import { Label } from "../components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "../components/ui/dialog";
import { EmptyState } from "../components/states/EmptyState";
import { ErrorState } from "../components/states/ErrorState";
import { TableSkeleton } from "../components/states/Skeletons";

// 카테고리 필터 칩 목록(백엔드 category 동등 필터).
const CATEGORIES = ["metal", "polymer", "rubber", "composite"];
// 목록 페이지 크기 — "더 보기"로 증가(백엔드 size 상한 200).
const PAGE_SIZE = 24;
const MAX_SIZE = 200;

export function MaterialsScreen() {
  // URL(?q=&cat=)이 필터의 단일 진실 — 목록→상세→뒤로가기에서 검색 상태 유지.
  const search = useSearch({ from: "/materials" }) as { q?: string; cat?: string };
  const navigate = useNavigate();
  const urlQ = search.q ?? "";
  const cat = search.cat ?? "";

  // 입력값은 로컬 상태, 디바운스(250ms) 후 URL에 반영.
  const [q, setQ] = React.useState(urlQ);
  const [size, setSize] = React.useState(PAGE_SIZE);

  const pushSearch = React.useCallback(
    (nextQ: string, nextCat: string) =>
      navigate({
        to: "/materials",
        search: {
          ...(nextQ ? { q: nextQ } : {}),
          ...(nextCat ? { cat: nextCat } : {}),
        },
        replace: true,
      }),
    [navigate],
  );

  React.useEffect(() => {
    if (q === urlQ) return;
    const t = setTimeout(() => pushSearch(q, cat), 250);
    return () => clearTimeout(t);
  }, [q, urlQ, cat, pushSearch]);

  // 외부 URL 변경(뒤로가기·네비 링크) → 입력값 역동기화.
  React.useEffect(() => {
    setQ(urlQ);
  }, [urlQ]);

  // 필터가 바뀌면 페이지 크기 초기화.
  React.useEffect(() => {
    setSize(PAGE_SIZE);
  }, [urlQ, cat]);

  const query = useQuery({
    queryKey: ["materials", urlQ, cat, size],
    queryFn: () =>
      listMaterials({ q: urlQ || undefined, category: cat || undefined, size }),
    placeholderData: keepPreviousData,
  });

  const filtered = Boolean(urlQ || cat);

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-overline">재료 라이브러리</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-[-0.01em] text-text-primary">
            재료
          </h1>
        </div>
        <NewMaterialDialog />
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative w-full max-w-sm">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-text-tertiary" />
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="재료명·코드 검색"
            className="pl-9 pr-8"
            aria-label="재료 검색"
          />
          {q && (
            <button
              type="button"
              onClick={() => {
                setQ("");
                pushSearch("", cat);
              }}
              aria-label="검색어 지우기"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-sm p-0.5 text-text-tertiary transition-colors duration-[130ms] hover:text-text-primary"
            >
              <X className="size-4" />
            </button>
          )}
        </div>
        {query.data && (
          <p className="text-sm text-text-tertiary">
            <span className="tnum">{query.data.total}</span>건
          </p>
        )}
      </div>

      <div className="flex flex-wrap gap-1.5" role="group" aria-label="분류 필터">
        <CategoryChip
          label="전체"
          pressed={!cat}
          onClick={() => pushSearch(q, "")}
        />
        {CATEGORIES.map((c) => (
          <CategoryChip
            key={c}
            label={c}
            pressed={cat === c}
            onClick={() => pushSearch(q, cat === c ? "" : c)}
          />
        ))}
      </div>

      {query.isPending ? (
        <TableSkeleton rows={4} cols={4} />
      ) : query.isError ? (
        <ErrorState onRetry={() => query.refetch()} />
      ) : query.data.items.length === 0 ? (
        <EmptyState
          icon={<Library className="size-6" />}
          title={filtered ? "검색 결과 없음" : "아직 재료가 없습니다"}
          description={
            filtered
              ? "다른 검색어나 분류를 시도하거나 새 재료를 추가하세요."
              : "첫 재료를 추가하고 시험 데이터를 업로드하세요."
          }
          action={<NewMaterialDialog />}
        />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {query.data.items.map((m) => (
              <MaterialCard key={m.id} material={m} />
            ))}
          </div>
          {query.data.total > query.data.items.length && size < MAX_SIZE && (
            <div className="flex justify-center">
              <Button
                variant="ghost"
                onClick={() => setSize((s) => Math.min(s + PAGE_SIZE, MAX_SIZE))}
                disabled={query.isFetching}
              >
                {query.isFetching ? "불러오는 중…" : "더 보기"}
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// 카테고리 필터 칩 — Badge 스타일 재사용, aria-pressed로 선택 상태 표시.
function CategoryChip({
  label,
  pressed,
  onClick,
}: {
  label: string;
  pressed: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={onClick}
      className={cn(
        badgeVariants({ variant: pressed ? "default" : "outline" }),
        "cursor-pointer transition-colors duration-[130ms]",
        !pressed && "hover:bg-surface-2 hover:text-text-primary",
      )}
    >
      {label}
    </button>
  );
}

function MaterialCard({ material }: { material: Material }) {
  return (
    <Link to="/materials/$id" params={{ id: String(material.id) }}>
      <Card className="group h-full cursor-pointer p-4 transition-colors duration-[160ms] hover:border-border-strong">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0">
            <p className="truncate font-medium text-text-primary">{material.name}</p>
            {material.material_code && (
              <p className="tnum mt-0.5 truncate text-xs text-text-tertiary">
                {material.material_code}
              </p>
            )}
          </div>
          <ArrowRight className="size-4 shrink-0 text-text-tertiary transition-transform duration-[160ms] group-hover:translate-x-0.5 group-hover:text-text-secondary" />
        </div>
        {material.category && (
          <div className="mt-3">
            <Badge>{material.category}</Badge>
          </div>
        )}
      </Card>
    </Link>
  );
}

function NewMaterialDialog() {
  const qc = useQueryClient();
  const navigate = useNavigate();
  const [open, setOpen] = React.useState(false);
  const [form, setForm] = React.useState<MaterialIn>({ name: "" });

  const mut = useMutation({
    mutationFn: () => createMaterial(form),
    onSuccess: (m) => {
      qc.invalidateQueries({ queryKey: ["materials"] });
      toast.success(`재료 "${m.name}" 생성됨`);
      setOpen(false);
      setForm({ name: "" });
      navigate({ to: "/materials/$id", params: { id: String(m.id) } });
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="size-4" />
          새 재료
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>새 재료 추가</DialogTitle>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault();
            if (form.name.trim()) mut.mutate();
          }}
        >
          <Field label="재료명" required>
            <Input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              placeholder="예: AL6061-T6"
              autoFocus
            />
          </Field>
          <Field label="재료 코드">
            <Input
              value={form.material_code ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, material_code: e.target.value || null }))
              }
              placeholder="선택"
            />
          </Field>
          <Field label="분류">
            <Input
              value={form.category ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, category: e.target.value || null }))
              }
              placeholder="metal / polymer / composite"
            />
          </Field>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="ghost">
                취소
              </Button>
            </DialogClose>
            <Button type="submit" disabled={!form.name.trim() || mut.isPending}>
              {mut.isPending ? "생성 중…" : "생성"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
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
