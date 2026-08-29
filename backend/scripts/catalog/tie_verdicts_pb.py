#!/usr/bin/env python3
# 이미 박힌 동률 판정이 **지금 분류기와 어긋난 군**을 찾아 다시 판정한다(54차 PB).
#
# 왜 있나 — 51차 MA·52차 NC 가 판정을 박은 뒤 분류기가 두 번 바뀌었다.
#   · 52차 NA 의 조건 어휘 통일(`axis`→`direction` · `temperature_C`→`temperature_c` …)이
#     "같은 축을 다른 이름으로 적었다"(키표기흔들림)를 실제로 **없앴다.**
#   · 53차 OB 가 둘을 고쳤다 — `basis: min/typical` 은 다른 항이 아니라 산포이고(`_is_pure_stat`),
#     한쪽에만 있는 축이 남아도 **다른 축이 양쪽에 닫혀 있으면 조건미기재가 아니다.**
# **그런데 이미 박힌 판정문은 안 고쳤다**(§522 — OB 가 재판정하지 않고 넘겼다).
# 결과로 값 옆에 *"이 축이 한쪽에만 적혀 있다"* 같은 **거짓 판정문**이 남아 있다(§505·556).
#
# 무엇을 하나 — 판정이 박힌 동률군 전수에서 `verdict_tie_axis` 의 부류와 **지금 `classify()`
# 가 내는 부류**를 대조해 어긋난 군만 다시 낸다. 값·등급·method·출처는 한 칸도 안 건드린다.
#
# 왜 새 파일인가 — 같은 파동의 PA 가 `ingest_agent_json.py` 와 병합기를 만진다.
# 경로 제한 커밋도 **같은 파일**을 공유하면 남의 수정을 같이 찍는다(§553).
# 52차 NC 가 `tie_verdicts_nc.py` 로 비킨 것과 같은 이유다.
#
# 사용:
#   MATERIALTWIN_DATA_DIR=<라이브> python3 tie_verdicts_pb.py scan
#   …                                        gen <out.json>
import json
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import tie_verdicts as tv                                            # noqa: E402

BY = os.environ.get("TIE_VERDICT_BY", "54차 PB")
tv.BY = BY


def stale():
    """[(재료,키), 1위행, 경쟁행, 박힌 부류, 지금 부류] — 부류가 어긋난 군만."""
    out = []
    for k, a, riv in tv.tie_groups(tv.db_path()):
        rows = [a] + riv
        axes = {(p.conditions or {}).get("verdict_tie_axis") for p in rows}
        axes = {x for x in axes if x}
        if not axes:
            continue
        now = tv.classify(a, riv)[0]
        for ax in sorted(axes):
            parts = str(ax).split(" — ")
            was = parts[1] if len(parts) > 1 else None
            if was != now:
                out.append((k, a, riv, was, now, parts[0]))
                break
    return out


def gen(out_path):
    DB = tv.db_path()
    G = tv.groups(tv.load(DB))
    _all = tv.load(DB, numeric_only=False)
    cnt = Counter((p.material_id, p.property_key, p.source_id, p.value_num, p.value_text)
                  for p in _all)
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    MAT = {r[0]: r[1] for r in con.execute("select id,name from material")}
    SRC = {r[0]: (r[1] or "") for r in con.execute("select id,title from source")}
    con.close()

    corr, skipped, done = [], [], []
    for k, a, riv, was, now, who in stale():
        blk = tv.blocked_rows(G, k, cnt)
        if blk:
            skipped.append({"material_id": k[0], "material_name": MAT.get(k[0]),
                            "property_key": k[1], "박힌 부류": was, "지금 부류": now,
                            "막은 행": blk})
            continue
        c, labs, diff = tv.classify(a, riv)
        f = tv.facets(a, riv)
        axis_keys = sorted(set(f["axis"]) | set(f["term"]) | set(f["spread"])
                           | set(f["replicate"]) | set(f["free"])) or diff
        tied = {a.id} | {b.id for b in riv}
        rows = sorted(G[k], key=tv._rep_rank)
        axis_txt = f"{c} — {'·'.join(labs)[:120]}" if labs else c
        for pv in rows:
            others = [o for o in rows if o.id != pv.id and o.id in tied]
            rival = " · ".join(f"{tv.fmt(o)} [{tv.axis_bits(o, axis_keys, 3)}]" for o in others[:4])
            if len(others) > 4:
                rival += f" · 외 {len(others)-4}건"
            pos = ("이 행이 대표로 뽑혀 있다" if pv.id == rows[0].id
                   else "이 행은 대표와 순위가 같다(적재 순서로 밀렸다)" if pv.id in tied
                   else "이 행은 순위에서 뒤에 있다(동률이 아니다)")
            note = (f"[{BY} 동률 재판정] {tv.HEAD[c]} {pos}. "
                    f"이 행 = {tv.fmt(pv)} [{tv.axis_bits(pv, axis_keys)}]. "
                    f"동률 경쟁행 = {rival or '(없다)'}. "
                    f"갈린 조건키 = {', '.join(diff[:12]) or '(없다 — 조건이 같다)'}.")
            if c == "의견차":
                note += f" 이 행의 출처 = {SRC.get(pv.source_id,'(없다)')[:90]}."
            corr.append({
                "target": {"property_value_id": pv.id,
                           "material_id": pv.material_id,
                           "material_name": MAT.get(pv.material_id),
                           "property_key": pv.property_key},
                "by": BY,
                "reason": tv._reason_with_prior(pv, (
                    f"대표값 동률 **재판정** — {who} 의 판정이 지금 분류기와 어긋나 다시 낸다"
                    f"(`{was}` → `{c}`). 값·등급·method·출처는 한 칸도 안 바꾼다(브리프 545·556). "
                    f"부류 {axis_txt}.")),
                "set": {"conditions": dict(pv.conditions or {},
                                           verdict_tie_axis=f"{BY} — {axis_txt}",
                                           verdict_tie_note=note)},
            })
        done.append({"material_id": k[0], "material_name": MAT.get(k[0]), "property_key": k[1],
                     "박힌 부류": was, "지금 부류": now, "박은 배치": who, "행": len(rows)})
    doc = {"_skipped": skipped, "_redone": done, "_comment": (
        f"{BY} — **이미 박힌 동률 판정의 재판정**이다. 값·등급·method·출처를 하나도 바꾸지 않고 "
        "`conditions.verdict_tie_axis`·`verdict_tie_note` 두 칸의 **내용만** 갱신한다(칸 수는 그대로라 "
        "`_rep_rank` 의 조건 수 자리가 안 흔들린다). 어긋난 이유는 둘이다 — 52차 NA 의 조건 어휘 "
        "통일이 `키표기흔들림` 을 실제로 없앴고, 53차 OB 가 `basis` 통계낱말과 `조건미기재` 판정을 "
        "고쳤는데 **이미 박힌 판정문은 안 고쳤다**(§522)."),
        "corrections": corr}
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print(f"{out_path}: 어긋난 군 {len(done)+len(skipped)} → 재판정 {len(done)}군 "
          f"· 정정 선언 {len(corr)}건 · 전파 불가로 뺀 군 {len(skipped)}")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__ or "scan | gen <out.json>")
    if sys.argv[1] == "scan":
        st = stale()
        print(f"[DB] {tv.db_path()}")
        print(f"판정이 지금 분류기와 어긋난 동률군: {len(st)}")
        for k, a, riv, was, now, who in st:
            print(f"  재료{k[0]:>5} {k[1]:<38} {was} -> {now}   [{who}]")
    elif sys.argv[1] == "gen":
        gen(sys.argv[2])
    else:
        sys.exit("scan | gen <out.json>")


if __name__ == "__main__":
    main()
