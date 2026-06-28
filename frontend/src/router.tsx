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
import { FlaskConical, Library, Upload } from "lucide-react";
import { cn } from "./lib/utils";
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

const rootRoute = createRootRoute({ component: AppShell });

// 루트("/")는 /materials 로 리다이렉트한다.
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  beforeLoad: () => {
    throw redirect({ to: "/materials" });
  },
});

const materialsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/materials",
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
  materialsRoute,
  materialDetailRoute,
  uploadRoute,
]);

export const router = createRouter({
  routeTree,
  history: createHashHistory(),
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
