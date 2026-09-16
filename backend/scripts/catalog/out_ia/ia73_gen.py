# 73차 IA — 영률 칸에 앉은 굽힘탄성률 101행의 표기를 바로잡고, 굽힘값을 올바른 키로도 넣는 생성기
#
# 라이브 DB 를 **읽기 전용(mode=ro)** 으로만 연다. 값·단위·등급·method·출처는 한 칸도 바꾸지 않는다.
# conditions 는 통째 치환이므로 기존 조건을 전부 읽어 보존한 뒤 표기 칸만 더한다.
#
# 이 배치가 72차 HB 와 다른 점 — **모드 판정 창을 의식한다.**
# 73차 직전 커밋 d57cd59 가 대표값 선택기에 시험모드 항을 넣었다. 판정은 conditions 의
# 아홉 칸(test_standard·test_method·test·test_mode·test_geometry·strength_property·
# method_detail·test_condition·loading_mode)만 본다. 그래서
#   ① 표기는 반드시 이 아홉 칸 안에 넣고,
#   ② **부정문("인장 탄성률은 미인쇄")은 이 칸 밖으로 뺀다** — 창 안에 인장 낱말이 있으면
#      굽힘 지문과 함께 잡혀 `판단 보류`(1)가 되고, 그러면 굽힘 행이 미표기 행과 같은 자리에 선다.
import json
import os
import re
import sqlite3
import sys

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR", ""), "materialtwin.db")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT_CORR = os.path.join(HERE, "ia73_01_corrections.json")
OUT_MAT = os.path.join(HERE, "ia73_02_materials.json")
BATCH = "73차 IA"

# 모드 판정 창(app/catalog_compare._mode_rank 와 같아야 한다).
WIN = ("test_standard", "test_method", "test", "test_mode", "test_geometry",
       "strength_property", "method_detail", "test_condition", "loading_mode")
FLEX_RX = re.compile(r"D\s?790|C\s?6481|K\s?7171|ISO\s?178|TM-650\s*2\.4\.4"
                     r"|flexur|bending|3-?point|three-?point|굽힘|曲げ|彎曲", re.I)
TENS_RX = re.compile(r"D\s?3039|D\s?638|D\s?882|E\s?111|K\s?7161|K\s?7113|ISO\s?527"
                     r"|tensil|인장|引張|引っ張|拉伸", re.I)
AUDIT = ("correction_reason", "corrected_by", "correction_evidence")

# 브리프가 못박은 과대 경고문. 상한 55 % 는 71차 GB·72차 HB 가 Panasonic R-5785(N) 위사에서 실측했다.
WARN = ("이 값은 굽힘탄성률이며 인장탄성률이 아니다. 해석에 쓸 때 12~55% 과대일 수 있다 — "
        "하한 12~23 % 는 68차 DC·71차 GB 실측이고, 상한 55 % 는 Panasonic 2021-03 특성일람표의 "
        "R-5785(N) 위사(`曲げ弾性係数` 18 GPa 대 `ヤング率(引張りモード)` 11.6 GPa)에서 나왔다.")

# 균질 등방 금속에는 위 경고문을 쓰지 않는다(72차 HB §7-3).
METAL_NOTE = ("이 값은 3점굽힘 하중 모드에서 얻었다. **과대 경고는 붙이지 않는다** — 균질 등방 "
              "금속에서는 3점굽힘 탄성률이 인장 탄성률과 이론적으로 같기 때문이다. 12~55 % 폭은 "
              "충전 고분자·직물 적층판의 두께방향 불균질에서 나오는 것이라 여기 적용되지 않는다. "
              "소결 페이스트는 기공률 구배가 있을 수 있어 중간이다.")


def mode_rank(cond: dict, want: str = "tensile") -> int:
    blob = " ".join(str(cond.get(k, "")) for k in WIN)
    f, t = bool(FLEX_RX.search(blob)), bool(TENS_RX.search(blob))
    if f == t:
        return 1
    return 0 if (("tensile" if t else "flexural") == want) else 2


def base(cond: dict) -> dict:
    """감사용 칸을 뺀 기존 조건. 되돌리기 표시는 적재기가 다시 만든다."""
    return {k: v for k, v in cond.items() if k not in AUDIT}


def main() -> int:
    if not os.path.exists(DB):
        print(f"DB 가 없다: {DB} — MATERIALTWIN_DATA_DIR 를 확인하라", file=sys.stderr)
        return 2
    con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    def row(pid):
        r = con.execute(
            "select pv.id, pv.material_id, pv.property_key, pv.value_num, pv.unit,"
            "       pv.quality_tier, pv.method, pv.source_id, pv.conditions, pv.notes,"
            "       m.name mname, s.url surl, s.title stitle, s.doi sdoi, s.kind skind,"
            "       s.publisher spub, s.authors sauth, s.year syear, s.local_path spath"
            "  from property_value pv join material m on m.id = pv.material_id"
            "  left join source s on s.id = pv.source_id where pv.id = ?", (pid,)).fetchone()
        assert r is not None, f"pv{pid} 이 라이브에 없다"
        return r

    corrections: list = []
    mat_rows: list = []          # (material_id, source_row, property dict)

    def add(pid, reason, cond_new, note_add, want="tensile", expect=2):
        r = row(pid)
        assert r["property_key"] == "mechanical.youngs_modulus", (pid, r["property_key"])
        got = mode_rank(cond_new, want)
        assert got == expect, (f"pv{pid} 정정 후 모드판정 {got} ≠ 기대 {expect} — "
                               f"창 안 문자열을 다시 봐라: "
                               f"{ {k: cond_new.get(k) for k in WIN if cond_new.get(k)} }")
        old_note = (r["notes"] or "").strip()
        notes = (old_note + "\n\n" + note_add) if old_note else note_add
        corrections.append({
            "target": {"property_value_id": pid},
            "by": BATCH,
            "reason": reason,
            "set": {"conditions": cond_new, "notes": notes},
        })
        return r

    # ══════════════════════════════════════════════════════════════════════════
    # G1 · G1b — 재료 92·93. 벤더가 `Flexural Modulus` 라고 **인쇄한** 값 66행
    # ══════════════════════════════════════════════════════════════════════════
    G1_REASON = (
        "벤더가 인쇄한 행 이름이 `Flexural Modulus` 인데 값이 영률 칸에 t1 로 앉아 있다. "
        "73차 IA 가 원문을 다시 열어 확인했다 — CAPLINQ 제품페이지의 Hysol/LINQSOL EMC 비교표와 "
        "Henkel LOCTITE ECCOBOND TDS 는 `Flexural modulus`·`Flexural strength`·"
        "`Storage Modulus by DMA` 만 인쇄하고 **인장 계열 행은 한 줄도 없다**(GR920·GR750·"
        "EMC-9012·GR15F-MOD2C·E 1216M 다섯 문서 전수, `Tensile` 적중 0). 그러므로 값을 진짜 "
        "인장값으로 갈아치울 원문 근거가 없다 — 값·단위·등급·method·출처는 그대로 두고 "
        "conditions 의 시험모드 표기와 notes 만 고친다. 같은 수를 "
        "`mechanical.flexural_modulus` 로도 넣어 굽힘 정보가 올바른 키에 서게 한다"
        "(ia73_02_materials.json).")

    g1_ids, g1b_ids = [], []
    for r in con.execute(
            "select id, conditions from property_value"
            " where material_id in (92, 93) and property_key='mechanical.youngs_modulus'"
            " order by material_id, id").fetchall():
        md = str(json.loads(r["conditions"] or "{}").get("method_detail") or "")
        if md.startswith("flexural modulus"):
            g1_ids.append(r["id"])
        elif "3-point bending" in md:      # DMA 저장탄성률을 3점굽힘 지그로 잰 행
            g1b_ids.append(r["id"])
    assert len(g1_ids) + len(g1b_ids) == 66, (len(g1_ids), len(g1b_ids))

    for pid in g1_ids:
        r = row(pid)
        old = json.loads(r["conditions"] or "{}")
        new = base(old)
        new["test_mode"] = "flexural"
        new["loading_mode"] = "bending"
        new["reported_as_youngs_modulus"] = True
        new["tensile_modulus_in_source"] = (
            "이 문서에는 인장 계열 행이 없다 — 73차 IA 가 원문 다섯 장을 다시 열어 확인했다.")
        new["duplicate_of"] = (
            "mechanical.flexural_modulus — 73차 IA 가 같은 출처·같은 수를 그 키에 세웠다"
            "(ia73_02_materials.json). 지우지 않았다 — 삭제는 사람이 정한다.")
        new["corrected_by_73ia"] = (
            f"{BATCH} — 시험모드 표기 정정(G1 벤더 인쇄 굽힘탄성률). 값·단위·등급·method·출처는 그대로다.")
        add(pid, G1_REASON, new, f"[{BATCH} 표기 정정] {WARN}")
        # 같은 수를 굽힘 키로도 넣는다.
        cond_f = {k: v for k, v in base(old).items()
                  if not k.endswith("_before_correction")
                  and k not in ("method_detail", "test_mode", "loading_mode")}
        cond_f["test_mode"] = "flexural"
        cond_f["loading_mode"] = "bending"
        cond_f["test_method"] = "3-point bend"
        cond_f["source_row_name"] = "Flexural Modulus (벤더 인쇄 행 이름 그대로)"
        cond_f["added_by_73ia"] = (
            f"{BATCH} — 같은 출처·같은 수를 올바른 키로 옮겨 적는다. 영률 칸의 원행"
            f"(pv{pid})은 지우지 않았다 — 삭제는 사람이 정한다.")
        mat_rows.append((r, {
            "key": "mechanical.flexural_modulus",
            "value": r["value_num"], "unit": r["unit"],
            "method": r["method"], "quality_tier": r["quality_tier"],
            "conditions": cond_f,
            "notes": (f"[{BATCH}] 벤더가 `Flexural Modulus` 로 인쇄한 값을 굽힘 키에 세운다. "
                      f"같은 수가 `mechanical.youngs_modulus` pv{pid} 에도 있다(73차 IA 가 그 행에 "
                      f"`test_mode: flexural` 을 달아 대표값 선택기가 뒤로 보내게 했다). "
                      f"원행 notes: {(r['notes'] or '')[:220]}"),
        }))

    for pid in g1b_ids:
        r = row(pid)
        new = base(json.loads(r["conditions"] or "{}"))
        new["test_mode"] = "flexural"
        new["loading_mode"] = "bending"
        new["reported_as_youngs_modulus"] = True
        new["corrected_by_73ia"] = (
            f"{BATCH} — 시험모드 표기 정정(G1b DMA 3점굽힘 저장탄성률).")
        add(pid, (G1_REASON + " 이 행은 벤더가 `Storage Modulus E' by DMA, 3-point bending` "
                  "으로 인쇄한 값이라 **굽힘 키로 복사하지 않았다** — 원문이 그것을 "
                  "`flexural modulus` 라고 부르지 않기 때문이다. 하중 모드가 굽힘이라는 "
                  "표기만 조건에 내린다."),
            new, f"[{BATCH} 표기 정정] {WARN}")

    # ══════════════════════════════════════════════════════════════════════════
    # G2 — 재료 245·246·266·299. **부정문이 판정 창 안에 있어 굽힘이 안 잡히던 6행**
    # ══════════════════════════════════════════════════════════════════════════
    G2 = {
        12981: ("ASTM D790", 245), 12982: ("ASTM D790", 245),
        12978: ("ASTM D790", 246), 12979: ("ASTM D790", 246),
        12965: ("ISO 178", 266), 12966: ("ISO 178", 299),
    }
    G2_REASON = (
        "이 행은 이미 `method_detail` 에 `굴곡 탄성률 (…) — 인장 탄성률은 이 TDS에 미인쇄` 라고 "
        "정직하게 적혀 있었다. 그런데 **그 정직함이 기계에는 반대로 작동했다** — 73차 직전 커밋 "
        "d57cd59 가 넣은 대표값 선택기의 시험모드 항은 conditions 의 시험 식별 아홉 칸만 읽고 "
        "부정문을 못 읽는다. 한 문자열 안에 굽힘 지문(D790/ISO 178)과 인장 낱말이 같이 있으면 "
        "`판단 보류`가 되어, 이 행이 **모드를 안 밝힌 행과 같은 자리**에 선다. 그래서 굽힘 지문은 "
        "판정 창 안(`test_standard`·`test_mode`·`loading_mode`)에 두고, **인장 부정문은 창 밖"
        "(`tensile_modulus_in_source`)으로 옮긴다.** 값·단위·등급·method·출처는 그대로다.")
    G2_TWIN = {12981: "pv4017", 12982: "pv4018", 12978: "pv4038", 12966: "pv7180",
               12979: None, 12965: None}
    for pid, (std, _mid) in G2.items():
        r = row(pid)
        old = json.loads(r["conditions"] or "{}")
        new = base(old)
        new["method_detail"] = f"굴곡 탄성률 — 3점 굽힘 ({std})"
        new["test_standard"] = std
        new["test_mode"] = "flexural"
        new["loading_mode"] = "bending"
        new["reported_as_youngs_modulus"] = True
        new["tensile_modulus_in_source"] = (
            "이 TDS 는 인장 탄성률 행을 인쇄하지 않는다 — 그래서 이 굽힘값이 영률 칸에 프록시로 "
            "들어왔다. (판정 창 밖에 둔다: 창 안에 두면 굽힘 지문과 같이 잡혀 판단 보류가 된다.)")
        tw = G2_TWIN[pid]
        new["duplicate_of"] = (
            f"mechanical.flexural_modulus {tw} (같은 수·같은 출처)." if tw else
            "mechanical.flexural_modulus — 73차 IA 가 같은 출처·같은 수를 그 키에 세웠다"
            "(ia73_02_materials.json).") + " 지우지 않았다 — 삭제는 사람이 정한다."
        new["corrected_by_73ia"] = f"{BATCH} — 부정문을 판정 창 밖으로 옮기고 굽힘 표기를 창 안에 세운다."
        add(pid, G2_REASON, new, f"[{BATCH} 표기 정정] {WARN}")

    # 굽힘 키에 같은 수가 **없는** 두 행만 굽힘 키로도 넣는다(나머지 넷은 이미 있다).
    for pid, direction in ((12979, "TD"), (12965, None)):
        r = row(pid)
        std, _ = G2[pid]
        cond_f = {"test_standard": std, "test_mode": "flexural", "loading_mode": "bending",
                  "temperature_c": json.loads(r["conditions"])["temperature_c"],
                  "added_by_73ia": (f"{BATCH} — 이 재료의 `mechanical.flexural_modulus` 에 이 수가 "
                                    f"없었다. 영률 칸의 원행 pv{pid} 은 지우지 않았다.")}
        if direction:
            cond_f["direction"] = direction
        for k in ("grade", "filler", "direction_verbatim"):
            v = json.loads(r["conditions"]).get(k)
            if v:
                cond_f[k] = v
        mat_rows.append((r, {
            "key": "mechanical.flexural_modulus",
            "value": r["value_num"], "unit": r["unit"],
            "method": r["method"], "quality_tier": r["quality_tier"],
            "conditions": cond_f,
            "notes": (f"[{BATCH}] TDS 가 `{std}` 로 인쇄한 굴곡 탄성률을 굽힘 키에 세운다 — "
                      f"이 재료의 굽힘 키에 이 수가 없었다. 같은 수가 "
                      f"`mechanical.youngs_modulus` pv{pid} 에도 있다. "
                      f"원행 notes: {(r['notes'] or '')[:220]}"),
        }))

    # ══════════════════════════════════════════════════════════════════════════
    # G3 — 72차 HB 가 고쳤는데 **선택기가 못 읽던 2행**(Bansal 1997)
    # ══════════════════════════════════════════════════════════════════════════
    G3_REASON = (
        "72차 HB 가 `test_mode: flexural` 을 달았는데도 이 행은 여전히 `판단 보류`로 읽힌다. "
        "`test_method` 문자열 끝의 `strain gauge on tensile surface` 가 판정 창 안에서 인장으로 "
        "잡히기 때문이다 — 굽힘 지문과 인장 낱말이 한 창에 같이 들어가면 선택기는 판단을 보류한다. "
        "**HB 의 43행 중 이 둘만 의도대로 반영되지 않았다**(41/43 은 굽힘으로 읽힌다). "
        "스트레인 게이지 부착 위치는 시험모드가 아니라 계측 방식이므로 창 밖 "
        "`strain_measurement` 로 옮긴다. 값·단위·등급·method·출처·HB 의 판정은 그대로다.")
    for pid in (32785, 32788):
        r = row(pid)
        old = json.loads(r["conditions"] or "{}")
        new = base(old)
        tm = str(new.get("test_method") or "")
        new["test_method"] = re.sub(r",?\s*strain gauge on tensile surface\s*", "", tm).strip().rstrip(",")
        new["strain_measurement"] = ("strain gauge on tensile surface — 처짐 컴플라이언스 역산이 "
                                     "아니라 실측 변형률이다(계측 방식이지 시험모드가 아니다).")
        new["corrected_by_73ia"] = (
            f"{BATCH} — 72차 HB 의 굽힘 표기가 선택기에 반영되도록 판정 창을 정리한다.")
        add(pid, G3_REASON, new, f"[{BATCH} 표기 정정] {WARN}")

    # ══════════════════════════════════════════════════════════════════════════
    # G4 — 균질 등방 금속 15행. **과대 경고문을 붙이지 않는다**
    # ══════════════════════════════════════════════════════════════════════════
    G4_REASON = (
        "3점굽힘(DMTA·미소시편)에서 얻은 탄성률이 영률 칸에 있다. 시험모드를 판정 창 안에 "
        "명시한다. **다만 12~55 % 과대 경고문은 붙이지 않는다** — 균질 등방 금속에서는 3점굽힘 "
        "탄성률이 인장 탄성률과 이론적으로 같고, 그 폭은 충전 고분자·직물 적층판의 두께방향 "
        "불균질에서 나오는 것이다(72차 HB §7-3). 소결 페이스트는 기공률 구배가 있을 수 있어 "
        "중간이다. 값·단위·등급·method·출처는 그대로다.")
    G4 = [31959, 31960, 31961, 31969, 31970, 31971, 31977, 31978, 31979,
          31986, 31987, 31988, 25446, 25461, 25472]
    for pid in G4:
        r = row(pid)
        new = base(json.loads(r["conditions"] or "{}"))
        new["test_mode"] = "flexural"
        new["loading_mode"] = "bending"
        new["modulus_equivalence"] = (
            "균질 등방 금속에서는 3점굽힘 탄성률과 인장 탄성률이 이론적으로 같다. 이 행에는 "
            "굽힘 과대 보정을 적용하지 마라. (판정 창 밖에 둔다 — 창 안에 두면 판단 보류가 된다.)")
        new["corrected_by_73ia"] = f"{BATCH} — 시험모드 표기만 명시(G4 균질 금속·소결 페이스트)."
        add(pid, G4_REASON, new, f"[{BATCH} 표기 정정] {METAL_NOTE}")

    # G4b — 같은 재료(962)의 **진짜 인장 실측**이 판정 창 밖에 있어 `미표기`로 읽히던 1행.
    r = row(27671)
    old = json.loads(r["conditions"] or "{}")
    new = base(old)
    new.pop("loading", None)
    new["loading_mode"] = "uniaxial tension"
    new["test_method"] = "uniaxial tension (ASTM E606 시편)"
    new["test_mode"] = "tensile"
    new["corrected_by_73ia"] = (
        f"{BATCH} — 인장 표기를 판정 창 안으로 옮긴다(`loading` → `loading_mode`·`test_mode`).")
    add(27671, ("이 행은 `loading: uniaxial tension` 으로 인장 실측임을 이미 밝혀 두었는데, "
                "`loading` 은 대표값 선택기의 시험모드 판정 창에 없는 칸이라 `미표기`로 읽혔다. "
                "같은 재료의 3점굽힘 DMTA 행 세 개는 창 안에 굽힘 지문이 있어 굽힘으로 읽힌다. "
                "**정직한 인장 표기가 창 밖에 있어 상을 못 받고 있었다** — 창 안 칸으로 옮긴다. "
                "값·단위·등급·method·출처는 그대로다."),
        new, (f"[{BATCH} 표기 정정] 인장 하중 모드임을 조건의 시험모드 판정 칸"
              f"(`test_mode`·`loading_mode`·`test_method`)에 명시했다. 값은 그대로다."),
        want="tensile", expect=0)

    # ══════════════════════════════════════════════════════════════════════════
    # G5 — 재료 97 BT Resin. 71차 GB 의 판정을 클래스 카드로 전파한다(굽힘이라 단정하지 않는다)
    # ══════════════════════════════════════════════════════════════════════════
    G5_REASON = (
        "71차 GB 가 같은 MGC BT 페이지의 등급별 행(재료 2711~2723)에 대해 내린 판정을 이 클래스 "
        "카드에 전파한다. 원문은 `ヤング率` 와 `曲げ弾性率` 를 **둘 다 인쇄하는데 13등급 전부 "
        "숫자가 같고**, 페이지 어디에도 시험규격 표기가 없다(`JIS`·`ASTM`·`IPC` 적중 0). "
        "그러므로 **굽힘이라고 단정할 수 없다** — 굽힘 표기를 달지 않고 `test_mode: unconfirmed` "
        "로 둔다(선택기에서 `미표기` 자리, 즉 인장 확정 행보다는 뒤·굽힘 확정 행보다는 앞이다). "
        "같은 수가 이미 `mechanical.flexural_modulus` 에도 t1 로 있다(pv5690·pv5701). "
        "값·단위·등급·method·출처는 그대로다 — 과대 경고문도 붙이지 않는다(굽힘 확정이 아니므로).")
    for pid, other in ((5692, "pv5690"), (5703, "pv5701")):
        r = row(pid)
        new = base(json.loads(r["conditions"] or "{}"))
        new["test_mode"] = "unconfirmed"
        new["mode_verdict_71gb"] = (
            "71차 GB 판정 전파 — MGC 원문이 ヤング率/曲げ弾性率 두 행을 같은 숫자로 인쇄하고 "
            "시험규격을 인쇄하지 않는다. 이 문서만으로는 어느 모드인지 갈리지 않는다.")
        new["duplicate_of"] = (
            f"mechanical.flexural_modulus {other} (같은 수·같은 출처). 지우지 않았다 — "
            f"삭제는 사람이 정한다.")
        new["corrected_by_73ia"] = f"{BATCH} — 71차 GB 판정을 클래스 카드로 전파(G5)."
        add(pid, G5_REASON, new,
            (f"[{BATCH} 표기 정정] 시험모드가 확정되지 않은 값이다 — MGC 원문이 `ヤング率` 와 "
             f"`曲げ弾性率` 를 같은 숫자로 인쇄하고 시험규격을 밝히지 않는다(71차 GB 판정). "
             f"굽힘이라 단정하지 않았고 과대 경고도 붙이지 않았다. 같은 수의 굽힘 행 {other} 이 "
             f"이미 있다 — **중복 후보이지만 지우지 않았다. 삭제는 사람이 정한다.** "
             f"참고: 같은 원문에서 나온 등급별 행(재료 2711~2723)은 71차 GB 가 t3 로 내렸는데 "
             f"이 클래스 카드 두 행은 t1 이다 — 등급 정합은 다음 배치로 넘긴다."),
            expect=1)

    # ══════════════════════════════════════════════════════════════════════════
    # G6 — 재료 739. HB §7-4 의 두-모드 문자열을 **원문으로 갈랐다** — 인장이다
    # ══════════════════════════════════════════════════════════════════════════
    G6_REASON = (
        "72차 HB §7-4 가 *'`DMA 3-point bending + uniaxial tensile` 로 두 모드를 한 문자열에 담고 "
        "있어 어느 쪽인지 안 갈린다 — 원문을 다시 열어 갈라라'* 라고 넘긴 9행이다. 73차 IA 가 "
        "코퍼스 원문(Chiu 2009, `.md` 전문)을 열어 갈랐다. 본문 verbatim — *'However, the "
        "three-point bending test configuration used in the DMA test is sensitive to sample "
        "flatness. **To overcome this issue, uniaxial tensile tests using Instron 5565 tester "
        "are also conducted to measure elastic modulus at various temperatures.**'* Table 3 의 "
        "`Young's Modulus (GPa)` 열이 바로 그 **온도별 탄성률**이고, 그 244 K 절점(32 GPa)이 "
        "본문의 인장 피팅 결과 E0 = 32 GPa 와 일치한다(카탈로그의 pv23623 이 그 값이다). "
        "즉 **이 9행은 굽힘이 아니라 인장이다** — DMA 3점굽힘은 같은 논문에서 Prony 급수·"
        "시간-경화 이동함수를 특성화하는 데 쓰였다. 두 모드를 한 칸에 담아 두면 선택기가 "
        "판단을 보류하므로, `test_method` 는 원문이 귀속시킨 시험만 담고 DMA 맥락은 창 밖으로 "
        "옮긴다. 값·단위·등급·method·출처는 그대로다.")
    for pid in range(23624, 23633):
        r = row(pid)
        new = base(json.loads(r["conditions"] or "{}"))
        new["test_method"] = "uniaxial tension (Instron 5565), 온도별 탄성률"
        new["test_mode"] = "tensile"
        new["dma_context"] = (
            "같은 논문의 DMA(TA Instruments DMA 2980, 3점굽힘 지그, 8주파수, -30~300 C)는 "
            "Prony 급수와 시간-경화 이동함수를 특성화하는 데 쓰였다. Table 3 의 온도별 탄성률은 "
            "그쪽이 아니다 — 본문이 인장시험에 귀속시킨다.")
        new["mode_attribution_caveat"] = (
            "논문이 인장시험의 온도 범위를 인쇄하지 않았다. 유리상 절점(244~393 K)은 본문의 "
            "E0 = 32 GPa 와 정합하지만, 고무상 절점(423~503 K)이 인장 실측인지 DMA 마스터커브 "
            "환산인지는 원문이 못박지 않는다. 이 불확실은 값에 반영하지 않고 기록만 남긴다.")
        new["corrected_by_73ia"] = f"{BATCH} — 두-모드 문자열을 원문 근거로 갈랐다(G6). 인장이다."
        add(pid, G6_REASON, new,
            (f"[{BATCH} 표기 정정] 72차 HB 가 넘긴 두-모드 물음을 원문으로 갈랐다 — "
             f"이 값은 **굽힘이 아니라 단축 인장 실측**이다(Chiu 2009 본문: 'uniaxial tensile "
             f"tests using Instron 5565 tester are also conducted to measure elastic modulus at "
             f"various temperatures'). 값은 그대로다. 고무상 절점의 귀속에는 주의가 남는다 — "
             f"conditions.mode_attribution_caveat 참고."),
            want="tensile", expect=0)

    # ══════════════════════════════════════════════════════════════════════════
    # G7 — 재료 434. 굽힘 표기가 `definition` 이라는 **창 밖 칸**에만 있던 1행
    # ══════════════════════════════════════════════════════════════════════════
    r = row(17051)
    old = json.loads(r["conditions"] or "{}")
    new = base(old)
    new["test_mode"] = "flexural"
    new["loading_mode"] = "bending"
    new["method_detail"] = "굴곡 탄성률 (굽힘 시험) — 원문 행 이름 `Flexural modulus at RT`"
    new["reported_as_youngs_modulus"] = True
    new["duplicate_of"] = (
        "mechanical.flexural_modulus — 73차 IA 가 같은 출처·같은 수를 그 키에 세웠다"
        "(ia73_02_materials.json). 지우지 않았다 — 삭제는 사람이 정한다.")
    new["corrected_by_73ia"] = f"{BATCH} — 굽힘 표기를 `definition`(창 밖)에서 판정 창 안으로 옮긴다."
    add(17051, ("굽힘이라는 표기가 `definition` 칸에만 있었다. 그 칸은 대표값 선택기의 시험모드 "
                "판정 창(아홉 칸)에 없어서 이 행은 `미표기`로 읽혔다 — 적재 당시 배치가 정직하게 "
                "적어 둔 문장이 기계에는 없는 것과 같았다. 표기를 창 안으로 옮긴다. 등급은 이미 "
                "t3 로 내려 있고(적재 배치가 굽힘값임을 이유로 내렸다), 값·단위·method·출처는 "
                "그대로다."),
        new, f"[{BATCH} 표기 정정] {WARN}")

    # 재료 434 의 굽힘 키는 비어 있다 — 빌려 온 값이라는 사실을 그대로 안고 한 벌 세운다.
    mat_rows.append((r, {
        "key": "mechanical.flexural_modulus",
        "value": r["value_num"], "unit": r["unit"],
        "method": r["method"], "quality_tier": r["quality_tier"],
        "conditions": {
            "temperature": old.get("temperature"), "grade_scope": old.get("grade_scope"),
            "test_mode": "flexural", "loading_mode": "bending",
            "method_detail": "굴곡 탄성률 (굽힘 시험) — 원문 행 이름 `Flexural modulus at RT`",
            "added_by_73ia": (f"{BATCH} — 이 재료의 굽힘 키가 비어 있었다. 영률 칸의 원행 "
                              f"pv17051 은 지우지 않았다."),
        },
        "notes": (f"[{BATCH}] 원문이 `Flexural modulus at RT 27 GN/m2` 로 인쇄한 값을 굽힘 키에 "
                  f"세운다. **자기 등급의 값이 아니다** — 같은 CEL-9200 계열 CEL-9220HF10 의 값을 "
                  f"클래스 대체값으로 빌린 것이라 t3 다(conditions.grade_scope). 같은 수가 "
                  f"`mechanical.youngs_modulus` pv17051 에도 있다. "
                  f"원행 notes: {(r['notes'] or '')[:220]}"),
    }))

    # ══════════════════════════════════════════════════════════════════════════
    # 자체 검사 — 적재기의 중복 가드(corr_would_duplicate)를 미리 흉내낸다
    # ══════════════════════════════════════════════════════════════════════════
    touched = {c["target"]["property_value_id"] for c in corrections}
    seen: dict = {}
    for c in corrections:
        pid = c["target"]["property_value_id"]
        r = row(pid)
        sig = (r["material_id"], r["source_id"],
               json.dumps({k: str(v) for k, v in sorted(c["set"]["conditions"].items())},
                          ensure_ascii=False))
        if sig in seen:
            print(f"✗ pv{pid} 정정 후 조건이 pv{seen[sig]} 과 같아진다", file=sys.stderr)
            return 3
        seen[sig] = pid
        for o in con.execute(
                "select id, conditions from property_value where material_id=?"
                " and property_key='mechanical.youngs_modulus' and source_id is ? and id != ?",
                (r["material_id"], r["source_id"], pid)).fetchall():
            if o["id"] in touched:
                continue
            osig = json.dumps({k: str(v) for k, v in
                               sorted(json.loads(o["conditions"] or "{}").items())},
                              ensure_ascii=False)
            if osig == sig[2]:
                print(f"✗ pv{pid} 정정 후 라이브 pv{o['id']} 과 조건이 같아진다", file=sys.stderr)
                return 4

    # 새로 넣는 굽힘 행끼리·기존 행과 조건이 겹치는지 본다(적재기의 조건충돌 가드).
    sigs: dict = {}
    for r, pr in mat_rows:
        sig = (r["material_id"], pr["key"], r["surl"] or r["sdoi"] or r["stitle"],
               json.dumps({k: str(v) for k, v in sorted(pr["conditions"].items())},
                          ensure_ascii=False))
        if sig in sigs:
            print(f"✗ 새 굽힘 행 조건 충돌: 재료 {r['material_id']} — {sig[3][:120]}", file=sys.stderr)
            return 5
        sigs[sig] = r["id"]

    # ── 산출 ────────────────────────────────────────────────────────────────
    with open(OUT_CORR, "w", encoding="utf-8") as f:
        json.dump({
            "batch": BATCH,
            "note": ("`mechanical.youngs_modulus` 에 앉은 굽힘탄성률 등 101행의 **표기**를 "
                     "바로잡는다. 값·단위·등급·method·출처는 한 칸도 바꾸지 않는다. 삭제 0건 — "
                     "중복 후보는 conditions 와 보고서에 적기만 했다. 이 배치의 실질은 "
                     "**표기를 대표값 선택기의 시험모드 판정 창(아홉 칸) 안으로 옮기고, "
                     "부정문·곁말은 창 밖으로 빼는 것**이다."),
            "corrections": corrections,
        }, f, ensure_ascii=False, indent=1)

    # materials 문서 — 출처별로 묶는다(같은 출처가 여러 번 오면 upsert_source 가 재사용한다).
    entries: dict = {}
    for r, pr in mat_rows:
        k = (r["material_id"], r["source_id"])
        e = entries.setdefault(k, {
            "match_name": r["mname"],
            "source": {"kind": r["skind"] or "datasheet", "url": r["surl"],
                       "doi": r["sdoi"], "title": r["stitle"], "authors": r["sauth"],
                       "year": r["syear"], "local_path": r["spath"],
                       "publisher": r["spub"]},
            "properties": [],
        })
        e["properties"].append(pr)
    with open(OUT_MAT, "w", encoding="utf-8") as f:
        json.dump({
            "batch": BATCH,
            "note": ("영률 칸에 앉아 있던 굽힘탄성률과 **같은 수·같은 출처**를 "
                     "`mechanical.flexural_modulus` 로도 세운다. 새로 캔 값이 아니다 — "
                     "이미 카탈로그에 있는 수를 올바른 키에 한 벌 더 놓는 것이고, 그래야 그 "
                     "재료가 굽힘 정보를 잃지 않는다. **원행은 지우지 않았다.** "
                     "원문이 행 이름을 `Flexural Modulus`(또는 `굴곡 탄성률`)로 인쇄한 것만 "
                     "옮겼다 — DMA 저장탄성률·인장면 게이지 실측은 옮기지 않았다."),
            "materials": list(entries.values()),
        }, f, ensure_ascii=False, indent=1)

    print(f"정정 {len(corrections)}건 → {OUT_CORR}")
    print(f"굽힘 키 신규 {len(mat_rows)}행 / 항목 {len(entries)}개 → {OUT_MAT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
