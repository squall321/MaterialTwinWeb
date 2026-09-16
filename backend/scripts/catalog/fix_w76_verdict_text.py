# 76차 정정 — 판정 사유문 두 가지를 고친다. 판정 칸의 유무·종류는 건드리지 않는다.
#
#   R  복원  판정 병합기(apply_core_verdicts.py)가 같은 칸을 두 번째로 바꾸며 흔적 없이 지운
#            앞 사유문 32칸을 되돌려 붙인다. 원문은 스냅샷에서 뽑아 둔
#            out_la/la76_02_overwritten_verdict_text.json 에 있다(생성기 la76_gen_restore.py).
#
#   W  문구  74차 JA·JB·JC 가 코퍼스 표 층 검색을 「전수」라고 적은 303칸(75차 KD 가 셌다).
#            KD 실측으로 표 파일 88,637장 중 9,327장(10.5%)은 추출 때 행을 잃고 캡션만 남았다.
#            등급명 grep 은 그 잃은 행을 볼 수 없으므로 「전수」는 사실이 아니다. 판정의 주 근거는
#            벤더 문서라 판정은 그대로 둔다. 문구만 고치고, 칸마다 무엇을 왜 고쳤는지 덧붙인다.
#            JC 문장이 적은 명령(`tables --want thermal.specific_heat`)은 색인 키가
#            `specific_heat` 라 그대로 치면 0편이 나온다 — 76차에 올바른 키로 다시 세어 고쳤다.
#
# 복원을 먼저 한다. 되찾은 74차 JA 원문 16칸에도 같은 문구가 들어 있다(JA 116 + 16 = 132).
# 다시 돌려도 늘지 않는다 — 복원 머리와 정정 머리가 이미 있으면 그 칸을 건너뛴다.
#
# 사용:  fix_w76_verdict_text.py [--db <경로>] [--apply]
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from collections import Counter
from pathlib import Path

DEFAULT_DB = os.path.join(
    os.environ.get("MATERIALTWIN_DATA_DIR",
                   "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
    "materialtwin.db")
RESTORE_FILE = Path(__file__).resolve().parent / "out_la" / "la76_02_overwritten_verdict_text.json"
VERDICTS = ("core_not_applicable", "core_absent_from_vendor_sheet",
            "core_rejected_printed_value", "core_no_public_document")
EXPECT = {"복원": 32, "JA": 132, "JB": 102, "JC": 69}

RESTORE_HEAD = ("**[76차 복원 — {batch} 가 이 칸을 새 사유로 바꿀 때 흔적 없이 지워진 앞 사유문이다. "
                "스냅샷 `{snap}` 에서 그대로 옮긴다]**")

LOSS = ("표 파일의 10.5%는 추출 때 행을 잃고 캡션만 남아 있어(75차 KD 실측 88,637장 중 9,327장) "
        "그 잃은 행 속 등급명은 이 grep 에 걸리지 않는다.")

# (갈래, 원문, 고친 문장)
REPLACE = (
    ("JA", "(5) 74차 JA: **코퍼스 표 층 전수** — /data/paper_patent_corpus 의 tables/*.md 88,532장을 "
           "등급 토큰으로 전수 grep 했다(FTS 색인 밖의 층이다).",
           "(5) 74차 JA: **코퍼스 표 층 grep — 행이 남은 표만 본다** — /data/paper_patent_corpus 의 "
           "tables/*.md 88,532장을 등급 토큰으로 grep 했다(FTS 색인 밖의 층이다). " + LOSS),
    ("JA", "결론: 벤더 층·규격 층(71차 GD 의 IPC-4101 판정)·학술 층이 모두 닫혔다.",
           "결론: 벤더 층·규격 층(71차 GD 의 IPC-4101 판정)은 닫혔고, 학술 층은 본문과 행이 남은 표의 "
           "범위에서 닫혔다."),
    ("JB", "74차 JB 가 `/data/paper_patent_corpus/structured` 의 **표 층 `tables/*.md` 전수**와 "
           "**본문 층 전수**를 이 벤더의 등급 토큰으로 따로 grep 했다.",
           "74차 JB 가 `/data/paper_patent_corpus/structured` 의 **표 층 `tables/*.md` 파일 전부**와 "
           "**본문 층 전수**를 이 벤더의 등급 토큰으로 따로 grep 했다. 다만 " + LOSS),
    ("JB", "가 **표 층까지 포함해 확정됐다.**",
           "가 **본문과 행이 남은 표까지 넓혀도 뒤집히지 않았다.**"),
    ("JC", "표 층도 두드렸다: `corpus_index.py tables --want thermal.specific_heat` 이 비열 표를 가진 "
           "논문 220편을 세지만 두산 등급을 잰 것은 0편이다.",
           "표 층도 두드렸다 — 표 색인(`corpus_index.py` 의 ptab)이 비열 표를 가진 것으로 잡는 논문은 "
           "220편이고, 그 논문들의 표 파일 1,271장에 두산 등급명은 0건이다. 표 파일 88,637장 전부를 "
           "`doosan|두산|斗山|DSflex|DS-숫자4자리` 로 훑어도 적중 3장은 모두 거짓 양성이다(HPC 작업 추적 "
           "이름 `SDSC-DS-2004`, LCD 디밍 논문의 영상 시퀀스 이름 `doosan`). 다만 캡션만 남은 표 "
           "9,327장(10.5%)의 잃은 행은 이 검색이 볼 수 없다."),
)

NOTE_HEAD = "**[76차 정정 — 코퍼스 표 층 검색 문구]**"
NOTE_COMMON = (
    " 75차 KD 가 재 보니 표 파일 88,637장 중 9,327장(10.5%)은 추출 때 행을 잃고 캡션만 남았고 "
    "그중 4,171장은 0바이트여서, 등급명 검색은 그 잃은 행을 볼 수 없다. 74차 문장은 이 한계를 적지 "
    "않아 표 층을 다 본 것처럼 읽혔으므로 한정을 넣었다. 이 판정의 주 근거는 벤더 문서이므로 판정은 "
    "그대로 둔다. 캡션만 남은 표를 품은 문서 3,156편 중 3,152편은 원본 PDF 가 있어 렌더로 복구할 수 "
    "있다.")
NOTE_ONLY = {
    "JA": " 고친 곳은 (5) 갈래의 이름·서술(원문 「코퍼스 표 층 전수 — … 전수 grep 했다」)과 결론 문장"
          "(원문 「…·학술 층이 모두 닫혔다」) 두 곳이다.",
    "JB": " 고친 곳은 「표 층 tables/*.md 전수」(파일 전부로 고치고 한계 한 문장을 붙였다)와 끝 문장"
          "(원문 「표 층까지 포함해 확정됐다」) 두 곳이다.",
    "JC": " 원문은 「`corpus_index.py tables --want thermal.specific_heat` 이 비열 표를 가진 논문 220편을 "
          "세지만 두산 등급을 잰 것은 0편이다」였다. 그 명령을 그대로 치면 색인 키가 `specific_heat` 라 "
          "0편이 나온다. 76차에 올바른 키로 220편과 그 표 파일 1,271장을 다시 훑고, 표 파일 88,637장 "
          "전부도 다시 훑어 결론(두산 등급 0)을 확인했다.",
}


def restore(attrs_by_mid: dict, st: Counter) -> None:
    rows = json.load(open(RESTORE_FILE))["rows"]
    for r in rows:
        mid, attr, key = r["material_id"], r["attr"], r["property_key"]
        cell = (attrs_by_mid.get(mid) or {}).get(attr)
        if not isinstance(cell, dict) or key not in cell:
            st["복원 · 칸 없음"] += 1
            print(f"  ✗ 복원할 칸이 없다 [{mid}] {attr} {key}")
            continue
        head = RESTORE_HEAD.format(batch=r["overwritten_by"], snap=r["lost_between"][0])
        if head in str(cell[key]):
            st["복원 · 이미"] += 1
            continue
        cell[key] = f"{cell[key]}\n\n{head}\n{r['old_text']}"
        st["복원"] += 1


def reword(attrs_by_mid: dict, st: Counter) -> set:
    touched = set()
    for mid, attrs in attrs_by_mid.items():
        for attr in VERDICTS:
            cell = attrs.get(attr)
            if not isinstance(cell, dict):
                continue
            for key, reason in cell.items():
                text = str(reason)
                groups = []
                for g, old, new in REPLACE:
                    if old in text:
                        text = text.replace(old, new)
                        if g not in groups:
                            groups.append(g)
                if not groups:
                    if NOTE_HEAD in text:
                        st["정정 · 이미"] += 1
                    continue
                note = NOTE_HEAD + NOTE_COMMON + "".join(NOTE_ONLY[g] for g in groups)
                cell[key] = f"{text}\n\n{note}"
                for g in groups:
                    st[g] += 1
                touched.add(mid)
    return touched


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    c = sqlite3.connect(a.db)
    print(f"[DB] {a.db}")
    raw = {mid: at for mid, at in c.execute("select id, attributes from material")}
    attrs_by_mid = {mid: json.loads(at or "{}") for mid, at in raw.items()}

    st = Counter()
    restore(attrs_by_mid, st)
    reword(attrs_by_mid, st)
    changed = [mid for mid, at in attrs_by_mid.items() if at != json.loads(raw[mid] or "{}")]
    for k, v in st.items():
        print(f"  {k}: {v}")
    print(f"  바뀐 재료: {len(changed)}종")

    # 새로 고친 수 + 이미 고쳐 둔 수가 기대와 맞아야 쓴다 — 어긋나면 문구가 바뀐 칸이 있다는 뜻이다.
    done_r = st["복원"] + st["복원 · 이미"]
    done_w = st["JA"] + st["JB"] + st["JC"]
    ok = done_r == EXPECT["복원"] and (
        done_w == 0 and st["정정 · 이미"] == EXPECT["JA"] + EXPECT["JB"] + EXPECT["JC"]
        or all(st[g] == EXPECT[g] for g in ("JA", "JB", "JC")))
    if not ok:
        print(f"  ✗ 기대({EXPECT})와 다르다 — 쓰지 않는다")
        return 1
    if a.apply:
        for mid in changed:
            c.execute("update material set attributes=? where id=?",
                      (json.dumps(attrs_by_mid[mid], ensure_ascii=False), mid))
        c.commit()
        print("[적용됨]")
    else:
        print("[예행] --apply 를 붙이면 쓴다")
    c.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
