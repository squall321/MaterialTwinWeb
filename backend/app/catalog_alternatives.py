# 대표값 옆에 "다른 후보가 있다" 를 드러내는 주석기 — 목록·비교·Ashby·상세 공용.
#
# 왜 있는가(51차 MB). 선택기는 (재료,물성키)당 한 행만 낸다. 라이브 41,368행에서
# 후보가 둘 이상인 쌍이 6,330개이고, 그중 3,642쌍은 **순위가 완전히 같은데 값이 1% 넘게 다르다**
# (§545). 지금까지 그 사실은 DYNA 카드 주석에만 있었다 — 목록·비교·Ashby·상세는 이긴 값만 냈다.
#
# **순위를 더 만들지 않는다**(§543·544 가 두 후보를 전수로 재고 둘 다 버렸다).
# 대신 진 쪽을 **같이 내보내고 왜 갈렸는지를 적는다** — 어느 쪽을 쓸지는 해석자가 정할 일이다.
#
# `catalog_compare` 의 순위 원시함수를 그대로 쓴다(`_rep_rank`·`_tie_key`·`_differs`).
# 같은 파동에서 다른 배치가 `catalog_compare.py` 를 만지고 있어 그 파일은 건드리지 않았다.
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.catalog_compare import _differs, _rep_rank, _tie_key
from app.models import PropertyValue

# `_rep_rank` 튜플의 자리 이름. 두 후보의 순위가 처음 갈리는 자리가 곧 "왜 졌는가" 다.
# 3번 자리(지배조건)는 물성에 따라 파장이므로 호출부에서 갈라 적는다.
_RANK_CODES = ("state", "tier", "numeric", "temperature", "n_conditions", "load_order")

# 한 키에 여러 항이 사는 물성(Prony·Anand·Garofalo…)의 항 구분 조건.
# 이런 키는 **대표값 자체가 뜻이 없다** — "동률로 임의 선택" 이 아니라 "항이 여럿" 이다(§545).
_TERM_KEYS = frozenset(("term", "prony_term", "term_index", "set_id", "unit_of_term"))

# 대안값을 응답에 몇 개까지 실을지. 비교가 무거워지지 않게 자른다 —
# 12종 비교는 칸이 342개이고 그중 274개에 대안이 붙는다. 총 수는 `n_candidates` 가 말하므로
# 예시는 2건이면 충분하다(상세 화면은 전 행을 그대로 보여준다).
_COMPARE_ALTERNATIVES = 2
_MAX_DIFF_KEYS = 6


def _cond(pv) -> dict:
    c = getattr(pv, "conditions", None)
    return c if isinstance(c, dict) else {}


def rank_group(rows: list) -> list:
    """후보 행들을 대표값 순서로 정렬. 맨 앞이 선택기가 고르는 그 행이다."""
    return sorted(rows, key=_rep_rank)


def _clip(v, n: int | None):
    """긴 조건 문자열을 자른다. 비교 응답이 조건 사본으로 부풀지 않게."""
    if n is None or not isinstance(v, str) or len(v) <= n:
        return v
    return v[: n - 1] + "…"


def condition_diff(rep, alt, limit: int = _MAX_DIFF_KEYS, clip: int | None = None) -> dict:
    """두 후보의 조건 dict 차이. **이것이 "왜 갈렸는가" 의 본체다.**

    라이브 실측 — 동률 3,642쌍 중 3,213쌍(88%)은 조건이 실제로 다르다.
    즉 "적재 순서로 골랐다" 가 아니라 **선택기에 그 축이 없다**(방향·율속·주파수·기준·템퍼…).

    `limit`·`clip` 은 목록성 응답(비교)에서 줄이기 위한 것이다. 상세는 그대로 다 낸다.
    """
    a, b = _cond(rep), _cond(alt)
    keys = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    return {k: {"rep": _clip(a.get(k), clip), "alt": _clip(b.get(k), clip)}
            for k in keys[:limit]}


def separated_by(rep, alt) -> str:
    """순위 튜플이 처음 갈리는 자리 — 그 후보가 진 이유. 안 갈리면 `load_order`."""
    ra, rb = _rep_rank(rep), _rep_rank(alt)
    for i, (x, y) in enumerate(zip(ra, rb)):
        if x != y:
            if i == 3 and str(getattr(rep, "property_key", "") or "").startswith("optical."):
                return "wavelength"
            return _RANK_CODES[i]
    return "load_order"


def _rel_diff(a, b) -> float | None:
    if a is None or b is None:
        return None
    m = max(abs(a), abs(b))
    return abs(a - b) / m if m else 0.0


def tie_info(ranked: list) -> dict | None:
    """대표값과 **순위가 완전히 같은데 값이 다른** 후보가 있으면 그 사실과 갈린 이유.

    `kind` 는 세 갈래다(라이브 실측 3,642쌍).
      · `condition_axis`   3,213 — 조건이 다른데 선택기에 그 축이 없다
      · `multi_term`         394 — 한 키에 여러 항이 산다(§545). 대표값 자체가 뜻이 없다
      · `indistinguishable`   35 — 조건 차이조차 없다. **이때만 "적재 순서로 골랐다" 가 맞는 말이다**

    "동률이면 무조건 적재 순서" 라고 적으면 3,642건 중 3,607건이 틀린 설명이 된다.
    매번 뜨는 같은 경고는 무시하는 법을 가르친다(49차 KA) — 그래서 원인을 이름으로 갈랐다.

    반올림 쌍둥이(7,850 대 7,855)는 `_differs` 가 걸러 세지 않는다.
    """
    if not ranked:
        return None
    head = ranked[0]
    tk = _tie_key(head)
    rivals = [pv for pv in ranked[1:]
              if _tie_key(pv) == tk and _differs(head.value_num, pv.value_num)]
    if not rivals:
        return None
    diff_keys: set = set()
    for pv in rivals:
        diff_keys |= set(condition_diff(head, pv, limit=999))
    if not diff_keys:
        kind = "indistinguishable"
    elif diff_keys <= _TERM_KEYS:
        kind = "multi_term"
    else:
        kind = "condition_axis"
    rels = [r for r in (_rel_diff(head.value_num, pv.value_num) for pv in rivals) if r is not None]
    return {
        "kind": kind,
        "n_tied": len(rivals) + 1,
        "max_rel_diff": max(rels) if rels else None,
        "condition_keys": sorted(diff_keys)[:_MAX_DIFF_KEYS],
    }


def alternative_payload(rep, alt, with_source: bool = False,
                       diff_limit: int = _MAX_DIFF_KEYS, clip: int | None = None) -> dict:
    """진 후보 한 건을 응답에 실을 형태로. 값·등급 + **왜 졌는지**.

    **조건 dict 전체는 안 싣는다 — 대표값과 다른 칸만 싣는다.** 대표행의 조건은 이미 응답에
    있으므로 전체를 다시 실으면 비교 응답이 213 KB → 386 KB(+81%)로 뛴다.
    사용자가 고르는 데 필요한 것은 "무엇이 다른가" 이지 같은 칸의 사본이 아니다.
    """
    out = {
        "value": alt.value_num, "value_text": alt.value_text, "unit": alt.unit,
        "tier": alt.quality_tier, "method": alt.method,
        "separated_by": separated_by(rep, alt),
        "condition_diff": condition_diff(rep, alt, limit=diff_limit, clip=clip),
    }
    if with_source:
        src = alt.source
        out["source_title"] = _clip((src.publisher or src.title) if src else None, clip)
    return out


def index_from_rows(rows: list) -> dict[tuple, dict]:
    """이미 읽어 온 행들로 (재료,키) → {n, ranked, tie} 색인. 추가 질의를 하지 않는다."""
    groups: dict[tuple, list] = defaultdict(list)
    for pv in rows:
        groups[(pv.material_id, pv.property_key)].append(pv)
    out: dict[tuple, dict] = {}
    for k, g in groups.items():
        ranked = rank_group(g)
        out[k] = {"n": len(ranked), "ranked": ranked, "tie": tie_info(ranked)}
    return out


def candidate_index(db: Session, keys: list[str], material_ids: list[int] | None = None,
                    numeric_only: bool = False) -> dict[tuple, dict]:
    """(재료,키) → {n, ranked, tie}. 질의 한 번.

    `numeric_only` 는 호출부의 선택기와 맞춘다 — `representative_numeric`(목록·Ashby)은
    수치행만 후보로 보고, `build_comparison`(비교)·상세는 텍스트행도 후보로 본다.
    (라이브 41,368행에서 두 방식이 고르는 행은 **한 건도 다르지 않다** — 순위 3번째 자리가
    수치 유무라 등급이 같으면 수치행이 먼저다. 그래도 후보 *수* 는 달라지므로 맞춰 센다.)
    """
    if not keys:
        return {}
    stmt = select(PropertyValue).where(PropertyValue.property_key.in_(keys))
    if numeric_only:
        stmt = stmt.where(PropertyValue.value_num.isnot(None))
    if material_ids is not None:
        stmt = stmt.where(PropertyValue.material_id.in_(material_ids))
    return index_from_rows(db.execute(stmt).scalars().all())


def annotate_comparison(db: Session, data: dict) -> dict:
    """`build_comparison` 결과의 각 칸에 후보 수·대안값·동률을 붙인다(제자리 수정).

    비교는 재료 12종 이하라 질의 한 번이면 끝난다. 대안값은 최대 3건까지만 싣는다.
    """
    mids = [m["id"] for m in data.get("materials", [])]
    keys = [p["key"] for dom in data.get("domains", []) for p in dom["properties"]]
    if not mids or not keys:
        return data
    idx = candidate_index(db, sorted(set(keys)), material_ids=mids)
    for dom in data["domains"]:
        for prop in dom["properties"]:
            for cell in prop["cells"]:
                if cell is None:
                    continue
                ent = idx.get((cell["material_id"], prop["key"]))
                # 후보가 하나뿐인 칸에는 아무것도 안 붙인다 — 12종 비교는 칸이 수천 개라
                # `"n_candidates":1` 만 깔아도 응답이 눈에 띄게 무거워진다.
                # 읽는 쪽은 없으면 1개·동률 없음으로 본다.
                if ent is None or ent["n"] <= 1:
                    continue
                ranked = ent["ranked"]
                head = ranked[0]
                cell["n_candidates"] = ent["n"]
                # 값이 실질적으로 같은 후보(반올림 쌍둥이 포함)는 실어도 고를 것이 없다.
                # 감추는 것이 아니다 — 그런 후보도 `n_candidates` 에는 세어져 있고 상세에 다 있다.
                alts = [alt for alt in ranked[1:] if _differs(head.value_num, alt.value_num)]
                if alts:
                    cell["alternatives"] = [
                        alternative_payload(head, alt, with_source=True, diff_limit=3, clip=40)
                        for alt in alts[:_COMPARE_ALTERNATIVES]]
                if ent["tie"]:
                    cell["tie"] = ent["tie"]
    return data


def annotate_ranking(db: Session, rk: dict) -> dict:
    """`property_ranking` 결과의 각 행에 후보 **수와 동률 여부만** 붙인다(제자리 수정).

    이것도 목록이다 — 값까지 실으면 200행 응답이 배로 뛴다. 값은 상세·비교에서 본다.
    """
    rows = rk.get("results") or []
    if not rows:
        return rk
    key = rk["property"]["key"]
    idx = candidate_index(db, [key], material_ids=[r["material_id"] for r in rows],
                          numeric_only=True)
    for r in rows:
        ent = idx.get((r["material_id"], key))
        r["n_candidates"] = ent["n"] if ent else 1
        r["tie"] = bool(ent and ent["tie"])
    return rk


def annotate_scatter(db: Session, data: dict) -> dict:
    """Ashby 점마다 x·y 의 후보 **수와 동률 여부만** 붙인다(제자리 수정).

    점이 수천 개라 값까지 실으면 응답이 배로 뛴다. 값은 상세·비교에서 본다.
    """
    pts = data.get("points") or []
    if not pts:
        return data
    x_key, y_key = data["x"]["key"], data["y"]["key"]
    ids = [p["material_id"] for p in pts]
    idx = candidate_index(db, sorted({x_key, y_key}), material_ids=ids, numeric_only=True)
    # 점이 738개다. 후보 1개·동률 없음이 대다수라 **그럴 때는 아예 안 붙인다** —
    # 전부 붙이면 162 KB 응답이 212 KB 로 뛴다. 읽는 쪽은 없으면 1개·동률 없음으로 본다.
    for p in pts:
        for axis, key in (("x", x_key), ("y", y_key)):
            ent = idx.get((p["material_id"], key))
            if ent is None:
                continue
            if ent["n"] > 1:
                p[f"{axis}_candidates"] = ent["n"]
            if ent["tie"]:
                p[f"{axis}_tie"] = True
    return data
