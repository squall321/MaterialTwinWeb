# 69차 EB — 이 배치가 실제로 연 형식과 거기서 확인한 '열 부재'를 표적별 판정으로 남긴다
import sqlite3, os, json, collections

DB = 'file:' + os.environ['MATERIALTWIN_DATA_DIR'] + '/materialtwin.db?mode=ro'
c = sqlite3.connect(DB, uri=True)
name = {i: n for i, n in c.execute('select id,name from material')}
have = collections.defaultdict(set)
for m, k in c.execute('select distinct material_id,property_key from property_value'):
    have[m].add(k)

V = []
def add(mid, key, verdict, reason):
    if key in have[mid]:
        return  # 이미 값이 있으면 부재판정을 걸지 않는다
    V.append({"material_id": mid, "key": key, "verdict": verdict,
              "name": name[mid], "reason": reason})

EMC = """**[69차 EB — 자국어(번체·간체) 로케일을 열었고, 그 문은 존재하지 않는다]**
브리프의 가설은 「台光電子가 자국 설계자용 產品型錄을 따로 낸다」였다. 실제로 열어 그 가설이 **틀렸음을 확정했다.**
① `https://www.emctw.com/zh-TW/product_name/index` · `/zh-CN/product_name/index` · `/en-global/product_name/index` 세 로케일의 PDF 링크 목록을 각각 뽑아 diff 했다 — **43장으로 개수가 같고 파일이 완전히 동일하다.** 중국어 페이지가 영문 데이터시트를 그대로 서빙한다.
② zh-TW 제품 페이지 HTML 에 `彈性模數`·`拉伸模數`·`比熱`·`導熱係數`·`拉伸強度`·`密度`·`泊松比` **0 hit**(`下載` 3회뿐). 물성 표가 아니라 목록 표다.
③ `for_customers`·`leading_technology`·`mass_lam_service`·`about_production`·`presentation_materials` 전수 — **產品型錄·技術資料 다운로드 구역이 없다.** presentation_materials 는 투자자 설명회 자료뿐.
④ 데이터시트 **43장 전수** 다운로드 후 grep. 이 등급 시트에서 `modulus|density|specific heat|poisson|tensile` **0 hit**.
verbatim (EM-370(Z) 시트, Rev 2024 July, 로컬 /data/paper_patent_corpus/standards_appnotes/pcb/EMC_EM-370Z_EM-37BZ_Datasheet_20240716.pdf):
`                  Thermal Conductivity                  0.58        W/m.K              -              ASTM D5470`
`                     Flexural              Warp       570~630        MPa          As Received`
`                    Strength                Fill      500~550        MPa          As Received`
→ **이 벤더가 이 등급에 대해 인쇄하는 기계·열 물성 축은 열전도율(ASTM D5470)과 굽힘강도(IPC-TM-650 2.4.4) 둘뿐이다.**
**다만 벤더가 이 물성을 아예 안 재는 것은 아니다** — 같은 서식의 `EM-526`·`EM-528`·`EM-528K`·`EM-A50`·`EM-S370(Z)`·`EM-S376`·`EM-S526`·`EM-S530`·`EM-S530K`·`EM-S570` 열한 등급은 `Flexural Modulus Warp/Fill GPa` 행을 찍는다(예 EM-526 `24~26 / 23~25 GPa`). **이 등급들만 안 찍는 것이다.** 그것도 굽힘이지 인장이 아니다."""

SHENGYI = """**[69차 EB — 중국어 사이트를 열었고, 중국어 총합 카탈로그는 존재하지 않는다]**
브리프의 가설은 「生益科技가 자국 설계자용 覆铜板综合样本을 낸다」였다. 실제로 열어 **틀렸음을 확정했다.**
① **도메인부터 함정이다.** `www.shengyi.com`·`www.sytech.com.cn`·`www.shengyi.com.cn` 은 셋 다 HTTP 200 이지만 **도메인 매매·광고 파킹 페이지**다(`精品域名：sytech.com.cn可出售！` / `is For Sale`). 진짜 벤더 사이트는 **`www.syst.com.cn`**(`<title>生益科技`).
② 그 사이트의 10개 제품 카테고리를 페이지네이션까지 돌아 **109 제품 전수** 열거하고 제품별 다운로드 목록을 받았다.
③ **중국 사이트가 내주는 'TDS' 는 영문 문서다.** `Shengyi_S1000-2M_TDS_zh.pdf` 는 코퍼스에 이미 있던 `CN-TDS-2308-04` 와 **md5 동일**(ed89ff95…).
④ `综合样本`·`产品手册`·`技术资料集` 에 해당하는 문서 구역이 없다. `Line up` 시트는 두께·ply-up·Dk/Df 뿐이고 `加工指南`(processing guide)은 보관·드릴·적층 파라미터뿐이다.
verbatim (S1170G, 로컬 /data/paper_patent_corpus/standards_appnotes/pcb/Shengyi_S1170G_TDS_zh.pdf):
`      Flexural Strength (LW/CW)                IPC-TM-650 2.4.4                      A                    Mpa            550/450`
S1000-2M: `Flexural Strength (LW/CW) … Mpa 567/442`. **S7439·S7439G 는 기계물성 행이 하나도 없다.** S7439GS(2025)에 하나 있으나 `Storage Modulus IPC-TM-650 2.4.24.4 DMA GPa 24` 로 **DMA 저장탄성률이지 영률이 아니다.**
`比热容`·`泊松比`·`密度` — 109 제품 전수에서 **0 hit**.
**벤더가 이 물성을 안 재는 것은 아니다** — `SCGA-500/GF255`(`Tensile Modulus(LW/CW) IPC-TM-650 2.4.4 A GPa 1.2/7.8`, `Tensile Strength 64/214 MPa`, `Density ASTM D792 g/cm3 2.25`), `S7136H`(`Tensile Modulus ASTM D638 A GPa 16.1/18.5`, `Tensile Strength 175/245 MPa`), `LNB33`(`15.6/19.7 GPa`, `112/143 MPa`), `SI10US`(`Young's modulus 50℃ 26 GPa / 200℃ 23 GPa`)는 인장 물성을 찍는다. **이 등급 시트에 안 싣는 것이다.**
**주의** — 이 사이트에 `S1170`(G 없는 것)은 **존재하지 않는다**(`S1170G` 11회, 맨 `S1170` 0회)."""

NANYA = """**[69차 EB — 대만 자국어(번체) 유통 포털을 열었고, 거기서도 영문 IPC-4101 서식만 나온다]**
브리프의 가설은 「南亞塑膠가 자국 설계자용 銅箔基板 產品型錄을 낸다」였다.
① `www.npc.com.tw/j2npc/zhtw/index` 는 404 다. 대만 번체 유통 포털(cclqc)에서 Nan Ya CCL 시트 30여 장을 받았다 — `NP-140TL`·`NP-155F`·`NP-155FBH`·`NP-175F`·`NP-175FM`·`NP-175FBH`·`NP-530`·`NP-535B`·`NP-536(HC)`·`NP-730`·`NP-822`·`NP-826`·`NPG-150D/N`·`NPG-151`·`NPG-170D/DC/N`·`NPG-171`·`NPG-180BH/BK`·`NPG-182H`·`NPG-188H/U`·`NPG-190BH`·`NPG-199(K/HK)`·`NPG-200WT`·`NPG-210BK`·`NPG-220KBK`·`NPG-630`·`NPGN-150LKHD/PY`.
② **그 시트들은 번체가 아니라 영문 IPC-4101 서식이다.** grep `彈性|模數|比熱|拉伸|密度|泊松|導熱|Modulus|Tensile|Specific|Density|Poisson|Conductivity` — 나오는 것은 `Specification: IPC-4101E is applicable` 한 줄뿐. **해당 물성 행이 없다.**
③ 참고 — 이 재료의 현재 영률은 유럽 파트너 Technolam 이 낸 Datenblatt 의 `19. Other / weitere` 절에서 온 **t2**(68차 DC)다. **제조사 자신의 표는 아직 못 봤다.**
④ **아직 안 연 문 하나** — `Nanya_CCL_ProductCatalog_2001-09_scanned_52p.pdf`(52쪽)를 받았으나 **텍스트층이 52자뿐인 스캔**이다. 이 배치는 렌더해 읽지 못했다. **이건 부재 근거가 아니다.**"""

DOOSAN_CP = """**[69차 EB — 한국어·중국어 로케일을 전부 열었고, 세 언어 어디에도 비열 열이 없다]**
브리프의 가설은 「두산전자가 한국어 동박적층판 종합 카탈로그를 낸다」였다. 실제로 열어 **비열에 대해서는 틀렸음을 확정했다.**
① 제품 상세표를 `/kr/` · `/en/` · `/cn/` 세 언어로 받아 `<tr>`/`<td>` 파서로 **행 단위 대조**했다(DS-7402HD 기준). **24행이 세 판 모두 동일**하고, **한국어 페이지의 행 이름조차 영어**다:
`Mechanical | Young's modulus | 24  | GPa  | As received | IPC-TM-650 2.4.18.3`
`             Density         | 1.7 | g/㎤ | -           | -`
`             Poisson ratio   | 0.2 | -    | -           | -`
→ 번역조차 하지 않은 같은 표다. **자국어 전환으로 열이 늘지 않는다.**
② 전 등급을 한 표에 늘어놓은 문서는 이미 있다 — `Copper Clad Laminate (CCL) - Technical Data Sheet (ver. 2024.09.30)` 8쪽(작성자 `김정현(Jeonghyun Kim) (주)두산 전자`). 그 `[Thermal Properties]` 절의 열 머리글 verbatim:
`Tg | Td (Decomposition Temperature) | T-288 (Time to Delamination) | CTE (X/Y/Z a1, Z a2) | Thermal Conductivity (ASTM E 1461 / ASTM D 5470 / UL 796) | Max. Operating Temperature | Z Expansion`
→ **비열 열이 없다.** `[Mechanical Properties]` 절도 `Young's Modulus | Flexural Strength | Storage Modulus | Tensile Strength | Peel Strength | Elongation | Dimensional Stability | Density | Poisson Ratio` 로 비열이 없다.
③ 사이트의 `기술지원` 4쪽(`CCL_tech_support01~04`)은 ANSYS 휨해석·3D Moire·T3STER 열저항·HFSS 시뮬레이션 **서비스 안내**이고 물성표가 아니다.
④ `POST /rest/product/msds/list {"language":"ko"}` 로 120 제품 객체를 받아 `productOption`·`productAttachmentList` 를 확인했다 — 옵션 필드는 `Tg/Td/CTE-XY/CTE-Z/Dk/Df` 뿐이고 첨부는 **전부 MSDS**(183건, `영문` 120 · `국문` 63)다. **TDS·카탈로그 첨부 구분이 없다.** (MSDS 축은 동시에 도는 형제 배치가 잡고 있어 건드리지 않았다.)
⑤ **아직 안 연 문** — `dse.co.kr` 구판 카탈로그 쪽(2003·2005)을 받아 두었다. `Doosan_CCL_DS-7402_LegacyCatalogPage_dse.co.kr_2005.pdf` 는 텍스트가 나오고 강성축이 `Flexural Modulus Gpa A 27 - 30`(굽힘)이다. **구판에 비열이 있는지는 아직 전수로 확인하지 못했다.**"""

DOOSAN_TS = """**[69차 EB — 열은 있는데 이 등급 칸이 비어 있다. '열이 없다'와 구분해 적는다]**
Doosan 8쪽 All-Properties TDS(ver. 2024.09.30)의 `[Mechanical Properties]` 절에는 `Tensile Strength` **열이 실제로 있다** — 단위 `MPa`, 시험법 `IPC-TM-650 2.4.18.3`, 조건 `As Received`.
그런데 그 열에 값이 든 등급은 **DSflex 계열**(600 `220` · 600P `180` · 600U `390` · 600D `290` · 600UY `185` · 600UF(DS) `280` · 600UK(SS) `280` · 900 `300` MPa)과 **DS-7402BS (DF) `200~230` · (DFM) `220~240` · DS-8402H BS (DFL) `180~220` · DS-9530 `4.5`** 뿐이고, **DS-74xx·84xx·85xx 강성 CCL 칸은 전부 공란**이다.
`/kr/`·`/en/`·`/cn/` 제품 상세 페이지에도 이 등급의 `Tensile strength` 행이 없다(위 비열 판정 ①과 같은 대조).
→ **벤더가 이 등급에 대해 인장강도를 인쇄하지 않는다.** 굽힘강도(`Flexural Strength`)로 대신 채우지 않았다."""

ARISAWA = """**[69차 EB — 일본어 카탈로그 전수를 열었고, 이 벤더는 커버레이에 기계물성을 안 찍는다]**
① 벤더의 일본어 카탈로그 디렉터리 `https://www.arisawa.co.jp/jp/products/data/CATALOG_*_JP.pdf` 를 찾아(`jp/products/fpc01~04.html` 에서 링크) **일본어 시트 19장 전수** + 영문 C33 을 받았다.
② C33 시트(`低誘電カバーレイ「C33シリーズ」`, `'25.07.01 (A)`, 1쪽, 텍스트 PDF)의 **행 전부** verbatim:
`  項目                                 単位          C33`
`  ポリイミド厚さ                             µm         12.5`
`  接着剤厚さ                               µm          25`
`  誘電率                カバーレイ             -         2.95`
`  (10GHz）             接着層              -         2.60`
`  誘電正接               カバーレイ             -       0.0053`
`  (10GHz)             接着層              -       0.0026`
`  引きはがし強さ`
`                                    N/cm         8.5`
`  (1oz Cu引き,90°方向)`
`  はんだ耐熱性                              ℃          300`
→ **여섯 항목이 전부다.** `引張強さ`·`ヤング率`·`引張弾性率`·`曲げ弾性率`·`比熱`·`熱伝導率`·`比重`·`密度`·`ポアソン比` **전부 없다.**
③ **영문판은 내용상 쌍둥이다** — `grep -icE 'tensile|elongation|modulus|density'` **0**. 자국어 전환의 이득이 0 인 사례다.
④ 다른 계열도 같다 — C/CG/C90/C91/C92 커버레이는 `接着剤 弾性率 GPa`(접착층만) 하나뿐. 기계물성이 있는 건 **RT 계열 감광성 커버레이**(`弾性率 GPa 0.8/1.1`, `破断強度 MPa 19/23` — 용어가 `引張強さ`가 아니라 `破断強度`)와 **2층 CCL**(`引張り弾性率 GPa 5.5~6.5`)인데 **둘 다 C33 이 아니다.**
⑤ **總合カタログ(총합 카탈로그)가 존재하지 않는다.** Arisawa 는 계열별 1쪽 시트만 낸다 — 이 배치가 표적으로 삼은 형식 자체가 이 벤더에는 없다.
→ **이 칸은 유추로 채우면 안 된다.** 형제 계열(RT `破断強度 19~23 MPa`, 2층 CCL `引張り弾性率 5.5 GPa`)은 수지계와 구조가 달라 C33 의 값이 될 수 없다."""

PANA_CP = """**[69차 EB — 두 판을 열었고, 이 한 칸만 두 판 사이에 끼여 있다]**
① **2013년판** 「電子回路基板材料」 총합 카탈로그(160쪽) 印刷ページ17 의 특성일람표는 `比熱(DSC法, 25℃, J/kg℃)` 열을 찍는다. **그런데 그 표에 R-1566S 행이 없다** — 2013년보다 뒤에 나온 등급이다(68차 DC §4-다와 같은 결론, 이 배치가 350 dpi 렌더로 재확인).
② **2021년판** 특성일람표(印刷ページ 9·10)에는 **R-1566S 행이 있다.** 이 배치가 거기서 이 등급의 영률(`ASTM D3039` 20.7/19.7 GPa)·열전도율(0.62 W/m·K)·포아송비(`JIS K 7161-1` 0.2)를 얻었다.
③ **그러나 2021년판에는 `比熱` 열 자체가 없다.** 그 판의 열물성 열은 `熱分解温度`·`熱膨張係数`·`熱伝導率` 까지이고 比重·比熱 열이 빠졌다.
→ **비열만 두 판 사이에 끼여 남았다.** 2013(比熱 있음·등급 없음) ∩ 2021(등급 있음·比熱 없음) = 공집합.
**다음 배치의 표적** — 로컬에 이미 있는 `Panasonic_ElectronicMaterials_Catalog_2015-11_*`(3장)와 `Panasonic_CircuitBoardMaterials_Catalog_2019-06_*`(4장)의 특성일람표 쪽을 렌더해서 **`比熱` 열과 R-1566S 행이 동시에 있는 판**을 찾아라. 있으면 이 한 칸이 닫힌다.
**이건 부재 판정이 아니라 '아직 못 찾았다' 다.**"""

# ---- 표적별로 건다 ----
for mid in (2433, 2434, 2435, 2517, 2518):
    for k in ('mechanical.youngs_modulus', 'thermal.specific_heat', 'mechanical.tensile_strength'):
        add(mid, k, 'core_absent_from_vendor_sheet', EMC)

for mid in (601, 2516, 2442, 2443):
    for k in ('mechanical.youngs_modulus', 'thermal.conductivity', 'thermal.specific_heat', 'mechanical.tensile_strength'):
        add(mid, k, 'core_absent_from_vendor_sheet', SHENGYI)

NANYA_TAIL = '''
**열전도율·비열은 이 배치가 닫았다 — 부재판정에서 뺀다.** 제조사 시트에는 없지만 유럽 파트너 Technolam 의 `19. Other / weitere` 절이 찍는다(`Thermal Conductivity 0,53 ASTM-E-1461 / 0,46 ASTM-D-5470 W/mK`, `Specific Heat at 25 °C 0,91 J/g°C`). 68차 DC §5-2 가 넘긴 그 문서이고 **이미 코퍼스에 있었다**. t2 로 넣었다.
**인장강도만 남는다** — Technolam §19 에도 인장강도 행은 없고, 제조사 시트의 기계축은 `Flexural strength LW/CW` 하나뿐이다. 굽힘강도로 대신 채우지 않았다.'''
for mid in (2440, 2441):
    add(mid, 'mechanical.tensile_strength', 'core_absent_from_vendor_sheet', NANYA + NANYA_TAIL)

add(253, 'mechanical.tensile_strength', 'core_absent_from_vendor_sheet', ARISAWA)
add(2521, 'thermal.specific_heat', 'not_found_yet', PANA_CP)

# Doosan — 전 등급을 덮는 8쪽 총합 TDS 와 3개 언어 상세표로 확인한 균일 판정
doo = [i for i, n in name.items() if n.startswith('Doosan ')]
for mid in sorted(doo):
    add(mid, 'thermal.specific_heat', 'core_absent_from_vendor_sheet', DOOSAN_CP)
    add(mid, 'mechanical.tensile_strength', 'core_absent_from_vendor_sheet', DOOSAN_TS)

out = {"batch": "69차 EB", "verdicts": V}
p = '/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_eb/eb02_verdicts.json'
json.dump(out, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
cnt = collections.Counter(v['key'].split('.')[1] for v in V)
print('verdicts', len(V), dict(cnt))
print('materials touched', len({v['material_id'] for v in V}))
