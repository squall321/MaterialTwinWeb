# 정정이 **운영까지 가는지**를 지킨다 — 병합기(`_materialtwin_merge.py`) 회귀.
#
# 왜 여기 있나. 브리프 464 가 *"병합기는 삽입만 한다"* 를 재료 attributes 에서 잡았는데,
# `property_value` 에는 같은 함정의 더 나쁜 얼굴이 남아 있었다 — 그 표의 자연키가
# `value_num`·`conditions`·`method` 를 포함하는데 **정정이 바꾸는 칸이 바로 그것들**이라,
# 고친 행이 운영에서 대응행을 못 찾고 **새 행으로 들어갔다**. 그러면 운영에는
# 틀린 옛 행과 고친 새 행이 나란히 남는다(48차 JA 예행에서 실제로 그랬다: added 2).
# 병합기는 다른 저장소(HEAXHub)에 있어 그쪽에 테스트가 없다 — 정정 경로를 만든 이 저장소가 지킨다.
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

_MERGER = Path(os.environ.get(
    "MATERIALTWIN_MERGER",
    Path(__file__).resolve().parents[3] / "HEAXHub" / "deploy" / "apptainer"
    / "_materialtwin_merge.py"))
pytestmark = pytest.mark.skipif(not _MERGER.exists(),
                                reason=f"병합기가 없다({_MERGER}) — 배포 저장소가 있어야 돈다")


def _make_db(tmp_path, name):
    """앱 스키마 그대로인 빈 SQLite 를 만든다(병합기는 실제 표 구조를 본다)."""
    import importlib
    os.environ["MATERIALTWIN_DATABASE_URL"] = f"sqlite:///{tmp_path / name}"
    os.environ["MATERIALTWIN_DATA_DIR"] = str(tmp_path / f"d_{name}")
    from app import config as cfg
    cfg.get_settings.cache_clear()
    import app.db as db
    db = importlib.reload(db)
    import app.models
    if app.models.Material.metadata is not db.Base.metadata:
        importlib.reload(app.models)
    db.Base.metadata.create_all(db.engine)
    return tmp_path / name


def _seed(path, *, pv_id, value, method, tier, conditions, filler=0):
    """재료·출처·물성값 한 벌을 넣는다. `filler` 로 id 를 어긋나게 만들 수 있다."""
    import sqlite3
    c = sqlite3.connect(path)
    c.execute("insert into property_definition(key,name,domain,si_unit,value_type) "
              "values('electrical.dielectric_constant','유전율','electrical','1','numeric')")
    c.execute("insert into material(id,name,category,attributes) values(1,'E-Glass','ceramic','{}')")
    c.execute("insert into source(id,kind,title) values(1,'book','어느 핸드북')")
    for i in range(filler):        # 운영 id 를 dev 와 어긋나게 하는 더미
        c.execute("insert into property_value(material_id,property_key,value_num,unit,method,"
                  "quality_tier,source_id) values(1,'electrical.dielectric_constant',?,'1',"
                  "'handbook',3,1)", (900.0 + i,))
    c.execute("insert into property_value(id,material_id,property_key,value_num,unit,method,"
              "quality_tier,source_id,conditions,notes) values(?,1,"
              "'electrical.dielectric_constant',?,'1',?,?,1,?,'n')",
              (pv_id, value, method, tier,
               None if conditions is None else json.dumps(conditions, ensure_ascii=False)))
    c.commit(); c.close()


def _pvs(path):
    import sqlite3
    c = sqlite3.connect(path)
    rows = c.execute("select value_num,method,quality_tier from property_value "
                     "where value_num < 900 order by id").fetchall()
    c.close()
    return rows


def _merge(dev, prod):
    r = subprocess.run([sys.executable, str(_MERGER), str(dev), str(prod)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_declared_correction_updates_the_operational_row(tmp_path):
    """정정된 행은 **운영의 옛 행을 갱신**한다 — 새 행으로 들어가면 안 된다.

    운영 id 를 일부러 어긋나게 둔다. 병합기가 id 동일성에 기대면 여기서 깨진다.
    """
    prod = _make_db(tmp_path, "prod.db")
    _seed(prod, pv_id=500, value=6.6, method="handbook", tier=2, conditions=None, filler=3)
    dev = _make_db(tmp_path, "dev.db")
    _seed(dev, pv_id=10, value=6.6, method="handbook", tier=3,
          conditions={"frequency": "미기재", "tier_before_correction": 2,
                      "correction_reason": "주파수가 없어 값으로 쓸 수 없다(브리프 373)",
                      "corrected_by": "48차 JA"}, filler=3)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0     # 중복이 안 생긴다
    assert out["value_corrections_total"] == 1
    assert _pvs(prod) == [(6.6, "handbook", 3)]               # 등급이 운영까지 갔다


def test_correction_that_changes_the_value_is_not_duplicated(tmp_path):
    """값 자체를 고친 정정도 갱신된다 — 자연키의 `value_num` 이 달라져도 옛 값으로 찾는다."""
    prod = _make_db(tmp_path, "prod2.db")
    _seed(prod, pv_id=500, value=6.6, method="handbook", tier=2, conditions=None)
    dev = _make_db(tmp_path, "dev2.db")
    _seed(dev, pv_id=10, value=6.8, method="handbook", tier=2,
          conditions={"value_before_correction": 6.6,
                      "correction_reason": "원문 렌더로 6.8 임을 확인했다",
                      "corrected_by": "48차 JA"})
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert _pvs(prod) == [(6.8, "handbook", 2)]


def test_remerge_is_idempotent(tmp_path):
    """두 번 병합해도 행이 늘지 않는다 — 두 번째는 자연키로 걸린다."""
    prod = _make_db(tmp_path, "prod3.db")
    _seed(prod, pv_id=500, value=6.6, method="handbook", tier=2, conditions=None)
    dev = _make_db(tmp_path, "dev3.db")
    _seed(dev, pv_id=10, value=6.8, method="handbook", tier=2,
          conditions={"value_before_correction": 6.6,
                      "correction_reason": "원문 렌더로 6.8 임을 확인했다"})
    _merge(dev, prod)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out.get("value_corrections_total") is None      # 두 번째엔 고칠 것이 없다
    assert _pvs(prod) == [(6.8, "handbook", 2)]


def test_midpoint_guard_marker_is_not_treated_as_a_correction(tmp_path):
    """`method_before_correction` 만 있는 행은 **정정이 아니다**(중앙값 가드가 남긴 표시다).

    선언(`correction_reason`)을 안 보고 접미어만 보면 실측 227행이 이 분기로 끌려간다.
    """
    prod = _make_db(tmp_path, "prod4.db")
    dev = _make_db(tmp_path, "dev4.db")
    _seed(dev, pv_id=10, value=6.6, method="computed", tier=3,
          conditions={"method_before_correction": "handbook"})
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1   # 평범한 삽입이다
    assert out.get("value_corrections_total") is None
    assert out.get("correction_misses_total") is None
