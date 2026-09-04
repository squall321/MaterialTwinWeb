#!/usr/bin/env python3
# 구식 문자열 키 `conditions.temperature` 를 둘로 갈라 처리한다 — 숫자는 `temperature_k` 로 옮기고, 진술은 어휘로 접는다(63차 YA).
"""63차 YA — `conditions.temperature`(2,255행)를 정리한다. **값은 한 칸도 안 고친다.**

두 문제를 섞지 않는다.

**(1) 숫자가 문자열 키에 앉은 행 — `temperature_k` 로 옮긴다.**
단위 환산(°C·K → K)은 같은 양을 다른 눈금으로 옮기는 것이라 §43 의 역산 금지선 밖이다.
원문 표기는 적재기가 `temperature_before_correction` 에 남긴다(§594).

**그런데 숫자가 있다고 다 옮기면 안 된다.** 전수로 열어 보니 숫자 196행 중 **86행이
시험온도가 아니었다** — 등급명(`high-Tg (180 degC)` 적층판) · 공정온도(증착·어닐·건조) ·
구간의 끝(`alpha -30 to +70 degC` 의 70) · 승온율(`10 degC/min`) · 값 자신의 재기재
(`Tg = 683 degC` 행의 조건에 683 degC). **옮기면 값은 안 바뀌지만
`catalog_compare._temp_distance` 가 그것을 시험온도로 읽어 대표값 선택과 카드 태그가 바뀐다.**
그래서 **그 행의 `detail`·`notes` 가 그 수를 측정 온도라고 말하는 행만** 옮긴다.
근거는 아래 `SKIP` 표에 사유별로 pv 번호까지 못박아 둔다(§648 — 사유문은 다음 파동의 검색어다).

**(2) 숫자가 없는 진술 1,987행 — 어휘로 접는다.**
`room temperature` · `not printed` · `원문 미인쇄` 는 **원문이 온도를 안 찍었다는 정직한
진술**이지 결함이 아니다. 숫자로 바꾸면 없는 정밀도를 만든다. 문제는 같은 말을 88가지로
적는다는 것뿐이고, 조건이 병합기 자연키에 들어 있어 **표기가 흔들리면 중복 적재가 안 걸린다**
(§547). `app/temperature_vocab.py` 가 두 정규값으로 접고 원문은 `_before_correction` 이 지킨다.

조건 칸 수가 안 바뀌는 것이 이 배치의 안전장치다 — `temperature` 하나가 나가고
`temperature_k` 하나가 들어오며, `_before_correction` 은 `_condition_axis_count` 가 안 센다.
그래서 `_rep_rank` 의 다섯째 자리가 안 흔들린다(§548 이 `direction` 에서 겪은 사고가 여기서는
구조적으로 안 난다). 흔들릴 수 있는 것은 넷째 자리(`_temp_distance`)뿐이고 그것이 (1)의 표적이라
`plan` 이 전/후 대표값을 전수로 대조해 바뀐 군을 낸다.

사용:
  MATERIALTWIN_DATA_DIR=<라이브> python3 migrate_temperature_ya.py plan
  …                                                            gen <out.json>
"""
import argparse
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.catalog_compare import _rep_rank  # noqa: E402
from app.temperature_vocab import NOT_REPORTED, ROOM, kelvin, normalize, printed  # noqa: E402
from tie_verdicts import PV, PRIOR_MARKERS, groups, load  # noqa: E402

BY = "63차 YA"

# 값 자체가 온도인 물성 — `integrity_check` 의 「온도가 값인데 시험온도 조건」 규칙이 보는 목록과
# 글자까지 같다. 여기에 `temperature_k` 를 넣으면 **신규 위반이 생긴다.**
TEMP_VALUED = frozenset((
    'thermal.melting_point', 'thermal.glass_transition', 'thermal.max_service_temp',
    'thermal.min_service_temp', 'thermal.decomposition_temp', 'thermal.heat_deflection_temp',
    'thermal.vicat_softening', 'thermal.dilatometric_softening_point',
    'thermal.viscosity_reference_temperature'))

# ── 옮기지 않는 행 — 사유별로 pv 번호를 못박는다 ─────────────────────────────
#
# 전부 그 행의 `conditions.detail` 또는 `notes` 를 읽고 갈랐다. 사유 문장에 **무엇이 그 수의
# 정체인지**를 적어 둔다 — 다음 파동이 "숫자가 있는데 왜 안 옮겼지" 로 같은 149행을 다시 연다.
SKIP: dict[str, tuple[str, tuple[int, ...]]] = {
    "값 자신의 재기재·승온 상한·승온율": (
        "물성 자체가 온도인 행이다(`thermal.glass_transition` 등). 조건의 숫자는 시험온도가 "
        "아니라 값 자신(`detail: 'SCHOTT N-LASF9, Tg = 683 degC'`)이거나, 승온 상한"
        "(`heating 22 to 120 degC at 2 degC/min` 의 120)이거나, 승온율(`Td at 5 % weight loss, "
        "10 degC/min` 의 10)이거나, 등급명이다. 옮기면 `integrity_check` 의 "
        "「온도가 값인데 시험온도 조건」이 신규 위반을 낸다.",
        (5524, 5530, 5542, 5554, 5566, 5578, 5590, 5605, 5614,
         5724, 5772, 5773, 5790, 5792, 5793)),
    "구간의 끝": (
        "평균 선팽창계수의 **구간 끝**이다 — `alpha -30 to +70 degC` 의 70, "
        "`alpha +20 to +300 degC` 의 300, `mean CTE between 21 degC and 100 degC` 의 21, "
        "NdFeB `20-200 degC` 가 `-200 degC` 로 남은 것. 한 점의 시험온도가 아니라 구간이라 "
        "`temperature_range_c` 축으로 갈라 넣어야 하고 그것은 정정이 아니라 채굴이다.",
        (5651, 5652, 5603, 5604, 5612, 5613,
         5540, 5541, 5552, 5553, 5564, 5565, 5675, 5576, 5577, 5588, 5589)),
    "등급명 Tg": (
        "Isola IS400(`150 degC-Tg`)·370HR(`high-Tg (180 degC)`)의 **등급 이름**이다. "
        "시험온도가 아니다 — 같은 행의 `detail` 이 시험을 IPC-TM-650 2.6.2.1A 흡습·"
        "2.5.17.1 절연저항·2.4.24C TMA 로 밝히고, 그중 둘은 `296 K (as-received)` 라고 "
        "따로 적어 두었다. 옮기면 이 16+7칸이 180 °C·150 °C 측정으로 둔갑한다.",
        (5800, 5798, 5799, 5797, 5794, 5795, 5796,
         5789, 5779, 5780, 5781, 5782, 5783, 5784, 5785, 5786, 5787, 5788, 5778,
         5774, 5775, 5776, 5777)),
    "공정온도(증착·어닐·건조·스퍼터)": (
        "시편을 **만든** 온도지 잰 온도가 아니다. 그리고 여러 행이 잰 온도를 따로 적어 두었다 — "
        "AgNW `annealed 160 degC for 50 min; measured at room temperature (~298 K)` · "
        "RuO2 `dried 150 degC/15 min, fired 850 degC; two-probe resistance at 298 K` · "
        "NiCr `sputtered … at 25 degC; TCR from sheet resistance over 298-398 K` · "
        "ta-C `substrate equilibrium temperature 80 degC, nanoindentation` · "
        "AR 코팅 `e-beam evaporation in O2 at 573 K` · `ALD at 200 degC` · `annealed 550 degC/2 h`.",
        (5621, 5622, 5623, 5624, 5628, 5629, 5632, 5633, 5630, 5631,
         5640, 5641, 5766, 5767, 5638, 5639, 5636, 5637)),
    "온도 아닌 축이 같은 칸에 섞였다": (
        "`23 C / 50 %RH` 는 온도와 습도, `200 degC, held 30 min` 은 온도와 유지시간이다. "
        "온도만 떼어 옮기면 나머지 축이 보이는 키에서 사라진다. **갈라 넣는 것은 정정이 아니라 "
        "채굴이다**(`normalize_condition_keys.NOT_MERGED` 의 `thickness` 판단과 같은 자리). "
        "표적으로 남긴다 — `humidity_rh` · `dwell_min` 을 같이 세우는 배치가 닫아라.",
        (4992, 4993, 4994, 4995, 4996, 29661, 29662, 29669, 29670, 29677, 29678)),
}

# ── 맨 숫자 17행 — 단위를 옆 칸이 답한다 ──────────────────────────────────────
#
# `temperature_vocab.kelvin()` 은 맨 숫자에 `None` 을 돌린다(단위를 지어내지 않는다).
# 단위를 정하는 것은 이 표이고, 근거를 행마다 적는다.
BARE_K: dict[int, str] = {}
for _pid in (1138, 1140, 1141, 1142, 1143, 1146, 1147, 1148):
    # 같은 조건 dict 안에 `temperature_unit: "K"` 가 같이 있다 — 원문이 단위를 적어 둔 것이다.
    BARE_K[_pid] = "같은 조건의 `temperature_unit: \"K\"` 가 단위를 밝힌다"
for _pid in (1055, 1057, 1059, 1066, 1067, 1069, 1070, 1071, 1073):
    # 298.15 · 296.15 · 293.15 는 정확히 25 · 23 · 20 °C 다. `.15` 는 K↔°C 환산상수의 지문이고,
    # 셋 다 섭씨로 읽으면 물질이 성립하지 않는다(액체 전해액 밀도 1243 kg/m³ @ 293.15 °C 등).
    BARE_K[_pid] = ".15 단위 소수가 K↔°C 환산상수의 지문이다(298.15/296.15/293.15 = 25/23/20 °C)"

SKIP_IDS = {i for _, ids in SKIP.values() for i in ids}


def db_path() -> str:
    d = os.environ.get("MATERIALTWIN_DATA_DIR")
    if not d:
        sys.exit("MATERIALTWIN_DATA_DIR 를 지정해라(브리프 30·49).")
    return str(Path(d) / "materialtwin.db")


def targets(pvs):
    """`conditions.temperature` 를 가진 행을 갈래별로 나눈다."""
    out = defaultdict(list)
    for pv in pvs:
        c = pv.conditions or {}
        if not isinstance(c, dict) or "temperature" not in c:
            continue
        raw = c["temperature"]
        if pv.id in SKIP_IDS:
            out["skip_declared"].append(pv)
        elif pv.id in BARE_K:
            out["move"].append(pv)
        elif pv.property_key in TEMP_VALUED and kelvin(raw) is not None:
            out["skip_temp_valued_unknown"].append(pv)
        elif kelvin(raw) is not None:
            out["move" if "temperature_k" not in c else "skip_both_keys"].append(pv)
        elif printed(raw) is not None:
            out["defect_below_absolute_zero"].append(pv)
        elif normalize(raw) in (ROOM, NOT_REPORTED):
            out["fold"].append(pv)
        else:
            out["skip_unfoldable"].append(pv)
    return out


def new_conditions(pv) -> tuple[dict, str] | None:
    """(새 조건, 무엇을 했는지). 바꿀 것이 없으면 None."""
    cur = dict(pv.conditions or {})
    raw = cur["temperature"]
    if pv.id in BARE_K:
        cur.pop("temperature")
        cur["temperature_k"] = float(raw)
        return cur, (f"맨 숫자 {raw} 를 `temperature_k` 로 옮겼다 — {BARE_K[pv.id]}. "
                     f"수는 그대로다(환산 없음).")
    k = kelvin(raw)
    if k is not None:
        v, u = printed(raw)
        cur.pop("temperature")
        cur["temperature_k"] = k
        conv = "환산 없음" if u == "K" else (f"{v} °C + 273.15" if u == "C"
                                             else f"({v} °F − 32)/1.8 + 273.15")
        return cur, (f"인쇄값 {raw!r}(원값 {v} {u})을 `temperature_k` = {k} 로 옮겼다 — {conv}. "
                     f"단위 환산이라 값은 같은 양이다.")
    canon = normalize(raw)
    if canon in (ROOM, NOT_REPORTED):
        if cur["temperature"] == canon:
            return None
        cur["temperature"] = canon
        return cur, (f"온도 진술 {raw!r} 를 정규값 {canon!r} 로 접었다 — "
                     f"숫자를 만들지 않았고 원문은 `temperature_before_correction` 에 남는다.")
    return None


def blocked(pvs) -> dict[int, str]:
    """정정을 남길 수 없는 행(§548). **군 전체가 아니라 그 행만** 뺀다 —
    이 배치는 조건 칸 수를 안 바꾸므로 §548 의 '군 전체' 사유(칸 수가 행마다 달라진다)가 없다."""
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in pvs)
    out = {}
    for p in pvs:
        c = p.conditions or {}
        why = []
        if cnt[(p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)] > 1:
            why.append("같은 (출처,값) 행이 둘 이상 — 병합기가 운영행을 특정 못 한다")
        if any(x in c for x in PRIOR_MARKERS):
            why.append("옛 *_before_correction 표시가 있다")
        if why:
            out[p.id] = " · ".join(why)
    return out


def _rank_with(pv, cond):
    class _P:
        pass
    p = _P()
    p.property_key, p.conditions, p.quality_tier = pv.property_key, cond, pv.quality_tier
    p.value_num, p.id = pv.value_num, pv.id
    return _rep_rank(p)


def build(db):
    pvs = load(db, numeric_only=False)
    t = targets(pvs)
    bl = blocked(pvs)
    plan = []
    skipped_blocked = []
    for pv in t["move"] + t["fold"]:
        r = new_conditions(pv)
        if r is None:
            continue
        if pv.id in bl:
            skipped_blocked.append((pv, bl[pv.id]))
            continue
        plan.append((pv, r[0], r[1]))
    return pvs, t, plan, skipped_blocked


def report(db):
    pvs, t, plan, blocked_out = build(db)
    print(f"[DB] {db}\n전체 {len(pvs)}행 · `conditions.temperature` "
          f"{sum(len(v) for v in t.values())}행")
    print("\n-- 갈래 --")
    for k in ("move", "fold", "skip_declared", "skip_both_keys", "skip_unfoldable",
              "skip_temp_valued_unknown", "defect_below_absolute_zero"):
        print(f"  {len(t[k]):>6}  {k}")

    print("\n-- 옮기지 않는 사유별 행수(선언) --")
    live = {p.id for p in t["skip_declared"]}
    for name, (_why, ids) in SKIP.items():
        got = len(live & set(ids))
        mark = "" if got == len(ids) else f"  ← 선언 {len(ids)} 대 라이브 {got} (§610)"
        print(f"  {got:>6}  {name}{mark}")

    if t["skip_temp_valued_unknown"]:
        print("\n**선언에 없는 TEMP_VALUED 행이 나왔다 — 표를 갱신해라**")
        for p in t["skip_temp_valued_unknown"]:
            print(f"  pv{p.id} 재료{p.material_id} {p.property_key} "
                  f"{(p.conditions or {}).get('temperature')!r}")

    print(f"\n-- 두 키를 다 가진 행 {len(t['skip_both_keys'])} — 값이 맞는지 본다 --")
    clash = []
    for p in t["skip_both_keys"]:
        c = p.conditions
        k, tk = kelvin(c["temperature"]), c.get("temperature_k")
        ok = isinstance(tk, (int, float)) and abs(float(tk) - k) <= 0.01
        if not ok:
            clash.append((p, k, tk))
    print(f"   어긋난 행 {len(clash)}")
    for p, k, tk in clash:
        print(f"   pv{p.id} 재료{p.material_id} {p.property_key}: "
              f"{p.conditions['temperature']!r} = {k} K 인데 temperature_k = {tk}")

    print(f"\n-- 절대영도 이하(옮기지 않는다 · 신고) {len(t['defect_below_absolute_zero'])} --")
    for p in t["defect_below_absolute_zero"]:
        print(f"  pv{p.id} 재료{p.material_id} {p.property_key} "
              f"{p.conditions['temperature']!r} · detail="
              f"{str((p.conditions or {}).get('detail'))[:80]!r}")

    print(f"\n-- 접히지 않는 표기 {len(t['skip_unfoldable'])}행 --")
    for s, n in Counter(str((p.conditions or {})['temperature'])
                        for p in t["skip_unfoldable"]).most_common():
        print(f"  {n:>6}  {s[:90]}")

    print(f"\n-- 정정을 못 남겨 뺀 행 {len(blocked_out)} --")
    for s, n in Counter(w for _, w in blocked_out).most_common():
        print(f"  {n:>6}  {s}")

    print(f"\n-- 낼 정정 {len(plan)}건 --")
    act = Counter("이관" if "옮겼다" in a else "어휘 접기" for _, _c, a in plan)
    for a, n in act.most_common():
        print(f"  {n:>6}  {a}")

    # 대표값 전/후 — 이 배치가 바꿀 수 있는 유일한 자리는 `_temp_distance` 다.
    newc = {pv.id: c for pv, c, _ in plan}
    G = groups(pvs)
    changed = []
    nsets = 0
    for k, rows in G.items():
        if len(rows) < 2 or not any(p.id in newc for p in rows):
            continue
        nsets += 1
        b = sorted(rows, key=_rep_rank)[0]
        a = sorted(rows, key=lambda p: _rank_with(p, newc.get(p.id, p.conditions)))[0]
        if a.id != b.id:
            changed.append((k, b, a))
    print(f"\n-- 대표값 전/후 (내가 건드리는 행이 든 군 {nsets}) --  바뀐 군 {len(changed)}")
    for k, b, a in changed:
        bt = (b.conditions or {}).get("temperature")
        at = (a.conditions or {}).get("temperature")
        print(f"  재료{k[0]} {k[1]}: pv{b.id}({b.value_num}, {bt!r}) "
              f"→ pv{a.id}({a.value_num}, {at!r})")
    return plan


def gen(db, out_path):
    plan = report(db)
    corr = []
    for pv, cond, act in plan:
        prev = (pv.conditions or {}).get("correction_reason")
        who = (pv.conditions or {}).get("corrected_by") or "미상"
        keep = (f" 이 행에는 앞선 정정이 있었다 — 적재기가 사유를 덮어쓰므로 여기 옮겨 둔다: "
                f"[{who}] {str(prev)[:300]}") if prev else ""
        corr.append({
            "target": {"property_value_id": pv.id, "material_id": pv.material_id,
                       "property_key": pv.property_key},
            "by": BY,
            "reason": (f"[{BY}] 구식 문자열 키 `conditions.temperature` 정리 — "
                       f"값·단위·등급·method·출처는 한 칸도 안 고친다. {act}{keep}"),
            "set": {"conditions": cond},
        })
    doc = {"_comment": (
        f"{BY} — `conditions.temperature` 를 숫자(→`temperature_k`)와 진술(→정규 어휘)로 "
        "가른다. **값은 한 행도 안 고친다.** 옮기지 않은 사유와 그 근거는 "
        "`migrate_temperature_ya.py` 의 `SKIP` 표에 pv 번호까지 적혀 있다."),
        "_not_moved": {name: why for name, (why, _ids) in SKIP.items()},
        "corrections": corr}
    Path(out_path).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{out_path}: 정정 선언 {len(corr)}건")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    g = sub.add_parser("gen")
    g.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "plan":
        report(db_path())
    else:
        gen(db_path(), a.out)


if __name__ == "__main__":
    main()
