# 값 **이동**이 운영까지 가는지를 지킨다 — 병합기(`_materialtwin_merge.py`) 회귀.
#
# 왜 여기 있나. 464 가 재료 `attributes` 에서, 522 가 `property_value` 정정에서 잡은 함정의
# **세 번째 얼굴**이다. `property_value` 의 자연키는 `material_id` 를 포함하는데
# **이동이 바꾸는 칸이 바로 그것**이라, 옮긴 행은 운영에서 대응행을 못 찾고 새 행으로 들어간다.
# 그러면 운영에는 같은 측정이 **두 재료에 하나씩** 남고, 옛 재료가 비지 않아 묘비가 거짓이 된다.
# 병합기는 다른 저장소(HEAXHub)에 있어 그쪽에 테스트가 없다 — 이동 경로를 연 이 저장소가 지킨다.
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

OLD = "Carbon Steel 45 (Kwofie 2007 …)"
NEW = "S45C_medium_carbon Bilinear"
KEY = "mechanical.fatigue_strength_coefficient"


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


def _seed(path, *, holder, conditions, filler=0, tombstone=False):
    """재료 둘·출처 하나·물성값 하나. `holder` 가 그 값을 든 재료 이름이다.

    `filler` 로 운영 id 를 dev 와 어긋나게 만든다 — 병합기가 id 동일성에 기대면 거기서 깨진다.
    """
    import sqlite3
    c = sqlite3.connect(path)
    c.execute("insert into property_definition(key,name,domain,si_unit,value_type) "
              f"values('{KEY}','피로강도계수','mechanical','Pa','numeric')")
    tomb = {"merge_verdict": "moved", "merge_moved_to": NEW,
            "merge_moved_keys": [KEY], "merge_reason": "같은 합금이다 — 강 45 = S45C = 1045",
            "merge_moved_at": "2026-08-28"} if tombstone else {}
    c.execute("insert into material(id,name,category,attributes) values(1,?,'metal',?)",
              (OLD, json.dumps(tomb, ensure_ascii=False)))
    c.execute("insert into material(id,name,category,attributes) values(2,?,'metal','{}')", (NEW,))
    c.execute("insert into source(id,kind,title) values(1,'journal','Kwofie 2007')")
    for i in range(filler):
        c.execute(f"insert into property_value(material_id,property_key,value_num,unit,method,"
                  f"quality_tier,source_id) values(2,'{KEY}',?,'Pa','handbook',3,1)", (9.0e9 + i,))
    holder_id = 1 if holder == OLD else 2
    c.execute(f"insert into property_value(material_id,property_key,value_num,unit,method,"
              f"quality_tier,source_id,conditions) values(?,'{KEY}',805500000.0,'Pa','measured',3,1,?)",
              (holder_id, None if conditions is None else json.dumps(conditions, ensure_ascii=False)))
    c.commit(); c.close()


def _rows(path):
    """(그 값을 든 재료 이름, 값) 목록. 더미(9e9 이상)는 뺀다."""
    import sqlite3
    c = sqlite3.connect(path)
    rows = c.execute("select m.name, pv.value_num from property_value pv "
                     "join material m on m.id=pv.material_id "
                     "where pv.value_num < 9.0e9 order by pv.id").fetchall()
    c.close()
    return rows


def _attrs(path, name):
    import sqlite3
    c = sqlite3.connect(path)
    a = c.execute("select attributes from material where name=?", (name,)).fetchone()[0]
    c.close()
    return json.loads(a) if a else {}


def _merge(dev, prod):
    r = subprocess.run([sys.executable, str(_MERGER), str(dev), str(prod)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


_MOVED_COND = {"set_id": "kwofie2007_carbonsteel45", "temperature_k": 298.15,
               "moved_from_material": OLD, "move_reason": "같은 합금이다 — 46차 HC 판정"}


def test_move_updates_the_operational_row_instead_of_inserting(tmp_path):
    """옮긴 값은 **운영의 옛 행을 옮긴다** — 새 행으로 들어가면 안 된다.

    운영은 아직 옛 재료 밑에 값을 들고 있다(병합이 앱 기동보다 먼저라 마이그레이션 전이다).
    """
    prod = _make_db(tmp_path, "prod.db")
    _seed(prod, holder=OLD, conditions={"set_id": "kwofie2007_carbonsteel45",
                                        "temperature_k": 298.15}, filler=3)
    dev = _make_db(tmp_path, "dev.db")
    _seed(dev, holder=NEW, conditions=_MOVED_COND, filler=3, tombstone=True)

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0     # 두 벌이 안 생긴다
    assert out["value_moves_total"] == 1
    assert _rows(prod) == [(NEW, 805500000.0)]                # 값이 새 재료로 갔다
    # 묘비도 함께 가야 한다 — `merge_` 는 큐레이션 접두어다.
    assert _attrs(prod, OLD)["merge_verdict"] == "moved"
    assert _attrs(prod, OLD)["merge_moved_to"] == NEW


def test_remerge_is_idempotent(tmp_path):
    """두 번 병합해도 행이 늘지 않는다 — 두 번째는 자연키로 걸린다."""
    prod = _make_db(tmp_path, "prod2.db")
    _seed(prod, holder=OLD, conditions={"set_id": "kwofie2007_carbonsteel45",
                                        "temperature_k": 298.15})
    dev = _make_db(tmp_path, "dev2.db")
    _seed(dev, holder=NEW, conditions=_MOVED_COND, tombstone=True)

    _merge(dev, prod)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out.get("value_moves_total") is None               # 두 번째엔 옮길 것이 없다
    assert _rows(prod) == [(NEW, 805500000.0)]


def test_missing_old_row_is_reported_not_swallowed(tmp_path):
    """옛 행을 못 찾으면 **삽입하되 크게 보고한다** — 조용히 넘기면 두 벌이 생긴 걸 아무도 모른다."""
    prod = _make_db(tmp_path, "prod3.db")
    _seed(prod, holder=NEW, conditions={"관계없는": "행"})     # 옛 재료 밑에 대응행이 없다
    dev = _make_db(tmp_path, "dev3.db")
    _seed(dev, holder=NEW, conditions=_MOVED_COND, tombstone=True)

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1      # 값은 버리지 않는다
    assert out["move_misses_total"] == 1
    assert out.get("value_moves_total") is None


def test_plain_row_without_the_marker_is_a_normal_insert(tmp_path):
    """이동 표시가 없으면 평범한 삽입이다 — 이 분기가 다른 행을 끌고 가면 안 된다."""
    prod = _make_db(tmp_path, "prod4.db")
    dev = _make_db(tmp_path, "dev4.db")
    _seed(dev, holder=NEW, conditions={"set_id": "kwofie2007_carbonsteel45"})

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1
    assert out.get("value_moves_total") is None
    assert out.get("move_misses_total") is None
