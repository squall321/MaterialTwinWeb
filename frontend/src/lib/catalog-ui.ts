// 물성 카탈로그 표시 헬퍼 — 도메인 색·라벨, 신뢰등급 스타일, 값 포맷(SI·조건).

export const DOMAIN_META: Record<string, { label: string; color: string; abbr: string }> = {
  mechanical: { label: "기계", color: "var(--chart-1)", abbr: "MECH" },
  interface: { label: "접착·계면", color: "var(--warning)", abbr: "INTF" },
  thermal: { label: "열", color: "var(--chart-2)", abbr: "THRM" },
  electrical: { label: "전기", color: "var(--chart-5)", abbr: "ELEC" },
  physical: { label: "물리", color: "var(--chart-3)", abbr: "PHYS" },
  optical: { label: "광학", color: "var(--info)", abbr: "OPT" },
  magnetic: { label: "자기", color: "var(--chart-7)", abbr: "MAG" },
  chemical: { label: "화학", color: "var(--accent)", abbr: "CHEM" },
  acoustic: { label: "음향", color: "var(--chart-8)", abbr: "ACST" },
  rheological: { label: "유변", color: "var(--chart-6)", abbr: "RHEO" },
  structure: { label: "구조", color: "var(--chart-4)", abbr: "STRC" },
};

export function domainMeta(d: string) {
  return DOMAIN_META[d] ?? { label: d, color: "var(--text-tertiary)", abbr: d.slice(0, 4).toUpperCase() };
}

// 신뢰등급 1 측정 · 2 핸드북/DB · 3 데이터시트 · 4 계산/등가 · 5 추정.
export const TIER_META: Record<number, { label: string; cls: string }> = {
  1: { label: "측정", cls: "border-transparent bg-[var(--accent-muted)] text-accent" },
  2: { label: "핸드북", cls: "border-transparent bg-[var(--accent-muted)] text-success" },
  3: { label: "데이터시트", cls: "border-transparent bg-primary-muted text-info" },
  4: { label: "계산/등가", cls: "border-[color:var(--warning)] bg-transparent text-warning" },
  5: { label: "추정", cls: "border-[color:var(--danger)] bg-transparent text-danger" },
};

export function tierMeta(t: number) {
  return TIER_META[t] ?? { label: `T${t}`, cls: "border-border-default bg-transparent text-text-secondary" };
}

// 가정값은 tier4 안에서도 성격이 다르다 — 계산으로 유도한 값이 아니라 클래스 대표를 빌려 온 값이라
// "계산/등가" 대신 "가정"으로 보여야 오해가 없다. conditions.assumption 이 표지다.
export function tierBadge(t: number, conditions?: Record<string, unknown> | null) {
  if (conditions && conditions.assumption === true) {
    return { label: "가정", cls: "border-[color:var(--danger)] bg-transparent text-danger" };
  }
  return tierMeta(t);
}

export const METHOD_LABEL: Record<string, string> = {
  measured: "측정", handbook: "핸드북", datasheet: "데이터시트",
  computed: "계산", estimated: "추정",
  digitized: "그림 판독",
};

// 값을 사람이 읽기 좋은 형태로(공학 표기: 큰/작은 값은 지수, 중간값은 유효 4자리).
export function formatValue(v: number | null, unit: string | null): string {
  if (v === null || v === undefined) return "—";
  const a = Math.abs(v);
  let num: string;
  if (a !== 0 && (a >= 1e5 || a < 1e-3)) {
    num = v.toExponential(3).replace(/e([+-])(\d)$/, "e$1$2");
  } else {
    num = Number(v.toPrecision(5)).toString();
  }
  return unit && unit !== "1" ? `${num} ${prettyUnit(unit)}` : num;
}

// 저장 단위 문자열을 표시용으로 살짝 다듬기(* → ·, ^ 유지).
export function prettyUnit(u: string): string {
  return u.replace(/\*/g, "·");
}

// conditions dict를 짧은 요약으로(온도·습도·주파수·파장 등).
export function formatConditions(c: Record<string, unknown> | null): string {
  if (!c) return "";
  const parts: string[] = [];
  const push = (k: string, label: string, suffix = "") => {
    if (c[k] !== undefined && c[k] !== null) parts.push(`${label} ${c[k]}${suffix}`);
  };
  push("temperature_k", "T", " K");
  push("temperature_C", "T", " °C");
  push("humidity_rh", "RH", "%");
  push("frequency_hz", "f", " Hz");
  push("frequency_kHz", "f", " kHz");
  push("wavelength_nm", "λ", " nm");
  // 나머지 키는 key=value로.
  for (const [k, v] of Object.entries(c)) {
    if (["temperature_k", "temperature_C", "humidity_rh", "frequency_hz", "frequency_kHz", "wavelength_nm"].includes(k)) continue;
    if (v === null || v === undefined) continue;
    parts.push(`${k}=${typeof v === "number" ? v : String(v)}`);
  }
  return parts.join(" · ");
}

export const SUBSYSTEM_LABEL: Record<string, string> = {
  camera: "카메라", display: "디스플레이", battery: "배터리", packaging: "패키지",
  magnetics: "자성/모터", speaker: "스피커", audio: "음향", rf: "RF",
  passive: "수동소자", sensor: "센서", thermal: "방열", pcb: "PCB",
  housing: "하우징", coating: "코팅", emi: "EMI", semiconductor: "반도체",
  soc: "SoC", 기타: "일반 엔지니어링재",
};

export function subsystemLabel(s: string | null | undefined): string {
  if (!s) return "일반";
  return SUBSYSTEM_LABEL[s] ?? s;
}
