"""47차 ID — 45·46차가 값을 손에 들고도 못 넣은 키 넷을 연다(+ 압축탄성계수 4행 이관).

값은 이미 확보돼 있고 담을 키만 없었다(브리프 468 — 키 부재는 값 하나가 아니라
갈래 전체를 막는다). **새로 캐지 않았다.**

  mechanical.monotonic_strain_hardening_exponent  [1]   ← 46차 HA (Hohlfelder 2001 TABLE I `n`)
  mechanical.plastic_strain_at_break              [1]   ← 46차 HA (같은 표 `e pl`)
  mechanical.compressive_modulus                  [Pa]  ← 46차 HC (Torlon 4301) + DB 발굴 2건
  mechanical.tensile_stress_at_strain             [Pa]  ← 46차 HC (Kraton 300 % 모듈러스)

**왜 기존 키로는 안 되는가 — 넷 다 정의가 다르다**(브리프 471 · 453).

① ``cyclic_strain_hardening_exponent`` 는 **안정화 히스테리시스 루프**의 Ramberg-Osgood n′
   (Δσ = A·Δεp^β)이고, 새 키는 **단조 인장곡선**의 멱함수 지수(σ = K·εp^n)다.
   정의식도 하중이력도 다르다. DB 실측 — 기존 24 행이 **전부** ``model: cyclic_stress_strain``.
   원문이 식을 인쇄하지 않으므로 ``model_form`` 에 저자 문장을 verbatim 으로 박는다(브리프 66).

② ``elongation_at_break`` 는 **총 연신**(탄성 + 소성)이고 새 키는 **소성분만**이다.
   원문 자신의 산술이 그것을 보인다 — Zymet 65 MPa/4 GPa = 1.63 % + 1.5 % = 3.13 %,
   Dexter 51/2 = 2.55 % + 0.5 % = 3.05 %, 둘 다 본문 *"brittle fracture at strains of
   approximately 3-4%"* 안에 든다. **탄성분이 소성분보다 크므로** 총 연신 키에 부으면
   Dexter 가 실제 파단변형의 1/6 로 앉는다.

③ ``youngs_modulus`` 는 ASTM E111 · D638 **인장** 이다. 압축은 강도·항복이 이미
   ``compressive_strength`` · ``compressive_yield_strength`` 로 갈려 있는데 **모듈러스만**
   빠져 있었다(46차 HA 의 율속 갈래와 같은 비대칭). 값이 실제로 갈린다 —
   Torlon 4301 인장 6830 / 굽힘 6890 / **압축 5310 MPa**, Rogers CLTE-AT 인장 1790 / **압축 1682**.

④ ``300% 모듈러스`` 는 이름과 달리 **모듈러스가 아니라 300 % 신장 시점의 응력**이라 Pa 다.
   ``youngs_modulus`` 도 ``tensile_strength``(파단점)도 아니다 — SBC 는 파단연신이 1,100 % 라
   두 값이 한 자릿수 벌어진다(0.69~4 MPa 대 21~26 MPa).
   **이름에 ``300`` 을 박지 않았다**(브리프 478) — 차원이 같고 파라미터만 다르니
   변형률을 조건축 ``strain_pct`` 로 올린다. 축 이름은 새로 만들지 않았다(DB 실측 172 행 사용 중).

**곁딸린 이관 — 압축탄성계수 4행**(브리프 162 · 480 · 89).
재료 435(Sandia EPON828/D230/30vol% alumina)의 4행이 ``mechanical.youngs_modulus`` 에
앉아 있는데, 그 배치가 노트에 **"문서가 인쇄한 라벨은 Compressive Modulus이며 인장 측정이
아니다 — taxonomy에 압축탄성률 키가 없어 youngs_modulus에 담았다"** 라고 적어 뒀다.
그 노트는 키가 열리는 순간 늙는다(브리프 89).

  **매처는 좁게 잡았다**(브리프 480 — 넓히면 진짜 값을 죽인다). 셋을 다 만족하는 행만 옮긴다:
  ``property_key = youngs_modulus`` · ``conditions.loading_mode == 'compression'`` ·
  ``notes`` 에 ``Compressive modulus``/``압축탄성률``. 전 재료 실측 결과 **4행 · 오탐 0**.

  ⚠ **폼·엘라스토머 37행은 옮기지 않았다.** ``conditions.loading`` 에 compression 이 적힌
  ``youngs_modulus`` 는 전 재료에 42행 있는데(재료 54·384·385·387~390·392·393·237·267·67),
  그쪽은 **원문이 ``Young's modulus``·``탄성계수``·구성모델 ``E`` 로 인쇄**하고 인장 대응값이
  아예 없다. 옮기면 그 재료들이 DYNA 카드(``dyna_export.K_E``)에서 E 를 통째로 잃는다.
  검토하고 남긴 둘을 특정해 둔다 — pv7071(ISODAMP C-1002, CLD 에서 우리가 계산한 10 % 시컨트)
  · pv20220(실리콘 폼, **다른 논문**의 접선계수를 빌린 tier4 가정값). 둘 다 원문이
  ``Compressive Modulus`` 라고 인쇄한 것이 아니다.

**왜 마이그레이션이 필요한가** — 개발 DB 는 부팅 시드가 정의를 넣지만 운영 DB 로 가는
경로는 병합 스크립트뿐이고 그건 값만 더한다. 정의 행이 없으면 그 값들이
"정의 없는 물성키" 로 무결성 검사에 걸린다(a8b9c0d1e2f3 · c0d1e2f3a4b5 · e2f3a4b5c6d7 와 같은 이유).

**전제를 두지 않는다**(b2c3d4e5f6a7 · 브리프 482) — 키가 없으면 넣고, 있으면 지나간다.
``property_definition`` 테이블 자체가 없는 아주 오래된 DB 도 그냥 지나간다.
예행은 옛 리비전 운영 DB 사본(``888056f1c5b8``)과 현재 운영 DB 사본(``e2f3a4b5c6d7``)
**둘 다**로 했다 — head 를 전제하지 않는다(브리프 482).

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
"""
from __future__ import annotations

import json
import re

import sqlalchemy as sa
from alembic import op

revision = "f3a4b5c6d7e8"
down_revision = "e2f3a4b5c6d7"
branch_labels = None
depends_on = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
# app/property_taxonomy.py 의 47차 ID 블록과 **같은 내용**이어야 한다.
_DEFS = [
    ("mechanical.monotonic_strain_hardening_exponent", "mechanical", "단조 변형경화지수", "n",
     "1", "numeric",
     ["model_form", "temperature_k", "strain_rate_s", "specimen_basis", "test_standard"], None),
    ("mechanical.plastic_strain_at_break", "mechanical", "소성 파단변형률", "eps_pl",
     "1", "numeric", ["temperature_k", "test_standard", "specimen"], None),
    ("mechanical.compressive_modulus", "mechanical", "압축탄성계수", "Ec", "Pa", "numeric",
     ["test_standard", "temperature_k", "strain_rate_s", "direction"], "ASTM D695"),
    ("mechanical.tensile_stress_at_strain", "mechanical", "지정 변형률에서의 인장응력", None,
     "Pa", "numeric", ["strain_pct", "test_standard", "specimen", "temperature_k"], "ASTM D412"),
]

_KEYS = [d[0] for d in _DEFS]

_SRC_KEY = "mechanical.youngs_modulus"
_DST_KEY = "mechanical.compressive_modulus"
_LABEL_RX = re.compile(r"compressive modulus|압축탄성률", re.I)


def _has_table(conn, name: str = "property_definition") -> bool:
    return sa.inspect(conn).has_table(name)


def _seed_defs(conn) -> None:
    for key, domain, name, symbol, unit, vtype, axes, std in _DEFS:
        if conn.execute(sa.text("select 1 from property_definition where key=:k"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text(
            "insert into property_definition "
            "(key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard) "
            "values (:k, :d, :n, :sy, :u, :v, :a, :s)"),
            {"k": key, "d": domain, "n": name, "sy": symbol, "u": unit, "v": vtype,
             "a": json.dumps(axes, ensure_ascii=False) if axes else None, "s": std})


def _matches(conditions: str | None, notes: str | None) -> bool:
    """이관 대상 지문 — 셋을 **다** 만족해야 한다(브리프 480 의 좁힌 매처)."""
    try:
        cond = json.loads(conditions or "{}")
    except Exception:
        return False
    if not isinstance(cond, dict):
        return False
    if str(cond.get("loading_mode", "")).strip().lower() != "compression":
        return False
    return bool(_LABEL_RX.search(notes or ""))


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
    _seed_defs(conn)

    if not _has_table(conn, "property_value"):
        return
    rows = conn.execute(sa.text(
        "select id, conditions, notes from property_value where property_key=:k"),
        {"k": _SRC_KEY}).fetchall()
    for rid, conditions, notes in rows:
        if not _matches(conditions, notes):
            continue
        try:
            cond = json.loads(conditions or "{}")
        except Exception:
            cond = {}
        cond["migrated_from"] = _SRC_KEY
        conn.execute(sa.text(
            "update property_value set property_key=:dst, conditions=:c where id=:i"),
            {"dst": _DST_KEY, "c": json.dumps(cond, ensure_ascii=False), "i": rid})


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
    # 이관을 되돌린다 — `migrated_from` 이 붙은 행만.
    if _has_table(conn, "property_value"):
        rows = conn.execute(sa.text(
            "select id, conditions from property_value where property_key=:k"),
            {"k": _DST_KEY}).fetchall()
        for rid, conditions in rows:
            try:
                cond = json.loads(conditions or "{}")
            except Exception:
                continue
            if cond.pop("migrated_from", None) != _SRC_KEY:
                continue
            conn.execute(sa.text(
                "update property_value set property_key=:src, conditions=:c where id=:i"),
                {"src": _SRC_KEY, "c": json.dumps(cond, ensure_ascii=False), "i": rid})
    # **값이 붙은 정의는 지우지 않는다** — 자식 행이 property_key 로 참조하므로
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다(e2f3a4b5c6d7 와 같은 규율).
    for key in _KEYS:
        if conn.execute(sa.text("select 1 from property_value where property_key=:k limit 1"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
