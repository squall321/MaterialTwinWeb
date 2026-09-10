#!/usr/bin/env python3
# 73차 IB — 재빌드 색인(29,846편)으로 재검색한 결과를 판정 갱신 JSON 으로 굽는다.
#
# 왜 이 스크립트가 있나 — 판정 사유는 `apply_core_verdicts.py` 가 **키 단위로 덮어쓴다.**
# 즉 유효기간 한 줄만 넣을 수 없고 **옛 사유 전문 + 새 도장** 을 통째로 다시 써야 한다.
# 라이브 DB 에서 옛 사유를 읽어 뒤에 도장을 붙이는 일을 손으로 하면 326칸에서 반드시 틀린다.
#
# 읽기 전용으로 DB 를 열고 out_ib/ib73_02_verdicts.json 만 쓴다. DB 에 쓰지 않는다.
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = ("/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/"
           "27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad")
DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                  "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
                  "materialtwin.db")

# 재검색이 **무엇을 아는 상태였는지** 를 판정문에 박아 둔다. 이게 이 배치의 요지다.
BLIND = (
    "**다만 이 재검색이 무엇을 아는지 못 박아 둔다** — `corpus_index.py` 의 FTS 는 문서당 "
    "**본문 md 한 장만** 색인한다(`build()` 가 `doc.path` 하나만 읽는다). 코퍼스 29,846편 중 "
    "**17,852편(59%)이 docling 이 본문에서 빼낸 `tables/*.md` 를 따로 갖고 있고**(표 파일 88,075장 · 187 MB) "
    "**그 표 층은 색인 밖이다** — 표를 읽는 것은 `scan()` 뿐이고 `search`·`near` 는 못 본다. "
    "물성 숫자는 표에 산다. 그러므로 이 판정의 유효기간은 **'2026-09-09 본문 색인까지'** 이지 "
    "'코퍼스 전체' 가 아니다. 표 층은 아직 안 두드렸다(73차 IB 가 다음 파동에 넘긴다)."
)
HEAD = ("**[73차 IB — 2026-09-09 재빌드 색인(29,846편)으로 재검색했다. 유효기간을 갱신한다]** "
        "8/15 자 색인(20,692편)이 25일 낡은 채로 여러 파동의 '전수 0건' 을 받치고 있었다. "
        "9/9 에 29,846편으로 재빌드했다(+9,154편 · 내려간 문서 0편). ")


def stamp_a(q: str, n_hit: int) -> str:
    return (HEAD + f"이 재료의 식별자 `{q}` 로 새 색인을 다시 쳤다 — "
            f"전체 적중 {n_hit}편이고 **새로 들어온 9,154편 중 걸린 문서는 0편이다.** 판정은 그대로다. " + BLIND)


def stamp_d(q: str, n_new: int, pk: str, why: str) -> str:
    """새 문서에 물성 낱말이 걸렸으나 **눈으로 열어 보니 이 재료의 값이 아니었다**."""
    return (HEAD + f"이 재료의 식별자 `{q}` 로 새 색인을 다시 쳐 **새 문서 {n_new}편이 걸렸고, 그중 "
            f"`{pk}` 낱말이 든 문서를 전부 열어 값꼴 줄을 눈으로 대조했다.** {why} "
            "**이 재료를 지목하면서 값을 찍는 새 문서는 0편이다.** 판정은 그대로다. " + BLIND)


def stamp_b(q: str, n_new: int, pk: str) -> str:
    return (HEAD + f"이 재료의 식별자 `{q}` 로 새 색인을 다시 쳐 **새 문서 {n_new}편이 걸렸고 그 {n_new}편을 "
            f"전부 본문 낱말검색했다 — `{pk}` 에 해당하는 낱말이 한 편에도 없다.** 판정은 그대로다. " + BLIND)


# 새 문서를 실제로 열어 확인한 것들 — 재료별로 따로 쓴다.
CUSTOM: dict[int, str] = {}
_EHRLER = (HEAD + "**이 재료의 출처 문서 Ehrler 2002 자체가 이번 재빌드로 처음 색인에 들어왔다** — "
           "`xd_papers/06_ecad_design_automation/Ehrler-2002-Properties-of-new-printed-circuit-board-base-materials`. "
           "즉 이 등급을 다룬 파동들은 **이 문서를 색인으로는 한 번도 못 봤다**(PDF 는 직접 열었다). "
           "이번에 색인에 들어온 그 문서를 전권으로 다시 읽었고 **판정을 뒤집지 않는다** — "
           "표가 열 장인데 밀도 행이 어디에도 없다. Table II(에폭시계 고성능 재료: Nelco4000-6 · N4000-13 · FR408 · GETEK)와 "
           "Table III(대체수지: CE · BT · RO4350 · RO4003 · A-PPE)가 인쇄하는 것은 "
           "Cu peel strength · Tg(TMA/DSC/DMA) · z-axis expansion · CTEz · 유전율(1 MHz) · 손실계수 · 체적·표면저항 뿐이다. "
           "`Specific Gravity` 는 **Table V 딱 한 곳에 나오는데 그것은 적층판이 아니라 보강재**의 값이다"
           "(Thermount 1.44 · E-Glass 2.54 · S-Glass 2.49 · Quartz 2.2 — Powell·Kirayohlu 1997 재인용). "
           "보강재 비중을 적층판 밀도로 옮기는 것은 §44 의 위반이다. 판정은 그대로다. " + BLIND)
for _m in (1273, 1274, 1277, 1278):
    CUSTOM[_m] = _EHRLER

_3M = (HEAD + "**이 등급의 TDS 세 판이 이번 재빌드로 처음 색인에 들어왔다** — "
       "`standards_appnotes/mech/` 아래 `3M_ScotchWeld_Epoxy_DP100_Clear_TDS_2024-09` · "
       "`3M_ScotchWeld_Epoxy_DP-100_Clear_NS_TDS_2016-02` · `3M_ScotchWeld_Epoxy_DP100NS_Translucent_TDS_2024-09` · "
       "`3M_ScotchWeld_EPX_Epoxy_DP100NS_PDS_1996-03`. 38차 AW·57차 SC 가 로컬 사본으로 열었던 바로 그 판들이고, "
       "이제 색인에서도 같은 것을 친다. **판정을 뒤집지 않는다** — TDS 세 판에 `densit`·`specific gravity`·`poisson`·"
       "`specific heat` 적중이 **0건**이고, 1996년 PDS 만 `Specific Gravity 1.16 / 1.15` 를 찍는데 그것은 "
       "**미경화 Base / Accelerator 성분별** 값이라 경화 접착층 밀도가 아니다(§44 — 57차 SC 가 이미 기각). "
       "판정은 그대로다. " + BLIND)
for _m in (2389, 2418):
    CUSTOM[_m] = _3M

CUSTOM[964] = (HEAD + "이 재료로 새로 걸린 문서는 **JESD88G 한 편뿐이고 그것은 값을 싣는 문서가 아니다** — "
               "`JEDEC Dictionary of Terms for Solid State Technology, 8th Edition`(2025-03), 즉 **용어사전**이다. "
               "`poisson`·`tensile strength`·`CTE` 가 걸린 것은 표제어 정의이지 이 컴파운드의 값이 아니다. "
               "판정은 그대로다. " + BLIND)

# 눈으로 확인한 위양성 사유(재료 → 사유). 도장 D 가 쓴다.
FALSE_POS: dict[int, str] = {}
for _m in (43, 44, 45, 46, 50):
    FALSE_POS[_m] = ("걸린 것은 `2005 - Flexible Flat Panel Displays`(단행본)와 Choi 2008 이고 둘이 찍는 OTR"
                     "(verbatim `from 1000 to 0.1 cm3 (STP)/m2/day/atm`, Shaw·Langlois 1994 재인용)은 "
                     "**진공증착 배리어막의 값이지 아크릴 OCA/PSA 접착층의 값이 아니다.**")
FALSE_POS[93] = ("걸린 넉 편(Park 1997 · Moisture Sensitivity 단행본 2010 · Khor 2012 · Wan 2007)에 "
                 "`specific heat` 낱말은 있으나 **값꼴(J/g·K, J/kg·K) 줄이 한 줄도 없다** — 본문 서술어일 뿐이다.")
FALSE_POS[578] = ("걸린 셋 중 Darveaux 두 편은 **이미 이 재료의 출처로 쓰고 있는 문서의 사본**이고"
                  "(§아래 파일명 중복 참조), Mysore 2009 는 **Sn3.0Ag0.5Cu** 를 다룬다 — 다른 조성이다. "
                  "Darveaux 1992 는 이 조성에 대해 `Assuming a Poisson's ratio of 0.35` 와 전단탄성계수 상수"
                  "(Go = 1.9e6 lbf/in2 · G1 = 8.1e3 lbf/in2/degC)만 찍고 **영률을 직접 인쇄하지 않는다** — "
                  "E = 2G(1+nu) 로 되돌리는 것은 역산이라 하지 않는다. "
                  "다만 그 상수로 나오는 25 degC 영률이 약 31.6 GPa 라 **Kester 23.51 GPa 기각(하한 31.2~32.0)을 "
                  "옆에서 받친다** — 기각 근거가 한 겹 두꺼워졌다.")
FALSE_POS[739] = "걸린 아홉 편 중 **이 컴파운드(Chiu 2009)를 지목하면서 값을 찍는 문서가 0편**이다."
FALSE_POS[1368] = ("`Moisture Sensitivity of Plastic Packages`(2010)가 `Density 1.79 g/cm3` · "
                   "`Storage modulus (at 25 degC) 14.65 GPa` 를 찍기는 하나 **그 책 자신의 시편 값이고 "
                   "Lau 2018 의 패널레벨 드라이필름 EMC 가 아니다.** Luo 2016 은 LED 기판 서술이다.")
FALSE_POS[1369] = "걸린 스물세 편 중 **이 언더필(Qun 2000)을 지목하면서 값을 찍는 문서가 0편**이다."
FALSE_POS[1651] = ("Hwang 2005 의 값꼴 줄은 **다른 이리듐 착체의 단결정 격자상수**"
                   "(verbatim `triclinic, space group P1; a) 11.1500(5) ...`)이지 fac-Ir(ppy)3 의 밀도가 아니다. "
                   "나머지 55편의 `density` 는 전부 **전류밀도(current density)** 다.")
for _m in (2233, 2283):
    FALSE_POS[_m] = ("걸린 것은 배리어·그래핀 리뷰들이고 값은 전부 **부류 일반값**이다 — "
                     "`Poisson's ratio (0.3-0.4)` 같은 서술, 또는 그래핀·CNT 의 GPa 표다. "
                     "**이 등급의 필름을 지목한 값이 아니다.**")
FALSE_POS[2225] = FALSE_POS[2254] = ("걸린 `2005 - Flexible Flat Panel Displays` 단행본에 "
                                     "**이 등급(Teijin PC · Melinex)을 지목한 행이 없고 밀도 값꼴 줄도 0줄**이다.")
FALSE_POS[2128] = ("걸린 JAYABAL 2011 은 **다른 불포화 폴리에스터의 유리섬유 하이브리드 적층판**을 다룬다 — "
                   "D-1103 을 지목하지 않는다.")
FALSE_POS[2380] = "걸린 한 편에 **PMMA 판을 지목한 값꼴 줄이 0줄**이다."
FALSE_POS[2689] = ("Joho 2002 는 **흑연 음극의 발열**을 다루고 Pasquier 1998 · Croce 2011 도 "
                   "전해액 자체의 비열을 찍지 않는다 — `heat` 낱말만 걸렸다.")

CUSTOM[2346] = (HEAD + "**이 칸은 색인이 낡았는지와 무관하다** — `core_not_applicable` 은 구조 판정이기 때문이다. "
                "이 레코드는 재료 962 `Sn63Pb37 Eutectic Solder Alloy` 의 **시험편** 레코드이고 코어 7 물성은 962 의 몫이다"
                "(§623·§586). 새 색인에서 Sn-Pb 공정 땜납 문서 25편이 새로 걸렸지만 그것들은 **962 의 표적이지 이 시험편의 "
                "표적이 아니다** — 새 문서가 아무리 늘어도 시험편 레코드가 모재료의 코어를 되찾아 오지는 않는다. "
                "판정은 그대로다. 다만 그 25편은 **재료 962 의 표적으로 다음 파동에 넘긴다**(Abtew 2000 "
                "`Lead-free Solders in Microelectronics` 가 밀도·열전도율·비열을 함께 싣는다). " + BLIND)


def main() -> int:
    sweep = {r["mid"]: r for r in json.load(open(f"{SCRATCH}/ib73/sweep_out.json"))}
    cells = json.load(open(f"{SCRATCH}/corpus_verdicts.json"))

    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    attrs = {i: json.loads(a or "{}") for i, a in c.execute("select id,attributes from material")}

    out: dict[int, dict] = {}
    stats = {"A": 0, "B": 0, "C": 0, "D": 0, "보류": 0}
    held: list[str] = []
    for r in cells:
        mid, pk, key = r["mid"], r["pk"], r["key"]
        s = sweep[mid]
        old = str(attrs[mid].get(key, {}).get(pk, ""))
        if not old:
            print(f"  ! {mid} {key}/{pk} — DB 에서 옛 사유를 못 찾았다. 건너뛴다", file=sys.stderr)
            continue
        if mid in CUSTOM:
            new, tag = CUSTOM[mid], "C"
        elif s["n_new"] == 0:
            new, tag = stamp_a(s["q"], s["n_hit"]), "A"
        elif not s["new_with_prop"]:
            new, tag = stamp_b(s["q"], s["n_new"], pk), "B"
        elif mid in FALSE_POS:
            new, tag = stamp_d(s["q"], s["n_new"], pk, FALSE_POS[mid]), "D"
        else:
            # 새 문서에 물성 낱말이 걸렸는데 아직 눈으로 안 봤다 — 도장을 찍지 않는다.
            stats["보류"] += 1
            held.append(f"{mid:5d} {pk:32s} new={s['n_new']:3d} {s['name'][:44]}")
            continue
        stats[tag] += 1
        out.setdefault(mid, {"material_id": mid, "name": s["name"]})
        out[mid].setdefault(key, {})[pk] = new + "\n\n" + old

    doc = {"batch": "73차 IB — 재빌드 색인(29,846편) 재검색에 따른 부재 판정 유효기간 갱신",
           "verdicts": list(out.values())}
    p = os.path.join(HERE, "ib73_02_verdicts.json")
    json.dump(doc, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"[쓰기] {p}\n  재료 {len(out)}종 · 칸 {sum(stats[k] for k in 'ABCD')}칸"
          f"\n   A 새 문서 0건            {stats['A']:4d}"
          f"\n   B 새 문서 있으나 물성낱말 0 {stats['B']:4d}"
          f"\n   C 새 문서를 열어 확인     {stats['C']:4d}"
          f"\n   D 물성낱말은 걸렸으나 위양성 {stats['D']:4d}")
    print(f"  보류(새 문서에 물성 낱말이 걸려 눈 확인이 남은 칸) {stats['보류']}칸:")
    for h in held:
        print("   ", h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
