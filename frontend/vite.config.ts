import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base: "./" → 모든 번들된 자산 URL 이 상대경로로 생성된다.
// 덕분에 Caddy 가 /apps/<slug>/ 서브패스로 마운트해도 자산 경로가 깨지지 않는다.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    // echarts는 의도적 단일 청크(gzip ~228KB) — 아래 분리로 나머지는 500KB 미만.
    chunkSizeWarningLimit: 700,
    rollupOptions: {
      output: {
        // 무거운 서드파티를 성격별 청크로 분리(PLAN §8.6·§14.8) — 앱 코드 변경 시
        // vendor 청크 캐시가 유지되어 재방문 로딩이 빨라진다.
        manualChunks(id) {
          if (id.includes("node_modules/echarts/") || id.includes("node_modules/zrender/")) {
            return "echarts";
          }
          if (/node_modules\/(react|react-dom|scheduler)\//.test(id)) {
            return "react";
          }
          if (id.includes("node_modules/@tanstack/")) {
            return "tanstack";
          }
          if (/node_modules\/(@radix-ui|lucide-react|sonner|class-variance-authority|clsx|tailwind-merge)\//.test(id)) {
            return "ui";
          }
        },
      },
    },
  },
});
