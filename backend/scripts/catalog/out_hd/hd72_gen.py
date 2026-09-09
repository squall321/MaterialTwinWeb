# 72차 HD 수집 배치 생성기 — 71차 GD 가 세운 카드의 코어7 빈칸을 이미 가진 문서의 안 읽은 판(版)으로 두드린다
#
# 값의 출처는 둘 다 **로컬 원문**이다:
#   ① Resonac 銅張積層板 총합 카탈로그 **영문판 2025-05** (65쪽) — GD 는 일문판 2023-2024 만 봤다
#   ② Sumitomo Bakelite LαZ **빌드업 페이지** — GD 가 「로컬에 없다」고 넘긴 형제 페이지
#
# 규율: 값을 지어내지 않는다 · 역산하지 않는다 · 인쇄된 구간은 두 행(bound) · 평균 금지 · t4 금지
#       열 밀림은 300~350 dpi 렌더 대조로만 확정한다

from __future__ import annotations

import json
import pathlib

OUT = pathlib.Path(__file__).parent

# ---------------------------------------------------------------- 출처

SRC_EN = {
    "kind": "datasheet",
    "title": "COPPER CLAD LAMINATES — General Characteristics / product sheets "
             "(Resonac 銅張積層板 총합 카탈로그 **영문판**, 2025-05, 65쪽)",
    "url": None,
    "publisher": "Resonac Corporation",
    "year": 2025,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/"
                  "Resonac_MCL-E-GEA-Series_CopperCladLaminates_Catalog_2025-05.pdf",
    "url_note": "PDF 메타(PowerPoint 2016 생성, Author `Resonac Corporation.`, CreationDate 2025-05-01)에 원 URL 이 "
                "없고 저장 시점 URL 도 파일에 남아 있지 않다. **URL 을 지어내지 않았다** — 로컬 원문 65쪽이 근거다. "
                "71차 GD 가 쓴 일문판(`Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf`, 66쪽)과 **다른 문서**다 — "
                "판(版)이 다르고 등급 구성과 일부 값이 다르다(hd72_09_verdicts.json 의 판 드리프트 표 참조).",
}

SRC_BU = {
    "kind": "datasheet",
    "title": "半導体パッケージ基板用材料 ビルドアップ材料 — 高密度パッケージ基板材料 “LαZ®” BLα-3700GS 特性表 (住友ベークライト)",
    "url": "https://web.archive.org/web/20210801015148id_/"
           "https://www.sumibe.co.jp/product/it-materials/package/buildup/index.html",
    "publisher": "Sumitomo Bakelite Co., Ltd. (住友ベークライト株式会社)",
    "year": 2021,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/"
                  "SumitomoBakelite_LAZ-Buildup_Spec_ja_2026-09-09.html",
    "url_note": "**원 URL `https://www.sumibe.co.jp/product/it-materials/package/buildup/` 는 지금 HTTP 404 다** — "
                "벤더 자기 사이트의 부모 인덱스(`/product/it-materials/package/`)가 아직 이 링크를 걸고 있는데 "
                "대상이 죽어 있다(깨진 링크). `index.html`·`build-up`·`/en/`·슬래시 없는 꼴까지 전부 404 를 준다. "
                "**그래서 `url` 은 실제로 읽은 Wayback 스냅샷 URL 을 적었다 — 지어낸 URL 이 아니다.** "
                "스냅샷은 셋뿐이고(2019-11-14 · 2020-08-04 · 2021-08-01) **특성표가 세 판 모두 바이트 동일**이라 "
                "판 드리프트가 없다. `year` 는 스냅샷 연도(2021)를 적었다 — 벤더가 페이지에 개정일을 안 찍으므로 "
                "**우리가 아는 최신 확인 시점**이 그것이다.",
}

SRC_PLEL = {
    "kind": "datasheet",
    "title": "ガラスエポキシ積層板 / 紙フェノール積層板 一般特性 (住友ベークライト スミライト® 積層板カタログ, 인쇄 25~32쪽)",
    "url": "https://www.sumibe.co.jp/ww-attaches/805.pdf",
    "publisher": "Sumitomo Bakelite Co., Ltd. (住友ベークライト株式会社)",
    "year": 2026,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/"
                  "SumitomoBakelite_Sumilite-PL-EL_Catalog_ja_2026-09-09.pdf",
    "url_note": "살아 있는 벤더 직접 URL 이다(2026-09-09 취득). **이 PDF 는 Illustrator 아웃라인 벡터 텍스트라 "
                "`pdftotext` 가 0자를 준다** — 값은 전부 150 dpi 렌더를 눈으로 읽어 옮겼다. "
                "다운스트림에서 재추출하려면 OCR 이나 렌더가 필요하다.",
}

RENDER_NOTE_P6 = (
    "**열 밀림 대조** — 이 쪽(PDF 6쪽 / 인쇄 7쪽)을 200 dpi 로 렌더해 표 머리와 값 행을 눈으로 대조한 뒤에만 옮겼다. "
    "렌더로 확정한 열 순서는 `GEA-705G | GEA-770G | GEA-795G | MCL-E-679FG(Type R) | MCL-E-679FG(Type S) | "
    "MCL-HS20N | MCL-HS20N(Type D) | MCL-HS100` 다. "
    "**`pdftotext -layout` 은 7번째 열을 `MCL-HS20N (Type S)` 로 뽑는다 — 렌더는 `(Type D)` 다.** "
    "이 카탈로그는 쪽 오른쪽 세로 탭 네비게이션(`Recommended PWB Materials by Application`·`General Properties` …)이 "
    "텍스트층에 끼어들어 헤더를 여러 줄로 흩는다. 표 하단 각주 verbatim: "
    "`*1: Cavity resonator; *2: RT foil; *3: HVLP foil, *4: 0.8 mmt; *5: Tensile`."
)

RENDER_NOTE_P7 = (
    "**열 밀림 대조** — 이 쪽(PDF 7쪽 / 인쇄 8쪽)을 350 dpi 로 렌더해 표 머리와 열전도율 행을 잘라 붙여 눈으로 대조했다. "
    "렌더로 확정한 열 순서는 `MCL-HS100(Type D) | GH-200(Type D) | GH-100(Type D) | MCL-HD60 | MCL-HD60(Type D) | "
    "MCL-HD80 | MCL-HD90 | MCL-HD90(Type D) | MCF-200HS | MCF-770G(Type P)` — **열 열(10)이다.** "
    "일문판 2023-2024 의 같은 쪽은 여덟 열이고 `MCL-HD60(Type D)`·`MCL-HD80` 두 열이 없다. "
    "표 하단 각주 verbatim: `*1: Cavity resonator; *2: RT foil; *3: HVLP foil, *4: 0.8 mmt; *5: Tensile`."
)

RENDER_NOTE_P28 = (
    "**열 밀림 대조** — 제품별 쪽(PDF 28쪽 / 인쇄 29쪽 `MCL-HD60/HD80/HD90 ● Copper Clad Laminates`)을 300 dpi 로 "
    "렌더해 표 전체(머리~각주)를 눈으로 대조했다. 렌더로 확정한 열 순서는 다섯 열 "
    "`HD60 | HD60HD90(Type D) | HD80 | HD90 | HD90HD90(Type D)` 다. "
    "**2·5번째 열 머리글은 원문이 실제로 `HD60HD90(Type D)`·`HD90HD90(Type D)` 로 인쇄돼 있다 — 벤더의 오타다"
    "(텍스트 추출 아티팩트가 아니다, 렌더로 확인했다).** 유리크로스(Low Dk)와 Dk 값(5.8-6.0 / 8.2-8.4)이 "
    "총괄표의 `MCL-HD60(Type D)`·`MCL-HD90(Type D)` 열과 정확히 일치하므로 그 두 등급으로 확정했다. "
    "각주 verbatim: `*1) Heating Rate: 10℃/min. (Tensile)  *2) SPDR method, Drying:105℃ / 1h.  "
    "*3) Cut-off circular waveguide method, Drying:105 ℃ / 1h.` "
    "`※Above data are experimental results and not guaranteed.`"
)

CORE4_ABSENT = (
    "밀도·포아송비·비열·인장강도 **행이 두 판 어디에도 없다.** 72차 HD 가 전수 확인했다 — "
    "일문판 2023-2024(66쪽)·영문판 2025-05(65쪽) 두 문서를 쪽별 텍스트 길이로 훑어 이미지 전용 쪽이 0 임을 먼저 확인한 뒤 "
    "전문 토큰 검사를 돌렸다: 일문판 `比重` 0 · `ポアソン` 0 · `比熱` 0 · `引張強さ` 0 (`密度` 3회는 전부 산문), "
    "영문판 `Density` 0 · `Poisson` 0 · `Specific Heat` 0 · `Tensile` 15회는 전부 **탄성률 행 이름과 각주**다. "
    "Resonac 의 기계축은 `Tensile modulus`·`Flexural modulus` 두 행뿐이고 **강도 행 자체가 없다.**"
)


def C(c):  # ℃ → K
    return round(c + 273.15, 2)


def rows_range(key, unit, lo, hi, conv, cond, note_head, note_tail, tier=1, method="measured"):
    """인쇄된 구간을 하한·상한 두 행으로 — 평균 내지 않는다."""
    out = []
    for b, v in (("lower", lo), ("upper", hi)):
        cc = dict(cond)
        cc["bound"] = b
        out.append({
            "key": key, "value": conv(v), "unit": unit, "method": method, "tier": tier,
            "conditions": cc,
            "notes": (f"{note_head} **인쇄된 값이 구간이므로 하한·상한 두 행으로 갈랐다 — 평균 내지 않았다.** "
                      f"이 행은 {'하한' if b == 'lower' else '상한'} {v} 이다. "
                      f"환산 {v} -> {conv(v):.6g} {unit}; 되돌리면 {conv(v):.6g} -> {v}. {note_tail}"),
        })
    return out


def rows_single(key, unit, v, conv, cond, note_head, note_tail, tier=1, method="measured"):
    return [{
        "key": key, "value": conv(v), "unit": unit, "method": method, "tier": tier,
        "conditions": dict(cond),
        "notes": (f"{note_head} 원문이 **구간이 아니라 단일 값**으로 인쇄한 칸이다. "
                  f"환산 {v} -> {conv(v):.6g} {unit}; 되돌리면 {conv(v):.6g} -> {v}. {note_tail}"),
    }]


GPa = lambda v: v * 1e9
PPM = lambda v: v * 1e-6
IDENT = lambda v: float(v)
KNM = lambda v: v * 1000.0
DEGC = lambda v: C(v)
PCT = lambda v: v / 100.0

# ================================================================ ① Resonac 영문판 2025-05

materials_en = []

# ---- (1) 코어7 빈칸을 닫는 값: MCL-HD90 · MCL-HD90(D) 열전도율 --------------
COND_HEAD = "원문 verbatim: `Thermal conductivity | W/(m·K) | 0.60 - 0.80`."
COND_TAIL = (
    "**이 칸이 이 배치의 핵심이다** — 같은 벤더의 **일문판 2023-2024 는 이 칸을 `－` 로 인쇄한다**(71차 GD 가 그렇게 읽었고 "
    "그 읽기는 맞다, 72차 HD 가 같은 쪽을 다시 렌더해 확인했다). **영문판 2025-05 에서 값이 새로 인쇄됐다.** "
    "판이 다른 문서이므로 덮어쓰기가 아니라 새 출처의 새 행이다. " + RENDER_NOTE_P7
)
for nm in ("Resonac MCL-HD90 (high-Dk glass/epoxy CCL)",
           "Resonac MCL-HD90 (D type) (high-Dk CCL)"):
    materials_en.append({
        "match_name": nm,
        "source": SRC_EN,
        "properties": rows_range(
            "thermal.conductivity", "W/(m*K)", 0.60, 0.80, IDENT,
            {"catalog_edition": "Resonac COPPER CLAD LAMINATES 영문판 2025-05, PDF 7쪽 / 인쇄 8쪽"},
            COND_HEAD, COND_TAIL),
    })

# ---- (2) 기존 카드에 붙는 새 측정법 행: CTE z (<Tg)(DIC) -------------------
DIC = {
    "Resonac MCL-E-795G (glass/epoxy CCL)": 8.5,
    "Resonac MCL-E-795G (LH type) (glass/epoxy CCL)": 5.5,
    "Resonac MCL-E-705G (glass/epoxy CCL)": 9.6,
    "Resonac MCL-E-705G (L type) (glass/epoxy CCL)": 7.0,
    "Resonac MCL-E-705G (LH type) (glass/epoxy CCL)": 6.9,
    "Resonac MCL-E-700G (R type) (glass/epoxy CCL)": 13.1,
}
DIC_TAIL = (
    "**일문판 2023-2024 는 이 행을 전 등급 `－` 로 비워 둔다**(71차 GD 가 세 쪽 21열 전부에서 확인했다). "
    "영문판 2025-05 에서 여섯 등급에 값이 인쇄됐다 — `MCL-E-770G(Type R)`·`(Type RLH)` 두 열은 여기서도 `-` 다. "
    "**같은 물성의 다른 측정법이라 기존 `(Comp.)` 행을 덮지 않고 별개 행으로 넣었다** — 행 이름이 `(DIC)` 로 갈려 있다. "
    "각주 `*4: 0.8 mmt` 가 이 행에 붙어 있어 시편 두께를 조건에 박았다. "
    "**열 밀림 대조** — PDF 5쪽 / 인쇄 6쪽을 300 dpi 로 렌더해 표 머리와 CTE z 세 행을 잘라 붙여 대조했다. "
    "렌더로 확정한 열 순서는 `MCL-E-795G | MCL-E-795G(Type LH) | MCL-E-705G | MCL-E-705G(Type L) | "
    "MCL-E-705G(Type LH) | MCL-E-700G(Type R) | MCL-E-770G(Type R) | MCL-E-770G(Type RLH)` 다."
)
for nm, v in DIC.items():
    materials_en.append({
        "match_name": nm,
        "source": SRC_EN,
        "properties": rows_single(
            "thermal.expansion_linear", "1/K", v, PPM,
            {"axis": "through-thickness (z)", "regime": "below Tg",
             "method_detail": "DIC (digital image correlation)",
             "specimen_thickness_mm": 0.8,
             "catalog_edition": "Resonac COPPER CLAD LAMINATES 영문판 2025-05, PDF 5쪽 / 인쇄 6쪽"},
            f"원문 verbatim: `CTE z (<Tg)(DIC)*4 | ppm/℃ | {v}`.", DIC_TAIL),
    })

# ---- (3) 기존 HD 카드에 붙는 제품별 쪽의 고주파 Dk/Df ----------------------
# PDF 28쪽 다섯 열. 값은 (Dk 5주파, Df 5주파) 각각 (lo,hi).
HD_P28 = {
    "HD60": {
        "match": "Resonac MCL-HD60 (high-Dk glass/epoxy CCL)",
        "dk": [(6.0, 6.2), (6.1, 6.3), (6.1, 6.3), (6.1, 6.3), (6.1, 6.3)],
        "df": [(0.0050, 0.0060), (0.0055, 0.0065), (0.0060, 0.0070), (0.0065, 0.0075), (0.0065, 0.0075)],
        "cte_xy": (8, 10), "emod": (19, 23), "tg_dma": (230, 240), "peel12": (0.5, 0.6),
        "glass": "E-glass, style 2116",
    },
    "HD90": {
        "match": "Resonac MCL-HD90 (high-Dk glass/epoxy CCL)",
        "dk": [(9.0, 9.2)] * 5,
        "df": [(0.0055, 0.0065), (0.0060, 0.0070), (0.0065, 0.0075), (0.0070, 0.0080), (0.0070, 0.0080)],
        "cte_xy": (9, 11), "emod": (18, 22), "tg_dma": (230, 240), "peel12": (0.5, 0.6),
        "glass": "E-glass, style 2116",
    },
    "HD90D": {
        "match": "Resonac MCL-HD90 (D type) (high-Dk CCL)",
        "dk": [(8.2, 8.4)] * 5,
        "df": [(0.0045, 0.0055), (0.0050, 0.0060), (0.0055, 0.0065), (0.0060, 0.0070), (0.0060, 0.0070)],
        "cte_xy": (9, 11), "emod": (17, 21), "tg_dma": (230, 240), "peel12": (0.5, 0.6),
        "glass": "Low Dk-glass, style 2116",
    },
}
FREQS = [("10 GHz", "SPDR", "*2"), ("20 GHz", "SPDR", "*2"),
         ("36 GHz", "cut-off circular waveguide", "*3"),
         ("50 GHz", "cut-off circular waveguide", "*3"),
         ("60 GHz", "cut-off circular waveguide", "*3")]

P28_TAIL_COMMON = (
    "**총괄표(PDF 7쪽)의 같은 물성과 조건이 다르다** — 총괄표는 묶음 이름이 `Electrical (SPDR)` 뿐이고 건조 전처리를 "
    "말하지 않는데, 이 제품별 쪽은 각주로 `Drying:105℃ / 1h` 를 박는다. **조건이 다르므로 덮지 않고 별개 행으로 넣었다.** "
    + RENDER_NOTE_P28
)

for key, d in HD_P28.items():
    props = []
    for i, (f, meth, fn) in enumerate(FREQS):
        lo, hi = d["dk"][i]
        props += rows_range("electrical.dielectric_constant", "1", lo, hi, IDENT,
                            {"frequency": f, "method_detail": meth,
                             "pretreatment": "drying 105 C / 1 h",
                             "glass_cloth_style": d["glass"],
                             "catalog_edition": "Resonac 영문판 2025-05, PDF 28쪽 / 인쇄 29쪽"},
                            f"원문 verbatim: `Dielectric Constant | {f}{fn} | － | {lo} - {hi}`.",
                            P28_TAIL_COMMON)
        lo, hi = d["df"][i]
        props += rows_range("electrical.dissipation_factor", "1", lo, hi, IDENT,
                            {"frequency": f, "method_detail": meth,
                             "pretreatment": "drying 105 C / 1 h",
                             "glass_cloth_style": d["glass"],
                             "catalog_edition": "Resonac 영문판 2025-05, PDF 28쪽 / 인쇄 29쪽"},
                            f"원문 verbatim: `Dissipation Factor | {f}{fn} | － | {lo} - {hi}`.",
                            P28_TAIL_COMMON)
    materials_en.append({"match_name": d["match"], "source": SRC_EN, "properties": props})

# ---- (4) 새 카드 — 영문판에만 있는 세 등급 --------------------------------

def resonac_card(name, desc, attrs, rows):
    return {"new_material": {"name": name, "category": "composite",
                             "description": desc, "attributes": attrs},
            "source": SRC_EN, "properties": rows}


COMMON_ATTR = {
    "subsystem": "pcb",
    "role": "product",
    "role_reason": "반도체 패키지·안테나인패키지 기판의 실부품 적층재. 벤더가 등급명으로 인쇄한 제품이다.",
    "role_confidence": "high",
    "manufacturer": "Resonac Corporation",
    "core7_absent_from_vendor_table": CORE4_ABSENT,
}

# GEA-795G (프리프레그) — PDF 6쪽 3번째 열
g = "GEA-795G"
head = lambda row, val: f"원문 verbatim: `{row} | {val}` (영문판 2025-05 PDF 6쪽, GEA-795G 열)."
rows = []
rows += rows_range("mechanical.youngs_modulus", "Pa", 20, 22, GPa,
                   {"test_mode": "tensile", "orientation": "X (in-plane)", "specimen_thickness_mm": 0.8},
                   head("Tensile modulus X*4 | GPa", "20 - 22"),
                   "**행 이름 자체가 `Tensile modulus` 라 인장 확정이다.** 각주 `*4: 0.8 mmt` 가 이 행에 붙어 있어 "
                   "시편 두께 0.8 mm 를 조건에 박았다 — 표 맨 위 `Thickness 0.020 mm` 는 프리프레그 자체의 두께지 "
                   "시편 두께가 아니다. " + RENDER_NOTE_P6)
rows += rows_range("thermal.conductivity", "W/(m*K)", 0.55, 0.75, IDENT, {},
                   head("Thermal conductivity | W/(m·K)", "0.55 - 0.75"), RENDER_NOTE_P6)
for ax in ("X", "Y"):
    rows += rows_range("thermal.expansion_linear", "1/K", 5, 7, PPM,
                       {"axis": f"in-plane ({ax})", "regime": "below Tg",
                        "test_mode": "tensile (각주 *5)", "method_detail": "TMA"},
                       head(f"CTE {ax.lower()} (<Tg) (Comp.)*5 | ppm/℃", "5 - 7"),
                       "이 칸에는 각주 `*5`(=Tensile)가 붙어 있어 **행 이름의 `(Comp.)` 를 덮는다** — "
                       "원문 표기 충돌을 그대로 적는다. 71차 GD 가 일문판 `(圧縮)` vs `*5: 引張` 에 쓴 규칙과 같다"
                       "(각주가 칸 단위로 걸리므로 각주를 따른다). " + RENDER_NOTE_P6)
rows += rows_range("thermal.expansion_linear", "1/K", 14, 24, PPM,
                   {"axis": "through-thickness (z)", "regime": "below Tg",
                    "test_mode": "compression (Comp.)", "method_detail": "TMA", "specimen_thickness_mm": 0.8},
                   head("CTE z (<Tg) (Comp.)*4 | ppm/℃", "14 – 24"),
                   "이 칸에는 `*5` 가 없다 — 행 이름의 `(Comp.)` 가 그대로 산다. " + RENDER_NOTE_P6)
rows += rows_range("thermal.expansion_linear", "1/K", 140, 170, PPM,
                   {"axis": "through-thickness (z)", "regime": "above Tg",
                    "test_mode": "compression (Comp.)", "method_detail": "TMA", "specimen_thickness_mm": 0.8},
                   head("CTE z (>Tg) (Comp.)*4 | ppm/℃", "140 - 170"), RENDER_NOTE_P6)
rows += rows_range("thermal.glass_transition", "K", 260, 290, DEGC, {"method_detail": "TMA"},
                   head("Tg (TMA) | ℃", "260 - 290"),
                   "TMA 와 DMA 는 같은 물성의 다른 측정법이라 별개 행으로 두었다. " + RENDER_NOTE_P6)
rows += rows_range("thermal.glass_transition", "K", 330, 350, DEGC, {"method_detail": "DMA"},
                   head("Tg (DMA) | ℃", "330 - 350"),
                   "TMA 와 DMA 는 같은 물성의 다른 측정법이라 별개 행으로 두었다. " + RENDER_NOTE_P6)
rows += rows_range("electrical.dielectric_constant", "1", 3.7, 3.9, IDENT,
                   {"frequency": "1 GHz", "method_detail": "SPDR"},
                   head("Dk (1 GHz) | －", "3.7 - 3.9"), RENDER_NOTE_P6)
rows += rows_range("electrical.dielectric_constant", "1", 3.6, 3.8, IDENT,
                   {"frequency": "10 GHz", "method_detail": "SPDR"},
                   head("Dk (10 GHz) | －", "3.6 - 3.8"), RENDER_NOTE_P6)
rows += rows_range("electrical.dissipation_factor", "1", 0.004, 0.006, IDENT,
                   {"frequency": "1 GHz", "method_detail": "SPDR"},
                   head("Df (1 GHz) | －", "0.004 - 0.006"), RENDER_NOTE_P6)
rows += rows_range("electrical.dissipation_factor", "1", 0.005, 0.007, IDENT,
                   {"frequency": "10 GHz", "method_detail": "SPDR"},
                   head("Df (10 GHz) | －", "0.005 - 0.007"), RENDER_NOTE_P6)
rows += rows_range("interface.peel_strength", "N/m", 0.5, 0.7, KNM,
                   {"copper_foil_thickness_um": 12, "copper_foil_type": "not stated"},
                   head("Peel Strength (12μm) | kN/m", "0.5 - 0.7"),
                   "`Peel strength (18μm)` 칸은 원문이 `—` 라 비웠다. " + RENDER_NOTE_P6)
materials_en.append(resonac_card(
    "Resonac GEA-795G (S-glass epoxy prepreg)",
    "レゾナック(Resonac) 銅張積層板 계열 프리프레그 `GEA-795G` — 코어재 `MCL-E-795G` 의 짝 프리프레그이고 "
    "벤더 표기상 `TYPE-F`(Superfine flat technology) 로고가 붙는 초평탄 표면 등급이다. "
    "**이 등급은 일문판 2023-2024 총괄표에 열이 없다** — 영문판 2025-05 에서 GEA-705G·GEA-770G 옆에 새로 선 열이다"
    "(일문판에도 이름은 나오지만 다층화 접착 조건 절뿐이다). 유리크로스 S-glass, 표 공칭 두께 0.020 mm. "
    "이 카드의 값은 영문판 PDF 6쪽 총괄표의 **한 열**을 그대로 옮긴 것이다.",
    {**COMMON_ATTR,
     "material_class": "glass/epoxy prepreg (GEA series, TYPE-F)",
     "product_form": "prepreg",
     "aliases": ["GEA-795G", "GEA795G", "Resonac GEA-795G", "GEA-795G (TYPE-F)"],
     "glass_cloth": "S-glass",
     "nominal_thickness_mm": 0.020,
     "paired_laminate": "MCL-E-795G",
     "ipc_4101_slash_sheet": "42",
     "ipc_4101_slash_sheet_note": "**IPC-4101 은 밀도를 규정하지 않는다 — 71차 GD 가 규격 본문 층에서 확인했다.** "
                                  "이 번호로는 밀도 빈칸이 닫히지 않는다.",
     "source_page": "영문판 2025-05, PDF 6쪽 / 인쇄 7쪽, 열 3"},
    rows))

# MCL-HD60 (Type D) · MCL-HD80 — PDF 7쪽 + PDF 28쪽
NEW_HD = [
    dict(name="Resonac MCL-HD60 (D type) (high-Dk CCL)",
         label="MCL-HD60 (Type D)", col7=5, glass="Low Dk-glass",
         dk10=(5.8, 6.0), df10=(0.0040, 0.0050), peel12=(0.5, 0.6), peel18=(0.6, 0.7),
         emod=(18, 22), tg_dma=(230, 240), cte_xy7=(9, 11), cond=(0.60, 0.80), ipc="N/A (Low Dk-glass)",
         p28_dk=[(5.8, 6.0), (5.9, 6.1), (5.9, 6.1), (5.9, 6.1), (5.9, 6.1)],
         p28_df=[(0.0040, 0.0050), (0.0045, 0.0055), (0.0050, 0.0060), (0.0055, 0.0065), (0.0055, 0.0065)],
         p28_cte=(8, 10), p28_emod=(18, 22)),
    dict(name="Resonac MCL-HD80 (high-Dk glass/epoxy CCL)",
         label="MCL-HD80", col7=6, glass="E-glass",
         dk10=(8.0, 8.2), df10=(0.0050, 0.0060), peel12=(0.5, 0.6), peel18=(0.6, 0.7),
         emod=(18, 22), tg_dma=(230, 240), cte_xy7=(10, 12), cond=(0.60, 0.80), ipc="44",
         p28_dk=[(8.0, 8.2)] * 5,
         p28_df=[(0.0050, 0.0060), (0.0055, 0.0065), (0.0060, 0.0070), (0.0065, 0.0075), (0.0065, 0.0075)],
         p28_cte=(9, 11), p28_emod=(18, 22)),
]

CTE_CONFLICT = (
    "**같은 카탈로그 안에서 총괄표와 제품별 쪽의 CTE 가 1 ppm/℃ 씩 다르다** — 총괄표(PDF 7쪽)는 "
    "`CTE x (<Tg) (Comp.)*5[=Tensile]`, 제품별 쪽(PDF 28쪽)은 `CTE XY*1[=Heating Rate 10℃/min. (Tensile)]` 로 "
    "**행 이름과 조건 표기가 서로 다르다**(총괄표만 `<Tg` 구간을 명시한다). 어느 칸이 틀렸는지 우리가 고르면 그건 "
    "우리 값이 되므로 **고르지 않았다 — 두 행을 조건으로 갈라 둘 다 넣었다.** 사유는 hd72_09_verdicts.json 에 적었다."
)

for d in NEW_HD:
    L = d["label"]
    h7 = lambda row, val: f"원문 verbatim: `{row} | {val}` (영문판 2025-05 PDF 7쪽, {L} 열)."
    h28 = lambda row, val: f"원문 verbatim: `{row} | {val}` (영문판 2025-05 PDF 28쪽, {L} 열)."
    r = []
    r += rows_range("mechanical.youngs_modulus", "Pa", *d["emod"], GPa,
                    {"test_mode": "tensile", "orientation": "X (in-plane)", "specimen_thickness_mm": 0.8,
                     "source_table": "총괄표 (PDF 7쪽)"},
                    h7("Tensile modulus X*4 | GPa", f"{d['emod'][0]} - {d['emod'][1]}"),
                    "**행 이름 자체가 `Tensile modulus` 라 인장 확정이다.** 각주 `*4: 0.8 mmt`. "
                    "제품별 쪽(PDF 28쪽)의 `Elastic Modulus | GPa` 가 같은 값이라 중복 행을 만들지 않았다. "
                    + RENDER_NOTE_P7)
    r += rows_range("thermal.conductivity", "W/(m*K)", *d["cond"], IDENT, {},
                    h7("Thermal conductivity | W/(m·K)", f"{d['cond'][0]} - {d['cond'][1]}"), RENDER_NOTE_P7)
    for ax in ("X", "Y"):
        r += rows_range("thermal.expansion_linear", "1/K", *d["cte_xy7"], PPM,
                        {"axis": f"in-plane ({ax})", "regime": "below Tg",
                         "test_mode": "tensile (각주 *5)", "method_detail": "TMA",
                         "source_table": "총괄표 (PDF 7쪽)"},
                        h7(f"CTE {ax.lower()} (<Tg) (Comp.)*5 | ppm/℃",
                           f"{d['cte_xy7'][0]} - {d['cte_xy7'][1]}"),
                        "칸 각주 `*5`(=Tensile)가 행 이름의 `(Comp.)` 를 덮는다. " + CTE_CONFLICT + " " + RENDER_NOTE_P7)
    r += rows_range("thermal.expansion_linear", "1/K", *d["p28_cte"], PPM,
                    {"axis": "in-plane (XY)", "regime": "not stated",
                     "test_mode": "tensile (각주 *1)", "heating_rate_c_per_min": 10,
                     "source_table": "제품별 쪽 (PDF 28쪽)"},
                    h28("CTE XY*1 | ppm/℃", f"{d['p28_cte'][0]} - {d['p28_cte'][1]}"),
                    CTE_CONFLICT + " " + RENDER_NOTE_P28)
    r += rows_range("thermal.glass_transition", "K", *d["tg_dma"], DEGC, {"method_detail": "DMA"},
                    h7("Tg (DMA) | ℃", f"{d['tg_dma'][0]} - {d['tg_dma'][1]}"),
                    "`Tg (TMA)` 칸은 원문이 `-` 라 비웠다. " + RENDER_NOTE_P7)
    r += rows_range("electrical.dielectric_constant", "1", *d["dk10"], IDENT,
                    {"frequency": "10 GHz", "method_detail": "SPDR", "source_table": "총괄표 (PDF 7쪽)"},
                    h7("Dk (10 GHz) | －", f"{d['dk10'][0]} - {d['dk10'][1]}"),
                    "`Dk (1 GHz)` 칸은 원문이 `-` 라 비웠다. " + RENDER_NOTE_P7)
    r += rows_range("electrical.dissipation_factor", "1", *d["df10"], IDENT,
                    {"frequency": "10 GHz", "method_detail": "SPDR", "source_table": "총괄표 (PDF 7쪽)"},
                    h7("Df (10 GHz) | －", f"{d['df10'][0]} - {d['df10'][1]}"),
                    "`Df (1 GHz)` 칸은 원문이 `-` 라 비웠다. " + RENDER_NOTE_P7)
    for i, (f, meth, fn) in enumerate(FREQS):
        lo, hi = d["p28_dk"][i]
        r += rows_range("electrical.dielectric_constant", "1", lo, hi, IDENT,
                        {"frequency": f, "method_detail": meth, "pretreatment": "drying 105 C / 1 h",
                         "glass_cloth_style": f"{d['glass']}, style 2116",
                         "source_table": "제품별 쪽 (PDF 28쪽)"},
                        h28(f"Dielectric Constant | {f}{fn} | －", f"{lo} - {hi}"), P28_TAIL_COMMON)
        lo, hi = d["p28_df"][i]
        r += rows_range("electrical.dissipation_factor", "1", lo, hi, IDENT,
                        {"frequency": f, "method_detail": meth, "pretreatment": "drying 105 C / 1 h",
                         "glass_cloth_style": f"{d['glass']}, style 2116",
                         "source_table": "제품별 쪽 (PDF 28쪽)"},
                        h28(f"Dissipation Factor | {f}{fn} | －", f"{lo} - {hi}"), P28_TAIL_COMMON)
    r += rows_range("interface.peel_strength", "N/m", *d["peel12"], KNM,
                    {"copper_foil_thickness_um": 12, "copper_foil_type": "LP (low profile, 제품별 쪽 각주)"},
                    h7("Peel Strength (12μm) | kN/m", f"{d['peel12'][0]} - {d['peel12'][1]}"),
                    "총괄표는 동박 종류를 안 적지만 제품별 쪽(PDF 28쪽)이 같은 값을 `Copper Peel Strength | 12 μm (LP)` 로 "
                    "인쇄한다 — 그쪽 표기를 조건에 넣었다. 참조규격 `IPC-TM-650 2.4.8`. " + RENDER_NOTE_P7)
    r += rows_range("interface.peel_strength", "N/m", *d["peel18"], KNM,
                    {"copper_foil_thickness_um": 18, "copper_foil_type": "not stated"},
                    h7("Peel strength (18μm) | kN/m", f"{d['peel18'][0]} - {d['peel18'][1]}"), RENDER_NOTE_P7)
    materials_en.append(resonac_card(
        d["name"],
        f"レゾナック(Resonac) 高Dk 다층재 `{L}` — 안테나인패키지(AiP)용 고유전율·저손실 동장적층판. "
        f"**이 등급은 일문판 2023-2024 총괄표에 열이 없다** — 영문판 2025-05 에서 새로 선 열이다. "
        f"유리크로스 {d['glass']}(제품별 쪽 style 2116), 표 공칭 두께 0.2 mm. 짝 프리프레그는 "
        f"`GD-60/GD-80/GD-90` 계열이다. 값은 영문판 총괄표(PDF 7쪽) **한 열**과 제품별 쪽(PDF 28쪽) **한 열**에서 "
        f"왔고 **두 표의 조건이 다른 물성은 덮지 않고 두 행으로 두었다.**",
        {**COMMON_ATTR,
         "material_class": "copper-clad laminate (MCL-HD high-Dk series)",
         "product_form": "copper-clad laminate",
         "aliases": [L, L.replace(" ", ""), L.replace("(Type D)", "(D type)").strip(),
                     d["name"].split(" (")[0].replace("Resonac ", "")],
         "glass_cloth": d["glass"],
         "glass_cloth_style": "2116",
         "nominal_thickness_mm": 0.2,
         "ipc_4101_slash_sheet": d["ipc"],
         "paired_prepreg": "GD-60 / GD-80 / GD-90",
         "vendor_header_typo": "제품별 쪽(PDF 28쪽) 표 머리글이 실제로 `HD60HD90(Type D)`·`HD90HD90(Type D)` 로 "
                               "인쇄돼 있다 — 벤더 오타다(300 dpi 렌더로 확인). 유리크로스와 Dk 값이 총괄표 열과 "
                               "일치해 등급을 확정했다.",
         "source_page": f"영문판 2025-05, PDF 7쪽(총괄표) 열 {d['col7']} + PDF 28쪽(제품별 쪽)"},
        r))

# ================================================================ ② Sumitomo LαZ 빌드업

BU_NOTE = (
    "**HTML `<tr>`/`<td>` 를 `colspan`/`rowspan` 까지 직접 파싱했다** — 레이아웃 추측이 끼어들 자리가 없으므로 "
    "열 밀림 위험이 원천적으로 없다. 이 표는 한 등급 한 열이라 소속 모호성도 없다. "
    "표 머리 verbatim: `| | Unit | ＬαＺ |` / `| | | BLα-3700GS |`."
)
bu = []
bu += rows_single("mechanical.youngs_modulus", "Pa", 5, GPa,
                  {"temperature_c": 25, "test_mode": "tensile", "temperature_note": "원문 표기 `R.T.`"},
                  "원문 verbatim: `Tensile Modulus（R.T.） | G Pa | 5`.",
                  "**행 이름이 `Tensile Modulus` 라 인장 확정이다 — t1 이다.** 71차 GD 가 같은 벤더의 코어·프리프레그·SR "
                  "세 장을 `弾性率`(모드 표기 없음)을 이유로 t3 에 둔 것과 대비된다. **같은 LαZ 계열인데 이 쪽만 모드를 "
                  "적는다 — 「이 벤더는 적을 때는 적는다」는 GD 의 판단을 뒷받침한다**(다만 그 판단으로 다른 쪽 t3 를 "
                  "올리지는 않았다, 사유는 hd72_09_verdicts.json). `R.T.` 를 25 ℃ 로 옮겼고 원문 표기를 조건에 남겼다. "
                  "짝 행은 `Tensile Modulus（250℃） | G Pa | 0.2` 다 — **두 온도가 별개 행이므로 두 행으로 넣었고 "
                  "평균 내지 않았다.** " + BU_NOTE)
bu += rows_single("mechanical.youngs_modulus", "Pa", 0.2, GPa,
                  {"temperature_c": 250, "test_mode": "tensile"},
                  "원문 verbatim: `Tensile Modulus（250℃） | G Pa | 0.2`.",
                  "**행 이름이 `Tensile Modulus` 라 인장 확정이다 — t1 이다.** 짝 행은 `R.T.` 의 5 GPa 다 — "
                  "**두 온도가 별개 행이므로 두 행으로 넣었고 평균 내지 않았다.** Tg(DMA) 200 ℃ 를 넘어서며 강성이 "
                  "25배 떨어지는 것이 그대로 읽힌다. " + BU_NOTE)
bu += rows_single("thermal.expansion_linear", "1/K", 35, PPM,
                  {"regime": "below Tg (CTE1 = α1)", "axis": "not stated"},
                  "원문 verbatim: `CTE1 | ppm／℃ | 35`.",
                  "**원문이 축을 적지 않는다** — `axis: not stated` 로 남겼고 지어내지 않았다. 짝 행 `CTE2 | 120` 은 "
                  "Tg 위 구간이라 별개 행이다. " + BU_NOTE)
bu += rows_single("thermal.expansion_linear", "1/K", 120, PPM,
                  {"regime": "above Tg (CTE2 = α2)", "axis": "not stated"},
                  "원문 verbatim: `CTE2 | ppm／℃ | 120`.",
                  "**원문이 축을 적지 않는다** — `axis: not stated` 로 남겼다. " + BU_NOTE)
bu += rows_single("thermal.glass_transition", "K", 200, DEGC, {"method_detail": "DMA"},
                  "원문 verbatim: `Tg（by DMA） | ℃ | 200`.",
                  "DMA 와 TMA 는 같은 물성의 다른 측정법이라 별개 행으로 두었다. " + BU_NOTE)
bu += rows_single("thermal.glass_transition", "K", 180, DEGC, {"method_detail": "TMA"},
                  "원문 verbatim: `Tg（by TMA） | ℃ | 180`.",
                  "DMA 와 TMA 는 같은 물성의 다른 측정법이라 별개 행으로 두었다. " + BU_NOTE)
bu += rows_single("electrical.dielectric_constant", "1", 3.1, IDENT,
                  {"frequency": "1 GHz", "method_detail": "not stated"},
                  "원문 verbatim: `Dielectric constant | （1GHz） | 3.1`.",
                  "**원문이 측정법을 적지 않는다** — 지어내지 않고 `not stated` 로 남겼다. " + BU_NOTE)
bu += rows_single("electrical.dissipation_factor", "1", 0.012, IDENT,
                  {"frequency": "1 GHz", "method_detail": "not stated"},
                  "원문 verbatim: `Dielectric Dissipation Factor | （1GHz） | 0.012`.",
                  "**원문이 측정법을 적지 않는다** — `not stated` 로 남겼다. " + BU_NOTE)
bu += rows_single("chemical.water_absorption_saturation", "1", 1.0, PCT,
                  {"test_condition": "PCT-2hr / 121 C", "specimen_thickness_mm": 0.2},
                  "원문 verbatim: `Moisture Absorption | wt％ | 1.0`, 각주 `（0.2t）（PCT-2hr／121℃）`.",
                  "PCT(압력솥) 2시간 조건이라 24시간 침지(`chemical.water_absorption_24h`)가 아니라 "
                  "포화 갈래 키에 넣었다. 1.0 wt% / 100 = 0.010 (무차원). " + BU_NOTE)

materials_bu = [{
    "new_material": {
        "name": "Sumitomo Bakelite BLα-3700GS (package buildup material)",
        "category": "composite",
        "description": "住友ベークライト(Sumitomo Bakelite) 반도체 패키지 기판용 고밀도 재료 「LαZ®」 계열 "
                       "`BLα-3700GS` — **빌드업 재료**. 71차 GD 가 코어(LAZ-4785)·프리프레그(LAZ-2002/6785)·"
                       "솔더레지스트 대체재(LAZ-7752) 세 장을 담으면서 「세 페이지의 네비게이션이 네 번째 형제 페이지"
                       "(`/product/it-materials/package/buildup/`)를 거는데 로컬에 없다」고 넘긴 바로 그 페이지다. "
                       "**이 형제 페이지만 `Tensile Modulus` 로 시험모드를 적는다** — 그래서 이 카드의 영률은 t1 이고 "
                       "GD 의 LαZ 13장 26행(t3)과 등급이 갈린다. 생산 공장 표기 `宇都宮工場`. "
                       "값은 이 페이지 특성표의 **유일한 열**을 그대로 옮긴 것이다.",
        "attributes": {
            "material_class": "package substrate buildup material (LαZ series)",
            "subsystem": "pcb",
            "role": "product",
            "role_reason": "반도체 패키지 기판의 빌드업 절연층 실부품. 벤더가 등급명으로 인쇄한 제품이다.",
            "role_confidence": "high",
            "manufacturer": "Sumitomo Bakelite Co., Ltd.",
            "product_series": "LαZ (LAZ)",
            "product_form": "buildup dielectric material",
            "aliases": ["BLα-3700GS", "BLa-3700GS", "BL-3700GS", "BLα3700GS",
                        "LαZ BLα-3700GS", "LAZ BLa-3700GS"],
            "plant": "宇都宮工場 (Utsunomiya)",
            "sibling_cards": "LAZ-4785(7장) · LAZ-2002/6785(5장) · LAZ-7752 VerJB(1장) — 71차 GD",
            "core7_absent_from_vendor_table": "이 페이지 표에도 **밀도·포아송비·비열·인장강도 행이 없다.** "
                                              "HTML 전문 토큰 검사 — `比重` 0 · `密度` 0 · `ポアソン` 0 · `比熱` 0 · "
                                              "`引張強さ` 0. 있는 것은 `Tensile Modulus` 두 행(모듈러스이지 강도가 아니다). "
                                              "형제 세 장과 같은 결과다.",
            "youngs_modulus_tier_note": "이 카드의 영률은 **t1** 이다 — 행 이름이 `Tensile Modulus` 라 모드가 확정된다. "
                                        "형제 세 장(GD)의 `弾性率` 는 모드 표기가 없어 t3 다. 같은 계열 안에서 등급이 "
                                        "갈리는 이유가 바로 이 표기 차이다.",
        },
    },
    "source": SRC_BU,
    "properties": bu,
}]

# ================================================================ ③ Sumitomo スミライト PL/EL 적층판 — **밀도가 인쇄된 표**

SG_NOTE = (
    "**이것은 라미네이트 자신의 비중이다 — 수지 비중이 아니다.** 브리프가 경계한 함정(`수지 비중은 라미네이트 밀도가 "
    "아니다`)은 MGC 시트의 `樹脂比重`(수지만의 무차원 값)에 대한 것이고, 이 행은 `一般特性 General Properties` 표 안에서 "
    "**적층판 시편**(같은 표의 시편 두께 각주가 걸린 그 시편)에 대해 인쇄된 `比重 Specific gravity` 다. "
    "비중은 정의상 4 ℃ 물 밀도(1000 kg/m³) 기준 무차원비이므로 x1000 은 **역산이 아니라 단위 환산**이다."
)
PLEL_RENDER = (
    "**이 PDF 는 아웃라인 벡터 텍스트라 `pdftotext` 가 0자를 준다** — A3 쪽을 150 dpi 로 렌더해 표를 눈으로 읽었다. "
    "열 밀림 위험은 렌더로만 막을 수 있고 실제로 렌더로만 읽었다. "
    "**교차검증**: `PL-1147`(1.38)과 `EL-3762`(1.92)는 두 표(打抜き加工用 · 機械加工用)에 **모두** 나오고 "
    "두 표의 比重 이 서로 같다 — 열 대응이 맞다는 독립 확인이다. 같은 두 등급의 曲げ強度·吸水率 은 "
    "시편 두께가 달라(1.0/1.5 mmt vs 15/13 mmt) 값이 다른데, **比重만 같다** — 밀도가 두께에 무관하다는 "
    "물리와 앞뒤가 맞는다."
)

PLEL = [
    dict(name="Sumitomo Bakelite Sumilite PL-1131 (paper phenolic laminate, punching grade)",
         label="PL-1131", sg=1.32,
         klass="paper phenolic laminate (紙フェノール積層板)", jis="PL-PEM相当 (PL-PEM equivalent)",
         feat="打抜き性に優れ、寸法変化が少ないボリュームスイッチ用途 / Good punching performance and few dimensional changes for volume switches",
         tables="打抜き加工用 표(인쇄 26쪽)에만 나온다",
         flex=[(150, None, "A", 1.0, "打抜き加工用 표 (시편 1.0 mmt)")],
         wabs=[(1.9, 1.0, "打抜き加工用 표 (시편 1.0 mmt)")]),
    dict(name="Sumitomo Bakelite Sumilite PL-1147 (flame-retardant paper phenolic laminate)",
         label="PL-1147", sg=1.38,
         klass="paper phenolic laminate (紙フェノール積層板), UL94V-0", jis="PL-PEM-PF相当 (PL-PEM-PF equivalent)",
         feat="難燃性が求められる分野での電子部品用途 / The electronic-components required for flame retardancy",
         tables="打抜き加工用(인쇄 26쪽)·機械加工用(인쇄 27쪽) **두 표에 모두** 나온다",
         flex=[(150, None, "A", 1.0, "打抜き加工用 표 (시편 1.0 mmt)"),
               (130, None, "A", 15.0, "機械加工用 표 (시편 15 mmt)")],
         wabs=[(1.3, 1.0, "打抜き加工用 표 (시편 1.0 mmt)"),
               (0.19, 15.0, "機械加工用 표 (시편 15 mmt)")]),
    dict(name="Sumitomo Bakelite Sumilite PL-1102 (paper phenolic laminate, machining grade)",
         label="PL-1102", sg=1.39,
         klass="paper phenolic laminate (紙フェノール積層板)", jis="PL-PEM相当 (PL-PEM equivalent)",
         feat="コストパフォーマンスに優れた標準材 / Standard grade which is excellent in cost performance",
         tables="機械加工用 표(인쇄 27쪽)에만 나온다",
         flex=[(200, None, "A", 15.0, "機械加工用 표 (시편 15 mmt)")],
         wabs=[(0.34, 15.0, "機械加工用 표 (시편 15 mmt)")]),
    dict(name="Sumitomo Bakelite Sumilite EL-3762 (FR-4 grade glass epoxy laminate, unclad)",
         label="EL-3762", sg=1.92,
         klass="glass/epoxy laminate (ガラスエポキシ積層板), unclad, FR-4 grade", jis="EL-GEF相当 (EL-GEF equivalent)",
         feat="G10グレードを上回る難燃性を付与したFR-4グレード / FR-4 grade which gave the flame retardancy which exceeds G10 grade",
         tables="打抜き加工用(인쇄 26쪽)·機械加工用(인쇄 27쪽) **두 표에 모두** 나온다",
         flex=[(540, "warp (たて / Lengthwise)", "A", 1.5, "打抜き加工用 표 (시편 1.5 mmt)"),
               (470, "fill (よこ / Widthwise)", "A", 1.5, "打抜き加工用 표 (시편 1.5 mmt)"),
               (390, "warp (たて / Lengthwise)", "A", 13.0, "機械加工用 표 (시편 13 mmt)"),
               (370, "fill (よこ / Widthwise)", "A", 13.0, "機械加工用 표 (시편 13 mmt)")],
         wabs=[(0.07, 1.5, "打抜き加工用 표 (시편 1.5 mmt)"),
               (0.01, 13.0, "機械加工用 표 (시편 13 mmt)")]),
]

materials_plel = []
for d in PLEL:
    L = d["label"]
    r = rows_single(
        "physical.density", "kg/m^3", d["sg"], lambda v: v * 1000.0,
        {"conditioning": "A (as received, 원문 処理条件 `A`)",
         "basis": "specific gravity (比重) of the laminate, dimensionless, x1000 -> kg/m^3"},
        f"원문 verbatim: `比重 Specific gravity | A | － | {d['sg']}` ({L} 열).",
        SG_NOTE + " " + PLEL_RENDER)
    for v, orient, cond, thk, tbl in d["flex"]:
        c = {"conditioning": cond, "specimen_thickness_mm": thk, "source_table": tbl}
        if orient:
            c["orientation"] = orient
        r += rows_single("mechanical.flexural_strength", "Pa", v, lambda x: x * 1e6, c,
                         f"원문 verbatim: `曲げ強度 Flexural strength | {cond} | MPa | {v}"
                         + (f" ({orient.split(' ')[0]})" if orient else "") + f"` ({L} 열, {tbl}).",
                         "**같은 등급이 두 표에 나오면 시편 두께가 달라 값도 다르다 — 평균 내지 않고 "
                         "`specimen_thickness_mm` 으로 갈라 두 행으로 두었다.** " + PLEL_RENDER
                         if len(d["flex"]) > 1 else PLEL_RENDER)
    for v, thk, tbl in d["wabs"]:
        r += rows_single("chemical.water_absorption_24h", "1", v, PCT,
                         {"test_condition": "E-24/50 + D-24/23 (24 h 50 C oven, then 24 h water immersion at 23 C)",
                          "specimen_thickness_mm": thk, "source_table": tbl},
                         f"원문 verbatim: `吸水率 Water absorption | E-24/50+D-24/23 | % | {v}` ({L} 열, {tbl}).",
                         f"{v} % / 100 = {v / 100:.6g} (무차원). " + PLEL_RENDER)
    materials_plel.append({
        "new_material": {
            "name": d["name"], "category": "composite",
            "description": f"住友ベークライト(Sumitomo Bakelite) スミライト® 적층판 `{L}` — {d['klass']}. "
                           f"벤더 표기 특징: {d['feat']}. JIS 적층판 기호 {d['jis']}. {d['tables']}. "
                           f"**이 카드가 이 배치에 선 이유는 하나다 — 이 표가 `比重 Specific gravity` 를 인쇄한다.** "
                           f"71차 GD 가 「밀도는 규격(IPC-4101) 층이 아니라 벤더 TDS 층의 문제다」라고 넘긴 자리를 "
                           f"같은 벤더의 다른 제품군에서 메운다. 동장적층판(ELC·LαZ) 표에는 이 행이 없다.",
            "attributes": {
                "material_class": d["klass"],
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "전자부품·기계가공용 실부품 적층판. 벤더가 등급명으로 인쇄한 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Sumitomo Bakelite Co., Ltd.",
                "product_series": "スミライト® (Sumilite) PL / EL laminate sheets",
                "product_form": "unclad laminate sheet",
                "aliases": [L, f"Sumilite {L}", f"スミライト {L}", L.replace("-", "")],
                "jis_symbol": d["jis"],
                "density_source": "`比重 Specific gravity` 행 — **라미네이트 자신의 비중**이다(수지 비중이 아니다). "
                                  "x1000 은 정의상 단위 환산이다.",
                "core7_absent_from_vendor_table": "이 표에도 포아송비·비열·인장강도 행은 없다. 있는 것은 "
                                                  "`曲げ強度`(굽힘강도)·`アイゾット衝撃強さ`·`へき開強さ` 다 — "
                                                  "**인장강도가 아니다.** 열전도율 행도 없다.",
                "not_to_be_confused_with": "`EL-3762`(무피복 유리에폭시 적층판)는 `ELC-4762`(동장적층판)와 **다른 제품이다.** "
                                           "비중 1.92 를 ELC-4762 에 옮기면 안 된다.",
                "source_page": "인쇄 26쪽(電子部品用積層板 打抜き加工用) · 인쇄 27쪽(機械・電気機器用積層板 機械加工用)",
            },
        },
        "source": SRC_PLEL,
        "properties": r,
    })

# ================================================================ ④ Hitachi Chemical KOBELITE (KEL) 무피복 적층판 — 여기도 比重 행이 있다

SRC_KEL = {
    "kind": "datasheet",
    "title": "KOBE LITE LAMINATES — Characteristics (t1.0mm) "
             "(Hitachi Chemical Copper Clad Laminates 총합 카탈로그 영문판, 인쇄 89쪽 / PDF 82쪽, 90쪽)",
    "url": None,
    "publisher": "Hitachi Chemical Co., Ltd. (현 Resonac Corporation 의 전신)",
    "year": 2017,
    "local_path": "/data/paper_patent_corpus/standards_appnotes/pcb/"
                  "HitachiChemical_CopperCladLaminates_FullCatalog_en_2017-03.pdf",
    "url_note": "Wayback 로 복구한 구(舊) 히타치화성 총합 카탈로그다(2017-03판). 원 벤더 사이트가 Resonac 으로 "
                "이관되며 사라졌다. **URL 을 지어내지 않았다** — 로컬 원문 90쪽이 근거다.",
}

KEL_RENDER = (
    "**렌더 대조** — 인쇄 89쪽(PDF 82쪽) `■Characteristics（t1.0mm）` 표를 200 dpi 로 렌더해 표 전체를 눈으로 읽었다. "
    "렌더로 확정한 열 순서는 네 열 `KEL-GEF / KEL-GEF(R) | KEL-9383NT | KEL-571 | KEL-973` 다 — "
    "**첫 열은 머리글이 `KEL-GEF` 와 `KEL-GEF（R）` 두 줄이고 값은 한 칸이다**(두 등급이 한 열을 공유한다). "
    "표 아래 문구 verbatim: `The contents of this report are based on the results of experiments conducted by "
    "HITACHI CHEMICAL and do not represent a guarantee of the values for each property.` "
    "각주 verbatim: `*2）Heating Rate:10℃/min.`"
)
KEL_SG_NOTE = (
    "**이것은 라미네이트 자신의 비중이다 — 수지 비중이 아니다.** 같은 표의 시편은 `t1.0mm` 적층판이다. "
    "비중은 정의상 4 ℃ 물 밀도(1000 kg/m³) 기준 무차원비이므로 x1000 은 **역산이 아니라 단위 환산**이다. "
    "**이 배치가 찾은 규칙을 두 번째 벤더에서 확인한 자리다** — 동장적층판(CCL) 표에는 比重/Specific gravity 행이 "
    "없고 **무피복 적층판(laminate sheet) 표에는 있다.** Sumitomo 의 スミライト PL/EL 이 첫 번째였다."
)

KEL = [
    dict(name="Hitachi Chemical KOBELITE KEL-GEF / KEL-GEF(R) (unclad glass/epoxy laminate)",
         label="KEL-GEF / KEL-GEF(R)", sg=(1.7, 1.9),
         base="Glass fabric", jis="EL-GEF",
         flex_s=[("Length", 600, 650), ("Width", 450, 500)],
         flex_m=[("Length", 22, 24), ("Width", 19, 22)],
         cte=[("X", 12, 14), ("Y", 14, 16), ("Z", 50, 70)],
         dk=[("C90/20/65", 4.5, 5.0), ("C90/20/65+D-24/23", 4.6, 5.1)],
         df=[("C90/20/65", 0.016, 0.025), ("C90/20/65+D-24/23", 0.020, 0.026)],
         shared="**원문이 `KEL-GEF` 와 `KEL-GEF（R）` 두 등급에 한 열을 준다** — 값이 같다는 뜻이다. "
                "70차 FA 가 `Sumilite ELC-4762 / ELC-4756` 을 한 장으로 세운 선례를 따라 한 장으로 세웠다."),
    dict(name="Hitachi Chemical KOBELITE KEL-9383NT (unclad glass + non-woven glass epoxy laminate)",
         label="KEL-9383NT", sg=(1.5, 1.7),
         base="Glass fabric + Non-woven glass fabric", jis=None,
         flex_s=[("Length", 350, 410), ("Width", 290, 350)],
         flex_m=[],
         cte=[("X", 20, 22), ("Y", 22, 25), ("Z", 40, 50)],
         dk=[("C90/20/65", 4.3, 4.7), ("C90/20/65+D-24/23", 4.4, 4.8)],
         df=[("C90/20/65", 0.015, 0.022), ("C90/20/65+D-24/23", 0.018, 0.023)],
         shared=None),
    dict(name="Hitachi Chemical KOBELITE KEL-571 (unclad non-woven aramid epoxy laminate)",
         label="KEL-571", sg=(1.4, 1.5),
         base="Non-woven aramid fabric", jis=None,
         flex_s=[("Length", 330, 400), ("Width", 300, 380)],
         flex_m=[("Length", 8.4, 8.6), ("Width", 7.8, 8.0)],
         cte=[("X", 6, 8), ("Y", 8, 10), ("Z", 105, 120)],
         dk=[("C90/20/65", 4.0, 4.2), ("C90/20/65+D-24/23", 4.1, 4.3)],
         df=[("C90/20/65", 0.020, 0.022), ("C90/20/65+D-24/23", 0.021, 0.023)],
         shared=None),
    dict(name="Hitachi Chemical KOBELITE KEL-973 (unclad aramid/polyester epoxy laminate)",
         label="KEL-973", sg=(1.5, 1.6),
         base="Non-woven aramid fabric + Polyester fabric", jis=None,
         flex_s=[("Length", 200, 220), ("Width", 170, 190)],
         flex_m=[("Length", 7.4, 7.6), ("Width", 6.6, 6.8)],
         cte=[("X", 27, 30), ("Y", 38, 40)],
         dk=[], df=[],
         shared=None),
]

materials_kel = []
for d in KEL:
    L = d["label"]
    r = rows_range("physical.density", "kg/m^3", d["sg"][0], d["sg"][1], lambda v: v * 1000.0,
                   {"conditioning": "A (as received, 원문 Condition `A`)",
                    "specimen_thickness_mm": 1.0,
                    "basis": "specific gravity of the laminate, dimensionless, x1000 -> kg/m^3"},
                   f"원문 verbatim: `specific gravity | A | － | {d['sg'][0]}〜{d['sg'][1]}` ({L} 열).",
                   KEL_SG_NOTE + " " + KEL_RENDER)
    for ax, lo, hi in d["cte"]:
        r += rows_range("thermal.expansion_linear", "1/K", lo, hi, PPM,
                        {"axis": f"{'in-plane' if ax in 'XY' else 'through-thickness'} ({ax})",
                         "temperature_range_c": "30-80", "heating_rate_c_per_min": 10,
                         "specimen_thickness_mm": 1.0, "conditioning": "A"},
                        f"원문 verbatim: `CTE *2 (30〜80℃) | {ax} | A | 1/℃ | {lo}〜{hi}x10^-6` ({L} 열).",
                        "**원문 단위가 이미 `1/℃` 이고 값에 `x10⁻⁶` 가 붙어 있다** — ppm 표기가 아니다. "
                        "`x1e-6` 은 원문이 인쇄한 지수를 그대로 편 것이다. " + KEL_RENDER)
    for orient, lo, hi in d["flex_s"]:
        r += rows_range("mechanical.flexural_strength", "Pa", lo, hi, lambda v: v * 1e6,
                        {"orientation": f"{'warp (Length)' if orient == 'Length' else 'fill (Width)'}",
                         "conditioning": "A", "specimen_thickness_mm": 1.0},
                        f"원문 verbatim: `Flexural strength | {orient} | A | N/mm² | {lo}〜{hi}` ({L} 열).",
                        "N/mm² = MPa 다. " + KEL_RENDER)
    for orient, lo, hi in d["flex_m"]:
        r += rows_range("mechanical.flexural_modulus", "Pa", lo, hi, GPa,
                        {"orientation": f"{'warp (Length)' if orient == 'Length' else 'fill (Width)'}",
                         "conditioning": "A", "specimen_thickness_mm": 1.0},
                        f"원문 verbatim: `Flexural Modulus | {orient} | A | kN/mm² | {lo}〜{hi}` ({L} 열).",
                        "**단위가 `kN/mm²` 다 — 1 kN/mm² = 1e3 N / 1e-6 m² = 1e9 Pa = 1 GPa** 이므로 "
                        "GPa 와 수치가 같다. " + KEL_RENDER)
    for cond, lo, hi in d["dk"]:
        r += rows_range("electrical.dielectric_constant", "1", lo, hi, IDENT,
                        {"frequency": "1 MHz", "conditioning": cond, "specimen_thickness_mm": 1.0},
                        f"원문 verbatim: `Dielectric Constant （1MHz） | {cond} | － | {lo}〜{hi}` ({L} 열).",
                        "**두 전처리 조건이 별개 행이라 두 행으로 두었다.** " + KEL_RENDER)
    for cond, lo, hi in d["df"]:
        r += rows_range("electrical.dissipation_factor", "1", lo, hi, IDENT,
                        {"frequency": "1 MHz", "conditioning": cond, "specimen_thickness_mm": 1.0},
                        f"원문 verbatim: `Dissipation Factor （1MHz） | {cond} | － | {lo}〜{hi}` ({L} 열).",
                        "**두 전처리 조건이 별개 행이라 두 행으로 두었다.** " + KEL_RENDER)
    materials_kel.append({
        "new_material": {
            "name": d["name"], "category": "composite",
            "description": f"Hitachi Chemical(현 Resonac 전신) `KOBELITE LAMINATE` 계열 무피복 적층판 `{L}` — "
                           f"기재 {d['base']}, 수지 에폭시, 색 Natural color. "
                           f"**이 카드가 이 배치에 선 이유는 하나다 — 이 표가 `specific gravity` 를 인쇄한다.** "
                           f"같은 카탈로그 90쪽 중 동장적층판(MCL·CEL·EM 계열) 표 어디에도 그 행이 없는데 "
                           f"**무피복 적층판 표에만 있다.** 같은 규칙을 이 배치가 Sumitomo スミライト PL/EL 에서도 "
                           f"확인했다 — 밀도는 CCL 층이 아니라 적층판 시트 층에 있다. "
                           + (d["shared"] or ""),
            "attributes": {
                "material_class": f"unclad epoxy laminate sheet (KOBELITE KEL series), base: {d['base']}",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "무피복 적층판 실부품(절연·기구 부품용 시트). 벤더가 등급명으로 인쇄한 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Hitachi Chemical Co., Ltd. (현 Resonac Corporation)",
                "product_series": "KOBELITE LAMINATE (KEL)",
                "product_form": "unclad laminate sheet",
                "aliases": [x for x in [L] + [s.strip() for s in L.split("/")] + [L.replace("-", "")] if x],
                **({"jis_symbol": d["jis"]} if d["jis"] else {}),
                "density_source": "`specific gravity` 행 — **라미네이트 자신의 비중**이다(수지 비중이 아니다). "
                                  "시편 `t1.0mm`. x1000 은 정의상 단위 환산이다.",
                "core7_absent_from_vendor_table": "이 표에도 **포아송비·비열·인장강도 행은 없다.** 있는 것은 "
                                                  "`Flexural strength`·`Compressive Strength`·`Izod impact strength`·"
                                                  "`Cleavage Strength` 다 — **인장강도가 아니다.** 열전도율 행도 없다.",
                "vendor_lineage_note": "Hitachi Chemical → Showa Denko Materials → Resonac. 이 카탈로그는 "
                                       "71차 GD·72차 HD 가 쓴 Resonac MCL 카탈로그의 **선대 문서**다.",
                "source_page": "인쇄 89쪽 / PDF 82쪽 `■Characteristics（t1.0mm）`",
            },
        },
        "source": SRC_KEL,
        "properties": r,
    })

# ================================================================ 자체검증 + 쓰기

UNITS = {
    "physical.density": "kg/m^3", "mechanical.youngs_modulus": "Pa",
    "mechanical.flexural_strength": "Pa", "chemical.water_absorption_24h": "1",
    "mechanical.flexural_modulus": "Pa",
    "mechanical.poisson_ratio": "1", "mechanical.tensile_strength": "Pa",
    "mechanical.flexural_modulus": "Pa",
    "thermal.expansion_linear": "1/K", "thermal.conductivity": "W/(m*K)",
    "thermal.specific_heat": "J/(kg*K)", "thermal.glass_transition": "K",
    "electrical.dielectric_constant": "1", "electrical.dissipation_factor": "1",
    "interface.peel_strength": "N/m", "chemical.water_absorption_saturation": "1",
}
METHODS = {"measured", "handbook", "datasheet", "computed", "estimated", "digitized"}


def check(docs):
    errs, names = [], set()
    n_prop = 0
    for fn, doc in docs:
        for e in doc["materials"]:
            nm = e.get("match_name") or e["new_material"]["name"]
            if "new_material" in e:
                if nm in names:
                    errs.append(f"{fn}: 이름 중복 {nm}")
                names.add(nm)
                if len(nm) > 200:
                    errs.append(f"{fn}: 이름 {len(nm)}자 > 200 — {nm[:60]}")
                a = e["new_material"].get("attributes") or {}
                for k in ("role", "aliases"):
                    if not a.get(k):
                        errs.append(f"{fn}: {nm} attributes.{k} 없음")
            if not (e["source"].get("url") or e["source"].get("title")):
                errs.append(f"{fn}: {nm} 출처 없음")
            for p in e["properties"]:
                n_prop += 1
                if UNITS.get(p["key"]) != p["unit"]:
                    errs.append(f"{fn}: {nm} {p['key']} 단위 {p['unit']} != {UNITS.get(p['key'])}")
                if p["method"] not in METHODS:
                    errs.append(f"{fn}: {nm} method 어휘 위반 {p['method']}")
                if p["tier"] == 4:
                    errs.append(f"{fn}: {nm} **t4 금지** {p['key']}")
                if p["tier"] == 3 and not p["conditions"].get("grade_scope"):
                    errs.append(f"{fn}: {nm} t3 인데 grade_scope 없음 {p['key']}")
                if not p.get("notes"):
                    errs.append(f"{fn}: {nm} notes 없음 {p['key']}")
    return errs, n_prop


docs = [
    ("hd72_01_resonac_en_catalog.json", {"batch": "72차 HD", "materials": materials_en}),
    ("hd72_02_sumitomo_laz_buildup.json", {"batch": "72차 HD", "materials": materials_bu}),
    ("hd72_03_sumitomo_plel_laminates.json", {"batch": "72차 HD", "materials": materials_plel}),
    ("hd72_04_hitachi_kobelite_kel.json", {"batch": "72차 HD", "materials": materials_kel}),
]
errs, n_prop = check(docs)
for fn, doc in docs:
    (OUT / fn).write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")

n_new = sum(1 for _, d in docs for e in d["materials"] if "new_material" in e)
n_match = sum(1 for _, d in docs for e in d["materials"] if "match_name" in e)
print(f"재료 항목 {n_new + n_match} (신규 카드 {n_new} · 기존 카드 보강 {n_match}) · 물성 {n_prop}행")
tiers = {}
for _, d in docs:
    for e in d["materials"]:
        for p in e["properties"]:
            tiers[p["tier"]] = tiers.get(p["tier"], 0) + 1
print("등급 분포:", dict(sorted(tiers.items())))
print("자체검증 오류:", len(errs))
for x in errs:
    print("  ✗", x)
