#!/usr/bin/env python3
# 75차 KC 산출 JSON 생성기 — Chukoh 미채굴 4등급 · Astra MT77 굽힘탄성률 · TLX-8 D902 모드 확정.
# 원문 표의 숫자가 리터럴로 박혀 있고, 단위 환산은 이 파일에서만 한다(역산 없음).
from __future__ import annotations
import json, pathlib

OUT = pathlib.Path(__file__).resolve().parent
BATCH = "75차 KC"
N = "[75차 KC] "

KSI = 6.894757e6          # ksi -> Pa
MPA = 1.0e6               # MPa -> Pa
KNM = 1000.0              # kN/m -> N/m
OHMCM_TO_OHMM = 0.01      # Ω·cm -> ohm*m
PPM = 1e-6                # ppm/℃ -> 1/K
GCC = 1000.0              # g/cc -> kg/m^3


def P(key, value, unit, tier, method, conditions, notes, value_text=None):
    d = {"key": key, "value": value, "unit": unit, "method": method,
         "quality_tier": tier, "conditions": conditions, "notes": notes}
    if value_text is not None:
        d["value_text"] = value_text
        d["value"] = None
    return d


# ── 출처 ──────────────────────────────────────────────────────────────────────
S_CHUKOH = {
    "kind": "datasheet",
    "url": "https://www.chukoh.co.jp/wp-content/uploads/catalog05_lami_ja-1.pdf",
    "title": "CHUKOH FLO 銅張積層板 製品カタログ (catalog05_lami_ja, 2023.12.01)",
    "publisher": "Chukoh Chemical Industries, Ltd.",
    "year": 2023,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/Chukoh_CopperCladLaminate_Catalog05_JA.pdf",
}
S_ASTRA_0317 = {
    "kind": "datasheet",
    "url": "https://www.pragoboard.cz/download/astra_mt77.pdf",
    "title": "Astra® MT77 Very Low-loss Laminate Material — Isola Group typical values (doc code 03/17 DSAstraMT77Q)",
    "publisher": "Isola Group",
    "year": 2017,
}

# ══════════════════════════════════════════════════════════════════════════════
# 1. Chukoh 미채굴 4등급 — CGP-500A · CGA-500 · CGH-500 · CGK-500
# ══════════════════════════════════════════════════════════════════════════════
# 製品性能 표(2면)를 350 dpi 로 렌더해 눈으로 대조했다. **인쇄면 열 순서**는
#   CGS-500A | CGN-500 | CGP-500A | CGA-500 | CGH-500 | CGK-500
# 이고 pdftotext 추출 순서와 정확히 같다(72차 HC 의 Rogers 열밀림 무늬는 여기 없다).
# **CTE 는 x/y/z 열여덟 칸 전부 양수다** — 렌더로 확인했다. 이 표에서 마이너스 부호가
# 붙는 곳은 線膨張係数의 측정구간 `-65〜150℃` 하나뿐이고 그 부호는 텍스트 추출에도 남았다.
# 지수는 텍스트 추출이 위첨자를 잃어 `1015` 로 뭉갠다 — 렌더로 10^15 임을 확인하고 박았다.

CH_NOTE = ("中興化成 `CHUKOH FLO 銅張積層板 製品カタログ`(catalog05_lami_ja, 2023.12.01) 2면 "
           "`製品性能` 표에서 그대로 옮겼다. 350 dpi 렌더로 열 순서·지수·부호를 눈 대조했다 — "
           "인쇄면 열 순서는 CGS-500A | CGN-500 | CGP-500A | CGA-500 | CGH-500 | CGK-500 다.")

# 등급별 시험조건 각주 — ※サンプルの厚さ・測定周波数
#   CGS:0.8mm/12GHz, CGN:0.8mm/10GHz, CGP:1.6mm/12GHz,
#   CGA:0.54mm/12GHz, CGH:1.6mm/9GHz, CGK:1.6mm/8GHz
GRADES = {
    "CGP-500A": {
        "material_class": "fluoropolymer (PTFE) impregnated glass cloth copper-clad laminate",
        "series_desc": ("ふっ素樹脂含浸ガラスクロスを積層した銅張積層板で当社のスタンダード製品です。"
                        "引きはがし強さ、吸水率、スルーホール加工性等に優れ、高い寸法安定性、機械的強度を有しています。"),
        "series_desc_ko": ("불소수지 함침 유리크로스를 적층한 동박적층판 — Chukoh 의 표준 제품. "
                           "박리강도·흡수율·스루홀 가공성이 좋고 치수안정성과 기계적 강도가 높다."),
        "thickness_mm": 1.6, "freq_ghz": 12,
        "dk": 2.60, "df": 0.0018,
        "rv_a": 1e15, "rv_c": 1e14,        # Ω·cm
        "rs_a": 1e14, "rs_c": 1e14,        # Ω
        "flex_mpa": 120, "wabs_pct": 0.01,
        "cte_x": 16, "cte_y": 20, "cte_z": 216,
        "sg": 2.2, "peel_a": 3.0, "peel_200": 1.5,
    },
    "CGA-500": {
        "material_class": "fluoropolymer (PTFE) + inorganic-filled glass cloth copper-clad laminate",
        "series_desc": ("ふっ素樹脂と特殊な無機物をガラスクロスに含浸し、その基材を積層した銅張積層板です。"
                        "優れた高周波特性を維持しながら量産用途に対応した製品です。"),
        "series_desc_ko": ("불소수지와 특수 무기물을 유리크로스에 함침한 기재를 적층한 동박적층판 — "
                           "고주파 특성을 유지하면서 양산 용도에 대응한 제품."),
        "thickness_mm": 0.54, "freq_ghz": 12,
        "dk": 3.00, "df": 0.0030,
        "rv_a": 1e15, "rv_c": 1e14,
        "rs_a": 1e14, "rs_c": 1e14,
        "flex_mpa": 60, "wabs_pct": 0.02,
        "cte_x": 16, "cte_y": 20, "cte_z": 216,
        "sg": 2.3, "peel_a": 1.5, "peel_200": 1.0,
    },
    "CGH-500": {
        "material_class": "fluoropolymer (PTFE) + inorganic-filled glass cloth copper-clad laminate",
        "series_desc": ("ふっ素樹脂と特殊な無機物をガラスクロスに含浸し、その基材を積層した銅張積層板です。"
                        "汎用基板と誘電率が同等で誘電正接が低いため、同一の設計でより低損失の回路が得られます。"),
        "series_desc_ko": ("불소수지와 특수 무기물을 유리크로스에 함침한 기재를 적층한 동박적층판 — "
                           "범용 기판과 유전율이 같으면서 유전정접이 낮아 같은 설계로 더 낮은 손실의 회로를 얻는다."),
        "thickness_mm": 1.6, "freq_ghz": 9,
        "dk": 3.45, "df": 0.0027,
        "rv_a": 1e15, "rv_c": 1e14,
        "rs_a": 1e14, "rs_c": 1e14,
        "flex_mpa": 120, "wabs_pct": 0.02,
        "cte_x": 13, "cte_y": 14, "cte_z": 174,
        "sg": 2.3, "peel_a": 1.5, "peel_200": 1.0,
    },
    "CGK-500": {
        "material_class": "fluoropolymer (PTFE) + high-permittivity inorganic-filled glass cloth copper-clad laminate",
        "series_desc": ("ふっ素樹脂と特殊な無機物をガラスクロスに含浸し、その基材を積層した銅張積層板です。"
                        "高誘電率により小型で軽量、低損失の高機能回路が得られます。"),
        "series_desc_ko": ("불소수지와 특수 무기물을 유리크로스에 함침한 기재를 적층한 동박적층판 — "
                           "높은 유전율로 소형·경량·저손실의 고기능 회로를 얻는다."),
        "thickness_mm": 1.6, "freq_ghz": 8,
        "dk": 5.00, "df": 0.0040,
        "rv_a": 1e13, "rv_c": 1e13,
        "rs_a": 1e12, "rs_c": 1e12,
        "flex_mpa": 240, "wabs_pct": 0.04,
        "cte_x": 12, "cte_y": 13, "cte_z": 120,
        "sg": 2.4, "peel_a": 1.5, "peel_200": 1.2,
    },
}

# 이 카탈로그 표에 **없는** 행 — 네 등급 전부 같다. 전권을 열어 확인했다.
ABSENT = {
    "mechanical.youngs_modulus":
        ("中興化成 `CHUKOH FLO 銅張積層板 製品カタログ`(catalog05_lami_ja, 2023.12.01)를 전권 열어 확인했다. "
         "2면 `製品性能` 표의 행은 열둘이다 — 比誘電率 · 誘電正接 · 体積抵抗率 · 表面抵抗率 · 絶縁抵抗 · "
         "**曲げ強さ** · 吸水率 · 線膨張係数(X/Y/Z) · 比重 · 引き剥がし強さ · 燃焼性 · 耐薬品性. "
         "**탄성률 행이 아예 없다 — 강도축이 굽힘 하나다**(曲げ強さ MPa). 인장탄성률도 굽힘탄성률도 인쇄하지 않는다. "
         "형제 등급 251 CGN-500 · 252 CGS-500A 가 같은 표를 쓰고 그쪽 영률은 Rogers RT/duroid 에서 빌린 t3 다. "
         "75차 KC 가 원본 렌더로 재확인했다."),
    "mechanical.poisson_ratio":
        ("같은 카탈로그 같은 표다. 포아송비 행이 없다 — 57차 SB 가 251·252 에서 확인한 것과 같은 표이고 "
         "75차 KC 가 350 dpi 렌더로 열두 행 전수를 다시 셌다. 이 벤더는 등방·이방 탄성상수를 인쇄하지 않는다."),
    "thermal.specific_heat":
        ("같은 카탈로그다. 전권 텍스트에 `比熱` 0건 · `熱伝導` 0건 · `specific heat` 0건이다. "
         "이 표는 열물성으로 線膨張係数(x/y/z) 하나만 인쇄한다."),
}


def chukoh_material(grade: str, g: dict) -> dict:
    cond_dk = {"frequency_hz": g["freq_ghz"] * 1e9,
               "sample_thickness_mm": g["thickness_mm"],
               "test_standard": "BCDR (balanced-type circular disk resonator)",
               "grade": grade}
    src_note = (f" 등급별 시험조건은 표 각주 `※サンプルの厚さ・測定周波数` 에서 왔다 — "
                f"{grade.split('-')[0]}:{g['thickness_mm']}mm/{g['freq_ghz']}GHz.")
    props = [
        P("electrical.dielectric_constant", g["dk"], "1", 1, "measured", dict(cond_dk),
          N + CH_NOTE + f" 인쇄값 比誘電率 {g['dk']:.2f} (BCDR法)." + src_note),
        P("electrical.dissipation_factor", g["df"], "1", 1, "measured", dict(cond_dk),
          N + CH_NOTE + f" 인쇄값 誘電正接 {g['df']:.4f} (BCDR法)." + src_note),

        P("electrical.resistivity_volume", g["rv_a"] * OHMCM_TO_OHMM, "ohm*m", 1, "measured",
          {"condition": "A", "test_condition": "A (受入れ状態 / as received)", "grade": grade},
          N + CH_NOTE + f" 인쇄값 体積抵抗率(A) {g['rv_a']:.0e} Ω·cm. "
          "위첨자가 텍스트 추출에서 뭉개져 렌더로 지수를 확인했다. Ω·cm → ohm*m 는 ×0.01."),
        P("electrical.resistivity_volume", g["rv_c"] * OHMCM_TO_OHMM, "ohm*m", 1, "measured",
          {"condition": "C-96/40/90", "test_condition": "C-96/40/90 (습열 처리 후)", "grade": grade},
          N + CH_NOTE + f" 인쇄값 体積抵抗率(C-96/40/90) {g['rv_c']:.0e} Ω·cm. Ω·cm → ohm*m 는 ×0.01."),

        P("electrical.surface_resistivity", g["rs_a"], "ohm", 1, "measured",
          {"condition": "A", "test_condition": "A (受入れ状態 / as received)", "grade": grade},
          N + CH_NOTE + f" 인쇄값 表面抵抗率(A) {g['rs_a']:.0e} Ω. 시트저항이라 환산 없음."),
        P("electrical.surface_resistivity", g["rs_c"], "ohm", 1, "measured",
          {"condition": "C-96/40/90", "test_condition": "C-96/40/90 (습열 처리 후)", "grade": grade},
          N + CH_NOTE + f" 인쇄값 表面抵抗率(C-96/40/90) {g['rs_c']:.0e} Ω."),

        P("mechanical.flexural_strength", g["flex_mpa"] * MPA, "Pa", 1, "measured",
          {"condition": "A", "test_condition": "A (受入れ状態 / as received)",
           "test_mode": "flexural", "loading_mode": "bending",
           "source_row_name": "曲げ強さ", "grade": grade},
          N + CH_NOTE + f" 인쇄값 曲げ強さ {g['flex_mpa']} MPa. "
          "**이 표의 유일한 강도축이다** — 인장강도 행이 없다. MPa → Pa 는 ×1e6."),

        P("chemical.water_absorption_24h", g["wabs_pct"] / 100.0, "1", 1, "measured",
          {"condition": "E-24/50 + D-24/23", "grade": grade},
          N + CH_NOTE + f" 인쇄값 吸水率 {g['wabs_pct']} % (試験方法 E-24/50+D-24/23). % → 무차원은 ÷100."),
    ]

    # ── 이방성 CTE — 축마다 별도 행 ──────────────────────────────────────────
    # PTFE·세라믹 충전 라미네이트는 z 축이 면내의 한 자릿수 위다. 축을 반드시 가른다.
    for axis, key_v, direction in (("X", "cte_x", "in-plane"),
                                   ("Y", "cte_y", "in-plane"),
                                   ("Z", "cte_z", "through-thickness")):
        props.append(
            P("thermal.expansion_linear", g[key_v] * PPM, "1/K", 1, "measured",
              {"direction": direction, "direction_verbatim": axis,
               "temperature_range_c": "-65 to 150", "grade": grade},
              N + CH_NOTE + f" 인쇄값 線膨張係数 {axis}軸 {g[key_v]} ppm/℃ (측정구간 -65〜150℃). "
              f"**부호는 350 dpi 렌더로 확인했다 — 양수다.** 이 표에서 마이너스가 붙는 곳은 "
              f"측정구간 `-65〜150℃` 하나뿐이다. ppm/℃ → 1/K 는 ×1e-6."))

    props += [
        P("physical.density", g["sg"] * GCC, "kg/m^3", 1, "measured",
          {"condition": "A", "test_condition": "A (受入れ状態 / as received)", "grade": grade},
          N + CH_NOTE + f" 인쇄값 比重 {g['sg']} g/cc. "
          "벤더가 인쇄한 것은 比重(비중)이고 단위 칸이 g/cc 라 수치를 그대로 밀도로 옮긴다 — "
          "형제 등급 252 CGS-500A(pv4166)가 같은 처리다. g/cc → kg/m^3 는 ×1000."),

        P("interface.peel_strength", g["peel_a"] * KNM, "N/m", 1, "measured",
          {"condition": "A", "test_condition": "A (受入れ状態 / as received)",
           "temperature_c": 23, "substrate": "1 oz 銅箔 (0.035 mm)",
           "test_method": "引き剥がし強さ (peel strength, カタログ 製品性能表)",
           "peel_angle_source": "카탈로그가 각도를 찍지 않는다 — **시트 미인쇄**라 각도를 적지 않는다(68차 DD).",
           "grade": grade},
          N + CH_NOTE + f" 인쇄값 引き剥がし強さ(A) {g['peel_a']} kN/m. "
          "표 각주 `※引き剥がし強さは、1oz銅箔（0.035㎜）の測定値です`. kN/m → N/m 는 ×1000."),
        P("interface.peel_strength", g["peel_200"] * KNM, "N/m", 1, "measured",
          {"condition": "200℃雰囲気", "test_condition": "200℃雰囲気 (in a 200 °C atmosphere)",
           "temperature_c": 200, "substrate": "1 oz 銅箔 (0.035 mm)",
           "test_method": "引き剥がし強さ (peel strength, カタログ 製品性能表)",
           "peel_angle_source": "카탈로그가 각도를 찍지 않는다 — **시트 미인쇄**라 각도를 적지 않는다(68차 DD).",
           "grade": grade},
          N + CH_NOTE + f" 인쇄값 引き剥がし強さ(200℃雰囲気) {g['peel_200']} kN/m. kN/m → N/m 는 ×1000."),

        P("chemical.chemical_resistance", None, None, 1, "measured",
          {"condition": "카탈로그 試験方法 칸이 `-` 다 — 시험법·시약이 인쇄돼 있지 않다", "grade": grade},
          N + CH_NOTE + " 인쇄값 耐薬品性 `優`. **벤더 자기 정성등급이고 시험법 칸은 `-` 다** — "
          "숫자를 만들지 않고 원문 그대로 문자열로 남긴다. 같은 표의 `燃焼性 = 不燃` 은 "
          "**넣지 않았다** — `thermal.flammability_ul94` 는 UL 94 등급 칸인데 不燃은 UL 94 등급이 아니다(74차 JD 판단 유지).",
          value_text="耐薬品性 優 (excellent chemical resistance — 벤더 정성등급, 시험법 미인쇄)"),
    ]

    return {
        "new_material": {
            "name": f"Chukoh CHUKOH FLO {grade} PTFE Copper-Clad Laminate",
            "category": "composite",
            "attributes": {
                "manufacturer": "Chukoh Chemical Industries",
                "grade": grade,
                "subsystem": "rf",
                "material_class": g["material_class"],
                "role": "product",
                "role_reason": "이름에 제조사+그레이드가 박혀 있고 출처가 해당 제품 카탈로그 — 이름·출처 둘 다 제품 신호",
                "role_confidence": "high",
                "product_series_note_ja": g["series_desc"],
                "product_series_note_ko": g["series_desc_ko"],
                "core_absent_from_vendor_sheet": dict(ABSENT),
            },
        },
        "source": dict(S_CHUKOH),
        "properties": props,
    }


chukoh = {
    "batch": BATCH,
    "note": ("74차 JD 가 넘긴 1순위 표적 — Chukoh 카탈로그의 **미채굴 4등급**"
             "(CGP-500A · CGA-500 · CGH-500 · CGK-500)을 새 카드로 세우고 製品性能 표를 전부 옮긴다. "
             "표는 형제 등급 251 CGN-500 · 252 CGS-500A 와 **같은 표**라 조건 어휘를 그쪽에 맞췄다. "
             "350 dpi 렌더로 열 순서·지수 위첨자·CTE 부호를 눈 대조했다. "
             "`絶縁抵抗`(Ω)는 **물성키가 없어 넣지 않았다** — 보고서에 표로 남긴다."),
    "materials": [chukoh_material(k, v) for k, v in GRADES.items()],
}

# ══════════════════════════════════════════════════════════════════════════════
# 2. Isola Astra MT77 — 03/17 시트의 **굽힘탄성률** 두 행
# ══════════════════════════════════════════════════════════════════════════════
# 74차 JD 가 넘긴 3번 표적(개정판 기준 결정)을 풀다가 나온 부산물이다.
# Rev D(2021-04-20)는 모듈러스 행을 통째로 지웠지만, 03/17 DSAstraMT77Q 시트는
# **인장탄성률과 굽힘탄성률을 제 이름으로 따로 인쇄한다** — Isola 의 D790 함정과 반대 자리다.
#   Tensile Modulus/Young's Modulus  A. 2,784 / B. 2,526 ksi  ASTM D3039-095a  ← 라이브에 이미 있다
#   Flexural Modulus/Taylor's Modulus A. 2,701 / B. 2,529 ksi  ASTM D790-10    ← 비어 있었다
# 라이브 재료 254 에 `mechanical.flexural_modulus` 가 0행이라 그 짝을 채운다.

ASTRA_NOTE = (
    "Isola Astra MT77 03/17 시트(DSAstraMT77Q)를 원본으로 열어 확인했다. 이 시트는 "
    "`Tensile Modulus/Young's Modulus … ASTM D3039-095a` 와 "
    "`Flexural Modulus/Taylor's Modulus … ASTM D790-10` 을 **제 이름으로 따로 인쇄한다** — "
    "Isola 가 굽힘값을 `Young's Modulus` 한 칸에 몰아 넣는 무늬(370HR·IS400·I-Tera)와 **반대 자리다**. "
    "인장 쪽 2,784/2,526 ksi 는 라이브 pv12968·12969·13435·13436 로 이미 서 있었고 "
    "**굽힘 쪽 짝이 비어 있어** 채운다(재료 254 의 `mechanical.flexural_modulus` 는 0행이었다). "
    "현행 Rev D(2021-04-20)에는 **모듈러스 행 자체가 없다** — 값이 바뀐 것이 아니라 행이 사라졌으므로 "
    "Rev D 와 충돌하지 않는다. ksi → Pa 는 ×6.894757e6.")

astra = {
    "batch": BATCH,
    "note": ("Astra MT77 개정판 기준을 Rev D(2021-04-20)로 정하면서, Rev D 가 **인쇄하지 않는** "
             "굽힘탄성률 두 행을 03/17 시트에서 채운다. Rev D 와 값이 어긋나는 행은 하나도 넣지 않았다."),
    "materials": [{
        "match_name": "Isola Astra MT77 Very Low Loss RF/MW Laminate",
        "source": dict(S_ASTRA_0317),
        "properties": [
            P("mechanical.flexural_modulus", round(2701 * KSI, 1), "Pa", 1, "measured",
              {"direction": "MD", "direction_verbatim": "A. Lengthwise direction",
               "test_standard": "ASTM D790-10", "test_mode": "flexural", "loading_mode": "bending",
               "test_method": "3-point bend (ASTM D790-10)",
               "source_row_name": "Flexural Modulus/Taylor's Modulus",
               "datasheet_revision": "03/17 DSAstraMT77Q (Isola, pre-Rev A)",
               "temperature_c": 23, "grade": "Astra MT77"},
              N + ASTRA_NOTE + " 인쇄값 2,701 ksi."),
            P("mechanical.flexural_modulus", round(2529 * KSI, 1), "Pa", 1, "measured",
              {"direction": "TD", "direction_verbatim": "B. Crosswise direction",
               "test_standard": "ASTM D790-10", "test_mode": "flexural", "loading_mode": "bending",
               "test_method": "3-point bend (ASTM D790-10)",
               "source_row_name": "Flexural Modulus/Taylor's Modulus",
               "datasheet_revision": "03/17 DSAstraMT77Q (Isola, pre-Rev A)",
               "temperature_c": 23, "grade": "Astra MT77"},
              N + ASTRA_NOTE + " 인쇄값 2,529 ksi. 인장 TD 2,526 ksi 와 **세 자리에서 갈리는 다른 수다** — "
              "같은 수를 두 키에 옮긴 것이 아니다."),
        ],
    }],
}

# ══════════════════════════════════════════════════════════════════════════════
# 3. Taconic TLX-8 — `ASTM D 902` 시험모드 확정 (정정 5행)
# ══════════════════════════════════════════════════════════════════════════════
# 74차 JD 가 "규격 본문을 못 봐서 단정하지 않았다" 고 넘긴 2번 표적이다. 확정했다.
#
# **ASTM D902 = Standard Test Methods for Flexible Resin-Coated Glass Fabrics and
#   Glass Fabric Tapes Used for Electrical Insulation** (2020-03-09 철회).
# 규격이 열거하는 시험 항목 전수 —
#   Breaking Strength · Conditioning · Dielectric Breakdown Voltage and Dielectric Strength ·
#   Dissipation Factor and Relative Permittivity · Effect of Elevated Temperature ·
#   Resistance to Oil · Sampling · Thermal Endurance · Thickness · Thread Count · Weight ·
#   Weight Loss at Elevated Temperature
# **굽힘·휨 시험이 하나도 없다.** 기계시험은 `Breaking Strength` 하나뿐이고 그 절차는
# **ASTM D828(정속신장 인장시험)** 을 참조한다. `Thread Count` 가 있는 것에서 보듯 대상은
# **유연한 코팅 유리직물·테이프**다 — 늘어진 직물 테이프는 3점 굽힘으로 잴 수가 없다.
# 굳은 적층판용 규격은 D902 가 아니라 ASTM D709 다.
#
# 결정적 방증은 벤더 자신에게 있다 — **Taconic 이 같은 `ASTM D 902` 로 `Tensile Strength`
# 행을 찍는다**(라이브 pv6274·6275: MD 35,600 psi · CD 27,500 psi). 같은 시트 계열에서
# 같은 규격이 인장강도를 재고 있다.
#
# 결론 — **TLX-8 의 D902 모듈러스는 인장이다. 키를 옮길 필요가 없다**(이미 youngs_modulus 에 있다).
# 판정 창에 모드만 박는다. D 3039 행은 원래 모호하지 않아 손대지 않는다.
#
# **기존 조건칸은 하나도 지우지 않는다.** 51차 MA 의 동률 판정, 52차 NB 의 중복 표시,
# 54차 PA 의 되돌리기 표시를 전부 그대로 옮겨 담고 모드 칸만 덧붙인다.

D902_REASON = (
    "74차 JD 가 넘긴 표적 — `ASTM D 902` 가 무엇을 재는 규격인지 확정했다. "
    "D902 = `Standard Test Methods for Flexible Resin-Coated Glass Fabrics and Glass Fabric Tapes "
    "Used for Electrical Insulation`(2020-03-09 철회)이고, 규격이 열거하는 시험은 "
    "Breaking Strength · Conditioning · Dielectric Breakdown · Dissipation Factor and Relative "
    "Permittivity · Effect of Elevated Temperature · Resistance to Oil · Sampling · Thermal Endurance · "
    "Thickness · Thread Count · Weight · Weight Loss 다 — **굽힘 시험이 하나도 없다.** "
    "기계시험은 `Breaking Strength` 하나뿐이고 그 절차는 **ASTM D828(정속신장 인장시험)** 을 참조한다. "
    "대상이 `Thread Count` 를 세는 **유연한 코팅 유리직물·테이프**라 3점 굽힘 자체가 성립하지 않는다. "
    "방증 — **Taconic 이 같은 `ASTM D 902` 로 `Tensile Strength` 행을 찍는다**(pv6274 MD 35,600 psi · "
    "pv6275 CD 27,500 psi). 따라서 이 행은 **인장이 맞고 키를 옮기지 않는다** — "
    "Isola 의 D790 무늬와 **다른 자리다**. 값·단위·등급·method·출처는 한 칸도 바꾸지 않고, "
    "기존 조건칸도 하나도 지우지 않고 시험모드 칸만 덧붙인다.")

D902_MODE = {
    "test_mode": "tensile",
    "loading_mode": "tension",
    "test_method": "strip tensile / breaking strength (ASTM D902, 절차는 ASTM D828 정속신장 인장)",
    "test_standard_scope": ("ASTM D902 — Flexible Resin-Coated Glass Fabrics and Glass Fabric Tapes "
                            "Used for Electrical Insulation (withdrawn 2020-03-09). 굽힘 시험 미수록."),
    "mode_confirmed_by": "75차 KC — 규격 수록 시험 전수 대조 + 같은 벤더가 D902 로 인장강도를 찍는 것",
}


def corr(pvid: str, existing: dict, extra: dict | None = None) -> dict:
    """기존 조건칸을 통째로 담고 모드 칸만 덧붙인다. 지우는 칸은 없다."""
    newc = dict(existing)
    newc.update(D902_MODE)
    if extra:
        newc.update(extra)
    prev = existing.get("correction_reason", "")
    newc["correction_reason"] = (
        (prev + " / " if prev else "")
        + "75차 KC 가 `ASTM D 902` 의 시험모드(test_mode·loading_mode·test_method)를 판정 창에 덧붙였다 — "
          "기존 칸은 하나도 지우지 않았다.")
    prevby = existing.get("corrected_by", "")
    newc["corrected_by"] = (prevby + " → 75차 KC") if prevby else "75차 KC"
    return {"target": {"property_value_id": int(pvid)}, "by": BATCH,
            "reason": D902_REASON, "set": {"conditions": newc}}


# 라이브에서 읽어 온 기존 조건칸 원문(한 칸도 빠뜨리지 않고 담는다).
TIE_MD = ("[51차 MA 동률 판정] 축이 다르므로 **둘 다 대표다** — 어느 쪽을 쓸지는 해석자가 정한다. "
          "이 행이 대표로 뽑혀 있다. 이 행 = 2.4545e+08 Pa [direction=\"MD (machine direction)\"]. "
          "동률 경쟁행 = 1.8961e+08 Pa [direction=\"CD (cross direction)\"]. 갈린 조건키 = direction.")
TIE_CD = ("[51차 MA 동률 판정] 축이 다르므로 **둘 다 대표다** — 어느 쪽을 쓸지는 해석자가 정한다. "
          "이 행은 대표와 순위가 같다(적재 순서로 밀렸다). 이 행 = 1.8961e+08 Pa [direction=\"CD (cross direction)\"]. "
          "동률 경쟁행 = 2.4545e+08 Pa [direction=\"MD (machine direction)\"]. 갈린 조건키 = direction.")
NA_TIE_REASON_MD = ("조건 어휘 통일(브리프 547·551) — 값·단위·등급·method·출처는 그대로다. direction 정규화 → MD | "
                    "앞 정정 사유(51차 MA): 대표값 동률 판정 — 값·등급·method·출처를 하나도 바꾸지 않고 "
                    "**왜 갈렸는지**만 조건에 적는다(브리프 545). 부류 다른조건 — 방향.")
NA_TIE_REASON_TD = ("조건 어휘 통일(브리프 547·551) — 값·단위·등급·method·출처는 그대로다. direction 정규화 → TD | "
                    "앞 정정 사유(51차 MA): 대표값 동률 판정 — 값·등급·method·출처를 하나도 바꾸지 않고 "
                    "**왜 갈렸는지**만 조건에 적는다(브리프 545). 부류 다른조건 — 방향.")
PA_REASON_MD = ("조건 어휘 통일 잔여(브리프 547·551·581) — 값·단위·등급·method·출처는 그대로다. "
                "standard→test_standard · direction 정규화 → MD.")
PA_REASON_MD_NOSTD = ("조건 어휘 통일 잔여(브리프 547·551·581) — 값·단위·등급·method·출처는 그대로다. "
                      "direction 정규화 → MD.")
PA_REASON_TD_NOSTD = ("조건 어휘 통일 잔여(브리프 547·551·581) — 값·단위·등급·method·출처는 그대로다. "
                      "direction 정규화 → TD.")
DUP_NOTE = ("52차 NB — 같은 출처의 같은 측정을 두 번 적재했다(조건 키 표기만 달랐다). "
            "값은 지우지 않고 표시만 한다")

tlx8 = {
    "batch": BATCH,
    "note": ("Taconic TLX-8 의 `ASTM D 902` 다섯 행에 **시험모드를 박는다**. 규격 본문의 수록 시험을 "
             "전수 대조해 **인장으로 확정**했다 — 키 이동은 없다(이미 제 키에 있다). "
             "D 3039 행은 원래 모호하지 않아 손대지 않았고, 기존 조건칸은 한 칸도 지우지 않았다."),
    "corrections": [
        # ── mechanical.youngs_modulus (D902) ─────────────────────────────────
        corr("5414", {
            "direction": "MD", "test_standard": "ASTM D 902", "direction_verbatim": "MD",
            "test_standard_before_correction": None, "direction_verbatim_before_correction": None,
            "standard_before_correction": "ASTM D 902",
            "correction_reason": PA_REASON_MD, "corrected_by": "54차 PA",
        }),
        corr("6353", {
            "direction": "MD", "test": "ASTM D 902",
            "verdict_duplicate_of": "direction=\"MD\" | standard=\"ASTM D 902\"",
            "verdict_duplicate_note": DUP_NOTE,
            "direction_verbatim": "MD (machine direction)",
            "direction_before_correction": "MD (machine direction)",
            "direction_verbatim_before_correction": None,
            "correction_reason": PA_REASON_MD_NOSTD, "corrected_by": "54차 PA",
        }),
        corr("6354", {
            "direction": "TD", "test": "ASTM D 902",
            "direction_verbatim": "CD (cross direction)",
            "direction_before_correction": "CD (cross direction)",
            "direction_verbatim_before_correction": None,
            "correction_reason": PA_REASON_TD_NOSTD, "corrected_by": "54차 PA",
        }),
        # ── mechanical.tensile_strength (D902) — 같은 규격, 같은 모드 ─────────
        corr("6274", {
            "direction": "MD", "test": "ASTM D 902",
            "verdict_tie_axis": "51차 MA — 다른조건 — 방향", "verdict_tie_note": TIE_MD,
            "verdict_tie_axis_before_correction": None, "verdict_tie_note_before_correction": None,
            "correction_reason": NA_TIE_REASON_MD, "corrected_by": "52차 NA",
            "direction_verbatim": "MD (machine direction)",
            "direction_verbatim_before_correction": None,
            "direction_before_correction": "MD (machine direction)",
        }),
        corr("6275", {
            "direction": "TD", "test": "ASTM D 902",
            "verdict_tie_axis": "51차 MA — 다른조건 — 방향", "verdict_tie_note": TIE_CD,
            "verdict_tie_axis_before_correction": None, "verdict_tie_note_before_correction": None,
            "correction_reason": NA_TIE_REASON_TD, "corrected_by": "52차 NA",
            "direction_verbatim": "CD (cross direction)",
            "direction_verbatim_before_correction": None,
            "direction_before_correction": "CD (cross direction)",
        }),
    ],
}


def dump(name: str, doc: dict) -> None:
    p = OUT / name
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(m.get("properties", [])) for m in doc.get("materials", []))
    n += len(doc.get("corrections", []))
    print(f"  {name}: {n} 행")


if __name__ == "__main__":
    dump("kc75_01_chukoh_4grades.json", chukoh)
    dump("kc75_02_astra_flexmod.json", astra)
    dump("kc75_03_tlx8_d902_mode.json", tlx8)
