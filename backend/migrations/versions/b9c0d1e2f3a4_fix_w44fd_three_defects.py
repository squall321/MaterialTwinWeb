"""44차 FD — 44차 FB 가 보고만 하고 안 고친 결함 셋을 고친다.

세 결함 다 **개발 DB 에서 SQL 로 고치면 cae00 에 안 간다** — 병합 스크립트는 값만 더한다.
그래서 b2c3d4e5f6a7(옛 키 이관)과 같은 방식으로 마이그레이션에 담는다.

**① Knoop 값이 Vickers 키에 앉아 있다.**
근거가 verbatim ``Knoop hardness HK 0.1/20 = 515`` 인데 키가 ``mechanical.hardness_vickers`` 였다.
비커스와 누프는 **압흔 형상과 면적 규약이 다른 별개 시험**이고 환산식이 없다 —
이 taxonomy 는 경도를 면적 규약으로 가른다(``hardness_meyer`` · ``hardness_ball_indentation`` 주석).
값은 그대로 두고 키와 단위만 옮긴다(HV → HK, 둘 다 kgf/mm^2 눈금이라 수가 안 바뀐다).

  ⚠ **b2c3d4e5f6a7 의 함정을 여기서도 만난다** — 운영 DB 예행에서 확인했다:
  cae00 계열 DB(alembic 888056f1c5b8)에는 ``mechanical.hardness_knoop`` **정의 행이 없다.**
  이관 대상 키가 없다고 건너뛰면 조용히 아무 일도 안 일어난다. 그래서 **없으면 넣는다.**
  (b2c3d4e5f6a7 처럼 옛 정의를 개명할 수는 없다 — ``hardness_vickers`` 는 다른 재료들이 쓴다.)

  브리프는 재료 156·182 의 3건이라 했는데 **매처를 전 재료에 돌리니 14행이었다**(§158).
  재료 137(색유리 필터)도 같은 배치의 같은 모양이다 — 같은 결함이므로 같이 옮긴다.

**② 파장이 ``thickness`` 조건에 들어가 있다.**
``{"detail": "SCHOTT N-LASF9, nd at 587.6 nm", "thickness": "587.6 nm"}`` — 587.6 nm 는
두께가 아니라 **d선 파장**이다. 광학값에 파장이 없으면 값이 아니라서(무결성 검사 항목)
이 오배치는 조건축 하나를 통째로 비운다.

  매처를 좁게 잡았다 — ``thickness`` 의 수가 ``detail`` 안에서 **``at``/``reference``/``line``
  뒤에 나오는 파장과 같을 때만** 옮긴다. 넓게 잡으면 **진짜 막두께를 파장으로 만든다**
  (재료 113·118·186 의 ``300 nm monolayer`` · ``287 nm film`` 이 실제로 걸렸다).
  좁힌 결과 32행 · 재료 넷(113·137·156·182)이고, 오탐 0 이다.

  ``detail`` 이 진짜 시편두께를 함께 밝히면(``10 mm sample thickness``) 그것도 옮겨 담는다 —
  내부투과율은 두께 없이는 값이 아니다(§328·373).
  이미 ``wavelength_nm`` 이 있는데 다른 두 행(재료 137 의 BG60·BG61)은 **그 값이 틀렸다** —
  노트의 λ50% 차단파장(633·648 nm)을 굴절률 파장으로 구조화한 것이다.
  덮어쓰되 옛 값을 ``wavelength_nm_before_correction`` 에 남긴다.

**③ 재료 77 이 Dragontrail 값 14행을 유통사 전재본으로 들고 있다.**
44차 FA 가 AGC 원본(연구보고 61호)으로 재료 2607 을 새로 세웠다. 재료 77 의 것은
Abrisa Technologies 전재본이고 **비커스가 원본 595 와 어긋난 596** 이다.

  **계보 표시를 골랐다(§456)** — 이관하지 않았다. 근거 셋:
  · 재료 77 은 제품이 아니라 **클래스 재료**다. 같은 재료가 Corning Gorilla 시트(출처 243)
    등 20개 출처의 값을 함께 들고 있어, Dragontrail 블록만 옮겨도 77 은 여전히 혼합이다.
  · 이관하면 2607 에 **같은 측정의 사본**이 7행 생긴다 — §456 이 경고하는 중복 계수다.
  · 지우는 것은 금지다(인쇄된 것을 없애는 것도 원문 훼손이다).
  그래서 **값은 그대로 두고** ``conditions.lineage`` 로 계보를 박고 등급을 tier1 → tier3
  (2차 인용)으로 내린다. 되돌릴 수 있게 ``tier_before_correction`` 을 남긴다.
  비커스 596 행에는 **595 대 596 불일치를 값 자체에 붙인다**(§415).

Revision ID: b9c0d1e2f3a4
Revises: a8b9c0d1e2f3
"""
from __future__ import annotations

import json
import re

import sqlalchemy as sa
from alembic import op

revision = "b9c0d1e2f3a4"
down_revision = "a8b9c0d1e2f3"
branch_labels = None
depends_on = None

_KNOOP = ("mechanical.hardness_knoop", "mechanical", "누프 경도", "HK", "HK", "numeric",
          ["load_kgf"], "ISO 4545")

# `detail` 안에서 이 수가 **파장으로** 불릴 때만 옮긴다.
_WL_CTX = r"(?:\bat\b|\breference\b|\bline\b)[^0-9]{{0,14}}{n}\s*nm|{n}\s*nm\s*(?:reference|line)"
# `detail` 이 진짜 시편두께를 함께 밝히는 꼴 — `10 mm sample thickness` · `1 mm reference thickness`
_TH_MM = re.compile(r"([0-9.]+)\s*mm\s*(?:sample|reference)?\s*thickness", re.I)
_HK_LOAD = re.compile(r"HK\s*([0-9.]+)\s*/\s*([0-9.]+)")

_LINEAGE = ("AGC Dragontrail 제조사 원본표 → Abrisa Technologies 유통사 전재본. "
            "재료 'AGC Dragontrail'(44차 FA 가 AGC 연구보고 61호 원본으로 세웠다)과 "
            "같은 계보다 — 두 재료가 같은 값을 내는 것은 교차확인이 아니다(브리프 456).")


def _load(cond):
    try:
        d = json.loads(cond) if cond else {}
    except (TypeError, ValueError):
        d = {}
    return d if isinstance(d, dict) else {}


def _dump(d):
    return json.dumps(d, ensure_ascii=False)


def _fix_knoop(conn) -> int:
    if not conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": "mechanical.hardness_vickers"}).fetchone():
        return 0
    # **대상 키 정의가 없으면 넣는다** — 없다고 건너뛰면 운영 DB 에서 조용히 무효가 된다.
    if not conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": _KNOOP[0]}).fetchone():
        key, domain, name, symbol, unit, vtype, axes, std = _KNOOP
        conn.execute(sa.text(
            "insert into property_definition "
            "(key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard) "
            "values (:k, :d, :n, :sy, :u, :v, :a, :s)"),
            {"k": key, "d": domain, "n": name, "sy": symbol, "u": unit, "v": vtype,
             "a": json.dumps(axes, ensure_ascii=False), "s": std})
    rows = conn.execute(sa.text(
        "select id, conditions from property_value "
        "where property_key='mechanical.hardness_vickers' "
        "and conditions like '%Knoop hardness%'")).fetchall()
    for pid, cond in rows:
        d = _load(cond)
        d["migrated_from"] = "mechanical.hardness_vickers"
        m = _HK_LOAD.search(str(d.get("detail") or ""))
        if m:
            # 인쇄된 `HK 0.1/20` 표기를 그대로 푼다 — 하중 kgf / 유지시간 s.
            d.setdefault("load_kgf", float(m.group(1)))
            d.setdefault("dwell_s", float(m.group(2)))
        conn.execute(sa.text(
            "update property_value set property_key=:nk, unit='HK', conditions=:c where id=:i"),
            {"nk": _KNOOP[0], "c": _dump(d), "i": pid})
    return len(rows)


def _fix_wavelength(conn) -> int:
    rows = conn.execute(sa.text(
        "select id, conditions from property_value where conditions like '%\"thickness\"%'")).fetchall()
    n = 0
    for pid, cond in rows:
        d = _load(cond)
        th = str(d.get("thickness") or "")
        det = str(d.get("detail") or "")
        m = re.fullmatch(r"\s*([0-9.]+)\s*nm\s*", th)
        if not m or not det:
            continue
        num = m.group(1)
        if not re.search(_WL_CTX.format(n=re.escape(num)), det):
            continue
        old = d.get("wavelength_nm")
        if old is not None and float(old) != float(num):
            d["wavelength_nm_before_correction"] = old
        d["wavelength_nm"] = float(num)
        d.pop("thickness", None)
        d["migrated_from_condition"] = "thickness"
        tm = _TH_MM.search(det)
        if tm and "thickness_mm" not in d:
            d["thickness_mm"] = float(tm.group(1))
        conn.execute(sa.text("update property_value set conditions=:c where id=:i"),
                     {"c": _dump(d), "i": pid})
        n += 1
    return n


def _fix_lineage(conn) -> int:
    src = conn.execute(sa.text(
        "select id from source where url like '%abrisatechnologies%Dragontrail%' "
        "or title like '%Dragontrail%Abrisa%'")).fetchall()
    if not src:
        return 0
    ids = [r[0] for r in src]
    n = 0
    for sid in ids:
        rows = conn.execute(sa.text(
            "select pv.id, pv.conditions, pv.quality_tier, pv.notes, pv.property_key, pv.value_num "
            "from property_value pv join material m on m.id = pv.material_id "
            "where pv.source_id=:s and m.name='Aluminosilicate Cover Glass'"),
            {"s": sid}).fetchall()
        for pid, cond, tier, notes, key, val in rows:
            d = _load(cond)
            if d.get("lineage"):
                continue                      # 멱등 — 이미 표시했다
            d["lineage"] = _LINEAGE
            d["lineage_of_material_name"] = "AGC Dragontrail"
            note = notes or ""
            if tier is not None and tier < 3:
                d["tier_before_correction"] = tier
            if key == "mechanical.hardness_vickers" and val is not None and abs(val - 596.0) < 0.5:
                d["value_conflict"] = "596 (Abrisa 전재본) 대 595 (AGC 원본 연구보고 61호 Table 1)"
                add = ("[44차 FD] **AGC 원본은 595 다** — 이 596 은 Abrisa 유통사 전재본의 값이고 "
                       "제조사 원본(연구보고 61호 Table 1, 재료 'AGC Dragontrail')과 한 자리 어긋난다"
                       "(브리프 415·456). 전재 과정의 오식으로 보이나 인쇄된 것이라 지우지 않았다.")
            else:
                add = ("[44차 FD] Abrisa 유통사 전재본이다 — 제조사 원본(AGC 연구보고 61호)으로 세운 "
                       "재료 'AGC Dragontrail' 과 같은 계보라 두 재료의 일치를 교차확인으로 읽으면 "
                       "안 된다(브리프 456). 2차 인용이므로 tier3 으로 내렸다.")
            if "[44차 FD]" not in note:
                note = (note + " " if note else "") + add
            conn.execute(sa.text(
                "update property_value set conditions=:c, quality_tier=:t, notes=:n where id=:i"),
                {"c": _dump(d), "t": max(tier or 3, 3), "n": note, "i": pid})
            n += 1
    return n


def upgrade() -> None:
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    _fix_knoop(conn)
    _fix_wavelength(conn)
    _fix_lineage(conn)


def downgrade() -> None:
    """표시가 남아 있는 행만 되돌린다 — 새로 들어온 행은 건드리지 않는다."""
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    for pid, cond in conn.execute(sa.text(
            "select id, conditions from property_value where property_key=:k "
            "and conditions like '%\"migrated_from\": \"mechanical.hardness_vickers\"%'"),
            {"k": _KNOOP[0]}).fetchall():
        d = _load(cond)
        d.pop("migrated_from", None)
        conn.execute(sa.text(
            "update property_value set property_key='mechanical.hardness_vickers', "
            "unit='HV', conditions=:c where id=:i"), {"c": _dump(d), "i": pid})
    for pid, cond in conn.execute(sa.text(
            "select id, conditions from property_value "
            "where conditions like '%\"migrated_from_condition\": \"thickness\"%'")).fetchall():
        d = _load(cond)
        wl = d.pop("wavelength_nm", None)
        d.pop("migrated_from_condition", None)
        d.pop("thickness_mm", None)
        old = d.pop("wavelength_nm_before_correction", None)
        if old is not None:
            d["wavelength_nm"] = old
        if wl is not None:
            d["thickness"] = f"{wl:g} nm"
        conn.execute(sa.text("update property_value set conditions=:c where id=:i"),
                     {"c": _dump(d), "i": pid})
    for pid, cond in conn.execute(sa.text(
            "select id, conditions from property_value where conditions like '%\"lineage\"%'")).fetchall():
        d = _load(cond)
        if d.get("lineage_of_material_name") != "AGC Dragontrail":
            continue
        tier = d.pop("tier_before_correction", None)
        for k in ("lineage", "lineage_of_material_name", "value_conflict"):
            d.pop(k, None)
        if tier is None:
            conn.execute(sa.text("update property_value set conditions=:c where id=:i"),
                         {"c": _dump(d), "i": pid})
        else:
            conn.execute(sa.text(
                "update property_value set conditions=:c, quality_tier=:t where id=:i"),
                {"c": _dump(d), "t": tier, "i": pid})
