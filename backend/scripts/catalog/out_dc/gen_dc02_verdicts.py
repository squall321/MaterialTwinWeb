# -*- coding: utf-8 -*-
# 68차 DC 가 새로 연 형식(문)을 기존 부재판정에 덧붙이는 판정 갱신 파일을 만든다.
import json, io, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dc02_verdicts.json')
K = 'mechanical.youngs_modulus'
PCB = '/data/paper_patent_corpus/standards_appnotes/pcb/'

IPC = (
 u"**[68차 DC — 문 ①(IPC-4101 슬래시시트)을 열었고, 그 문은 이 물성에 대해 구조적으로 닫혀 있다]**\n"
 u"브리프가 기대한 첫 문은 `벤더 TDS 가 IPC-4101 /126 등을 명시하니 규격 본문이 요구 물성을 인쇄할 것` 이었다. 규격을 실제로 열었다.\n"
 u"① IPC 배포 **IPC-4101E 공식 목차**(https://www.electronics.org/TOC/TOC-IPC-4101E.pdf · 로컬 " + PCB + u"IPC_IPC-4101E_TableOfContents_2017.pdf). "
 u"§3.9.1 `Physical Requirements of Laminate Materials` 하위는 3.9.1.1 Peel Strength(+열스트레스후·고온·공정약품후 세 변형) · 3.9.1.2 Dimensional Stability · "
 u"**3.9.1.3 Flexural Strength** · **3.9.1.4 Flexural Strength at Elevated Temperature** · 3.9.1.5 Thermal Conductivity · 3.9.1.6 CTE(선택) · 3.9.1.7 Z-Axis CTE/Total Expansion(선택) · "
 u"3.9.1.8 Fracture Toughness(선택) **여덟이 전부이고 탄성률 항목이 하나도 없다**. §3.10 화학·§3.11 전기·§3.12 환경에도 없다.\n"
 u"② **ANSI/IPC-4101 1997 초판**(https://www.professionalplastics.com/professionalplastics/IPC-4101spec1997.pdf · 로컬 " + PCB + u"IPC-4101_1997_BaseMaterials_Rigid_Multilayer_Spec.pdf) — `modulus`·`elastic` 낱말 **0건**.\n"
 u"③ 슬래시시트 재판본 `Technical Data Sheet IPC4101/24`(로컬 " + PCB + u"LaminatedPlastics_IPC-4101-24_TechnicalDataSheet.pdf) — IPC Spec·보강재·수지계·ID Ref·Tg·Dk 여섯 칸뿐.\n"
 u"→ **결론: 슬래시시트는 굽힘'강도' 하한을 규정하지 그 등급의 탄성률을 규정하지 않는다. 이 문을 이 물성 때문에 다시 두드리지 마라.**\n"
 u"(부수 수확 — Panasonic 공식 대응표를 받아 두었다: R-1755V→/126, R-1755M·R-1755D→/99, R-1755E→/101, R-1766→/21, R-1566→/127. 로컬 " + PCB + u"Epec_IPC-4101E_SlashSheetMatrix_Panasonic.pdf)\n"
)

TECHNOLAM = (
 u"\n**[68차 DC — 문 ④를 찾아냈다: 유럽 공급사가 다시 낸 IPC-4101 서식 데이터시트. 다만 이 벤더에는 그 문이 없다]**\n"
 u"이번 배치가 실제로 연 문은 **유럽 라미네이트 공급사가 제조사 TDS 와 별개로 내는 `Data Sheet / Datenblatt`** 다. "
 u"그 서식은 IPC-4101 항목 1~18 을 따른 뒤 **`19. Other / weitere` 절을 덧붙여 IPC-4101 이 규정하지 않는 행을 더 찍는다** — "
 u"`Young's Modulus / E-Modul`(경사 Kettrichtung·위사 Schussrichtung 을 갈라서, GPa) · `Specific Heat at 25 °C` · `Density (50 % resin content)` · `Thermal Conductivity`(ASTM-E-1461 / ASTM-D-5470 두 값) · `Caloric Value` · `CTI`. "
 u"이 문으로 Nan Ya NP-175FR·NP-175FTL 의 영률이 실제로 열렸다(Technolam GmbH 판, 23-25 / 22-24 GPa).\n"
 u"그러나 발행처 Technolam 은 **Nan Ya 전용 파트너**다. 이 배치가 받아 본 Technolam 시트 **열넉 장이 전부 Nan Ya 계열**이고(NP-140TL/B · NP-155F · NP-175F · NP-175FBH · NPG-150N · NPG-151 · NPG-170TL/R/B · NPG-170D · NPG-180BH · NPGN-150PY · FR-4-11PY · UV-Block FR-4-86) "
 u"**이 벤더의 등급을 다루는 시트는 한 장도 없다.** 즉 이 등급에는 문 ④가 (적어도 이 발행처에는) 존재하지 않는다.\n"
 u"→ **다음 배치가 이어서 두드릴 곳**: Technolam 말고 다른 유럽·아시아 유통사가 같은 서식을 쓰는지. 독일어 검색어가 잘 먹는다 — `Datenblatt` + `E-Modul` + `Kettrichtung` + `Schussrichtung` + `Laminat`.\n"
)

PANA_LESSON = (
 u"\n**[68차 DC — 이 배치 최대의 형식 교훈: 제품별 TDS 가 아니라 벤더의 '국가별 총합 카탈로그'를 열어라]**\n"
 u"같은 배치에서 Panasonic 여섯 등급의 부재판정이 **깨졌다**. 깬 것은 새 TDS 가 아니라 **2013년 일본어 「電子回路基板材料」 총합 카탈로그(160쪽)** 였다. "
 u"그 카탈로그의 `特性一覧表《参考値》板厚：1.6mm` 두 쪽짜리 표는 제품별 TDS 가 한 번도 안 찍는 열들을 한꺼번에 찍는다 — "
 u"`ヤング率（引張り）ASTM D3039`(경사·위사) · `曲げ弾性係数 JIS C6481` · `ポアソン比 JIS K7113` · `比重` · `比熱 DSC法` · `熱伝導率 레이저플래시法`. "
 u"**교훈: 벤더의 제품 페이지·등급별 TDS·SDS 를 다 열고도 '없다'고 하기 전에, 그 벤더가 자국어로 내는 수십~수백 쪽짜리 총합 카탈로그를 찾아라.** "
 u"→ 이 등급에 대해 다음 배치가 두드릴 곳: 이 벤더의 **자국어 종합 카탈로그**(대만·중국 벤더면 `綜合型錄` / `综合型录` / `产品手册`, 일본이면 `総合カタログ`), 그리고 그 구판(웹아카이브).\n"
)

ISOLA = (
 u"\n**[68차 DC — 검색어 교훈: 이 업계에서 `Young's Modulus` 라는 이름은 굽힘시험을 가리키기도 한다]**\n"
 u"Isola 는 370HR·IS400·FR408 시트에서 `Young's Modulus` 행의 시험방법을 **`ASTM D790-15e2`(3점굽힘)** 으로 명시하고, 인장 갈래는 `Tensile Strength (ASTM D3039)`·`Poisson's Ratio (ASTM D3039)` 로 따로 둔다 "
 u"(로컬 " + PCB + u"Isola_370HR_Laminate_Prepreg_DataSheet_RevC_2021-04-15.pdf — Young's Modulus Length 3744 ksi · Cross 3178 ksi = 25.8 / 21.9 GPa). "
 u"반대로 Panasonic 은 같은 표에 굽힘과 인장을 **두 열로 갈라** 찍는다(23~24 GPa 대 17.8~20.9 GPa — 인장이 12~23 %% 낮다). "
 u"→ **다음 배치는 `tensile modulus` 만 검색하지 마라. `Young's Modulus`·`E-Modul`·`ヤング率`·`弹性模量` 를 다 걸고, 찾은 뒤에 시험방법 칸을 반드시 확인해라.**\n"
)

SCHOLAR = (
 u"\n**[아직 안 열린 문 하나 — 학술 전문(全文)검색]**\n"
 u"문 ③(이 등급을 시편으로 쓴 논문)은 **제대로 열리지 않았다.** OpenAlex·Semantic Scholar 는 제목·초록만 색인해서 논문 *표 안*에 사는 등급명을 못 찾고, "
 u"DuckDuckGo·Mojeek·scholar.archive.org·HathiTrust 전문검색은 이 실행환경에서 막혔다(403·DNS). "
 u"**이 문에 대한 0건은 부재의 근거가 아니다.** 다음 배치는 Google Scholar 세션이나 CORE/Elsevier 전문색인 키로 이 문만 따로 두드려라.\n"
)

V=[]
def add(mid,name,verdict,reason,url,path):
    V.append({"material_id":mid,"key":K,"verdict":verdict,"name":name,"reason":reason,"source_url":url,"local_path":path})

IPC_URL="https://www.electronics.org/TOC/TOC-IPC-4101E.pdf"
IPC_PATH=PCB+"IPC_IPC-4101E_TableOfContents_2017.pdf"

for mid,nm in [(2433,u"Elite Material EM-370(Z) / EM-37B(Z) High-Tg Halogen-Free Laminate"),
               (2434,u"Elite Material EM-370(5) / EM-37B(5) Mid-Tg Halogen-Free Laminate"),
               (2435,u"Elite Material EM-890 / EM-89B High-Tg Ultra-Low-Loss Halogen-Free Laminate"),
               (2517,u"Elite Material EM-888 / EM-888B High-Tg Low-Loss Halogen-Free Laminate"),
               (2518,u"Elite Material EM-891 / EM-891B High-Tg Ultra-Low-Loss Laminate")]:
    add(mid,nm,"core_absent_from_vendor_sheet",
        u"기존 판정(제조사 TDS 의 `Basic Laminate Property` 표에 탄성률 **행 자체가 없다**)은 그대로 맞는다. 68차 DC 가 그 위에 **TDS 밖의 형식 셋을 더 열었다.**\n\n"
        + IPC
        + u"\n**[68차 DC — 문 ②(벤더 설계가이드·응용노트·기술회보)]** emctw.com 공개 문서 구역을 전수로 폈다 — 제품 목록 페이지가 내주는 PDF **48 장이 모두 등급별 TDS 한 종류**이고 "
          u"`Design Guide`·`Processing Guide`·`Technical Bulletin` 에 해당하는 문서가 공개 사이트에 **존재하지 않는다**. "
          u"유통사 경로도 폈다 — insulectro.com/em-370z · pcbdirectory.com 의 EM-370(Z) 전체 스펙표 · 중국 미러의 EM-370(Z)-15 TDS. 모두 같은 TDS 의 사본이고 탄성률 행이 없다. "
          u"EM-890 TDS 를 다시 확인하면 이 벤더의 강도축은 `Flexural Strength Warp 430~470 MPa / Fill 410~450 MPa` 하나다 — **강도이지 탄성률이 아니다.**\n"
        + TECHNOLAM + PANA_LESSON + ISOLA + SCHOLAR,
        IPC_URL, IPC_PATH)

for mid,nm in [(601,u"Shengyi S1170 high-Tg (170 degC) epoxy glass copper clad laminate"),
               (2516,u"Shengyi S1170G Halogen-Free High-Tg Copper Clad Laminate"),
               (2443,u"Shengyi S7439 High-Speed Low-Loss Laminate")]:
    add(mid,nm,"core_absent_from_vendor_sheet",
        u"기존 판정(데이터시트 GENERAL PROPERTIES 와 MSDS 9항 어디에도 영률이 없다)은 그대로 맞는다. 68차 DC 가 그 위에 **형식 넷을 더 열었다.**\n\n"
        + IPC
        + u"\n**[68차 DC — 문 ②(벤더 공정가이드)를 실제로 받았다]** shengyi-usa.com 이 S7439 에 대해 TDS 말고 **`Process Guidelines` 와 `Lineups`** 를 따로 내는 것을 확인하고 셋 다 받아 낱말 검색을 걸었다 — "
          u"`modulus`·`GPa` **0건**. S7439G 데이터시트도 같다. S1170 은 shengyi-usa.com 에 등재조차 없어 스캔 브로슈어(V15.0, mclpcb.com 미러)를 눈으로 읽었고 강도축은 "
          u"`Flexural Strength LW ≥415 / 587 MPa, CW ≥345 / 531 MPa` 하나였다. paramount-usa.com 의 2006년 S1170 전체 물성표(텍스트 추출됨)에도 탄성률 행이 없다.\n"
        + u"\n**[68차 DC — 로컬 웹표 xlsx 를 셀 단위로 다시 폈다]** `Shengyi_S1170G_HalogenFree_WebTable_2017-08.xlsx` 의 공유문자열 79 개를 전부 뽑아 확인했다 — "
          u"TEST ITEMS 는 Tg·난연·체적/표면저항·Dielectric Breakdown·Dk/Df·Thermal Stress·**굽힘강도 LW/CW**·흡수율·CTE Z·Td·T288/T260·Arc·박리강도뿐이고 "
          u"`modul`·`弹性`·`彈性`·`Young` **0건**이다.\n"
        + TECHNOLAM + PANA_LESSON + ISOLA
        + SCHOLAR + u"특히 이 벤더는 **중국어 문헌(CNKI)에서 `生益 S1170` 의 `弹性模量`** 이 나올 여지가 크게 남아 있다.\n",
        IPC_URL, IPC_PATH)

add(2521, u"Panasonic R-1566S Halogen-Free Automotive Glass Epoxy Laminate", "core_absent_from_vendor_sheet",
    u"기존 판정(Panasonic 문서 일곱 층 어디에도 인장 영률이 없다)은 **이 등급에 대해서는 그대로 맞는다** — 다만 같은 배치가 형제 등급 여섯(R-1755V/M/D/E · R-1566 · R-1766)의 판정은 깼으므로 그 경위와 이 등급만 남은 이유를 적는다.\n\n"
    u"**[68차 DC — 여덟 번째 층을 열었다. 그러나 이 등급이 그 표에 없다]**\n"
    u"형제들의 영률은 **2013년 일본어 「電子回路基板材料」 총합 카탈로그**(160쪽, PDF 제목 `Electronic Materials`, 저자 `Panasonic Corporation`, 2013-03-08)의 "
    u"`特性一覧表《参考値》板厚：1.6mm` 표에서 나왔다 — 그 표에 `ヤング率（引張り） ASTM D3039` 열이 경사·위사로 갈려 있다. "
    u"**그런데 그 표의 품번 목록에 R-1566S 가 없다.** R-1566S 는 이 카탈로그보다 뒤에 나온 등급이고(제품페이지 기준 할로겐프리 자동차용 신품종), 표에 실린 것은 `R-1566` 까지다. "
    u"로컬 " + PCB + u"Panasonic_ElectronicMaterials_catalog_2013_JP_YoungsModulus_ASTM-D3039_table.pdf 로 확인했다.\n\n"
    u"**[68차 DC — 이 등급 전용 문서 둘을 더 폈고, 탄성률은 '숫자'가 아니라 '그래프'로만 있다]**\n"
    u"① `Panasonic_CircuitBoardMaterials_Catalog_2020-07_R-1566S_ja.pdf` — 이 등급 전용 카탈로그다. 여기에 **`●曲げ弾性率` 그래프가 있다**(세로축 曲げ弾性率 0~30 GPa, 가로축 温度 0~200 ℃). "
    u"**그러나 그것은 온도-탄성률 곡선이고 표에 인쇄된 숫자가 아니다.** 곡선을 눈으로 읽어 넣는 것은 추정이라 규율상 넣지 않았다.\n"
    u"② `Panasonic_HalogenFree_R-1566S_ProductPage_ja_2026-09-02.html` — 一般特性 표를 태그를 걷어 내고 셀 단위로 다시 읽었다. **`弾性率` 낱말이 0건이다**(형제 페이지 hiperm·hipere 에는 `曲げ弾性率` 행이 있는데 이 페이지에는 그 행 자체가 없다).\n\n"
    u"**→ 다음 배치가 이 한 칸을 닫는 두 갈래.** (가) **2013 카탈로그의 최신판을 찾아라** — 같은 서식의 뒷 판(2015·2019·최근판)에는 R-1566S 행이 있을 수 있다. 그 표에는 `ヤング率（引張り）`·`ポアソン比`·`比熱`·`熱伝導率` 가 함께 들어 있어 한 문서로 여러 칸이 닫힌다. "
    u"(나) 2020-07 카탈로그의 굽힘탄성률 곡선을 digitize_curve 로 읽되 **method `digitized` · t4 로** 정직하게 넣어라(상온 절편만).\n"
    + ISOLA,
    "https://www.relianceems.com/static/upload/file/20260123/1769167011136894.pdf",
    PCB+"Panasonic_ElectronicMaterials_catalog_2013_JP_YoungsModulus_ASTM-D3039_table.pdf")

add(2694, u"LEXAN 3413R (PC-GF30, SABIC)", "core_absent_from_vendor_sheet",
    u"기존 판정(64차 ZA)은 `Americas·Asia·UL Prospector 세 장이 다 ASTM 서식이라 Flexural Modulus 6610 MPa 만 찍고 Tensile Modulus 행이 없다. 성격상 V5 — 벤더가 안 찍는 게 아니라 3413R 의 Europe(ISO) 층을 아직 못 열었다` 였다. "
    u"68차 DC 가 그 두 갈래를 다 두드렸고, **판정을 V5(못 연 것)에서 '그 층이 이 등급에는 존재하지 않아 보인다'로 좁힌다.**\n\n"
    u"**[68차 DC — ① 아직 안 열렸던 Asia 개정판을 새로 열었다]**\n"
    u"64차가 연 Asia 판은 Rev 20180905 였다. 이번에 **Rev 20190920 판**을 새로 받아 열었다(로컬 /data/paper_patent_corpus/standards_appnotes/poly/SABIC_LEXAN_FR_Resins_3413R_Asia_TDS_Rev20190920.pdf, "
    u"출처 http://www.honcere.com/upfile/2020020311083058.pdf). 표제가 `LEXAN FR RESINS 3413R / REGION ASIA / TYPICAL PROPERTY VALUES  Revision 20190920` 다. "
    u"MECHANICAL 절 전체 verbatim — `Tensile Stress, brk, Type I, 5 mm/min 99 MPa ASTM D 638` · `Tensile Strain, brk 2 % ASTM D 638` · `Flexural Stress, yld, 1.3 mm/min, 50 mm span 153 MPa ASTM D 790` · "
    u"**`Flexural Modulus, 1.3 mm/min, 50 mm span 6610 MPa ASTM D 790`** · `Hardness, Rockwell M 92` · `R 120` · `Taber Abrasion 24`. "
    u"**한 해 뒤 개정판에도 Tensile Modulus 행이 없다** — 인장 갈래는 강도·연신만 찍고 강성은 굽힘으로만 찍는 것이 SABIC 의 ASTM 서식 규칙이다.\n\n"
    u"**[68차 DC — ② Europe(ISO) 층을 겨냥해 두드렸고, 이 등급에는 그 층이 안 보인다]**\n"
    u"SABIC 지역판 TDS 를 호스팅하는 곳들을 이 등급 이름으로 직접 두드렸다 — pakrokimya.com(Americas 판과 **3412ECR Europe 판**을 실제로 호스팅하는 곳) · petromall.net(`lexan-fr-resins_<grade>_europe_technical_data_sheet.pdf` 규칙) · "
    u"plastore.it(`cgi2018/file818/<n>_pc lexan <grade>.pdf` 규칙, 758~767 훑음) · campusplastics.com · materialfinder.sabic-specialties.com. "
    u"**3413R 의 Europe 판은 어느 경로에서도 나오지 않았고, 같은 규칙으로 `3412ECR Europe` 은 200 으로 열린다**(petromall.net/wp-content/uploads/2026/03/lexan-fr-resins_3412ecr_europe_technical_data_sheet.pdf). "
    u"검색 결과도 3413R 에 대해서는 Americas·Asia 두 지역만 되풀이해 내놓고, SABIC 의 유럽 FR·유리충전 계열은 3412ECR/3413ECR 쪽으로 갈린다. "
    u"→ **즉 `Europe ISO TDS 를 아직 못 열었다`(V5)가 아니라 `이 등급에는 Europe 판이 없어 보인다`(V2 쪽)로 성격이 바뀐다.** 다만 이것은 호스팅 경로 탐침이지 SABIC 의 공식 부재 선언이 아니다 — 그 한계를 여기 밝힌다.\n"
    u"열지 못한 곳도 적는다 — matweb.com 의 `SABIC Lexan 3413R Polycarbonate (Europe)` 항목(matguid=2ac88f3836144bb293630db0dbfd54bf)은 **HTTP 403** 으로 못 열었고, "
    u"matmatch.com 은 이 환경에서 DNS·연결이 막힌다. **이 둘은 다음 배치가 다른 경로로 열어 볼 값이 있다** — matweb 이 Europe 항목을 따로 갖고 있다는 것 자체가 Europe 데이터의 존재를 시사한다.\n\n"
    u"**[68차 DC — 굽힘값으로 메우지 않은 이유]** 이 배치는 CCL 여섯 등급에서 굽힘·인장을 나란히 인쇄한 표를 얻어 **인장이 굽힘보다 12~23 %% 낮다**는 것을 확인했다. "
    u"그런데 유리충전 사출 열가소성은 스킨-코어 배향 때문에 그 대소가 **반대로** 나기도 한다 — 실제로 이 등급의 형제 3412R(GF20)은 Europe ISO TDS 의 `Tensile Modulus` 가 6000 MPa 인데 같은 등급의 ASTM 굽힘탄성률은 5511 MPa 로 **인장이 더 높다**. "
    u"즉 이 재료계에서는 굽힘 6610 MPa 를 영률로 옮길 때 방향도 크기도 예측할 수 없다. **그래서 굽힘값 대입을 하지 않고 칸을 비워 두었다 — 빈칸이 틀린 값보다 낫다.**",
    "http://www.honcere.com/upfile/2020020311083058.pdf",
    "/data/paper_patent_corpus/standards_appnotes/poly/SABIC_LEXAN_FR_Resins_3413R_Asia_TDS_Rev20190920.pdf")

PES_COMMON = (
    u"**[68차 DC — 원출처를 내 손으로 다시 폈다. 기존 판정이 맞는다]**\n"
    u"Thompson 1983 의 표 다섯 장을 구조화 추출본에서 전부 폈다(로컬 /data/paper_patent_corpus/structured/elec_papers/pcb_03_embedded_component/Thompson - 1983 - Polyethersulphone—A Thermoplastic PCB Substrate/tables/). "
    u"`Table 2 Mechanical Properties` 의 행은 **Tensile strength at 20/150/180 °C · Elongation at break · Flexural strength · Flexural modulus at 20/150/180 °C · Izod · Rockwell · Taber** 여덟이다 — "
    u"**강성축이 `Flexural modulus (ASTM D790)` 하나뿐이고 인장탄성률 행이 없다.** 인장 갈래는 강도와 연신만 찍는다. 기존 판정 그대로다.\n\n"
    u"**[68차 DC — ICI/Victrex 원자료 쪽으로 문 일곱을 새로 열었다. 모두 이 등급코드가 없다]**\n"
    u"① Victrex, `Comparison of PEEK, PPS, and PES Polymers Injection Moulded Grades`(victrex.com 공식) — `Tensile Modulus (ISO 527) ~2.65 GPa` 를 찍지만 **`PES (unfilled)` 라는 계열 이름뿐이고 등급코드가 한 번도 안 나온다.**\n"
    u"② Victrex `Materials Properties Guide` — PES 는 비교차트에만 나오고 PES 데이터시트 절 자체가 없다.\n"
    u"③ Sumitomo Chemical `SUMIKAEXCEL PES Technical Notes`(35쪽) — 등급코드가 **3600P/4100P/4800P/5200P** 계열이고 200P/300P/420P/430P 행도, ICI 코드 대응표도 없다.\n"
    u"④ NASA CR `Development of fire resistant, nontoxic aircraft interior materials`(NTRS 19770007262) — `Polyethersulfone 200P (PES 200P), Batch No. 7172/60, ICI` 로 **이 등급을 이름으로 부르지만** TGA·성형개시 데이터만 찍고 탄성률이 없다.\n"
    u"⑤ 高分子論文集 49(1) 7 (1992) — `ICI社製, Victrex PES 300P` 를 쓰지만 연신 블렌드의 인장강도·파단연신만 낸다.\n"
    u"⑥ 高分子論文集 50(8) 605 (1993) · 51(2) 99 (1994) — 인장탄성률(~2.9 GPa)을 내지만 쓴 재료가 **Victrex PES 4800P** 로 표적 등급이 아니다.\n"
    u"⑦ MatWeb·Victrex 웹 목록 — PES 계열값뿐이고 Victrex 등급 항목이 없다.\n\n"
    u"**열지 못한 곳(다음 배치의 표적)** — (가) Searle & Pfeiffer, `Victrex poly(ethersulfone) (PES) and Victrex poly(etheretherketone) (PEEK)`, Polym. Eng. Sci. 25(8):474-476 (1985), **ICI Americas 저자** — "
    u"유료장벽. **ICI 자신이 쓴 등급표가 실릴 가장 유력한 후보다.** doi 10.1002/pen.760250808. "
    u"(나) 원 브로슈어 `Victrex, Polyethersulphone, the High Temperature Resistant Technical Thermoplast`, Imperial Chemical Industries Ltd., 1979 — 특허 인용문에는 나오는데 온라인에 없다. "
    u"(다) matmatch.com 의 `Poly(ether sulfone), 30% Glass Fiber Reinforced (PES-GF30)` 페이지가 **`Victrex 430P` 를 상품명으로 열거**한다 — 다만 그 페이지 값은 PES-GF30 계열값이라 열어도 t3 다. 이 환경에서는 DNS 가 막혀 못 열었다.\n\n"
    u"**[68차 DC — 굽힘값으로 메우지 않은 이유]** 이 논문이 주는 굽힘탄성률(200P/300P 2.6 GPa · 420P 5.9 · 430P 8.2~8.4 @20~150 °C)을 영률 칸에 옮기지 않았다. "
    u"유리충전 사출 열가소성은 스킨-코어 섬유배향 때문에 굽힘탄성률이 인장탄성률을 웃도는 것이 보통이고(420P·430P), 그 차이가 등급마다 달라 예측이 안 된다. "
    u"무충전 200P/300P 는 굽힘 2.6 GPa 가 Victrex 공식 계열값 `Tensile Modulus (ISO 527) ~2.65 GPa` 와 우연히 가깝지만, **그 2.65 는 등급이 아니라 계열값이라 t3 이고 이 등급의 인쇄값이 아니다.** "
    u"빈칸을 지켰다.\n"
)
for mid,nm in [(1370,u"Victrex PES 200P/300P, unreinforced polyethersulphone (ICI, Thompson 1983)"),
               (1371,u"Victrex PES 420P, 20% glass-reinforced polyethersulphone (ICI, Thompson 1983)"),
               (1372,u"Victrex PES 430P, 30% glass-reinforced polyethersulphone (ICI, Thompson 1983)")]:
    add(mid,nm,"core_absent_from_vendor_sheet", PES_COMMON,
        "https://www.victrex.com/-/media/downloads/literature/compare-peek-pps-and-pes-polymers-table.pdf", None)

json.dump({"batch":"68차 DC","verdicts":V}, io.open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('verdicts:',len(V))
for v in V: print('  ',v['material_id'], v['name'][:56])
