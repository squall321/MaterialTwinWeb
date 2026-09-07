# 66차 BA — 포아송비 한 칸만 채우면 구조해석 카드가 서는 재료 64종의 적재 JSON 을 만든다.
#
# 두 갈래다.
#   ba01  하드페라이트 25등급 — Eclipse 시트 `Physical Characteristics (Typical)` 의 ν 0.28.
#         형제 424·425·2533 이 같은 표의 같은 값을 t3 `grade_scope` 규약으로 이미 들고 있고,
#         65차 AB 가 같은 표의 밀도·영률을 t4 로 이 25등급에 세운 선례를 그대로 따른다.
#   ba02  조달한 벤더 설계가이드·응용노트가 그 등급을 이름으로 찍은 세 칸.
#         Delrin 500 (DuPont Design Guide Module III) · Torlon 4301 (Solvay PAI Design Guide)
#         · 순수 인듐 (Indium Corporation Application Note 97532 R7).
#
# 안 만든 것 — §43 역산은 하지 않았고, 인쇄값이 이미 기각된 칸(재료 2293)은 되살리지 않았다.
import json

OUT_A = "ba01_hard_ferrite_poisson.json"
OUT_B = "ba02_handbook_poisson.json"

# ---- ba01 -----------------------------------------------------------------
FERRITE = [
    (2651, "Hard Ferrite Magnet Y8T (Sr Ferrite)"),
    (2652, "Hard Ferrite Magnet Y10T (Sr Ferrite)"),
    (2653, "Hard Ferrite Magnet Y20 (Sr Ferrite)"),
    (2654, "Hard Ferrite Magnet Y22H (Sr Ferrite)"),
    (2655, "Hard Ferrite Magnet Y23 (Sr Ferrite)"),
    (2656, "Hard Ferrite Magnet Y25 (Sr Ferrite)"),
    (2657, "Hard Ferrite Magnet Y26H (Sr Ferrite)"),
    (2658, "Hard Ferrite Magnet Y26H-1 (Sr Ferrite)"),
    (2659, "Hard Ferrite Magnet Y26H-2 (Sr Ferrite, = C7)"),
    (2660, "Hard Ferrite Magnet Y27H (Sr Ferrite)"),
    (2661, "Hard Ferrite Magnet Y28 (Sr Ferrite)"),
    (2662, "Hard Ferrite Magnet Y28H-1 (Sr Ferrite)"),
    (2663, "Hard Ferrite Magnet Y28H-2 (Sr Ferrite)"),
    (2664, "Hard Ferrite Magnet Y30BH (Sr Ferrite)"),
    (2665, "Hard Ferrite Magnet Y30H-2 (Sr Ferrite, = C9 / C12)"),
    (2666, "Hard Ferrite Magnet Y32 (Sr Ferrite)"),
    (2667, "Hard Ferrite Magnet Y32H-1 (Sr Ferrite)"),
    (2668, "Hard Ferrite Magnet Y32H-2 (Sr Ferrite)"),
    (2669, "Hard Ferrite Magnet Y33 (Sr Ferrite, = C8B)"),
    (2670, "Hard Ferrite Magnet Y33H (Sr Ferrite, = C10)"),
    (2671, "Hard Ferrite Magnet Y34 (Sr Ferrite, = C11)"),
    (2672, "Hard Ferrite Magnet Y36 (Sr Ferrite)"),
    (2673, "Hard Ferrite Magnet Y38 (Sr Ferrite)"),
    (2674, "Hard Ferrite Magnet Y40 (Sr Ferrite)"),
    (2675, "Hard Ferrite Magnet C1 (Sr Ferrite, American standard, = Y10T / Y8T)"),
]

ECLIPSE = {
    "kind": "datasheet",
    "url": "https://www.eclipsemagnetics.com/site/assets/files/19602/ferrite_ceramic_datasheet.pdf",
    "title": "Ferrite Magnets/Ceramic Magnets Datasheet",
    "authors": "Eclipse Magnetics Ltd (corporate author)",
    "year": 2021,
    "publisher": "Eclipse Magnetics",
    "local_path": "standards_appnotes/passive/Eclipse_Magnetics_Ferrite_Ceramic_Magnets_Datasheet.pdf",
}

FERRITE_NOTES = (
    "원문 verbatim `Poisson’s Ratio  ν  0.28`. Eclipse Magnetics "
    "`Ferrite Magnets/Ceramic Magnets Datasheet`(Rev.2021) p.3 `Physical Characteristics (Typical)` 표에서 왔다 — "
    "**등급별이 아니라 소결 하드페라이트 공통값**이다(58차 TA 가 PDF 전문을 열어 확인했고, 같은 문서의 등급표는 "
    "Br·Hc·Hci·(BH)max 자기특성만 싣고 물리특성 열이 하나도 없다). 그래서 이 행은 그 공통값을 이 등급에 대입한 "
    "**가정값**이라 tier4·estimated·assumption 으로 세운다 — 등급별 실측이 들어오면 대표값 선택이 자동으로 밀어낸다. "
    "계보 — 같은 표의 같은 값이 형제 등급 재료 424(Y30)·425(Y35)·2533(C8/C8A)에 이미 "
    "`grade_scope: class value — sintered hard ferrite, not grade-specific` tier3 규약으로 실려 있고, "
    "65차 AB 가 같은 표의 밀도(4.9~5.1 g/cc)와 영률(1.8x10^11 Pa)을 이 25등급에 같은 규약으로 세웠다. "
    "이 행은 그 표의 세 번째 열을 같은 규율로 닫는 것이다. "
    "**기존 `core_rejected_printed_value` 판정은 지우지 않았다** — '벤더가 이 등급에 대해 이 열을 찍지 않는다' 는 "
    "사실은 여전히 참이고, 그 판정문이 verbatim *\"계보를 따를지 안 따를지는 다음 파동의 판단\"* 이라 적어 두었다. "
    "물리 검산 — 등방재 한계 −1<ν<0.5 안이고, 소결 산화물 세라믹의 통상 대역(0.24~0.31)에 든다. "
    "§657 자기검사 — 이 한 값이 25종에 간다. 값 가짓수 1 / 재료 25 는 주입 지문이지만, "
    "그것이 **원문이 이 값을 등급별로 찍지 않기 때문**임을 `grade_scope` 조건축과 이 문장이 그대로 밝힌다."
)

mats_a = [{
    "match_name": nm,
    "source": ECLIPSE,
    "properties": [{
        "key": "mechanical.poisson_ratio",
        "value": 0.28,
        "unit": None,
        "method": "estimated",
        "tier": 4,
        "conditions": {
            "assumption": True,
            "temperature_c": 20,
            "basis": "vendor class value (grade-independent)",
            "grade_scope": "class value — sintered hard ferrite (Sr ferrite), not grade-specific",
            "prior_verdict": "core_rejected_printed_value — 58차 TA 가 '이 표는 등급별이 아니다' 로 기각한 칸이다. "
                             "t4·assumption 으로 다시 세우는 것은 원문의 주장을 되살리는 것이 아니라 우리 가정으로 세우는 것이다",
        },
        "notes": FERRITE_NOTES,
    }],
} for mid, nm in FERRITE]

# ---- ba02 -----------------------------------------------------------------
DELRIN_GUIDE = {
    "kind": "datasheet",
    "url": "https://kmsbearings.com/content/category/pdfs/Delrin_Acetal_Design_Guide.pdf",
    "title": "Delrin® acetal resin — Design Guide, Module III (DuPont Engineering Polymers, Reorder No. H-57472 (95.1))",
    "authors": "DuPont Engineering Polymers (corporate author)",
    "year": 1995,
    "publisher": "DuPont",
    "local_path": "standards_appnotes/poly/DuPont_Delrin_Acetal_Resin_Design_Guide_ModuleIII.pdf",
}
TORLON_GUIDE = {
    "kind": "datasheet",
    "url": "https://drakeplastics.com/wp-content/uploads/2020/01/Torlon-PAI-Design-Guide_EN-227547.pdf",
    "title": "Torlon® PAI Design Guide (Solvay Specialty Polymers, Version 5.0, R 07/2015)",
    "authors": "Solvay Specialty Polymers (corporate author)",
    "year": 2015,
    "publisher": "Solvay Specialty Polymers",
    "local_path": "standards_appnotes/poly/Solvay_Torlon_PAI_Design_Guide_EN_227547.pdf",
}
INDIUM_APPNOTE = {
    "kind": "datasheet",
    "url": "https://www.indium.com/wp-content/uploads/2025/03/Physical-Constants-of-Pure-Indium-APPNOTE-97532-R7-1.pdf",
    "title": "Physical Constants of Pure Indium — Application Note (Indium Corporation, Form No. 97532 R7)",
    "authors": "Indium Corporation (corporate author)",
    "year": 2022,
    "publisher": "Indium Corporation",
    "local_path": "standards_appnotes/mech/IndiumCorporation_Physical_Constants_of_Pure_Indium_APPNOTE-97532-R7-1.pdf",
}

mats_b = [
    {
        "match_name": "Delrin 500 — 폴리아세탈 호모폴리머 POM-H (Böhm 1990)",
        "source": DELRIN_GUIDE,
        "properties": [{
            "key": "mechanical.poisson_ratio",
            "value": 0.35,
            "unit": None,
            "method": "handbook",
            "tier": 2,
            "conditions": {
                "temperature_c": 23,
                "grade": "Delrin 500",
                "test_method": "표에 시험법이 없다 — 물성표의 `Poisson Ratio` 행만 ASTM·ISO 열이 둘 다 `—` 다",
            },
            "notes": (
                "원문 verbatim(본문) — `Poissons’ Ratio for Delrin 500 at 23°C (73°F) is 0.35. The value is not "
                "expected to change significantly for other Delrin acetal resins.` **등급과 온도를 이름으로 찍은 문장**이다. "
                "같은 문서 물성표의 `Poisson Ratio` 행도 100·500·900·1700 네 등급 열에 전부 0.35 를 찍는다(그 행만 "
                "ASTM·ISO 시험법 열이 `—` 라 tier1 실측으로 세지 않고 tier2·handbook 으로 둔다). "
                "재료 동일성 검산 — 같은 문서의 Delrin 500 인장탄성률 3100 MPa 가 이 DB 재료의 tier1 영률 "
                "3200 MPa(Delrin 500 NC010 TDS, 출처 4736)와 3% 안에서 만난다. "
                "**조달 경위 — 제품 TDS 가 아니라 설계가이드다.** Delrin 500 NC010 제품정보(출처 4736)에는 포아송비 행이 없다. "
                "ISO 10350-1/CAMPUS 서식에 그 항목이 없기 때문이고(BLOCKED_SOURCES I절), 같은 벤더의 **설계가이드**에는 있다. "
                "§43 역산은 하지 않았다 — 이 값은 원문이 인쇄한 것이지 E·G 에서 만든 것이 아니다."
            ),
        }],
    },
    {
        "match_name": "Torlon 4301 — 폴리아미드이미드 PAI (Böhm 1990)",
        "source": TORLON_GUIDE,
        "properties": [{
            "key": "mechanical.poisson_ratio",
            "value": 0.39,
            "unit": None,
            "method": "handbook",
            "tier": 2,
            "conditions": {
                "grade": "4301",
                "temperature": "not stated in the source row (Table 3 `Typical properties`)",
                "test_method": "표에 시험법이 없다 — `Poisson’s ratio` 행만 ASTM 열이 비어 있다(이웃 행은 D638·D790·D695)",
            },
            "notes": (
                "원문 verbatim — Solvay `Torlon® PAI Design Guide`(Version 5.0) p.6 `Table 3: Typical properties – SI units` "
                "의 `Poisson’s ratio` 행 `0.45  0.43  0.39  0.39  0.39  0.42`. 여덟 등급 열(4203L·5030·7130·**4301**·4275·4435·"
                "4630·4645) 중 넷째 열이 4301 이고 그 값이 **0.39** 다(마지막 두 등급은 이 행이 빈칸). "
                "**열 배정을 두 번 독립 검산했다**(브리프 604·606) — 같은 표 같은 열의 `Tensile modulus 6.8 GPa` 가 이 DB 재료의 "
                "tier1 영률 6830 MPa(Torlon 4301 TDS, 출처 4737)와 0.4% 안에서 만나고, `Density 1.46 g/cm³` 가 tier1 밀도 "
                "1460 kg/m³ 와 정확히 같다. 같은 값이 p.8 의 US 단위 표(Table 4)에도 같은 순서로 한 번 더 인쇄돼 있다. "
                "**조달 경위 — 제품 TDS 가 아니라 설계가이드다.** Torlon 4301 TDS(출처 4737)에는 포아송비 행이 없다. "
                "§43 역산은 하지 않았다."
            ),
        }],
    },
    {
        "match_name": "Indium Solder (99.99% In)",
        "source": INDIUM_APPNOTE,
        "properties": [{
            "key": "mechanical.poisson_ratio",
            "value": 0.4498,
            "unit": None,
            "method": "handbook",
            "tier": 2,
            "conditions": {
                "temperature_c": 20,
                "grade_scope": "pure indium (문서 제목이 `Physical Constants of Pure Indium` 이다). "
                               "이 재료는 99.99% In 이라 순금속 상수표가 그대로 적용된다",
            },
            "notes": (
                "원문 verbatim — `Poisson’s ratio at 20°C: 0.4498` (Indium Corporation Application Note "
                "`Physical Constants of Pure Indium`, Form No. 97532 R7, `Mechanical Properties` 블록). "
                "재료 동일성 검산 두 줄 — 같은 문서의 `20°C 7.300 g/cc` 가 이 DB 재료의 밀도 7310 kg/m³ 와 0.14% 안에서 만나고, "
                "`Tensile modulus: 10.6 GPa` 가 tier1 이 아닌 영률 10.82 GPa(INDALLOY 합금표, 출처 4753)와 2% 안에서 만난다. "
                "(같은 블록이 `Elastic modulus at 20°C: 12.74 GPa in tension` 도 함께 찍는데 두 값의 차이는 원문이 설명하지 않는다 — "
                "포아송비 칸에는 영향이 없다.) 물리 검산 — 순금속 In 은 연질 FCT 금속이라 ν 가 Pb(0.44)와 같은 대역이고 등방 한계 0.5 아래다. "
                "**조달 경위** — 이 재료의 기존 출처(INDALLOY 합금표·중국 벤더 제품매뉴얼·Wu 2008 Anand 논문) 셋 다 포아송비 열이 없다. "
                "벤더의 **응용노트**가 그 열을 가진 유일한 서식이었다(§669 — ν 의 첫 문은 제품 시트가 아니라 설계 핸드북·응용노트다). "
                "§43 역산은 하지 않았다."
            ),
        }],
    },
]

json.dump({"batch": "66차 BA — 하드페라이트 25등급 포아송비(클래스 공통값 t4)", "materials": mats_a},
          open(OUT_A, "w"), ensure_ascii=False, indent=1)
json.dump({"batch": "66차 BA — 조달한 벤더 설계가이드·응용노트의 등급 지목 포아송비 3칸(t2)", "materials": mats_b},
          open(OUT_B, "w"), ensure_ascii=False, indent=1)
print(f"{OUT_A}: {len(mats_a)}종 {sum(len(m['properties']) for m in mats_a)}행")
print(f"{OUT_B}: {len(mats_b)}종 {sum(len(m['properties']) for m in mats_b)}행")
