# 60차 VC 의 코어 빈칸 판정 15칸을 apply_core_verdicts.py 입력 JSON 으로 굽는다(재료당 한 행 — 브리프 610).
import json

E   = "mechanical.youngs_modulus"
NU  = "mechanical.poisson_ratio"
UTS = "mechanical.tensile_strength"
RHO = "physical.density"
CTE = "thermal.expansion_linear"
TC  = "thermal.conductivity"
HC  = "thermal.specific_heat"

def spread(keys, text):
    return {k: text for k in keys}

V = []

# ── (1) packaging 비솔더 13칸 ────────────────────────────────────────────────
r1314 = ("[60차 VC] 값 출처 Shi 2012(EPTC, doi 10.1109/eptc.2012.6522604)를 전권으로 다시 열었다. "
 "표는 셋뿐이고 Table 1 은 시험보드 제원, Table 3 은 신뢰성 지표다. 물성은 "
 "`Table 2. Properties of the underfill used in this study` 한 장뿐이고 그 표의 행은 "
 "chemical type · appearance · components · specific gravity · dispensing method · DSC conversion · "
 "reworkable · viscosity · flow time 4행 · cure shrinkage · density · water absorption · Tg(DMTA) · "
 "CTE(ISO 11359-2) α1/α2 · Shore D · flexural strength(ASTM D790) · flexural modulus · "
 "lap shear strength(ISO 4587) **열여덟이 전부**다. "
 "**이 표는 논문이 만든 표가 아니라 언더필 벤더 TDS 를 그대로 전재한 표**이고(시험규격 번호가 행마다 붙어 있다), "
 "그 TDS 의 강성·강도축이 굽힘(flexural)과 랩전단이라 인장탄성률·인장강도·포아송비 행이 원래 없다(브리프 613 의 언더필 판). "
 "열전도율·비열도 없다. 그리고 원문이 제품명을 인쇄하지 않아(`trade name not printed`) 붙일 벤더 시트가 없다. "
 "**flexural modulus 3.5 GPa 로 영률을, flexural strength 120 MPa 로 인장강도를 대신하지 않았다** — 다른 물성이다. "
 "본문 검산 하나 — 같은 논문 본문이 `CTE (α1) of about 60 ppm/°C` 라고 다시 적어 이미 들어가 있는 CTE 2행을 지지한다.")

V.append({"material_id": 1314,
          "name": "Reworkable one-component capillary-flow epoxy underfill (Shi 2012)",
          "core_absent_from_vendor_sheet": spread([E, NU, TC, HC, UTS], r1314)})

r615 = ("[60차 VC] 이 재료가 쓰는 문서 넷을 전부 다시 열었다. "
 "① He 2007(ECTC, doi 10.1109/ECTC.2007.373974) `Table 1. General properties of the 70 um thick BT core substrate` 는 "
 "density 1.79 g/cm3 · fiber content 56.46 wt% · CTE(0-50 C) 16e-6 · CTE(150-200 C) 18.5e-6 · storage modulus(@25 C) 14.65 GPa · "
 "loss modulus peak 207 C · tan δ peak 215.6 C **일곱 행이 전부**이고 카탈로그가 그 일곱을 이미 다 담고 있다. "
 "② Ehrler 2004(doi 10.1108/03056120410539858)는 Cu 박리강도·Tg(TMA)·CTE(z축)·내열시험뿐이라 "
 "`poisson|tensile|thermal conductivity|specific heat` 가 전권 **0건**이다. "
 "③ Iguchi 1979(doi 10.1109/eic.1979.7461149)도 같은 네 낱말이 전권 0건이다(박리강도·드릴 가공성·화학처리). "
 "④ Sahin 2026(Polymers 18(14) 1690)·Ueki 2015(Trans. JSME 81(821))는 이 재료에 **계열 대입한 피로계수**만 주는데, "
 "그 행의 `grade_scope` 가 스스로 `measured on IEC 60893 EPGC 203 woven E-glass/epoxy laminate (UTS 418.45 MPa …), NOT on this product` "
 "라고 적어 두었다 — 즉 인쇄된 UTS 418.45 MPa 는 **딴 제품 것**이고 옮기면 브리프 147·616 위반이다. "
 "그리고 이 재료는 `BT/glass-fibre laminate substrate core, 70 um` 이라는 **클래스 서술**이고 벤더·등급명이 원문에 없어 붙일 시트가 없다.")

V.append({"material_id": 615,
          "name": "BT/glass-fibre laminate substrate core, 70 um (He 2007)",
          "core_absent_from_vendor_sheet": spread([NU, TC, HC, UTS], r615)})

r617 = ("[60차 VC] 57차 SA 가 밀도·열전도율·비열에 박은 판정과 같은 이유로 포아송비도 닫는다. "
 "값 출처 Chowdhury 2017(ITherm, doi 10.1109/ITHERM.2017.8023955)에 `poisson` 이 전권 **0건**이다 — "
 "이 논문이 내는 것은 흡습조건·시효시간별 응력-변형 곡선의 유효탄성률과 UTS, CTE α1 = 28e-6, 크리프율뿐이다. "
 "원문이 언더필을 `The commercially underfill … silica filled epoxy with Tg = 137 C` 로만 부르므로 붙일 벤더 시트도 없다. "
 "**같은 저자군의 Chowdhury 2019(doi 10.1109/itherm.2019.8756500)가 스트레인게이지로 잰 ν = 0.2989~0.30 을 인쇄하지만 "
 "그 값을 여기로 옮기지 않았다** — 2019 는 재료를 `a typical underfill material` 로만 부르고 Tg·CTE·밀도 어느 축도 인쇄하지 않아 "
 "이 재료와 동일 등급임을 닫을 대조축이 하나도 없다(브리프 51·586·620). "
 "그 값은 카탈로그 재료 738 `Underfill encapsulant … Chowdhury 2019` 에 이미 제자리로 들어가 있다. "
 "**결함 신고** — 이 재료의 `mechanical.wlf_c1/c2`(14.76 / 91.52) 2행이 출처 Chowdhury 2019 인데 "
 "같은 값·같은 출처가 재료 738 에도 있다(같은 배치가 21초 간격으로 넣었다). 둘이 같은 언더필이면 738 이 중복이고 "
 "다르면 617 의 WLF 2행이 등급 이전이다 — 어느 쪽이든 지금은 이중 계상이다(브리프 116·123·586). 병합·삭제는 이 배치의 권한이 아니라 신고만 한다.")

V.append({"material_id": 617,
          "name": "Underfill encapsulant, silica-filled epoxy (Chowdhury 2017)",
          "core_absent_from_vendor_sheet": {NU: r617}})

r438 = ("[60차 VC] 값 출처 Yang & Ding 2024(Polymers 16(7) 930, doi 10.3390/polym16070930)를 전문으로 열었다. "
 "본문 verbatim 이 이 재료를 못박는다 — `curing agent I (D230 polyether amine) and 14 g of curing agent II (D400 polyether amine) "
 "into 100 g of E-44 epoxy resin (bisphenol A epoxy resin WSR6101)`. "
 "그런데 이 논문이 재는 것은 **구속 실린더 체적완화계수와 전단완화계수**이고 표는 다섯이다 — "
 "Table 1 시험온도 · Table 2 구속실린더 제원 · Table 3 온도별 K·G · Table 4 시프트인자 · Table 5 마스터커브 적합계수. "
 "`tensile` 이 나오는 자리는 전부 `tensile relaxation modulus`(완화탄성률)이고 **인장강도(파단응력)는 한 줄도 없다.** "
 "벤더 쪽도 닫힌다 — E-44(WSR6101)는 **미경화 수지 등급**이라 벤더 시트가 찍는 것은 에폭시값·점도·연화점이고, "
 "이 재료의 정체는 `Jeffamine D230/D400 경화계`라 경화물 인장강도는 경화제 배합에 딸린 양이다. "
 "수지 시트로는 원리적으로 못 닫는다(브리프 147).")

V.append({"material_id": 438,
          "name": "E-44 (WSR6101) bisphenol-A epoxy potting resin",
          "core_absent_from_vendor_sheet": {UTS: r438}})

r403 = ("[60차 VC] 값 출처 Yang 2017(Materials 10(9) 1077, doi 10.3390/ma10091077)을 전문으로 열었다. 표는 둘뿐이다 — "
 "`Table 1 Material properties for the sensor`(Si·Glass·Ceramic·Adhesive 의 E·ν·CTE)와 "
 "`Table 2 Prony pairs of the die attach adhesive`. 인장강도 행이 없고 `tensile` 은 본문의 열응력 서술에만 나온다. "
 "다이어태치 쪽 벤더 문서도 강도축이 다르다 — 이 재료가 이미 쓰는 NAMICS 다이어태치 제품가이드가 찍는 것은 "
 "**다이전단강도**(25 MPa)와 흡습률이고 인장강도가 아니다(브리프 613 — 다이어태치·언더필 시트 6장 중 인장강도를 찍는 것은 1장). "
 "게다가 이 재료는 `Epoxy die attach adhesive (MEMS accelerometer)` 라는 클래스 서술이라 붙일 등급 시트가 없다.\n"
 "**결함 신고(브리프 3)** — 같은 Table 1 바로 앞 문장이 verbatim 으로 "
 "`The Poisson ratio and CTE of the adhesive were assumed as constant values, because they have little impact on the packaging stress [23]` "
 "라고 적는다. 그런데 이 재료의 `mechanical.poisson_ratio` 0.37 과 `thermal.expansion_linear` 6e-05 가 "
 "**tier1 · method=measured** 로 이 출처에 걸려 있다 — 해석 입력 가정값을 실측으로 받은 자리다. "
 "값은 지우지 않고 신고만 한다(등급 정정은 정정 문서의 일이다).")

V.append({"material_id": 403,
          "name": "Epoxy die attach adhesive (MEMS accelerometer)",
          "core_absent_from_vendor_sheet": {UTS: r403}})

r292 = ("[60차 VC] 문서 둘을 다시 열었다. "
 "① 값 출처 Kim 2018(Metals 8(1) 42, doi 10.3390/met8010042)의 표는 셋이고 "
 "Table 1 은 solder ACF 사양(두께·조성), Table 2 는 냉각 중 수축률, Table 3 은 냉각 중 저장탄성률이다 — "
 "인장강도 행이 없다(이 논문의 강도축은 솔더접합 크랙과 저장탄성률이다). "
 "② 이 재료가 이미 쓰는 Hitachi ANISOLM AC-7206U-18 데이터시트(9쪽)를 열었다. "
 "8절 `Physical Properties` 표는 **`Elastic modules(GPa) 40 C = 1.2` 와 `tanΔ max (C) = 125` 두 칸이 전부**이고 "
 "시트의 나머지 절은 접속저항·박리강도(peel)·절연신뢰성이다. **ACF 시트의 강도축은 박리강도이지 인장강도가 아니다**(브리프 613). "
 "그리고 이 재료 자신이 `ACF acrylic solder-type (generic, literature)` 라는 **클래스 레코드**라 특정 등급 시트가 없다.")

V.append({"material_id": 292,
          "name": "ACF acrylic solder-type (generic, literature)",
          "core_absent_from_vendor_sheet": {UTS: r292}})

# ── (3) 미태깅 잔여 2칸 ─────────────────────────────────────────────────────
r392 = ("[60차 VC] 59차 UD 가 남긴 오픈액세스 논문을 **셋** 열었고 D3O 공개 데이터시트 **일곱** 장을 조달했다. 결론은 등급 미확정이다.\n"
 "① Smeets, Koohbor & Youssef 2023(ACS Appl. Polym. Mater., PMC10112387) — 이 레코드의 397 kg/m3 이 나온 문서다. "
 "Table 1 이 `D3O (benchmark foam) 397/-/- 397` 을 찍고 본문은 `a benchmark foam (ϱf = 395 kg/m3) that is commonly used as "
 "high-impact-mitigating padding in protective gears` 라고만 쓴다 — **등급명이 없다**(본문 395 대 표 397 로 문서가 자기 안에서도 2 kg/m3 갈린다). "
 "시험은 준정적 **압축**뿐이고 `tensile` 은 참고문헌 제목에만 나온다.\n"
 "② Bhagavathula 2018(J. Dynamic Behavior Mater., doi 10.1007/s40870-018-0176-0) — `Table 1. Manufacturer's listed properties for D3O LITE D` 가 "
 "**Tensile Strength 2.2 MPa (ISO 1798:2008)** 을 찍는다. **그러나 그 등급은 200-220 kg/m3(ISO 845:2009) 이라 이 레코드의 397 과 밀도가 두 배 다르다.** "
 "이 재료의 기존 `mechanical.poisson_ratio` 0.0 행이 그 문서에서 왔고 그 행의 `grade_scope` 가 이미 `STRONG GRADE MISMATCH` 를 적어 두었다 — "
 "같은 이유로 인장강도도 못 옮긴다(브리프 147·600·616).\n"
 "③ Zhao 2019(ACS Omega, PMC6641077) — **몰딩 D3O 무릎컵을 0.41 g/cm3 = 410 kg/m3 로 재서 397 에 가장 가깝다.** "
 "그러나 이 논문의 역학시험도 `mechanical property in a compression mode` 뿐이다(`Instron universal tensile testing machine` 은 장비 이름이지 인장시험이 아니다).\n"
 "④ 벤더 조달 — D3O 공개 TDS 를 일곱 장 열었고 인장강도가 **등급마다 4.3배 갈린다**: "
 "Formable Foams FF006 LITE Low(120 kg/m3) 1.4 · FF007 LITE Mid(220) 1.9 · FF008 LITE High(300) 2.2 · FF009 LITE Orange(130) 1.4 N/mm2 · "
 "Aero Defence SF010(0.37 g/cm3) 0.6 N/mm2 · AeroMax(208 kg/m3) 0.51 MPa(전부 ISO 1798:2008) · "
 "Lite Defence 시트 1.4~2.2 N/mm2. 그리고 `D3O Material Sheet Guide`(전 제품 편찬표)에는 **인장강도 열 자체가 없고** "
 "밀도가 0.22~0.62 g/cm3 로 널려 있는데 0.397 인 등급이 없다(가장 가까운 것이 Decell Solid 4mm 0.39 · Aero Defence 0.37).\n"
 "**즉 벤더가 안 찍는 것이 아니라 우리 레코드의 등급이 특정되지 않아 어느 열을 쓸지 못 고르는 자리다 — 성격상 V4(등급 미확정, 브리프 58)이고, "
 "V4 는 운영으로 전파되지 않으므로(브리프 608) 전파되는 이 칸에 적고 사유에 성격을 못박는다.** "
 "다음 파동에 열릴 조건은 하나다 — 원문 저자가 등급명을 밝히거나, 397~410 kg/m3 의 몰딩 D3O 등급 TDS 가 공개되는 것.\n"
 "**주의(조정자 인계문 확인)** — 카탈로그 재료 66 PORON SR-S 의 notes 가 적은 `Tensile Strength min. 103 kPa (15 psi). "
 "192 kg/m3 등급은 83 kPa` 는 **Rogers PORON 폼**의 값이라 D3O 와 아무 관계가 없고, 밀도 등급도 다르다. 쓰지 않았다.")

V.append({"material_id": 392, "name": "D3O impact protection foam (397 kg/m3)",
          "core_absent_from_vendor_sheet": {UTS: r392}})

r393 = ("[60차 VC] 59차 UD 가 남긴 오픈액세스 논문을 열었다. "
 "이 재료의 밀도 255 kg/m3·하이퍼탄성계수·항복(플래토)응력이 전부 나온 "
 "Smeets, Koohbor & Youssef 2023(ACS Appl. Polym. Mater., PMC10112387)이 유일한 1차 문서인데, "
 "**이 폼은 저자가 실험실에서 직접 부은 것**이다 — 2.1 절 verbatim: "
 "`All samples were made of elastomeric polyurea foams in-house … mixing modified methylene diisocyanate (Isonate 143L MDI, Dow Chemical) "
 "with oligomeric diamine (Versalink P1000, Evonik) using a 1:4 weight ratio … in deionized water`. "
 "이 레코드가 가리키는 `mono-density (M)` 시료는 단층 시트에서 뚫은 플러그(255 kg/m3)다. "
 "**제품이 아니라 실험실 주조물이라 벤더 시트가 원리적으로 존재하지 않는다.** "
 "그리고 논문의 역학시험은 힘제어 준정적 **압축**(Instron 5843, 피크 500 N, 250 N/min) 하나뿐이고 "
 "`tensile` 이 나오는 자리는 참고문헌 제목뿐이다 — 표 셋(Table 1 시료 제원 · Table 2 계면 · Table 3 Avalle 적합계수) 어디에도 인장강도가 없다. "
 "**대체 출처도 못 쓴다** — 이 재료가 계열 대입으로 쓰는 AZoM 폴리우레탄 표·PORON 4701-40 시트·3M VHB 시트는 "
 "전부 **폴리우레탄/아크릴 폼**이고 폴리우레아가 아니며 밀도 등급도 다르다(브리프 616).")

V.append({"material_id": 393, "name": "Elastomeric polyurea foam, mono-density (255 kg/m3)",
          "core_absent_from_vendor_sheet": {UTS: r393}})

# ── (2) V3 자유 키 17칸 ─────────────────────────────────────────────────────
r1911 = ("[60차 VC] 45차 GD 의 자유 키 `core_verdict_undecided` 에만 있던 판정을 집계가 읽는 칸으로 옮긴다(브리프 593·608). "
 "**옮기면서 사유를 다시 셌고, 그 사유는 늙어 있었다** — `core_verdict_undecided` 는 아직도 "
 "*'판정 보류 … 조정자가 소자용 role 을 열지 정해라'* 라고 적는데, 그 물음은 이 재료의 `verdict_device` 가 이미 닫았다"
 "(*'소자 표시를 만들지 않는다'*). **보류가 아니라 결정된 자리인데 집계는 아직 V3 로 세고 있었다.**\n"
 "판정의 내용은 이렇다. 이 레코드는 **완제 MLCC 칩(소자)** 이다 — 3×2×1.6 mm, 활성층 150장, "
 "유전체 Ba0.95Ca0.05Ti0.825Zr0.175(Kyorix)에 산화물 첨가제 <1 wt%. "
 "**적층체의 유효 밀도·E·ν·CTE·k·Cp·UTS 는 소자 유효물성이지 재료 물성이 아니다**(브리프 475). "
 "재료로서의 코어 7 은 카탈로그 재료 **106 `BaTiO3 MLCC Dielectric` 이 일곱 칸을 이미 다 담고 있고**(189 `Class I MLCC Dielectric (C0G/NP0)` 도 마찬가지다), "
 "여기 복제하면 이중 계상이다(브리프 116·123·623 의 AlN 2448 · 솔더페이스트 2125 와 같은 자리). "
 "이 레코드가 담는 것은 연마 단면의 비커스 경도 3행과 전극 기준 방향별 잔류응력 6행이고, 그것이 이 레코드의 존재 이유다.\n"
 "**출처도 닫혔다** — 유일한 출처 Shin 2003(J. Eur. Ceram. Soc., doi 10.1016/S0955-2219(02)00346-1)이 인쇄하는 코어값은 "
 "`α_BT = 9.5~11.5e-6, α_Ni = 13.3e-6, E_BT = 125 GPa, E_Ni = 200 GPa, ν_BT = 0.25, ν_Ni = 0.31` 인데 "
 "**칩이 아니라 유전체·전극 각 구성상의 값이고 본문이 [17-19] 로 2차 인용임을 밝힌다**(브리프 3·195). "
 "칩의 밀도·유효 E·유효 CTE 는 한 줄도 인쇄되지 않는다.\n"
 "유효 밀도·E·CTE 를 나중에 넣게 되면 그때는 소자값이므로 `role`/`attributes` 를 다시 판정해라(45차 GD·앞 배치의 인계 그대로).")

V.append({"material_id": 1911,
          "name": "BaTiO3/Ni MLCC chip, Y5V (Shin 2003)",
          "core_not_applicable": spread([RHO, E, NU, CTE, TC, HC, UTS], r1911)})

alx_common = (
 "이 판정을 받치는 문서는 둘이고 이번에 **둘 다 다시 열어 사유가 아직 맞는지 확인했다**(브리프 599). "
 "① Huffman 2009(ECTC, doi 10.1109/ectc.2009.5074241) `Table 1: Physical Properties of BCB and ALX-211` — "
 "본문 verbatim 이 *'based on information from AGC and published information on BCB [6]'* 라 AGC 제공값 전재다. "
 "전권에서 `densit|poisson|thermal conductiv|specific heat` 가 **0건**이다. "
 "② 47차 IC 가 조달한 AGC 자사 발표자료 Eriguchi 2010(IMAPS Device Packaging, doi 10.4071/2010DPC-tp34, "
 "`/data/paper_patent_corpus/standards_appnotes/pkg/Eriguchi_2010_IMAPS_DPC_ALX_Polymer_WLP_Mechanical_Property_Multiple_Reflows.pdf`) — "
 "`Polymer Dielectrics for WLP` 슬라이드의 ALX 열이 찍는 것은 Modulus 1.3 GPa · Elongation 20% · Tensile 90 MPa · CTE 60 ppm/C · "
 "Stress 28 MPa · Dk 2.6 · Breakdown 5.5 MV/cm · Resistivity · Cure temp 190 C · Shrinkage ~5% · Water absorption 0.4% **열하나가 전부**이고, "
 "여기서도 네 낱말이 **0건**이다. AGC AL-X 공개 데이터시트는 제한 배포라 웹에 없다(브리프 145). "
 "**1차 출처와 벤더 자사자료를 둘 다 열고 확정한 구조적 부재다.**")

V.append({"material_id": 1358,
          "name": "ALX-211 photoimageable fluorinated aromatic polymer dielectric (AGC)",
          "core_absent_from_vendor_sheet": spread([RHO, NU, TC, HC],
              "[60차 VC] 46차 HD·47차 IC 가 자유 키 `core_fill_sheet`·`procurement_47ic` 에 적어 둔 판정을 "
              "집계가 읽는 칸으로 옮긴다(브리프 593·608). 자유 키는 사람이 읽을 계보로 그대로 둔다. " + alx_common)})

V.append({"material_id": 1359,
          "name": "ALX-215 photoimageable fluorinated aromatic polymer dielectric (AGC)",
          "core_absent_from_vendor_sheet": spread([RHO, NU, TC, HC],
              "[60차 VC] 46차 HD·47차 IC 가 자유 키 `core_fill_sheet`·`procurement_47ic` 에 적어 둔 판정을 "
              "집계가 읽는 칸으로 옮긴다(브리프 593·608). 자유 키는 사람이 읽을 계보로 그대로 둔다. " + alx_common +
              " 이 재료의 E·인장강도·CTE 3칸은 ALX-211(재료 1358)에서 자매등급 이전한 것인데(원문 verbatim "
              "`ALX-215, a higher viscosity formulation of ALX-211 … The same 190°C/2 hour cure process was used for the ALX-215`), "
              "**두 문서 어디에도 ALX-215 전용 열이 없으므로 이 네 칸은 이전할 원본조차 없다.**")})

r1360 = ("[60차 VC] 46차 HC 가 자유 키 `core_fill_sheet` 에 적어 둔 판정을 집계가 읽는 칸으로 옮긴다(브리프 593·608). "
 "자유 키는 사람이 읽을 계보로 그대로 둔다.\n"
 "**옮기기 전에 문서를 다시 열었고 판정은 지금도 맞는다.** DuPont(구 Dow) CYCLOTENE 4000 Series Photo-BCB "
 "`Processing Procedures (DS2100 Puddle Develop)` 를 **판 셋**으로 대조했다 — "
 "2009-03 판(코퍼스 사본 `/data/paper_patent_corpus/standards_appnotes/pkg/Dow_CYCLOTENE_4000_Series_PhotoBCB_ProcessingProcedures_DS2100_PuddleDevelop_2009-03.pdf`) · "
 "UCSB nanofab 사본(`BCB-cyclotene-4000-revA`) · ostec 배포 사본. **세 판이 한 칸도 다르지 않다.** "
 "Table 2(전기·열)는 Dk 2.65 · Df 0.0008 · breakdown 5.3 MV/cm · leakage · volume resistivity 1e19 · "
 "**thermal conductivity 0.29 W/m·K at 24 C** · thermal stability 일곱 행이고, "
 "Table 3(기계)은 CTE 42 ppm/C · Tg >350 C · tensile modulus 2.9 GPa · tensile strength 87 MPa · elongation 8% · "
 "**Poisson ratio 0.34** · stress on Si 28 MPa 일곱 행이며, Table 4 는 습도별 평형 흡수율이다. "
 "세 판 전부에서 `densit|specific gravity|specific heat` 가 **0건**이다. "
 "1차 출처 Huffman 2009 Table 1 의 BCB 열에도 그 두 행이 없다(같은 낱말 전권 0건).\n"
 "**곁가지 — 자유 키의 머리절이 스스로 거짓이다.** `core_fill_sheet` 는 아직도 첫 문단에서 "
 "*'코어 7 중 밀도·영률·포아송비·CTE·열전도율·인장강도가 한 표에 다 있다. 이 94종에서 가장 확실한 단일 표적이다'* 라고 적는데, "
 "**같은 필드의 뒷문단이 이미 *'인계문의 밀도가 한 표에 있다 는 틀렸다'* 로 그것을 뒤집어 두었다.** "
 "한 필드 안에 서로 어긋나는 두 문장이 앉아 있고 집계는 둘 다 못 읽는다(브리프 599 의 자유 키 판).")

V.append({"material_id": 1360,
          "name": "Photo-BCB benzocyclobutene repassivation dielectric (Dow Cyclotene 4000)",
          "core_absent_from_vendor_sheet": {RHO: r1360, HC: r1360}})

doc = {"batch": "60차 VC", "verdicts": V}
json.dump(doc, open("vc01_core_verdicts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

n = sum(len(v) for r in V for k, v in r.items() if isinstance(v, dict))
print(f"재료 {len(V)}종 · 선언 칸 {n}")
for r in V:
    cells = sum(len(v) for k, v in r.items() if isinstance(v, dict))
    print(f"  [{r['material_id']}] {cells}칸  {[k for k in r if k not in ('material_id','name')]}")
