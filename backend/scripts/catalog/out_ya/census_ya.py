#!/usr/bin/env python3
# 63차 YA — 구식 문자열 키 `conditions.temperature` 2,255행을 갈래별로 세는 조사 스크립트.
import json
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from app.temperature_vocab import ROOM, NOT_REPORTED, head, kelvin, normalize, printed  # noqa

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR", ""), "materialtwin.db")
TEMP_VALUED = {
    'thermal.melting_point', 'thermal.glass_transition', 'thermal.max_service_temp',
    'thermal.min_service_temp', 'thermal.decomposition_temp', 'thermal.heat_deflection_temp',
    'thermal.vicat_softening', 'thermal.dilatometric_softening_point',
    'thermal.viscosity_reference_temperature'}


def rows():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    out = []
    for r in con.execute("select id,material_id,property_key,value_num,unit,conditions,notes,"
                         "source_id,quality_tier from property_value where conditions is not null"):
        d = json.loads(r[5])
        if isinstance(d, dict) and "temperature" in d:
            out.append((*r[:5], d, *r[6:]))
    con.close()
    return out


def bucket(v):
    """(갈래, 부가정보)."""
    if isinstance(v, bool):
        return "기타", ""
    if isinstance(v, (int, float)):
        return "맨숫자", ""
    k = kelvin(v)
    if k is not None:
        return "숫자표기", f"{printed(v)} → {k} K"
    n = normalize(v)
    if n == ROOM:
        return "실온진술", ""
    if n == NOT_REPORTED:
        return "부재진술", ""
    if printed(v) is not None:
        return "숫자결함", f"{printed(v)}"   # 절대영도 이하
    return "미접힘", ""


def main():
    rs = rows()
    print(f"[DB] {DB}\n`conditions.temperature` 행 {len(rs)}")
    b = Counter()
    detail = defaultdict(Counter)
    both = []
    tv = []
    for pid, mid, pk, vn, unit, d, notes, src, tier in rs:
        v = d["temperature"]
        g, info = bucket(v)
        b[g] += 1
        detail[g][repr(v)] += 1
        if "temperature_k" in d:
            both.append((pid, mid, pk, v, d["temperature_k"], g))
        if pk in TEMP_VALUED:
            tv.append((pid, mid, pk, v, g))
    print("\n-- 갈래별 행수 --")
    for g, n in b.most_common():
        print(f"  {n:>6}  {g}  (표기 {len(detail[g])}종)")
    print(f"\n표기 총 {sum(len(v) for v in detail.values())}종")

    for g in ("숫자표기", "맨숫자", "숫자결함", "미접힘"):
        print(f"\n-- {g} ({b[g]}행 · {len(detail[g])}종) --")
        for s, n in detail[g].most_common():
            print(f"  {n:>4}  {s}")

    print(f"\n-- `temperature` 와 `temperature_k` 를 둘 다 가진 행 {len(both)} --")
    for pid, mid, pk, v, tk, g in both:
        print(f"  pv{pid} 재료{mid} {pk}  temperature={v!r} · temperature_k={tk}  [{g}]")

    print(f"\n-- 값 자체가 온도인 물성(TEMP_VALUED)에 걸린 행 {len(tv)} --")
    for pid, mid, pk, v, g in tv:
        print(f"  pv{pid} 재료{mid} {pk} {v!r} [{g}]")

    for g in ("실온진술", "부재진술"):
        print(f"\n-- {g} 표기 {len(detail[g])}종 (상위 25) --")
        for s, n in detail[g].most_common(25):
            print(f"  {n:>4}  {s}")


if __name__ == "__main__":
    main()
