#!/usr/bin/env python3
# 조건 어휘를 통일한다 — 같은 축을 다른 키 이름으로 적은 것을 한 이름으로 모으고,
# `direction` 자유서술을 정규값과 원문으로 가른다. **값·등급·method·출처는 한 칸도 안 고친다.**
#
# 왜 있나(52차 NA). 51차 MA 가 동률 3,975군을 축으로 갈랐더니 81군이 **축이 아니라 표기**로
# 갈려 있었다(§547). 그리고 그 흔들림이 더 나쁜 것을 가린다 — 병합기 자연키에 `conditions` 가
# 들어 있어서, 키 이름이 다르면 같은 값이 두 번 들어와도 안 걸린다.
# 51차 MC 는 `_direction_clash` 오탐 39종 중 38종이 **같은 방향의 다른 표기**임을 밝히고
# *"진짜 고칠 자리는 `direction` 어휘다"* 로 넘겼다(§551).
#
# 정본을 고르는 규칙(다수결이 아니다) ─────────────────────────────────────────
#   ① **코드가 읽는 이름**이 하나뿐이면 그것.  `_DESCRIPTIVE_COND`·`_RATE_COND`·`_COND_SHOW`·
#      `_temp_distance`·프런트 `formatConditions` 를 전수로 봤다.
#   ② 없으면 **taxonomy `condition_axes`** 가 선언한 이름. 조건축을 어휘로 선언하는 곳은
#      코드에서 거기 하나뿐이다(171종).
#   ③ 둘 다 없고 **대소문자만 다르면** taxonomy 의 전체 관례를 따른다 — 171종 중 166종이
#      전부 소문자다. 그래서 `temperature_C` → `temperature_c` 다.
#   ④ 그래도 안 갈리면 행수 다수.
#
# **환산이 필요하면 합치지 않는다** — 그건 정정이 아니라 채굴이다.
#   `thickness`("37.5 um" 문자열) ↔ `thickness_um`(숫자 25) 가 그 예다.
#
# 안전장치 ──────────────────────────────────────────────────────────────────
#   · 48차 JA 의 `corrections` 경로로만 바꾼다(§521). 옛 값이 `<칸>_before_correction` 에 남는다.
#   · 51차 MA 의 `blocked_rows` 필터를 그대로 쓴다(§548) — 운영에 새 행을 만드는 군은 뺀다.
#   · 옮길 자리에 이미 다른 값이 있으면(두 키 공존) 그 행은 건너뛴다.
#   · `_rep_rank` 5번째 자리가 `len(conditions)` 라 정정이 대표값을 뒤집을 수 있다 —
#     `plan` 이 전/후 대표값을 전수로 대조해 바뀐 군을 낸다.
#
# 사용:
#   MATERIALTWIN_DATA_DIR=<라이브> python3 normalize_condition_keys.py census
#   … plan            영향 행수·막힌 군·대표값 전/후 대조
#   … gen <out.json>  `corrections` 선언 생성
import argparse
import json
import os
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from app.catalog_compare import _rep_rank  # noqa: E402
from app.direction_vocab import normalize as dir_normalize  # noqa: E402
from tie_verdicts import PV, blocked_rows, groups, load  # noqa: E402

BY = os.environ.get("NORM_BY", "52차 NA")
VERBATIM = "direction_verbatim"

# ── 통일할 키 (옛 이름 → 정본) ────────────────────────────────────────────────
# 전부 **공존 0행**을 확인했다. 값의 종류·단위가 같고 환산이 필요 없는 것만이다.
RENAME: dict[str, str] = {}

# ① 대소문자만 다른 것 — 39쌍 전부. 규칙 ③(taxonomy 관례가 전부 소문자).
for _k in ("temperature_C", "temperature_K", "temperature_F",
           "reference_temperature_C", "reference_temperature_K",
           "temperature_range_C", "temperature_range_K", "temperature_range_F",
           "temperature_min_K", "temperature_max_K",
           "frequency_Hz", "frequency_GHz", "frequency_range_Hz",
           "stress_MPa", "stress_Pa", "pressure_Pa", "pressure_kPa",
           "sintering_temperature_C", "humidity_RH", "reference_tg_C",
           "load_N", "load_range_mN", "exposure_temperature_C",
           "heating_rate_K_per_min", "heating_rate_C_min", "cooling_rate_C_per_min",
           "range_C", "deposition_temperature_C", "bath_temperature_C",
           "melting_temperature_K", "melting_temperature_C",
           "preheat_C", "PDI", "SOC", "Mn_g_per_mol", "D50_um", "DOL_um"):
    RENAME[_k] = _k.lower()
RENAME["CS_MPa"] = "cs_mpa"
RENAME["cs_MPa"] = "cs_mpa"

# ② `_percent` ↔ `_pct` — 같은 단위의 다른 철자. taxonomy 는 `_pct` 를 쓴다.
for _k in ("strain_percent", "shear_strain_percent", "relative_humidity_percent",
           "deflection_percent", "relative_density_percent", "strain_amplitude_percent",
           "humidity_rh_percent"):
    RENAME[_k] = _k[: -len("percent")] + "pct"

# ③ `test_` 접두 — 조건은 정의상 시험 조건이라 접두가 정보를 더하지 않는다.
#    **단 `test_standard`·`test_geometry` 는 예외다** — 규칙 ①·②가 반대로 가리킨다(아래 ④).
for _k, _v in (("test_temperature", "temperature"), ("test_temperature_c", "temperature_c"),
               ("test_temperature_k", "temperature_k"),
               ("test_temperature_note", "temperature_note"),
               ("test_temperature_status", "temperature_status"),
               ("test_temperature_stated", "temperature_stated"),
               ("test_mode", "mode"), ("test_liquid", "liquid"),
               ("test_instrument", "instrument"), ("test_condition", "condition"),
               ("test_specimen", "specimen"), ("test_apparatus", "apparatus"),
               ("test_speed", "speed"), ("test_speed_mm_min", "speed_mm_min"),
               ("test_speed_mm_per_min", "speed_mm_per_min"),
               ("test_voltage_V", "voltage_v"), ("voltage_V", "voltage_v")):
    RENAME[_k] = _v

# ④ 낱말이 다른 같은 축.
#    `standard` → `test_standard` : 규칙 ① — `dyna_export._DESCRIPTIVE_COND` 가 읽는 이름이
#      `test_standard` 하나다. 규칙 ②도 같은 쪽이다(taxonomy 17 대 5). 그리고 `standard` 는
#      **재료 속성 쪽에서 이미 '재료 규격'** 으로 쓰이고 있다(`material_metadata.py`) —
#      같은 낱말이 두 층에서 다른 뜻이면 조건 쪽이 비켜야 한다.
#    `geometry` → `test_geometry` : 규칙 ②(taxonomy 가 `test_geometry` 만 선언한다).
#    `method`·`measurement_method` → `method_detail` : 규칙 ②(taxonomy 12 대 3 대 1).
#      **`test_method` 은 합치지 않는다** — `method_detail` 과 242행에서 공존하고, 그 242행에서
#      두 칸은 규격/절차(`test_method`)와 기법 세부(`method_detail`)로 층이 갈린다.
#      그리고 `test_method` 은 적재기가 스스로 쓰는 칸이라(자유서술 method 를 거기 넣는다)
#      은퇴시키면 다음 적재가 옛 어휘를 되살린다(§466).
RENAME["standard"] = "test_standard"
RENAME["geometry"] = "test_geometry"
RENAME["method"] = "method_detail"
RENAME["measurement_method"] = "method_detail"

# ⑤ 같은 단위의 다른 철자(환산 없음).
RENAME["duration_hr"] = "duration_h"
RENAME["strain_rate_1/s"] = "strain_rate_s"          # 규칙 ① — `_RATE_COND` 가 읽는 이름
RENAME["strain_rate_per_s"] = "strain_rate_s"
RENAME["reference_strain_rate_1/s"] = "reference_strain_rate_s"
RENAME["shear_rate_1_s"] = "shear_rate_1/s"          # 규칙 ② — taxonomy 가 선언한 이름
RENAME["shear_rate_1_per_s"] = "shear_rate_1/s"
RENAME["rate_mm/min"] = "rate_mm_min"                # 규칙 ④ — taxonomy 가 둘 다 선언한다
RENAME["rate_mm_per_min"] = "rate_mm_min"
RENAME["crosshead_speed_mm_per_min"] = "crosshead_speed_mm_min"   # 규칙 ①(_DESCRIPTIVE_COND)
RENAME["heating_rate_K_per_min"] = "heating_rate_k_min"           # 규칙 ②
RENAME["heating_rate_k_per_min"] = "heating_rate_k_min"
RENAME["angular_frequency_rad_s"] = "angular_frequency_rad_per_s"  # 규칙 ④

# **합치지 않기로 한 것** — 사유를 코드에 남긴다. 다음 배치가 다시 세지 않게.
NOT_MERGED = {
    "thickness ↔ thickness_um·_mm·_m": "값이 단위를 품은 문자열('37.5 um')이라 숫자 칸으로 옮기려면 "
                                       "환산이 필요하다. 환산은 정정이 아니라 채굴이다.",
    "temperature_c ↔ temperature_k": "C 와 K 는 같은 축의 다른 단위다. 합치려면 환산해야 한다.",
    "thickness_mil ↔ thickness_mm · film_thickness_nm ↔ _um · aging_time ↔ aging_time_h 등":
        "전부 환산이 필요하다.",
    "method_detail ↔ test_method": "242행에서 공존하고 그 행들에서 층이 갈린다"
                                   "(규격/절차 대 기법 세부).",
    "test ↔ test_method": "`test` 는 하중 모드다(`dyna_export._MODE_COND` 가 그렇게 읽는다).",
    "condition ↔ conditioning": "`condition` 은 야금 상태(annealed·as-drawn)고 `conditioning` 은 "
                                "조습 전처리(As received·C-24/23/50)다. ISO 291 코드가 양쪽에 "
                                "있어 겹쳐 보이지만 축이 다르다. "
                                "**`tie_verdicts.SYN` 이 이 둘을 같다고 본 것은 틀렸다.**",
    "type ↔ test_type": "`type` 은 물리량의 종류(mu_i·G')고 `test_type` 은 시험 종류(lap shear)다.",
    "axis(그래프축 서술) ↔ direction": "`axis` 값 80종 중 22종·약 320행이 디지타이즈 그림의 "
                                      "**축 서술**이다('좌축 이중(ksi 290..29 …)'). 방향이 아니다.",
    "porosity ↔ porosity_pct · angle ↔ angle_deg · strain ↔ strain_pct":
        "무단위 칸과 % 칸이라 값을 봐야 갈린다. 환산 위험이 있어 안 건드렸다.",
}


def db_path() -> str:
    d = os.environ.get("MATERIALTWIN_DATA_DIR")
    if not d:
        sys.exit("MATERIALTWIN_DATA_DIR 를 지정해라(브리프 30·49).")
    return str(Path(d) / "materialtwin.db")


def _is_bookkeeping(k: str) -> bool:
    return (k.endswith("_before_correction")
            or k in ("correction_reason", "corrected_by", "correction_evidence"))


def new_conditions(pv: PV, move_axis: bool = True):
    """(새 조건, 무엇을 했는지 목록, 건너뛴 사유 목록). 바뀔 것이 없으면 (None, [], [])."""
    old = pv.conditions or {}
    if not isinstance(old, dict) or not old:
        return None, [], []
    cur = dict(old)
    acts: list[str] = []
    skips: list[str] = []

    # ① 키 이름 통일
    for src, dst in RENAME.items():
        if src not in cur:
            continue
        if dst in cur:
            skips.append(f"{src}→{dst}: 대상 칸에 이미 값이 있다")
            continue
        cur[dst] = cur.pop(src)
        acts.append(f"{src}→{dst}")

    # ② `axis` 가 **방향값**이고 `direction` 이 비었으면 옮긴다.
    #    그래프축 서술은 `dir_normalize` 가 None 을 돌려줘 저절로 걸러진다.
    #    **군 단위로 결정한다**(`move_axis`) — 한 군 안에서 어떤 행의 `axis` 는 방향이고
    #    어떤 행의 `axis` 는 그래프축 서술이면, 방향 쪽만 칸이 늘어 대표값이 뒤집힌다.
    #    실측 — Ehrler 2004 PCB 라미네이트 10종에서 TMA 행(`axis: "z (through-thickness)"`)만
    #    칸이 늘어 대표 Tg 가 **TMA 458 K → DMA 481 K** 로 넘어갔다. 시험법을 바꾸는 것은
    #    이 배치가 할 일이 아니다.
    if move_axis and "axis" in cur and "direction" not in cur and dir_normalize(cur["axis"]):
        cur["direction"] = cur.pop("axis")
        acts.append("axis→direction")

    # ③ `direction` 을 정규값과 원문으로 가른다.
    #
    # **원문은 정규값과 같아도 반드시 남긴다.** 조건 칸 수가 `_rep_rank` 5번째 자리라
    # 일부 행에만 칸을 더하면 대표값이 조용히 뒤집힌다(§548). `direction` 을 가진 행은
    # **전부 정확히 한 칸** 늘어나야 군 안의 순서가 보존된다. 실측 — 이 규율 없이 돌렸더니
    # 67군이 뒤집혔고 그중 절반이 "한쪽만 원문 칸이 붙어서" 였다.
    # 정규값을 못 정한 행은 `direction` 을 **null 로 비운다**(지우지 않는다) — 지우면
    # 그 행만 칸이 안 늘어 같은 사고가 난다. null 은 `_direction_clash`·`_COND_SHOW`·
    # 프런트 `formatConditions` 가 전부 "없는 것" 으로 읽는다.
    if "direction" in cur and VERBATIM not in cur:
        raw = cur["direction"]
        if isinstance(raw, str) and raw.strip():
            canon = dir_normalize(raw)
            cur["direction"] = canon
            cur[VERBATIM] = raw
            acts.append(f"direction 정규화 → {canon or '(미배정 · null)'}")

    if {k: v for k, v in cur.items()} == old:
        return None, [], skips
    return cur, acts, skips


def build(db):
    pvs = load(db, numeric_only=False)
    G = groups(pvs)
    # `axis`→`direction` 이동은 **군 전체가 방향일 때만** 한다(위 ② 참조).
    move = {}
    for k, rows in G.items():
        ax = [p for p in rows if isinstance((p.conditions or {}).get("axis"), str)]
        move[k] = bool(ax) and all(dir_normalize(p.conditions["axis"]) for p in ax)
    plan = []
    skips = Counter()
    for pv in pvs:
        cur, acts, sk = new_conditions(pv, move.get((pv.material_id, pv.property_key), False))
        for s in sk:
            skips[s] += 1
        if cur is not None:
            plan.append((pv, cur, acts))
    return pvs, plan, skips


def _rank_key(pv, cond):
    class _P:
        pass
    p = _P()
    p.property_key, p.conditions, p.quality_tier = pv.property_key, cond, pv.quality_tier
    p.value_num, p.id = pv.value_num, pv.id
    return _rep_rank(p)


def plan_report(db, verbose=False):
    pvs, plan, skips = build(db)
    print(f"[DB] {db}\n대상 행 {len(plan)} / 전체 {len(pvs)}")
    act = Counter()
    for _, _, acts in plan:
        for a in acts:
            act[a.split(" ")[0] if a.startswith("direction 정규화") else a] += 1
    print("\n-- 한 일별 행수 --")
    for a, n in act.most_common(60):
        print(f"  {n:>6}  {a}")
    if skips:
        print("\n-- 건너뛴 행(대상 칸에 이미 값이 있다) --")
        for s, n in skips.most_common():
            print(f"  {n:>6}  {s}")

    # 막힌 군(§548) — 운영 전파가 불가능한 행
    G = groups(pvs)
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in pvs)
    blocked = {}
    for k in {(pv.material_id, pv.property_key) for pv, _, _ in plan}:
        b = blocked_rows(G, k, cnt)
        if b:
            # **군 전체를 뺀다.** 막힌 행 하나만 빼면 그 행만 조건 칸이 안 늘어
            # `_rep_rank` 의 `len(conditions)` 자리에서 대표값이 뒤집힌다(§548).
            # 51차 MA 의 `gen` 이 같은 이유로 군 단위로 뺀다.
            blocked[k] = b
    nb = sum(len(rows) for k, rows in G.items() if k in blocked)
    print(f"\n-- 전파 불가로 뺄 군 {len(blocked)} (그 군의 행 {nb}) --")
    wc = Counter(why for v in blocked.values() for _, why in v)
    for w, n in wc.most_common():
        print(f"  {n:>6}행이 그 사유로 막혔다  {w}")

    # 대표값 전/후
    newc = {pv.id: cur for pv, cur, _ in plan}
    drop = {p.id for k in blocked for p in G[k]}
    before = after = 0
    changed = []
    for k, rows in G.items():
        if len(rows) < 2:
            continue
        b = sorted(rows, key=lambda p: _rep_rank(p))[0]
        a = sorted(rows, key=lambda p: _rank_key(
            p, newc[p.id] if (p.id in newc and p.id not in drop) else p.conditions))[0]
        before += 1
        if a.id != b.id:
            after += 1
            changed.append((k, b, a))
    print(f"\n-- 대표값 전/후 (후보 둘 이상 {before}군) --  바뀐 군 {after}")
    for k, b, a in changed[:60]:
        print(f"  재료{k[0]} {k[1]}: pv{b.id}({b.value_num}) → pv{a.id}({a.value_num})")
    return plan, drop


def gen(db, out_path):
    plan, drop = plan_report(db)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.close()
    corr = []
    for pv, cur, acts in plan:
        if pv.id in drop:
            continue
        # 적재기는 `correction_reason` 을 통째로 덮는다. 이미 정정된 행(51차 MA 의 동률 판정
        # 1,511행)의 사유가 사라지지 않게 **앞 사유를 내 사유 안에 옮겨 적는다.**
        prev = (pv.conditions or {}).get("correction_reason")
        keep = f" | 앞 정정 사유({(pv.conditions or {}).get('corrected_by') or '?'}): {prev}" if prev else ""
        corr.append({
            "target": {"property_value_id": pv.id, "material_id": pv.material_id,
                       "property_key": pv.property_key},
            "by": BY,
            "reason": ("조건 어휘 통일(브리프 547·551) — 값·단위·등급·method·출처는 그대로다. "
                       + " · ".join(acts) + keep),
            "set": {"conditions": cur},
        })
    doc = {"_comment": (
        "52차 NA — 조건 키 이름 통일과 `direction` 정규값 분리다. **값은 한 행도 안 고친다.** "
        "정본 선정 근거와 합치지 않은 쌍의 사유는 `normalize_condition_keys.py` 머리말에 있다."),
        "_not_merged": NOT_MERGED,
        "corrections": corr}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"\n{out_path}: 정정 선언 {len(corr)}건 (전파 불가로 뺀 행 {len(drop)})")


def census():
    db = db_path()
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    cnt, mats = Counter(), defaultdict(set)
    for m, c in con.execute("select material_id,conditions from property_value "
                            "where conditions is not null"):
        d = json.loads(c)
        if not isinstance(d, dict):
            continue
        for k in d:
            cnt[k] += 1
            mats[k].add(m)
    print(f"[DB] {db}\n조건키 {len(cnt)}종 · 조건 있는 행 {sum(1 for _ in [0])}")
    print(f"총 조건키 {len(cnt)}종")
    low = defaultdict(list)
    for k in cnt:
        low[k.lower()].append(k)
    pairs = [v for v in low.values() if len(v) > 1]
    print(f"\n-- 대소문자만 다른 쌍 {len(pairs)} --")
    for ks in sorted(pairs, key=lambda ks: -sum(cnt[k] for k in ks)):
        print("  " + " ↔ ".join(f"{k}({cnt[k]})" for k in sorted(ks, key=lambda k: -cnt[k])))
    print(f"\n-- 통일 대상 {len(RENAME)}쌍 --")
    for a, b in sorted(RENAME.items(), key=lambda x: -cnt[x[0]]):
        print(f"  {cnt[a]:>6}행  {a} → {b} ({cnt[b]}행)")
    print("\n-- 합치지 않은 것 --")
    for k, v in NOT_MERGED.items():
        print(f"  · {k}\n      {v}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("census")
    sub.add_parser("plan")
    g = sub.add_parser("gen")
    g.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "census":
        census()
    elif a.cmd == "plan":
        plan_report(db_path())
    else:
        gen(db_path(), a.out)


if __name__ == "__main__":
    main()
