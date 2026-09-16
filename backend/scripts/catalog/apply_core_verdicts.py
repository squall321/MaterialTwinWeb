#!/usr/bin/env python3
# 배치가 낸 코어 빈칸 판정(해당없음·문서 부재·인쇄값 기각)을 material.attributes 에 병합한다.
#
# 왜 따로 있나 — `ingest_agent_json.py` 는 **신규 재료를 만들 때만** attributes 를 쓴다.
# 기존 재료의 판정은 넣을 길이 없어 배치마다 일회용 스크립트를 써 왔다(브리프 593:
# 판정이 집계가 읽는 자리에 없으면 다음 파동이 같은 칸을 또 표적으로 센다).
#
# 사용:  apply_core_verdicts.py <json...> [--apply]
#
# 입력 JSON — {"batch": "...", "verdicts": [{"material_id": 1, "name": "...",
#              "<attr>": {"<물성키>": "<사유>"} | null | "<문자열>"} ...]}
#   · dict 이면 기존 dict 와 **키 단위로 병합**한다. 같은 키는 새 사유로 바꾸되 앞 사유문을
#     새 사유 뒤에 머리를 달아 남긴다(`merge_reasons`).
#   · null 이면 그 attribute 를 **내린다**(재료 단위 문자열 판정을 정정할 때).
#   · 덮거나 내리기 전의 값은 `<attr>_before_correction` 에 남긴다(브리프 594).
#     이미 기록이 있으면 덮지 않고 쌓는다(`keep_before`).
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from collections import Counter

# 경로를 박아 두면 **사본 리허설이 조용히 무력화된다.** 배치들은 `VACUUM INTO` 로 사본을
# 뜨고 거기 먼저 `--apply` 해 diff 를 본 뒤 라이브에 넣으라고 배웠는데(§647), 이 도구만
# 환경변수를 무시해 그 리허설이 라이브에 쓰였다(65차 AD 실측 — 판정이 리허설 중 들어갔다).
# 형제 도구(integrity_check·coverage_report)와 같은 관례로 맞춘다. 기본값은 그대로라
# 기존 호출은 안 변하고, `--db` 로 사본을 직접 지목할 수도 있다.
DEFAULT_DB = os.path.join(
    os.environ.get("MATERIALTWIN_DATA_DIR",
                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
    "materialtwin.db")

SKIP = {"material_id", "name"}

# 같은 키를 새 사유로 바꿀 때, 남겨 두는 앞 사유문 앞에 다는 머리.
PRESERVED_HEAD = "**[앞 판정문 — {batch} 가 이 칸을 새 사유로 바꾸며 지우지 않고 남긴다]**"


def merge_reasons(old, new: dict, batch: str) -> dict:
    """판정 dict 를 키 단위로 병합한다. **같은 키의 앞 사유문을 지우지 않는다.**

    예전엔 같은 키를 새 사유로 그냥 덮었다. 앞 사유는 `<attr>_before_correction` 에
    **처음 한 번만** 남으므로, 그 칸이 두 번째로 바뀌는 순간부터 앞 사유가 흔적 없이
    사라졌다. 76차 스냅샷 대조 실측 — 74차 적용에서 10칸(71차 GC 의 근거문),
    75차 적용에서 22칸(74차 JA 의 근거문 등)이 그렇게 지워졌다.
    """
    merged = dict(old) if isinstance(old, dict) else {}
    for k, n in new.items():
        o = merged.get(k)
        if o in (None, "") or o == n:
            merged[k] = n
            continue
        o_s = o if isinstance(o, str) else json.dumps(o, ensure_ascii=False)
        n_s = n if isinstance(n, str) else json.dumps(n, ensure_ascii=False)
        if o_s in n_s:                 # 새 사유가 앞 사유를 이미 품고 있다
            merged[k] = n
        elif n_s in o_s:               # 같은 파일을 다시 돌렸다 — 이미 들어가 있다
            continue
        else:
            merged[k] = f"{n_s}\n\n{PRESERVED_HEAD.format(batch=batch)}\n{o_s}"
    return merged


def keep_before(attrs: dict, attr: str, old) -> None:
    """`<attr>_before_correction` 에 old 를 남긴다. **이미 있는 기록은 덮지 않고 쌓는다.**

    판정을 내리는 갈래는 이 칸을 무조건 덮어 앞선 정정 기록을 지웠고, 문자열 판정 갈래는
    처음 한 번만 남겨 두 번째 정정부터 중간 값을 잃었다.
    """
    k = f"{attr}_before_correction"
    if k not in attrs:
        attrs[k] = old
        return
    prev = attrs[k]
    hist = prev if isinstance(prev, list) else [prev]
    if old not in hist:
        attrs[k] = hist + [old]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB,
                    help="쓸 DB. 기본은 MATERIALTWIN_DATA_DIR/materialtwin.db")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(a.db)
    have = {i: (n, at) for i, n, at in c.execute("select id,name,attributes from material")}
    print(f"[DB] {a.db}\n     재료 {len(have)}종")

    rows: list[tuple[str, dict]] = []
    for p in a.paths:
        doc = json.load(open(p))
        batch = doc.get("batch") or os.path.basename(p)
        rows += [(batch, r) for r in doc.get("verdicts", [])]
    print(f"     판정 입력 {len(rows)}종")

    st = Counter()
    for batch, r in rows:
        mid = r.get("material_id")
        if mid not in have:
            st["없는 재료"] += 1
            print(f"  ✗ 없는 material_id {mid} — {str(r.get('name'))[:60]}")
            continue
        name, raw = have[mid]
        attrs = json.loads(raw or "{}")
        if not isinstance(attrs, dict):
            st["attributes 가 dict 가 아님"] += 1
            continue
        changed = []
        for attr, new in r.items():
            if attr in SKIP:
                continue
            old = attrs.get(attr)
            if new is None:                                  # 판정을 내린다
                if attr not in attrs:
                    continue
                attrs.pop(attr)
                keep_before(attrs, attr, old)
                changed.append(f"-{attr}")
                st["내림"] += 1
                continue
            if isinstance(new, dict):
                merged = merge_reasons(old, new, batch)
                if merged == old:
                    continue
                if old is not None and not isinstance(old, dict):
                    keep_before(attrs, attr, old)               # 문자열 판정 → dict 로 승격
                elif f"{attr}_before_correction" not in attrs:
                    attrs[f"{attr}_before_correction"] = old    # null = 정정 전에 없었다(브리프 558②)
                attrs[attr] = merged
                changed.append(f"{attr}[{len(merged)}]")
                st["병합"] += 1
            else:
                if old == new:
                    continue
                keep_before(attrs, attr, old)
                attrs[attr] = new
                changed.append(attr)
                st["설정"] += 1
        if not changed:
            st["변화 없음"] += 1
            continue
        st["재료"] += 1
        print(f"  · [{mid}] {name[:56]} — {' '.join(changed)}")
        # 같은 재료에 판정 행이 둘 오면 뒤엣것이 앞엣것을 덮던 자리다(57차 SA).
        # `have` 를 시작에 한 번만 읽어 두 번째 행이 낡은 스냅샷 위에 병합됐다 —
        # 조용히 사라지고 도구는 성공을 찍었다. 여기서 되먹여 다음 행이 이어받게 한다.
        have[mid] = (name, json.dumps(attrs, ensure_ascii=False))
        if a.apply:
            c.execute("update material set attributes=? where id=?",
                      (json.dumps(attrs, ensure_ascii=False), mid))
    if a.apply:
        c.commit()
        print("\n[적용됨]")
    else:
        print("\n[예행] --apply 를 붙이면 쓴다")
    for k, v in st.items():
        print(f"  {k}: {v}")
    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
