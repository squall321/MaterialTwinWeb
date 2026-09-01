#!/usr/bin/env python
# thermal 계통 코어 빈칸 110개 중 93개의 판정을 §582 가 정한 칸에 박는다(56차 RD).
#
#   core_not_applicable            물리적으로 그 물성이 정의되지 않는다 (V1)
#   core_absent_from_vendor_sheet  시트를 실제로 열어 그 열이 없음을 확인했다 (V2)
#
# 둘 다 **{물성키: 사유} dict** 로 적는다 — 문자열로 적으면 그 재료의 코어 전부를 덮어
# 집계가 범위를 지어낸다(§582·593). 남은 11칸(V5)에는 아무것도 안 적는다 — 그게 표적이다.
#
# 사용: MATERIALTWIN_DATA_DIR=<라이브> python3 scripts/catalog/out_rd/rd02_core_verdicts.py [--apply]
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import mcp_server as M  # noqa: E402

RHO = "physical.density"
E = "mechanical.youngs_modulus"
NU = "mechanical.poisson_ratio"
UTS = "mechanical.tensile_strength"
CTE = "thermal.expansion_linear"
TC = "thermal.conductivity"
CP = "thermal.specific_heat"

NA = "core_not_applicable"
VEND = "core_absent_from_vendor_sheet"

R_DEVICE = (
    "밀봉 히트파이프 모듈이라 재료가 아니라 소자다(브리프 475). 이미 든 열전도율은 상변화 소자의 "
    "유효값이고(1,061~2,468 W/(m*K), 순동 400을 넘는다) 검사기가 이미 소자값으로 드러낸다. "
    "소자에는 밀도·탄성계수·포아송비·선팽창·비열·인장강도가 재료 코어로 정의되지 않는다 — "
    "구성 부품(소결동 윅·구리관·Cu 합금판)이 따로 서야 한다. 56차 RD 판정."
)
R_GREASE = (
    "비경화 실리콘 페이스트다. 자립 시편이 존재하지 않아 인장·압축 시험을 걸 수 없고 "
    "탄성계수·포아송비·인장강도가 물리적으로 정의되지 않는다(브리프 584 의 OSP 전환피막과 같은 자리). "
    "이 갈래의 물성축은 열전도율·열저항·본드라인 두께·점도다. 56차 RD 판정."
)
R_LIQUID60 = (
    "Indalloy 60(75.5 Ga, 24.5 In)은 공정점이 16 °C 다 — 원문(Roy 2015)이 'wet thermal interface "
    "material' 로 쓰고 실제로 녹여 발라 시험한다. 사용 온도에서 액상이라 탄성계수·포아송비·인장강도가 "
    "정의되지 않는다. 제조사 편찬표(Indalloy alloy chart, 2006)의 60행도 융점과 밀도만 인쇄한다. 56차 RD 판정."
)

R_3M = (
    "3M Thermally Conductive Adhesive Transfer Tapes 8805/8810/8815/8820 기술자료(2015-07)를 열어 "
    "확인했다 — 인장강도 행이 없다. 캐리어 없는 접착 전사테이프라 시트가 강도축을 90° 박리·중첩전단·"
    "정하중 유지력으로 인쇄하고 그 셋은 이미 카탈로그에 있다. 56차 RD 확인."
)
R_LAIRD_STIFF = (
    "Laird T-flex 300 시리즈 시트 두 판(2006 A15293-00 Rev.B · 2023-09-18 판)을 열어 확인했다 — "
    "탄성계수·포아송비 행이 없다. 시트가 강성축을 경도(Shore 00)와 압력별 % Deflection 으로만 인쇄한다. 56차 RD 확인."
)
R_LAIRD_CP = (
    "Laird T-flex 300 시리즈 시트 두 판(2006·2023)에 비열 행이 없다. 열전도율을 ASTM D5470 으로 "
    "직접 재므로 ρ·Cp 가 필요 없다(브리프 50). 56차 RD 확인."
)
R_LAIRD_320_UTS = (
    "Laird T-flex 300 시리즈 2006 시트가 T-flex 320 열의 인장강도(ASTM D412)와 연신율을 'N/A' 로 "
    "인쇄한다 — 0.020 in(0.51 mm) 두께라 D412 시편을 못 뜬다. 같은 표의 340~3100 은 15 psi 를 "
    "인쇄하고 그 넷은 이미 카탈로그에 있다. 56차 RD 확인."
)
R_SHINETSU = (
    "Shin-Etsu MicroSi G751 (Non-Solvent) 기술자료(2016-09-15)를 열어 확인했다 — General properties "
    "상자가 색·점도·비중·열전도율·열저항·본드라인 두께만 인쇄하고 선팽창·비열 행이 없다. "
    "열전도율을 hot disc 로 직접 재므로 비열이 필요 없다(브리프 50). 56차 RD 확인."
)
R_HENKEL = (
    "Henkel BERGQUIST GAP PAD TGP 시트 넉 장(2400 2018-11 · HC5000 · 1300U 2018-10 · A2000 2018-10)을 "
    "열어 확인했다 — 포아송비·선팽창·인장강도 행이 없다. 이 시트들은 밀도(ASTM D792)·비열(ASTM E1269)·"
    "탄성계수(ASTM D575)·열전도율(ASTM D5470)을 인쇄하고 그 넷은 이미 카탈로그에 있다. 56차 RD 확인."
)
R_CHOM_STIFF = (
    "Parker Chomerics THERM-A-GAP Pads 자료(TB-1016-1-07)를 열어 확인했다 — 탄성계수·포아송비·인장강도 "
    "행이 없다. 시트가 강성축을 경도(Shore 00/A)·Penetrometer·압력별 % Deflection(ASTM C165)으로만 인쇄한다. 56차 RD 확인."
)
R_CHOM_HCS10_CTE = (
    "Parker Chomerics THERM-A-GAP Pads 자료(TB-1016-1-07)가 HCS10 열의 선팽창계수(ASTM E831)를 "
    "'N/A' 로 인쇄한다. 같은 표의 569/570 은 250, 579/580 은 150, G974/974/976 은 100 ppm/K 를 "
    "인쇄하고 그 일곱은 이미 카탈로그에 있다. 56차 RD 확인."
)
R_IND60 = (
    "Indium Corporation 자사 Indalloy 편찬표(alloy chart sorted by Indalloy number, 2006)의 60행"
    "(75.5 Ga, 24.5 In)이 융점과 밀도(6.35 g/cm3 — 카탈로그 기존 t3 6350 kg/m3 과 일치)만 인쇄한다. "
    "열전도율(W/cm·°C)·선팽창(PPM/°C) 칸이 비어 있고, Ga 계열 액상 합금 행이 계통적으로 그렇다"
    "(14·51·60·77행 모두). 56차 RD 확인."
)
R_IND14 = (
    "Indium Corporation 자사 Indalloy 편찬표(2006)의 14행(100.0 Ga)이 융점 30 °C 와 밀도 5.90 g/cm3"
    "(카탈로그 기존 t3 5900 kg/m3 과 일치)만 인쇄한다 — 열전도율·선팽창·인장강도·탄성계수 칸이 모두 "
    "비어 있다. 원문(Roy 2015) Table 1 도 융점·밀도·비열 셋뿐이다. 순 갈륨(원소)이라 핸드북으로 닫을 수 "
    "있는 자리이나, 상(고상 사방정 대 액상)과 결정 이방성을 먼저 갈라야 한다. 56차 RD 확인."
)
R_IND19 = (
    "Indium Corporation 자사 Indalloy 편찬표(2006)의 19행이 Young's Modulus(PSI x 10^6)·열전도율"
    "(W/cm·°C) 칸을 비워 둔다 — 같은 행의 선팽창 22 PPM/°C 와 인장강도 4,850 PSI 는 인쇄돼 있어 "
    "56차 RD 가 넣었다. 포아송비는 이 표에 열 자체가 없다. 56차 RD 확인."
)

# (material_id, attribute, {key: reason})
PLAN: list[tuple[int, str, dict]] = [
    (2588, NA, {k: R_DEVICE for k in (RHO, E, NU, CTE, CP, UTS)}),
    (2566, NA, {k: R_GREASE for k in (E, NU, UTS)}),
    (2584, NA, {k: R_GREASE for k in (E, NU, UTS)}),
    (2585, NA, {k: R_GREASE for k in (E, NU, UTS)}),
    (2586, NA, {k: R_GREASE for k in (E, NU, UTS)}),
    (2587, NA, {k: R_GREASE for k in (E, NU, UTS)}),
    (924,  NA, {k: R_LIQUID60 for k in (E, NU, UTS)}),

    (57,  VEND, {UTS: R_3M}),
    (349, VEND, {UTS: R_3M}),
    (350, VEND, {UTS: R_3M}),
    (351, VEND, {UTS: R_3M}),

    (2561, VEND, {E: R_LAIRD_STIFF, NU: R_LAIRD_STIFF, CP: R_LAIRD_CP, UTS: R_LAIRD_320_UTS}),
    (2562, VEND, {E: R_LAIRD_STIFF, NU: R_LAIRD_STIFF, CP: R_LAIRD_CP}),
    (2563, VEND, {E: R_LAIRD_STIFF, NU: R_LAIRD_STIFF, CP: R_LAIRD_CP}),
    (2564, VEND, {E: R_LAIRD_STIFF, NU: R_LAIRD_STIFF, CP: R_LAIRD_CP}),
    (2565, VEND, {E: R_LAIRD_STIFF, NU: R_LAIRD_STIFF, CP: R_LAIRD_CP}),

    (2566, VEND, {CTE: R_SHINETSU, CP: R_SHINETSU}),

    (2567, VEND, {NU: R_HENKEL, CTE: R_HENKEL, UTS: R_HENKEL}),
    (2568, VEND, {NU: R_HENKEL, CTE: R_HENKEL, UTS: R_HENKEL}),
    (2569, VEND, {NU: R_HENKEL, CTE: R_HENKEL, UTS: R_HENKEL}),
    (2570, VEND, {NU: R_HENKEL, CTE: R_HENKEL, UTS: R_HENKEL}),

    (2571, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF, CTE: R_CHOM_HCS10_CTE}),
    (2572, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),
    (2573, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),
    (2574, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),
    (2575, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),
    (2576, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),
    (2577, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),
    (2578, VEND, {E: R_CHOM_STIFF, NU: R_CHOM_STIFF, UTS: R_CHOM_STIFF}),

    (924, VEND, {CTE: R_IND60, TC: R_IND60}),
    (925, VEND, {E: R_IND14, NU: R_IND14, CTE: R_IND14, TC: R_IND14, UTS: R_IND14}),
    (926, VEND, {E: R_IND19, NU: R_IND19, TC: R_IND19}),
]


def main() -> int:
    apply = "--apply" in sys.argv
    from app.db import SessionLocal
    from app.models import Material, PropertyValue

    n_cells = 0
    with SessionLocal() as s:
        for mid, attr, verdict in PLAN:
            mat = s.get(Material, mid)
            if mat is None:
                print(f"  ✗ 재료 {mid} 없음")
                return 1
            have = {k for (k,) in s.query(PropertyValue.property_key)
                    .filter(PropertyValue.material_id == mid).distinct()}
            filled = sorted(k for k in verdict if k in have)
            if filled:
                # **채워진 칸에 판정을 박으면 안 된다** — 판정은 빈칸에만 붙는다.
                print(f"  ✗ 재료 {mid} · {attr}: 이미 값이 있는 키에 판정을 붙이려 한다 — {filled}")
                return 1
            n_cells += len(verdict)
            print(f"  {mid:5d} {attr:30s} {len(verdict)}칸  {mat.name[:52]}")

    print(f"\n  판정 칸 합계 {n_cells}")
    if not apply:
        print("  [DRY-RUN] --apply 로 적용한다")
        return 0
    for mid, attr, verdict in PLAN:
        r = M.update_material(material_id=mid, attributes={attr: verdict})
        if "error" in r:
            print(f"  ✗ {mid}: {r['error']}")
            return 1
    print("  [APPLY] 완료")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
