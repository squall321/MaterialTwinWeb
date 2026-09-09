# 72차 HC 수집 배치 생성기 — 71차 GD 가 넘긴 「밀도를 찍는 로컬 벤더 시트」 표적을 카드로 세운다
"""72차 HC — Technolam/Nan Ya · Nan Ya CCL · Shengyi · Rogers 의 로컬 원문에서
코어7(밀도·영률·포아송비·CTE·열전도율·비열·인장강도)을 인쇄된 대로 전부 담는다.

규율
  - 값을 지어내지 않는다. 표에 없으면 빈칸으로 둔다.
  - 인쇄된 구간은 두 행(bound lower/upper). 평균 0건.
  - 한쪽 부등호(>·<·↑·↓)만 있는 칸은 담지 않는다(보고서에 적는다).
  - method 는 6어휘만: measured·handbook·datasheet·computed·estimated·digitized
  - t4 금지 · t3 는 grade_scope 필수 · 역산 금지
"""
import json
import os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- 단위 환산
LB_IN_TO_N_M = 4.4482216152605 / 0.0254  # 175.126835... N/m per lbf/in


def gpa(v):
    return v * 1e9


def mpa(v):
    return v * 1e6


def gcm3(v):
    return v * 1000.0


def jgk(v):
    return v * 1000.0


def ppmk(v):
    return v * 1e-6


def pct(v):
    return v / 100.0


def degc(v):
    return v + 273.15


def mjkg(v):
    return v * 1e6


def nmm(v):
    return v * 1000.0


def lbin(v):
    return v * LB_IN_TO_N_M


def minutes(v):
    return v * 60.0


def kv(v):
    return v * 1000.0


def kvmm(v):
    return v * 1e6


def mohmcm(v):
    return v * 1e4  # MΩ·cm -> Ω·m


def mohm(v):
    return v * 1e6  # MΩ -> Ω


MATS = []

# ================================================================ 공통 조각
TECHNOLAM_PUB = "Technolam GmbH (Nan Ya Plastics 유럽 파트너)"
CORPUS = "/data/paper_patent_corpus/standards_appnotes/pcb/"

# Technolam 시트의 두 두께 열
THIN = "laminate thickness < 0,50 mm [0,0197 in]"
THICK = "laminate thickness >= 0,50 mm [0,0197 in]"

# 영률 모드 미확정 사유 (Technolam 공통)
TECHNOLAM_YM_SCOPE = (
    "값 자체는 이 등급의 이 열에 인쇄된 것이고 등급 범위 문제는 없다. t3 로 내린 이유는 "
    "**시험모드 미확정**이다 — 원문 `Young's Modulus / E-Modul` 행의 `Test Method (IPC-TM-650)` 칸과 "
    "`Ref. Para.` 칸이 둘 다 `-` 다(300 dpi 렌더로 확인). 같은 표의 8번 `Flexural Strength / Biegefestigkeit` "
    "행은 `2.4.4` 를 명시하므로 이 벤더는 적을 때는 적는다 — 여기서 안 적은 것은 누락이지 인장 확정이 아니다. "
    "70차 FA(MGC BT `ヤング率`) · 71차 GD(Sumitomo LαZ `弾性率`) 의 선례를 따랐다."
)
TECHNOLAM_YM_NOTE_TAIL = (
    " 원문 시험법 칸 verbatim = `-` · Ref. Para. 칸 verbatim = `-` (인장/굽힘 표기 없음)."
)


def prop(key, value, unit, method="measured", tier=1, cond=None, notes=""):
    p = {"key": key, "value": value, "unit": unit, "method": method, "tier": tier}
    if cond:
        p["conditions"] = cond
    p["notes"] = notes
    return p


def rng_rows(key, unit_out, lo_src, hi_src, conv, cond, verbatim, unit_src, extra="",
             method="measured", tier=1):
    """인쇄된 구간 -> 두 행 (bound lower/upper). 평균 내지 않는다."""
    rows = []
    for b, v in (("lower", lo_src), ("upper", hi_src)):
        c = dict(cond)
        c["bound"] = b
        rows.append(prop(key, conv(v), unit_out, method=method, tier=tier, cond=c,
                         notes=f"원문 verbatim: `{verbatim}`. 인쇄된 구간의 {b} 끝값 {v} {unit_src} 를 "
                               f"환산했다 — {arith(v, conv, unit_src, unit_out)}.{extra}"))
    return rows


def arith(v, conv, unit_src, unit_out):
    out = conv(v)
    if conv is gpa:
        return f"{v} GPa x 1e9 = {out:.6g} Pa; 되돌리면 {out:.6g}/1e9 = {out/1e9:.6g}"
    if conv is mpa:
        return f"{v} {unit_src} x 1e6 = {out:.6g} Pa; 되돌리면 {out:.6g}/1e6 = {out/1e6:.6g}"
    if conv is gcm3:
        return f"{v} g/cm^3 x 1000 = {out:.6g} kg/m^3; 되돌리면 {out:.6g}/1000 = {out/1000:.6g}"
    if conv is jgk:
        return f"{v} {unit_src} x 1000 = {out:.6g} J/(kg*K); 되돌리면 {out:.6g}/1000 = {out/1000:.6g}"
    if conv is ppmk:
        return f"{v} ppm/degC x 1e-6 = {out:.6g} 1/K; 되돌리면 {out:.6g}/1e-6 = {out/1e-6:.6g}"
    if conv is pct:
        return f"{v} % / 100 = {out:.6g}; 되돌리면 {out:.6g} x 100 = {out*100:.6g}"
    if conv is degc:
        return f"{v} + 273.15 = {out:.6g} K; 되돌리면 {out:.6g} - 273.15 = {out-273.15:.6g}"
    if conv is mjkg:
        return f"{v} MJ/kg x 1e6 = {out:.6g} J/kg; 되돌리면 {out:.6g}/1e6 = {out/1e6:.6g}"
    if conv is nmm:
        return f"{v} N/mm x 1000 = {out:.6g} N/m; 되돌리면 {out:.6g}/1000 = {out/1000:.6g}"
    if conv is lbin:
        return (f"{v} lb/in x 175.126835 = {out:.6g} N/m "
                f"(1 lbf = 4.4482216152605 N, 1 in = 0.0254 m -> 4.4482216152605/0.0254 = 175.126835); "
                f"되돌리면 {out:.6g}/175.126835 = {out/LB_IN_TO_N_M:.6g}")
    if conv is minutes:
        return f"{v} min x 60 = {out:.6g} s; 되돌리면 {out:.6g}/60 = {out/60:.6g}"
    if conv is kv:
        return f"{v} kV x 1000 = {out:.6g} V; 되돌리면 {out:.6g}/1000 = {out/1000:.6g}"
    if conv is kvmm:
        return f"{v} kV/mm x 1e6 = {out:.6g} V/m; 되돌리면 {out:.6g}/1e6 = {out/1e6:.6g}"
    if conv is mohmcm:
        return (f"{v:.6g} MOhm*cm x 1e4 = {out:.6g} Ohm*m "
                f"(1 MOhm*cm = 1e6 Ohm x 1e-2 m = 1e4 Ohm*m); 되돌리면 {out:.6g}/1e4 = {out/1e4:.6g}")
    if conv is mohm:
        return f"{v:.6g} MOhm x 1e6 = {out:.6g} Ohm; 되돌리면 {out:.6g}/1e6 = {out/1e6:.6g}"
    return f"{v} {unit_src} -> {out:.6g} {unit_out}"


def one(key, unit_out, v_src, conv, cond, verbatim, unit_src, extra="",
        method="measured", tier=1):
    return [prop(key, conv(v_src), unit_out, method=method, tier=tier, cond=dict(cond),
                 notes=f"원문 verbatim: `{verbatim}`. {arith(v_src, conv, unit_src, unit_out)}.{extra}")]


# ================================================================================
# A. Technolam / Nan Ya — IPC-4101 서식 독영 2개국어 Datenblatt (로컬 텍스트층 있음)
# ================================================================================
# 표 구조(300 dpi 렌더로 확정):
#   Laminate Requirement | Specification <0,50 mm {Specification|Property}
#                        | Specification >= 0,50 mm {Specification|Property}
#                        | Units | Test Method (IPC-TM-650) | Ref. Para.
#   -> 카드에 담는 것은 **Property 열**(벤더 실측 대표값)뿐이다. Specification 열은
#      IPC-4101 슬래시시트 요구(최소/최대)이지 물성이 아니다.

TECHNOLAM_TABLE_NOTE = (
    "이 값은 원문 `Property` 열(벤더 대표값)에서 왔다. 같은 행의 `Specification` 열은 "
    "IPC-4101 슬래시시트 요구(최소/최대)이지 물성이 아니므로 담지 않았다."
)


def technolam_sheet(name, desc, aliases, grades, src, ipc_sheet, ul_id, tg_header,
                    data, extra_attrs=None):
    props = []
    for entry in data:
        props.extend(entry)
    attrs = {
        "material_class": "flame-retardant woven E-glass / epoxy copper clad laminate",
        "subsystem": "pcb",
        "role": "product",
        "role_reason": "제조사(Nan Ya)+등급명이 이름에 박혀 있고 출처가 해당 등급의 공식 Datenblatt 이다. 실제 PCB 적층재 제품.",
        "role_confidence": "high",
        "manufacturer": "Nan Ya Plastics Corporation",
        "distributor": "Technolam GmbH",
        "grades_covered": grades,
        "ipc_spec_sheet": ipc_sheet,
        "ul_ansi_id": ul_id,
        "glass_transition_header": tg_header,
        "aliases": aliases,
        "value_column": ("원문은 등급별 열이 아니라 **두께별 열**(<0,50 mm · >=0,50 mm)로 갈린다. "
                         "한 장의 시트가 위 grades_covered 전부에 같은 값 집합을 인쇄하므로 "
                         "등급을 쪼개 같은 값을 복제하지 않고 한 장으로 세웠다 — 각 등급명은 aliases 에 있다."),
    }
    if extra_attrs:
        attrs.update(extra_attrs)
    MATS.append({
        "new_material": {"name": name, "category": "composite", "description": desc,
                         "attributes": attrs},
        "source": src,
        "properties": props,
    })


def tl_src(title, local, year):
    return {"kind": "datasheet", "title": title, "url": None,
            "publisher": TECHNOLAM_PUB, "year": year,
            "local_path": CORPUS + local,
            "url_note": ("절대 URL 을 확정하지 못했다 — PDF 안에 canonical/og:url 이 없고 지어내지 않았다. "
                         "로컬 원문 경로가 값의 출처다.")}


# ---------------------------------------------------------------- A1. NPG-150N / NPG-150NB
S = tl_src("Data Sheet / Datenblatt NPG-150N, NPG-150NB (Rev. Feb.19) — Performance List 1/2, 2/2",
           "Technolam_NanYa_NPG-150N-NPG-150NB_Datasheet_2019-02.pdf", 2019)
CT, CK = {"specimen": THIN}, {"specimen": THICK}
technolam_sheet(
    "Nan Ya NPG-150N / NPG-150NB Halogen-Free Low-CTE FR-4 Copper Clad Laminate",
    "南亞(Nan Ya) 할로겐프리 저CTE FR-4 동박적층판 `NPG-150N` 및 흑색판 `NPG-150NB`. "
    "유럽 파트너 Technolam 이 IPC-4101 슬래시시트 서식(IPC-4101/128)으로 낸 Datenblatt 2019-02 판이 출처다. "
    "이 서식의 특징은 **번호 붙은 1~19번 항목이 IPC-4101 요구**이고 그 아래 `20. Other / weitere` 가 "
    "**벤더가 덤으로 붙인 값**이라는 것 — 밀도·영률·비열이 바로 거기 있고 `Ref. Para.` 칸이 `-` 다. "
    "표는 등급이 아니라 두께(<0,50 mm · >=0,50 mm)로 열이 갈린다.",
    ["NPG-150N", "NPG-150NB", "NPG150N", "NPG150NB", "NPG-150 N", "Nan Ya NPG-150N"],
    ["NPG-150N", "NPG-150NB"], S, "IPC-4101/128", "UL/ANSI FR-4.1/128", "150 degC minimum",
    [
        # ---- 코어7
        one("physical.density", "kg/m^3", 2.00, gcm3, {"resin_content": "50%", "specimen": THIN},
            "Density (50 % resin content) / Dichte 50 % Harzgehalt  -  2,00  -  2,00  g/cm3  -  -", "g/cm^3",
            " 시험법 칸과 Ref. Para. 칸이 둘 다 `-` 다 — IPC 요구가 아니라 벤더가 덤으로 붙인 값이다. " + TECHNOLAM_TABLE_NOTE),
        one("physical.density", "kg/m^3", 2.00, gcm3, {"resin_content": "50%", "specimen": THICK},
            "Density (50 % resin content) / Dichte 50 % Harzgehalt  -  2,00  -  2,00  g/cm3  -  -", "g/cm^3",
            " " + TECHNOLAM_TABLE_NOTE),
        rng_rows("mechanical.youngs_modulus", "Pa", 23, 25, gpa,
                 {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
                  "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
                 "Young's Modulus / E-Modul  A. Length direction / Kettrichtung  -  -  -  23-25  GPa  -  -",
                 "GPa", TECHNOLAM_YM_NOTE_TAIL + " " + TECHNOLAM_TABLE_NOTE, tier=3),
        rng_rows("mechanical.youngs_modulus", "Pa", 22, 24, gpa,
                 {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
                  "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
                 "Young's Modulus / E-Modul  B. Cross direction / Schussrichtung  -  -  -  22-24  GPa  -  -",
                 "GPa", TECHNOLAM_YM_NOTE_TAIL + " " + TECHNOLAM_TABLE_NOTE, tier=3),
        one("thermal.conductivity", "W/(m*K)", 0.42, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THIN},
            "Thermal Conductivity l / Thermische Leitfaehigkeit lambda  -  0,42  -  0,42  W/mK  ASTM-E-1461", "W/mK",
            " 원문 단위 `W/mK` 는 SI `W/(m*K)` 와 같다 — 환산 없음. " + TECHNOLAM_TABLE_NOTE),
        one("thermal.conductivity", "W/(m*K)", 0.42, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THICK},
            "Thermal Conductivity l  -  0,42  -  0,42  W/mK  ASTM-E-1461", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.37, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THIN},
            "Thermal Conductivity l  -  0,37  -  0,37  W/mK  ASTM-D-5470", "W/mK",
            " 같은 물성의 다른 측정법이므로 ASTM-E-1461 행과 두 행으로 갈랐다."),
        one("thermal.conductivity", "W/(m*K)", 0.37, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THICK},
            "Thermal Conductivity l  -  0,37  -  0,37  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.specific_heat", "J/(kg*K)", 0.946, jgk, {"temperature_c": 25, "specimen": THIN},
            "Specific Heat at 25 degC / Spezifische Waermekapazitaet bei 25 degC  -  0,946  -  0,946  J/g degC  -  -", "J/(g*K)",
            " 시험법 칸 `-`."),
        one("thermal.specific_heat", "J/(kg*K)", 0.946, jgk, {"temperature_c": 25, "specimen": THICK},
            "Specific Heat at 25 degC  -  0,946  -  0,946  J/g degC  -  -", "J/(g*K)", ""),
        rng_rows("thermal.expansion_linear", "1/K", 9, 13, ppmk,
                 {"axis": "x/y", "regime": "prior Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  prior Tg / vor Tg  -  9-13  -  9-13  ppm/degC  2.4.24  3.9.1.6", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 9, 13, ppmk,
                 {"axis": "x/y", "regime": "above Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  above Tg / ueber Tg  -  9-13  -  9-13  ppm/degC  2.4.24  3.9.1.6", "ppm/degC",
                 " 원문이 prior Tg 와 above Tg 에 같은 구간(9-13)을 인쇄한다 — 유리크로스가 면내 팽창을 지배하므로 "
                 "Tg 를 넘어도 면내 CTE 가 거의 변하지 않는다. 렌더로 두 행이 실제로 같은 값임을 확인했다."),
        one("thermal.expansion_linear", "1/K", 50, ppmk,
            {"axis": "z", "regime": "alpha1 (prior Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  A. Alpha 1, maximum  prior Tg / vor Tg  -  50  60  50  ppm/degC  2.4.24  3.9.1.7", "ppm/degC"),
        one("thermal.expansion_linear", "1/K", 230, ppmk,
            {"axis": "z", "regime": "alpha2 (above Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  B. Alpha 2, maximum  above Tg / ueber Tg  -  230  300  230  ppm/degC  2.4.24  3.9.1.7", "ppm/degC"),
        one("thermal.expansion_total", "1", 3.2, pct,
            {"axis": "z", "temperature_range_c": "50-260", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  C. 50 to 260 degC, maximum (Total Expansion)  -  3,2  3,5  3,2  %", "%"),
        # ---- 그 밖에 인쇄된 것
        one("mechanical.flexural_strength", "Pa", 450, mpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength, minimum / Biegefestigkeit  A. Length direction  -  -  415 [60190]  450 [65267]  N/mm2  2.4.4  3.9.1.3",
            "N/mm^2", " 원문 단위 N/mm^2 = MPa. **이 행은 굽힘이다** — 시험법 2.4.4 가 IPC-TM-650 의 굽힘강도법이다."),
        one("mechanical.flexural_strength", "Pa", 390, mpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength  B. Cross direction  -  -  345 [50040]  390 [56565]  N/mm2  2.4.4", "N/mm^2", ""),
        one("thermal.glass_transition", "K", 140, degc, {"test_method": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
            "14. Glass Transition Temperature, minimum  TMA  -  140  150  140  degC  2.4.24  3.10.1.6", "degC",
            " Tg 는 측정법마다 다른 값이므로 TMA/DMA/DSC 를 세 행으로 갈랐다."),
        one("thermal.glass_transition", "K", 160, degc, {"test_method": "DMA", "test_standard": "IPC-TM-650 2.4.24.4"},
            "14. Glass Transition Temperature  DMA  160  160  degC  2.4.24.4", "degC", ""),
        one("thermal.glass_transition", "K", 150, degc, {"test_method": "DSC", "test_standard": "IPC-TM-650 2.4.25"},
            "14. Glass Transition Temperature  DSC  150  150  degC  2.4.25", "degC", ""),
        one("thermal.decomposition_temp", "K", 350, degc,
            {"test_standard": "IPC-TM-650 2.4.24.6", "basis": "5% weight loss"},
            "15. Decomposition Temperature, minimum  325  350  325  350  degC  2.4.24.6 (5% wt loss)  3.10.1.8", "degC"),
        one("thermal.heat_of_combustion", "J/kg", 8.989, mjkg, {"test_standard": "ISO 1716"},
            "Caloric Value / Bruttoverbrennungswaerme  -  8,989  -  8,989  MJ/kg  ISO 1716  -", "MJ/kg"),
        one("electrical.dielectric_constant", "1", 4.4, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
            "6. Permittivity at 1 MHz, maximum  5,4  4,4  5,4  4,4  -  2.5.5.2/'2.5.5.3/'2.5.5.9", "-", " 무차원."),
        one("electrical.dielectric_constant", "1", 4.44, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
            "Permittivity at 1 GHz C-24/23/50  -  4,44  -  4,45  -  2.5.5.9  3.11.1.1", "-", " 무차원."),
        one("electrical.dielectric_constant", "1", 4.45, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THICK},
            "Permittivity at 1 GHz C-24/23/50  -  4,44  -  4,45  -  2.5.5.9  3.11.1.1", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.011, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
            "7. Loss Tangent at 1 MHz, maximum  0,035  0,011  0,035  0,011  -", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.013, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
            "Loss Tangent at 1 GHz C-24/23/50  -  0,013  -  0,013  -  2.5.5.9", "-", " 무차원."),
        one("interface.peel_strength", "N/m", 0.78, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THIN},
            "1. Peel Strength, minimum  A. Low profile ... >17um  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,88 [5,00]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 0.88, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THICK},
            "1. Peel Strength  A.  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,88 [5,00]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.23, nmm,
            {"conditioning": "after thermal stress", "copper_foil_type": "standard profile, 35 um",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.1. After thermal stress (35 um)  0,80 [4,57]  0,88 [5,00]  1,05 [6,00]  1,23 [7,00]  N/mm", "N/mm"),
        one("interface.peel_strength", "N/m", 0.88, nmm,
            {"conditioning": "at 125 degC", "temperature_c": 125, "copper_foil_type": "standard profile",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.2. At 125 degC [257 degF]  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,88 [5,00]  N/mm", "N/mm"),
        one("chemical.water_absorption_24h", "1", 0.30, pct,
            {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THIN},
            "4. Moisture Absorption, maximum / Feuchteaufnahme  -  0,30  0,80  0,10  %  2.6.2.1  3.12.1.1", "%"),
        one("chemical.water_absorption_24h", "1", 0.10, pct,
            {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THICK},
            "4. Moisture Absorption, maximum  -  0,30  0,80  0,10  %  2.6.2.1", "%"),
        one("electrical.arc_resistance", "s", 120, lambda v: v,
            {"test_standard": "IPC-TM-650 2.5.1", "specimen": THICK},
            "10. Arc Resistance, minimum / Lichtbogenbestaendigkeit  60  120  60  120  s  2.5.1  3.11.1.5", "s", " 환산 없음."),
        one("electrical.dielectric_strength", "V/m", 40, kvmm,
            {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THIN},
            "12. Electric Strength, minimum / Spannungsfestigkeit  30  40  -  -  kV/mm  2.5.6.2", "kV/mm"),
        one("electrical.comparative_tracking_index", "V", 250, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "lower", "plc": 2},
            "Comparative Tracking Index (CTI) / Kriechstromfestigkeit  -  2 / 250/399  -  2 / 250/399  PLC / V  ASTM-D-3638", "V",
            " 원문 `2 / 250/399` 는 `PLC 2 / 250~399 V` 로 읽힌다(PLC 2 의 정의 구간). 구간이므로 두 행이다."),
        one("electrical.comparative_tracking_index", "V", 399, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "upper", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V  ASTM-D-3638", "V", ""),
        one("thermal.time_to_delamination", "s", 60, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 260, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination (TMA) (Copper removed)  A. T260, minimum  -  60  30  60  Minutes  2.4.24.1", "min"),
        one("thermal.time_to_delamination", "s", 20, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 288, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  B. T288, minimum  -  20  5  20  Minutes  2.4.24.1", "min"),
        one("thermal.time_to_delamination", "s", 5, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 300, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  C. T300, minimum  -  5  AABUS  5  Minutes  2.4.24.1", "min"),
    ])

# ---------------------------------------------------------------- A2. NPG-170TL / 170R / 170B
S = tl_src("Data Sheet / Datenblatt NPG-170R, NPG-170TL, NPG-170B (Rev. Feb.19) — Performance List 1/2, 2/2",
           "Technolam_NanYa_NPG-170TL-NPG-170R-NPG-170B_Datasheet_2019-02.pdf", 2019)
technolam_sheet(
    "Nan Ya NPG-170TL / NPG-170R / NPG-170B Halogen-Free High-Tg FR-4 Copper Clad Laminate",
    "南亞(Nan Ya) 할로겐프리 고Tg(DSC 170 degC) FR-4 동박적층판 3등급 — 저전송손실판 `NPG-170TL`, "
    "표준판 `NPG-170R`, 흑색판 `NPG-170B`. Technolam Datenblatt 2019-02(IPC-4101/128, 적용시트 127·130)이 출처다. "
    "밀도·영률·비열은 IPC 요구가 아닌 `20. Other / weitere` 칸에 있고 `Ref. Para.` 가 `-` 다.",
    ["NPG-170TL", "NPG-170R", "NPG-170B", "NPG170TL", "NPG170R", "NPG170B", "Nan Ya NPG-170R"],
    ["NPG-170TL", "NPG-170R", "NPG-170B"], S, "IPC-4101/128", "UL/ANSI FR-4.1/128", "150 degC minimum",
    [
        one("physical.density", "kg/m^3", 2.10, gcm3, {"resin_content": "50%", "specimen": THIN},
            "Density (50 % resin content) / Dichte 50 % Harzgehalt  -  2,10  -  2,10  g/cm3  -  -", "g/cm^3",
            " 시험법 칸·Ref. Para. 칸 둘 다 `-`. " + TECHNOLAM_TABLE_NOTE),
        one("physical.density", "kg/m^3", 2.10, gcm3, {"resin_content": "50%", "specimen": THICK},
            "Density (50 % resin content)  -  2,10  -  2,10  g/cm3  -  -", "g/cm^3", ""),
        rng_rows("mechanical.youngs_modulus", "Pa", 23, 25, gpa,
                 {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
                  "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
                 "Young's Modulus / E-Modul  A. Length direction  -  -  -  23-25  GPa  -  -", "GPa",
                 TECHNOLAM_YM_NOTE_TAIL, tier=3),
        rng_rows("mechanical.youngs_modulus", "Pa", 22, 24, gpa,
                 {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
                  "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
                 "Young's Modulus / E-Modul  B. Cross direction  -  -  -  22-24  GPa  -  -", "GPa",
                 TECHNOLAM_YM_NOTE_TAIL, tier=3),
        one("thermal.conductivity", "W/(m*K)", 0.43, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THIN},
            "Thermal Conductivity l  -  0,43  -  0,43  W/mK  ASTM-E-1461  3.9.1.5", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.43, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THICK},
            "Thermal Conductivity l  -  0,43  -  0,43  W/mK  ASTM-E-1461", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.39, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THIN},
            "Thermal Conductivity l  -  0,39  -  0,39  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.39, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THICK},
            "Thermal Conductivity l  -  0,39  -  0,39  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.specific_heat", "J/(kg*K)", 0.946, jgk, {"temperature_c": 25, "specimen": THIN},
            "Specific Heat at 25 degC  -  0,946  -  0,946  J/g degC  -  -", "J/(g*K)"),
        one("thermal.specific_heat", "J/(kg*K)", 0.946, jgk, {"temperature_c": 25, "specimen": THICK},
            "Specific Heat at 25 degC  -  0,946  -  0,946  J/g degC  -  -", "J/(g*K)"),
        rng_rows("thermal.expansion_linear", "1/K", 9, 13, ppmk,
                 {"axis": "x/y", "regime": "prior Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  prior Tg  -  9-13  -  9-13  ppm/degC  2.4.24  3.9.1.6", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 9, 13, ppmk,
                 {"axis": "x/y", "regime": "above Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  above Tg  -  9-13  -  9-13  ppm/degC  2.4.24  3.9.1.6", "ppm/degC"),
        one("thermal.expansion_linear", "1/K", 50, ppmk,
            {"axis": "z", "regime": "alpha1 (prior Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  A. Alpha 1, maximum  -  50  60  50  ppm/degC  2.4.24", "ppm/degC"),
        one("thermal.expansion_linear", "1/K", 230, ppmk,
            {"axis": "z", "regime": "alpha2 (above Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  B. Alpha 2, maximum  -  230  300  230  ppm/degC  2.4.24", "ppm/degC"),
        one("thermal.expansion_total", "1", 2.7, pct,
            {"axis": "z", "temperature_range_c": "50-260", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  C. 50 to 260 degC, maximum (Total Expansion)  -  2,7  3,5  2,7  %", "%"),
        one("mechanical.flexural_strength", "Pa", 450, mpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength, minimum  A. Length direction  -  -  415 [60190]  450 [65267]  N/mm2  2.4.4", "N/mm^2",
            " **굽힘이다** — 2.4.4 는 IPC-TM-650 굽힘강도법."),
        one("mechanical.flexural_strength", "Pa", 390, mpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength  B. Cross direction  -  -  345 [50040]  390 [56565]  N/mm2  2.4.4", "N/mm^2"),
        one("thermal.glass_transition", "K", 160, degc, {"test_method": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
            "14. Glass Transition Temperature, minimum  TMA  160  160  degC  2.4.24", "degC"),
        one("thermal.glass_transition", "K", 180, degc, {"test_method": "DMA", "test_standard": "IPC-TM-650 2.4.24.4"},
            "14. Glass Transition Temperature  DMA  180  180  degC  2.4.24.4", "degC"),
        one("thermal.glass_transition", "K", 170, degc, {"test_method": "DSC", "test_standard": "IPC-TM-650 2.4.25"},
            "14. Glass Transition Temperature  DSC  170  170  degC  2.4.25", "degC"),
        one("thermal.decomposition_temp", "K", 350, degc,
            {"test_standard": "IPC-TM-650 2.4.24.6", "basis": "5% weight loss"},
            "15. Decomposition Temperature, minimum  325  350  325  350  degC  2.4.24.6 (5% wt loss)", "degC"),
        one("thermal.heat_of_combustion", "J/kg", 8.828, mjkg, {"test_standard": "ISO 1716"},
            "Caloric Value / Bruttoverbrennungswaerme  -  8,828  -  8,828  MJ/kg  ISO 1716", "MJ/kg"),
        one("electrical.dielectric_constant", "1", 4.9, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
            "6. Permittivity at 1 MHz, maximum  5,4  4,9  5,4  4,9  -", "-", " 무차원."),
        one("electrical.dielectric_constant", "1", 4.17, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
            "Permittivity at 1 GHz C-24/23/50  -  4,17  -  4,21  -  2.5.5.9", "-", " 무차원."),
        one("electrical.dielectric_constant", "1", 4.21, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THICK},
            "Permittivity at 1 GHz C-24/23/50  -  4,17  -  4,21  -  2.5.5.9", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.010, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
            "7. Loss Tangent at 1 MHz, maximum  0,035  0,010  0,035  0,010  -", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.015, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
            "Loss Tangent at 1 GHz C-24/23/50  -  0,015  -  0,015  -  2.5.5.9", "-", " 무차원."),
        one("interface.peel_strength", "N/m", 0.78, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THIN},
            "1. Peel Strength  A.  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,88 [5,00]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 0.88, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THICK},
            "1. Peel Strength  A.  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,88 [5,00]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.23, nmm,
            {"conditioning": "after thermal stress", "copper_foil_type": "standard profile, 35 um",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.1. After thermal stress (35 um)  0,80 [4,57]  0,88 [5,00]  1,05 [6,00]  1,23 [7,00]", "N/mm"),
        one("chemical.water_absorption_24h", "1", 0.30, pct, {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THIN},
            "4. Moisture Absorption, maximum  -  0,30  0,80  0,10  %  2.6.2.1", "%"),
        one("chemical.water_absorption_24h", "1", 0.10, pct, {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THICK},
            "4. Moisture Absorption, maximum  -  0,30  0,80  0,10  %  2.6.2.1", "%"),
        one("electrical.arc_resistance", "s", 120, lambda v: v, {"test_standard": "IPC-TM-650 2.5.1", "specimen": THICK},
            "10. Arc Resistance, minimum  60  120  60  120  s  2.5.1", "s", " 환산 없음."),
        one("electrical.dielectric_strength", "V/m", 40, kvmm, {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THIN},
            "12. Electric Strength, minimum  30  40  -  -  kV/mm  2.5.6.2", "kV/mm"),
        one("thermal.time_to_delamination", "s", 60, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 260, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  A. T260, minimum  -  60  30  60  Minutes", "min"),
        one("thermal.time_to_delamination", "s", 20, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 288, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  B. T288, minimum  -  20  5  20  Minutes", "min"),
        one("electrical.comparative_tracking_index", "V", 250, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "lower", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V  ASTM-D-3638", "V",
            " `2 / 250/399` = PLC 2 / 250~399 V. 구간이므로 두 행."),
        one("electrical.comparative_tracking_index", "V", 399, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "upper", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V", "V"),
    ])

# ---------------------------------------------------------------- A3. NPG-170DTL / DR / DB
S = tl_src("Data Sheet / Datenblatt NPG-170DTL, NPG-170DR, NPG-170DB (Rev. Feb.19) — Performance List 1/2, 2/2",
           "Technolam_NanYa_NPG-170DTL-NPG-170DR-NPG-170DB_Datasheet_2019-02.pdf", 2019)
technolam_sheet(
    "Nan Ya NPG-170DTL / NPG-170DR / NPG-170DB Halogen-Free Low-Dk High-Tg FR-4 Laminate",
    "南亞(Nan Ya) 할로겐프리 저유전율(Dk 1 GHz 3,9~4,0) 고Tg FR-4 동박적층판 3등급 — `NPG-170DTL`(저전송손실), "
    "`NPG-170DR`, `NPG-170DB`(흑색). Technolam Datenblatt 2019-02(IPC-4101/128, 적용시트 127·128). "
    "이 시트는 형제 시트와 달리 **밀도가 2,15 g/cm3 로 더 높고**(무기 필러가 더 많다) "
    "**열전도율 ASTM-E-1461 칸이 `-` 이며 ASTM-D-5470 만 0,53 W/mK 를 찍는다** — 없는 칸을 채우지 않았다.",
    ["NPG-170DTL", "NPG-170DR", "NPG-170DB", "NPG170DTL", "NPG170DR", "NPG170DB"],
    ["NPG-170DTL", "NPG-170DR", "NPG-170DB"], S, "IPC-4101/128", "UL/ANSI FR-4.1/128", "150 degC minimum",
    [
        one("physical.density", "kg/m^3", 2.15, gcm3, {"resin_content": "50%", "specimen": THIN},
            "Density (50 % resin content) / Dichte 50 % Harzgehalt  -  2,15  -  2,15  g/cm3  -  -", "g/cm^3",
            " 시험법 칸·Ref. Para. 칸 둘 다 `-`. " + TECHNOLAM_TABLE_NOTE),
        one("physical.density", "kg/m^3", 2.15, gcm3, {"resin_content": "50%", "specimen": THICK},
            "Density (50 % resin content)  -  2,15  -  2,15  g/cm3  -  -", "g/cm^3", ""),
        one("mechanical.youngs_modulus", "Pa", 24, gpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "specimen": THIN, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
            "Young's Modulus / E-Modul  A. Length direction  -  24  -  24  GPa  -  -", "GPa",
            TECHNOLAM_YM_NOTE_TAIL + " 이 시트는 형제와 달리 구간이 아니라 단일값을 찍는다.", tier=3),
        one("mechanical.youngs_modulus", "Pa", 24, gpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
            "Young's Modulus / E-Modul  A. Length direction  -  24  -  24  GPa  -  -", "GPa",
            TECHNOLAM_YM_NOTE_TAIL, tier=3),
        one("mechanical.youngs_modulus", "Pa", 22, gpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "specimen": THIN, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
            "Young's Modulus / E-Modul  B. Cross direction  -  22  -  22  GPa  -  -", "GPa",
            TECHNOLAM_YM_NOTE_TAIL, tier=3),
        one("mechanical.youngs_modulus", "Pa", 22, gpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
            "Young's Modulus / E-Modul  B. Cross direction  -  22  -  22  GPa  -  -", "GPa",
            TECHNOLAM_YM_NOTE_TAIL, tier=3),
        one("thermal.conductivity", "W/(m*K)", 0.53, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THIN},
            "Thermal Conductivity l  -  -  -  -  ASTM-E-1461 / -  0,53  -  0,53  W/mK  ASTM-D-5470", "W/mK",
            " 환산 없음. **ASTM-E-1461 행은 네 칸 전부 `-` 라 담지 않았다** — 형제 시트에는 값이 있으나 이 시트에는 없다."),
        one("thermal.conductivity", "W/(m*K)", 0.53, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THICK},
            "Thermal Conductivity l  -  0,53  -  0,53  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.specific_heat", "J/(kg*K)", 0.95, jgk, {"temperature_c": 25, "specimen": THIN},
            "Specific Heat at 25 degC  -  0,95  -  0,95  J/g degC  -  -", "J/(g*K)"),
        one("thermal.specific_heat", "J/(kg*K)", 0.95, jgk, {"temperature_c": 25, "specimen": THICK},
            "Specific Heat at 25 degC  -  0,95  -  0,95  J/g degC  -  -", "J/(g*K)"),
        rng_rows("thermal.expansion_linear", "1/K", 9, 13, ppmk,
                 {"axis": "x/y", "regime": "prior Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  prior Tg  -  9-13  -  9-13  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 9, 13, ppmk,
                 {"axis": "x/y", "regime": "above Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  above Tg  -  9-13  -  9-13  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 30, 40, ppmk,
                 {"axis": "z", "regime": "alpha1 (prior Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "16. Z-Axis CTE  A. Alpha 1, maximum  -  30-40  60  30-40  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 200, 230, ppmk,
                 {"axis": "z", "regime": "alpha2 (above Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "16. Z-Axis CTE  B. Alpha 2, maximum  -  200-230  300  200-230  ppm/degC  2.4.24", "ppm/degC"),
        one("thermal.expansion_total", "1", 3.0, pct,
            {"axis": "z", "temperature_range_c": "50-260", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  C. 50 to 260 degC, maximum (Total Expansion)  -  3,0  3,0  3,0  %", "%"),
        rng_rows("mechanical.flexural_strength", "Pa", 475, 550, mpa,
                 {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
                  "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
                 "8. Flexural Strength, minimum  A. Length direction  -  <blank>  415 [60190]  475-550  N/mm2  2.4.4", "N/mm^2",
                 " N/mm^2 = MPa. **굽힘이다**(2.4.4)."),
        rng_rows("mechanical.flexural_strength", "Pa", 360, 440, mpa,
                 {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
                  "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
                 "8. Flexural Strength  B. Cross direction  -  <blank>  345 [50040]  360-440  N/mm2  2.4.4", "N/mm^2"),
        one("mechanical.flexural_strength", "Pa", 365, mpa,
            {"direction": "warp", "regime": "at elevated temperature",
             "test_standard": "IPC-TM-650 2.4.4.1", "specimen": THIN},
            "9. Flexural Strength at Elevated Temperature length direction, minimum  -  365  -  385  N/mm2  2.4.4.1", "N/mm^2",
            " 원문이 시험온도를 적지 않는다 — 온도 조건을 지어내지 않고 `regime` 에 원문 표기만 남겼다."),
        one("mechanical.flexural_strength", "Pa", 385, mpa,
            {"direction": "warp", "regime": "at elevated temperature",
             "test_standard": "IPC-TM-650 2.4.4.1", "specimen": THICK},
            "9. Flexural Strength at Elevated Temperature length direction, minimum  -  365  -  385  N/mm2  2.4.4.1", "N/mm^2",
            " 원문이 시험온도를 적지 않는다."),
        one("thermal.glass_transition", "K", 160, degc, {"test_method": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
            "14. Glass Transition Temperature, minimum  TMA  160  160  degC  2.4.24", "degC"),
        one("thermal.glass_transition", "K", 180, degc, {"test_method": "DMA", "test_standard": "IPC-TM-650 2.4.24.4"},
            "14. Glass Transition Temperature  DMA  180  180  degC  2.4.24.4", "degC"),
        one("thermal.glass_transition", "K", 170, degc, {"test_method": "DSC", "test_standard": "IPC-TM-650 2.4.25"},
            "14. Glass Transition Temperature  DSC  170  170  degC  2.4.25", "degC"),
        one("thermal.decomposition_temp", "K", 380, degc,
            {"test_standard": "IPC-TM-650 2.4.24.6", "basis": "5% weight loss"},
            "15. Decomposition Temperature, minimum  340  380  340  380  degC  2.4.24.6 (5% wt loss)", "degC"),
        one("electrical.dielectric_constant", "1", 4.03, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
            "6. Permittivity at 1 MHz, maximum  5,4  4,03  5,4  4,04  -", "-", " 무차원."),
        one("electrical.dielectric_constant", "1", 4.04, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THICK},
            "6. Permittivity at 1 MHz, maximum  5,4  4,03  5,4  4,04  -", "-", " 무차원."),
        rng_rows("electrical.dielectric_constant", "1", 3.9, 4.0, lambda v: v,
                 {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
                 "Permittivity at 1 GHz C-24/23/50  -  3,9-4,0  -  3,9-4,0  -  2.5.5.9", "-", " 무차원."),
        rng_rows("electrical.dissipation_factor", "1", 0.005, 0.006, lambda v: v,
                 {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
                 "7. Loss Tangent at 1 MHz, maximum  0,035  0,005-0,006  0,035  0,005-0,006  -", "-", " 무차원."),
        rng_rows("electrical.dissipation_factor", "1", 0.005, 0.006, lambda v: v,
                 {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
                 "Loss Tangent at 1 GHz C-24/23/50  -  0,005-0,006  -  0,005-0,006  -  2.5.5.9", "-", " 무차원."),
        rng_rows("interface.peel_strength", "N/m", 1.23, 1.40, nmm,
                 {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
                  "test_standard": "IPC-TM-650 2.4.8", "specimen": THICK},
                 "1. Peel Strength  A.  0,70 [4,00]  1,23-1,40  0,70 [4,00]  1,23-1,40  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.21, nmm,
            {"conditioning": "after thermal stress", "copper_foil_type": "standard profile, 35 um",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.1. After thermal stress (35 um)  0,80 [4,57]  1,21  1,05 [6,00]  1,21", "N/mm"),
        one("interface.peel_strength", "N/m", 1.15, nmm,
            {"conditioning": "at 125 degC", "temperature_c": 125, "copper_foil_type": "standard profile",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.2. At 125 degC [257 degF]  0,70 [4,00]  1,15  0,70 [4,00]  1,15", "N/mm"),
        rng_rows("chemical.water_absorption_24h", "1", 0.2, 0.3, pct,
                 {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THIN},
                 "4. Moisture Absorption, maximum  -  0,2-0,3  0,80  0,2-0,3  %  2.6.2.1", "%"),
        one("electrical.dielectric_strength", "V/m", 48, kvmm, {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THIN},
            "12. Electric Strength, minimum  30  48  -  48  kV/mm  2.5.6.2", "kV/mm"),
        one("electrical.dielectric_strength", "V/m", 48, kvmm, {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THICK},
            "12. Electric Strength, minimum  30  48  -  48  kV/mm  2.5.6.2", "kV/mm"),
        one("thermal.time_to_delamination", "s", 60, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 260, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  A. T260, minimum  -  60  30  60  Minutes", "min"),
        one("thermal.time_to_delamination", "s", 60, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 288, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  B. T288, minimum  -  60  15  60  Minutes", "min"),
        one("thermal.time_to_delamination", "s", 40, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 300, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  C. T300, minimum  -  40  2  40  Minutes", "min"),
        one("electrical.comparative_tracking_index", "V", 250, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "lower", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V  ASTM-D-3638", "V",
            " `2 / 250/399` = PLC 2 / 250~399 V."),
        one("electrical.comparative_tracking_index", "V", 399, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "upper", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V", "V"),
    ])

# ---------------------------------------------------------------- A4. NPG-180BH / BHB
S = tl_src("Data Sheet / Datenblatt NPG-180BH, NPG-180BHB (Rev. Aug.19) — Performance List 1/2, 2/2",
           "Technolam_NanYa_NPG-180BH-NPG-180BHB_Datasheet_2019-08.pdf", 2019)
technolam_sheet(
    "Nan Ya NPG-180BH / NPG-180BHB Halogen-Free High-Tg Low-CTE FR-4 Laminate",
    "南亞(Nan Ya) 할로겐프리 고Tg(DMA 190 degC) 저CTE FR-4 동박적층판 `NPG-180BH` 와 흑색판 `NPG-180BHB`. "
    "Technolam Datenblatt 2019-08(IPC-4101/128, 적용시트 127·128). z축 alpha2 가 135~150 ppm/degC 로 형제 등급의 "
    "절반 수준이고 총팽창(50~260 degC)이 1,6 % 다.",
    ["NPG-180BH", "NPG-180BHB", "NPG180BH", "NPG180BHB"],
    ["NPG-180BH", "NPG-180BHB"], S, "IPC-4101/128", "UL/ANSI FR-4.1/128", "150 degC minimum",
    [
        one("physical.density", "kg/m^3", 2.10, gcm3, {"resin_content": "50%", "specimen": THIN},
            "Density (50 % resin content) / Dichte 50 % Harzgehalt  -  2,10  -  2,10  g/cm3  -  -", "g/cm^3",
            " 시험법 칸·Ref. Para. 칸 둘 다 `-`. " + TECHNOLAM_TABLE_NOTE),
        one("physical.density", "kg/m^3", 2.10, gcm3, {"resin_content": "50%", "specimen": THICK},
            "Density (50 % resin content)  -  2,10  -  2,10  g/cm3  -  -", "g/cm^3", ""),
        one("mechanical.youngs_modulus", "Pa", 24, gpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
            "Young's Modulus / E-Modul  A. Length direction  -  -  -  24  GPa  -  -", "GPa",
            TECHNOLAM_YM_NOTE_TAIL + " <0,50 mm 열은 `-` 라 담지 않았다.", tier=3),
        one("mechanical.youngs_modulus", "Pa", 22, gpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
            "Young's Modulus / E-Modul  B. Cross direction  -  -  -  22  GPa  -  -", "GPa",
            TECHNOLAM_YM_NOTE_TAIL, tier=3),
        one("thermal.conductivity", "W/(m*K)", 0.55, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THIN},
            "Thermal Conductivity l  -  0,55  -  0,55  W/mK  ASTM-E-1461", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.55, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THICK},
            "Thermal Conductivity l  -  0,55  -  0,55  W/mK  ASTM-E-1461", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.46, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THIN},
            "Thermal Conductivity l  -  0,46  -  0,46  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.46, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THICK},
            "Thermal Conductivity l  -  0,46  -  0,46  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.specific_heat", "J/(kg*K)", 0.94, jgk, {"temperature_c": 25, "specimen": THIN},
            "Specific Heat at 25 degC  -  0,94  -  0,94  J/g degC  -  -", "J/(g*K)"),
        one("thermal.specific_heat", "J/(kg*K)", 0.94, jgk, {"temperature_c": 25, "specimen": THICK},
            "Specific Heat at 25 degC  -  0,94  -  0,94  J/g degC  -  -", "J/(g*K)"),
        rng_rows("thermal.expansion_linear", "1/K", 11, 13, ppmk,
                 {"axis": "x/y", "regime": "prior Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  prior Tg  -  11-13  -  11-13  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 11, 13, ppmk,
                 {"axis": "x/y", "regime": "above Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THIN},
                 "X/Y-Axis CTE  above Tg  -  11-13  -  11-13  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 33, 43, ppmk,
                 {"axis": "z", "regime": "alpha1 (prior Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "16. Z-Axis CTE  A. Alpha 1, maximum  -  33-43  60  33-43  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 135, 150, ppmk,
                 {"axis": "z", "regime": "alpha2 (above Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "16. Z-Axis CTE  B. Alpha 2, maximum  -  135-150  300  135-150  ppm/degC  2.4.24", "ppm/degC"),
        one("thermal.expansion_total", "1", 1.6, pct,
            {"axis": "z", "temperature_range_c": "50-260", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "16. Z-Axis CTE  C. 50 to 260 degC, maximum (Total Expansion)  -  1,6  3,0  1,6  %", "%"),
        one("mechanical.flexural_strength", "Pa", 450, mpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength, minimum  A. Length direction  -  -  415 [60190]  450 [65250]  N/mm2  2.4.4", "N/mm^2",
            " **굽힘이다**(2.4.4)."),
        one("mechanical.flexural_strength", "Pa", 390, mpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength  B. Cross direction  -  -  345 [50040]  390 [56550]  N/mm2  2.4.4", "N/mm^2"),
        one("thermal.glass_transition", "K", 170, degc, {"test_method": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
            "14. Glass Transition Temperature, minimum  TMA  170  170  degC  2.4.24", "degC"),
        one("thermal.glass_transition", "K", 190, degc, {"test_method": "DMA", "test_standard": "IPC-TM-650 2.4.24.4"},
            "14. Glass Transition Temperature  DMA  -  190  170  190  degC  2.4.24.4", "degC"),
        one("thermal.glass_transition", "K", 175, degc, {"test_method": "DSC", "test_standard": "IPC-TM-650 2.4.25"},
            "14. Glass Transition Temperature  DSC  175  175  degC  2.4.25", "degC"),
        one("thermal.decomposition_temp", "K", 380, degc,
            {"test_standard": "IPC-TM-650 2.4.24.6", "basis": "5% weight loss"},
            "15. Decomposition Temperature, minimum  -  380  340  380  degC  2.4.24.6 (5% wt loss)", "degC"),
        one("electrical.dielectric_constant", "1", 4.5, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
            "6. Permittivity at 1 MHz, maximum  5,4  4,5  5,4  4,6  -", "-", " 무차원."),
        one("electrical.dielectric_constant", "1", 4.6, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THICK},
            "6. Permittivity at 1 MHz, maximum  5,4  4,5  5,4  4,6  -", "-", " 무차원."),
        rng_rows("electrical.dielectric_constant", "1", 4.3, 4.6, lambda v: v,
                 {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THIN},
                 "Permittivity at 1 GHz C-24/23/50  -  4,3-4,6  -  4,3-4,5  -  2.5.5.9", "-", " 무차원."),
        rng_rows("electrical.dielectric_constant", "1", 4.3, 4.5, lambda v: v,
                 {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THICK},
                 "Permittivity at 1 GHz C-24/23/50  -  4,3-4,6  -  4,3-4,5  -  2.5.5.9", "-", " 무차원."),
        rng_rows("electrical.dissipation_factor", "1", 0.016, 0.020, lambda v: v,
                 {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THIN},
                 "7. Loss Tangent at 1 MHz, maximum  0,035  0,016-0,020  0,035  0,016  -", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.016, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THICK},
            "7. Loss Tangent at 1 MHz, maximum  0,035  0,016-0,020  0,035  0,016  -", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.01, lambda v: v,
            {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THICK},
            "Loss Tangent at 1 GHz C-24/23/50  -  0,01-0,013  -  0,01  -  2.5.5.9", "-", " 무차원."),
        one("interface.peel_strength", "N/m", 0.78, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THIN},
            "1. Peel Strength  A.  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,70 [4,00]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 0.70, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THICK},
            "1. Peel Strength  A.  0,70 [4,00]  0,78 [4,50]  0,70 [4,00]  0,70 [4,00]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.05, nmm,
            {"conditioning": "after thermal stress", "copper_foil_type": "standard profile, 35 um",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.1. After thermal stress (35 um)  0,80 [4,57]  0,88 [5,00]  1,05 [6,00]  1,05 [6,00]", "N/mm"),
        one("chemical.water_absorption_24h", "1", 0.20, pct, {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THIN},
            "4. Moisture Absorption, maximum  -  0,20  0,8  0,12  %  2.6.2.1", "%"),
        one("chemical.water_absorption_24h", "1", 0.12, pct, {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THICK},
            "4. Moisture Absorption, maximum  -  0,20  0,8  0,12  %  2.6.2.1", "%"),
        one("electrical.dielectric_strength", "V/m", 30, kvmm, {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THIN},
            "12. Electric Strength, minimum  30  30  -  30  kV/mm  2.5.6.2", "kV/mm"),
        one("electrical.dielectric_strength", "V/m", 30, kvmm, {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THICK},
            "12. Electric Strength, minimum  30  30  -  30  kV/mm  2.5.6.2", "kV/mm"),
        one("thermal.time_to_delamination", "s", 40, minutes,
            {"test_method": "TMA, copper removed", "temperature_c": 300, "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
            "17. Time to Delamination  C. T300, minimum  -  40  2  40  Minutes", "min",
            " T260·T288 은 원문이 `>60` 이라 한쪽 부등호뿐이므로 담지 않았다."),
        one("electrical.comparative_tracking_index", "V", 250, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "lower", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V  ASTM-D-3638", "V"),
        one("electrical.comparative_tracking_index", "V", 399, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "upper", "plc": 2},
            "Comparative Tracking Index (CTI)  -  2 / 250/399  -  2 / 250/399  PLC / V", "V"),
    ])

# ---------------------------------------------------------------- A5. UV Block FR-4-86
S = tl_src("Data Sheet / Datenblatt UV Block FR-4-86 (Rev. Feb.19) — Performance List 1/2, 2/2",
           "Technolam_NanYa_UV-Block-FR-4-86_Datasheet_2019-02.pdf", 2019)
technolam_sheet(
    "Nan Ya UV Block FR-4-86 Copper Clad Laminate",
    "南亞(Nan Ya) UV 차단 표준 Tg FR-4 동박적층판 `UV Block FR-4-86`. Technolam Datenblatt 2019-02 "
    "(IPC-4101/21, UL/ANSI FR-4.0/21, Tg 110 degC minimum). 이 시트는 형제 NPG 시트와 달리 "
    "**`<0,50 mm` 열이 전부 `-` 이고 `>=0,50 mm` 열만 값을 찍는다** — 없는 열을 채우지 않았다. "
    "번호 항목이 1~14 번까지이고 `15. Other / weitere` 아래에 밀도(1,92 g/cm3)·영률·비열이 있다.",
    ["UV Block FR-4-86", "FR-4-86", "FR4-86", "UV-Block FR-4-86", "UV Block FR4-86"],
    ["UV Block FR-4-86"], S, "IPC-4101/21", "UL/ANSI FR-4.0/21", "110 degC minimum",
    [
        one("physical.density", "kg/m^3", 1.92, gcm3, {"resin_content": "50%", "specimen": THICK},
            "Density (50 % resin content) / Dichte 50 % Harzgehalt  -  -  -  1,92  g/cm3  -  -", "g/cm^3",
            " 시험법 칸·Ref. Para. 칸 둘 다 `-`. 형제 NPG 등급(2,00~2,15)보다 낮다 — 이 등급은 FILLERS `<5%` 로 "
            "무기 필러가 거의 없다(시트 머리 verbatim). " + TECHNOLAM_TABLE_NOTE),
        rng_rows("mechanical.youngs_modulus", "Pa", 21, 23, gpa,
                 {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
                  "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
                 "Young's Modulus / E-Modul  A. Length direction  -  -  -  21-23  GPa  -  -", "GPa",
                 TECHNOLAM_YM_NOTE_TAIL, tier=3),
        rng_rows("mechanical.youngs_modulus", "Pa", 20, 22, gpa,
                 {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
                  "specimen": THICK, "test_mode": "unconfirmed", "grade_scope": TECHNOLAM_YM_SCOPE},
                 "Young's Modulus / E-Modul  B. Cross direction  -  -  -  20-22  GPa  -  -", "GPa",
                 TECHNOLAM_YM_NOTE_TAIL, tier=3),
        one("thermal.conductivity", "W/(m*K)", 0.36, lambda v: v, {"test_standard": "ASTM E1461", "specimen": THICK},
            "Thermal Conductivity l  -  -  -  0,36  W/mK  ASTM-E-1461  3.9.1.5", "W/mK", " 환산 없음."),
        one("thermal.conductivity", "W/(m*K)", 0.32, lambda v: v, {"test_standard": "ASTM D5470", "specimen": THICK},
            "Thermal Conductivity l  -  -  -  0,32  W/mK  ASTM-D-5470", "W/mK", " 환산 없음."),
        one("thermal.specific_heat", "J/(kg*K)", 0.913, jgk, {"temperature_c": 25, "specimen": THICK},
            "Specific Heat at 25 degC / Spezifische Waermekapzitaet bei 25 degC  -  -  -  0,913  J/g degC  -  -", "J/(g*K)"),
        rng_rows("thermal.expansion_linear", "1/K", 15, 18, ppmk,
                 {"axis": "x/y", "regime": "prior Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "CTE, X/Y-Axis  prior Tg / vor Tg  -  -  -  15-18  ppm/degC  2.4.24  3.9.1.6", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 15, 18, ppmk,
                 {"axis": "x/y", "regime": "above Tg", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "CTE, X/Y-Axis  above Tg / ueber Tg  -  -  -  15-18  ppm/degC  2.4.24", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 50, 70, ppmk,
                 {"axis": "z", "regime": "alpha1 (prior Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "Z-Axis CTE  A. Alpha 1  prior Tg  -  -  -  50-70  ppm/degC  2.4.24  3.9.1.7", "ppm/degC"),
        rng_rows("thermal.expansion_linear", "1/K", 250, 350, ppmk,
                 {"axis": "z", "regime": "alpha2 (above Tg)", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
                 "Z-Axis CTE  B. Alpha 2  above Tg  -  -  -  250-350  ppm/degC  2.4.24", "ppm/degC"),
        one("thermal.expansion_total", "1", 4.2, pct,
            {"axis": "z", "temperature_range_c": "50-260", "test_standard": "IPC-TM-650 2.4.24", "specimen": THICK},
            "Z-Axis CTE  C. 50 to 260 degC, (Total Expansion)  -  -  -  4,2  %", "%"),
        one("mechanical.flexural_strength", "Pa", 480, mpa,
            {"direction": "warp", "direction_verbatim": "A. Length direction / Kettrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength, minimum  A. Length direction  -  -  415 [60190]  480 [69618]  N/mm2  2.4.4", "N/mm^2",
            " **굽힘이다**(2.4.4)."),
        one("mechanical.flexural_strength", "Pa", 415, mpa,
            {"direction": "fill", "direction_verbatim": "B. Cross direction / Schussrichtung",
             "test_standard": "IPC-TM-650 2.4.4", "specimen": THICK},
            "8. Flexural Strength  B. Cross direction  -  -  345 [50040]  415 [60190]  N/mm2  2.4.4", "N/mm^2"),
        one("thermal.glass_transition", "K", 130, degc, {"test_method": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
            "14. Glass Transition Temperature, minimum  TMA  -  -  110  130  degC  2.4.24", "degC"),
        one("thermal.glass_transition", "K", 135, degc, {"test_method": "DSC", "test_standard": "IPC-TM-650 2.4.25"},
            "14. Glass Transition Temperature  DSC  -  135  degC  2.4.25", "degC",
            " 이 시트에는 DMA 행이 없다(형제 NPG 시트에는 있다)."),
        one("thermal.decomposition_temp", "K", 310, degc,
            {"test_standard": "IPC-TM-650 2.4.24.6", "basis": "5% weight loss"},
            "Decomposition Temperature / Zersetzungstemperatur  -  -  -  310  degC  2.4.24.6 (5% wt loss)", "degC"),
        one("thermal.heat_of_combustion", "J/kg", 10.081, mjkg, {"test_standard": "ISO 1716"},
            "Caloric Value / Bruttoverbrennungswaerme  -  -  -  10,081  MJ/kg  ISO 1716", "MJ/kg"),
        one("electrical.dielectric_constant", "1", 4.7, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THICK},
            "6. Permittivity at 1 MHz, maximum  5,4  -  5,4  4,7  -", "-", " 무차원."),
        rng_rows("electrical.dielectric_constant", "1", 4.0, 4.2, lambda v: v,
                 {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THICK},
                 "Permittivity at 1 GHz C-24/23/50  -  -  -  4,0-4,2  -  2.5.5.9", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", 0.020, lambda v: v,
            {"frequency_hz": 1e6, "test_standard": "IPC-TM-650 2.5.5.2/2.5.5.3/2.5.5.9", "specimen": THICK},
            "7. Loss Tangent at 1 MHz, maximum  0,035  -  0,035  0,020  -", "-", " 무차원."),
        rng_rows("electrical.dissipation_factor", "1", 0.012, 0.014, lambda v: v,
                 {"frequency_hz": 1e9, "conditioning": "C-24/23/50", "test_standard": "IPC-TM-650 2.5.5.9", "specimen": THICK},
                 "Loss Tangent at 1 GHz C-24/23/50  -  -  -  0,012-0,014  -  2.5.5.9", "-", " 무차원."),
        one("interface.peel_strength", "N/m", 0.96, nmm,
            {"conditioning": "as received", "copper_foil_type": "low profile / very low profile, >17 um",
             "test_standard": "IPC-TM-650 2.4.8", "specimen": THICK},
            "1. Peel Strength  A.  0,70 [4,00]  <blank>  0,70 [4,00]  0,96 [5,50]  N/mm [lb/in]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.75, nmm,
            {"conditioning": "after thermal stress", "copper_foil_type": "standard profile, 35 um",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.1. After thermal stress (35 um)  0,80 [4,57]  <blank>  1,05 [6,00]  1,75 [10,00]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.22, nmm,
            {"conditioning": "at 125 degC", "temperature_c": 125, "copper_foil_type": "standard profile",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.2. At 125 degC [257 degF]  0,70 [4,00]  <blank>  0,70 [4,00]  1,22 [7,00]", "N/mm"),
        one("interface.peel_strength", "N/m", 1.13, nmm,
            {"conditioning": "after process solutions", "copper_foil_type": "standard profile",
             "test_standard": "IPC-TM-650 2.4.8.2/2.4.8.3", "specimen": THICK},
            "1. Peel Strength  B.3. After process solutions  0,55 [3,14]  <blank>  0,80 [4,57]  1,13 [6,50]", "N/mm"),
        one("chemical.water_absorption_24h", "1", 0.10, pct, {"test_standard": "IPC-TM-650 2.6.2.1", "specimen": THICK},
            "4. Moisture Absorption, maximum  -  -  0,80  0,10  %  2.6.2.1", "%"),
        one("electrical.arc_resistance", "s", 120, lambda v: v, {"test_standard": "IPC-TM-650 2.5.1", "specimen": THICK},
            "10. Arc Resistance, minimum  60  -  60  120  s  2.5.1", "s", " 환산 없음."),
        one("electrical.dielectric_strength", "V/m", 40, kvmm, {"test_standard": "IPC-TM-650 2.5.6.2", "specimen": THICK},
            "12. Electric Strength, minimum  30  -  -  40  kV/mm  2.5.6.2", "kV/mm"),
        rng_rows("thermal.time_to_delamination", "s", 20, 30, minutes,
                 {"test_method": "TMA, copper removed", "temperature_c": 260,
                  "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
                 "Time to Delamination (TMA) (Copper removed)  A. T260  -  -  -  20-30  Minutes  2.4.24.1", "min"),
        rng_rows("thermal.time_to_delamination", "s", 2, 5, minutes,
                 {"test_method": "TMA, copper removed", "temperature_c": 288,
                  "test_standard": "IPC-TM-650 2.4.24.1", "specimen": THICK},
                 "Time to Delamination  B. T288  -  -  -  2-5  Minutes  2.4.24.1", "min",
                 " T300 칸은 `-` 라 담지 않았다."),
        one("electrical.comparative_tracking_index", "V", 175, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "lower", "plc": 3},
            "Comparative Tracking Index (CTI)  -  -  -  3 / 175-249  PLC / V  ASTM-D-3638", "V",
            " 원문 `3 / 175-249` = PLC 3 / 175~249 V. 구간이므로 두 행."),
        one("electrical.comparative_tracking_index", "V", 249, lambda v: v,
            {"test_standard": "ASTM D3638", "bound": "upper", "plc": 3},
            "Comparative Tracking Index (CTI)  -  -  -  3 / 175-249  PLC / V  ASTM-D-3638", "V"),
    ])

# ================================================================================
# B. Nan Ya CCL 대만 포털 시트 (Characteristics | Unit | Conditioning | Typical Values | SPEC | Test Method)
# ================================================================================
NANYA_COL_NOTE = (
    "**열 확인** — 이 표의 열 순서는 `Characteristics | Unit | Conditioning | Typical Values | SPEC | Test Method` 다"
    "(300 dpi 렌더로 확정). 담은 값은 **Typical Values** 열이고, `SPEC` 열은 합격 한계이지 물성이 아니라 담지 않았다."
)
NANYA_SPECIMEN = "0.030 in (0.76 mm) 1/1 (원문 NOTE: The average value in the table refers to samples of 0.030\" 1/1)"


def nanya_ccl(name, desc, aliases, grade, local, issued, rows, extra_attrs=None):
    src = {"kind": "datasheet",
           "title": f"NAN YA PLASTICS CORPORATION, Electronic Materials Division, Copper Clad Laminate "
                    f"Department — {grade} PERFORMANCE LIST (Issued {issued}, New 2024/10/11)",
           "url": None, "publisher": "Nan Ya Plastics Corporation", "year": 2024,
           "local_path": CORPUS + local,
           "url_note": ("대만 유통 포털(cclqc.npc.com.tw)에서 받은 PDF 다. 파일별 URL 에 난수 접미어가 붙어 "
                        "이 등급의 절대 URL 을 확정하지 못했다 — 지어내지 않았다.")}
    attrs = {"material_class": "copper clad laminate for RF / microwave circuits",
             "subsystem": "pcb", "role": "product",
             "role_reason": "제조사(Nan Ya)+등급명이 이름에 박혀 있고 출처가 해당 등급의 공식 PERFORMANCE LIST 다.",
             "role_confidence": "high",
             "manufacturer": "Nan Ya Plastics Corporation",
             "grades_covered": [grade], "aliases": aliases,
             "column_layout": NANYA_COL_NOTE,
             "core7_absent_from_vendor_sheet": (
                 "이 표에는 **영률·포아송비·비열·인장강도 행이 없다.** 전수 확인 — 기계축은 "
                 "`Peel strength 1 oz` 하나뿐이고 굽힘강도조차 없다. 밀도·열전도율·CTE 는 있다.")}
    if extra_attrs:
        attrs.update(extra_attrs)
    props = []
    for r in rows:
        props.extend(r)
    MATS.append({"new_material": {"name": name, "category": "composite", "description": desc,
                                  "attributes": attrs},
                 "source": src, "properties": props})


DENS_SPEC_NOTE = (
    " **71차 GD 의 인계가 이 칸을 잘못 읽었다** — GD 는 `2.05~2.15` 를 「인쇄된 구간」으로 넘겼으나 "
    "300 dpi 렌더로 확인하니 `2.1` 이 **Typical Values** 열이고 `2.05~2.15` 는 그 오른쪽 **SPEC** 열이다. "
    "SPEC 은 합격 한계이지 측정 구간이 아니므로 두 행으로 가르지 않고 notes 에만 남긴다."
)

for grade, name, desc_extra, local, issued, dk, df_5555, df_spdr, cte_z, cte_xy, peel, moist, tc, aliases in [
    ("NP-730", "Nan Ya NP-730 Ultra-Low-Loss RF Copper Clad Laminate",
     "안정한 유전율·초저손실(Df 0.0021 @10 GHz)·저PIM 을 내세운 기지국 안테나/5G 인프라용 동박적층판이다. "
     "밀도는 `ASTM D792` 로 재고 열전도율은 `ASTM F 433` 이다 — IPC 슬래시시트가 밀도를 규정하지 않는다는 "
     "71차 GD 의 판정과 앞뒤가 맞는다.",
     "Nanya_CCL_NP-730_Datasheet_cclqc_zhTWportal_2026-09-09.pdf", "2017/12/05",
     3.0, 0.0021, 0.0022, (70, 90), (20, 30), 10, 0.04, 0.6,
     ["NP-730", "NP730", "Nan Ya NP-730"]),
    ("NP-822", "Nan Ya NP-822 Extremely-Low-Loss RF Copper Clad Laminate",
     "극저손실(Df 0.0008 @10 GHz, Dk 2.20)을 내세운 군용 레이더 급전망·위상배열 안테나용 동박적층판이다. "
     "z축 CTE 가 357 ppm/degC 로 형제 등급보다 훨씬 크다(저Dk 수지계의 특징) — 원문 단일값이다.",
     "Nanya_CCL_NP-822_Datasheet_cclqc_zhTWportal_2026-09-09.pdf", "2019/09/05",
     2.20, 0.0008, 0.0009, 357, (20, 30), (10, 12), 0.02, 0.25,
     ["NP-822", "NP822", "Nan Ya NP-822"]),
    ("NP-826", "Nan Ya NP-826 Low-Loss RF Copper Clad Laminate",
     "Dk 2.60 · Df 0.0019 @10 GHz 의 LNB·전력증폭기·안테나용 동박적층판이다.",
     "Nanya_CCL_NP-826_Datasheet_cclqc_zhTWportal_2026-09-09.pdf", "2018 (문서에 발행일 표기 확인)",
     2.60, 0.0019, 0.0018, (185, 215), (20, 50), (11, 13), 0.03, 0.37,
     ["NP-826", "NP826", "Nan Ya NP-826"]),
]:
    rows = [
        one("physical.density", "kg/m^3", 2.1, gcm3,
            {"test_standard": "ASTM D792", "specimen": NANYA_SPECIMEN},
            "Density (Specific Gravity)  g/cm3  <Conditioning 빈칸>  2.1  2.05~2.15  ASTM D792", "g/cm^3",
            DENS_SPEC_NOTE + " " + NANYA_COL_NOTE),
        one("thermal.conductivity", "W/(m*K)", tc, lambda v: v,
            {"test_standard": "ASTM F433", "specimen": NANYA_SPECIMEN},
            f"Thermal Conductivity  W/mK  <Conditioning 빈칸>  {tc}  0.2 (SPEC)  ASTM F 433", "W/mK",
            " 원문 단위 `W/mK` = SI `W/(m*K)`, 환산 없음. " + NANYA_COL_NOTE),
        one("thermal.decomposition_temp", "K", 540, degc,
            {"test_standard": "ASTM D3850", "test_method": "TGA, 10 degC/min", "basis": "5% weight loss",
             "specimen": NANYA_SPECIMEN},
            "Td (5% weight loss)  degC  TGA, 10 degC/min  540  500 (SPEC)  ASTM D3850", "degC"),
        one("chemical.water_absorption_24h", "1", moist, pct,
            {"test_standard": "IPC-TM-650 2.6.2.1", "conditioning": "D-24/23", "specimen": NANYA_SPECIMEN},
            f"Moisture absorption  %  D-24/23  {moist}  0.15(down-arrow) (SPEC)  IPC-TM-650 2.6.2.1", "%"),
        one("electrical.dielectric_constant", "1", dk, lambda v: v,
            {"frequency_hz": 1e10, "temperature_c": 23, "test_standard": "IPC-TM-650 2.5.5.5",
             "test_method": "process", "specimen": NANYA_SPECIMEN},
            f"Permittivity (Process)  -  10GHz/23degC  {dk}  -  2.5.5.5", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", df_5555, lambda v: v,
            {"frequency_hz": 1e10, "temperature_c": 23, "test_standard": "IPC-TM-650 2.5.5.5",
             "specimen": NANYA_SPECIMEN},
            f"Loss Tangent  -  10GHz/23degC  {df_5555}  -  2.5.5.5", "-", " 무차원."),
        one("electrical.dissipation_factor", "1", df_spdr, lambda v: v,
            {"frequency_hz": 1e10, "temperature_c": 23, "test_method": "SPDR", "specimen": NANYA_SPECIMEN},
            f"Loss Tangent  -  10GHz/23degC  {df_spdr}  -  SPDR", "-",
            " 무차원. 같은 물성의 다른 측정법이므로 2.5.5.5 행과 두 행으로 갈랐다."),
        one("electrical.resistivity_volume", "ohm*m", 1e9, mohmcm,
            {"conditioning": "C-96/35/90", "test_standard": "IPC-TM-650 2.5.17", "specimen": NANYA_SPECIMEN},
            "Volume resistivity  MOhm-cm  C-96/35/90  10^9  10^6(up-arrow) (SPEC)  IPC-TM-650 2.5.17", "MOhm*cm",
            " 지수표기는 렌더로 확인했다(10 의 9승)."),
        one("electrical.surface_resistivity", "ohm", 1e8, mohm,
            {"conditioning": "C-96/35/90", "test_standard": "IPC-TM-650 2.5.17", "specimen": NANYA_SPECIMEN},
            "Surface resistivity  MOhm  C-96/35/90  10^8  10^4(up-arrow) (SPEC)  IPC-TM-650 2.5.17", "MOhm",
            " 지수표기는 렌더로 확인했다(10 의 8승)."),
    ]
    tr = "25 - 260" if grade == "NP-730" else "50 - 260"
    if isinstance(cte_z, tuple):
        rows.append(rng_rows("thermal.expansion_linear", "1/K", cte_z[0], cte_z[1], ppmk,
                             {"axis": "z", "temperature_range_c": tr, "test_method": "TMA",
                              "test_standard": "IPC-TM-650 2.4.24", "specimen": NANYA_SPECIMEN},
                             f"CTE (z) ({tr}degC)  ppm/degC  TMA  {cte_z[0]}-{cte_z[1]}  N/A  IPC-TM-650 2.4.24", "ppm/degC"))
    else:
        rows.append(one("thermal.expansion_linear", "1/K", cte_z, ppmk,
                        {"axis": "z", "temperature_range_c": tr, "test_method": "TMA",
                         "test_standard": "IPC-TM-650 2.4.24", "specimen": NANYA_SPECIMEN},
                        f"CTE (z) ({tr}degC)  ppm/degC  TMA  {cte_z}  N/A  IPC-TM-650 2.4.24", "ppm/degC"))
    rows.append(rng_rows("thermal.expansion_linear", "1/K", cte_xy[0], cte_xy[1], ppmk,
                         {"axis": "x/y", "temperature_range_c": tr, "test_method": "TMA",
                          "test_standard": "IPC-TM-650 2.4.24", "specimen": NANYA_SPECIMEN},
                         f"CTE (x,y) ({tr}degC)  ppm/degC  TMA  {cte_xy[0]}-{cte_xy[1]}  N/A  IPC-TM-650 2.4.24", "ppm/degC"))
    if isinstance(peel, tuple):
        rows.append(rng_rows("interface.peel_strength", "N/m", peel[0], peel[1], lbin,
                             {"conditioning": "288 degC x 10 s solder floating", "copper_foil_type": "1 oz",
                              "test_standard": "IPC-TM-650 2.4.8", "specimen": NANYA_SPECIMEN},
                             f"Peel strength 1 oz  lb/in  288degCx10\" solder floating  {peel[0]}-{peel[1]}  6(up-arrow) (SPEC)  IPC-TM-650 2.4.8",
                             "lb/in"))
    else:
        rows.append(one("interface.peel_strength", "N/m", peel, lbin,
                        {"conditioning": "288 degC x 10 s solder floating", "copper_foil_type": "1 oz",
                         "test_standard": "IPC-TM-650 2.4.8", "specimen": NANYA_SPECIMEN},
                        f"Peel strength 1 oz  lb/in  288degCx10\" solder floating  {peel}  6(up-arrow) (SPEC)  IPC-TM-650 2.4.8",
                        "lb/in"))
    nanya_ccl(name,
              f"南亞(Nan Ya) `{grade}` 동박적층판. {desc_extra} "
              "밀도(2.1 g/cm3, ASTM D792)·열전도율·CTE(z, x/y)·Td 를 찍지만 "
              "**영률·포아송비·비열·인장강도 행은 없다**.",
              aliases, grade, local, issued, rows)

# ================================================================================
# C. Shengyi SCGA-500 GF255 — 이름은 인장인데 인용 시험법은 굽힘법이다
# ================================================================================
SCGA_SPEC = "0.76 mm (0.030 in) (원문 Notes: All the typical value is based on the 0.76mm (0.030\") specimen)"
SCGA_CONFLICT = (
    "값 자체는 이 등급의 이 칸에 인쇄된 것이고 등급 범위 문제는 없다. t3 로 내린 이유는 "
    "**행 이름과 인용 시험법이 서로 어긋나기 때문**이다 — 행 이름은 `Tensile Modulus(LW/CW)` / "
    "`Tensile Strength(LW/CW)`(인장)인데 `Test Method` 칸은 `IPC-TM-650 2.4.4` 다. "
    "IPC-TM-650 2.4.4 는 적층판 **굽힘강도(Flexural Strength of Laminates)** 시험법이다 — "
    "같은 코퍼스의 Technolam/Nan Ya Datenblatt 가 `8. Flexural Strength / Biegefestigkeit` 행에 "
    "정확히 `2.4.4` 를 붙여 이것을 독립으로 확인해 준다. 브리프의 지침(이름이 아니라 시험규격을 봐라)에 따르면 "
    "굽힘이고, 행 이름에 따르면 인장이다. **어느 쪽도 혼자 이기지 못하므로 값은 행 이름이 말하는 물성 키에 넣되 "
    "등급을 t3 로 내리고 충돌 사실을 지우지 않고 남긴다.** 71차 GD 가 Resonac 각주 충돌을 처리한 방식과 같다."
)
MATS.append({
    "new_material": {
        "name": "Shengyi SCGA-500 GF255 Glass-Reinforced PTFE RF Laminate",
        "category": "composite",
        "description": "生益(Shengyi) `SCGA-500 GF255` — 유리섬유 강화 PTFE RF 회로재(Dk 2.55 ± 0.04 @10 GHz). "
                       "기지국 안테나·위성통신·필터/커플러/LNA/전력증폭기용. 이 시트가 드문 것은 "
                       "**밀도(2.25 g/cm3, ASTM D792)와 함께 탄성률·강도까지 LW/CW 로 갈라 찍는다**는 점이다. "
                       "다만 그 두 행은 이름이 `Tensile`인데 인용 시험법이 IPC-TM-650 2.4.4(굽힘법)라 "
                       "서로 어긋난다 — 두 행은 t3 이고 사유는 각 행 `grade_scope` 에 있다. "
                       "CTE 는 X/Y/Z 세 축(8.2 / 7.9 / 145 ppm/degC)을 한 칸에 슬래시로 찍는다.",
        "attributes": {
            "material_class": "woven-glass reinforced PTFE copper clad laminate",
            "subsystem": "pcb", "role": "product",
            "role_reason": "제조사(Shengyi)+등급명이 이름에 박혀 있고 출처가 해당 등급의 공식 TDS(CN-TDS-1810-03)다.",
            "role_confidence": "high",
            "manufacturer": "Shengyi Technology Co., Ltd.",
            "grades_covered": ["SCGA-500 GF255"],
            "aliases": ["SCGA-500 GF255", "SCGA-500", "SCGA500 GF255", "SCGA500", "SCGA-500GF255"],
            "document_code": "CN-TDS-1810-03-SCGA-500 GF255",
            "core7_absent_from_vendor_sheet": "포아송비 행이 없다(`Poisson` 전수 적중 0). 비열 행도 없다.",
            "name_method_conflict": SCGA_CONFLICT,
        }},
    "source": {"kind": "datasheet",
               "title": "Shengyi SCGA-500 GF255 — PTFE with Glass Reinforced RF Circuit Material, "
                        "GENERAL PROPERTIES (doc. CN-TDS-1810-03)",
               "url": None, "publisher": "Shengyi Technology Co., Ltd.", "year": 2019,
               "local_path": CORPUS + "Shengyi_SCGA-500_GF255_TDS_zh_2019.pdf",
               "url_note": "PDF 안에 절대 URL 이 없다 — 지어내지 않았다. 문서코드 CN-TDS-1810-03 가 식별자다."},
    "properties": (
        one("physical.density", "kg/m^3", 2.25, gcm3, {"test_standard": "ASTM D792", "specimen": SCGA_SPEC},
            "Density  ASTM D792  -  g/cm3  2.25", "g/cm^3",
            " 시험조건 칸은 `-` 다. 350 dpi 렌더로 행 정렬을 확인했다.")
        + one("mechanical.youngs_modulus", "Pa", 1.2, gpa,
              {"direction": "warp", "direction_verbatim": "LW (length-wise)",
               "test_standard": "IPC-TM-650 2.4.4", "test_mode": "conflict (row name vs cited method)",
               "specimen": SCGA_SPEC, "conditioning": "A", "grade_scope": SCGA_CONFLICT},
              "Tensile Modulus(LW/CW)  IPC-TM-650 2.4.4  A  GPa  1.2/7.8", "GPa",
              " 슬래시 왼쪽이 LW, 오른쪽이 CW 다(행 이름 `(LW/CW)` 가 순서를 밝힌다). "
              "**LW 1.2 GPa 가 CW 7.8 GPa 보다 6.5 배 낮다** — 균형직물이라면 드문 비대칭이다. "
              "값을 고치지 않고 원문 그대로 옮기고 이 사실을 여기에 남긴다.", tier=3)
        + one("mechanical.youngs_modulus", "Pa", 7.8, gpa,
              {"direction": "fill", "direction_verbatim": "CW (cross-wise)",
               "test_standard": "IPC-TM-650 2.4.4", "test_mode": "conflict (row name vs cited method)",
               "specimen": SCGA_SPEC, "conditioning": "A", "grade_scope": SCGA_CONFLICT},
              "Tensile Modulus(LW/CW)  IPC-TM-650 2.4.4  A  GPa  1.2/7.8", "GPa", "", tier=3)
        + one("mechanical.tensile_strength", "Pa", 64, mpa,
              {"direction": "warp", "direction_verbatim": "LW (length-wise)",
               "test_standard": "IPC-TM-650 2.4.4", "test_mode": "conflict (row name vs cited method)",
               "specimen": SCGA_SPEC, "conditioning": "A", "grade_scope": SCGA_CONFLICT},
              "Tensile Strength(LW/CW)  IPC-TM-650 2.4.4  A  MPa  64/214", "MPa", "", tier=3)
        + one("mechanical.tensile_strength", "Pa", 214, mpa,
              {"direction": "fill", "direction_verbatim": "CW (cross-wise)",
               "test_standard": "IPC-TM-650 2.4.4", "test_mode": "conflict (row name vs cited method)",
               "specimen": SCGA_SPEC, "conditioning": "A", "grade_scope": SCGA_CONFLICT},
              "Tensile Strength(LW/CW)  IPC-TM-650 2.4.4  A  MPa  64/214", "MPa", "", tier=3)
        + one("thermal.conductivity", "W/(m*K)", 0.29, lambda v: v,
              {"test_standard": "ASTM C518", "temperature_c": 100, "specimen": SCGA_SPEC},
              "Thermal Conductivity  ASTM C518  100degC  W/(m.K)  0.29", "W/(m*K)", " 환산 없음.")
        + one("thermal.expansion_linear", "1/K", 8.2, ppmk,
              {"axis": "x", "temperature_range_c": "30-260", "test_standard": "IPC-TM-650 2.4.24",
               "specimen": SCGA_SPEC},
              "CTE (X/Y/Z-axis)  IPC-TM-650 2.4.24  30-260degC  ppm/degC  8.2/7.9/145", "ppm/degC",
              " 한 칸에 X/Y/Z 를 슬래시로 붙여 찍으므로 축마다 세 행으로 갈랐다.")
        + one("thermal.expansion_linear", "1/K", 7.9, ppmk,
              {"axis": "y", "temperature_range_c": "30-260", "test_standard": "IPC-TM-650 2.4.24",
               "specimen": SCGA_SPEC},
              "CTE (X/Y/Z-axis)  ...  8.2/7.9/145", "ppm/degC", "")
        + one("thermal.expansion_linear", "1/K", 145, ppmk,
              {"axis": "z", "temperature_range_c": "30-260", "test_standard": "IPC-TM-650 2.4.24",
               "specimen": SCGA_SPEC},
              "CTE (X/Y/Z-axis)  ...  8.2/7.9/145", "ppm/degC", "")
        + [prop("electrical.dielectric_constant", 2.55, "1", cond={
            "frequency_hz": 1e10, "temperature_c": 23, "test_standard": "IPC-TM-650 2.5.5.5",
            "test_method": "process Dk", "specimen": SCGA_SPEC},
            notes="원문 verbatim: `Dielectric Constant, Process Dk  IPC-TM-650 2.5.5.5  10GHz/23degC  -  2.55+/-0.04`. "
                  "무차원. 원문이 `+/-0.04` 를 붙이므로 uncertainty 로 남겼다(구간이 아니라 공차다).")]
        + one("electrical.dissipation_factor", "1", 0.0014, lambda v: v,
              {"frequency_hz": 1e10, "temperature_c": 23, "test_standard": "IPC-TM-650 2.5.5.5",
               "specimen": SCGA_SPEC},
              "Loss Tangent  IPC-TM-650 2.5.5.5  10GHz/23degC  -  0.0014", "-", " 무차원.")
        + one("electrical.resistivity_volume", "ohm*m", 1.5e8, mohmcm,
              {"conditioning": "A", "test_standard": "IPC-TM-650 2.5.17.1", "specimen": SCGA_SPEC},
              "Volume Resistivity  IPC-TM-650 2.5.17.1  A  MOhm-cm  1.5X10^8", "MOhm*cm")
        + one("electrical.surface_resistivity", "ohm", 1.6e8, mohm,
              {"conditioning": "A", "test_standard": "IPC-TM-650 2.5.17.1", "specimen": SCGA_SPEC},
              "Surface Resistivity  IPC-TM-650 2.5.17.1  A  MOhm  1.6X10^8", "MOhm")
        + one("interface.peel_strength", "N/m", 1.2, nmm,
              {"conditioning": "288 degC / 10 s", "test_standard": "IPC-TM-650 2.4.8", "specimen": SCGA_SPEC},
              "Peel Strength  IPC-TM-650 2.4.8  288degC/10s  N/mm [lb/in]  1.2 [6.86]", "N/mm",
              " 원문이 괄호로 병기한 6.86 lb/in 로 검산 — 6.86 x 175.126835 = 1201.4 N/m, 두 표기가 서로 맞는다.")
        + one("chemical.water_absorption_24h", "1", 0.007, pct,
              {"conditioning": "D-24/23", "test_standard": "IPC-TM-650 2.6.2.1", "specimen": SCGA_SPEC},
              "Water Absorption  IPC-TM-650 2.6.2.1  D-24/23  %  0.007", "%")
    )})
MATS[-1]["properties"] = [
    (dict(p, uncertainty=0.04) if p["key"] == "electrical.dielectric_constant" else p)
    for p in MATS[-1]["properties"]]

# ================================================================================
# D. Rogers RO3000 Series — 여기서는 시험규격이 ASTM D638(인장)이라 영률이 t1 이다
# ================================================================================
RO_COL_NOTE = (
    "**열 확인** — 이 표의 등급 열 순서는 인쇄면 기준 `RO3003 | RO3035 | RO3006 | RO3010` 이고 "
    "**파일 이름의 순서(RO3003_RO3006_RO3010_RO3035)와 다르다**. 300 dpi 렌더로 확정했다. "
    "형제 등급 RO3003 은 이 카탈로그에 이미 재료 241 로 있으므로 이 배치는 담지 않았다."
)
RO_YM_NOTE = (
    "원문 `Young's Modulus` 행은 등급 열마다 값 두 개를 위/아래로 쌓고 **그 행에는 방향 표기가 없다**. "
    "같은 표의 `Dimensional Stability (MD, CMD)` 행이 똑같은 2단 배치를 쓰면서 순서를 `(MD, CMD)` 로 밝히고, "
    "바로 위 CTE 행들은 `- x`, `- y`, `- z` 순으로 인쇄된다. 같은 제조사의 형제 시트 "
    "(RO4003C/RO4350B · RT/duroid 5870-5880)는 `Tensile Modulus` 를 `X`(위) / `Y`(아래) 로 명시한다. "
    "그래서 위=x(MD)·아래=y(CMD) 로 읽었고 그 근거를 여기에 남긴다 — **값 자체는 두 개 다 담았으므로 "
    "방향 배정이 뒤집혀도 잃는 값은 없다.** 시험법이 `ASTM D638`(인장)이라 이 행은 굽힘이 아니라 인장이다."
)
for grade, dk_p, dk_d, df, vr, sr, cte_x, cte_y, cte_z, tc, peel, ym_x, ym_y, moist, dens, cp, desc in [
    ("RO3035", 3.50, 3.60, 0.0015, 1e7, 1e7, 17, 17, 24, 0.50, 10.2, 1025, 1006, 0.04, 2.1, None,
     "Dk 3.50 ± 0.05 급 세라믹 충전 PTFE 고주파 적층판. 비열 칸이 이 등급만 **비어 있다**(형제 셋은 값이 있다)."),
    ("RO3006", 6.15, 6.50, 0.0020, 1e5, 1e5, 17, 17, 24, 0.79, 7.1, 1498, 1293, 0.02, 2.6, 0.86,
     "Dk 6.15 ± 0.15 급 세라믹 충전 PTFE 고주파 적층판."),
    ("RO3010", 10.2, 11.20, 0.0022, 1e5, 1e5, 13, 11, 16, 0.95, 9.4, 1902, 1934, 0.05, 2.8, 0.8,
     "Dk 10.2 ± 0.30 급 세라믹 충전 PTFE 고주파 적층판. 이 등급만 영률의 아래 값(1934 MPa)이 위 값(1902 MPa)보다 크다."),
]:
    props = (
        one("physical.density", "kg/m^3", dens, gcm3, {"test_standard": "ASTM D792", "temperature_c": 23},
            f"Density  {dens}  g/cm3  23degC  ASTM D792", "g/cm^3", " " + RO_COL_NOTE)
        + one("mechanical.youngs_modulus", "Pa", ym_x, mpa,
              {"direction": "x", "direction_verbatim": "(행에 방향 표기 없음 — 2단 중 위 칸)",
               "temperature_c": 23, "test_standard": "ASTM D638"},
              f"Young's Modulus  {ym_x} / {ym_y}  MPa  23degC  ASTM D638", "MPa", " " + RO_YM_NOTE)
        + one("mechanical.youngs_modulus", "Pa", ym_y, mpa,
              {"direction": "y", "direction_verbatim": "(행에 방향 표기 없음 — 2단 중 아래 칸)",
               "temperature_c": 23, "test_standard": "ASTM D638"},
              f"Young's Modulus  {ym_x} / {ym_y}  MPa  23degC  ASTM D638", "MPa", " " + RO_YM_NOTE)
        + one("thermal.conductivity", "W/(m*K)", tc, lambda v: v,
              {"test_standard": "ASTM D5470", "temperature_c": 50},
              f"Thermal Conductivity  {tc}  W/(m.K)  50degC  ASTM D5470", "W/(m*K)", " 환산 없음.")
        + one("thermal.expansion_linear", "1/K", cte_x, ppmk,
              {"axis": "x", "temperature_range_c": "-55 to 288", "conditioning": "23degC / 50% RH",
               "test_standard": "IPC-TM-650 2.4.41"},
              f"Coefficient of Thermal Expansion - x  {cte_x}  ppm/degC  -55 to 288degC, 23degC/50% RH  IPC TM-650 2.4.41",
              "ppm/degC")
        + one("thermal.expansion_linear", "1/K", cte_y, ppmk,
              {"axis": "y", "temperature_range_c": "-55 to 288", "conditioning": "23degC / 50% RH",
               "test_standard": "IPC-TM-650 2.4.41"},
              f"Coefficient of Thermal Expansion - y  {cte_y}  ppm/degC  IPC TM-650 2.4.41", "ppm/degC")
        + one("thermal.expansion_linear", "1/K", cte_z, ppmk,
              {"axis": "z", "temperature_range_c": "-55 to 288", "conditioning": "23degC / 50% RH",
               "test_standard": "IPC-TM-650 2.4.41"},
              f"Coefficient of Thermal Expansion - z  {cte_z}  ppm/degC  IPC TM-650 2.4.41", "ppm/degC")
        + one("thermal.decomposition_temp", "K", 500, degc, {"test_standard": "ASTM D3850", "test_method": "TGA"},
              "Decomposition Temperature (Td)  500  degC TGA  ASTM D3850", "degC")
        + one("electrical.dielectric_constant", "1", dk_p, lambda v: v,
              {"frequency_hz": 1e10, "temperature_c": 23, "test_standard": "IPC-TM-650 2.5.5.5",
               "test_method": "process"},
              f"Dielectric Constant (process)  {dk_p}  -  23degC, 10 GHz  IPC TM-650 2.5.5.5", "-", " 무차원.")
        + one("electrical.dielectric_constant", "1", dk_d, lambda v: v,
              {"frequency_range_hz": "8e9-40e9", "test_method": "differential phase length (design Dk)"},
              f"Dielectric Constant (design)  {dk_d}  -  8 GHz - 40 GHz  Differential Phase Length", "-",
              " 무차원. 제조사 각주 verbatim: `The design Dk is an average number from several different tested lots "
              "of material and on the most common thickness/s.`")
        + one("electrical.dissipation_factor", "1", df, lambda v: v,
              {"frequency_hz": 1e10, "temperature_c": 23, "test_standard": "IPC-TM-650 2.5.5.5"},
              f"Dissapation Factor  {df}  -  23degC, 10 GHz  IPC TM-650 2.5.5.5", "-", " 무차원(원문 철자 그대로).")
        + one("electrical.resistivity_volume", "ohm*m", vr, mohmcm,
              {"conditioning": "Condition A", "test_standard": "IPC-TM-650 2.5.17.1"},
              f"Volume Resistivity  10^{int(round(__import__('math').log10(vr)))}  MOhm-cm  Condition A  IPC TM-650 2.5.17.1",
              "MOhm*cm")
        + one("electrical.surface_resistivity", "ohm", sr, mohm,
              {"conditioning": "Condition A", "test_standard": "IPC-TM-650 2.5.17.1"},
              f"Surface Resistivity  10^{int(round(__import__('math').log10(sr)))}  MOhm  Condition A  IPC TM-650 2.5.17.1",
              "MOhm")
        + one("interface.peel_strength", "N/m", peel, lbin,
              {"conditioning": "after solder float", "copper_foil_type": "1 oz. EDC",
               "test_standard": "IPC-TM-650 2.4.8"},
              f"Copper Peel Strength  {peel}  lbs/in  1 oz. EDC After Solder Float  IPC TM-650 2.4.8", "lb/in")
        + one("chemical.water_absorption_24h", "1", moist, pct,
              {"conditioning": "D48/50", "test_standard": "IPC-TM-650 2.6.2.1"},
              f"Moisture Absorption  {moist}  %  D48/50  IPC TM-650 2.6.2.1", "%")
    )
    if cp is not None:
        props = props + one("thermal.specific_heat", "J/(kg*K)", cp, jgk,
                            {"test_method": "vendor-calculated (Test Method 칸 verbatim = `Calculated`)"},
                            f"Specifc Heat Capacity  {cp}  J/g/K  -  Calculated", "J/(g*K)",
                            " 원문 시험법 칸이 `Calculated` 다 — 벤더가 계산해 인쇄한 값이고 이 배치가 계산한 것이 아니다. "
                            "**RO3035 칸은 비어 있다**(300 dpi 렌더로 확인) — 텍스트 추출만 보면 0.86/0.8 이 한 칸씩 "
                            "왼쪽으로 밀려 RO3035/RO3006 에 붙을 수 있는 자리다. 그래서 RO3035 카드에는 비열 행이 없다.")
    MATS.append({
        "new_material": {
            "name": f"Rogers {grade} Ceramic-Filled PTFE Laminate",
            "category": "composite",
            "description": f"Rogers RO3000 시리즈 `{grade}` — 세라믹 충전 PTFE 고주파 적층판. {desc} "
                           "이 시트가 이번 배치에서 특별한 이유는 **`Young's Modulus` 행의 시험법이 `ASTM D638`(인장)로 "
                           "명시돼 있다**는 것 — 같은 배치의 Technolam(시험법 `-`)·Shengyi(이름은 인장, 시험법은 굽힘법) "
                           "와 달리 여기서는 인장이 확정되므로 영률이 t1 이다. "
                           "밀도(ASTM D792)·비열·CTE(x/y/z)·열전도율까지 코어7 중 다섯을 찍고 포아송비만 없다.",
            "attributes": {
                "material_class": "ceramic-filled PTFE laminate",
                "subsystem": "rf", "role": "product",
                "role_reason": "제조사(Rogers)+등급명이 이름에 박혀 있고 출처가 해당 시리즈의 공식 데이터시트다.",
                "role_confidence": "high",
                "manufacturer": "Rogers Corporation",
                "product_series": "RO3000",
                "grades_covered": [grade],
                "aliases": [grade, grade.replace("RO", "RO "), f"Rogers {grade}", f"{grade}TM"],
                "column_layout": RO_COL_NOTE,
                "core7_absent_from_vendor_sheet": {
                    "mechanical.poisson_ratio": "RO3000 시리즈 표준물성표에 포아송비 행이 없다(`Poisson` 전수 적중 0). "
                                                "57차 SB 가 Rogers 네 시트에서 같은 부재를 확인한 바 있다.",
                    "mechanical.tensile_strength": "이 표는 `Young's Modulus` 는 찍지만 인장강도 행이 없다. "
                                                   "형제 시트(RO4003C/RO4350B · RT/duroid)에는 `Tensile Strength` 가 있으나 "
                                                   "그 값은 이 등급의 값이 아니므로 가져오지 않았다.",
                },
            }},
        "source": {"kind": "datasheet",
                   "title": "RO3000 Series Circuit Materials Data Sheet — RO3003, RO3006, RO3010 and RO3035 "
                            "High Frequency Laminates (Standard Properties Table)",
                   "url": "https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/ro3000-laminate-data-sheet-ro3003----ro3006----ro3010----ro3035.pdf",
                   "publisher": "Rogers Corporation", "year": 2024,
                   "local_path": CORPUS + "Rogers_RO3000_Laminate_DataSheet_RO3003_RO3006_RO3010_RO3035_2024-01.pdf",
                   "url_note": "URL 은 이 카탈로그의 기존 출처(source 3019)에 이미 등록된 것을 그대로 썼다 — 새로 지어내지 않았다."},
        "properties": props,
    })

# ================================================================================
# 자체검증
# ================================================================================
UNIT_OF = {
    "physical.density": "kg/m^3", "mechanical.youngs_modulus": "Pa",
    "mechanical.poisson_ratio": "1", "mechanical.tensile_strength": "Pa",
    "mechanical.flexural_strength": "Pa", "thermal.conductivity": "W/(m*K)",
    "thermal.specific_heat": "J/(kg*K)", "thermal.expansion_linear": "1/K",
    "thermal.expansion_total": "1", "thermal.glass_transition": "K",
    "thermal.decomposition_temp": "K", "thermal.heat_of_combustion": "J/kg",
    "thermal.time_to_delamination": "s", "electrical.dielectric_constant": "1",
    "electrical.dissipation_factor": "1", "electrical.resistivity_volume": "ohm*m",
    "electrical.surface_resistivity": "ohm", "electrical.arc_resistance": "s",
    "electrical.dielectric_strength": "V/m", "electrical.comparative_tracking_index": "V",
    "interface.peel_strength": "N/m", "chemical.water_absorption_24h": "1",
}
METHODS = {"measured", "handbook", "datasheet", "computed", "estimated", "digitized"}

errs, names = [], set()
for m in MATS:
    nm = m["new_material"]["name"]
    a = m["new_material"]["attributes"]
    if len(nm) > 200:
        errs.append(f"이름 200자 초과({len(nm)}): {nm}")
    if nm in names:
        errs.append(f"이름 중복: {nm}")
    names.add(nm)
    if not a.get("role"):
        errs.append(f"role 없음: {nm}")
    if not a.get("aliases"):
        errs.append(f"aliases 없음: {nm}")
    if not m["source"].get("local_path"):
        errs.append(f"local_path 없음: {nm}")
    for p in m["properties"]:
        if p["key"] not in UNIT_OF:
            errs.append(f"미등록 키: {nm} {p['key']}")
        elif p["unit"] != UNIT_OF[p["key"]]:
            errs.append(f"단위 불일치: {nm} {p['key']} {p['unit']} != {UNIT_OF[p['key']]}")
        if p["method"] not in METHODS:
            errs.append(f"method 어휘 위반: {nm} {p['key']} {p['method']}")
        if p["tier"] == 4:
            errs.append(f"t4 금지: {nm} {p['key']}")
        if p["tier"] == 3 and not p.get("conditions", {}).get("grade_scope"):
            errs.append(f"t3 인데 grade_scope 없음: {nm} {p['key']}")
        if not p.get("notes"):
            errs.append(f"notes 없음: {nm} {p['key']}")
        if p["value"] is None:
            errs.append(f"값 없음: {nm} {p['key']}")

import collections
tc_ = collections.Counter(p["tier"] for m in MATS for p in m["properties"])
kc_ = collections.Counter(p["key"] for m in MATS for p in m["properties"])
n_props = sum(len(m["properties"]) for m in MATS)

print(f"재료 {len(MATS)}장 · 물성 {n_props}행")
print("등급 분포:", dict(sorted(tc_.items())))
print("자체검증 오류:", len(errs))
for e in errs[:40]:
    print("   !", e)
print()
for m in MATS:
    core = collections.Counter(p["key"] for p in m["properties"])
    have = [k for k in ("physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
                        "thermal.expansion_linear", "thermal.conductivity", "thermal.specific_heat",
                        "mechanical.tensile_strength") if core.get(k)]
    print(f"  {len(m['properties']):3d}행  코어7 {len(have)}/7  {m['new_material']['name']}")

if not errs:
    groups = [("hc72_01_technolam_nanya.json", MATS[0:5]),
              ("hc72_02_nanya_ccl_rf.json", MATS[5:8]),
              ("hc72_03_shengyi_scga500.json", MATS[8:9]),
              ("hc72_04_rogers_ro3000.json", MATS[9:12])]
    for fn, ms in groups:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            json.dump({"batch": "72차 HC", "materials": ms}, f, ensure_ascii=False, indent=1)
        print(f"wrote {fn}: 재료 {len(ms)} · 물성 {sum(len(x['properties']) for x in ms)}")
