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
#   · dict 이면 기존 dict 와 **키 단위로 병합**한다(같은 키는 새 사유로 덮는다).
#   · null 이면 그 attribute 를 **내린다**(재료 단위 문자열 판정을 정정할 때).
#   · 덮거나 내리기 전의 값은 `<attr>_before_correction` 에 남긴다(브리프 594).
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

    rows: list[dict] = []
    for p in a.paths:
        doc = json.load(open(p))
        rows += doc.get("verdicts", [])
    print(f"     판정 입력 {len(rows)}종")

    st = Counter()
    for r in rows:
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
                attrs[f"{attr}_before_correction"] = old
                changed.append(f"-{attr}")
                st["내림"] += 1
                continue
            if isinstance(new, dict):
                merged = dict(old) if isinstance(old, dict) else {}
                merged.update(new)
                if merged == old:
                    continue
                if old is not None and not isinstance(old, dict):
                    attrs[f"{attr}_before_correction"] = old   # 문자열 판정 → dict 로 승격
                elif f"{attr}_before_correction" not in attrs:
                    attrs[f"{attr}_before_correction"] = old    # null = 정정 전에 없었다(브리프 558②)
                attrs[attr] = merged
                changed.append(f"{attr}[{len(merged)}]")
                st["병합"] += 1
            else:
                if old == new:
                    continue
                if f"{attr}_before_correction" not in attrs:
                    attrs[f"{attr}_before_correction"] = old
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
