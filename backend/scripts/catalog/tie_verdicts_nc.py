#!/usr/bin/env python3
# 51차 MA 가 카드 8키에 박은 동률 판정을 **카드 밖 키로 넓힌다**(52차 NC).
#
# MA 의 도구(`tie_verdicts.py`)가 세는 것·분류하는 것·전파 못 하는 군을 거르는 것을 그대로 쓴다.
# 이 파일이 더하는 것은 셋뿐이다.
#   ① **이미 판정이 박힌 군을 뺀다** — MA 의 486군에 두 번째 정정을 얹으면 `correction_reason`
#      이 덮이고 병합기의 `*_before_correction` 복원이 어긋난다(브리프 522).
#   ② **표적을 도메인·격차로 고른다** — MA 는 카드 8키뿐이었다. 전기·광학·열이 다음이다.
#   ③ **"한 재료에 여러 제품" 지문을 센다**(브리프 123·435). **가르지는 않는다** —
#      자동 분리는 금지돼 있고, 이 목록은 사람이 볼 표적일 뿐이다.
#
# 왜 새 파일인가 — 같은 파동의 NA·NB 가 같은 작업트리에서 돈다. 경로 제한 커밋도 **같은 파일**을
# 공유하면 남의 수정을 같이 찍는다(브리프 553). MB 가 `catalog_alternatives.py` 로 비킨 것과 같다.
#
# 사용:
#   MATERIALTWIN_DATA_DIR=<라이브> python3 tie_verdicts_nc.py plan
#   … targets                                  제품 갈림 지문 표적 목록
#   … gen <out.json> [--domains electrical,optical,thermal] [--min-gap 0.10]
import argparse
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import tie_verdicts as tv                                            # noqa: E402
from app.catalog_compare import _temp_distance                        # noqa: E402

BY = os.environ.get("TIE_VERDICT_BY", "52차 NC")
tv.BY = BY

# 제품·등급을 **조건에 적어 둔** 키. 여기서 갈렸다면 그 군은 이미 제대로 갈려 있다 —
# 갈라야 할 표적이 아니라 **이미 처리된 것**이다(브리프 123 이 시킨 그대로다).
PRODUCT_KEYS = {"grade", "brand", "product", "product_form", "formulation", "foil_grade",
                "alloy", "grade_scope", "series"}
# 조건축이 하나도 설명 못 한 갈림. 여기서 출처가 둘 이상이면 §123 의 지문이다.
UNEXPLAINED = {"의견차", "서술차이", "같은출처중복"}


def judged(rows) -> bool:
    return any("verdict_tie_axis" in (p.conditions or {}) for p in rows)


def candidates(min_gap=0.10, domains=None, keys=None, extra=()):
    """판정을 아직 안 단 동률군. `extra` 는 격차 문턱을 넘기고 싶은 (재료,키) 집합이다."""
    out = []
    for k, a, riv in tv.tie_groups(tv.db_path()):
        if judged([a] + riv):
            continue
        if domains and k[1].split(".")[0] not in domains:
            continue
        if keys and k[1] not in keys:
            continue
        if tv.gap(a, riv) <= min_gap and k not in extra:
            continue
        out.append((k, a, riv))
    return out


def optical_temp_groups():
    """`_rep_rank` 가 `optical.*` 에서 파장만 보는 탓에 **온도가 갈렸는데 동률**인 군.

    51차 MA 가 15군을 셌다고 인계했다 — 직접 세서 확인한다(브리프 479·505).
    """
    out = []
    for k, a, riv in tv.tie_groups(tv.db_path()):
        if not k[1].startswith("optical."):
            continue
        if len({_temp_distance(p.conditions) for p in [a] + riv}) > 1:
            out.append((k, a, riv))
    return out


# ── "한 재료에 여러 제품" 지문(브리프 123 의 실증) ────────────────────────────────
# 재료 119 EMI Shield 하나에 전도성 잉크·그래핀·CNF/PTFE 가 들어 있어 값이 100% 갈린다.
# **지문은 셋으로 갈라 센다** — 뒤로 갈수록 약하다. 자동으로 가르지 않는다(브리프 435).
def product_fingerprint(k, a, riv, SRC):
    cls = tv.classify(a, riv)[0]
    diff_keys = set(tv.facets(a, riv)["all"])
    if diff_keys & PRODUCT_KEYS:
        return "조건에 이미 갈려 있다", cls          # 표적이 아니다
    srcs = {p.source_id for p in [a] + riv}
    titles = {(SRC.get(p.source_id) or "").strip() for p in [a] + riv}
    if cls in UNEXPLAINED and len(titles) > 1:
        return "출처가 다른 문서다", cls              # 강한 지문
    if cls == "서술차이" and len(titles) == 1:
        return "한 문서 안에서 서술만 다르다", cls     # 약한 지문(제품 목록표일 수 있다)
    if cls in UNEXPLAINED and len(srcs) == 1:
        return "같은 출처인데 조건이 같다", cls        # 지문 아님 — 진짜 의견차/중복
    return None, cls


def targets():
    DB = tv.db_path()
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    MAT = {r[0]: r[1] for r in con.execute("select id,name from material")}
    SRC = {r[0]: (r[1] or "") for r in con.execute("select id,title from source")}
    tally = Counter()
    hits = defaultdict(list)
    for k, a, riv in tv.tie_groups(DB):
        tag, cls = product_fingerprint(k, a, riv, SRC)
        if tag is None:
            continue
        tally[tag] += 1
        if tag in ("출처가 다른 문서다", "한 문서 안에서 서술만 다르다"):
            hits[k[0]].append((k[1], cls, tv.gap(a, riv),
                               [(p.value_num, p.unit, (SRC.get(p.source_id) or "")[:64])
                                for p in [a] + riv[:4]]))
    print(f"[DB] {DB}\n동률군 전수에서 본 §123 지문")
    for t, c in tally.most_common():
        print(f"  {t:<26}{c:>6}")
    print(f"\n갈라야 할 표적 후보 — 재료 {len(hits)}종 · 군 "
          f"{sum(len(v) for v in hits.values())}")
    for mid in sorted(hits, key=lambda m: -len(hits[m])):
        print(f"\n· 재료{mid} {MAT.get(mid,'')[:60]} — {len(hits[mid])}군")
        for key, cls, g, rows in hits[mid][:6]:
            print(f"    {key} [{cls}] 격차 {g*100:.0f}%")
            for v, u, t in rows:
                print(f"      {v:<12.6g} {u or '':<10} {t}")


def plan():
    DB = tv.db_path()
    ties = tv.tie_groups(DB)
    G = tv.groups(tv.load(DB))
    _all = tv.load(DB, numeric_only=False)
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in _all)
    done = sum(1 for k, a, r in ties if judged([a] + r))
    print(f"[DB] {DB}\n동률군 {len(ties)} · 이미 판정 {done} · 미판정 {len(ties)-done}")
    dom = defaultdict(Counter)
    for k, a, riv in ties:
        if judged([a] + riv):
            dom[k[1].split('.')[0]]["판정끝"] += 1
            continue
        d = dom[k[1].split('.')[0]]
        d["미판정"] += 1
        if tv.gap(a, riv) > 0.10:
            d["10%초과"] += 1
            d["전파불가" if tv.blocked_rows(G, k, cnt) else "판정가능"] += 1
            d["행"] += len(G[k])
    print(f"\n{'도메인':<13}{'판정끝':>7}{'미판정':>7}{'10%초과':>8}{'판정가능':>8}"
          f"{'전파불가':>8}{'행':>7}")
    tot = Counter()
    for d in sorted(dom, key=lambda x: -dom[x]["10%초과"]):
        c = dom[d]
        tot.update(c)
        print(f"{d:<13}{c['판정끝']:>7}{c['미판정']:>7}{c['10%초과']:>8}"
              f"{c['판정가능']:>8}{c['전파불가']:>8}{c['행']:>7}")
    print(f"{'합':<13}{tot['판정끝']:>7}{tot['미판정']:>7}{tot['10%초과']:>8}"
          f"{tot['판정가능']:>8}{tot['전파불가']:>8}{tot['행']:>7}")


def gen(out_path, min_gap, domains, keys, with_optical_temp):
    DB = tv.db_path()
    G = tv.groups(tv.load(DB))
    _all = tv.load(DB, numeric_only=False)
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in _all)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    MAT = {r[0]: r[1] for r in con.execute("select id,name from material")}
    SRC = {r[0]: (r[1] or "") for r in con.execute("select id,title from source")}

    extra = set()
    if with_optical_temp:
        # 광학 순위가 온도를 안 보는 탓에 생긴 동률은 **격차와 무관하게** 판정한다.
        # 값 차이는 작아도(2~3%) 20 °C 용액과 77 K 유리는 다른 물리다.
        extra = {k for k, a, riv in optical_temp_groups()}
    sel = candidates(min_gap, domains, keys, extra)
    corr, skipped = [], []
    seen_class = Counter()
    for k, a, riv in sel:
        blk = tv.blocked_rows(G, k, cnt)
        if blk:
            skipped.append({"material_id": k[0], "material_name": MAT.get(k[0]),
                            "property_key": k[1], "부류": tv.classify(a, riv)[0],
                            "막은 행": blk})
            continue
        c, labs, diff = tv.classify(a, riv)
        seen_class[c] += 1
        f = tv.facets(a, riv)
        axis_keys = sorted(set(f["axis"]) | set(f["term"]) | set(f["spread"])
                           | set(f["replicate"]) | set(f["free"])) or diff
        tied = {a.id} | {b.id for b in riv}
        rows = sorted(G[k], key=tv._rep_rank)
        axis_txt = f"{c} — {'·'.join(labs)[:120]}" if labs else c
        for pv in rows:
            others = [o for o in rows if o.id != pv.id and o.id in tied]
            rival = " · ".join(f"{tv.fmt(o)} [{tv.axis_bits(o, axis_keys, 3)}]"
                               for o in others[:4])
            if len(others) > 4:
                rival += f" · 외 {len(others)-4}건"
            pos = ("이 행이 대표로 뽑혀 있다" if pv.id == rows[0].id
                   else "이 행은 대표와 순위가 같다(적재 순서로 밀렸다)" if pv.id in tied
                   else "이 행은 순위에서 뒤에 있다(동률이 아니다)")
            note = (f"[{BY} 동률 판정] {tv.HEAD[c]} {pos}. "
                    f"이 행 = {tv.fmt(pv)} [{tv.axis_bits(pv, axis_keys)}]. "
                    f"동률 경쟁행 = {rival or '(없다)'}. "
                    f"갈린 조건키 = {', '.join(diff[:12]) or '(없다 — 조건이 같다)'}.")
            if c in UNEXPLAINED:
                note += f" 이 행의 출처 = {SRC.get(pv.source_id,'(없다)')[:90]}."
            if k[1].startswith("optical.") and k in extra:
                note += (" 이 군은 **광학 순위가 온도를 안 봐서** 동률이 됐다 — "
                         "`_rep_rank` 가 `optical.*` 에서 파장만 본다. 순위는 안 고쳤다"
                         "(브리프 543·544).")
            corr.append({
                "target": {"property_value_id": pv.id,
                           "material_id": pv.material_id,
                           "material_name": MAT.get(pv.material_id),
                           "property_key": pv.property_key},
                "by": BY,
                "reason": (f"대표값 동률 판정 — 값·등급·method·출처를 하나도 바꾸지 않고 "
                           f"**왜 갈렸는지**만 조건에 적는다(브리프 545). 부류 {axis_txt}."),
                "set": {"conditions": dict(pv.conditions or {},
                                           verdict_tie_axis=f"{BY} — {axis_txt}",
                                           verdict_tie_note=note)},
            })
    doc = {"_skipped": skipped, "_comment": (
        f"{BY} — 51차 MA 가 카드 8키에 박은 동률 판정을 카드 밖 키로 넓힌 것이다. "
        "값·등급·method·출처를 하나도 바꾸지 않고 `conditions` 에 두 칸만 더한다. "
        "한 (재료,키) 군의 **모든 행**에 같은 수의 칸을 더해 `_rep_rank` 의 `len(conditions)` "
        "자리가 군 안의 순서를 바꾸지 않게 했다. "
        "`_skipped` 는 판정을 남기지 못한 군이다 — 운영 전파가 불가능해 중복을 만든다"
        "(브리프 548). 같은 파동 NB 가 그 중복을 정리하면 열린다."),
        "corrections": corr}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"{out_path}: 후보 {len(sel)}군 → 판정 {len(sel)-len(skipped)}군 "
          f"· 선언 {len(corr)}행 · 전파 불가로 뺀 군 {len(skipped)}")
    print("  부류별 — " + " · ".join(f"{c} {n}" for c, n in seen_class.most_common()))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    sub.add_parser("targets")
    g = sub.add_parser("gen")
    g.add_argument("out")
    g.add_argument("--min-gap", type=float, default=0.10)
    g.add_argument("--domains", default="")
    g.add_argument("--keys", default="")
    g.add_argument("--optical-temp", action="store_true",
                   help="광학 순위가 온도를 안 봐 생긴 동률군은 격차와 무관하게 넣는다")
    a = ap.parse_args()
    if a.cmd == "plan":
        plan()
    elif a.cmd == "targets":
        targets()
    else:
        gen(a.out, a.min_gap,
            set(x for x in a.domains.split(",") if x),
            set(x for x in a.keys.split(",") if x),
            a.optical_temp)


if __name__ == "__main__":
    main()
