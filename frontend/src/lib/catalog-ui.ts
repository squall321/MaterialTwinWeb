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
  magnetics: "자성/모터", acoustics: "음향", rf: "RF",
  passive: "수동소자", sensor: "센서", thermal: "방열", pcb: "PCB",
  housing: "하우징", coating: "코팅", emi: "EMI", semiconductor: "반도체",
  // `기타` 는 계통이 아니라 **계통을 아직 안 정한 재료가 모이는 칸**이다.
  // 옛 라벨 "일반 엔지니어링재" 는 의도된 분류처럼 읽혀서, 실제로 읽는 사람이
  // 그 칸을 세지 않고 지나쳤다 — 49차 KA·48차 JC 가 같은 오독을 각각 겪었다(§528).
  // 미분류임을 라벨이 스스로 말하게 한다.
  wlp: "웨이퍼레벨패키지", 기타: "미분류",
  // 옛 값 — `fix_subsystem_vocab.py` 가 acoustics·pcb·wlp 로 합쳤다. 그 스크립트를
  // 아직 안 돌린 DB 를 붙여도 라벨이 깨지지 않게 남겨 둔다.
  speaker: "음향", audio: "음향", fpcb: "PCB", soc: "웨이퍼레벨패키지",
};

export function subsystemLabel(s: string | null | undefined): string {
  // 위와 같은 이유로 "일반" 이 아니라 "미분류" 다 — 계통이 비었다는 것은
  // '일반 재료' 라는 판정이 아니라 **아직 판정하지 않았다** 는 뜻이다.
  if (!s) return "미분류";
  return SUBSYSTEM_LABEL[s] ?? s;
}

// ── 대표값의 "다른 후보" 표시(51차 MB) ──────────────────────────────────────
// 대표값 하나만 보여주면 "다른 후보가 있다" 가 화면에서 통째로 사라진다. 값을 감추지 않는다.

/** 후보가 진 자리 — `_rep_rank` 튜플에서 대표값과 처음 어긋난 칸의 이름. */
export const SEPARATED_BY_LABEL: Record<string, string> = {
  state: "고체가 아님",
  tier: "신뢰등급이 낮음",
  numeric: "수치값이 없음",
  temperature: "상온에서 더 멂",
  wavelength: "기준 파장에서 더 멂",
  n_conditions: "조건을 더 많이 적음",
  load_order: "순위가 못 가름",
};

export function separatedByLabel(s: string | null | undefined): string {
  if (!s) return "";
  return SEPARATED_BY_LABEL[s] ?? s;
}

/**
 * 동률 안내 문구. **갈래마다 다르게 적는다.**
 *
 * "동률이면 적재 순서로 골랐다" 를 일률로 띄우면 라이브 3,642건 중 3,607건이 틀린 설명이 되고,
 * 매번 뜨는 같은 경고는 무시하는 법을 가르친다(49차 KA). 원인을 이름으로 갈라야 경고가 산다.
 */
export function tieMessage(kind: string, nTied: number, condKeys: string[]): string {
  const keys = condKeys.length ? condKeys.join(" · ") : "";
  if (kind === "multi_term")
    return `이 물성 키에는 항이 ${nTied}개 산다 — 대표값 하나는 이 재료의 ${keys || "그 항들"} 중 하나일 뿐이다`;
  if (kind === "indistinguishable")
    return `순위가 같은 후보 ${nTied}개를 가를 조건이 없다 — 적재 순서로 골랐다`;
  return `순위가 같은 후보 ${nTied}개가 ${keys} 에서 갈린다 — 선택기는 이 축을 안 본다`;
}

/** 두 조건 dict에서 다른 칸만. 상세 화면은 전 행을 이미 들고 있어 서버가 안 보내 준다. */
export function conditionDelta(
  rep: Record<string, unknown> | null,
  alt: Record<string, unknown> | null,
): { key: string; rep: unknown; alt: unknown }[] {
  const a = rep ?? {};
  const b = alt ?? {};
  const keys = Array.from(new Set([...Object.keys(a), ...Object.keys(b)])).sort();
  return keys
    .filter((k) => JSON.stringify(a[k]) !== JSON.stringify(b[k]))
    .map((k) => ({ key: k, rep: a[k], alt: b[k] }));
}

export function condValue(v: unknown): string {
  if (v === null || v === undefined) return "없음";
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  if (typeof v === "string") return v;
  return JSON.stringify(v);
}
