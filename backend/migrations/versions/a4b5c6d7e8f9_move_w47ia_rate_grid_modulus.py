"""47차 IA — 율속 격자로 서 있는 영률 336행을 `youngs_modulus_at_rate` 로 옮기고, base 에는 대표 한 칸만 남긴다.

46차 HA 가 ``mechanical.youngs_modulus_at_rate`` 를 열면서 "base 에 율속 조건을 단 영률
445행이 있고 그중 327행이 ``tensile_strength_at_rate`` 와 1:1 대응한다" 고 넘겼다.
**둘 다 다시 셌다**(브리프 479·496 — 인계 수치는 검증 대상이다).

  율속 조건이 붙은 base 영률 행    인계 445  →  실측 **476**
  형제 `*_at_rate` 와 1:1 대응     인계 327  →  실측 **369** (재료 91·572·573·575·586·2267)

인계는 재료 셋(91·572·575)만 셌는데 **573 SAC205 36행 · 586 SAC(307)-2In 2행 ·
2267 Zytel 3행**이 같은 모양으로 더 있었다(§480 — 매처를 전 재료에 돌려라).
2267 은 형제가 ``strain_rate_s`` 인데 자기는 ``strain_rate_per_s`` 라 이름만으로는 안 걸린다.

**HA 가 "572·575 를 옮기면 두 솔더의 탄성 카드가 통째로 안 선다" 고 한 것도 반만 맞다.**
575 SAC-Q 는 **밀도가 0행이라 지금도 카드가 안 선다**. 573·586·2267 도 같다.
실제로 카드를 잃을 재료는 **572 SAC105 하나뿐**이다(밀도 7,320 보유).

## 오염 조사 — 브리프 491 이 `yield_strength_at_rate` 에서 본 것이 여기에도 있다

491 이 SIGY 폴백을 금지한 근거는 "폴백이라서" 가 아니라 **그 키가 오염돼서** 다.
같은 조사를 율속 영률 476행에 행 단위로 돌렸다. **오염은 있다 — 66행(13.9%)이
단축인장 탄성계수가 아니다.**

| 재료 | 행 | 실제 물리량 |
|---|---|---|
| 54 Foam PU Impact Absorber | 17 | ``loading: uniaxial compression``. 그중 **5행은 ``E_max, densification tangent modulus near 75% strain``** — 같은 재료·같은 율속의 초기 선형계수(0.34~0.56 MPa) 대비 **20.7~68.9 MPa 로 60배**다 |
| 384 PORON XRD LD / 385 XRD HD | 6+6 | 폼 압축계수(SHPB 포함, 0.12~92 MPa) |
| 51 VHB 4905 / 322 VHB 4910 | 22+9 | ``basis: secant modulus P/(lambda-1)`` — **신장률 1.25~2.0 의 시컨트**다. 같은 율속에서도 stretch 가 바뀌면 값이 바뀐다 |
| 322 VHB 4910 | 2 | 점탄성 모델의 **평형·순간 극한계수**(strain rate -> 0 / -> infinity) |
| 2567~2570 Bergquist Gap Pad | 4 | 시트가 ``Young's Modulus`` 라 인쇄했지만 규격이 **ASTM D575 = 고무 압축-변형 시험**이다 |

즉 **키 이름이 물리량을 보장하지 않는다는 491 의 문장이 이 키에도 그대로 성립한다.**
폼 압괴·시컨트·밀실화 접선이 한 키에 섞여 있고, 최저 율속 값을 자동으로 집으면
VHB 는 신장률 2.0 의 시컨트 39.9 kPa 를, 폼은 압축계수를 영률로 내보낸다.

**곁가지 — 율속 축 자체도 오염돼 있다.** 2546~2548 TOPAS 3행의 ``strain_rate_mm_per_min: 1``
과 2567~2570 의 ``strain_rate: "0.01 in/min step rate of strain"`` 은 **크로스헤드 속도**지
변형률속도가 아니다. 이 7행은 이관 대상이 아니다(격자도 아니다 — 재료마다 한 율속뿐).

## 결정 — base 에 대표 한 칸을 남긴다. `dyna_export` 에 폴백을 만들지 않는다.

오염이 있으므로 491 의 금지 근거가 이 키에도 적용된다. 근거를 셋 더 얹는다.

1. **저장소에 이미 규약이 있다.** ``rate_scale_points`` 는 ``yield_strength_at_rate`` 를
   **배율 곡선(형상)** 으로만 쓰고 SIGY 의 **수준**은 base ``yield_strength`` 에서 가져온다.
   ``*_at_rate`` 는 형상이고 base 는 수준이다 — 모듈러스도 같은 자리에 둔다.
2. **대표값 선택기는 율속을 안 본다.** ``_rep_rank`` 는 등급 → 상온거리 → 조건수 → id 만 본다
   (브리프 462 가 방향에서 같은 사고를 냈다). 폴백을 열면 SAC-Q 의 4율속 x 시효 격자에서
   아무 칸이나 E 로 뽑히고, 준정적 SIGY·UTS 와 짝지어져 조용히 틀린다.
3. **자동으로 고르지 않는다** 는 것이 462 의 결론이었다. 여기서도 사람이 지정한 한 칸을 남긴다.

### 무엇을 옮기는가 — 지문 넷을 다 만족하는 행만(id 목록이 아니다, §466·480)

  ① ``mechanical.youngs_modulus`` 이고 조건에 **수치** 변형률속도 축이 있다
     (``strain_rate_s`` · ``strain_rate_1/s`` · ``strain_rate_per_s``. 문자열은 축이 아니다)
  ② 같은 **재료 x 출처** 안에서 그 속도가 **두 값 이상**으로 갈린다 — 격자여야 한다.
     한 율속뿐이면 그것은 축이 아니라 **기록된 시험조건**이고, base 의 대표값 선택이
     잘못 고를 것이 없다. 573(36행 @0.001/s) · 737(14행) · 2363(7행) · 586 · 579 · 966 ·
     1074 · 1075 · 962 · 963 이 여기서 걸러진다.
  ③ 조건이 **인장을 명시**하고(``tensi|tension``), 압축·시컨트·밀실화·저장탄성률·
     점탄성 극한계수 어휘가 **없다**. 위 오염 66행이 여기서 걸러진다.
  ④ 옮기면서 율속 축 이름을 ``strain_rate_s`` 로 정규화한다 — 대상 키의 선언된 조건축이고
     형제 둘의 실측 어휘다(§419. 옛 이름은 ``migrated_rate_axis`` 에 남긴다).

  → **336행 · 재료 다섯**: 91 SAC305 84 · 572 SAC105 85 · 575 SAC-Q 160 · 282 OCA 4 ·
    2267 Zytel 3. (91 의 나머지 3행은 다른 출처의 단일 율속·무조건 행이라 남는다.)

### 무엇을 남기는가 — 이관으로 base 가 **비는** 재료에만 한 칸

572·575·2267 이 그렇다(91·282 는 base 에 다른 행이 남아 손대지 않는다 — 사본을 만들면
그것이야말로 중복 계수다, §435).

남길 칸의 규칙은 ``rate_scale_points`` 가 배율 1.0 의 기준으로 삼는 칸과 **같다** —
**상온에 가장 가까운 계열의 최저 율속**(동률이면 최소 id). 결과가 검산이 된다:

  572 → id 22035 35.0 GPa (298.15 K, 10/s)   575 → id 22146 41.3 GPa (298.15 K, 10/s)
  2267 → id 34821 7.26 GPa (296.15 K, 8.33e-4/s)

**셋 다 이관 전 ``representative_numeric`` 이 이미 뽑던 행이다** — 즉 이 이관은
**카드 값을 바꾸지 않는다.** 카드가 서는 재료 수도 그대로여야 한다.

사본은 중복 계수로 보이면 안 되므로(§435) 조건에 ``representative_of`` ·
``representative_basis`` 를 박고 notes 에 사유를 적는다. **격자 쪽에는 구멍을 내지 않는다** —
336행을 다 옮기고 base 에 사본을 따로 넣는다. 격자에서 한 칸을 빼는 쪽이 더 안 보인다.

**남긴 칸이 준정적이 아니라는 사실은 숨기면 안 된다.** 572·575 의 Cai 격자에는
준정적 칸이 아예 없어 최저 율속이 **10/s(충격 영역)** 다. 그래서 같은 커밋에서
``dyna_export._COND_SHOW`` 에 ``strain_rate_s`` 를 추가했다 — 그 전에는 ``strain_rate_1/s``
만 있어 **SAC105 카드가 10/s 값을 율속 표시 없이 싣고 있었다.**

**예행** — 옛 리비전 운영 DB 사본(alembic ``888056f1c5b8``, 재료 544 · 값 21,268)으로 돌렸다.
그 DB 에는 대상 키 정의가 없어(§482) 체인의 e2f3a4b5c6d7 이 넣고 이 리비전이 4행(재료 282)만
옮긴다 — 나머지 62행은 전부 위 오염·단일율속이라 걸러진다. 정의가 없는 아주 오래된 DB 를 위해
여기서도 **없으면 넣는다**.

같은 파동의 47차 ID 가 35초 먼저 ``f3a4b5c6d7e8`` 을 잡았다(§504 — 병렬 배치는 트리를 공유한다).
리비전을 갈고 **ID 위에 얹었다** — 둘은 독립이지만(ID 는 새 키 정의, 여기는 기존 키의 행 이동)
같은 down_revision 을 쓰면 head 가 둘이 되어 파동 전체의 pytest 가 죽는다.

Revision ID: a4b5c6d7e8f9
Revises: f3a4b5c6d7e8
"""
from __future__ import annotations

import json
import re

import sqlalchemy as sa
from alembic import op

revision = "a4b5c6d7e8f9"
down_revision = "f3a4b5c6d7e8"
branch_labels = None
depends_on = None

SRC_KEY = "mechanical.youngs_modulus"
DST_KEY = "mechanical.youngs_modulus_at_rate"
# e2f3a4b5c6d7 · app/property_taxonomy.py 와 **같은 내용**이어야 한다.
_DST_DEF = (DST_KEY, "mechanical", "변형률속도별 영률", None, "Pa", "numeric",
            ["strain_rate_s", "temperature_k"], None)

_AXES = ("strain_rate_s", "strain_rate_1/s", "strain_rate_per_s")
_CANON_AXIS = "strain_rate_s"
# 조건 중 "이 값이 무엇인가" 를 말하는 칸만 본다. 산문(notes)은 보지 않는다 — 브리프 472 가
# 부정문에 걸린 사고를 냈다. 구조를 보고 판정한다.
_DESC_KEYS = ("loading", "test_method", "definition", "property_definition",
              "basis", "regime", "measurement", "test_mode", "mode")
_TENSION = re.compile(r"tensi|tension", re.I)
_EXCLUDE = re.compile(r"compress|secant|densific|storage modulus|strain rate ->", re.I)
_ROOM_K = 298.15
_MARK = "[47차 IA]"


def _load(cond):
    try:
        d = json.loads(cond) if cond else {}
    except (TypeError, ValueError):
        d = {}
    return d if isinstance(d, dict) else {}


def _dump(d) -> str:
    return json.dumps(d, ensure_ascii=False)


def _axis(d) -> str | None:
    """수치 변형률속도 축의 이름. 문자열 값('0.01 in/min ...')은 축이 아니다."""
    for k in _AXES:
        if isinstance(d.get(k), (int, float)) and not isinstance(d.get(k), bool):
            return k
    return None


def _is_tensile_modulus(d) -> bool:
    desc = " | ".join(str(d.get(k, "")) for k in _DESC_KEYS)
    return bool(_TENSION.search(desc)) and not _EXCLUDE.search(desc)


def _temp_distance(d) -> float:
    t = d.get("temperature_k")
    return abs(float(t) - _ROOM_K) if isinstance(t, (int, float)) else 1e9


def _ensure_definition(conn) -> None:
    if conn.execute(sa.text("select 1 from property_definition where key=:k"),
                    {"k": DST_KEY}).fetchone():
        return
    key, domain, name, symbol, unit, vtype, axes, std = _DST_DEF
    conn.execute(sa.text(
        "insert into property_definition "
        "(key, domain, name, symbol, si_unit, value_type, condition_axes, test_standard) "
        "values (:k, :d, :n, :sy, :u, :v, :a, :s)"),
        {"k": key, "d": domain, "n": name, "sy": symbol, "u": unit, "v": vtype,
         "a": json.dumps(axes, ensure_ascii=False), "s": std})


def _candidates(conn) -> list[tuple]:
    """이관 지문 ①②③ 을 통과한 행 → [(id, material_id, source_id, cond_dict, axis)]."""
    rows = conn.execute(sa.text(
        "select id, material_id, source_id, conditions from property_value "
        "where property_key=:k and value_num is not null"), {"k": SRC_KEY}).fetchall()
    hits = []
    for pid, mid, sid, cond in rows:
        d = _load(cond)
        ax = _axis(d)
        if ax is None or not _is_tensile_modulus(d):
            continue
        hits.append((pid, mid, sid, d, ax))
    # ② 같은 재료 x 출처 안에서 율속이 둘 이상으로 갈려야 격자다.
    grid: dict[tuple, set] = {}
    for pid, mid, sid, d, ax in hits:
        grid.setdefault((mid, sid), set()).add(float(d[ax]))
    return [h for h in hits if len(grid[(h[1], h[2])]) >= 2]


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if not insp.has_table("property_value") or not insp.has_table("property_definition"):
        return
    _ensure_definition(conn)

    moved = _candidates(conn)
    by_mat: dict[int, list] = {}
    for pid, mid, sid, d, ax in moved:
        by_mat.setdefault(mid, []).append((pid, d, ax))
        if d.get("migrated_from"):
            continue                                    # 멱등 — 이미 옮긴 행
        # 이미 `strain_rate_s` 인 행은 **건드리지 않는다** — 값의 형(10 vs 10.0)과 키 순서가
        # 바뀌면 되돌렸을 때 원문과 글자가 달라진다. 이름이 다른 행만 옮겨 담는다.
        nd = dict(d)
        if ax != _CANON_AXIS:
            nd["migrated_rate_axis"] = ax               # 되돌릴 수 있게 옛 이름을 남긴다
            nd[_CANON_AXIS] = nd.pop(ax)
        nd["migrated_from"] = SRC_KEY
        conn.execute(sa.text(
            "update property_value set property_key=:nk, conditions=:c, "
            "notes = coalesce(notes,'') || :n where id=:i"),
            {"nk": DST_KEY, "c": _dump(nd), "i": pid,
             "n": f"\n{_MARK} 율속 격자라 {SRC_KEY} 에서 옮겼다 — 형제 "
                  "tensile_strength_at_rate / yield_strength_at_rate 와 같은 자리다."})

    # base 가 **비는** 재료에만 대표 한 칸을 남긴다.
    for mid, rows in by_mat.items():
        left = conn.execute(sa.text(
            "select count(*) from property_value where property_key=:k and material_id=:m"),
            {"k": SRC_KEY, "m": mid}).fetchone()[0]
        if left:
            continue
        pid, d, ax = min(rows, key=lambda r: (_temp_distance(r[1]), float(r[1][r[2]]), r[0]))
        src = conn.execute(sa.text(
            "select value_num, value_text, unit, uncertainty, conditions, method, "
            "quality_tier, source_id, source_detail, notes from property_value where id=:i"),
            {"i": pid}).fetchone()
        nd = _load(src[4])
        nd.pop("migrated_from", None)
        nd.pop("migrated_rate_axis", None)
        nd["representative_of"] = DST_KEY
        nd["representative_basis"] = (
            "율속 격자의 기준 칸(상온에 가장 가까운 계열의 최저 율속)을 base 대표값으로 남긴 것이다. "
            "독립 측정이 아니라 같은 칸의 사본이므로 두 번 세면 안 된다(브리프 435). "
            "격자 전체는 " + DST_KEY + " 에 있다.")
        conn.execute(sa.text(
            "insert into property_value (material_id, property_key, value_num, value_text, "
            "unit, uncertainty, conditions, method, quality_tier, source_id, source_detail, notes) "
            "values (:m, :k, :vn, :vt, :u, :un, :c, :me, :t, :s, :sd, :n)"),
            {"m": mid, "k": SRC_KEY, "vn": src[0], "vt": src[1], "u": src[2], "un": src[3],
             "c": _dump(nd), "me": src[5], "t": src[6], "s": src[7], "sd": src[8],
             # 원본 행의 notes 에는 방금 붙인 "옮겼다" 줄이 들어 있다 — 사본에는 맞지 않으므로 뗀다.
             "n": (src[9] or "").split(f"\n{_MARK}")[0]
                  + f"\n{_MARK} **이 행은 사본이다.** 이관으로 base 가 비면 "
                  f"dyna_export 의 K_E 가 사라져 카드가 통째로 안 선다. 율속 격자에서 기준 칸 "
                  f"하나만 base 에 남긴다 — 값·출처·등급은 {DST_KEY} 의 같은 칸과 동일하다. "
                  "SIGY 폴백을 만들지 않은 이유는 브리프 491·이 리비전 docstring 을 봐라."})


def downgrade() -> None:
    """표시가 남아 있는 행만 되돌린다 — 새로 들어온 행은 건드리지 않는다."""
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    conn.execute(sa.text(
        "delete from property_value where property_key=:k "
        "and conditions like :p"), {"k": SRC_KEY, "p": '%"representative_of": "' + DST_KEY + '"%'})
    for pid, cond, notes in conn.execute(sa.text(
            "select id, conditions, notes from property_value where property_key=:k "
            "and conditions like '%\"migrated_from\": \"mechanical.youngs_modulus\"%'"),
            {"k": DST_KEY}).fetchall():
        d = _load(cond)
        d.pop("migrated_from", None)
        old = d.pop("migrated_rate_axis", None)
        if old:
            d[old] = d.pop(_CANON_AXIS)
        n = (notes or "").split(f"\n{_MARK}")[0] or None
        conn.execute(sa.text(
            "update property_value set property_key=:k, conditions=:c, notes=:n where id=:i"),
            {"k": SRC_KEY, "c": _dump(d), "n": n, "i": pid})
