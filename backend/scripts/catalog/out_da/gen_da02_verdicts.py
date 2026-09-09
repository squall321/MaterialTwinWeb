# 68차 DA — 기존 부재판정에 SDS 확인 결과를 덧붙여 da02_verdicts.json 을 만든다
import sqlite3, os, json

DB = 'file:'+os.environ['MATERIALTWIN_DATA_DIR']+'/materialtwin.db?mode=ro'
c = sqlite3.connect(DB, uri=True)
KEY = 'physical.density'
ATTR = 'core_absent_from_vendor_sheet'

DOOSAN_INDEX = (
 "\n\n**[68차 DA — SDS 형식으로 다시 열었다]** 두산 공개 MSDS 목록을 **전수로** 받았다 — "
 "`POST https://www.doosanelectronics.com/rest/product/msds/list` (제품 페이지 "
 "`/en/product/CCL_tech_support04` 가 쓰는 그 엔드포인트)에 language 를 en·ko·kr·zh·jp·빈값 "
 "여섯으로 바꿔 가며 던졌고 **여섯 응답이 모두 같은 120건**이었다(halogen free·PTFE·DFP·halogen·"
 "NWB·FCCL·MCCL·RCC·PKG 아홉 계열). 그 120건에 이 등급 이름이 없다. 두산은 이 등급의 SDS 를 "
 "공개하지 않는다 — 목록을 열어 확인한 부재이지 검색 0건이 아니다."
)

def doosan_opened(fname, dateline, verbatim):
    return (
     f"\n\n**[68차 DA — SDS 형식으로 다시 열었다]** 기존 판정은 `TDS 에 없다` 였고 그것은 여전히 맞는다. "
     f"이번에는 **같은 제품의 SDS 를 실제로 내려받아 9절을 폈다** — {dateline}. "
     f"9절 verbatim: {verbatim} "
     f"두산의 현행 GHS 판 CCL SDS 는 9절을 **제품 단위가 아니라 CAS 성분 단위 열로** 짜고 "
     f"비중 행을 성분마다 `자료없음 / No data available` 로 비운다. 즉 SDS 도 이 제품의 밀도를 안 찍는다. "
     f"로컬 사본 `/data/paper_patent_corpus/standards_appnotes/sds/{fname}`. "
     f"※ 두산의 **구판 템플릿** SDS 는 이 칸을 채운다 — 같은 목록의 DST-9000(2012.05.04)·DSF-400G(2018.01.02)·"
     f"DSflex-600 Single Side(2023.02.01)가 `SPECIFIC GRAVITY : (Water=1.0) ...` 에 실수를 찍는다. "
     f"이 제품이 신판 템플릿으로 갈아탄 것이 부재의 원인이다."
    )

UPDATES = {
 2483: doosan_opened(
   "Doosan_DSR-1000-BS_MSDS_2023-12-20.pdf",
   "`GHS-MSDS DSR-1000 BS_231220_Ver.2.pdf`(개정 2023-12-20, 영문판). 표지가 `Product name  DSR-1000`, "
   "1절이 `A. Name of Product  DSR-1000 BS` 로 이 등급을 가리킨다",
   "`N. Specific gravity   No data available   No data available   No data available   No data available   No data available` "
   "— CAS 65997-17-3 · 28906-96-9 · 29160-69-8 · 7631-86-9 · 1818863-75-0 다섯 열이 전부 비어 있다."),

 2509: doosan_opened(
   "Doosan_DS-7409S-N-BS_SDS_2024-04-04_en.pdf",
   "**두 판을 다 열었다** — 영문 `General_DS-7409S (N) BS_SDS_240404_Ver.7.pdf`(개정 2024-04-04)와 "
   "국문 `DS-7409S(N)BS_MSDS_210520.pdf`(개정 2021-05-20). 두 판 다 1절 제품명이 `DS-7409S (N) BS` 다",
   "영문판 `N. Specific gravity  No data available  No data available  No data available` · "
   "국문판 `하. 비중  자료없음  자료없음  자료없음` — CAS 65997-17-3 · 26265-08-7 · Cured Epoxy Resin 세 열이 다 비어 있다. "
   "국문 사본은 `/data/paper_patent_corpus/standards_appnotes/sds/Doosan_DS-7409S-N-BS_MSDS_2021-05-20_ko.pdf` 다."),

 2461: DOOSAN_INDEX, 2462: DOOSAN_INDEX, 2463: DOOSAN_INDEX, 2480: DOOSAN_INDEX,
}

ABF = (
 "\n\n**[68차 DA — SDS 형식으로도 확인했다]** 기존 판정은 `원문(Fujishima 2017)에도 없고 붙일 벤더 TDS 도 없다` "
 "였다. 이번 파동은 **SDS** 를 따로 팠다 — 아지노모토 파인테크노의 층간절연재(ABF) 제품 페이지 "
 "`https://www.aft-website.com/products/insulating_film-abf/` 를 열어 전문을 훑었고, 페이지가 등급 "
 "GX-92·GX-T31·GZ-41·GL-102 를 나열하지만 **SDS·安全データシート·MSDS 링크가 한 건도 없고 다운로드 구역 자체가 없다.** "
 "유일한 접점이 문의폼(`/contact/product-contact/`)이다. 즉 이 벤더는 TDS 도 SDS 도 공개하지 않는다. "
 "**SDS 경로도 이 갈래에서는 닫혀 있다.**"
)

for mid in (978, 979, 980, 981, 982, 983):
    UPDATES[mid] = ABF

UPDATES[1273] = (
 "\n\n**[68차 DA — SDS 형식으로 다시 열었다]** 기존 판정은 TDS·제품페이지·전제품 가이드 세 층을 다 판 것이었다. "
 "이번에는 **SDS 층**을 팠다. ① Isola 가 공개하는 것은 형제 등급 SDS 뿐이다 — `FR408HR LAMINATE` "
 "iSDS(REVISION DATE: January 11, 2024)와 `FR408HR PREPREG` SDS 다. ② 그 FR408HR 라미네이트 SDS 를 "
 "실제로 열었고 9절이 이렇게 적는다 — verbatim `SPECIFIC GRAVITY (@25 oC):  Not Available for product`. "
 "9절 전체가 `APPEARANCE - COLOR: Copper colored` · `PHYSICAL STATE: Solid` · `SOLUBILITY IN WATER: Insoluble` "
 "셋만 값이고 나머지 열여섯 행이 전부 `Not Available for product` 다. 2절이 이유도 적어 둔다 — "
 "`Product is an Article that is not subject to SDS requirements`. ③ **FR408(HR 아닌 판) 자체의 SDS 는 없다** — "
 "제품 페이지 `isola-group.com/products/all-printed-circuit-materials/fr408/` 의 다운로드는 "
 "`FR408-Laminate-RoHS-Declaration.pdf` 하나뿐이다. 즉 형제 SDS 도 비어 있고 이 등급 SDS 는 존재하지 않는다. "
 "로컬 사본 `/data/paper_patent_corpus/standards_appnotes/sds/Isola_FR408HR-Laminate_SDS_2024-01-11.pdf`."
)

UPDATES[1360] = (
 "\n\n**[68차 DA — SDS 를 열었고, 값을 보았고, 기각했다]** 기존 판정은 Processing Procedures 세 판에 밀도가 없다는 것이었다. "
 "이번에 **SDS 를 팠고 밀도가 있었다** — The Dow Chemical Company, `CYCLOTENE* 4022-35 Advanced Electronics Resin` "
 "MSDS(Issue Date 04/12/2006). 9절 verbatim: `Physical State  Liquid` · `Color  Yellow` · `Odor  Aromatic` · "
 "`Specific Gravity (H2O = 1)  0.9521 Literature` · `Liquid Density  0.9521 g/cm3 ASTM B311` · "
 "`Kinematic Viscosity  192 mm2/s @ 25 °C` · `Flash Point - Closed Cup  44 °C` · `Boiling Point (760 mmHg)  162 °C`. "
 "**이 0.9521 을 이 재료에 넣지 않았다.** 이 재료는 스핀코팅 후 250 °C 로 경화한 **repassivation 유전막**이고, "
 "SDS 가 기술하는 것은 메시틸렌에 녹인 **B-stage 액상 바니시**다(9절이 스스로 `Liquid`·인화점 44 °C·점도 192 mm2/s "
 "로 못 박는다 — 용매가 든 용액이다). 용매를 날려 굳힌 막의 밀도는 이 값이 아니다. "
 "**이것이 이 배치가 경계하라고 한 함정이고, 실제로 걸렸다.** 로컬 사본 "
 "`/data/paper_patent_corpus/standards_appnotes/sds/Dow_CYCLOTENE-4022-35_MSDS_2006-04-12.pdf`. "
 "→ 경화막 밀도는 여전히 부재다."
)

UPDATES[1658] = (
 "\n\n**[68차 DA — SDS 형식으로도 확인했다]** Permabond 의 공개 SDS 색인 **두 곳을 다 열었다** — "
 "`permabond.com/safety-data-sheets/`(Anaerobics·Cyanoacrylates·Epoxies·Polyurethane·MS Polymer·"
 "Structural Acrylics·UVs 로 나뉜 목록)와 `permabond.com/sds-americas-asia/`. **두 색인 어디에도 ESP110/ESP 계열 항목이 없다.** "
 "두 번째 쪽은 아예 `use the contact form to request a Safety Data Sheet` 라고 적어 요청제임을 밝힌다. "
 "유통사(Ellsworth webaps·Chemical Concepts)가 호스팅하는 Permabond SDS 도 200·910·HL126·HM118·POP·"
 "ET5147A·ET5428A 등이고 ESP110 은 없다. 이 등급은 Kawashita 2004 당시의 구판 등급이라 현행 목록에서 내려간 것으로 보인다. "
 "**SDS 경로도 이 재료에서는 닫혀 있다** — 문서를 못 연 것이 아니라 색인 두 개를 열어 부재를 확인했다."
)

FILLED = {
 2545: ("\n\n**[68차 DA — SDS 가 이 칸을 닫았다]** 이 판정은 이제 유효하지 않다. "
        "ZEON 의 **TDS·브로슈어 다섯 문서에 없다**는 진술은 그대로 맞는다. 그러나 문서 형식을 바꾸자 값이 나왔다 — "
        "`Zeonex 330R Safety Data Sheet`(Zeon Chemicals L.P., Issue Date 01-23-2015, MSDS Number Z01391) "
        "9절 verbatim `Relative Density (water = 1):  0.95` · `Appearance: Colorless Solid`. "
        "이 SDS 는 8쪽 전 페이지 꼬리말이 `Zeonex 330R` 하나이고 3절 조성이 `Polycycloolefin Resin ~100 wt%` 라 "
        "이 등급 전용 문서다. **경고했던 `360R 값 옮기기` 가 아니다** — 330R 자기 문서다. "
        "밀도 950 kg/m^3 을 t1 으로 등재했다(68차 DA)."),
 2484: ("\n\n**[68차 DA — SDS 가 이 칸을 닫았다]** `전제품 TDS v9 의 Density 칸이 비어 있다`는 진술은 그대로 맞는다. "
        "그러나 **같은 벤더의 SDS 는 이 칸을 찍는다** — `Doosan DST-9000 Safety Data Sheet`(SDS Number MSDS-J-064, "
        "Current Issue Date 2012.05.04) 9절 verbatim `SPECIFIC GRAVITY : (Water=1.0) 2.5 to 3.3`. "
        "인쇄 구간이라 하한 2500 · 상한 3300 kg/m^3 두 행으로 등재했다(68차 DA). "
        "부재는 문서 형식마다 따로 판정해야 한다는 브리프 627 의 실증이다."),
 2485: ("\n\n**[68차 DA — SDS 가 이 칸을 닫았다]** `전제품 TDS v9 의 Density 칸이 비어 있다`는 진술은 그대로 맞는다. "
        "그러나 **같은 벤더의 MSDS 는 이 칸을 찍는다** — `Doosan DST-9000HT Material Safety Data Sheet`"
        "(MSDS Number MSDS-DSE-J-067, Current Issue Date 2015.12.18) 9절 verbatim "
        "`SPECIFIC GRAVITY : (Water=1.0) 2.5 to 3.3`. 인쇄 구간이라 하한 2500 · 상한 3300 kg/m^3 두 행으로 등재했다(68차 DA). "
        "※ 형제 DST-9000 의 SDS 가 같은 숫자를 찍는다 — 등급 변별력은 없다."),
 2486: ("\n\n**[68차 DA — SDS 목록을 열었으나 이 등급은 없다]** 두산 공개 MSDS 목록 전수 120건(language 6종 응답 동일)에 "
        "`DST-9000S` 항목이 없다. 형제 DST-9000(2012.05.04)·DST-9000HT(2015.12.18)의 SDS 는 둘 다 "
        "`SPECIFIC GRAVITY : (Water=1.0) 2.5 to 3.3` 을 찍지만 **이 등급 자기 문서가 아니라 옮기지 않았다.**"),
}
UPDATES.update(FILLED)

out = {"batch": "68차 DA", "verdicts": []}
missing = []
for mid, add in UPDATES.items():
    row = c.execute("select name,attributes from material where id=?", (mid,)).fetchone()
    if row is None:
        missing.append(mid); continue
    name, raw = row
    attrs = json.loads(raw or "{}")
    old = (attrs.get(ATTR) or {}).get(KEY)
    if not old:
        missing.append((mid, name, 'no existing verdict')); continue
    out["verdicts"].append({"material_id": mid, "name": name, ATTR: {KEY: old + add}})

json.dump(out, open('/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_da/da02_verdicts.json', 'w'),
          ensure_ascii=False, indent=1)
print("판정 갱신", len(out["verdicts"]), "종")
if missing: print("빠짐:", missing)
for v in out["verdicts"]: print("  ", v["material_id"], v["name"][:55], len(v[ATTR][KEY]), "자")
