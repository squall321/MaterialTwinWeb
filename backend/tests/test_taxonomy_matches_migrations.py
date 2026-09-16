# 물성 키를 여는 마이그레이션과 부팅 시드 분류표가 같은 내용인지 — 76차 회귀시험.
#
# 키는 두 곳에 산다. 라이브는 alembic 마이그레이션으로 받고, 새로 만든 DB 는 부팅 시드
# (`db._seed_reference_data` → `property_taxonomy.seed_property_definitions`)로 받는다.
# 마이그레이션 머리 주석이 늘 *"property_taxonomy.py 의 N차 블록과 같은 내용이어야 한다"*
# 라고 적어 왔지만 **주석이라 아무것도 막지 못했다** — 70~73차에 연 키 넷
# (withstand_voltage_surface · relaxation_modulus_normalized · tts_shift_factor ·
# relaxation_modulus)이 마이그레이션에만 들어가고 분류표에서 빠졌다. 새로 만든 DB 에는
# 그 넷이 없었다.
#
# 반대 방향도 위험하다. 시드는 **upsert** 라 분류표와 다른 기존 정의를 부팅할 때 조용히
# 덮어쓴다. 그래서 「있다」만이 아니라 **필드 일곱이 같다**를 본다.
from __future__ import annotations

import ast
import glob
from pathlib import Path

from app.property_taxonomy import all_definitions

_COLS = ("key", "domain", "name", "symbol", "si_unit", "value_type",
         "condition_axes", "test_standard")
_MIG = Path(__file__).resolve().parents[1] / "migrations" / "versions"


def _migration_defs():
    """키를 여는 마이그레이션의 `_DEFS`(8요소 튜플 목록)를 코드 실행 없이 읽는다."""
    for f in sorted(glob.glob(str(_MIG / "*.py"))):
        tree = ast.parse(Path(f).read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if not any(getattr(t, "id", None) == "_DEFS" for t in node.targets):
                continue
            try:
                defs = ast.literal_eval(node.value)
            except ValueError:
                continue
            for t in defs or []:
                if isinstance(t, tuple) and len(t) == 8:
                    yield Path(f).name, dict(zip(_COLS, t))


def test_every_migrated_key_is_in_the_boot_seed():
    tax = {d["key"] for d in all_definitions()}
    missing = [(f, d["key"]) for f, d in _migration_defs() if d["key"] not in tax]
    assert not missing, f"마이그레이션에만 있고 분류표에 없는 키 — 새 DB 에 안 생긴다: {missing}"


def test_migrated_fields_equal_the_boot_seed():
    """다르면 부팅 시드가 라이브 정의를 조용히 덮어쓴다."""
    tax = {d["key"]: d for d in all_definitions()}
    diff = []
    for f, d in _migration_defs():
        t = tax.get(d["key"])
        if t is None:
            continue
        for c in _COLS[1:]:
            if t[c] != d[c]:
                diff.append((f, d["key"], c, d[c], t[c]))
    assert not diff, f"마이그레이션과 분류표가 다르다: {diff[:5]}"


def test_there_are_migrations_to_check():
    """읽는 방법이 깨져 0개를 읽고 통과하는 일을 막는다."""
    assert sum(1 for _ in _migration_defs()) >= 28
