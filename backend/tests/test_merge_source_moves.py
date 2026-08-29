# **출처 병합**이 운영까지 가는지를 지킨다 — 병합기(`_materialtwin_merge.py`) 회귀.
#
# 왜 여기 있나. 464 가 재료 `attributes` 에서, 522 가 `property_value` 정정에서, 536 이
# 재료 이동에서 잡은 함정의 **다섯 번째 얼굴**이다. `property_value` 의 자연키는 `source_id`
# 를 포함하는데 **출처 병합이 바꾸는 칸이 바로 그것**이라, 합친 행은 운영에서 대응행을 못 찾고
# 새 행으로 들어간다. 그러면 운영에는 같은 측정이 **두 출처에 하나씩** 남는다.
# 실측(53차 OA, 옮긴 193행) — 고치기 전 예행 `property_value added 181`.
#
# `source_id` 재매핑은 이것을 **대신하지 않는다** — 재매핑은 dev 의 출처 id 를 운영 id 로
# 바꿔 줄 뿐이고, 운영 행은 여전히 옛 출처를 가리킨다. 그 사실을 못박는 시험이 아래 첫째다.
# 병합기는 다른 저장소(HEAXHub)에 있어 그쪽에 테스트가 없다 — 경로를 연 이 저장소가 지킨다.
from __future__ import annotations

import importlib
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
MAT = "Uddeholm Dievar hot-work tool steel"
# 합칠 출처(drop)와 남길 출처(keep). **자연키가 지문이다** — 출처에는 재료의 `name` 같은
# 자연 이름이 없어서, 병합기의 출처 자연키 전체를 표시에 적는다(§535 의 출처판).
DROP = {"kind": "datasheet", "doi": None, "isbn": None, "url": "https://www.uddeholm.com/",
        "title": "Uddeholm Dievar — product datasheet, Edition 15 (10.2025)",
        "publisher": None, "license": None}
KEEP = dict(DROP, url="https://www.uddeholm.com/tech_uddeholm-dievar_en.pdf",
            publisher="Uddeholms AB")


def _make_db(tmp_path, name):
    """앱 스키마 그대로인 빈 SQLite 를 만든다(병합기는 실제 표 구조를 본다)."""
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


def _seed(path, rows, *, filler=0):
    """재료 하나 · 출처 둘(keep/drop) · `rows` 의 물성값.

    `rows` 는 (출처 자연키, 값, 조건) 목록이다.
    `filler` 로 운영 id 를 dev 와 어긋나게 만든다 — 병합기가 id 동일성에 기대면 거기서 깨진다.
    """
    import sqlite3
    c = sqlite3.connect(path)
    c.execute("insert into property_definition(key,name,domain,si_unit,value_type) "
              f"values('{KEY}','열전도율','thermal','W/(m*K)','numeric')")
    c.execute("insert into material(id,name,category,attributes) values(1,?,'metal','{}')", (MAT,))
    cols = ",".join(KEEP)
    for sid, spec in ((1, KEEP), (2, DROP)):
        c.execute(f"insert into source(id,{cols}) values(?,{','.join('?' * len(spec))})",
                  [sid] + [spec[k] for k in spec])
    for i in range(filler):
        c.execute(f"insert into property_value(material_id,property_key,value_num,unit,method,"
                  f"quality_tier,source_id) values(1,'{KEY}',?,'W/(m*K)','handbook',3,1)",
                  (900.0 + i,))
    for spec, val, cond in rows:
        c.execute(f"insert into property_value(material_id,property_key,value_num,unit,method,"
                  f"quality_tier,source_id,conditions) values(1,'{KEY}',?,'W/(m*K)','measured',1,?,?)",
                  (val, 1 if spec is KEEP else 2,
                   None if cond is None else json.dumps(cond, ensure_ascii=False)))
    c.commit()
    c.close()


def _by_source(path):
    """(출처 url, 값) 목록. 더미(900 이상)는 뺀다."""
    import sqlite3
    c = sqlite3.connect(path)
    rows = c.execute("select s.url, pv.value_num from property_value pv "
                     "join source s on s.id=pv.source_id "
                     "where pv.value_num < 900 order by pv.value_num").fetchall()
    c.close()
    return rows


def _merge(dev, prod):
    r = subprocess.run([sys.executable, str(_MERGER), str(dev), str(prod)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def _moved(cond):
    """마이그레이션이 남기는 표시 — 옛 출처의 **자연키 전체**(§535 의 출처판)."""
    return dict(cond or {}, moved_from_source=dict(DROP, note="[53차 OA] 같은 판이다"))


def test_source_move_updates_the_operational_row_instead_of_inserting(tmp_path):
    """합친 값은 **운영의 옛 행을 옮긴다** — 새 행으로 들어가면 안 된다.

    운영은 아직 옛 출처 밑에 값을 들고 있다(병합이 앱 기동보다 먼저라 마이그레이션 전이다).
    `source_id` 재매핑만으로는 절대 안 된다 — 재매핑은 dev↔운영 id 만 잇는다.
    """
    prod = _make_db(tmp_path, "prod.db")
    _seed(prod, [(DROP, 26.3, {"temperature_C": 20})], filler=3)
    dev = _make_db(tmp_path, "dev.db")
    _seed(dev, [(KEEP, 26.3, _moved({"temperature_C": 20}))])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0      # 두 벌이 안 생긴다
    assert out["source_moves_total"] == 1
    assert _by_source(prod) == [(KEEP["url"], 26.3)]           # 값이 남길 출처로 갔다


def test_remerge_is_idempotent(tmp_path):
    """두 번 병합해도 행이 늘지 않는다 — 두 번째는 자연키로 걸린다."""
    prod = _make_db(tmp_path, "prod2.db")
    _seed(prod, [(DROP, 26.3, {"temperature_C": 20})])
    dev = _make_db(tmp_path, "dev2.db")
    _seed(dev, [(KEEP, 26.3, _moved({"temperature_C": 20}))])

    _merge(dev, prod)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out.get("source_moves_total") is None               # 두 번째엔 옮길 것이 없다
    assert _by_source(prod) == [(KEEP["url"], 26.3)]


def test_same_value_twice_is_split_by_conditions(tmp_path):
    """옛 출처 밑에 **같은 값이 둘** 있으면 조건을 사전으로 대조해 가른다.

    실측이 낸 시험이다 — Uddeholm 그래프 디지타이즈는 같은 재료·키에 26.3 J 를 세 번 인쇄한다.
    값만으로 좁히면 그 행들이 운영에 새 행으로 들어간다(고치기 전 예행 `added 7`).
    """
    prod = _make_db(tmp_path, "prod3.db")
    _seed(prod, [(DROP, 26.3, {"temperature_C": 20}), (DROP, 26.3, {"temperature_C": 200})])
    dev = _make_db(tmp_path, "dev3.db")
    _seed(dev, [(KEEP, 26.3, _moved({"temperature_C": 20})),
                (KEEP, 26.3, _moved({"temperature_C": 200}))])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out["source_moves_total"] == 2
    assert _by_source(prod) == [(KEEP["url"], 26.3), (KEEP["url"], 26.3)]


def test_correction_and_source_move_together_do_not_miss(tmp_path):
    """정정과 출처 병합이 **한 행에 겹치면** 조회축을 옛 출처로 바꿔야 한다(②-c).

    안 바꾸면 정정 분기가 새 `source_id` 로 옛 행을 찾다 전부 놓친다 —
    실측(53차 OA)에서 옮긴 193행 중 **78행이 정정을 함께 달고 있었다.**
    """
    prod = _make_db(tmp_path, "prod4.db")
    _seed(prod, [(DROP, 26.3, {"temperature_C": 20})])
    dev = _make_db(tmp_path, "dev4.db")
    _seed(dev, [(KEEP, 31.0, _moved({"temperature_C": 20, "value_before_correction": 26.3,
                                     "correction_reason": "원문 재확인 — 그래프 눈금 오독"}))])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out.get("correction_misses_total") is None
    assert out["value_corrections_total"] == 1
    assert _by_source(prod) == [(KEEP["url"], 31.0)]           # 정정과 병합이 같이 갔다


def test_missing_old_source_is_reported_not_swallowed(tmp_path):
    """옛 출처를 운영에서 못 찾으면 **삽입하되 크게 보고한다**(§536 과 같은 규율)."""
    prod = _make_db(tmp_path, "prod5.db")
    import sqlite3
    _seed(prod, [])
    sqlite3.connect(prod).execute("delete from source where id=2").connection.commit()
    dev = _make_db(tmp_path, "dev5.db")
    _seed(dev, [(KEEP, 26.3, _moved({"temperature_C": 20}))])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1      # 값은 버리지 않는다
    assert out["source_move_misses_total"] == 1
    assert out.get("source_moves_total") is None


def test_plain_row_without_the_marker_is_a_normal_insert(tmp_path):
    """표시가 없으면 평범한 삽입이다 — 이 분기가 다른 행을 끌고 가면 안 된다."""
    prod = _make_db(tmp_path, "prod6.db")
    _seed(prod, [])
    dev = _make_db(tmp_path, "dev6.db")
    _seed(dev, [(KEEP, 26.3, {"temperature_C": 20})])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1
    assert out.get("source_moves_total") is None
    assert out.get("source_move_misses_total") is None
