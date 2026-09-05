# 64차 ZB 적재 JSON 생성기 — 니켈실버(C7521·C7701)와 형제 스프링 합금(C5210·C1990)
# 표 데이터를 손으로 옮기다 생기는 오식을 막으려고 원문 표를 그대로 파이썬 리터럴로 두고 JSON 을 찍는다.
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))
KSI = 6.894757e6          # 1 ksi -> Pa
BTU_FT_HR_F = 1.730735    # 1 Btu/(sq ft * ft * hr * degF) -> W/(m*K)
BTU_LB_F = 4186.8         # 1 Btu/(lb*degF) -> J/(kg*K)
IACS = 5.8e5              # 1 %IACS -> S/m (재료 179 베릴륨동 행이 쓰는 환산계수와 같다)

# ── 출처 ────────────────────────────────────────────────────────────────────
S_KIYO = {
    "kind": "datasheet",
    "title": "清峰金属工業 洋白(Nickel Silver) 製品ページ — 洋白 成分・特性一覧(化学成分・物理的性質・機械的性質)",
    "url": "https://www.kiyomine.co.jp/product/nickel/",
    "publisher": "清峰金属工業株式会社 (Kiyomine Metal Industry Co., Ltd.)",
    "year": 2026,
}
S_TOKKIN_7701 = {
    "kind": "datasheet",
    "title": "特殊金属エクセル(TOKKIN) 製品ページ C7701 ばね用洋白 — 規格・化学成分・物理的性質",
    "url": "https://www.tokkin.co.jp/search/non-ferrous/copper-alloys/c7701/",
    "publisher": "株式会社特殊金属エクセル (Tokushu Kinzoku Excel Co., Ltd.)",
    "year": 2026,
}
S_TOKKIN_5210 = {
    "kind": "datasheet",
    "title": "特殊金属エクセル(TOKKIN) 製品ページ C5210 ばね用りん青銅 — 規格・化学成分・物理的性質",
    "url": "https://www.tokkin.co.jp/search/non-ferrous/copper-alloys/c5210/",
    "publisher": "株式会社特殊金属エクセル (Tokushu Kinzoku Excel Co., Ltd.)",
    "year": 2026,
}
S_DOWA = {
    "kind": "datasheet",
    "title": "DOWAメタルテック YCuT-M(チタン銅) 製品ページ — 標準組成・物理的性質・機械的性質(関連規格 CDA C19900、JIS C1990相当)",
    "url": "https://www.dowa-metaltech.co.jp/products/ycut-m/",
    "publisher": "DOWAメタルテック株式会社 (DOWA Metaltech Co., Ltd.)",
    "year": 2026,
}


def S_JCBA(fid, title):
    return {"kind": "database",
            "title": ("一般社団法人日本伸銅協会 伸銅品板条材料特性データベース — " + title
                      + " (試験方法 2.4 は method/bjm001.pdf·bjm002.pdf)"),
            "url": "https://www.copper-brass.gr.jp/data/file/banjou/result/%s.pdf" % fid,
            "publisher": "一般社団法人日本伸銅協会 (Japan Copper and Brass Association, JCBA)"}


S_JCBA_7701 = S_JCBA("bjr001007", "表1.2 機械的性質 C7701(ばね用洋白) 一覧表")
S_JCBA_5210 = S_JCBA("bjr001005", "表1.2 機械的性質 C5210(ばね用りん青銅) 一覧表")
S_JCBA_1990 = S_JCBA("bjr001006", "表1.2 機械的性質 C1720·C1990 一覧表")
S_JCBA_FAT = S_JCBA("bjr002001", "表2.2 疲労試験結果(破断応力) 一覧")


def S_CDA(uns, name):
    return {"kind": "database",
            "title": "Copper Development Association — Alloy %s (%s) Standards & Properties" % (uns, name),
            "url": "https://alloys.copper.org/alloy/%s" % uns,
            "publisher": "Copper Development Association Inc. (CDA)",
            "year": 2026}


S_CDA_75200 = S_CDA("C75200", "Nickel Silver, 65-18")
S_CDA_77000 = S_CDA("C77000", "Nickel Silver, 55-18")
S_CDA_52100 = S_CDA("C52100", "Phosphor Bronze, 8% C")

# ── JCBA 표 1.2 실측(平均値). 열 배정은 pdftotext -bbox-layout x좌표로 확정했다(브리프 606·671).
#    (조질, 두께mm, HV, 結晶粒度mm, {방향: (引張強さ, 耐力, 伸び%, n値, 縦弾性係数kN/mm2, ばね限界値, たわみ係数)})
DIRS = [("L.D.", "MD (rolling direction)", "L.D. (圧延方向に平行)"),
        ("45", "45 deg to rolling direction", "45° (圧延方向に45度)"),
        ("T.D.", "TD (transverse to rolling)", "T.D. (圧延方向に直角)")]

JCBA = {
    "C7701": [
        ("1/2H", 0.30, 159, 0.015, {"L.D.": (566, 330, 30.2, 0.28, 131, 338, 103),
                                    "45":   (537, 309, 35.2, 0.28, 123, 345, 103),
                                    "T.D.": (545, 320, 34.6, 0.28, 145, 362, 110)}),
        ("H",    0.30, 210, 0.015, {"L.D.": (685, 546, 12.5, 0.13, 136, 570, 111),
                                    "45":   (641, 492, 16.1, 0.13, 128, 550, 105),
                                    "T.D.": (662, 496, 14.3, 0.13, 142, 576, 116)}),
        ("EH",   0.30, 242, 0.010, {"L.D.": (770, 668,  6.7, 0.09, 142, 676, 112),
                                    "45":   (705, 580,  9.7, 0.11, 120, 643, 102),
                                    "T.D.": (733, 574,  8.5, 0.12, 146, 643, 115)}),
    ],
    "C5210": [
        ("1/2H", 0.30, 169, 0.005, {"L.D.": (516, 347, 48.0, 0.21, 119, 367, 96),
                                    "45":   (500, 380, 48.2, 0.19, 103, 379, 88),
                                    "T.D.": (497, 394, 47.8, 0.19, 109, 443, 95)}),
        ("H",    0.30, 216, 0.010, {"L.D.": (643, 531, 29.1, 0.11, 103, 471, 90),
                                    "45":   (647, 545, 22.9, 0.07, 104, 503, 85),
                                    "T.D.": (662, 547, 24.7, 0.08, 104, 583, 94)}),
        ("EH",   0.30, 242, 0.005, {"L.D.": (719, 633, 18.3, 0.07, 110, 552, 89),
                                    "45":   (759, 676, 16.9, 0.08, 116, 618, 88),
                                    "T.D.": (737, 654, 15.9, 0.07, 110, 686, 98)}),
    ],
    "C1990": [
        ("1/4HM", 0.30, 312, 0.020, {"L.D.": (897, 692, 21.2, 0.09, 135, 734, 102),
                                     "45":   (876, 656, 22.7, 0.12, 127, 760, 100),
                                     "T.D.": (855, 665, 24.7, 0.13, 133, 769, 106)}),
        ("EHM",   0.30, 350, 0.020, {"L.D.": (1012, 868, 11.1, 0.05, 126,  850, 103),
                                     "45":   (1020, 838, 12.9, 0.07, 132,  926, 105),
                                     "T.D.": (1038, 829, 15.2, 0.06, 138, 1074, 118)}),
    ],
}

JCBA_METHOD = ("JCBA 시험조건(bjm001.pdf 2.4.1) — 引張試験 JIS Z 2241/Z 2201 준거, 100 kN 유압만능시험기, "
               "JIS 5호 시험편, 인장속도 25 mm/min, 신율 계측은 차동트랜스식 신율계(크로스헤드 변위가 아니다), "
               "耐力은 0.2% 오프셋. 硬さ JIS Z 2244 HV0.3(시험하중 2.942 N). 시험편은 L.D./45°/T.D. 각 n=3 이고 "
               "표가 3본의 평균(平均値)을 인쇄한다 — 우리가 만든 평균이 아니다.")

JCBA_COLS = ("열 배정은 `pdftotext -bbox-layout` x좌표로 확정했다(브리프 606·671) — "
             "引張強さ 195-226 · 耐力 240-266 · 伸び 272-293 · 硬さHV 299-320 · 結晶粒度 331-349 · "
             "n値 362-378 · ばね限界値 389-421 · 縦弾性係数 430-461 · たわみ係数 472-503. "
             "`-layout` 텍스트만 보면 방향별로 한 번만 찍히는 縦弾性係数와 시편마다 찍히는 たわみ係数가 섞인다.")


def jcba_rows(alloy, src, e_note, extra_note=""):
    rows = []
    for temper, thk, hv, grain, byd in JCBA[alloy]:
        for tag, dnorm, dverb in DIRS:
            uts, ys, el, n, e, kb, dc = byd[tag]
            base = {"temper": temper, "direction": dnorm, "direction_verbatim": dverb,
                    "thickness_mm": thk, "statistic": "3본 평균(平均値)",
                    "grain_size_mm": grain, "test_standard": "JIS Z 2241 / JIS Z 2201 (JIS 5号)",
                    "temperature_c": "미인쇄(실온 시험)"}
            common = ("%s %s 材 %s 방향, 원문 표 1.2 의 平均値 행. 같은 행이 함께 인쇄하는 값 — "
                      "引張強さ %s · 耐力 %s · 伸び %s%% · HV %s · 結晶粒度 %s mm · n値 %s · "
                      "ばね限界値 %s N/mm2 · 縦弾性係数 %s kN/mm2 · たわみ係数 %s kN/mm2. %s %s %s"
                      % (alloy, temper, tag, uts, ys, el, hv, grain, n, kb, e, dc,
                         JCBA_COLS, JCBA_METHOD, extra_note))
            rows.append({"key": "mechanical.tensile_strength", "value": uts * 1e6, "unit": "Pa",
                         "method": "measured", "tier": 1,
                         "conditions": dict(base, printed_as="%s N/mm2" % uts),
                         "notes": common, "value_check": "%s N/mm2 = %s Pa" % (uts, uts * 1e6)})
            rows.append({"key": "mechanical.yield_strength", "value": ys * 1e6, "unit": "Pa",
                         "method": "measured", "tier": 1,
                         "conditions": dict(base, printed_as="%s N/mm2" % ys, offset_pct=0.2),
                         "notes": common, "value_check": "%s N/mm2 = %s Pa" % (ys, ys * 1e6)})
            rows.append({"key": "mechanical.elongation_at_break", "value": round(el / 100.0, 4), "unit": "1",
                         "method": "measured", "tier": 1,
                         "conditions": dict(base, printed_as="%s %%" % el,
                                            gauge_length="JIS 5号 시험편(표점거리 50 mm)"),
                         "notes": common, "value_check": "%s %% = %s" % (el, round(el / 100.0, 4))})
            rows.append({"key": "mechanical.youngs_modulus", "value": e * 1e9, "unit": "Pa",
                         "method": "measured", "tier": 1,
                         "conditions": dict(base, printed_as="縦弾性係数 %s kN/mm2" % e,
                                            modulus_type="인장 縦弾性係数(방향별 1개 값, 시편별 아님)",
                                            statistic="방향별 단일 인쇄값"),
                         "notes": common + " " + e_note,
                         "value_check": "%s kN/mm2 = %s GPa = %s Pa" % (e, e, e * 1e9)})
            rows.append({"key": "mechanical.monotonic_strain_hardening_exponent", "value": n, "unit": "1",
                         "method": "measured", "tier": 1,
                         "conditions": dict(base, printed_as="n値 %s" % n,
                                            statistic="방향별 단일 인쇄값"),
                         "notes": common})
        rows.append({"key": "mechanical.hardness_vickers", "value": float(hv), "unit": "HV",
                     "method": "measured", "tier": 1,
                     "conditions": {"temper": temper, "thickness_mm": thk,
                                    "direction": "미인쇄(조질 단위로 한 값만 인쇄된다)",
                                    "test_standard": "JIS Z 2244, HV0.3, 시험하중 2.942 N",
                                    "grain_size_mm": grain, "printed_as": "%s HV(0.5)" % hv},
                     "notes": ("%s %s 材, 원문 표 1.2 의 硬さ 열. 이 값은 방향별로 나뉘지 않고 "
                               "조질·두께 단위로 한 번만 인쇄된다(세 방향 블록의 세로 중앙에 놓여 있다). %s %s"
                               % (alloy, temper, JCBA_COLS, JCBA_METHOD))})
    return {"source": src, "properties": rows}


# ── 재료 정의 ────────────────────────────────────────────────────────────────
NAME_7521 = "C7521 Nickel Silver (JIS H 3110 / UNS C75200 / CuNi18Zn20)"
NAME_7701 = "C7701 Spring Nickel Silver (JIS H 3130 / UNS C77000 / CuNi18Zn27)"
NAME_5210 = "C5210 Spring Phosphor Bronze (JIS H 3130 / UNS C52100 / CuSn8)"
NAME_1990 = "C1990 Spring Titanium Copper (JIS H 3130 / UNS C19900)"

XREF_NOTE = ("등급 대응은 우리가 지은 것이 아니라 **벤더가 자기 시트에 인쇄**한다(브리프 632·663) — "
             "TOKKIN 제품페이지의 `規格` 블록이 `JIS C7701 (H3130)` 과 `UNS/CDA C77000` 과 `主要成分 CuNi18Zn27` 을 "
             "한 표에 나란히 찍고, 清峰金属工業의 `洋白 成分・特性一覧` 은 `合金名 CDA No. C77000 / JIS No. C7701` "
             "행을 찍는다. C7521 은 같은 두 문서가 `C75200 / C7521 / CuNi18Zn20` 로 찍는다.")

GRADE_WARN = ("주의 — EN 기호 `CuNi18Zn20` 은 두 UNS 를 가리킨다. Weber+Calibra 의 CuNi18Zn20 시트는 "
              "UNS 를 `C76400` 으로 적고 Cu 를 60.0~63.0% 로 찍는데 JIS C7521 은 Cu 62.0~66.0% 라 다른 합금이다. "
              "그 시트는 쓰지 않았다(브리프 621·586).")

mat_7521 = {"name": NAME_7521, "category": "metal", "attributes": {
    "source": "agent-batch-64-ZB", "role": "product", "subsystem": "pcb",
    "role_reason": ("JIS H 3110 이 규정하는 상용 압연 洋白 등급이다. 清峰金属工業·特殊金属エクセル·"
                    "安芸メタル工業·岩崎商店이 板/条 로 판다. 이름에 조성비·시료라벨이 없다(브리프 115)."),
    "role_confidence": "high",
    "subsystem_basis": ("커넥터·스위치·シールドケース·水晶発振子ケース 용 압연 동합금 조/판이다. "
                        "카탈로그의 형제 동합금(37 C26000 · 38 C36000 · 39 C51000 · 179 Beryllium Copper)이 "
                        "전부 `pcb` 라 그 계보를 따랐다(브리프 612)."),
    "material_class": "Cu-Ni-Zn 洋白(nickel silver) 압연 판·조",
    "composition_note": ("JIS H 3110 표2 verbatim — Cu 62.0~66.0 · Ni(Co 포함) 16.5~19.5 · Mn 0~0.50 · "
                         "Fe 0.25 이하 · Pb 0.10 이하 · Zn 残部. " + XREF_NOTE + " " + GRADE_WARN),
    "manufacturer": "清峰金属工業 · 特殊金属エクセル 외 일본 신동업체(단일 벤더 제품이 아니라 규격 등급이다)",
    "core_absent_from_vendor_sheet": {
        "mechanical.yield_strength": (
            "洋白(C7351·C7451·C7521·C7541)에는 **0.2% 耐力 규정 자체가 없다.** JIS H 3110 표3 의 열은 "
            "`引張試験(引張強さ·伸び)` · `曲げ試験` · `硬さ試験(HV)` 셋뿐이고 耐力 열이 아예 없으며, "
            "清峰金属工業 一覧表의 `耐力 [N/mm2] 0.2% Offset` 행도 **C7701 열만 차 있고 C7521·C7541·C7451 은 "
            "전 조질이 `-` 다**(같은 표 안에서 형제 등급이 갈린다 — 브리프 613). "
            "즉 벤더가 안 찍는 것이 아니라 이 등급군에 그 보증항목이 없다. "
            "닫으려면 실측 문서가 필요하다 — JCBA 材料特性DB 는 洋白 중 C7701 만 시험했고 C7521 은 목록에 없다"
            "(합금 선택 목록 전수 확인: C1020·C1720·C1990·C2600·C2801·C5191·C5210·C7701 여덟뿐).")},
    "core_fill_sheet": ("64차 ZB — 연 문서: 清峰金属工業 제품페이지 · TOKKIN C7521 페이지(물리적성질 블록이 "
                        "**없다**. 형제 C7701·C5210 페이지에는 있다 — 브리프 613 의 형제 갈림) · "
                        "CDA copper.org C75200 · JIS H 3110 기계적성질 표(長井技研 資料館 転載판, "
                        "kikakurui.com 의 2018년판 목차) · 安芸メタル·岩崎商店·滑川(비중만). "
                        "**안 연 문:** JIS H 3110 정본 PDF · 三菱伸銅 · JX金属 · 古河電工 · Wieland N17."),
}}

mat_7701 = {"name": NAME_7701, "category": "metal", "attributes": {
    "source": "agent-batch-64-ZB", "role": "product", "subsystem": "pcb",
    "role_reason": ("JIS H 3130 이 규정하는 상용 ばね用洋白 등급이다. 低温焼なまし 처리된 고성능 스프링재로 "
                    "전자·통신·계측기기용 스위치·커넥터·릴레이에 쓴다(JIS H 0500 용어 1404 verbatim). "
                    "特殊金属エクセル·清峰金属工業이 조·판으로 판다(브리프 115)."),
    "role_confidence": "high",
    "subsystem_basis": "커넥터·스프링 콘택트용 압연 동합금 조. 형제 동합금 37·38·39·179 의 `pcb` 계보를 따랐다.",
    "material_class": "Cu-Ni-Zn ばね用洋白(spring nickel silver) 압연 판·조, 低温焼なまし",
    "composition_note": ("JIS 표 verbatim — Cu 54.0~58.0 · Ni(Co 포함) 16.5~19.5 · Mn 0.50 이하 · "
                         "Fe 0.25 이하 · Pb 0.03 이하 · Zn 残部. " + XREF_NOTE),
    "manufacturer": "特殊金属エクセル · 清峰金属工業 외 일본 신동업체(규격 등급이다)",
    "why_this_grade": ("64차 ZB 는 사용자가 스프링 콘택트 재료를 못 찾아 베릴륨동으로 근사했다는 실사용 신고에서 나왔다. "
                       "니켈실버는 베릴륨동과 E(125~127 대 131 GPa) 는 가깝지만 **전기전도도가 5.5 대 22 %IACS 로 네 배 차이**나고 "
                       "인장·항복 대역이 통째로 다르다. 근사가 성립하지 않는다."),
    "core_fill_sheet": ("64차 ZB — 응력완화(応力緩和特性)는 JCBA 가 C7701-H 材에 대해 85/120/150 ℃ 3장을 공개하지만 "
                        "`result/bjr004010.pdf` 가 **전부 그림(応力緩和率 대 試験時間)** 이라 디지타이즈가 필요하다. "
                        "이 배치는 안 했다 — 다음 파동의 표적이다(브리프 648). "
                        "剪断抵抗(bjr005001·005002·005003)·曲げ加工性(bjr003009·003010)도 같은 DB 에 있다."),
}}

mat_5210 = {"name": NAME_5210, "category": "metal", "attributes": {
    "source": "agent-batch-64-ZB", "role": "product", "subsystem": "pcb",
    "role_reason": ("JIS H 3130 이 규정하는 상용 ばね用りん青銅 등급이다(JIS H 0500 용어 1403 — "
                    "`ばね限界値가 규정되어 있는 Sn 7.0~9.0% 인청동`). TOKKIN 이 `JIS C5210 (H3130) / UNS C52100 / "
                    "CuSn8` 로 판다."),
    "role_confidence": "high",
    "subsystem_basis": "커넥터·스위치·릴레이용 스프링 조. 형제 동합금 39 C51000 의 `pcb` 계보를 따랐다.",
    "material_class": "Cu-8Sn-P ばね用りん青銅(spring phosphor bronze) 압연 판·조, 低温焼なまし",
    "why_this_grade": ("브리프가 명시한 확장 표적이고, **JCBA 표 1.2 가 C7701 과 같은 표에 찍는다**"
                       "(브리프 602·649 — 표를 열었으면 지금 표적이 아닌 행도 그 자리에서 다 읽어라). "
                       "카탈로그에는 일반 인청동 39 `C51000_Phosphor_Bronze` 만 있고 **스프링 등급 C5210 이 없다** — "
                       "커넥터 스프링에 쓰는 것은 C51000 이 아니라 C5210 이다(Sn 5% 대 8% · 低温焼なまし 유무 · "
                       "ばね限界値 규정 유무로 갈린다)."),
    "verdict_vendor_divergence": (
        "**TOKKIN(t1 벤더 시트)과 CDA C52100(t2 공인DB)이 세 칸에서 갈린다.** "
        "열전도율 79.5 대 62.31 W/(m·K)(28%) · 전기저항 9.6 µΩ·cm(=17.96 %IACS) 대 13 %IACS(38%) · "
        "영률 98 대 110.3 GPa(12%). Wiedemann-Franz(L=2.44e-8, T=293 K)로 두 짝을 각각 재면 "
        "TOKKIN 74.5 대 인쇄 79.5(6% 안) · CDA 53.9 대 인쇄 62.3(13% 안) 으로 **둘 다 자기정합**이다 — "
        "한 열이 죽은 것이 아니라 두 문서가 서로 다른 Sn 함량대의 청동을 찍고 있다(브리프 642). "
        "영률은 **우리 DB 가 심판이다**(브리프 642 62차 XA) — 같은 JCBA 표의 C5210 실측 縦弾性係数가 "
        "103~119 kN/mm2 라 CDA 110.3 을 감싸고 TOKKIN 98 은 그 아래다. "
        "**갈리는 세 칸은 CDA 만 적재하고 TOKKIN 인쇄값은 지우지 않고 여기와 각 행 notes 에 verbatim 으로 남겼다**(브리프 565). "
        "일치하는 칸(밀도 8.86 대 8.8 · 비열 377 대 376.8 · CTE 17.8 대 18.18e-6/K · 융점)은 TOKKIN(t1)으로 적재했다. "
        "닫으려면 JIS H 3130 정본이나 三菱伸銅·JX金属의 C5210 시트 한 장이 필요하다."),
    "core_absent_from_vendor_sheet": {
        "mechanical.poisson_ratio": (
            "TOKKIN C5210 제품페이지 `物理的性質` 블록(밀도·비열·전기저항·탄성계수·열팽창계수·열전도율·융점·자성 "
            "여덟 행)에 ポアソン比 행이 없고, CDA copper.org C52100 `Physical Properties` 블록에도 없다. "
            "**둘 다 E 와 G 는 찍는다**(CDA 16000 ksi / 6000 ksi) — `nu = E/(2G)-1 = 0.333` 이 나오지만 "
            "우리가 만들면 브리프 43 위반이라 **만들지 않았다**. "
            "닫으려면 ν 를 인쇄하는 문서 한 장이 필요하다 — 같은 벤더군에서 清峰金属工業은 洋白에 대해 ポアソン比를 "
            "찍고 DOWAメタルテック은 チタン銅에 대해 찍으므로 인청동 시트에도 존재할 수 있다(브리프 628 — 서식마다 담는 행이 다르다).")},
}}

mat_1990 = {"name": NAME_1990, "category": "metal", "attributes": {
    "source": "agent-batch-64-ZB", "role": "product", "subsystem": "pcb",
    "role_reason": ("JIS H 3130 이 규정하는 상용 ばね用チタン銅 등급이다(Cu-Ti 2.9~3.5%). "
                    "DOWAメタルテック이 `YCuT-M`(관련규격 `CDA C19900、JIS C1990相当(1/4H、EH材)`)으로 팔고 "
                    "JX金属도 고강도·고도전 チタン銅 라인을 낸다."),
    "role_confidence": "high",
    "subsystem_basis": "스위치·커넥터·잭·릴레이용 스프링 조. 형제 동합금의 `pcb` 계보를 따랐다.",
    "material_class": "Cu-3.2Ti ばね用チタン銅(spring titanium copper), ミルハーデン(mill-hardened) 조질",
    "why_this_grade": ("브리프가 명시한 확장 표적이고 **JCBA 표 1.2(bjr001006)가 C1720 베릴륨동과 같은 표에 찍는다** — "
                       "표를 이미 열었다(브리프 602·649). 스마트폰 커넥터에서 **베릴륨동의 무Be 대체재**로 쓰이고 "
                       "응력완화 저항이 베릴륨동급이라, 사용자가 지적한 `베릴륨동 근사` 문제의 반대편 후보다."),
    "core_fill_sheet": (
        "**비열을 못 채웠다.** 연 문서 셋을 이름으로 적는다(브리프 627③·676) — "
        "① DOWAメタルテック YCuT-M 제품페이지의 物理的性質 표는 융점·밀도·熱膨張係数·熱伝導度·導電率·縦弾性係数·"
        "ポアソン比·磁気的特性 여덟 행이고 **比熱 행이 없다**. "
        "② CDA copper.org C19900 은 `Physical Properties: No physical properties for this alloy` 로 블록 자체가 비었다"
        "(조성 Cu-Ti 2.9~3.5 만 있다). "
        "③ TOKKIN 에는 C1990 제품페이지가 **없다**(`/search/non-ferrous/copper-alloys/c1990/` 404). "
        "**안 연 문:** JX金属(nmmjx-dc.com 고강도·고도전 チタン銅) · 古河電工 · 三菱伸銅 · JIS H 3130 정본. "
        "브리프 675 의 비대칭(k 는 찍고 Cp 는 안 찍는다)이 이 갈래에서도 그대로 나왔다."),
    "grade_identity_note": (
        "DOWA 는 자기 제품을 `YCuT-M` 이라 부르고 **`JIS C1990相当`(相当=equivalent)** 이라고 적는다 — "
        "동일 선언이 아니다. 그래서 그 시트에서 온 물리물성은 **t3** 로 넣고 그 문장을 각 행 `grade_scope` 에 박았다"
        "(브리프 632). 조질 표기도 갈린다 — DOWA 는 1/4H·1/2H·H·EH·SH, JCBA 는 1/4HM·EHM(ミルハーデン)이다. "
        "**섞지 않았다**(브리프 586). DOWA 의 조질별 引張強さ·耐力·伸び·HV 표는 그래서 안 옮겼다."),
}}


# ── 벤더·공인DB 물성 행 ───────────────────────────────────────────────────────
# 브리프 633 — 원문이 축을 안 찍었다는 사실 자체가 조건이다. 빈 키는 조사 잔여로 읽히고
# `미인쇄` 는 판정으로 읽힌다. 밀도·비열·열전도율·CTE·융점·도전율은 벤더가 조질을 갈라
# 찍지 않는 물성이라 그 사실을 조건으로 박는다.
NO_TEMPER = "미인쇄(벤더가 조질을 갈라 찍지 않는다 — 이 물성은 조질에 둔감하다)"
NO_DIR = "미인쇄(벤더가 방향을 갈라 찍지 않는다)"

_PHYS_KEYS = {"physical.density", "thermal.specific_heat", "thermal.melting_point",
              "electrical.conductivity", "electrical.resistivity_volume",
              "thermal.conductivity", "thermal.expansion_linear"}


def stamp_axes(doc):
    """물리물성 행에 temper/direction 미인쇄 진술을 채운다(값·단위·등급·출처는 안 건드린다)."""
    for pr in doc["properties"]:
        if pr["key"] in _PHYS_KEYS:
            pr["conditions"].setdefault("temper", NO_TEMPER)
            pr["conditions"].setdefault("direction", NO_DIR)
    return doc

E_NOTE_7701 = (
    "브리프 604 검산 — Cu-Ni-Zn 의 E 통용대역은 110~130 GPa 인데 이 표의 T.D. 값이 142~146 kN/mm2 로 "
    "대역 상단을 12% 넘는다. **기각하지 않은 근거 셋** — ① 같은 재료의 벤더 등방값이 전부 대역 안이다"
    "(清峰 125 · TOKKIN 127 · CDA C77000 18000 ksi = 124.1 GPa). ② **이방성 패턴이 세 조질에서 똑같다** "
    "(T.D. > L.D. > 45°: 145>131>123 · 142>136>128 · 146>142>120) — 추출 손상이면 이 계통성이 안 나온다"
    "(브리프 642 — 형제 행이 같은 편차를 재현하면 오식이 아니라 조직·측정법이다). 압연 집합조직을 가진 "
    "FCC 판재에서 E_TD > E_RD 는 알려진 거동이다. ③ 측정법이 크로스헤드 변위가 아니라 차동트랜스식 "
    "신율계라 브리프 604 의 컴플라이언스 편향(E 를 **낮춘다**)과 방향이 반대다. "
    "**등방값으로 쓰면 안 되는 값이라 `direction` 을 조건에 박았다.**")

E_NOTE_5210 = (
    "브리프 604 검산 — 인청동(Cu-8Sn)의 E 통용대역은 105~115 GPa 이고 이 표의 방향별 값 103~119 가 "
    "그 대역을 감싼다. 그리고 **이 값이 심판 노릇도 한다**(브리프 642 62차 XA — 인쇄값을 가르는 자가 "
    "우리 DB 안에 있다) — TOKKIN C5210 시트의 弾性係数 98 GPa 는 이 대역 아래이고 "
    "CDA C52100 의 16000 ksi = 110.3 GPa 는 안이다.")

E_NOTE_1990 = (
    "브리프 604 검산 — Cu-3Ti 티탄동의 E 통용대역은 115~130 GPa 이고 이 표의 방향별 값이 126~138 kN/mm2 다. "
    "DOWAメタルテック YCuT-M 시트의 縦弾性係数 117 kN/mm2(EH材)가 대역 하단이라 방향평균과 정합한다. "
    "조질이 ミルハーデン(석출경화 완료 후 출하)이라 냉간압연 집합조직이 남아 있고, C7701·C5210 과 같은 "
    "방향 의존이 나온다.")

XCHK_7701 = (
    "다중출처 검산 — 이 재료의 물리물성은 서로 독립인 문서 셋이 만난다. "
    "밀도 TOKKIN 8.70 · 清峰 8.7 · CDA C77000 비중 8.7 · 滑川(유통) 8.70 g/cm3. "
    "열전도율 TOKKIN 29 W/(m·K)@25℃ · 清峰 29@20℃ · CDA 17 Btu/(sq ft·ft·hr·°F) = 29.42. "
    "선팽창 TOKKIN 16.7e-6/K · 清峰 16.7e-6/K(20~300℃) · CDA 9.3e-6/°F(68~572°F) = 16.74e-6/K. "
    "비열 TOKKIN 377 J/(kg·K) · CDA 0.09 Btu/(lb·°F) = 376.8. "
    "도전율 清峰 5.5 %IACS · CDA 5.5 %IACS · TOKKIN 전기저항 30 µΩ·cm(=1.7241/30 = 5.75 %IACS). "
    "영률 清峰 125 · TOKKIN 127 · CDA 18000 ksi = 124.1 GPa.")

SPEC_BASIS = ("규격·벤더 보증 밴드의 **인쇄된 하한**이다. 구간 중앙값은 만들지 않았다(브리프 451·616). "
              "카탈로그 선례를 따랐다 — 재료 179 베릴륨동의 인장강도가 `원문: 1140-1380 MPa (범위 하한 기록)` 로 "
              "이미 그렇게 서 있다(브리프 612 — 이미 있는 계보를 따른다).")

# 清峰 洋白 一覧表(機械的性質) — (조질, 引張強さ밴드, 伸び하한%, HV밴드)  · None 은 원문이 `-` 인 칸
KIYO_MECH = {
    "C7521": [("O",    (375, None), 20, None),
              ("1/2H", (440, 570),   5, (120, 180)),
              ("H",    (540, 640),   3, (150, 210)),
              ("EH",   (610, None), None, (185, None))],
    "C7701": [("1/2H", (540, 655),   8, (150, 210)),
              ("H",    (630, 735),   4, (180, 240)),
              ("EH",   (705, 805), None, (210, 260)),
              ("SH",   (765, 865), None, (230, 270))],
}
# 清峰 一覧表(耐力 0.2% Offset) — C7701 만 차 있다
KIYO_YS = {"C7701": [("1/2H", 390), ("H", 500), ("EH", 600), ("SH", 680)]}


def band_txt(b):
    lo, hi = b
    return ("%s-%s N/mm2" % (lo, hi)) if hi else ("%s N/mm2 이상" % lo)


def spec_rows(alloy, extra=""):
    rows = []
    for temper, band, el, hv in KIYO_MECH[alloy]:
        base = {"temper": temper, "basis": "규격·벤더 보증치(실측 아님)",
                "direction": "미인쇄(規格値는 방향을 갈라 찍지 않는다)",
                "thickness_mm": "0.15~5 (JIS H 3110 표3 적용 두께)" if alloy == "C7521" else "미인쇄"}
        rows.append({"key": "mechanical.tensile_strength", "value": band[0] * 1e6, "unit": "Pa",
                     "method": "handbook", "tier": 2,
                     "conditions": dict(base, printed_range=band_txt(band),
                                        printed_as="引張強さ %s" % band_txt(band)),
                     "notes": ("清峰金属工業 `洋白 成分・特性一覧 > 機械的性質` 표의 %s %s 행. %s %s"
                               % (alloy, temper, SPEC_BASIS, extra)),
                     "value_check": "%s N/mm2 = %s Pa" % (band[0], band[0] * 1e6)})
        if el is not None:
            rows.append({"key": "mechanical.elongation_at_break", "value": round(el / 100.0, 4), "unit": "1",
                         "method": "handbook", "tier": 2,
                         "conditions": dict(base, printed_as="伸び %s%% 이상" % el,
                                            gauge_length="미인쇄(JIS H 3110 은 JIS 5号 시험편을 지정한다)"),
                         "notes": ("清峰金属工業 一覧表 `伸び[%%]Elongation` 행의 %s %s 칸(원문 `%s-`, "
                                   "즉 %s%% 이상). %s %s" % (alloy, temper, el, el, SPEC_BASIS, extra))})
        if hv is not None:
            rows.append({"key": "mechanical.hardness_vickers", "value": float(hv[0]), "unit": "HV",
                         "method": "handbook", "tier": 2,
                         "conditions": dict(base, printed_range=("%s-%s HV" % hv) if hv[1] else ("%s HV 이상" % hv[0]),
                                            printed_as="ビッカース硬さ %s" % (("%s-%s" % hv) if hv[1] else ("%s-" % hv[0]))),
                         "notes": ("清峰金属工業 一覧表 `ビッカース硬さ[HV]` 행의 %s %s 칸. %s %s"
                                   % (alloy, temper, SPEC_BASIS, extra))})
    for temper, ys in KIYO_YS.get(alloy, []):
        rows.append({"key": "mechanical.yield_strength", "value": ys * 1e6, "unit": "Pa",
                     "method": "handbook", "tier": 2,
                     "conditions": {"temper": temper, "offset_pct": 0.2, "basis": "규격·벤더 보증 하한(실측 아님)",
                                    "direction": "미인쇄", "printed_range": "%s N/mm2 이상" % ys,
                                    "printed_as": "耐力 %s-" % ys},
                     "notes": ("清峰金属工業 一覧表 `耐力[N/mm2] 0.2%% Offset Yield Strength` 행의 C7701 %s 칸. "
                               "%s **주의 — 같은 재료의 JCBA 실측과 1/2H 에서 어긋난다**: JCBA 실측 L.D. 330 · "
                               "45° 309 · T.D. 320 N/mm2 로 이 보증 하한 390 을 밑돈다(H 는 546 대 500 ✔, "
                               "EH 는 668 대 600 ✔ 로 통과한다). 耐力/引張 비가 1/2H 만 0.58 이고 H·EH 는 "
                               "0.80·0.87 이라 **JCBA 1/2H 시험재가 低温焼なまし 상태가 아닐 가능성**이 지문으로 보이는데 "
                               "원문이 그것을 밝히지 않는다. 어느 쪽도 버리지 않았다 — 조건축(`basis`)이 다르다"
                               "(브리프 615·662). 닫으려면 JIS H 3130 정본의 C7701 1/2H 耐力 규정을 확인해야 한다."
                               % (temper, SPEC_BASIS))})
    return rows


# ── 문서별 항목 조립 ─────────────────────────────────────────────────────────
KIYO_TABLE = ("清峰金属工業 `洋白 成分・特性一覧 > 物理的性質` 표 verbatim(열은 C7701·C7521·C7541·C7451·"
              "HCR-C7701·HCR-C7521) — 융점 1055/1060/1075/1020 ℃ · ポアソン比 0.32/0.32/0.32/0.34 · "
              "比重 8.7/8.73/8.68/8.61 · 導電率 5.5/6/7/9 %IACS · 熱伝導率 29/33/38/46 W/(m·K)(20℃) · "
              "縦弾性係数 125/125/125/121 kN/mm2 · 熱膨張係数 16.7/16.2/16.2/16.4 ppm/K(20~300℃).")

c7521_kiyo = {"source": S_KIYO, "properties": [
    {"key": "physical.density", "value": 8730.0, "unit": "kg/m^3", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "比重 8.73", "temperature_c": "미인쇄"},
     "notes": KIYO_TABLE + " 유통사 滑川(namekawa) 手配品 시트는 C7521 을 `比重 8.80` 으로 찍어 0.8% 높다 — "
              "제조사 값을 넣고 유통사 값은 여기 남긴다(브리프 565). CDA C75200 의 Specific Gravity 8.75 와는 0.2% 안이다.",
     "value_check": "8.73 g/cm3 x 1000 = 8730 kg/m^3"},
    {"key": "mechanical.youngs_modulus", "value": 1.25e11, "unit": "Pa", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "縦弾性係数 125 kN/mm2", "temper": "미인쇄(조질을 갈라 찍지 않는다)",
                    "direction": "미인쇄", "modulus_type": "縦弾性係数(인장 영률)"},
     "notes": KIYO_TABLE + " 브리프 604 검산 — Cu-Ni-Zn 통용대역 110~130 GPa 안이다. "
              "CDA C75200 의 Modulus of Elasticity in Tension 18000 ksi = 124.1 GPa 와 0.7% 안에서 만난다.",
     "value_check": "125 kN/mm2 = 125 GPa = 1.25e11 Pa"},
    {"key": "mechanical.poisson_ratio", "value": 0.32, "unit": "1", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "ポアソン比 0.32", "temper": "미인쇄", "direction": "미인쇄"},
     "notes": KIYO_TABLE + " **역산하지 않았다**(브리프 43) — CDA C75200 이 E 18000 ksi 와 G 6800 ksi 를 "
              "함께 인쇄해 `nu = E/(2G)-1 = 0.3235` 가 나오고 이 인쇄값 0.32 와 1% 안에서 만나지만, "
              "우리가 나눈 것이 아니라 벤더가 인쇄한 값을 넣었고 그 계산이 성립한다는 사실만 여기 적는다."},
    {"key": "thermal.expansion_linear", "value": 1.62e-5, "unit": "1/K", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "熱膨張係数 16.2 ppm/K (20~300℃)", "temperature_range_c": "20-300",
                    "direction": "미인쇄"},
     "notes": KIYO_TABLE + " CDA C75200 의 9.0e-6/°F(68~572°F) x 1.8 = 16.2e-6/K 와 **글자까지 같다**.",
     "value_check": "16.2 ppm/K = 1.62e-5 1/K"},
    {"key": "thermal.conductivity", "value": 33.0, "unit": "W/(m*K)", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "熱伝導率 33 W/(m·K) (20℃)", "temperature_c": 20, "direction": "미인쇄"},
     "notes": KIYO_TABLE + " CDA C75200 의 19 Btu/(sq ft·ft·hr·°F) x 1.730735 = 32.88 W/(m·K) 와 0.4% 안이다."},
    {"key": "electrical.conductivity", "value": 6 * IACS, "unit": "S/m", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "導電率 6 %IACS", "temperature_c": 20},
     "notes": KIYO_TABLE + " CDA C75200 의 Electrical Conductivity 6 %IACS 와 같다. "
              "환산계수는 카탈로그 재료 179 베릴륨동 행이 쓰는 것과 같다(%IACS x 5.8e5 S/m).",
     "value_check": "6 %IACS x 5.8e5 = 3.48e6 S/m"},
    {"key": "thermal.melting_point", "value": 1333.15, "unit": "K", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "融点 1060 ℃",
                    "phase_boundary": "벤더가 `융점` 한 값만 찍고 고상선/액상선을 안 가른다"},
     "notes": KIYO_TABLE + " CDA C75200 은 이 자리를 둘로 갈라 Liquidus 2030°F(1110.0℃) · Solidus 1960°F(1071.1℃) 로 "
              "찍는다 — 벤더의 단일 `融点 1060` 은 고상선 쪽에 가깝고 11℃ 낮다. 두 문서가 자리를 다르게 잡으므로 "
              "여기서는 벤더 인쇄값만 넣고 CDA 의 두 값은 이 문장에 남긴다(브리프 565·662).",
     "value_check": "1060 degC + 273.15 = 1333.15 K"},
] + spec_rows("C7521",
              "JIS H 3110 표3(りん青銅及び洋白の板及び条の機械的性質)이 같은 밴드를 찍는다 — "
              "長井技研 資料館의 JIS H 3110:2000 転載판에서 C7521P/R 의 O 375 이상·伸び 20 이상, "
              "1/2H 440~570·伸び 5 이상·HV 120~180, H 540 이상·伸び 3 이상·HV 150 이상을 확인했고, "
              "kikakurui.com 의 H 3110:2018 판도 C7521P-O 를 375 N/mm2 이상·20% 이상으로 찍는다. "
              "**두 판·두 문서가 같은 밴드를 준다**(브리프 615).")}

c7521_cda = {"source": S_CDA_75200, "properties": [
    {"key": "thermal.specific_heat", "value": 377.0, "unit": "J/(kg*K)", "method": "handbook", "tier": 2,
     "conditions": {"printed_as": "Specific Heat Capacity 0.09 Btu/lb/°F at 68°F", "temperature_c": 20,
                    "precision_note": "원문이 유효숫자 1자리(0.09)라 해상도는 ±0.005 Btu = ±21 J/(kg·K) 다"},
     "notes": ("CDA copper.org C75200 `Physical Properties` 블록. 0.09 Btu/(lb·°F) x 4186.8 = 376.81 → 377 로 "
               "적었다. **이 칸을 채운 유일한 문**이다 — 清峰 一覧表의 物理的性質 블록(융점·ポアソン比·比重·導電率·"
               "熱伝導率·縦弾性係数·熱膨張係数 일곱 행)에 比熱 행이 없고, TOKKIN 은 형제 C7701·C5210 페이지에는 "
               "比熱 377 J/(kg·K)를 찍으면서 **C7521 페이지에는 物理的性質 블록 자체가 없다**"
               "(브리프 613·675 — k 는 찍고 Cp 는 안 찍는 비대칭, 그리고 형제 등급끼리 갈린다). "
               "교차검산 — TOKKIN 이 C7701 에 찍는 377 J/(kg·K)와 CDA 가 C77000·C52100 에 찍는 0.09 Btu 가 모두 같은 값이다."),
     "value_check": "0.09 x 4186.8 = 376.81 J/(kg*K)"},
    {"key": "mechanical.shear_modulus", "value": round(6800 * KSI, 0), "unit": "Pa",
     "method": "handbook", "tier": 2,
     "conditions": {"printed_as": "Modulus of Rigidity 6800 ksi", "temper": "미인쇄", "direction": "미인쇄"},
     "notes": ("CDA copper.org C75200 `Physical Properties` 블록. 6800 ksi x 6.894757e6 = 4.6884e10 Pa = 46.88 GPa. "
               "같은 블록의 Modulus of Elasticity in Tension 18000 ksi = 124.1 GPa 와 짝이다 — 이 둘로 ν 를 "
               "만들지 않았다(브리프 43). 清峰의 인쇄 ポアソン比 0.32 를 따로 넣었다."),
     "value_check": "6800 ksi x 6.894757e6 = 4.6884e10 Pa"},
]}


TOKKIN_7701_TABLE = ("TOKKIN(特殊金属エクセル) C7701 제품페이지 `物理的性質` 블록 verbatim — 密度 8.70 g/cm3 · "
                     "比熱 377 J/(kg·K) · 電気抵抗 30 µΩ·cm · 弾性係数 127 GPa · 熱膨張係数 16.7x10-6/K · "
                     "熱伝導率 29 W/(m·K)(25℃) · 融点 1050 ℃ · 磁性 なし. 같은 페이지 `規格` 블록이 "
                     "`JIS C7701 (H3130)` · `UNS/CDA C77000` · `主要成分 CuNi18Zn27` 을 인쇄한다.")

c7701_tokkin = {"source": S_TOKKIN_7701, "properties": [
    {"key": "physical.density", "value": 8700.0, "unit": "kg/m^3", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "密度 8.70 g/cm3", "temperature_c": "미인쇄"},
     "notes": TOKKIN_7701_TABLE + " " + XCHK_7701, "value_check": "8.70 g/cm3 x 1000 = 8700 kg/m^3"},
    {"key": "thermal.specific_heat", "value": 377.0, "unit": "J/(kg*K)", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "比熱 377 J/(kg·K)", "temperature_c": "미인쇄"},
     "notes": TOKKIN_7701_TABLE + " CDA C77000 의 Specific Heat Capacity 0.09 Btu/(lb·°F) at 68°F x 4186.8 = "
              "376.81 J/(kg·K) 와 만난다 — 서로 독립인 두 문서가 같은 값을 준다."},
    {"key": "mechanical.youngs_modulus", "value": 1.27e11, "unit": "Pa", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "弾性係数 127 GPa", "temper": "미인쇄", "direction": "미인쇄",
                    "modulus_type": "弾性係数(등방 대표값. 방향별 값은 JCBA 실측 행에 따로 있다)"},
     "notes": TOKKIN_7701_TABLE + " " + XCHK_7701 + " 방향별 실측(JCBA 120~146)의 45° 대역과 겹친다.",
     "value_check": "127 GPa = 1.27e11 Pa"},
    {"key": "electrical.resistivity_volume", "value": 3.0e-7, "unit": "ohm*m", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "電気抵抗 30 µΩ·cm", "temperature_c": "미인쇄"},
     "notes": TOKKIN_7701_TABLE + " 자기검산 — 1.7241 µΩ·cm / 30 µΩ·cm = 5.75 %IACS 이고 "
              "清峰·CDA 가 찍는 導電率 5.5 %IACS 와 4.5% 안에서 만난다.",
     "value_check": "30 uOhm*cm = 30e-8 ohm*m = 3.0e-7 ohm*m"},
]}

c7701_kiyo = {"source": S_KIYO, "properties": [
    {"key": "mechanical.poisson_ratio", "value": 0.32, "unit": "1", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "ポアソン比 0.32", "temper": "미인쇄", "direction": "미인쇄"},
     "notes": KIYO_TABLE + " **역산하지 않았다**(브리프 43) — CDA C77000 이 E 18000 ksi 와 G 6800 ksi 를 함께 "
              "인쇄해 `nu = E/(2G)-1 = 0.3235` 가 나오고 이 인쇄값 0.32 와 1% 안에서 만나지만, "
              "우리가 나눈 것이 아니라 벤더가 인쇄한 값을 넣었고 그 계산이 성립한다는 사실만 여기 적는다."},
    {"key": "mechanical.youngs_modulus", "value": 1.25e11, "unit": "Pa", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "縦弾性係数 125 kN/mm2", "temper": "미인쇄", "direction": "미인쇄",
                    "modulus_type": "縦弾性係数(등방 대표값)"},
     "notes": KIYO_TABLE + " TOKKIN 은 같은 등급을 127 GPa 로 찍어 1.6% 높고 CDA C77000 은 18000 ksi = 124.1 GPa 다 — "
              "세 문서가 124~127 안에 모인다. " + XCHK_7701,
     "value_check": "125 kN/mm2 = 1.25e11 Pa"},
    {"key": "thermal.expansion_linear", "value": 1.67e-5, "unit": "1/K", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "熱膨張係数 16.7 ppm/K (20~300℃)", "temperature_range_c": "20-300",
                    "direction": "미인쇄"},
     "notes": KIYO_TABLE + " TOKKIN 이 온도구간 없이 16.7x10-6/K 를 찍고 CDA C77000 이 "
              "9.3e-6/°F(68~572°F) x 1.8 = 16.74e-6/K 를 찍는다 — 세 문서가 같은 값이고 온도구간을 인쇄한 것은 "
              "清峰뿐이라 이 행을 골랐다(브리프 677 — 온도 조건이 없는 행은 다른 종류의 진술이다).",
     "value_check": "16.7 ppm/K = 1.67e-5 1/K"},
    {"key": "thermal.conductivity", "value": 29.0, "unit": "W/(m*K)", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "熱伝導率 29 W/(m·K) (20℃)", "temperature_c": 20, "direction": "미인쇄"},
     "notes": KIYO_TABLE + " TOKKIN 은 같은 29 를 25℃ 로, CDA C77000 은 17 Btu/(sq ft·ft·hr·°F) x 1.730735 = "
              "29.42 W/(m·K) 를 68°F 로 찍는다."},
    {"key": "electrical.conductivity", "value": 5.5 * IACS, "unit": "S/m", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "導電率 5.5 %IACS", "temperature_c": 20},
     "notes": KIYO_TABLE + " CDA C77000 도 5.5 %IACS 다. TOKKIN 의 電気抵抗 30 µΩ·cm 를 뒤집으면 5.75 %IACS 라 "
              "4.5% 안에서 만난다. **베릴륨동(재료 179)의 22 %IACS 와 네 배 차이**다 — 사용자가 지적한 근사 오차의 축이다.",
     "value_check": "5.5 %IACS x 5.8e5 = 3.19e6 S/m"},
    {"key": "thermal.melting_point", "value": 1328.15, "unit": "K", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "融点 1055 ℃",
                    "phase_boundary": "벤더가 `융점` 한 값만 찍고 고상선/액상선을 안 가른다"},
     "notes": KIYO_TABLE + " CDA C77000 의 Melting Point - Liquidus 1930°F = 1054.4 ℃ 와 0.6℃ 안에서 만난다. "
              "TOKKIN 은 같은 자리를 1050 ℃ 로 찍는다.",
     "value_check": "1055 degC + 273.15 = 1328.15 K"},
] + spec_rows("C7701",
              "이 밴드는 JIS H 3130(ばね用のベリリウム銅，チタン銅，りん青銅，ニッケル−すず銅及び洋白の板並びに条)의 "
              "C7701 규정과 같은 자리다 — JIS H 0500 용어 1404 가 `ばね用洋白 … ばね限界値가 규정되어 있는 "
              "Cu 54.0~58.0%, Ni 16.5~19.5%, 나머지 Zn 합금(C7701)` 이라 정의하고, 質別 SH 는 "
              "`ほとんど曲げ加工を施さない板ばね` 용이라 밝힌다. JIS 정본은 아직 안 열었다(브리프 627③).")}

c7701_jcba = jcba_rows("C7701", S_JCBA_7701, E_NOTE_7701,
                       extra_note=("규격 밴드 대조 — 清峰/JIS 의 C7701 引張強さ 밴드(1/2H 540-655 · H 630-735 · "
                                   "EH 705-805 N/mm2)와 HV 밴드(150-210 · 180-240 · 210-260)를 이 실측이 전부 "
                                   "만족한다. 다만 **45° 1/2H 의 537 만 밴드 하한 540 을 0.6% 밑돈다** — "
                                   "규격 인수는 45° 방향으로 하지 않으므로 위반이 아니다. "
                                   "耐力은 1/2H 에서만 보증 하한(390)을 밑돈다(330/309/320) — 그 사유는 "
                                   "같은 재료의 규격 耐力 행 notes 에 적었다."))

# JCBA 표2.2 疲労試験結果(破断応力) — C7701-H 材만 시험했다
FAT = {"L.D.": {100000: 408, 1000000: 246, 10000000: 200},
       "T.D.": {100000: 432, 1000000: 264, 10000000: 217}}
FAT_METHOD = ("JCBA 시험조건(bjm002.pdf 2.4.2) — JCBA T308:2001(仮) 준거 양진 반복굽힘(両振り), 시험편 폭 10±0.2 mm, "
              "편진폭 δ=2 mm, 나이프에지 간극 0.05 mm, 시험기 アカシ AST-52B 및 IMV VS-1030S-140. "
              "응력은 원문 식 (2-1) `σ = 3·E·t·δ / (2·l²)` 로 산출하고 그때의 E 는 같은 DB 의 たわみ係数 실측값을 쓴다 — "
              "**하중을 직접 잰 것이 아니라 변위에서 만든 응력**이라 그 사실을 조건에 적는다.")

c7701_fat = {"source": S_JCBA_FAT, "properties": [
    {"key": "mechanical.fatigue_strength", "value": v * 1e6, "unit": "Pa", "method": "measured", "tier": 1,
     "conditions": {"temper": "H", "direction": ("MD (rolling direction)" if d == "L.D."
                                                 else "TD (transverse to rolling)"),
                    "direction_verbatim": ("L.D. (圧延方向に平行)" if d == "L.D." else "T.D. (圧延方向に直角)"),
                    "cycles": c, "stress_ratio_R": -1, "loading": "fully reversed plane bending (両振り)",
                    "thickness_mm": 0.30, "printed_as": "%s N/mm2" % v,
                    "test_method": "JCBA T308:2001(仮) 銅および銅合金薄板条の疲労特性試験方法",
                    "stress_basis": "변위(δ=2 mm)에서 σ=3Etδ/(2l²)로 산출한 최대굽힘응력"},
     "notes": ("JCBA 표2.2 `疲労試験結果(破断応力 N/mm2)` 의 C7701 %s / %s 행. 이 DB 는 C7701 에 대해 "
               "**H 材만** 피로시험했다(1/2H·EH 행은 비어 있다). 같은 표의 형제 등급이 심판이 된다 — "
               "C5210-H 는 1e7 에서 L.D. 247 · T.D. 252 이고 C1720(베릴륨동 2종) HM 은 403·393 이라 "
               "**C7701-H 의 200·217 이 인청동보다 낮고 베릴륨동의 절반**이다. 이것이 사용자의 "
               "`베릴륨동으로 근사` 가 위험한 이유의 정량이다. %s" % (c, d, FAT_METHOD)),
     "value_check": "%s N/mm2 = %s Pa" % (v, v * 1e6)}
    for d, byc in FAT.items() for c, v in sorted(byc.items())]}


TOKKIN_5210_TABLE = ("TOKKIN(特殊金属エクセル) C5210 제품페이지 `物理的性質` 블록 verbatim — 密度 8.86 g/cm3 · "
                     "比熱 377 J/(kg·K) · 電気抵抗 9.6 µΩ·cm · 弾性係数 98 GPa · 熱膨張係数 17.8x10-6/K · "
                     "熱伝導率 79.5 W/(m·K) · 融点 871-982 ℃ · 磁性 なし. 같은 페이지 `規格` 블록이 "
                     "`JIS C5210 (H3130)` · `UNS/CDA C52100` · `主要成分 CuSn8` 을 인쇄한다.")
DIVERGE_5210 = ("**이 시트는 CDA C52100 과 세 칸에서 갈린다**(熱伝導率 79.5 대 62.31 W/(m·K) · "
                "電気抵抗 9.6 µΩ·cm(=17.96 %IACS) 대 13 %IACS · 弾性係数 98 대 110.3 GPa). "
                "그 세 칸은 CDA 로 넣었고 사유는 재료 attributes 의 `verdict_vendor_divergence` 에 있다. "
                "여기 넣는 칸은 두 문서가 **일치하는** 칸이다.")

c5210_tokkin = {"source": S_TOKKIN_5210, "properties": [
    {"key": "physical.density", "value": 8860.0, "unit": "kg/m^3", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "密度 8.86 g/cm3", "temperature_c": "미인쇄"},
     "notes": TOKKIN_5210_TABLE + " CDA C52100 의 Specific Gravity 8.8 과 0.7% 안이다. " + DIVERGE_5210,
     "value_check": "8.86 g/cm3 x 1000 = 8860 kg/m^3"},
    {"key": "thermal.specific_heat", "value": 377.0, "unit": "J/(kg*K)", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "比熱 377 J/(kg·K)", "temperature_c": "미인쇄"},
     "notes": TOKKIN_5210_TABLE + " CDA C52100 의 0.09 Btu/(lb·°F) at 68°F x 4186.8 = 376.81 과 만난다. "
              + DIVERGE_5210},
    {"key": "thermal.expansion_linear", "value": 1.78e-5, "unit": "1/K", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "熱膨張係数 17.8x10-6/K", "temperature_range_c": "미인쇄", "direction": "미인쇄"},
     "notes": TOKKIN_5210_TABLE + " CDA C52100 의 10.1e-6/°F(68~572°F) x 1.8 = 18.18e-6/K 와 2.1% 안이다. "
              "**온도구간은 이 시트가 안 찍는다** — 원문이 안 찍었다는 사실 자체가 조건이다(브리프 677). "
              + DIVERGE_5210,
     "value_check": "17.8e-6 /K = 1.78e-5 1/K"},
    {"key": "thermal.melting_point", "value": 1144.15, "unit": "K", "method": "measured", "tier": 1,
     "conditions": {"printed_as": "融点 871-982 ℃", "phase_boundary": "고상선(범위 하한)",
                    "printed_range": "871-982 degC"},
     "notes": TOKKIN_5210_TABLE + " 인쇄된 것은 구간이고 그 **하한(고상선)** 만 넣었다. 구간 중앙값은 만들지 "
              "않았다(브리프 451). CDA C52100 은 같은 자리를 Solidus 1620°F(882.2℃) · Liquidus 1880°F(1026.7℃)로 "
              "찍어 고상선이 11℃ 높고 액상선이 45℃ 높다. " + DIVERGE_5210,
     "value_check": "871 degC + 273.15 = 1144.15 K"},
]}

c5210_cda = {"source": S_CDA_52100, "properties": [
    {"key": "mechanical.youngs_modulus", "value": round(16000 * KSI, 0), "unit": "Pa",
     "method": "handbook", "tier": 2,
     "conditions": {"printed_as": "Modulus of Elasticity in Tension 16000 ksi", "temper": "미인쇄",
                    "direction": "미인쇄", "modulus_type": "인장 영률(등방 대표값)"},
     "notes": ("CDA copper.org C52100 `Physical Properties` 블록. 16000 ksi x 6.894757e6 = 1.1032e11 Pa = 110.3 GPa. "
               + E_NOTE_5210 + " TOKKIN C5210 시트의 弾性係数 98 GPa 는 인쇄값이지만 여기 안 넣었다 — "
               "지운 것이 아니라 재료 attributes 의 `verdict_vendor_divergence` 와 이 문장에 남겼다(브리프 565)."),
     "value_check": "16000 ksi x 6.894757e6 = 1.1032e11 Pa"},
    {"key": "mechanical.shear_modulus", "value": round(6000 * KSI, 0), "unit": "Pa",
     "method": "handbook", "tier": 2,
     "conditions": {"printed_as": "Modulus of Rigidity 6000 ksi", "temper": "미인쇄", "direction": "미인쇄"},
     "notes": ("CDA copper.org C52100 `Physical Properties` 블록. 6000 ksi x 6.894757e6 = 4.1369e10 Pa = 41.37 GPa. "
               "같은 블록의 E 16000 ksi 와 짝이라 `nu = E/(2G)-1 = 0.333` 이 나오지만 **만들지 않았다**(브리프 43) — "
               "이 재료의 포아송비는 두 문서 어디에도 인쇄돼 있지 않다."),
     "value_check": "6000 ksi x 6.894757e6 = 4.1369e10 Pa"},
    {"key": "thermal.conductivity", "value": round(36 * BTU_FT_HR_F, 2), "unit": "W/(m*K)",
     "method": "handbook", "tier": 2,
     "conditions": {"printed_as": "Thermal Conductivity 36 Btu/(sq ft·ft·hr·°F) at 68°F", "temperature_c": 20,
                    "direction": "미인쇄"},
     "notes": ("CDA copper.org C52100 `Physical Properties` 블록. 36 x 1.730735 = 62.31 W/(m·K). "
               "**TOKKIN C5210 시트는 같은 칸을 79.5 W/(m·K)로 찍어 28% 높다.** 두 값을 Wiedemann-Franz "
               "(L=2.44e-8 W·Ω/K², T=293 K)로 각각 자기 도전율과 대 보면 TOKKIN 74.5 대 인쇄 79.5(6% 안) · "
               "CDA 53.9 대 인쇄 62.3(13% 안) 으로 **둘 다 자기정합**이다 — 한 열이 죽은 것이 아니라 두 문서가 "
               "서로 다른 Sn 함량대를 찍는다(브리프 642). 공인 DB 쪽을 넣고 벤더 인쇄값은 여기 남긴다."),
     "value_check": "36 Btu/(sq ft*ft*hr*degF) x 1.730735 = 62.31 W/(m*K)"},
    {"key": "electrical.conductivity", "value": 13 * IACS, "unit": "S/m", "method": "handbook", "tier": 2,
     "conditions": {"printed_as": "Electrical Conductivity 13 %IACS at 68°F", "temperature_c": 20},
     "notes": ("CDA copper.org C52100 `Physical Properties` 블록. 13 %IACS x 5.8e5 = 7.54e6 S/m. "
               "**TOKKIN C5210 시트의 電気抵抗 9.6 µΩ·cm 를 뒤집으면 17.96 %IACS 라 38% 높다.** "
               "Cu-8Sn 인청동의 통용 도전율은 11~13 %IACS 이고 Cu-6Sn(C5191)이 15~18 %IACS 라 "
               "TOKKIN 값은 한 단계 낮은 Sn 대역에 해당한다 — 열전도율 칸과 **같은 방향으로 함께** 어긋난다."),
     "value_check": "13 %IACS x 5.8e5 = 7.54e6 S/m"},
]}

c5210_jcba = jcba_rows("C5210", S_JCBA_5210, E_NOTE_5210,
                       extra_note=("이 표는 브리프가 명시한 확장 표적이라 열었다 — C7701 과 **같은 표**다"
                                   "(브리프 602·649). 카탈로그에는 일반 인청동 재료 39 `C51000_Phosphor_Bronze` 만 "
                                   "있고 스프링 등급 C5210 이 없었다."))

DOWA_TABLE = ("DOWAメタルテック `YCuT-M` 제품페이지 物理的性質 표 verbatim — 融点 1075 ℃ · 密度 8.7 g/cm3(20℃) · "
              "熱膨張係数 17.6x10-6/K(20~300℃) · 熱伝導度 50 W/(m·K)(20℃, EH) · 導電率 12 %IACS(20℃, EH) · "
              "縦弾性係数 117 kN/mm2(EH) · ポアソン比 0.33 · 磁気的特性 非磁性. 標準組成는 Ti 3.2 / Cu Rem.")
DOWA_SCOPE = ("등급 대응이 **동일 선언이 아니다** — 같은 페이지가 `関連規格 CDA C19900、JIS C1990相当(1/4H、EH材)` 로 "
              "`相当`(equivalent)이라 적는다. 그래서 이 시트에서 온 값은 t3 다(브리프 632·123). "
              "조질 표기도 갈린다 — DOWA 는 1/4H·1/2H·H·EH·SH, JCBA 실측은 1/4HM·EHM(ミルハーデン)이다. "
              "**섞지 않았다**(브리프 586) — DOWA 의 조질별 引張強さ·耐力·伸び·HV 표는 옮기지 않았다. "
              "조성은 만난다 — CDA C19900 이 Ti 2.9~3.5% / Cu Rem. 이고 DOWA 標準組成가 Ti 3.2 다.")

c1990_dowa = {"source": S_DOWA, "properties": [
    {"key": "physical.density", "value": 8700.0, "unit": "kg/m^3", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "密度 8.7 g/cm3 (20℃)", "temperature_c": 20,
                    "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE, "value_check": "8.7 g/cm3 x 1000 = 8700 kg/m^3"},
    {"key": "mechanical.youngs_modulus", "value": 1.17e11, "unit": "Pa", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "縦弾性係数 117 kN/mm2 (EH)", "temper": "EH (DOWA 표기)",
                    "direction": "미인쇄", "modulus_type": "縦弾性係数(등방 대표값)", "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE + " " + E_NOTE_1990, "value_check": "117 kN/mm2 = 1.17e11 Pa"},
    {"key": "mechanical.poisson_ratio", "value": 0.33, "unit": "1", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "ポアソン比 0.33", "temper": "미인쇄", "direction": "미인쇄",
                    "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE + " CDA C19900 은 `Physical Properties: No physical properties for this alloy` 라 "
              "대조군이 없다. 이 시트가 이 칸을 찍는 유일한 문서다."},
    {"key": "thermal.expansion_linear", "value": 1.76e-5, "unit": "1/K", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "熱膨張係数 17.6x10-6/K (20~300℃)", "temperature_range_c": "20-300",
                    "direction": "미인쇄", "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE, "value_check": "17.6e-6 /K = 1.76e-5 1/K"},
    {"key": "thermal.conductivity", "value": 50.0, "unit": "W/(m*K)", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "熱伝導度 50 W/(m·K) (20℃, EH)", "temperature_c": 20,
                    "temper": "EH (DOWA 표기)", "direction": "미인쇄", "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE + " 자기검산 — Wiedemann-Franz(L=2.44e-8, T=293 K)로 같은 시트의 導電率 12 %IACS"
              "(=ρ 14.37 µΩ·cm)에서 전자열전도만 재면 49.8 W/(m·K)이고 인쇄값 50 과 0.4% 안이다. "
              "**같은 표의 두 열이 서로를 검산한다**(브리프 603)."},
    {"key": "electrical.conductivity", "value": 12 * IACS, "unit": "S/m", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "導電率 12 %IACS (20℃, EH)", "temperature_c": 20,
                    "temper": "EH (DOWA 표기)", "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE + " 베릴륨동(재료 179)의 22 %IACS 보다 낮고 니켈실버 C7701 의 5.5 %IACS 보다 두 배 높다.",
     "value_check": "12 %IACS x 5.8e5 = 6.96e6 S/m"},
    {"key": "thermal.melting_point", "value": 1348.15, "unit": "K", "method": "measured", "tier": 3,
     "conditions": {"printed_as": "融点 1075 ℃",
                    "phase_boundary": "벤더가 `융점` 한 값만 찍고 고상선/액상선을 안 가른다",
                    "grade_scope": DOWA_SCOPE},
     "notes": DOWA_TABLE, "value_check": "1075 degC + 273.15 = 1348.15 K"},
]}

c1990_jcba = jcba_rows("C1990", S_JCBA_1990, E_NOTE_1990,
                       extra_note=("이 표는 브리프가 명시한 확장 표적이라 열었다 — C1720(베릴륨동 2종)과 **같은 표**다"
                                   "(브리프 602·649). 조질 1/4HM·EHM 은 ミルハーデン(석출경화를 성형 전에 끝낸 상태)이라 "
                                   "DOWA 시트의 1/4H~SH 표기와 다른 축이다 — 섞지 않았다(브리프 586)."))


# ── 파일로 찍는다 ────────────────────────────────────────────────────────────
def entry(new_mat, match, doc):
    e = dict(stamp_axes(doc))
    if new_mat is not None:
        e["new_material"] = new_mat
    else:
        e["match_name"] = match
    return e


FILES = {
    "zb01_c7521_nickel_silver.json": {"materials": [
        entry(mat_7521, None, c7521_kiyo),
        entry(None, NAME_7521, c7521_cda),
    ]},
    "zb02_c7701_spring_nickel_silver.json": {"materials": [
        entry(mat_7701, None, c7701_tokkin),
        entry(None, NAME_7701, c7701_kiyo),
        entry(None, NAME_7701, c7701_jcba),
        entry(None, NAME_7701, c7701_fat),
    ]},
    "zb03_c5210_spring_phosphor_bronze.json": {"materials": [
        entry(mat_5210, None, c5210_tokkin),
        entry(None, NAME_5210, c5210_cda),
        entry(None, NAME_5210, c5210_jcba),
    ]},
    "zb04_c1990_spring_titanium_copper.json": {"materials": [
        entry(mat_1990, None, c1990_dowa),
        entry(None, NAME_1990, c1990_jcba),
    ]},
}

if __name__ == "__main__":
    tot = 0
    for fn, doc in FILES.items():
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
        n = sum(len(m["properties"]) for m in doc["materials"])
        tot += n
        print("%-46s 항목 %d · 물성행 %d" % (fn, len(doc["materials"]), n))
    print("합계 물성행 %d" % tot)
