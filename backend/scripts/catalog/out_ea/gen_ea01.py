# 69차 EA — Panasonic 특성일람표(2013 인쇄쪽 17~18 · 2021 인쇄쪽 9~10)의 전 열을 ea01_materials.json 으로 옮긴다
"""표 전수 전사기.

두 문서만 읽는다.
  A = 2013 「電子回路基板材料」総合カタログ 인쇄쪽 17~18 `特性一覧表《参考値》板厚：1.6mm`
  B = 2021-03 「特性一覧表《参考値》」 2쪽 (인쇄쪽 9~10)

표에서 읽은 원값을 그대로 담고, SI 환산은 여기서 한 번만 한다.
빈칸(−)은 아예 담지 않는다. DB 에 이미 t1 로 같은 조건이 들어 있는 칸도 담지 않는다
(그 판정은 ea00_report.md §2 에 칸별로 적었다).
"""
from __future__ import annotations
import json
from pathlib import Path

OUT = Path(__file__).with_name("ea01_materials.json")

SRC_2013 = {
    "kind": "datasheet",
    "title": ("Panasonic 「電子回路基板材料」総合カタログ (PDF 내부 제목 `Electronic Materials`, "
              "저자 `Panasonic Corporation`, 160쪽, 2013-03-08 생성) — 인쇄쪽 16~18 의 "
              "`特性一覧表《参考値》板厚：1.6mm` 두 쪽짜리 표. 그 오른쪽 절반(인쇄쪽 18)에 "
              "`ヤング率（引張り） ASTM D3039` 열이 있다"),
    "url": "https://www.relianceems.com/static/upload/file/20260123/1769167011136894.pdf",
    "publisher": "Panasonic Corporation",
    "year": 2013,
    "local_path": ("/data/paper_patent_corpus/standards_appnotes/pcb/"
                   "Panasonic_ElectronicMaterials_catalog_2013_JP_YoungsModulus_ASTM-D3039_table.pdf"),
}

# 2021 판은 URL 을 못 찾았다(industrial.panasonic.com 이 이 실행환경에서 403·타임아웃).
# **URL 을 지어내지 않는다** — 제목·발행처·연도·로컬경로만 적는다.
SRC_2021 = {
    "kind": "datasheet",
    "title": ("Panasonic 「電子回路基板材料」 特性一覧表《参考値》 2쪽 (인쇄쪽 9~10, PDF 2021-03-08 생성) — "
              "`曲げ弾性係数 JIS C 6481` · `ヤング率(引張りモード) ASTM D3039` · "
              "`ポアソン比 JIS K 7161-1 23±3℃` 열을 나란히 인쇄한다. "
              "머리글 단서: 板厚 1.6mm、ポアソン比 0.8mm、ヤング率(引張りモード) 0.1mm、貫層耐電圧 0.2mm"),
    "publisher": "Panasonic Corporation",
    "year": 2021,
    "local_path": ("/data/paper_patent_corpus/standards_appnotes/pcb/"
                   "Panasonic_CircuitBoardMaterials_PropertyList_FlexModulus_YoungsModulus_Poisson_2021-03.pdf"),
}

NOTE_TAIL_2013 = ("출처: 2013 총합카탈로그 인쇄쪽 17~18 `特性一覧表《参考値》`. "
                  "머리글 verbatim `板厚：1.6mm（R-1515B, R-1515Sは0.8mm）、貫層耐電圧：0.2mm`, "
                  "각주 verbatim `注）上記の数値は参考値であり特性を保証するものではありません。`. "
                  "열 어긋남 검증: 300 dpi 렌더를 눈으로 읽어 pdftotext -layout 추출과 칸 단위로 대조했고, "
                  "같은 행의 Td·CTE·Tg(DSC)·曲げ弾性係数 가 DB 에 이미 든 다른 Panasonic 문서 값과 전부 일치한다.")
NOTE_TAIL_2021 = ("출처: 2021-03 특성일람표 인쇄쪽 9~10. "
                  "머리글 verbatim `板厚: 1.6mm、ポアソン比: 0.8mm、ヤング率(引張りモード): 0.1mm、貫層耐電圧: 0.2mm`, "
                  "각주 verbatim `注) 上記の数値は参考値であり特性を保証するものではありません。`. "
                  "열 어긋남 검증: 300 dpi 렌더를 눈으로 읽어 추출과 대조했고, 2013 판과 겹치는 5등급이 칸마다 같은 값을 준다.")


def C2K(c: float) -> float:
    return round(c + 273.15, 2)


def P(key, value, unit, cond, notes, tier=1, method="measured"):
    return {"key": key, "value": value, "unit": unit, "method": method,
            "tier": tier, "conditions": cond, "notes": notes}


# ── 2013 표 원값 ─────────────────────────────────────────────────────────────
# grade: 比重, 比熱[J/kg℃], 熱伝導率[W/m・K], ポアソン比, TgTMA, TgDSC, TgDMA, Td[℃],
#        曲げ縦, 曲げ横, ヤング縦, ヤング横[GPa], Dk1M, Dk1G, Df1M, Df1G, 貫層[kV/mm]
T2013 = {
    "R-5775":  dict(sg=1.82, cp=880, k=0.42, nu=0.2, tma=None, dsc=185, dma=210, td=410,
                    fx=(20, 19), ym=(16.3, 14.3), dk=(3.8, 3.7), df=(0.002, 0.002), ds=69),
    "R-1755V": dict(sg=1.96, cp=910, k=0.53, nu=0.2, tma=165, dsc=173, dma=190, td=350,
                    fx=(24, 22), ym=(20.3, 18.2), dk=(4.7, 4.4), df=(0.015, 0.016), ds=70),
    "R-1755D": dict(sg=1.98, cp=900, k=0.63, nu=0.2, tma=154, dsc=163, dma=185, td=345,
                    fx=(23, 21), ym=(19.2, 17.8), dk=(4.9, 4.4), df=(0.016, 0.016), ds=70),
    "R-1755M": dict(sg=2.00, cp=930, k=0.57, nu=0.2, tma=150, dsc=153, dma=175, td=355,
                    fx=(24, 22), ym=(20.5, 19.0), dk=(5.1, 4.6), df=(0.015, 0.014), ds=70),
    "R-1755E": dict(sg=1.98, cp=930, k=0.55, nu=0.2, tma=133, dsc=133, dma=153, td=370,
                    fx=(24, 22), ym=(20.0, 18.5), dk=(5.1, 4.6), df=(0.015, 0.013), ds=70),
    "R-1566":  dict(sg=2.00, cp=950, k=0.62, nu=0.2, tma=145, dsc=148, dma=170, td=350,
                    fx=(24, 22), ym=(20.9, 19.8), dk=(5.2, 4.6), df=(0.010, 0.010), ds=70),
    "R-1766":  dict(sg=1.91, cp=920, k=0.38, nu=0.2, tma=140, dsc=140, dma=150, td=315,
                    fx=(23, 21), ym=(17.8, 16.5), dk=(4.7, 4.3), df=(0.015, 0.016), ds=64),
}

# ── 2021 표 원값 (2013 에 없는 등급만) ─────────────────────────────────────────
T2021 = {
    "R-1566S":   dict(k=0.62, nu=0.2, tma=170, dsc=175, dma=195, td=355,
                      fx=(24, 22), ym=(20.7, 19.7), dk=(5.2, 4.7), df=(0.011, 0.010), ds=70),
    "R-5785(N)": dict(k=0.40, nu=None, tma=None, dsc=200, dma=210, td=400,
                      fx=(19, 18), ym=(13.5, 11.6), dk=(3.4, 3.4), df=(0.001, 0.001), ds=None),
}

SPEC_2013 = "laminate, 板厚 1.6 mm"
SPEC_2013_DS = "laminate, 板厚 0.2 mm"          # 貫層耐電圧만 0.2 mm
SPEC_2021 = "laminate, 板厚 1.6 mm"
SPEC_2021_NU = "laminate, 板厚 0.8 mm"          # 2021 판은 포아송비를 0.8 mm 로 잰다
SPEC_2021_YM = "laminate, 板厚 0.1 mm"          # 2021 판은 인장 영률을 0.1 mm 로 잰다
SPEC_2021_DS = "laminate, 板厚 0.2 mm"

DIRS = (("warp", "縦方向", "MD"), ("fill", "横方向", "TD"))
DIRS21 = (("warp", "タテ", "MD"), ("fill", "ヨコ", "TD"))


# 이미 든 행과 숫자가 겹치는 칸에 붙이는 경고. **행을 고치지 않고 표시만 남긴다** —
# 키 이동 경로가 적재기에 없어서(46차 HC) 다음 배치 몫이다. ea00_report.md §5 참조.
WARN_FX = {
    "R-5775": ("주의 — 재료 232 의 `mechanical.youngs_modulus` 행 10440·10441 이 제품페이지의 "
               "19/18 GPa 를 `test: flexural modulus` 로 달고 **영률 칸에** 들어 있다. "
               "그 19/18 은 이 표에서 **R-5775(N)** 의 굽힘값이고 플레인 R-5775 의 굽힘은 20/19 다 — "
               "제품페이지 값이 (N) 등급일 가능성이 높다. 여기 넣는 20/19 는 플레인 R-5775 행이다. "),
    "R-5785(N)": ("주의 — 재료 233 의 `mechanical.youngs_modulus` 행 10448·10449 가 같은 19/18 GPa 를 "
                  "`test: flexural modulus, grade: R-5785(N)` 로 달고 **영률 칸에** 들어 있다. "
                  "숫자가 겹치는 것은 같은 굽힘값이 두 키에 있기 때문이다 — 이 행이 제 자리이고 "
                  "저 두 행은 키 이동이 필요하다(적재기에 이동 경로가 없다). "),
}


def rows_2013(g: str, want: set) -> list:
    """2013 표에서 `want` 로 지정한 칸만 뽑는다."""
    d = T2013[g]
    out = []
    if "nu" in want:
        out.append(P("mechanical.poisson_ratio", d["nu"], "1",
                     {"test_standard": "JIS K7113", "temperature_c": 23, "specimen": SPEC_2013},
                     f"원문 verbatim — `ポアソン比 / 試験方法 JISK7113 / 処理条件 23±3℃ / 単位 − / {g} … {d['nu']}`. "
                     f"무차원이라 환산 없다(단위 정의 `1`). 시험조건 23±3℃ 를 temperature_c 23 으로 옮겼다. "
                     f"굽힘·인장 열과 나란히 인쇄된 독립 열이고 그 등급 행에 찍혀 있다. " + NOTE_TAIL_2013))
    if "sg" in want:
        v = round(d["sg"] * 1000, 1)
        out.append(P("physical.density", v, "kg/m^3",
                     {"test_standard": "JIS K6911", "specimen": SPEC_2013},
                     f"원문 verbatim — `比重 / 試験方法 JISK6911 / 単位 − / {g} … {d['sg']}`. "
                     f"**비중은 무차원이다** — 4 ℃ 물의 밀도 1000 kg/m^3 을 곱해 SI 밀도로 옮겼다: "
                     f"{d['sg']} × 1000 = {v} kg/m^3. 검산 {v}/1000 = {d['sg']} ✓. "
                     f"원문이 처리조건을 `−` 로 두어 온도를 적지 않았다(23 ℃ 로 가정하지 않았다). " + NOTE_TAIL_2013))
    if "cp" in want:
        out.append(P("thermal.specific_heat", float(d["cp"]), "J/(kg*K)",
                     {"test_method": "DSC", "temperature_c": 25, "specimen": SPEC_2013},
                     f"원문 verbatim — `比熱 / 試験方法 DSC法 / 処理条件 25℃ / 単位 J/kg℃ / {g} … {d['cp']}`. "
                     f"J/kg℃ 는 온도 '차'당 값이라 J/(kg·K) 와 수치가 같다(1 ℃ 간격 = 1 K 간격) — 곱한 수 없다. "
                     f"검산 {d['cp']} J/kg℃ = {d['cp']} J/(kg·K) ✓. " + NOTE_TAIL_2013))
    if "k" in want:
        out.append(P("thermal.conductivity", d["k"], "W/(m*K)",
                     {"test_method": "laser flash", "test_method_verbatim": "レーザーフラッシュ法",
                      "temperature_c": 25, "specimen": SPEC_2013},
                     f"원문 verbatim — `熱伝導率 / 試験方法 レーザーフラッシュ法 / 処理条件 25℃ / 単位 W/m・K / {g} … {d['k']}`. "
                     f"W/m・K = W/(m*K) 로 표기만 바꿨다 — 곱한 수 없다. " + NOTE_TAIL_2013))
    for meth, key in (("TMA", "tma"), ("DSC", "dsc"), ("DMA", "dma")):
        if f"tg_{meth}" in want and d[key] is not None:
            rate = {"TMA": "10℃/min", "DSC": "20℃/min", "DMA": "5℃/min"}[meth]
            out.append(P("thermal.glass_transition", C2K(d[key]), "K",
                         {"method_detail": meth, "heating_rate": rate, "specimen": SPEC_2013},
                         f"원문 verbatim — `ガラス転移温度(Tg) / 試験方法 {meth}法 / 処理条件 昇温：{rate.replace('/min','/分')} / "
                         f"単位 ℃ / {g} … {d[key]}`. {d[key]} ℃ + 273.15 = {C2K(d[key])} K. "
                         f"검산 {C2K(d[key])} − 273.15 = {d[key]} ✓. "
                         f"같은 행의 DSC 값은 DB 에 이미 t1 로 들어 있고 이 표와 일치한다. " + NOTE_TAIL_2013))
    if "td" in want:
        out.append(P("thermal.decomposition_temp", C2K(d["td"]), "K",
                     {"method_detail": "TG/DTA", "criterion": "5% weight loss",
                      "heating_rate": "10℃/min", "specimen": SPEC_2013},
                     f"원문 verbatim — `熱分解温度 / TG/DTA法（5％減） / 昇温：10℃/分 / {g} … {d['td']}`. "
                     f"{d['td']} ℃ + 273.15 = {C2K(d['td'])} K. " + NOTE_TAIL_2013))
    if "fx" in want:
        for (o, ov, dd), v in zip(DIRS, d["fx"]):
            out.append(P("mechanical.flexural_modulus", float(v) * 1e9, "Pa",
                         {"test_mode": "flexural", "test_standard": "JIS C6481",
                          "orientation": o, "orientation_verbatim": ov, "direction": dd,
                          "specimen": SPEC_2013},
                         f"원문 verbatim — `曲げ弾性係数 / JIS C6481に準拠 / {ov} / GPa / {g} … {v}`. "
                         f"**굽힘이다** — 같은 표가 오른쪽에 `ヤング率（引張り） ASTM D3039` 열을 따로 두므로 "
                         f"이 열을 영률 칸에 넣지 않았다. {v} GPa × 1e9 = {v * 1e9:.6g} Pa. "
                         + WARN_FX.get(g, "") + NOTE_TAIL_2013))
    if "ym" in want:
        for (o, ov, dd), v in zip(DIRS, d["ym"]):
            out.append(P("mechanical.youngs_modulus", float(v) * 1e9, "Pa",
                         {"test_mode": "tensile", "test_standard": "ASTM D3039",
                          "orientation": o, "orientation_verbatim": ov, "direction": dd,
                          "specimen": SPEC_2013},
                         f"원문 verbatim — `ヤング率（引張り） / ASTM D3039 / {ov} / GPa / {g} … {v}`. "
                         f"인쇄쪽 19 `試験項目の用語解説` verbatim: "
                         f"「●ヤング率（ASTM D3039）幅15mmの短冊状サンプルをつかみ間距離125mmで引張・圧縮試験機にセットします。"
                         f"引張り速度2mm/分で引張り強度を測定し、引張り応力と歪みの関係から求めます。」 "
                         f"{v} GPa × 1e9 = {v * 1e9:.6g} Pa. " + NOTE_TAIL_2013))
    for i, (lbl, hz, std) in enumerate((("1MHz", 1e6, "JIS C6481"),
                                        ("1GHz", 1e9, "IPC TM-650 2.5.5.9"))):
        if f"dk_{lbl}" in want and d["dk"][i] is not None:
            out.append(P("electrical.dielectric_constant", d["dk"][i], "1",
                         {"frequency_hz": hz, "test_standard": std, "specimen": SPEC_2013},
                         f"원문 verbatim — `比誘電率 / 1MHz：JIS C6481, 1GHZ：IPC TM650 2.5.5.9 / {lbl} / {g} … {d['dk'][i]}`. "
                         f"무차원. 환산 없다. " + NOTE_TAIL_2013))
        if f"df_{lbl}" in want and d["df"][i] is not None:
            out.append(P("electrical.dissipation_factor", d["df"][i], "1",
                         {"frequency_hz": hz, "test_standard": std, "specimen": SPEC_2013},
                         f"원문 verbatim — `誘電正接 / 1MHz：JIS C6481, 1GHZ：IPC TM650 2.5.5.9 / {lbl} / {g} … {d['df'][i]}`. "
                         f"무차원(tanδ). 환산 없다. " + NOTE_TAIL_2013))
    if "ds" in want and d["ds"] is not None:
        v = d["ds"] * 1e6
        out.append(P("electrical.dielectric_strength", v, "V/m",
                     {"test_standard": "ASTM D149", "specimen": SPEC_2013_DS,
                      "orientation": "through-thickness", "orientation_verbatim": "貫層"},
                     f"원문 verbatim — `貫層耐電圧 / ASTM D149に準拠 / kV/mm / {g} … {d['ds']}`. "
                     f"1 kV/mm = 1000 V / 0.001 m = 1e6 V/m 이므로 {d['ds']} × 1e6 = {v:.6g} V/m. "
                     f"검산 {v:.6g}/1e6 = {d['ds']} kV/mm ✓. "
                     f"**이 열만 시편이 0.2 mm 다**(머리글 `貫層耐電圧：0.2mm`). "
                     f"같은 표의 `沿層耐電圧`(kV)은 전계강도가 아니라 절연파괴 전압이라 이 키에 넣지 않았다. "
                     + NOTE_TAIL_2013))
    return out


def rows_2021(g: str, want: set) -> list:
    d = T2021[g]
    sub = {"sub_grade": g} if g.endswith(")") else {}
    out = []
    if "nu" in want and d["nu"] is not None:
        out.append(P("mechanical.poisson_ratio", d["nu"], "1",
                     dict(test_standard="JIS K 7161-1", temperature_c=23,
                          specimen=SPEC_2021_NU, **sub),
                     f"원문 verbatim — `ポアソン比 / JIS K 7161-1 / 23±3℃ / − / {g} … {d['nu']}`. "
                     f"무차원이라 환산 없다. **2021 판은 포아송비 시편만 0.8 mm 다**"
                     f"(머리글 `ポアソン比: 0.8mm`) — 2013 판의 JIS K7113·1.6 mm 와 시험법·시편이 다르다. "
                     + NOTE_TAIL_2021))
    if "k" in want:
        out.append(P("thermal.conductivity", d["k"], "W/(m*K)",
                     dict(test_method="laser flash", test_method_verbatim="レーザーフラッシュ法",
                          temperature_c=25, specimen=SPEC_2021, **sub),
                     f"원문 verbatim — `熱伝導率 / レーザーフラッシュ法 / 25℃ / W/m・K / {g} … {d['k']}`. "
                     f"표기만 바꿨다 — 곱한 수 없다. " + NOTE_TAIL_2021))
    for meth, key, std, rate in (("TMA", "tma", "IPC-TM-650", "10℃/min"),
                                 ("DSC", "dsc", "IPC-TM-650", "20℃/min"),
                                 ("DMA", "dma", "JIS C 6481", "5℃/min")):
        if f"tg_{meth}" in want and d[key] is not None:
            out.append(P("thermal.glass_transition", C2K(d[key]), "K",
                         dict(method_detail=meth, test_standard=std, heating_rate=rate,
                              specimen=SPEC_2021, **sub),
                         f"원문 verbatim — `ガラス転移温度(Tg) / {meth}({std}) / 昇温速度：{rate.replace('/min','/分')} / "
                         f"℃ / {g} … {d[key]}`. {d[key]} ℃ + 273.15 = {C2K(d[key])} K. "
                         f"검산 {C2K(d[key])} − 273.15 = {d[key]} ✓. " + NOTE_TAIL_2021))
    if "td" in want:
        out.append(P("thermal.decomposition_temp", C2K(d["td"]), "K",
                     dict(method_detail="TGA", test_standard="IPC-TM-650",
                          criterion="5% weight loss", heating_rate="10℃/min",
                          specimen=SPEC_2021, **sub),
                     f"원문 verbatim — `熱分解温度 / TGA(IPC-TM-650)(5% 重量減) / 昇温速度：10℃/分 / {g} … {d['td']}`. "
                     f"{d['td']} + 273.15 = {C2K(d['td'])} K. " + NOTE_TAIL_2021))
    if "fx" in want:
        for (o, ov, dd), v in zip(DIRS21, d["fx"]):
            out.append(P("mechanical.flexural_modulus", float(v) * 1e9, "Pa",
                         dict(test_mode="flexural", test_standard="JIS C 6481",
                              orientation=o, orientation_verbatim=ov, direction=dd,
                              specimen=SPEC_2021, **sub),
                         f"원문 verbatim — `曲げ弾性係数 / JIS C 6481 / {ov} / GPa / {g} … {v}`. "
                         f"**굽힘이다** — 같은 표가 오른쪽에 `ヤング率(引張りモード) ASTM D3039` 열을 따로 둔다. "
                         f"{v} GPa × 1e9 = {v * 1e9:.6g} Pa. "
                         + WARN_FX.get(g, "") + NOTE_TAIL_2021))
    if "ym" in want:
        for (o, ov, dd), v in zip(DIRS21, d["ym"]):
            out.append(P("mechanical.youngs_modulus", float(v) * 1e9, "Pa",
                         dict(test_mode="tensile", test_standard="ASTM D3039",
                              orientation=o, orientation_verbatim=ov, direction=dd,
                              specimen=SPEC_2021_YM, **sub),
                         f"원문 verbatim — `ヤング率(引張りモード) / ASTM D3039 / {ov} / GPa / {g} … {v}`. "
                         f"{v} GPa × 1e9 = {v * 1e9:.6g} Pa. "
                         f"**2021 판은 인장 영률 시편만 0.1 mm 다**(머리글 `ヤング率(引張りモード): 0.1mm`). "
                         + NOTE_TAIL_2021))
    for i, (lbl, hz, std) in enumerate((("1MHz", 1e6, "JIS C 6481"),
                                        ("1GHz", 1e9, "IPC-TM-650 2.5.5.9"))):
        if f"dk_{lbl}" in want and d["dk"][i] is not None:
            out.append(P("electrical.dielectric_constant", d["dk"][i], "1",
                         dict(frequency_hz=hz, test_standard=std, specimen=SPEC_2021, **sub),
                         f"원문 verbatim — `比誘電率 / 1MHz：JIS C 6481, 1GHz：IPC-TM-650 2.5.5.9 / {lbl} / "
                         f"{g} … {d['dk'][i]}`. 무차원. " + NOTE_TAIL_2021))
        if f"df_{lbl}" in want and d["df"][i] is not None:
            out.append(P("electrical.dissipation_factor", d["df"][i], "1",
                         dict(frequency_hz=hz, test_standard=std, specimen=SPEC_2021, **sub),
                         f"원문 verbatim — `誘電正接 / 1MHz：JIS C 6481, 1GHz：IPC-TM-650 2.5.5.9 / {lbl} / "
                         f"{g} … {d['df'][i]}`. 무차원(tanδ). " + NOTE_TAIL_2021))
    if "ds" in want and d["ds"] is not None:
        v = d["ds"] * 1e6
        out.append(P("electrical.dielectric_strength", v, "V/m",
                     dict(test_standard="IPC-TM-650", specimen=SPEC_2021_DS,
                          orientation="through-thickness", orientation_verbatim="貫層", **sub),
                     f"원문 verbatim — `貫層耐電圧 / IPC-TM-650 / kV/mm / {g} … {d['ds']}`. "
                     f"{d['ds']} kV/mm × 1e6 = {v:.6g} V/m. 검산 {v:.6g}/1e6 = {d['ds']} ✓. "
                     f"**이 열만 시편이 0.2 mm 다.** " + NOTE_TAIL_2021))
    return out


# ── 재료별로 '아직 안 든 칸' 만 고른다 ─────────────────────────────────────────
# 판정 근거는 ea00_report.md §2 의 칸별 대조표에 있다.
PLAN_2013 = {
    "Panasonic MEGTRON 6 R-5775 Laminate":
        {"sg", "cp", "fx", "ym", "dk_1MHz", "df_1MHz", "ds"},
    "Panasonic R-1755V / R-1650V High-Tg Low-CTE High-Reliability Glass Epoxy Laminate":
        {"nu", "sg", "cp", "k", "ds"},
    "Panasonic R-1755M / R-1650M Mid-Tg Low-CTE High-Reliability Glass Epoxy Laminate":
        {"nu", "sg", "cp", "k", "ds"},
    "Panasonic R-1755D (HIPER D) High-Heat-Resistance Automotive Glass Epoxy Laminate":
        {"nu", "sg", "cp", "k", "ds", "tg_TMA", "tg_DMA", "dk_1MHz", "df_1MHz"},
    "Panasonic R-1755E (HIPER E) High-Reliability Automotive Glass Epoxy Laminate":
        {"nu", "sg", "cp", "k", "ds", "tg_TMA", "tg_DMA", "dk_1MHz", "df_1MHz"},
    "Panasonic R-1566 Halogen-Free Automotive Glass Epoxy Laminate":
        {"nu", "sg", "cp", "k", "ds", "tg_TMA", "tg_DMA", "dk_1MHz", "df_1MHz"},
    "Panasonic R-1766 Standard FR-4 Automotive Glass Epoxy Laminate":
        {"nu", "sg", "cp", "k", "ds", "tg_TMA", "tg_DMA", "dk_1MHz", "df_1MHz"},
}
GRADE_OF = {
    "Panasonic MEGTRON 6 R-5775 Laminate": "R-5775",
    "Panasonic R-1755V / R-1650V High-Tg Low-CTE High-Reliability Glass Epoxy Laminate": "R-1755V",
    "Panasonic R-1755M / R-1650M Mid-Tg Low-CTE High-Reliability Glass Epoxy Laminate": "R-1755M",
    "Panasonic R-1755D (HIPER D) High-Heat-Resistance Automotive Glass Epoxy Laminate": "R-1755D",
    "Panasonic R-1755E (HIPER E) High-Reliability Automotive Glass Epoxy Laminate": "R-1755E",
    "Panasonic R-1566 Halogen-Free Automotive Glass Epoxy Laminate": "R-1566",
    "Panasonic R-1766 Standard FR-4 Automotive Glass Epoxy Laminate": "R-1766",
}
PLAN_2021 = {
    "Panasonic R-1566S Halogen-Free Automotive Glass Epoxy Laminate":
        ("R-1566S", {"nu", "k", "ds", "tg_DMA", "fx", "ym", "df_1MHz"}),
    "Panasonic MEGTRON 7 R-5785 Laminate":
        ("R-5785(N)", {"fx", "ym"}),
}


def main():
    mats = []
    for name, want in PLAN_2013.items():
        mats.append({"match_name": name, "source": SRC_2013,
                     "properties": rows_2013(GRADE_OF[name], want)})
    for name, (grade, want) in PLAN_2021.items():
        mats.append({"match_name": name, "source": SRC_2021,
                     "properties": rows_2021(grade, want)})
    doc = {"batch": "69차 EA", "materials": mats}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(m["properties"]) for m in mats)
    print(f"{OUT} — 재료 {len(mats)} · 값 {n}행")
    for m in mats:
        print(f"  {len(m['properties']):3d}행  {m['match_name']}")


if __name__ == "__main__":
    main()
