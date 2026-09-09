# 71차 GC 가 연 문서로 코어 밀도 빈칸 판정을 새로 세우거나 보강하는 판정문 생성기
import json, os, sqlite3

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
    "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
NAME = {i: n for i, n in c.execute("select id,name from material")}

K = "core_absent_from_vendor_sheet"
V = []
def add(mid, text, key=K):
    assert mid in NAME, mid
    V.append({"material_id": mid, "name": NAME[mid], key: {"physical.density": text}})

MGC_COMMON = (
 "**[71차 GC — 벤더 제품표를 일문판·영문판 둘 다 열었다. 비중 행이 있으나 라미네이트의 것이 아니다]** "
 "이 재료는 이 파동 전까지 밀도 칸에 판정이 한 줄도 없었다. 이번에 벤더 제품표를 **두 지역판으로** 열었다 — "
 "일문 `https://www.mgc.co.jp/products/sc/btprint/lineup/fr4.html` 과 영문 `https://www.mgc.co.jp/eng/products/sc/btprint/lineup/fr4.html`. "
 "두 판은 **행 단위로 같다**(項目/Item · 測定条件/Condition · 単位/Unit · EL190T · EL230T 네 열, 熱膨張係数~耐燃性 까지 동일 순서). "
 "그리고 이 표에 비중처럼 보이는 행이 **하나 있다** — verbatim 일문 `樹脂比重 | A | － | 1.44 | 1.42` · 영문 `Specific Gravity of Resin | A | － | 1.44 | 1.42`. "
 "**이것을 이 재료의 밀도로 옮기지 않았다.** 행 이름이 스스로 밝히듯 이 1.44/1.42 는 **매트릭스 수지의 비중**이고 "
 "이 재료는 유리직물과 동박을 포함한 **동장적층판**이다. 유리(2.55)와 동(8.96)이 든 적층판의 밀도가 수지 비중과 같을 수 없다 "
 "(같은 표의 다른 행 — Tg·CTE·曲げ弾性率·ピール強度 — 은 전부 적층판 값이라 이 한 행만 대상이 다르다). "
 "69차 ED 가 두산 CCL 에서 잡은 '같은 등급의 두 숫자가 다른 물건' 함정과 같은 자리이고, "
 "70차 FB 가 FM300K 에서 면적중량÷두께를 안 넣은 것과 같은 규율이다. **적층판 밀도 행은 이 표에 없다.** "
 "㉠ SDS 경로도 닫혀 있다 — `https://www.mgc.co.jp/sitemap.xml`(391 kB)을 통째로 받아 훑었고 "
 "`sds`·`msds`·`安全` 적중이 **0건**이다. 이 벤더는 어떤 제품에 대해서도 SDS 를 웹에 두지 않는다. "
 "㉡ **지역축 검증** — 일문판과 영문판이 같으므로 70차 FB 가 세운 '미국판은 채우고 EU/일본판은 비운다' 가설은 이 벤더에서 성립하지 않는다."
)

add(2724, MGC_COMMON.replace("EL190T · EL230T", "EL190T · EL230T").replace("1.44/1.42", "1.44/1.42"))
add(2725, MGC_COMMON)
add(2726,
 "**[71차 GC — 벤더 제품표를 일문판·영문판 둘 다 열었다. 비중 행 자체가 없다]** "
 "이 재료는 이 파동 전까지 밀도 칸에 판정이 한 줄도 없었다. Chip-LED 용 BT 재료 제품표를 두 지역판으로 열었다 — "
 "일문 `https://www.mgc.co.jp/products/sc/btprint/lineup/led.html` · 영문 `.../eng/products/sc/btprint/lineup/led.html`. "
 "`一般材料特性一覧表 / Typical properties of Materials` 가 HL820WDI 한 열에 인쇄하는 것은 "
 "比誘電率·誘電正接(1 MHz·1 GHz) · 絶縁抵抗 · 表面抵抗 · 体積抵抗率 · 曲げ強さ · 曲げ弾性率 · 引張強さ · ヤング率 · "
 "ガラス転移温度(DMA 210 ℃ · TMA 180 ℃) · 熱膨張係数(縦横 15 · Z 45/180 ppm/℃) · ピール強度 · 耐燃性 **뿐이고 비중·밀도 행이 없다**. "
 "같은 벤더의 FR-4 표에는 `樹脂比重` 행이 있는데 이 LED 용 표에는 그것조차 없다 — 즉 시트마다 층이 다르다(브리프 601). "
 "일문판과 영문판이 행 단위로 같아 **지역축으로 갈리지 않는다**. "
 "SDS 경로도 닫혀 있다 — mgc.co.jp sitemap 전수에서 `sds|msds|安全` 적중 0건."
)

SB = (
 "**[71차 GC — 벤더 사양표를 일문판·영문판 둘 다 열었고 밀도 행이 구조적으로 없다]** "
 "이 재료는 이 파동 전까지 밀도 칸에 판정이 한 줄도 없었다. 스미토모베이클라이트 스미라이트 ELC 계열의 "
 "**사양 일람(仕様一覧 / Specifications)** 을 두 지역판으로 열었다 — "
 "일문 `https://www.sumibe.co.jp/product/hpp/circuitry/{PATH}/spec/index.html` 과 "
 "영문 `https://www.sumibe.co.jp/english/product/hpp/circuitry/{PATH}/spec/index.html`. "
 "**두 판은 행 단위로 같다** — 熱膨張係数(CTE X/Y/Z α1·α2) · ガラス転移温度(TMA/DMA/DSC) · はんだ耐熱 · 引き剥がし強さ · "
 "曲げ強さ · 曲げ弾性率 · 引っ張り強さ · 引っ張り弾性率 · 比誘電率 · 誘電正接 · 体積抵抗率 · 表面抵抗 · 吸水率 · 耐燃性 · 熱伝導率 로 끝나고 "
 "**比重·密度·Specific Gravity 행이 한 줄도 없다.** 표 꼬리에 벤더가 스스로 `上表のデータは代表値であり、保証値ではありません / "
 "The data mentioned above is not guaranteed value but representative one` 이라 적는다. "
 "㉠ 한 층 더 갔다 — 영문 카탈로그 PDF 두 건(`{PDF}`)을 받아 전권 검색했고 `specific gravity|densit|比重|g/cm` 적중 **0건**이다. "
 "㉡ SDS 경로 — `www.sumibe.co.jp/sitemap.xml` 은 404 이고 사이트맵 페이지(`/sitemap/`)가 매다는 회로재 링크 여섯 갈래 어디에도 SDS 구역이 없다. "
 "㉢ **지역축 검증** — 일문판과 영문판이 같으므로 70차 FB 의 지역 가설은 이 벤더에서 성립하지 않는다. "
 "IPC-4101 적층판이 밀도를 안 찍는 구조적 부재(브리프 585)의 같은 자리다."
)
for mid, path, pdf in [
    (2727, "sumilite-elc", "catalog001.pdf"), (2728, "sumilite-elc", "catalog001.pdf"),
    (2729, "sumilite-elc", "catalog001.pdf"), (2730, "sumilite-elc", "catalog001.pdf"),
    (2731, "sumilite-elc-pwb", "material001.pdf"), (2732, "sumilite-elc-pwb", "material001.pdf")]:
    add(mid, SB.replace("{PATH}", path).replace("{PDF}", pdf))

RESONAC = (
 "**[71차 GC — 벤더 총괄 카탈로그와 유럽 법인 제품페이지를 둘 다 열었고 밀도 행이 구조적으로 없다]** "
 "이 재료는 이 파동 전까지 밀도 칸에 판정이 한 줄도 없었다. 레조낙 **동장적층판 총괄 카탈로그** "
 "`COPPER CLAD LAMINATES 2023-2024`(영문, `https://www.resonac.com/sites/default/files/2024-07/2023-2024MCL_catalog_EN.pdf`, "
 "6.79 MB · 추출 텍스트 388 kB)를 전권으로 열었다. 이 카탈로그가 우리 표적 등급을 전부 덮는다 "
 "(MCL-E-795G · MCL-E-705G · MCL-E-700G(R) · MCL-E-770G(R) · MCL-E-679FG(R/S) 가 목차와 개별 절에 있다). "
 "각 등급의 `General Properties` 표가 인쇄하는 것은 Tg(TMA/DMA) · CTE(X·Y·Z, Tg 상하) · Solder Heat Resistance · T-260/T-288 · "
 "Decomposition Temperature · Copper Peel Strength · Surface Roughness · Flexural Modulus · Dielectric Constant · Dissipation Factor · "
 "Volume Resistivity · Surface Resistance · Insulation Resistance 이고 **밀도·비중 행이 없다** — "
 "전권 낱말 `density` 적중은 **2건뿐이고 둘 다 `high density electronic equipment`·`High density multi-layer PWB`** 라는 용도 서술이다(브리프 667). "
 "㉠ **지역축 검증** — 유럽 법인 페이지 `https://eu.resonac.com/project/e679fg/` 를 따로 열었고 표 구성이 본사 카탈로그와 같으며 밀도 행이 없다. "
 "일본 본사판과 유럽판이 같으므로 70차 FB 의 지역 가설은 이 벤더에서 성립하지 않는다. "
 "㉡ SDS 경로 — `www.resonac.com/sitemap.xml`(144 kB) 전수에서 `sds|msds` 적중 **0건**이다. "
 "69차 ED 가 확인한 것과 일치한다 — 히타치화성 시절 공개 SDS 색인은 납축전지와 커패시터 둘뿐이었고 회로재는 처음부터 없었다. "
 "IPC-4101 적층판의 구조적 부재(브리프 585)이고, 이 카탈로그가 그 규칙의 또 하나의 증거다."
)
for mid in range(2733, 2743):
    add(mid, RESONAC)

print("1부 판정", len(V), "건")

# ── 2부: 미국판 SDS 를 새로 열어 판정을 보강한다 ───────────────────────────────
V2 = []
def add2(mid, text, key=K):
    assert mid in NAME, mid
    V2.append({"material_id": mid, "name": NAME[mid], key: {"physical.density": text}})

OLED_HEAD = (
 "**[71차 GC — 미국 OSHA 서식 SDS 를 새로 열었다. {WHAT}]** "
 "69차 ED 가 연 것은 Ossila(영국, `EC-REGULATIONS 1907/2006 (REACH), 1272/2008 (CLP) & 2015/830` 를 표지에 인쇄) 판 하나였다. "
 "70차 FB 의 지역축 가설 — '미국판은 채우고 EU/UK 판은 비운다' — 을 이 갈래에서 시험하려고 **같은 CAS 의 미국 시장 SDS 를 새로 받았다.** "
)
OLED_TAIL = (
 " **지역축 결론(이 갈래 7종 전수)** — 미국판을 연 일곱 화합물 중 EU/UK 판이 비운 칸을 미국판이 채운 것은 **BCP 하나뿐**이고, "
 "그 BCP 조차 같은 미국 시장의 다른 두 공급사(TCI America · Chem-Impex)는 비운다. "
 "그리고 BCP 를 채운 바로 그 Thermo Fisher 템플릿이 **같은 개정 주기의 TCTA 시트에서는 같은 행을 `No data available` 로 비운다.** "
 "즉 이 갈래에서 칸을 가르는 것은 지역도 서식도 아니라 **그 물질에 대해 그 공급사가 값을 가지고 있느냐**다."
)

add2(1651, OLED_HEAD.format(WHAT="미국판도 비어 있다") +
 "㉠ **TCI America**(Portland, OR, USA) `Tris(2-phenylpyridine)iridium(III)` T1946, Revision 1(2018-07-06). "
 "표지가 `OSHA Haz Com: CFR 1910.1200` 을 인용하고 `NFPA Rating: Health 2 / Flammability 0 / Instability 0` · "
 "`HMIS Classification: Health 2 / Flammability 0 / Physical 0` 등급표를 단다 — 미국 서식이 맞다. "
 "9절 verbatim: `Relative density:                    No data available`. "
 "㉡ **Chem-Impex International**(Wood Dale, IL, USA) 카탈로그 41208, Version 1.0(2024-08-06). "
 "9절 verbatim: `VAPOR DENSITY   NO DATA AVAILABLE` · `RELATIVE DENSITY` — **값 칸이 통째로 비어 있다**(`-layout`·`-raw` 둘 다로 확인해 추출 잡음이 아니다). "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/TCI-America_fac-Ir-ppy-3-T1946_SDS_US_2018-07-06.pdf` · "
 "`Chem-Impex_fac-Ir-ppy-3-41208_SDS_US_2024-08-06.pdf`." + OLED_TAIL)

add2(1746, OLED_HEAD.format(WHAT="미국판도 비어 있다") +
 "**TCI America** `9,10-Di(2-naphthyl)anthracene` D4127, Version 1.1(2024-12-12). "
 "표지 verbatim `GHS classification in accordance with the OSHA Hazard Communication Standard (29 CFR 1910.1200) (OSHA HCS)` — 미국 서식이 맞다. "
 "9절 verbatim: `Relative vapor density  :   No data available` · `Relative density  :   No data available`. "
 "미국 시장에서 이 CAS(122648-99-1)를 파는 다른 공급사를 못 찾았다(Fisher·Acros·Alfa·Chem-Impex·Matrix 전부 취급 없음). "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/TCI-America_ADN-D4127_SDS_US_2024-12-12.pdf`." + OLED_TAIL)

add2(1761, OLED_HEAD.format(WHAT="미국판도 비어 있고, 같은 시트가 BCP 에서는 채운다") +
 "㉠ **Acros Organics / Fisher Scientific Company**(Fair Lawn, NJ, USA) `4,4',4\"-Tris(carbazol-9-yl)triphenylamine, 99%` "
 "AC459180010/050, Revision Number 5(2025-12-20). 표지 verbatim "
 "`This safety data sheet was created pursuant to the requirements of: US OSHA Hazard Communication Standard 2024 (29 CFR 1910.1200)`. "
 "9절 verbatim: `Vapor Pressure  No data available` · **`Density / Specific Gravity  No data available`** · `Bulk Density  No data available`. "
 "**같은 시트가 융점 행에는 `297 - 300 °C / 566.6 - 572 °F   Measured` 를 찍는다** — 서식이 막은 것이 아니라 값이 없는 것이다. "
 "㉡ **TCI America** T2274, Version 1.1(2024-11-14, OSHA HCS): `Relative density : No data available`. "
 "**이 건이 지역축 가설을 정면으로 깬다** — 같은 회사·같은 미국 템플릿·같은 개정 주기(2025-12-19 vs 2025-12-20)의 "
 "형제 시트가 BCP(4733-39-5)에서는 `Density / Specific Gravity  1.17 g/cm3` 를 찍고 TCTA 에서는 비운다. "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/AcrosOrganics_TCTA-AC459180_SDS_US_2025-12-20.pdf` · "
 "`TCI-America_TCTA-T2274_SDS_US_2024-11-14.pdf`." + OLED_TAIL)

add2(1762, OLED_HEAD.format(WHAT="미국판도 비어 있다") +
 "**TCI America** `1,1-Bis[4-[N,N-di(p-tolyl)amino]phenyl]cyclohexane` B2079, Version 1.1(2024-11-14, OSHA HCS 29 CFR 1910.1200). "
 "9절 verbatim: `Relative density  :   No data available`. 미국 시장에서 이 CAS(58473-78-2)를 파는 다른 공급사를 못 찾았다. "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/TCI-America_TAPC-B2079_SDS_US_2024-11-14.pdf`." + OLED_TAIL)

add2(1763, OLED_HEAD.format(WHAT="미국판도 비어 있다") +
 "**TCI America** `4,4'-Bis(9H-carbazol-9-yl)biphenyl` B2713, Version 1.1(2024-12-09, OSHA HCS 29 CFR 1910.1200). "
 "9절 verbatim: `Relative density  :   No data available`. 미국 시장에서 이 CAS(58328-31-7)를 파는 다른 공급사를 못 찾았다. "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/TCI-America_CBP-B2713_SDS_US_2024-12-09.pdf`." + OLED_TAIL)

add2(1764, OLED_HEAD.format(WHAT="미국판도 비어 있다") +
 "㉠ **TCI America** `1,3-Di-9-carbazolylbenzene (purified by sublimation)` D4087, Revision 1(2018-07-06). "
 "`OSHA Haz Com: CFR 1910.1200: Not classifiable` · NFPA/HMIS 등급표를 단 미국 구서식이다. "
 "9절 verbatim: `Relative density:   No data available`. "
 "㉡ **Chem-Impex** 42732, Version 1.0(2024-08-06): `RELATIVE DENSITY` 값 칸이 비어 있다. "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/TCI-America_mCP-D4087_SDS_US_2018-07-06.pdf` · "
 "`Chem-Impex_mCP-42732_SDS_US_2024-08-06.pdf`." + OLED_TAIL)

add2(1760,
 "**[71차 GC — 철회. 미국판 SDS 가 이 칸을 채운다. 밀도를 넣었다]** "
 "옛 판정은 *'밀도에 관한 한 시약 SDS 경로는 이 갈래에서 닫혀 있다(연 7건 전부 Not known)'* 였다. "
 "**그 7건은 전부 Ossila(영국, REACH·CLP) 판이었다.** 이번에 같은 CAS 의 **미국 OSHA 서식** 시트를 열었고 값이 있다 — "
 "**Thermo Fisher Scientific Chemicals, Inc.**(Ward Hill, MA) `Bathocuproin` B22841, Revision Number 5(2025-12-21), "
 "표지 verbatim `created pursuant to the requirements of: US OSHA Hazard Communication Standard 2024 (29 CFR 1910.1200)`. "
 "9절 verbatim: `Density / Specific Gravity             1.17 g/cm3` — **1170 kg/m^3** 을 넣었다. "
 "같은 9절이 `Physical State  Powder Solid` · `Melting Point/Range  279 - 283 °C` 를 찍고 **바로 다음 행에 `Bulk Density  No data available` 를 따로 둔다** — "
 "즉 1.17 은 겉보기 밀도가 아니라 참밀도 자리다. Acros Organics 판(AC161340, Revision 5, 2025-12-19)이 같은 행에 같은 수를 찍지만 "
 "**같은 Thermo 계열의 같은 템플릿이라 독립 출처로 세지 않았다.** "
 "**등급 2인 이유** — 9절의 `Remarks•Method` 열이 이 행에서 비어 있어 측정법이 인쇄되지 않았다. "
 "69차 ED 가 이 재료의 융점을 Ossila SDS 에서 t2 로 넣은 관례를 그대로 따랐다. "
 "**형태** — 인쇄값은 승화정제 분말의 것이고 Swensen 2011 의 소자층은 진공증착 비정질 박막이다. "
 "비정질 박막은 결정 분말보다 보통 몇 % 가볍지만 **그 보정을 계산해 넣지 않았고** `conditions.physical_form` 에 사실만 남겼다. "
 "**같은 미국 시장의 다른 공급사는 비운다** — TCI America(D0711, 2024-10-29)와 Chem-Impex(47659, 2024-08-06)는 `Relative density : No data available`. "
 "**옛 판정의 나머지(공급사 사양표가 밀도를 안 싣는다)는 그대로 맞아 아래에 보존한다.**\n\n")

add2(2486,
 "**[71차 GC — 형제 등급의 영문(수출)판 SDS 가 비중을 찍는다. 쓰지 않았다]** "
 "이 등급의 SDS 는 벤더 공개 색인(제품 120종 · 첨부 183건)에 **없다**(69차 ED 가 전수로 확인). "
 "이번에 **형제 등급**을 두 건 열었다 — `DST-9000` SDS(MSDS-J-064, Current Issue Date 2012.05.04)와 "
 "`DST-9000HT` MSDS(MSDS-DSE-J-067, 2015.12.18), 둘 다 **영문 수출판 구서식**(WHMIS 인용)이고 9절 verbatim이 같다: "
 "`SPECIFIC GRAVITY  :  (Water=1.0) 2.5 to 3.3`. **이 수를 이 재료에 넣지 않았다.** 두 이유다. "
 "㉠ **등급이 다르다** — 문서는 DST-9000 · DST-9000HT 이고 표적은 DST-9000S 다. "
 "㉡ **더 중요한 것 — 그 2.5~3.3 은 재료의 밀도가 아니라 조립체의 겉보기 밀도다.** "
 "같은 문서 1절이 `OTHER/GENERIC NAMES : Al based Cu Clad Laminate` 라 적고 2절이 "
 "`Copper 2.4~88 wt%` · `Cured Epoxy Resin Blend 1.45~40 wt%` · `Al 9.65~94.3 wt%` 를 적는다 — "
 "**알루미늄 방열판 두께가 구성마다 달라 비중이 2.5~3.3 으로 벌어지는 것**이지 한 재료의 산포가 아니다(폭 32 %). "
 "이 재료가 담고 있는 값들(Dk 6.5 · 열전도율 2.5 W/mK · CTE 25/55 ppm · Tg 130 ℃)은 **절연층**의 것이라 "
 "동·알루미늄을 포함한 적층 스택의 밀도와 대상이 다르다 — 69차 ED 가 두산 CCL 에서 잡은 함정, "
 "70차 FB 가 FM300K 면적중량÷두께에서 멈춘 자리와 같다. "
 "**지역축** — 두산은 국문판과 영문판을 따로 낸다. 61쌍 중 4쌍은 영문만, 2쌍은 국문만 비중을 찍어 방향이 갈린다. "
 "예측하는 것은 언제나 템플릿이다(구판 21/21 찍음 · 신판 1/160). "
 "사본 `/data/paper_patent_corpus/standards_appnotes/sds/Doosan_DST-9000_SDS_2012-05-04.pdf` · `Doosan_DST-9000HT_SDS_2015-12-18.pdf`.")

DOOSAN_NO_SDS = (
 "**[71차 GC — 벤더 공개 색인에 이 등급의 SDS 가 없다는 것을 한 번 더, 지역판까지 확인했다]** "
 "68차 DA·69차 ED 가 `doosanelectronics.com` 의 MSDS 목록 엔드포인트로 제품 120종 · 첨부 183건을 전수로 받았다. "
 "이번에 **제품 페이지가 가리키는 다른 도메인**(`www.doosanelectromaterials.com`, 이 재료의 출처 URL)이 같은 사이트인지 확인했다 — "
 "두 도메인이 **같은 `/kr` 로 리다이렉트하고 같은 51,604 바이트 문서를 준다.** "
 "`POST /rest/product/msds/list` 를 `{}`·`{\"lang\":\"en\"}`·`{\"language\":\"en\"}` 세 가지로 불러도 **응답이 230,290 바이트로 똑같다** — "
 "즉 **MSDS 색인은 언어·지역으로 갈리지 않는 한 벌**이고 69차 ED 가 이미 그 전수를 열었다. "
 "이 등급의 영문 제품 페이지(`/en/product/Copper_Clad_Laminate/{GRADE}`)는 열리지만 "
 "`<ul id=\"contents-msds\"></ul>` 이 **빈 채로** 렌더된다 — 매달린 SDS 가 한 건도 없다는 뜻이다. "
 "**문서를 못 연 것이므로 '9절에 없다' 고 적지 않는다.** "
 "다만 같은 벤더의 열린 문서 181건이 말해 주는 것은 있다 — 비중을 찍는 것은 **구서식** 21건뿐이고 "
 "GHS 신서식은 160건 중 1건(그 1건도 성분값)이다. 지역판(국문 61 · 영문 120)으로 갈리지 않는다."
)
for mid, grade in [(2461,"DS-7409DYN"),(2462,"DS-7409DYN2"),(2463,"DS-7409DYQ"),(2480,"DS-9000")]:
    add2(mid, DOOSAN_NO_SDS.replace("{GRADE}", grade), key="core_no_public_document")

DOOSAN_NEW_TMPL = (
 "**[71차 GC — 이 등급의 SDS 는 신서식판 하나뿐이고 지역판이 갈리지 않는다]** "
 "69차 ED 가 이 등급의 문서를 열어 `N. Specific gravity  No data available` 를 확인했다. "
 "이번에 **지역판이 따로 있는지**를 물었다. 두산의 공개 색인에서 이 등급에 달린 파일은 {DOCS} 이고 "
 "**둘 다 GHS 신서식**이라 두 판 다 비어 있다 — 즉 이 등급에 대해서는 '미국판을 찾아라' 가 통하지 않는다. "
 "같은 벤더에서 지역판이 실제로 갈리는 등급이 있기는 하다(DS-7409DV 계열은 영문 12건이 전부 구서식으로 "
 "`SPECIFIC GRAVITY : (Water=1.0) 1.9+/-0.2` 를 찍고 국문 3건이 전부 신서식으로 비운다) — "
 "**그러나 방향이 일정하지 않다.** 반대 방향도 둘 있다(DS-7402H BS (D) · DS-7409HD BS 는 **국문**이 구서식으로 "
 "`비중 2.0 +/- 0.5 (물=1.0)` 를 찍고 영문이 신서식으로 비운다). "
 "61개 국문/영문 쌍 중 54쌍은 양쪽 다 비고 4쌍은 영문만 · 2쌍은 국문만 찍는다. "
 "**예측하는 것은 지역이 아니라 템플릿이다** — 구판 21/21 찍음 · 신판 1/160. 69차 ED 의 진단이 지역축까지 포함해 그대로 맞는다."
)
add2(2483, DOOSAN_NEW_TMPL.replace("{DOCS}", "영문 `GHS-MSDS DSR-1000 BS_231220_Ver.2.pdf`(2023-12-20) 한 건"))
add2(2509, DOOSAN_NEW_TMPL.replace("{DOCS}", "영문 `General_DS-7409S (N) BS_SDS_240404_Ver.7.pdf`(2024-04-04)와 국문 `DS-7409S(N)BS_MSDS_210520.pdf`(2021-05-20) 두 건"))

ROGERS = (
 "**[71차 GC — 이 벤더의 SDS 는 지역판이 아니라 한 벌의 번역판이고 여섯 판 전부 비어 있다]** "
 "70차 FB 는 다음 파동에 '미국판 SDS 를 표적으로 삼아라' 를 넘겼다. 이 벤더에서 그것을 시험했고 **가설이 성립하지 않는다.** "
 "코퍼스에 있는 RO4000 계열 문서 여섯 판을 전부 다시 열어 9절을 대조했다 — "
 "㉠ 미국 MSDS(2009-05-12, en) `SPECIFIC GRAVITY:  NA (Water = 1)` · `DENSITY:  NA` "
 "㉡ PSIS(2022-07-05, en) `SPECIFIC GRAVITY: NA (Water = 1)` · `RELATIVE DENSITY: NA` "
 "㉢ PSIS(2022-07-05, cn) `比重： NA（水= 1）` "
 "㉣ SDS(2014-03-13 · 2018-02-19, fr) `DENSITÉ RELATIVE:  S.O.` "
 "㉤ SDS(2018-02-19, de) `DICHTE:  Nicht zutreffend` "
 "㉥ SDS(2014-03-13, sp). "
 "**결정적인 것은 서식이다** — 같은 문서 한 장이 `HMIS RATING: H 1 F 1 R 0`(미국)과 "
 "`REGULATION (EC) N° 1907/2006`(EU)을 **동시에** 인용한다. 즉 Rogers 는 미국판과 EU 판을 따로 내지 않고 "
 "**미국에서 쓴 한 벌을 다섯 언어로 번역해 돌린다.** 지역판이 없으니 지역축도 없다. "
 "그리고 2절이 비운 이유를 스스로 적는다 — verbatim `This material is produced as an “article” as defined in 29 CFR 1910.1200 and "
 "REGULATION (EC) N° 1907/2006 is therefore exempt from the Hazard Communication Standard and REACH`. "
 "70차 FB 가 확인한 것(EDL 의 `Rogers Corporation` 은 엘라스토머·테이프 사업부라 고주파 회로재가 0건)도 그대로 유효하다."
)
add2(1277, ROGERS); add2(1278, ROGERS)

add2(1273,
 "**[71차 GC — 이 벤더는 한 문서로 네 규제권을 덮는다. 지역판을 찾을 자리가 없다]** "
 "69차 ED 가 이 등급의 SDS 를 서로 다른 템플릿 세 세대로 열어 전부 비어 있음을 확인했다. "
 "이번 파동의 표적은 '미국판' 이었는데 **Isola 에서는 그 물음이 성립하지 않는다** — "
 "2016-10-03 · 2020-07-19 · 2024-02-26 판이 한 문서 안에서 "
 "`OSHA 29 CFR 1910.1200` · `REACH 1907/2006` · `CLP 1272/2008` · `WHMIS` 를 **모두** 인용한다. "
 "지역판이 나뉘지 않으므로 '미국판을 따로 찾아라' 로 열릴 문이 없다. "
 "가장 오래된 구판(2010-02-12, NFPA·WHMIS)도 `Specific Gravity:  Not Determined` 로 같다. "
 "판정은 그대로다 — 이 벤더는 적층판을 물품(article)으로 보고 9절 열여섯 행을 통째로 비운다.")

add2(2254,
 "**[71차 GC — 이 벤더에서는 미국판과 EU 판이 **둘 다** 찍는다. 그래도 Melinex 자체 문서는 여전히 못 열었다]** "
 "70차 FB 가 다음 파동에 '미국판 SDS 를 노려라' 를 넘겼다. 이 벤더에서 그것을 시험했더니 **가설의 반례가 나왔다** — "
 "㉠ 미국판 `MYLAR(R) POLYESTER FILM (NOT INCLUDING PVdC COATED TYPES)` MSDS MYL045(2009-10-26, OSHA·HMIS·NFPA 표기): "
 "`Specific Gravity: 1.2-1.4` "
 "㉡ EU 판 `Mylar(R) A Polyester Film` Article Information Sheet v2.8(2016-04-26, **DuPont Teijin Films Luxembourg SA**, REACH 표기): "
 "`Density: 1.23 - 1.41 g/cm3` "
 "**둘 다 찍고 EU 판이 오히려 더 정밀하다.** 즉 이 갈래의 빈칸은 지역 탓이 아니다. "
 "그리고 **두 판 다 못 쓰는 이유는 그대로다** — Mylar 는 Melinex 와 다른 상표이고, "
 "EU 판이 스스로 `Colour: various` 라 적듯 1.23-1.41 은 안료·보이드 함유판까지 덮는 계열 폭이다. "
 "**Melinex 자체 문서는 이번에도 못 찾았다** — 69차 ED 가 찾아 둔 역사적 색인 항목 "
 "`usa.dupontteijinfilms.com/informationcenter/downloads/Melinex_Film_MSDS.pdf` 는 아카이브 적중 0 이고 "
 "70차 FB 의 EDL 24,113 항목에서도 `melinex` 0건이다. **문서를 못 연 것이므로 '9절에 없다' 고 적지 않는다.**")

add2(618,
 "**[71차 GC — 같은 등급의 미국판을 OCR 로 읽었고 미국판도 비어 있다. 70차 FB 의 지역 가설을 정정한다]** "
 "70차 FB 는 이 벤더에서 '미국 Cytec 서식은 `Specific Gravity/Density` 를 채우고 EU/UK CLP 서식은 비운다' 를 세웠다. "
 "그 비교는 **FM 300(미국, 2017-02-05) vs FM 300-2(영국, 2023-08-25)** 였는데 **등급도 다르고 연도도 6년 차이다.** "
 "이번에 **같은 등급의 두 지역판**을 맞췄다 — EDL `item_id 40945` 로 받은 미국판 "
 "`FM(R) 300-2 Adhesive Red` SDS 0059418(Date Prepared 11/21/2017, **CYTEC INDUSTRIES INC., 504 CARNEGIE CENTER, PRINCETON, NEW JERSEY 08540, USA**, "
 "8절에 `OSHA (PEL): 200 ppm (TWA)`)은 이미지 전용 PDF 라 300 dpi 렌더 + OCR 로 읽었고 9절 verbatim이 "
 "**`Specific Gravity/Density:  Not available`** 이다. 영국판(`CYTEC ENGINEERED MATERIALS LTD, WREXHAM`, 2023-08-25)은 "
 "`Density  No data available` · `Relative density  No data available` 다. "
 "**같은 등급에서 미국판도 비었다** — 즉 FB 가 본 차이는 지역이 아니라 **제품**이 만든 것이다. "
 "이 등급(CYCOM 5250-4-RTM)에 대해서는 69차 ED 의 판정이 그대로다 — Solvay 는 SDS 를 메일 자동발송으로만 돌리고, "
 "옛 cytec.com 아카이브의 MSDS 1,368건은 전부 화학 사업부이며 복합재 갈래가 0건이고, "
 "70차 FB 가 훑은 EDL 의 Cytec 항목 50건에도 `cycom` 은 Cycom 3001 한 건뿐이다.")
add2(619, V2[-1]["core_absent_from_vendor_sheet"]["physical.density"])


DP100 = (
 "**[71차 GC — EU/UK/독일/프랑스판을 넷 다 열었다. 전부 미국판과 같은 수를 찍는다. 판정은 그대로다]** "
 "70차 FB 가 다음 파동에 '미국판 SDS 를 표적으로 삼아라' 를 넘겼다. **이 벤더에서 그 가설이 가장 확실하게 깨진다.** "
 "이 등급의 SDS 를 이제 **다섯 지역판**으로 가지고 있고 아홉 절이 모두 같은 수를 찍는다 — "
 "{ROWS} "
 "**미국·캐나다·영국·독일·프랑스 다섯 판이 한 칸도 다르지 않다.** 영국·독일·프랑스판은 표지에 "
 "`This Safety Data Sheet has been prepared in accordance with the REACH Regulation (EC) 1907/2006` / "
 "`Sicherheitsdatenblatt nach Verordnung (EU) 1907/2006 (REACH)` 를 명시한 **진짜 CLP/REACH 판**이다 — "
 "즉 EU 서식이 밀도 칸을 비운다는 일반화는 성립하지 않는다. "
 "**판정 자체는 바뀌지 않는다** — 이 수들은 여전히 **2액형의 A액·B액 각각**이고 혼합·경화물 밀도가 아니다. "
 "같은 9절이 형태를 못 박는다(`Physical state Liquid` · `Specific Physical Form Viscous` · 인화점 240~257 °C · 점도 수만 cP). "
 "혼합비가 9절에 없어 역산도 못 한다. 69차 ED·70차 FB 의 결론이 지역판 다섯을 다 열고도 그대로다."
)
add2(2389, DP100.replace("{ROWS}",
 "㉠ 미국판 Part A(2022-10-10) `Density 1.15 g/ml` · `Specific Gravity 1.15 [Ref Std:WATER=1]` / Part B(2025-06-13) `Density 1.17 g/ml` · "
 "㉡ 캐나다판(11-3180-4 v16.05, 2022-06-07) 같은 수 · "
 "㉢ **프랑스판**(11-3180-4 v3.00, 2019-06-05) `Densité 1,17 g/ml` · `Densité relative 1,17` / `Densité 1,15 g/ml` · `Densité relative 1,15 [Réf. Standard :Eau = 1]` · "
 "㉣ **독일판**(DP100 Plus Clear Kit, 05-6638-0 v2.05, 2022-10-12) `Dichte 1,15 g/ml` · `Relative Dichte 1,15 [Referenzstandard:Wasser = 1]` / `Dichte 1,17 g/ml` · "
 "㉤ **영국판**(DP100 Plus Clear, 2021-05-04)."))
add2(2418, DP100.replace("{ROWS}",
 "㉠ 미국판 Part A(2024-07-29) `Density 1.15 g/ml` / Part B(2024-11-11) `Density 1.18 g/ml` · "
 "㉡ 캐나다판(11-2403-1 v14.00, 2018-06-27) 같은 수 · "
 "㉢ **영국판**(11-2403-1 v15.00, 2020-02-18) `Density 1.18 g/ml` · `Relative density 1.18 [Ref Std:WATER=1]` / `Density 1.15 g/ml` · `Relative density 1.15` · "
 "㉣ **독일판**(11-2403-1 v12.00, 2020-02-18) `Dichte 1,15 g/ml` · `Relative Dichte 1,15` / `Dichte 1,18 g/ml` · "
 "㉤ **프랑스판**(11-2403-1 v2.01, 2022-07-28) `Densité 1,15 g/ml` / `Densité 1,18 g/ml`."))

add2(1360,
 "**[71차 GC — 2023년 개정판을 미국·영국·독일 세 지역판으로 열었다. 셋 다 찍고 셋 다 같은 값이며, 68차 DA 의 기각 사유가 그대로다]** "
 "68차 DA 가 2006년 미국 MSDS 의 `Specific Gravity (H2O = 1)  0.9521` 을 보고 **기각**했다 — 그것이 메시틸렌에 녹인 B-stage 액상 바니시의 값이고 "
 "이 재료는 스핀코팅 후 250 °C 로 경화한 유전막이기 때문이다. 이번 파동은 '미국판을 찾아라' 가 표적이었는데 "
 "**이 벤더는 세 지역판을 다 내고 셋 다 이 칸을 채운다** — "
 "㉠ 미국판 `CYCLOTENE(TM) 4022-35 Advanced Electronics Resin`(Issue Date 07/31/2023, `GHS classification in accordance with 29 CFR 1910.1200`): "
 "`Relative Density (water = 1)  0.94 at 25 °C (77 °F)` · `Liquid Density  0.94 g/cm3` "
 "㉡ 영국판(`Safety Data Sheet according to Regulation (EC) No 1907/2006 - Annex II`, Revision Date 06.09.2023, **Version 11.0**): "
 "`Density and / or relative density  Density  0.94 g/cm3` "
 "㉢ 독일판(`Sicherheitsdatenblatt gemäß Verordnung (EG) Nr. 1907/2006 - Anhang II`, Version 11.0): "
 "`Dichte und / oder relative Dichte  0,94 g/cm3`. "
 "**세 판의 수가 같다 — 지역이 이 칸을 가르지 않는다.** "
 "그리고 **여전히 넣지 않는다**: 같은 9절이 `Physical state  Liquid.` · `Flash point  closed cup 44 °C (111 °F) Literature (setaflash)` · "
 "`Kinematic Viscosity  192 mm2/s at 25 °C  Supplier` 로 **용매가 든 액상 바니시**임을 스스로 못 박는다. "
 "용매를 날려 굳힌 막의 밀도는 이 값이 아니다(2006년 0.9521 과 2023년 0.94 가 같은 물건이라는 것도 이로써 확인된다). "
 "**경화막 밀도는 여전히 부재다.** 사본 `/data/paper_patent_corpus/standards_appnotes/sds/DuPont-RohmHaas_CYCLOTENE-4022-35_SDS_US_2023-07-31.pdf` · "
 "`DuPont_CYCLOTENE-4022-35_SDS_GB_2023-09-06.pdf` · `DuPont_CYCLOTENE-4022-35_SDS_DE_2023-09-06.pdf`.")

# 옛 판정문을 잃지 않는다 — 병합기는 같은 물성키를 통째로 덮는다(브리프 594).
# 그래서 기존 텍스트를 읽어 새 문단 **뒤에** 그대로 붙인다(70차 FB 관례).
import re as _re
ATTR = {i: json.loads(a or "{}") for i, a in c.execute("select id,attributes from material")}
kept = 0
for r in V + V2:
    for attr in [k for k in r if k not in ("material_id", "name")]:
        old_text = (ATTR.get(r["material_id"], {}).get(attr) or {}).get("physical.density")
        if not old_text:
            continue
        new_text = r[attr]["physical.density"]
        if old_text.strip() in new_text:
            continue
        r[attr]["physical.density"] = new_text.rstrip() + "\n\n" + old_text
        kept += 1
print("옛 판정문 보존:", kept, "건")

json.dump({"batch": "71차 GC", "verdicts": V + V2},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gc71_03_verdicts.json"), "w"),
          ensure_ascii=False, indent=1)
print("wrote", len(V) + len(V2), "verdicts total")
