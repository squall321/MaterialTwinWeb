# 73차 ID — V5(판정도 값도 없는 코어7 칸)을 벤더 문서 실사로 닫는 판정 JSON 생성기.
import sqlite3, os, json, collections

DB = 'file:' + os.environ['MATERIALTWIN_DATA_DIR'] + '/materialtwin.db?mode=ro'
CORE7 = ['physical.density','mechanical.youngs_modulus','mechanical.poisson_ratio',
         'thermal.expansion_linear','thermal.conductivity','thermal.specific_heat','mechanical.tensile_strength']
VK = ('core_not_applicable','core_absent_from_vendor_sheet','core_rejected_printed_value','core_no_public_document')

c = sqlite3.connect(DB, uri=True)
prod = {i:(n, json.loads(a or '{}')) for i,n,a in c.execute('select id,name,attributes from material')
        if json.loads(a or '{}').get('role') == 'product'}
have = collections.defaultdict(set)
for m,k in c.execute('select distinct material_id,property_key from property_value'): have[m].add(k)
gap = collections.defaultdict(list)
for m,(n,a) in prod.items():
    judged = set()
    for K in VK: judged |= set((a.get(K) or {}).keys())
    for k in CORE7:
        if k not in have[m] and k not in judged: gap[m].append(k)

TAG = "**[73차 ID]** "

# ---- 계열별 증거 블록. 각 블록은 (재료 id 목록, 문서 목록, 행 어휘, 물성별 사유) ----
def rows(*r): return " · ".join(r)

FAM = {}

FAM['RESONAC'] = dict(
  ids=[2733,2734,2735,2736,2737,2738,2739,2740,2741,2742,
       2763,2764,2765,2766,2767,2768,2769,2770,2771,2772,2773,2774,2775,2776,2777,
       2778,2779,2780,2781,2782,2796,2797,2798],
  docs=[
    "/data/paper_patent_corpus/standards_appnotes/pcb/Resonac_MCL_CopperCladLaminates_Catalog_ja_2023-2024.pdf (66쪽)",
    "/data/paper_patent_corpus/standards_appnotes/pcb/Resonac_MCL-E-GEA-Series_CopperCladLaminates_Catalog_2025-05.pdf (65쪽)",
    "/data/paper_patent_corpus/standards_appnotes/pcb/Resonac_MCL_CopperCladLaminates_Catalog_en_2026-07.pdf (51쪽)",
    "/data/paper_patent_corpus/standards_appnotes/pcb/Resonac_MCL_CopperCladLaminates_Catalog_ja_2026-04.pdf (59쪽)",
    "/data/paper_patent_corpus/standards_appnotes/pcb/Resonac_MCL-HD60-HD80-HD90_Datasheet_en_2025-05.pdf (1쪽, 텍스트층 0자 — 250 dpi 렌더로 눈으로 읽었다)",
    "日立化成テクニカルレポート 별쇄 6건 (AS-400HS No.58 · TD-002 No.58 · MCL-HS100 No.59 · MCL-LW-900G/910G No.58 · MCL-LW-990G No.62 · MCL-E-700G(R) No.54)",
  ],
  vocab=("Thickness · Glass Cloth(type/Style) · Dk · Df · Copper Peel Strength · "
         "弾性率/Elastic(Tensile) Modulus · Flexural modulus · Tg(TMA/DMA) · CTE x/y/z · "
         "熱伝導率/Thermal conductivity · Water Absorption · Volume/Surface/Insulation Resistance · "
         "Solder Heat Resistance · Flammability · IPC-4101 slash sheet"),
  audit=("네 판(版) 카탈로그 전권 토큰 검사 — `比重` 0 · `比熱` 0 · `熱容量` 0 · `ポアソン` 0 · `ポアッソン` 0 · "
         "`引張強さ` 0 · `引張強度` 0 · `Poisson` 0 · `Specific Gravity` 0 · `Specific Heat` 0. "
         "`密度` 3회와 `Density` 1~2회는 **전부 산문**(`高密度電子機器` · `high density multi-layer PWB`)이고 표 행이 아니다. "
         "`specific` 19회는 전부 `Standard Specifications` 라는 절 제목이다. "
         "`Tensile` 14~15회는 전부 `Tensile modulus` 행 이름과 각주 `*5: Tensile` · "
         "`*1) Heating Rate: 10℃/min. (Tensile)` 이다 — **강도가 아니라 모듈러스의 시험모드 표시다.**"),
)

FAM['LAZ_CORE'] = dict(
  ids=[2750,2751,2752,2753,2754,2755,2756],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_LAZ-4785_PackageCore_Spec_ja_2026-09-09.html (LAZ-4785 特性一覧, 7등급 1표)"],
  vocab=("特長 · 最薄/最厚の厚み(생산실적) · ガラスクロス番手 · 厚み(공칭) · Tg(DMA) · CTE-1 xy · CTE-1 z · "
         "弾性率(30 ℃ / 260 ℃) · Dk(1 GHz) · Df(1 GHz) · ピール強度(12LP銅箔) · 吸水率(D-24/23) · 熱伝導率"),
  audit="표를 행 단위로 전부 펴서 어휘를 세었다. 위 13행이 전부다.",
)

FAM['LAZ_PREPREG'] = dict(
  ids=[2757,2758,2759,2760,2761],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_LAZ-6785_Prepreg_Spec_ja_2026-09-09.html (LAZ-2002 / LAZ-6785 特性一覧, 5등급 1표)"],
  vocab=("ガラスクロス(Type/番手) · 厚み · Tg(DMA) · CTE-1(XY) · 弾性率(30 ℃ / 260 ℃) · Dk(1 GHz) · Df(1 GHz) · "
         "ピール強度 · 吸水率(D-24/23)"),
  audit=("표를 행 단위로 전부 펴서 어휘를 세었다. 위 9행이 전부다. "
         "**같은 벤더의 코어재 표(LAZ-4785)에는 있는 `熱伝導率` 행조차 프리프레그 표에는 없다** — "
         "행 부재가 이 표 고유의 것이지 우리가 못 찾은 것이 아니라는 증거다."),
)

FAM['LAZ_SR'] = dict(
  ids=[2762],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_LAZ-7752_SolderResistAlt_Spec_ja_2026-09-09.html (LAZ-7752 VerJB 特性一覧, 1등급 1표)"],
  vocab="特長 · 用途 · 厚み · Tg(DMA) · CTE-1(XY) · 弾性率(30 ℃ / 260 ℃) · Dk(1 GHz) · Df(1 GHz) · ピール強度(12 um VLP 銅箔) · 吸水率(D-24/23)",
  audit="표를 행 단위로 전부 펴서 어휘를 세었다. 위 10행이 전부다.",
)

FAM['LAZ_BUILDUP'] = dict(
  ids=[2799],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_LAZ-Buildup_Spec_ja_2026-09-09.html (BLα-3700GS 特性表, 1등급 1표)"],
  vocab=("Tg(by DMA) · Tg(by TMA) · CTE1 · CTE2 · Tensile Modulus(R.T.) · Tensile Modulus(250 ℃) · "
         "Dielectric constant(1 GHz) · Dielectric Dissipation Factor(1 GHz) · Moisture Absorption"),
  audit=("표를 행 단위로 전부 펴서 어휘를 세었다. 위 9행이 전부다. "
         "**`Tensile Modulus` 두 행이 있지만 `Tensile Strength` 행은 없다** — 모듈러스와 강도를 혼동하지 않았다."),
)

FAM['ELC'] = dict(
  ids=[2727,2728,2729,2730,2731,2732],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_Sumilite_ELC_DoubleSided_CCL_Spec_ja_2026-09-09.html (両面 PWB 용 4등급)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_Sumilite_ELC_Multilayer_PWB_Spec_ja_2026-09-09.html (多層 PWB 용 2등급)"],
  vocab=("熱膨張係数 CTE X/Y/Z(α1,α2) · ガラス転移温度(TMA/DMA/DSC) · はんだ耐熱 · 引き剥がし強さ · "
         "曲げ強さ(タテ/ヨコ) · 曲げ弾性率(タテ/ヨコ) · 引っ張り強さ(タテ/ヨコ) · 引っ張り弾性率(タテ/ヨコ) · "
         "比誘電率 · 誘電正接 · 体積抵抗率 · 表面抵抗 · 吸水率 · 耐燃性(UL-94V) · 熱伝導率(레이저플래시법)"),
  audit=("두 페이지의 표를 행 단위로 전부 펴서 어휘를 세었다. 위 15행이 전부다. "
         "이 표는 **인장(引っ張り)과 굽힘(曲げ)을 따로 인쇄하는 드문 시트**인데도 "
         "`比重`·`密度`·`ポアソン比`·`比熱` 네 행은 없다."),
)

FAM['PLEL'] = dict(
  ids=[2800,2801,2802,2803],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/SumitomoBakelite_Sumilite-PL-EL_Catalog_ja_2026-09-09.pdf (4쪽 = 인쇄 25~32쪽; **텍스트층 0자** — 4쪽 전부 200 dpi 렌더로 눈으로 읽었다)"],
  vocab=("[인쇄 25~26쪽 打抜き加工用] 絶縁抵抗 · 曲げ強度(Flexural strength) · 吸水率 · 加熱後外観 · "
         "比重(Specific gravity) · 耐燃性(UL法) · JIS積層板記号 · 納入サイズ  ‖  "
         "[인쇄 27~28쪽 機械加工用] 貫層耐電圧 · 沿層耐電圧 · 絶縁抵抗 · 曲げ強度 · アイゾット衝撃強さ · "
         "へき開強さ · 吸水率 · 加熱後外観 · 比重 · 耐アセトン性 · 耐燃性 · JIS積層板記号 · 納入サイズ"),
  audit=("4쪽 전부를 렌더로 확인했다 — 3쪽은 鉄道車両用材料燃焼試験成績書(연소시험 성적서) 두 장이고 "
         "4쪽은 厚さ許容差(두께 공차) 표다. **물성표는 1·2쪽의 `一般特性 General Properties` 둘뿐이고 "
         "그 둘의 행 어휘가 위가 전부다.** 기계축은 `曲げ強度` 하나뿐이라 인장강도·인장탄성률 행이 아예 없고, "
         "열축은 `比重` 하나뿐이라 熱伝導率·比熱·線膨張係数 행이 없다."),
)

FAM['KEL'] = dict(
  ids=[2804,2805,2806,2807],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/HitachiChemical_CopperCladLaminates_FullCatalog_en_2017-03.pdf "
        "(90쪽 전권; KEL 특성표 세 장 = PDF 82쪽 4등급 합본 · 84쪽 KEL-GEF · 86쪽 KEL-571/973)"],
  vocab=("Withstand voltage vertical to layer · Insulation Resistance · Dielectric Constant(1 MHz) · "
         "Dissipation Factor(1 MHz) · Flexural strength(Length/Width) · Flexural Modulus(Length/Width) · "
         "Compressive Strength(vertical/parallel) · Izod impact strength · Cleavage Strength · Air Flammability · "
         "specific gravity · chemical resistance(HCl/NaOH) · Flammability(UL94) · Aptitude punching temperature · "
         "CTE X/Y/Z(30~80 ℃)"),
  audit=("90쪽 전권을 쪽별 텍스트 길이로 감사했다 — **40자 미만인 쪽이 0이다**(이미지 전용 쪽이 없으므로 "
         "토큰 검사가 표를 놓칠 수 없다). 전권 토큰 검사: `specific heat` **0** · `thermal conductivity` **0** · "
         "`Poisson` 2회(둘 다 PDF 44쪽 MCL-E-67 의 **눈금만 있는 그래프** 제목이고 KEL 등급이 아니다) · "
         "`Tensile` 2회(하나는 다른 등급의 `Elastic Modulus (Tensile)` 행, 하나는 같은 그래프 쪽). "
         "KEL 특성표 세 장의 행 어휘는 위 15행이 전부이고 세 장이 서로 같다."),
)

FAM['TECHNOLAM'] = dict(
  ids=[2784,2785,2786,2787,2788],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/Technolam_NanYa_NPG-150N-NPG-150NB_Datasheet_2019-02.pdf (6쪽)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/Technolam_NanYa_NPG-170TL-NPG-170R-NPG-170B_Datasheet_2019-02.pdf (6쪽)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/Technolam_NanYa_NPG-170DTL-NPG-170DR-NPG-170DB_Datasheet_2019-02.pdf (6쪽)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/Technolam_NanYa_NPG-180BH-NPG-180BHB_Datasheet_2019-08.pdf (6쪽)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/Technolam_NanYa_UV-Block-FR-4-86_Datasheet_2019-02.pdf (4쪽)"],
  vocab=("[Performance List 1/2 = IPC-4101 서식 1~19항] Peel Strength · Volume/Surface Resistivity · "
         "Moisture Absorption · Dielectric Breakdown · Permittivity · Loss Tangent · **Flexural Strength(2.4.4)** · "
         "Flexural Strength at Elevated Temperature · Arc Resistance · Thermal Stress · Electric Strength · "
         "Flammability · Tg(TMA/DMA/DSC) · Td · Z-Axis CTE(α1/α2) · Time to Delamination · Halogen Content · CAF  ‖  "
         "[Performance List 2/2 = 20항 Other] Permittivity/Loss Tangent at 1 GHz · Dimensional stability · "
         "X/Y-Axis CTE · **Thermal Conductivity** · **Young's Modulus(Length/Cross)** · **Specific Heat at 25 ℃** · "
         "Caloric Value · **Density(50 % resin content)** · PCT · RoHS · REACH · Conflict Minerals · DIN EN 45545-2 · CTI"),
  audit=("다섯 시트 전부를 토큰 검사했다 — `Poisson` **0** · `Querkontraktion` **0** · `Tensile` **0** · "
         "`Zugfestigkeit` **0** (독영 병기 시트라 독일어 표제까지 걸었다). "
         "**이 시트는 밀도·비열·열전도율·영률을 다 인쇄하는 드문 시트다** — 그래서 이 두 칸의 부재는 "
         "「벤더가 물성을 안 찍는다」가 아니라 「이 두 물성만 안 찍는다」는 뜻이고, 더 강한 판정이다."),
)

FAM['NANYA_NP'] = dict(
  ids=[2789,2790,2791],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/Nanya_CCL_NP-730_Datasheet_cclqc_zhTWportal_2026-09-09.pdf (1쪽)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/Nanya_CCL_NP-822_Datasheet_cclqc_zhTWportal_2026-09-09.pdf (1쪽)",
        "/data/paper_patent_corpus/standards_appnotes/pcb/Nanya_CCL_NP-826_Datasheet_cclqc_zhTWportal_2026-09-09.pdf (1쪽)"],
  vocab=("Permittivity(Process/Design) · Loss Tangent · Thermal Coefficient of εr · Volume resistivity · "
         "Surface resistivity · Arc resistance · Dielectric breakdown · Td(5 % weight loss) · CTE(z) · CTE(x,y) · "
         "Thermal stress · Peel strength 1 oz · Moisture absorption · **Density (Specific Gravity)** · Flammability · "
         "**Thermal Conductivity** · Dimensional stability X-Y axis · Passive Intermodulation"),
  audit=("세 시트의 `PERFORMANCE LIST` 를 행 단위로 전부 펴서 어휘를 세었고 **셋이 서로 같다**(위 18행). "
         "토큰 검사: `Poisson`·`泊松` 0 · `Tensile`·`抗拉`·`拉伸` 0 · `Specific Heat`·`比熱`·`比热` 0 · "
         "`Young`·`彈性`·`弹性` 0. 텍스트층이 살아 있다(1,796~1,882자/1쪽). "
         "**밀도와 열전도율은 이 시트에 인쇄돼 있고 이미 카드에 들어가 있다** — 부재는 네 물성에 한정된다."),
)

FAM['ROGERS'] = dict(
  ids=[2793,2794,2795],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/Rogers_RO3000_Laminate_DataSheet_RO3003_RO3006_RO3010_RO3035_2024-01.pdf "
        "(4쪽; `Standard Properties Table` 2쪽 — 350 dpi 렌더로 열 대조했다)"],
  vocab=("[Electrical] Dielectric Constant(process/design) · Dissipation Factor · Thermal Coefficient of Dk · "
         "Volume Resistivity · Surface Resistivity  ‖  [Thermal] Decomposition Temperature · CTE x/y/z · "
         "**Thermal Conductivity**  ‖  [Mechanical] Copper Peel Strength · **Young's Modulus(ASTM D638, 2행)** · "
         "Dimensional Stability  ‖  [Physical] Flammability · Moisture Absorption · **Density(ASTM D792)** · "
         "**Specific Heat Capacity**"),
  audit=("전권 토큰 검사 — `Poisson` **0** · `Tensile` **0** · `Flexural` **0**. "
         "열 순서는 **RO3003 / RO3035 / RO3006 / RO3010** 이고, `Density` 행 2.1 / 2.1 / 2.6 / 2.8 이 "
         "카드에 이미 들어간 값(RO3035 2100 · RO3006 2600 · RO3010 2800 kg/m³)과 정확히 맞아 "
         "**열 대응이 밀리지 않았음을 값으로 교차검증했다.**"),
)

FAM['SHENGYI'] = dict(
  ids=[2792],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/Shengyi_SCGA-500_GF255_TDS_zh_2019.pdf (1쪽, `GENERAL PROPERTIES` 1표)"],
  vocab=("Dielectric Constant(Process Dk) · Loss Tangent · TcDk · CTE(X/Y/Z-axis) · Volume Resistivity · "
         "Surface Resistivity · Peel Strength · Water Absorption · **Thermal Conductivity** · "
         "Tensile Modulus(LW/CW) · Tensile Strength(LW/CW) · **Density** · Flammability"),
  audit=("표를 행 단위로 전부 펴서 어휘를 세었다. 위 13행이 전부이고 `Poisson`·`泊松` 0 · "
         "`Specific Heat`·`比熱`·`比热` 0 이다."),
)

FAM['MGC_820'] = dict(
  ids=[2726],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/MGC_CCL-HL820WDI_ChipLED_BT_Lineup_ja_2026-09-09.html "
        "(Chip-LED用BT材料 제품 라인업 페이지, 표 2개)"],
  vocab=("比誘電率(1 MHz/1 GHz) · 誘電正接(1 MHz/1 GHz) · 絶縁抵抗 · 表面抵抗 · 体積抵抗率 · "
         "曲げ強さ(縦/横) · 曲げ弾性率(縦/横) · 引張強さ(縦/横) · ヤング率(縦/横) · "
         "ガラス転移温度(DMA/TMA) · 熱膨張係数(縦横 / Z α1,α2) · ピール強度(12/18 µm) · 耐燃性(UL94)"),
  audit=("페이지의 `<table>` 두 개를 HTML 파서로 전부 펴서 셀 단위로 읽었다. 첫 표는 두께 라인업이고 "
         "물성표는 둘째 하나뿐이며 그 행 어휘가 위가 전부다(`耐燃性` 에서 끝난다). "
         "**같은 벤더의 BT 재료 라인업 페이지(CCL-HL832/HL972)에는 `密度`·`比熱`·`熱伝導率`·`ポアッソン比` "
         "네 행이 있는데 이 Chip-LED 페이지에는 그 네 행이 통째로 없다** — 벤더가 제품군마다 "
         "다른 서식을 쓴다는 뜻이고, 이 페이지에 관한 한 부재가 확정이다."),
)

FAM['MGC_972'] = dict(
  ids=[2720,2721],
  docs=["/data/paper_patent_corpus/standards_appnotes/pcb/MGC_CCL-HL832-HL972_BTResin_Lineup_ja_2026-09-09.html "
        "(半導体パッケージ用低熱膨張率ハロゲンフリーBT材料 라인업, `一般材料特性一覧表` 3표)"],
  vocab="… 耐燃焼性 · 密度 · 比熱 · 熱伝導率 · **ポアッソン比** · 吸水率",
  audit=("셋째 표(HL972LF typeLD / **HL972LFG** / **HL972LFG typeLD** / GHPL-830SR / GHPL-830SR typeLC, 5열)의 "
         "원시 HTML 을 셀 단위로 읽었다. `ポアッソン比` **행은 있다.** 그 행의 다섯 셀은 "
         "`0.2` · **`-`** · **`-`** · `0.21` · `0.21` 이다 — **HL972LFG 와 HL972LFG typeLD 두 열만 대시다.** "
         "열 대응은 같은 표의 다섯 행으로 교차검증했다: 密度 1.9/**1.8**/**1.8**/1.8/1.8 · 比熱 0.9/**0.95**/**0.95**/0.9/0.9 · "
         "熱伝導率 0.6/**0.6**/**0.6**/0.7/0.7 · 引張強さ 220/**210**/**210**/290/300 · ヤング率 25/**23**/**21**/21/22 — "
         "다섯 행 전부가 카드에 이미 들어간 값과 글자 그대로 일치한다."),
)

# ---- 물성별 사유 문장 ----
def why(fam, key, f):
    K = {'physical.density':'밀도(比重/Specific gravity/Density)',
         'mechanical.youngs_modulus':'인장 탄성률(영률)',
         'mechanical.poisson_ratio':'포아송비',
         'thermal.expansion_linear':'선열팽창계수',
         'thermal.conductivity':'열전도율',
         'thermal.specific_heat':'비열',
         'mechanical.tensile_strength':'인장강도'}[key]
    extra = ''
    if key == 'mechanical.youngs_modulus' and fam in ('KEL','PLEL'):
        extra = (" **이 시트의 기계축은 `Flexural Modulus`(굽힘) 뿐이다** — 이름이 아니라 시험모드로 갈랐고, "
                 "굽힘 탄성률을 영률로 옮기지 않았다.")
    if key == 'mechanical.tensile_strength' and fam in ('KEL','PLEL','TECHNOLAM','ELC'):
        extra = (" **이 시트가 인쇄하는 강도는 `曲げ強度`/`Flexural strength`(굽힘) 이다** — "
                 "IPC-TM-650 2.4.4 · JIS 굽힘 시험이라 인장강도로 옮기면 틀린 값이 된다.")
    if key == 'mechanical.tensile_strength' and fam in ('RESONAC','LAZ_BUILDUP'):
        extra = " **이 시트에는 강도 행 자체가 없다** — 기계축이 모듈러스뿐이다."
    if key == 'thermal.conductivity' and fam == 'LAZ_CORE':
        extra = (" 이 표에는 `熱伝導率` **행이 있으나 이 등급 열이 `N.D.`** 다(같은 행의 TH-G·GH-G·TH-B 0.7, "
                 "GS-BA 0.6 은 값이 인쇄돼 이미 카드에 들어가 있다). 벤더가 이 등급은 측정값을 안 내놓은 것이다.")
    if key == 'thermal.specific_heat' and fam == 'ROGERS':
        extra = (" 이 표에는 `Specific Heat Capacity` **행이 있으나 RO3035 열만 공란**이다"
                 "(RO3003 0.9 · RO3006 0.86 · RO3010 0.8 J/g/K 은 인쇄돼 있다). "
                 "350 dpi 렌더로 눈으로 확인했다 — 추출 누락이 아니라 **인쇄 자체가 비어 있다.**")
    if key == 'mechanical.poisson_ratio' and fam == 'MGC_972':
        extra = " 행은 있고 **이 등급 열만 `-`** 다. 위 교차검증 참조."
    return (TAG + f"이 재료의 자기 문서를 전부 열었고 **{K} 행이 없다.**" + extra +
            "\n\n**연 문서** — " + "; ".join(f['docs']) +
            "\n\n**표 행 어휘 전수** — " + f['vocab'] +
            "\n\n**감사** — " + f['audit'] +
            "\n\n이 판정은 「없다」이지 「못 찾았다」가 아니다. 이 칸을 닫으려면 벤더 기술문의뿐이다.")

out = {"batch": "73차 ID",
       "note": "V5(판정도 값도 없던 코어7 칸)을 벤더 문서 실사로 닫는다. 값이 아니라 **판정**이다 — "
               "문을 열었고 그 행이 없다는 것을 행 어휘 전수로 확정한다.",
       "verdicts": []}

covered = {}
for fam, f in FAM.items():
    for mid in f['ids']:
        keys = gap.get(mid, [])
        if not keys:
            print(f"  ! [{mid}] V5 칸이 없다 — 건너뜀"); continue
        out['verdicts'].append({
            "material_id": mid, "name": prod[mid][0],
            "core_absent_from_vendor_sheet": {k: why(fam, k, f) for k in sorted(keys)},
        })
        covered[mid] = (fam, keys)

json.dump(out, open('id73_02_verdicts.json','w'), ensure_ascii=False, indent=1)
n = sum(len(v['core_absent_from_vendor_sheet']) for v in out['verdicts'])
print(f"판정 재료 {len(out['verdicts'])}종 · 칸 {n}")
print("계열별:", {fam: sum(len(covered[m][1]) for m in f['ids'] if m in covered) for fam, f in FAM.items()})
# 완결 카드 판정
done = 0
for mid,(fam,keys) in covered.items():
    if len(have[mid] & set(CORE7)) + len({k for K in VK for k in (prod[mid][1].get(K) or {})} & set(CORE7)) + len(keys) == 7:
        done += 1
print("이 배치로 코어7 이 전부 값 아니면 판정으로 채워지는 카드:", done)
