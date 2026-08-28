"""49차 KC — 46차 HC 가 판정한 2290 `Carbon Steel 45` 의 Basquin 세트를 36 `S45C_medium_carbon` 으로 옮기고, 2290 에 묘비를 세운다.

48차 JA 가 §523 으로 낸 묘비 규약을 실행한다. **재료는 지우지 않는다** — 이름·출처·attributes 가
남아야 다음 파동이 "이건 이미 옮겼다" 를 안다(§435 가 자동 병합을 금지한 이유와 같다).

## 인계 검증(§479 — 인계는 언제나 검증 대상이다)

HC 가 2290·36 의 `attributes` 에 남긴 계획을 원문과 DB 로 다시 쟀다. **넷 다 맞다.**

| HC 의 주장 | 검증 |
|---|---|
| 강 45 = JIS S45C = AISI 1045 | 36 이 **이미 `45钢`(45 강) 논문을 출처로 갖고 있다**(source 2911, JC 상수 5 + 율속 항복 23행). 36 의 다른 출처도 `MakeItFrom: SAE-AISI 1045 (S45C)`·`Otai: S45C / AISI 1045`·`JIS G4051 S45C = SAE-AISI 1045` 다 |
| 겹침 2/2 (45차 GD 의 "겹침 0" 이 틀렸다) | 맞다. 36 은 `fatigue_strength_coefficient` 1077 MPa · `fatigue_strength_exponent` −0.1077 을 SAE FD&E 출처로 갖고 있다 |
| 그래도 모순이 아니다 — 열처리가 갈린다 | Kwofie 원문 verbatim: *"the carbon steel 45 [26] **was quenched and tempered**"*. 36 의 세트는 출처 제목이 `SAE1045 **Normalized, BHN=187**` 이다. **두 세트는 `set_id` 로 공존해야 한다** |
| 상수가 Kwofie 자신의 측정이 아니다 | 원문 [26] = *Yang Xianjie, Int J Fatigue 2005;27:1124-32*. §359 의 가운데 부류다 — 폐기하지 않되 `conditions.data_provenance` 가 함께 가야 한다(이미 들어 있다) |

HC 의 계획 ②(*"병합기 자연키에 conditions 를 반드시 포함해야 한다"*)는 **이미 만족한다** —
`_materialtwin_merge.PLAN` 의 `property_value` 자연키가 `conditions` 를 담고 있다. 손댈 것이 없다.

## 왜 마이그레이션인가 — 적재기에 `moves` 선언 경로를 만들지 않았다

§455 는 *"검사기로 잡을 것을 적재기로 막아라"* 인데, **여기서는 반대 방향이 맞다.**

- **확정된 이동 대상이 지금 하나뿐이다.** DB 전수로 `merge_*`·`same_alloy_*` 를 세면 이동
  후보가 여덟인데(2290 외에 618·619→756, 1754·1755→1753, 1786·1787·1788→1785),
  **일곱은 45차 GD 의 제안이지 판정이 아니다**(전부 `core_verdict_axis` 에
  *"병합은 별도 배치"* 라 적혀 있다). §435 가 자동 병합을 금지했으므로 그 일곱은
  각각 원문 판정이 먼저다 — 경로가 있어도 못 돈다.
- **이동은 배치가 반복해서 만드는 결함이 아니라 드문 큐레이션 행위다.** 정정 경로(§521)는
  한 파동에 세 번 걸려서 열었다. 이동은 지금까지 **0 번** 실행됐다.
- **경로에 반드시 박아야 하는 것은 따로 있다** — 검사기(다음 파동이 묘비를 오독하지 않게)와
  **병합기**(이동이 운영까지 가게). 그 둘은 이 커밋에서 같이 고쳤다. 선언 형식은
  대상이 둘째로 생길 때 만들면 된다.

## 규약을 §523 에서 한 군데 고쳤다 — **`merge_moved_to` 에 id 를 적으면 안 된다**

§523 은 `"merge_moved_to": 36` 처럼 **재료 id** 를 제안했다. **그러면 운영에서 엉뚱한 재료를 가리킨다.**
`_materialtwin_merge.py` 머리말 그대로 *"id 는 정수 autoincrement 라 dev/cae00 에서 같은 id 가
다른 행일 수 있다"* 이고, `merge_` 접두어는 큐레이션이라 **dev 값이 운영에 그대로 덮인다.**
즉 dev 의 `36` 이 운영의 재료 36(전혀 다른 재료)으로 전파된다.

→ **값은 재료 이름**을 적는다. 이름이 병합기의 재료 자연키이고, 두 DB 를 잇는 유일한 축이다.
검사기는 정수가 들어오면 **그 자체를 위반으로 잡는다.**

## 무엇을 옮기는가 — id 가 아니라 이름으로 건다(§466·480)

옛 리비전 운영 DB 에는 재료 2290 이 없고 **id 36 은 다른 재료일 수 있다.** 그래서 두 재료를
**이름으로** 찾고, 하나라도 없으면 아무 것도 하지 않는다.

  `Carbon Steel 45 (Kwofie 2007 zero-mean-stress Basquin fit)` 의 **모든** 물성값
  → `S45C_medium_carbon Bilinear`

`conditions` 는 **글자 그대로 보존한다**(set_id · model_form · data_provenance ·
mean_stress_sensitivity_factor_k · control_mode). 되돌리기 표시 두 칸만 뒤에 덧붙인다 —
`moved_from_material`(옛 재료 **이름**) · `move_reason`. 실측으로 기존 두 행의
`json.dumps(..., ensure_ascii=False)` 왕복이 원문과 바이트까지 같음을 확인했다.

## 알고 옮긴다 — **이 이동은 36 의 대표값을 뒤집는다**

`catalog_compare._rep_rank` 는 등급이 같으면 **상온 거리**로 고른다. 옮겨 온 두 행은
`temperature_k: 298.15`(23 °C 에서 2.0)를 달고 있고 36 의 SAE 세트는 온도 조건이 없어
미기재 벌점 5.0 을 받는다. 그래서 이동 뒤 36 의 대표 Basquin 상수가

  σ'f  1077 MPa (SAE FD&E, normalized BHN187, 20 점 실측)
    → 805.5 MPa (Kwofie 가 **남의** S-N 자료를 회귀한 값, quenched and tempered)
  b    −0.1077 → −0.0749

로 바뀐다. **값이 틀려서가 아니라 한쪽이 온도를 적었기 때문에** 갈린다 — §462·512 와 같은 부류다.
카드 추출에는 영향이 없다(Basquin 상수는 `dyna_export` 의 키 목록에 없다). 비교·Ashby·
`search_by_property` 에서만 보인다. **숨기지 않고 브리프에 남긴다** — 조건을 지어내
순위를 되돌리는 것이 더 큰 조작이다(원문 Kwofie 는 `room temperature` 라고만 쓴다).

Revision ID: b6c7d8e9f0a1
Revises: a5b6c7d8e9f0
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "b6c7d8e9f0a1"
down_revision = "a5b6c7d8e9f0"
branch_labels = None
depends_on = None

SRC_NAME = "Carbon Steel 45 (Kwofie 2007 zero-mean-stress Basquin fit)"
DST_NAME = "S45C_medium_carbon Bilinear"
_MARK = "[49차 KC]"
MOVED_AT = "2026-08-28"

# 조건에 남기는 이동 표시. **병합기가 운영행을 찾는 열쇠이기도 하다**(§522 의 정정 표시와 같은 역할).
MOVE_FROM = "moved_from_material"
MOVE_REASON = "move_reason"

_REASON = (
    "강 45(GB 45钢 / GOST Сталь 45, 0.42~0.50 %C) = JIS S45C = AISI/SAE 1045 로 같은 합금이라 "
    "46차 HC 판정에 따라 " + DST_NAME + " 로 옮겼다. 원자료는 Kwofie 2007 Fig.4 이고 "
    "S-N 원자료 출처는 Yang Xianjie, Int J Fatigue 2005;27:1124-32 다(§359 가운데 부류). "
    "열처리가 quenched and tempered 라 대상 재료의 SAE FD&E normalized BHN=187 세트와 "
    "**set_id 로 공존한다** — 어느 쪽도 지우지 않는다.")

_TOMB_REASON = (
    "[49차 KC] 이 재료의 값을 전부 '" + DST_NAME + "' 로 옮겼다. 같은 합금이다 — "
    "강 45 = GB 45钢 = JIS S45C = AISI/SAE 1045(0.42~0.50 %C). 대상 재료가 이미 "
    "'45钢 동적 소성 구성모델' 논문과 'MakeItFrom: SAE-AISI 1045 (S45C)' 를 출처로 갖고 있어 "
    "그 합금의 집이 거기다. **재료를 지우지 않는 이유** — 이름·출처·판정이 남아야 다음 파동이 "
    "'이건 이미 옮겼다' 를 안다(§435·523). 값의 계보는 conditions.moved_from_material 로 따라간다.")


def _load(cond) -> dict:
    try:
        d = json.loads(cond) if cond else {}
    except (TypeError, ValueError):
        d = {}
    return d if isinstance(d, dict) else {}


def _dump(d) -> str:
    return json.dumps(d, ensure_ascii=False)


def _material(conn, name):
    """이름으로 재료 한 행을 찾는다 — **id 로 걸면 옛 리비전 운영 DB 에서 엉뚱한 재료를 잡는다.**"""
    return conn.execute(sa.text("select id, attributes from material where name=:n"),
                        {"n": name}).fetchone()


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if not insp.has_table("material") or not insp.has_table("property_value"):
        return
    src = _material(conn, SRC_NAME)
    dst = _material(conn, DST_NAME)
    if not src or not dst:
        return                      # 옛 리비전 운영 DB — 옮길 재료가 아직 없다
    attrs = _load(src[1])
    if attrs.get("merge_verdict") == "moved":
        return                      # 멱등 — 이미 묘비가 서 있다

    rows = conn.execute(sa.text(
        "select id, property_key, conditions, notes from property_value where material_id=:m"),
        {"m": src[0]}).fetchall()
    keys = sorted({r[1] for r in rows})
    for pid, _key, cond, notes in rows:
        d = _load(cond)
        # **기존 칸은 순서까지 그대로 두고 표시 둘만 뒤에 붙인다** — 되돌리면 원문과 바이트가 같다.
        d[MOVE_FROM] = SRC_NAME
        d[MOVE_REASON] = _REASON
        conn.execute(sa.text(
            "update property_value set material_id=:m, conditions=:c, notes=:n where id=:i"),
            {"m": dst[0], "c": _dump(d), "i": pid,
             "n": (notes or "") + f"\n{_MARK} 재료 '{SRC_NAME}' 에서 옮겨 왔다 — 같은 합금이다. "
                  f"옛 재료에는 묘비(attributes.merge_verdict='moved')가 서 있고 지우지 않았다."})

    # 2290 의 `merge_verdict` 에는 HC 가 **산문**을 적어 뒀다(왜 보류했는지). 규약이 그 칸을
    # 판정어(`moved`)로 쓰므로 산문을 잃지 않게 옮겨 둔다 — §521 의 `*_before_correction` 과 같은 규율.
    if attrs.get("merge_verdict"):
        attrs["merge_verdict_before_move"] = attrs["merge_verdict"]
    attrs["merge_verdict"] = "moved"
    # **id 가 아니라 이름이다** — id 는 dev/운영에서 다른 행을 가리킨다(docstring 참조).
    attrs["merge_moved_to"] = DST_NAME
    attrs["merge_moved_keys"] = keys
    attrs["merge_reason"] = _TOMB_REASON
    attrs["merge_moved_at"] = MOVED_AT
    conn.execute(sa.text("update material set attributes=:a where id=:i"),
                 {"a": _dump(attrs), "i": src[0]})


def downgrade() -> None:
    """표시가 남아 있는 행만 되돌린다 — **행을 지우지 않는다.**"""
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    src = _material(conn, SRC_NAME)
    if not src:
        return
    for pid, cond, notes in conn.execute(sa.text(
            "select id, conditions, notes from property_value where conditions like :p"),
            {"p": '%"' + MOVE_FROM + '": "' + SRC_NAME + '"%'}).fetchall():
        d = _load(cond)
        d.pop(MOVE_FROM, None)
        d.pop(MOVE_REASON, None)
        conn.execute(sa.text(
            "update property_value set material_id=:m, conditions=:c, notes=:n where id=:i"),
            {"m": src[0], "c": _dump(d), "i": pid,
             "n": (notes or "").split(f"\n{_MARK}")[0] or None})
    attrs = _load(src[1])
    for k in ("merge_moved_to", "merge_moved_keys", "merge_reason", "merge_moved_at"):
        attrs.pop(k, None)
    # 판정어로 덮기 전의 산문을 **제자리에** 되돌린다(dict 는 기존 키의 순서를 지킨다).
    prose = attrs.pop("merge_verdict_before_move", None)
    if prose is None:
        attrs.pop("merge_verdict", None)
    else:
        attrs["merge_verdict"] = prose
    conn.execute(sa.text("update material set attributes=:a where id=:i"),
                 {"a": _dump(attrs), "i": src[0]})
