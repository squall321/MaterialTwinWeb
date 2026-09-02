# 59차 UD — out_of_scope 분류 · 코어 판정 JSON 을 한 벌로 생성한다(§610 — 한 재료 한 행).
import json

RHO="physical.density"; E="mechanical.youngs_modulus"; NU="mechanical.poisson_ratio"
CTE="thermal.expansion_linear"; TC="thermal.conductivity"; HC="thermal.specific_heat"
UTS="mechanical.tensile_strength"
CORE7=[RHO,E,NU,CTE,TC,HC,UTS]

NAMES=json.load(open("ud00_names.json"))   # 재료 id -> DB 이름(적용 시점 스냅샷)
N=lambda i: NAMES[str(i)]

# ── 1. out_of_scope ────────────────────────────────────────────────────────────
UDDEHOLM=[2381,2390,2391,2392,2393,2394,2395,2396,2419,2420,2421,2422,2423]
UDD_REASON=("금형·공구강이다 — 스마트폰 부품이 아니라 그 부품을 사출·단조하는 **금형의 강**이다"
  "(45차 GD 판정 · 49차 KA 가 `verdict_subsystem=not_applicable` 로 굳혔다 · 57차 SC 가 out_of_scope 를 제안했다). "
  "선례가 이미 격자 안에 있다 — 재료 406~417 Smooth-On/Polytek **몰드용 실리콘 11종**이 같은 사유로 "
  "`out_of_scope` 다. '무엇을 만드는 재료' 와 '무엇에 들어가는 재료' 를 격자는 가른다. "
  "**값은 하나도 지우지 않는다**(밀도·E·CTE·열전도율·경도·충격에너지 약 300행). 금형 해석에는 정당한 입력이고 "
  "이 격자가 재는 것이 '스마트폰 해석 준비도' 라서 격자 밖으로만 옮긴다(§193). — 59차 UD")
TAPE_REASON=("웹 가공 라인의 롤-이음용 스플라이싱 테이프다 — **완제 부품에 남지 않는 제조 공정 소모재**다"
  "(49차 KA 의 `subsystem_basis` verbatim: '웹 가공용 스플라이싱 테이프 — 제품에 남는 부재가 아니라 제조 공정 소모재다'). "
  "선례가 격자 안에 있다 — 재료 2426~2429 **MLCC 테이프캐스팅 바인더 4종**이 '소성 전 탈바인더로 전량 제거되므로 "
  "완제 부품에 남지 않는다' 는 같은 사유로 `out_of_scope` 다. 값(두께·박리력 등 7행)은 공정 해석에 정당하므로 그대로 둔다. — 59차 UD")

# **`apply_material_role.py` 가 아니라 `apply_core_verdicts.py` 로 넣는다.** 이유 둘 —
# ① 그 도구는 `role_reason` 을 **300자로 잘라 덮어쓴다.** 45차가 쓴 원래 사유가 사라진다(삭제 금지).
# ② `apply_core_verdicts.py` 는 덮기 전 값을 `<키>_before_correction` 에 남긴다(브리프 594).
# `role_basis` 는 병합기 `CURATION_KEYS` 안에 있으므로 운영까지 전파된다(브리프 464·608).
classification=[{"material_id":m,"name":N(m),"role":"out_of_scope",
                 "role_basis":(UDD_REASON if m in UDDEHOLM else TAPE_REASON),
                 "role_confidence":"high"} for m in UDDEHOLM+[364]]
EPE_KEEP=("[SC 의 out_of_scope 제안을 기각한다 · 브리프 193·505] 57차 SC 가 EPE 발포PE 완충재 3종을 `out_of_scope` 로 "
 "제안했으나 59차 UD 가 실행하지 않았다. 사유 셋이다. "
 "① **SC 자신의 문서가 반대 근거를 적어 두었다** — `sc04` verbatim: '낙하시험 해석에서 **상자째 떨어뜨리는** 모형은 "
 "실재하므로 완충폼은 정당한 해석 입력이다.' 그 뒤 SC 가 든 이유는 '어휘(subsystem)를 새로 열 값어치가 없다' 였는데, "
 "그것은 **계통 어휘의 문제이지 격자 안팎의 문제가 아니다.** 계통이 없다는 것과 해석 대상이 아니라는 것은 다른 명제다. "
 "② **선례가 가른다** — 지금 `out_of_scope` 67종은 전부 (a) 다른 도메인의 제품(교정 아치와이어·치과 시멘트·PV 백시트·"
 "식품 포장 배리어·발전 압력용기·산업 베어링 스톡)이거나 (b) 완제품에 남지 않는 공정 소모재(MLCC 바인더·몰드용 실리콘)다. "
 "휴대폰 출하 상자의 완충폼은 **다른 도메인도 아니고 공정에서 사라지지도 않는다** — 그 제품 자신의 포장이고 포장낙하 "
 "해석에서 실물로 남는다. §193 의 경계 규칙 '5:5면 product' 가 그대로 적용된다(같은 규칙으로 연질 PU 폼이 남았다). "
 "③ **얻는 것이 없고 잃는 것이 있다** — 이 3종은 **코어 빈칸이 0칸**이다. 격자에서 빼면 줄어드는 빈칸은 없고 "
 "차 있는 21칸이 분모에서 빠져 `(태깅 없음)` 채움률만 내려간다. "
 "다음 파동에게 — 이 판정을 뒤집으려면 '휴대폰 포장낙하 해석은 이 격자의 대상이 아니다' 를 먼저 세워라. — 59차 UD")
classification += [{"material_id":m,"name":N(m),"verdict_role_scope":EPE_KEEP} for m in (387,388,389)]

json.dump({"batch":"59차 UD — role='out_of_scope' 실행 14종(SC 제안 17종 중 EPE 3종은 기각)",
           "tool":"apply_core_verdicts.py (apply_material_role.py 는 role_reason 을 300자로 자르고 옛 사유를 덮는다)",
           "verdicts":classification},
          open("ud01_out_of_scope.json","w"),ensure_ascii=False,indent=1)

# ── 2. 코어 판정 ───────────────────────────────────────────────────────────────
V=[]   # 재료당 정확히 한 행

def row(mid,**kw):
    r={"material_id":mid,"name":N(mid)}
    r.update(kw); V.append(r)

# 2-a. 열 문서가 존재하지 않는다 — `core_no_public_document`(§609 가 제안한 자리, `core_` 접두어라 운영까지 간다)
SY_BASE=("[V3 → 새 갈래 · 브리프 609·626·600] **공개 시트가 존재하지 않는다.** 北京航空材料研究院(BIAM) SY-14M-III 는 "
 "공개 TDS 가 없고(37·49차부터 반복 확인), 57차 SC 가 조달을 시도해 실패했다. 59차 UD 가 §626 대로 조달 전에 "
 "코퍼스를 먼저 검색해 **유일한 1차 문서를 찾았다** — Cheng 2019(Composites Part B, `10.1016/j.compositesb.2019.03.002`, "
 "`cae_papers/15_cohesive_xfem`)가 이 접착제의 **벌크 인장시험을 직접 수행**했다(Instron 8801, 12층 필름 적층 시편, 7환경 21편). "
 "그 논문을 전권으로 읽었고 이 물성은 **표에도 본문에도 없다** — 논문이 인쇄하는 것은 흡습계수·확산계수·"
 "DCB/ENF 파괴에너지(Table 2)·CZM 계면 파라미터(Table 4)·복합재 T800/AC531 의 탄성상수(Table 3)뿐이다. "
 "Table 3 은 **접착제가 아니라 피착 복합재**의 표이니 옮기지 마라(§123·140). "
 "**V2 와 다른 점** — 벤더 시트를 열어 행이 없음을 확인한 것이 아니라 **열 벤더 시트 자체가 없다.** "
 "다시 조달하러 가지 마라. — 59차 UD")
row(587, core_no_public_document={k:SY_BASE for k in (RHO,NU,CTE,TC,HC)})

AF_BASE=("[V3 → 새 갈래 · 브리프 609·615·22·586] **열 문서가 존재하지 않는다.** 3M AF-130 은 단종이고 현행 TDS 가 없다"
 "(49차 KA 가 `core_fill_sheet` 에 적었고 57차 SC 가 조달을 시도해 실패했다). 59차 UD 가 다시 확인했다 — "
 "유일한 1차 문서인 Thiedmanu 1987(`mech_papers/25_adhesion_chem`, 코퍼스에 있다)을 전권으로 읽었고 "
 "AF-130 에 대해 인쇄하는 것은 **Table II 의 경화조건(60 min at 177 °C)·수지 계열(unmodified epoxy)·"
 "Table IV 의 랩전단강도·웨지시험 초기균열길이 53.3~54.2 mm** 뿐이다. 코어 7물성은 한 줄도 없다. "
 "**이름이 비슷한 딴 등급을 붙이지 마라(§22·586)** — 3M 현행 목록의 `AF 130-2`·`AF 163-2` 는 경화조건과 "
 "사용온도가 다른 별개 제품이다. **V2 와 다른 점** — 시트를 열어 행이 없음을 본 것이 아니라 열 시트가 없다. "
 "남은 길은 Wayback·구판 카탈로그뿐이고(§615) 두 파동이 실패했다. — 59차 UD")
row(1110, core_no_public_document={k:AF_BASE for k in CORE7})

# 2-b. V5 → V2 · V6 · V4
def v2(mid,keys,text): row(mid, core_absent_from_vendor_sheet={k:text for k in keys})

HEAD="[V5 → V2 · 브리프 127·582·613] 59차 UD 가 이 재료의 **유일한 출처 문서를 실제로 열어**(코퍼스 md 전권 + docling 표 파일) 확인했다. "

v2(641,[RHO,CTE,TC,HC], HEAD+"English 2016(`10.1016/j.compstruct.2015.09.033`) Table 3 `CFRP material properties` 는 "
 "탄성상수 9개·파괴에너지 5개·강도 12개·손상계수 3개를 전부 인쇄하는데 **밀도·CTE·열전도율·비열 행이 하나도 없다.** "
 "이 논문은 저속충격 시뮬레이션 검증 논문이라 인쇄 축이 탄성·강도·CZM 이다. 전권 낱말검색으로 "
 "`densit`·`W/m`·`specific heat` 적중 0 이다(§613). — 59차 UD")

v2(756,[E,NU,CTE,TC,HC,UTS], HEAD+"Bao 2002(`10.1016/s0032-3861(02)00189-1`)는 흡습 논문이다. 인쇄하는 표는 "
 "확산계수(Table 1)·활성화에너지와 전지수인자(Table 2)·흡습열(Table 3)·IR 피크(Table 4)뿐이고 "
 "**기계·열 물성 표가 아예 없다.** 전권에서 `modulus`·`Poisson`·`W/m`·`specific heat`·`tensile strength` 적중 0 이다. "
 "밀도 한 칸만 이미 들어가 있고 나머지 여섯은 이 문서에 없다. — 59차 UD")

v2(1299,[NU,CTE,TC,HC], HEAD+"Ding 2021(`10.1016/j.compstruct.2020.113400`) Table 1 의 원재료 사양행 verbatim — "
 "`T300; Tensile strength:3530 MPa; Elastic modulus: 230 GPa; Elongation:1.5%; Density: 1.76 g/cm3`. "
 "**넉 줄이 전부이고 그 넷은 이미 DB 에 있다.** 포아송비·CTE·열전도율·비열은 이 표에 없다 — "
 "탄소섬유 공급사 사양은 강도·탄성률·연신·비중으로 규격되고 이방성 ν 는 인쇄하지 않는다. — 59차 UD")

v2(1300,[RHO,E,NU,CTE,TC,HC], HEAD+"Ding 2021 Table 1 의 원재료 사양행 verbatim — "
 "`YPH-160; Tensile strength: 55 MPa; Flexural strength: 105 MPa; Flexural modulus: 3.125 GPa; Tg: 147 °C`. "
 "**넉 줄이 전부이고 그 넷은 이미 DB 에 있다.** 인쇄된 탄성률은 **굽힘탄성률**이지 인장탄성률이 아니므로 "
 "`mechanical.youngs_modulus` 로 옮기지 않았다(§604 의 라벨 규율). 밀도·ν·CTE·k·Cp 행은 없다. — 59차 UD")

v2(1345,[E,NU,CTE,HC], HEAD+"Zhou 2007(`10.1016/j.tca.2006.10.018`) Table 2 `Properties of the composites` 의 HDPE 열 verbatim — "
 "`열전도율 0.26 W/mK · 인장강도 26 MPa · 파단연신 650% · 절연파괴 38 kV/mm · 유전율 2.0 · 체적저항 1e17 Ωcm`. "
 "**여섯 줄이 전부다.** 영률·포아송비·CTE·비열 행이 없다 — 이 논문의 축은 절연·열전도이지 강성이 아니다. — 59차 UD")

v2(1347,[CTE,TC,UTS], HEAD+"Li 2011(`10.1016/j.tsf.2011.02.051`) Table 2 의 PET 기재 사양표는 "
 "두께 188 µm · 밀도 1.33 · **항복인장강도 57–59 MPa** · 항복연신 4% · 탄성률 2.2 GPa · 인열강도 54–59 kN/m · "
 "비열 1100 J/kg°C · 헤이즈 · 투과율을 인쇄한다. **CTE·열전도율 행이 없다.** "
 "인장강도 칸을 채우지 않은 이유는 둘이다 — ① 인쇄된 것은 `Tensile strength **at yield**` 라 항복응력이지 "
 "인장강도가 아니고, ② **구간(57–59)으로만 인쇄돼 어느 끝도 근거가 없다**(§616·451). — 59차 UD")

v2(1380,[CTE,TC,HC], HEAD+"Okutan 2002(`10.1177/002199802761675502`) Table 1 `Properties of glass-fiber-epoxy composites` 는 "
 "밀도 1.506 g/cm³ · Vf 0.57 · E1 44000 · E2 10500 · G12 3740 MPa · ν12 0.36 · 비선형파라미터와 강도 5종을 인쇄한다. "
 "**여섯 칸이 이미 DB 에 있고 CTE·열전도율·비열 행은 이 표에 없다** — 핀-하중 파손강도 논문이라 인쇄 축이 탄성·강도다. — 59차 UD")

v2(1422,[E,NU,CTE,TC,HC,UTS], HEAD+"Zhao 2019(`10.3390/polym11111797`)는 **경화속도론 논문**이다. 표 넷이 전부 "
 "유리비드 입도·배합·Kamal-Sourour 모델 상수이고, 순수 EP 246-1 에 대해 인쇄한 물성은 **밀도 한 칸**뿐이다"
 "(이미 DB 에 있다). 전권에서 `modulus`·`Poisson`·`W/m`·`specific heat` 적중 0 이다(§613). — 59차 UD")

v2(1430,[RHO,TC,HC,UTS], HEAD+"Watanabe 2018(`10.1016/j.microrel.2017.12.045`) Table 1 `Material properties of electroplated "
 "copper and resin` 은 **온도별 영률·항복응력·포아송비·CTE 네 열만** 갖는다. E·ν·CTE 는 이미 DB 에 있고 "
 "**밀도·열전도율·비열·인장강도 열 자체가 없다** — TH 비아 열피로 해석 논문이라 인쇄 축이 탄소성·열팽창이다. — 59차 UD")

v2(1462,[RHO,E,NU,CTE,TC,HC], HEAD+"Pan 2020(`10.1002/app.49813`)은 **난연 논문**이다. 표 다섯이 LOI/UL-94·TG/DTG·"
 "콘칼로리미터·XPS·인장이고, 순수 PP 행이 인쇄하는 것은 `인장강도 36.3±2.5 MPa · 파단연신 150.6% · 충격강도 5.8 kJ/m²` 뿐이다"
 "(이미 DB 에 있다). **밀도·영률·ν·CTE·열전도율·비열 행이 없다.** — 59차 UD")

FIB=("[V5 → V2 · 브리프 127·613] 59차 UD 가 Keith 2006(`10.1002/app.25102`, `mech_papers/06_lcp_properties`)의 "
 "섬유 사양표를 열었다. 인쇄 항목은 **탄소함량·전기저항률·축방향 열전도율·인장강도·인장탄성률·비중·섬유직경·"
 "섬유형상·섬유길이·벌크밀도**뿐이다(그 넷은 이미 DB 에 있다). **포아송비·CTE·비열 행이 없다** — "
 "촙/밀드 탄소섬유 사양은 그 축으로 규격되지 않는다. §626 확인 — 이 출처의 `local_path` 는 비어 있지만 "
 "논문은 코퍼스에 있다. — 59차 UD")
v2(1502,[NU,CTE,HC], FIB+" (TABLE IV, Fortafil 243)")
v2(1503,[NU,CTE,HC], FIB+" (TABLE III, Panex 30 MF)")

v2(1509,[RHO,E,NU,CTE,TC,HC], HEAD+"Pittman 2000(`10.1002/pen.11271`)이 인쇄하는 표는 인장(강도·연신·아이조드)과 "
 "굽힘(강도·모듈러스·처짐)뿐이고 PVC 5225 순수 시료의 **밀도·영률·ν·CTE·열전도율·비열 행이 없다.** "
 "본문의 `density` 적중 둘은 전부 `crosslinking density`·`low density polyethylene` 문맥이라 값이 아니다(§0·5). "
 "§626 확인 — `local_path` 는 비어 있으나 논문은 코퍼스에 있다. — 59차 UD")

v2(1525,[RHO,NU,CTE,TC,HC], HEAD+"Faiz 2014(`10.1002/pc.23800`) TABLE 3~5 는 융점·결정화온도·융해열·결정화도·"
 "열분해온도·차르수율·인장강도·탄성률·파단변형·굽힘강도·굽힘탄성률을 인쇄한다. NEAT HDPE 열의 그 값들은 이미 DB 에 있고 "
 "**밀도·포아송비·CTE·열전도율·비열 행은 없다.** 본문의 `density` 적중은 전부 `high density polyethylene` 이라는 "
 "이름의 일부다(§0·5 — 낱말검색의 함정). §626 확인 — 논문은 코퍼스에 있다. — 59차 UD")

v2(1542,[E,NU,CTE,TC,HC], HEAD+"Li 2008(`10.1002/app.28588`)의 원료표는 `Material | Density (g/cm³) | Tensile strength (MPa) | "
 "Elongation at break (%)` **세 열뿐**이고 그 둘이 이미 DB 에 있다. 논문이 재는 모듈러스는 DMTA 저장탄성률 곡선과 "
 "굽힘탄성률이라 **정적 영률이 아니다**(§604 라벨 규율). ν·CTE·k·Cp 는 어디에도 없다. "
 "§626 확인 — `local_path` 는 비어 있으나 논문은 코퍼스에 있다. — 59차 UD")

v2(1643,[NU,CTE,TC,HC], HEAD+"Aijuan 1997(`10.1002/pc.10269`) Table 1 `Properties of Neat Resin` 은 "
 "RT 인장(강도 81 MPa·모듈러스 3.87 GPa·연신 3.2%)·굽힘·충격·GIC·흡습·Tg·분해온도·HDT·밀도를 인쇄한다. "
 "**포아송비·CTE·열전도율·비열 행이 없다.** — 59차 UD")
v2(1644,[RHO,NU,CTE,TC,HC], HEAD+"Aijuan 1997 Table 2 `Properties of Composite` 는 RT 인장(650 MPa·31 GPa·2.9%)·"
 "SBS 3온도·충격강도·굽힘 3온도·**Vf 56%·보이드 0.3%** 를 인쇄한다. 복합재의 **밀도 행은 없다**(Vf 와 보이드는 있으나 "
 "그것으로 밀도를 만들면 우리 산술이다 — §43 역산 금지). ν·CTE·k·Cp 행도 없다. — 59차 UD")

DAD=("[V5 → V2 · 브리프 127·613] 59차 UD 가 Dadej 2020(`10.1016/j.ijfatigue.2020.105843`, `mech_papers/09_foldable_bending_mech`)을 "
 "열었다. Table 1 `Mechanical and thermal properties of materials used in fibre metal laminates` 는 "
 "**E1·E2·ν12·ν21·G12·α1·α2 일곱 열뿐**이고 그 값들은 이미 DB 에 있다. **밀도·열전도율·비열 행이 없다** — "
 "전권에서 `densit`·`W/m`·`specific heat` 적중 0 이다. §626 확인 — `local_path` 는 비어 있으나 논문은 코퍼스에 있다. — 59차 UD")
DAD_UTS=("[V5 → V6 · 브리프 195·456·3] 인쇄는 **돼 있으나 넣지 않았다.** Dadej 2020 Table 2 "
 "`K-V model function parameters describing fatigue behaviour of monolithic materials **[25]**` 이 "
 "`X_T` 를 Aluminium 474 · CFRP 1895 · GFRP 1535 MPa 로 인쇄하고, 기호표가 `X = static strength` 라고 밝힌다. "
 "행 배정 자체는 닫힌다 — 2024-T3 의 474 MPa 가 통용 UTS(약 470)와 만난다(§129 의 순금속 행 검산과 같은 용법). "
 "**그런데 캡션에 `[25]` 가 박혀 있고 본문이 `The values of K-V model for monolithic constituent materials were "
 "determined in previous research [25]` 라고 못박는다 — 재인용이다**(§195: Ref./Source 표시가 재인용의 최강 신호다). "
 "게다가 X_T 는 Kohout-Vechet **피로수명 모델의 피팅 파라미터**이지 이 논문이 잰 인장강도가 아니다. "
 "두 사유가 겹쳐 기각했다. 닫으려면 원 논문 [25](Dadej et al. 의 선행 연구)를 열어야 한다. — 59차 UD")
row(1652, core_absent_from_vendor_sheet={k:DAD for k in (RHO,TC,HC)},
          core_rejected_printed_value={UTS:DAD_UTS+" (CFRP 열, 1895 MPa)"})
row(1653, core_absent_from_vendor_sheet={k:DAD for k in (RHO,TC,HC)},
          core_rejected_printed_value={UTS:DAD_UTS+" (GFRP 열, 1535 MPa)"})

v2(1658,[RHO,CTE,TC,HC,UTS], HEAD+"Kawashita 2004(`10.1080/00218460490279215`, `mech_papers/10_adhesion_mechanics`)의 "
 "표는 **알루미늄 필암**의 탄소성 파라미터뿐이고, Permabond ESP110 접착제에 대해 인쇄하는 것은 영률·포아송비·"
 "항복강도·GIC·파괴인성이다(전부 이미 DB 에 있다). **밀도·CTE·열전도율·비열·인장강도 행이 없다.** "
 "⚠ **벤더 시트로 메우려다 §22·586 함정을 만났다** — 검색에 걸리는 `LOCTITE ESP110`(Henkel) TDS 는 "
 "**제조사가 다른 동명 제품**이고 Permabond 공식 ESP110 TDS 는 현행 목록에 없다. 옮기지 않았다. "
 "§626 확인 — `local_path` 는 비어 있으나 논문은 코퍼스에 있다. — 59차 UD")

v2(2128,[E,NU,CTE,TC,HC,UTS], HEAD+"Gawdzik 2001(`10.1002/app.2045`) Table III `Properties of the Resins Before Curing` 은 "
 "밀도·점도·겔화시간을, Table IV `Properties of the Cured Resins` 는 **볼압입경도·초기분해온도·유리전이온도**를 인쇄한다. "
 "경화 수지의 **영률·포아송비·CTE·열전도율·비열·인장강도 행이 하나도 없다** — 이 논문의 강도축은 볼압입경도다"
 "(§613 의 '갈래마다 강도축이 다르다' 의 또 한 사례). — 59차 UD")

v2(2233,CORE7, HEAD+"da Silva Sobrinho 2000(`10.1116/1.582132`, `expert_papers/_enrich`)은 배리어 결함-투과 상관 논문이다. "
 "기재를 `The substrate used is a 13 µm biaxially oriented commercial PET film (ICI 800)` 로 한 줄 밝히고 끝이며, "
 "유일한 표는 OTR/WVTR 겉보기 활성화에너지다. **코어 7물성이 한 줄도 없다.** 본문의 `densit` 적중 16건은 전부 "
 "`defect density`(결함밀도)라 질량밀도가 아니다(§5 — 부재를 선언하기 전에 질의를 의심해라). "
 "§626 확인 — `local_path` 는 비어 있으나 논문은 코퍼스에 있다. — 59차 UD")

v2(2283,CORE7, HEAD+"Lazar 2019(`10.1002/admi.201901369`, `materials_papers/disp_thin_film_encapsulation`)의 유일한 표는 "
 "`Oxygen permeability of crosslinked CHQ/PAA` 이고 `Bare PET` 행이 갖는 것은 OTR 과 투과계수뿐이다. "
 "전권에서 `densit`·`modulus`·`Poisson`·`W/m`·`specific heat`·`tensile` 적중 **0건**이다(§613 — 전권 낱말검색이 "
 "가장 싼 부재 증거다). §626 확인 — `local_path` 는 비어 있으나 논문은 코퍼스에 있다. — 59차 UD")

v2(2380,[CTE,TC,HC], HEAD+"Liu 2009(`10.1016/j.polymertesting.2009.04.008`) Table 1 `Mechanical properties of cast acrylic and steel` 의 "
 "cast acrylic 행 verbatim — `Density 1190 kg/m³ · Young's modulus 3 GPa · Tensile strength 75 MPa · Poisson's ratio 0.4`. "
 "**네 칸이 전부이고 넷 다 이미 DB 에 있다.** CTE·열전도율·비열 행이 없다 — 낙하충격 시험·FE 논문이라 인쇄 축이 탄성·강도다. — 59차 UD")

v2(2398,[E,NU,CTE,TC,HC,UTS], HEAD+"Abu-Sharkh 2004(`10.1016/j.polymdegradstab.2003.10.022`) Table 2 "
 "`Product data for Epolene E-43 wax` verbatim — `연화점 157 °C · 침입도 <0.5 dmm · 밀도 0.93 g/ml · 산가 47 · "
 "브룩필드 점도 400 cP(190 °C) · 가드너 색 11`. **여섯 줄이 전부다.** 이 재료는 배합용 **왁스**라 벤더 사양이 "
 "연화점·산가·점도로 규격되고 **탄성·강도·열물성 행이 구조적으로 없다**(§607 의 액상·분말판과 같은 갈래이나 "
 "여기는 '정의되지 않는다' 가 아니라 '이 갈래의 시트가 안 찍는다' 이므로 V1 이 아니라 V2 다). — 59차 UD")

PZN=("[V5 → V2 · 브리프 127·613·43] 59차 UD 가 Park 1997(`10.1063/1.365983`, `snowball_papers/from_cae`)을 열었다. "
 "유일한 물성표 TABLE I 이 인쇄하는 열은 **결정방위·조성·모드·전기기계결합계수 k33·탄성컴플라이언스 s33^E·"
 "유전율·손실·압전상수 d33** 이다(그 셋이 이미 DB 에 있다). **밀도·영률·포아송비·CTE·열전도율·비열·인장강도 행이 없다.** "
 "⚠ `E = 1/s33^E` 로 영률을 만들지 않았다 — 인쇄된 것은 컴플라이언스이고 그 역수는 **우리 산술**이다"
 "(§43 역산 금지 · §10·469 에서 G→E 환산을 거부한 것과 같은 자리). 릴랙서 단결정은 방위마다 s33 이 "
 "7.4e-12 대 48e-12 로 6배 갈리므로(<111> 대 <001>) 역수 하나를 '영률' 로 세울 수도 없다. — 59차 UD")
v2(2446,CORE7,PZN); v2(2447,CORE7,PZN)

# 2-c. 값을 캔 재료의 남은 칸
row(2266, core_absent_from_vendor_sheet={
 NU:("[V5 → V2 · 브리프 127] 59차 UD 가 GlidCop® AL-15 (C15715) 공식 TDS(No. 700A, Revised 05/02/03)를 받아 열었다. "
     "`PHYSICAL PROPERTIES` 블록이 인쇄하는 것은 융점·밀도·전기전도도·열전도율·전기저항률·CTE·인장탄성계수 **일곱 줄**이고 "
     "**포아송비 줄이 없다**(전권 `Poisson` 적중 0). 밀도·열전도율·CTE 는 이 시트에서 캐 채웠다. — 59차 UD"),
 HC:("[V5 → V2 · 브리프 127·613] 같은 GlidCop® AL-15 TDS(No. 700A)에 **`Specific heat` 줄이 없다**(전권 적중 0). "
     "분산강화동 시트는 전기·열전도와 고온강도 유지로 규격되고 비열은 인쇄 축이 아니다. — 59차 UD")})

row(2417, core_absent_from_vendor_sheet={
 UTS:("[V5 → V2 · 브리프 127·602] 59차 UD 가 Lee 2010(`10.1002/app.31873`) TABLE III `Material Properties of the Polymer "
      "Resin for Numerical Flow Simulation` 을 열어 코어 여섯 칸을 채웠는데 **인장강도 행만 그 표에 없다.** "
      "표의 일곱 줄은 용융밀도·고체밀도·탄성계수·포아송비·선팽창계수·비열·열전도율이다. "
      "이 논문은 워피지 유동해석 논문이라 강도축이 없다. — 59차 UD")})

# 2-d. 등급 미확정(V4) — §58
row(70, identification_status=("미식별 — 이름 `visco-6` 이 내부 코드이고 제품이 특정되지 않는다(§58). "
  "45차의 `role_reason` 이 이미 '이름 \"visco-6\"이 내부 코드라 제품 식별 불가' 라고 적었고, "
  "유일한 출처가 `점탄성 제진재 대표물성(Sorbothane/EAR 클래스)` 이라 **제품조차 특정 안 된다**(57차 SC 재확인). "
  "[V5 → V4 · 브리프 58·582·608] 남은 코어 빈칸(인장강도 1칸)은 채굴 잔여가 아니라 **원리적으로 못 닫는 칸**이다 — "
  "어느 제품의 인장강도인지 물을 대상이 없다. 이 판정을 `identification_status` 에 적는 이유는 그 키를 "
  "집계(`coverage_report.subsystem_core`)가 읽고 병합기 `CURATION_KEYS` 가 운영까지 옮기기 때문이다(§608). — 59차 UD"))

json.dump({"batch":"59차 UD — 계통 태그 없는 재료의 코어 판정(열 문서 부재 12칸 · V5 148칸 분해)",
           "verdicts":V}, open("ud03_core_verdicts.json","w"),ensure_ascii=False,indent=1)

ids=[r["material_id"] for r in V]
assert len(ids)==len(set(ids)), "한 재료에 판정 행이 둘이다 — §610"
n=0
for r in V:
    for k,v in r.items():
        if isinstance(v,dict): n+=len(v)
        elif k not in ("material_id","name"): n+=1
print(f"분류 {len(classification)}종 · 판정 재료 {len(V)}종 · 판정 칸 {n}")
