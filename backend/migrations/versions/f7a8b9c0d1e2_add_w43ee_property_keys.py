"""43차 EE — 값이 손에 있는데 키가 없어 버려졌던 물성 열 가지를 연다.

43차 EB(카메라)·ED(배터리·음향)가 값을 확보하고도 **카탈로그에 키가 없어 버렸다.**
이 마이그레이션은 그 키 열 개의 정의 행을 넣는다.

키를 가른 기준은 전부 브리프 453(**차원이 정한다**)이다. 차원이 같아도 측정량이 다르면
별개 키다 — 이 taxonomy 는 이미 그렇게 되어 있다(``cure_shrinkage`` · ``mold_shrinkage`` ·
``compression_set`` 이 전부 무차원 변형률인데 키가 셋이다).

* ``magnetic.energy_product_max`` (J/m^3) — NdFeB 8등급 x min/typ + 하드페라이트가
  이 키 하나 때문에 통째로 막혀 있었다. 기존 자기 키가 전부 SI 기본단위(T · A/m)라 맞췄다.
* ``mechanical.puncture_strength`` (N) — 시트가 gf 로 인쇄한다. 바늘 끝 면적이 없어
  응력으로 못 간다(브리프 117).
* ``thermal.heat_shrinkage`` (1) — ``thermal.expansion_total`` 은 승온 중의 **가역 팽창**이고
  이쪽은 유지 후 남는 **비가역 치수변화**다. 양수 = 수축.
* ``physical.air_permeability_gurley`` (s) — 부피·압력·면적은 조건축이다.
* ``optical.stress_optical_coefficient`` (1/Pa) — CGS(cm^2/dyne) x10 = Pa^-1.
* ``interface.tensile_adhesion_strength`` (Pa) — ``interface.peel_strength`` 는 **N/m 라
  차원이 다르다**. 저자가 "peel strength" 라 불러도 정의가 sigma = Fmax/S 면 이 키다.
* ``mechanical.lankford_r_value`` (1) — 판재 이방소성(Hill48) 입력.
* ``thermal.dilatometric_softening_point`` (K) — HOYA 카탈로그가 Tg 와 Ts 를 같은 행에
  나란히 인쇄하고 Ts > Tg 가 4유리 전부에서 성립한다. 한 키에 넣으면 그 쌍이 깨진다.
* ``mechanical.abrasion_factor`` (1) — 표준시료 BSC7 = 100 기준 상대값.
* ``mechanical.hardness_ball_indentation`` (Pa) — 경도는 **면적 규약으로** 가른다
  (Meyer 투영 · Martens 접촉표면 · H_IT 투영접촉). ISO 2039-1 은 구면 자국의 곡면적이다.

**왜 마이그레이션이 필요한가** — 개발 DB 는 부팅 시드(``seed_property_definitions``)가
새 정의를 넣지만, 운영(cae00) DB 로 가는 경로는 병합 스크립트뿐이고 그건 **값만 더한다.**
정의 행이 없으면 그 값들이 "정의 없는 물성키" 로 무결성 검사에 걸린다.

**b2c3d4e5f6a7 이 겪은 함정** — 마이그레이션이 *다른* 행의 존재를 전제하면 운영 DB 에서
조용히 건너뛴다. 여기서는 전제를 두지 않는다: 키가 없으면 넣고, 있으면 지나간다.
``property_definition`` 테이블 자체가 없는 아주 오래된 DB 도 그냥 지나간다.

Revision ID: f7a8b9c0d1e2
Revises: e5f6a7b8c9d0
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "f7a8b9c0d1e2"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None

# (key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard)
# app/property_taxonomy.py 의 43차 EE 블록과 **같은 내용**이어야 한다.
_DEFS = [
    ("magnetic.energy_product_max", "magnetic", "최대자기에너지적 (BH)max", "(BH)max", "J/m^3",
     "numeric", ["temperature_k", "value_type", "grade"], "IEC 60404-5"),
    ("mechanical.puncture_strength", "mechanical", "관통강도", None, "N", "numeric",
     ["thickness_um", "probe", "test_speed_mm_min", "value_type", "test_standard"], None),
    ("thermal.heat_shrinkage", "thermal", "열수축률", None, "1", "numeric",
     ["temperature_k", "time_s", "direction", "value_type"], None),
    ("physical.air_permeability_gurley", "physical", "걸리 투기도", None, "s", "numeric",
     ["air_volume_cm3", "pressure_pa", "test_area_mm2", "test_standard"], "JIS P8117"),
    ("optical.stress_optical_coefficient", "optical", "광탄성계수(응력광학계수)", "C", "1/Pa",
     "numeric", ["wavelength_m", "temperature_k"], None),
    ("interface.tensile_adhesion_strength", "interface", "직각인장 접착강도(풀오프)", None, "Pa",
     "numeric", ["adherend", "substrate", "test_method", "temperature_k"], "ASTM D4541"),
    ("mechanical.lankford_r_value", "mechanical", "Lankford r값(소성변형비)", "r", "1", "numeric",
     ["direction", "strain_level", "temperature_k"], "ISO 10113"),
    ("thermal.dilatometric_softening_point", "thermal", "팽창계 연화점(새그온도 Ts)", "Ts", "K",
     "numeric", ["heating_rate_k_min", "test_standard"], "ISO 7884-8"),
    ("mechanical.abrasion_factor", "mechanical", "연마도 FA(BSC7=100 기준)", "FA", "1", "numeric",
     ["reference_specimen", "test_standard"], "JOGIS 10"),
    ("mechanical.hardness_ball_indentation", "mechanical", "볼압입경도 H", "H", "Pa", "numeric",
     ["load_n", "dwell_s", "temperature_k"], "ISO 2039-1"),
]

_KEYS = [d[0] for d in _DEFS]


def _has_table(conn) -> bool:
    return sa.inspect(conn).has_table("property_definition")


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
    # **값이 붙은 정의는 지우지 않는다** — 자식 행이 property_key 로 참조하므로
    # 지우면 "정의 없는 물성키" 가 생긴다. 빈 정의만 되돌린다.
    conn = op.get_bind()
    if not _has_table(conn):
        return
    for key in _KEYS:
        if conn.execute(sa.text("select 1 from property_value where property_key=:k limit 1"),
                        {"k": key}).fetchone():
            continue
        conn.execute(sa.text("delete from property_definition where key=:k"), {"k": key})
