"""63차 YC — NASA RP-1121 의 `ε_n` 5행을 `optical.emissivity_spectral` 에서 `optical.emissivity_total` 로 옮긴다.

62차 XB 가 신고했다 — *"NASA RP-1121 의 `ε_n` 열을 52차 NA 가 `optical.emissivity_spectral` 에
넣었다(5행). 이름이 **normal emittance** 라 '분광' 으로 읽힌 것이다."* 원문을 직접 열어 확인했다.

## 원문이 반대를 말한다 (`NASA_RP-1121_Henninger_1984_…pdf`, `pdftotext -layout`)

`DESCRIPTION OF MEASUREMENTS` 절 `Normal Emittance (ε_n)` 이 그대로 정의한다.

> verbatim `Spectral reflectance measurements were made over the wavelength region from 5 to 35
> micrometers. This region contains approximately 90 percent of the energy of a 300 K blackbody radiator`
> verbatim `The following formulas are used for computing **total normal emittance**, ε_n (reference 4):`
> 적분식은 `∫(5..35 µm) ρ_λ(λ) J_λ(T) dλ / ∫(5..35 µm) J_λ(T) dλ` 이고
> 기호표가 `ε_n (T) = **Total normal emittance** at T` 라고 못박는다 — **파장이 적분으로 사라진다.**
> `INSTRUMENTATION` 절 verbatim `The Gier-Dunkle portable emissometer, model DB-100 …
> **gives a single integrated value of emittance**.`

**가른 것은 우리 DB 자신이다**(62차 XB 의 규율) — `property_definition` 이
`optical.emissivity_total` 의 `test_standard` 로 **ASTM E408**(*Total Normal Emittance of Surfaces
Using Inspection-Meter Techniques*)을 적어 두었고, DB-100 inspection emissometer 가 정확히 그 규격의
기기다. 반대로 `optical.emissivity_spectral` 의 선언된 조건축은 `["wavelength_nm","temperature_k"]`
인데 **이 5행에는 파장 축이 한 칸도 없다** — 대신 `band_um: "5-35"` 라는 적분 대역이 들어 있다.
축이 없다는 사실 자체가 이 행들이 분광값이 아니라는 구조적 증거다.

값도 원문과 글자까지 대조했다(표 이름 · 행 라벨 · ε_n 열).

| 재료 | 원문 표 · 행 | ε_n |
|---|---|---|
| 194 Kapton HN | `FILMS AND TAPES` · `Kapton Film (Aluminum Backing)` `1.0 mil` | 0.67 |
| 151 Anodized Al | `ANODIZED ALUMINUM SAMPLES` · `Sulphuric` | 0.87 |
| 179 Beryllium Copper | `METALS AND CONVERSION COATINGS` · `Plain Beryllium Copper` | 0.03 |
| 41 Tungsten | 같은 표 · `Tungsten Polished` | 0.03 |
| 3 SUS304 | 같은 표 `Stainless Steel` 블록 · `1-mil 304 Foil` | 0.05 |

## 무엇을 바꾸고 무엇을 안 바꾸나

**이동은 삭제가 아니다**(§565·594). `property_key` 하나만 옮기고 **값·단위·등급·`method`·출처는
한 칸도 안 건드린다.** 되돌리기 표시로 `conditions.migrated_from` 에 옛 키를 남긴다
(47차 IA `a4b5c6d7e8f9` 가 세운 규약과 같은 모양이다).

**조건은 어떻게 하나** — `emissivity_spectral` 은 파장이 필수 축이지만 `emissivity_total` 의
축은 `temperature_k` 다. 다섯 행 전부 `temperature_k: 300` 을 이미 갖고 있어 옮기면 축이 채워진다.
`band_um: "5-35"` 는 **지우지 않는다** — 그것이 이 값의 정의(적분 대역)이고, 지우면 다음 파동이
"대역 없는 전방사율" 로 읽는다. 대신 `quantity` 를 62차 XB 가 같은 표에서 넣은 행
(`pv43892`·`pv43893`)과 **글자까지 같은 문구**로 붙여 두 행이 같은 물리량임을 드러낸다.

## 중복 한 쌍 — 지우지 않고 표시한다(52차 NB 규약)

62차 XB 가 같은 표의 같은 행(`Plain Beryllium Copper`)을 **옳은 키로 이미 넣었다**(`pv43892`,
재료 179, 0.03). 그래서 이동하면 재료 179 에만 같은 측정이 두 행이 된다.
**지우지 않는다** — `c7d8e9f0a1b2`(52차 NB)의 규약대로 **중복 쪽에만**
`verdict_duplicate_of`(정본의 **원문 조건 지문**) · `verdict_duplicate_note` 를 단다.
`_rep_rank` 다섯째 자리가 조건 수 오름차순이라 중복 쪽에 칸이 늘면 **정본이 자동으로 이긴다** —
표시가 없으면 조건이 성긴 옛 행이 대표로 뽑혀 XB 가 적어 둔 계보를 가린다.

## 이 이동은 운영까지 안 간다 — 병합기에 키 이동 분기가 없다

`_materialtwin_merge.py` 의 `property_value` 자연키에 `property_key` 가 들어 있고,
정정(③)·재료이동(④)·출처병합(⑤) **세 분기 전부가 `property_key IS ?` 로 좁힌다.**
`migrated_from` 을 보는 분기는 없다. 그래서 옮긴 행은 운영에서 대응행을 못 찾고 **새 행으로
들어가며**, 그 뒤 운영에서 이 마이그레이션이 돌아 옛 행까지 옮기면 **두 벌이 된다**(§536 이
재료 이동에서 이미 겪은 그 모양이다). 이 배치는 공유 도구를 안 고친다(§468) — **고칠 자리를
적어 둔다**: `MOVE_MARKER` 옆에 `KEY_MOVE_MARKER = "migrated_from"` 을 두고,
`find_moved_row` 와 같은 모양으로 **옛 키 밑에서** (재료·출처·값)으로 대응행을 찾는 분기 하나면 된다.
그때까지 이 5행은 dev 에서만 옳다.

Revision ID: b3c4d5e6f7a8
Revises: a7b8c9d0e1f2
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "b3c4d5e6f7a8"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None

SRC_KEY = "optical.emissivity_spectral"
DST_KEY = "optical.emissivity_total"
# 출처는 id 가 아니라 **제목 접두어**로 잡는다(§466·480 — id 목록은 지문이 아니다).
SRC_TITLE_PREFIX = "NASA Reference Publication 1121"
# 62차 XB 가 같은 표에서 넣은 행의 문구와 **글자까지 같아야** 두 행이 같은 물리량으로 읽힌다.
QUANTITY = "total normal emittance (Planck-weighted 300 K)"
MARK = "[63차 YC]"
MOVE_MARKER = "migrated_from"
K_DUP_OF = "verdict_duplicate_of"
K_DUP_NOTE = "verdict_duplicate_note"
# 조건 지문에서 뺄 살림살이 칸 — 측정을 가르는 축이 아니다.
_HOUSEKEEPING = ("correction_reason", "corrected_by", "correction_evidence",
                 MOVE_MARKER, K_DUP_OF, K_DUP_NOTE)

NOTE = (
    f"\n{MARK} 키 이동 — {SRC_KEY} → {DST_KEY}. NASA RP-1121 의 `ε_n` 열은 분광 방사율이 아니라 "
    "**전방사율**이다. 정의절 verbatim `The following formulas are used for computing total normal "
    "emittance, e_n` 이고, 적분식이 5~35 um 분광반사율을 300 K Planck 함수로 가중적분해 파장이 "
    "사라진다(`This region contains approximately 90 percent of the energy of a 300 K blackbody "
    "radiator`). 측정기는 Gier-Dunkle DB-100 이고 `gives a single integrated value of emittance` 다 — "
    "그 기기가 곧 property_definition 이 optical.emissivity_total 의 시험규격으로 적어 둔 "
    "ASTM E408(Total Normal Emittance … Inspection-Meter Techniques)의 기기다. "
    "옛 키의 선언된 조건축인 wavelength 가 이 행에 한 칸도 없다는 것도 같은 결론을 가리킨다. "
    "**값·단위·등급·method·출처는 한 칸도 안 바꿨다**(conditions.migrated_from 으로 되돌린다)."
)


def _load(cond):
    try:
        d = json.loads(cond) if cond else {}
    except (TypeError, ValueError):
        d = {}
    return d if isinstance(d, dict) else {}


def _dump(d) -> str:
    return json.dumps(d, ensure_ascii=False)


def _has_wavelength(d) -> bool:
    """분광 축이 실제로 있는가. 있으면 이 행은 이동 대상이 아니다."""
    for k in ("wavelength_nm", "wavelength_um", "wavelength_m", "wavelength"):
        if isinstance(d.get(k), (int, float)) and not isinstance(d.get(k), bool):
            return True
    return False


def _fingerprint(d) -> str:
    """52차 NB 와 같은 모양의 **원문 조건 지문** — 정규화하지 않는다(그러면 정본을 못 가른다)."""
    items = [(k, v) for k, v in sorted(d.items())
             if v is not None and not k.endswith("_before_correction") and k not in _HOUSEKEEPING]
    return " | ".join(f'{k}="{v}"' for k, v in items)


def _targets(conn):
    """이동 지문 셋을 다 만족하는 행 → [(id, material_id, source_id, value_num, cond_dict)].

    ① `optical.emissivity_spectral` 이다
    ② 출처 제목이 `NASA Reference Publication 1121` 로 시작한다
    ③ 조건에 **분광 축이 없고** 적분 대역(`band_um`)이 있다 — 구조가 전방사율이라고 말한다
    """
    rows = conn.execute(sa.text(
        "select v.id, v.material_id, v.source_id, v.value_num, v.conditions "
        "  from property_value v join source s on s.id = v.source_id "
        " where v.property_key = :k and s.title like :t"),
        {"k": SRC_KEY, "t": SRC_TITLE_PREFIX + "%"}).fetchall()
    out = []
    for pid, mid, sid, val, cond in rows:
        d = _load(cond)
        if _has_wavelength(d) or "band_um" not in d:
            continue
        out.append((pid, mid, sid, val, d))
    return out


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if not insp.has_table("property_value") or not insp.has_table("source"):
        return

    for pid, mid, sid, val, d in _targets(conn):
        if d.get(MOVE_MARKER):
            continue                                   # 멱등 — 이미 옮긴 행
        nd = dict(d)
        nd[MOVE_MARKER] = SRC_KEY
        nd.setdefault("quantity", QUANTITY)
        # 옳은 키에 같은 출처·같은 값의 행이 이미 있으면 **중복 쪽에만** 표시를 단다(52차 NB).
        twin = conn.execute(sa.text(
            "select id, conditions from property_value "
            " where material_id = :m and property_key = :k and source_id is :s "
            "   and value_num is :v and id <> :i"),
            {"m": mid, "k": DST_KEY, "s": sid, "v": val, "i": pid}).fetchall()
        if len(twin) == 1:
            nd[K_DUP_OF] = _fingerprint(_load(twin[0][1]))
            nd[K_DUP_NOTE] = (
                f"{MARK} 62차 XB 가 같은 표의 같은 행을 옳은 키로 이미 넣었다 — 이 행은 52차 NA 가 "
                f"{SRC_KEY} 에 넣었던 같은 측정이고 키만 옮겨 왔다. 지우지 않고 중복으로 표시한다"
                "(브리프 565 — 삭제는 dev 에서만 사라진다).")
        conn.execute(sa.text(
            "update property_value set property_key = :nk, conditions = :c, "
            "       notes = coalesce(notes,'') || :n where id = :i"),
            {"nk": DST_KEY, "c": _dump(nd), "n": NOTE, "i": pid})


def downgrade() -> None:
    """표시가 남아 있는 행만 되돌린다 — 새로 들어온 행은 건드리지 않는다."""
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    rows = conn.execute(sa.text(
        "select id, conditions, notes from property_value "
        " where property_key = :k and conditions like :p"),
        {"k": DST_KEY, "p": '%"' + MOVE_MARKER + '": "' + SRC_KEY + '"%'}).fetchall()
    for pid, cond, notes in rows:
        d = _load(cond)
        if d.get(MOVE_MARKER) != SRC_KEY:
            continue
        d.pop(MOVE_MARKER, None)
        d.pop(K_DUP_OF, None)
        d.pop(K_DUP_NOTE, None)
        if d.get("quantity") == QUANTITY:
            d.pop("quantity", None)
        n = (notes or "").split(f"\n{MARK}")[0] or None
        conn.execute(sa.text(
            "update property_value set property_key = :k, conditions = :c, notes = :n where id = :i"),
            {"k": SRC_KEY, "c": _dump(d), "n": n, "i": pid})
