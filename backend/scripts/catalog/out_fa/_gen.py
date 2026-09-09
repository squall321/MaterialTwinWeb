# 70차 FA — MGC·Sumitomo·Resonac 등급 카드를 세우고 벤더 총합표의 인쇄값을 옮기는 생성기
# 값은 전부 로컬 원문(HTML `<td>` 파싱 / PDF 300~350dpi 렌더 대조)에서 옮긴 것이고 계산·추정은 없다.
import json, os, collections

OUT = os.path.dirname(os.path.abspath(__file__))
PCB = "/data/paper_patent_corpus/standards_appnotes/pcb"

GPa, MPa, kNm = 1e9, 1e6, 1e3
def C2K(c): return round(c + 273.15, 2)
def ppm(v): return float(f"{v * 1e-6:.12g}")   # 2진 부동소수 잡음 제거(값은 안 바뀐다)
def pct(v): return float(f"{v / 100:.12g}")   # % -> 무차원. 같은 이유로 잡음만 턴다

MATS = []

# ─────────────────────────────────────────────────────────────────────────────
# 1. MGC BT 계열 13등급 — hfbt.html 일람표
# ─────────────────────────────────────────────────────────────────────────────
SRC_MGC_BT = {
    "kind": "datasheet",
    "title": "半導体パッケージ用低熱膨張率ハロゲンフリーBT材料 — CCL-HL832/HL972・GHPL-830 一般特性一覧 (三菱ガス化学 製品ラインアップ)",
    "url": "https://www.mgc.co.jp/products/sc/btprint/lineup/hfbt.html",
    "publisher": "Mitsubishi Gas Chemical Company, Inc.",
    "year": 2026,
    "local_path": f"{PCB}/MGC_CCL-HL832-HL972_BTResin_Lineup_ja_2026-09-09.html",
    "url_note": "저장본은 일본어판. 영문 동일 표는 `https://www.mgc.co.jp/eng/products/sc/btprint/lineup/hfbt.html`(라이브 출처 306 이 쓰는 URL)이고 69차 EB 가 행 하나까지 같음을 확인했다.",
}

# 등급별 인쇄값. 열 순서는 원문 표와 같다.
# (표시명, 표기(CCL/프리프레그), 曲げ強さMPa, 曲げ弾性率GPa, 引張強さMPa, ヤング率GPa,
#  Tg_DMA, Tg_TMA, CTE_a1, CTE_a2, peel_kNm, 密度, 比熱, 熱伝導率, ポアッソン, 吸水率%,
#  Dk(1/5/10GHz), Df(1/5/10GHz))
BT = [
 ("CCL-HL832NX type A", "ccl", 450, 28, 270, 28, 230, 200, 14, 5, 0.85, 2.1, 1.00, 0.8, 0.19, 0.44,
  (4.9, 4.8, 4.7), (0.011, 0.011, 0.012)),
 ("CCL-HL832NS", "ccl", 490, 27, 290, 27, 255, 230, 10, 3, 1.0, 1.9, 1.00, 0.6, 0.18, 0.31,
  (4.4, 4.3, 4.3), (0.006, 0.008, 0.008)),
 ("CCL-HL832NS type LC", "ccl", 750, 30, 400, 30, 255, 230, 7, 3, 1.0, 1.9, 0.95, 0.6, 0.18, 0.30,
  (4.0, 3.9, 3.9), (0.006, 0.007, 0.008)),
 ("CCL-HL832NSR", "ccl", 550, 30, 280, 30, 230, 210, 8, 3, 1.0, 2.0, 0.95, 0.7, 0.18, 0.32,
  (4.5, 4.4, 4.4), (0.008, 0.011, 0.012)),
 ("CCL-HL832NSR type LCA", "ccl", 670, 33, 420, 33, 230, 210, 4.5, 2, 1.0, 2.0, 0.95, 0.7, 0.18, 0.32,
  (4.1, 4.0, 4.0), (0.008, 0.011, 0.012)),
 ("CCL-HL832NSF", "ccl", 510, 32, 290, 32, 300, 270, 5, 3, 0.8, 2.0, 0.9, 0.7, 0.19, 0.35,
  (4.4, 4.4, 4.3), (0.006, 0.008, 0.008)),
 ("CCL-HL832NSF type LCA", "ccl", 600, 34, 390, 34, 300, 270, 3, 2, 0.8, 2.0, 0.9, 0.7, 0.18, 0.35,
  (4.0, 4.0, 3.9), (0.006, 0.008, 0.008)),
 ("CCL-HL832NSA type LCA", "ccl", 420, 31, 350, 31, None, 270, 1, 0.5, 0.6, 2.0, 0.9, 0.7, 0.15, 0.39,
  (4.0, 4.0, 3.9), (0.005, 0.007, 0.007)),
 ("CCL-HL972LF type LD", "ccl", 370, 25, 220, 25, 270, 240, 10, 4, 0.7, 1.9, 0.9, 0.6, 0.2, 0.35,
  (3.5, 3.5, 3.4), (0.003, 0.004, 0.004)),
 ("CCL-HL972LFG", "ccl", 450, 23, 210, 23, 215, 200, 11, 4, 0.7, 1.8, 0.95, 0.6, None, 0.27,
  (4.0, 3.9, 3.8), (0.003, 0.004, 0.004)),
 ("CCL-HL972LFG type LD", "ccl", 440, 21, 210, 21, 215, 200, 10, 4, 0.7, 1.8, 0.95, 0.6, None, 0.27,
  (3.5, 3.5, 3.4), (0.002, 0.002, 0.002)),
 ("GHPL-830SR", "ppg", 420, 21, 290, 21, 195, 160, 8.3, 3, 1.0, 1.8, 0.9, 0.7, 0.21, 0.25,
  (3.9, 3.8, 3.7), (0.009, 0.010, 0.011)),
 ("GHPL-830SR type LC", "ppg", 490, 22, 300, 22, 195, 160, 6.3, 2, 1.0, 1.8, 0.9, 0.7, 0.21, 0.25,
  (3.7, 3.6, 3.5), (0.009, 0.010, 0.011)),
]

# 이 표에서 ヤング率 와 曲げ弾性率 가 13등급 전부 같은 숫자다 — 그 사실을 값마다 적는다.
E_DUP_NOTE = (
 "원문 verbatim: `ヤング率 |  |  | GPa | {v}`. 같은 표의 `曲げ弾性率 |  |  | GPa | {v}` 와 **숫자가 같다** — "
 "이 페이지 13등급 전부가 그렇다(28/28·27/27·30/30·30/30·33/33·32/32·34/34·31/31·25/25·23/23·21/21·21/21·22/22). "
 "게다가 이 페이지에는 시험규격 표기가 하나도 없다(HTML 전문에서 `JIS`·`ASTM`·`IPC` 적중 0). "
 "따라서 **이 문서만으로는 이 값이 인장인지 굽힘인지 확정되지 않는다** — 그래서 t3 로 낮췄다. "
 "환산 {v} GPa x 1e9 = {p:g} Pa; 되돌리면 {p:g}/1e9 = {v}. "
 "다만 같은 벤더의 다른 두 표는 두 행을 가른다 — `lineup/led.html` CCL-HL820WDI 가 曲げ弾性率 23/22 vs ヤング率 25/24, "
 "`lineup/fr4.html` CCL-EL190T 가 曲げ弾性率 縦27/横27 vs ヤング率 縦27/横26 로 **다른 숫자**를 찍는다. "
 "MGC 템플릿에서 ヤング率 행은 引張強さ 바로 아래 인장 블록에 놓인다. 다음 배치가 이 근거로 t1 승격을 검토할 수 있다."
)
E_DUP_SCOPE = (
 "값 자체는 이 등급에 인쇄된 것이고 등급 범위 문제는 없다. t3 로 내린 이유는 **시험모드 미확정**이다 — "
 "曲げ弾性率 행과 숫자가 동일하고 시험규격이 인쇄되지 않아 인장탄성률임을 이 문서가 말하지 않는다."
)

MGC_TABLE_NOTE = (
 "MGC 일본어 라인업 페이지의 `一般特性` 표. 값은 HTML `<tr>`/`<td>` 를 직접 파싱해 셀 경계를 확정했다 — "
 "레이아웃 추측이 끼어들 자리가 없다(열 밀림 위험 없음)."
)

def mgc_bt_card(row):
    (nm, form, flexS, flexE, uts, E, tgd, tgt, a1, a2, peel, rho, cp, k, nu, wa, dk, df) = row
    short = nm.replace("CCL-", "").replace("GHPL-", "GHPL-")
    aliases = sorted({nm, nm.replace(" ", ""), nm.replace("-", ""), nm.replace("CCL-", ""),
                      nm.replace("CCL-", "").replace(" ", ""), nm.replace(" type ", " Type "),
                      nm.replace(" type ", "-type-")})
    kind = "동장적층판(CCL)" if form == "ccl" else "프리프레그"
    P = []
    def add(key, val, unit, tier=1, cond=None, notes="", method="measured"):
        if val is None: return
        p = {"key": key, "value": val, "unit": unit, "method": method, "tier": tier}
        if cond: p["conditions"] = cond
        p["notes"] = notes
        P.append(p)

    add("physical.density", rho * 1000, "kg/m^3", 1, None,
        f"원문 verbatim: `密度 | g/cm3 | {rho}`. 원문 단위가 g/cm3(무차원 比重 이 아니라 밀도)이므로 "
        f"**곱한 수는 1000 g/cm3->kg/m^3 하나뿐**이다: {rho} x 1000 = {rho*1000:g} kg/m^3; 되돌리면 {rho*1000:g}/1000 = {rho}. "
        + MGC_TABLE_NOTE)
    add("mechanical.youngs_modulus", E * GPa, "Pa", 3,
        {"grade_scope": E_DUP_SCOPE, "test_mode": "unconfirmed", "orientation": "not stated"},
        E_DUP_NOTE.format(v=E, p=E * GPa))
    add("mechanical.flexural_modulus", flexE * GPa, "Pa", 1,
        {"test_mode": "flexural", "orientation": "not stated"},
        f"원문 verbatim: `曲げ弾性率 |  |  | GPa | {flexE}`. 행 이름이 굽힘탄성률로 명확하다(같은 표의 ヤング率 행과 "
        f"숫자가 같은 문제는 굽힘 쪽 해석에는 영향이 없다). 시험규격은 이 페이지에 인쇄되지 않았다. "
        f"환산 {flexE} x 1e9 = {flexE*GPa:g} Pa; 되돌리면 {flexE*GPa:g}/1e9 = {flexE}.")
    add("mechanical.flexural_strength", flexS * MPa, "Pa", 1, {"orientation": "not stated"},
        f"원문 verbatim: `曲げ強さ |  |  | MPa | {flexS}`. 환산 {flexS} x 1e6 = {flexS*MPa:g} Pa; 되돌리면 {flexS*MPa:g}/1e6 = {flexS}.")
    add("mechanical.tensile_strength", uts * MPa, "Pa", 1, {"orientation": "not stated"},
        f"원문 verbatim: `引張強さ |  |  | MPa | {uts}`. 굽힘강도({flexS} MPa)와 값이 크게 달라 이 표가 인장시험을 실제로 "
        f"돌린다는 증거다. 환산 {uts} x 1e6 = {uts*MPa:g} Pa; 되돌리면 {uts*MPa:g}/1e6 = {uts}.")
    add("mechanical.poisson_ratio", nu, "1", 1, None,
        f"원문 verbatim: `ポアッソン比 |  |  | － | {nu}`. 무차원이라 환산 없음. "
        f"인쇄 자릿수가 소수 둘이므로 그대로 옮겼다(부풀려 읽지 않았다). "
        f"MGC 는 같은 사이트에서 BT 쪽을 `ポアッソン比`, FR-4 쪽을 `ポアソン比` 로 달리 쓴다.")
    add("thermal.specific_heat", cp * 1000, "J/(kg*K)", 1, None,
        f"원문 verbatim: `比熱 |  |  | J/g・K | {cp}`. 환산 {cp} J/(g*K) x 1000 g/kg = {cp*1000:g} J/(kg*K); "
        f"되돌리면 {cp*1000:g}/1000 = {cp}. 측정법·온도는 이 페이지에 인쇄되지 않았다.")
    add("thermal.conductivity", k, "W/(m*K)", 1, None,
        f"원문 verbatim: `熱伝導率 |  |  | W/m*K | {k}`. 단위가 이미 SI 라 환산 없음. 측정법은 인쇄되지 않았다.")
    add("thermal.expansion_linear", ppm(a1), "1/K", 1,
        {"axis": "in-plane (X,Y)", "regime": "alpha1"},
        f"원문 verbatim: `熱膨張係数 | X,Y | α1 | ppm/℃ | {a1}`. 환산 {a1} ppm/℃ x 1e-6 = {ppm(a1):g} 1/K; "
        f"되돌리면 {ppm(a1):g}/1e-6 = {a1}. ppm/℃ 와 1/K 는 구간 크기가 같아 수치가 그대로 간다.")
    add("thermal.expansion_linear", ppm(a2), "1/K", 1,
        {"axis": "in-plane (X,Y)", "regime": "alpha2"},
        f"원문 verbatim: `熱膨張係数 | X,Y | α2 | ppm/℃ | {a2}`. **두 CTE 행 모두 원문이 `X,Y` 로 찍혀 있다** "
        f"(HTML 원본에서 `<th class=\"st002 bdrL\" scope=\"row\">X,Y</th>` 확인 — Z 축 행이 아니다). "
        f"환산 {a2} x 1e-6 = {ppm(a2):g} 1/K.")
    if tgd is not None:
        add("thermal.glass_transition", C2K(tgd), "K", 1, {"method_detail": "DMA"},
            f"원문 verbatim: `ガラス転移温度 | DMA | ℃ | {tgd}`. 환산 {tgd} + 273.15 = {C2K(tgd)} K; "
            f"되돌리면 {C2K(tgd)} - 273.15 = {tgd}.")
    else:
        add("thermal.glass_transition", C2K(350), "K", 1,
            {"method_detail": "DMA", "bound": "lower"},
            "원문 verbatim: `ガラス転移温度 | DMA | ℃ | >350`. **부등호로만 인쇄된 하한**이라 하한 한 행으로만 넣었다 — "
            "상한이 없으므로 두 행으로 가르지 않았다. 환산 350 + 273.15 = 623.15 K.")
    add("thermal.glass_transition", C2K(tgt), "K", 1, {"method_detail": "TMA"},
        f"원문 verbatim: `ガラス転移温度 | TMA | ℃ | {tgt}`. 환산 {tgt} + 273.15 = {C2K(tgt)} K. "
        f"DMA 와 TMA 는 다른 측정이라 평균 내지 않고 두 행으로 갈랐다.")
    add("interface.peel_strength", peel * kNm, "N/m", 1, {"copper_foil_thickness_um": 12},
        f"원문 verbatim: `ピール強度 | 12μm | KN/m | {peel}`. 환산 {peel} kN/m x 1000 = {peel*kNm:g} N/m.")
    add("chemical.moisture_absorption_equilibrium", pct(wa), "1", 1,
        {"temperature_c": 85, "relative_humidity_pct": 85, "duration_h": 168},
        f"원문 verbatim: `吸水率 | 85 ℃/85RH% 168h | % | {wa}`. 환산 {wa} % / 100 = {pct(wa):g}. "
        f"**원문은 168h 시점의 흡습률이고 평형 도달을 명시하지 않는다** — 키 이름이 평형흡습율이지만 조건의 duration_h 가 실제 값이다.")
    for f_, v in zip(("1 GHz", "5 GHz", "10 GHz"), dk):
        add("electrical.dielectric_constant", v, "1", 1, {"frequency": f_},
            f"원문 verbatim: `比誘電率 | {f_.replace(' ','')} | － | {v}`. 무차원.")
    for f_, v in zip(("1 GHz", "5 GHz", "10 GHz"), df):
        add("electrical.dissipation_factor", v, "1", 1, {"frequency": f_},
            f"원문 verbatim: `誘電正接 | {f_.replace(' ','')} | － | {v}`. 무차원.")
    add("thermal.flammability_ul94", "V-0" if not nm.startswith("CCL-HL972LFG") and not nm.startswith("GHPL")
        else "V-0 相当", None, 1, {"conditioning": "E-168/70"},
        "원문 verbatim: `耐燃焼性 | E-168/70 | － | V-0`" +
        ("(`相当`=상당 표기 포함)" if nm.startswith("CCL-HL972LFG") or nm.startswith("GHPL") else "") + ".")

    desc = (
        f"미쓰비시가스화학(MGC) BT(비스말레이미드-트리아진) 수지 {kind} `{nm}`. "
        f"반도체 패키지(FC-CSP/BGA 등) 기판용 할로겐프리 저열팽창 재료로, MGC 일본어 라인업 `hfbt.html` 의 "
        f"13등급 일반특성 일람표 중 한 열이다. "
        f"**라이브 DB 재료 97 `BT Resin` 과의 관계** — 97 은 같은 MGC 표(출처 306, 영문판 URL)에서 값을 가져온 **클래스 카드**인데, "
        f"밀도 2.1/2.0 · 영률 28/32 GPa · 인장강도 270/290 MPa 처럼 **HL832NX 와 HL832NSF 두 등급의 값을 등급 표시 없이 섞어** 담고 있다. "
        f"이 카드는 그 표의 **한 등급만**을 가리키는 등급 카드이므로 97 과 겹치지 않고 97 을 대체하지도 않는다."
        + (" 이 등급은 CCL 이 없는 프리프레그 전용 항목이다(원문 표의 銅張積層板 칸이 `-`)."
           if form == "ppg" else "")
    )
    return {
        "new_material": {
            "name": f"MGC {nm} (BT resin {'CCL' if form=='ccl' else 'prepreg'})",
            "category": "composite",
            "description": desc,
            "attributes": {
                "material_class": "BT resin copper-clad laminate" if form == "ccl" else "BT resin prepreg",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "스마트폰·반도체 패키지 기판의 실부품 적층재. 벤더 자체 데이터시트에 등급명으로 인쇄된 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Mitsubishi Gas Chemical Company, Inc.",
                "product_form": "copper-clad laminate" if form == "ccl" else "prepreg",
                "aliases": aliases,
                "related_material_ids": [97, 1276],
                "vendor_table_footnote": (
                    "표 하단에 `*2: 45umプリプレグの特性値を記載しております` 각주가 있으나 **표 안에 *2 앵커가 없다** — "
                    "HTML 의 `<sup>` 를 전수로 확인했고 전부 지수 표기(10^15-16, g/cm3, W/m*K)뿐이다. "
                    "GHPL-830SR 두 열이 프리프레그 전용이라 이 각주가 걸릴 가능성이 가장 높으나 문서가 확정하지 않는다."
                ),
            },
        },
        "source": SRC_MGC_BT,
        "properties": P,
    }

for r in BT:
    MATS.append(mgc_bt_card(r))

# ─────────────────────────────────────────────────────────────────────────────
# 2. MGC 고성능 FR-4 2등급 — fr4.html. 縦/横 를 가르고 ヤング率≠曲げ弾性率 인 표.
# ─────────────────────────────────────────────────────────────────────────────
SRC_MGC_FR4 = {
    "kind": "datasheet",
    "title": "多層プリント配線板用高性能FR-4材料 — CCL-EL190T / CCL-EL230T 一般特性一覧 (三菱ガス化学 製品ラインアップ)",
    "url": "https://www.mgc.co.jp/products/sc/btprint/lineup/fr4.html",
    "publisher": "Mitsubishi Gas Chemical Company, Inc.",
    "year": 2026,
    "local_path": f"{PCB}/MGC_CCL-EL190T-EL230T_FR4_Lineup_ja_2026-09-09.html",
}

FR4_E_NOTE = (
 "이 표는 `曲げ弾性率` 와 `ヤング率` 를 **다른 행으로 세우고 EL190T 에서 다른 숫자를 찍는다** "
 "(曲げ弾性率 縦27/横27 vs ヤング率 縦27/横26). 또 `引張強さ` 縦330/横330 과 `曲げ強さ` 縦580/横530 이 크게 달라 "
 "이 표가 인장·굽힘 두 시험을 실제로 나눠 돌린다는 증거다. 같은 벤더의 `lineup/led.html` 도 "
 "曲げ弾性率 23/22 vs ヤング率 25/24 로 두 행을 가른다. 따라서 이 표의 ヤング率 는 인장탄성률로 읽었다. "
 "**다만 이 페이지에도 시험규격 번호는 인쇄되어 있지 않다**(HTML 전문 `JIS`·`ASTM`·`IPC` 적중 0) — "
 "그래서 `conditions.test_standard` 를 비웠다."
)

FR4 = [
 # nm, dk(1M/1G/10G), df, flexS(t,y), flexE, uts, E, nu, tg(DMA,TMA,DSC), cte_xy, cte_z(a1,a2),
 # k, cp, td, t260/t288/t300, peel(12,18,18vlp)
 ("CCL-EL190T", (4.7, 4.3, 4.1), (0.010, 0.011, 0.012), (580, 530), (27, 27), (330, 330), (27, 26),
  (0.17, 0.16), (240, 220, 215), 14, (40, 180), 0.45, 0.95, 345, (60, 20, 7), (0.9, 1.2, 1.1), 1.44),
 ("CCL-EL230T", (4.0, 3.8, 3.6), (0.004, 0.005, 0.007), (470, 460), (22, 22), (300, 250), (22, 22),
  (0.16, 0.15), (210, 175, 175), 15, (45, 240), 0.44, 0.95, 335, (60, 12, 3), (0.9, 1.2, 1.1), 1.42),
]
ORI = ("warp", "fill")
ORI_JA = ("縦方向", "横方向")

for (nm, dk, df, flexS, flexE, uts, E, nu, tg, cte_xy, cte_z, k, cp, td, tdel, peel, resin_sg) in FR4:
    P = []
    def add(key, val, unit, tier=1, cond=None, notes="", method="measured"):
        if val is None: return
        p = {"key": key, "value": val, "unit": unit, "method": method, "tier": tier}
        if cond: p["conditions"] = cond
        p["notes"] = notes
        P.append(p)
    for i in range(2):
        add("mechanical.youngs_modulus", E[i] * GPa, "Pa", 1,
            {"test_mode": "tensile", "orientation": ORI[i], "conditioning": "A"},
            f"원문 verbatim: `ヤング率 | {ORI_JA[i]} | A | GPa | {E[i]}`. " + FR4_E_NOTE +
            f" 환산 {E[i]} x 1e9 = {E[i]*GPa:g} Pa; 되돌리면 {E[i]*GPa:g}/1e9 = {E[i]}. "
            f"경사(縦)·위사(横)는 두 행으로 갈랐고 평균 내지 않았다." +
            (" 이 등급은 縦·横 가 같은 숫자(22/22)지만, 같은 표의 EL190T 가 두 행을 가르므로 표 자체는 두 시험을 구분한다."
             if E[0] == E[1] else ""))
        add("mechanical.flexural_modulus", flexE[i] * GPa, "Pa", 1,
            {"test_mode": "flexural", "orientation": ORI[i], "conditioning": "A"},
            f"원문 verbatim: `曲げ弾性率 | {ORI_JA[i]} | A | GPa | {flexE[i]}`. 환산 x1e9 = {flexE[i]*GPa:g} Pa.")
        add("mechanical.flexural_strength", flexS[i] * MPa, "Pa", 1,
            {"orientation": ORI[i], "conditioning": "A"},
            f"원문 verbatim: `曲げ強さ | {ORI_JA[i]} | A | MPa | {flexS[i]}`. 환산 x1e6 = {flexS[i]*MPa:g} Pa.")
        add("mechanical.tensile_strength", uts[i] * MPa, "Pa", 1,
            {"orientation": ORI[i], "conditioning": "A"},
            f"원문 verbatim: `引張強さ | {ORI_JA[i]} | A | MPa | {uts[i]}`. 환산 x1e6 = {uts[i]*MPa:g} Pa. "
            f"굽힘강도 {flexS[i]} MPa 와 크게 달라 인장시험이 별도로 돌아간다.")
        add("mechanical.poisson_ratio", nu[i], "1", 1,
            {"orientation": ORI[i], "conditioning": "A"},
            f"원문 verbatim: `ポアソン比 | {ORI_JA[i]} | A | － | {nu[i]}`. 무차원, 환산 없음. "
            f"**포아송비를 방향별로 찍는 흔치 않은 표다** — 縦{nu[0]}/横{nu[1]} 를 평균 내지 않고 두 행으로 갈랐다. "
            f"MGC 는 이 FR-4 쪽을 `ポアソン比`, BT 쪽을 `ポアッソン比` 로 달리 표기한다.")
    add("thermal.conductivity", k, "W/(m*K)", 1,
        {"test_method": "laser flash (レーザーフラッシュ法)", "conditioning": "A"},
        f"원문 verbatim: `熱伝導率 | レーザー フラッシュ法 | A | W/m・K | {k}`. 단위가 이미 SI 라 환산 없음.")
    add("thermal.specific_heat", cp * 1000, "J/(kg*K)", 1,
        {"test_method": "DSC", "conditioning": "A"},
        f"원문 verbatim: `比熱 | DSC | A | J/g・K | {cp}`. 환산 {cp} x 1000 g/kg = {cp*1000:g} J/(kg*K).")
    add("thermal.expansion_linear", ppm(cte_xy), "1/K", 1, {"axis": "in-plane (縦、横方向)", "conditioning": "A"},
        f"원문 verbatim: `熱膨張係数 | 縦、横方向 | A | ppm/℃ | {cte_xy}`. **원문이 경사·위사를 한 값으로 묶어 찍는다** — "
        f"쪼개지 않았다. 환산 {cte_xy} x 1e-6 = {ppm(cte_xy):g} 1/K.")
    for lbl, v in zip(("alpha1", "alpha2"), cte_z):
        add("thermal.expansion_linear", ppm(v), "1/K", 1, {"axis": "Z", "regime": lbl, "conditioning": "A"},
            f"원문 verbatim: `熱膨張係数 | Z （α1、α2） | A | ppm/℃ | {cte_z[0]}/{cte_z[1]}`. "
            f"한 칸에 `/` 로 두 값이 들어 있어 α1·α2 두 행으로 갈랐다. 환산 {v} x 1e-6 = {ppm(v):g} 1/K.")
    for meth, v in zip(("DMA", "TMA", "DSC"), tg):
        add("thermal.glass_transition", C2K(v), "K", 1, {"method_detail": meth, "conditioning": "A"},
            f"원문 verbatim: `ガラス転移温度 | {meth} | A | ℃ | {v}`. 환산 {v} + 273.15 = {C2K(v)} K. "
            f"세 측정법을 세 행으로 갈랐고 평균 내지 않았다.")
    add("thermal.decomposition_temp", C2K(td), "K", 1, {"test_method": "TG-DTA", "conditioning": "A"},
        f"원문 verbatim: `熱分解温度 | TG-DTA | A | ℃ | {td}`. 환산 {td} + 273.15 = {C2K(td)} K.")
    for lbl, v in zip(("T-260", "T-288", "T-300"), tdel):
        add("thermal.time_to_delamination", v * 60, "s", 1,
            {"test_label": lbl, "conditioning": "E-2/105",
             **({"bound": "lower"} if lbl == "T-260" else {})},
            f"원문 verbatim: `Time to Delamination | {lbl} | E-2/105 | minutes | " +
            ("＞60" if lbl == "T-260" else str(v)) + "`. " +
            ("원문이 `＞60` 부등호라 하한 한 행으로만 넣었다. " if lbl == "T-260" else "") +
            f"환산 {v} min x 60 s/min = {v*60} s.")
    for th, v in zip((12, 18, "18-VLP"), peel):
        add("interface.peel_strength", v * kNm, "N/m", 1,
            {"copper_foil": f"{th} um" if th != "18-VLP" else "18 um VLP", "conditioning": "A"},
            f"원문 verbatim: `ピール強度 | {th}μ | A | KN/m | {v}`. 환산 {v} x 1000 = {v*kNm:g} N/m.")
    for f_, v in zip(("1 MHz", "1 GHz", "10 GHz"), dk):
        add("electrical.dielectric_constant", v, "1", 1, {"frequency": f_, "conditioning": "A"},
            f"원문 verbatim: `比誘電率 | {f_.replace(' ','')} | A | － | {v}`. 무차원.")
    for f_, v in zip(("1 MHz", "1 GHz", "10 GHz"), df):
        add("electrical.dissipation_factor", v, "1", 1, {"frequency": f_, "conditioning": "A"},
            f"원문 verbatim: `誘電正接 | {f_.replace(' ','')} | A | － | {v}`. 무차원.")
    add("thermal.flammability_ul94", "V-0", None, 1, {"conditioning": "E-168/70"},
        "원문 verbatim: `耐燃性 | UL94 | E-168/70 | － | V-0`.")

    g = nm.replace("CCL-", "")
    MATS.append({
        "new_material": {
            "name": f"MGC {nm} (high-performance FR-4 CCL)",
            "category": "composite",
            "description": (
                f"미쓰비시가스화학(MGC) 다층 프린트배선판용 고성능 FR-4 동장적층판 `{nm}`(대응 프리프레그 "
                f"`{'GEPL-190T' if g=='EL190T' else 'GEPL-230T'}`). MGC 일본어 라인업 `fr4.html` 의 2등급 일반특성 일람표 한 열이다. "
                f"**이 표는 MGC 표들 중 조건이 가장 잘 갈린 것이다** — 시험조건 열(`A`)과 경사/위사(縦/横)를 모두 찍고, "
                f"포아송비까지 방향별로 인쇄한다(EL190T 縦0.17/横0.16). "
                f"라이브 DB 재료 97 `BT Resin` 은 MGC 의 **BT 계열** 클래스 카드이고 이 등급은 **FR-4 계열**이라 계통이 다르다 — 겹치지 않는다. "
                f"밀도는 이 표에 없다: 인쇄된 것은 `樹脂比重 {resin_sg}` 로 **수지만의 비중**이지 적층판 밀도가 아니라서 옮기지 않았다."
            ),
            "attributes": {
                "material_class": "high-performance FR-4 copper-clad laminate",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "다층 PCB 실부품 적층재. 벤더 데이터시트에 등급명으로 인쇄된 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Mitsubishi Gas Chemical Company, Inc.",
                "product_form": "copper-clad laminate",
                "prepreg_grade": "GEPL-190T" if g == "EL190T" else "GEPL-230T",
                "aliases": [nm, nm.replace("-", ""), nm.replace("CCL-", ""), g, f"CCL {g}", f"MGC {g}"],
                "resin_specific_gravity_printed": resin_sg,
                "density_absent_reason": (
                    f"표에 적층판 밀도 행이 없다. 있는 것은 `樹脂比重 | A | － | {resin_sg}` 로 **무차원 수지 비중**이며 "
                    f"이것을 x1000 해 적층판 밀도로 쓰는 것은 역산이라 하지 않았다."
                ),
            },
        },
        "source": SRC_MGC_FR4,
        "properties": P,
    })

# ─────────────────────────────────────────────────────────────────────────────
# 3. MGC Chip-LED 용 BT — led.html. ヤング率≠曲げ弾性率 를 증명하는 열쇠 문서.
# ─────────────────────────────────────────────────────────────────────────────
SRC_MGC_LED = {
    "kind": "datasheet",
    "title": "Chip-LED用BT材料 — CCL-HL820WDI 一般特性一覧 (三菱ガス化学 製品ラインアップ)",
    "url": "https://www.mgc.co.jp/products/sc/btprint/lineup/led.html",
    "publisher": "Mitsubishi Gas Chemical Company, Inc.",
    "year": 2026,
    "local_path": f"{PCB}/MGC_CCL-HL820WDI_ChipLED_BT_Lineup_ja_2026-09-09.html",
}
P = []
def addL(key, val, unit, tier=1, cond=None, notes=""):
    p = {"key": key, "value": val, "unit": unit, "method": "measured", "tier": tier}
    if cond: p["conditions"] = cond
    p["notes"] = notes
    P.append(p)
LED_E = (25, 24); LED_FE = (23, 22); LED_UTS = (290, 280); LED_FS = (480, 470)
for i in range(2):
    addL("mechanical.youngs_modulus", LED_E[i] * GPa, "Pa", 1,
         {"test_mode": "tensile", "orientation": ORI[i], "conditioning": "A"},
         f"원문 verbatim: `ヤング率 | {ORI_JA[i]} | A | GPa | {LED_E[i]}`. "
         f"**이 표가 MGC 의 `ヤング率` 행이 굽힘이 아님을 증명하는 열쇠다** — 같은 표의 "
         f"`曲げ弾性率 縦23/横22` 와 `ヤング率 縦25/横24` 가 **다른 숫자**다. "
         f"환산 {LED_E[i]} x 1e9 = {LED_E[i]*GPa:g} Pa; 되돌리면 {LED_E[i]*GPa:g}/1e9 = {LED_E[i]}. "
         f"시험규격 번호는 이 페이지에도 인쇄되지 않았다.")
    addL("mechanical.flexural_modulus", LED_FE[i] * GPa, "Pa", 1,
         {"test_mode": "flexural", "orientation": ORI[i], "conditioning": "A"},
         f"원문 verbatim: `曲げ弾性率 | {ORI_JA[i]} | A | GPa | {LED_FE[i]}`. 환산 x1e9 = {LED_FE[i]*GPa:g} Pa.")
    addL("mechanical.tensile_strength", LED_UTS[i] * MPa, "Pa", 1,
         {"orientation": ORI[i], "conditioning": "A"},
         f"원문 verbatim: `引張強さ | {ORI_JA[i]} | A | MPa | {LED_UTS[i]}`. 환산 x1e6 = {LED_UTS[i]*MPa:g} Pa.")
    addL("mechanical.flexural_strength", LED_FS[i] * MPa, "Pa", 1,
         {"orientation": ORI[i], "conditioning": "A"},
         f"원문 verbatim: `曲げ強さ | {ORI_JA[i]} | A | MPa | {LED_FS[i]}`. 환산 x1e6 = {LED_FS[i]*MPa:g} Pa.")
addL("thermal.expansion_linear", ppm(15), "1/K", 1, {"axis": "in-plane (縦、横方向)", "conditioning": "A"},
     "원문 verbatim: `熱膨張係数 | 縦、横方向 | A | ppm/℃ | 15`. 환산 15 x 1e-6 = 1.5e-05 1/K.")
for lbl, v in zip(("alpha1", "alpha2"), (45, 180)):
    addL("thermal.expansion_linear", ppm(v), "1/K", 1, {"axis": "Z", "regime": lbl, "conditioning": "A"},
         f"원문 verbatim: `熱膨張係数 | Z(α1, α2) | A | ppm/℃ | 45/180`. 한 칸의 `/` 를 두 행으로 갈랐다. 환산 {v} x 1e-6 = {ppm(v):g} 1/K.")
for meth, v in zip(("DMA", "TMA"), (210, 180)):
    addL("thermal.glass_transition", C2K(v), "K", 1, {"method_detail": meth, "conditioning": "A"},
         f"원문 verbatim: `ガラス転移温度 | {meth} | A | ℃ | {v}`. 환산 {v} + 273.15 = {C2K(v)} K.")
for th, v in zip((12, 18), (1.0, 1.1)):
    addL("interface.peel_strength", v * kNm, "N/m", 1, {"copper_foil": f"{th} um", "conditioning": "A"},
         f"원문 verbatim: `ピール強度 | {th}µ | A | KN/m | {v}`. 환산 x1000 = {v*kNm:g} N/m.")
addL("electrical.dielectric_constant", 5.7, "1", 1, {"frequency": "1 GHz", "conditioning": "A"},
     "원문 verbatim: `比誘電率 | 1GHz | A | － | 5.7`. 1MHz 칸은 `－`(값 없음)이라 넣지 않았다.")
addL("electrical.dissipation_factor", 0.020, "1", 1, {"frequency": "1 GHz", "conditioning": "A"},
     "원문 verbatim: `誘電正接 | 1GHz | A | － | 0.020`. 1MHz 칸은 `－`.")
addL("thermal.flammability_ul94", "HB", None, 1, {"conditioning": "E-168/70"},
     "원문 verbatim: `耐燃性 | UL94 | E-168/70 | － | HB`. 이 등급만 V-0 가 아니라 HB 다.")
MATS.append({
    "new_material": {
        "name": "MGC CCL-HL820WDI (Chip-LED BT resin CCL)",
        "category": "composite",
        "description": (
            "미쓰비시가스화학(MGC) Chip-LED 용 BT 수지 동장적층판 `CCL-HL820WDI`. MGC 일본어 라인업 `led.html` 의 단일 등급 표다. "
            "**이 카드는 카탈로그 전체에서 판정 근거로도 쓰인다** — 같은 MGC 표 서식에서 `曲げ弾性率 縦23/横22` 와 "
            "`ヤング率 縦25/横24` 가 다른 숫자라, MGC 의 `ヤング率` 행이 굽힘 값의 복사가 아님을 보여 준다. "
            "라이브 DB 재료 97 `BT Resin` 은 MGC BT 계열의 클래스 카드이고 이 카드는 그 계열의 한 등급이다 — 값이 겹치지 않는다("
            "97 이 담은 값은 HL832NX·HL832NSF 의 것이다). "
            "밀도·비열·열전도율·포아송비는 이 표에 열 자체가 없다."
        ),
        "attributes": {
            "material_class": "BT resin copper-clad laminate (Chip-LED grade)",
            "subsystem": "pcb",
            "role": "product",
            "role_reason": "Chip-LED 패키지 기판 실부품 적층재. 벤더 데이터시트에 등급명으로 인쇄된 제품이다.",
            "role_confidence": "high",
            "manufacturer": "Mitsubishi Gas Chemical Company, Inc.",
            "product_form": "copper-clad laminate",
            "aliases": ["CCL-HL820WDI", "CCLHL820WDI", "HL820WDI", "HL-820WDI", "HL820 WDI", "MGC HL820WDI"],
            "related_material_ids": [97, 1276],
        },
    },
    "source": SRC_MGC_LED,
    "properties": P,
})

# ─────────────────────────────────────────────────────────────────────────────
# 4. Sumitomo Bakelite Sumilite ELC 6등급
# ─────────────────────────────────────────────────────────────────────────────
SRC_SB_DS = {
    "kind": "datasheet",
    "title": "エポキシ樹脂両面プリント配線板用材料 スミライト®ELC 仕様一覧 (住友ベークライト)",
    "url": None,
    "url_note": (
        "저장된 HTML 에 절대 URL 이 남아 있지 않다(`og:url`·canonical 없음, href 는 `/common/css/...`·`/index.html` 뿐). "
        "69차 EB 가 이 페이지를 Sumitomo Bakelite 사이트의 ELC `spec/index.html` 로 적었으나 **URL 을 지어내지 않았다** — "
        "로컬 원문이 근거다."
    ),
    "publisher": "Sumitomo Bakelite Co., Ltd.",
    "year": 2026,
    "local_path": f"{PCB}/SumitomoBakelite_Sumilite_ELC_DoubleSided_CCL_Spec_ja_2026-09-09.html",
}
SRC_SB_ML = dict(SRC_SB_DS)
SRC_SB_ML.update({
    "title": "エポキシ樹脂多層プリント配線板用材料 スミライト®ELC 仕様一覧 (住友ベークライト)",
    "local_path": f"{PCB}/SumitomoBakelite_Sumilite_ELC_Multilayer_PWB_Spec_ja_2026-09-09.html",
})

SB_TYPICAL = ("표 하단 각주 verbatim: `※ 上表のデータは代表値であり、保証値ではありません`(대표값이며 보증값이 아니다).")
SB_E_NOTE = (
 "Sumitomo 는 `曲げ弾性率` 와 `引っ張り弾性率` 를 **행 이름부터 갈라서** 찍고 대부분 등급에서 다른 숫자를 낸다"
 "(ELC-4970 굽힘 タテ18/ヨコ16 vs 인장 タテ14/ヨコ12). 행 이름이 명시적 인장이므로 시험모드는 확정이다. "
 "**시험규격 번호는 이 페이지에 인쇄되지 않았다**(HTML 전문 `JIS`·`ASTM`·`IPC` 적중 0) — 인쇄된 것은 처리조건 코드 `A` 뿐이다. "
 "`引張強さ` 로만 grep 하면 이 벤더의 `引っ張り強さ`(っ 있음)를 놓친다."
)
ORI_SB = ("warp (タテ)", "fill (ヨコ)")
ORI_SB_JA = ("タテ", "ヨコ")

# nm, sheet(FR-4/CEM-3), flexS(t,y), flexE(t,y), uts(t,y), E(t,y),
# cte(x,y,z1,z2), tg(TMA,DMA,DSC), peel(A, S-20/260), dk(1M,1G), df(1M,1G), wa, wa_cond, ul, k, src, tens_thk
ELC = [
 ("ELC-4762 / ELC-4756", "FR-4", (539, 470), (16, 15), (260, 260), (15, 15),
  (14, 16, 65, 270), (135, 150, 145), (1.5, 1.5), (4.7, 4.5), (0.018, 0.014), 0.10,
  "E-24/50 + D-24/23", "94V-0", 0.40, "ds", None),
 ("ELC-4970", "CEM-3", (350, 300), (18, 16), (160, 100), (14, 12),
  (20, 24, 47, 300), (125, 150, 130), (1.4, 1.4), (4.5, 4.1), (0.020, 0.018), 0.09,
  "E-24/50 + D-24/23", "94V-0", 0.70, "ds", None),
 ("ELC-4972R&S", "CEM-3", (350, 300), (18, 16), (160, 100), (14, 12),
  (20, 24, 47, 300), (125, 150, 110), (1.4, 1.4), (4.5, 4.1), (0.020, 0.018), 0.09,
  "E-24/50 + D-24/23", "94-0", 1.00, "ds", None),
 ("ELC-4970GS", "CEM-3", (350, 300), (19, 19), (130, 90), (14, 12),
  (20, 24, 47, 300), (120, 140, 110), (1.5, 1.5), (4.5, 4.4), (0.020, 0.018), 0.09,
  "E-24/50 + D-24/23", "94-0", 1.00, "ds", None),
 ("ELC-4765", "FR-4.0", (620, 460), (16, 15), (260, 250), (16, 15),
  (14, 16, 65, 270), (135, 150, 145), (1.4, 1.3), (4.7, 4.5), (0.018, 0.014), 0.10,
  "E-24/40/90", "94V-0", 0.40, "ml", 0.1),
 ("ELC-4768", "FR-4.0", (640, 480), (18, 16), (330, 250), (16, 15),
  (14, 16, 45, 250), (125, 150, 135), (1.0, 1.0), (5.5, 4.8), (0.014, 0.015), 0.10,
  "E-24/40/90", "94V-0", 0.68, "ml", 0.1),
]

for (nm, sheet, flexS, flexE, uts, E, cte, tg, peel, dk, df, wa, wa_cond, ul, k, which, tens_thk) in ELC:
    src = SRC_SB_DS if which == "ds" else SRC_SB_ML
    P = []
    def addS(key, val, unit, tier=1, cond=None, notes=""):
        p = {"key": key, "value": val, "unit": unit, "method": "measured", "tier": tier}
        if cond: p["conditions"] = cond
        p["notes"] = notes
        P.append(p)
    thk_note = ""
    thk_cond = {}
    if tens_thk:
        thk_note = (" 이 행에는 `※` 가 붙어 있고 각주가 `※0.1mmtで測定`(0.1 mm 두께로 측정)이라 조건에 박았다.")
        thk_cond = {"specimen_thickness_mm": tens_thk}
    for i in range(2):
        addS("mechanical.youngs_modulus", E[i] * GPa, "Pa", 1,
             {"test_mode": "tensile", "orientation": ORI_SB[i], "conditioning": "A", **thk_cond},
             f"원문 verbatim: `{'引っ張り弾性率※' if tens_thk else '引っ張り弾性率'} | {ORI_SB_JA[i]} | A | GPa | {E[i]}`. "
             + SB_E_NOTE + thk_note +
             f" 환산 {E[i]} x 1e9 = {E[i]*GPa:g} Pa; 되돌리면 {E[i]*GPa:g}/1e9 = {E[i]}. "
             f"タテ(경사)·ヨコ(위사)를 두 행으로 갈랐고 평균 내지 않았다. " + SB_TYPICAL)
        addS("mechanical.tensile_strength", uts[i] * MPa, "Pa", 1,
             {"orientation": ORI_SB[i], "conditioning": "A", **thk_cond},
             f"원문 verbatim: `{'引っ張り強さ※' if tens_thk else '引っ張り強さ'} | {ORI_SB_JA[i]} | A | MPa | {uts[i]}`. "
             f"굽힘강도 {flexS[i]} MPa 와 크게 달라 인장시험이 별도로 돌아간다." + thk_note +
             f" 환산 {uts[i]} x 1e6 = {uts[i]*MPa:g} Pa. " + SB_TYPICAL)
        addS("mechanical.flexural_modulus", flexE[i] * GPa, "Pa", 1,
             {"test_mode": "flexural", "orientation": ORI_SB[i], "conditioning": "A"},
             f"원문 verbatim: `曲げ弾性率 | {ORI_SB_JA[i]} | A | GPa | {flexE[i]}`. 환산 x1e9 = {flexE[i]*GPa:g} Pa. " + SB_TYPICAL)
        addS("mechanical.flexural_strength", flexS[i] * MPa, "Pa", 1,
             {"orientation": ORI_SB[i], "conditioning": "A"},
             f"원문 verbatim: `曲げ強さ | {ORI_SB_JA[i]} | A | MPa | {flexS[i]}`. 환산 x1e6 = {flexS[i]*MPa:g} Pa. " + SB_TYPICAL)
    for lbl, axis, v in (("alpha1", "X", cte[0]), ("alpha1", "Y", cte[1]),
                         ("alpha1", "Z", cte[2]), ("alpha2", "Z", cte[3])):
        z2 = (axis == "Z" and lbl == "alpha2")
        addS("thermal.expansion_linear", ppm(v), "1/K", 1,
             {"axis": axis, "regime": lbl, "heating_rate_c_per_min": 10},
             f"원문 verbatim: `熱膨張係数 | CTE {axis}({'α2' if z2 else 'α1'}) | 10℃/min | ppm/℃ | {v}`. "
             f"X({cte[0]})·Y({cte[1]}) 를 벤더가 따로 찍어 두 행으로 갈랐다 — 평균 내지 않았다. "
             f"환산 {v} x 1e-6 = {ppm(v):g} 1/K. " +
             ("**주의 — 이 다층 PWB 페이지는 Z 축 두 행 이름을 `CTE Z (α1)` 로 두 번 인쇄한다(원문 오식).** "
              "형제 페이지(양면 CCL)가 같은 자리를 `CTE Z(α1)`·`CTE Z(α2)` 로 찍고 값 크기(65->270)도 같은 꼴이라 "
              "두 번째 행을 α2 로 읽었다. 원문 표기는 α1 임을 여기에 남긴다."
              if (z2 and which == "ml") else "") + " " + SB_TYPICAL)
    for meth, v in zip(("TMA", "DMA", "DSC"), tg):
        rate = {"TMA": 10, "DMA": 5, "DSC": 20}[meth]
        addS("thermal.glass_transition", C2K(v), "K", 1,
             {"method_detail": meth, "heating_rate_c_per_min": rate},
             f"원문 verbatim: `ガラス転移温度 | {meth} | {rate}℃/min | ℃ | {v}`. 환산 {v} + 273.15 = {C2K(v)} K. "
             f"세 측정법을 세 행으로 갈랐다. " + SB_TYPICAL)
    addS("thermal.conductivity", k, "W/(m*K)", 1,
         {"test_method": "laser flash (レーザーフラッシュ法)"},
         f"원문 verbatim: `熱伝導率 | レーザーフラッシュ法 | W/mk | {k}`. 단위가 이미 SI 라 환산 없음. " + SB_TYPICAL)
    for lbl, v in zip(("A", "S-20\"/260"), peel):
        addS("interface.peel_strength", v * kNm, "N/m", 1,
             {"copper_foil": "18 um", "conditioning": lbl},
             f"원문 verbatim: `引き剥がし強さ | 銅箔18㎛ | {lbl} | kN/m | {v}`. 환산 {v} x 1000 = {v*kNm:g} N/m. " + SB_TYPICAL)
    for f_, v in zip(("1 MHz", "1 GHz"), dk):
        addS("electrical.dielectric_constant", v, "1", 1, {"frequency": f_, "conditioning": "C-96/20/65" if which == "ds" else "A"},
             f"원문 verbatim: `比誘電率 | {f_.replace(' ','')} | － | {v}`. 무차원. " + SB_TYPICAL)
    for f_, v in zip(("1 MHz", "1 GHz"), df):
        addS("electrical.dissipation_factor", v, "1", 1, {"frequency": f_, "conditioning": "C-96/20/65" if which == "ds" else "A"},
             f"원문 verbatim: `誘電正接 | {f_.replace(' ','')} | － | {v}`. 무차원. " + SB_TYPICAL)
    addS("chemical.water_absorption_saturation", pct(wa), "1", 1, {"conditioning": wa_cond},
         f"원문 verbatim: `吸水率 | {wa_cond} | % | {wa}`. 환산 {wa}% / 100 = {pct(wa):g}. " + SB_TYPICAL)
    addS("thermal.flammability_ul94", ul, None, 1, None,
         f"원문 verbatim: `耐燃性 | UL-94V | - | {ul}`.")

    base = nm.split(" / ")[0]
    al = set()
    for g in nm.split(" / "):
        al |= {g, g.replace("-", ""), g.replace("-", " "), g.replace("ELC-", ""), "Sumilite " + g, "スミライト " + g}
    MATS.append({
        "new_material": {
            "name": f"Sumitomo Bakelite Sumilite {nm} ({sheet} CCL)",
            "category": "composite",
            "description": (
                f"스미토모베이크라이트 에폭시계 프린트배선판용 동장적층판 `스미라이트(Sumilite) {nm}`, 규격 계열 {sheet}"
                + (" (UV type)" if nm != "ELC-4768" else "") + ". "
                + ("양면 프린트배선판용 사양표" if which == "ds" else "다층 프린트배선판용 사양표") + "의 한 열이다. "
                "이 벤더 표의 값어치는 **`曲げ弾性率`(굽힘)와 `引っ張り弾性率`(인장)를 방향별로 따로 찍는다**는 데 있다 — "
                "굽힘이 인장보다 높게 나오는 것(FR-4 등급 16 vs 15, CEM-3 등급 18/16 vs 14/12)까지 그대로 보인다. "
                "라이브 DB 에 ELC 계열 카드는 하나도 없었다(69차 EB 가 '이 배치 최대의 손실'로 적은 항목). "
                "밀도·포아송비·비열은 이 표에 열 자체가 없다."
            ),
            "attributes": {
                "material_class": f"{sheet} copper-clad laminate (epoxy)",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "프린트배선판 실부품 적층재. 벤더 사양표에 등급명으로 인쇄된 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Sumitomo Bakelite Co., Ltd.",
                "brand": "Sumilite (スミライト)",
                "product_form": "copper-clad laminate",
                "ipc_sheet_class": sheet,
                "aliases": sorted(al),
                "combined_column_note": (
                    "원문 열 머리가 `ELC-4762/4756 (UV type)` 로 두 등급을 한 칸에 묶는다 — "
                    "표가 두 등급을 가르지 않으므로 카드도 가르지 않고 한 장으로 세웠다."
                    if " / " in nm else None
                ),
            },
        },
        "source": src,
        "properties": P,
    })

# ─────────────────────────────────────────────────────────────────────────────
# 5. Resonac MCL 계열 — 2023-2024 일본어 총합 카탈로그 p5(印刷 6)·p6(印刷 7)
#    인쇄된 구간은 전부 두 행(lower/upper)으로 가른다.
# ─────────────────────────────────────────────────────────────────────────────
SRC_RES = {
    "kind": "datasheet",
    "title": "MCL 一般特性一覧 — 銅張積層板 総合カタログ 2023-2024 (レゾナック)",
    "url": None,
    "url_note": (
        "PDF 메타(CubePDF/iTextSharp)에 원 URL 이 없고 저장 시점 URL 이 파일에 남아 있지 않다. **URL 을 지어내지 않았다** — "
        "로컬 원문(66쪽)이 근거다. 69차 EB 가 코퍼스에 넣은 파일이다."
    ),
    "publisher": "Resonac Corporation (구 Showa Denko Materials / Hitachi Chemical)",
    "year": 2024,
    "local_path": f"{PCB}/Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf",
}

RES_SPLIT = (
 "Resonac 는 `弾性率(引張モード)` 와 `弾性率(曲げモード)` 를 **행 이름에 시험모드를 박아 따로** 찍는다 — "
 "이 등급도 인장 {t} GPa vs 굽힘 {f} 로 다르다. 시험모드 확정이다. "
 "**인쇄된 것이 구간이라 평균 내지 않고 하한·상한 두 행으로 갈랐다.** "
 "쪽 각주 verbatim: `*1: 空洞共振器; *2: RT箔; *3: HVLP箔, *4: 0.8 mmt; *5: 引張` — "
 "`弾性率(引張モード) X` 에는 각주 번호가 없고 `弾性率(曲げモード) X` 에만 `*4`(0.8 mmt)가 붙는다. "
 "그래서 인장탄성률의 시편 두께는 표 맨 위 `厚み {thk} mm` 다."
)

# nm, page(pdf), thickness_mm, glass, E_t(lo,hi), E_f(lo,hi)|None, tgTMA, tgDMA, ctex, ctey,
# ctez1, ctez2, ctez_dic|None, k(lo,hi)|None, dk1(lo,hi), dk10, df1, df10, peel12, peel18|None, slash
RES = [
 ("MCL-E-795G", 5, 0.2, "E-glass", (26, 28), (35, 37), (260, 290), (315, 345), (7, 9), (7, 9),
  (10, 15), (70, 100), 8.5, (0.55, 0.75), (4.3, 4.5), (4.3, 4.5), (0.005, 0.007), (0.006, 0.008),
  (0.8, 1.0), (0.9, 1.1), "42"),
 ("MCL-E-795G (LH type)", 5, 0.2, "S-glass (H.D.)", (31, 33), (40, 42), (260, 290), (315, 345), (4.5, 6.5), (4.5, 6.5),
  (10, 15), (70, 100), 5.5, (0.55, 0.75), (4.1, 4.3), (4.1, 4.3), (0.005, 0.007), (0.006, 0.008),
  (0.8, 1.0), (0.9, 1.1), "N/A (S-glass)"),
 ("MCL-E-705G", 5, 0.2, "E-glass", (20, 22), (32, 34), (250, 270), (295, 305), (8.5, 10.5), (8.5, 10.5),
  (10, 15), (70, 100), 9.6, (0.55, 0.75), (4.4, 4.6), (4.4, 4.6), (0.007, 0.009), (0.009, 0.011),
  (0.8, 1.0), (0.9, 1.1), "42"),
 ("MCL-E-705G (L type)", 5, 0.2, "S-glass", (22, 24), (34, 36), (250, 270), (295, 305), (6, 8), (6, 8),
  (10, 15), (70, 100), 7.0, (0.55, 0.75), (4.1, 4.3), (4.1, 4.3), (0.007, 0.009), (0.009, 0.011),
  (0.8, 1.0), (0.9, 1.1), "N/A (S-glass)"),
 ("MCL-E-705G (LH type)", 5, 0.2, "S-glass (H.D.)", (23, 25), (37, 39), (250, 270), (295, 305), (6, 8), (6, 8),
  (10, 15), (70, 100), 6.9, (0.55, 0.75), (4.1, 4.3), (4.1, 4.3), (0.007, 0.009), (0.009, 0.011),
  (0.8, 1.0), (0.9, 1.1), "N/A (S-glass)"),
 ("MCL-E-700G (R type)", 5, 0.2, "E-glass", (20, 22), (32, 34), (250, 270), (295, 305), (11, 13), (11, 13),
  (15, 25), (90, 120), 13.1, (0.60, 0.80), (4.7, 4.9), (4.6, 4.8), (0.008, 0.010), (0.008, 0.010),
  (0.9, 1.1), (1.0, 1.2), "42"),
 ("MCL-E-770G (R type)", 5, 0.2, "E-glass", (18, 20), (30, 32), (260, 280), (300, 330), (7, 9), (7, 9),
  (10, 15), (70, 100), None, (0.55, 0.75), (4.3, 4.5), (4.2, 4.4), (0.005, 0.007), (0.006, 0.008),
  (0.7, 0.9), (0.8, 1.0), "42"),
 ("MCL-E-770G (RLH type)", 5, 0.2, "S-glass (H.D.)", (20, 22), (34, 36), (260, 280), (300, 330), (5, 7), (5, 7),
  (10, 15), (70, 100), None, (0.55, 0.75), (4.0, 4.2), (3.9, 4.1), (0.005, 0.007), (0.006, 0.008),
  (0.7, 0.9), (0.8, 1.0), "N/A (S-glass)"),
 ("MCL-E-679FG (R type)", 6, 0.2, "E-glass", (20, 26), (23, 28), (165, 175), (200, 220), (13, 15), (13, 15),
  (23, 33), (140, 170), None, (0.79, 0.83), (4.6, 4.8), None, (0.016, 0.018), None,
  (0.8, 1.0), (0.9, 1.1), "128,130"),
 ("MCL-E-679FG (S type)", 6, 0.2, "E-glass", (21, 27), (24, 29), (175, 185), (210, 230), (12, 14), (12, 14),
  (20, 30), (130, 160), None, (0.79, 0.83), (4.6, 4.8), None, (0.016, 0.018), None,
  (0.9, 1.1), (1.0, 1.2), "128,130"),
]

RENDER_NOTE = {
 5: ("열 밀림 확인 — PDF 5쪽(印刷 6)을 350 dpi 로 렌더해 눈으로 대조했다. `pdftotext -layout` 의 8개 열 머리와 "
     "렌더의 열 머리가 자리까지 일치한다(MCL-E-795G / MCL-E-795G(LH) / MCL-E-705G / MCL-E-705G(L) / MCL-E-705G(LH) / "
     "MCL-E-700G(R) / MCL-E-770G(R) / MCL-E-770G(RLH))."),
 6: ("**열 밀림 확인 — 이 쪽은 렌더가 실제로 오독을 잡았다.** PDF 6쪽(印刷 7)의 `pdftotext -layout` 출력은 오른쪽 "
     "세로 탭(`ＭＣＬ用途別推奨品種一覧` 등)을 본문 사이에 끼워 넣어 열 머리 두 줄을 "
     "`MCL-E-679FG MCL-E-679FG MCL-HS200 MCL-HS200 MCL-HS100` / `GEA-705G GEA-770G (R タイプ) (S タイプ) (D タイプ)` 로 "
     "쪼개 놓는다 — 그대로 읽으면 GEA-705G 에 `(R タイプ)` 가 붙는다. 350 dpi 렌더로 실제 열 순서가 "
     "`GEA-705G | GEA-770G | MCL-E-679FG(R) | MCL-E-679FG(S) | MCL-HS200 | MCL-HS200(D) | MCL-HS100` 임을 확인하고 "
     "그 순서로만 값을 옮겼다."),
}

def rng(P, key, unit, lo, hi, cond, note_base, conv=lambda x: x, fmt="{}"):
    for b, v in (("lower", lo), ("upper", hi)):
        c = dict(cond); c["bound"] = b
        P.append({"key": key, "value": conv(v), "unit": unit, "method": "measured", "tier": 1,
                  "conditions": c,
                  "notes": note_base + f" 이 행은 인쇄 구간의 **{'하한' if b=='lower' else '상한'}** {v} 이다 — "
                                       f"두 행으로 갈랐고 평균 내지 않았다."})

for (nm, pg, thk, glass, Et, Ef, tgT, tgD, cx, cy, cz1, cz2, cz_dic, k, dk1, dk10, df1, df10,
     p12, p18, slash) in RES:
    P = []
    base = f"출처: 레조낙 `MCL一般特性一覧` 표, PDF {pg}쪽(印刷 {pg+1}쪽), 열 `{nm}`. " + RENDER_NOTE[pg]
    rng(P, "mechanical.youngs_modulus", "Pa", Et[0], Et[1],
        {"test_mode": "tensile", "orientation": "X", "specimen_thickness_mm": thk},
        f"원문 verbatim: `弾性率(引張モード) X | GPa | {Et[0]} - {Et[1]}`. "
        + RES_SPLIT.format(t=f"{Et[0]}-{Et[1]}", f=f"{Ef[0]}-{Ef[1]}", thk=thk)
        + f" 환산 GPa x 1e9 -> Pa; 되돌리면 {Et[0]*GPa:g}/1e9 = {Et[0]}, {Et[1]*GPa:g}/1e9 = {Et[1]}. " + base,
        conv=lambda v: v * GPa)
    rng(P, "mechanical.flexural_modulus", "Pa", Ef[0], Ef[1],
        {"test_mode": "flexural", "orientation": "X", "specimen_thickness_mm": 0.8},
        f"원문 verbatim: `弾性率(曲げモード) X*4 | GPa | {Ef[0]} - {Ef[1]}`. 각주 `*4: 0.8 mmt` 가 이 행에만 붙어 "
        f"시편 두께가 0.8 mm 다(표 맨 위 `厚み` 는 {thk} mm). 환산 x1e9 -> Pa. " + base,
        conv=lambda v: v * GPa)
    for axis, c in (("X", cx), ("Y", cy)):
        rng(P, "thermal.expansion_linear", "1/K", c[0], c[1],
            {"axis": axis, "regime": "alpha1 (<Tg)", "test_mode": "compression (圧縮)"},
            f"원문 verbatim: `CTE {axis.lower()} (<Tg) (圧縮) | ppm/℃ | {c[0]} - {c[1]}`. "
            f"**측정모드가 압축(圧縮)이라고 인쇄돼 있어 조건에 그대로 박았다** — 이 쪽의 각주 `*5: 引張` 는 "
            f"이 열에 붙어 있지 않다(같은 쪽 GEA/HS 열에는 붙는다). 환산 ppm/℃ x 1e-6 -> 1/K. " + base,
            conv=ppm)
    for reg, c in (("alpha1 (<Tg)", cz1), ("alpha2 (>Tg)", cz2)):
        rng(P, "thermal.expansion_linear", "1/K", c[0], c[1],
            {"axis": "Z", "regime": reg, "test_mode": "compression (圧縮)", "specimen_thickness_mm": 0.8},
            f"원문 verbatim: `CTE z ({'<Tg' if 'alpha1' in reg else '>Tg'}) (圧縮)*4 | ppm/℃ | {c[0]} - {c[1]}`. "
            f"각주 `*4: 0.8 mmt`. 환산 x1e-6 -> 1/K. " + base, conv=ppm)
    if cz_dic is not None:
        P.append({"key": "thermal.expansion_linear", "value": ppm(cz_dic), "unit": "1/K",
                  "method": "measured", "tier": 1,
                  "conditions": {"axis": "Z", "regime": "alpha1 (<Tg)", "test_method": "DIC",
                                 "specimen_thickness_mm": 0.8},
                  "notes": f"원문 verbatim: `CTE z (<Tg) (DIC)*4 | ppm/℃ | {cz_dic}`. "
                           f"**같은 Z 축 CTE 를 압축법과 DIC 두 방법으로 따로 찍는다** — 방법이 다르므로 "
                           f"압축법 값({cz1[0]}-{cz1[1]})과 평균 내지 않고 따로 넣었다. 단일 값이라 구간이 아니다. "
                           f"환산 {cz_dic} x 1e-6 = {ppm(cz_dic):g} 1/K. " + base})
    for meth, t in (("TMA", tgT), ("DMA", tgD)):
        rng(P, "thermal.glass_transition", "K", t[0], t[1], {"method_detail": meth},
            f"원문 verbatim: `Tg ({meth}) | ℃ | {t[0]} - {t[1]}`. 환산 ℃ + 273.15 = K; "
            f"되돌리면 {C2K(t[0])} - 273.15 = {t[0]}. TMA·DMA 두 측정을 갈랐다. " + base, conv=C2K)
    if k:
        rng(P, "thermal.conductivity", "W/(m*K)", k[0], k[1], {},
            f"원문 verbatim: `熱伝導率 | W/(m·K) | {k[0]} - {k[1]}`. 단위가 이미 SI 라 환산 없음. " + base)
    rng(P, "electrical.dielectric_constant", "1", dk1[0], dk1[1],
        {"frequency": "1 GHz", "test_method": "SPDR"},
        f"원문 verbatim: `Dk (1 GHz) | {dk1[0]} - {dk1[1]}`(표 왼쪽 `電気特性 (SPDR)`). 무차원. " + base)
    if dk10:
        rng(P, "electrical.dielectric_constant", "1", dk10[0], dk10[1],
            {"frequency": "10 GHz", "test_method": "SPDR"},
            f"원문 verbatim: `Dk (10 GHz) | {dk10[0]} - {dk10[1]}`. 무차원. " + base)
    rng(P, "electrical.dissipation_factor", "1", df1[0], df1[1],
        {"frequency": "1 GHz", "test_method": "SPDR"},
        f"원문 verbatim: `Df (1 GHz) | {df1[0]} - {df1[1]}`. 무차원. " + base)
    if df10:
        rng(P, "electrical.dissipation_factor", "1", df10[0], df10[1],
            {"frequency": "10 GHz", "test_method": "SPDR"},
            f"원문 verbatim: `Df (10 GHz) | {df10[0]} - {df10[1]}`. 무차원. " + base)
    for th, pk in ((12, p12), (18, p18)):
        if pk is None: continue
        rng(P, "interface.peel_strength", "N/m", pk[0], pk[1], {"copper_foil": f"{th} um"},
            f"원문 verbatim: `ピール強度 ({th}μm) | kN/m | {pk[0]} - {pk[1]}`. 환산 kN/m x 1000 -> N/m. " + base,
            conv=lambda v: v * kNm)

    g = nm.split(" (")[0]
    al = {nm, g, g.replace("-", ""), g.replace("MCL-", ""), "Resonac " + g, "Showa Denko " + g,
          "Hitachi Chemical " + g}
    if "(" in nm:
        t = nm.split("(")[1].rstrip(")").replace(" type", "")
        al |= {f"{g} {t}", f"{g}-{t}", f"{g}({t})", f"{g} {t} type", f"{g} {t}タイプ"}
    MATS.append({
        "new_material": {
            "name": f"Resonac {nm} (glass/epoxy CCL)",
            "category": "composite",
            "description": (
                f"레조낙(Resonac, 구 쇼와덴코머티리얼즈/히타치화성) 다층 프린트배선판용 동장적층판 `{nm}`. "
                f"유리포 {glass}, 표 기준 두께 {thk} mm, IPC-4101 슬래시시트 {slash}. "
                f"2023-2024 일본어 총합 카탈로그 `MCL一般特性一覧` 표(PDF {pg}쪽)의 한 열이다. "
                f"이 표의 값어치는 **`弾性率(引張モード)`와 `弾性率(曲げモード)`를 행 이름에 시험모드를 박아 가른다**는 데 있다. "
                + ("**라이브 DB 재료 1227·1228 `Hitachi MCL-679`(Hsiung 2003, role=evidence)와의 관계** — "
                   "그 둘은 논문이 잰 적층판 *표면 상태* 카드이고 등급 접미(`MCL-679` vs `MCL-E-679FG`)도 다르다. "
                   "이 카드는 벤더가 인쇄한 등급 카드이고 값이 겹치지 않는다."
                   if "679" in nm else "")
                + " 이 카탈로그에는 밀도·포아송비·비열·인장강도 열이 없다(66쪽 전수 확인)."
            ),
            "attributes": {
                "material_class": "glass/epoxy copper-clad laminate",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "다층 PCB·반도체 패키지 기판 실부품 적층재. 벤더 총합 카탈로그에 등급명으로 인쇄된 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Resonac Corporation",
                "manufacturer_former": ["Showa Denko Materials", "Hitachi Chemical"],
                "product_form": "copper-clad laminate",
                "glass_cloth": glass,
                "ipc_4101_slash_sheet": slash,
                "aliases": sorted(al),
                "related_material_ids": [1227, 1228] if "679" in nm else [],
            },
        },
        "source": SRC_RES,
        "properties": P,
    })

# ─────────────────────────────────────────────────────────────────────────────
out = {"batch": "70차 FA", "materials": MATS}
with open(os.path.join(OUT, "fa01_materials.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# ── 자체 검증 ────────────────────────────────────────────────────────────────
UNITS = {
 "mechanical.youngs_modulus": "Pa", "mechanical.flexural_modulus": "Pa",
 "mechanical.tensile_strength": "Pa", "mechanical.flexural_strength": "Pa",
 "mechanical.poisson_ratio": "1", "physical.density": "kg/m^3",
 "thermal.conductivity": "W/(m*K)", "thermal.specific_heat": "J/(kg*K)",
 "thermal.expansion_linear": "1/K", "thermal.glass_transition": "K",
 "thermal.decomposition_temp": "K", "thermal.time_to_delamination": "s",
 "interface.peel_strength": "N/m", "electrical.dielectric_constant": "1",
 "electrical.dissipation_factor": "1", "chemical.water_absorption_saturation": "1",
 "chemical.moisture_absorption_equilibrium": "1", "thermal.flammability_ul94": None,
}
CORE7 = ["physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
         "thermal.expansion_linear", "thermal.conductivity", "thermal.specific_heat",
         "mechanical.tensile_strength"]
errs, nrows = [], 0
core_hit = collections.Counter()
for m in MATS:
    n = m["new_material"]["name"]
    if len(n) > 200: errs.append(f"NAME>200 ({len(n)}): {n}")
    a = m["new_material"]["attributes"]
    if "role" not in a: errs.append(f"NO ROLE: {n}")
    if not a.get("aliases"): errs.append(f"NO ALIASES: {n}")
    ks = set()
    for p in m["properties"]:
        nrows += 1
        if p["key"] not in UNITS: errs.append(f"UNKNOWN KEY {p['key']} @ {n}")
        elif p["unit"] != UNITS[p["key"]]: errs.append(f"UNIT {p['key']} {p['unit']} != {UNITS[p['key']]} @ {n}")
        if p["tier"] == 3 and "grade_scope" not in p.get("conditions", {}):
            errs.append(f"t3 NO grade_scope: {p['key']} @ {n}")
        if p["tier"] == 4: errs.append(f"UNEXPECTED t4 @ {n}")
        if not p.get("notes"): errs.append(f"NO NOTES {p['key']} @ {n}")
        ks.add(p["key"])
    core_hit[len(ks & set(CORE7))] += 1
    m["_core7_filled"] = sorted(ks & set(CORE7))

full = [m["new_material"]["name"] for m in MATS
        if {"physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio"} <= set(m["_core7_filled"])]
print(f"재료 {len(MATS)}장 · 물성행 {nrows}행")
print("코어7 채움 분포:", dict(sorted(core_hit.items())))
print(f"카드가 선 것(밀도+영률+포아송비 완비) {len(full)}장:")
for x in full: print("   -", x)
print("검증 오류", len(errs))
for e in errs[:30]: print("   !", e)
