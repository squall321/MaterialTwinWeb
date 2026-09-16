# 76차 — 판정 병합기가 흔적 없이 덮은 판정 사유문을 스냅샷에서 되찾아 복원 파일로 만든다.
#
# 스냅샷을 시간순으로 이어 보고, 앞 스냅샷의 판정 사유문이 다음 스냅샷에서
#   ① 같은 칸에 그대로·덧붙여 남아 있지 않고
#   ② `<attr>_before_correction` 에도 없고
#   ③ 같은 재료·같은 물성키의 다른 판정 칸으로 옮겨 가지도 않았으면
# 지워진 것으로 센다. 그중 **라이브에서도 여전히 없는 것**만 복원 대상으로 낸다.
# 덮은 쪽은 새 사유문이 어느 배치 판정 파일에 있는지로 찾는다.
#
# 사용:  python3 scripts/catalog/out_la/la76_gen_restore.py   → la76_02_overwritten_verdict_text.json
#
# **정정을 적용한 뒤에는 다시 돌리지 마라.** 76차 정정은 303칸의 문장을 제자리에서 고쳤으므로,
# 적용 후 라이브를 기준으로 돌리면 그 303칸도 「앞 문장이 사라진 칸」으로 잡혀 복원 파일이
# 틀린 내용으로 덮인다(실제로 한 번 그렇게 덮였다 — 적용 직전 스냅샷 pre-w76txt 를
# MATERIALTWIN_DATA_DIR 의 materialtwin.db 로 걸어 다시 만들었다). 그래서 기존 파일은 덮지 않는다.
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
SNAP_DIR = "/data/appdata/materialtwin_web"
LIVE = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
                    "materialtwin.db")
VERDICTS = ("core_not_applicable", "core_absent_from_vendor_sheet",
            "core_rejected_printed_value", "core_no_public_document")


def load(db: str) -> tuple[dict, dict, dict]:
    """(칸 → 사유문, (재료, 판정) → before_correction, 재료 → 이름)."""
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    cells, before, names = {}, {}, {}
    for mid, name, raw in c.execute("select id, name, attributes from material"):
        names[mid] = name
        try:
            a = json.loads(raw or "{}")
        except Exception:
            continue
        if not isinstance(a, dict):
            continue
        for attr in VERDICTS:
            if f"{attr}_before_correction" in a:
                before[(mid, attr)] = a[f"{attr}_before_correction"]
            if isinstance(a.get(attr), dict):
                for key, reason in a[attr].items():
                    cells[(mid, attr, key)] = str(reason)
    c.close()
    return cells, before, names


def batch_of(text: str) -> str | None:
    """이 사유문을 낸 배치 판정 파일의 batch 이름."""
    for p in sorted(glob.glob(str(HERE.parent / "out_*" / "*verdicts*.json"))):
        try:
            doc = json.load(open(p))
        except Exception:
            continue
        for r in doc.get("verdicts", []):
            for attr in VERDICTS:
                if isinstance(r.get(attr), dict) and text in r[attr].values():
                    return doc.get("batch") or os.path.basename(p)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="기존 복원 파일을 덮는다")
    a = ap.parse_args()
    out = HERE / "la76_02_overwritten_verdict_text.json"
    if out.exists() and not a.force:
        print(f"✗ {out.name} 이 이미 있다 — 덮지 않는다(머리 주석 참고). 덮으려면 --force")
        return
    snaps = [p for p in glob.glob(f"{SNAP_DIR}/materialtwin.db.pre-*")
             if not p.endswith(("-shm", "-wal"))]
    snaps.sort(key=lambda p: re.search(r"(\d{8}-\d{6})Z", p).group(1))
    chain = snaps + [LIVE]
    live_cells, _, _ = load(LIVE)
    rows = []
    prev = load(chain[0])
    for older, newer in zip(chain, chain[1:]):
        cur = load(newer)
        for (mid, attr, key), old in prev[0].items():
            new = cur[0].get((mid, attr, key))
            if new is not None and old in new:
                continue
            kept = cur[1].get((mid, attr))
            if isinstance(kept, dict) and str(kept.get(key)) == old:
                continue
            if any(k[0] == mid and k[2] == key and old in t for k, t in cur[0].items()):
                continue
            if old in live_cells.get((mid, attr, key), ""):
                continue
            rows.append({
                "material_id": mid, "name": prev[2][mid], "attr": attr, "property_key": key,
                "lost_between": [os.path.basename(older), os.path.basename(newer)],
                "overwritten_by": batch_of(new) if new is not None else None,
                "old_len": len(old), "old_text": old,
            })
        prev = cur
    json.dump({"batch": "76차 복원", "rows": rows}, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"{len(rows)}칸 → {out.name}")
    for r in rows:
        print(f"  [{r['material_id']}] {r['property_key']:28s} {r['old_len']:5d}자  "
              f"{r['lost_between'][1][16:32]}  덮은 배치 {r['overwritten_by']}")


if __name__ == "__main__":
    main()
