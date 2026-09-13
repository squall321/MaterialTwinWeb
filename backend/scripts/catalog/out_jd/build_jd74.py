#!/usr/bin/env python3
# 74차 JD 산출 JSON 생성기 — RF 라미네이트 벤더군(Rogers·Taconic/AGC·Chukoh·Arisawa·Isola).
# 원문 표의 숫자가 리터럴로 박혀 있고, 단위 환산은 여기서만 한다(역산 없음).
from __future__ import annotations
import json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
BATCH = "74차 JD"
KSI = 6.894757e6          # ksi -> Pa
MPA = 1.0e6               # MPa -> Pa
KNM = 1000.0              # kN/m -> N/m
NMM = 1000.0              # N/mm -> N/m
OHMCM_TO_OHMM = 0.01      # Ω·cm -> Ω·m


def P(key, value, unit, tier, method, conditions, notes, value_text=None):
    d = {"key": key, "value": value, "unit": unit, "method": method,
         "quality_tier": tier, "conditions": conditions, "notes": notes}
    if value_text is not None:
        d["value_text"] = value_text
        d["value"] = None
    return d


# ── 출처 ──────────────────────────────────────────────────────────────────────
S = {
 "370hr": {"kind": "datasheet", "url": "https://www.isola-group.com/wp-content/uploads/data-sheets/370hr.pdf",
   "title": "370HR Industry Leading, Standard Loss, Thermally Robust Epoxy Laminate and Prepreg (Rev C, 2021-04-15)",
   "publisher": "Isola", "year": 2021,
   "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Isola_370HR_Laminate_Prepreg_DataSheet_RevC_2021-04-15.pdf"},
 "is400": {"kind": "datasheet", "url": "https://www.isola-group.com/wp-content/uploads/data-sheets/is400.pdf",
   "title": "IS400 Lead Free, Mid Tg Epoxy Laminate and Prepreg (Rev C, 2021-04-15)",
   "publisher": "Isola", "year": 2021,
   "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Isola_IS400_Laminate_Prepreg_DataSheet_RevC_2021-04-15.pdf"},
 "itera": {"kind": "datasheet", "url": "https://www.isola-group.com/wp-content/uploads/data-sheets/i-tera-mt40.pdf",
   "title": "I-Tera MT40 Laminate and Prepreg (Rev F, 2025-12-08)", "publisher": "Isola", "year": 2025,
   "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Isola_I-Tera_MT40_Laminate_Prepreg_DataSheet_RevF_2025-12-08.pdf"},
 "astra": {"kind": "datasheet", "url": "https://www.isola-group.com/wp-content/uploads/data-sheets/astra-mt77.pdf",
   "title": "Astra MT77 Laminate and Prepreg (Rev D, 2021-04-20)", "publisher": "Isola", "year": 2021,
   "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Isola_Astra_MT77_Laminate_Prepreg_DataSheet_RevD_2021-04-20.pdf"},
 "clte": {"kind": "datasheet",
   "url": "https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/clte-and-clte-xt-laminates-data-sheet.pdf",
   "title": "CLTE and CLTE-XT Series Laminates Data Sheet", "publisher": "Rogers Corporation", "year": 2024,
   "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Rogers_CLTE_CLTE-XT_Laminates_DataSheet.pdf"},
 "clteat": {"kind": "datasheet",
   "url": "https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/clte-at-laminates-data-sheet.pdf",
   "title": "CLTE-AT Series Laminates Data Sheet", "publisher": "Rogers Corporation",
   "local_path": "/data/paper_patent_corpus/standards_appnotes/poly/Rogers_CLTE-AT_Series_Laminates_DataSheet.pdf"},
 "ro3000": {"kind": "datasheet",
   "url": "https://www.rogerscorp.com/-/media/project/rogerscorp/documents/advanced-electronics-solutions/english/data-sheets/ro3000-laminate-data-sheet-ro3003----ro3006----ro3010----ro3035.pdf",
   "title": "RO3000 Series Circuit Materials Data Sheet (RO3003, RO3006, RO3010, RO3035)",
   "publisher": "Rogers Corporation", "year": 2024,
   "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Rogers_RO3000_Laminate_DataSheet_RO3003_RO3006_RO3010_RO3035_2024-01.pdf"},
 "tsmds3": {"kind": "datasheet", "url": "https://www.agc-multimaterial.com/agc-downloads/AGC_TSM-DS3_TDS.pdf",
   "title": "AGC TSM-DS3 Dimensionally Stable Low Loss Laminate TDS"},
 "tly5": {"kind": "datasheet", "url": "https://www.agc-multimaterial.com/agc-downloads/AGC_TLY-5_TDS.pdf",
   "title": "TLY-5 Avionics & aerospace grade very low DK base material, Technical Data Sheet (2024-03)",
   "publisher": "AGC Inc. (Taconic / AGC Multi Material)"},
 "tlx8": {"kind": "datasheet", "url": "https://www.agc-multimaterial.com/agc-downloads/AGC_TLX-8_TDS.pdf",
   "title": "TLX-8 Technical Data Sheet (AGC Multi Material)", "publisher": "AGC Multi Material (Taconic)"},
 "chukoh": {"kind": "datasheet", "url": "https://www.chukoh.co.jp/wp-content/uploads/catalog05_lami_ja-1.pdf",
   "title": "CHUKOH FLO 銅張積層板 製品カタログ (catalog05_lami_ja)",
   "publisher": "Chukoh Chemical Industries, Ltd."},
 "jacob09": {"kind": "journal",
   "url": "https://researchonline.jcu.edu.au/6789/",
   "title": "Mohan V. Jacob, 'Low Loss Dielectric Materials for High Frequency Applications' — Table 1, complex permittivity of RO3035 / TLY-5-0100 / RF35-0200 by Split Post Dielectric Resonator at ~10 GHz, 25 K and 290 K",
   "authors": "Mohan V. Jacob", "year": 2009,
   "local_path": "/data/paper_patent_corpus/structured/elec_papers/pcb_05_transmission_loss_pcb/JACOB - 2009 - LOW LOSS DIELECTRIC MATERIALS FOR HIGH FREQUENCY APPLICATIONS/tables/table-1.md"},
}

N = "[74차 JD] "

# ── 1. Isola ─────────────────────────────────────────────────────────────────
ARC_NOTE = ("Isola 'Typical Values Table' 의 `Arc Resistance` 행 그대로. "
            "시험법 칸 verbatim = IPC-TM-650 2.5.1B. 초 단위 인쇄값이라 환산 없음.")
FLEX_NOTE = ("Isola 가 `Young's Modulus` 로 인쇄한 행인데 **시험법 칸이 `ASTM D790-15e2`(3점 굽힘)** 이다"
             "(71차 GB·72차 HB 가 같은 무늬를 확인했다). 같은 출처·같은 수를 **굽힘 키에도 세운다** — "
             "73차 IA 가 EMC 에서 한 것과 같은 처리다. **영률 칸의 원행은 지우지 않았다**(삭제는 사람이 정한다). "
             "ksi → Pa 는 ×6.894757e6.")

isola = {"batch": BATCH,
 "note": ("Isola 네 등급(370HR·IS400·I-Tera MT40·Astra MT77)의 데이터시트를 로컬 원본으로 다시 열어 "
          "**아크저항 4행**과 **370HR·IS400 의 굽힘탄성률 4행**을 세운다. "
          "굽힘탄성률은 새로 캔 수가 아니라 **영률 칸에 앉은 D790 값을 올바른 키에 한 벌 더 놓는 것**이다. "
          "`Comparative Tracking Index` 는 넣지 않았다 — 인쇄된 것은 **등급(Class 3)** 이고 "
          "괄호의 175–249 V 는 그 등급의 정의 구간이지 이 재료의 측정값이 아니다."),
 "materials": [
  {"match_name": "Isola 370HR High-Tg Laminate", "source": S["370hr"], "properties": [
     P("electrical.arc_resistance", 115.0, "s", 1, "measured",
       {"test_standard": "IPC-TM-650 2.5.1B", "test_method": "arc resistance (IPC-TM-650 2.5.1B)",
        "grade": "370HR"}, N + ARC_NOTE + " 인쇄값 115 Seconds."),
     P("mechanical.flexural_modulus", round(3744 * KSI, 1), "Pa", 1, "measured",
       {"direction": "MD", "direction_verbatim": "A. Length direction",
        "test_standard": "ASTM D790-15e2", "test_mode": "flexural", "loading_mode": "bending",
        "test_method": "3-point bend (ASTM D790-15e2)",
        "source_row_name": "Young's Modulus (벤더 인쇄 행 이름 그대로 — 시험법 칸은 D790)",
        "grade": "370HR"},
       N + FLEX_NOTE + " 인쇄값 3744 ksi. 같은 수가 mechanical.youngs_modulus pv3356·pv6081 에도 있다."),
     P("mechanical.flexural_modulus", round(3178 * KSI, 1), "Pa", 1, "measured",
       {"direction": "TD", "direction_verbatim": "B. Cross direction",
        "test_standard": "ASTM D790-15e2", "test_mode": "flexural", "loading_mode": "bending",
        "test_method": "3-point bend (ASTM D790-15e2)",
        "source_row_name": "Young's Modulus (벤더 인쇄 행 이름 그대로 — 시험법 칸은 D790)",
        "grade": "370HR"},
       N + FLEX_NOTE + " 인쇄값 3178 ksi. 같은 수가 mechanical.youngs_modulus pv3357·pv6082 에도 있다."),
   ]},
  {"match_name": "Isola IS400 Mid-Tg Laminate", "source": S["is400"], "properties": [
     P("electrical.arc_resistance", 120.0, "s", 1, "measured",
       {"test_standard": "IPC-TM-650 2.5.1B", "test_method": "arc resistance (IPC-TM-650 2.5.1B)",
        "grade": "IS400"}, N + ARC_NOTE + " 인쇄값 120 Seconds."),
     P("mechanical.flexural_modulus", round(3663 * KSI, 1), "Pa", 1, "measured",
       {"direction": "MD", "direction_verbatim": "A. Length direction",
        "test_standard": "ASTM D790-15e2", "test_mode": "flexural", "loading_mode": "bending",
        "test_method": "3-point bend (ASTM D790-15e2)",
        "source_row_name": "Young's Modulus (벤더 인쇄 행 이름 그대로 — 시험법 칸은 D790)",
        "grade": "IS400"},
       N + FLEX_NOTE + " 인쇄값 3663 ksi. 같은 수가 mechanical.youngs_modulus pv3382·pv6096 에도 있다."),
     P("mechanical.flexural_modulus", round(3328 * KSI, 1), "Pa", 1, "measured",
       {"direction": "TD", "direction_verbatim": "B. Cross direction",
        "test_standard": "ASTM D790-15e2", "test_mode": "flexural", "loading_mode": "bending",
        "test_method": "3-point bend (ASTM D790-15e2)",
        "source_row_name": "Young's Modulus (벤더 인쇄 행 이름 그대로 — 시험법 칸은 D790)",
        "grade": "IS400"},
       N + FLEX_NOTE + " 인쇄값 3328 ksi. 같은 수가 mechanical.youngs_modulus pv3383·pv6097 에도 있다."),
   ]},
  {"match_name": "Isola I-Tera MT40 Low-Loss Laminate", "source": S["itera"], "properties": [
     P("electrical.arc_resistance", 139.0, "s", 1, "measured",
       {"test_standard": "IPC-TM-650 2.5.1B", "test_method": "arc resistance (IPC-TM-650 2.5.1B)",
        "grade": "I-Tera MT40"}, N + ARC_NOTE + " 인쇄값 139 Seconds (Rev F, 2025-12-08)."),
   ]},
  {"match_name": "Isola Astra MT77 Very Low Loss RF/MW Laminate", "source": S["astra"], "properties": [
     P("electrical.arc_resistance", 139.0, "s", 1, "measured",
       {"test_standard": "IPC-TM-650 2.5.1B", "test_method": "arc resistance (IPC-TM-650 2.5.1B)",
        "grade": "Astra MT77"}, N + ARC_NOTE + " 인쇄값 139 Seconds (Rev D, 2021-04-20)."),
   ]},
 ]}

# ── 2. Rogers ────────────────────────────────────────────────────────────────
rogers = {"batch": BATCH,
 "note": ("Rogers CLTE·CLTE-AT·RO3000 시트를 원본으로 다시 열어 남은 칸을 채운다. "
          "CLTE 시트에는 **인장탄성률 행이 아예 없다** — `Flex Modulus (MD, CMD) … ASTM D790` 뿐이다. "
          "RO3000 은 350 dpi 렌더로 열 순서(RO3003|RO3035|RO3006|RO3010)와 비열 빈칸(RO3035)을 눈으로 대조했다."),
 "materials": [
  {"match_name": "Rogers CLTE Ceramic-PTFE Woven Glass Laminate", "source": S["clte"], "properties": [
     P("mechanical.flexural_modulus", 7984 * MPA, "Pa", 1, "measured",
       {"direction": "TD", "direction_verbatim": "CMD", "temperature_c": 25,
        "test_standard": "ASTM D790", "test_mode": "flexural", "loading_mode": "bending",
        "test_method": "3-point bend (ASTM D790)",
        "source_row_name": "Flex Modulus (MD, CMD)", "grade": "CLTE"},
       N + "CLTE 시트 `Flex Modulus (MD, CMD) 8122, 7984 MPa (1178, 1158 ksi) · 25˚C ± 3˚C · ASTM D790` 의 "
           "**CMD 칸**. MD 8122 는 이미 mechanical.flexural_modulus pv4038 에 있는데 **CMD 짝이 빠져 있었다**. "
           "같은 수가 mechanical.youngs_modulus pv12979 에도 앉아 있다(이 시트에는 인장탄성률 행이 없다)."),
     P("chemical.outgassing_tml", 0.0002, "1", 1, "measured",
       {"test_standard": "ASTM E595", "test_method": "NASA outgassing (ASTM E595)", "grade": "CLTE"},
       N + "CLTE 시트 NASA Outgassing 블록 `Total Mass Lost 0.02 %` → 0.0002(무차원 분율). "
           "형제 등급 CLTE-XT 는 이미 들어가 있었는데 **CLTE 열만 빠져 있었다**."),
     P("chemical.outgassing_cvcm", 0.0, "1", 1, "measured",
       {"test_standard": "ASTM E595", "test_method": "NASA outgassing (ASTM E595)", "grade": "CLTE"},
       N + "CLTE 시트 NASA Outgassing 블록 `Collected Volatiles 0.00 %` → 0.0. "
           "**인쇄된 0 이다** — 빈칸이 아니라 값이다."),
   ]},
  {"match_name": "Rogers CLTE-AT Ceramic-PTFE Woven Glass Laminate", "source": S["clteat"], "properties": [
     P("electrical.arc_resistance", 250.0, "s", 1, "measured",
       {"test_standard": "IPC TM-650 2.5.1", "test_method": "arc resistance (IPC TM-650 2.5.1)",
        "grade": "CLTE-AT"},
       N + "CLTE-AT 시트 `Arc Resistance 250 sec · IPC TM-650 2.5.1`. "
           "같은 블록의 `Dielectric Breakdown` 은 **값 칸이 비어 있어** 넣지 않았다."),
   ]},
  {"match_name": "Rogers RO3035 Ceramic-Filled PTFE Laminate", "source": S["ro3000"], "properties": [
     P("thermal.flammability_ul94", None, None, 1, "measured",
       {"test_standard": "UL 94", "grade": "RO3035"},
       N + "RO3000 시트 Physical Properties `Flammability V-0 · UL 94` — 네 등급 전부 V-0 이다. "
           "350 dpi 렌더로 열 정렬을 눈으로 확인했다(RO3003|RO3035|RO3006|RO3010).",
       value_text="V-0"),
   ]},
  {"match_name": "Rogers RO3006 Ceramic-Filled PTFE Laminate", "source": S["ro3000"], "properties": [
     P("thermal.flammability_ul94", None, None, 1, "measured",
       {"test_standard": "UL 94", "grade": "RO3006"},
       N + "RO3000 시트 Physical Properties `Flammability V-0 · UL 94`.", value_text="V-0"),
   ]},
  {"match_name": "Rogers RO3010 Ceramic-Filled PTFE Laminate", "source": S["ro3000"], "properties": [
     P("thermal.flammability_ul94", None, None, 1, "measured",
       {"test_standard": "UL 94", "grade": "RO3010"},
       N + "RO3000 시트 Physical Properties `Flammability V-0 · UL 94`.", value_text="V-0"),
   ]},
 ]}

# ── 3. Taconic/AGC · Chukoh ──────────────────────────────────────────────────
tac = {"batch": BATCH,
 "note": ("AGC(Taconic) TSM-DS3·TLY-5·TLX-8 TDS 와 中興化成 CHUKOH FLO 카탈로그를 원본으로 열어 "
          "빠져 있던 행을 채운다. 박리강도는 **동박 종류·시험조건마다 다른 행**이라 조건을 칸에 적어 따로 세운다."),
 "materials": [
  {"match_name": "AGC Taconic TSM-DS3 Ceramic-Filled Low-Loss Laminate", "source": S["tsmds3"], "properties": [
     P("mechanical.poisson_ratio", 0.20, "1", 1, "measured",
       {"direction": "TD", "direction_verbatim": "CD",
        "test_standard": "ASTM D 3039 / IPC-650 2.4.19",
        "test_method": "in-plane tensile test on laminate (ASTM D3039 / IPC-TM-650 2.4.19)",
        "test_mode": "tensile", "loading_mode": "uniaxial tension"},
       N + "AGC TSM-DS3 TDS `Poisson's Ratio MD 0.24 / CD 0.20 · ASTM D 3039/IPC-650 2.4.19`. "
           "MD 0.24 만 pv4115 로 들어가 있고 **CD 짝이 빠져 있었다** — 직물유리 적층판은 MD·CD 가 다르다."),
     P("electrical.arc_resistance", 226.0, "s", 1, "measured",
       {"test_standard": "IPC-650 2.5.1", "test_method": "arc resistance (IPC-TM-650 2.5.1)"},
       N + "AGC TSM-DS3 TDS `Arc Resistance 226 Seconds · IPC-650 2.5.1`."),
   ]},
  {"match_name": "Taconic TLY-5 (PTFE/woven glass RF laminate)", "source": S["tly5"], "properties": [
     P("interface.peel_strength", 2.86 * NMM, "N/m", 1, "measured",
       {"substrate": "1 oz. CL1 copper (reverse-treated ED)", "test_standard": "IPC-650 2.4.8",
        "test_method": "peel strength (IPC-TM-650 2.4.8)",
        "peel_angle_source": "IPC-TM-650 2.4.8 이 규정하는 90° 박리 — **시트에는 각도가 인쇄되지 않는다**(68차 DD)."},
       N + "TLY-5 TDS 박리강도 블록 `1 oz. CL1 copper 2.86 (16) N/mm (lbs/in)`. "
           "블록의 네 조건 중 ½oz ED(1.96)·1oz C1(3.04) 만 들어가 있었다."),
     P("interface.peel_strength", 2.32 * NMM, "N/m", 1, "measured",
       {"substrate": "(동박 종류 미인쇄 — 고온 조건 행)", "test_standard": "IPC-650 2.4.8",
        "test_condition": "at elevated temperature", "test_method": "peel strength (IPC-TM-650 2.4.8, elevated temp.)",
        "peel_angle_source": "IPC-TM-650 2.4.8 이 규정하는 90° 박리 — **시트에는 각도가 인쇄되지 않는다**(68차 DD)."},
       N + "TLY-5 TDS 박리강도 블록 마지막 행 `2.32 (13) N/mm (lbs/in) · IPC-650 2.4.8 (at elevated temp.)`. "
           "**이 행에는 동박 종류가 인쇄되어 있지 않다** — 지어내지 않고 미인쇄로 적는다."),
   ]},
  {"match_name": "Taconic TLX-8 (PTFE/woven glass RF laminate)", "source": S["tlx8"], "properties": [
     P("interface.peel_strength", 2.98 * NMM, "N/m", 1, "measured",
       {"substrate": "1 oz. RTF copper", "test_standard": "IPC-650 2.4.8 Sec. 5.2.2",
        "test_condition": "after thermal stress", "test_method": "peel strength (IPC-TM-650 2.4.8 Sec. 5.2.2, thermal stress)",
        "peel_angle_source": "IPC-TM-650 2.4.8 이 규정하는 90° 박리 — **시트에는 각도가 인쇄되지 않는다**(68차 DD)."},
       N + "TLX-8 TDS 박리강도 블록 `1 oz. RTF 2.98 (17) N/mm (lb/in)`. "
           "병합 칸이라 350 dpi 렌더로 어느 시험법 칸에 걸리는지 눈으로 대조했다 — 1oz ED·1oz RTF 두 행이 Sec. 5.2.2(Thermal Stress) 다."),
     P("interface.peel_strength", 1.93 * NMM, "N/m", 1, "measured",
       {"substrate": "1/2 oz. ED copper", "test_standard": "IPC-650 2.4.8 Sec. 5.2.2",
        "test_condition": "after thermal stress", "test_method": "peel strength (IPC-TM-650 2.4.8 Sec. 5.2.2, thermal stress)",
        "peel_angle_source": "IPC-TM-650 2.4.8 이 규정하는 90° 박리 — **시트에는 각도가 인쇄되지 않는다**(68차 DD)."},
       N + "TLX-8 TDS 박리강도 블록 `½ oz. ED 1.93 (11) N/mm (lb/in)` — **같은 ½oz ED 가 두 번 인쇄된다**: "
           "2.45 는 2.4.8.3(Elevated Temp.), 1.93 은 2.4.8 Sec. 5.2.2(Thermal Stress) 다. 렌더로 확인했다."),
     P("interface.peel_strength", 2.28 * NMM, "N/m", 1, "measured",
       {"substrate": "1 oz. rolled copper", "test_standard": "IPC-650 2.4.8 Sec. 5.2.2",
        "test_condition": "after thermal stress", "test_method": "peel strength (IPC-TM-650 2.4.8 Sec. 5.2.2, thermal stress)",
        "peel_angle_source": "IPC-TM-650 2.4.8 이 규정하는 90° 박리 — **시트에는 각도가 인쇄되지 않는다**(68차 DD)."},
       N + "TLX-8 TDS 박리강도 블록 `1 oz. rolled 2.28 (13) N/mm (lb/in)`."),
   ]},
  {"match_name": "Chukoh CHUKOH FLO CGN-500 PTFE Copper-Clad Laminate", "source": S["chukoh"], "properties": [
     P("interface.peel_strength", 0.5 * KNM, "N/m", 1, "measured",
       {"substrate": "1 oz 銅箔 (0.035 mm)", "temperature_c": 200,
        "test_condition": "200℃雰囲気 (in a 200 °C atmosphere)",
        "test_method": "引き剥がし強さ (peel strength, カタログ 製品性能表)",
        "peel_angle_source": "카탈로그가 각도를 찍지 않는다 — JIS C6481 계열 90° 박리로 보이나 **시트 미인쇄**라 각도를 적지 않는다(68차 DD)."},
       N + "CHUKOH FLO 카탈로그 `引き剥がし強さ … 200℃雰囲気 0.5 kN/m` (CGN-500 열). "
           "상온(A) 조건 1.0 kN/m 만 들어가 있고 **고온 행이 빠져 있었다**."),
     P("electrical.resistivity_volume", 1e14 * OHMCM_TO_OHMM, "ohm*m", 1, "measured",
       {"condition": "C-96/40/90", "test_condition": "C-96/40/90 (습열 처리 후)"},
       N + "CHUKOH FLO 카탈로그 `体積抵抗率 … C-96/40/90 10^14 Ω·cm` (CGN-500 열) → 1e12 Ω·m. "
           "조건 A(10^15 Ω·cm) 행만 들어가 있었다."),
     P("electrical.surface_resistivity", 1e13, "ohm", 1, "measured",
       {"condition": "C-96/40/90", "test_condition": "C-96/40/90 (습열 처리 후)"},
       N + "CHUKOH FLO 카탈로그 `表面抵抗率 … C-96/40/90 10^13 Ω` (CGN-500 열). 조건 A(10^14 Ω) 행만 들어가 있었다."),
   ]},
  {"match_name": "Chukoh CHUKOH FLO CGS-500A PTFE Copper-Clad Laminate", "source": S["chukoh"], "properties": [
     P("interface.peel_strength", 0.5 * KNM, "N/m", 1, "measured",
       {"substrate": "1 oz 銅箔 (0.035 mm)", "temperature_c": 200,
        "test_condition": "200℃雰囲気 (in a 200 °C atmosphere)",
        "test_method": "引き剥がし強さ (peel strength, カタログ 製品性能表)",
        "peel_angle_source": "카탈로그가 각도를 찍지 않는다 — **시트 미인쇄**라 각도를 적지 않는다(68차 DD)."},
       N + "CHUKOH FLO 카탈로그 `引き剥がし強さ … 200℃雰囲気 0.5 kN/m` (CGS-500A 열)."),
     P("electrical.resistivity_volume", 1e14 * OHMCM_TO_OHMM, "ohm*m", 1, "measured",
       {"condition": "C-96/40/90", "test_condition": "C-96/40/90 (습열 처리 후)"},
       N + "CHUKOH FLO 카탈로그 `体積抵抗率 … C-96/40/90 10^14 Ω·cm` (CGS-500A 열) → 1e12 Ω·m."),
     P("electrical.surface_resistivity", 1e13, "ohm", 1, "measured",
       {"condition": "C-96/40/90", "test_condition": "C-96/40/90 (습열 처리 후)"},
       N + "CHUKOH FLO 카탈로그 `表面抵抗率 … C-96/40/90 10^13 Ω` (CGS-500A 열)."),
   ]},
 ]}

# ── 4. 표 층 — JACOB 2009 극저온 복소유전율 ──────────────────────────────────
JN = (N + "**표 층(`tables/table-1.md`)에서 캔 값이다** — FTS 색인 밖에 있던 표다(73차 IB). "
      "Split Post Dielectric Resonator(SPDR, TE01δ) 로 저자가 직접 잰 값이고 벤더 시트에는 없는 **극저온 데이터**다. "
      "온도 표기 주의 — 표 머리글은 `25K`, 초록·본문 일부는 `10K` 라고 쓴다. **표를 따른다**(25 K).")


def jacob(mat, grade, f25, f290, e25, e290, t25, t290, gradenote):
    return {"match_name": mat, "source": S["jacob09"], "properties": [
      P("electrical.dielectric_constant", e25, "1", 1, "measured",
        {"temperature_k": 25, "frequency_hz": f25 * 1e6, "grade": grade,
         "test_method": "Split Post Dielectric Resonator (SPDR), TE01delta mode",
         "test_standard": "SPDR (Krupka Rayleigh-Ritz inversion) — 규격이 아니라 측정법이다"},
        JN + f" 표 1 Permittivity 25K = {e25}, 공진주파수 {f25} MHz. " + gradenote),
      P("electrical.dielectric_constant", e290, "1", 1, "measured",
        {"temperature_k": 290, "frequency_hz": f290 * 1e6, "grade": grade,
         "test_method": "Split Post Dielectric Resonator (SPDR), TE01delta mode",
         "test_standard": "SPDR (Krupka Rayleigh-Ritz inversion) — 규격이 아니라 측정법이다"},
        JN + f" 표 1 Permittivity 290 K = {e290}, 공진주파수 {f290} MHz. " + gradenote),
      P("electrical.dissipation_factor", t25, "1", 1, "measured",
        {"temperature_k": 25, "frequency_hz": f25 * 1e6, "grade": grade,
         "test_method": "Split Post Dielectric Resonator (SPDR), unloaded Q via STMQF",
         "test_standard": "SPDR — 규격이 아니라 측정법이다"},
        JN + f" 표 1 Loss Tangent 25K = {t25}. " + gradenote),
      P("electrical.dissipation_factor", t290, "1", 1, "measured",
        {"temperature_k": 290, "frequency_hz": f290 * 1e6, "grade": grade,
         "test_method": "Split Post Dielectric Resonator (SPDR), unloaded Q via STMQF",
         "test_standard": "SPDR — 규격이 아니라 측정법이다"},
        JN + f" 표 1 Loss Tangent 290 K = {t290}. " + gradenote),
    ]}


jacob_doc = {"batch": BATCH,
 "note": ("**표 층에서 캔 유일한 문서다.** Jacob 2009 가 RO3035·TLY-5·RF-35 세 라미네이트를 "
          "SPDR 로 25 K·290 K 에서 재어 복소유전율을 표로 인쇄한다. 벤더 시트는 상온만 찍으므로 "
          "이 12행은 **카탈로그에 없던 온도축**이다."),
 "materials": [
   jacob("Rogers RO3035 Ceramic-Filled PTFE Laminate", "RO3035",
         9704.967, 9695.140, 3.58, 3.65, 0.0025, 0.00370,
         "본문 표기 등급 `Rogers-RO3035`."),
   jacob("Taconic TLY-5 (PTFE/woven glass RF laminate)", "TLY-5-0100 (10 mil)",
         9911.2, 9911.5, 2.48, 2.42, 0.0009, 0.0015,
         "본문 표기 등급 `Taconic-TLY-5-0100` — 10 mil 품이다."),
   jacob("Taconic RF-35 (ceramic-filled PTFE/woven glass)", "RF35-0200 (20 mil)",
         9784.0, 9781.9, 3.59, 3.61, 0.0025, 0.0042,
         "본문 표기 등급 `Taconic-RF35-0200` — 20 mil 품이다."),
 ]}

# ── 5. 정정 — 영률 칸에 앉은 D790 값의 표기를 판정 창 안으로 ────────────────
def corr(pvid, reason, cond):
    return {"target": {"property_value_id": pvid}, "by": BATCH, "reason": reason, "set": {"conditions": cond}}


CLTE_REASON = ("Rogers CLTE/CLTE-XT 시트를 원본(`Rogers_CLTE_CLTE-XT_Laminates_DataSheet.pdf`)으로 다시 열어 "
               "확인했다 — 이 시트의 기계물성 블록에는 **인장탄성률 행이 없다**. 있는 것은 "
               "`Flexural Strength … ASTM D790` · `Tensile Strength … ASTM D638` · `Flex Modulus (MD, CMD) … ASTM D790` "
               "셋뿐이고, 영률 칸에 앉은 값은 그 **Flex Modulus** 행이다. 값·단위·등급·method·출처는 한 칸도 "
               "바꾸지 않는다. 시험모드는 이미 `method_detail` 한국어 산문에 적혀 있었지만 **`test_standard` 라는 "
               "제 칸이 비어 있어** 규격을 토큰으로 읽는 쪽에서는 보이지 않았다 — 기존 칸을 하나도 지우지 않고 "
               "`test_standard`·`test_mode`·`loading_mode`·`test_method` 를 **덧붙이기만 한다**(52차 NA 의 "
               "되돌리기 표시도 그대로 옮겨 담는다).")

# 라이브의 기존 조건칸을 **하나도 잃지 않도록 그대로 옮겨 적고** 그 위에 시험모드 칸만 덧붙인다.
_NA52 = {"direction_verbatim_before_correction": None,
         "temperature_C_before_correction": 25,
         "temperature_c_before_correction": None,
         "correction_reason": ("조건 어휘 통일(브리프 547·551) — 값·단위·등급·method·출처는 그대로다. "
                               "temperature_C→temperature_c · direction 정규화 [52차 NA] "
                               "/ 74차 JD 가 시험모드 칸(test_standard·test_mode·loading_mode·test_method)을 덧붙였다."),
         "corrected_by": "52차 NA → 74차 JD"}

_D790ADD = {"test_standard": "ASTM D790", "test_mode": "flexural", "loading_mode": "bending",
            "test_method": "3-point bend (ASTM D790)",
            "method_detail": "굴곡 탄성률 (ASTM D790) — 인장 탄성률은 이 TDS에 미인쇄",
            "temperature_c": 25,
            "reported_as_youngs_modulus": True,
            "source_row_name": "Flex Modulus (MD, CMD)",
            "tensile_modulus_in_source": "이 TDS 에는 인장탄성률 행이 없다 — 74차 JD 가 원문을 다시 열어 확인했다.",
            "duplicate_of": "mechanical.flexural_modulus — 같은 출처·같은 수가 그 키에도 있다. 원행은 지우지 않았다(삭제는 사람이 정한다)."}


def clte_cond(direction, verbatim, grade, dir_before):
    return {**_NA52, **_D790ADD, "direction": direction, "direction_verbatim": verbatim,
            "direction_before_correction": dir_before, "grade": grade}


corrections = {"batch": BATCH,
 "note": ("영률 칸에 앉은 **굽힘탄성률**의 시험모드 표기를 대표값 선택기의 판정 창 안에 "
          "제 칸으로 세운다. 값·단위·등급·method·출처는 한 칸도 바꾸지 않고, 기존 조건칸도 하나도 지우지 않는다. 삭제 0건.\n"
          "Isola 370HR(pv3356·3357·6081·6082)도 같은 무늬라 후보로 열었지만 **고치지 않았다** — "
          "그 네 행은 이미 `test_standard: ASTM D790-15e2` 를 판정 창 안에 갖고 있고, "
          "`conditions` 는 통째로 교체되므로 손대면 54차 PB·51차 MA 의 동률 판정 기록이 사라진다. "
          "표기가 이미 유효한 행을 꾸미려고 앞 파동의 판정을 지우지 않는다."),
 "corrections": [
  corr(12978, CLTE_REASON, clte_cond("MD", "MD (machine direction)", "CLTE", "MD (machine direction)")),
  corr(12979, CLTE_REASON, clte_cond("TD", "CMD (cross-machine direction)", "CLTE", "CMD (cross-machine direction)")),
  corr(12981, CLTE_REASON, clte_cond("MD", "MD (machine direction)", "CLTE-XT", "MD (machine direction)")),
  corr(12982, CLTE_REASON, clte_cond("TD", "CMD (cross-machine direction)", "CLTE-XT", "CMD (cross-machine direction)")),
 ]}

# ── 6. 판정 ──────────────────────────────────────────────────────────────────
RO3000_SHEET = ("Rogers RO3000 Series Circuit Materials Data Sheet(2024-01, Pub #92-130)를 로컬 원본으로 열고 "
                "**2면을 350 dpi 로 렌더해 눈으로 대조했다**(`jd74_ro3000_mechphys_350dpi.png`). "
                "Standard Properties Table 의 열 순서는 파일 이름과 달리 **RO3003 | RO3035 | RO3006 | RO3010** 이다"
                "(72차 HC 실측을 재확인). 기계물성 블록의 행은 셋뿐이다 — "
                "`Copper Peel Strength` · `Young's Modulus`(2단, ASTM D638) · `Dimensional Stability (MD, CMD)`. ")

verdicts = {"batch": BATCH,
 "note": ("RO3000 세 등급의 코어 빈칸을 판정한다. **문서를 못 연 것이 아니라 열어서 그 행이 없음을 확인한 것**이다. "
          "형제 등급 RO3003(재료 241)에는 같은 사유의 판정이 이미 들어가 있다 — 이번에 RO3035·RO3006·RO3010 을 맞춘다."),
 "verdicts": [
  {"material_id": 2793, "name": "Rogers RO3035 Ceramic-Filled PTFE Laminate",
   "core_absent_from_vendor_sheet": {
     "mechanical.poisson_ratio": RO3000_SHEET + "**포아송비 행이 없다**(`Poisson` 적중 0). "
       "Rogers 는 RO3000 시리즈에 포아송비를 찍지 않는다.",
     "mechanical.tensile_strength": RO3000_SHEET + "**인장강도 행이 없다**(`Tensile Strength` 적중 0). "
       "인장 계열로 인쇄되는 것은 `Young's Modulus … ASTM D638` 뿐이고 강도 행은 따라오지 않는다.",
     "thermal.specific_heat": RO3000_SHEET + "`Specifc Heat Capacity` 행은 있는데 **RO3035 칸이 비어 있다** — "
       "인쇄된 값은 셋뿐이다(RO3003 0.9 · RO3006 0.86 · RO3010 0.8, J/g/K, Test Method 칸 verbatim `Calculated`). "
       "텍스트만 보면 값 3개·열 4개라 한 칸씩 밀리는데, **렌더로 대조해 빈칸이 RO3035 임을 확인했다**. "
       "이웃 등급 값을 끌어다 채우지 않는다."}},
  {"material_id": 2794, "name": "Rogers RO3006 Ceramic-Filled PTFE Laminate",
   "core_absent_from_vendor_sheet": {
     "mechanical.poisson_ratio": RO3000_SHEET + "**포아송비 행이 없다**(`Poisson` 적중 0).",
     "mechanical.tensile_strength": RO3000_SHEET + "**인장강도 행이 없다**(`Tensile Strength` 적중 0)."}},
  {"material_id": 2795, "name": "Rogers RO3010 Ceramic-Filled PTFE Laminate",
   "core_absent_from_vendor_sheet": {
     "mechanical.poisson_ratio": RO3000_SHEET + "**포아송비 행이 없다**(`Poisson` 적중 0).",
     "mechanical.tensile_strength": RO3000_SHEET + "**인장강도 행이 없다**(`Tensile Strength` 적중 0)."}},
  {"material_id": 246, "name": "Rogers CLTE Ceramic-PTFE Woven Glass Laminate",
   "core_absent_from_vendor_sheet": {
     "mechanical.poisson_ratio": ("Rogers CLTE/CLTE-XT Series Laminates Data Sheet 를 원본으로 열어 확인했다 — "
       "**포아송비 행이 없다**(`Poisson` 적중 0). 지금 이 칸에 있는 0.17 은 형제 등급 CLTE-AT 시트"
       "(ASTM D-3039)의 값을 t3 로 빌려 온 것이고 0.183 은 클래스 대표값(t4) 이다 — 둘 다 CLTE 열에서 온 수가 아니다. "
       "덧붙임: 같은 시트에는 **인장탄성률 행도 없다**. 영률 칸의 8122·7984 MPa 는 `Flex Modulus (MD, CMD) … ASTM D790` "
       "행이다(74차 JD 가 표기를 판정 창 안으로 옮기고 같은 수를 `mechanical.flexural_modulus` 에도 세웠다). "
       "그 칸은 값이 있으므로 판정으로 덮지 않는다 — 빈칸이 아니라 **이름이 틀린 칸**이다.")}},
  {"material_id": 245, "name": "Rogers CLTE-XT Ceramic-PTFE Woven Glass Laminate",
   "core_absent_from_vendor_sheet": {
     "mechanical.poisson_ratio": ("Rogers CLTE/CLTE-XT Series Laminates Data Sheet 를 원본으로 열어 확인했다 — "
       "**포아송비 행이 없다**(`Poisson` 적중 0). 지금 값은 형제 등급 CLTE-AT 에서 빌린 t3 와 클래스 대표값 t4 다. "
       "덧붙임: 영률 칸의 3247·3261 MPa 도 `Flex Modulus (MD, CMD) … ASTM D790` 행이고 같은 수가 이미 "
       "`mechanical.flexural_modulus` pv4017·pv4018 에 있다 — 그 칸은 비어 있지 않으므로 판정 대상이 아니다.")}},
 ]}

for name, doc in (("jd74_01_isola.json", isola),
                  ("jd74_02_rogers.json", rogers),
                  ("jd74_03_taconic_chukoh.json", tac),
                  ("jd74_04_jacob2009_cryo_tables.json", jacob_doc),
                  ("jd74_05_corrections.json", corrections),
                  ("jd74_06_verdicts.json", verdicts)):
    (OUT / name).write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    n = (sum(len(m["properties"]) for m in doc["materials"]) if "materials" in doc
         else len(doc.get("corrections", doc.get("verdicts", []))))
    print(f"  {name}: {n}")
