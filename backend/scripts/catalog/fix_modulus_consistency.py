#!/usr/bin/env python
# E와 G가 등방관계(E=2G(1+nu))를 크게 벗어나는 재료를, **근거가 더 좋은 쪽에서 유도**해 정합화.
#
# 사용: fix_modulus_consistency.py [--apply]
#
# 배경: 대표값을 물성마다 독립으로 고르다 보니 E는 계열 추정(tier4)인데 G는 실측(tier1)인
# 조합이 생긴다. 그러면 E/G가 1이나 6.7처럼 물리적으로 불가능한 값이 되고, 해석에서
# 전단·인장 응답이 서로 모순된다. 등급이 더 좋은 쪽을 남기고 반대쪽을 유도한다.
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"
K_E, K_G, K_NU = ("mechanical.youngs_modulus", "mechanical.shear_modulus",
                  "mechanical.poisson_ratio")
# 등방 고체는 nu 0~0.5 → E/G = 2(1+nu) = 2~3. 여유를 둬 이 밖만 손댄다.
LO, HI = 1.95, 3.05
# 이방성 결정·이방성 소재는 등방관계가 성립하지 않는다 — 손대면 안 된다.
ANISOTROPIC = ("silicon", "(si)", "sapphire", "quartz", "linbo3", "mos2", "graphite",
               "aln", "scaln", "mems", "wafer", "single-crystal", "단결정", "pgs")
# 슬롯에 성격이 다른 제품이 섞여 있다고 이미 표시된 값은 유도로 덮으면 안 된다.
MISMATCH_MARK = "[주의] 이 슬롯의"


# 실측값을 유도값으로 덮으면 데이터가 파괴된다. 추정·계산값만 대체 대상이다.
OVERWRITABLE = ("estimated", "computed")


def _temp_of(c, rid):
    """행의 측정 온도(°C). 없으면 None."""
    import json
    raw = c.execute("select conditions from property_value where id=?", (rid,)).fetchone()[0]
    try:
        d = json.loads(raw) if raw else {}
    except Exception:
        return None
    if not isinstance(d, dict):
        return None
    for k, conv in (("temperature_C", lambda v: v), ("temperature_c", lambda v: v),
                    ("temperature_K", lambda v: v - 273.15), ("temperature_k", lambda v: v - 273.15)):
        v = d.get(k)
        if isinstance(v, (int, float)):
            return float(conv(v))
    return None


def load_reps():
    """앱과 **같은 대표값 규칙**을 쓴다 — 자체 SQL로 고르면 상온 우선 규칙이 빠져
    -40 °C 유리상 값 같은 극단값을 집는다."""
    from app.db import SessionLocal
    from app.catalog_compare import representative_rows
    with SessionLocal() as s:
        rows = representative_rows(s, [K_E, K_G, K_NU])
    return {k: (v.id, v.value_num, v.quality_tier, v.notes or "", v.method or "")
            for k, v in rows.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    c = sqlite3.connect(DB)
    reps = load_reps()
    fixed = skipped = 0
    for mid, name in c.execute("select id, name from material").fetchall():
        e, g = reps.get((mid, K_E)), reps.get((mid, K_G))
        if not (e and g):
            continue
        te, tg = _temp_of(c, e[0]), _temp_of(c, g[0])
        if te is not None and tg is not None and abs(te - tg) > 20.0:
            print(f"  건너뜀(측정 온도 다름) {name[:34]:34s} E@{te:g}°C vs G@{tg:g}°C")
            skipped += 1
            continue
        if MISMATCH_MARK in e[3] or MISMATCH_MARK in g[3]:
            print(f"  건너뜀(제품 혼재 표시됨) {name[:36]:36s} E/G {e[1]/g[1]:.2f}")
            skipped += 1
            continue
        ratio = e[1] / g[1]
        if LO <= ratio <= HI:
            continue
        if any(k in name.lower() for k in ANISOTROPIC):
            print(f"  건너뜀(이방성) {name[:40]:40s} E/G {ratio:.2f}")
            skipped += 1
            continue
        nu_row = reps.get((mid, K_NU))
        nu = min(nu_row[1], 0.499) if nu_row else 0.45
        # 신뢰등급이 더 좋은 쪽을 남긴다. 같으면 실측이 있는 G 쪽을 신뢰한다.
        if e[2] <= g[2] and e[2] < 4:
            tgt, src_v, newv = ("G", e[1], e[1] / (2 * (1 + nu)))
            rid, base = g[0], f"E={e[1]:.4g} Pa(tier{e[2]})"
        else:
            tgt, src_v, newv = ("E", g[1], 2 * g[1] * (1 + nu))
            rid, base = e[0], f"G={g[1]:.4g} Pa(tier{g[2]})"
        target_method = (g if tgt == "G" else e)[4]
        if target_method not in OVERWRITABLE:
            print(f"  건너뜀(실측을 덮을 수 없음) {name[:34]:34s} E/G {ratio:8.2f} "
                  f"— {tgt}가 {target_method}")
            skipped += 1
            continue
        print(f"  {name[:38]:38s} E/G {ratio:8.2f} → {tgt} 유도 {newv:.4g} Pa  (근거 {base})")
        if a.apply:
            c.execute("""update property_value set value_num=?, method='computed', quality_tier=4,
                notes=trim(coalesce(notes,'')||' [정합화] '||?)
                where id=? and coalesce(notes,'') not like '%[정합화]%'""",
                (newv, f"E/G가 {ratio:.2f}로 등방관계(2~3)를 벗어나, 근거가 더 좋은 {base}와 "
                       f"nu={nu:g}에서 유도했다.", rid))
            fixed += 1
    if a.apply:
        c.commit()
    print(f"\n{'[APPLIED]' if a.apply else '[DRY-RUN]'} 정합화 {fixed} / 이방성 건너뜀 {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
