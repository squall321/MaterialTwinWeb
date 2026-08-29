#!/usr/bin/env python3
# 정정이 **운영까지 갈 수 있는 행인가**를 병합기와 같은 자로 재고, 그 자로 조건 어휘 통일의
# 잔여분을 낸다. **값·등급·method·출처는 한 칸도 안 고친다** — 조건 키 이름과 `direction` 뿐이다.
#
# 왜 새 파일인가(§553). 같은 파동에 다른 배치가 돈다. `normalize_condition_keys.py` 와
# `tie_verdicts.py` 는 한 줄도 안 고치고 **읽기만** 한다.
#
# 왜 있나(54차 PA). 52차 NA 가 조건 어휘를 통일하다 **691군 5,265행을 못 했다.**
# 막은 것은 데이터가 아니라 **경로**였다(§581) — 병합기의 정정 탐색축
# `(재료·물성키·출처·옛 값)` 이 라이브에서 유일하지 않아서다(4,265행 1,832군, §548·564).
#
# 53차 OA 가 출처 이동 분기(⑤)에서 같은 문제를 **조건을 파싱해 사전으로 대조**해 풀었다(§579).
# 그 방식을 정정 분기(③)에 줬다. 여기서는 한 걸음 더 든다 — 정정이 바꾼 칸이 조건 그 자체라
# **정정 전 조건을 표시로 되돌려** 대조한다(`_materialtwin_merge.prior_conditions`).
#
# 이 파일의 `reachable()` 은 그 병합기 분기의 **거울**이다. 둘이 어긋나면 예행에서
# `correction_misses` 로 즉시 드러난다 — 그래서 예행이 이 파일의 시험이다.
#
# 막는 것이 어느 쪽인가(직접 쟀다) ─────────────────────────────────────────────
#   · **적재기는 안 막는다.** 생성하는 선언이 `property_value_id` 로 대상을 못박으므로
#     `match_targets` 는 언제나 1건이다. 라이브 실측 — 대상 4,455행 전부 유일.
#   · **막는 것은 병합기다.** 그래서 고친 곳도 거기 하나다.
#
# 여전히 막히는 것 ────────────────────────────────────────────────────────────
#   옛 `*_before_correction` **컬럼 표시**(§451·455 중앙값 가드)를 단 행이다. 병합기가 그것을
#   컬럼의 옛 값으로 읽어 `where method=<가드 이전 값>` 으로 찾는데 0건이 된다. 조건 대조로는
#   못 푼다 — 좁히는 축 자체가 틀리기 때문이다. 라이브 71군 276행.
#
# 사용:
#   MATERIALTWIN_DATA_DIR=<라이브> python3 correction_reach.py plan
#   … gen <out.json>   `corrections` 선언 생성
import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize_condition_keys as N  # noqa: E402
from tie_verdicts import PRIOR_MARKERS, groups  # noqa: E402

BY = os.environ.get("REACH_BY", "54차 PA")
SUFFIX = "_before_correction"
HOUSEKEEPING = ("correction_reason", "corrected_by", "correction_evidence")


def condition_core(d):
    """조건 dict → 대조용 사전. **살림살이 키와 `null` 칸을 벗긴다.**

    병합기 `_condition_core` 와 같은 모양이어야 한다. `null` 을 벗기는 이유는 적재기가
    "칸이 없다" 와 "칸이 null 이다" 를 같은 표시로 남기기 때문이다(§558 ②) —
    가를 수 없는 것은 합쳐서 대조해야 틀린 행을 고르는 대신 거부된다.
    """
    if not isinstance(d, dict):
        return {}
    return {k: v for k, v in d.items()
            if v is not None and not (k.endswith(SUFFIX) or k in HOUSEKEEPING)}


class Index:
    """(재료·물성키·출처·값) 으로 라이브 행을 모아 둔 것 — 병합기의 탐색축 그대로다."""

    def __init__(self, pvs):
        self.by_axis = defaultdict(list)
        for p in pvs:
            self.by_axis[(p.material_id, p.property_key, p.source_id,
                          p.value_num, p.value_text)].append(p)

    def candidates(self, p):
        return self.by_axis[(p.material_id, p.property_key, p.source_id,
                             p.value_num, p.value_text)]


def reachable(p, index):
    """병합기가 이 행의 운영 대응행을 **유일하게** 찾을 수 있는가. (bool, 사유)."""
    c = p.conditions or {}
    hit = [x for x in PRIOR_MARKERS if x in c]
    if hit:
        # 컬럼의 옛 값을 잘못 복원한다 — 좁히는 축이 틀려서 조건 대조로도 못 푼다.
        return False, f"옛 컬럼 표시 `{hit[0]}` 가 탐색축을 틀리게 만든다"
    rows = index.candidates(p)
    if len(rows) == 1:
        return True, ""
    mine = condition_core(p.conditions)
    hits = [q for q in rows if condition_core(q.conditions) == mine]
    if len(hits) == 1:
        return True, ""
    return False, f"(출처,값)이 같은 {len(rows)}행이고 조건까지 봐도 {len(hits)}행이 같다"


def survey(db):
    """(pvs, plan, 막힌 군 dict, index) — 군 단위로 막힘을 판정한다.

    **군 전체를 뺀다**(51차 MA·52차 NA 와 같다, §548). 막힌 행 하나만 빼면 그 행만 조건
    칸이 안 늘어 `_rep_rank` 의 조건 수 자리에서 대표값이 조용히 뒤집힐 수 있다.
    """
    pvs, plan, skips = N.build(db)
    G = groups(pvs)
    index = Index(pvs)
    blocked = {}
    for k in {(pv.material_id, pv.property_key) for pv, _, _ in plan}:
        bad = []
        for p in G[k]:
            ok, why = reachable(p, index)
            if not ok:
                bad.append((p.id, why))
        if bad:
            blocked[k] = bad
    return pvs, plan, G, blocked, skips


def _old_blocked(pvs, plan, G):
    """52차 NA 가 쓰던 판정(조건 대조 없음) — 인계 수치를 직접 재기 위해서다(§479·505)."""
    from tie_verdicts import blocked_rows
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in pvs)
    out = {}
    for k in {(pv.material_id, pv.property_key) for pv, _, _ in plan}:
        b = blocked_rows(G, k, cnt)
        if b:
            out[k] = b
    return out


def plan_report(db, verbose=False):
    pvs, plan, G, blocked, skips = survey(db)
    old = _old_blocked(pvs, plan, G)
    print(f"[DB] {db}\n전체 행 {len(pvs)} · 통일 대상 행 {len(plan)}")

    act = Counter()
    for _, _, acts in plan:
        for a in acts:
            act[a.split(" ")[0] if a.startswith("direction 정규화") else a] += 1
    print("\n-- 한 일별 행수 --")
    for a, n in act.most_common(80):
        print(f"  {n:>6}  {a}")
    if skips:
        print("\n-- 건너뛴 행(대상 칸에 이미 값이 있다) --")
        for s, n in skips.most_common():
            print(f"  {n:>6}  {s}")

    no = sum(len(G[k]) for k in old)
    nn = sum(len(G[k]) for k in blocked)
    print(f"\n-- 막힘 --")
    print(f"  조건 대조 넣기 전 : {len(old):>4}군 {no:>6}행   ← 52차 NA 가 포기한 수")
    print(f"  조건 대조 넣은 뒤 : {len(blocked):>4}군 {nn:>6}행")
    print(f"  열린 것           : {len(old) - len(blocked):>4}군 {no - nn:>6}행")
    wc = Counter(w for v in blocked.values() for _, w in v)
    print("\n-- 여전히 막힌 사유 --")
    for w, n in wc.most_common(10):
        print(f"  {n:>6}행  {w}")

    # 대표값 전/후 전수 대조 — 이 파동이 세 번 밟은 자리다(§548·558·580).
    newc = {pv.id: cur for pv, cur, _ in plan}
    drop = {p.id for k in blocked for p in G[k]}
    cand = flip_row = flip_val = 0
    changed = []
    for k, rows in G.items():
        if len(rows) < 2:
            continue
        b = sorted(rows, key=N._rep_rank)[0]
        a = sorted(rows, key=lambda p: N._rank_key(
            p, newc[p.id] if (p.id in newc and p.id not in drop) else p.conditions))[0]
        cand += 1
        if a.id != b.id:
            flip_row += 1
            if a.value_num != b.value_num or (a.value_text or "") != (b.value_text or ""):
                flip_val += 1
            changed.append((k, b, a))
    print(f"\n-- 대표값 전/후 (후보 둘 이상 {cand}군) --  대표 행 변동 {flip_row}군 · "
          f"대표 값 변동 {flip_val}군")
    for k, b, a in changed[:40]:
        print(f"  재료{k[0]} {k[1]}: pv{b.id}({b.value_num}) → pv{a.id}({a.value_num})")
    return plan, drop, blocked


def gen(db, out_path):
    plan, drop, blocked = plan_report(db)
    corr = []
    for pv, cur, acts in plan:
        if pv.id in drop:
            continue
        # 적재기는 `correction_reason`·`corrected_by` 를 **덮어쓴다**(§573).
        # 이미 정정된 행이면 앞 사유를 **새 사유 문장 안에 쌓는다** — 조건 칸을 새로 만들지
        # 않는다(칸이 행마다 달라지면 §548 의 "군 전체에 같은 수" 를 못 지킨다).
        c = pv.conditions or {}
        prev, who = c.get("correction_reason"), c.get("corrected_by")
        keep = (f" 이 행에는 앞선 정정이 있었다 — 적재기가 사유를 덮어쓰므로 여기 옮겨 둔다: "
                f"[{who or '미상'}] {str(prev)[:400]}") if prev else ""
        corr.append({
            "target": {"property_value_id": pv.id, "material_id": pv.material_id,
                       "property_key": pv.property_key},
            "by": BY,
            "reason": ("조건 어휘 통일 잔여(브리프 547·551·581) — 값·단위·등급·method·출처는 "
                       "그대로다. " + " · ".join(acts) + "." + keep),
            "set": {"conditions": cur},
        })
    doc = {"_comment": (
        "54차 PA — 52차 NA 가 전파 불가로 남긴 조건 어휘 통일의 잔여분이다. "
        "**값은 한 행도 안 고친다.** 정본 선정 근거와 합치지 않은 쌍은 "
        "`normalize_condition_keys.py` 머리말에 그대로 있고 이 배치가 다시 정하지 않았다. "
        "막혀 있던 이유와 무엇을 고쳐 열었는지는 `correction_reach.py` 머리말에 있다."),
        "_still_blocked": {
            "군": len(blocked), "그 군의 행": len(drop),
            "직접 막힌 행": sum(len(v) for v in blocked.values()),
            "사유": "옛 `*_before_correction` 컬럼 표시(§451·455 중앙값 가드)가 병합기의 "
                    "탐색축을 틀리게 만든다 — 조건 대조로는 못 푼다. 막힌 행만 빼면 그 행만 "
                    "조건 칸이 안 늘어 대표값이 뒤집힐 수 있어 **군 전체를 뺀다**(§548)"},
        "corrections": corr}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"\n{out_path}: 정정 선언 {len(corr)}건 (전파 불가로 뺀 행 {len(drop)})")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    g = sub.add_parser("gen")
    g.add_argument("out")
    a = ap.parse_args()
    if a.cmd == "plan":
        plan_report(N.db_path())
    else:
        gen(N.db_path(), a.out)


if __name__ == "__main__":
    main()
