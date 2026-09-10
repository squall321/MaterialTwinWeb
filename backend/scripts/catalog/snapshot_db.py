# 라이브 DB 의 **현재 상태** 사본을 뜬다 — 리허설·백업 공용. `cp` 를 쓰지 마라.
#
# 왜 이 도구가 있는가
#   라이브는 WAL 모드다. `cp materialtwin.db copy.db` 는 **체크포인트 이전 상태**를 준다 —
#   최근 쓰기가 `-wal` 에만 있고 본체에 아직 안 접혔기 때문이다. 실측(2026-09-10):
#       cp           값 46,419 · 정의 274 · 새 키 없음
#       VACUUM INTO  값 46,498 · 정의 275 · 새 키 있음   ← 라이브와 동일
#
#   73차 IC 가 이것에 걸렸다 — 새로 연 키가 `-wal` 에만 있어 55행 중 52행이 "미정의 key" 로
#   거부됐다. 그리고 IC 가 더 나쁜 얼굴을 짚었다:
#
#       **키가 이미 있는 배치였다면 아무 소리 없이 구 DB 기준으로 「검증 통과」가 나왔을 것이다.**
#
#   즉 이 사고는 요란하게 실패하는 대신 **조용히 틀린 합격**을 낸다. 그래서 도구로 못 박는다.
#
# 사용
#   python3 scripts/catalog/snapshot_db.py <대상경로>            라이브 → 대상
#   python3 scripts/catalog/snapshot_db.py <대상경로> --src <경로>
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path


def snapshot(src: str, dst: str) -> tuple[int, int]:
    """`VACUUM INTO` 로 현재 상태를 뜬다. (값 행수, 정의 수)를 돌려준다."""
    dst_p = Path(dst)
    if dst_p.exists():
        dst_p.unlink()          # VACUUM INTO 는 기존 파일을 덮지 않는다
    dst_p.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    con.execute("VACUUM INTO ?", (str(dst_p),))
    con.close()
    chk = sqlite3.connect(f"file:{dst_p}?mode=ro", uri=True)
    n_val = chk.execute("select count(*) from property_value").fetchone()[0]
    n_def = chk.execute("select count(*) from property_definition").fetchone()[0]
    chk.close()
    return n_val, n_def


def main() -> int:
    ap = argparse.ArgumentParser(description="라이브 DB 의 현재 상태 사본(WAL 포함)")
    ap.add_argument("dst")
    ap.add_argument("--src", default=None,
                    help="원본. 기본값은 $MATERIALTWIN_DATA_DIR/materialtwin.db")
    a = ap.parse_args()
    src = a.src or (os.environ.get("MATERIALTWIN_DATA_DIR", "") + "/materialtwin.db")
    if not Path(src).exists():
        print(f"✗ 원본 없음: {src}\n  MATERIALTWIN_DATA_DIR 를 설정했는가?", file=sys.stderr)
        return 1
    n_val, n_def = snapshot(src, a.dst)
    wal = Path(str(src) + "-wal")
    extra = f" (WAL {wal.stat().st_size / 1e6:.1f} MB 포함)" if wal.exists() else ""
    print(f"✔ {a.dst}\n  값 {n_val:,} · 정의 {n_def}{extra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
