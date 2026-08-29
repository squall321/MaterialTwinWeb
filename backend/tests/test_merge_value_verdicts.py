# 물성값 **판정**(`conditions.verdict_*`)이 운영까지 가는지를 지킨다 — 병합기 회귀.
#
# 왜 여기 있나. 464 가 재료 `attributes` 에서, 522 가 값 정정에서, 536 이 값 이동에서 잡은
# 함정의 **네 번째 얼굴**이다. `property_value` 자연키에 `conditions` 가 들어 있어
# **판정 한 칸만 더해도 자연키가 깨지고** 운영에 사본이 생긴다.
#
# 정정 경로(§521)로는 못 우회한다 — 그 경로는 `(재료·키·출처·옛 값)` 이 **유일해야** 도는데
# 중복 적재 군은 정의상 유일하지 않다. 51차 MA 가 그 이유로 **128군을 포기했다**(§548).
# 그래서 병합기가 판정 키를 **자연키에서 빼고** 찾은 뒤 그 키만 얹도록 고쳤다.
# 병합기는 다른 저장소(HEAXHub)에 있어 그쪽에 테스트가 없다 — **경로를 연 쪽이 지킨다**(§522·536).
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

MAT = "Rogers RO4350B High-Frequency Laminate"
KEY = "thermal.expansion_linear"
VAL = 3.2e-05
# 같은 시트를 두 번 적재해 생긴 실제 모양이다 — `axis` 판과 `direction` 판(§547).
CANON = {"axis": "z", "temperature_range_C": "-55 to 288", "standard": "IPC-TM-650 2.4.41"}
DUP = {"direction": "Z", "temperature_range_c": "-55 to 288", "standard": "IPC-TM-650 2.4.41"}
VERDICT = {"verdict_duplicate_of": 'axis="z" | standard="IPC-TM-650 2.4.41"',
           "verdict_duplicate_note": "52차 NB — 같은 측정을 두 번 적재했다"}


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


def _seed(path, conds, *, filler=0):
    """재료 하나·출처 하나에 `conds` 대로 물성값을 넣는다.

    `filler` 로 운영 id 를 dev 와 어긋나게 만든다 — 병합기가 id 동일성에 기대면 거기서 깨진다.
    """
    import sqlite3
    c = sqlite3.connect(path)
    c.execute("insert into property_definition(key,name,domain,si_unit,value_type) "
              f"values('{KEY}','선팽창계수','thermal','1/K','numeric')")
    c.execute("insert into material(id,name,category,attributes) values(1,?,'composite','{}')",
              (MAT,))
    c.execute("insert into source(id,kind,title) values(1,'datasheet','RO4000 Series TDS')")
    for i in range(filler):
        c.execute(f"insert into property_value(material_id,property_key,value_num,unit,method,"
                  f"quality_tier,source_id) values(1,'{KEY}',?,'1/K','handbook',3,1)", (9.0 + i,))
    for cond in conds:
        c.execute(f"insert into property_value(material_id,property_key,value_num,unit,method,"
                  f"quality_tier,source_id,conditions) values(1,'{KEY}',{VAL},'1/K','measured',1,1,?)",
                  (json.dumps(cond, ensure_ascii=False),))
    c.commit(); c.close()


def _conds(path):
    """더미(9.0 이상)를 뺀 조건 목록. 삽입 순서 그대로."""
    import sqlite3
    c = sqlite3.connect(path)
    rows = [json.loads(r[0]) for r in c.execute(
        "select conditions from property_value where value_num < 9.0 order by id")]
    c.close()
    return rows


def _merge(dev, prod):
    r = subprocess.run([sys.executable, str(_MERGER), str(dev), str(prod)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


def test_verdict_lands_on_the_operational_row_instead_of_inserting(tmp_path):
    """판정은 **운영의 그 행에 얹혀야 한다** — 새 행으로 들어가면 판정 없는 옛 행이 그대로 남는다.

    이것이 고치기 전의 실패다: 라이브 41,368행 예행에서 옛 병합기는 `added 63` 을 냈다.
    """
    prod = _make_db(tmp_path, "prod.db")
    _seed(prod, [CANON, DUP], filler=3)
    dev = _make_db(tmp_path, "dev.db")
    _seed(dev, [CANON, dict(DUP, **VERDICT)])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0      # 사본이 안 생긴다
    assert out["value_verdicts_total"] == 1
    after = _conds(prod)
    assert after[0] == CANON                                   # 정본은 한 칸도 안 건드린다
    assert after[1] == dict(DUP, **VERDICT)                    # 중복에만 판정이 얹혔다


def test_the_correction_path_now_reaches_this_too(tmp_path):
    """**54차 PA 가 이 자리를 열었다.** 전에는 정정 경로가 옛 행을 특정 못 했다(§548).

    옛 모습 — `(재료·키·출처·값)` 만으로 좁혀 두 행에 걸리고, 값이 운영에 **새 행**으로
    들어갔다(`added 1 · correction_misses 1`). 그것이 51차 MA 가 128군을, 52차 NA 가
    691군을 포기한 이유다. 지금은 값으로 안 갈리면 **정정 전 조건을 표시로 되돌려
    사전으로 대조**하므로 유일하게 찾는다(§579 의 방식을 분기 ③ 에 준 것이다).

    **판정 경로(②-b)가 없어도 된다는 뜻은 아니다.** 그쪽은 `correction_reason` 을 남기지
    않는 판정 — 즉 정정으로 선언되지 않은 행 — 을 맡는다. 아래 테스트들이 그 자리를 지킨다.
    """
    prod = _make_db(tmp_path, "prod2.db")
    _seed(prod, [CANON, DUP])
    dev = _make_db(tmp_path, "dev2.db")
    # 정정으로 선언한다(§521 의 표시 그대로).
    corrected = dict(DUP, correction_reason="중복이라 표시한다",
                     value_before_correction=VAL)
    _seed(dev, [CANON, corrected])
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0      # 사본이 안 생긴다
    assert out["value_corrections_total"] == 1
    assert out.get("correction_misses_total") is None
    assert _conds(prod)[0] == CANON                            # 정본은 한 칸도 안 건드린다


def test_remerge_is_idempotent(tmp_path):
    """두 번 병합해도 행이 늘지 않고 판정을 두 번 쓰지 않는다 — 자연키 탐색이 먼저다."""
    prod = _make_db(tmp_path, "prod3.db")
    _seed(prod, [CANON, DUP])
    dev = _make_db(tmp_path, "dev3.db")
    _seed(dev, [CANON, dict(DUP, **VERDICT)])

    _merge(dev, prod)
    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    assert out.get("value_verdicts_total") is None             # 두 번째엔 얹을 것이 없다
    assert _conds(prod) == [CANON, dict(DUP, **VERDICT)]


def test_operational_only_keys_are_not_erased(tmp_path):
    """**지우지 않는다** — dev 에 없는 판정 키는 운영 값을 그대로 둔다(§464 의 비파괴 약속)."""
    prod = _make_db(tmp_path, "prod4.db")
    _seed(prod, [CANON, dict(DUP, verdict_tie_axis="운영에만 있는 51차 판정")])
    dev = _make_db(tmp_path, "dev4.db")
    _seed(dev, [CANON, dict(DUP, **VERDICT)])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    got = _conds(prod)[1]
    assert got["verdict_tie_axis"] == "운영에만 있는 51차 판정"
    assert got["verdict_duplicate_of"] == VERDICT["verdict_duplicate_of"]


def test_missing_operational_row_is_reported_not_swallowed(tmp_path):
    """대응행을 못 찾으면 **삽입하되 크게 보고한다** — 조용히 넘기면 두 벌이 생긴 걸 아무도 모른다."""
    prod = _make_db(tmp_path, "prod5.db")
    _seed(prod, [CANON])                                       # 중복 쪽 행이 운영에 없다
    dev = _make_db(tmp_path, "dev5.db")
    _seed(dev, [CANON, dict(DUP, **VERDICT)])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1       # 값은 버리지 않는다
    assert out["verdict_misses_total"] == 1
    assert out.get("value_verdicts_total") is None


def test_plain_row_without_a_verdict_is_a_normal_insert(tmp_path):
    """판정 키가 없으면 평범한 삽입이다 — 이 분기가 다른 행을 끌고 가면 안 된다."""
    prod = _make_db(tmp_path, "prod6.db")
    _seed(prod, [CANON])
    dev = _make_db(tmp_path, "dev6.db")
    _seed(dev, [CANON, DUP])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 1
    assert out.get("value_verdicts_total") is None
    assert out.get("verdict_misses_total") is None


def test_verdict_does_not_overwrite_the_value(tmp_path):
    """판정 경로는 **조건의 판정 키만** 쓴다 — 값·등급을 덮으면 그건 정정이지 판정이 아니다."""
    import sqlite3
    prod = _make_db(tmp_path, "prod7.db")
    _seed(prod, [CANON, DUP])
    c = sqlite3.connect(prod)
    c.execute("update property_value set quality_tier=2, notes='운영 메모' "
              "where json_extract(conditions,'$.direction')='Z'")
    c.commit(); c.close()
    dev = _make_db(tmp_path, "dev7.db")
    _seed(dev, [CANON, dict(DUP, **VERDICT)])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0
    c = sqlite3.connect(prod)
    tier, notes = c.execute(
        "select quality_tier, notes from property_value "
        "where json_extract(conditions,'$.direction')='Z'").fetchone()
    c.close()
    assert (tier, notes) == (2, "운영 메모")     # 판정만 얹고 나머지는 그대로다


def test_verdict_declared_through_the_correction_path_makes_no_noise(tmp_path):
    """**판정을 §521 의 `corrections` 경로로 넣은 행은 ③ 이 맡는다 — ②-b 가 손대면 안 된다.**

    그 경로는 `correction_reason`·`corrected_by` 를 반드시 남기는데 그 둘은 판정 키가 아니라
    dev 쪽에만 있다. ②-b 가 조건 사전을 대조하면 전건이 안 맞아 **결과는 옳은데(③ 이 다
    받아낸다) 경고만 수천 건** 뜬다 — 실측 52차 NC, 판정 3,400행.
    **매번 뜨는 같은 경고는 무시하는 법을 가르친다**(§546). 그래서 아예 안 들어오게 막았다.
    """
    # 정정 경로가 **돌 수 있는** 모양으로 둔다 — (재료·키·출처·값)이 유일해야 한다(§548).
    prod = _make_db(tmp_path, "prod8.db")
    _seed(prod, [DUP], filler=2)
    dev = _make_db(tmp_path, "dev8.db")
    # 51차 MA·52차 NC 가 실제로 넣은 모양 — 판정 + 정정 선언 + 칸 단위 되돌리기 표시.
    via_corrections = dict(DUP, verdict_tie_axis="방향축이 갈렸다",
                           verdict_tie_axis_before_correction=None,
                           correction_reason="동률 사유를 남긴다", corrected_by="52차 NC")
    _seed(dev, [via_corrections])

    out = _merge(dev, prod)
    assert out["summary"]["property_value"]["added"] == 0    # ③ 이 받아낸다
    assert out["value_corrections_total"] == 1
    assert out.get("verdict_misses_total") is None           # ②-b 가 경고를 안 만든다
    assert _conds(prod) == [via_corrections]                 # 정정 선언까지 통째로 간다
