# 74차 JB 수집 배치 산출물 생성기 — Elite Material 신규 4등급 · Sumitomo 연마캐리어 2등급 · 코어7 판정
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))
BATCH = "74차 JB"
LBIN = 175.126835          # 1 lb/in -> N/m
C2K = 273.15

def MPa(v): return v * 1e6
def GPa(v): return v * 1e9
def ppm(v): return v * 1e-6

EMC_URL_BASE = "https://www.emctw.com/upload/website/item/"
EMC_NOTE = ("**세 로케일(`zh-TW`·`zh-CN`·`en-global`) 제품목록이 서빙하는 PDF URL 목록 43개가 완전히 같다**"
            "(74차 JB 가 셋을 각각 받아 정렬 비교 — diff 0). 68차 DC 의 「세 로케일이 같은 PDF 를 서빙한다」는 "
            "결론이 2026-09-13 에도 유지된다. 로컬 사본과 벤더 현행본의 md5 도 같다.")

def prop(key, value, unit, tier, cond, notes, method="measured"):
    return {"key": key, "value": value, "unit": unit, "method": method,
            "tier": tier, "conditions": cond, "notes": notes}

# ─────────────────────────────────────────────────────────────────────────────
# ① Elite Material 신규 4등급
# ─────────────────────────────────────────────────────────────────────────────
EM = [
 dict(id="EM-390", pair="EM-39B", pdf="EM-390 Datasheet-20240716_24081911789.pdf",
      title="High Tg / Low Dk / Halogen Free",
      local="/data/paper_patent_corpus/standards_appnotes/pcb/EMC_EM-390_Datasheet_20240716.pdf",
      slash="IPC-4101 /127, /128, /130; IPC-4103 /240, /540",
      tg=[("TMA", 165), ("DMA", 190)], tg_dsc="N/A",
      cte_xy=(12, 13), cte_z1=(35, 40), cte_z2=(160, 180), zexp=2.2, td=385,
      k=0.49, k_method="ASTM D5470",
      dk=[("1GHz", 4.0, 3.5), ("10GHz", 3.8, 3.3)],
      df=[("1GHz", 0.007, 0.008), ("10GHz", 0.011, 0.012)],
      wa=0.08,
      peel=[("0.5 oz HTE", "As Received", 6.0), ("0.5 oz HTE", "After Thermal Stress", 6.0)],
      flex_str=[("warp", 510, 570), ("fill", 450, 500)], flex_mod=None,
      feat="Low Dk for impedance control. Low CTE and high modulus. Good peel strength and suitable for mSAP process."),
 dict(id="EM-526", pair="EM-526B", pdf="EM-526 Datasheet 20240716_24081910532.pdf",
      title="Low Loss / Low CTE / Halogen Free",
      local="/data/paper_patent_corpus/standards_appnotes/pcb/EMC_EM-526_Datasheet_20240716.pdf",
      slash="IPC-4103 /240, /540",
      tg=[("TMA", 230), ("DMA", 260)], tg_dsc="N/A",
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(120, 140), zexp=1.3, td=430,
      k=0.60, k_method="원문 시험법 칸이 비어 있다 — `IPC-TM-650` 열에 값 `0.60` 이 잘못 인쇄돼 있다(벤더 오식)",
      dk=[("1GHz", 4.0, 3.5), ("10GHz", 3.9, 3.4), ("10GHz(SPC)", 3.9, 3.4)],
      df=[("1GHz", 0.005, 0.006), ("10GHz", 0.007, 0.008), ("10GHz(SPC)", 0.007, 0.007)],
      wa=0.12,
      peel=[("RTF H oz", "As Received", 5.5), ("HVLP H oz", "As Received", 4.4)],
      flex_str=None, flex_mod=[("warp", 24, 26), ("fill", 23, 25)],
      feat="Low Df for excellent electrical performance. Low CTE for X/Y/Z-axis direction. For high reliability applications."),
 dict(id="EM-528", pair="EM-528B", pdf="EM-528 Datasheet 20240716_24081910773.pdf",
      title="High Tg / Very Low Loss / Halogen Free",
      local="/data/paper_patent_corpus/standards_appnotes/pcb/EMC_EM-528_Datasheet_20240716.pdf",
      slash="IPC-4103 /240, /540",
      tg=[("TMA", 220), ("DMA", 250)], tg_dsc="N/A",
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(130, 150), zexp=1.4, td=420,
      k=0.6, k_method="ASTM D5470",
      dk=[("1GHz", 4.0, 3.6), ("10GHz", 3.9, 3.5), ("10GHz(SPC)", 3.9, 3.5)],
      df=[("1GHz", 0.0047, 0.0044), ("10GHz", 0.0061, 0.0058), ("10GHz(SPC)", 0.0050, 0.0046)],
      wa=0.11,
      peel=[("RTF H oz", "As Received", 5.0), ("HVLP H oz", "As Received", 4.0)],
      flex_str=None, flex_mod=[("warp", 24, 26), ("fill", 23, 25)],
      feat="Low Df for excellent electrical performance. Low CTE for X/Y/Z-axis direction. Multiple lamination and high thermal reliability applications."),
 dict(id="EM-528K", pair="EM-528BK", pdf="EM-528K Datasheet 20240716_24081910250.pdf",
      title="High Tg / Ultra Low Loss / Halogen Free",
      local="/data/paper_patent_corpus/standards_appnotes/pcb/EMC_EM-528K_Datasheet_20240716.pdf",
      slash="IPC-4103 /240, /540",
      tg=[("TMA", 220), ("DMA", 250)], tg_dsc="N/A",
      cte_xy=(9, 10), cte_z1=(25, 30), cte_z2=(130, 150), zexp=1.4, td=420,
      k=0.58, k_method="ASTM D5470",
      dk=[("1GHz", 3.5, 3.3), ("10GHz", 3.4, 3.2), ("10GHz(SPC)", 3.4, 3.2)],
      df=[("1GHz", 0.0031, 0.0032), ("10GHz", 0.0041, 0.0042), ("10GHz(SPC)", 0.0031, 0.0032)],
      wa=0.11,
      peel=[("RTF H oz", "As Received", 5.0), ("HVLP H oz", "As Received", 4.0)],
      flex_str=None, flex_mod=[("warp", 24, 26), ("fill", 23, 25)],
      feat="Very low Df for excellent electrical performance. Low CTE for X/Y/Z-axis direction. Multiple lamination and high thermal reliability applications."),
]

EM_ABSENT = {
 "physical.density": None, "mechanical.youngs_modulus": None, "mechanical.poisson_ratio": None,
 "thermal.specific_heat": None, "mechanical.tensile_strength": None,
}

def em_absent_reason(g, key):
    label = {"physical.density": "`Density`·`Specific Gravity`",
             "mechanical.youngs_modulus": "`Young's Modulus`·`Tensile Modulus`",
             "mechanical.poisson_ratio": "`Poisson`",
             "thermal.specific_heat": "`Specific Heat`",
             "mechanical.tensile_strength": "`Tensile Strength`"}[key]
    return ("**[74차 JB]** 이 등급의 벤더 데이터시트를 열었고 " + label + " 행이 **없다.**\n\n"
      "**연 문서** — `" + g["local"] + "` (Elite Material Co., Ltd. `" + g["id"] + " / " + g["pair"] +
      "` Datasheet, Rev 2024 July, 1쪽). 이 시트의 `Basic Laminate Property` 표는 **한 장에 전부 인쇄되고** "
      "행 구성이 이렇다 — Tg(DSC/TMA/DMA) · CTE X/Y · CTE Z(<Tg, >Tg) · Z-axis Expansion · Td · T288 · "
      "Thermal Conductivity · Dk · Df · Volume Resistivity · Surface Resistivity · Water Absorption · "
      "Peel Strength · " + ("Flexural Modulus" if g["flex_mod"] else "Flexural Strength") + " · Flame Resistance. "
      "**밀도·영률·포아송비·비열·인장강도 행은 이 표에 자리 자체가 없다.**\n\n"
      "**벤더 전수** — 74차 JB 가 `emctw.com` 제품목록이 서빙하는 **데이터시트 43장을 전부 받아** 전문 토큰 검사를 "
      "돌렸다(단어 단위). `density` 0 · `specific gravity` 0 · `specific heat` 0 · `Young` 0 · `tensile` 0 · "
      "`Poisson` 0 — **43장 중 한 장도 없다.** 이 벤더의 기계축은 `Flexural Strength`(구형 등급)와 "
      "`Flexural Modulus`(저손실 신형 등급) 둘뿐이고, 둘 다 **IPC-TM-650 2.4.4 = 굽힘**이라 인장 칸에 옮길 수 없다.\n\n"
      "**주의 — 구(句) 검색은 이 시트에서 거짓 음성을 낸다.** `pdftotext` 가 두 낱말 행이름을 두 줄로 쪼개 "
      "(`Flexural` / `Modulus`) 뽑는다. `\"flexural modulus\"` 로 찾으면 43장 전부 0건이 나오는데 **실제로는 "
      "10장에 있다.** 72차 HD 가 ELC HTML 의 `引っ張り<br>強さ` 에서 밟은 것과 같은 함정이다 — **낱말 단위로 세라.**\n\n"
      "**로케일** — " + EMC_NOTE)

def build_em():
    mats = []
    for g in EM:
        url = EMC_URL_BASE + g["pdf"].replace(" ", "%20")
        src = {"kind": "datasheet",
               "title": "Elite Material Co., Ltd. — " + g["id"] + " / " + g["pair"] + " Datasheet (" + g["title"] + "), Rev 2024 July",
               "url": url,
               "publisher": "Elite Material Co., Ltd. (台光電子材料股份有限公司)",
               "year": 2024,
               "local_path": g["local"],
               "url_note": "2026-09-13 에 벤더 제품목록(`/en-global/product_name/index`)에서 직접 받았고 로컬 사본과 md5 가 같다. " + EMC_NOTE}
        P = []
        vb = "원문 verbatim"
        # Tg
        for meth, v in g["tg"]:
            P.append(prop("thermal.glass_transition", round(v + C2K, 2), "K", 1,
                          {"method_detail": meth, "test_standard": "IPC-TM-650 2.4.24" if meth == "TMA" else "IPC-TM-650 2.4.24.4"},
                          vb + ": `Tg | " + str(v) + " | oC | " + meth + "`. 환산 " + str(v) + " ℃ + 273.15 = " +
                          str(round(v + C2K, 2)) + " K. **같은 표의 DSC 칸은 `N/A` 로 인쇄돼 있어 행을 만들지 않았다.** "
                          "TMA 와 DMA 는 서로 다른 시험이라 두 행으로 갈랐고 평균 내지 않았다."))
        # CTE x/y
        for ax, v in (("X", g["cte_xy"][0]), ("Y", g["cte_xy"][1])):
            P.append(prop("thermal.expansion_linear", ppm(v), "1/K", 1,
                          {"axis": "in-plane (" + ax + ")", "regime": "below Tg (alpha1)",
                           "method_detail": "TMA", "test_standard": "IPC-TM-650 2.4.24.5"},
                          vb + ": `CTE, X/Y-axis | " + str(g["cte_xy"][0]) + "/" + str(g["cte_xy"][1]) +
                          " | ppm/ oC | < Tg, TMA`. 원문이 `X/Y` 를 슬래시로 갈라 인쇄하므로 두 축을 두 행으로 나눴다. "
                          "환산 " + str(v) + " ppm/℃ x 1e-6 = " + repr(ppm(v)) + " 1/K."))
        # CTE z
        for reg, (lo, hi), lbl in ((("below Tg (alpha1)"), g["cte_z1"], "< Tg, TMA"),
                                   (("above Tg (alpha2)"), g["cte_z2"], "> Tg, TMA")):
            for b, v in (("lower", lo), ("upper", hi)):
                P.append(prop("thermal.expansion_linear", ppm(v), "1/K", 1,
                              {"axis": "through-thickness (Z)", "regime": reg, "bound": b,
                               "method_detail": "TMA", "test_standard": "IPC-TM-650 2.4.24"},
                              vb + ": `CTE, Z-axis | " + str(lo) + "~" + str(hi) + " | ppm/ oC | " + lbl +
                              "`. **인쇄 구간이라 평균 내지 않고 두 행(`bound`)으로 갈랐다.** 환산 " + str(v) +
                              " ppm/℃ x 1e-6 = " + repr(ppm(v)) + " 1/K."))
        # Z expansion
        P.append(prop("thermal.expansion_total", g["zexp"] / 100.0, "1", 1,
                      {"axis": "through-thickness (Z)", "temperature_range_c": "50-260",
                       "test_standard": "IPC-TM-650 2.4.24"},
                      vb + ": `Z-axis Expansion | " + str(g["zexp"]) + " | % | 50~260 oC`. 환산 " +
                      str(g["zexp"]) + " % / 100 = " + repr(g["zexp"] / 100.0) + " (무차원)."))
        # Td
        P.append(prop("thermal.decomposition_temp", round(g["td"] + C2K, 2), "K", 1,
                      {"method_detail": "TGA, 5% weight loss", "test_standard": "IPC-TM-650 2.4.24.6"},
                      vb + ": `Td | " + str(g["td"]) + " | oC | TGA (5% W.L)`. 환산 " + str(g["td"]) +
                      " ℃ + 273.15 = " + str(round(g["td"] + C2K, 2)) + " K."))
        # T288
        for st in ("Clad", "Etched"):
            P.append(prop("thermal.time_to_delamination", 3600.0, "s", 1,
                          {"temperature_c": 288, "specimen_state": st, "bound": "lower",
                           "test_standard": "IPC-TM-650 2.4.24.1"},
                          vb + ": `T288 | >60 | min. | " + st + "`. **원문이 부등호(`>60`)로 인쇄한 하한이다** — "
                          "`bound: lower` 로 넣었고 상한 행은 만들지 않았다. 환산 60 min x 60 = 3600 s."))
        # k
        P.append(prop("thermal.conductivity", g["k"], "W/(m*K)", 1,
                      {"test_standard": g["k_method"], "test_geometry": "through-thickness (laminate stack)"},
                      vb + ": `Thermal Conductivity | " + str(g["k"]) + " | W/m.K`. 단위가 이미 W/(m·K) 라 환산이 없다. "
                      "시험법 칸 원문: `" + g["k_method"] + "`."))
        # Dk / Df
        for key, rows, label in (("electrical.dielectric_constant", g["dk"], "Dk"),
                                 ("electrical.dissipation_factor", g["df"], "Df")):
            for freq, v50, v70 in rows:
                for rc, v in (("50%", v50), ("70%", v70)):
                    P.append(prop(key, v, "1", 1,
                                  {"frequency": freq.replace("(SPC)", ""), "resin_content": rc,
                                   "conditioning": "C-24/23/50",
                                   "method_detail": "SPC method" if "SPC" in freq else "Cavity Resonator",
                                   "test_standard": "IPC-TM-650 2.5.5.9"},
                                  vb + ": `" + label + " (R/C: 50/70%) | " + freq + " | " + str(v50) + "/" + str(v70) +
                                  "`. **원문이 수지함량 50%/70% 두 값을 슬래시로 갈라 인쇄한다** — 두 행으로 나누고 "
                                  "`resin_content` 에 박았다. 평균 0건."))
        # water absorption
        P.append(prop("chemical.water_absorption_24h", g["wa"] / 100.0, "1", 1,
                      {"conditioning": "E-1/105+D-24/23", "test_standard": "IPC-TM-650 2.6.2.1"},
                      vb + ": `Water Absorption | " + str(g["wa"]) + " | % | E-1/105+D-24/23`. 환산 " +
                      str(g["wa"]) + " % / 100 = " + repr(g["wa"] / 100.0) + "."))
        # peel
        for foil, cond, v in g["peel"]:
            P.append(prop("interface.peel_strength", round(v * LBIN, 2), "N/m", 1,
                          {"foil": foil, "conditioning": cond, "test_standard": "IPC-TM-650 2.4.8"},
                          vb + ": `Peel Strength | " + foil + " | " + str(v) + " | lb/in | " + cond +
                          "`. 환산 " + str(v) + " lb/in x 175.126835 = " + str(round(v * LBIN, 2)) +
                          " N/m; 되돌리면 " + str(round(v * LBIN, 2)) + " / 175.126835 = " + str(v) + "."))
        # flexural
        if g["flex_str"]:
            for d, lo, hi in g["flex_str"]:
                for b, v in (("lower", lo), ("upper", hi)):
                    P.append(prop("mechanical.flexural_strength", MPa(v), "Pa", 1,
                                  {"direction": d, "conditioning": "As Received", "bound": b,
                                   "test_standard": "IPC-TM-650 2.4.4", "test_mode": "flexural (3-point bend)"},
                                  vb + ": `Flexural Strength | " + d.capitalize() + " | " + str(lo) + "~" + str(hi) +
                                  " | MPa | As Received`. **인쇄 구간이라 두 행(`bound`)으로 갈랐다.** 환산 " +
                                  str(v) + " MPa x 1e6 = " + repr(MPa(v)) + " Pa. **이 행은 굽힘이다 — "
                                  "`mechanical.tensile_strength` 로 옮기지 마라**(IPC-TM-650 2.4.4)."))
        if g["flex_mod"]:
            for d, lo, hi in g["flex_mod"]:
                for b, v in (("lower", lo), ("upper", hi)):
                    P.append(prop("mechanical.flexural_modulus", GPa(v), "Pa", 1,
                                  {"direction": d, "conditioning": "As Received", "bound": b,
                                   "test_standard": "IPC-TM-650 2.4.4", "test_mode": "flexural (3-point bend)"},
                                  vb + ": `Flexural Modulus | " + d.capitalize() + " | " + str(lo) + "~" + str(hi) +
                                  " | GPa | As Received`. **인쇄 구간이라 두 행(`bound`)으로 갈랐다.** 환산 " +
                                  str(v) + " GPa x 1e9 = " + repr(GPa(v)) + " Pa. **굽힘탄성률이다 — "
                                  "`mechanical.youngs_modulus` 칸에 옮기지 않았다.** 68차 DC 가 Panasonic 여섯 등급에서 "
                                  "굽힘값을 영률 칸에 넣었다가 진짜 인장값과 12~23 % 어긋나는 것을 보고 전부 되돌린 자리다."))
        P.append(prop("thermal.flammability_ul94", "V-0", None, 1,
                      {"conditioning": "C-48/23/50", "test_standard": "UL-94"},
                      vb + ": `Flame Resistance | V-0 | C-48/23/50 | UL-94`."))

        nm = {"name": "Elite Material " + g["id"] + " / " + g["pair"] + " " + g["title"].replace(" / ", " ").replace("Halogen Free", "Halogen-Free") + " Laminate",
              "category": "composite",
              "description": ("台光電子材料(Elite Material Co., Ltd.) 동장적층판 `" + g["id"] + " / " + g["pair"] +
                 "` — " + g["title"] + ". 벤더 표기 특징: " + g["feat"] + " 적용 IPC 슬래시시트: " + g["slash"] + ". "
                 "**이 카드가 74차 JB 에 선 이유** — 68차 DC 가 이 벤더 다섯 등급(EM-370Z·EM-370(5)·EM-890·EM-888·EM-891)에 "
                 "영률 부재판정을 달면서 나머지 등급을 카드로 세우지 않았다. 이 등급은 벤더 시트가 "
                 "**열전도율과 CTE 를 인쇄**하므로 코어7 두 칸을 갖고 태어난다." +
                 ("  그리고 **DC 가 「이 벤더의 강도축은 Flexural Strength 하나다」라고 한 것이 이 신형 저손실 등급에서는 "
                  "성립하지 않는다 — `Flexural Modulus` 를 GPa 로 인쇄한다.** 다만 시험법이 IPC-TM-650 2.4.4(굽힘)이라 "
                  "영률 칸은 여전히 못 채운다." if g["flex_mod"] else "")),
              "attributes": {
                 "material_class": "copper-clad laminate (glass fabric / halogen-free epoxy)",
                 "subsystem": "pcb",
                 "role": "product",
                 "role_reason": "PCB 실부품 동장적층판. 벤더가 등급명으로 인쇄한 제품이다.",
                 "role_confidence": "high",
                 "manufacturer": "Elite Material Co., Ltd. (EMC, 台光電子材料)",
                 "product_series": "EM series copper-clad laminate",
                 "product_form": "copper-clad laminate / prepreg",
                 "aliases": [g["id"], g["pair"], "EMC " + g["id"], "Elite Material " + g["id"],
                             g["id"].replace("-", ""), g["pair"].replace("-", "")],
                 "grade_pair_note": "`" + g["id"] + "` 는 동장적층판(laminate), `" + g["pair"] +
                     "` 는 같은 수지계의 프리프레그(B-stage)다. 벤더가 한 시트에 두 품번을 묶어 인쇄하고 "
                     "**특성값은 한 벌뿐**이라 카드도 하나다.",
                 "ipc_slash_sheets": g["slash"],
                 "ul_file": "E150504",
                 "datasheet_revision": "Rev: 2024 July",
                 "core7_absent_from_vendor_sheet": "밀도·영률·포아송비·비열·인장강도 다섯 행이 이 시트에 없다. "
                     "벤더 데이터시트 43장 전수 검사에서도 0건이다(사유는 아래 판정 attributes 에 물성키별로 적었다).",
                 "locale_note": EMC_NOTE,
                 "core_absent_from_vendor_sheet": {k: em_absent_reason(g, k) for k in EM_ABSENT},
              }}
        mats.append({"new_material": nm, "source": src, "properties": P})
    return mats

# ─────────────────────────────────────────────────────────────────────────────
# ② Sumitomo 연마·랩핑 캐리어용 무피복 적층판 2등급
# ─────────────────────────────────────────────────────────────────────────────
SB_CARRIER_LOCAL_PDF = "/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_Sumilite-PL-EL_Catalog_ja_2026-09-09.pdf"
SB_CARRIER_LOCAL_TDS = "/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_ELC-4765-4768_TDS_en_2026-09-09.pdf"

CARRIER = [
 dict(id="EL-3700", flex=(650, 540), ins=("2E+11", "9E+10"), thick="0.4 - 2.0 mm",
      feat="シリコンウェハー、HDD研磨用途に長年の実績があるスタンダード材 / The standard material which is used for silicon wafer and HDD polishing carrier."),
 dict(id="EL-3700M", flex=(740, 580), ins=("4E+10", "3E+10"), thick="0.2 - 1.0 mm",
      feat="更なる板厚精度、表面平滑性が求められるキャリアへの対応材料 / Good accuracy for board thickness and surface smoothness for high performance polishing carrier."),
]

CARRIER_KEYS = ["physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
                "thermal.expansion_linear", "thermal.conductivity", "thermal.specific_heat",
                "mechanical.tensile_strength"]

def carrier_absent(g, key):
    lbl = {"physical.density": "`比重 Specific gravity`·`密度`",
           "mechanical.youngs_modulus": "`曲げ弾性率`·`引っ張り弾性率`·`Young's Modulus`(어떤 탄성률도)",
           "mechanical.poisson_ratio": "`ポアソン比`",
           "thermal.expansion_linear": "`熱膨張係数`·`CTE`",
           "thermal.conductivity": "`熱伝導率 Thermal conductivity`",
           "thermal.specific_heat": "`比熱`",
           "mechanical.tensile_strength": "`引っ張り強さ Tensile strength`"}[key]
    return ("**[74차 JB]** 이 등급의 벤더 문서 **두 종**을 전부 열었고 " + lbl + " 행이 **없다.**\n\n"
      "**연 문서 ①** — `" + SB_CARRIER_LOCAL_PDF + "` 인쇄 28쪽 `研磨キャリア用積層板 Polishing & lapping carrier "
      "EL-3700 / EL-3700M` 의 `一般特性 General Properties` 표. **이 PDF 는 Illustrator 아웃라인 벡터라 "
      "`pdftotext` 가 4쪽 전체에 0자를 준다** — 74차 JB 가 A3 네 쪽을 150 dpi 로 렌더해 눈으로 읽었다. "
      "표의 행은 여덟뿐이다: 色 Color · 厚み Thickness · 絶縁抵抗 Insulation resistance(2행) · "
      "曲げ強さ Flexural strength(たて/よこ) · 硬度 Hardness(Rockwell) · 吸水率 Water absorption · "
      "耐燃性 Flame retardancy · 納入サイズ Size.\n\n"
      "**연 문서 ②** — `" + SB_CARRIER_LOCAL_TDS + "` 2쪽 `Umclad glass epoxy lamnetes for polishing & lapping "
      "carrier`(원문 오식 그대로). 영문 TDS 인데 **행 구성이 ①과 완전히 같다**(Color · Thickness · Insulation "
      "resistance · Flexural strength · Hardness · Water absorption · Flame retardancy · Size). 이 쪽은 텍스트층이 "
      "살아 있어 토큰 검사를 돌렸다 — `density`·`gravity`·`modulus`·`Poisson`·`expansion`·`conductivity`·"
      "`specific heat`·`tensile` **전부 0건.**\n\n"
      "**같은 카탈로그의 형제 표와 대비된다** — 인쇄 26·27쪽의 PL/EL 적층판 표는 `比重 Specific gravity` 행을 "
      "갖는데(72차 HD 가 그 행으로 카드 넉 장을 세웠다) **연마캐리어 표에는 그 행이 없다.** 같은 벤더 같은 "
      "카탈로그 안에서 제품군별로 행 구성이 다르다 — 누락이 아니라 이 표의 설계다.\n\n"
      "**SDS 경로는 이 제품군에서 닫혀 있다** — 72차 HD 가 확인했다: Sumitomo 는 SDS 포털 자체가 없고"
      "(사이트맵 435링크에 `SDS` 적중 0), 고체 물품(article)인 적층판에는 SDS 의무가 없다. 74차 JB 는 "
      "이 경로에 시간을 쓰지 않았다.")

def build_carrier():
    mats = []
    for g in CARRIER:
        src = {"kind": "datasheet",
               "title": "住友ベークライト スミライト® 積層板カタログ 인쇄 28쪽 『研磨キャリア用積層板 EL-3700 / EL-3700M』 "
                        "(+ 영문 Technical Data Sheet 2쪽, 같은 등급)",
               "url": "https://www.sumibe.co.jp/ww-attaches/805.pdf",
               "publisher": "Sumitomo Bakelite Co., Ltd. (住友ベークライト株式会社)",
               "year": 2026,
               "local_path": SB_CARRIER_LOCAL_PDF,
               "url_note": "**이 PDF 는 아웃라인 벡터라 `pdftotext` 가 0자를 준다** — 값은 A3 쪽을 150 dpi 로 렌더해 "
                           "눈으로 읽었다. 같은 값이 `" + SB_CARRIER_LOCAL_TDS + "` 2쪽(텍스트층 살아 있음)에 "
                           "**독립으로 다시 인쇄돼 있어 두 문서로 교차검증했다** — 여덟 칸 전부 일치한다."}
        vb = "원문 verbatim"
        P = []
        for d, jp, v in (("lengthwise (たて)", "たて Lengthwise", g["flex"][0]),
                         ("widthwise (よこ)", "よこ Widthwise", g["flex"][1])):
            P.append(prop("mechanical.flexural_strength", MPa(v), "Pa", 1,
                          {"direction": d, "conditioning": "A (as received)", "specimen_thickness_mm": 1.0,
                           "test_mode": "flexural", "test_condition": "試験片は1.0mmtで測定 / Test piece thickness: 1.0 mmt"},
                          vb + ": `曲げ強さ Flexural strength | " + jp + " | MPa | " + str(v) + "` (" + g["id"] +
                          " 열). 원문이 **구간이 아니라 단일 값**으로 인쇄한 칸이다. 환산 " + str(v) + " MPa x 1e6 = " +
                          repr(MPa(v)) + " Pa. **굽힘강도다 — 인장강도 칸에 옮기지 않았다.** 같은 값이 영문 TDS 2쪽에 "
                          "`Flexural strength | Lengthwise/Widthwise | MPa` 로 똑같이 인쇄돼 있어 두 문서로 대조했다."))
        P.append(prop("mechanical.hardness_rockwell", 110.0, "HR", 1,
                      {"scale": "M", "test_method": "Rockwell (ロックウェル)", "specimen_thickness_mm": 1.0},
                      vb + ": `硬度 Hardness | ロックウェル Rockwell | HRM | 110`. 스케일 M 이다(`HRM`). "
                      "무차원 경도 눈금이라 환산이 없다. 영문 TDS 2쪽도 `Hardness | Rockwell | HRM | 110` 로 같다. "
                      "**두 등급이 같은 110 이다** — 벤더가 실제로 같은 값을 인쇄했다."))
        P.append(prop("chemical.water_absorption_24h", 0.0008, "1", 1,
                      {"conditioning": "E-24/50+D-24/23", "specimen_thickness_mm": 1.0},
                      vb + ": `吸水率 Water absorption | E-24/50+D-24/23 | % | 0.08`. 환산 0.08 % / 100 = 0.0008. "
                      "영문 TDS 2쪽도 같다. **두 등급이 같은 0.08 이다.**"))
        P.append(prop("thermal.flammability_ul94", "V-0 equivalent (V-0相当)", None, 1,
                      {"conditioning": "A / E-168/70", "test_standard": "UL method (UL法)"},
                      vb + ": `耐燃性（UL法）Flame retardancy (UL method) | A · E-168/70 | V-0相当 V-0 equivalent`. "
                      "**원문이 `相当 / equivalent` 라고 적는다 — UL 인증 등급이 아니라 동등 수준 표기다.** "
                      "그 표기를 값 문자열에 그대로 남겼다."))
        nm = {"name": "Sumitomo Bakelite Sumilite " + g["id"] + " (unclad glass epoxy polishing & lapping carrier laminate)",
              "category": "composite",
              "description": ("住友ベークライト(Sumitomo Bakelite) スミライト® 적층판 `" + g["id"] +
                 "` — 研磨キャリア用積層板 / polishing & lapping carrier (무피복 유리에폭시 적층판). 벤더 표기: " +
                 g["feat"] + " **72차 HD 가 세운 PL/EL 넉 장과 같은 카탈로그(인쇄 25~32쪽)의 마지막 제품군인데 "
                 "HD 가 카드로 세우지 않고 남긴 두 등급이다.** 실리콘 웨이퍼·HDD 연마 공정의 캐리어 판으로, "
                 "PCB 재료가 아니라 **공정 치구재**다. 74차 JB 가 카탈로그 네 쪽을 전부 렌더해 훑다가 찾았고, "
                 "같은 등급의 **영문 Technical Data Sheet** 가 로컬에 이미 있어 두 문서로 교차검증했다."),
              "attributes": {
                 "material_class": "unclad glass epoxy laminate (無銅張ガラスエポキシ積層板), polishing carrier grade",
                 "subsystem": "pcb",
                 "role": "product",
                 "role_reason": "벤더가 등급명으로 인쇄해 파는 실제품 적층판이다. 다만 **PCB 기판재가 아니라 "
                     "반도체·HDD 연마공정의 캐리어 치구재**이므로 PCB 격자에서 동장적층판과 섞어 읽으면 안 된다.",
                 "role_confidence": "high",
                 "manufacturer": "Sumitomo Bakelite Co., Ltd. (住友ベークライト株式会社)",
                 "product_series": "スミライト® (Sumilite) EL laminate sheets",
                 "product_form": "unclad laminate sheet (" + g["thick"] + " thick)",
                 "aliases": [g["id"], "Sumilite " + g["id"], "スミライト " + g["id"], g["id"].replace("-", "")],
                 "not_to_be_confused_with": "`" + g["id"] + "`(연마캐리어용 무피복재)는 `EL-3762`(FR-4 그레이드 "
                     "무피복 적층판)·`ELC-47xx`(동장적층판)와 **다른 제품이다.** EL-3762 의 比重 1.92 를 이 카드에 "
                     "옮기면 틀린 값이다 — 이 등급의 比重 은 **어느 문서에도 인쇄돼 있지 않다.**",
                 "insulation_resistance_printed": "이 표는 `絶縁抵抗 Insulation resistance` 를 A 조건 " + g["ins"][0] +
                     " Ω · D-2/100 조건 " + g["ins"][1] + " Ω 로 인쇄한다. **우리 분류에 이 측정에 맞는 키가 없어 "
                     "행을 만들지 않았다** — `electrical.surface_resistivity`(Ω)나 `electrical.resistivity_volume`"
                     "(Ω·m)은 다른 측정이다. 값을 버리지 않도록 여기 적어 둔다.",
                 "core7_absent_from_vendor_sheet": "이 제품군 표에는 코어7 일곱 칸이 **한 칸도 없다.** 있는 것은 "
                     "色·厚み·絶縁抵抗·曲げ強さ·硬度·吸水率·耐燃性·納入サイズ 여덟 행뿐이다. "
                     "**이 카드는 코어7 을 0/7 로 갖고 태어나며 일곱 칸 전부에 부재판정이 걸려 있다** — "
                     "다음 파동이 이 칸들을 「진짜 남은 것」으로 다시 세지 않게 하려는 것이다.",
                 "core_absent_from_vendor_sheet": {k: carrier_absent(g, k) for k in CARRIER_KEYS},
              }}
        mats.append({"new_material": nm, "source": src, "properties": P})
    return mats

if __name__ == "__main__":
    a = {"batch": BATCH, "materials": build_em()}
    json.dump(a, open(os.path.join(OUT, "jb74_01_elite_material_new_grades.json"), "w"),
              ensure_ascii=False, indent=1)
    b = {"batch": BATCH, "materials": build_carrier()}
    json.dump(b, open(os.path.join(OUT, "jb74_02_sumitomo_polishing_carriers.json"), "w"),
              ensure_ascii=False, indent=1)
    for nm, d in (("01 Elite Material", a), ("02 Sumitomo carrier", b)):
        print(nm, "카드", len(d["materials"]), "· 물성행", sum(len(m["properties"]) for m in d["materials"]))
