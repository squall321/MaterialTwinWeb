// 앱 진입점 — QueryClientProvider + RouterProvider + Sonner Toaster 조립.
import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClientProvider } from "@tanstack/react-query";
import { RouterProvider } from "@tanstack/react-router";
import { Toaster } from "sonner";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import { queryClient } from "./lib/queryClient";
import { router } from "./router";
import "./index.css";

/** 문서 루트(data-theme/클래스)에서 현재 테마를 읽는다 — 다크 기본, light 오버라이드. */
function readDocTheme(): "light" | "dark" {
  const el = document.documentElement;
  return el.dataset.theme === "light" || el.classList.contains("light") ? "light" : "dark";
}

/** 테마 토글에 반응하는 Toaster 래퍼(echarts 번들을 엔트리에 끌어오지 않도록 로컬 구현). */
function ThemedToaster() {
  const [theme, setTheme] = React.useState<"light" | "dark">(readDocTheme);
  React.useEffect(() => {
    const mo = new MutationObserver(() => setTheme(readDocTheme()));
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });
    return () => mo.disconnect();
  }, []);
  return <Toaster theme={theme} position="bottom-right" richColors closeButton />;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
      <ThemedToaster />
    </QueryClientProvider>
  </React.StrictMode>,
);
