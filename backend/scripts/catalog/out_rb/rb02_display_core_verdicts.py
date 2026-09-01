# 56차 RB — display 계통 빈 코어 칸의 판정을 집계가 읽는 자리에 박는다(브리프 582·593).
#
# 규율 셋.
#   · `core_not_applicable` 은 **dict** 로 쓴다. 문자열로 쓰면 그 재료의 코어 7칸을 통째로 덮어
#     집계가 덮이는 범위를 우리가 지어낸다(coverage_report.subsystem_core 의 na_all 분기).
#   · `core_absent_from_vendor_sheet` 는 **시트를 실제로 연 것만** 적는다(브리프 127).
#   · 판정이 없는 칸은 손대지 않는다 — V5 로 남겨 다음 파동의 표적이 되게 한다(브리프 584 S7).
#
# 사용: MATERIALTWIN_DATA_DIR=... python3 rb02_display_core_verdicts.py [--apply]
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import mcp_server as M  # noqa: E402

RHO, E, NU = "physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio"
CTE, TC, HC = "thermal.expansion_linear", "thermal.conductivity", "thermal.specific_heat"
UTS = "mechanical.tensile_strength"

# ── V1 해당 없음 — 증착 유기 소분자 ────────────────────────────────────────────
# 45차 GD 가 이미 판정을 내렸으나 **문자열**로 적어 코어 7칸을 통째로 덮었다.
# GD 자신의 문장이 "밀도(단결정)·열전도율(박막)은 원리적으로 가능하다" 라고 밝히므로
# 해당 없음은 역학 4칸뿐이다. dict 로 좁힌다.
OLED_NA = {
    UTS: "증착 박막으로만 존재해 자립 인장시편이 없다 — 인장강도는 물리적으로 정의되지 않는다. 45차 GD 판정을 dict 로 좁혀 다시 박았다(브리프 603 대비 §582·593).",
    NU: "포아송비는 자립 시편의 2축 변형 측정을 요구한다. 기판에 구속된 증착 박막에서는 정의되지 않는다(48차 JC 가 172종을 molecular 로 옮긴 그 갈래).",
    E: "벌크 시편이 존재하지 않는다. 이 갈래의 물성축은 HOMO/LUMO·밴드갭·삼중항에너지·발광파장·이동도다 — 45차 GD.",
    CTE: "벌크 시편이 존재하지 않아 선팽창계수가 정의되지 않는다 — 45차 GD.",
}
OLED_NOT_SOLD = {1759, 1758}          # PO1 · PO14 — 저자 연구실 합성물이라 벤더 자체가 없다
OLED_IDS = [1746, 1760, 1763, 1759, 1758, 1762, 1761, 1651, 1764]

_OSSILA = ("공급사 시트를 열었다 — Ossila 의 CBP(58328-31-7) 제품 사양표는 "
           "`CAS Number · Chemical Formula · Molecular weight · HOMO/LUMO · Purity(>99.5% sublimed) · "
           "Melting Point · Appearance` 일곱 칸만 인쇄하고 밀도·열전도율·비열·탄성계수·포아송비·"
           "인장강도·선팽창계수를 한 칸도 싣지 않는다(브리프 127). OLED 승화정제 소분자는 이 사양표 "
           "형식을 공유하므로 같은 판정을 이 갈래에 붙인다 — **연 시트는 CBP 한 장이다.**")
OLED_VENDOR = {
    RHO: "이 갈래의 밀도는 단결정 XRD 로 원리적으로 얻을 수 있으나 공급사가 인쇄하지 않는다. " + _OSSILA,
    TC: "박막 열전도율은 3ω 등으로 원리적으로 측정 가능하나 공급사가 인쇄하지 않는다. " + _OSSILA,
    HC: "DSC 로 얻을 수 있으나 공급사가 인쇄하지 않는다. " + _OSSILA,
}

# ── V2 벤더 구조적 부재 — 시트를 직접 열어 그 행이 없음을 확인한 것만 ───────────
GORILLA_SHEET = ("Corning Gorilla 계열 PI 시트를 직접 열어 확인했다 — 이 시트들은 "
                 "`Density · Young's Modulus · Poisson's Ratio · Shear Modulus · Hardness · "
                 "Fracture Toughness · Coefficient of Expansion` 까지만 싣고 인장강도·연신 행이 없다"
                 "(브리프 127 재확인). 유리는 흠결 지배 파괴라 인장강도가 시편 상태에 좌우돼 "
                 "벤더가 등급값으로 인쇄하지 않는다.")
GORILLA_THERMAL = ("Corning Gorilla 계열 PI 시트에는 열확산율·비열·열전도율 표가 아예 없다. "
                   "**같은 Corning 안에서 갈린다** — 디스플레이 기판 시트(EAGLE XG · EAGLE XG Slim · "
                   "Lotus NXT · Astra)는 25~500 °C 6점 표를 싣는데, 커버유리 시트(GG2·3·4·5·6·7i · "
                   "Victus · Victus 2 · Glass Ceramic 1/2)는 아홉 장 전부 그 표가 없다.")
CORNING_DISPLAY_UTS = ("Corning 디스플레이 기판 PI 시트(EAGLE XG · EAGLE XG Slim · Lotus NXT · Astra)를 "
                       "직접 열어 확인했다 — 네 장 모두 인장강도 행이 없다(브리프 127).")

V2 = {}


def add(mid, mapping):
    V2.setdefault(mid, {}).update(mapping)


# Corning 커버유리
add(429, {UTS: GORILLA_SHEET + " [연 시트] Gorilla Glass 2 PI 시트(Valley Design 미러, DB 출처 243) — "
                               "`Density 2.42 · Young's Modulus 71.5 GPa · Poisson 0.21 · Shear 29.6 GPa · "
                               "Vickers 534/649 · Fracture Toughness 0.68 · CTE 81.4e-7` 로 끝난다."})
for mid, sheet in [(571, "Gorilla Glass 3 with NDR PI 시트(E_050613)"),
                   (2604, "Gorilla Glass 5 PI 시트(Rev C, 2018-04)"),
                   (2605, "Gorilla Glass 6 PI 시트(Rev 1, 2018-09)"),
                   (2606, "Gorilla Glass 7i PI 시트(2024)"),
                   (2676, "Corning Willow Glass Fact Sheet(2019-08)")]:
    add(mid, {UTS: GORILLA_SHEET + f" [연 시트] {sheet}.",
              TC: GORILLA_THERMAL + f" [연 시트] {sheet}.",
              HC: GORILLA_THERMAL + f" [연 시트] {sheet}."})
add(275, {UTS: GORILLA_SHEET + " [연 시트] Gorilla Glass Victus PI 시트."})
add(274, {UTS: GORILLA_SHEET + " [연 시트] Gorilla Glass Victus 2 PI 시트."})

# Corning 디스플레이 기판 — 열물성은 있고 인장강도만 없다
for mid, sheet in [(2618, "EAGLE XG Glass PI 시트(2023)"),
                   (2619, "EAGLE XG Slim Glass PI 시트(2013-08)"),
                   (2620, "Lotus NXT Glass PI 시트(2023)")]:
    add(mid, {UTS: CORNING_DISPLAY_UTS + f" [연 시트] {sheet} — 같은 시트가 열확산율·비열·열전도율은 "
                                         "6점 표로 싣는데 인장강도 칸만 없다."})

# NEG 알칼리프리 기판 4종
NEG = ("Nippon Electric Glass 기판 시트를 직접 열어 확인했다 — Properties 표는 "
       "`Strain point · Young's modulus · Density · CTE(30-380 °C) · Poisson's ratio · Vickers · "
       "Volume resistivity · Dielectric constant · tan δ · Light transmittance · Refractive index · "
       "Chemical durability · Alkali oxide · As,Sb` 로 끝나고 열전도율·비열·인장강도 행이 없다(브리프 127).")
for mid, ref in [(2621, "OA-10G/OA-11 Ref. No. 1910-01E"), (2622, "OA-11 Ref. No. 2510-01E"),
                 (2623, "OA-20 Ref. No. 2510-02E"), (2624, "OA-31 Ref. No. 2510-03E")]:
    add(mid, {UTS: NEG + f" [연 시트] {ref}.", TC: NEG + f" [연 시트] {ref}.", HC: NEG + f" [연 시트] {ref}."})

NEG_FRIT = ("NEG Powder Glass 카탈로그(Ref. No. 2410-19E) `Low Temperature Sealing Glass 2` 표를 직접 열었다 — "
            "LS-3075 열은 `Sealing temperature 450 °C · CTE(30-250 °C) 36.5e-7 · Density 6.91e3 · "
            "Transformation point 300 · Deformation point 330 · Softening point ― · Volume resistivity 10.8 · Color Black` "
            "여덟 칸이 전부다. 봉착용 분말 유리라 벤더가 탄성률·포아송비·열전도율·비열·인장강도를 인쇄하지 않는다(브리프 127).")
add(2627, {E: NEG_FRIT, NU: NEG_FRIT, TC: NEG_FRIT, HC: NEG_FRIT, UTS: NEG_FRIT})

# SCHOTT
SCHOTT_XEN = ("SCHOTT Xensation 데이터시트(ENGLISH 07/2022 kn/nino)를 직접 열어 확인했다 — "
              "밀도·탄성률·포아송비·비틀림계수·경도·CTE·Tg·점도·유전율·손실각·광학상수까지 싣고 "
              "열전도율·비열·인장강도 행이 없다. 강도로 인쇄되는 것은 `4-Point bending strength capable > 800 MPa` "
              "하나뿐인데 부등호이고 두께가 없어 값이 아니다(브리프 474·110·132).")
for mid in (2608, 2609, 2610):
    add(mid, {TC: SCHOTT_XEN, HC: SCHOTT_XEN, UTS: SCHOTT_XEN})
AS87 = ("SCHOTT AS 87 neo 사양시트를 직접 열어 확인했다 — Thermal properties 블록은 "
        "`CTE α(20-300 °C) 9.2e-6 · Mean specific heat cp(20-100 °C) 0.87 J/(g·K) · Tg 598 °C · 점도 3점` "
        "이고 **열전도율 행이 없다.** Mechanical properties 블록도 밀도·이온교환(CS/DoL)·E·ν·G·Knoop·Vickers "
        "까지이고 인장강도 행이 없다(브리프 127).")
add(2611, {TC: AS87, UTS: AS87})

# AGC Dragontrail
DT = ("AGC Dragontrail 스펙시트(Abrisa Technologies, DT 10/22)를 직접 열어 확인했다 — "
      "Mechanical Properties 표는 `Density · Young's Modulus · Poisson's Ratio · Shear Modulus · "
      "Vickers Hardness · Fracture Toughness` 이고, Thermal Properties 표는 **CTE 한 줄뿐**이다. "
      "열전도율·비열·인장강도 행이 없다(브리프 127).")
add(2607, {TC: DT, HC: DT, UTS: DT})

# 3M OCA — TDS 네 장을 직접 열었다
M3 = ("3M 광학투명접착제 TDS 네 장(8171/8172 · 8211~8215 · OCA 817X Series 2018 · 8173KCL 2015)을 "
      "직접 내려받아 확인했다 — 네 장 모두 `tensile`·`elongation`·`modulus` 라는 낱말이 물성표에 없다. "
      "전사테이프형 PSA 는 자립 필름 인장이 관행이 아니라 벤더가 박리력·전단유지력·두께·광학·유전율만 인쇄한다"
      "(브리프 127).")
for mid in (279, 281, 286, 238, 42, 43):
    add(mid, {UTS: M3})

# Dexerials ACF — 제품 사양표 세 장을 직접 열었다
DEX = ("Dexerials ACF 제품 사양표를 직접 열어 확인했다 — 인쇄되는 것은 "
       "`Minimum space · Minimum connection area · Thickness · Particle diameter · "
       "Bonding temperature/time/pressure` 일곱 칸이고 역학·열물성이 한 칸도 없다(브리프 127).")
for mid, page in [(283, "CP540 Series"), (284, "CP692 Series"), (285, "PAF700 Series")]:
    add(mid, {UTS: DEX + f" [연 시트] {page} 제품 사양표."})

# ── V4 등급 미확정 — 광학등급 배리어 기재 필름 4종(브리프 58) ────────────────
GRADE_UNDET = ("미식별 — 원문이 `optical grade` 라는 클래스 서술만 인쇄하고 등급 코드를 밝히지 않는다. "
               "Melinex 도 Teijin PEN/PET/PC 도 등급마다 인장강도·탄성률·CTE 가 갈리므로 "
               "등급이 안 닫히면 벤더 시트를 붙일 수 없다(브리프 58). 코어 7칸이 원리적으로 못 닫힌다 — "
               "닫으려면 원논문(Erlat 2003 · Low 2005)이 등급 코드를 인쇄했는지부터 확인해야 한다. — 56차 RB")
V4_IDS = {2254: GRADE_UNDET, 2225: GRADE_UNDET, 2224: GRADE_UNDET, 2223: GRADE_UNDET}


def main() -> int:
    apply = "--apply" in sys.argv
    n_na = n_v2 = n_v4 = 0
    plan = []
    for mid in OLED_IDS:
        attrs = {"core_not_applicable": dict(OLED_NA),
                 "core_not_applicable_before_correction":
                     "45차 GD 가 남긴 **문자열** 판정을 dict 로 좁혔다(브리프 594 — 이미 있던 칸을 "
                     "덮어쓰면 되돌릴 값을 남긴다). 옛 문자열: '증착 박막으로 쓰는 유기 소분자다. "
                     "벌크 시편이 존재하지 않아 인장강도·포아송비·탄성계수·선팽창은 물리적으로 정의되지 않고 "
                     "공급사도 인쇄하지 않는다. 이 갈래의 물성축은 HOMO/LUMO·밴드갭·삼중항에너지·발광파장·"
                     "이동도다. 밀도(단결정)·열전도율(박막)은 원리적으로 가능하나 소자 해석의 표적이 아니다. "
                     "— 45차 GD'"}
        n_na += len(OLED_NA)
        if mid not in OLED_NOT_SOLD:
            attrs["core_absent_from_vendor_sheet"] = dict(OLED_VENDOR)
            n_v2 += len(OLED_VENDOR)
        else:
            attrs["core_verdict_undecided"] = (
                "밀도·열전도율·비열은 판정을 못 내린다 — PO1·PO14 는 저자 연구실이 합성해 이름 붙인 "
                "포스핀옥사이드 수송재라 **공급사 자체가 없다**. 벤더 구조적 부재도 해당 없음도 아니고, "
                "원논문(Swensen 2011)이 재지 않았을 뿐이다. 다음 파동의 표적으로 남긴다. — 56차 RB")
        plan.append((mid, attrs))
    for mid, mapping in V2.items():
        plan.append((mid, {"core_absent_from_vendor_sheet": mapping}))
        n_v2 += len(mapping)
    for mid, why in V4_IDS.items():
        plan.append((mid, {"identification_status": why}))
        n_v4 += 7

    print(f"대상 재료 {len(plan)}종 · V1 {n_na}칸 · V2 {n_v2}칸 · V4 {n_v4}칸")
    if not apply:
        print("[DRY-RUN] --apply 를 붙여야 쓴다.")
        return 0
    for mid, attrs in plan:
        r = M.update_material(material_id=mid, attributes=attrs)
        if "error" in r:
            print(f"  ✗ [{mid}] {r['error']}")
        else:
            print(f"  · [{mid}] {r['name'][:60]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
