# 69차 ED — 기존 부재판정에 '벤더 SDS 색인 전수 열람' 결과를 덧붙여 ed08_verdicts.json 을 만든다
import sqlite3, os, json, pathlib

DB = 'file:' + os.environ['MATERIALTWIN_DATA_DIR'] + '/materialtwin.db?mode=ro'
c = sqlite3.connect(DB, uri=True)
KEY = 'physical.density'
ABSENT = 'core_absent_from_vendor_sheet'
NA = 'core_not_applicable'

SDSDIR = '/data/paper_patent_corpus/standards_appnotes/sds'
IDX = 'backend/scripts/catalog/out_ed/indexes'

# ── 두산 — 색인 181건 전수 ────────────────────────────────────────────────
DOOSAN_HEAD = (
 "\n\n**[69차 ED — 두산 공개 MSDS 색인을 문서 단위로 전수 열었다]** 68차 DA 는 목록 **120건**(제품 단위)을 "
 "받아 이름만 대조했고 그중 14건만 폈다. 이번에는 그 목록이 매단 **첨부 183건 = 고유 파일 181건을 전부 내려받아 "
 "9절까지 폈다**(`POST https://www.doosanelectronics.com/rest/product/msds/list` 로 색인, "
 "`GET /file/productAttachment/download/<productAttachmentId>` 로 파일 — 인증 없다. "
 "색인·스캔 결과 사본은 `" + IDX + "/doosan_msds_index.json` 과 `doosan_msds_section9_scan.json`). "
 "181건 중 **비중에 실수를 찍은 것은 22건**이고, 그 22건 중 21건이 **구판 템플릿**(`SPECIFIC GRAVITY : (Water=1.0) ...`, "
 "제품 단위 한 칸)이다. 신판 GHS 템플릿(`N. Specific gravity`, CAS 성분 열)은 **160건 중 1건**만 수를 찍는데 "
 "그 하나(DSF-900SQ, 2023-04-11)조차 `1.33 - 1.45 g/cm3` 가 첫 열 CAS 25038-59-9(PET) 의 **성분값**이지 제품값이 아니다. "
 "즉 **구판 100 %(21/21) 대 신판 0.6 %(1/160)** — 부재의 원인은 개정 연도가 아니라 템플릿이다"
 "(구판은 2025-11-13 자 DS-7409DV (N) 까지 아직 발행된다)."
)

DOOSAN_ABSENT = DOOSAN_HEAD + (
 " 이 등급은 색인 120제품·181문서 **어디에도 없다.** 두산은 이 등급의 SDS 를 공개하지 않는다 — "
 "문서 단위 전수 열람으로 확인한 부재이지 검색 0건이 아니다."
)

def doosan_blank(fname, dateline, verbatim):
    return DOOSAN_HEAD + (
     f" 이 등급은 색인에 있고 문서도 열렸다 — {dateline}. 9절 verbatim: {verbatim} "
     f"**신판 GHS 템플릿이라 비어 있는 것**이고, 위 통계가 그 이유를 수치로 받친다. "
     f"로컬 사본 `{SDSDIR}/{fname}`."
    )

UPDATES = {}
for mid in (2461, 2462, 2463, 2480, 2486):
    UPDATES[mid] = {ABSENT: {KEY: DOOSAN_ABSENT}}

UPDATES[2483] = {ABSENT: {KEY: doosan_blank(
  "Doosan_DSR-1000-BS_MSDS_2023-12-20.pdf",
  "`GHS-MSDS DSR-1000 BS_231220_Ver.2.pdf`(개정 2023-12-20, 영문)",
  "`N. Specific gravity   No data available x5`(CAS 5열 전부).")}}
UPDATES[2509] = {ABSENT: {KEY: doosan_blank(
  "Doosan_DS-7409S-N-BS_SDS_2024-04-04_en.pdf",
  "영문 `General_DS-7409S (N) BS_SDS_240404_Ver.7.pdf`(2024-04-04)와 국문 `DS-7409S(N)BS_MSDS_210520.pdf`(2021-05-20) 두 판",
  "영문 `N. Specific gravity  No data available x3` · 국문 `하. 비중  자료없음 x3`.")}}

# ── 아지노모토 파인테크노 — 사이트 색인 전수 ──────────────────────────────
AFT = (
 "\n\n**[69차 ED — 벤더 사이트 색인을 통째로 받아 확인했다]** 68차 DA 는 ABF 제품 페이지 **한 장**을 보고 "
 "'SDS 링크가 없다' 고 적었다. 이번에는 **사이트 전체 색인을 받았다** — "
 "`GET https://www.aft-website.com/sitemap.xml` → `page-sitemap.xml`(Yoast SEO) 이 매단 **공개 페이지 75장 전부**를 "
 "각각 내려받아 `sds|msds|安全データシート|safety data` 를 찾았고 **적중 0장**이다. 사이트 전체에서 발견된 PDF 링크는 "
 "**단 하나**이고 그것은 모든 페이지 꼬리말에 같이 붙는 회사 문서라 제품 문서가 아니다. "
 "즉 아지노모토 파인테크노는 **어떤 제품에 대해서도 SDS 를 공개하지 않는다** — 이 갈래는 페이지 한 장이 아니라 "
 "색인 전수로 닫혔다. 색인 사본 `" + IDX + "/ajinomoto_aft_site_index.json`."
)
for mid in (978, 979, 980, 981, 982, 983, 1241):
    UPDATES[mid] = {ABSENT: {KEY: AFT}}

# ── 히타치화성(현 Resonac) — 아카이브 SDS 색인 ────────────────────────────
HITACHI = (
 "\n\n**[69차 ED — 벤더 SDS 색인을 아카이브에서 통째로 받았다]** 기존 판정은 논문·TDS 근거였다. "
 "SDS 형식으로 다시 물었다. 히타치화성은 현행 사이트(Resonac, sitemap 969 URL)에 SDS 색인이 없지만 "
 "**옛 사이트에는 공개 SDS 색인이 있었다** — `hitachi-chem.co.jp/{english,japanese}/products/sds/`. "
 "web.archive.org CDX 로 그 경로의 아카이브 URL **238건**을 통째로 받았고 그중 **SDS PDF 가 98건**이다. "
 "그런데 색인 표지(2016-01-04 스냅숏)가 스스로 밝히는 갈래는 `Industrial Batteries`(고정형 납축전지)와 "
 "`Capacitors` **둘뿐**이고, 98건도 전부 그 둘이다. **이방성도전필름(ANISOLM)·빌드업 필름·에폭시 수지는 "
 "이 벤더의 공개 SDS 색인에 처음부터 없었다.** 색인 사본 `" + IDX + "/hitachi_chem_archived_sds_index.json`."
)
for mid in (1098, 1291, 1430):
    UPDATES[mid] = {ABSENT: {KEY: HITACHI}}

# ── OLED 저분자 — Ossila 카탈로그 색인 + SDS 9절 ──────────────────────────
def ossila_opened(fname, cas, mp_line):
    return (
     "\n\n**[69차 ED — 시약 벤더 SDS 를 열었다]** 이 화합물은 등급명이 아니라 **CAS 로 동정되는 순물질**이라 "
     "시약 벤더 SDS 가 유효한 문서다. Ossila 전 상품 색인을 통째로 받고(Shopify `products.json`, **1,258 품목**, "
     "사본 `" + IDX + "/ossila_product_index.json`) 이 화합물의 SDS 를 내려받아 9절을 폈다 — "
     f"1절 `CAS No. {cas}` 로 동정이 걸린다. 9절 verbatim: `Density  Not known.` · `Relative density  Not known.` "
     "— **밀도는 이 SDS 에 없다.** 같은 9절이 `Particle characteristics  Not known.` 까지 비운다. "
     f"다만 **융점은 찍는다** — `{mp_line}` — 그 값은 이번에 `thermal.melting_point` 로 등재했다. "
     f"로컬 사본 `{SDSDIR}/{fname}`. **밀도에 관한 한 시약 SDS 경로는 이 갈래에서 닫혀 있다**(연 7건 전부 `Not known`)."
    )

OSSILA_MP = {
 1746: ("Ossila_ADN_SDS_2022-12-12.pdf", "122648-99-1", "Melting point/freezing point  382-384 °C (lit.)"),
 1760: ("Ossila_BCP-Bathocuproine_SDS_2022-12-12.pdf", "4733-39-5", "Melting point/freezing point  280-282 °C (lit.)"),
 1763: ("Ossila_CBP_SDS_2023-03-24.pdf", "58328-31-7", "Melting point/freezing point  281-285 °C (lit.)"),
 1764: ("Ossila_mCP_SDS_2023-03-24.pdf", "550378-78-4", "Melting point/freezing point  173-178 °C"),
 1762: ("Ossila_TAPC_SDS_2022-11-14.pdf", "58473-78-2", "Melting point/freezing point  186 °C"),
 1651: ("Ossila_Ir-ppy-3_SDS_2022-12-12.pdf", "94928-86-6", "Melting point/freezing point  451 °C (lit.)"),
}
for mid, (fn, cas, mp) in OSSILA_MP.items():
    UPDATES[mid] = {ABSENT: {KEY: ossila_opened(fn, cas, mp)}}

UPDATES[1761] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — 시약 벤더 SDS 를 열었다]** Ossila 전 상품 색인 1,258 품목을 받아 TCTA 를 찾아 SDS 를 폈다"
 f"(로컬 사본 `{SDSDIR}/Ossila_TCTA_SDS_2022-12-12.pdf`, 1절 `CAS No. 139092-78-7`). "
 "9절 verbatim `Density  Not known.` · `Relative density  Not known.` · "
 "`Melting point/freezing point  Not known.` — **밀도도 융점도 없다.** 형제 여섯(ADN·BCP·CBP·mCP·TAPC·Ir(ppy)3)은 "
 "같은 벤더 같은 템플릿에서 융점을 찍는데 TCTA 만 그 칸도 비어 있다.")}}

PO = (
 "\n\n**[69차 ED — 시약 벤더 색인을 받았으나 이 화합물이 없다]** Ossila 전 상품 색인을 통째로 받았고"
 f"(Shopify `products.json`, **1,258 품목**, 사본 `{IDX}/ossila_product_index.json`) "
 "이 포스핀옥사이드 호스트는 그 색인에 없다. OLED 전문 벤더 Lumtec 은 sitemap 이 MSDS PDF **211건**을 매달지만 "
 "그 URL 이 전부 404 로 죽어 있어 **문서를 열지 못했다**(살아 있는 한 건을 확인해 보니 Lumtec MSDS 9절은 "
 "`Appearance` 와 `Melting point(DSC)` 두 줄뿐이라 애초에 밀도가 없다). "
 "**문서를 못 연 것은 판정이 아니다** — 이 칸의 기존 판정은 그대로 두고 다음 파동에 넘긴다."
)
for mid in (1758, 1759):
    UPDATES[mid] = {ABSENT: {KEY: PO}}

# ── KOKI 솔더 페이스트 — '해당없음' 판정 철회 ─────────────────────────────
KOKI_RETRACT = (
 "**[69차 ED — 이 판정을 철회한다]** 옛 판정문은 아래에 그대로 보존한다. "
 "그 판정은 **밀도에 대해서는 틀렸다.** 벤더 SDS 가 이 제품의 밀도를 직접 찍는다 — "
 "KOKI Company Limited 의 EU CLP 판 안전보건자료(개정 2015-07-10, 체코어) 9절 verbatim "
 "`· Hustota při 20 °C:  4-5 g/cm3` 이고, 같은 절이 성상을 `Skupenství: Pastovité`(페이스트)로 못 박는다. "
 "1절 상품명 칸이 `S3X48-M500, S3X58-M500, S3X70-M500 ...` 로 이 세 등급을 명시적으로 덮는다. "
 "미경화 페이스트에 영률·포아송비·인장강도가 정의되지 않는다는 옛 판정의 논지는 지금도 맞지만, "
 "**밀도는 자립 시편을 요구하지 않는 물성이라 페이스트에도 정의되고 실제로 측정된다.** "
 "4-5 g/cm^3 를 상·하한 두 행(4000 / 5000 kg/m^3, 20 °C)으로 등재했다. "
 f"로컬 사본 `{SDSDIR}/KOKI_S3X48-M500-S3X58-M500-S3X70-M500_SDS_2015-07-10_cz.pdf`.\n\n---\n(옛 판정문)\n"
)
for mid in (2125, 2126, 2127):
    UPDATES[mid] = {NA: {KEY: KOKI_RETRACT}}


# ── Rogers RO4000 계열 — 판 7개·언어 5개 전수 ──────────────────────────────
ROGERS = (
 "\n\n**[69차 ED — SDS 형식으로 다시 열었다]** 기존 판정은 TDS·논문 근거였다. SDS 를 팠다. "
 "로저스는 **RO4350B·RO4003C 각각의 SDS 를 따로 내지 않는다** — 두 제품 페이지가 같은 계열 문서 "
 "`RO4000(R) Series Laminates` 하나를 건다. 그 문서를 **개정 7판·5개 언어**로 모아 9절을 전부 폈고 "
 "**모든 판이 이 칸을 비운다**. 최신 영문판(PSIS, 발행 2022-07-05) verbatim — "
 "`SPECIFIC GRAVITY:  NA (Water = 1)` · `RELATIVE DENSITY:  NA` · `MELTING POINT:  NA` · `VISCOSITY:  NA`. "
 "**구판이 채워 줄 것이라는 기대도 여기서는 깨진다** — GHS 이전 템플릿인 2009-05-12 판(`MSDS`)도 "
 "`SPECIFIC GRAVITY:  NA (Water = 1)` · `DENSITY:  NA` 로 똑같이 비어 있다. 독·불·서·중 판도 같다"
 "(`DICHTE: Nicht zutreffend` · `POIDS SPECIFIQUE: S.O. (Eau = 1)` · `GRAVEDAD ESPECIFICA: NA (Agua = 1)` · `比重: NA`). "
 "2절이 이유를 적는다 — 제품이 SDS 의무 대상이 아닌 **성형품(article)** 이다. "
 f"로컬 사본 8건 `{SDSDIR}/Rogers_RO4000-*`. 색인 사본 `{IDX}/rogers_sds_index.json` "
 "(로저스는 sitemap 도 문서 API 도 없다 — SDS 경로는 제품 페이지 HTML 에서 "
 "`/-/media/project/rogerscorp/documents/ehs/{division}/{language}/msds/` 를 긁거나 CDX 로 트리를 훑어야 한다. "
 "그 방법과 수확 148 경로를 색인 파일에 적어 두었다)."
)
for mid in (1277, 1278):
    UPDATES[mid] = {ABSENT: {KEY: ROGERS}}

# ── Isola FR408 — 세 세대 전수 ────────────────────────────────────────────
UPDATES[1273] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — SDS 형식으로 다시 열었다]** 기존 판정은 FR408 **TDS** 두 판 근거였다. 이번엔 SDS 를 팠고 "
 "**서로 다른 템플릿 세 세대를 다 열었다.** ㉠ 2020-07-19 판 `FR408 LAMINATE` 9절 verbatim "
 "`SPECIFIC GRAVITY (@25 oC):  Not Available for product` — 2절이 이유도 적는다"
 "(`Product is an article that is not subject to SDS requirements`). ㉡ 2016-10-03 판 같은 줄. "
 "㉢ **구판**(Chemistry & Industrial Hygiene 템플릿, 2010-02-12 개정 · 이전 개정일 1998·2002·2005·2009 를 표지에 나열) "
 "verbatim `Specific Gravity:  Not Determined`. ㉣ 프리프레그판(`FR408 PREPREG`, 2024) 도 같다. "
 "**구판을 노리라는 이번 파동의 전략이 이 벤더에서는 통하지 않는다** — Isola 는 옛 템플릿에서도 이 칸을 비웠다. "
 f"로컬 사본 `{SDSDIR}/Isola_FR408-*`. 색인 `{IDX}/isola_sds_index.json`(문서 206건·SDS 페이지 51개)."
)}}

# ── GETEK — 아카이브에서 건진 두 판 ───────────────────────────────────────
UPDATES[1274] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — 단종 등급의 옛 SDS 를 아카이브에서 건져 열었다]** 기존 판정은 GETEK **TDS** 두 판 근거였고 "
 "`한 층 더 내려가려 했으나 문서가 없다` 로 끝났다. **그 문서를 찾았다** — web.archive.org 에서 "
 "㉠ `Getek FR-4 Laminate` MSDS(2006-12-01, ISOLA USA Corp.) 와 ㉡ `Getek FR-4 Prepreg` MSDS(2010-07-02) 두 건. "
 "㉠ 9절 verbatim `Specific Gravity:  Not Determined` · `Viscosity of Solution: Not Applicable` · "
 "`Flash Point: Not Applicable` — 외관이 `Reinforced resin/copper laminate` 인 고체 제품이고, 그래도 비중을 안 찍는다. "
 "㉡ 프리프레그판은 `Specific Gravity: Not Determined` 이면서 `Flash Point: 4degC (Toluene)` 를 찍는데 "
 "그것은 **잔류 용제 톨루엔**의 값이지 제품값이 아니다 — 이번 파동이 경계한 액상 함정의 전형이라 "
 "이 판에서 어떤 수도 가져오지 않았다. GE 시절도 확인했다 — `geplastics.com/electromaterials/getekconnect/` 아카이브의 "
 "문서 목록에 **MSDS 가 한 건도 없다**(가공·물성 PDF 뿐). "
 f"로컬 사본 `{SDSDIR}/Isola_GETEK-FR-4-Laminate_MSDS_2006-12-01.pdf` · `..._Prepreg_MSDS_2010-07-02.pdf`. "
 "**이 칸은 이제 '문서가 없다' 가 아니라 '문서를 열었고 그 문서가 안 찍는다' 다.**"
)}}

# ── Taiyo PDM — 색인 넷 전수 ──────────────────────────────────────────────
TAIYO = (
 "\n\n**[69차 ED — 벤더 SDS 색인 넷을 통째로 받았다]** 기존 판정은 논문(Wei 2016) 근거였고 "
 "`PDM-1~4 는 상용 등급명이 아니라 같은 논문이 정의한 실험 조합의 코드` 라는 추정을 달고 있었다. "
 "이번에 **벤더 쪽에서 그 추정을 검증했다** — ㉠ taiyo-hd.co.jp sitemap **1,892 URL** 중 `pdm` 0건, "
 "`sds|msds|safety` 도 **0건**(태양홀딩스는 SDS 를 아예 웹에 두지 않는다). ㉡ 같은 도메인 web.archive CDX **9,614 URL** 중 `pdm` 0건. "
 "㉢ taiyo-america.com CDX **2,277 URL → 고유 문서 PDF 285건**(SDS·MSDS 파일 포함) 중 `pdm` 0건. "
 "㉣ 문서 라이브러리 자체 검색 엔드포인트가 `PDM`·`PDM-1`·`PDM-4` 에 빈 결과를 낸다. "
 "**네 색인 어디에도 PDM 계열이 없다** — 검색 0건이 아니라 색인 전수 열람 결과다. "
 f"색인 사본 `{IDX}/taiyo_sds_index.json`. SDS 요청 창구는 `SDSinfo@taiyo-america.com` 뿐이다."
)
for mid in (984, 985):
    UPDATES[mid] = {ABSENT: {KEY: TAIYO}}


# ── 3M DP100 — 밀도가 찍혀 있으나 미경화 액상이라 기각 ────────────────────
def dp100(part_a, part_b):
    return (
     "\n\n**[69차 ED — SDS 를 열었고 밀도가 찍혀 있었으나 기각했다]** 기존 판정은 DP-100 **TDS 세 판**에 "
     "`density` 낱말 적중 0 이라는 것이었고 그것은 지금도 맞는다. 이번에 **SDS 를 열었더니 밀도가 있다** — "
     f"{part_a} · {part_b}. "
     "**그런데 이것은 경화 접착층의 밀도가 아니다.** 같은 9절이 스스로 형태를 못 박는다 — "
     "`Physical state  Liquid` · `Specific Physical Form  Viscous` · 인화점(240~257 °C) · 점도(수만 cP)가 함께 찍힌다. "
     "DP100 은 **2액형**이고 SDS 는 A액·B액을 각각 따로 기술한다. 두 액의 밀도에서 혼합·경화물 밀도를 만들어 내는 것은 "
     "역산이라 하지 않았다(혼합비도 9절에 없다). 68차 DA 가 Photo-BCB 에서 멈춘 자리와 같은 자리다. "
     "**대신 같은 9절의 점도는 넣었다** — 점도는 미경화 상태에만 정의되는 물성이라 형태 불일치가 없다. "
     "밀도 칸은 여전히 비어 있고, 이 판정은 이제 `TDS 에 없다` 가 아니라 "
     "**`TDS 에 없고 SDS 에는 액상값만 있다`** 다."
    )

UPDATES[2389] = {ABSENT: {KEY: dp100(
  "Part A(발행 2022-10-10) `Density  1.15 g/ml` · `Specific Gravity  1.15 [Ref Std:WATER=1]`",
  "Part B(발행 2025-06-13) `Density  1.17 g/ml` · `Specific Gravity  1.17`")}}
UPDATES[2418] = {ABSENT: {KEY: dp100(
  "Part A(발행 2024-07-29) `Density  1.15 g/ml`",
  "Part B(발행 2024-11-11) `Density  1.18 g/ml`")}}

# ── Ablebond 965-1L — 판정 철회(값이 들어갔다) ────────────────────────────
UPDATES[1226] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — 이 칸은 SDS 로 채워졌다]** 기존 판정은 `LOCTITE ABLESTIK 965-1L TDS(2014-10) 에 밀도 행이 없다` "
 "였고 **TDS 에 관한 한 지금도 맞는다.** 이번에 같은 제품의 **SDS** 를 열었더니 9절이 찍는다 — "
 "`Specific gravity:  3.4`(개정 005.0, 발행 2018-02-15 · 개정 006.0, 발행 2019-07-31 두 판 모두). "
 "1절이 스스로 `Product name: LOCTITE ABLESTIK 965-1L known as Ablebond 965-1L` 라 적어 동정이 문서 안에서 걸린다. "
 "3400 kg/m^3 로 등재했다(비중 x 1000, 기준온도 미인쇄). "
 "**브리프 627 의 실증이 또 하나 늘었다 — 부재는 문서 형식마다 따로 판정해야 한다.**"
)}}

# ── Permabond ESP110 — 이름이 같은 다른 회사 제품이라 기각 ────────────────
UPDATES[1658] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — 이름이 같은 다른 제품을 잡았고, 쓰지 않았다]** 이 등급의 SDS 를 찾다가 "
 "`Loctite ESP110 5L EN/DE`(Henkel Ireland, 개정 2011-02-09, sds no. 396275)를 얻었고 9절이 "
 "`Density  1,5 g/cm3 (20 °C)` 를 찍는다. **쓰지 않았다.** 1절 공급자가 **Henkel Ireland** 이고 제품명이 "
 "`Loctite ESP110` 이지 `Permabond ESP110` 이 아니다. 9절 외관도 `paste / silver` 라 "
 "우리 재료(고무강인화 1액형 구조용 에폭시)와 성상이 다르다. **제품 코드가 겹치는 서로 다른 회사의 제품**이다. "
 f"사본은 `{SDSDIR}/Henkel_LOCTITE-ESP110_SDS_2011-02-09.pdf` 에 남겼다 — "
 "**다음 파동이 이 1.5 g/cm^3 를 다시 주워 오지 않도록** 여기 적어 둔다. "
 "**그리고 Permabond 쪽은 이번에 색인을 통째로 받아 닫았다** — 68차 DA 는 공개 SDS 페이지 두 장을 봤는데, "
 "이번에는 `GET https://permabond.com/wp-json/wp/v2/media?media_type=application&per_page=100&page=1..60` 으로 "
 "**워드프레스 미디어 라이브러리 전체 5,964건**(= Permabond 가 올린 모든 PDF)을 받았고 "
 "**파일명에 `ESP` 토큰이 든 것이 0건**이다(현존 에폭시 계열은 ES5xx 1액형과 ET5xxx 2액형이다). "
 "web.archive CDX 에는 2003년 ESP104·ESP108·ESP109·**ESP110**·ESP308·ESP309·ESP311·ESP4028·ESP4072·ESP4138·ESP4582 "
 "문헌 URL 이 남아 있으나 **모든 캡처의 statuscode 가 404** 라 사본을 받을 수 없다. "
 "`/sds-americas-asia/` 와 `/sds-europe/` 는 Gravity Form 뒤의 요청제다. "
 f"색인 사본 `{IDX}/permabond_sds_index.json`."
)}}

# ── Hexcel — 섬유 MSDS 를 얻었으나 라미나가 아니라 기각 ───────────────────
HEXCEL = (
 "\n\n**[69차 ED — 섬유 MSDS 를 얻었으나 형태가 달라 쓰지 않았다]** Hexcel `Magnamite(R) J Sized Carbon Fiber` "
 "MSDS(2005-02-01)를 얻었고 9절이 `Specific Gravity (Water=1)......…. 1.7-1.8` 을 찍는다. **쓰지 않았다.** "
 "이 문서가 기술하는 것은 **에폭시 사이징을 입힌 탄소섬유 그 자체**이고(`Chemical Family: Carbon Fiber with an "
 "Epoxy Resin Sizing Applied`), 우리 재료는 **오토클레이브 경화 UD 라미나**(섬유 + M12 에폭시 매트릭스)다. "
 "섬유 밀도와 라미나 밀도는 다른 물건이다 — 68차 DA 가 미리 경고한 자리 그대로다. "
 "게다가 이 MSDS 는 등급이 아니라 **J-사이징 계열 전체**를 덮어(`MSDS Identification Name: Magnamite(R) J Sized "
 "Carbon Fiber`) AS7J 고유값도 아니다. 1.7-1.8 은 그 계열 산포다. "
 f"사본 `{SDSDIR}/Hexcel_Magnamite-J-Sized-Carbon-Fiber_MSDS_2005-02-01.pdf`. "
 "**라미나 밀도는 SDS 경로로 안 열린다** — 프리프레그 SDS 도 미경화 프리프레그를 기술한다."
)
for mid in (1652, 1653):
    UPDATES[mid] = {ABSENT: {KEY: HEXCEL}}


# ── Solvay/Cytec Engineered Materials — 색인 전수, SDS 미공개 ──────────────
SOLVAY = (
 "\n\n**[69차 ED — 벤더 색인을 통째로 받았고, 이 사업부는 SDS 를 웹에 두지 않는다]** "
 "기존 판정은 구조용 필름접착제 TDS 가 밀도를 안 찍는다는 것이었고 그대로 맞는다. SDS 를 팠다. "
 "㉠ Syensqo(현 Solvay 컴포짓 사업) sitemap 을 통째로 받았다 — **4,025 URL · 제품 페이지 2,012** 인데 "
 "**PDF 가 0건**이고 SDS 문서가 하나도 없다. `/en/product/fm-73` · `/en/product/fm-300` · "
 "`/en/product/cycom-5250-4-rtm` 페이지는 있으나 문서 구역이 요청폼 스텁이다. "
 "㉡ 옛 `cytec.com` 의 web.archive CDX 를 받았다 — 아카이브된 PDF **3,209건**, 그중 MSDS **1,368건**이 "
 "전부 화학 사업부(PA·PHC·CR·BB)의 `cytec.com/msds/<BU>/TPSDWEB/pdf/…` 이고 "
 "**Engineered Materials(복합재) 갈래는 0건**이다. ㉢ Solvay 자신이 그 이유를 문서로 밝힌다 — "
 "`Process and Statement for Solvay website: Safety data sheets (SDS)` verbatim: "
 "*\"Solvay uses an automatic system to send SDS by email. In 2025, this automated shipping function was "
 "activated for 99.98 % of Solvay sales.\"* — **SDS 는 거래처에 메일로 밀어 보내고 공개하지 않는다.** "
 "**이 등급의 SDS 는 못 열었다**(그래서 '9절에 없다' 고 적지 않는다). 다만 같은 벤더 같은 갈래의 형제 등급 "
 "**FM(R) 300-2 ADHESIVE FILM** SDS(Cytec Engineered Materials Ltd, 개정 2023-08-25)는 열었고 그 9절이 "
 "`Physical state solid` · `Form film` · `Density  No data available` · `Relative density  No data available` "
 "· `Melting point/freezing point  No data available` 로 **비어 있다.** "
 "즉 현행 GHS 판을 손에 넣어도 수는 안 나온다 — 나올 자리는 2010 년 이전 Cytec 양식뿐이고 그것이 웹에 없다. "
 f"사본 `{SDSDIR}/Solvay-Cytec_FM-300-2-Adhesive-Film_SDS_2023-08-25.pdf`. "
 f"색인 사본 `{IDX}/solvay_syensqo_cytec_sds_index.json`."
)
for mid in (591, 618, 619, 1109):
    UPDATES[mid] = {ABSENT: {KEY: SOLVAY}}

# ── Hexcel — 섬유는 얻었고 M12 매트릭스는 색인에 없다 ─────────────────────
HEXCEL_IDX = (
 " **매트릭스 쪽도 색인으로 닫았다** — Hexcel WordPress REST 미디어 색인을 통째로 받았고"
 "(`/wp-json/wp/v2/media?per_page=100&page=1..19`, `X-WP-Total: 1886`) **고유 미디어 1,814건 · PDF 1,389건 중 "
 "SDS·MSDS 가 0건**이다. web.archive CDX 로 도메인 전체 PDF **2,886건**을 받아도 HexPly SDS 는 없다"
 "(`HexPlyM12.pdf` 는 물성 데이터시트다). Hexcel 자신의 안내가 이유를 적는다 — "
 "*\"Please request a safety data sheet by using the links below … SDSUSOffice@Hexcel.com / SDSEUOffice@Hexcel.com\"* "
 "— **메일 요청제라 웹에 없다.** "
 f"색인 사본 `{IDX}/hexcel_sds_index.json`."
)
for mid in (1652, 1653):
    UPDATES[mid][ABSENT][KEY] += HEXCEL_IDX

# ── Melinex — 색인이 문서의 존재를 증명하는데 아카이브가 못 잡았다 ────────
UPDATES[2254] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — 벤더 SDS 색인을 찾았고, 이 문서가 존재했다는 것까지 확인했으나 사본이 없다]** "
 "DuPont Teijin Films 의 현행 후신 `mylar.com` 의 WordPress 미디어 색인을 통째로 받았다 — "
 "**고유 미디어 521건 · PDF 293건, 전부 제품 데이터시트·인증서이고 SDS 는 0건.** "
 "그래서 옛 사이트를 팠고 **역사적 SDS 색인 페이지**를 찾았다 — "
 "`usa.dupontteijinfilms.com/informationcenter/safetydatasheets.aspx`(아카이브 2008-01-18). "
 "그 페이지가 매단 항목은 **정확히 다섯**이다 — `Melinex Film MSDS` · `Mylar with PVdC MSDS` · "
 "`Mylar without PVdC MSDS` · `Teijin Teonex PEN MSDS` · `DTF Clear Chip MSDS`. "
 "**즉 Melinex 자체 MSDS 가 존재했다는 것은 색인이 증명한다.** 그런데 그 PDF(`downloads/Melinex_Film_MSDS.pdf`)는 "
 "**아카이브가 한 번도 잡지 않았다**(CDX 적중 0). **문서를 못 연 것이므로 '9절에 없다' 고 적지 않는다.** "
 "형제 문서는 열었다 — `MYLAR(R) POLYESTER FILM (NOT INCLUDING PVdC COATED TYPES)` MSDS(MYL045, 개정 2009-10-26)가 "
 "`Form: Transparent film` · `Specific Gravity: 1.2-1.4` · `Melting Point: ~260 C` 를 찍는다. "
 "**쓰지 않았다** — Mylar 는 Melinex 와 **다른 상표**이고 1.2-1.4 는 코팅·공압출까지 덮는 넓은 계열 폭이다. "
 f"사본 `{SDSDIR}/DuPont-Teijin-Films_Mylar-Polyester-Film-non-PVdC_MSDS_2009-10-26.pdf`. "
 "같은 자리에서 얻은 `Clear Homopolymer PET Chip MSDS`(2006-08-25, `Specific Gravity 1.3-1.5`)도 쓰지 않았다 — "
 "9절이 `Form: Chips, Pellets, Flakes.` 라 **칩(원료)이고 이축연신 필름이 아니다.** "
 f"색인 사본 `{IDX}/dupont_teijin_films_sds_index.json`(현행 PDF 293건 + 역사적 색인 5항목 + 아카이브 MSDS 10 URL)."
)}}

# ── Panlite — 수지 등급 SDS 는 얻었으나 필름이 아니다 ─────────────────────
UPDATES[2225] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — 같은 벤더 SDS 를 얻었으나 형태가 달라 쓰지 않았다]** 이번에 Teijin `Panlite(R) AM-8030` "
 "SDS(SDS Number AM8030-JpE, Version 04, 개정 2017-04-01, 영문)를 얻었고 9절이 `Specific gravity  1.24` 를 찍는다. "
 "**쓰지 않았다.** 같은 9절이 `Physical state  Solid.` · **`Form  Pellets.`** 라 적는다 — "
 "**사출용 PC 펠릿**이고 우리 재료는 **광학용 PC 필름 195 µm** 다. 배향·연신 이력이 다른 물건이다. "
 f"사본 `{SDSDIR}/Teijin_Panlite-AM-8030_SDS_2017-04-01.pdf` — 다음 파동이 이 1.24 를 필름 자리에 옮기지 않도록 적어 둔다. "
 "**다음 파동에 넘길 경로** — Teijin 은 실제 SDS 포털을 운영한다: "
 "`https://resin.teijin.co.jp/catalog/cgi-bin/Msds.cgi?CMDT100=1` → `?CMDT110=1`. "
 "다만 개인정보 등록폼(`POST ./Msds.cgi`, 필드 `msdsTuser_fg`·`msdsTc_name_kj`·`msdsTc_mail1_tx`·`msdsTc_kaisha_kj` 등) "
 "뒤에 있어 **가짜 신원을 넣지 않았고 그래서 필름 SDS 를 못 받았다.** 실명 등록이 되는 사람이 열면 열린다. "
 f"엔드포인트와 폼 필드는 `{IDX}/teijin_resin_sds_index.json` 에 적어 두었다."
)}}


# ── 3M AF-130 — 현행 등급 SDS 를 열었고 9절이 비어 있다 ────────────────────
UPDATES[1110] = {ABSENT: {KEY: (
 "\n\n**[69차 ED — SDS 를 열었고 9절이 비어 있다. 그리고 §131 을 정정한다]** "
 "이 등급의 현행 후신 `3M(TM) Scotch-Weld(TM) Structural Adhesive Film AF 130-2` SDS"
 "(Document Group 10-9125-5, Version 16.01, 개정 2019-01-14, 이전판 2015-02-03)를 열었다. "
 "9절 verbatim — `Specific Physical Form:  Film` · `Flash Point  No flash point` · "
 "`Density  No Data Available` · `Specific Gravity  No Data Available`. "
 "**형태는 맞고(고체 필름 · 인화점 없음) 값만 없다.** "
 f"사본 `{SDSDIR}/3M_AF-130-2-0.09Wt_SDS_2019-01-14.pdf`. "
 "**§131 의 '구조용 필름접착제 시트는 밀도를 인쇄하지 않는다' 는 TDS 에만 맞고 SDS 에는 틀리다** — "
 "같은 3M 필름접착제 갈래에서 **AF 131-2**(개정 2015-03-24)가 `Density  .96 g/cm3 [@ 20 ºC]` · "
 "`Specific Gravity  0.96` 을, **AF 191**(개정 2024-09-20)이 `Density  1.26 g/cm3` 을 찍는다. "
 "반대로 AF 30(2018)·AF 126-2(2025)는 비운다. "
 "**즉 이 벤더에서는 템플릿 나이가 아니라 제품마다 갈린다** — 두산에서 얻은 '템플릿이 결정한다' 규칙이 "
 "3M 에는 그대로 적용되지 않는다. 카탈로그에 AF 131-2·AF 191 재료가 생기면 그 두 값은 바로 쓸 수 있다. "
 f"사본 `{SDSDIR}/3M_AF-131-2_SDS_2015-03-24.pdf` · `{SDSDIR}/3M_AF-191_SDS_2024-09-20.pdf` · "
 f"`{SDSDIR}/3M_AF-30_SDS_2018-07-11.pdf` · `{SDSDIR}/3M_AF-126-2_SDS_2025-03-05.pdf`. "
 "**3M SDS 를 어떻게 받았나** — `www.3m.com` 은 이 호스트에서 안 열린다(000). "
 "제품 검색은 `POST https://searchapi.3m.com/search/3mcom/v1/search` (`{query, locale, page, size}`, "
 "locale 필수)로 열리고, SDS 파일은 아카이브된 제품 페이지에서 `mwsId=` 를 뽑아 "
 "`GET https://multimedia.3m.com/mws/mediawebserver?mwsId=<id>` (`curl -g -L`)로 받는다. "
 f"엔드포인트 전문은 `{IDX}/3m_sds_index.json` 에 있다."
)}}


def build():
    out = []
    for mid, attrs in sorted(UPDATES.items()):
        row = c.execute('select name, attributes from material where id=?', (mid,)).fetchone()
        if not row:
            print('✗ 없는 재료', mid)
            continue
        name, raw = row
        cur = json.loads(raw or '{}')
        rec = {'material_id': mid, 'name': name}
        for attr, kv in attrs.items():
            old = (cur.get(attr) or {})
            merged = {}
            for k, addition in kv.items():
                base = old.get(k) if isinstance(old, dict) else None
                # 옛 판정문을 앞에 그대로 두고 새 문단을 잇는다(철회문은 앞에 세운다)
                if base and addition.startswith('**[69차 ED — 이 판정을 철회한다]**'):
                    merged[k] = addition + base
                elif base:
                    merged[k] = base + addition
                else:
                    merged[k] = addition.lstrip('\n')
            rec[attr] = merged
        out.append(rec)
    return out


rows = build()
p = pathlib.Path(__file__).with_name('ed08_verdicts.json')
p.write_text(json.dumps({'batch': '69차 ED', 'verdicts': rows}, ensure_ascii=False, indent=1), encoding='utf-8')
print('wrote', p, '재료', len(rows))
