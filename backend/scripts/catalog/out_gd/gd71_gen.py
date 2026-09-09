# 71차 GD — Sumitomo LAZ 온도별 영률과 Resonac 총합표 나머지 쪽을 등급 카드로 세우는 생성기
# 값은 전부 로컬 원문(HTML <td> 직접 파싱 / PDF 350dpi 렌더 눈대조)에서 옮긴 것이고 계산·추정은 없다.
import json, os, collections

OUT = os.path.dirname(os.path.abspath(__file__))
PCB = "/data/paper_patent_corpus/standards_appnotes/pcb"

GPa, MPa = 1e9, 1e6
def C2K(c): return round(c + 273.15, 2)
def ppm(v): return float(f"{v * 1e-6:.12g}")
def pct(v): return float(f"{v / 100:.12g}")

MATS = []

# ═════════════════════════════════════════════════════════════════════════════
# ① Sumitomo Bakelite LαZ 계열 — 온도별 영률(30 ℃ / 260 ℃)
# ═════════════════════════════════════════════════════════════════════════════
# 값은 세 HTML 을 html.parser 로 <tr>/<td> 직접 파싱(colspan/rowspan 포함)해 셀 경계를 확정한 것이다.
# 레이아웃 추측이 끼어들 자리가 없으므로 열 밀림 위험이 원천적으로 없다.

LAZ_URL_NOTE = (
 "저장본에 절대 URL 이 남아 있지 않다 — `og:url`·canonical 없음이고 살아 있는 절대 URL 은 "
 "구글 태그매니저와 사이트검색(`https://search-sumibe.dga.jp/`)뿐이다. **도메인을 지어내지 않았다.** "
 "다만 페이지 안 네비게이션이 형제 페이지만 걸고 자기 자신은 안 거는 구조라 사이트 내 **상대 경로는 확정된다** — "
 "이 페이지는 `{path}` 다(형제 링크 {sibs} 가 다 있고 자기 자신만 없다). 70차 FA 가 같은 벤더의 ELC 두 장에 쓴 처리와 같다."
)

def laz_src(title, path, sibs, local):
    return {
        "kind": "datasheet",
        "title": title,
        "url": None,
        "publisher": "Sumitomo Bakelite Co., Ltd. (住友ベークライト株式会社)",
        "year": 2026,
        "local_path": f"{PCB}/{local}",
        "url_note": LAZ_URL_NOTE.format(path=path, sibs=sibs),
    }

SRC_LAZ_CORE = laz_src(
    "半導体パッケージ基板用材料 コア材料 — 高密度パッケージ基板材料 “LαZ®” LAZ-4785 特性一覧 (住友ベークライト)",
    "/product/it-materials/package/core/", "`buildup/`·`prepreg/`·`sr/`",
    "SumitomoBakelite_LAZ-4785_PackageCore_Spec_ja_2026-09-09.html")
SRC_LAZ_PPG = laz_src(
    "半導体パッケージ基板用材料 プリプレグ材料 — 高密度パッケージ基板材料 “LαZ®” LAZ-2002 / LAZ-6785 特性一覧 (住友ベークライト)",
    "/product/it-materials/package/prepreg/", "`buildup/`·`core/`·`sr/`",
    "SumitomoBakelite_LAZ-6785_Prepreg_Spec_ja_2026-09-09.html")
SRC_LAZ_SR = laz_src(
    "半導体パッケージ基板用材料 ソルダーレジスト代替材料 — 高密度パッケージ基板材料 “LαZ®” LAZ-7752 特性一覧 (住友ベークライト)",
    "/product/it-materials/package/sr/", "`buildup/`·`core/`·`prepreg/`",
    "SumitomoBakelite_LAZ-7752_SolderResistAlt_Spec_ja_2026-09-09.html")

LAZ_TABLE_NOTE = (
 "값은 저장된 HTML 의 `<tr>`/`<td>` 를 `colspan`/`rowspan` 까지 직접 파싱해 셀 경계를 확정한 것이다 — "
 "레이아웃 추측이 없으므로 열 밀림 위험이 원천적으로 없다."
)

# 弾성률 행에 시험모드 표기가 없다 — t3 로 내린 사유
E_LAZ_SCOPE = (
 "값 자체는 **이 등급의 이 온도에 인쇄된 것**이고 등급 범위 문제는 없다. t3 로 내린 이유는 **시험모드 미확정**이다 — "
 "이 표의 `弾性率` 행에는 인장/굽힘 표기가 전혀 없다. 같은 표의 CTE 행은 `TMA(引張モード)` 로 모드를 박아 두었고, "
 "같은 벤더의 스미라이트 ELC 표(70차 FA 가 담은 6등급)는 `曲げ弾性率` 와 `引っ張り弾性率` 를 **행 이름으로** 가른다. "
 "즉 이 벤더는 모드를 적을 때는 적는다 — 여기서 안 적은 것은 누락이지 인장 확정이 아니다. "
 "70차 FA 가 MGC BT 13등급의 `ヤング率` 를 같은 사유로 t3 에 둔 선례를 따랐다."
)
E_LAZ_NOTE = (
 "원문 verbatim: `弾性率 | {tc}deg.C | GPa | {v}`. 같은 등급의 짝 행은 `弾性率 | {other}deg.C | GPa | {ov}` 다 — "
 "**두 온도가 별개 행이므로 두 행으로 넣었고 평균 내지 않았다.** "
 "환산 {v} GPa x 1e9 = {p:g} Pa; 되돌리면 {p:g}/1e9 = {v}. "
 "온도 {tc} ℃ 는 `conditions.temperature_c` 에 그대로 넣었다(K 환산 없이 조건 축의 어휘를 라이브 DB 관행에 맞췄다). "
 "이 페이지에는 **시험규격 번호가 하나도 인쇄돼 있지 않다**(HTML 전문에서 `JIS` 0회 · `ASTM` 0회 · `IPC` 0회). " + LAZ_TABLE_NOTE
)

def laz_card(prod, grade, form, desc_extra, attrs_extra, rows, src):
    """rows: dict of property inputs. 값이 None(원문 `N.D.`)이면 넣지 않는다."""
    name = f"Sumitomo Bakelite {prod}{(' ' + grade) if grade else ''} ({form})"
    assert len(name) <= 200, name
    # 별칭은 **이 카드 하나만** 가리키게 만든다 — 형제 등급 7장이 같은 `LAZ-4785` 를 물면
    # 매칭이 모호해진다. 등급이 있으면 등급이 붙은 꼴만 넣는다.
    if grade:
        al = {f"{prod} {grade}", f"{prod}{grade}", f"{prod}-{grade}", f"LαZ {prod} {grade}"}
    else:
        al = {prod, prod.replace("-", ""), f"LαZ {prod}"}
    P = []

    def add(key, val, unit, tier=1, cond=None, notes="", method="measured"):
        if val is None: return
        p = {"key": key, "value": val, "unit": unit, "method": method, "tier": tier}
        if cond: p["conditions"] = cond
        p["notes"] = notes
        P.append(p)

    # ── 온도별 영률: 이 배치의 표적 ──────────────────────────────────────────
    e30, e260 = rows["E30"], rows["E260"]
    for tc, v, ov in ((30, e30, e260), (260, e260, e30)):
        add("mechanical.youngs_modulus", v * GPa, "Pa", 3,
            {"temperature_c": tc, "test_mode": "unconfirmed", "grade_scope": E_LAZ_SCOPE,
             "orientation": "not stated"},
            E_LAZ_NOTE.format(tc=tc, v=v, p=v * GPa, other=(260 if tc == 30 else 30), ov=ov))

    # ── 같은 표에서 조건이 확정된 나머지 ─────────────────────────────────────
    if rows.get("tg") is not None:
        add("thermal.glass_transition", C2K(rows["tg"]), "K", 1, {"method_detail": "DMA"},
            f"원문 verbatim: `Tg | DMA | deg.C | {rows['tg']}`. "
            f"환산 {rows['tg']} + 273.15 = {C2K(rows['tg'])} K; 되돌리면 {C2K(rows['tg'])} - 273.15 = {rows['tg']}. " + LAZ_TABLE_NOTE)
    if rows.get("cte_xy") is not None:
        add("thermal.expansion_linear", ppm(rows["cte_xy"]), "1/K", 1,
            {"axis": "in-plane (X,Y)", "regime": "alpha1 (CTE-1)", "test_mode": "tensile (引張モード)",
             "method_detail": "TMA"},
            f"원문 verbatim: `{rows['cte_xy_label']} | TMA(引張モード) | ppm/C | {rows['cte_xy']}`. "
            f"**행 이름에 시험모드가 박혀 있다**(弾性率 행과 대비된다). "
            f"환산 {rows['cte_xy']} ppm/℃ x 1e-6 = {ppm(rows['cte_xy']):g} 1/K; 되돌리면 {ppm(rows['cte_xy']):g}/1e-6 = {rows['cte_xy']}. "
            f"ppm/℃ 와 1/K 는 구간 크기가 같아 수치가 그대로 간다. " + LAZ_TABLE_NOTE)
    if rows.get("cte_z") is not None:
        add("thermal.expansion_linear", ppm(rows["cte_z"]), "1/K", 1,
            {"axis": "z (through-thickness)", "regime": "alpha1 (CTE-1)",
             "test_mode": "tensile (引張モード)", "method_detail": "TMA"},
            f"원문 verbatim: `CTE-1 z | TMA(引張モード) | ppm/C | {rows['cte_z']}`. "
            f"원문 표는 `TMA(引張モード)` 를 CTE-1 xy 행에 rowspan=2 로 걸어 **z 행까지 덮는다** — HTML 태그로 확인했다. "
            f"환산 {rows['cte_z']} ppm/℃ x 1e-6 = {ppm(rows['cte_z']):g} 1/K. " + LAZ_TABLE_NOTE)
    if rows.get("k") is not None:
        add("thermal.conductivity", rows["k"], "W/(m*K)", 1, None,
            f"원문 verbatim: `熱伝導率 | W/m・k | {rows['k']}`. 단위가 이미 SI 라 환산 없음. "
            f"측정법은 이 페이지에 인쇄되지 않았다. " + LAZ_TABLE_NOTE)
    if rows.get("dk") is not None:
        add("electrical.dielectric_constant", rows["dk"], "1", 1, {"frequency": "1 GHz"},
            f"원문 verbatim: `Dk | 1GHz | - | {rows['dk']}`. 무차원. " + LAZ_TABLE_NOTE)
    if rows.get("df") is not None:
        add("electrical.dissipation_factor", rows["df"], "1", 1, {"frequency": "1 GHz"},
            f"원문 verbatim: `Df | 1GHz | - | {rows['df']}`. 무차원. " + LAZ_TABLE_NOTE)
    if rows.get("peel") is not None:
        cond = {"copper_foil": rows["peel_foil"]}
        add("interface.peel_strength", rows["peel"] * 1000, "N/m", 1, cond,
            f"원문 verbatim: `{rows['peel_label']} | kN/m | {rows['peel']}`. "
            f"환산 {rows['peel']} kN/m x 1000 = {rows['peel']*1000:g} N/m; 되돌리면 {rows['peel']*1000:g}/1000 = {rows['peel']}. " + LAZ_TABLE_NOTE)
    if rows.get("wa") is not None:
        add("chemical.water_absorption_24h", pct(rows["wa"]), "1", 1,
            {"conditioning": "D-24/23", "duration_h": 24, "temperature_c": 23},
            f"원문 verbatim: `吸水率 | (D-24/23) | {rows['wa_unit']} | {rows['wa']}`. "
            f"환산 {rows['wa']} % / 100 = {pct(rows['wa']):g} (무차원). "
            f"`D-24/23` 은 건조 후 23 ℃ 물에 24 시간 침지하는 표준 전처리 표기다. " + LAZ_TABLE_NOTE)

    return {
        "new_material": {
            "name": name,
            "category": "composite",
            "description": (
                f"住友ベークライト(Sumitomo Bakelite) 반도체 패키지 기판용 고밀도 재료 「LαZ®」 계열 `{prod}"
                f"{(' ' + grade) if grade else ''}` — {desc_extra} "
                f"이 카드의 값은 벤더 제품 페이지의 특성일람표 중 **한 열**을 그대로 옮긴 것이다. "
                f"**이 표의 드문 점은 영률을 30 ℃ 와 260 ℃ 두 온도에서 찍는다는 것**이다(리플로 피크 부근의 강성이 그대로 읽힌다) — "
                f"두 값을 `conditions.temperature_c` 로 갈라 두 행으로 넣었다. "
                f"다만 `弾性率` 행에 시험모드 표기가 없어 영률 두 행은 t3 다(사유는 각 행 `grade_scope`)."
            ),
            "attributes": dict({
                "material_class": "package substrate laminate (LαZ series)",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "반도체 패키지 기판(FC-CSP/BGA 등)의 실부품 적층재. 벤더가 등급명으로 인쇄한 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Sumitomo Bakelite Co., Ltd.",
                "product_series": "LαZ (LAZ)",
                "aliases": sorted(al),
                "core7_absent_from_vendor_table": (
                    "이 페이지 표에는 **밀도·포아송비·비열·인장강도 행이 아예 없다.** HTML 전문 토큰 검사로 확인했다 — "
                    "`比重` 0회 · `ポアソン` 0회 · `ポアッソン` 0회 · `比熱` 0회 · `引張強さ` 0회. "
                    "`密度` 는 적중하지만 전부 산문(`高密度パッケージ基板材料`)이고 물성 행이 아니다."
                ),
            }, **attrs_extra),
        },
        "source": src,
        "properties": P,
    }

# ── LAZ-4785 패키지 코어 7등급 (원문 열 순서 그대로) ──────────────────────────
# (등급, 特長, 最薄um, 最厚um, 유리크로스Type, 番手, Tg, CTExy, CTEz, E30, E260, Dk, Df, peel, 吸水率, k)
LAZ4785 = [
 ("TH-G",  "低CTE",   25, 150, "S", "2116", 255,  4,   12, 32, 21, 4.0, 0.005, 0.7, 0.4, 0.7),
 ("GH-G",  "低CTE",   25, 150, "E", "2116", 255,  6,   12, 31, 20, 4.2, 0.007, 0.7, 0.4, 0.7),
 ("TH-B",  "低CTE",   40, 150, "S", "2116", 250,  6,   12, 32, 21, 4.0, 0.006, 0.9, 0.4, 0.7),
 ("GS-BA", "中CTE",   20, 150, "E", "2116", 255, 10,   16, 29, 18, 4.2, 0.007, 0.9, 0.4, 0.6),
 ("GS-BE", "高CTE",   25, 150, "E", "2013", 240, 14, None, 18, 10, 4.1, 0.008, 1.2, 0.4, None),
 ("GH-T",  "低透過率", 40, 100, "E", "2013", 240, 12, None, 18, 10, None, None, 0.8, None, None),
 ("GS-W",  "高反射率", 40, 100, "E", "2116", 220, 14, None, 18, 10, None, None, 0.8, None, None),
]
for (g, tokucho, tmin, tmax, gtype, gcount, tg, cxy, cz, e30, e260, dk, df, peel, wa, k) in LAZ4785:
    MATS.append(laz_card(
        "LAZ-4785", g, "package core laminate",
        f"패키지 코어재. 벤더 표기 特長 `{tokucho}`, 유리크로스 {gtype}-glass #{gcount}(100 µm 두께 기준), "
        f"생산실적 두께 {tmin}~{tmax} µm, 표의 공칭 두께는 100 µm 다.",
        {"product_form": "package core laminate",
         "vendor_feature_label": tokucho,
         "glass_cloth": f"{gtype}-glass #{gcount} (100 um 두께 기준)",
         "thickness_produced_um": [tmin, tmax],
         "nominal_thickness_um": 100,
         "nd_cells_in_source": "원문이 `N.D.` 로 인쇄한 칸은 값을 만들지 않고 비웠다."},
        {"E30": e30, "E260": e260, "tg": tg, "cte_xy": cxy, "cte_xy_label": "CTE-1 xy",
         "cte_z": cz, "k": k, "dk": dk, "df": df,
         "peel": peel, "peel_foil": "12 um LP foil (12LP銅箔)", "peel_label": "ピール強度(12LP銅箔)",
         "wa": wa, "wa_unit": "wt%"},
        SRC_LAZ_CORE))

# ── LAZ-2002 / LAZ-6785 프리프레그 5등급 ────────────────────────────────────
# 원문 헤더는 `LAZ-` 아래 `2002`(rowspan=2, 하위등급 표기 없음) + `6785`(colspan=4: TT-R/GT-R/TS-FG/GS-FG) 다.
LAZPPG = [
 ("LAZ-2002", "",       "S", "1037", 200,  7, 22, 11, 3.9, 0.008, 0.8, 0.35),
 ("LAZ-6785", "TT-R",   "S", "1037", 210,  8, 22, 10, 3.9, 0.008, 0.8, 0.35),
 ("LAZ-6785", "GT-R",   "E", "1024", 210, 10, 21,  9, 4.1, 0.007, 0.8, 0.35),
 ("LAZ-6785", "TS-FG",  "S", "1037", 240, 11, 18, 10, 3.7, 0.010, 0.8, 0.30),
 ("LAZ-6785", "GS-FG",  "E", "1024", 240, 13, 17,  9, 3.8, 0.008, 0.8, 0.30),
]
for (prod, g, gtype, gcount, tg, cxy, e30, e260, dk, df, peel, wa) in LAZPPG:
    MATS.append(laz_card(
        prod, g, "prepreg",
        f"패키지 기판용 프리프레그. 유리크로스 {gtype}-glass #{gcount}, 표의 두께 40 µm. "
        f"원문 헤더는 `LAZ-` 아래 `2002`(rowspan=2, 하위등급 표기 없음)와 `6785`(colspan=4: TT-R/GT-R/TS-FG/GS-FG)로 갈린다 — "
        f"`colspan`/`rowspan` 을 읽어 열 소속을 확정했다.",
        {"product_form": "prepreg",
         "glass_cloth": f"{gtype}-glass #{gcount}",
         "nominal_thickness_um": 40},
        {"E30": e30, "E260": e260, "tg": tg, "cte_xy": cxy, "cte_xy_label": "CTE-1(XY)",
         "cte_z": None, "k": None, "dk": dk, "df": df,
         "peel": peel, "peel_foil": "not stated (원문 행 이름이 `ピール強度` 뿐이다)", "peel_label": "ピール強度",
         "wa": wa, "wa_unit": "%"},
        SRC_LAZ_PPG))

# ── LAZ-7752 솔더레지스트 대체재 1등급 ──────────────────────────────────────
MATS.append(laz_card(
    "LAZ-7752", "VerJB", "solder-resist alternative film",
    "솔더레지스트(SR) 대체 재료. 벤더 표기 特長 `黒：低透過率`, 用途 `SR`, 두께 10~100 µm. "
    "70차 FA 의 인계 목록에는 없던 표적인데 같은 LαZ 계열 형제 페이지가 로컬에 있었고 서식이 같아 함께 담았다.",
    {"product_form": "solder-resist alternative film",
     "vendor_feature_label": "黒：低透過率",
     "vendor_use_label": "SR (solder resist)",
     "thickness_range_um": [10, 100]},
    {"E30": 15, "E260": 2.6, "tg": 260, "cte_xy": 15, "cte_xy_label": "CTE-1(XY)",
     "cte_z": None, "k": None, "dk": 3.4, "df": 0.006,
     "peel": 0.7, "peel_foil": "12 um VLP foil (12umVLP銅箔)", "peel_label": "ピール強度(12umVLP銅箔)",
     "wa": 0.3, "wa_unit": "%"},
    SRC_LAZ_SR))

# ═════════════════════════════════════════════════════════════════════════════
# ③ Resonac MCL 총합 카탈로그 — FA 가 안 본 쪽 (PDF 6·7·8쪽)
# ═════════════════════════════════════════════════════════════════════════════
SRC_RES = {
    "kind": "datasheet",
    "title": "MCL 一般特性一覧 — 銅張積層板 総合カタログ 2023-2024 (レゾナック)",
    "url": None,
    "publisher": "Resonac Corporation (구 Showa Denko Materials / Hitachi Chemical)",
    "year": 2024,
    "local_path": f"{PCB}/Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf",
    "url_note": "PDF 메타(CubePDF/iTextSharp)에 원 URL 이 없고 저장 시점 URL 도 파일에 남아 있지 않다. **URL 을 지어내지 않았다** — 로컬 원문(66쪽)이 근거다. 69차 EB 가 코퍼스에 넣은 파일이다.",
}

RENDER_NOTE = (
 "**열 밀림 대조**: 이 쪽(PDF {pg}쪽 / 인쇄 {pr}쪽)을 350 dpi 로 렌더해 표 머리·기계특성대·전기특성대·하단대를 "
 "눈으로 대조한 뒤에만 값을 옮겼다. 렌더로 확정한 열 순서는 {order} 다. "
 "이 카탈로그는 쪽 옆 세로 탭 네비게이션이 `pdftotext -layout` 출력에 끼어들어 70차 FA 가 실제로 열 밀림을 잡은 전력이 있다."
)

RES_FOOTNOTES = "표 하단 각주 verbatim: `*1: 空洞共振器; *2: RT箔; *3: HVLP箔, *4: 0.8 mmt; *5: 引張`."

def rng(lo, hi):
    return [("lower", lo), ("upper", hi)]

def res_card(name_core, page, pg, pr, order, col, data):
    name = f"Resonac {name_core}"
    assert len(name) <= 200, name
    # name_core 의 **마지막** 괄호는 제품형태 설명이다 — 그 앞이 벤더 등급명이다.
    grade_full = name_core.rsplit(" (", 1)[0]
    base = grade_full.split(" (")[0]
    if " (" in grade_full:                       # 예: `MCL-HS200 (D type)`
        typ = grade_full.split(" (", 1)[1].rstrip(")")
        letter = typ.split()[0]
        al = {grade_full, f"{base} {letter}", f"{base}-{letter}",
              f"{base} ({letter} タイプ)", f"{base}({letter})"}
    else:                                        # 형제 타입 카드와 겹치지 않는 단독 등급
        al = {grade_full, grade_full.replace("-", "")}
    P = []
    rnote = RENDER_NOTE.format(pg=pg, pr=pr, order=order)

    def addr(key, label, unit_src, vals, conv, unit_out, cond_base, extra_note="", tier=1):
        """인쇄된 구간을 lower/upper 두 행으로 나눈다. 평균 내지 않는다."""
        if vals is None: return
        lo, hi = vals
        for bound, v in rng(lo, hi):
            c = dict(cond_base); c["bound"] = bound
            P.append({
                "key": key, "value": conv(v), "unit": unit_out, "method": "measured", "tier": tier,
                "conditions": c,
                "notes": (f"원문 verbatim: `{label} | {unit_src} | {lo} - {hi}`. "
                          f"**인쇄된 값이 구간이므로 하한·상한 두 행으로 갈랐다 — 평균 내지 않았다.** "
                          f"이 행은 {'하한' if bound=='lower' else '상한'} {v} 이다. "
                          f"환산 {v} -> {conv(v):g} {unit_out}. {extra_note} {rnote} {RES_FOOTNOTES}").strip(),
            })

    d = data
    # 영률 — 引張モード (행 이름에 시험모드가 박혀 있다)
    addr("mechanical.youngs_modulus", "弾性率 (引張モード) X", "GPa", d.get("Et"),
         lambda v: v * GPa, "Pa",
         {"test_mode": "tensile (引張モード)", "orientation": "X (in-plane)",
          "specimen_thickness_mm": d["t"]},
         extra_note=(f"**행 이름 자체가 `(引張モード)` 라 인장 확정이다** — 같은 표의 `弾性率(曲げモード)` 와 별개 행이고 값도 다르다. "
                     f"각주 `*4: 0.8 mmt` 는 **굽힘 행과 CTE z 행에만** 붙고 이 인장 행에는 번호가 없다 → "
                     f"시편 두께는 표 맨 위 `厚み {d['t']} mm` 다."))
    # 굽힘탄성률 — 曲げモード, *4 = 0.8 mmt
    addr("mechanical.flexural_modulus", "弾性率 (曲げモード) X*4", "GPa", d.get("Ef"),
         lambda v: v * GPa, "Pa",
         {"test_mode": "flexural (曲げモード)", "orientation": "X (in-plane)",
          "specimen_thickness_mm": 0.8},
         extra_note="각주 `*4` 가 이 행에 붙는다 → 시편 두께 0.8 mm(표 맨 위 厚み 와 다르다).")
    # Tg
    for lab, key_detail, vals in (("Tg (TMA)", "TMA", d.get("TgT")), ("Tg (DMA)", "DMA", d.get("TgD"))):
        addr("thermal.glass_transition", lab, "℃", vals, C2K, "K", {"method_detail": key_detail},
             extra_note="TMA 와 DMA 는 같은 물성의 다른 측정법이라 별개 행으로 두었다.")
    # CTE x / y (<Tg)
    for ax, vals, tm in (("x", d.get("CTEx"), d.get("cte_mode")), ("y", d.get("CTEy"), d.get("cte_mode"))):
        addr("thermal.expansion_linear", f"CTE {ax} (<Tg) (圧縮){'*5' if d.get('cte_star5') else ''}",
             "ppm/℃", vals, ppm, "1/K",
             {"axis": f"in-plane ({ax.upper()})", "regime": "below Tg", "test_mode": tm, "method_detail": "TMA"},
             extra_note=(("이 칸에는 각주 `*5`(=引張)가 붙어 있어 **행 이름의 `(圧縮)` 를 덮는다** — 원문 표기 충돌을 그대로 적는다: "
                          "행 이름은 `(圧縮)`, 칸 각주는 `*5: 引張`. 각주가 칸 단위로 걸리므로 각주를 따랐다.")
                         if d.get("cte_star5") else
                         "이 칸에는 `*5` 각주가 없다 → 행 이름 그대로 압축(圧縮) 모드다."))
    # CTE z
    addr("thermal.expansion_linear", "CTE z (<Tg) (圧縮)*4", "ppm/℃", d.get("CTEzL"), ppm, "1/K",
         {"axis": "z (through-thickness)", "regime": "below Tg", "test_mode": "compression (圧縮)",
          "method_detail": "TMA", "specimen_thickness_mm": 0.8},
         extra_note="각주 `*4` 가 이 행에 붙는다 → 시편 두께 0.8 mm.")
    addr("thermal.expansion_linear", "CTE z (>Tg) (圧縮)*4", "ppm/℃", d.get("CTEzH"), ppm, "1/K",
         {"axis": "z (through-thickness)", "regime": "above Tg", "test_mode": "compression (圧縮)",
          "method_detail": "TMA", "specimen_thickness_mm": 0.8},
         extra_note="각주 `*4` 가 이 행에 붙는다 → 시편 두께 0.8 mm.")
    # 열전도율
    addr("thermal.conductivity", "熱伝導率", "W/(m·K)", d.get("k"), lambda v: v, "W/(m*K)", {},
         extra_note="단위가 이미 SI 라 환산 없음. 측정법은 인쇄되지 않았다.")
    # Dk / Df
    for freq, vals, star in (("1 GHz", d.get("Dk1"), d.get("Dk1s")), ("10 GHz", d.get("Dk10"), d.get("Dk10s"))):
        addr("electrical.dielectric_constant", f"Dk ({freq}){'*1' if star else ''}", "－", vals,
             lambda v: v, "1",
             {"frequency": freq, "method_detail": "cavity resonator (空洞共振器, *1)" if star else "SPDR"},
             extra_note=("표 좌측 묶음 이름이 `電気特性(SPDR)` 인데 이 칸에는 `*1`(空洞共振器)이 붙는다 → 이 칸만 공동공진기다."
                         if star else "표 좌측 묶음 이름 `電気特性(SPDR)` 를 따랐다(이 칸에 `*1` 각주가 없다)."))
    for freq, vals, star in (("1 GHz", d.get("Df1"), d.get("Df1s")), ("10 GHz", d.get("Df10"), d.get("Df10s"))):
        addr("electrical.dissipation_factor", f"Df ({freq}){'*1' if star else ''}", "－", vals,
             lambda v: v, "1",
             {"frequency": freq, "method_detail": "cavity resonator (空洞共振器, *1)" if star else "SPDR"},
             extra_note=("이 칸에는 `*1`(空洞共振器) 각주가 붙는다." if star else
                         "표 좌측 묶음 이름 `電気特性(SPDR)` 를 따랐다(이 칸에 `*1` 각주가 없다)."))
    # 피일강도
    for foil_um, vals, star in ((12, d.get("P12"), d.get("P12s")), (18, d.get("P18"), d.get("P18s"))):
        foil = {"2": "RT foil (RT箔, *2)", "3": "HVLP foil (HVLP箔, *3)"}.get(star, "not stated")
        addr("interface.peel_strength", f"ピール強度 ({foil_um}μm){'*'+star if star else ''}", "kN/m", vals,
             lambda v: v * 1000, "N/m",
             {"copper_foil_thickness_um": foil_um, "copper_foil_type": foil},
             extra_note=(f"각주 `*{star}` 가 이 칸에 붙는다 → 동박 종류 {foil}." if star else
                         "이 칸에는 동박 종류 각주가 없다."))

    return {
        "new_material": {
            "name": name,
            "category": "composite",
            "description": (
                f"レゾナック(Resonac, 구 Showa Denko Materials / Hitachi Chemical) 동장적층판 `{base}`"
                f"{' — ' + d['blurb'] if d.get('blurb') else ''}. "
                f"값은 2023-2024 총합 카탈로그의 `MCL一般特性一覧` 표(PDF {pg}쪽 / 인쇄 {pr}쪽) 한 열이다. "
                f"70차 FA 가 같은 카탈로그의 PDF 5쪽과 6쪽 일부(MCL-E-679FG 두 등급)만 담았고 이 카드는 FA 가 안 본 열이다. "
                f"표의 값은 전부 **구간**이라 하한·상한 두 행으로 갈라 넣었다(평균 0건)."
            ),
            "attributes": {
                "material_class": "copper-clad laminate (MCL series)",
                "subsystem": "pcb",
                "role": "product",
                "role_reason": "스마트폰·반도체 패키지·서버 기판의 실부품 적층재. 벤더가 등급명으로 인쇄한 제품이다.",
                "role_confidence": "high",
                "manufacturer": "Resonac Corporation",
                "product_form": d.get("form", "copper-clad laminate"),
                "aliases": sorted(al),
                "glass_cloth": d["glass"],
                "nominal_thickness_mm": d["t"],
                "ipc_4101_slash_sheet": d["slash"],
                "ipc_4101_slash_sheet_note": (
                    "**IPC-4101 은 밀도를 규정하지 않는다 — 71차 GD 가 규격 본문 층에서 확인했다.** "
                    "그러므로 이 슬래시시트 번호로는 밀도 빈칸이 닫히지 않는다. 사유는 `gd71_09_verdicts.json` 참조."
                ),
                "core7_absent_from_vendor_table": (
                    "이 카탈로그 66쪽 전체에 밀도·포아송비·비열·인장강도 **행이 없다**(70차 FA 가 전수 grep 으로 확인했고 "
                    "71차 GD 가 6·7·8쪽 렌더로 재확인했다). Resonac 의 기계축은 `弾性率(引張/曲げモード)` 두 행뿐이다."
                ),
                "source_page": f"PDF {pg}쪽 / 인쇄 {pr}쪽, 열 {col}",
            },
        },
        "source": SRC_RES,
        "properties": P,
    }

# ── PDF 6쪽(인쇄 7) — FA 가 679FG 두 열만 가져간 쪽의 나머지 5열 ─────────────
P6_ORDER = "`GEA-705G | GEA-770G | MCL-E-679FG(R) | MCL-E-679FG(S) | MCL-HS200 | MCL-HS200(D) | MCL-HS100`"
P6 = [
 # (카드명, 열번호, blurb, form, glass, 厚み, slash, Et, Ef, TgT, TgD, CTEx, CTEy, star5, CTEzL, CTEzH, k,
 #  Dk1, Dk10, Df1, Df10, P12, P18)
 ("GEA-705G (glass/epoxy prepreg)", 1, "TYPE-F 프리프레그", "prepreg", "E-glass", 0.025, "42",
  (17,19), None, (250,270), (295,305), (8,10), (8,10), True, (15,25), (90,120), None,
  (3.7,4.0), (3.7,4.0), (0.008,0.010), (0.008,0.010), (0.7,0.9), None),
 ("GEA-770G (glass/epoxy prepreg)", 2, "TYPE-F 프리프레그", "prepreg", "E-glass", 0.025, "42",
  (18,20), None, (260,280), (280,300), (6,8), (6,8), True, (15,25), (90,120), (0.40,0.60),
  (3.6,3.9), (3.6,3.9), (0.007,0.009), (0.007,0.009), (0.5,0.7), None),
 ("MCL-HS200 (glass/epoxy CCL)", 5, "고열전도 적층판", "copper-clad laminate", "E-glass", 0.2, "44",
  (17,20), (21,26), (250,270), (330,350), (8,10), (8,10), True, (25,35), (140,200), (0.60,0.80),
  (3.8,4.0), (3.8,4.0), (0.0030,0.0040), (0.0040,0.0050), (0.5,0.7), (0.6,0.8)),
 ("MCL-HS200 (D type) (glass/epoxy CCL)", 6, "고열전도 적층판 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.2, "N/A (Low Dk-glass)",
  (17,20), (21,26), (250,270), (330,350), (8,10), (8,10), True, (25,35), (140,200), (0.60,0.80),
  (3.4,3.6), (3.4,3.6), (0.0020,0.0030), (0.0020,0.0030), (0.5,0.7), (0.6,0.8)),
 ("MCL-HS100 (glass/epoxy CCL)", 7, "고열전도 적층판", "copper-clad laminate", "E-glass", 0.2, "44",
  (20,22), (23,28), (240,260), (240,260), (6,8), (6,8), True, (20,30), (130,180), (0.40,0.50),
  (4.2,4.4), (4.2,4.4), (0.0030,0.0040), (0.0050,0.0060), (0.5,0.7), (0.5,0.7)),
]

# ── PDF 7쪽(인쇄 8) — 8열 전부 새것 ────────────────────────────────────────
P7_ORDER = ("`MCL-HS100(D) | GH-200(D) | GH-100(D) | MCL-HD60 | MCL-HD90 | MCL-HD90(D) | "
            "MCF-200HS | MCF-770G(P)`")
P7 = [
 ("MCL-HS100 (D type) (glass/epoxy CCL)", 1, "고열전도 적층판 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.2, "N/A (Low Dk-glass)",
  (20,22), (23,28), (240,260), (240,260), (6,8), (6,8), True, (20,30), (130,180), (0.40,0.50),
  (3.7,3.9), (3.5,3.7), (0.0020,0.0030), (0.0025,0.0035), (0.5,0.7), (0.5,0.7)),
 ("GH-200 (D type) (TYPE-F thin laminate)", 2, "TYPE-F 박판 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.025, "N/A (Low Dk-glass)",
  (10,12), None, (220,240), (250,270), (13,15), (13,15), True, (30,50), (210,240), (0.50,0.70),
  (3.2,3.4), (3.2,3.4), (0.001,0.003), (0.0020,0.0040), (0.4,0.6), None),
 ("GH-100 (D type) (TYPE-F thin laminate)", 3, "TYPE-F 박판 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.025, "N/A (Low Dk-glass)",
  (10,12), None, (240,260), (240,260), (13,15), (13,15), True, (30,50), (210,240), None,
  (3.3,3.5), (3.3,3.5), (0.002,0.004), (0.0030,0.0050), (0.4,0.6), None),
 ("MCL-HD60 (high-Dk glass/epoxy CCL)", 4, "고유전율(Dk 6) 적층판", "copper-clad laminate",
  "E-glass", 0.2, "44",
  (17,21), None, None, (230,250), (10,12), (10,12), True, None, None, None,
  None, (6.0,6.2), None, (0.0050,0.0060), (0.5,0.7), (0.6,0.8)),
 ("MCL-HD90 (high-Dk glass/epoxy CCL)", 5, "고유전율(Dk 9) 적층판", "copper-clad laminate",
  "E-glass", 0.2, "44",
  (14,18), None, None, (230,250), (11,13), (11,13), True, None, None, None,
  None, (9.0,9.2), None, (0.0045,0.0055), (0.4,0.6), (0.5,0.7)),
 ("MCL-HD90 (D type) (high-Dk CCL)", 6, "고유전율(Dk 8.7) 적층판 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.2, "N/A (Low Dk-glass)",
  (14,18), None, None, (230,250), (11,13), (11,13), True, None, None, None,
  None, (8.6,8.8), None, (0.0030,0.0040), (0.4,0.6), (0.5,0.7)),
 ("MCF-200HS (low-loss adhesive film)", 7, "저전송손실·저열팽창 접착필름", "adhesive film",
  "－ (유리크로스 없음)", 0.025, "N/A",
  (5,7), None, None, (250,270), (35,40), (35,40), True, None, None, None,
  None, (2.9,3.1), None, (0.0030,0.0040), (0.5,0.7), None),
 ("MCF-770G (P type) (low-loss adhesive film)", 8, "저전송손실 접착필름", "adhesive film",
  "－ (유리크로스 없음)", 0.025, "N/A",
  (8,10), None, None, (290,310), (18,20), (18,20), True, None, None, None,
  None, (3.2,3.3), None, (0.0060,0.0080), (0.9,1.0), None),
]

# ── PDF 8쪽(인쇄 9) — 7열 전부 새것 ────────────────────────────────────────
P8_ORDER = "`MCL-LW-990(RFD) | MCL-LW-910G | MCL-LW-900G | MCL-HE-679G(S) | AS-400HS | MCL-I-671 | TD-002`"

MATS_RES = []

def build_res(rows, pg, pr, order, star_over=None):
    for r in rows:
        (nm, col, blurb, form, glass, t, slash, Et, Ef, TgT, TgD, CTEx, CTEy, s5,
         CzL, CzH, k, Dk1, Dk10, Df1, Df10, P12, P18) = r
        d = dict(blurb=blurb, form=form, glass=glass, t=t, slash=slash,
                 Et=Et, Ef=Ef, TgT=TgT, TgD=TgD, CTEx=CTEx, CTEy=CTEy,
                 cte_star5=s5, cte_mode=("tensile (引張, 각주 *5)" if s5 else "compression (圧縮)"),
                 CTEzL=CzL, CTEzH=CzH, k=k, Dk1=Dk1, Dk10=Dk10, Df1=Df1, Df10=Df10,
                 P12=P12, P18=P18,
                 Dk1s=None, Dk10s=None, Df1s=None, Df10s=None, P12s=None, P18s=None)
        if star_over:
            d.update(star_over.get(col, {}))
        MATS_RES.append(res_card(nm, pg, pg, pr, order, col, d))

build_res(P6, 6, 7, P6_ORDER)
build_res(P7, 7, 8, P7_ORDER)

# p8: Dk/Df 에 *1(空洞共振器), 피일강도에 *2(RT箔)/*3(HVLP箔) 각주가 칸 단위로 붙는다
P8 = [
 ("MCL-LW-990 (RFD type) (low-loss CCL)", 1, "저전송손실 다층재 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.8, "N/A (Low Dk-glass)",
  (16,22), (14,19), (180,230), (220,260), (7,10), (7,10), False, (35,55), (240,290), (0.30,0.50),
  None, (3.1,3.3), None, (0.0018,0.0028), None, (0.4,0.6)),
 ("MCL-LW-910G (low-loss CCL)", 2, "저전송손실 다층재 · Low Dk 유리", "copper-clad laminate",
  "Low Dk-glass", 0.8, "N/A (Low Dk-glass)",
  (18,24), (16,21), (190,210), (220,260), (12,15), (12,15), False, (35,45), (230,280), (0.40,0.60),
  None, (3.2,3.4), None, (0.0025,0.0035), None, (0.4,0.7)),
 ("MCL-LW-900G (low-loss CCL)", 3, "저전송손실 다층재", "copper-clad laminate",
  "E-glass", 0.8, "44",
  (18,24), (16,21), (190,210), (220,260), (12,15), (12,15), False, (35,45), (230,280), (0.40,0.60),
  None, (3.6,3.8), None, (0.0040,0.0050), None, (0.4,0.7)),
 ("MCL-HE-679G (S type) (glass/epoxy CCL)", 4, "고내열 다층재", "copper-clad laminate",
  "E-glass", 0.8, "42",
  (17,23), (23,26), (180,190), (260,280), (12,15), (12,15), False, (30,40), (190,230), (0.40,0.50),
  (3.7,3.9), (3.6,3.8), (0.006,0.008), (0.008,0.010), None, (0.5,0.7)),
 ("AS-400HS (low-loss adhesive film)", 5, "저전송손실 접착필름", "adhesive film",
  "－ (유리크로스 없음)", 0.1, "N/A",
  (2,4), None, None, (190,240), (30,55), (30,55), False, (20,45), (35,75), None,
  None, (2.9,3.1), None, (0.0020,0.0030), None, (0.4,0.7)),
 ("MCL-I-671 (glass/epoxy CCL)", 6, "범용 다층재", "copper-clad laminate",
  "E-glass", 0.2, "42",
  (21,24), (24,26), (200,213), (230,245), (12,15), (12,16), False, (50,80), (200,300), (0.30,0.40),
  (4.2,4.3), None, (0.013,0.015), None, None, (1.3,1.5)),
 ("TD-002 (low-modulus solder-crack CCL)", 7, "はんだクラック対策 저탄성 재료", "copper-clad laminate",
  "E-glass", 0.4, "N/A",
  (6,9), (5,8), (155,170), (180,200), (6,9), (6,9), True, (80,130), (200,300), None,
  (3.6,3.8), None, (0.011,0.013), None, None, (0.8,0.9)),
]
P8_STARS = {
 1: {"Dk10s": "1", "Df10s": "1", "P18s": "3"},
 2: {"Dk10s": "1", "Df10s": "1", "P18s": "3"},
 3: {"Dk10s": "1", "Df10s": "1", "P18s": "2"},
 4: {"Dk1s": "1", "Dk10s": "1", "Df1s": "1", "Df10s": "1", "P18s": "2"},
 5: {"Dk10s": "1", "Df10s": "1", "P18s": "2"},
 6: {},
 7: {"Dk1s": "1", "Df1s": "1"},
}
build_res(P8, 8, 9, P8_ORDER, P8_STARS)

MATS.extend(MATS_RES)

# ═════════════════════════════════════════════════════════════════════════════
# 자체검증
# ═════════════════════════════════════════════════════════════════════════════
UNIT = {
 "mechanical.youngs_modulus": "Pa", "mechanical.flexural_modulus": "Pa",
 "thermal.glass_transition": "K", "thermal.expansion_linear": "1/K",
 "thermal.conductivity": "W/(m*K)", "electrical.dielectric_constant": "1",
 "electrical.dissipation_factor": "1", "interface.peel_strength": "N/m",
 "chemical.water_absorption_24h": "1",
}
errs = []
seen_names = set()
for m in MATS:
    nm = m["new_material"]["name"]
    a = m["new_material"]["attributes"]
    if len(nm) > 200: errs.append(f"이름 200자 초과: {nm}")
    if nm in seen_names: errs.append(f"이름 중복: {nm}")
    seen_names.add(nm)
    if a.get("role") != "product": errs.append(f"role 없음/틀림: {nm}")
    if not a.get("aliases"): errs.append(f"aliases 없음: {nm}")
    if not m["properties"]: errs.append(f"물성 0행: {nm}")
    for p in m["properties"]:
        if p["unit"] != UNIT.get(p["key"]):
            errs.append(f"단위 불일치 {nm} {p['key']} {p['unit']} != {UNIT.get(p['key'])}")
        if not p.get("notes"): errs.append(f"notes 없음: {nm} {p['key']}")
        if p["tier"] == 3 and not p.get("conditions", {}).get("grade_scope"):
            errs.append(f"t3 인데 grade_scope 없음: {nm} {p['key']}")
        if p["tier"] == 4: errs.append(f"t4 금지: {nm} {p['key']}")
        if not isinstance(p["value"], (int, float)): errs.append(f"값이 숫자가 아니다: {nm} {p['key']}")

laz = [m for m in MATS if m["new_material"]["attributes"]["manufacturer"].startswith("Sumitomo")]
res = [m for m in MATS if m["new_material"]["attributes"]["manufacturer"].startswith("Resonac")]

print("=== 71차 GD 자체검증")
print("오류:", len(errs))
for e in errs[:30]: print("  !", e)
print(f"재료 {len(MATS)}장 (Sumitomo LAZ {len(laz)} · Resonac {len(res)})")
tc = collections.Counter(p["tier"] for m in MATS for p in m["properties"])
print("물성행", sum(len(m["properties"]) for m in MATS), "등급분포", dict(sorted(tc.items())))
kc = collections.Counter(p["key"] for m in MATS for p in m["properties"])
for k, v in sorted(kc.items()): print(f"  {k}: {v}")
# 온도별 영률 검산
tE = [p for m in MATS for p in m["properties"]
      if p["key"] == "mechanical.youngs_modulus" and "temperature_c" in p.get("conditions", {})]
print("온도조건 달린 영률 행:", len(tE),
      "온도값:", sorted({p["conditions"]["temperature_c"] for p in tE}))

json.dump({"batch": "71차 GD", "materials": laz},
          open(f"{OUT}/gd71_01_sumitomo_laz.json", "w"), ensure_ascii=False, indent=1)
json.dump({"batch": "71차 GD", "materials": res},
          open(f"{OUT}/gd71_02_resonac_mcl.json", "w"), ensure_ascii=False, indent=1)
print("wrote gd71_01_sumitomo_laz.json / gd71_02_resonac_mcl.json")
