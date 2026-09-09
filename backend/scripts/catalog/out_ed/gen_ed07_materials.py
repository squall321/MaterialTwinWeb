# 69차 ED 가 벤더 SDS·TDS 9절에서 얻은 값을 적재용 JSON 으로 만드는 생성기.
import json, pathlib

SDS = "/data/paper_patent_corpus/standards_appnotes/sds"
POLY = "/data/paper_patent_corpus/standards_appnotes/poly"

def K(c):  # degC -> K
    return round(c + 273.15, 2)

OSSILA = "https://downloads.ossila.com/msds/%s.pdf"

# (재료명, Ossila handle, 파일, 개정일, CAS, 9절 verbatim, 값들, lit 여부)
MP = [
 ("9,10-di(2-naphthyl)anthracene (ADN), benchmark blue host - blue OLED host, compound ADN (Balaganesan 2003)",
  "adn", "Ossila_ADN_SDS_2022-12-12.pdf", "2022-12-12", 2022, "122648-99-1",
  "Melting point/freezing point                382-384 °C (lit.)", [(382.0,"lower"),(384.0,"upper")], True,
  "ADN", "9,10-Bis(2-naphthyl)anthrace"),
 ("BCP - 2,9-dimethyl-4,7-diphenyl-1,10-phenanthroline (bathocuproine), OLED host / charge-transport material (Swensen 2011 CV values)",
  "bathocuproine", "Ossila_BCP-Bathocuproine_SDS_2022-12-12.pdf", "2022-12-12", 2022, "4733-39-5",
  "Melting point/freezing point                280-282 °C (lit.)", [(280.0,"lower"),(282.0,"upper")], True,
  "BCP", "2,9-Dimethyl-4,7-diphenyl-1,10-phenanthroline"),
 ("CBP - 4,4'-bis(carbazol-9-yl)biphenyl, OLED host / charge-transport material (Swensen 2011 CV values)",
  "cbp", "Ossila_CBP_SDS_2023-03-24.pdf", "2023-03-24", 2023, "58328-31-7",
  "Melting point/freezing point                281-285 °C (lit.)", [(281.0,"lower"),(285.0,"upper")], True,
  "CBP", "4,4'-Bis(9H-carbazol-9-yl)biphenyl"),
 ("mCP - 1,3-bis(carbazol-9-yl)benzene, OLED host / charge-transport material (Swensen 2011 CV values)",
  "mcp", "Ossila_mCP_SDS_2023-03-24.pdf", "2023-03-24", 2023, "550378-78-4",
  "Melting point/freezing point                173-178 °C", [(173.0,"lower"),(178.0,"upper")], False,
  "mCP", "1,3-Bis(N-carbazolyl)benzene"),
 ("TAPC - 1,1-bis[(di-4-tolylamino)phenyl]cyclohexane, OLED host / charge-transport material (Swensen 2011 CV values)",
  "tapc", "Ossila_TAPC_SDS_2022-11-14.pdf", "2022-11-14", 2022, "58473-78-2",
  "Melting point/freezing point            186 °C", [(186.0,None)], False,
  "TAPC", "4,4'-Cyclohexylidenebis[N,N-bis(4-methylphenyl)benzenamine]"),
 ("fac-Ir(ppy)3 트리스(2-페닐피리딘)이리듐(III) (Tavasli 2012 기준물질)",
  "irppy3", "Ossila_Ir-ppy-3_SDS_2022-12-12.pdf", "2022-12-12", 2022, "94928-86-6",
  "Melting point/freezing point                451 °C (lit.)", [(451.0,None)], True,
  "Ir(ppy)3", "Tris[2-(2-pyridinyl)phenyl]iridium(III)"),
]

mats = []

# ── SABIC HDPE M300054 — 밀도 ─────────────────────────────────────────────
mats.append({
 "match_name": "HDPE M300054 (SABIC, injection moulded) neat (Faiz 2014)",
 "source": {"kind": "datasheet",
   "title": "SABIC(R) HDPE M300054 — High density polyethylene for Injection moulding, Typical data (Revision 20100303)",
   "url": "https://resimport.com.br/painel/arquivos/6103c782c8.pdf",
   "publisher": "SABIC Europe", "year": 2010,
   "local_path": f"{POLY}/SABIC_HDPE_M300054_TDS_rev-2010-03-03.pdf"},
 "properties": [{
   "key": "physical.density", "value": 954.0, "unit": "kg/m^3",
   "method": "measured", "tier": 1,
   "conditions": {"grade": "SABIC HDPE M300054",
     "physical_form": "compression moulded sheet (ASTM D1928 Procedure C) of the injection-moulding grade",
     "test_method": "ASTM D 1505"},
   "notes": ("원문 verbatim(Typical data 표) — `Density   kg/m³   954   ASTM D 1505`. "
     "각주 1) verbatim — `Test specimens are prepared from compression moulded sheet made according to "
     "ASTM D 1928 Procedure C.` 환산은 없다(시트가 이미 kg/m^3 로 인쇄한다). "
     "**두 판 대조** — 같은 등급의 최신 개정 20220721 판(`SABIC_HDPE_M300054_TDS_rev-2022-07-21.pdf`) 도 "
     "`Density at 23... | 954 | kg/m³ | ASTM D1505` 로 같은 수를 찍는다. 12 년 사이 MFR·인장·경도 열은 값이 "
     "바뀌었는데(예: Shore D 68 → 60, 1% 시컨트 1200 → 750 MPa) **밀도만 954 로 같다.** "
     "기준온도는 2010 판이 인쇄하지 않고 2022 판의 `Density at 23` 뒤 문자열이 추출에서 깨져 "
     "온도를 단정하지 않았다 — conditions 에 temperature_c 를 두지 않은 이유가 이것이다. "
     "**이 값은 SDS 가 아니라 벤더 TDS 에서 왔다** — 69차 ED 의 SDS 색인 경로가 아니라 곁가지 수확이다. "
     "기존 부재판정(59차 UD)은 Faiz 2014 논문에 밀도 열이 없다는 진술이라 지금도 맞고, 이 값은 그 진술을 "
     "뒤집는 것이 아니라 **다른 문서에서 온 것**이다.")}]})

# ── Ossila SDS 9절 융점 ───────────────────────────────────────────────────
for (name, handle, fname, rev, year, cas, verbatim, vals, is_lit, prodname, chemname) in MP:
    props = []
    for c_deg, bound in vals:
        cond = {"substance_cas": cas, "physical_form": "solid powder (as-supplied sublimed grade)",
                "test_method": "SDS 9절 인쇄값"}
        if bound:
            cond["bound"] = bound
        note = (f"Ossila SDS 9절 verbatim — `{verbatim}`. 같은 절 verbatim `Physical State  Solid: Powder.` · "
                f"`Density  Not known.` · `Relative density  Not known.` — **밀도는 이 문서에 없다.** "
                f"1절 verbatim `Chemical Name  {chemname}` · `CAS No.  {cas}` 로 동정이 걸린다. "
                f"환산 {c_deg} °C + 273.15 = {K(c_deg)} K. ")
        if bound:
            note += ("원문이 구간으로 인쇄해 두 행으로 넣었다 — 이 행이 "
                     + ("하한" if bound == "lower" else "상한") + "이다. ")
        if is_lit:
            note += ("**등급 2 인 이유** — 원문이 값 옆에 `(lit.)` 를 붙여 스스로 문헌 인용임을 밝힌다. "
                     "제조사가 이 로트를 잰 값이 아니므로 method 는 handbook 이고 t1 을 주지 않았다(브리프 3).")
        else:
            note += ("**등급 1 인 이유** — 같은 문서의 다른 항목들과 달리 이 값에는 `(lit.)` 표기가 없다. "
                     "제조사가 이 제품에 대해 스스로 인쇄한 값으로 읽었다.")
        props.append({"key": "thermal.melting_point", "value": K(c_deg), "unit": "K",
                      "method": "handbook" if is_lit else "measured",
                      "tier": 2 if is_lit else 1,
                      "conditions": cond, "notes": note})
    mats.append({"match_name": name,
      "source": {"kind": "datasheet",
        "title": f"Ossila {prodname} Safety Data Sheet (개정 {rev}, 영문)",
        "url": OSSILA % handle, "publisher": "Ossila Ltd", "year": year,
        "local_path": f"{SDS}/{fname}"},
      "properties": props})


# ── KOKI 무연 솔더 페이스트 S3X48/S3X58/S3X70 + M500 — 밀도 ────────────────
KOKI_GRADES = [
 ("무연 솔더 페이스트 S3X48 + M500 플럭스 (Type 3, 분말 20-45 um) — Krammer 2018", "S3X48-M500"),
 ("무연 솔더 페이스트 S3X58 + M500 플럭스 (Type 4, 분말 20-38 um) — Krammer 2018", "S3X58-M500"),
 ("무연 솔더 페이스트 S3X70 + M500 플럭스 (Type 5, 분말 10-25 um) — Krammer 2018", "S3X70-M500"),
]
KOKI_VERB = "· Hustota při 20 °C:                     4-5 g/cm3"
for name, grade in KOKI_GRADES:
    props = []
    for v, bound in ((4.0, "lower"), (5.0, "upper")):
        props.append({
          "key": "physical.density", "value": v * 1000.0, "unit": "kg/m^3",
          "method": "measured", "tier": 1,
          "conditions": {"temperature_c": 20, "grade": grade, "bound": bound,
            "physical_form": "solder paste (SAC305 powder suspended in M500 rosin flux, as supplied)",
            "value_scope": "제품군 공통값 — 이 SDS 한 장이 S3X48-M500 부터 S3X48-A310D-3 까지 34개 상품명을 함께 덮는다"},
          "notes": ("KOKI SDS 9절 verbatim — `" + KOKI_VERB + "`. "
            "같은 절 verbatim `Skupenství:  Pastovité`(성상 = 페이스트) · `Relativní hustota  Není určeno.` · "
            "`Viskozita: Dynamicky  Nedá se použít.`. **환산** — " + str(v) + " g/cm^3 x 1000 = " + str(v*1000.0) + " kg/m^3 "
            "(g/cm^3 은 무차원 비중이 아니라 이미 밀도라 물밀도를 곱하지 않는다). "
            "원문이 구간으로 인쇄해 두 행으로 넣었고 이 행이 " + ("하한" if bound == "lower" else "상한") + "이다. "
            "**형태 검산 — 액상 함정이 아니다.** 9절이 인화점 `Bod vzplanutí: 141 °C` 를 함께 찍지만 "
            "성상 칸이 스스로 `Pastovité`(페이스트) 라 못 박고, 우리 카탈로그 재료 자체가 **미경화 솔더 페이스트**다. "
            "인화점은 플럭스(로진·용제)의 것이고 형태 불일치의 신호가 아니다. "
            "**주의 — 등급 고유값이 아니다.** 1절 상품명 칸이 34개 등급을 한 줄에 늘어놓고 그 전부를 이 한 값이 덮는다. "
            "S3X48/S3X58/S3X70 은 분말 Type 3/4/5 차이(입도 20-45 / 20-38 / 10-25 um)이고 금속 함유율도 다르므로 "
            "4-5 g/cm^3 폭은 그 산포를 그대로 안고 있다. 세 등급에 같은 두 행이 들어가는 이유가 이것이다. "
            "**검산** — SAC305 합금 7.4 g/cm^3, 로진 플럭스 ~0.9 g/cm^3, 9절이 인쇄한 불휘발분 96.0 wt%. "
            "금속 88~90 wt% 페이스트의 체적 금속분율이 대략 0.5 이므로 4~5 g/cm^3 대가 맞는다"
            "(조성으로 값을 만들어 낸 것이 아니라 인쇄값의 물리적 타당성만 본 것이다). "
            "**이 값은 기존 판정을 뒤집는다** — 이 재료의 `core_not_applicable['physical.density']` 는 "
            "'솔더 페이스트라 코어 7물성이 정의되지 않는다' 였는데, 영률·포아송비·인장강도는 그 말이 맞아도 "
            "**밀도는 페이스트에도 정의되고 벤더가 실제로 쟀다.** ed08_verdicts.json 에 철회문을 적었다.")})
    mats.append({"match_name": name,
      "source": {"kind": "datasheet",
        "title": "KOKI S3X48-M500 / S3X58-M500 / S3X70-M500 외 Bezpečnostní list (SDS, EU CLP 1907/2006/ES, 개정 2015-07-10, 체코어판)",
        "url": "https://web.archive.org/web/20160802152021id_/http://koki.org/pdf/BL/sd_-_lead_free_solder_paste-4_(cz).pdf",
        "publisher": "KOKI Company Limited (Higashimatsuyama plant, Saitama, Japan)", "year": 2015,
        "local_path": f"{SDS}/KOKI_S3X48-M500-S3X58-M500-S3X70-M500_SDS_2015-07-10_cz.pdf"},
      "properties": props})


# ── Henkel LOCTITE ABLESTIK 965-1L (옛 Ablebond 965-1L) — 밀도 ────────────
mats.append({
 "match_name": "Ablebond 965-1L silver-filled epoxy die attach adhesive (Ablestik) - Hsiung 2003",
 "source": {"kind": "datasheet",
   "title": "LOCTITE ABLESTIK 965-1L known as Ablebond 965-1L (15g) Safety Data Sheet (Revision Number 005.0, 발행 2018-02-15, 영문)",
   "url": "https://www.henkel-adhesives.com/", "publisher": "Henkel Corporation (Rocky Hill, CT, USA)", "year": 2018,
   "local_path": f"{SDS}/Henkel_LOCTITE-ABLESTIK-965-1L-15g_SDS_2018-02-15.pdf"},
 "properties": [{
   "key": "physical.density", "value": 3400.0, "unit": "kg/m^3", "method": "measured", "tier": 1,
   "conditions": {"grade": "LOCTITE ABLESTIK 965-1L (= Ablebond 965-1L)",
     "physical_form": "uncured silver-filled paste as supplied (100 % solids — 3절에 휘발성 용제가 없다)",
     "temperature_status": "not printed — SDS 가 specific gravity 의 기준온도를 안 적는다"},
   "notes": ("SDS 9절 verbatim — `Specific gravity:  3.4`. 같은 절 verbatim `Physical state:  Liquid, Paste` · "
     "`Color:  Silver` · `Viscosity:  Not available.` · `Flash point:  > 93 °C (> 199.4 °F)`. "
     "**동정** — 1절이 스스로 `Product name: LOCTITE ABLESTIK 965-1L known as Ablebond 965-1L (15g)` 라 적어 "
     "카탈로그 재료명과 문서가 직접 이어진다(추정이 아니다). "
     "**환산** — 비중은 무차원이라 물밀도를 곱해야 한다. 기준온도가 인쇄되지 않아 규율대로 1000 kg/m^3 를 썼고 "
     "그 사실을 여기 밝힌다: 3.4 x 1000 = 3400 kg/m^3. "
     "**두 판 대조** — 개정 006.0(발행 2019-07-31, 6.6 g 포장, IDH 1199778) 도 같은 줄이 `Specific gravity: 3.4` 다. "
     "사본 `" + SDS + "/Henkel_LOCTITE-ABLESTIK-965-1L-6p6g_SDS_2019-07-31.pdf`. "
     "**액상 함정인가 — 아니다, 그리고 그 이유를 문서가 스스로 준다.** 9절에 인화점이 있어 이 배치의 경계 신호에 걸리지만, "
     "3절 조성이 `Silver 70-80 % · Bisphenol-F Epichlorhydrin resin 10-20 % · 1,4-Bis(2,3-epoxypropoxy)butane 5-10 % · "
     "Phenol-formaldehyde polymer 1-5 %` 로 **휘발성 용제가 한 줄도 없다.** "
     "1,4-비스(2,3-에폭시프로폭시)부탄은 반응성 희석제라 경화물에 그대로 남는다 — 68차 DA 가 기각한 Photo-BCB "
     "(메시틸렌 용액)와 결정적으로 다른 자리다. 인화점 93 °C 는 그 희석제의 값이다. "
     "**검산 — 인쇄값이 조성과 맞는다.** 은 10.49 g/cm^3 를 75 wt%, 에폭시 매트릭스 ~1.15 g/cm^3 를 25 wt% 로 놓으면 "
     "1/rho = 0.75/10.49 + 0.25/1.15 = 0.2889 → 3.46 g/cm^3 로, 인쇄된 3.4 와 맞는다"
     "(조성으로 값을 만든 것이 아니라 인쇄값의 타당성만 본 것이다). "
     "**주의** — 이 값은 **미경화 페이스트**의 것이다. 이 재료의 나머지 행(영률 -65~250 °C · 다이쉬어 · Tg · CTE)은 "
     "경화물이라 형태가 다르다. 무용제 100 % 고형분이라 경화수축분(수 %)만큼만 차이 나겠지만 "
     "**그 차이를 우리가 계산해 넣지는 않았다** — conditions.physical_form 을 보고 판단해 써라.")}]})

# ── 3M Scotch-Weld DP100 — 점도(밀도는 기각, 4절 참조) ────────────────────
DP100 = [
 ("3M Scotch-Weld Epoxy Adhesive DP100 Clear (two-part room-temperature-cure epoxy)",
  [("Part A", "3M_DP100-Clear-PartA_SDS_2022-10-10.pdf", "2022-10-10", 2022,
    "Viscosity                                                     8,000 - 15,000 centipoise [@ 73 ºF ]",
    8.0, 15.0, 22.8, "73 ºF"),
   ("Part B", "3M_DP100-Clear-PartB_SDS_2025-06-13.pdf", "2025-06-13", 2025,
    "Viscosity                                                     10,000 - 30,000 centipoise [@ 73.4 ºF ] [Details:MITS data]",
    10.0, 30.0, 23.0, "73.4 ºF")]),
 ("3M Scotch-Weld Epoxy Adhesive DP100 NS Translucent (two-part room-temperature-cure non-sag epoxy)",
  [("Part A", "3M_DP100NS-Translucent-PartA_SDS_2024-07-29.pdf", "2024-07-29", 2024,
    "Viscosity                                                      50,000 - 85,000 centipoise",
    50.0, 85.0, None, None),
   ("Part B", "3M_DP100NS-Translucent-PartB_SDS_2024-11-11.pdf", "2024-11-11", 2024,
    "Viscosity                                                      90,000 - 150,000 centipoise [@ 73.4 ºF ] [Details:MITS data]",
    90.0, 150.0, 23.0, "73.4 ºF")]),
]
for name, parts in DP100:
    for (part, fname, rev, year, verb, lo, hi, tc, tprint) in parts:
        props = []
        for v, bound in ((lo, "lower"), (hi, "upper")):
            cond = {"component": part, "bound": bound,
                    "physical_form": "uncured component as supplied (9절 `Physical state Liquid` · `Specific Physical Form Viscous`)"}
            if tc is not None:
                cond["temperature_c"] = tc
            else:
                cond["temperature_status"] = "not printed — 이 판 9절이 점도에 온도를 안 적는다"
            props.append({"key": "rheological.viscosity", "value": v, "unit": "Pa*s",
              "method": "measured", "tier": 1, "conditions": cond,
              "notes": ("SDS 9절 verbatim — `" + verb + "`. "
                "**환산** — 1 cP = 0.001 Pa*s 이므로 " + ("%g" % (v*1000)) + " cP x 0.001 = " + ("%g" % v) + " Pa*s. "
                + ("원문 기준온도 `" + tprint + "` 를 섭씨로 옮겨 " + str(tc) + " °C 로 적었다. " if tprint else
                   "이 판은 점도에 기준온도를 인쇄하지 않아 conditions 에 온도를 두지 않았다. ")
                + "원문이 구간으로 인쇄해 두 행으로 넣었고 이 행이 " + ("하한" if bound == "lower" else "상한") + "이다. "
                "**이 값은 " + part + " 단독의 것이다** — DP100 은 2액형이고 이 SDS 는 한쪽 액만 기술한다. "
                "혼합액 점도가 아니며 우리가 두 액에서 혼합값을 만들어 내지도 않았다. "
                "**같은 9절의 밀도(`Density 1.15~1.18 g/ml`)는 넣지 않았다** — 9절이 스스로 "
                "`Physical state Liquid` · `Specific Physical Form Viscous` · 인화점 · 점도를 같이 찍어 "
                "**미경화 액상**임을 못 박기 때문이다. 이 재료의 나머지 행은 경화물 물성이다(랩전단·압축강도·Tg·CTE). "
                "점도는 미경화 상태에만 정의되는 물성이라 형태 불일치가 없다 — 그래서 이것만 넣었다.")})
        mats.append({"match_name": name,
          "source": {"kind": "datasheet",
            "title": "3M(TM) Scotch-Weld(TM) Epoxy Adhesive " + name.split("Adhesive ")[1].split(" (")[0] + ", " + part + " Safety Data Sheet (발행 " + rev + ", 영문)",
            "url": "https://www.3m.com/3M/en_US/company-us/SDS-search/",
            "publisher": "3M Company", "year": year,
            "local_path": f"{SDS}/{fname}"},
          "properties": props})


# ── Teijin DuPont Films — Tetoron(PET) · Teonex(PEN) 구판 MSDS ────────────
SCOPE_NOTE = ("**등급 3 인 이유** — 출처 논문(Low 2005)은 필름을 `optical-grade ... film (Teijin)` 로만 부르고 "
  "**등급 코드를 인쇄하지 않는다**. 이 MSDS 도 개별 등급이 아니라 **필름 계열 한 장**이다. "
  "즉 이 값은 '그 등급에 인쇄된 값'(t1)이 아니라 **그 등급이 속한 벤더 계열의 인쇄값**이라 t3 로 두고 "
  "`grade_scope` 를 달았다. 등급이 특정되면 t1 로 올릴 수 있다.")

TEIJIN = [
 ("PET optical-grade film 188 um (Teijin) — Low 2005 AlxOy barrier substrate",
  "Teijin(R) Tetoron(R) Film : Clear Type",
  "Teijin-DuPont-Films_Tetoron-Film-Clear-type_MSDS_2001-09-14.html", "2001-09-14", 2001,
  "Bi-axially Oriented PET Film", "25038-59-9",
  "Appearance : Transparent sheet-shaped solid · Melting point : 258 C · Specific gravity : 1.4 g/cm 3 · Volatility : Not volatile · Flash point : None",
  [(1400.0, None)], 258.0,
  "Teijin Tetoron Film Clear Type — 테이진의 투명 이축연신 PET 필름 계열 전체"),
 ("PEN optical-grade film 200 um (Teijin) — Low 2005 AlxOy barrier substrate",
  "Teonex(R)",
  "Teijin-DuPont-Films_Teonex-PEN-Film_MSDS_2000-01-13.html", "2000-01-13", 2000,
  "Bi-axially Oriented PEN Film", "25853-85-4",
  "Appearance : Transparent sheet-shaped solid · Melting point : 269 C · Specific gravity : 1.35-1.36 g/cm 3 · Volatility : Not volatile · Flash point : None",
  [(1350.0, "lower"), (1360.0, "upper")], 269.0,
  "Teijin Teonex — 테이진의 이축연신 PEN 필름 계열 전체"),
]
for (name, trade, fname, rev, year, chem, cas, verb, dens, mp_c, scope) in TEIJIN:
    props = []
    for v, bound in dens:
        cond = {"physical_form": "biaxially oriented film (`Transparent sheet-shaped solid`)",
                "grade_scope": scope, "trade_name": trade,
                "temperature_status": "not printed — MSDS 가 비중에 기준온도를 안 적는다"}
        if bound:
            cond["bound"] = bound
        props.append({"key": "physical.density", "value": v, "unit": "kg/m^3",
          "method": "measured", "tier": 3, "conditions": cond,
          "notes": ("MSDS `Physical and Chemical Properties` 절 verbatim — `" + verb + "`. "
            "**환산** — 원문이 `g/cm 3` 단위를 함께 인쇄하므로 이미 밀도다(무차원 비중이 아니라 물밀도를 곱할 필요가 없다). "
            + ("%g" % (v/1000.0)) + " g/cm^3 x 1000 = " + ("%g" % v) + " kg/m^3. "
            + ("원문이 구간으로 인쇄해 두 행으로 넣었고 이 행이 " + ("하한" if bound == "lower" else "상한") + "이다. " if bound else "")
            + "**동정** — 문서 2절 verbatim `Chemical Name  " + chem.replace("Bi-axially Oriented ", "") + "` · `CAS No. " + cas + "`, "
            "제품명 `" + chem + "` · 상표 `" + trade + "`. "
            "**액상 함정이 아니다** — 같은 절이 `Volatility: Not volatile` · `Flash point: None` 이고 외관이 고체 시트다. "
            "**두 판 대조** — 여섯 해 뒤 개정판(2006-05-19, 스캔 PDF 라 `pdftoppm` 으로 렌더해 읽었다)이 같은 칸에 "
            "같은 수를 찍는다(Tetoron `Specific gravity 1.40 g/cm3` · Teonex `Specific gravity 1.35-1.36 g/cm3`). "
            "사본 `" + SDS + "/Teijin-DuPont-Films_Tetoron-Film-Clear-type_MSDS_2006-05-19.pdf` · "
            "`" + SDS + "/Teijin-DuPont-Films_Teonex-Film_MSDS_2006-05-19.pdf`. "
            + SCOPE_NOTE)})
    props.append({"key": "thermal.melting_point", "value": round(mp_c + 273.15, 2), "unit": "K",
      "method": "measured", "tier": 3,
      "conditions": {"physical_form": "biaxially oriented film", "grade_scope": scope, "trade_name": trade},
      "notes": ("같은 절 verbatim — `Melting point : " + ("%g" % mp_c) + " C`. 환산 " + ("%g" % mp_c) + " + 273.15 = "
        + str(round(mp_c + 273.15, 2)) + " K. 2006-05-19 개정판도 같은 수를 찍는다(두 판 대조). " + SCOPE_NOTE)})
    mats.append({"match_name": name,
      "source": {"kind": "datasheet",
        "title": "Teijin DuPont Films " + trade + " MSDS (최종개정 " + rev + ", 영문)",
        "url": "https://www.teijin.com/", "publisher": "Teijin DuPont Films Japan Limited", "year": year,
        "local_path": f"{SDS}/{fname}"},
      "properties": props})

out = pathlib.Path(__file__).with_name("ed07_materials.json")
out.write_text(json.dumps({"batch": "69차 ED", "materials": mats}, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", out, "materials", len(mats), "rows", sum(len(m["properties"]) for m in mats))
