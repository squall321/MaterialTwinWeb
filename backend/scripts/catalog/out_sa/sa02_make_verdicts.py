#!/usr/bin/env python3
# packaging 계통 코어 빈칸 판정을 §582 가 정한 두 칸에 넣을 JSON 을 만든다(57차 SA).
#   core_not_applicable            물리적으로 그 물성이 정의되지 않는다 (V1)
#   core_absent_from_vendor_sheet  출처 문서를 실제로 열어 그 열이 없음을 확인했다 (V2)
#   core_rejected_printed_value    원문이 인쇄했으나 검산에서 기각했다 (56차 RA 가 낸 칸. 집계는 아직 못 읽는다)
# 셋 다 {물성키: 사유} dict 다 — 문자열로 적으면 그 재료의 코어 전부를 덮는다(브리프 582·593, 56차 RA).
import json, pathlib

RHO="physical.density"; E="mechanical.youngs_modulus"; NU="mechanical.poisson_ratio"
CTE="thermal.expansion_linear"; TC="thermal.conductivity"; CP="thermal.specific_heat"
UTS="mechanical.tensile_strength"
NA="core_not_applicable"; VEND="core_absent_from_vendor_sheet"; REJ="core_rejected_printed_value"

R_PASTE = (
    "솔더 페이스트(SAC305 분말 + M500 플럭스 서스펜션)라 코어 7물성이 이 재료에 정의되지 않는다 — "
    "분말 합금의 것이고 카탈로그 재료 91 'SAC305 Solder Alloy' 가 코어 7칸을 이미 다 채우고 있다. "
    "미경화 페이스트는 자립 시편이 없어 탄성계수·포아송비·인장강도를 걸 수 없고(브리프 584 의 OSP 전환피막과 같은 자리), "
    "리플로 뒤에는 재료 자체가 SAC305 가 된다. 이 갈래의 물성축은 점도·항복응력·틱소지수·분말 입도(Type 3/4/5)이고 "
    "그 축은 이 재료에 이미 25행이 들어 있다(rheological.viscosity 8행 · yield_stress · storage/loss modulus). "
    "브리프 582 가 '솔더 페이스트 3종 21칸은 0/7 이 정상이다' 로 이미 판정한 자리이며, 57차 SA 가 그 판정을 집계가 읽는 칸으로 옮겼다."
)

NEG_HEAD = ("Nippon Electric Glass 'Powder Glass' 카탈로그(Ref. No. 2410-19E)를 열어 확인했다(브리프 127). ")
R_NEG_A = (NEG_HEAD +
    "저온봉착유리 LS-1401S/LS-2010/LS-3051S/LS-1301/BF-0901 의 Properties 표(p.24)가 인쇄하는 것은 "
    "봉착온도·유전율·tanδ·선팽창(30-250 degC)·전이점·연화점·밀도·체적저항·**열전도율·비열**·내산성·색·유리종류 열 뿐이다 — "
    "탄성계수·포아송비·인장강도 행이 없다. 같은 카탈로그에 Young's modulus·Poisson's ratio 열이 있는 표가 따로 있으나(금속봉착용 ST/BH 계열, p.?) "
    "그 표에 이 등급들은 없고, 굽힘강도는 LTCC 용 MLS 계열 표에만 있다. 57차 SA 확인.")
R_NEG_B = (NEG_HEAD +
    "저온봉착유리 LS-3081/LS-0118/LS-0206/LS-7105/BF-0606 의 Properties 표(p.26)는 "
    "봉착온도·선팽창(30-250 degC)·밀도·전이점·변형점·연화점·체적저항·색·유리종류만 인쇄한다 — "
    "탄성계수·포아송비·인장강도뿐 아니라 **열전도율·비열 열도 없다**. "
    "같은 카탈로그의 마주 보는 앞 표(p.24, 알루미나·AlN·Si 봉착용 LS-1401S 계열)는 열전도율과 비열을 인쇄하는데 "
    "이 표(윈도우글라스·50/426 합금 봉착용)는 그 두 열을 통째로 뺐다 — **한 카탈로그 안에서도 계열마다 열 구성이 다르다.** 57차 SA 확인.")

R_353ND = (
    "EPO-TEK 353ND Technical Data Sheet(Rev XXIX, 2017-09)를 열어 확인했다. "
    "PHYSICAL PROPERTIES 상자가 색·점도·틱소지수·Tg·CTE(Tg 위·아래)·Shore D·랩전단·다이전단·분해온도·중량감소·저장탄성률·이온함량을, "
    "ELECTRICAL AND THERMAL 상자가 체적저항·유전율·유전손실을 인쇄한다 — 포아송비·비열·인장강도 행이 없고, "
    "**열전도율은 행이 있는데 값이 'N/A' 다**(부재가 아니라 벤더의 판정이다 — 브리프 56차 RD 의 Laird 320 인장강도와 같은 자리). "
    "강도축은 랩전단 >2,000 psi 와 다이전단 5,334 psi 로만 인쇄한다. 57차 SA 확인.")
R_H20E = (
    "EPO-TEK H20E Technical Data Sheet(Rev. XVIII, 2021-02)를 열어 확인했다. "
    "포아송비·비열·인장강도 행이 없다. 강도축은 랩전단 1,475 psi 와 다이전단 3,556 psi 로만 인쇄하고, "
    "열전도율은 두 값을 나란히 싣는다(레이저플래시 2.5 W/mK 와 열저항 환산 29 W/mK). 57차 SA 확인.")
R_FP4527 = (
    "Henkel LOCTITE ECCOBOND FP4527 TDS(2018-11, 옛 Dexter Hysol FP4527)를 열어 확인했다. "
    "경화 후 물성으로 CTE(Tg 위·아래)·Tg(TMA/DSC)·글로브 높이·선수축·추출이온·흡습률·굽힘탄성률 10.3 GPa·"
    "탄성계수(23 degC) 5.5 GPa·파단연신 1.39%·굽힘강도 17,000 psi·인장강도 10,000 psi 를 인쇄한다 — "
    "밀도(비중)·포아송비·열전도율·비열 행이 없다. 57차 SA 확인.")
R_FP4526 = (
    "Henkel LOCTITE ECCOBOND FP4526 TDS(2014-12, 옛 Dexter Hysol FP4526)를 열어 확인했다. "
    "미경화 물성으로 점도·**비중 1.7**·입도·유동시간·가사시간·겔타임을, 경화 후로 CTE(Tg 위·아래)·Tg(TMA)·"
    "추출이온·굽힘탄성률 8,500 N/mm2 를 인쇄한다 — 포아송비·열전도율·비열·인장강도 행이 없다. "
    "형제 등급 FP4527 시트는 인장강도를 인쇄하는데 이 시트는 굽힘탄성률만 인쇄한다. 57차 SA 확인.")
R_AB965 = (
    "Henkel LOCTITE ABLESTIK 965-1L TDS(2014-10, 옛 ABLEBOND 965-1L)를 열어 확인했다. "
    "인장탄성률(DMTA, -65/25/150/250 degC 네 점)·물추출전도도·열전도율 3.0 W/(m-K)·체적저항·다이전단·랩전단을 인쇄한다 — "
    "밀도·포아송비·비열·인장강도 행이 없다. 강도축을 다이전단(kg-f/die)과 랩전단으로만 인쇄하는 것이 다이어태치 갈래의 계통적 관행이다. 57차 SA 확인.")
R_AB2025D = (
    "Henkel LOCTITE ABLESTIK 2025D TDS(2014-04)를 열어 확인했다 — 인장강도 행이 없다. "
    "인장탄성률(DMTA, 25~300 degC 여섯 점)·CTE(Tg 위·아래)·Tg(TMA)·추출이온·흡습률은 인쇄하고 "
    "강도축은 다이전단(2x2 mm 및 3x3 mm Si die on PBGA, 25/260 degC)으로만 낸다. 57차 SA 확인.")

R_ABF = (
    "값 출처인 Fujishima 2017(ICEP, doi 10.23919/icep.2017.7939390)의 물성표 셋을 다 열어 확인했다 — "
    "GX13/GX92/GX-T31 표 · GX-T31/GZ-41/GY 표 · LE 표가 인쇄하는 것은 "
    "CTE x-y(25-150 / 150-240 degC)·Tg(인장 TMA · DMA)·영률·인장강도·연신율·유전율·유전손실·흡수율·HAST 뿐이다. "
    "밀도·포아송비·열전도율·비열 행이 없다. 그리고 **Ajinomoto 는 ABF 계열의 공개 데이터시트를 내지 않는다** — "
    "21차 R1 이 제품 페이지가 정성 서술과 문의폼뿐임을 확인했고(브리프 127), 57차 SA 가 다시 접속을 시도했으나 응답이 없었다. "
    "원문에도 없고 붙일 벤더 시트도 없다. 57차 SA 확인.")
R_AGL1020 = (
    "값 출처인 Narahashi 2010(JIEP, doi 10.5104/jiepeng.3.86)의 AGL-1020 표를 열어 확인했다 — "
    "CTE x-y(25-150 / 150-240 degC)·Tg(인장 TMA · DMA)·유전율·유전손실·UL94 다섯 줄뿐이다. "
    "**같은 논문의 ABF 필름 표(GX-13 / New ABF)는 영률과 인장강도를 인쇄하는데 동판적층판인 AGL-1020 표에서는 그 두 줄이 빠진다** — "
    "밀도·포아송비·열전도율·비열도 없다. Ajinomoto 는 공개 데이터시트를 내지 않는다(브리프 127). 57차 SA 확인.")
R_KASAHARA = (
    "값 출처인 Kasahara 2016(ECTC, doi 10.1109/ECTC.2016.212) TABLE I 'MATERIAL PROPERTIES' 를 열어 확인했다 — "
    "CTE x-y 두 구간·Tg(인장 TMA · DMA)·저장탄성률(30 / 250 degC)·영률·인장강도·연신율·유전율·유전손실·흡수율뿐이다. "
    "밀도·포아송비·열전도율·비열 행이 없다. 원문이 이 필름을 'Developed film' 으로만 부르고 등급명을 인쇄하지 않아 "
    "**붙일 벤더 시트 자체가 없다**(성격상 등급 미확정이나, 집계가 읽는 칸이 둘뿐이라 여기 적는다). 57차 SA 확인.")
R_HORIKI = (
    "값 출처인 Horiki 2011(EPTC, doi 10.1109/eptc.2011.6184447)의 물성표를 열어 확인했다 — "
    "두께·Tg·CTE(X-Y, 25-150 degC)·디스미어 후 표면조도(Ra/Rz)·도금 박리강도·유전율·유전손실 일곱 줄뿐이다. "
    "밀도·탄성계수·포아송비·열전도율·비열·인장강도 행이 없다. 원문이 등급명을 인쇄하지 않아 붙일 벤더 시트도 없다. 57차 SA 확인.")
R_TAIYO = (
    "값 출처인 Wei 2016(ECTC, doi 10.1109/ectc.2016.183)의 PDM 물성표를 열어 확인했다 — "
    "PDM-1 과 PDM-4 에 대해 Tg·CTE(alpha1/alpha2)·Dk(20 GHz)·Df(20 GHz) 네 줄뿐이다. "
    "밀도·탄성계수·포아송비·열전도율·비열·인장강도 행이 없다. 그리고 PDM-1~4 는 상용 등급명이 아니라 "
    "**같은 논문이 정의한 실험 조합**(필러 크기 nano/micro x 표면처리 유무)의 코드라 붙일 벤더 시트가 존재하지 않는다. 57차 SA 확인.")

R_CHHANDA = (
    "값 출처인 Chhanda 2012(ITherm, doi 10.1109/itherm.2012.6231440)를 열어 확인했다 — "
    "율속·온도별 응력-변형 곡선에서 뽑은 유효탄성률과 UTS, 크리프 곡선과 Garofalo 상수, Prony 급수만 낸다. "
    "밀도·포아송비·선팽창·열전도율·비열의 **값이 인쇄되지 않는다**(포아송비는 G = E/2(1+nu) 식 안에만 나오고 수치가 없다). "
    "그리고 이 논문 자신이 그 이유를 적어 두었다 — verbatim: 'underfill mechanical property data are scarce on vendor datasheets, "
    "and typically only the room temperature elastic modulus is available'. Zymet 사는 없어져 시트를 구할 길도 없다. 57차 SA 확인.")
R_HOHLFELDER = (
    "값 출처인 Hohlfelder 2001(J. Mater. Res., doi 10.1557/jmr.2001.0037) TABLE I 'Salient mechanical properties for the BCB "
    "and underfill materials' 를 열어 확인했다 — 항복강도·인장강도·탄성계수·n·소성변형·파괴인성 여섯 열뿐이고 "
    "밀도·포아송비·선팽창·열전도율·비열 행이 없다. 본문도 실리카 충전율(62 wt%)과 경화조건만 밝힌다. "
    "**주의 — 이 표의 'n' 열(Zymet 0.62 · Dexter 0.77 · BCB-hard 0.68)을 포아송비로 읽으면 안 된다. "
    "등방재의 포아송비 상한 0.5 를 넘어 물리적으로 불가능하다**(브리프 443). Zymet 사는 없어져 시트를 구할 길도 없다. 57차 SA 확인.")
R_CHIU2018 = (
    "값 출처인 Chiu 2018(Microelectron. Reliab., doi 10.1016/j.microrel.2017.11.008)을 열어 확인했다 — "
    "경화도 의존 Prony 급수(Table 3)·DiBenedetto/Vogel 상수(Table 4)·탄성물성표(Table 6, 영률·포아송비·CTE)·화학수축변형만 낸다. "
    "밀도·열전도율·비열·인장강도가 인쇄되지 않는다. 원문이 이 EMC 를 '89 wt% 실리카 충전 상용 fan-out WLP 컴파운드' 로만 부르고 "
    "등급명·공급사를 인쇄하지 않아 붙일 벤더 시트도 없다. (포아송비 0.371 은 이번에 Table 6 에서 넣었다.) 57차 SA 확인.")
R_CHOWDHURY17 = (
    "값 출처인 Chowdhury 2017(ITherm, doi 10.1109/ITHERM.2017.8023955)을 열어 확인했다 — "
    "흡습 조건·시효시간별 응력-변형 곡선에서 뽑은 유효탄성률과 UTS, 그리고 CTE 만 낸다. "
    "밀도·열전도율·비열이 인쇄되지 않는다. 원문이 언더필을 등급명 없이 '상용 언더필' 로만 불러 붙일 벤더 시트도 없다. 57차 SA 확인.")
R_CHOWDHURY19 = (
    "값 출처인 Chowdhury 2019(ITherm, doi 10.1109/itherm.2019.8756500)를 열어 확인했다 — "
    "완화탄성률 마스터커브와 전단·체적 Prony 쌍, WLF 시프트 상수, 그리고 스트레인게이지로 잰 포아송비(0.2989~0.30)만 낸다. "
    "밀도·탄성계수·선팽창·열전도율·비열·인장강도가 인쇄되지 않는다. 원문이 언더필을 등급명 없이 부르므로 붙일 벤더 시트도 없다. 57차 SA 확인.")
R_WANG93 = (
    "값 출처인 Wang & Papathomas 1993(IEEE T-CPMT-B, doi 10.1109/33.273686)을 열어 확인했다 — "
    "무용제 조성표(CTE <40 ppm·Tg >125 degC·가사시간·점도·필러크기·알파선·추출이온), 열분해 표, "
    "기계물성표(굽힘탄성률 9.72 GPa·굽힘강도 82.0 MPa·파단변형 0.85%·인장탄성률 16.6 GPa·인장강도 65.5 MPa·연신 0.53%·"
    "고온강도 4점), 접착전단강도표가 전부다. 밀도·포아송비·열전도율·비열 행이 없다. "
    "IBM Endicott 사내 개발 수지라 벤더 시트가 존재하지 않는다. 57차 SA 확인.")
R_WANG93_E = (
    "원문(Wang 1993) 기계물성표의 'Tensile Modulus 16.6 GPa' 를 **넣지 않았다**. 같은 표 안에서 두 삼각검산이 갈린다(브리프 35) — "
    "굽힘 쪽은 82.0 MPa / 0.85% = 9.65 GPa 로 인쇄된 굽힘탄성률 9.72 GPa 와 0.7% 안에서 닫히는데, "
    "인장 쪽은 65.5 MPa / 0.53% = 12.36 GPa 라 인쇄된 16.6 GPa 와 34% 어긋난다. "
    "등방 충전 에폭시에서 인장탄성률이 굽힘탄성률의 1.7 배가 되는 것도 물리적으로 이상하다. "
    "**한 칸만 어긋나므로 그 칸만 버렸다**(브리프 141) — 굽힘탄성률·굽힘강도·인장강도·연신은 이미 들어 있고 그대로 둔다. "
    "이 칸은 '원문이 인쇄했으나 검산에서 기각' 이라 집계에는 아직 V5(진짜 남은 것)로 세어진다(56차 RA 초안 C 의 V6 제안). 57차 SA 판정.")

R_IND151_E = (
    "Indium Corporation 자사 Indalloy 편찬표(2006) 151행(92.5 Pb / 5.0 Sn / 2.5 Ag)의 "
    "'Young's Modulus (PSI x 10^6)' 열 = 2.0, 즉 13.8 GPa 를 **넣지 않았다**. 같은 표의 성분 순금속이 "
    "순 Pb 2.61e6 psi = 18.0 GPa · 순 Sn 6.1e6 psi = 42.1 GPa 이고 Ag 는 83 GPa 급이라 "
    "**인쇄값이 모든 성분보다 낮다**(브리프 25 의 혼합물 상하한 규칙). 부피분율 Pb 0.898 / Sn 0.0755 / Ag 0.0262 로 "
    "Reuss 하한을 재면 1/(0.898/18 + 0.0755/42 + 0.0262/83) = 19.2 GPa 라 인쇄값이 28% 아래다. "
    "같은 표의 Pb-Sn 계열 E 가 Sn 함량에 단조증가하는데(순 Pb 2.61 → 90Pb10Sn 2.76 → 80Pb20Sn 2.90 → "
    "70Pb30Sn 3.05 → 60Pb40Sn 3.34 → 순 Sn 6.1) 이 한 칸만 그 아래로 떨어진다. "
    "**그 칸만 버렸다**(브리프 141) — 같은 행의 비열 0.13 J/(g*degC) 와 인장강도 4,210 psi 는 각각 "
    "Kopp-Neumann 검산(136.6 J/(kg*K), 5% 안)과 The Solder Connection 표(295 kgf/cm2 = 28.9 MPa, 0.5% 안)를 "
    "통과해 넣었다. 57차 SA 판정."
)

R_PARSA = (
    "원문(Parsa 2014)이 이 재료를 'PWA 포팅용 실리콘 컴파운드' 라는 클래스명으로만 부르고 등급·공급사를 인쇄하지 않아 "
    "**붙일 벤더 시트가 원리적으로 없고**, 원문 자신도 코어 7물성을 인쇄하지 않는다. "
    "성격상 브리프 582 의 V4(등급 미확정)이지만 집계가 읽는 칸이 core_not_applicable 과 core_absent_from_vendor_sheet 둘뿐이고 "
    "V4 를 정하는 attributes.identification_status 는 병합기의 CURATION 접두어에 없어 운영까지 가지 않는다 — "
    "그래서 전파되는 이 칸에 적는다(브리프 593 의 자리 문제). "
    "앞 배치가 같은 판정을 자유 키 attributes.core_fill_sheet 에 적어 두어 집계가 못 읽고 있었다. 57차 SA 가 옮겼다.")
R_PALANIAPPAN = (
    "원문(Palaniappan 2000)이 네 상용 언더필을 제품코드 A/B/C/D 로만 인쇄해 등급이 원리적으로 확정되지 않는다(브리프 58) — "
    "붙일 벤더 시트가 없고 원문도 코어 7물성을 인쇄하지 않는다. "
    "성격상 브리프 582 의 V4 이지만 V4 를 정하는 attributes.identification_status 는 병합기의 CURATION 접두어에 없어 "
    "운영까지 가지 않으므로, 전파되는 이 칸에 적는다. "
    "앞 배치가 같은 판정을 자유 키 attributes.core_fill_sheet 에 적어 두어 집계가 V3(판정은 있으나 못 읽음)로 세고 있었다. 57차 SA 가 옮겼다.")

V: list[dict] = []
def add(mid, name, attr, keys, reason):
    V.append({"material_id": mid, "name": name, attr: {k: reason for k in keys}})

for mid, nm in ((2125,"솔더 페이스트 S3X48+M500"),(2126,"솔더 페이스트 S3X58+M500"),(2127,"솔더 페이스트 S3X70+M500")):
    add(mid, nm, NA, (RHO,E,NU,CTE,TC,CP,UTS), R_PASTE)

for mid, nm in ((2634,"NEG LS-1401S"),(2635,"NEG LS-2010"),(2636,"NEG LS-3051S"),(2637,"NEG LS-1301"),(2638,"NEG BF-0901")):
    add(mid, nm, VEND, (E,NU,UTS), R_NEG_A)
for mid, nm in ((2639,"NEG LS-3081"),(2640,"NEG LS-0118"),(2641,"NEG LS-0206"),(2642,"NEG LS-7105"),(2643,"NEG BF-0606")):
    add(mid, nm, VEND, (E,NU,TC,CP,UTS), R_NEG_B)

add(774,  "EPO-TEK 353ND",              VEND, (NU,TC,CP,UTS),      R_353ND)
add(776,  "EPO-TEK H20E (ICA-2)",       VEND, (NU,CP,UTS),         R_H20E)
add(1105, "Dexter/Henkel FP4527",       VEND, (RHO,NU,TC,CP),      R_FP4527)
add(2363, "Dexter/Henkel FP4526",       VEND, (NU,TC,CP,UTS),      R_FP4526)
add(1226, "LOCTITE ABLESTIK 965-1L",    VEND, (RHO,NU,CP,UTS),     R_AB965)
add(318,  "LOCTITE ABLESTIK 2025D",     VEND, (UTS,),              R_AB2025D)
for mid, nm in ((978,"ABF GX13"),(979,"ABF GX92"),(980,"ABF GX-T31"),(981,"ABF GZ-41"),(982,"ABF GY"),(983,"ABF LE")):
    add(mid, nm, VEND, (RHO,NU,TC,CP), R_ABF)
add(1241, "Ajinomoto AGL-1020 CCL",     VEND, (RHO,E,NU,TC,CP,UTS), R_AGL1020)
add(1291, "Hitachi ultra-low-loss film",VEND, (RHO,NU,TC,CP),      R_KASAHARA)
add(1315, "Low-Dk/low-CTE build-up film",VEND,(RHO,E,NU,TC,CP,UTS), R_HORIKI)
add(984,  "Taiyo Ink PDM-1",            VEND, (RHO,E,NU,TC,CP,UTS), R_TAIYO)
add(985,  "Taiyo Ink PDM-4",            VEND, (RHO,E,NU,TC,CP,UTS), R_TAIYO)
add(737,  "Zymet X6-82-5LV50",          VEND, (RHO,NU,CTE,TC,CP),  R_CHHANDA)
for mid, nm in ((1106,"Zymet X6-82-5"),(1107,"Zymet X6-82-8"),(1108,"Zymet X6-82-0")):
    add(mid, nm, VEND, (RHO,NU,CTE,TC,CP), R_HOHLFELDER)
add(744,  "EMC fan-out WLP (Chiu 2018)",VEND, (RHO,TC,CP,UTS),     R_CHIU2018)
add(617,  "Underfill Tg 137 C (Chowdhury 2017)", VEND, (RHO,TC,CP), R_CHOWDHURY17)
add(738,  "Underfill CAVE3 (Chowdhury 2019)",    VEND, (RHO,E,CTE,TC,CP,UTS), R_CHOWDHURY19)
# **한 재료의 판정 둘은 한 행에 담아야 한다** — apply_core_verdicts.py 가 재료의 attributes 를
# 시작할 때 한 번만 읽어 캐시하므로, 같은 material_id 로 행을 둘 내면 뒤엣것이 앞엣것을 덮는다.
V.append({"material_id": 1356, "name": "IBM Endicott C4 encapsulant",
          VEND: {k: R_WANG93 for k in (RHO, NU, TC, CP)},
          REJ: {E: R_WANG93_E}})
V.append({"material_id": 576, "name": "92.5Pb5Sn2.5Ag Solder Alloy", REJ: {E: R_IND151_E}})
add(616,  "Silicone potting (Parsa 2014)", VEND, (RHO,E,NU,CTE,TC,CP,UTS), R_PARSA)
for mid, nm in ((2305,"상용 언더필 A"),(2306,"상용 언더필 B"),(2307,"상용 언더필 C"),(2308,"상용 언더필 D")):
    add(mid, nm, VEND, (RHO,E,NU,CTE,TC,CP,UTS), R_PALANIAPPAN)

doc = {"batch": "57차 SA — packaging 코어 빈칸 판정", "verdicts": V}
out = pathlib.Path(__file__).with_name("sa02_core_verdicts.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
cells = sum(len(v) for r in V for k, v in r.items() if isinstance(v, dict))
print(f"{out.name}: 재료 {len({r['material_id'] for r in V})}종 · 판정 {len(V)}건 · 칸 {cells}")
for a in (NA, VEND, REJ):
    print(f"  {a}: {sum(len(r[a]) for r in V if a in r)}칸")
