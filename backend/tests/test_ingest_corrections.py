# 적재기의 명시적 정정 경로(48차 JA) — **데이터를 덮는 유일한 길이라 여기서 못 지키면 아무도 못 잡는다**.
# 브리프 314 가 남긴 "적재기는 UPDATE 를 못 한다" 를 여는 경로이므로, 안전 모델(암묵적 정정 금지·
# 대상 유일성·사유 필수·되돌리기 가능·드라이런)이 깨지지 않는지를 이 파일이 지킨다.
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest

_BACKEND = Path(__file__).resolve().parents[1]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))
_CATALOG = _BACKEND / "scripts" / "catalog"
if str(_CATALOG) not in sys.path:
    sys.path.insert(0, str(_CATALOG))


@pytest.fixture()
def ing(tmp_path, monkeypatch):
    """tmp DB 로 격리한 적재기 모듈. conftest 의 mcp_env 와 같은 재로딩 순서를 지킨다."""
    monkeypatch.setenv("MATERIALTWIN_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MATERIALTWIN_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    from app import config as config_mod
    config_mod.get_settings.cache_clear()
    import app.db as db_mod
    import app.models as models_mod
    db_mod = importlib.reload(db_mod)
    models_mod = importlib.reload(models_mod)
    import mcp_server as mcp_mod
    importlib.reload(mcp_mod)
    db_mod.init_db()
    import ingest_agent_json as I
    I = importlib.reload(I)
    yield I
    config_mod.get_settings.cache_clear()


def _seed(ing, *, value=6.6, tier=2, method="handbook", conditions=None,
          key="electrical.dielectric_constant", name="E-Glass Cloth"):
    """정정 대상 한 행을 심는다. (material_id, property_value_id) 를 돌려준다."""
    import mcp_server as M
    mid = M.register_material(name, "ceramic")["material_id"]
    r = M.register_property(mid, key, value=value, unit="1", method=method,
                            quality_tier=tier, conditions=conditions,
                            notes="원래 노트", source_title="어느 핸드북", source_kind="book")
    assert "error" not in r, r
    return mid, r["property_value_id"]


def _run(ing, tmp_path, doc, apply):
    f = tmp_path / "corr.json"
    f.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return ing.apply_corrections(ing.load([str(f)]), apply)


def _row(ing, pvid):
    from app.db import SessionLocal
    from app.models import PropertyValue
    with SessionLocal() as s:
        pv = s.get(PropertyValue, pvid)
        return {"value": pv.value_num, "tier": pv.quality_tier, "method": pv.method,
                "unit": pv.unit, "notes": pv.notes,
                "conditions": dict(pv.conditions or {})}


# ── 성공 ──────────────────────────────────────────────────────────────────────

def test_correction_applies_and_keeps_old_value_in_conditions(ing, tmp_path):
    """정정이 실제로 값을 고치고, **옛 값·옛 등급·사유가 조건에 남는다**(되돌릴 수 있어야 한다)."""
    mid, pvid = _seed(ing)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "주파수 조건이 없어 값으로 쓸 수 없다(브리프 373) — 등급을 내린다",
        "by": "48차 JA",
        "set": {"quality_tier": 4, "value": 6.8},
    }]}, apply=True)
    assert st["corr_ok"] == 1
    r = _row(ing, pvid)
    assert r["tier"] == 4 and r["value"] == pytest.approx(6.8)
    # 옛 값이 사라지지 않았다.
    assert r["conditions"]["tier_before_correction"] == 2
    assert r["conditions"]["value_before_correction"] == pytest.approx(6.6)
    assert "브리프 373" in r["conditions"]["correction_reason"]
    assert r["conditions"]["corrected_by"] == "48차 JA"


def test_correction_records_each_changed_condition_key(ing, tmp_path):
    """조건을 고치면 **바뀐 칸마다** `<칸>_before_correction` 이 남는다(44차 FD 의 선례)."""
    mid, pvid = _seed(ing, conditions={"frequency": "1 MHz", "temperature": "23 C"})
    _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "원문이 1 GHz 라 주파수 표기가 틀렸다 — 렌더로 확인했다",
        "set": {"conditions": {"frequency": "1 GHz", "temperature": "23 C"}},
    }]}, apply=True)
    c = _row(ing, pvid)["conditions"]
    assert c["frequency"] == "1 GHz"
    assert c["frequency_before_correction"] == "1 MHz"
    assert "temperature_before_correction" not in c   # 안 바뀐 칸은 안 남긴다


# ── 거부 ──────────────────────────────────────────────────────────────────────

def test_correction_without_reason_is_rejected(ing, tmp_path):
    """사유가 없으면 거부한다 — 왜 고치는지가 값과 함께 남아야 한다."""
    mid, pvid = _seed(ing)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid}, "set": {"quality_tier": 4},
    }]}, apply=True)
    assert st["corr_no_reason"] == 1 and st["corr_ok"] == 0
    assert _row(ing, pvid)["tier"] == 2


def test_correction_matching_many_rows_is_rejected(ing, tmp_path):
    """대상이 여러 행에 걸리면 거부한다 — 어느 행인지 우리가 고르면 그건 우리 판정이다."""
    import mcp_server as M
    mid, pvid = _seed(ing, conditions={"frequency": "1 MHz"})
    r2 = M.register_property(mid, "electrical.dielectric_constant", value=6.1, unit="1",
                             method="handbook", quality_tier=2,
                             conditions={"frequency": "10 GHz"},
                             source_title="어느 핸드북", source_kind="book")
    assert "error" not in r2
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"material_id": mid, "property_key": "electrical.dielectric_constant"},
        "reason": "두 행 다 고치려 한다 — 대상이 유일하지 않다",
        "set": {"quality_tier": 3},
    }]}, apply=True)
    assert st["corr_multi_match"] == 1 and st["corr_ok"] == 0
    assert _row(ing, pvid)["tier"] == 2 and _row(ing, r2["property_value_id"])["tier"] == 2


def test_correction_with_no_matching_row_is_rejected(ing, tmp_path):
    """대상이 0건이면 거부한다 — 조용히 넘어가면 배치가 고쳤다고 착각한다."""
    mid, pvid = _seed(ing)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid + 9999},
        "reason": "있지도 않은 행을 고치려 한다",
        "set": {"quality_tier": 4},
    }]}, apply=True)
    assert st["corr_no_match"] == 1 and st["corr_ok"] == 0


def test_correction_cannot_move_key_or_material(ing, tmp_path):
    """`property_key`·`material_id` 이동은 정정이 아니다 — 묘비 규약이 먼저다(46차 HC)."""
    mid, pvid = _seed(ing)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "연화점을 최대사용온도 키에 넣었으니 키를 옮기겠다",
        "set": {"property_key": "thermal.dilatometric_softening_point"},
    }]}, apply=True)
    assert st["corr_rejected"] == 1 and st["corr_ok"] == 0
    from app.db import SessionLocal
    from app.models import PropertyValue
    with SessionLocal() as s:
        assert s.get(PropertyValue, pvid).property_key == "electrical.dielectric_constant"


def test_correction_obeys_same_range_guard_as_insertion(ing, tmp_path):
    """정정이 범위 가드의 우회로가 되면 안 된다 — 삽입과 **같은 가드**를 통과해야 한다."""
    mid, pvid = _seed(ing, key="physical.density", value=2540.0, tier=2)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "g/cm^3 원값으로 되돌리겠다 — 물리적으로 불가능한 값이다",
        "set": {"value": 2.54},
    }]}, apply=True)
    assert st["corr_rejected"] == 1
    assert _row(ing, pvid)["value"] == pytest.approx(2540.0)


def test_tier_upgrade_requires_evidence(ing, tmp_path):
    """**등급 상향은 더 엄격하다** — 사유만으로는 안 되고 `evidence` 가 따로 있어야 한다."""
    mid, pvid = _seed(ing, tier=3)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "실측인 것 같으니 등급을 올린다",
        "set": {"quality_tier": 2},
    }]}, apply=True)
    assert st["corr_rejected"] == 1 and _row(ing, pvid)["tier"] == 3

    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "원 시트를 찾아 값의 출처가 실측표임을 확인했다",
        "evidence": "AGY LIT-2009-351 p.38 각주가 ASTM D150 측정법까지 밝힌다",
        "set": {"quality_tier": 2},
    }]}, apply=True)
    assert st["corr_ok"] == 1 and _row(ing, pvid)["tier"] == 2


def test_tier1_upgrade_requires_measured_method(ing, tmp_path):
    """t1 은 **측정법이 적힌 값**만이다(브리프 3번) — handbook 을 t1 로 올릴 수 없다."""
    mid, pvid = _seed(ing, tier=3, method="handbook")
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "핸드북 값이지만 원 논문이라 t1 로 올리고 싶다",
        "evidence": "같은 값이 원 논문 Table 2 에 있다",
        "set": {"quality_tier": 1},
    }]}, apply=True)
    assert st["corr_rejected"] == 1 and _row(ing, pvid)["tier"] == 3


def test_correction_that_would_duplicate_is_rejected(ing, tmp_path):
    """정정 결과가 다른 행과 (재료·키·출처·조건)이 같아지면 거부한다 — 중복은 정정이 아니다."""
    import mcp_server as M
    mid, pvid = _seed(ing, conditions={"frequency": "1 MHz"})
    M.register_property(mid, "electrical.dielectric_constant", value=6.1, unit="1",
                        method="handbook", quality_tier=2, conditions={"frequency": "10 GHz"},
                        source_title="어느 핸드북", source_kind="book")
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "주파수를 10 GHz 로 고치면 옆 행과 조건이 같아진다",
        "set": {"conditions": {"frequency": "10 GHz"}},
    }]}, apply=True)
    assert st["corr_would_duplicate"] == 1
    assert _row(ing, pvid)["conditions"]["frequency"] == "1 MHz"


# ── 드라이런 ──────────────────────────────────────────────────────────────────

def test_dry_run_writes_nothing(ing, tmp_path):
    """`--apply` 없이는 무엇을 고칠지만 출력한다 — 한 칸도 쓰지 않는다."""
    mid, pvid = _seed(ing)
    before = _row(ing, pvid)
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "드라이런이 쓰지 않는지 본다 — 이 정정은 유효하다",
        "set": {"quality_tier": 4, "value": 6.8, "notes": "새 노트"},
    }]}, apply=False)
    assert st["corr_ok"] == 1          # 유효한 정정으로 세지만
    assert _row(ing, pvid) == before   # DB 는 그대로다


# ── 안전 모델 ─────────────────────────────────────────────────────────────────

def test_plain_materials_doc_never_corrects(ing, tmp_path):
    """**암묵적 정정은 없다** — 같은 재료·같은 키에 값이 또 와도 옛 행을 고치지 않는다."""
    mid, pvid = _seed(ing, conditions={"frequency": "1 MHz"})
    doc = {"materials": [{
        "match_name": "E-Glass Cloth",
        "source": {"title": "어느 핸드북", "kind": "book"},
        "properties": [{"key": "electrical.dielectric_constant", "value": 9.9, "unit": "1",
                        "tier": 1, "method": "measured", "conditions": {"frequency": "1 MHz"}}],
    }]}
    f = tmp_path / "ins.json"
    f.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    st = ing.apply_corrections(ing.load([str(f)]), True)
    assert st["corr_ok"] == 0          # 정정 선언이 없으니 정정은 0건이다
    assert _row(ing, pvid)["value"] == pytest.approx(6.6)


def test_target_by_material_key_conditions_pins_one_row(ing, tmp_path):
    """행 id 를 몰라도 **재료+키+조건**으로 유일하게 걸면 정정된다(조건 없는 행도 못박힌다)."""
    import mcp_server as M
    mid, pvid = _seed(ing, conditions=None)          # 조건이 비어 있는 행
    M.register_property(mid, "electrical.dielectric_constant", value=6.1, unit="1",
                        method="handbook", quality_tier=2, conditions={"frequency": "10 GHz"},
                        source_title="어느 핸드북", source_kind="book")
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"material_name": "E-Glass Cloth",
                   "property_key": "electrical.dielectric_constant",
                   "conditions": None, "value": 6.6},
        "reason": "조건축이 비어 값으로 쓸 수 없다(브리프 373) — 등급을 내린다",
        "set": {"quality_tier": 4},
    }]}, apply=True)
    assert st["corr_ok"] == 1 and _row(ing, pvid)["tier"] == 4


# ── 52차 NA: 되돌리기 표시가 병합기까지 살아 있어야 한다 ────────────────────────
# 표시가 없거나 컬럼 표시와 이름이 겹치면 **병합기가 정정을 못 알아보고 운영에 새 행을
# 만든다**(§522 가 막으려던 사고 그대로). 실측 — 조건 어휘 통일 12,049행을 예행했더니
# 574행이 그렇게 새 행이 됐다(값이 null 인 칸 91 · `conditions.method` 483).

def test_renaming_a_null_valued_condition_key_still_leaves_a_marker(ing, tmp_path):
    """값이 `null` 인 칸의 **이름만** 바꿔도 표시가 남아야 한다.

    `old.get(k) != new.get(k)` 로만 보면 "칸이 없다" 와 "칸이 null 이다" 가 같아져
    표시가 하나도 안 남는다. 표시가 없으면 병합기의 `correction_prior` 가 None 을 돌려
    **정정 전파 분기가 아예 안 돈다.**
    """
    mid, pvid = _seed(ing, conditions={"temperature_C": None, "grade": "A"})
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "조건 어휘 통일 — temperature_C 를 정본 temperature_c 로 옮긴다",
        "set": {"conditions": {"temperature_c": None, "grade": "A"}},
    }]}, apply=True)
    assert st["corr_ok"] == 1
    cond = _row(ing, pvid)["conditions"]
    assert "temperature_C" not in cond and "temperature_c" in cond
    assert "temperature_C_before_correction" in cond
    assert cond["correction_reason"]


def test_condition_cell_named_like_a_column_gets_its_own_namespace(ing, tmp_path):
    """조건 칸 이름이 컬럼 이름과 겹치면 `conditions.` 를 붙인다.

    안 붙이면 `conditions.method` 를 고칠 때 `method_before_correction` 이 남고,
    병합기가 그것을 **컬럼 `method` 의 옛 값**으로 읽어 `where method='DMA tan-delta'`
    로 운영행을 찾는다 — 0건이라 정정이 통째로 miss 가 된다(실측 483행).
    """
    mid, pvid = _seed(ing, conditions={"method": "DMA tan-delta"})
    st = _run(ing, tmp_path, {"corrections": [{
        "target": {"property_value_id": pvid},
        "reason": "조건 어휘 통일 — conditions.method 는 method_detail 이 정본이다",
        "set": {"conditions": {"method_detail": "DMA tan-delta"}},
    }]}, apply=True)
    assert st["corr_ok"] == 1
    cond = _row(ing, pvid)["conditions"]
    assert cond["conditions.method_before_correction"] == "DMA tan-delta"
    assert "method_before_correction" not in cond      # 컬럼 표시와 겹치지 않는다
    assert _row(ing, pvid)["method"] == "handbook"     # 컬럼은 그대로다
