# 완전 중복 물성값 병합 — 값·출처 동일, 조건 키 표기만 다른 쌍을 정보량 많은 쪽으로 통합.
import json
import re
import sqlite3
import sys

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
DRY = "--apply" not in sys.argv

# 조건 키 정규화(표기 흔들림 흡수) — 어느 쪽이 더 정보량 많은지 비교하기 위함.
ALIAS = {"test": "standard", "test_method": "standard", "temp_C": "temperature_C",
         "freq_Hz": "frequency_Hz", "frequency_kHz": "frequency_Hz",
         "frequency_hz": "frequency_Hz", "frequency_MHz": "frequency_Hz",
         "frequency_GHz": "frequency_Hz", "temp_range_C": "temperature_range_C",
         "load_gf": "load_g", "line": "spectral_line",
         # 이방성 물성의 방향 표기는 수집자마다 axis/direction으로 갈린다.
         "direction": "axis", "orientation": "axis"}
# 단위가 다른 주파수 표기를 Hz로 환산해 같은 조건인지 정확히 비교한다.
FREQ_SCALE = {"frequency_kHz": 1e3, "frequency_MHz": 1e6, "frequency_GHz": 1e9}
# 방향 값 표기 흔들림("in-plane (X,Y)" ↔ "in-plane") 흡수. 같은 물리 방향만 묶는다.
AXIS_CANON = {"in-plane": "in-plane", "in plane": "in-plane", "x-y": "in-plane",
              "xy": "in-plane", "x,y": "in-plane", "through-plane": "through-plane",
              "through plane": "through-plane", "z": "through-plane",
              "thickness": "through-plane", "normal": "through-plane"}


def _canon_axis(v):
    s = str(v).lower().split("(")[0].strip().strip(",")
    return AXIS_CANON.get(s, v)


# 두께로 등급을 나누는 제품(PGS 등)은 grade="25 um"과 thickness_um=25가 섞여 들어온다.
_GRADE_UM = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*(?:um|µm|μm)\s*$", re.I)


def norm_cond(raw):
    if not raw:
        return {}
    try:
        d = json.loads(raw)
    except Exception:
        return {}
    # 이중 인코딩된 조건("{...}"이 문자열로 한 번 더 감싸인 경우)을 한 번 더 푼다.
    if isinstance(d, str):
        try:
            d = json.loads(d)
        except Exception:
            return {}
    if not isinstance(d, dict):
        return {}
    out = {}
    for k, v in (d or {}).items():
        nk = ALIAS.get(k, k)
        if k in FREQ_SCALE and isinstance(v, (int, float)):
            v = v * FREQ_SCALE[k]
        if nk == "axis":
            v = _canon_axis(v)
        # grade="25 um" 을 thickness_um=25 로 흡수(같은 등급을 다르게 적은 것뿐이다).
        if nk == "grade" and isinstance(v, str) and _GRADE_UM.match(v):
            out["thickness_um"] = float(_GRADE_UM.match(v).group(1))
            continue
        out[nk] = v
    return out


def score(cond, notes):
    """정보량 점수 — 조건 키 수 + 표준 명시 + 노트 유무."""
    return (len(cond), 1 if "standard" in cond else 0, 1 if notes else 0)


c = sqlite3.connect(DB)
groups = c.execute("""select material_id, property_key, value_num, source_id, group_concat(id)
    from property_value
    group by material_id, property_key, value_num, source_id having count(*)>1""").fetchall()

merged = deleted = 0
for mid, key, val, sid, ids in groups:
    rows = c.execute(
        "select id, conditions, notes from property_value where id in (%s)" % ids).fetchall()
    # 정규화 조건이 동일한 것끼리만 묶어서 병합 — 조건이 다르면 별개 측정이다.
    # (Isola Dk 3.92 @5GHz와 @10GHz는 값·출처가 같아도 서로 다른 측정이다.)
    # 조건별로 버킷을 나눠야 A/A/B가 섞여 있어도 A 두 건을 놓치지 않는다.
    buckets: dict[str, list] = {}
    for rid, raw, notes in rows:
        cond = norm_cond(raw)
        sig = json.dumps({k: str(v) for k, v in sorted(cond.items())}, ensure_ascii=False)
        buckets.setdefault(sig, []).append((score(cond, notes), rid, cond, notes))
    for sig, cand in buckets.items():
        if len(cand) < 2:
            continue
        cand.sort(reverse=True)
        keep, drop = cand[0], cand[1:]
        # 버리는 쪽의 노트 중 keeper에 없는 정보는 흡수(정보 손실 방지).
        kcond, knotes = dict(keep[2]), keep[3]
        for _, _, _, notes in drop:
            if notes and (not knotes or notes not in knotes):
                knotes = f"{knotes} {notes}".strip() if knotes else notes
        name = c.execute("select name from material where id=?", (mid,)).fetchone()[0]
        print(f"  keep#{keep[1]} drop={[d[1] for d in drop]}  {name[:24]:24s} {key[:30]:30s}")
        print(f"      조건 → {sig[:70]}")
        if not DRY:
            c.execute("update property_value set conditions=?, notes=? where id=?",
                      (json.dumps(kcond, ensure_ascii=False) if kcond else None, knotes, keep[1]))
            for _, rid, _, _ in drop:
                c.execute("delete from property_value where id=?", (rid,))
                deleted += 1
        merged += 1

if not DRY:
    c.commit()
print(f"\n{'[DRY-RUN]' if DRY else '[APPLIED]'} 병합 그룹 {merged}, 삭제 {deleted if not DRY else '(예정 %d)' % sum(1 for g in groups)}")
tot = c.execute("select count(*) from property_value").fetchone()[0]
left = c.execute("""select count(*) from (select 1 from property_value
    group by material_id, property_key, value_num, source_id having count(*)>1)""").fetchone()[0]
print(f"총 물성값: {tot}   남은 중복 그룹: {left}")
