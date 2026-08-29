# 정정 탐색축이 **유일하지 않을 때** 병합기가 조건으로 갈라내는지를 지킨다 — 54차 PA 회귀.
#
# 왜 별도 파일인가(§553). 같은 파동에 다른 배치가 돌아 `test_merge_corrections.py` 를 공유한다.
#
# 왜 있나. 병합기의 정정 탐색축 `(재료·물성키·출처·옛 값)` 은 라이브에서 유일하지 않다 —
# 4,265행 1,832군이 겹친다(§548·564). 그래서 조건 어휘 통일 같은 전수 정정이 **691군
# 5,265행 통째로 막혀 있었다**(52차 NA). 53차 OA 가 출처 이동 분기(⑤)에서 같은 문제를
# **조건을 파싱해 사전으로 대조**해 풀었고(§579), 54차 PA 가 그 방식을 정정 분기(③)에 줬다.
# 여기서는 한 걸음 더 든다 — 정정이 바꾼 칸이 **조건 그 자체**라, 표시로 **정정 전 조건**을
# 되돌려 대조해야 한다. 병합기는 다른 저장소(HEAXHub)에 있어 그쪽에 테스트가 없다.
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

KEY = "thermal.conductivity"


def _make_db(tmp_path, name):
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


def _seed(path, rows):
    """같은 (재료·키·출처·값) 인 행 여럿을 넣는다 — 탐색축이 안 갈리는 상황 그대로다."""
    import sqlite3
    c = sqlite3.connect(path)
    c.execute("insert into property_definition(key,name,domain,si_unit,value_type) "
              f"values('{KEY}','열전도율','thermal','W/(m*K)','numeric')")
    c.execute("insert into material(id,name,category,attributes) values(1,'Kapton HN','polymer','{}')")
    c.execute("insert into source(id,kind,title) values(1,'datasheet','어느 시트')")
    for pid, value, cond in rows:
        c.execute(f"insert into property_value(id,material_id,property_key,value_num,unit,method,"
                  f"quality_tier,source_id,conditions,notes) values(?,1,'{KEY}',?,"
                  "'W/(m*K)','measured',1,1,?,'n')",
                  (pid, value, None if cond is None else json.dumps(cond, ensure_ascii=False)))
    c.commit(); c.close()


def _conds(path):
    import sqlite3
    c = sqlite3.connect(path)
    rows = c.execute(f"select id,conditions from property_value where property_key='{KEY}' "
                     "order by id").fetchall()
    c.close()
    return {r[0]: (json.loads(r[1]) if r[1] else None) for r in rows}


def _merge(dev, prod):
    r = subprocess.run([sys.executable, str(_MERGER), str(dev), str(prod)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def _renamed(old_key, new_key, cond, by="54차 PA"):
    """적재기가 조건 키를 통일했을 때 남기는 모양 그대로."""
    out = {k: v for k, v in cond.items()}
    out[new_key] = out.pop(old_key)
    out[f"{old_key}_before_correction"] = cond[old_key]
    out[f"{new_key}_before_correction"] = None
    out["correction_reason"] = "조건 어휘 통일 — 값·등급·method·출처는 그대로다"
    out["corrected_by"] = by
    return out


def test_conditions_break_a_tie_the_value_axis_cannot(tmp_path):
    """`(재료·키·출처·값)` 이 같은 두 행 중 **조건이 맞는 쪽**을 고쳐야 한다.

    이것이 없으면 두 행 다 후보라 병합기가 거부하고, 값은 운영에 **새 행**으로 들어간다
    (52차 NA 가 691군을 포기한 이유 그대로다).
    """
    prod = _make_db(tmp_path, "prod.db")
    _seed(prod, [(500, 15.0, {"standard": "ASTM E1461", "thickness_um": 25}),
                 (501, 15.0, {"standard": "ASTM D5470", "thickness_um": 50})])
    dev = _make_db(tmp_path, "dev.db")
    _seed(dev, [(10, 15.0, _renamed("standard", "test_standard",
                                    {"standard": "ASTM E1461", "thickness_um": 25})),
                (11, 15.0, _renamed("standard", "test_standard",
                                    {"standard": "ASTM D5470", "thickness_um": 50}))])
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0        # 사본이 안 생긴다
    assert out["value_corrections_total"] == 2
    assert out.get("correction_misses_total") is None
    got = _conds(prod)
    assert got[500]["test_standard"] == "ASTM E1461"             # 짝이 안 바뀌었다
    assert got[501]["test_standard"] == "ASTM D5470"


def test_indistinguishable_rows_are_still_refused(tmp_path):
    """조건까지 봐도 둘 이상 걸리면 **여전히 거부한다** — §521 의 안전 모델은 그대로다."""
    prod = _make_db(tmp_path, "prod2.db")
    _seed(prod, [(500, 15.0, {"standard": "ASTM E1461"}),
                 (501, 15.0, {"standard": "ASTM E1461"})])
    dev = _make_db(tmp_path, "dev2.db")
    _seed(dev, [(10, 15.0, _renamed("standard", "test_standard", {"standard": "ASTM E1461"})),
                (11, 15.0, {"standard": "ASTM E1461"})])
    out = _merge(dev, prod)
    assert out["correction_misses_total"] == 1                   # 고르지 않고 보고한다
    assert "정정 전 조건" in out["correction_misses"][0]["사유"]
    assert _conds(prod)[500] == {"standard": "ASTM E1461"}       # 한 칸도 안 고쳤다


def test_namespaced_condition_marker_is_restored_not_read_as_a_column(tmp_path):
    """`conditions.method_before_correction` 은 **조건 칸**의 옛 값이다(§558 ③).

    컬럼 `method` 의 옛 값으로 읽으면 복원이 어긋나 짝이 뒤바뀐다.
    """
    prod = _make_db(tmp_path, "prod3.db")
    _seed(prod, [(500, 15.0, {"method": "laser flash", "grade": "25 um"}),
                 (501, 15.0, {"method": "guarded hot plate", "grade": "50 um"})])
    dev = _make_db(tmp_path, "dev3.db")
    dev_rows = []
    for pid, meth, grade in ((10, "laser flash", "25 um"), (11, "guarded hot plate", "50 um")):
        dev_rows.append((pid, 15.0, {
            "method_detail": meth, "grade": grade,
            "conditions.method_before_correction": meth,
            "method_detail_before_correction": None,
            "correction_reason": "조건 어휘 통일 — method_detail 이 정본이다",
            "corrected_by": "54차 PA"}))
    _seed(dev, dev_rows)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out["value_corrections_total"] == 2
    got = _conds(prod)
    assert got[500]["method_detail"] == "laser flash"
    assert got[501]["method_detail"] == "guarded hot plate"


def test_remerge_is_idempotent(tmp_path):
    """두 번 병합해도 행이 안 늘고 두 번째엔 고칠 것이 없다 — ② 자연키가 먼저 걸린다."""
    prod = _make_db(tmp_path, "prod4.db")
    _seed(prod, [(500, 15.0, {"standard": "ASTM E1461", "thickness_um": 25}),
                 (501, 15.0, {"standard": "ASTM D5470", "thickness_um": 50})])
    dev = _make_db(tmp_path, "dev4.db")
    _seed(dev, [(10, 15.0, _renamed("standard", "test_standard",
                                    {"standard": "ASTM E1461", "thickness_um": 25})),
                (11, 15.0, _renamed("standard", "test_standard",
                                    {"standard": "ASTM D5470", "thickness_um": 50}))])
    _merge(dev, prod)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out.get("value_corrections_total") is None
    assert out.get("correction_misses_total") is None


def test_a_correction_on_an_already_corrected_row_is_refused_not_mismatched(tmp_path):
    """**한계를 못박는다** — 두 세대 표시는 복원 못 한다. 그래도 *틀린 행을 고르지 않는다.*

    앞 세대 표시가 남아 있으면 한 세대가 아니라 두 세대를 되돌리게 되는데, 그 결과는
    대응행 **0건**이라 `correction_misses` 로 뜬다. 54차 PA 의 표적 4,455행에는 앞 정정이
    붙은 행이 0행이라 이 한계에 안 닿았다 — 닿는 날 조용히 틀리지 않게 여기 박아 둔다.
    """
    prod = _make_db(tmp_path, "prod5.db")
    _seed(prod, [(500, 15.0, {"test_standard": "ASTM E1461",
                              "standard_before_correction": "ASTM E1461",
                              "test_standard_before_correction": None,
                              "correction_reason": "앞 파동의 어휘 통일",
                              "corrected_by": "52차 NA"}),
                 (501, 15.0, {"test_standard": "ASTM D5470"})])
    dev = _make_db(tmp_path, "dev5.db")
    _seed(dev, [(10, 15.0, {"test_standard": "ASTM E1461", "temperature_c": 23,
                            "standard_before_correction": "ASTM E1461",
                            "test_standard_before_correction": None,
                            "temperature_C_before_correction": 23,
                            "temperature_c_before_correction": None,
                            "correction_reason": "두 번째 정정",
                            "corrected_by": "54차 PA"}),
                (501, 15.0, {"test_standard": "ASTM D5470"})])
    out = _merge(dev, prod)
    assert out["correction_misses_total"] == 1          # 조용히 틀리지 않고 보고한다
    assert _conds(prod)[501] == {"test_standard": "ASTM D5470"}   # 남의 행을 안 건드린다


def test_correction_lands_even_when_the_source_move_already_reached_production(tmp_path):
    """**출처 병합이 먼저 운영까지 간 뒤 같은 행을 또 고치면** 정정이 갈 곳을 잃는다.

    ②-c 가 조회축을 옛 출처로 바꾸는데(§579), 운영이 이미 새 출처를 가리키고 있으면
    옛 출처 밑에는 아무것도 없다 — 0건이라 정정이 miss 가 되고 값이 **새 행**으로 들어간다.
    54차 PA 예행에서 실측 69행이 이랬다(53차 OA 가 옮긴 Kapton EN·Pyralux·Dievar 행).
    **0건일 때만** 새 출처로 한 번 더 묻는다 — 2건 이상이면 거부가 맞다.
    """
    import sqlite3
    prod = _make_db(tmp_path, "prod6.db")
    _seed(prod, [(500, 15.0, {"standard": "ASTM E1461",
                              "moved_from_source": {"kind": "datasheet", "title": "옛 시트"}})])
    c = sqlite3.connect(prod)
    c.execute("insert into source(id,kind,title) values(2,'datasheet','옛 시트')")
    c.execute("update property_value set source_id=1 where id=500")   # 이미 새 출처를 가리킨다
    c.commit(); c.close()

    dev = _make_db(tmp_path, "dev6.db")
    _seed(dev, [(10, 15.0, _renamed("standard", "test_standard",
                                    {"standard": "ASTM E1461",
                                     "moved_from_source": {"kind": "datasheet",
                                                           "title": "옛 시트"}}))])
    c = sqlite3.connect(dev)
    c.execute("insert into source(id,kind,title) values(2,'datasheet','옛 시트')")
    c.commit(); c.close()

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out["value_corrections_total"] == 1
    assert out.get("correction_misses_total") is None
    assert out.get("source_move_misses_total") is None
    assert _conds(prod)[500]["test_standard"] == "ASTM E1461"
