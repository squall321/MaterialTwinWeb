# 58차 TD — housing V5 93칸 분해 판정(일회용). 재료마다 한 행(브리프 610).
import json
RHO="physical.density"; E="mechanical.youngs_modulus"; NU="mechanical.poisson_ratio"
CTE="thermal.expansion_linear"; K="thermal.conductivity"; CP="thermal.specific_heat"
UTS="mechanical.tensile_strength"
CORE7=[RHO,E,NU,CTE,K,CP,UTS]
TD="58차 TD"
V=[]
def add(mid,name,**kw): V.append(dict(material_id=mid,name=name,**kw))
def spread(keys,r): return {k:r for k in keys}

# ── (A) 점착테이프 20종 × 인장강도 → V2 ────────────────────────────────────────
TAPE_HEAD=("[V5 → V2 · 브리프 127·613] 이 계통의 남은 코어 빈칸은 인장강도 한 칸뿐이라 58차 TD 가 "
 "20종의 벤더 문서를 **전부 실제로 받아 전권 낱말 검색**을 걸었다(브리프 613 — 부재 판정의 가장 싼 증거는 "
 "전권 낱말 검색이다). 결과: 열여덟 문서에서 `tensile`/`Zugfestigkeit`/`Reissfestigkeit` **총 1건**이고 "
 "그 1건마저 값이 아니라 `NA` 다(아래 344 참조). 점착테이프 시트가 강도축으로 인쇄하는 것은 "
 "박리력(N/25 mm · N/100 mm)·전단유지력·택·SAFT·두께·내열구간이다 — 인장강도는 **자립 시편이 아니라 "
 "기재(carrier)의 성질**이라 이 갈래의 판정축이 아니다. `coverage_report` 의 `_TAPE` UNFILLABLE 선언이 "
 "이미 CTE·비열·영률·항복강도·Prony 를 담고 있는데 **인장강도만 빠져 있어** 이 20칸이 세 파동 동안 "
 f"'진짜 남은 것' 으로 세어졌다. — {TD}\n\n열어 본 문서: ")
NITTO="Nitto `Mounting Tapes 2025 (EN)` 제품 카탈로그(358줄 전권, `tensile` 0건). 인쇄 열은 두께·라이너·접착력(N/20mm)·응집력·SAFT·설명뿐이다."
def tape(mid,name,doc): add(mid,name,core_absent_from_vendor_sheet={UTS:TAPE_HEAD+doc})
for mid,name in ((336,"Nitto No.500 double-coated tape 0.16mm"),
                 (337,"Nitto No.5015E double-coated tape 0.16mm"),
                 (338,"Nitto No.5050S double-coated tape 0.105mm")):
    tape(mid,name,NITTO)
LOH=("Lohmann `DuploCOLL {g}` technical data sheet(`tensile` 0건). 인쇄 항목은 제품구성(라이너·접착제·기재)·"
     "온도구간·DIN EN 1939 박리력(피착재별)·DIN EN 1943 전단강도·Tack Loop·시공온도·보관·규격뿐이다.")
for mid,name,g in ((339,"Lohmann DuploCOLL 330 (perm/peel PET 0.16mm)","330"),
                   (340,"Lohmann DuploCOLL 365.2 (pure acrylic PET 0.54mm)","365.2"),
                   (355,"Lohmann DuploCOLL 918 (1.15mm pure acrylic)","918"),
                   (356,"Lohmann DuploCOLL 9042 (0.76mm pure acrylic)","9042"),
                   (357,"Lohmann DuploCOLL 200 (0.23mm dispersion acrylic)","200"),
                   (358,"Lohmann DuploCOLL 56003 (2.10mm pure acrylic)","56003"),
                   (359,"Lohmann DuploCOLL VP 6504 (0.15mm thin film tape)","VP 6504"),
                   (366,"Lohmann DuploCOLL 2501 (0.12mm rubber double-coated film)","2501")):
    tape(mid,name,LOH.format(g=g))
AD=("Avery Dennison `{g}` Technical Data Sheet(`tensile` 0건). 인쇄 항목은 두께(ASTM D-3652, 라이너/기재/합계)·"
    "피착재별 박리력(PSTC-101 · ASTM D-3330)·전단·내열구간·보관뿐이다.")
for mid,name,g in ((341,"Avery Dennison AFT Clear 1000 (1mm acrylic foam adhesive)","AFT CLEAR 1000"),
                   (342,"Avery Dennison FT F2001 MAT (43um acrylic transfer)","FT F2001 MAT"),
                   (346,"Avery Dennison OF 2429 (134um heat-sensitive LDPE film tape)","OF 2429"),
                   (352,"Avery Dennison XD 3827 (94um double-sided tape)","XD 3827"),
                   (354,"Avery Dennison FT 2018 (0.147mm modified acrylic transfer tape)","FT 2018"),
                   (367,"Avery Dennison FT B (0.21mm double coated tape)","FT B"),
                   (368,"Avery Dennison FT D (0.23mm double coated tape)","FT D"),
                   (382,"Avery Dennison FT Series Rubber Adhesive Transfer Tape","FT 2162 / FT 167")):
    tape(mid,name,AD.format(g=g))
tape(344,"Avery Dennison FT F2070 (45um acrylic transfer)",
 "Avery Dennison `FT F2070` Technical Data Sheet. **`tensile` 1건이 여기 있는데 값이 아니다** — "
 "`CARRIER DATA` 블록의 `Thickness (µ)` · `Tensile (N/15 mm)` · `Elongation (%) (max)` 세 행이 전부 `NA` 다. "
 "F2070 은 기재 없는 전사테이프라 기재 열 자체가 성립하지 않는다. **이것은 부재가 아니라 벤더의 판정이다"
 "(브리프 614)** — 다음 파동이 이 등급의 시트를 다시 찾지 않게 사유에 못박는다. 그리고 인쇄 단위가 "
 "`N/15 mm`, 즉 **폭당 힘이지 응력이 아니다** — 값이 있었더라도 `mechanical.tensile_strength`(Pa) 로 넣으려면 "
 "두께로 나눠야 하고 그것은 우리가 나누는 것이라 금지선 안이다(브리프 43).")

# ── (B) 폴리머 — 문서를 열어 확인한 구조적 부재 ────────────────────────────────
add(276,"Stanyl TW341 (PA46, Envalior)",
 core_absent_from_vendor_sheet={UTS:
  "[V5 → V2 · 브리프 127·454] 58차 TD 가 이 재료의 기존 출처 두 시트를 다시 받아 전권 검색했다 — "
  "① CAMPUS Property Data `Stanyl TW341 PA46 (heat stabilized, lubricated)`(plastore.it 사본) · "
  "② `Property Data — Stanyl TW341 PA46`(2025 인쇄본, sunpolymersindia 사본). "
  "**둘 다 `Tensile strength`·`Stress at break` 0건**이고 인쇄하는 것은 `Stress at yield`(건조 100 MPa / "
  "조습 55 MPa, 이미 DB 에 4행)와 `Strain at break` 40% 다. **파단 전에 항복하는 연성 수지라 "
  "ISO 527 시트가 항복응력만 찍는 것**이고 이름을 바꿔 넣으면 지어내는 것이 된다(브리프 454 — 규격시험이 "
  "무엇을 재는지가 무엇이 인쇄되는지를 정한다). 브리프 6 의 곁가지도 확인했다 — 두 시트 다 `Poisson` 0건인데 "
  f"이 재료의 ν 는 이미 t4 클래스 가정으로 차 있다. — {TD}"})

add(645,"Vectra A950RX LCP (Ticona, neat, Miller 2006)",
 core_absent_from_vendor_sheet=spread([NU,CP],
  "[V5 → V2 · 브리프 127·613] 유일한 출처 Miller 2006(10.1002/pc.20231)의 `Vectra A950RX` 물성표는 "
  "제조사(Ticona) 데이터시트를 저자가 전재한 것인데(`provenance: vendor datasheet (Ticona), ref [26]`), "
  "그 표 전권에 **`Poisson` 0건 · `specific heat` 0건**이다. 인쇄 행은 인장강도·인장탄성률·굴곡탄성률·"
  "노치아이조드·밀도·체적/표면저항·열전도율·CTE(MD/TD)·융점·흡습·성형수축뿐이다. "
  "브리프 6·613 의 재현이다 — 사출 폴리머 시트는 포아송비를 구조적으로 안 찍고, 비열은 "
  "`ASTM E1269 줄이 그 시트에 있는가` 로 갈리는데 없다(브리프 50·77). "
  f"⚠ 상위 문서 층(Celanese/Avient 의 Vectra LCP Design Guide)은 조달에 실패해 안 열린 채로 남는다(브리프 601). — {TD}"))

add(1161,"Celanex 3300 D PBT, 30% glass filled, as received untreated control (Ticona, O'Neill 2008)",
 core_absent_from_vendor_sheet=spread([NU,K,CP],
  "[V5 → V2 · 브리프 127·613] 58차 TD 가 이 재료의 기존 출처인 Celanese `CELANEX 3300D Polybutylene "
  "Terephthalate — Technical Data` 시트를 다시 받아 전권 검색했다(337줄). "
  "**`Poisson` 0건 · `specific heat` 0건 · `thermal conductivity` 0건 · 단위문자열 `W/m`·`J/kg` 0건**이다. "
  "이 시트는 온도별 인장강도·인장탄성률·연신·굴곡응력·밀도·CTE(MD/TD, ISO 11359-2 `CLTE`)·Tg·Tm·HDT·Vicat·"
  "유전율·유전정접·CTI·체적저항만 인쇄한다 — **CTE 는 찍고 열전도율은 안 찍는 IPC/CAMPUS 서식**이다. "
  "그 시트에서 이미 22행을 캐 갔으므로 브리프 602 의 '옆 칸' 검사를 이 파동이 실제로 돌렸고 "
  f"세 칸은 옆 칸이 아니라 없는 칸이었다. — {TD}"))

_pes=("[V5 → V2 · 브리프 127·613·615] 세 등급의 유일한 출처는 Thompson 1983 "
 "`Polyethersulphone — A Thermoplastic PCB Substrate`(10.1108/eb043698) 한 편이고, 58차 TD 가 "
 "전문(31.8 KB)에 낱말 검색을 걸었다 — **`Poisson` 0건 · `specific heat` 0건**, `thermal conduct` 1건은 "
 "본문의 '증가시킬 수 있다' 라는 서술이지 값이 아니다. 논문이 인쇄하는 표는 다섯이다 — "
 "Table 1 일반물성(비중·굴절률·성형수축·유리함량) · Table 2 기계물성 · Table 3 열물성 · Table 4 난연 · "
 "Table 5 전기물성. **Table 2 의 강성축은 굴곡탄성률(ASTM D790)뿐이고 인장탄성률 행이 없다** — "
 "브리프 613 의 '강성축이 시트마다 다른 양으로 인쇄된다' 가 그대로 재현된다. Table 3 은 HDT·Vicat·CTE·"
 "UL746 온도지수만 담고 열전도율·비열 행이 없다. "
 "**벤더 문서 층도 닫혀 있다** — `Victrex 200P/300P/420P/430P` 는 ICI 의 PES 등급명인데 Victrex 사는 "
 "현재 PEEK 전업이고 PES 사업은 다른 회사로 넘어가 등급 코드가 바뀌었다. 이름이 비슷한 후속 등급의 값을 "
 "옮기는 것은 브리프 586·22 위반이라 하지 않았다. 브리프 609 의 '열 시트가 존재하지 않는다' 에 가까운 자리인데 "
 f"집계가 읽는 칸이 아직 없어 V2 에 적고 사유에 그 차이를 못박는다(57차 SA 와 같은 처리). — {TD}")
for mid,name in ((1370,"Victrex PES 200P/300P, unreinforced polyethersulphone (ICI, Thompson 1983)"),
                 (1371,"Victrex PES 420P, 20% glass-reinforced polyethersulphone (ICI, Thompson 1983)"),
                 (1372,"Victrex PES 430P, 30% glass-reinforced polyethersulphone (ICI, Thompson 1983)")):
    add(mid,name,core_absent_from_vendor_sheet=spread([E,NU,K,CP],_pes))

add(2319,"Ertalyte — 폴리에틸렌 테레프탈레이트 PET (Böhm 1990)",
 core_absent_from_vendor_sheet=spread([NU,CP],
  "[V5 → V2 · 브리프 127·613] 58차 TD 가 이 재료의 기존 출처 `Ertalyte(TM) PET-P Product Datasheet`"
  "(Mitsubishi Chemical Advanced Materials, rev. 04/12/2024)를 다시 받아 전권 검색했다 — "
  "**`Poisson` 0건 · `specific heat` 0건 · `J/(kg` 0건**이다. 이 시트는 밀도·인장강도·인장탄성률·연신·"
  "압축·경도·열전도율(0.29 W/(K·m) — 이미 DB)·CTE 세 구간(이미 DB 3행)·융점·HDT·마찰계수·흡수율을 "
  "인쇄하지만 포아송비 행과 비열 행이 없다. **이 재료의 코어 5칸이 전부 이 한 시트에서 왔다** — "
  f"브리프 602 의 옆 칸 검사를 돌렸고 남은 둘은 옆 칸이 아니라 없는 칸이었다. — {TD}"))

# ── (C) 금속 — 문서를 열어 확인한 구조적 부재 ─────────────────────────────────
add(2262,"6082-T6 aluminium alloy, commercial quality bar, bending-torsion fatigue specimen (Kluger 2015)",
 core_absent_from_vendor_sheet=spread([NU,CP],
  "[V5 → V2 · 브리프 127] 58차 TD 가 이 등급의 코어를 닫으려고 문서 셋을 열었다 — "
  "① Nedal Aluminium `ALLOY DATA SHEET EN-AW 6082 [AlMgSi]`(Rev. 02, 2018-02) → 물리물성 표에서 "
  "밀도 2700 · CTE 23.4e-6 · 열전도율 170-220 을 얻어 이 파동에 넣었다. **그 표에 `Poisson` 0건 · "
  "`specific heat` 0건**이고 열 구성은 밀도·융점구간·전기전도도·열전도율·CTE·탄성계수 여섯뿐이다. "
  "② Aalco `Aluminium Alloy 6082 T6~T651` 데이터시트 → 같은 여섯 열이고 역시 ν·비열이 없다. "
  "③ 원 출처 Kluger 2015(10.1016/j.ijfatigue.2015.05.005) 전문 → `Poisson` 0건 · `specific heat` 0건, "
  "`density` 1건은 `Power Spectral Density` 다. "
  "⚠ 편찬 사이트는 값을 주지만 **등급값이 아니라 클래스값이다** — makeitfrom.com 은 6013·2017A·6082·7075 "
  "넷에 ν 0.33/0.33/0.33/0.32 · 비열 900/880/870 J/(kg·K) 를 인쇄하는데, 같은 페이지의 밀도가 "
  "7075-T651 3.0 g/cm³(참값 2.81, +6.8%) · 6013 2.8(참값 2.71) 로 **유효숫자 두 자리로 뭉개져 틀렸다.** "
  f"두 자리로 뭉갠 편찬값은 이 등급의 값이 아니므로 넣지 않았다(브리프 616 의 '그 숫자가 이 등급 것이냐'). — {TD}"))

add(2559,"Al 7003 extrusion alloy (EN AW-7003, AlZn6Mg0.8Zr)",
 core_absent_from_vendor_sheet=spread([NU,CP],
  "[V5 → V2 · 브리프 127·602] 58차 TD 가 이 재료의 기존 출처 Nedal Aluminium `EN AW-7003 [AlZn6Mg0.8Zr]` "
  "데이터시트(Rev. 02, 2018-02)를 다시 받아 전권 검색했다 — **`Poisson` 0건 · `specific heat` 0건**이다. "
  "물리물성 표(`Physical properties (approximate values, 20°C)`)의 열은 밀도·융점구간·전기전도도·열전도율·"
  "CTE·탄성계수 여섯이고 이 재료의 코어 다섯 칸이 이미 그 한 행에서 다 왔다(2770 | 600-650 | 19-23 | "
  "130-160 | 23.1 | ~70). 즉 옆 칸 검사(브리프 602)를 돌렸고 남은 둘은 그 표에 없는 칸이다. "
  f"편찬 사이트의 두 자리 클래스값은 넣지 않았다(2262 판정의 makeitfrom 검증 참조). — {TD}"))

add(2560,"Al 6013 sheet alloy (AA6013, Al-Mg-Si-Cu)",
 core_absent_from_vendor_sheet=spread([RHO,E,NU,CTE,K,CP],
  "[V5 → V2 · 브리프 127] 58차 TD 가 이 재료의 기존 출처 `Alcoa Technical Fact Sheet — Alloy 6013 Sheet, "
  "Maximum Strength 6XXX Series Sheet`(rev. 5/07, 로컬 사본)를 열어 전권 검색했다 — "
  "**`Density`·`Modulus`·`Thermal`·`Specific`·`Expansion`·`Poisson` 이 전부 0건**이다. "
  "이 시트에는 **물리물성 블록 자체가 없다** — 장 구성이 서론 · 화학조성한계 · 기계물성(6013-T4/T6 와 "
  "6061-T6·7021·7029/7129 비교) · 성형 · 접합 · 인공시효 · 부식 · 마감뿐이다. 6013 은 Alcoa 가 등록한 "
  "합금이고 이 문서가 그 벤더 문서다. 다음 문서 층은 Aluminum Association `Aluminum Standards and Data`"
  f"(유료)이고 이 파동에서는 못 열었다. 편찬 사이트의 두 자리 클래스값은 넣지 않았다(2262 판정 참조). — {TD}"))

# ── (D) 계보 — 대표 레코드가 코어를 담는다(V1) ────────────────────────────────
add(1364,"7075-T651 aluminium alloy plate 10 mm, parent metal (Southwest Aluminum, Li 2018)",
 core_not_applicable=spread([RHO,E,NU,CTE,K,CP],
  "[V5 → V1 계보 · 브리프 623·586·116·123] 이 레코드는 Li 2018(10.3390/ma11030379)이 PVPPA 용접부를 재면서 "
  "**모재로 쓴 10 mm 판재**다 — 존재 이유는 그 판재에서 잰 UTS 589.2 · YS 535.3 · 연신 12% · HV 150 이고, "
  "그 넷은 이미 들어 있다. 코어의 나머지 여섯은 판재가 아니라 **합금**의 것이고 카탈로그에 그 대표 레코드가 "
  "이미 있다 — 재료 23 `Al7075-T6 Bilinear` 가 ρ 2810 · E 71.7 GPa · ν 0.33 · CTE 2.36e-5 · k 130 · "
  "Cp 960 을 담고 있고, **그 출처(src1847)의 제목이 `ASM Material Data Sheet — Aluminum 7075-T6; 7075-T651` "
  "로 T651 을 명시한다.** 여기 복제하면 이중 계상이다. 그리고 Li 2018 자신은 이 여섯 중 한 줄도 인쇄하지 "
  f"않는다(Table 1 은 조성 규격만 담는다). — {TD}"),
 catalog_twin=("재료 23 `Al7075-T6 Bilinear` 가 이 합금의 대표 레코드다 — 코어 7 을 다 담고 출처 "
  "`ASM Material Data Sheet — Aluminum 7075-T6; 7075-T651` 이 T651 을 제목에 명시한다. 이 레코드는 "
  f"Li 2018 의 특정 10 mm 판재(Southwest Aluminum) 모재 실측 4행을 담는 변종 시료다. {TD}."))

add(2432,"Type 316 austenitic stainless steel bar, solution-annealed 1050 C + water-quenched (Yamaguchi 1980)",
 core_not_applicable=spread([RHO,E,NU,CTE,K,CP],
  "[V5 → V1 계보 · 브리프 623·586·116·123] 이 레코드는 Yamaguchi 1980(10.1007/bf02655121)이 "
  "**고온 저주기피로·크리프**를 재려고 쓴 Type 316 봉재다 — 존재 이유는 온도별 인장·크리프파단 30여 행이고 "
  "그 값들은 이미 들어 있다(UTS 665/480/326 MPa · YS · 연신 · 단면감소율 · 진파단연성). 코어의 나머지 여섯은 "
  "이 시편이 아니라 **강종**의 것이고 카탈로그에 그 대표 레코드가 이미 있다 — 재료 5 "
  "`SUS316_annealed Bilinear`(같은 subsystem housing, role product)가 ρ 8000 · E 193 GPa · ν 0.27/0.265 · "
  "CTE 1.59e-5 · k 16.3 · Cp 500 · UTS 를 담는다. Type 316 = SUS316 = EN 1.4401 이고 이 레코드의 "
  "`composition_note`(C 0.07 · Si 0.53 · Mn 1.66 · Ni 10.73 · Cr 16.75 · Mo 2.23 wt%)가 규격 범위 안이며 "
  "열처리(고용화 1050 °C + 수냉)도 재료 5 의 `annealed` 와 같은 상태다. 여기 복제하면 이중 계상이다. "
  f"그리고 Yamaguchi 1980 자신은 이 여섯 중 한 줄도 인쇄하지 않는다. — {TD}"),
 catalog_twin=("재료 5 `SUS316_annealed Bilinear` 가 이 강종의 대표 레코드다(코어 7 을 다 담는다). "
  "Type 316 = JIS SUS316 = EN 1.4401. 이 레코드는 Yamaguchi 1980 의 고온 피로·크리프 축을 담는 "
  f"특정 열(heat)의 시편이다. {TD}."))

# ── (E) 인쇄됐으나 기각(V6) ───────────────────────────────────────────────────
add(2376,"Zinc HF high-fluidity zinc die casting alloy (NADCA, Zn-4.5Al-0.01Mg)",
 core_rejected_printed_value={CTE:
  "[V5 → V6 인쇄됐으나 기각 · 브리프 603·25·129] NADCA `Zinc HF Alloy Typical Properties` 단독표는 CTE 를 "
  "**두 단위로 인쇄하는데 둘이 서로 안 맞는다** — `µ in/in°F at 68-212 °F  16.5` 와 "
  "`(µ m/m°K) at 20-100 °C  26.2`. 온도구간은 같은 구간이고(68-212 °F = 20-100 °C) 환산은 ×1.8 이므로 "
  "16.5 → 29.7 이어야 하는데 인쇄 SI 는 26.2 다(**13% 어긋난다**). 유효숫자 세 자리라 반올림으로 못 덮는다. "
  "**추출 손상이 아니다** — 400 dpi 렌더로 확인했고 md·pdftotext·렌더가 셋 다 16.5 / 26.2 다(브리프 603). "
  "**판 오식도 아니다** — 2015 판(A-3-14-15)의 같은 칸도 글자 그대로 16.5 / 26.2 다(브리프 615). "
  "**같은 표의 다른 두 칸은 닫힌다** — 열전도율 65.3 BTU/ft·hr·°F × 1.7307 = 113.0 W/(m·K) 로 정확히 맞고, "
  "비열 0.1 BTU/lb°F 는 유효숫자 한 자리라 403 J/(kg·K) 를 반올림 구간 안에 담는다. **어긋난 칸이 CTE 하나뿐**"
  "이라 그 칸만 버린다(브리프 141). 어느 쪽이 참인지는 안 닫힌다 — 같은 문서의 자매합금 ZAMAK 3(Zn-4Al)이 "
  "15.2 / 27.4 로 자기정합인데 Zinc HF 는 조성이 거의 같은 Zn-4.5Al 이므로 27.4 근처가 기대값이다. "
  "SI 26.2 는 -4.4%, 환산 29.7 은 +8.4% 로 **SI 쪽이 더 가깝지만 4.4% 는 거의 같은 합금에 대해 닫혔다고 할 "
  "수 없다.** 조성 혼합칙(체적비 Zn 0.889 · Al 0.111 → 29.4e-6)은 금속간상 때문에 계통적으로 높게 나와 "
  "심판이 못 된다(같은 규칙을 ZAMAK 3 에 걸면 29.4 대 인쇄 27.4). "
  f"→ 심판이 없으므로 두 값 다 안 넣는다(브리프 25). 같은 표의 비열·열전도율은 이 파동에 넣었다. — {TD}"})

add(2388,"PMMA/ABS laminated insert-molding decorating film, PMMA 0.05 mm / ABS 0.45 mm (Nissha Printing, Baek 2008)",
 core_rejected_printed_value={
  E:"[V5 → V6 · 브리프 3] Baek 2008 Table 2 는 제목이 `Material properties of the resin and film used in this "
    "study for **numerical simulation**` 이라 브리프 3 의 정중앙이다 — 저자가 해석을 돌리려고 모아 놓은 "
    "입력값이고 측정법이 인쇄돼 있지 않다(측정법을 밝힌 것은 CTE 한 칸뿐이다: `determined by experiments as "
    "-4.2 × 10-5 K-1`). Film 열의 `Elastic modulus 2240 MPa` 는 각주도 인용표시도 없고 같은 논문의 다른 표가 "
    "재구성하지도 않는다(브리프 622 의 조건을 못 채운다). 밀도는 고상/용융 쌍이 서로를 검산해 넣었지만 "
    f"이 칸에는 그런 심판이 없다. — {TD}",
  "mechanical.poisson_ratio":
    "[V5 → V6 · 브리프 3·25·605] 같은 Table 2 의 ν 행은 `Resin(Lupoy HR 5007AB) 0.23` · `Film(Techno ABS545) "
    "0.392` 다. **Resin 값 0.23 이 물리적으로 못 믿을 값이다** — PC/ABS 계 사출수지의 포아송비는 0.35~0.42 "
    "대이고 0.23 은 열가소성 수지가 아니라 취성 세라믹·유리 대역이다. 한 표의 두 칸 중 하나가 그 정도로 "
    "벗어나면 그 행(열)의 출처를 못 믿는다(브리프 25 — 자기모순이면 양쪽을 다 버려라). 게다가 이 표는 "
    "FE 입력표라 브리프 3 의 '포아송비가 관용값이고 각주가 없으면 가정이다' 판별에도 걸린다. "
    f"0.392 만 골라 넣으면 남의 해석 가정을 우리 실측으로 세탁하는 것이 된다. — {TD}",
  K:"[V5 → V6 · 브리프 3] Table 2 Film 열의 `Thermal conductivity 0.116 W/m·°C (at 75 °C, temperature "
    "dependent)` 는 측정법도 각주도 없는 해석 입력값이다. 같은 논문의 다른 표가 재구성하지 않아 브리프 622 의 "
    f"예외에 못 들어간다. — {TD}",
  CP:"[V5 → V6 · 브리프 3·20] Table 2 Film 열의 `Specific heat 2202 J/kg·°C (at 200 °C, temperature "
     "dependent)` 는 측정법이 없을뿐더러 **인쇄된 조건이 200 °C 다** — 이 필름의 사용·해석 온도(성형 후 "
     "80 °C 어닐)와 전혀 다른 상태의 값이고 ABS 의 상온 비열(약 1400 J/(kg·K))과 1.6배 갈린다. "
     f"조건을 빼고 옮기면 그 값은 자체 모순이 된다. — {TD}"},
 core_next_target=("[58차 TD] 인장강도 한 칸이 남았다. Baek 2008 은 이 필름의 인장강도를 인쇄하지 않는다"
  "(논문이 재는 것은 휨량·수축률이다). 다음 문서 층은 논문이 Film 열 머리에 밝힌 등급명 "
  "`Techno ABS545`(Techno Polymer / 현 Techno-UMG) 의 ABS 시트다 — 이 파동에서는 조달을 시도하지 않았다. "
  "⚠ 등급 주의 — 카탈로그 재료는 PMMA 0.05 / ABS 0.45 mm **적층 필름**이고 Techno ABS545 는 그 기재층이다. "
  f"기재 시트의 인장강도를 적층 필름에 옮기려면 그 차이를 조건에 못박아야 한다(브리프 123·140). {TD}."))

# ── (F) 진짜 남은 것 — 다음 표적을 못박는다(집계는 V5 로 센다) ─────────────────
add(1083,"Nylon 6,6 Zytel 101 NC010, unfilled injection-moulded plaque (Heiser 2004 factorial baseline)",
 core_next_target=("[58차 TD — V5 로 남긴다. 이유와 다음 한 걸음] 이 재료의 코어 빈칸 6(ρ·E·ν·CTE·비열·인장강도)은 "
  "**한 문서만 더 열면 닫힐 가능성이 높다.** 이미 붙어 있는 출처 src3684 `DuPont Zytel 101L NC010 — Product "
  "Information (rev. 2018-03-27)` 를 58차 TD 가 다시 열어 보니 그 시트가 "
  "**`Tensile Modulus 3100/1400 MPa` · `Poisson's ratio 0.37/0.43 (ISO 527-1/-2)` · "
  "`Coeff. of linear therm. expansion, parallel 100 E-6/K · normal 110 E-6/K` · `Density 1140 kg/m³` 를 "
  "전부 인쇄한다**(브리프 602 의 옆 칸 — 앞 배치는 이 시트에서 유전율·유전정접 두 줄만 캐 갔다). "
  "**그런데 등급이 101L 이고 카탈로그 재료는 101 이다.** 이 재료의 기존 두 행은 46차가 "
  "`grade_substitution: Zytel 101L NC010 -> Zytel 101 NC010` 을 달되 **독립 문서인 UL Prospector 의 "
  "`Zytel 101F NC010` TDS(Form No. TDS-37043-en)를 나란히 열어 값이 글자 그대로 같은 항목만** 옮기는 "
  "규율로 넣었다(브리프 59·140). 58차 TD 는 그 두 번째 문서(101F TDS)를 이 파동에 확보하지 못해 "
  "**같은 검산을 못 걸었고, 그래서 여섯 칸을 넣지 않았다.** 다음 파동의 한 걸음은 명확하다 — "
  "101F NC010 TDS 를 열어 ν·인장탄성률·CTE·밀도가 101L 과 글자 단위로 같은지 대조하고, 같은 항목만 "
  "`grade_substitution` 표시와 함께 옮겨라. 브리프 6 의 반례이기도 하다 — **CAMPUS 서식 시트가 "
  "포아송비를 인쇄한다.** ⚠ 조습 주의 — 이 시트의 값은 전부 `dry / cond` 두 열이라 옮길 때 "
  f"`moisture_state` 를 반드시 못박아라(ν 가 0.37 → 0.43 으로 움직인다). {TD}."))

add(2261,"2017A-T4 aluminium alloy, commercial quality bar, bending-torsion fatigue specimen (Kluger 2015)",
 core_next_target=("[58차 TD — V5 로 남긴다. 이유와 함정] 코어 빈칸 5(ρ·ν·CTE·k·비열). 이 파동에 문서 셋을 "
  "시도했다. ① 원 출처 Kluger 2015 전문 → `Poisson` 0건 · `specific heat` 0건 · `thermal conduct` 0건, "
  "`density` 1건은 `Power Spectral Density` 다. ② Smith Metal Centres `2017A Aluminium Product Datasheet` → "
  "받았는데 **물리물성 블록이 없다**(조성·기계물성·규격대조뿐, `Density`·`Modulus`·`Thermal` 0건). "
  "③ ⚠ **브리프 438 의 사고를 그대로 밟았다** — `https://www.aalco.co.uk/datasheets/"
  "Aluminium-Alloy-2017-T4_147.ashx` 가 **HTTP 200 · 41 KB 로 응답하는데 내용이 6082 데이터시트다.** "
  "본문 제목이 `Aluminium Alloy - Commercial Alloy - 6082 - T4 Extrusions` 이고 문자열 `2017` 이 "
  "**전권 0건**, `6082` 가 16건이며, 물리물성 값(2.70 g/cm³ · 555 °C · 24e-6/K · 70 GPa · 180 W/m·K)이 "
  "같은 사이트의 6082 페이지(`_148.ashx`)와 **글자 단위로 같다.** 상태코드·크기·`content_type` 어느 것도 "
  "이것을 못 잡는다 — **본문에서 등급 문자열을 세는 것만이 잡는다.** 다음 파동의 한 걸음 — "
  "EN AW-2017A 는 유럽 규격 합금이라 벤더가 여럿이다. Kloeckner·Gleich·Amari 는 이 파동에 타임아웃/404 였고, "
  "가장 확실한 문서는 EN 485-2 / EN 754-2 배경자료나 ASM Handbook Vol.2 다. "
  f"편찬 사이트(makeitfrom)의 두 자리 클래스값은 쓰지 마라 — 그 페이지의 2017A 밀도가 3.0 g/cm³ 다(참값 2.79). {TD}."))

add(2267,"Zytel 70G33HS1L short E-glass/PA-6,6 33 wt% (18 vol%), injection-moulded 2.5 mm plaque (DuPont, Mallick 2004)",
 core_next_target=("[58차 TD — V5 로 남긴다. 이유] 코어 빈칸 6(ρ·ν·CTE·k·비열·인장강도). "
  "원 출처 Mallick 2004(10.1016/j.ijfatigue.2004.02.003) 전문에 낱말 검색을 걸면 "
  "**`density` 0건 · `Poisson` 0건 · `specific heat` 0건 · `thermal conduct` 0건**이다 — 이 논문이 재는 것은 "
  "율속별 인장탄성률·인장강도·파단변형과 평균응력 의존 피로수명이고 그 값들은 이미 다 들어 있다. "
  "벤더 문서 층은 **이미 대장에 막힌 것으로 올라 있다** — `docs/BLOCKED_SOURCES.md` B절에 "
  "`DuPont / Celanese Zytel 전 계열 TDS (70G33L·70G43L·HTN51G45HSL)` 가 "
  "'CAMPUS·MatWeb·UL Prospector 가 JS 렌더링이라 표 추출 불가' 로 기재돼 있다. "
  "이 파동은 그 항목을 재확인만 하고 새 경로를 뚫지 않았다. 다음 한 걸음 — plastore.it 사본 경로가 "
  "Stanyl TW341·Zytel 101L 두 건에서 실제로 통했으므로(둘 다 이 파동에 받았다) **같은 미러에서 "
  f"`Zytel 70G33HS1L`(또는 70G33L) 사본을 찾아라.** ⚠ HS1L 과 L 은 열안정 등급이 달라 브리프 586 이 걸린다. {TD}."))

json.dump({"batch":"58차 TD — housing V5 93칸 분해","verdicts":V},
          open("td03_housing_v5_split.json","w"),ensure_ascii=False,indent=1)
c={"V1":0,"V2":0,"V6":0}
for r in V:
    c["V1"]+=len(r.get("core_not_applicable",{}))
    c["V2"]+=len(r.get("core_absent_from_vendor_sheet",{}))
    c["V6"]+=len(r.get("core_rejected_printed_value",{}))
print("PART2 재료",len(V),c,"합",sum(c.values()))
