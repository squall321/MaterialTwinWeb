# 72차 HB — 영률 칸에 앉은 굽힘탄성률 43행의 표기를 바로잡는 정정 JSON 생성기
#
# 라이브 DB 를 **읽기 전용(mode=ro)** 으로만 연다. 값·단위·등급·method 는 건드리지 않는다.
# conditions 는 통째 치환이므로 기존 조건을 전부 읽어 보존한 뒤 표기 칸만 더한다.
import json
import os
import re
import sqlite3
import sys

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR", ""), "materialtwin.db")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hb72_01_corrections.json")
BATCH = "72차 HB"

# 브리프가 못박은 문장. 여기에 이 배치가 실측한 확장을 덧붙인다.
WARN = ("이 값은 굽힘탄성률이며 인장탄성률이 아니다. 해석에 쓸 때 12~23% 과대일 수 있다"
        "(68차 DC·71차 GB 실측). 72차 HB 가 Panasonic 2021-03 특성일람표에서 같은 등급의 "
        "`曲げ弾性係数`/`ヤング率(引張りモード)` 쌍을 다시 재 보니 폭이 더 넓었다 — "
        "R-5775 20/19 대 16.3/14.3 GPa(+23 %/+33 %) · R-5785(N) 19/18 대 13.5/11.6 GPa"
        "(+41 %/+55 %). 12~23 % 는 하한이지 상한이 아니다.")

# (그룹, 사유 머리말, 그 그룹의 pv id 목록)
GROUPS = [
    ("I-Isola",
     "Isola 벤더 시트가 `Young's Modulus` 라는 이름을 붙인 행의 시험규격이 `ASTM D790-15e2`"
     "(3점 굽힘)다. 같은 시트가 `Tensile Strength`는 `ASTM D3039`로 따로 인쇄하지만 "
     "**인장탄성률 행은 없다**(370HR·IS400·I-Tera MT40·FR408 네 장 전수 확인 — `modulus` 적중은 "
     "`Young's Modulus` 한 행뿐). 그러므로 값을 인장으로 갈아치울 원문 근거가 없다 — 값은 두고 "
     "표기만 바로잡는다.",
     [5761, 5762, 3356, 3357, 6081, 6082, 3382, 3383, 6096, 6097,
      3408, 3409, 6111, 6112, 10426, 10427, 43576, 43577]),
    ("II-Isola-차용",
     "이 행은 자기 등급의 값이 아니라 동급 Isola 시트(370HR·IS400)의 `Young's Modulus` 행을 "
     "클래스 대체값으로 빌려 온 것이고, 그 원본이 `ASTM D790-15e2`(3점 굽힘)다. 굽힘값을 빌렸다는 "
     "사실이 등급 대체와 겹쳐 두 겹으로 가려져 있었다.",
     [16961, 16962, 16963, 16964]),
    ("III-Dudek2001",
     "Dudek 2001 Table 3 의 열 머리글은 `Young's-Modulus (GPa)` 이지만, 같은 논문 본문이 "
     "verbatim 으로 *'The elastic moduli and breaking elongation were measured by three point "
     "bending tests according to standard EN ISO 178'* 라고 밝힌다. 논문 전문에 인장 탄성률 측정은 "
     "없다(방법절이 여는 시험은 3점굽힘과 SENB 파괴인성뿐). 값은 두고 표기만 바로잡는다.",
     [27245, 27246, 27247, 27248, 27257, 27258, 27259, 27260,
      27269, 27270, 27271, 27272, 27281, 27282, 27283, 27284]),
    ("IV-벤더프록시",
     "벤더 데이터시트가 인쇄한 것이 굽힘탄성률이고 그 시트에 인장탄성률 행이 없다. 적재 당시 "
     "notes 에는 그 사실을 정직하게 적었으나 **conditions 의 시험모드 칸이 비어 있어** 조건만 읽는 "
     "소비자·집계기에는 인장으로 보인다. 표기를 조건까지 내린다.",
     [1177, 6763]),
    ("V-Bansal1997",
     "Bansal 1997 Table 1 의 `Elastic modulus, E (GPa)` 는 3점 굽힘 시험에서 얻었다 — 본문 verbatim "
     "*'Mechanical properties of the composites were determined from stress-strain curves recorded "
     "in three-point flexure'* · *'The elastic modulus was determined from the linear portion of the "
     "load vs. strain curve'*. 인장 시험은 이 논문에 없다. 다만 이 값은 **인장면에 붙인 스트레인 "
     "게이지의 실측 변형률**로 얻은 것이라 처짐-컴플라이언스로 역산한 D790 굽힘탄성률보다 인장에 "
     "가깝다 — 그 사실을 조건에 같이 남긴다.",
     [32785, 32788]),
    ("VI-DMA굽힘",
     "이 값은 DMA 3점굽힘 마스터커브의 유리상 순간탄성률 E0 다(Chiu 2011 TABLE IV). 같은 재료의 "
     "단축 인장 실측(32 GPa, Chiu 2009, pv23623)이 이미 카탈로그에 있고 그쪽이 대표로 뽑혀 있으므로 "
     "값을 옮길 필요는 없다. 다만 이 행이 굽힘 하중 모드라는 것이 조건에 안 적혀 있었다.",
     [26783]),
]

# 이 행의 값과 **같은 수가 mechanical.flexural_modulus 에 이미 있는** 행(중복 후보).
DUP_NOTE = ("**중복 후보** — 같은 재료의 `mechanical.flexural_modulus` 에 같은 수가 이미 "
            "t1 로 들어 있다(재료 135 → pv4452 · 재료 222 → pv11135·pv11136). 이 행을 지워도 "
            "숫자는 DB 에 남는다. **72차 HB 는 지우지 않았다 — 삭제는 사람이 정한다.**")
DUPS = {1177: "pv4452", 3408: "pv11135", 3409: "pv11136", 6111: "pv11135",
        6112: "pv11136", 10426: "pv11135", 10427: "pv11136"}

# 조건에서 시험규격을 잘못된 칸에 담고 있던 행 — 표준 칸으로 옮긴다.
# 이 옮김이 이 배치의 핵심이다: 다음 인구조사(test_standard·test_method·test_mode 3칸만 보는
# 정규식)가 이 행들을 **비로소** 볼 수 있게 된다.
RENAME_TO_STANDARD = {"test", "standard"}
# 굽힘 지문. conditions 값 어디에 있어도 잡는다.
FLEX = re.compile(r"D\s?790|C6481|K\s?7171|ISO\s?178|flexur|굽힘|굴곡|曲げ|"
                  r"three[- ]point|3-?point|3점", re.I)
AUDIT = ("correction_reason", "corrected_by", "correction_evidence")


def flex_standard(cond: dict) -> str | None:
    """조건 어딘가에 적힌 굽힘 시험규격을 골라낸다(없으면 None)."""
    for k in ("test_standard", "test", "standard", "test_method", "method_detail", "detail",
              "modulus_basis", "definition"):
        v = str(cond.get(k) or "")
        m = re.search(r"(ASTM\s*D\s?790[\w.\-]*|EN\s*ISO\s*178|ISO\s*178|JIS\s*C\s?6481"
                      r"|JIS\s*K\s?7171|ASTM\s*D5045)", v, re.I)
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()
    return None


def main() -> int:
    if not os.path.exists(DB):
        print(f"DB 가 없다: {DB} — MATERIALTWIN_DATA_DIR 를 확인하라", file=sys.stderr)
        return 2
    con = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    corrections = []
    seen_sig: dict[tuple, int] = {}
    for gname, why, ids in GROUPS:
        for pid in ids:
            r = con.execute(
                "select pv.id, pv.material_id, pv.property_key, pv.value_num, pv.unit,"
                "       pv.quality_tier, pv.method, pv.source_id, pv.conditions, pv.notes,"
                "       m.name mname"
                "  from property_value pv join material m on m.id = pv.material_id"
                " where pv.id = ?", (pid,)).fetchone()
            if r is None:
                print(f"✗ pv{pid} 이 라이브에 없다 — 건너뛴다", file=sys.stderr)
                continue
            assert r["property_key"] == "mechanical.youngs_modulus", (pid, r["property_key"])
            old = json.loads(r["conditions"] or "{}")

            new = {k: v for k, v in old.items() if k not in AUDIT}
            std = flex_standard(old)
            # 잘못된 칸에 있던 규격을 표준 칸으로 옮긴다(다음 인구조사가 보게 하려고).
            for k in list(new):
                if k in RENAME_TO_STANDARD and FLEX.search(str(new[k])):
                    new.pop(k)
            if std and not new.get("test_standard"):
                new["test_standard"] = std
            new["test_mode"] = "flexural"
            new["reported_as_youngs_modulus"] = True
            new["loading_mode"] = "bending"
            new["corrected_by_72hb"] = (
                f"{BATCH} — 시험모드 표기 정정. 값·단위·등급·method·출처는 그대로다. "
                f"갈래 {gname}.")
            if pid in DUPS:
                new["duplicate_of"] = (
                    f"mechanical.flexural_modulus {DUPS[pid]} (같은 수·같은 출처). "
                    f"지우지 않았다 — 삭제는 사람이 정한다.")
            if pid in (32785, 32788):
                new["flexural_modulus_basis"] = (
                    "인장면 스트레인 게이지의 실측 변형률로 얻은 굽힘탄성률 — 처짐 컴플라이언스 "
                    "역산이 아니다. D790 식 굽힘탄성률보다 인장값에 가깝다.")

            note_old = (r["notes"] or "").strip()
            add = f"[{BATCH} 표기 정정] {WARN}"
            if pid in DUPS:
                add += " " + DUP_NOTE
            notes = (note_old + "\n\n" + add) if note_old else add

            corrections.append({
                "target": {"property_value_id": r["id"]},
                "by": BATCH,
                "reason": (f"영률 칸에 앉은 굽힘탄성률의 표기를 바로잡는다({gname}). {why} "
                           f"값·단위·등급·method 는 그대로 두고 conditions.test_mode 와 notes 만 "
                           f"고친다."),
                "set": {"conditions": new, "notes": notes},
            })

            sig = (r["material_id"], r["source_id"],
                   json.dumps({k: str(v) for k, v in sorted(new.items())}, ensure_ascii=False))
            if sig in seen_sig:
                print(f"✗ pv{pid} 정정 후 조건이 pv{seen_sig[sig]} 과 같아진다 — "
                      f"적재기가 중복으로 거부한다", file=sys.stderr)
                return 3
            seen_sig[sig] = pid

    # 라이브에 이미 있는 형제행과도 겹치지 않는지 본다(적재기의 corr_would_duplicate 가드).
    for c in corrections:
        pid = c["target"]["property_value_id"]
        r = con.execute("select material_id, source_id from property_value where id=?",
                        (pid,)).fetchone()
        newsig = json.dumps({k: str(v) for k, v in sorted(c["set"]["conditions"].items())},
                            ensure_ascii=False)
        others = con.execute(
            "select id, conditions from property_value"
            " where material_id=? and property_key='mechanical.youngs_modulus'"
            "   and source_id is ? and id != ?",
            (r["material_id"], r["source_id"], pid)).fetchall()
        touched = {x["target"]["property_value_id"] for x in corrections}
        for o in others:
            if o["id"] in touched:
                continue
            osig = json.dumps({k: str(v) for k, v in
                               sorted(json.loads(o["conditions"] or "{}").items())},
                              ensure_ascii=False)
            if osig == newsig:
                print(f"✗ pv{pid} 정정 후 라이브 pv{o['id']} 과 조건이 같아진다", file=sys.stderr)
                return 4

    doc = {
        "batch": BATCH,
        "note": ("`mechanical.youngs_modulus` 에 앉아 있는 굽힘탄성률 43행의 **표기**를 "
                 "바로잡는다. 값·단위·등급·method·출처는 한 칸도 바꾸지 않는다. 삭제는 없다 — "
                 "중복 후보 7행은 conditions.duplicate_of 로 표시만 하고 보고서에 적었다."),
        "corrections": corrections,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print(f"정정 {len(corrections)}건 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
