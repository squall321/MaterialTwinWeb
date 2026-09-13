# 74차 JB 코어7 부재판정 생성기 — Sumitomo 24장의 열린 칸을 문서 실사로 닫는다
import json, os, sqlite3, collections

OUT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
     "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
P = "/data/paper_patent_corpus/standards_appnotes/pcb/"

K_DEN, K_YM, K_PR = "physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio"
K_CTE, K_TC, K_CP, K_TS = ("thermal.expansion_linear", "thermal.conductivity",
                           "thermal.specific_heat", "mechanical.tensile_strength")
LBL = {K_DEN: "`比重 Specific gravity`·`密度 Density`",
       K_YM: "`ヤング率`·`引っ張り弾性率`·`Tensile Modulus`(인장 탄성률)",
       K_PR: "`ポアソン比 Poisson's ratio`",
       K_CTE: "`熱膨張係数 CTE`",
       K_TC: "`熱伝導率 Thermal conductivity`",
       K_CP: "`比熱 Specific heat`",
       K_TS: "`引っ張り強さ Tensile strength`"}

HEAD = "**[74차 JB]** "
SDS = ("\n\n**SDS 경로는 두드리지 않았다 — 이 제품군에서 닫혀 있기 때문이다.** 72차 HD 가 확인했다: "
       "Sumitomo 는 SDS 포털 자체가 없고(사이트맵 435링크에 `SDS` 적중 0), **고체 물품(article)인 적층판에는 "
       "SDS 의무가 없다.** 같은 결과가 Resonac 에서도 나왔다. 74차 JB 는 이 경로에 시간을 쓰지 않았다.")
CORPUS = ("\n\n**논문 코퍼스 표 층까지 두드렸다(73차 IB 의 교훈).** 우리 FTS 검색은 본문만 보고 코퍼스의 59 % 는 "
          "표를 `tables/*.md` 로 빼 두어 색인 밖이다. 74차 JB 가 `/data/paper_patent_corpus/structured` 의 "
          "**표 층 `tables/*.md` 전수**와 **본문 층 전수**를 이 벤더의 등급 토큰으로 따로 grep 했다. "
          "표 층 적중 **1건인데 거짓 양성**이다(광물명 `osumilite` 가 `Sumilite` 에 걸렸다). 본문 층 적중 35건은 "
          "전부 `Sumitomo Bakelite`/`住友` 를 소속·일반 EMC 공급사로 언급한 것이고 **이 등급들의 물성표는 0건**이다. "
          "72차 HD 의 「로컬 논문 코퍼스에 이 등급들의 물성표는 사실상 없다」가 **표 층까지 포함해 확정됐다.**")

def rows(doc_desc, inventory, extra=""):
    def f(key):
        return (HEAD + "이 재료의 벤더 문서를 전부 열었고 " + LBL[key] + " 행이 **없다.**\n\n" +
                doc_desc + "\n\n**그 표의 행 전수** — " + inventory + extra + SDS + CORPUS)
    return f

# ── ① ELC 両面 (2727~2730)
ELC_D = ("**연 문서 셋**\n"
 "- `" + P + "SumitomoBakelite_Sumilite_ELC_DoubleSided_CCL_Spec_ja_2026-09-09.html` — 벤더 사양 페이지. "
 "**토큰으로 훑지 않고 `<tr>`/`<td>` 를 직접 파싱해 37행을 셀 단위로 재구성했다**(72차 HD 가 같은 페이지에서 "
 "`引っ張り<br>強さ` 때문에 naive grep 거짓 음성을 밟은 자리다).\n"
 "- `" + P + "SumitomoBakelite_Sumilite-ELC_SpecList_ja_2026-09-09.pdf` — 『スミライト®ELC仕様一覧』 1쪽. "
 "**텍스트층이 2자뿐이라 130 dpi 로 렌더해 눈으로 읽었다.** HTML 과 행·값이 전부 일치한다(독립 교차검증).\n"
 "- `" + P + "SumitomoBakelite_ELC-DoubleSided_Catalog_ja_2026-09-09.pdf` — A3 2쪽 제품별 카탈로그. "
 "**아웃라인 벡터라 `pdftotext` 가 0자를 준다 — 150 dpi 렌더로 읽었다.** 여기는 두께(1.6/1.0 mmt)별로 열이 "
 "더 갈리는데 **행 구성은 같다.**")
ELC_INV = ("熱膨張係数(CTE X/Y/Z α1·Z α2) · ガラス転移温度(TMA/DMA/DSC) · はんだ耐熱(2조건) · 引き剥がし強さ(2조건) · "
 "曲げ強さ(タテ/ヨコ) · 曲げ弾性率(タテ/ヨコ) · 引っ張り強さ(タテ/ヨコ) · 引っ張り弾性率(タテ/ヨコ) · "
 "比誘電率(4) · 誘電正接(4) · 体積抵抗率(2) · 表面抵抗(2) · 吸水率 · 耐燃性 · 熱伝導率. "
 "**比重·密度·ポアソン比·比熱 은 이 표에 자리 자체가 없다.**")
ELC_X = ("\n\n**이 벤더가 적을 때는 적는다는 것이 같은 표 안에서 증명된다** — ELC 표는 `曲げ弾性率` 와 "
 "`引っ張り弾性率` 를 **행 이름으로 갈라** 인쇄하고 `引っ張り強さ` 도 따로 찍는다. "
 "그러므로 여기서 `比重`·`ポアソン比`·`比熱` 이 없는 것은 **표기 누락이 아니라 벤더가 재지 않거나 공개하지 "
 "않는다는 뜻**이다. 70차 FA·72차 HD 가 여섯 문서에서 같은 결론에 이르렀고, 74차 JB 가 세 문서로 다시 확인했다.")

# ── ② ELC 多層 (2731~2732)
ELCM_D = ("**연 문서 셋**\n"
 "- `" + P + "SumitomoBakelite_Sumilite_ELC_Multilayer_PWB_Spec_ja_2026-09-09.html` — 벤더 사양 페이지. "
 "`<tr>`/`<td>` 직접 파싱, 32행.\n"
 "- `" + P + "SumitomoBakelite_ELC-Multilayer_Catalog_ja_2026-09-09.pdf` — A3 1쪽. 아웃라인 벡터(0자) → "
 "150 dpi 렌더.\n"
 "- `" + P + "SumitomoBakelite_ELC-4765-4768_TDS_en_2026-09-09.pdf` — **영문 Technical Data Sheet 1쪽.** "
 "**이 문서는 텍스트층이 살아 있어(2,493자) 토큰 검사를 돌렸다** — `densit`·`gravity`·`Poisson`·`specific heat` "
 "**전부 0건**. 일문 사양과 행 구성·값이 완전히 같다.")
ELCM_INV = ("Coefficient of thermal expansion(X/Y/Z α1·Z α2) · Glass transition temperature(TMA/DMA/DSC) · "
 "Solder heat resistance(2) · Peel strength(2) · Flexural strength(MD/TD) · Flexural modulus(MD/TD) · "
 "Tensile strength(MD/TD) · Tensile modulus(MD/TD) · Dielectric constant(2) · Dissipation factor(2) · "
 "Volume resistivity(2) · Surface resistivity(2) · Water absorption · Flame resistance · Thermal conductivity. "
 "**Density·Poisson·Specific heat 행이 없다.**")

# ── ③ LAZ-4785 코어 (2750~2756)
LAZ_D = ("**연 문서 둘 — 하나는 이 배치가 오늘 라이브로 다시 읽었다**\n"
 "- `" + P + "SumitomoBakelite_LAZ-4785_PackageCore_Spec_ja_2026-09-09.html` — 71차 GD 가 13장을 세운 그 페이지. "
 "`<tr>`/`<td>` 를 `colspan`/`rowspan` 까지 직접 파싱해 17행을 셀 단위로 재구성했다.\n"
 "- **라이브 재독** `https://www.sumibe.co.jp/product/it-materials/package/core/` — **2026-09-13 에 직접 받아 "
 "같은 방식으로 파싱했다. 17행이 로컬 스냅샷(2026-09-09)과 완전히 같다 — 판 드리프트 0, 새 행 0.** "
 "72차 HD 가 Resonac 에서 밟은 「판이 셋인데 셋이 다 다르다」 함정을 이 벤더에서는 확인적으로 배제했다.")
LAZ_INV = ("特長 · 最薄/最厚の厚み(生産実績) · ガラスクロス番手 · 厚み(公称) · Tg(DMA) · CTE-1 xy(TMA 引張モード) · "
 "CTE-1 z · 弾性率(30 ℃ / 260 ℃) · Dk(1 GHz) · Df(1 GHz) · ピール強度(12LP銅箔) · 吸水率(D-24/23) · 熱伝導率. "
 "**比重·密度·ポアソン比·比熱·引っ張り強さ 는 이 표에 자리 자체가 없다.**")
LAZ_X = ("\n\n**있는 것은 `弾性率` 이지 `引っ張り強さ` 가 아니다.** 강성과 강도는 다른 물성이고, 이 표에는 "
 "**강도 행이 피ール강도(접착) 하나뿐**이다. 71차 GD 가 이 `弾性率` 를 **t3**(시험모드 미확정)로 둔 이유는 "
 "이 표가 인장/굽힘을 안 적기 때문인데, 그 판단은 74차 JB 의 라이브 재독에서도 유지된다 — "
 "세 페이지 전문에 `JIS`·`ASTM`·`IPC` 가 한 번도 안 나온다.")
LAZ_TC = ("\n\n**열전도율만은 「행이 없다」가 아니라 「행은 있는데 이 등급 칸이 `N.D.` 다」이다.** 원문 verbatim: "
 "`熱伝導率 | W/m・k | 0.7 | 0.7 | 0.7 | 0.6 | N.D. | N.D. | N.D.` — 앞 네 등급(TH-G·GH-G·TH-B·GS-BA)은 값이 "
 "인쇄돼 있고 **뒤 세 등급(GS-BE·GH-T·GS-W)은 `N.D.`(not determined)** 다. 같은 행의 형제 값을 이 칸에 "
 "옮기는 것은 지어내는 것이다. 라이브 페이지(2026-09-13)도 같은 `N.D.` 를 인쇄한다.")

# ── ④ LAZ 프리프레그 (2757~2761)
PRE_D = ("**연 문서 둘 — 하나는 이 배치가 오늘 라이브로 다시 읽었다**\n"
 "- `" + P + "SumitomoBakelite_LAZ-6785_Prepreg_Spec_ja_2026-09-09.html` — `<tr>`/`<td>` 직접 파싱, 13행.\n"
 "- **라이브 재독** `https://www.sumibe.co.jp/product/it-materials/package/prepreg/` — 2026-09-13 취득. "
 "**13행이 로컬 스냅샷과 완전히 같다.**")
PRE_INV = ("ガラスクロス(Type/#) · 厚み · Tg(DMA) · CTE-1(XY)(TMA 引張モード) · 弾性率(30 ℃ / 260 ℃) · "
 "Dk(1 GHz) · Df(1 GHz) · ピール強度 · 吸水率(D-24/23). "
 "**열 행뿐이고 比重·ポアソン比·比熱·引っ張り強さ 는 물론 `熱伝導率` 행조차 아예 없다** — "
 "형제 표인 코어(LAZ-4785)에는 `熱伝導率` 행이 있는데 프리프레그 표에는 그 행이 통째로 빠져 있다.")

# ── ⑤ LAZ-7752 SR (2762)
SR_D = ("**연 문서 둘 — 하나는 이 배치가 오늘 라이브로 다시 읽었다**\n"
 "- `" + P + "SumitomoBakelite_LAZ-7752_SolderResistAlt_Spec_ja_2026-09-09.html` — `<tr>`/`<td>` 직접 파싱, 12행.\n"
 "- **라이브 재독** `https://www.sumibe.co.jp/product/it-materials/package/sr/` — 2026-09-13 취득. "
 "**12행이 로컬 스냅샷과 완전히 같다.**")
SR_INV = ("特長 · 用途 · 厚み · Tg(DMA) · CTE-1(XY)(TMA 引張モード) · 弾性率(30 ℃ / 260 ℃) · Dk(1 GHz) · "
 "Df(1 GHz) · ピール強度(12umVLP銅箔) · 吸水率(D-24/23). "
 "**아홉 행뿐이다. `熱伝導率` 행이 없고 比重·ポアソン比·比熱·引っ張り強さ 도 없다.**")

# ── ⑥ BLα-3700GS 빌드업 (2799)
BU_D = ("**연 문서 하나 + 라이브 재확인**\n"
 "- `" + P + "SumitomoBakelite_LAZ-Buildup_Spec_ja_2026-09-09.html` — 72차 HD 가 Wayback 스냅샷에서 받아 둔 "
 "빌드업 사양 페이지. `<tr>`/`<td>` 직접 파싱, 11행.\n"
 "- **라이브 재확인(2026-09-13)** — `https://www.sumibe.co.jp/product/it-materials/package/buildup/` 는 "
 "**여전히 HTTP 404** 다. 그런데 부모 인덱스 `https://www.sumibe.co.jp/product/it-materials/` 는 "
 "**오늘도 이 링크를 걸고 있다**(형제 셋 `core/`·`prepreg/`·`sr/` 은 전부 200). 72차 HD 가 찾은 깨진 링크가 "
 "넉 달 뒤에도 안 고쳐졌다 — **이 페이지의 현행 원본은 세상에 없고 Wayback 스냅샷이 유일본이다.** "
 "HD 가 확인한 대로 스냅샷은 셋뿐이고(2019-11 · 2020-08 · 2021-08) 특성표가 세 판 바이트 동일이다.")
BU_INV = ("Tg(by DMA) · Tg(by TMA) · CTE1 · CTE2 · Tensile Modulus(R.T.) · Tensile Modulus(250 ℃) · "
 "Dielectric constant(1 GHz) · Dielectric Dissipation Factor(1 GHz) · Moisture Absorption. "
 "**아홉 행뿐이다. 比重·ポアソン比·熱伝導率·比熱·引っ張り強さ 가 없다.**")
BU_X = ("\n\n**있는 것은 `Tensile Modulus` 이지 `Tensile Strength` 가 아니다.** 이 페이지는 형제 셋과 달리 "
 "시험모드를 명시하는 유일한 쪽이라(72차 HD) 영률이 t1 인데, **강도 행은 여전히 없다** — "
 "모듈러스를 강도 칸으로 옮기는 것은 물성을 바꿔치기하는 것이다.")

# ── ⑦ PL/EL 무피복 적층판 (2800~2803)
PLEL_D = ("**연 문서 하나를 네 쪽 전부 렌더해 훑었다**\n"
 "- `" + P + "SumitomoBakelite_Sumilite-PL-EL_Catalog_ja_2026-09-09.pdf` — 72차 HD 가 比重 으로 이 카드를 "
 "세운 그 카탈로그다. **A3 4쪽(인쇄 25~32쪽) 전부 텍스트층이 0자인 아웃라인 벡터라 150 dpi 로 네 쪽을 "
 "모두 렌더해 눈으로 읽었다.** HD 는 값이 나온 두 쪽(인쇄 26·27)만 보고했는데, 74차 JB 는 **나머지 두 쪽까지 "
 "확인해 「이 카탈로그 어디에도 없다」를 확정했다.**")
PLEL_INV = ("**인쇄 26쪽 『電子部品用積層板(打抜き加工用)』** — 絶縁抵抗(2조건) · 曲げ強度 · 吸水率 · 加熱後外観 · "
 "**比重** · 耐燃性(UL法) · JIS積層板記号 · 納入サイズ. 여덟 행.\n"
 "**인쇄 27쪽 『機械・電気機器用積層板(機械加工用)』** — 貫層耐電圧 · 沿層耐電圧 · 絶縁抵抗(2조건) · 曲げ強度 · "
 "**アイゾット衝撃強さ** · **へき開強さ** · 吸水率 · 加熱後外観 · **比重** · 耐アセトン性 · 耐燃性 · "
 "JIS積層板記号 · 納入サイズ. 열세 행.\n"
 "**인쇄 28쪽** — 研磨キャリア(EL-3700/EL-3700M) 표, 이 등급들과 무관.  "
 "**인쇄 29·30쪽** — 鉄道車両用材料燃焼試験成績書(연소시험 성적서 사본).  "
 "**인쇄 31쪽** — 厚さ許容差(두께 허용차)만.  **인쇄 32쪽** — 試験方法/成形条件.\n\n"
 "**두 특성표 어디에도 탄성률 행이 없다** — 있는 강도는 `曲げ強度`(굽힘) · `アイゾット衝撃強さ`(충격) · "
 "`へき開強さ`(벽개)뿐이고 **인장은 강도도 탄성률도 없다.** CTE·熱伝導率·比熱·ポアソン比 행도 없다.")
PLEL_X = ("\n\n**같은 벤더의 형제 제품군이 대비를 준다** — 동장적층판 ELC 표는 `曲げ弾性率` 와 `引っ張り弾性率` 를 "
 "행 이름으로 갈라 인쇄하고 `熱伝導率` 도 찍는다. **무피복 PL/EL 표는 그 대신 `比重` 를 찍는다**(72차 HD 의 "
 "「동박을 붙이면 밀도 행이 사라진다」 규칙). 두 표가 서로 다른 축을 인쇄하는 것이고, **이 여섯 칸은 "
 "어느 쪽 표에도 없다.**")

GROUPS = [
 (range(2727, 2731), [K_PR, K_CP], rows(ELC_D, ELC_INV, ELC_X)),
 (range(2731, 2733), [K_PR, K_CP], rows(ELCM_D, ELCM_INV, ELC_X)),
 (range(2750, 2754), [K_DEN, K_PR, K_CP, K_TS], rows(LAZ_D, LAZ_INV, LAZ_X)),
 (range(2754, 2757), [K_DEN, K_PR, K_CP, K_TS], rows(LAZ_D, LAZ_INV, LAZ_X)),
 (range(2754, 2757), [K_TC], rows(LAZ_D, LAZ_INV, LAZ_TC)),
 (range(2757, 2762), [K_DEN, K_PR, K_TC, K_CP, K_TS], rows(PRE_D, PRE_INV, LAZ_X)),
 (range(2762, 2763), [K_DEN, K_PR, K_TC, K_CP, K_TS], rows(SR_D, SR_INV, LAZ_X)),
 (range(2799, 2800), [K_DEN, K_PR, K_TC, K_CP, K_TS], rows(BU_D, BU_INV, BU_X)),
 (range(2800, 2804), [K_YM, K_PR, K_CTE, K_TC, K_CP, K_TS], rows(PLEL_D, PLEL_INV, PLEL_X)),
]

def main():
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    names = {i: n for i, n in c.execute("select id,name from material")}
    have = collections.defaultdict(set)
    for m, k in c.execute("select distinct material_id,property_key from property_value"):
        have[m].add(k)
    out, skipped = collections.OrderedDict(), []
    for ids, keys, fn in GROUPS:
        for mid in ids:
            if mid not in names:
                skipped.append(("없는 재료", mid, "")); continue
            d = out.setdefault(mid, {"material_id": mid, "name": names[mid],
                                     "core_absent_from_vendor_sheet": {}})
            for k in keys:
                if k in have[mid]:            # 값이 이미 있으면 판정하지 않는다
                    skipped.append(("이미 값이 있다", mid, k)); continue
                d["core_absent_from_vendor_sheet"][k] = fn(k)
    v = [d for d in out.values() if d["core_absent_from_vendor_sheet"]]
    json.dump({"batch": "74차 JB", "verdicts": v},
              open(os.path.join(OUT, "jb74_03_verdicts.json"), "w"), ensure_ascii=False, indent=1)
    print("판정 재료", len(v), "· 칸", sum(len(d["core_absent_from_vendor_sheet"]) for d in v))
    for s in skipped: print("  건너뜀:", s)

main()
