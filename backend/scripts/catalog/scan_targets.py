#!/usr/bin/env python3
# 다음 파동의 표적 논문을 뽑는다 — 기채굴(mined_index)과 **기폐기(정본 대장)** 를 둘 다 걸러서.
#
# 왜 필요한가
#   36차에 표적 목록을 손으로 만들었더니 **두 방향으로 틀렸다.**
#   ① 이미 캔 논문 셋(Ehrler 143행 · Fujishima 59행 · Narahashi 19행)이 목록에 올라
#      배치들이 중복 작업을 했다 — `mined_index` 결함이었고 고쳤다(브리프 410·427).
#   ② **판정하고 버린 논문 9편이 그대로 남았다.** 행이 0이니 기채굴 조회로는 영영 안 걸린다.
#      다음 파동이 열어서 읽고 같은 이유로 다시 버린다. 이쪽은 조회가 아니라 **기록**의 문제다.
#
# 그래서 폐기를 정본 대장 하나에 모은다 — `_index/_verdicts/discarded.jsonl`.
# 배치는 논문을 버릴 때마다 여기에 한 줄 덧붙인다(제목·파동·사유).
#
# **대장은 보수적으로 쓴다.** 거짓 폐기는 **논문을 잃고**, 놓친 폐기는 재발굴로 일만 낭비한다.
# 그래서 제목 정규화가 정확히 맞을 때만 거른다 — 접두·인용키 같은 느슨한 축은 안 쓴다.
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mined_index import DB as MT_DB, build, look, norm_title  # noqa: E402


def norm_full(t: str | None) -> str:
    """폐기 대조용 — **자르지 않은** 전체 제목 정규화.

    `norm_title` 은 45자에서 자른다. 조회에는 그게 맞지만(표기 흔들림을 흡수한다)
    **폐기 대조에는 치명적이다** — 자매논문이 접두로 겹치면 한쪽을 버렸을 때
    다른 쪽까지 사라진다. 37차 AT 의 Liu 2009 두 편이 정확히 그랬다
    (cast acrylic 편 11행 대 bi-layer 편 폐기, 45자까지 글자가 같다).
    폐기는 **정확히 맞을 때만** 걸러야 하므로 전체 제목을 쓴다.
    """
    return norm_title(t) if t is None else __import__("re").sub(
        r"[^a-z0-9]", "", __import__("unicodedata").normalize("NFKD", t).lower())

CORPUS = "/data/paper_patent_corpus/_index/corpus_fts.db"

# ── 재인용 위험도 ──────────────────────────────────────────────────────────────
# 37차 AU 가 패키징·신뢰성 6편을 **6/6 전량 폐기**하고 짚었다 —
# *"물성키 개수 순위는 이 갈래에서 신호가 없다"*. 맞다. 리뷰·해석입력 논문은
# **남의 데이터를 모았기 때문에** 키가 많고, 그래서 이 정렬의 맨 위로 온다.
#
# 실측(폐기 14편 대 수확 8편)으로 고른 지표 둘 —
#   ① 표 캡션 **및 표를 소개하는 앞 문장**에 인용이 붙은 비율
#   ② 표에 `Ref.`/`References`/`Source` **열**이 있는가(195번의 최강 신호)
# 재현율 50%(7/14) · 오탐 25%(2/8).
#
# **이 점수로 제외하지 마라.** 오탐 둘은 둘 다 실제로 값이 나온 논문이다
# (Liu 2011 은 36행, Fujishima 2017 은 5행 — 표 일부만 재인용이었다).
# 410·416번과 같은 비대칭이다: 거짓 제외는 **논문을 잃고**, 놓친 경고는 일만 낭비한다.
# 그리고 **못 잡는 부류가 절반이다** — 출처 표시가 아예 없는 벤더 스펙 편찬표
# (Palm 2003 · Huang 2001)는 인용이 0건이라 이 지표로는 안 걸린다.
_TAB = re.compile(r"(?im)^\s*(?:\*\*)?tab(?:le|\.)\s*[0-9IVX]+[.:]?")
_CIT = re.compile(r"\[\s*\d{1,3}\s*(?:[,\-–]\s*\d{1,3}\s*)*\]"
                  r"|\((?:[A-Z][a-zA-Z]+(?: et al\.?)?[ ,]+(?:19|20)\d{2})\)")
_REFCOL = re.compile(r"(?i)\|\s*(?:ref\.?|references?|source)\s*\|")
# ③ **FEA 입력표를 스스로 밝히는 문구** — 38차 AX 가 폐기한 셋이 거의 같은 말을 썼다:
#    *"The material properties used in FEA modeling … are listed in Table I."* ·
#    *"material properties in Table 2"* · *"The material properties used are shown in Table 1,
#    and have been obtained from the literature [7-10]."*
# 실측(폐기 20편 대 수확 10편): 재현율 40% · 오탐 20%. 캡션 지표와 **잡는 논문이 다르다.**
_FEA = re.compile(
    r"(?i)(?:material|mechanical|thermal)\s+propert\w+\s+(?:\w+\s+){0,6}?"
    r"(?:used|utilis\w+|utiliz\w+|adopted|employed|taken|selected|sourced)"
    r"|propert\w+\s+(?:\w+\s+){0,4}(?:are|is|were|was)\s+"
    r"(?:listed|shown|summari[sz]ed|given|presented)\s+in\s+tab")
# **기각한 후보** — "측정 소절(Experimental·Characterization 표제)이 있는가" 는 38차 AX 의 제안인데
# 실측하니 **신호가 아니다**: 폐기 6/20(30%) 대 수확 5/10(50%) 로 오히려 방향이 반대다.
# 해석입력 논문도 자기 실험(휨 측정 등)은 하기 때문이다. 넣지 않았다.


# ④ **물리 상한 위반** — 등방재의 포아송비는 0.5 를 못 넘는다(체적탄성률이 발산한다).
# 38차 AZ 가 Wang 2017 에서 ν = 0.50·0.53 을 잡아 표 전체를 30초에 죽였다.
# 실측: 폐기 24편 중 **1편**만 걸린다(재현율 4%). 그런데 **수확 11편에서 0건 — 오탐이 없다.**
# 통계 지표가 아니라 **확정 신호**라 정렬에 쓰지 않고 별도 경고로 낸다.
# 걸리면 그 표는 물리적으로 틀린 것이고, 10번대로 **표 전체**를 의심해야 한다.
# **표 행만 본다.** 처음엔 산문까지 훑었더니 실제 코퍼스에서 오탐이 4건 났다 —
# `\bnu\b` 가 낱말 안에 걸리고, 긴 산문 줄의 아무 소수나 집었다.
# (수확 11편에서 오탐 0 이었지만 그건 표본이 작아서였다. 실제 163편에 걸어 보고 알았다.)
# 그래서 **파이프표 행 + 라벨 셀에 poisson 이 있는 것**만 본다.
_NU_ROW = re.compile(r"(?im)^\|[^|\n]*poisson[^|\n]*\|(.+)$")
_NUM = re.compile(r"(?<![\d.])(0?\.\d+|\d\.\d+)(?![\d])")


def physics_violation(text: str) -> list[float]:
    """등방 포아송비가 0.5 를 넘는 칸을 찾는다. 걸리면 그 표는 못 쓴다.

    **이방성 적층판은 nu12 가 0.5 를 넘을 수 있다** — 그러니 걸린 것도 사람이 확인해야 한다.
    라벨에 방향 표기(nu12·in-plane·warp 등)가 있으면 위반이 아니다.
    """
    bad = set()
    for m in _NU_ROW.finditer(text):
        lab = m.group(0).split("|")[1].lower()
        if re.search(r"(?:12|21|13|23|xy|in.?plane|warp|fill|major|minor)", lab):
            continue          # 이방성 방향 성분은 0.5 를 넘을 수 있다
        for v in _NUM.findall(m.group(1)):
            if 0.5 < float(v) <= 0.99:
                bad.add(float(v))
    return sorted(bad)


def recite_risk(path: str) -> dict:
    """표가 남의 것인지 예측한다. 판정이 아니라 **읽는 순서와 경고**용이다."""
    try:
        t = open(path, encoding="utf-8", errors="replace").read(400_000)
    except OSError:
        return {"tables": 0, "cited": 0, "ratio": 0.0, "ref_col": 0, "flag": False}
    ms = list(_TAB.finditer(t))
    hit = 0
    for m in ms:
        # 캡션 뒤 180자 + 표를 소개하는 **앞 문장** 300자를 함께 본다.
        # Yang 2019 는 캡션이 아니라 앞 문장이 인용을 달고 있었다
        # (*"The related material parameters are shown as follow [7][15][20]."*).
        if _CIT.search(t[max(0, m.start() - 300):m.start()] + t[m.end():m.end() + 180]):
            hit += 1
    ref = len(_REFCOL.findall(t))
    ratio = hit / len(ms) if ms else 0.0
    cap = bool(ref) or (len(ms) >= 2 and ratio >= 0.34)
    fea = bool(_FEA.search(t))
    # **0~2 점수로 쓴다. 불리언 OR 은 오탐이 40% 라 수확 논문을 뒤로 민다.**
    # 둘 다 걸린 것(2점)은 오탐 10% 로 정밀하고, 0점은 가장 깨끗하다.
    return {"tables": len(ms), "cited": hit, "ratio": round(ratio, 2), "ref_col": ref,
            "caption": cap, "fea_phrase": fea, "score": int(cap) + int(fea),
            "flag": cap and fea, "physics": physics_violation(t)}
VERDICTS = Path("/data/paper_patent_corpus/_index/_verdicts/discarded.jsonl")


def db_rows_by_full_title() -> dict[str, int]:
    """DB 출처를 **전체 제목**으로 색인해 행수를 낸다 — 폐기 가드용."""
    c = sqlite3.connect(MT_DB)
    agg = {r[0]: r[1] for r in c.execute(
        "select source_id,count(*) from property_value where source_id is not null group by 1")}
    out: dict[str, int] = {}
    for sid, t in c.execute("select id,title from source where title is not null"):
        k = norm_full(t)
        out[k] = max(out.get(k, 0), agg.get(sid, 0))
    return out


def load_verdicts(idx: dict | None = None) -> dict[str, dict]:
    """정본 폐기 대장을 읽는다. 키는 정규화 제목.

    **가드**: DB 에 값이 들어 있는 제목은 폐기로 받지 않는다.
    37차 AT 가 예측된 실패를 한 파동 만에 냈다 — 자매논문(제목이 접두로 겹치고 DOI 가 다르다)과
    표 사이드카를, 각각 **본 논문 제목**으로 적었다. 그대로 두면
    11행짜리 cast acrylic 편과 36행짜리 단행본이 통째로 표적에서 사라진다.
    거짓 폐기는 **논문을 잃는다** — 그러니 값이 있으면 대장보다 DB 를 믿는다.
    """
    out: dict[str, dict] = {}
    if not VERDICTS.exists():
        return out
    _rows = db_rows_by_full_title()
    out["__by_path__"] = {}  # 경로 축 — 제목보다 정확하다
    for ln in VERDICTS.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        try:
            r = json.loads(ln)
        except json.JSONDecodeError:
            continue
        t = r.get("title")
        if not t:
            continue
        # 가드도 **전체 제목**으로 본다 — 느슨한 조회를 쓰면 자매논문의 정당한 폐기까지 무시한다.
        if _rows.get(norm_full(t), 0) > 2:
            print(f"  ⚠ 대장 무시 — **{t[:56]}** 에 DB 값 {_rows[norm_full(t)]}행이 있다. "
                  f"자매논문·사이드카를 본 논문 제목으로 적은 것이 아닌지 확인해라.",
                  file=sys.stderr)
            continue
        out[norm_full(t)] = r
        # **경로가 있으면 그것으로도 건다.** 배치가 제목을 줄여 적으면 제목 축은 안 맞는다 —
        # 37차에 21건 중 5건이 그랬다(`Nahill - 1967` 처럼 부제를 통째로 뺀 꼴).
        # 경로는 코퍼스가 정한 식별자라 줄어들지 않는다.
        if pth := r.get("path"):
            out["__by_path__"][str(pth)] = r
        if ct := r.get("corpus_title"):
            out[norm_full(ct)] = r
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="다음 파동 표적 추출 — 기채굴·기폐기를 걸러서")
    ap.add_argument("--min-keys", type=int, default=4, help="합집합 물성키 하한")
    ap.add_argument("--limit", type=int, default=0, help="0이면 전부")
    ap.add_argument("--out", help="JSON 저장 경로")
    a = ap.parse_args()

    idx = build(sqlite3.connect(MT_DB))
    verd = load_verdicts(idx)
    cp = sqlite3.connect(CORPUS)
    rows = cp.execute(
        """select d.path, d.title, max(p.n_keys_union) nk, sum(p.n_num_rows) nr,
                  group_concat(distinct p.key) ks
             from ptab p join doc d on d.rowid = p.doc_id
            group by p.doc_id having nk >= ? order by nk desc, nr desc""",
        (a.min_keys,),
    ).fetchall()

    out, n_mined, n_disc, n_amb = [], 0, 0, 0
    for p, t, nk, nr, ks in rows:
        r = look(idx, path=p, title=t)
        if r and r.get("confidence") != "low" and (r["rows"] > 2 or (r["min_tier"] or 9) <= 2):
            n_mined += 1
            continue
        if verd["__by_path__"].get(p) or verd.get(norm_full(t)):
            n_disc += 1
            continue
        if r and r.get("ambiguous"):
            n_amb += 1
        rk = recite_risk(p)
        out.append({"path": p, "title": t, "nk": nk, "nr": nr, "keys": ks,
                    "prior": r, "ambiguous": bool(r and r.get("ambiguous")),
                    "recite": rk})
    # **재인용 위험이 낮은 것을 먼저 읽는다.** 제외는 절대 하지 않는다 — 목록에는 다 남는다.
    out.sort(key=lambda u: (u["recite"]["score"], u["recite"]["ratio"], -u["nk"], -(u["nr"] or 0)))

    print(f"[코퍼스] 합집합 {a.min_keys}키+ {len(rows)}편", file=sys.stderr)
    print(f"  기채굴 제외 {n_mined}편 · **기폐기 제외 {n_disc}편**(대장 {len(verd)}건)"
          f" → 표적 {len(out)}편", file=sys.stderr)
    if n_amb:
        print(f"  그중 {n_amb}편은 제목 충돌로 **모호** — 반드시 열어서 확인해라", file=sys.stderr)
    phys = [u for u in out if u["recite"]["physics"]]
    if phys:
        print(f"  ✗ **물리 상한 위반 {len(phys)}편** — 등방 포아송비가 0.5 를 넘는다. "
              f"오탐이 없는 확정 신호다(10번: 표 전체를 의심해라):", file=sys.stderr)
        for u in phys[:5]:
            print(f"      nu={u['recite']['physics']} | {os.path.basename(u['path'])[:62]}",
                  file=sys.stderr)
    c2 = sum(1 for u in out if u["recite"]["score"] == 2)
    c1 = sum(1 for u in out if u["recite"]["score"] == 1)
    print(f"  재인용 위험 — 2점 {c2}편(오탐 10%) · 1점 {c1}편 · 0점 {len(out)-c1-c2}편. "
          f"**제외가 아니라 읽는 순서다.** 0점부터 읽어라", file=sys.stderr)

    seen = {norm_full(t) for _, t, *_ in rows} | set(verd["__by_path__"])
    # `not_in_corpus` 는 웹 자료·규격 문서다 — 코퍼스에 없는 게 정상이라 경고하지 않는다.
    stale = [k for k in verd if k != "__by_path__" and k not in seen
             and not verd[k].get("path") and not verd[k].get("not_in_corpus")]
    if stale:
        print(f"  ⚠ 대장 {len(stale)}줄이 코퍼스의 어떤 논문과도 안 맞는다 — "
              f"제목을 줄여 적었거나 오타다. `path` 를 박아라: "
              f"{', '.join(verd[k]['title'][:34] for k in stale[:3])}", file=sys.stderr)

    if a.limit:
        out = out[: a.limit]
    if a.out:
        json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
        print(f"  → {a.out}", file=sys.stderr)
    else:
        for u in out[:30]:
            rk = u["recite"]
            mark = ("⚑" if rk["score"] == 2 else "·") if rk["score"] else " "
            print(f" {mark}{u['nk']}키 {u['nr']:>4}행 재인용{rk['ratio']:>5.0%}"
                  f"{('/Ref' + str(rk['ref_col'])) if rk['ref_col'] else '     '}"
                  f" | {os.path.basename(u['path'])[:64]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
