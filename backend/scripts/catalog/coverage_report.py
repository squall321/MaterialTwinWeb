#!/usr/bin/env python
# 해석별 물성 커버리지 — "필요한 것의 몇 %"를 재료×물성 격자로 정직하게 센다.
#
# 분모를 두 가지로 낸다.
#   (a) 셀 채움률  = 채워진 (재료, 필수물성) 칸 / 전체 칸.  물성 수집의 진척도.
#   (b) 재료 준비율 = 그 해석을 실제로 돌릴 수 있는 재료 수 / 대상 재료 수.  해석 가능성.
# (a)가 높아도 (b)는 낮을 수 있다 — 재료마다 마지막 한 칸이 다르면 그렇다.
#
# 사용: .venv/bin/python scripts/catalog/coverage_report.py [--json]
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"

E = "mechanical.youngs_modulus"
NU = "mechanical.poisson_ratio"
G = "mechanical.shear_modulus"
RHO = "physical.density"
CTE = "thermal.expansion_linear"
TC = "thermal.conductivity"
HC = "thermal.specific_heat"

# 택일군 — 하나만 있어도 그 역할이 채워진다.
PLAS = (("mechanical.yield_strength",), ("mechanical.tensile_strength", "mechanical.elongation_at_break"))
RATE = ("mechanical.cowper_symonds_c", "mechanical.cowper_symonds_p",
        "mechanical.dynamic_increase_factor", "mechanical.yield_strength_at_rate",
        "mechanical.johnson_cook_c")
PRONY = ("mechanical.prony_relaxation_time", "mechanical.prony_tensile_modulus",
         "mechanical.prony_shear_modulus", "mechanical.prony_relative_modulus", G)
WET = ("physical.contact_angle_water", "physical.surface_energy")
# 흡습 세 키를 다 넣는다. 24h만 세던 것은 자의적이었다 — 셋 다 "이 재료가 물을 얼마나
# 머금는가"라는 같은 양이고, 어느 것이 인쇄되는지는 시험규격 관행이 정한다.
# 유럽식 ISO 62 시트(BASF·Covestro·Victrex·Celanese·EMS)는 포화와 23 °C/50 %RH 평형만 싣고
# 24h 침지값을 아예 발표하지 않는다. 18종을 벤더 문서까지 가서 확인했고 24h가 있는 건
# Envalior 2종뿐이었다. 24h만 요구하면 이 계열은 자료가 있어도 영원히 빈 칸이다.
# 오히려 흡습 팽윤은 사용 조건인 23 °C/50 %RH 평형이 가장 적합하다.
MOIST = ("physical.water_vapor_transmission", "physical.gas_permeability_h2o",
         "physical.diffusion_coefficient", "chemical.water_absorption_24h",
         "chemical.water_absorption_saturation", "chemical.moisture_absorption_equilibrium")
HYPER = ("mechanical.hyperelastic_coefficient", "mechanical.hyperelastic_exponent")
ADH = ("interface.peel_strength", "interface.lap_shear_strength", "interface.die_shear_strength")
# taxonomy 실명이다. volume_resistivity·loss_tangent로 쓰면 존재하지 않는 키를 세게 돼
# 전기·EMI가 실제보다 낮게 나온다(실제로 그랬다 — 유전율 하나만 세고 있었다).
ELEC = ("electrical.dielectric_constant", "electrical.resistivity_volume",
        "electrical.dissipation_factor")
FATIG = ("mechanical.fatigue_strength_coefficient", "mechanical.fatigue_ductility_coefficient",
         "mechanical.darveaux_constant", "mechanical.morrow_energy_coefficient",
         # Stromeyer형도 수명 곡선을 세운다 — 점근 응력이 있는 재료는 이쪽으로만 담긴다.
         "mechanical.fatigue_stromeyer_coefficient")
O2 = ("physical.gas_permeability_o2", "physical.gas_solubility")
PHOTO = ("optical.excited_state_lifetime", "optical.stern_volmer_constant",
         "optical.bimolecular_quenching_rate")

# 대상 필터 — 전 재료가 대상이 아닌 해석이 있다. 벌크 금속에 층두께를 요구하면 척도가 왜곡된다.
FILMISH = ("film", "tape", "oca", "ocr", "psa", "adhesive", "coating", "laminate",
           "foil", "sheet", "pi base", "foam", "폼")
# 산소 소광은 두 역할로 갈라야 한다. 한 묶음으로 재면 분모가 거짓이 된다.
#   발광체 — 고립 분자다. 투과계수·용해도는 벌크 수송 물성이라 정의 자체가 없다.
#   매트릭스 — 벌크 필름이다. 여기수명·Stern-Volmer는 발광체가 아니면 없다.
# 이전 정의는 둘을 한 스코프에 넣고 양쪽을 다 요구해서, 92종 중 71종이
# "원리적으로 못 채우는 칸"을 세고 있었다. 0.0%는 수집 실패가 아니라 척도 오류였다.
EMITTER = ("emitter", "dopant", "tadf", "iridium", "ir(", "ir-", "pt(", "pd(",
           "ptoep", "pdoep", "porphyrin", "coumarin", "photoinitiator", "irgacure",
           "thioxanthone", "benzophenone", "quantum dot", "phosphorescent", "phosphor dye",
           "red phosphor", "blue emitter", "o2 sensor")
# 매트릭스는 산소가 실제로 확산해 지나가는 벌크 층이다.
MATRIX_O2 = ("oca", "psa", "optically clear", "color filter", "encapsulation", "barrier",
             "polyimide", "acrylate", "coverlay", "adhesive film")
# 피로는 반복하중을 받는 구조·솔더 계열이 대상이다.
FATIGUE_CAT = ("metal", "composite", "ceramic")
ELASTOMER = ("rubber", "foam")
ABSORBENT = ("polymer", "composite", "rubber", "foam")

# (이름, 필수물성, [택일군], 대상필터, 설명)
ANALYSES = [
    ("구조·강성", [E, NU, RHO], [], None,
     "정적 변형·모달. 모든 해석의 기본 골격"),
    ("낙하·충격", [E, NU, RHO], [PLAS, RATE], None,
     "율속 경화가 없으면 항복을 20~50% 과소평가한다"),
    ("열전달·방열", [RHO, TC, HC], [], None,
     "SoC 발열 → 방열시트 → 프레임 경로의 과도해석"),
    ("열응력·워피지", [E, NU, RHO, CTE], [], None,
     "리플로우 휨, 라미네이션 잔류응력, 온도사이클"),
    ("폴더블 벤딩", [E, NU, RHO], [PRONY], "film",
     "점탄성 완화가 접힘자국(crease) 회복을 지배한다"),
    ("결로(표면)", [RHO, TC, HC], [WET], None,
     "표면온도가 이슬점 아래로 가는가 + 물방울이 맺히는가"),
    ("결로(투습)", [RHO, TC, HC], [MOIST], "absorbent",
     "실링을 통과하는 수증기량. 밀폐공간 내부 결로"),
    ("초탄성(실링·완충)", [RHO], [HYPER], "elastomer",
     "가스켓 압축, 완충폼 거동"),
    ("접착·박리", [RHO], [ADH], "film",
     "낙하 시 실제로 깨지는 건 접착층인 경우가 많다"),
    ("전기·EMI", [], [ELEC], None,
     "고속 신호 무결성, 안테나, 차폐"),
    ("피로·수명", [E, RHO], [FATIG], "fatigue",
     "솔더 열피로, 장기 반복하중"),
    ("산소소광-발광체", [], [PHOTO], "emitter",
     "여기수명·Stern-Volmer. 소광 자체를 푸는 쪽"),
    ("산소확산-매트릭스", [], [O2], "matrix_o2",
     "산소가 지나가는 벌크 층의 투과·용해"),
]


def load():
    c = sqlite3.connect(DB)
    mat = {i: (n, cat) for i, n, cat in c.execute("select id,name,category from material")}
    own = defaultdict(set)
    # tier4는 **가정·계산값**이다. 칸은 채우지만 근거가 아니다.
    # 두 집합을 따로 들고 다니며 "가정 포함"과 "실측 기반"을 나란히 낸다 —
    # 하나만 내면 2,628칸(18.1%p)이 실제 확보인 것처럼 보인다.
    meas = defaultdict(set)
    for mid, k, t in c.execute(
            "select material_id, property_key, quality_tier from property_value"):
        own[mid].add(k)
        if t <= 3:
            meas[mid].add(k)
    return c, mat, own, meas


def scope(mat, filt):
    if filt == "film":
        return [m for m in mat if any(w in mat[m][0].lower() for w in FILMISH)]
    if filt == "elastomer":
        return [m for m in mat if mat[m][1] in ELASTOMER]
    if filt == "absorbent":
        return [m for m in mat if mat[m][1] in ABSORBENT]
    if filt == "emitter":
        return [m for m in mat if any(w in mat[m][0].lower() for w in EMITTER)]
    if filt == "matrix_o2":
        return [m for m in mat if any(w in mat[m][0].lower() for w in MATRIX_O2)]
    if filt == "fatigue":
        return [m for m in mat if mat[m][1] in FATIGUE_CAT]
    return list(mat)


def grp_ok(ks, grp):
    """택일군 판정. PLAS는 '항복 OR (인장 AND 연신)'이라 중첩 튜플로 온다."""
    if grp and isinstance(grp[0], tuple):
        return any(all(k in ks for k in alt) for alt in grp)
    return any(k in ks for k in grp)


# ── 구조적 부재 ────────────────────────────────────────────────────────────────
# **그 물성이 그 재료군에서 애초에 발표되지 않는다**고 여러 파동이 각자 확인한 칸이다.
# 분모에 남겨 두면 100%를 향해 가는 것처럼 보이지만 실제로는 도달할 수 없다.
#
# 규율 셋.
#  1. **재료 단위가 아니라 (재료군 × 물성) 단위다.** 저분자 도판트도 광물리 물성은 있고,
#     점착테이프도 박리강도는 있다. 없는 것만 뺀다.
#  2. **증거 있는 것만.** 파동을 넘어 반복 확인되고 BLOCKED_SOURCES·PROPERTY_DATA_HISTORY에
#     기록된 것만 넣는다. 한 번 못 찾은 것은 부재가 아니다.
#  3. **페이월은 부재가 아니다.** 접근 문제는 언제든 열릴 수 있으므로 분모에 남긴다.
#     (FR-4 방향별 열전도율, EMC 포아송비 등이 그 예다.)
# [2026-08-14] `"ir-"` 가 **"a`ir-`sintered"** 와 **"`IR-`cut dye"** 를 잡고 있었다.
# 소결 Ag 페이스트 4종·컬러필터 2종·PSZ-air 3종이 도판트로 분류돼 이 선언의 반례가 됐고,
# **그 반례 때문에 발광체 43종의 젖음 부재 선언이 통째로 은퇴해 있었다.**
# 20차 H가 발광체 × 젖음을 근거 다섯으로 부재 판정하면서 드러났다.
# 부분일치 매처는 **짧은 토큰일수록 위험하다** — 17차 무결성 오탐과 같은 유형이다.
_DOPANT = ("emitter", "dopant", "tadf", "iridium", "ir(", "ir-containing", "pt(", "porphyrin",
           "coumarin", "photoinitiator", "irgacure", "thioxanthone", "benzophenone",
           "phosphor dye", "phosphorescent", "ptoep", "pdoep")
_TAPE = ("tape", "psa", "oca ", "ocr", "adhesive transfer", "vhb", "acxplus",
         "duplocoll", "arclear", "optically clear adhesive")
_LAMINATE = ("laminate", "prepreg", "ccl", "coverlay", "megtron", "duroid", "i-tera",
             "astra mt", "tu-", "it-1", "it-9", "np-155", "s1000", "rf-35", "tly-",
             "tlx-", "clte", "ro40", "ro30", "ultralam", "tsm-ds3", "chukoh")

# (재료 매처, 못 채우는 물성 키 집합, 사유)
# 피로 택일군 다섯 키 — 13차 선언이 여러 군에서 같은 집합을 쓴다.
_FATIG_SET = {
    "mechanical.fatigue_strength_coefficient", "mechanical.fatigue_ductility_coefficient",
    "mechanical.darveaux_constant", "mechanical.morrow_energy_coefficient",
    "mechanical.fatigue_stromeyer_coefficient",
}

UNFILLABLE = [
    # 광물리 논문은 λ·Φ_PL·τ·HOMO/LUMO만 인쇄한다. 벤더 TDS 자체가 없다.
    # 4·5·6·7차 파동이 각각 독립으로 확인(PubChem에 Heat Capacity 항목 없음,
    # NIST WebBook CAS 조회 전무, 젖음·CTE·기계물성 문자열 0건).
    (_DOPANT, {
        "physical.density", "thermal.conductivity", "thermal.specific_heat",
        "thermal.expansion_linear", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
        "physical.contact_angle_water", "physical.surface_energy",
        "electrical.dielectric_constant", "electrical.resistivity_volume",
        "electrical.dissipation_factor",
    }, "저분자 도판트 — 광물리 물성만 발표된다"),

    # 벤더가 두께·박리력·유지력·내열만 찍는 문서 형식이다. 전 벤더 카탈로그 grep 0건.
    # CTE는 "피착재 팽창 차이를 흡수한다"는 판매 문구만 나온다.
    # 아크릴 PSA·VHB에는 **항복점 자체가 없다**(초탄성-점탄성으로 모델링한다).
    (_TAPE, {
        "thermal.expansion_linear", "thermal.specific_heat",
        "mechanical.youngs_modulus", "mechanical.yield_strength",
        "mechanical.prony_relaxation_time",
    }, "점착테이프 — 벤더가 발표하지 않는다(항복점은 물리적으로도 정의되지 않는다)"),

    # 11개 벤더 전수 확인. 유일한 예외가 AGC RF-35TC다. 밀도도 안 낸다(수지 함량·두께로 대신).
    # 피로는 IPC-4101 보고 항목이 아니다.
    (_LAMINATE, {
        "thermal.specific_heat",
        "mechanical.fatigue_strength_coefficient", "mechanical.fatigue_strength_exponent",
        "mechanical.fatigue_ductility_coefficient", "mechanical.fatigue_ductility_exponent",
    }, "PCB·RF 라미네이트 — 비열·피로를 어느 벤더도 발표하지 않는다"),
    # [2026-08-10] 위 선언의 **전제는 참이고 결론이 틀렸다.** 벤더가 발표하지 않는 것은 맞지만
    # 그렇다고 못 채우는 것은 아니었다 — 10차가 학술 문헌에서 직조유리/에폭시 적층판의
    # S-N 회귀식을 찾아 19종에 tier3을 넣었다(IEC 60893 EPGC 203 축하중, JIS-K6912 굽힘).
    # 반례 검증이 이 선언의 피로 키를 자동 은퇴시킨다. **"벤더가 안 낸다"와 "문헌에도 없다"는
    # 다른 명제다. 부재 사유를 쓸 때 둘을 구분해라.**

    # [2026-08-14 · 20차 G] 아크릴 PSA/OCA × 산소투과·용해도.
    # **"아직 못 찾았다"가 아니라 근거 넷을 갖춘 부재다.**
    #  (1) 표적 55종의 고유 출처 18편을 md·PDF 양쪽 `grep -a` 로 전수 확인 — 값 0편.
    #  (2) 재료군 대표값도 없다. 동의어·기기명(Mocon/Ox-Tran)·규격번호(ASTM D3985)까지
    #      바꿔 물어 나온 40편이 전부 배리어필름·TFE·식품포장·COC·PI·실리콘·셀룰로스다.
    #      **접착제는 한 편도 없다.**
    #  (3) 뒷문이 닫혀 있다 — `oxygen inhibition` 이 16,007편 전수에서 0건이다.
    #      UV 경화 PSA 논문은 산소를 N2 퍼지로 공정에서 제거하지 정량하지 않는다.
    #  (4) 구조적 이유 — PSA/OCA는 Tg가 낮은 고자유부피 고무상 아크릴레이트라 투과도가 높고
    #      제품 기능(택·박리·크리프·광학)과 무관하다. 논문이 싣는 것은 G'·Tg·Mw·젤분율·박리·택이다.
    # 가장 아까운 것은 Fotie 2017 — PO2·D·S를 **전부 측정하는데** 값이 Figure 3·4·5에만 있다.
    #
    # **이 선언은 지금 반례 검증에 걸려 자동 은퇴한다. 그리고 그 반례가 우리 자신이다.**
    # 제품 OCA/PSA 14종이 전부 `1.1813e-14` 를 tier3 `measured` 로 갖고 있는데, 그 숫자의
    # 출처는 poly(hexyl acrylate) 한 물질이다 — 한 값을 14종에 편 **클래스 전이**이지
    # "문헌이 아크릴 PSA의 산소투과도를 발표한다"는 증거가 아니다.
    # 반례 검증은 tier<=3 을 실측으로 보는데, **tier3 클래스 전이는 실측이 아니다.**
    # 지표 결함으로 NEXT_WAVES 에 올렸다. 선언은 증거 보존을 위해 남긴다.
    #
    # 그리고 표적 55종(Wang 2015·Park 2020·Kuo 2018 등)에 이 클래스값을 **펴지 않았다.**
    # Wang 2015는 GMA/MMA 함량을 바꾼 조성 시리즈다 — 자유부피가 조성마다 다르므로
    # 한 숫자를 55번 복사하면 그건 빈 칸이 아니라 **틀린 값 55개**다.
    (_TAPE, {"physical.gas_permeability_o2", "physical.gas_solubility"},
     "아크릴 PSA/OCA — 산소투과를 재지 않는다(기능과 무관, 코퍼스 전수 0편)"),

    # [2026-08-14 · 20차 G] 스퍼터 확산배리어와 RF 적층판에 기체투과도를 요구한 것은
    # 택일군 설계의 사고다. Ta/TaN은 금속 박막이고 RF 적층판은 유전 기판이다 —
    # **"못 채운 칸"이 아니라 애초에 그 물성을 발표할 이유가 없는 칸**이다.
    (("ta/tan", "tsv barrier", "ro4835", "ro4350", "rogers ro"),
     {"physical.gas_permeability_o2", "physical.gas_solubility"},
     "스퍼터 확산배리어·RF 적층판 — 기체투과도 발표 자체가 없다"),

    # Corning PI 시트에 항목 자체가 없고 자사 백서는 접촉각을 상한(`< 10°`)으로만 인쇄한다.
    (("gorilla", "victus", "ultra-thin glass", "utg"), {
        "physical.contact_angle_water", "physical.surface_energy",
        "thermal.conductivity", "thermal.specific_heat",
    }, "커버글래스 — 젖음·열물성 발표 자체가 없다"),

    # ── 아래 셋은 "벤더가 안 낸다"가 아니라 **물리적으로 정의되지 않는다**이다.
    # 8차 파동 항복강도 배치가 258종을 훑어 171종을 이 사유로 분류했고,
    # 각 군에 실측(tier<=3) 반례가 0이다.

    # 세라믹·유리는 항복 없이 파괴한다 — 소성 유동 구간이 없어 Rp0.2가 성립하지 않는다.
    (("cat:ceramic",), {"mechanical.yield_strength"},
     "세라믹·유리 — 취성 파괴라 항복점이 물리적으로 없다"),

    # 가황 고무·엘라스토머는 초탄성으로 모델링한다. 입력은 항복점이 아니라 응력-변형 곡선이다.
    (("cat:rubber",), {"mechanical.yield_strength"},
     "고무·엘라스토머 — 초탄성이라 항복점이 정의되지 않는다"),

    # 증착 박막·분산체로 쓰이는 저분자 유기 고체다. 벌크 소성 시험 자체가 성립하지 않는다.
    (_DOPANT, {"mechanical.yield_strength"},
     "저분자 유기 고체 — 벌크 항복 시험이 성립하지 않는다"),

    # 진공증착 저분자에 ASTM D570 침지·ISO 62 평형·WVTR을 요구하는 것은 시험 자체가
    # 성립하지 않는다(자립 필름을 만들 수 없다). 9차 투습 배치가 55종을 훑어 확인했고
    # 이 군의 실측 반례는 0건이다.
    (_DOPANT, {
        "physical.water_vapor_transmission", "physical.gas_permeability_h2o",
        "physical.diffusion_coefficient",
        "chemical.water_absorption_24h", "chemical.water_absorption_saturation",
        "chemical.moisture_absorption_equilibrium",
    }, "저분자 유기 고체 — 흡습·투습 시험이 성립하지 않는다"),

    # ── 접착 택일군 — **접착물이 아닌 것**에 박리·전단강도를 요구하면 척도 오류다.
    # 10·12차가 제품별 TDS로 판정했고(Rogers PORON 7판 `peel` 0건, Panasonic PGS는
    # 기본이 접착제 없는 S type), 네 군 전부 실측 반례가 0건이다.
    # **9차의 "폼엔 박리강도 없다"가 VHB 폼테이프 반례 25건으로 무너진 것을 기억해
    # 카테고리가 아니라 제품 이름으로 좁혔다** — VHB·ACXplus 같은 점착 폼은 여기 없다.
    (("poron", "epe epe", "d3o", "polyurea foam", "seat foam", "foam pu impact"), {
        "interface.peel_strength", "interface.lap_shear_strength", "interface.die_shear_strength",
    }, "무점착 폼 — 접착제가 없어 박리·전단이 정의되지 않는다"),
    # 코팅은 스크래치 임계하중(ASTM C1624)·풀오프(D4541)·크로스컷으로 재고 **모드가 다르다.**
    (("dlc coating", "tin pvd", "parylene", "ar/ir coating", "polyurethane coating",
      "thin-film encapsulation"), {
        "interface.peel_strength", "interface.lap_shear_strength", "interface.die_shear_strength",
    }, "코팅 — 접착을 스크래치·풀오프로 재므로 박리·전단과 모드가 다르다"),
    # 맨 필름·흑연시트는 접착제가 없다. 접착 변종이 따로 있는 제품도 카탈로그 등재분은 무점착이다.
    (("lexan", "peek film", "pei ultem", "pen film", "toppan g", "prism sheet",
      "pe packaging film", "pecvd siox", "quantum dot film",
      "pgs", "kaneka multilayer", "graphene film"), {
        "interface.peel_strength", "interface.lap_shear_strength", "interface.die_shear_strength",
    }, "맨 필름·흑연시트 — 접착제가 없다"),

    # ── 피로 택일군 — 사이클 기준 S-N이 물리적으로 성립하지 않는 군.
    # **유리**: 순환 데이터가 등가파단시간 축에서 정적피로 띠에 겹쳐, 이 분야는 사이클 S-N을
    # 만들지 않고 정적피로(σⁿ·t=B)·동적피로(응력속도)만 발표한다(材料 40(454) 914 / 40(458) 1491).
    (("gorilla glass", "ultra-thin glass", "soda-lime", "quartz crystal", "aspheric lens",
      "ir cut filter", "periscope prism", "aluminosilicate cover"), {
        "mechanical.fatigue_strength_coefficient", "mechanical.fatigue_ductility_coefficient",
        "mechanical.darveaux_constant", "mechanical.morrow_energy_coefficient",
        "mechanical.fatigue_stromeyer_coefficient",
    }, "유리 — 사이클 기준 S-N이 성립하지 않는다(정적피로·동적피로로만 발표된다)"),
    # **박막 기능층·배터리 활물질**: 벌크 피로 시편을 만들 수 없다(nm~µm 증착막·분말).
    (("ito transparent", "igzo", "high-k dielectric", "ltps polysilicon", "gan hemt",
      "soi substrate", "vcsel epitaxy", "scaln", "lfp cathode", "nca cathode", "ncm811",
      "carbon black", "2d material"), {
        "mechanical.fatigue_strength_coefficient", "mechanical.fatigue_ductility_coefficient",
        "mechanical.darveaux_constant", "mechanical.morrow_energy_coefficient",
        "mechanical.fatigue_stromeyer_coefficient",
    }, "박막 기능층·활물질 분말 — 벌크 피로 시편이 성립하지 않는다"),

    # 진공증착 저분자는 **자립 인장시편을 만들 수 없다.** 벌크 소성 구간도 율속 의존
    # 항복도 존재하지 않는다. 8·9·10차가 각각 독립으로 확인했고(8차: 벌크 항복 시험 불가,
    # 9차: 소성 구성모델 자체가 없음, 10차: 율속 배치가 건너뜀), 51종 전체에 대해
    # **소성 택일군·율속 택일군 둘 다 실측(tier<=3) 반례가 0건**이다.
    # 이 선언으로 낙하·충격의 '적용 대상'에서 이 군이 빠진다 — 이 재료로 낙하해석을
    # 돌리는 일 자체가 없다.
    (_DOPANT, {
        "mechanical.tensile_strength", "mechanical.elongation_at_break",
        "mechanical.cowper_symonds_c", "mechanical.cowper_symonds_p",
        "mechanical.dynamic_increase_factor", "mechanical.yield_strength_at_rate",
        "mechanical.johnson_cook_c",
    }, "저분자 유기 고체 — 자립 인장시편이 없어 소성·율속이 정의되지 않는다"),

    # Coffin-Manson·Morrow는 **순환소성**을 전제한 변형률-수명·에너지 정식이고
    # Darveaux는 솔더 균열식이다. 세라믹은 전위소성이 없어 이 셋의 구간이 없다.
    #
    # **[2026-08-10 축소] `fatigue_strength_coefficient`를 뺐다.** 9차가 "세라믹은 피로계수가
    # 없다"고 선언했으나 **틀렸다** — 11차가 알루미나의 S-N 회귀식을 찾았다
    # (Maekawa 1988, 材料 37(415) 441). **응력-수명(Basquin/S-N)은 세라믹에도 존재한다.**
    # 없는 것은 소성을 전제한 정식뿐이다. 그 반례가 `Alumina Ceramic Package (Kyocera A440)`인데
    # 분류가 composite라 반례 검증에 안 걸리고 있었다 — 함께 ceramic으로 고쳤다.
    # **"순환소성이 없다"에서 "피로 데이터가 없다"로 넘어간 것이 오류였다.**
    (("cat:ceramic",), {
        "mechanical.fatigue_ductility_coefficient",
        "mechanical.darveaux_constant", "mechanical.morrow_energy_coefficient",
    }, "세라믹 — 순환소성이 없어 변형률-수명·에너지 계수가 정의되지 않는다(S-N은 존재한다)"),

    # ── 13차 파동 선언. 65종을 훑은 피로 배치가 declined 53종의 출처 328건 중 281건을
    # 재다운로드해 grep했고 **피로 모델 상수 0건**이었다. 다만 "전수 검색이 비었다"는
    # 검색 실패와 구분되지 않는다 — 그래서 **인쇄된 부재 문장이나 기전(機轉) 논거가 있는
    # 군만** 여기 넣는다. METGLAS·나노결정·분말코어·ACF/DAF/Ag에폭시·E-glass·커버레이는
    # 근거가 검색 소진뿐이라 **일부러 남겼다** — 다음 파동의 일감이지 부재가 아니다.

    # MMPA 0100-00 본문이 영구자석 전체를 덮어 인쇄한다 —
    # *"Most permanent magnet materials lack ductility and are inherently brittle. Such materials
    # should not be utilized as structural components… Measurement of properties such as hardness
    # and tensile strength is not appropriate or feasible."*
    # 이 군에 발표되는 것은 굽힘강도이고, 13차가 그 굽힘강도로 S-N을 세웠다(피로는 채워졌다).
    (("recoma", "alnico", "hard ferrite magnet", "ndfeb sintered"), {
        "mechanical.yield_strength", "mechanical.tensile_strength",
        "mechanical.elongation_at_break",
    }, "영구자석 — MMPA 0100-00이 인장·경도 측정이 적절하지도 가능하지도 않다고 인쇄한다"),

    # 알루미나의 순환 열화는 **입계 브리징의 마모**가 기전이다. 단결정에는 입계가 없다.
    # 게다가 Si는 문헌 자신이 지수가 재료상수가 아님을 밝힌다 — *"The slopes of S–N plots have
    # been strongly dependent on specimens, test methods, and environments… The reason for this
    # variation is still unknown"* (같은 실험실·같은 재료가 파운드리만 달라 n=27 대 19다).
    # **재료상수가 아닌 것은 카탈로그에 담기지 않는다.**
    (("sapphire single-crystal", "lithium niobate", "lithium tantalate",
      "crystalline silicon", "capacitive mems"), _FATIG_SET,
     "단결정 — 입계 브리징이 없어 순환 열화 기전이 없고, Si는 지수가 재료상수가 아니다"),

    # 카탈로그 자신의 출처가 부재를 인쇄한다 — AlN 박막(J. Alloys Compd. 772, 306):
    # *"No clear signs of fatigue were observed after 10,000 cycles at 83% of the fracture strength."*
    # 이 분야는 밀착을 스크래치 임계하중으로, 열화를 균열밀도로 잰다. 응력-수명 축이 아니다.
    (("dlc coating", "tin pvd", "anodized aluminum", "ar/ir coating",
      "thin-film encapsulation", "piezo mems", "silver nanowire", "magnetic sensor",
      "imag surface", "oled cathode"), _FATIG_SET,
     "PVD·CVD 박막 — 응력-수명이 아니라 임계하중·균열밀도로 재는 분야다"),

    # 배리어 필름의 수명은 **굽힘/비틀림 횟수 대 배리어·전기 기능 상실**로 잰다(WVTR 열화).
    # 응력-수명 곡선이 아니다. **택시노미에 굽힘 횟수 키(MIT folding endurance,
    # IPC-TM-650 2.4.3)가 없어서 이 군은 담을 그릇 자체가 없다** — 다음 파동의 숙제로 남긴다.
    (("toppan g", "pecvd siox", "quantum dot film", "emi shielding film"), _FATIG_SET,
     "배리어 필름 — 수명을 굽힘 횟수 대 기능 상실로 재고 응력-수명 축이 없다"),

    # J-Stage 疲労 표제 18,750건 전수 grep에 불소수지 용어 0건이고, 세라믹충전 PTFE 논문
    # 약 20편이 전부 유전특성만 보고한다. 게다가 11종 중 9종은 σB가 Okabe 적합 하한
    # (≈69 MPa) 아래라 **적층재 상수를 옮기는 길도 범위 밖이다.**
    (("ro3003", "clte", "rt/duroid", "taconic", "chukoh", "tsm-ds3"), _FATIG_SET,
     "불소수지 RF 적층판 — S-N이 발표되지 않고 σB가 Okabe 적합 하한 아래다"),

    # 위 '박막 기능층·활물질' 선언과 같은 사유인데 매처가 두 활물질을 놓치고 있었다.
    (("graphite anode", "silicon anode"), _FATIG_SET,
     "활물질 분말 — 벌크 피로 시편이 성립하지 않는다"),
]


# 선언은 **주장이 아니라 반례로 검증되는 것**이다.
#
# 처음엔 UNFILLABLE을 그대로 믿었더니 102칸이 "부재인데 값이 있음"으로 걸렸다 —
# 벤조페논은 상용 화학물질이라 CRC에 밀도가 있고, `laminate`·`coverlay` 매처가 비열을 가진
# 재료까지 잡았다. **한 건의 반례가 선언을 무너뜨린다.**
#
# 그래서 (재료군 × 물성) 쌍은 두 조건을 **다** 만족할 때만 부재로 친다.
#   (1) 문서에 기록된 사유가 있다(UNFILLABLE에 적혀 있다) — "아직 못 찾았다"와 구분한다.
#   (2) 그 군의 어느 재료도 그 물성을 갖고 있지 않다 — 반례가 0이다.
# 나중에 값이 하나라도 들어오면 그 쌍은 **자동으로 부재에서 빠진다.**
_ACTIVE: dict | None = None


def _match(entry: tuple, matcher: tuple) -> bool:
    """이름 부분일치, 또는 `cat:<카테고리>`로 카테고리 일치.

    취성·엘라스토머처럼 **부재의 근거가 이름이 아니라 재료 부류**인 경우가 있다
    (세라믹은 항복 없이 파괴한다). 이름 매처로는 44종을 다 잡을 수 없어 카테고리를 연다.
    """
    name, cat = entry[0].lower(), (entry[1] or "").lower()
    for w in matcher:
        if w.startswith("cat:"):
            if cat == w[4:]:
                return True
        elif w in name:
            return True
    return False


def _build_active(mat: dict, own: dict, meas: dict | None = None) -> dict:
    """반례가 없는 (매처, 키) 쌍만 남긴다. 반례가 있으면 그 쌍은 부재가 아니다.

    **반례는 실측(tier<=3)만 인정한다.** 8차 파동에서 우리가 넣은 tier4 가정값이
    "이 물성은 물리적으로 정의되지 않는다"는 선언을 무효화하는 일이 실제로 났다 —
    아크릴 폼 테이프 11종에 항복강도 가정값을 넣자 점착테이프 항복점 부재 선언이
    자동 은퇴했다. **우리가 만든 가정이 우리의 부재 선언을 지우면 안 된다.**
    반례는 바깥에서 온 근거여야 하고, 가정값은 근거가 아니다.
    """
    global _ACTIVE
    src = meas if meas is not None else own
    active, retired = {}, []
    for idx, (matcher, keys, why) in enumerate(UNFILLABLE):
        members = [m for m in mat if _match(mat[m], matcher)]
        alive = set()
        for k in keys:
            counter = [mat[m][0] for m in members if k in src[m]]
            if counter:
                retired.append((why, k, len(counter), counter[0]))
            else:
                alive.add(k)
        active[idx] = (matcher, alive)
    _ACTIVE = {"active": active, "retired": retired}
    return _ACTIVE


def unfillable_keys(name: str, cat: str = "") -> set:
    """그 재료에서 구조적으로 못 채우는 물성 키 집합(반례 검증 통과분만).

    `cat`은 `cat:<카테고리>` 매처용이다 — 취성·초탄성처럼 부재의 근거가 이름이
    아니라 재료 부류인 선언이 있다. 넘기지 않으면 이름 매처만 동작한다.
    """
    entry = (name, cat)
    out = set()
    src = (_ACTIVE["active"].items() if _ACTIVE
           else ((i, (m, k)) for i, (m, k, _) in enumerate(UNFILLABLE)))
    for _idx, (matcher, keys) in src:
        if _match(entry, matcher):
            out |= keys
    return out


def _cell_unfillable(mat_name: str, keys, cat: str = "") -> bool:
    """칸 하나가 구조적 부재인가. 택일군은 **후보가 전부** 부재여야 부재다 —
    하나라도 채울 길이 있으면 그 칸은 채울 수 있는 칸이다."""
    bad = unfillable_keys(mat_name, cat)
    if not bad:
        return False
    flat = []
    for k in keys:
        flat.extend(k if isinstance(k, tuple) else (k,))
    return bool(flat) and all(k in bad for k in flat)


def compute():
    c, mat, own, meas = load()
    # 반례 검증 — 실측(tier<=3)이 하나라도 있는 쌍은 부재에서 뺀다.
    # own이 아니라 meas를 넘긴다: 우리가 만든 tier4 가정값은 반례가 아니다.
    _build_active(mat, own, meas)
    out = []
    for name, must, anyof, filt, desc in ANALYSES:
        tgt = scope(mat, filt)
        n = len(tgt)
        # (a) 셀 채움률 — 필수물성은 칸 1개, 택일군은 통째로 칸 1개.
        #     구조적 부재 칸은 따로 센다. 분모에 남겨 두면 도달할 수 없는 100%를 좇게 된다.
        cells = filled = 0
        unfill = 0          # 구조적으로 못 채우는 칸
        # **부재로 뺀 칸에 tier4 가정값이 들어 있으면 분자에도 남아 유효채움이 100%를 넘는다.**
        # 실제로 워피지 107.4%, 구조·강성 106.5%가 나왔다. 분모에서 뺀 칸은 분자에서도 뺀다.
        unfill_filled = 0
        wrong_unfill = []   # 부재로 선언했는데 실제로 값이 있는 칸 — 선언이 틀렸다는 뜻
        miss_by_key = Counter()
        m_filled = 0   # tier4 가정을 뺀 채움
        for m in tgt:
            ks = own[m]
            ms = meas[m]
            for k in must:
                cells += 1
                m_filled += (k in ms)
                has = k in ks
                if _cell_unfillable(mat[m][0], (k,), mat[m][1]):
                    unfill += 1
                    unfill_filled += has
                    # 반례는 **실측(tier<=3)**만 인정한다. 8차 파동 방침대로 넣은 tier4
                    # 가정값이 부재 칸에 앉는 것은 정상이다 — 선언이 틀렸다는 뜻이 아니다.
                    if k in ms:
                        wrong_unfill.append((mat[m][0], k))
                if has:
                    filled += 1
                else:
                    miss_by_key[k] += 1
            for grp in anyof:
                cells += 1
                m_filled += grp_ok(ms, grp)
                has = grp_ok(ks, grp)
                if _cell_unfillable(mat[m][0], grp, mat[m][1]):
                    unfill += 1
                    unfill_filled += has
                    if grp_ok(ms, grp):
                        wrong_unfill.append((mat[m][0], "택일군"))
                if has:
                    filled += 1
                else:
                    label = " | ".join(
                        ("+".join(x.split(".", 1)[1] for x in alt) if isinstance(alt, tuple)
                         else alt.split(".", 1)[1]) for alt in grp)
                    miss_by_key["택일군: " + label[:70]] += 1
        # (b) 재료 준비율
        # **그 해석이 원리적으로 성립하지 않는 재료는 분모에서 뺀다.**
        # 세라믹에 변형률-수명 피로계수를 요구하면 그 재료는 영원히 '준비 안 됨'으로 남아
        # 준비율을 끌어내린다 — 셀 지표에는 이미 부재를 반영해 놓고 준비율에는 안 했다.
        # 알루미나로 strain-life 피로해석을 돌리는 일은 없다. 적용 대상이 아니다.
        def _na(m):
            if any(_cell_unfillable(mat[m][0], (k,), mat[m][1]) for k in must):
                return True
            return any(_cell_unfillable(mat[m][0], g, mat[m][1]) for g in anyof)
        applicable = [m for m in tgt if not _na(m)]
        ready = [m for m in tgt
                 if all(k in own[m] for k in must) and all(grp_ok(own[m], g) for g in anyof)]
        ready_m = [m for m in tgt
                   if all(k in meas[m] for k in must) and all(grp_ok(meas[m], g) for g in anyof)]
        eff = cells - unfill              # 채울 수 있는 칸
        eff_filled = filled - unfill_filled  # 그중 채워진 칸(부재 칸의 가정값은 뺀다)
        out.append({
            "name": name, "desc": desc, "n_target": n,
            "cells": cells, "filled": filled,
            "cell_pct": round(filled * 100 / cells, 1) if cells else 0.0,
            # 구조적 부재를 뺀 분모. **이 상승은 수집 성과가 아니라 분모 정의다.**
            "unfillable": unfill,
            "eff_cells": eff,
            "eff_filled": eff_filled,
            "unfill_filled": unfill_filled,
            "eff_pct": round(eff_filled * 100 / eff, 1) if eff else 0.0,
            "wrong_unfillable": wrong_unfill,
            "meas_filled": m_filled,
            "meas_pct": round(m_filled * 100 / cells, 1) if cells else 0.0,
            "n_ready": len(ready),
            "ready_pct": round(len(ready) * 100 / n, 1) if n else 0.0,
            "n_applicable": len(applicable),
            # 분자도 같은 집합에서 센다. 부재 칸에 tier4 가정값이 들어 있으면
            # 적용 대상에서 뺀 재료가 '준비 완료'로 세어져 100%를 넘는다(실제로 109.9%가 나왔다).
            "n_ready_app": len([m for m in applicable if m in set(ready)]),
            "ready_app_pct": (round(len([m for m in applicable if m in set(ready)]) * 100
                                    / len(applicable), 1) if applicable else 0.0),
            "n_ready_meas": len(ready_m),
            "ready_meas_pct": round(len(ready_m) * 100 / n, 1) if n else 0.0,
            "missing": miss_by_key.most_common(6),
        })
    return c, mat, own, out


def property_stats(c, mat, own):
    """물성별 보유 재료 수 — 무엇이 채워졌고 무엇이 비었나."""
    rows = []
    for key, nm, unit, dom in c.execute(
            "select key,name,si_unit,domain from property_definition order by domain,key"):
        m = c.execute("select count(distinct material_id) from property_value where property_key=?",
                      (key,)).fetchone()[0]
        v = c.execute("select count(*) from property_value where property_key=?", (key,)).fetchone()[0]
        rows.append({"key": key, "name": nm, "unit": unit, "domain": dom,
                     "n_mat": m, "n_val": v, "pct": round(m * 100 / len(mat), 1)})
    return rows


def main():
    c, mat, own, cov = compute()
    props = property_stats(c, mat, own)
    if "--json" in sys.argv:
        print(json.dumps({"coverage": cov, "properties": props}, ensure_ascii=False, indent=1))
        return

    tot_cells = sum(x["cells"] for x in cov)
    tot_filled = sum(x["filled"] for x in cov)
    tot_unfill = sum(x["unfillable"] for x in cov)
    tot_eff = tot_cells - tot_unfill
    tot_meas = sum(x["meas_filled"] for x in cov)
    # **적용대비**가 준비율의 정직한 형태다 — 그 해석이 구조적으로 성립하지 않는 재료
    # (액체에 항복강도, 도판트에 투습)를 분모에서 뺀다. 빼지 않으면 영원히 못 채우는 칸이
    # 미완료로 남아, 다 한 일도 덜 한 것처럼 보인다.
    print(f"\n{'해석':18s} {'대상':>5s}  {'셀채움':>7s} {'실측기반':>7s}  "
          f"{'재료준비':>7s} {'적용대비':>7s} {'실측':>6s}   가장 큰 공백")
    print("  " + "─" * 112)
    for x in cov:
        top = x["missing"][0][0].replace("택일군: ", "") if x["missing"] else "—"
        top = top.split(".", 1)[-1][:26]
        print(f"  {x['name']:18s} {x['n_target']:5d}  "
              f"{x['cell_pct']:6.1f}% {x['meas_pct']:6.1f}%  "
              f"{x['ready_pct']:6.1f}% {x['ready_app_pct']:6.1f}% {x['ready_meas_pct']:5.1f}%   {top}")
    print("  " + "─" * 104)
    print(f"  {'전체':18s} {'':5s}  {tot_filled*100/tot_cells:6.1f}% "
          f"{tot_meas*100/tot_cells:6.1f}%")
    print(f"\n  **실측기반**은 tier4(가정·계산)를 뺀 값이다. 차이 "
          f"{(tot_filled-tot_meas)*100/tot_cells:.1f}%p({tot_filled-tot_meas}칸)가 "
          f"가정값이 만든 착시다.")
    print(f"  구조적 부재는 {tot_unfill}칸({tot_unfill*100/tot_cells:.1f}%)뿐이다 — "
          f"**천장은 100%에 가깝고, 남은 일은 실측 기준 {tot_cells-tot_meas}칸이다.**")
    print(f"\n  구조적 부재 {tot_unfill}칸을 뺀 분모가 '유효채움'이다 — "
          f"**그 물성이 그 재료군에서 애초에 발표되지 않는 칸**이다.")
    # 부재 칸에 들어앉은 가정값은 분자에서도 빼야 한다 — 안 빼면 남은 일이 음수로 나온다.
    tot_eff_filled = tot_filled - sum(x["unfill_filled"] for x in cov)
    print(f"  전체 유효채움 {tot_eff_filled*100/tot_eff:.1f}% — "
          f"남은 일은 {tot_cells - tot_filled}칸이 아니라 **{tot_eff - tot_eff_filled}칸**이다.")
    # 부재로 선언했는데 값이 있으면 선언이 틀린 것이다 — 반드시 드러낸다.
    wrong = [w for x in cov for w in x["wrong_unfillable"]]
    if wrong:
        uniq = sorted({w for w in wrong})
        print(f"\n  [경고] 구조적 부재로 선언했는데 값이 있는 칸 {len(uniq)}종 — 선언이 틀렸다:")
        for nm, k in uniq[:12]:
            print(f"        {nm[:52]:52s} {k}")

    print(f"\n\n  물성 보유율 상위/하위 (재료 {len(mat)}종 기준)")
    ordered = sorted(props, key=lambda p: -p["n_mat"])
    print("\n  ── 잘 채워진 것")
    for p in ordered[:12]:
        print(f"   {p['n_mat']:4d}종 {p['pct']:5.1f}%  {p['name'][:30]:30s} {p['key']}")
    print("\n  ── 비어 있는 것(값은 있으나 재료 수가 적은 것)")
    for p in [x for x in ordered if x["n_mat"] > 0][-12:]:
        print(f"   {p['n_mat']:4d}종 {p['pct']:5.1f}%  {p['name'][:30]:30s} {p['key']}")
    zero = [p for p in props if p["n_mat"] == 0]
    print(f"\n  ── 값이 하나도 없는 정의: {len(zero)}종")
    for p in zero:
        print(f"        {p['name'][:34]:34s} {p['key']}")


if __name__ == "__main__":
    main()
