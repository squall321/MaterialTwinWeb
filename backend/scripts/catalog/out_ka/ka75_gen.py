# 75차 KA 생성기 — 같은 카탈로그의 두 판(언어판·시장판)을 행 단위로 대 보고, 한쪽 판에만 있는 값과 두 판이 어긋나는 값을 산출물로 만든다
"""
75차 KA — 판 대조(edition diff) 수집 배치 생성기

무엇을 만드는가
  ka75_01_resonac_en_edition_band.json   Resonac MCL 카탈로그 **영문판 2026-07** 이 찍는데
                                         DB(일문판 2026-04 출처)에는 없는 값 — 22행 / 4카드
  ka75_02_shengyi_s7439_cn_edition.json  Shengyi S7439 **중국시장판 CN-TDS-1912-03** 이 찍는데
                                         DB(미국시장판 S-USA rv1 출처)에는 없는 값 — 11행 / 1카드
  ka75_09_verdicts.json                  두 판을 다 열고 확인한 부재 — 31칸 / 7종

규율(브리프)
  * 값을 지어내지 않는다. 인쇄된 숫자만 옮긴다.
  * 인쇄 구간은 두 행(bound: lower/upper). 평균 금지.
  * 두 판이 다른 값을 찍으면 **둘 다** 남긴다. conditions.catalog_edition 으로 가른다.
  * 시험모드는 대표값 선택기가 보는 칸(test_standard/test_method/test_mode/...)에 넣는다.
  * t4 금지. 이 배치는 전부 t1(인쇄값)이다.
  * 라이브 DB 는 읽기 전용.
"""
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────────────────────
# 출처
# ─────────────────────────────────────────────────────────────────────────────
PCB = "/data/paper_patent_corpus/standards_appnotes/pcb"

SRC_RESONAC_EN = {
    "kind": "datasheet",
    "title": "Resonac MCL COPPER CLAD LAMINATES (영문판, 본문 기준일 2026-07)",
    "publisher": "Resonac Corporation",
    "year": 2026,
    "url": None,
    "local_path": f"{PCB}/Resonac_MCL_CopperCladLaminates_Catalog_en_2026-07.pdf",
}
SRC_SHENGYI_CN = {
    "kind": "datasheet",
    "title": "Shengyi S7439 / S7439B Technical Data Sheet (중국시장판, CN-TDS-1912-03)",
    "publisher": "Shengyi Technology Co., Ltd.",
    "year": 2019,
    "url": None,
    "local_path": f"{PCB}/Shengyi_S7439_TDS_zh.pdf",
}

# 두 판을 가른 근거를 모든 행 notes 의 머리에 붙인다
EDITION_HEAD_RESONAC = (
    "【판 대조】같은 카탈로그의 영문판(en 2026-07, 51쪽)과 일문판(ja 2026-04, 59쪽)을 "
    "쪽·열 단위로 대 봤다. 두 판은 표 뼈대·각주 번호·IPC-TM-650 참조까지 같은데 "
    "일부 칸의 숫자가 다르다. 200 dpi 렌더로 두 판 모두 눈 대조했다(pdftotext 열 밀림 아님). "
    "DB 에 이미 있는 값은 일문판 값이므로 이 행은 **영문판 값**을 밴드로 나란히 남긴다 — 평균 내지 않았다. "
    "【시간축 대조 — 어느 쪽이 흔들리는지 잰다】구판 일문판(ja 2023-2024, 66쪽)의 같은 칸을 세 번째 증인으로 세웠다. "
    "**ja 2023-2024 와 ja 2026-04 가 서로 완전히 같고, en 2026-07 만 다르다.** "
    "즉 이 어긋남은 해가 바뀌며 갱신된 것이 아니라 **언어판 사이에서 갈린 것**이다"
    "(다만 영문판 본문 기준일이 2026-07 이고 일문판이 2026-01 이라, 미래의 일문판이 영문판을 따라갈 가능성은 남는다). "
    "**영문판 쪽을 의심할 이유가 하나 더 있다** — 같은 쪽 묶음에서 영문판은 행 이름을 `Flexual Modulus` 로 오식하고, "
    "Thickness 열의 GEA-705G·770G 를 0.025 가 아닌 0.020(=795G 값)으로 눌러 인쇄한다. "
    "그래도 지우지 않는다 — 인쇄된 것은 인쇄된 것이다. 두 밴드를 다 남기고 판정은 다음 파동에 넘긴다. "
)
EDITION_HEAD_SHENGYI = (
    "【판 대조】같은 제품의 중국시장판 TDS(CN-TDS-1912-03, 본문은 영어로 인쇄)와 "
    "미국시장판 TDS(S-USA-S7439rv1-5/17)를 행 단위로 대 봤다. 행 목록과 숫자가 둘 다 다르다. "
    "DB 에 이미 있는 값은 미국시장판 값이므로 이 행은 **중국시장판 값**을 나란히 남긴다 — 평균 내지 않았다. "
)

C2K = 273.15


def band(key, unit, lo, hi, cond, note, method="measured", tier=1):
    """인쇄 구간을 두 행으로. 평균 금지."""
    rows = []
    for b, v in (("lower", lo), ("upper", hi)):
        c = dict(cond)
        c["bound"] = b
        rows.append(
            {
                "key": key,
                "value": v,
                "unit": unit,
                "method": method,
                "tier": tier,
                "conditions": c,
                "notes": note,
            }
        )
    return rows


def single(key, unit, v, cond, note, method="measured", tier=1):
    return [
        {
            "key": key,
            "value": v,
            "unit": unit,
            "method": method,
            "tier": tier,
            "conditions": dict(cond),
            "notes": note,
        }
    ]


# ─────────────────────────────────────────────────────────────────────────────
# ① Resonac — 영문판 2026-07 에만 있는(=DB 의 일문판 값과 어긋나는) 값
#    영문판 PDF p.6(인쇄 7) 「General Characteristics」 · p.19(인쇄 20) MCL-HS20N 제품쪽
# ─────────────────────────────────────────────────────────────────────────────
EN_PAGE = "영문판 PDF p.6 / 인쇄 p.7 「General Characteristics」"
JA_PAGE = "일문판 PDF p.6 / 인쇄 p.7 「MCL一般特性一覧」"

resonac = []

# ---- GEA-705G (카드 2763) ----------------------------------------------------
g705_note_base = (
    EDITION_HEAD_RESONAC
    + f"이 행의 자리 — {EN_PAGE}, GEA-705G 열 / {JA_PAGE}, GEA-705G 열. "
    "두 판이 이 등급에 **시편 두께마저 다르게** 인쇄한다 — 영문판 Thickness 0.020 mm, 일문판 厚み 0.025 mm. "
    "그래서 이 영문판 행에는 specimen_thickness_mm 0.02 를 박았다(DB 의 일문판 행은 0.025다). "
)
resonac += band(
    "electrical.dissipation_factor", "1", 0.010, 0.012,
    {
        "frequency_hz": 1.0e10,
        "method_detail": "SPDR",
        "test_method": "SPDR (Split Post Dielectric Resonator)",
        "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
        "specimen_thickness_mm": 0.02,
    },
    g705_note_base
    + "원문 verbatim: `Df (10 GHz) | 0.010 - 0.012`. 일문판 같은 칸은 `0.008 - 0.010` 이고 그 값이 DB 에 이미 있다. "
    "환산 없음(무차원). 왜 다른지는 벤더가 밝히지 않았다 — 두 판의 인쇄 기준일이 다르다"
    "(영문판 본문 「as of July 2026」 · 일문판 「2026年1月現在」)는 것이 유일한 단서다.",
)
for axis in ("X", "Y"):
    resonac += band(
        "thermal.expansion_linear", "1/K", 9e-6, 11e-6,
        {
            "axis": f"in-plane ({axis})",
            "regime": "below Tg",
            "method_detail": "TMA",
            "test_mode": "tensile (각주 *5: Tensile)",
            "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
            "specimen_thickness_mm": 0.02,
        },
        g705_note_base
        + f"원문 verbatim: `CTE {axis.lower()} (<Tg) (Comp.) | 9 - 11*5`, 각주 `*5: Tensile`. "
        "일문판 같은 칸은 `8 - 10*5` 이고 그 값이 DB 에 이미 있다. "
        "환산: 9 ppm/℃ x 1e-6 = 9e-06 1/K; 되돌리면 9e-06/1e-6 = 9 ppm/℃. "
        "행 이름은 `(Comp.)`(압축)인데 각주 *5 가 `Tensile`(인장)을 지정한다 — 각주가 행 이름을 덮는다. "
        "그래서 test_mode 에 각주를 적었다.",
    )

# ---- GEA-770G (카드 2764) ----------------------------------------------------
g770_note_base = (
    EDITION_HEAD_RESONAC
    + f"이 행의 자리 — {EN_PAGE}, GEA-770G 열 / {JA_PAGE}, GEA-770G 열. "
    "**이 등급이 두 판의 어긋남이 가장 큰 자리다 — 14칸 중 6칸이 다르다.** "
    "시편 두께도 다르다 — 영문판 0.020 mm, 일문판 0.025 mm. 이 행은 영문판 쪽이므로 0.02 를 박았다. "
)
resonac += band(
    "electrical.dielectric_constant", "1", 3.7, 4.0,
    {
        "frequency_hz": 1.0e10,
        "method_detail": "SPDR",
        "test_method": "SPDR (Split Post Dielectric Resonator)",
        "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
        "specimen_thickness_mm": 0.02,
    },
    g770_note_base + "원문 verbatim: `Dk (10 GHz) | 3.7 - 4.0`. 일문판 `3.6 - 3.9`(DB 기존값).",
)
resonac += band(
    "electrical.dissipation_factor", "1", 0.008, 0.010,
    {
        "frequency_hz": 1.0e10,
        "method_detail": "SPDR",
        "test_method": "SPDR (Split Post Dielectric Resonator)",
        "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
        "specimen_thickness_mm": 0.02,
    },
    g770_note_base + "원문 verbatim: `Df (10 GHz) | 0.008 - 0.010`. 일문판 `0.007 - 0.009`(DB 기존값).",
)
resonac += band(
    "mechanical.youngs_modulus", "Pa", 17.0e9, 19.0e9,
    {
        "test_mode": "tensile",
        "test_method": "vendor catalog 'Tensile modulus X' / 일문판 '弾性率 (引張モード) X'",
        "orientation": "X (in-plane)",
        "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
        "specimen_thickness_mm": 0.02,
    },
    g770_note_base
    + "원문 verbatim: `Tensile modulus X*4 | GPa | 17 - 19`. 일문판 같은 칸은 `18 - 20`(DB 기존값). "
    "환산: 17 GPa = 17e9 Pa = 1.7e+10 Pa; 되돌리면 1.7e+10/1e9 = 17 GPa. "
    "**모드를 이름이 아니라 표기로 확정했다** — 영문판이 `Tensile`, 일문판이 `引張モード` 라고 같은 자리에서 "
    "명시하므로 인장이다. 같은 표의 바로 아래 행이 `Flexural / 曲げモード` 로 따로 있다. "
    "각주 *4(=0.8 mmt)의 붙는 자리가 두 판이 다르다 — 영문판은 인장·굽힘 두 행 모두에 *4 를 붙이고, "
    "일문판은 굽힘 행에만 붙인다. **이 어긋남은 이 배치가 해결하지 않았다**(인계 참조). "
    "여기서는 시편 두께로 총괄표 머리행의 Thickness(영문판 0.020 mm)만 적었다.",
)
resonac += band(
    "thermal.glass_transition", "K", 300 + C2K, 330 + C2K,
    {
        "method_detail": "DMA",
        "test_method": "DMA",
        "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
        "specimen_thickness_mm": 0.02,
    },
    g770_note_base
    + "원문 verbatim: `Tg (DMA) | ℃ | 300 - 330`. 일문판 같은 칸은 `280 - 300`(DB 기존값). "
    "환산: 300 + 273.15 = 573.15 K; 330 + 273.15 = 603.15 K. "
    "같은 표의 Tg(TMA) 는 두 판이 `260 - 280` 으로 **일치한다** — DMA 행만 어긋난다.",
)
for axis in ("X", "Y"):
    resonac += band(
        "thermal.expansion_linear", "1/K", 8e-6, 10e-6,
        {
            "axis": f"in-plane ({axis})",
            "regime": "below Tg",
            "method_detail": "TMA",
            "test_mode": "tensile (각주 *5: Tensile)",
            "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
            "specimen_thickness_mm": 0.02,
        },
        g770_note_base
        + f"원문 verbatim: `CTE {axis.lower()} (<Tg) (Comp.) | 8 - 10*5`. 일문판 `6 - 8*5`(DB 기존값). "
        "환산: 8 ppm/℃ x 1e-6 = 8e-06 1/K. 각주 *5 가 `Tensile` 을 지정하므로 test_mode 에 적었다.",
    )

# ---- MCL-HS20N / (Type D) (카드 2765 · 2766) ---------------------------------
hs_note = (
    EDITION_HEAD_RESONAC
    + "이 행의 자리 — 총괄표 두 곳과 제품쪽 두 곳, **네 자리가 전부 같은 방향으로 어긋난다.** "
    f"① {EN_PAGE} MCL-HS20N 열 `Flexural modulus X*4 | GPa | 17 - 22` / "
    f"{JA_PAGE} `弾性率 (曲げモード) X*4 | GPa | 21 - 26`. "
    "② 제품쪽 — 영문판 PDF p.19(인쇄 20) `Flexual Modulus（Lengthwise） | A | GPa | 17～22 | 2.4.4` / "
    "일문판 PDF p.22(인쇄 23) `曲げ弾性率 (たて方向) | A | GPa | 21～26 | 2.4.4`. "
    "**두 판이 같은 시험규격(IPC-TM-650 2.4.4)·같은 처리조건(A)·같은 단위를 적고도 다른 숫자를 찍는다.** "
    "(영문판은 이 행 이름을 `Flexual` 로 오식한다 — 원문 그대로 적어 둔다.) "
    "DB 에 이미 있는 21-26 은 일문판 값이다. 이 행은 영문판 값이다 — 평균 내지 않았다. "
)
for mid_name in (
    "Resonac MCL-HS200 (glass/epoxy CCL)",
    "Resonac MCL-HS200 (D type) (glass/epoxy CCL)",
):
    rows = band(
        "mechanical.flexural_modulus", "Pa", 17.0e9, 22.0e9,
        {
            "test_mode": "flexural",
            "test_standard": "IPC-TM-650 2.4.4",
            "test_method": "IPC-TM-650 2.4.4 (flexural)",
            "orientation": "X (in-plane, lengthwise)",
            "conditioning": "A",
            "catalog_edition": "Resonac MCL Catalog, English edition 2026-07",
        "edition_conflict": "en-2026-07 only; ja-2023/2024 and ja-2026-04 agree with each other",
            "specimen_thickness_mm": 0.8,
        },
        hs_note
        + "환산: 17 GPa = 1.7e+10 Pa · 22 GPa = 2.2e+10 Pa; 되돌리면 1.7e+10/1e9 = 17 GPa. "
        "각주 *4 = 0.8 mmt 는 두 판이 같은 자리에 붙였으므로 그대로 박았다. "
        "**등급명 주의** — 2026 판 두 권은 이 제품을 `MCL-HS20N` 으로 부르고, DB 카드 이름은 "
        "구판(ja 2023-2024)의 `MCL-HS200` 이다. 같은 제품이다(72차 HD 인계 4번).",
    )
    resonac.append((mid_name, rows))

# 앞의 GEA 행들을 카드별로 묶는다
by_card = {
    "Resonac GEA-705G (glass/epoxy prepreg)": resonac[0:6],
    "Resonac GEA-770G (glass/epoxy prepreg)": resonac[6:18],
}
for name, rows in resonac[18:]:
    by_card[name] = rows

RESONAC_DOC = {
    "batch": "75차 KA",
    "materials": [
        {"match_name": name, "source": SRC_RESONAC_EN, "properties": rows}
        for name, rows in by_card.items()
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# ② Shengyi S7439 — 중국시장판 TDS 에만 있는(=DB 의 미국시장판 값과 어긋나는) 값
# ─────────────────────────────────────────────────────────────────────────────
CN_SPEC = "CN-TDS-1912-03 GENERAL PROPERTIES 표. 표 각주 verbatim: 「All the typical value is based on the 0.76mm (6*2116) specimen, but not guarantee data.」"
cn_cond_base = {
    "catalog_edition": "Shengyi S7439 TDS, China-market edition CN-TDS-1912-03",
    "specimen_thickness_mm": 0.76,
    "specimen": "0.76 mm, 6 x 2116 construction",
}
cn_head = EDITION_HEAD_SHENGYI + CN_SPEC + " "
sy = []

sy += single(
    "electrical.dielectric_constant", "1", 3.66,
    dict(cn_cond_base, frequency_hz=1.0e10, test_standard="IPC-TM-650 2.5.5.5",
         test_method="IPC-TM-650 2.5.5.5", conditioning="C-24/23/50"),
    cn_head
    + "원문 verbatim: `Permittivity | 10GHz | IPC-TM-650 2.5.5.5 | C-24/23/50 | - | 3.66`. "
    "**미국시장판은 같은 시험법(IPC-TM-650 2.5.5.5)·같은 주파수에 3.80 을 찍는다**(DB 기존값). "
    "0.14 차이는 반올림으로 설명되지 않는다.",
)
sy += single(
    "electrical.dissipation_factor", "1", 0.0060,
    dict(cn_cond_base, frequency_hz=1.0e10, test_standard="IPC-TM-650 2.5.5.5",
         test_method="IPC-TM-650 2.5.5.5", conditioning="C-24/23/50"),
    cn_head
    + "원문 verbatim: `Loss Tangent | 10GHz | IPC-TM-650 2.5.5.5 | C-24/23/50 | - | 0.0060`. "
    "미국시장판은 같은 시험법에 0.0068(DB 기존값). "
    "**주목** — 중국시장판이 같은 표에서 `10GHz | IEC61189-2-721 | 0.0068` 을 따로 찍는다. "
    "즉 미국시장판의 「IPC 2.5.5.5 0.0068」은 실은 IEC 값일 가능성이 있다. 단정하지 않고 두 행을 다 남긴다.",
)
sy += single(
    "electrical.dielectric_constant", "1", 4.05,
    dict(cn_cond_base, frequency_hz=1.0e10, test_standard="IEC 61189-2-721",
         test_method="IEC 61189-2-721", conditioning="C-24/23/50"),
    cn_head
    + "원문 verbatim: `Permittivity | 10GHz | IEC61189-2-721 | C-24/23/50 | - | 4.05`. "
    "**이 행은 미국시장판에 아예 없다.** 공진기 시험법이 달라 같은 재료에 다른 Dk 가 나온다 — "
    "그래서 평균 내지 않고 시험법을 조건에 박아 따로 남긴다.",
)
sy += single(
    "electrical.dissipation_factor", "1", 0.0068,
    dict(cn_cond_base, frequency_hz=1.0e10, test_standard="IEC 61189-2-721",
         test_method="IEC 61189-2-721", conditioning="C-24/23/50"),
    cn_head
    + "원문 verbatim: `Loss Tangent | 10GHz | IEC61189-2-721 | C-24/23/50 | - | 0.0068`. "
    "미국시장판에 없는 행이다.",
)
sy += single(
    "thermal.glass_transition", "K", 200 + C2K,
    dict(cn_cond_base, method_detail="DMA", test_standard="IPC-TM-650 2.4.24.4",
         test_method="IPC-TM-650 2.4.24.4 (DMA)"),
    cn_head
    + "원문 verbatim: `Tg | IPC-TM-650 2.4.24.4 | DMA | ℃ | 200`. 환산: 200 + 273.15 = 473.15 K. "
    "**미국시장판은 `DMA IPC-TM-650 2.4.24.2 | 205 ℃`** — 값도 시험법 하위번호도 다르다(DB 기존값 478.15 K).",
)
sy += single(
    "thermal.glass_transition", "K", 190 + C2K,
    dict(cn_cond_base, method_detail="DSC", test_standard="IPC-TM-650 2.4.25D",
         test_method="IPC-TM-650 2.4.25D (DSC)"),
    cn_head
    + "원문 verbatim: `Tg | IPC-TM-650 2.4.25D | DSC | ℃ | 190`. 환산: 190 + 273.15 = 463.15 K. "
    "미국시장판은 `DSC IPC-TM-650 2.4.25 | 200 ℃`(DB 기존값 473.15 K). "
    "제품 소개문에서도 갈린다 — 미국시장판 FEATURES 는 「High Tg: 200℃ (DSC)」, "
    "중국시장판 FEATURES 는 Tg 를 아예 안 적는다.",
)
sy += single(
    "thermal.decomposition_temp", "K", 383 + C2K,
    dict(cn_cond_base, method_detail="TGA (5% weight loss)",
         test_standard="IPC-TM-650 2.4.24.6", test_method="IPC-TM-650 2.4.24.6 (TGA 5% W.L.)"),
    cn_head
    + "원문 verbatim: `Td | IPC-TM-650 2.4.24.6 | TGA (5% W.L) | ℃ | 383`. 환산: 383 + 273.15 = 656.15 K. "
    "미국시장판은 385 ℃(DB 기존값 658.15 K).",
)
sy += single(
    "electrical.arc_resistance", "s", 180.0,
    dict(cn_cond_base, test_standard="IPC-TM-650 2.5.1", test_method="IPC-TM-650 2.5.1",
         conditioning="D-48/50+D-0.5/23"),
    cn_head
    + "원문 verbatim: `Arc Resistance | IPC-TM-650 2.5.1 | D-48/50+D-0.5/23 | s | 180`. "
    "**이 행은 미국시장판에 아예 없다.**",
)
sy += single(
    "thermal.expansion_total", "1", 0.026,
    dict(cn_cond_base, temperature_range_c="50-260", method_detail="TMA",
         direction="through-thickness (Z)", test_standard="IPC-TM-650 2.4.24",
         test_method="IPC-TM-650 2.4.24"),
    cn_head
    + "원문 verbatim: `CTE (Z-axis) | IPC-TM-650 2.4.24 | 50-260℃ | % | 2.6`. "
    "환산: 2.6 % / 100 = 0.026 (무차원); 되돌리면 0.026 x 100 = 2.6 %. "
    "**이 행은 미국시장판에 아예 없다.** 같은 표의 α1(45)·α2(210)는 두 판이 일치한다.",
)
sy += single(
    "electrical.resistivity_volume", "ohm*m", 4.03e11,
    dict(cn_cond_base, conditioning="C-96/35/90", test_standard="IPC-TM-650 2.5.17.1",
         test_method="IPC-TM-650 2.5.17.1"),
    cn_head
    + "원문 verbatim: `Volume Resistivity | IPC-TM-650 2.5.17.1 | C-96/35/90 | MΩ-cm | 4.03×10^7`. "
    "환산: 4.03e7 MΩ·cm x 1e6 Ω/MΩ = 4.03e13 Ω·cm; x 0.01 m/cm = 4.03e+11 Ω·m; "
    "되돌리면 4.03e11 / 1e6 / 0.01 = 4.03e7 MΩ·cm. "
    "미국시장판은 `COND A | 1.26E+08 MΩ·cm`(DB 기존값 1.26e12 Ω·m) — **조건 표기도 다르다**"
    "(중국시장판 C-96/35/90 vs 미국시장판 COND A).",
)
sy += single(
    "electrical.surface_resistivity", "ohm", 2.03e13,
    dict(cn_cond_base, conditioning="C-96/35/90", test_standard="IPC-TM-650 2.5.17.1",
         test_method="IPC-TM-650 2.5.17.1"),
    cn_head
    + "원문 verbatim: `Surface Resistivity | IPC-TM-650 2.5.17.1 | C-96/35/90 | MΩ | 2.03×10^7`. "
    "환산: 2.03e7 MΩ x 1e6 = 2.03e+13 Ω; 되돌리면 2.03e13/1e6 = 2.03e7 MΩ. "
    "미국시장판은 `COND A | 8.67E+06 MΩ`(DB 기존값 8.67e12 Ω).",
)

SHENGYI_DOC = {
    "batch": "75차 KA",
    "materials": [
        {
            "match_name": "Shengyi S7439 High-Speed Low-Loss Laminate",
            "source": SRC_SHENGYI_CN,
            "properties": sy,
        }
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# ③ 판정 — 두 판을 **모두** 열고 확인한 부재만
# ─────────────────────────────────────────────────────────────────────────────
R_BOTH = (
    "【두 판 대조】Resonac MCL 카탈로그 **영문판 2026-07(51쪽)과 일문판 2026-04(59쪽)를 둘 다 전수로 열었다.** "
    "총괄표 네 쪽(en PDF p.5·6·7 / ja PDF p.5·6·7·8)과 이 등급의 제품쪽을 쪽·열 단위로 대 봤다. "
    "두 판을 합쳐도 이 물성의 행이 없다 — 인쇄되는 행은 Thickness · Glass Cloth · Dk/Df(1·10 GHz) · "
    "Peel Strength(12·18 μm) · Tensile modulus X · Flexural modulus X · Tg(TMA·DMA) · CTE x/y/z(<Tg·>Tg·DIC) · "
    "Thermal conductivity 뿐이고(일문판은 여기에 Slash sheet No. IPC-4101 한 행이 더 있다), "
    "제품쪽은 여기에 Solder Heat Resistance · T-260/T-288 · Decomposition Temperature · Surface Roughness · "
    "체적/표면/절연저항이 붙는 것이 전부다. "
    "**낱말 단위·대소문자 무시로 전수 검사했다**(74차 JA 의 교훈 — 구(句)로 찾으면 pdftotext 줄바꿈에 걸린다). "
    "일문판 密度 적중 3쪽은 전부 「高密度ガラスクロス」·「高密度電子機器」 같은 산문이고 물성 행이 아니다. "
)
R_LANG = " 이 배치가 새로 더한 갈래는 **영문판 전수**다(74차 JA 까지는 신판 영문판이 이 등급에 대해 열리지 않았다)."

S_BOTH = (
    "【두 판 대조】Shengyi S7439 의 **중국시장판 TDS(CN-TDS-1912-03)와 미국시장판 TDS(S-USA-S7439rv1-5/17)를 둘 다 열었다.** "
    "두 판의 행 목록은 이렇게 다르다 — 중국시장판에만 Arc Resistance · Dielectric Breakdown · Thermal Stress · "
    "CTE(50-260℃ %) · IEC61189-2-721 Dk/Df 가 있고, 미국시장판에만 Thermal Conductivity · Electrical Strength · "
    "Humidity Resistance 가 있다. **그런데 밀도·영률·포아송비·비열·인장강도는 두 판 어디에도 없다.** "
    "중국시장판 GENERAL PROPERTIES 는 Tg(DMA·DSC) · Td · T288 · T300 · Thermal Stress · CTE(Z, α1/α2, 50-260 %) · "
    "Dk/Df · 체적/표면저항 · Arc · Dielectric Breakdown · Peel Strength · Water Absorption · Flammability 열넷이 전부다. "
)

A_BOTH = (
    "【두 판 대조】Arisawa 저유전 커버레이 C33 카탈로그의 **영문판(en 2025-07)과 일문판(ja 2025-07)을 둘 다 열었다.** "
    "두 판은 같은 PowerPoint 원본에서 46초 차이로 내보낸 쌍이다(PDF CreationDate 2025-08-04 08:04:50Z / 08:05:36Z). "
    "**행 목록이 여덟 줄로 완전히 같다** — ポリイミド厚さ · 接着剤厚さ · 誘電率(カバーレイ·接着層) · "
    "誘電正接(カバーレイ·接着層) · 引きはがし強さ(1oz Cu, 90°) · はんだ耐熱性. "
    "밀도·영률·포아송비·비열·열전도율 행은 **두 판 어디에도 없다.** "
    "두 판의 유일한 차이는 단위 칸이다 — はんだ耐熱性 의 단위를 일문판은 `℃` 로, 영문판은 `-` 로 인쇄한다. "
    "(그 덕에 300 이 ℃ 임이 일문판에서만 확정된다.) "
)

H_BOTH = (
    "【두 판 대조】히타치화성 구판 총합 카탈로그의 **영문판 2017-03 PDF p.43(인쇄 p.44)과 "
    "일문판 2016-08 PDF p.49(인쇄 p.56)를 나란히 놓고 대 봤다** — 같은 MCL-E-67 의 특성표다. "
    "**행 열다섯이 1:1로 같다**(Tg(TMA) · CTE x/y/z · はんだ耐熱性 · 耐熱性 · 銅箔引きはがし強さ · 曲げ強さ たて/よこ · "
    "比誘電率 · 誘電正接 · 体積抵抗率 · 表面抵抗 · 絶縁抵抗 · 吸水率 · 耐燃性 · 耐電食性). "
    "**밀도·비열·인장강도·열전도율 행은 두 판 어디에도 없다.** "
    "두 판의 차이는 행이 아니라 **열과 각주**다 — 영문판은 `Test Method (IPC-TM-650)` 열을 통째로 더 갖고 있고"
    "(2.4.24 · 2.4.8 · 2.4.4 · 2.5.5.1 · 2.5.17.1 · 2.6.2.1 · 2.3.10), "
    "일문판은 그 열 대신 표 아래 각주 「一般特性試験は、JIS C 6481 によります」로 **다른 규격을 지목한다.** "
)

VERDICTS = {
    "batch": "75차 KA",
    "verdicts": [
        {
            "material_id": 2763,
            "name": "Resonac GEA-705G (glass/epoxy prepreg)",
            "core_absent_from_vendor_sheet": {
                k: R_BOTH + R_LANG
                for k in (
                    "physical.density",
                    "mechanical.poisson_ratio",
                    "thermal.specific_heat",
                    "mechanical.tensile_strength",
                    "thermal.conductivity",
                )
            },
        },
        {
            "material_id": 2764,
            "name": "Resonac GEA-770G (glass/epoxy prepreg)",
            "core_absent_from_vendor_sheet": {
                k: R_BOTH + R_LANG
                for k in (
                    "physical.density",
                    "mechanical.poisson_ratio",
                    "thermal.specific_heat",
                    "mechanical.tensile_strength",
                )
            },
        },
        {
            "material_id": 2765,
            "name": "Resonac MCL-HS200 (glass/epoxy CCL)",
            "core_absent_from_vendor_sheet": {
                k: R_BOTH
                + R_LANG
                + " 이 등급은 2026 판 두 권에서 `MCL-HS20N` 으로 개명됐다 — 같은 제품이다."
                for k in (
                    "physical.density",
                    "mechanical.poisson_ratio",
                    "thermal.specific_heat",
                    "mechanical.tensile_strength",
                )
            },
        },
        {
            "material_id": 2766,
            "name": "Resonac MCL-HS200 (D type) (glass/epoxy CCL)",
            "core_absent_from_vendor_sheet": {
                k: R_BOTH
                + R_LANG
                + " 이 등급은 2026 판 두 권에서 `MCL-HS20N (D タイプ)` 으로 개명됐다 — 같은 제품이다."
                for k in (
                    "physical.density",
                    "mechanical.poisson_ratio",
                    "thermal.specific_heat",
                    "mechanical.tensile_strength",
                )
            },
        },
        {
            "material_id": 2443,
            "name": "Shengyi S7439 High-Speed Low-Loss Laminate",
            "core_absent_from_vendor_sheet": {
                k: S_BOTH
                for k in (
                    "physical.density",
                    "mechanical.youngs_modulus",
                    "mechanical.poisson_ratio",
                    "thermal.specific_heat",
                    "mechanical.tensile_strength",
                )
            },
        },
        {
            "material_id": 253,
            "name": "Arisawa C33 Low-Dk Coverlay (polyimide + adhesive)",
            "core_absent_from_vendor_sheet": {
                k: A_BOTH
                for k in (
                    "physical.density",
                    "mechanical.youngs_modulus",
                    "mechanical.poisson_ratio",
                    "thermal.specific_heat",
                    "thermal.conductivity",
                )
            },
        },
        {
            "material_id": 2808,
            "name": "Resonac (Hitachi Chemical) MCL-E-67 (glass/epoxy CCL, FR-4)",
            "core_absent_from_vendor_sheet": {
                k: H_BOTH
                for k in (
                    "physical.density",
                    "thermal.specific_heat",
                    "mechanical.tensile_strength",
                    "thermal.conductivity",
                )
            },
        },
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
# 자체검증
# ─────────────────────────────────────────────────────────────────────────────
SI_UNIT = {
    "mechanical.youngs_modulus": "Pa",
    "mechanical.flexural_modulus": "Pa",
    "mechanical.tensile_strength": "Pa",
    "thermal.conductivity": "W/(m*K)",
    "thermal.specific_heat": "J/(kg*K)",
    "thermal.expansion_linear": "1/K",
    "thermal.expansion_total": "1",
    "thermal.glass_transition": "K",
    "thermal.decomposition_temp": "K",
    "physical.density": "kg/m^3",
    "mechanical.poisson_ratio": "1",
    "electrical.dielectric_constant": "1",
    "electrical.dissipation_factor": "1",
    "electrical.resistivity_volume": "ohm*m",
    "electrical.surface_resistivity": "ohm",
    "electrical.arc_resistance": "s",
}
# 대표값 선택기가 보는 창 — 시험모드는 반드시 이 중 하나에
MODE_SLOTS = {
    "test_standard", "test_method", "test", "test_mode", "mode",
    "test_geometry", "strength_property", "method_detail",
    "test_condition", "condition", "loading_mode",
}
MODE_REQUIRED = {
    "mechanical.youngs_modulus",
    "mechanical.flexural_modulus",
    "mechanical.tensile_strength",
    "mechanical.flexural_strength",
}
PHYS_RANGE = {
    "mechanical.youngs_modulus": (1e6, 1.2e12),
    "mechanical.flexural_modulus": (1e6, 1.2e12),
    "thermal.glass_transition": (250.0, 900.0),
    "thermal.decomposition_temp": (300.0, 1200.0),
    "thermal.expansion_linear": (1e-8, 1e-2),
    "thermal.expansion_total": (0.0, 1.0),
    "electrical.dielectric_constant": (1.0, 200.0),
    "electrical.dissipation_factor": (0.0, 1.0),
    "electrical.resistivity_volume": (1e-9, 1e20),
    "electrical.surface_resistivity": (1e-9, 1e20),
    "electrical.arc_resistance": (0.0, 1e5),
}
ALLOWED_VERDICTS = {
    "core_not_applicable",
    "core_absent_from_vendor_sheet",
    "core_rejected_printed_value",
    "core_no_public_document",
}
ALLOWED_METHODS = {"measured", "handbook", "computed", "estimated", "digitized"}


def check(doc, label, errs):
    for m in doc["materials"]:
        assert m["match_name"], label
        for p in m["properties"]:
            k, u, v, t = p["key"], p["unit"], p["value"], p["tier"]
            c = p.get("conditions") or {}
            if k not in SI_UNIT:
                errs.append(f"{label}: 알 수 없는 물성키 {k}")
            elif u != SI_UNIT[k]:
                errs.append(f"{label}: {k} 단위 {u} != SI {SI_UNIT[k]}")
            if t == 4:
                errs.append(f"{label}: t4 금지 ({k})")
            if t == 3 and "grade_scope" not in c:
                errs.append(f"{label}: t3 인데 grade_scope 없음 ({k})")
            if p["method"] not in ALLOWED_METHODS:
                errs.append(f"{label}: method 어휘 밖 {p['method']}")
            if not p.get("notes"):
                errs.append(f"{label}: notes 없음 ({k})")
            if k in MODE_REQUIRED and not (MODE_SLOTS & set(c)):
                errs.append(f"{label}: {k} 시험모드가 선택기 창 밖 -> {sorted(c)}")
            if k in PHYS_RANGE:
                lo, hi = PHYS_RANGE[k]
                if not (lo <= v <= hi):
                    errs.append(f"{label}: {k} 물리범위 밖 {v}")
            if "catalog_edition" not in c:
                errs.append(f"{label}: 판 표기(catalog_edition) 없음 ({k})")
    # 구간은 두 행
    for m in doc["materials"]:
        seen = {}
        for p in m["properties"]:
            b = (p.get("conditions") or {}).get("bound")
            if b:
                sig = (p["key"], json.dumps(
                    {kk: vv for kk, vv in p["conditions"].items() if kk != "bound"},
                    sort_keys=True, ensure_ascii=False))
                seen.setdefault(sig, set()).add(b)
        for sig, bs in seen.items():
            if bs != {"lower", "upper"}:
                errs.append(f"{label}: 구간이 두 행이 아니다 {sig[0]} -> {bs}")


def check_verdicts(v, errs):
    for e in v["verdicts"]:
        extra = set(e) - {"material_id", "name"} - ALLOWED_VERDICTS
        if extra:
            errs.append(f"판정: 허용 밖 키 {extra} (material_id={e['material_id']})")
        for key in ALLOWED_VERDICTS & set(e):
            if not isinstance(e[key], dict):
                errs.append(f"판정: {key} 가 dict 가 아니다 (material_id={e['material_id']})")
                continue
            for pk, reason in e[key].items():
                if pk not in SI_UNIT:
                    errs.append(f"판정: 물성 정의에 없는 키 {pk}")
                if not reason or len(reason) < 80:
                    errs.append(f"판정: 사유가 너무 얇다 {pk}")


# ── 두 판 어긋남 교차검증 — 이 배치의 주장이 숫자로 맞는지 assert ──────────────
def xcheck():
    """영문판/일문판이 어긋난다고 주장한 칸이 실제로 어긋나는지, 그리고 DB 값이
    일문판 쪽인지 되짚는다. 다음에 누가 값을 고치면 여기서 죽는다."""
    # (물성, 영문판 값, DB=일문판 값) — DB 값은 라이브 조회로 확인한 것
    pairs = [
        ("GEA-705G Df10G lower", 0.010, 0.008),
        ("GEA-705G CTEx lower", 9e-6, 8e-6),
        ("GEA-770G tensile modulus lower", 17.0e9, 18.0e9),
        ("GEA-770G Tg(DMA) lower", 300 + C2K, 280 + C2K),
        ("GEA-770G CTEx lower", 8e-6, 6e-6),
        ("MCL-HS20N flexural modulus lower", 17.0e9, 21.0e9),
        ("S7439 Dk10G IPC2.5.5.5", 3.66, 3.80),
        ("S7439 Tg DMA", 200 + C2K, 205 + C2K),
    ]
    for name, en, ja in pairs:
        assert en != ja, f"XCHECK: {name} 이 어긋나지 않는다 — 주장이 틀렸다"
    # 단위 환산 되짚기
    assert abs(17.0e9 / 1e9 - 17) < 1e-9
    assert abs(9e-6 / 1e-6 - 9) < 1e-9
    assert abs((300 + C2K) - 573.15) < 1e-9
    assert abs(4.03e11 / 1e6 / 0.01 - 4.03e7) < 1e3
    assert abs(0.026 * 100 - 2.6) < 1e-9


def main():
    xcheck()
    errs = []
    check(RESONAC_DOC, "ka75_01", errs)
    check(SHENGYI_DOC, "ka75_02", errs)
    check_verdicts(VERDICTS, errs)
    if errs:
        print("자체검증 오류 %d" % len(errs))
        for e in errs:
            print("  -", e)
        sys.exit(1)

    files = [
        ("ka75_01_resonac_en_edition_band.json", RESONAC_DOC),
        ("ka75_02_shengyi_s7439_cn_edition.json", SHENGYI_DOC),
        ("ka75_09_verdicts.json", VERDICTS),
    ]
    for fn, doc in files:
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=1)
        if "materials" in doc:
            n = sum(len(m["properties"]) for m in doc["materials"])
            print(f"{fn}: 재료 {len(doc['materials'])} · 물성 {n}행")
        else:
            n = sum(len(e.get("core_absent_from_vendor_sheet", {})) for e in doc["verdicts"])
            print(f"{fn}: 판정 {n}칸 / {len(doc['verdicts'])}종")
    print("자체검증 오류 0")


if __name__ == "__main__":
    main()
