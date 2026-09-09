# 70차 FB — 라이브 DB 의 기존 부재판정문을 읽어 이번 파동의 문단을 앞/뒤에 붙여 판정 JSON 을 만든다.
import json, os, sqlite3, pathlib

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                  "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)

IDX = "`backend/scripts/catalog/out_ed/indexes/ellsworth_edl_sds_index.json` (EDL 24,113 고유 문서·언어쌍 · 발행처 1,407)"

# (material_id, 앞에 세울 철회문 or None, 뒤에 붙일 보강문)
NEW = {
 737: ("**[70차 FB — 철회. Zymet 은 없어지지 않았고 SDS 도 있다. 밀도를 넣었다.]** "
       "옛 판정은 *'Zymet 사는 없어져 시트를 구할 길도 없다'* 로 닫혀 있었다. **두 대목이 틀렸다.** "
       "㉠ `zymet.com` 은 살아 있다(HTTP 200, `(c) 2005-2024 Zymet`, 제품군 12쪽 sitemap). 다만 등급별 TDS 를 웹에 두지 않고 문의 창구만 둔다. "
       "㉡ **Ellsworth Document Library 가 Zymet 자사 SDS 를 무인증으로 서빙한다** — `X6-82-5LV` SDS(Version 005, 2020-04-29, `item_id 54928`). "
       "그 9절이 `Specific Gravity  1.65 g/cc` 를 찍어 **1650 kg/m^3** 를 넣었다(같은 절의 `Viscosity 20,000 cps` 도 20 Pa*s 로 넣었다). "
       "**형태는 다르다** — 인쇄값은 **미경화 액상**의 것이고 Chhanda 2012 가 잰 것은 경화 자립 시편이다. 3절에 휘발성 용제가 없어(실리카 45-75 % + 에폭시 2종 + 경화제) "
       "용액이 아니라는 것을 확인하고 `physical_form: liquid, as supplied (uncured)` 로 못박아 넣었다(68차 DA 의 Ablebond 965-1L 과 같은 자리). "
       "**등급도 완전히 같지는 않다** — 문서는 `X6-82-5LV`, 논문은 `X6-82-5LV50` 이라 t3 + `grade_scope` 다. "
       "옛 판정문의 나머지(논문이 밀도를 인쇄하지 않는다)는 그대로 맞아 아래에 보존한다.",
       "\n\n**[70차 FB 덧붙임]** 이 판정의 다른 네 칸(포아송비·선팽창·열전도율·비열)에 대해서도 같은 SDS 를 확인했다 — "
       "9절에 `Melting point  Not applicable` · `Boiling point  None` 외에는 열물성이 한 줄도 없다. **SDS 9절은 원래 열전도율·비열을 담는 절이 아니다**(68차 DA·69차 ED 가 이미 확인). "
       "그 네 칸은 이 문서로 닫히지 않는다."),

 591: ("**[70차 FB — 철회. FM 300 계열 SDS 는 밀도를 찍는다. 두 행을 넣었다.]** "
       "옛 판정(46차 HD · 57차 SC · 69차 ED)은 두 진술로 되어 있었다 — ㉠ *'구조용 필름접착제 TDS 는 밀도를 인쇄하지 않는다(§131)'* ㉡ *'Solvay 는 SDS 를 웹에 두지 않는다'*. "
       "**㉠ 은 TDS 에 대해서는 지금도 맞고, ㉡ 은 틀렸다.** Ellsworth Document Library 가 Cytec 자사 SDS 를 무인증으로 서빙한다 — "
       "`FM(R) 300 Adhesive Film` SDS 0001535(2017-02-05, `item_id 40941`). 9절 verbatim `Appearance: film` · `Color: green` · "
       "**`Specific Gravity/Density:  1.3 -  1.4-`** · `Percent Volatile (% by wt.): <1` · `Flash Point: Not applicable`. "
       "구간이므로 **1300 · 1400 kg/m^3 두 행**으로 넣었다(t3 — 문서가 등급별이 아니라 계열 한 장이고, `Color: green` 이 FM 300K·300M·300U 로 범위를 좁힌다). "
       "**같은 등급의 두 숫자가 다른 물건이었다** — 같은 벤더 TDS(AEAD-00002 Rev 01, 2011-08-12) Table 1 의 `FM 300K | 0.05 psf (244 gsm) | 0.008 in (0.20 mm)` 를 나누면 "
       "1201 kg/m^3, `0.08 psf (390 gsm) | 0.013 in (0.32 mm)` 는 1181 kg/m^3 로 **SDS 인쇄값보다 10~15 % 가볍다**. 같은 표의 FM 300 두 행끼리도 1181 vs 1286 으로 9 % 어긋난다(0.08 psf/0.013 in vs 0.10 psf/0.015 in). "
       "공칭두께가 0.001 in 단위 반올림이고 면적중량 공차가 ±25 gsm 이기 때문이다 — **면적중량/두께는 필름의 겉보기 면적밀도이지 재료 밀도가 아니다.** 계산값은 넣지 않았다. "
       "**형제 문서 하나는 버렸다** — `FM(R) 300-2 Adhesive Red` SDS 0059418(2017-11-21, `item_id 40945`)은 9절이 `Appearance: liquid` · "
       "`Percent Volatile ~16(methyl ethyl ketone)` · `Intended/Recommended Use: Intermediate` 인 **바니시 중간체**이고 `Specific Gravity/Density: Not available` 라 값도 없다. "
       "옛 판정문 전문은 아래에 보존한다.",
       f"\n\n**[70차 FB 덧붙임 — 지역·템플릿이 또 하나의 축이다]** 69차 ED 는 부재의 원인을 '두산=템플릿 · Senju=연도 · 3M=제품 · Rogers/Isola=정책 · 여섯 벤더=요청제' 로 갈랐다. "
       "Solvay/Cytec 에서 **일곱째 축**이 나왔다 — **지역판**이다. 같은 갈래에서 미국 Cytec 템플릿(`SDS: 0001535`, `9. PHYSICAL AND CHEMICAL PROPERTIES` 에 "
       "`Specific Gravity/Density`)은 값을 찍는데, ED 가 이미 갖고 있던 EU/UK 판(`Solvay-Cytec_FM-300-2-Adhesive-Film_SDS_2023-08-25.pdf`, "
       "`Transition document following UK exit from the EU`)은 같은 칸이 `Density  No data available` · `Relative density  No data available` 다. "
       "**같은 벤더·같은 갈래에서 미국판은 찍고 EU/UK판은 비운다.** 다음 파동은 벤더가 아니라 **문서의 지역·템플릿**으로 표적을 골라라. 색인 사본 " + IDX + "."),

 1109: ("**[70차 FB — 철회. FM 73M SDS 가 밀도를 찍는다. 값을 넣었다.]** "
        "옛 판정(46차 HD · 69차 ED)은 *'밀도는 이 갈래의 구조적 부재이고 Solvay 는 SDS 를 웹에 두지 않는다'* 였다. **SDS 에 대해서는 틀렸다.** "
        "Ellsworth Document Library 의 `FM(R) 73 M Adhesive Film` SDS 0001202(2017-02-05, `item_id 2165` · `MSDS12601`) 9절 verbatim — "
        "`Color: yellow` · `Appearance: film` · **`Specific Gravity/Density:  1.16`** · `Percent Volatile (% by wt.): 1.2 - 1.5(methyl ethyl ketone)` · `Flash Point: Not applicable`. "
        "**1160 kg/m^3** 를 t3 + `grade_scope` 로 넣었다 — 문서는 M(폴리에스터 매트) 캐리어 변종이고 Thiedmann 1987 은 캐리어를 지정하지 않은 `FM-73` 이다. "
        "이 재료의 전단강도 4행이 이미 같은 근거로 t3 + `grade_measured`/`grade_target` 을 달고 있어 그 관례를 그대로 따랐다. "
        "**형태** — 미경화 필름의 값이다(잔류 MEK 1.2~1.5 wt%). **자릿수 검산** — 3절이 무기 충전재도 할로겐도 없는 고무변성 에폭시(`Modified poly(aromatic glycidyl ether) - "
        "Elastomer modified phenolic epoxy resin 40-70`)라 1.16 은 무충전 에폭시 대역에 정확히 들고, 같은 벤더 FM 300(브롬화 에폭시 50-75 %)의 1.3-1.4 와 서로를 검증한다. "
        "옛 판정문 전문은 아래에 보존한다.",
        f"\n\n**[70차 FB 덧붙임]** TDS 쪽 진술은 이번에도 다시 확인해 그대로 맞다 — `Solvay_FM73_FilmAdhesive_TDS.pdf` 의 `Density  7.3 lb/gal (875 g/L)` 는 "
        "여전히 **BR(R) 127 프라이머 표**의 행이고 필름 행이 아니다. 바뀐 것은 TDS 가 아니라 **SDS 라는 다른 문서 갈래가 열렸다**는 것이다. 색인 사본 " + IDX + "."),

 2389: (None,
        f"\n\n**[70차 FB — 캐나다판 SDS 와 TDS 를 더 열었고 결론은 같다]** Ellsworth 색인에서 이 갈래 문서를 전수로 뽑아(`dp100` 토큰 20건) 세 건을 더 열었다. "
        "㉠ `3M(TM) Scotch-Weld(TM) Epoxy Adhesive DP100, Clear` **캐나다판 SDS**(Document group 11-3180-4, Version 16.05, 2022-06-07, `item_id 34315`, 20쪽 영/불 합본) — "
        "9절이 `Density 1.15 g/ml` · `Relative density 1.15 [Ref Std:WATER=1]`(A액)와 `Density 1.17 g/ml` · `Relative density 1.17`(B액)로 "
        "**69차 ED 가 미국판에서 읽은 것과 같은 수**를 찍는다. 여전히 A액·B액 각각의 액상값이고 혼합·경화물 값이 아니다. "
        "㉡ `Scotch-Weld Epoxy Adhesive DP100NS Translucent` **TDS**(Last Revision June 2024, `item_id 61953`) — `Typical Uncured Physical Properties` 에 "
        "`Base Net Weight 9.6 - 10.0 lb/gal` · `Accelerator Net Weight 9.2 - 9.6 lb/gal`(= 1150~1198 · 1102~1150 kg/m^3)가 있는데 **이것도 미경화 A/B 액의 값**이다. "
        "같은 TDS 의 `Typical Cured Characteristics` 표에는 압축강도·Shore D 만 있고 **경화물 밀도 행이 없다**. "
        "**판정은 바뀌지 않는다** — 이 등급의 밀도 칸은 '문서를 못 열어서' 가 아니라 **'벤더가 경화물 밀도를 어느 문서에도 찍지 않아서'** 비어 있다. "
        "사본 `/data/paper_patent_corpus/standards_appnotes/sds/3M_DP100-Clear_SDS_2022-06-07_ca.pdf` · "
        "`/data/paper_patent_corpus/standards_appnotes/adhesive/3M_ScotchWeld_DP100NS_TDS_2024-06.pdf`. 색인 사본 " + IDX + "."),

 2418: (None,
        f"\n\n**[70차 FB — 캐나다판 SDS 와 TDS 를 더 열었고 결론은 같다]** `3M(TM) Scotch-Weld(TM) Epoxy Adhesive DP100NS Translucent` **캐나다판 SDS**"
        "(Document group 11-2403-1, Version 14.00, 2018-06-27, `item_id 42304`) 9절이 `Density 1.15 g/ml`(A액) · `Density 1.18 g/ml`(B액)로 "
        "**69차 ED 가 미국판에서 읽은 것과 같은 수**를 찍는다. 같은 등급 TDS(June 2024, `item_id 61953`)의 `Base Net Weight 9.6 - 10.0 lb/gal` · "
        "`Accelerator Net Weight 9.2 - 9.6 lb/gal` 도 미경화 A/B 액의 값이고, 같은 TDS 의 `Typical Cured Characteristics` 표에는 **경화물 밀도 행이 없다**. "
        "**판정은 바뀌지 않는다.** 사본 `/data/paper_patent_corpus/standards_appnotes/sds/3M_DP100NS-Translucent_SDS_2018-06-27_ca.pdf` · "
        "`/data/paper_patent_corpus/standards_appnotes/adhesive/3M_ScotchWeld_DP100NS_TDS_2024-06.pdf`. 색인 사본 " + IDX + "."),

 2254: (None,
        f"\n\n**[70차 FB — Mylar 문서를 한 판 더 열었고 같은 이유로 버렸다]** Ellsworth 색인의 발행처 `DuPont Teijin Films` 항목은 **단 한 건**(`Mylar Polyester Film`, `item_id 25420`)이고, "
        "받아 보니 `Mylar(R) A Polyester Film` **Article Information Sheet Version 2.8 (2016-04-26, DuPont Teijin Films Luxembourg SA)** 였다. "
        "`Physical and chemical properties` 절 verbatim — `Form: Film` · `Colour: various` · **`Density: 1.23 - 1.41 g/cm3`** · `Water Solubility: insoluble`. "
        "**쓰지 않았다** — 69차 ED 가 2009 판을 버린 이유가 그대로 유효하다. ㉠ Mylar 는 Melinex 와 다른 상표다. ㉡ `Colour: various` 가 스스로 밝히듯 "
        "이 1.23-1.41 은 투명 무충전판부터 안료·보이드 함유판까지 덮는 **계열 폭**이다(순수 이축연신 PET 는 1.39~1.40 한 점이다). "
        "하한 1.23 은 보이드가 든 등급이 아니면 나올 수 없는 수라 Erlat 2003 의 광학등급 50 µm 무코팅 필름에 붙일 수 없다. "
        "**Melinex 자체 문서는 이번에도 못 찾았다** — EDL 24,113 항목 중 `melinex` 토큰 0건. 판정은 그대로 '문서를 못 열었다' 다. "
        "사본 `/data/paper_patent_corpus/standards_appnotes/sds/DuPont-Teijin-Films_Mylar-A-Polyester-Film_AIS_2016-04-26.pdf`. 색인 사본 " + IDX + "."),

 1658: (None,
        f"\n\n**[70차 FB — 두 번째 독립 색인에서도 ESP 계열이 0건이다]** 69차 ED 는 Permabond 자사 워드프레스 미디어 5,964건에서 `ESP` 토큰 0건을 확인했다. "
        "이번에 **유통사 색인이라는 다른 경로**로 같은 결론에 닿았다 — Ellsworth Document Library 의 발행처 `Permabond Int LLC` / `Permabond Engineering Adhesives Ltd` 항목 "
        "**284건을 전수로 열거**했고(SDS·TDS·RoHS·REACH 합계), 제품명에 `ESP` 가 든 것이 **0건**이다. 현존 에폭시 계열은 ES5xx 1액형(ES550·ES558·ES562·ES569·ES570M·ES578·ES579·ES5691)과 "
        "ET5xxx 2액형뿐으로 ED 가 자사 색인에서 본 것과 정확히 같다. **제조사 색인과 유통사 색인이 독립적으로 같은 부재를 가리키므로 ESP110 은 단종 확정이다** — "
        "다음 파동은 이 등급을 웹에서 다시 찾지 마라. 색인 사본 " + IDX + "."),

 1110: (None,
        f"\n\n**[70차 FB — 유통사 색인에도 AF-130 계열이 없다]** Ellsworth Document Library 에서 발행처가 3M 인 항목 중 `AF<숫자>` 꼴 제품을 전수로 뽑았다 — "
        "`AF-111 Structural Film`(SDS·TDS) · `AF42` / `AF-42 Structural Adhesive Film` · `AF 126FR` · `AF 3024 Film` · `AF 126-2/AF 126-3`(TDS) · `AF 163-2`(RoHS) **여섯 갈래뿐이고 "
        "AF-130 계열은 0건**이다. 69차 ED 가 3M 자사 경로(`searchapi.3m.com` + `multimedia.3m.com`)로 AF 130-2 SDS(2019-01-14)를 실제로 열어 "
        "`Density  No Data Available` 를 확인한 판정이 그대로 유효하고, **유통사 색인은 그 부재를 뒤집을 다른 판을 갖고 있지 않다.** 색인 사본 " + IDX + "."),

 1273: (None,
        f"\n\n**[70차 FB — 함정: EDL 의 `Von Roll Isola` 는 우리 Isola 가 아니다]** Ellsworth Document Library 의 발행처 목록에 `Von Roll Isola USA, Inc.` 가 있어 이름만 보면 걸린다. "
        "**다른 회사다** — 항목 6건이 전부 전기절연 바니시·솔더킷(`7031 Insulating Varnish and Adhesive` · `3022 E Solder Kit` · `EB-41` · `3030` · `E-kote 3030`)이고 "
        "PCB 라미네이트가 한 건도 없다. 우리 재료의 제조사는 **Isola Group**(FR408 라미네이트)이다. 69차 ED 가 Isola Group sitemap 에서 SDS 6건을 실제로 열어 확인한 "
        "`Not Available for product` · 구판 `Not Determined` 판정이 그대로 유효하다. 색인 사본 " + IDX + "."),

 1274: (None,
        f"\n\n**[70차 FB — 함정: EDL 의 `Von Roll Isola` 는 우리 Isola 가 아니다]** 1273 과 같은 확인이다. Ellsworth 의 `Von Roll Isola USA, Inc.` 6건은 전기절연 바니시·솔더킷이고 "
        "PCB 라미네이트가 없다. GETEK 토큰도 EDL 24,113 항목에서 **0건**이다. 69차 ED 가 아카이브에서 라미네이트판·프리프레그판을 실제로 열어 확인한 "
        "`Specific Gravity: Not Determined` 판정이 그대로 유효하다. 색인 사본 " + IDX + "."),

 1277: (None,
        f"\n\n**[70차 FB — 함정: EDL 의 `Rogers Corporation` 은 라미네이트 사업부가 아니다]** Ellsworth Document Library 에 발행처 `Rogers Corporation` 항목 14건이 있는데 "
        "**전부 엘라스토머·테이프 사업부**다(`Poron Urethane Materials (Article)` · `Bisco Silicone` · `MOX-TAPE Self-Fusing Silicone Tape` · `HT-800 Series` · `Poron 4701-40 Soft` 등). "
        "`RO4350`·`RO4003` 토큰은 EDL 24,113 항목에서 **0건**이다 — 고주파 회로재 사업부의 문서는 이 유통사 색인에 없다. "
        "69차 ED 가 Rogers 자사 EHS 경로에서 7개정 x 5언어를 열어 확인한 `SPECIFIC GRAVITY: NA (Water = 1)` 판정이 그대로 유효하다. 색인 사본 " + IDX + "."),

 1278: (None,
        f"\n\n**[70차 FB — 함정: EDL 의 `Rogers Corporation` 은 라미네이트 사업부가 아니다]** 1277 과 같은 확인이다. Ellsworth 의 Rogers 항목 14건은 전부 "
        "Poron/Bisco/MOX-TAPE 계열이고 `RO4003`·`RO4350` 토큰은 0건이다. 판정은 그대로다. 색인 사본 " + IDX + "."),

 984: (None,
       f"\n\n**[70차 FB — 다섯째 색인에서도 PDM 계열이 0건이다]** 69차 ED 가 네 색인(taiyo-hd sitemap 1,892 · CDX 9,614 · taiyo-america CDX 2,277 -> PDF 285 · 라이브러리 검색 API)에서 "
       "`pdm` 0건을 확인했다. 이번에 **유통사 색인이라는 다섯째 경로**를 더했다 — Ellsworth Document Library 의 발행처 `Taiyo America, Inc.` 항목은 **9건뿐**이고 "
       "전부 솔더레지스트·잉크다(`PSR-4000 MP` · `PSR-4000 BN Series` · `PSR-4000 HFX Series` · `UVR-150 Green` · `UVR-150 Touch Up Blue` · "
       "`S-222NA (402LV), S-222NA (402), S-200ELV, S-200YNP` · `HD-3` · RoHS 총괄 1건). **감광성 드라이필름 유전체(PDM) 는 한 건도 없다.** "
       "다섯 색인이 독립적으로 같은 부재를 가리킨다 — 다음 파동은 웹에서 다시 찾지 말고 `SDSinfo@taiyo-america.com` 창구를 쓸 사람에게 넘겨라. 색인 사본 " + IDX + "."),

 985: (None,
       f"\n\n**[70차 FB — 다섯째 색인에서도 PDM 계열이 0건이다]** 984 와 같은 확인이다. Ellsworth Document Library 의 `Taiyo America, Inc.` 9건은 전부 "
       "PSR-4000·UVR-150·S-222NA·HD-3 계열 솔더레지스트·잉크이고 PDM 계열이 0건이다. 판정은 그대로다. 색인 사본 " + IDX + "."),
}

rows = []
for mid, (pre, post) in NEW.items():
    r = c.execute("select name, attributes from material where id=?", (mid,)).fetchone()
    name, attrs = r[0], json.loads(r[1] or "{}")
    old = (attrs.get("core_absent_from_vendor_sheet") or {}).get("physical.density")
    if old is None:
        raise SystemExit(f"재료 {mid} 에 physical.density 판정문이 없다 — 확인 필요")
    txt = (pre + "\n\n" + old if pre else old) + (post or "")
    rows.append({"material_id": mid, "name": name,
                 "core_absent_from_vendor_sheet": {"physical.density": txt}})

out = {"batch": "70차 FB", "verdicts": rows}
p = pathlib.Path(__file__).with_name("fb05_verdicts.json")
p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{p} — 판정 {len(rows)}종")
