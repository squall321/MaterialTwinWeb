# 물성값 중복 적재를 **조건 키 이름에 안 휘둘리는 방법으로** 전수 검출하고 부류로 가른다(52차 NB).
#
# 왜 새 모듈인가 — `dedupe_values.py` 는 **지운다**(§435 가 금지한 자동 병합의 값 판이다).
# 여기서는 한 행도 지우지 않는다. 찾고, 부류로 가르고, 손확인 표본을 내놓는다.
# 그리고 같은 파동의 NA 가 `conditions` 의 키 이름을 통일하는 중이라, 이 검출은
# **키 이름을 정규화한 뒤 비교**해야 NA 의 진행 상태와 무관하게 같은 답을 낸다(§547).
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict

DB = os.environ.get(
    "MATERIALTWIN_DB",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db")

# ── 우리가 붙인 주석 — 측정 조건이 아니다 ────────────────────────────────────
# 이것들이 있고 없고로 두 행이 갈리면 그건 **적재 이력**이지 다른 측정이 아니다.
# `*_before_correction`(§521 되돌리기) · `correction_reason`(§521 선언) ·
# `verdict_*`(§464 큐레이션 접두어, 51차 MA 의 동률 판정) · `migrated_from` · `method_restored`.
# **`source_table`·`figure` 는 여기 넣지 마라.** 그건 그 문서 안의 **어느 표/그림인가**라
# 측정을 가르는 축이다. 넣었더니 BIO-PSA 66군이 "조건 동일" 로 올라왔는데, 같은 논리면
# `Table 3` 과 `Table 5` 도 같아진다 — 그 66군은 손확인으로 올려야지 규칙으로 올릴 것이 아니다.
ANNOTATION_KEYS = {"correction_reason", "corrected_by", "migrated_from", "method_restored",
                   "duplicate_of", "duplicate_group", "duplicate_note"}
ANNOTATION_PREFIXES = ("verdict_", "merge_", "core_", "same_alloy_")


def is_annotation(k: str) -> bool:
    kl = k.lower()
    return (kl in ANNOTATION_KEYS or kl.endswith("_before_correction")
            or kl.startswith(ANNOTATION_PREFIXES))


# ── 조건 키 이름 정규화 ──────────────────────────────────────────────────────
# §547 이 센 여섯 흔들림 + DB 전수(2,020 키)에서 실제로 걸리는 것만 넣는다.
# **넓히면 오탐이 는다** — 그래서 부류로 가르고 손확인을 붙인다.
ALIAS = {
    # 규격/시험법
    "test": "standard", "test_standard": "standard", "test_method": "standard",
    "testing_standard": "standard", "test_norm": "standard",
    # 방향
    "direction": "axis", "orientation": "axis",
    # 방법 서술
    "method_detail": "method", "measurement_method": "method", "test_mode": "mode",
    # 두께
    "thickness": "thickness_um", "thickness_um": "thickness_um", "film_thickness_um": "thickness_um",
    # 온도 구간 — 자유서술로 적히는 축이라 이름이 넷으로 갈려 있다.
    "temp_range_c": "temperature_range_c", "temperature_range": "temperature_range_c",
    "temperature_range_C": "temperature_range_c", "range": "temperature_range_c",
    # 습도
    "humidity_rh": "humidity_pct", "relative_humidity_pct": "humidity_pct", "rh_pct": "humidity_pct",
}
# 구간 서술은 **숫자 쌍**으로 읽는다 — `"40-125"` · `"40C to 125C, below Tg"` · `"40-125 degC"`
# 가 같은 구간인데 글자로는 셋 다 다르다(51차 MA 가 못 본 자리다).
RANGE_AXES = {"temperature_range_c", "temperature_range_k", "strain_rate_range_s",
              "sweep_range_hz"}
# `"40-125"` 의 `-` 는 부호가 아니라 구분자다 — 그냥 `-?\d+` 로 읽으면 (40, **-125**) 가 된다.
_RANGE_NUM = re.compile(r"(?<![\d.])-?\d+(?:\.\d+)?")
# 단위가 키 이름에 박힌 축 — 값을 기준 단위로 환산해 **같은 조건인지**를 정확히 본다.
# (키 이름만 통일하면 `temperature_k=300` 과 `temperature_c=300` 이 같아져 버린다.)
UNIT_AXES = {
    "temperature": ("temperature_c", {"c": (1.0, 0.0), "C": (1.0, 0.0),
                                      "k": (1.0, -273.15), "K": (1.0, -273.15)}),
    "reference_temperature": ("reference_temperature_c", {"c": (1.0, 0.0), "C": (1.0, 0.0),
                                                          "k": (1.0, -273.15), "K": (1.0, -273.15)}),
    "aging_temperature": ("aging_temperature_c", {"c": (1.0, 0.0), "C": (1.0, 0.0),
                                                  "k": (1.0, -273.15), "K": (1.0, -273.15)}),
    "exposure_temperature": ("exposure_temperature_c", {"c": (1.0, 0.0), "C": (1.0, 0.0),
                                                        "k": (1.0, -273.15), "K": (1.0, -273.15)}),
    "frequency": ("frequency_hz", {"hz": (1.0, 0.0), "Hz": (1.0, 0.0), "khz": (1e3, 0.0),
                                   "kHz": (1e3, 0.0), "mhz": (1e6, 0.0), "MHz": (1e6, 0.0),
                                   "ghz": (1e9, 0.0), "GHz": (1e9, 0.0)}),
    "thickness": ("thickness_um", {"um": (1.0, 0.0), "mm": (1e3, 0.0), "nm": (1e-3, 0.0),
                                   "μm": (1.0, 0.0), "µm": (1.0, 0.0)}),
    "wavelength": ("wavelength_nm", {"nm": (1.0, 0.0), "um": (1e3, 0.0), "μm": (1e3, 0.0)}),
}
_UNIT_RE = re.compile(r"^(?P<base>[a-z_]+?)_(?P<unit>[a-zA-Zμµ]+)$")
# **값 안에 단위가 들어간 표기**도 같은 축이다 — 브리프가 준 Kapton 세 행이 정확히 이것이다
# (`thickness: "37.5 um"` 대 `thickness_um: 37.5`). 숫자로 못 바꾸면 자연키가 안 걸린다.
_NUM_UNIT_RE = re.compile(r"^\s*(?P<num>-?\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Zμµ°Ω/]+)\s*$")


def _split_num_unit(v):
    """`"37.5 um"` → (37.5, 'um'). 숫자만이거나 단위가 없으면 None."""
    if not isinstance(v, str):
        return None
    m = _NUM_UNIT_RE.match(v)
    return (float(m.group("num")), m.group("unit")) if m else None

# 값 표기 흔들림 — 같은 물리 방향/상태를 다르게 적은 것만 흡수한다.
VALUE_CANON = {
    "in-plane": "in-plane", "in plane": "in-plane", "x-y": "in-plane", "xy": "in-plane",
    "x,y": "in-plane", "through-plane": "through-plane", "through plane": "through-plane",
    "z": "through-plane", "normal": "through-plane", "out-of-plane": "through-plane",
    "md": "md", "machine direction": "md", "td": "td", "transverse direction": "td",
}

# 이 축이 갈리면 **정당한 반복**이다 — 반복 시편·통계량·세트 항 (§435).
REPEAT_AXES = {"run", "specimen", "specimen_number", "specimen_id", "sample", "sample_id",
               "replicate", "replicates", "test_number", "trial", "batch", "lot",
               "statistic", "bound", "set_id", "term", "term_index", "prony_term",
               "n_terms", "unit_of_term", "component", "layer", "position"}
# 등급·제품이 갈리면 다른 재료 판이다 — 값이 같아도 중복이 아니다.
GRADE_AXES = {"grade", "grade_scope", "temper", "product_family", "composition", "filler",
              "filler_content_wt", "matrix", "substrate", "backing", "form", "phase",
              "microstructure", "state", "material_state", "cure", "process", "species"}


# 괄호 안 수식어를 떼는 것은 **방향축에만** 건다. 규격에 걸면
# `JIS C-2318` 과 `JIS C-2318 (modified to TDF)` 가 같아져 버린다 — 그건 손확인 대상이지
# 자동으로 같다고 할 것이 아니다(§435 가 자동 병합을 금지한 이유와 같은 자리다).
PAREN_STRIP_AXES = {"axis", "loading", "mode"}


def _canon_value(v, key=None):
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return round(float(v), 9) + 0.0
    low = " ".join(str(v).strip().lower().split())
    if key in PAREN_STRIP_AXES:
        base = low.split("(")[0].strip().strip(",").strip()
        return VALUE_CANON.get(base, base or low)
    return VALUE_CANON.get(low, low)


_PAREN = re.compile(r"\s*\([^)]*\)\s*")


def _paren_base(v):
    """괄호 수식어를 뗀 알맹이. 두 값이 이것만 다르면 **표기 흔들림 의심**이다."""
    if not isinstance(v, str):
        return v
    return " ".join(_PAREN.sub(" ", v).split()).strip().strip(",")


def norm_conditions(raw):
    """조건 JSON → (측정 조건 정규화 dict, 주석 키 집합). 키 이름·단위·값 표기를 흡수한다."""
    if not raw:
        return {}, set()
    try:
        d = json.loads(raw)
    except (TypeError, ValueError):
        return {}, set()
    if isinstance(d, str):                      # 이중 인코딩
        try:
            d = json.loads(d)
        except (TypeError, ValueError):
            return {}, set()
    if not isinstance(d, dict):
        return {}, set()
    out, ann = {}, set()
    for k, v in d.items():
        if is_annotation(k):
            ann.add(k)
            continue
        kl = k.lower()
        # ① 단위가 이름에 박힌 축은 기준 단위로 환산한다.
        m = _UNIT_RE.match(kl)
        handled = False
        base = m.group("base") if m else kl
        if base in UNIT_AXES:
            canon, table = UNIT_AXES[base]
            # ①-a 단위가 **키 이름**에 있다.
            unit = k.rsplit("_", 1)[-1] if m else None
            fac = table.get(unit) or table.get((unit or "").lower())
            num = v if isinstance(v, (int, float)) and not isinstance(v, bool) else None
            # ①-b 단위가 **값 안**에 있다(`"37.5 um"`). 키 쪽 단위보다 값 쪽을 우선한다.
            nu = _split_num_unit(v)
            if nu:
                f2 = table.get(nu[1]) or table.get(nu[1].lower())
                if f2:
                    num, fac = nu[0], f2
            if fac is not None and num is not None:
                out[canon] = round(float(num) * fac[0] + fac[1], 6)
                handled = True
            elif fac is not None:
                out[canon] = _canon_value(v, canon)
                handled = True
        if handled:
            continue
        # ② 이름만 흔들린 축.
        nk = ALIAS.get(k, ALIAS.get(kl, kl))
        if nk in RANGE_AXES:
            nums = _RANGE_NUM.findall(str(v)) if not isinstance(v, (list, tuple)) else [str(x) for x in v]
            if len(nums) >= 2:
                out[nk] = (round(float(nums[0]), 6), round(float(nums[1]), 6))
                continue
        out[nk] = _canon_value(v, nk)
    return out, ann


def cond_sig(cond: dict) -> str:
    return json.dumps({k: str(v) for k, v in sorted(cond.items())}, ensure_ascii=False)


def val_key(value_num, value_text, unit):
    """값의 지문. 부동소수 잡음(1e-5 대 9.999999999999999e-06)을 흡수한다."""
    if value_num is None:
        return ("t", (value_text or "").strip(), (unit or "").strip())
    if value_num == 0:
        return ("n", 0.0, (unit or "").strip())
    mag = math.floor(math.log10(abs(value_num)))
    return ("n", round(value_num / (10.0 ** mag), 9), mag, (unit or "").strip())


# ── 출처 계보 — 같은 문서가 출처 행 둘로 들어와 있을 수 있다(§185·§456) ──────
def source_families(c):
    """같은 문서로 보이는 출처 id 를 한 대표 id 로 묶는다. 제목의 핵심 토큰이 같으면 한 집안."""
    rows = c.execute("select id, kind, coalesce(doi,''), coalesce(url,''), coalesce(title,'') "
                     "from source").fetchall()
    by_doi, by_key = defaultdict(list), defaultdict(list)
    for sid, kind, doi, url, title in rows:
        if doi:
            by_doi[doi].append(sid)
        # 제목에서 문서번호(EI-10172/QE-10172 처럼)와 괄호를 떼고 남는 알파벳 토큰.
        t = re.sub(r"[^a-z0-9 ]+", " ", title.lower())
        toks = tuple(sorted({w for w in t.split() if len(w) > 3 and not w.isdigit()}))
        if toks:
            by_key[(kind, toks)].append(sid)
    fam = {}
    for group in list(by_doi.values()) + list(by_key.values()):
        if len(group) > 1:
            rep = min(group)
            for sid in group:
                fam[sid] = rep
    return fam


def load_rows(c):
    q = """select pv.id, pv.material_id, m.name, pv.property_key, pv.value_num, pv.value_text,
                  pv.unit, pv.conditions, pv.method, pv.quality_tier, pv.source_id,
                  coalesce(pv.source_detail,''), coalesce(pv.notes,'')
           from property_value pv join material m on m.id = pv.material_id"""
    for r in c.execute(q):
        yield r


VERDICT_CERTAIN = "certain"
VERDICT_SUSPECT = "suspect"
VERDICT_REPEAT = "repeat"


def classify(members):
    """한 (재료·키·출처·값) 군 안에서 조건을 비교해 부류를 정한다.

    **확실**은 정규화(키 이름·단위·주석 제거)만으로 조건이 글자까지 같아진 것이다.
    값 표기를 주물러야 같아지는 것(괄호 수식어·한쪽에만 적힌 조건)은 **의심**으로 내린다 —
    손으로 봐야 한다. 반복 시편·통계량·등급이 갈리면 **정당한 반복**이다(§435).
    """
    sigs = {m["sig"] for m in members}
    if len(sigs) == 1:
        return VERDICT_CERTAIN, "정규화 조건 동일"
    allk = set().union(*(set(m["cond"]) for m in members))
    missing, paren, real = set(), set(), set()
    for k in allk:
        present = [m["cond"][k] for m in members if k in m["cond"]]
        if len(present) < len(members):
            missing.add(k)
        vals = {v for v in present}
        if len(vals) > 1:
            if len({_paren_base(v) for v in present}) == 1:
                paren.add(k)
            else:
                real.add(k)
    if real & REPEAT_AXES:
        return VERDICT_REPEAT, "반복/세트 축이 갈린다: " + ",".join(sorted(real & REPEAT_AXES))
    if real & GRADE_AXES:
        return VERDICT_REPEAT, "등급/제품 축이 갈린다: " + ",".join(sorted(real & GRADE_AXES))
    if real:
        return VERDICT_REPEAT, "조건값이 실제로 다르다: " + ",".join(sorted(real))
    # **한쪽에만 있는 것은 확정이 아니다.** 손확인에서 반례가 나왔다 —
    # TAIFLEX 2UPDR2010JD 는 `grade` 가 한쪽에만 있는데 그 grade 가 곧 재료 이름이라 중복이고,
    # Norseal F-12·Arisawa C33 도 같다. 값이 실제로 갈렸을 때만 반복으로 확정한다.
    if missing & (REPEAT_AXES | GRADE_AXES):
        return VERDICT_SUSPECT, ("반복/등급 축이 한쪽에만 적혔다: "
                                 + ",".join(sorted(missing & (REPEAT_AXES | GRADE_AXES))))
    why = []
    if paren:
        why.append("괄호 수식어만 다르다: " + ",".join(sorted(paren)))
    if missing:
        why.append("한쪽에만 적힌 조건: " + ",".join(sorted(missing)))
    return VERDICT_SUSPECT, " / ".join(why)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", help="결과를 이 경로에 쓴다")
    ap.add_argument("--show", choices=[VERDICT_CERTAIN, VERDICT_SUSPECT, VERDICT_REPEAT])
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--cross-source", action="store_true",
                    help="출처 행이 다르지만 같은 문서인 군도 낸다(§185·456)")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    fam = source_families(c) if a.cross_source else {}
    groups = defaultdict(list)
    for (pid, mid, mname, key, vn, vt, unit, raw, method, tier, sid, sdet, notes) in load_rows(c):
        cond, ann = norm_conditions(raw)
        skey = fam.get(sid, sid) if a.cross_source else sid
        groups[(mid, key, skey, val_key(vn, vt, unit))].append({
            "id": pid, "material_id": mid, "material": mname, "key": key, "value_num": vn,
            "value_text": vt, "unit": unit, "method": method, "tier": tier, "source_id": sid,
            "source_detail": sdet, "notes": notes, "raw": raw, "cond": cond,
            "sig": cond_sig(cond), "ann": sorted(ann)})

    out = {VERDICT_CERTAIN: [], VERDICT_SUSPECT: [], VERDICT_REPEAT: []}
    for gk, members in groups.items():
        if len(members) < 2:
            continue
        members.sort(key=lambda m: m["id"])
        verdict, why = classify(members)
        # 같은 군 안에서도 조건이 동일한 부분집합은 확실한 중복이다 — 버킷을 나눠 다시 본다.
        buckets = defaultdict(list)
        for m in members:
            buckets[m["sig"]].append(m)
        exact = [b for b in buckets.values() if len(b) > 1]
        if verdict != VERDICT_CERTAIN and exact:
            for b in exact:
                out[VERDICT_CERTAIN].append({"why": "정규화 조건 동일(혼합군 안)",
                                             "rows": b, "cross_source":
                                             len({x["source_id"] for x in b}) > 1})
            rest = [m for m in members if len(buckets[m["sig"]]) == 1]
            if len(rest) < 2:
                continue
            members = rest
            verdict, why = classify(members)
        out[verdict].append({"why": why, "rows": members,
                             "cross_source": len({m["source_id"] for m in members}) > 1})

    print(f"DB {DB}")
    print(f"전체 물성값 {c.execute('select count(*) from property_value').fetchone()[0]:,}행")
    for v in (VERDICT_CERTAIN, VERDICT_SUSPECT, VERDICT_REPEAT):
        n_rows = sum(len(g["rows"]) for g in out[v])
        extra = sum(len(g["rows"]) - 1 for g in out[v])
        print(f"  {v:8s} 군 {len(out[v]):5d} · 행 {n_rows:6d} · 여분행 {extra:6d}")
    if a.show:
        for g in out[a.show][: a.limit]:
            r0 = g["rows"][0]
            print(f"\n── {r0['material'][:52]} | {r0['key']} | {r0['value_num'] if r0['value_num'] is not None else r0['value_text']} {r0['unit'] or ''}")
            print(f"   사유: {g['why']}{'  [출처행 다름]' if g['cross_source'] else ''}")
            for m in g["rows"]:
                print(f"   pv{m['id']:<6d} src{m['source_id']} t{m['tier']} {m['method']:9s} {m['raw']}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump({k: [{"why": g["why"], "cross_source": g["cross_source"],
                            "rows": [{kk: vv for kk, vv in m.items() if kk != "cond"}
                                     for m in g["rows"]]} for g in v]
                       for k, v in out.items()}, f, ensure_ascii=False, indent=1)
        print(f"\n→ {a.json}")
    return out


if __name__ == "__main__":
    main()
