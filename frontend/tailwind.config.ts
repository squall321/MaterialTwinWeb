import type { Config } from "tailwindcss";

// PLAN §14.2 디자인 토큰을 색/반경/폰트로 Tailwind 에 노출한다(값의 SSOT 는 index.css 의 CSS 변수).
const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        base: "var(--bg-base)",
        surface: "var(--bg-surface)",
        "surface-2": "var(--bg-surface-2)",
        inset: "var(--bg-inset)",
        "border-subtle": "var(--border-subtle)",
        "border-default": "var(--border-default)",
        "border-strong": "var(--border-strong)",
        "text-primary": "var(--text-primary)",
        "text-secondary": "var(--text-secondary)",
        "text-tertiary": "var(--text-tertiary)",
        "text-disabled": "var(--text-disabled)",
        primary: "var(--primary)",
        "primary-hover": "var(--primary-hover)",
        "primary-muted": "var(--primary-muted)",
        "primary-fg": "var(--primary-fg)",
        accent: "var(--accent)",
        "accent-hover": "var(--accent-hover)",
        "accent-muted": "var(--accent-muted)",
        success: "var(--success)",
        warning: "var(--warning)",
        danger: "var(--danger)",
        info: "var(--info)",
        border: "var(--border-default)",
        muted: "var(--text-secondary)",
      },
      borderRadius: {
        xs: "3px",
        sm: "4px",
        md: "6px",
        lg: "8px",
        full: "9999px",
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["Inter", "ui-monospace", "SF Mono", "Cascadia Mono", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
