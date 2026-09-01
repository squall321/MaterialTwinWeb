"""58차 TA — 값을 손에 들고도 못 넣던 키 일곱을 연다(콘칼로리미터 넷은 한 세트다).

값은 이미 확보돼 있고 담을 키만 없었다(브리프 468 — 키 부재는 값 하나가 아니라
갈래 전체를 막는다). **새로 캐지 않았다** — 셋 다 앞 파동의 인계다.

  mechanical.elastic_compliance      [1/Pa]    ← 57차 SC (Park 1997 TABLE I `s33^E` 4행)
  physical.density_model_constant    [1]       ← 47차 IC → 56차 RA (Landesfeind 2019 SI Table S1 9행)
  electrical.arc_resistance          [s]       ← 57차 SD (Roechling Glastic ASTM D 495 2행)
  thermal.time_to_ignition           [s]   ┐
  thermal.heat_release_rate          [W/m^2]├─ 57차 SD (Roechling Glastic UTR ASTM E 1354 5행)
  thermal.heat_of_combustion         [J/kg] │  **다섯 칸이 한 시험의 한 세트라 갈래 전체가 막혀 있었다**
  thermal.smoke_extinction_area      [m^2/kg]┘

**왜 기존 키로는 안 되는가**(브리프 471 — 저자가 부르는 이름이 아니라 정의가 키를 정한다).

① ``elastic_compliance`` 는 ``youngs_modulus`` 의 역수지만 **역수를 취하는 것이 우리 산술이다**
   (브리프 10·469 의 역산 금지). 57차 SC 가 그래서 4행을 통째로 넘겼다.
   위첨자가 값의 정체라(``s^E`` 전기장 일정 · ``s^D`` 전기변위 일정) ``component`` 에 verbatim 으로 박는다.

② ``density_model_constant`` 는 ``physical.density`` 가 아니다. Landesfeind 2019 SI 는 밀도를
   표가 아니라 회귀식으로만 싣고, **임의의 (c,T) 에서 평가하면 그 점을 우리가 고른 것이 된다**
   (브리프 76·184). 형제 ``viscosity_model_constant``·``moisture_diffusion_constant`` 와
   같은 규약이다 — si_unit 1 · ``term``/``unit_of_term``/``set_id``.

③ ``arc_resistance``(ASTM D 495, **초**)와 기존 ``comparative_tracking_index``(IEC 60112, **볼트**)는
   다른 시험이고 차원부터 다르다. 57차 SD 가 *"같은 키에 넣으면 안 된다"* 고 명시해 넘겼다.

④ 콘칼로리미터 넷은 **한 시험의 한 세트**라 낱개로 세우지 않고 축을 공유시켰다
   (``test_standard``·``heat_flux_kw_m2``·``specimen_thickness_m``·``set_id``).
   **열방출률은 키를 둘로 가르지 않았다**(브리프 478) — 최대치와 300 초 시점은 차원이 같고
   파라미터만 다르다. ``statistic``(DB 356행 사용 중) 과 ``time_s``(115행)로 올렸다.
   새 어휘를 만들지 않았다(브리프 419).

**왜 마이그레이션이 필요한가** — 개발 DB 는 부팅 시드가 정의를 넣지만 운영 DB 로 가는 경로는
병합 스크립트뿐이고 그건 값만 더한다. 정의 행이 없으면 그 값들이 "정의 없는 물성키" 로
무결성 검사에 걸린다(a8b9c0d1e2f3 · c0d1e2f3a4b5 · e2f3a4b5c6d7 · f3a4b5c6d7e8 와 같은 이유).

**전제를 두지 않는다**(브리프 482) — 키가 없으면 넣고, 있으면 지나간다.
``property_definition`` 테이블 자체가 없는 아주 오래된 DB 도 그냥 지나간다.

Revision ID: a7b8c9d0e1f2
Revises: e6f7a8b9c0d1
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "a7b8c9d0e1f2"
down_revision = "e6f7a8b9c0d1"
branch_labels = None
depends_on = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
# app/property_taxonomy.py 의 58차 TA 블록과 **같은 내용**이어야 한다.
_DEFS = [
    ("mechanical.elastic_compliance", "mechanical", "탄성 컴플라이언스", "s", "1/Pa", "numeric",
     ["component", "crystal_orientation", "poling", "temperature_k"], "IEEE 176"),
    ("physical.density_model_constant", "physical", "밀도 모델 상수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "solvent_blend", "temperature_range_k",
      "concentration_range_mol_l", "fit_r2", "set_id"], None),
    ("electrical.arc_resistance", "electrical", "내아크성", None, "s", "numeric",
     ["test_standard", "thickness_m", "electrode", "temperature_k"], "ASTM D495"),
    ("thermal.time_to_ignition", "thermal", "착화시간(콘칼로리미터)", "t_ig", "s", "numeric",
     ["test_standard", "heat_flux_kw_m2", "specimen_thickness_m", "set_id"], "ASTM E1354"),
    ("thermal.heat_release_rate", "thermal", "열방출률(콘칼로리미터)", "HRR", "W/m^2", "numeric",
     ["statistic", "time_s", "test_standard", "heat_flux_kw_m2", "specimen_thickness_m", "set_id"],
     "ASTM E1354"),
    ("thermal.heat_of_combustion", "thermal", "유효연소열(콘칼로리미터)", "EHC", "J/kg", "numeric",
     ["test_standard", "heat_flux_kw_m2", "specimen_thickness_m", "set_id"], "ASTM E1354"),
    ("thermal.smoke_extinction_area", "thermal", "평균 연기소멸면적(콘칼로리미터)", "SEA", "m^2/kg",
     "numeric", ["statistic", "test_standard", "heat_flux_kw_m2", "specimen_thickness_m", "set_id"],
     "ASTM E1354"),
]

_KEYS = [d[0] for d in _DEFS]


def _has_table(conn, name: str = "property_definition") -> bool:
    return sa.inspect(conn).has_table(name)


def upgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
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


def downgrade() -> None:
    conn = op.get_bind()
    if not _has_table(conn):
        return
    # **값이 붙은 정의는 지우지 않는다** — 자식 행이 property_key 로 참조하므로
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다(f3a4b5c6d7e8 와 같은 규율).
    has_values = _has_table(conn, "property_value")
    for key in _KEYS:
        if has_values and conn.execute(
                sa.text("select 1 from property_value where property_key=:k limit 1"),
                {"k": key}).fetchone():
            continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
