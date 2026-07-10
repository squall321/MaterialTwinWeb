// TanStack Router 정의 — 해시 라우팅(createHashHistory) + 공통 셸(사이드/헤더) 루트 라우트.
import {
  createRootRoute,
  createRoute,
  createRouter,
  createHashHistory,
  redirect,
  Link,
  Outlet,
} from "@tanstack/react-router";
import type { ReactNode } from "react";
import { FlaskConical, Library, Upload, LayoutDashboard, SearchX } from "lucide-react";
import { cn } from "./lib/utils";
import { Button } from "./components/ui/button";
import { EmptyState } from "./components/states/EmptyState";
import { InsightsScreen } from "./routes/insights";
import { MaterialsScreen } from "./routes/materials";
import { MaterialDetailScreen } from "./routes/material-detail";
import { UploadScreen } from "./routes/upload";

// ── 공통 셸: 좌측 256px 고정 사이드 + 우측 콘텐츠(max-width 1180px, §14.3) ──
function AppShell() {
  return (
    <div className="flex min-h-screen bg-base text-text-primary">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-border-subtle bg-surface md:flex">
        <div className="flex h-14 items-center gap-2 px-5">
          <FlaskConical className="size-5 text-primary" />
          <span className="text-md font-medium tracking-[-0.005em]">MaterialTwin</span>
        </div>
        <nav className="flex flex-col gap-1 px-3 py-2">
          <NavItem to="/insights" icon={<LayoutDashboard className="size-4" />} label="인사이트" />
          <NavItem to="/materials" icon={<Library className="size-4" />} label="재료 라이브러리" />
          <NavItem to="/upload" icon={<Upload className="size-4" />} label="업로드" />
        </nav>
      </aside>
      <main className="flex-1">
        <div className="mx-auto max-w-[1180px] px-[clamp(1.25rem,5vw,4rem)] py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function NavItem({
  to,
  icon,
  label,
}: {
  to: string;
  icon: ReactNode;
  label: string;
}) {
  return (
    <Link
      to={to}
      className={cn(
        "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium text-text-secondary",
        "transition-colors duration-[130ms] hover:bg-surface-2 hover:text-text-primary",
      )}
      activeProps={{
        className: "bg-primary-muted text-[var(--primary-hover)] hover:bg-primary-muted",
      }}
    >
      {icon}
      {label}
    </Link>
  );
}

// 404 화면 — 잘못된 URL 진입 시 인사이트로 안내.
function NotFoundScreen() {
  return (
    <EmptyState
      icon={<SearchX className="size-6" />}
      title="페이지를 찾을 수 없습니다"
      description="주소가 잘못되었거나 삭제된 페이지입니다."
      action={
        <Link to="/insights">
          <Button>인사이트로 이동</Button>
        </Link>
      }
    />
  );
}

const rootRoute = createRootRoute({ component: AppShell });

// 루트("/")는 인사이트 대시보드로 리다이렉트한다.
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({ to: "/insights" });
  },
});

const insightsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/insights",
  component: InsightsScreen,
});

const materialsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/materials",
  // /materials?q=…&cat=… — 검색어·카테고리 필터를 URL과 동기화(뒤로가기 시 유지).
  validateSearch: (s: Record<string, unknown>): { q?: string; cat?: string } => {
    const out: { q?: string; cat?: string } = {};
    if (typeof s.q === "string" && s.q) out.q = s.q;
    if (typeof s.cat === "string" && s.cat) out.cat = s.cat;
    return out;
  },
  component: MaterialsScreen,
});

const materialDetailRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/materials/$id",
  component: MaterialDetailScreen,
});

const uploadRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/upload",
  // /upload?material=12 — 재료 상세에서 진입 시 사전 선택.
  validateSearch: (s: Record<string, unknown>): { material?: number } => {
    const m = Number(s.material);
    return Number.isFinite(m) && m > 0 ? { material: m } : {};
  },
  component: UploadScreen,
});

const routeTree = rootRoute.addChildren([
  indexRoute,
  insightsRoute,
  materialsRoute,
  materialDetailRoute,
  uploadRoute,
]);

export const router = createRouter({
  routeTree,
  history: createHashHistory(),
  defaultNotFoundComponent: NotFoundScreen,
  scrollRestoration: true,
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
