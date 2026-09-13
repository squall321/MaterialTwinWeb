#!/usr/bin/env python3
# 74차 JA 수집 배치 산출물 생성기 — Resonac/Hitachi 계열의 표 층·구판 카탈로그 수확과 코어 빈칸 판정을 만든다.
#
# 왜 생성기인가 — 손으로 쓴 JSON 은 단위·키·tier 규율을 조용히 어긴다.
# 여기서 만들고 여기서 검증한다(자체검증 실패면 파일을 쓰지 않는다).
#
# 산출:
#   ja74_01_kobelite_tensile_ja_edition.json  구판 일문 카탈로그 p.98 이 인쇄한 引っ張り強さ
#   ja74_02_mcl_e_67_digitized.json           구판 영문 카탈로그 p.44 그래프 디지타이즈 + 특성표
#   ja74_09_verdicts.json                     코어 빈칸 판정(집계가 읽는 dict 꼴)
from __future__ import annotations

import json
import os
import sqlite3
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                                 "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"),
                  "materialtwin.db")
BATCH = "74차 JA"

PCB = "/data/paper_patent_corpus/standards_appnotes/pcb"
JA_CAT = f"{PCB}/HitachiChemical_CopperCladLaminates_FullCatalog_ja_2016-08.pdf"
EN_CAT = f"{PCB}/HitachiChemical_CopperCladLaminates_FullCatalog_en_2017-03.pdf"

SRC_JA = {"kind": "datasheet",
          "title": "日立化成 銅張積層板 総合カタログ (Copper Clad Laminates Full Catalog, 日本語版)",
          "publisher": "Hitachi Chemical (現 Resonac)", "year": 2016,
          "url": None, "local_path": JA_CAT}
SRC_EN = {"kind": "datasheet",
          "title": "Hitachi Chemical Copper Clad Laminates Full Catalog (English edition)",
          "publisher": "Hitachi Chemical (now Resonac)", "year": 2017,
          "url": None, "local_path": EN_CAT}

MPa = 1.0e6
GPa = 1.0e9


# ─────────────────────────────────────────────────────────────────────────────
# ① KOBELITE 引っ張り強さ — 구판 **일문판** p.98 (영문판에는 이 행이 없다)
#
# 열 대응은 같은 표의 曲げ弾性率·曲げ強さ 가 **이미 DB 에 들어 있는 영문판 구간값과
# 일치하는지**로 독립 검증했다(아래 XCHECK). 350 dpi 렌더로 눈 대조도 했다.
# ─────────────────────────────────────────────────────────────────────────────
KOBELITE = [
    # (DB 재료명, 등급 표기, 引っ張り強さ N/mm^2, 曲げ弾성률 kN/mm^2, 曲げ強さ N/mm^2)
    ("Hitachi Chemical KOBELITE KEL-571 (unclad non-woven aramid epoxy laminate)",
     "KEL-571", 250.0, 8.5, 330.0),
    ("Hitachi Chemical KOBELITE KEL-973 (unclad aramid/polyester epoxy laminate)",
     "KEL-973", 120.0, 7.5, 220.0),
    ("Hitachi Chemical KOBELITE KEL-GEF / KEL-GEF(R) (unclad glass/epoxy laminate)",
     "KEL-GEF(R)", 320.0, 22.0, 600.0),
]

# 영문판 2017-03 p.82 가 인쇄한 구간 — 이미 DB 에 t1 로 들어 있다(72차 HD).
# 일문판 단일값이 이 구간 안에 들어가야 **열 대응이 맞다**는 증거가 된다.
XCHECK = {"KEL-571": {"flex_mod": (8.4, 8.6), "flex_str": (330.0, 400.0)},
          "KEL-973": {"flex_mod": (7.4, 7.6), "flex_str": (200.0, 220.0)},
          "KEL-GEF(R)": {"flex_mod": (22.0, 24.0), "flex_str": (600.0, 650.0)}}


def kobelite_doc() -> dict:
    mats = []
    for name, grade, tens, fmod, fstr in KOBELITE:
        x = XCHECK[grade]
        assert x["flex_mod"][0] <= fmod <= x["flex_mod"][1], grade
        assert x["flex_str"][0] <= fstr <= x["flex_str"][1], grade
        note = (
            f"原文 verbatim: 「■積層板特性」表(日本語版カタログ PDF p.98 / 印刷 p.112), "
            f"品番 {grade} の行「引っ張り強さ（N/mm2）」= {tens:g}. "
            f"표 각주 verbatim: 「上記数値は、1.0mm厚さにおける測定値で、保証値ではありません。」 "
            f"환산: {tens:g} N/mm^2 = {tens:g} MPa = {tens:g}e6 Pa = {tens * MPa:.6g} Pa; "
            f"되돌리면 {tens * MPa:.6g}/1e6 = {tens:g} N/mm^2. "
            f"열 대응 독립 검증 — 같은 표의 曲げ弾性率 {fmod:g} kN/mm^2 와 曲げ強さ {fstr:g} N/mm^2 가 "
            f"영문판 2017-03 p.82 의 같은 등급 구간 {x['flex_mod']} kN/mm^2 · {x['flex_str']} N/mm^2 "
            f"안에 정확히 들어간다(그 구간값은 72차 HD 가 이미 t1 으로 넣어 두었다). "
            f"pdftotext -layout 은 이 행에서 인접 그래프(耐摩耗性評価結果)의 y축 눈금 `60` 을 "
            f"네 번째 숫자로 끌어와 열을 밀었다 — 350 dpi 렌더로 표가 3열임을 눈으로 확인하고 옮겼다. "
            f"이 행은 **영문판 2017-03 에는 없다**(영문판 KOBELITE 표의 기계축은 "
            f"Flexural strength/modulus · Compressive · Izod · Cleavage 뿐이다)."
        )
        mats.append({
            "match_name": name,
            "source": SRC_JA,
            "properties": [{
                "key": "mechanical.tensile_strength",
                "value": tens * MPa, "unit": "Pa",
                "method": "measured", "tier": 1,
                "conditions": {"test_method": "vendor catalog 積層板特性 (試験法 표기 없음)",
                               "specimen_thickness_mm": 1.0,
                               "grade": grade,
                               "source_table": "■積層板特性 (ja 2016-08, PDF p.98)",
                               "guaranteed_value": False},
                "notes": note,
            }],
        })
    return {"batch": BATCH, "materials": mats}


# ─────────────────────────────────────────────────────────────────────────────
# ② MCL-E-67 — 구판 영문 카탈로그 p.44(인쇄 47)의 두 그래프를 디지타이즈
#
# 71차 GD·72차 HD 가 「이 벤더 계열에서 포아송비 원문은 이 그래프 하나뿐」이라고 인계했다.
# 350 dpi 렌더에서 축 눈금선을 픽셀로 잡아 보정했다(아래 CAL 주석).
# ─────────────────────────────────────────────────────────────────────────────
#
# 픽셀 보정 (350 dpi, PDF p.44):
#   플롯 박스 상단 y=826 · 하단 y=1515 (전체 높이 688 px, 페이지 좌표계 y-2251 기준)
#   가로 눈금선이 **완전 등간격**으로 검출됐다 —
#     Elastic Modulus: 7선 [0,115,229,344,459,574,688] → 위=30 GPa, 아래=0 (5 GPa/115 px)
#     Poisson's Ratio: 6선 [0,137,275,413,551,688]     → 위=0.50,  아래=0.00 (0.10/137.6 px)
#   세로 눈금선 5개도 등간격(138 px) — x축은 30·50·100·150·200 ℃ 의 **순서축**이다.
#   1 px = 0.0436 GPa · 0.000727(포아송). 판독 오차 ±4 px → ±0.2 GPa · ±0.003.
#
# **평탄부만 옮겼다.** 100~150 ℃ 의 급강하 구간은 곡선 추적이 파선(Width)을 놓쳐
# 두 방법의 편차가 판독 오차를 넘었다 — 빈칸이 틀린 값보다 낫다.
MCL_E_67_NAME = "Resonac (Hitachi Chemical) MCL-E-67 (glass/epoxy CCL, FR-4)"

DIGI = [  # (key, unit, 30℃ Length, 30℃ Width, 200℃ Length, 200℃ Width, figure, ±)
    ("mechanical.youngs_modulus", "Pa", 24.4, 21.4, 15.6, 10.6,
     "●Elastic Modulus（Tensile）", "±0.2 GPa"),
    ("mechanical.poisson_ratio", "1", 0.149, 0.121, 0.46, 0.315,
     "●Poisson's Ratio", "±0.003 (30 ℃) / ±0.01 (200 ℃, 급경사부)"),
]

# 영문판 p.43 ■Characteristics (t1.6mm) 표 — 인쇄된 구간은 두 행이다.
MCL_E_67_TABLE = [
    # (key, unit, lower, upper, conditions, verbatim, 환산식)
    ("thermal.glass_transition", "K", 393.15, 403.15,
     {"test_method": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
     "Tg | TMA | ℃ | 120〜130 | 2.4.24",
     "120 + 273.15 = 393.15 K; 130 + 273.15 = 403.15 K; 되돌리면 393.15-273.15 = 120"),
    ("thermal.expansion_linear", "1/K", 13e-6, 16e-6,
     {"axis": "in-plane (X)", "regime": "<Tg", "temperature_range_c": "30-120",
      "test_standard": "IPC-TM-650 2.4.24", "test_method": "TMA"},
     "CTE X （30〜120℃） | ppm/℃ | 13〜16 | 2.4.24",
     "13 ppm/℃ x 1e-6 = 1.3e-05 1/K; 되돌리면 1.3e-05/1e-6 = 13"),
    ("thermal.expansion_linear", "1/K", 14e-6, 17e-6,
     {"axis": "in-plane (Y)", "regime": "<Tg", "temperature_range_c": "30-120",
      "test_standard": "IPC-TM-650 2.4.24", "test_method": "TMA"},
     "CTE Y （30〜120℃） | ppm/℃ | 14〜17 | 2.4.24",
     "14 ppm/℃ x 1e-6 = 1.4e-05 1/K"),
    ("thermal.expansion_linear", "1/K", 50e-6, 70e-6,
     {"axis": "through-thickness (Z)", "regime": "<Tg",
      "test_standard": "IPC-TM-650 2.4.24", "test_method": "TMA"},
     "CTE Z （＜Tg） | ppm/℃ | 50〜70 | 2.4.24",
     "50 ppm/℃ x 1e-6 = 5.0e-05 1/K"),
    ("thermal.expansion_linear", "1/K", 200e-6, 300e-6,
     {"axis": "through-thickness (Z)", "regime": ">Tg",
      "test_standard": "IPC-TM-650 2.4.24", "test_method": "TMA"},
     "CTE Z （＞Tg） | ppm/℃ | 200〜300 | 2.4.24",
     "200 ppm/℃ x 1e-6 = 2.0e-04 1/K"),
    ("mechanical.flexural_strength", "Pa", 500 * MPa, 600 * MPa,
     {"direction": "Length", "direction_verbatim": "Length", "conditioning": "A",
      "test_standard": "IPC-TM-650 2.4.4", "test_mode": "flexural"},
     "Flexural Strength Length | A | N/mm2 | 500〜600 | 2.4.4",
     "500 N/mm^2 = 500 MPa = 5.0e+08 Pa; 되돌리면 5.0e+08/1e6 = 500"),
    ("mechanical.flexural_strength", "Pa", 400 * MPa, 500 * MPa,
     {"direction": "Width", "direction_verbatim": "Width", "conditioning": "A",
      "test_standard": "IPC-TM-650 2.4.4", "test_mode": "flexural"},
     "Flexural Strength Width | A | N/mm2 | 400〜500 | 2.4.4",
     "400 N/mm^2 = 4.0e+08 Pa"),
    ("interface.peel_strength", "N/m", 1400.0, 1600.0,
     {"copper_foil_thickness_um": 18, "conditioning": "A",
      "test_standard": "IPC-TM-650 2.4.8"},
     "Copper Peel Strength 18μm | A | kN/m | 1.4〜1.6 | 2.4.8",
     "1.4 kN/m x 1000 = 1400 N/m; 되돌리면 1400/1000 = 1.4"),
    ("electrical.dielectric_constant", "1", 4.7, 4.8,
     {"frequency_hz": 1.0e6, "conditioning": "C-96/20/65",
      "test_standard": "IPC-TM-650 2.5.5.1"},
     "Dielectric Constant（1MHz） | C-96/20/65 | − | 4.7〜4.8 | 2.5.5.1",
     "무차원 — 환산 없음"),
    ("electrical.dissipation_factor", "1", 0.0130, 0.0170,
     {"frequency_hz": 1.0e6, "conditioning": "C-96/20/65",
      "test_standard": "IPC-TM-650 2.5.5.1"},
     "Dissipation Factor（1MHz） | C-96/20/65 | − | 0.0130〜0.0170 | 2.5.5.1",
     "무차원 — 환산 없음"),
    ("chemical.water_absorption_24h", "1", 0.0006, 0.0008,
     {"conditioning": "E-24/50+D-24/23", "test_standard": "IPC-TM-650 2.6.2.1"},
     "Water Absorption | E-24/50+D-24/23 | ％ | 0.06〜0.08 | 2.6.2.1",
     "0.06 % / 100 = 0.0006; 되돌리면 0.0006 x 100 = 0.06 %"),
]

PAGE_NOTE = (
    "출처 쪽 verbatim 머리: 「Copper Clad Laminate for Double Sided PWBs / "
    "MCL-E-67 ［UV Block Type MCL-E-67 Type（WK）］ / Glass Epoxy Copper Clad Laminate（FR-4）」. "
    "이 쪽은 MCL-E-67 과 UV 차단 변종 Type(WK) 를 함께 다루는데, **UV 차단 그래프에만** "
    "「（Type（WK））」 가 붙고 나머지 그래프·특성표에는 형식 표기가 없다. "
    "그래서 이 배치는 기본 등급 MCL-E-67 한 장만 세웠고 Type(WK) 카드는 세우지 않았다."
)


def mcl_e_67_doc() -> dict:
    props = []
    for key, unit, l30, w30, l200, w200, fig, unc in DIGI:
        for temp, direction, val in ((30, "Length", l30), (30, "Width", w30),
                                     (200, "Length", l200), (200, "Width", w200)):
            if key == "mechanical.youngs_modulus":
                stored, conv = val * GPa, (
                    f"{val:g} GPa x 1e9 = {val * GPa:.6g} Pa; "
                    f"되돌리면 {val * GPa:.6g}/1e9 = {val:g}")
                mode = {"test_mode": "tensile"}
            else:
                stored, conv = val, "무차원 — 환산 없음"
                mode = {}
            props.append({
                "key": key, "value": stored, "unit": unit,
                "method": "digitized", "tier": 1,
                "conditions": {**mode, "temperature_c": temp,
                               "direction": direction, "direction_verbatim": direction,
                               "specimen_thickness_mm": 1.6,
                               "figure": fig,
                               "source_page": "en 2017-03 PDF p.44 (인쇄 p.47)"},
                "notes": (
                    f"원문은 숫자가 아니라 **그래프**다 — {fig}, 가로축 「Laminate Surface "
                    f"Temperature（℃）」 30·50·100·150·200, 세로축 t1.6mm. "
                    f"{direction} 곡선의 {temp} ℃ 값을 350 dpi 렌더에서 픽셀로 읽었다: {val:g}"
                    f"{' GPa' if key.endswith('youngs_modulus') else ''}. {conv} "
                    f"축 보정 — 플롯 박스 높이 688 px 에 가로 눈금선이 완전 등간격으로 검출됐고"
                    f"(Elastic Modulus 7선 = 0~30 GPa, Poisson 6선 = 0.00~0.50), "
                    f"세로 눈금선 5개도 등간격 138 px 라 x축은 순서축이다. "
                    f"판독 불확도 {unc}. "
                    f"**평탄부만 옮겼다** — 100~150 ℃ 급강하 구간은 파선(Width) 곡선 추적이 "
                    f"끊겨 두 판독법의 편차가 불확도를 넘어 값을 만들지 않았다. "
                    f"모드 근거: 같은 쪽 모듈러스 그래프 제목이 「（Tensile）」 를 명시한다"
                    + ("." if key.endswith("youngs_modulus") else
                       "; 포아송비 그래프 자체에는 모드 표기가 없으나 이 벤더 표에 "
                       "「굽힘 포아송비」 라는 행은 존재하지 않는다.")
                    + " " + PAGE_NOTE),
            })
    for key, unit, lo, hi, cond, verbatim, conv in MCL_E_67_TABLE:
        for bound, val in (("lower", lo), ("upper", hi)):
            props.append({
                "key": key, "value": val, "unit": unit,
                "method": "measured", "tier": 1,
                "conditions": {**cond, "bound": bound, "specimen_thickness_mm": 1.6,
                               "source_table": "■Characteristics (en 2017-03 PDF p.43)"},
                "notes": (f"원문 verbatim: 「{verbatim}」 (표 머리 「■Characteristics （t1.6mm）」). "
                          f"인쇄된 구간이므로 bound:{bound} 로 **두 행**으로 갈랐다 — 평균 내지 않았다. "
                          f"환산: {conv}. {PAGE_NOTE}"),
            })
    return {"batch": BATCH, "materials": [{
        "new_material": {
            "name": MCL_E_67_NAME,
            "category": "composite",
            "attributes": {
                "role": "product",
                "role_reason": "벤더 카탈로그에 품번·표준치수·특성표가 인쇄된 판매 등급이다.",
                "role_confidence": "high",
                "vendor": "Resonac (formerly Hitachi Chemical / Showa Denko Materials)",
                "aliases": ["MCL-E-67", "MCL-E-67(WK)", "MCL-E-67 Type(WK)"],
                "grade_family": "MCL-E (glass epoxy double sided, FR-4)",
                "note_type_wk": (
                    "Type(WK) 는 같은 쪽이 다루는 UV 차단 변종이다. 이 배치는 별도 카드를 "
                    "세우지 않았다 — 그래프·특성표에 형식 표기가 없어 값을 둘로 귀속시킬 근거가 없다."),
                "note_in_use": (
                    "Ouyang 2020 (Warpage and Void Simulation of System in Package) 의 "
                    "TABLE I SUBSTRATE STRIP STACK-UP 이 Core 재료로 `MCL-E-67` 을 적는다 — "
                    "실사용 등급임을 코퍼스가 독립으로 확인해 준다."),
            },
        },
        "source": SRC_EN,
        "properties": props,
    }]}


# ─────────────────────────────────────────────────────────────────────────────
# ③ 코어 빈칸 판정 — `apply_core_verdicts.py` 가 병합하고
#    `coverage_report.py` 가 읽는 **dict 꼴**이다({물성키: 사유}).
#    73차 ID 가 산문 문자열 판정이 집계에 안 읽혀 V5 가 294 로 튄 것을 찾았다.
# ─────────────────────────────────────────────────────────────────────────────
VENDOR = "core_absent_from_vendor_sheet"

RESONAC_REASON = (
    "Resonac(구 Hitachi Chemical) 동장적층판 계열은 이 물성의 **행 자체를 인쇄하지 않는다**. "
    "여섯 갈래를 열어 확인했다 — "
    "(1) 71차 GD: 일문판 카탈로그 2023-2024 총괄표 PDF 6·7·8쪽을 350 dpi 렌더로 전수; "
    "(2) 72차 HD: 카탈로그 네 판(ja 2023-24 66쪽 · en 2025-05 65쪽 · en 2026-07 51쪽 · ja 2026-04), "
    "벤더 웹페이지 29장, 日立化成テクニカルレポート No.54~62 아홉 호 327쪽, "
    "SDS 포털 전 카테고리(적층판은 고체 물품이라 SDS 의무가 없어 시스템에 아예 없다); "
    "(3) 74차 JA(이 배치): **구판 종합 카탈로그 두 권을 새로 전수했다** — "
    "en 2017-03 (90쪽) · ja 2016-08 (102쪽). 쪽별 텍스트 길이 감사를 토큰 검사 앞에 돌려 "
    "이미지 전용 쪽이 없음을 확인한 뒤, 대소문자 무시 토큰 전수: "
    "en 판 `specific gravity` 는 KOBELITE 무피복 적층판 쪽(p.82) 한 곳뿐이고 "
    "동장적층판 쪽에는 0, `density` 적중 3건은 전부 산문(`high density multi-layer PWB`), "
    "`Poisson` 은 MCL-E-67 그래프 쪽(p.44) 하나뿐, `Specific Heat` 0, `Tensile strength` 0; "
    "ja 판 `比重` 0 · `比熱` 0 · `密度` 26쪽 적중은 전부 산문(`高密度実装`), "
    "`引っ張り強` 은 KOBELITE 연마캐리어 쪽(p.98) 한 곳뿐; "
    "(4) 74차 JA: 구판 제품별 쪽의 ■Characteristics 표 행 어휘를 확인했다 — "
    "예 TD-002(en p.22)는 Tg·CTE·Solder Heat·T260/T288·Decomposition Temp·Peel·"
    "Flexural Modulus·Elastic Modulus(Tensile)·Dk·Df·Volume/Surface/Insulation Resistance·"
    "Water Absorption 이 전부이고 밀도·비열·인장강도 행이 없다; "
    "(5) 74차 JA: **코퍼스 표 층 전수** — /data/paper_patent_corpus 의 tables/*.md 88,532장을 "
    "등급 토큰으로 전수 grep 했다(FTS 색인 밖의 층이다). 적중 2장뿐이고 둘 다 값이 없다 "
    "(Ouyang 2020 은 스택업 재료명만, Yoshii 2008 은 다른 제품 CEL-9240ZHF10 의 조성표); "
    "(6) 74차 JA: 코퍼스 본문 층 전수 grep 에서 이 계열 등급을 실제로 부르는 논문은 4편뿐이고 "
    "물성표를 가진 것은 Chen 2017 하나인데 72차 HD 가 기각했다(같은 표의 영률·CTE 가 "
    "벤더 카탈로그와 어긋나는 해석용 등가 물성이다). "
    "결론: 벤더 층·규격 층(71차 GD 의 IPC-4101 판정)·학술 층이 모두 닫혔다. "
    "근거 문서: " + EN_CAT + " · " + JA_CAT
)

CONDUCTIVITY_REASON = (
    "이 등급의 열전도율 칸은 벤더 총괄표가 **`－` 로 비워 인쇄한다**. "
    "71차 GD 가 일문판 2023-2024 PDF 6·7·8쪽에서, 72차 HD 가 영문판 2025-05 과 2026-07 "
    "두 판에서 같은 칸이 세 판 모두 `－` 임을 확인했다. 형제 등급에는 값이 인쇄되므로 "
    "추출 누락이 아니라 **벤더가 그 등급에 대해 공표하지 않는 것**이다. "
    "74차 JA 가 구판 카탈로그 두 권(en 2017-03 · ja 2016-08)을 새로 전수해 "
    "이 등급들의 구판 제품별 쪽에도 熱伝導率/Thermal Conductivity 행이 없음을 확인했다."
)

KOBELITE_REASON_TMPL = (
    "KOBELITE(コウベライト) 무피복 적층판 표에 이 물성의 행이 없다. "
    "두 판을 **모두** 열어 확인했다 — 영문판 2017-03 PDF p.82 의 KOBELITE 일반특성표는 "
    "Flexural strength/modulus · Compressive Strength · Izod impact · Cleavage Strength · "
    "Air Flammability · specific gravity · chemical resistance · Flammability · "
    "Aptitude punching temperature · CTE X/Y/Z · Dk · Df · 절연저항 이 전부이고, "
    "일문판 2016-08 PDF p.97~99 의 KOBELITE 절(품번일람표 · 두께허용차 · 積層板特性 · UL인정)은 "
    "引き裂き強度 · 引っ張り強さ · 曲げ強さ · 曲げ弾性率 · 耐薬品性 이 전부다. "
    "**두 판을 합쳐도 {miss} 행은 없다.** "
    "이 벤더는 이 제품군에 대해 굽힘(曲げ) 모드만 인쇄하고 인장 탄성률을 공표하지 않으며, "
    "포아송비·비열·열전도율은 어느 판에도 없다. "
    "근거 문서: " + EN_CAT + " (p.82) · " + JA_CAT + " (p.97-99)"
)

KOBELITE_MISS = {
    "mechanical.youngs_modulus": "인장 탄성률(曲げ弾性率 만 인쇄한다)",
    "mechanical.poisson_ratio": "포아송비",
    "thermal.conductivity": "열전도율",
    "thermal.specific_heat": "비열",
    "mechanical.tensile_strength": "引っ張り強さ",
}

RESONAC_KEYS = ["physical.density", "mechanical.poisson_ratio",
                "thermal.specific_heat", "mechanical.tensile_strength"]


def verdicts_doc(conn: sqlite3.Connection) -> dict:
    have: dict[int, set[str]] = {}
    for mid, k in conn.execute("select distinct material_id,property_key from property_value"):
        have.setdefault(mid, set()).add(k)
    names = {mid: n for mid, n in conn.execute("select id,name from material")}

    kel_ids = {n: i for i, n in names.items() if "KOBELITE" in (n or "")}
    # 이 배치가 값을 넣는 KEL 세 장의 인장강도는 판정 대상이 아니다.
    getting_tensile = {kel_ids[n] for n, *_ in KOBELITE if n in kel_ids}

    out, flat = [], []
    for mid, name in sorted(names.items()):
        if not name:
            continue
        is_resonac_ccl = (mid in range(2733, 2799)
                          and ("Resonac" in name))
        is_kel = "KOBELITE" in name
        if not (is_resonac_ccl or is_kel):
            continue
        d: dict[str, str] = {}
        if is_resonac_ccl:
            for k in RESONAC_KEYS:
                if k not in have.get(mid, set()):
                    d[k] = RESONAC_REASON
            if "thermal.conductivity" not in have.get(mid, set()):
                d["thermal.conductivity"] = CONDUCTIVITY_REASON
        else:
            for k, label in KOBELITE_MISS.items():
                if k in have.get(mid, set()):
                    continue
                if k == "mechanical.tensile_strength" and mid in getting_tensile:
                    continue   # 이 배치가 t1 값을 넣는다
                d[k] = KOBELITE_REASON_TMPL.format(miss=label)
        if d:
            out.append({"material_id": mid, "name": name, VENDOR: d})
            flat += [{"material_id": mid, "key": k, "verdict": VENDOR} for k in d]
    return {"batch": BATCH,
            "note": ("코어 빈칸 판정이다. 꼴은 `apply_core_verdicts.py` 가 병합하고 "
                     "`coverage_report.py` 가 읽는 **{물성키: 사유} dict** 다 — "
                     "73차 ID 가 산문 문자열 판정이 집계에 안 읽히는 것을 찾았다."),
            "verdicts": out,
            "summary": {"materials": len(out), "cells": len(flat)}}


# ─────────────────────────────────────────────────────────────────────────────
# 자체검증
# ─────────────────────────────────────────────────────────────────────────────
RANGE = {"physical.density": (1.0, 25000.0), "mechanical.youngs_modulus": (1e3, 1.5e12),
         "mechanical.poisson_ratio": (-1.0, 0.5), "mechanical.tensile_strength": (1e3, 1e11),
         "thermal.conductivity": (0.0, 5e4), "thermal.specific_heat": (10.0, 5000.0),
         "thermal.expansion_linear": (-1e-4, 5e-3), "electrical.dielectric_constant": (1.0, 1e7),
         "chemical.water_absorption_24h": (0.0, 1.0), "interface.peel_strength": (0.0, 5e5),
         "mechanical.flexural_strength": (1e3, 1e11)}
METHODS = {"measured", "handbook", "computed", "estimated", "digitized"}
MODE_KEYS = {"test_standard", "test_method", "test", "test_mode", "mode", "test_geometry",
             "strength_property", "method_detail", "test_condition", "condition",
             "loading_mode"}


def validate(docs: list[tuple[str, dict]], conn: sqlite3.Connection) -> list[str]:
    units = {k: u for k, u in conn.execute("select key,si_unit from property_definition")}
    dbnames = {n for n, in conn.execute("select name from material")}
    err: list[str] = []
    for fn, doc in docs:
        for ent in doc.get("materials", []):
            mn = ent.get("match_name")
            nm = (ent.get("new_material") or {}).get("name")
            if mn and mn not in dbnames:
                err.append(f"{fn}: match_name 이 DB 에 없다 — {mn}")
            if nm:
                if nm in dbnames:
                    err.append(f"{fn}: new_material 이름이 이미 DB 에 있다 — {nm}")
                if len(nm) > 200:
                    err.append(f"{fn}: 재료명 {len(nm)}자 > 200 — {nm[:60]}")
                at = (ent.get("new_material") or {}).get("attributes") or {}
                for req in ("role", "aliases"):
                    if req not in at:
                        err.append(f"{fn}: new_material 에 {req} 없음 — {nm}")
            if not (ent.get("source") or {}).get("title"):
                err.append(f"{fn}: source.title 없음")
            for p in ent.get("properties", []):
                k, u, t, m = p["key"], p["unit"], p["tier"], p["method"]
                if k not in units:
                    err.append(f"{fn}: 물성 정의에 없는 키 {k}")
                elif units[k] != u:
                    err.append(f"{fn}: 단위 불일치 {k} — 정의 {units[k]} vs 준 값 {u}")
                if m not in METHODS:
                    err.append(f"{fn}: method 어휘 위반 {m} ({k})")
                if t == 4:
                    err.append(f"{fn}: t4 금지 — {k}")
                if t == 3 and "grade_scope" not in (p.get("conditions") or {}):
                    err.append(f"{fn}: t3 인데 grade_scope 없음 — {k}")
                if not p.get("notes"):
                    err.append(f"{fn}: notes 없음 — {k}")
                lo, hi = RANGE.get(k, (None, None))
                if lo is not None and not (lo <= p["value"] <= hi):
                    err.append(f"{fn}: 물리범위 밖 {k} = {p['value']}")
                if k in ("mechanical.youngs_modulus", "mechanical.tensile_strength",
                         "mechanical.flexural_strength"):
                    if not (MODE_KEYS & set((p.get("conditions") or {}).keys())):
                        err.append(f"{fn}: 시험모드가 대표값 선택기가 보는 칸 밖이다 — {k}")
    return err


def main() -> int:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    docs = [("ja74_01_kobelite_tensile_ja_edition.json", kobelite_doc()),
            ("ja74_02_mcl_e_67_digitized.json", mcl_e_67_doc())]
    err = validate(docs, conn)
    docs.append(("ja74_09_verdicts.json", verdicts_doc(conn)))
    if err:
        print("자체검증 실패 — 파일을 쓰지 않는다:", file=sys.stderr)
        for e in err:
            print("  ✗", e, file=sys.stderr)
        return 1
    for fn, doc in docs:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        if "verdicts" in doc:
            print(f"  ✓ {fn} — 재료 {doc['summary']['materials']}종 · 판정 {doc['summary']['cells']}칸")
        else:
            n = sum(len(m.get("properties", [])) for m in doc["materials"])
            print(f"  ✓ {fn} — 재료 {len(doc['materials'])}항목 · 물성 {n}행")
    print("자체검증 오류 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
