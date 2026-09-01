#!/usr/bin/env python3
# 58차 TC 의 코어 빈칸 판정 JSON 을 만든다 — 사유 문장이 여기 산다.
# 규율: 한 재료는 반드시 한 행이다(브리프 610 — apply_core_verdicts 가 attributes 를 한 번만 캐시한다).
import json

VEND = "core_absent_from_vendor_sheet"   # V2 — 문서를 열어 그 열이 없음을 확인했다
REJ  = "core_rejected_printed_value"     # V6 — 문서에 값이 있는데 검산에서 죽었다

# ── 공통 사유 조각 ────────────────────────────────────────────────────────────
UF_GENRE = (
    "그리고 이것은 언더필 갈래의 구조적 부재다 — 58차 TC 가 플립칩 언더필 벤더 시트 20장을 "
    "실제로 열어 전권 낱말검색을 걸었다(NAMICS U8443-14 · NAMICS 플립칩 UF 선택표 12등급 · "
    "NAMICS Product Guide 2015 · Henkel LOCTITE ECCOBOND UF3800/UF3808/UF3810/UF1173/FP4549/E-1216M · "
    "Zymet X6-82-5LV/CN-1432/CN-1453/CN-1703/CN-1735/SMTAi2013 · Master Bond EP3UF/EP3UF-1/"
    "Supreme 3HTND-2GT/EP30LV-1). `Poisson` 0/20 · `specific heat` 0/20 · 인장강도 0/20 이다. "
    "이 갈래가 강도축으로 인쇄하는 것은 굽힘강도와 다이전단·랩전단이다(브리프 613 의 재현). "
    "Chhanda 2012 가 적은 'underfill mechanical property data are scarce on vendor datasheets' 를 "
    "권위로 받지 않고 20장으로 검산한 결과다."
)
UF_RHO_K = (
    "다만 밀도와 열전도율은 갈래 차원의 부재가 아니다 — Henkel 6장 중 5장이 비중을, "
    "NAMICS U8443-14 와 Henkel UF3810·E-1216M 이 열전도율을 인쇄한다. "
    "이 재료에서 비어 있는 이유는 갈래가 아니라 **이 등급에 붙일 벤더 문서가 없다는 것**이다."
)
NAMICS_LEAD = (
    "조달 기록 — `lamics.co.jp` 는 NXDOMAIN 이고 Wayback CDX 에 캡처가 0건이다(도메인·서브도메인 전수). "
    "반면 NAMICS(니가타, 일본) 자사 Product Guide 2015 의 플립칩 언더필 선택표가 `U8437-2`(Tg 137 C · "
    "탄성률 8.0 GPa · CTE 32/100 ppm)와 `U8437-48`(Tg 145 · 7.0 GPa · 33/100)을 싣는다. "
    "**원문의 'Lamics' 는 NAMICS 의 오기일 가능성이 높다 — 그러나 확정하지 않았고 등급도 빌리지 않았다**"
    "(브리프 22·123·140·586). `-3` 접미 등급은 어느 NAMICS 문서에도 없고 NAMICS 는 U8437 계열 TDS 를 "
    "웹에 올린 적이 없다(namics.co.jp 전 PDF CDX 에 제품 TDS 0건). "
    "그리고 등급을 빌리면 안 된다는 증거가 값 자체에 있다 — 제3자 교육자료가 전재한 `Namics U8437-2` 표는 "
    "밀도 1.6 · 영률 7.0 GPa · 포아송비 0.33 · 열전도율 0.67 W/mK 인데, 이 재료의 원문 인쇄 영률은 9 GPa 라 "
    "22% 어긋난다. 다른 등급이다."
)
UF_SRC_KP = ("출처 Kaltenpoth 2001(Soldering & Surface Mount Technology, DOI 10.1108/eum0000000006024) "
             "Table I 'Mechanical properties of the underfill material U-8437-3 from Lamics, Japan' 은 "
             "Tg(TMA)·CTE(T<Tg)·CTE(T>Tg)·Young's modulus·Adhesion strength **다섯 열뿐**이다. "
             "md 와 pdftotext 가 같고 카탈로그는 그 다섯을 이미 다 가지고 있다. "
             "로컬 사본 — /data/paper_patent_corpus/structured/materials_papers/pkg_underfill_material/"
             "Kaltenpoth - 2001 - .../*.md (출처 행의 local_path 가 비어 있을 뿐 코퍼스에 있다).")
UF_SRC_QUN = ("출처 Qun 2000(같은 저널 12(3) 24-28, DOI 10.1108/09540910010347863) Table I "
              "'Mechanical properties of the underfill' 은 Tg(K)(TMA)·CTE(<Tg)·CTE(>Tg)·Young's modulus·"
              "Apparent adhesion strength **다섯 열뿐**이다. "
              "로컬 사본 — /data/paper_patent_corpus/structured/snowball_papers/from_pkg/"
              "Qun - 2000 - On the degradation of the solder joints of underfilled flip chip packages_ a case study/*.md.")
UF_TWIN = ("**그리고 이 표는 재료 1352 의 표와 같은 표다**(브리프 586·620) — 408 / 26 / 110 / 9.0 / 75 로 "
           "다섯 칸이 전부 같고 각주 '300N pull force on a 2mm x 2mm chip' 까지 글자 단위로 같다. "
           "두 논문은 같은 회사(DaimlerChrysler SIM Technology, 상하이) 소속이고 Xie Xiaoming 이 공저자로 겹치며 "
           "Kaltenpoth 2001 이 본문에서 'Zhang et al., 2000' 을 인용한다. Kaltenpoth 판만 재료명을 "
           "'U-8437-3 from Lamics, Japan' 으로 밝힌다 — 즉 이 재료의 정체는 1352 와 같은 언더필이다. "
           "**재료를 합치지 않았다(삭제·병합은 이 배치의 권한이 아니다). 조정자가 판단할 중복 신고다.**")
UF_KAT = ("출처 Katsurayama 2008(JSMME 2(8) 987-998, DOI 10.1299/jmmp.2.987) Table 3 "
          "'Physical properties of UF materials used' 의 행은 material name·feature·filler content·"
          "viscosity·Tg·alpha1·alpha2·Young's modulus·application **여덟뿐**이고 카탈로그는 그것을 이미 다 가지고 있다"
          "(alpha2 두 칸은 앞 배치가 자릿수 충돌로 기각했다). 같은 표에 밀도·포아송비·열전도율·비열·인장강도 행이 없다. "
          "같은 연구실의 자매 논문도 확인했다 — Katsurayama 2007 은 다른 등급(충전 50%)이고, "
          "Katsurayama 2013 의 UF1/UF2/UF3 는 충전 0/50/60% 로 이 셋(65/60/0%)과 다른 세트이며, "
          "2013 의 Table II 에 인쇄된 포아송비는 Si 칩·Cu·솔더레지스트·패시베이션 것이지 언더필 것이 아니다. "
          "로컬 사본 — /data/paper_patent_corpus/structured/pkg_papers/11_mold_warpage_cpi/"
          "KATSURAYAMA - 2008 - Reliability Evaluation of Warpage of Flip Chip Package with Some Kinds of Underfill Material/*.md. "
          "**그리고 이 셋은 성격상 V4(등급 미확정)다** — 저자가 공급사와 상품명을 가리고 CUF-1/NUF-2/NUF-3 으로만 "
          "인쇄해 어느 벤더 시트도 붙일 수 없다(브리프 608 대로 전파되는 이 칸에 적는다).")
KAT1_FE = ("같은 논문 Table 1 'Physical properties used for FE analysis' 의 UF 행이 "
           "`Young's modulus = Arbitrary data (10 types)` · `CTE = 2.3e-5` · `Poisson's ratio = 0.3` 을 인쇄하지만 "
           "**이 셋의 값이 아니다** — 저자가 E 를 0.313~640 GPa 로 10단계 훑는 매개변수 연구용 가상 UF 행이고 "
           "E 칸이 'Arbitrary data' 라고 스스로 밝힌다. 포아송비 0.3 은 브리프 3번이 지목한 관용값 2자리다. "
           "옮기면 우리 가정을 남의 인쇄값으로 세탁하는 것이다.")

def uf_common(extra=""):
    return {
        "physical.density": "V2 " + extra,
        "mechanical.poisson_ratio": "V2 " + extra,
        "thermal.conductivity": "V2 " + extra,
        "thermal.specific_heat": "V2 " + extra,
        "mechanical.tensile_strength": "V2 " + extra,
    }

IMC_THERMAL_ABSENT = {666: (
 "[58차 TC] V2 — 유일 출처 Kouters 2013 은 5절에서 verbatim 'We were able to prepare three usable samples of "
 "intermetallics for thermal conductivity measurement: CuAl, Cu3Al2 and Cu9Al4' 라고 밝히고 Table 5 도 그 세 상만 싣는다. "
 "즉 이 상의 비열·열전도율은 **시편을 못 만들어 재지 못한 것**이다. "
 "**대체 출처를 실제로 열었고, 열어서 안 쓰기로 판정했다** — Nazarahari et al. 2026(Adv. Eng. Mater. 28, e202501357, "
 "CC-BY, 로컬 사본 /home/koopark/claude/MaterialTwinWeb/.agent_work/w58tc/imc/nazarahari2026.pdf) Table 3 이 "
 "다섯 상의 확산율·비열·열전도율을 싣고, 그 `Zeta` 행의 명목 조성 Cu 56.10 at% 는 Kouters Table 1 이 인쇄한 "
 "Cu4Al3 구간(55.2~56.3 at%) 안에 정확히 든다. **그런데 두 가지가 막는다.** "
 "① **그 논문은 이 상을 Cu4Al3 라 부르지 않는다** — Table 1 의 상 열은 그리스문자 `ζ2` 뿐이고 본문은 "
 "'ζ2 (Al9Cu11.5)' 로 인쇄한다. ② **다섯 시편 중 그것만 단상이 아니다** — 결과절 verbatim 'These evidence that, "
 "except for the Zeta sample, all other samples feature a single phase' 와 'the coexistence of ζ1 and η2 phases "
 "in cast samples', 초록 verbatim 'evidenced the precipitation of secondary phases in the ζ2 and θ samples'. "
 "즉 Zeta 행(확산율 23.5 mm2/s · 비열 0.433 J/gK · 열전도율 57.6 W/mK)은 ζ1+η2 **이상혼합 시편**의 값이지 "
 "Cu4Al3 단상의 값이 아니다. 조성이 겹친다고 옮기면 브리프 123·140 위반이다. "
 "**같은 표의 Theta 행은 옮겼다** — 그쪽은 본문이 'Al2Cu (θ)' 로 상을 명시하고 밀도 4.23 이 카탈로그의 "
 "Kouters 실측 4.27 과 0.9% 안이라 동정이 닫힌다(재료 664). "
 "**이 칸은 새 1차 출처가 나와야 열린다 — 벤더 부재가 아니다.**"
)}

V = []

# ── 언더필 5종 25칸 ───────────────────────────────────────────────────────────
for mid, name, head in [
    (1352, "Flip-chip underfill U-8437-3 (Lamics)", UF_SRC_KP + " " + NAMICS_LEAD),
    (1369, "Flip-chip capillary underfill (Qun 2000)", UF_SRC_QUN + " " + UF_TWIN + " " + NAMICS_LEAD),
]:
    d = {}
    for k in ("physical.density", "mechanical.poisson_ratio", "thermal.conductivity",
              "thermal.specific_heat", "mechanical.tensile_strength"):
        s = f"[58차 TC] {head}"
        if k in ("mechanical.poisson_ratio", "thermal.specific_heat", "mechanical.tensile_strength"):
            s += " " + UF_GENRE
        else:
            s += " " + UF_GENRE + " " + UF_RHO_K
        d[k] = s
    V.append({"material_id": mid, "name": name, VEND: d})

for mid, name in [(1676, "Underfill CUF-1 (Katsurayama 2008)"),
                  (1677, "Underfill NUF-2 (Katsurayama 2008)"),
                  (1678, "Underfill NUF-3 (Katsurayama 2008)")]:
    d = {}
    for k in ("physical.density", "mechanical.poisson_ratio", "thermal.conductivity",
              "thermal.specific_heat", "mechanical.tensile_strength"):
        s = f"[58차 TC] {UF_KAT} {UF_GENRE}"
        if k == "mechanical.poisson_ratio":
            s += " " + KAT1_FE
        if k in ("physical.density", "thermal.conductivity"):
            s += " " + UF_RHO_K
        d[k] = s
    V.append({"material_id": mid, "name": name, VEND: d})

# ── EMC 3종 16칸 ─────────────────────────────────────────────────────────────
EMC_V4 = ("**성격상 V4(등급 미확정)다** — 논문이 벤더도 상품명도 인쇄하지 않아 어느 EMC 벤더 시트도 "
          "붙일 수 없다. V4 를 정하는 `identification_status` 는 병합기의 CURATION 전파 목록 밖이라 "
          "운영에 안 가므로 전파되는 이 칸에 적는다(브리프 608 · 57차 SA 선례).")
CHIU2020 = ("[58차 TC] V2 — 유일 출처 Chiu 2020(ECTC, DOI 10.1109/ECTC32862.2020.00193)을 전권으로 열었다. "
            "표는 TABLE I(흡습·탈습 확산계수와 포화흡습률) · TABLE II(Arrhenius 상수) · TABLE III(포화흡습 모델 상수) "
            "**셋뿐**이고 카탈로그는 그 24행을 이미 다 가지고 있다. 역학·열물성 표가 아예 없다. "
            "식 (1)의 DCB 해에 E 와 nu 가 기호로 들어가지만 EMC 의 수치는 인쇄되지 않고, 4장의 FE 절도 "
            "'all packaging constiuents are assumed to be elastic with temperature-dependent properties' 라고만 적고 표를 싣지 않는다. "
            "밀도는 단독으로 인쇄되지 않는다 — 본문이 흡습팽창계수와의 곱으로 `beta*rho = 0.304` 만 준다(분리 불가). "
            "로컬 사본 — /data/paper_patent_corpus/structured/rel_papers/23_moisture_sensitivity/"
            "Chiu - 2020 - A Mechanics Model for the Moisture Induced Delamination in Fan-Out Wafer-Level Package/*.md. " + EMC_V4)
CHIU739 = ("[58차 TC] V2 — 출처 둘을 다 열었다. Chiu 2009(InterPACK, DOI 10.1115/interpack2009-89040) 의 표는 "
           "Table 1·2(경화속도 상수) · Table 3(칩스케일 BGA 재료상수 — E(T)·nu·CTE(T)) · Prony 21항 표뿐이고, "
           "Chiu 2011(IEEE TDMR 11(2) 339-347) 의 표는 TABLE I~V(경화속도·화학수축·CTE·일반화 맥스웰·시간-경화 이동)뿐이다. "
           "두 논문 어디에도 밀도·열전도율·비열·인장강도 행이 없다. 단축인장시험은 했지만 인쇄한 것은 "
           "탄성계수(유리상 E0 = 32 GPa)이고 파단강도가 아니다. "
           "로컬 사본 — Chiu 2009: /data/paper_patent_corpus/structured/pkg_papers/11_mold_warpage_cpi/Chiu - 2009 - .../*.md · "
           "Chiu 2011: /data/paper_patent_corpus/structured/snowball_papers/from_cae/Tz-Cheng Chiu - 2011 - .../*.md "
           "(두 출처 행 모두 local_path 가 비어 있지만 코퍼스에 있다). " + EMC_V4)
LAU1368 = ("[58차 TC] V2 — 유일 출처 Lau 2018(IWLPC, DOI 10.23919/iwlpc.2018.8573284) Table 1 "
           "'Material property of the dry-film EMC' 는 Tg(DMA) · Tg(TMA) · CTE 세 구간 · Young's Modulus · "
           "Elongation · Poisson's Ratio **여덟 행뿐**이고 카탈로그는 그 여덟을 이미 다 가지고 있다. "
           "밀도·열전도율·비열·인장강도 행이 없다. 같은 저자의 Lau 2019(Recent Advances and Trends in "
           "Fan-Out Wafer/Panel-Level Packaging) Table I 도 확인했으나 그쪽 EMC 는 CTE 10 ppm/C · E 19 GPa · nu 0.25 로 "
           "**이 건식필름 EMC(CTE 7 · E 7 GPa)와 다른 재료**라 빌리지 않았다(브리프 123·140). "
           "로컬 사본 — /data/paper_patent_corpus/structured/smartphone_pcb/27_panel_level_packaging/"
           "Lau - 2018 - Redistribution-Layers (RDLS) for Fan-Out Panel-Level Packaging/*.md. " + EMC_V4)

V.append({"material_id": 964, "name": "Silica-filled liquid EMC for fan-out WLP (Chiu 2020)",
          VEND: {k: CHIU2020 for k in ("physical.density", "mechanical.youngs_modulus",
                                       "mechanical.poisson_ratio", "thermal.expansion_linear",
                                       "thermal.conductivity", "thermal.specific_heat",
                                       "mechanical.tensile_strength")}})
V.append({"material_id": 739, "name": "Epoxy molding compound (Chiu 2009/2011)",
          VEND: {k: CHIU739 for k in ("physical.density", "thermal.conductivity",
                                      "thermal.specific_heat", "mechanical.tensile_strength")}})
V.append({"material_id": 1368, "name": "Dry-film EMC for FOPLP (Lau 2018)",
          VEND: {k: LAU1368 for k in ("physical.density", "thermal.conductivity",
                                      "thermal.specific_heat", "mechanical.tensile_strength")}})


# ── Cu-Al 금속간화합물 5종 ────────────────────────────────────────────────────
IMC_UTS = (
 "[58차 TC] Kouters 2013(Microelectron. Reliab. 53:1068)은 인장시험을 하지 않는다 — "
 "압입경도(Table 3) · 압입영률(Table 2) · 압입파괴인성(Table 4) · 아르키메데스 밀도(Table 4) · "
 "MDSC 비열과 플래시 열확산율(Table 5)뿐이고 Table 6 요약표에도 강도축이 없다. "
 "**본문이 1차 출처를 지목한다** — verbatim 'Rabkin et al. [10] presented the micro-hardness, tensile strength, "
 "electrical resistivity and coefficient of linear expansion of the intermetallic phases in the CuAl system.' "
 "[10] = Rabkin D.M., Ryabov V.R., Lozovskaya A.V., Dovzhenko V.A., Powder Metall. Met. Ceram. 9:695-700 (1970), "
 "DOI 10.1007/BF00803820 (Poroshkovaya Metallurgiya No.8(92) 1970 pp.101-107 의 영역본). "
 "**58차 TC 가 조달을 시도해 실패했다** — Springer 유료(초록조차 비공개), Unpaywall `oa_status=closed` · "
 "`oa_locations=[]`, OpenAlex `best_oa_location=null`, Semantic Scholar CLOSED, CORE 0건. "
 "또 다른 후보 Wulff & Breach(IEEE EPTC 2004 p.348)도 IEEE 유료다. "
 "**따라서 이 칸은 '벤더가 안 찍는다'가 아니라 '1차 문서를 아직 못 구했다'이다**(브리프 609 의 "
 "`core_no_public_document` 성격 — 그 칸은 집계가 못 읽으므로 전파되는 이 칸에 적고 사유에 못박는다). "
 "다음 파동이 Rabkin 1970 을 도서관 경유로 조달하면 다섯 상의 인장강도가 한꺼번에 열린다. "
 "대신 연 두 문헌은 값을 주지 않았다 — Xiao et al. 2020(J. Alloys Compd. 822:153536, green OA)은 "
 "네 상의 임계응력확대계수를 'within a similar magnitude, 1.4-3.1 MPa sqrt(m)' 구간으로만 인쇄하고"
 "(브리프 616 — 범위만 인쇄된 값은 부재다) 상별 수치는 전부 그림 안이며, "
 "Nazarahari et al. 2026(Adv. Eng. Mater., DOI 10.1002/adem.202501357, CC-BY)은 열물성만 싣는다."
)
IMC_E665 = (
 "[58차 TC] V6 — Kouters 2013 Table 2 'UNAT measurements for the indentation Young's moduli' 는 다섯 상 머리글"
 "(CuAl2 Theta · CuAl eta · Cu4Al3 zeta · Cu3Al2 delta · Cu9Al4 gamma)에 **네 값만** 인쇄한다"
 "(123.5±6.6 · 180.2±12.5 · 174.4±19.5 · 186.8±9.0). 400 dpi 렌더로 보면 180.2 가 CuAl 열과 Cu4Al3 열 사이에 "
 "걸쳐 있어 **표만으로는 어느 열이 빈칸인지 안 갈린다.** 심판은 본문 세 문장이다 — "
 "(1) 3.1절 verbatim 'The thinnest intermetallic layer CuAl was too thin to be measured (1 lm)', "
 "(2) Fig.6 캡션 verbatim 'The CuAl layer is too thin to discriminate it from the adjacent layers', "
 "(3) 3.3절 verbatim 'As the indentation Young's modulus of CuAl was not measured, in this case the value of "
 "Cu4Al3 was taken'. 즉 빈칸이 CuAl 이고 180.2 는 Cu4Al3 것이다(52차 NA 의 열 배정이 옳았음을 재확인했다). "
 "**그런데 Table 6 요약표는 CuAl 열과 Cu4Al3 열에 둘 다 180.2±12.5 를 인쇄한다** — 그것은 저자가 3.3절에서 "
 "밝힌 대입값이지 CuAl 의 측정값이 아니므로 인쇄돼 있으나 기각한다. "
 "그리고 이 논문의 영률은 전부 **압입탄성률**이고 저자가 포아송비 0.30 을 가정해 산출했다(2절 명시) — "
 "벌크 영률로 옮기는 것은 별개 문제다."
)
IMC_NU665 = (
 "[58차 TC] V2 — 이 논문의 포아송비는 측정값이 아니라 나노인덴테이션 환산에 쓴 **저자 가정 0.30** 이다(2절 명시). "
 "CuAl 은 층이 약 1 um 라 압입 자체를 못 했으므로(3.1절) 그 가정이 이 상에 적용된 적이 없다 — "
 "형제 네 상(664·666·667·668)에 t4 0.30 이 있는데 이 상만 비어 있는 이유가 그것이고, "
 "브리프 612 대로 갈린 칸에 사유를 박아 둔다. 그리고 포아송비는 브리프 6 이 표적에서 내린 물성이며 "
 "'측정법이 명시된 것만 넣는다'는 예외에도 해당하지 않는다. Kouters Table 1 의 편찬표에도 포아송비 열이 없다."
)

IMC_NAMES = {664: "CuAl2 (theta) Cu-Al IMC", 665: "CuAl (eta) Cu-Al IMC",
             666: "Cu4Al3 (zeta) Cu-Al IMC", 667: "Cu3Al2 (delta) Cu-Al IMC",
             668: "Cu9Al4 (gamma2) Cu-Al IMC"}
for mid in (664, 665, 666, 667, 668):
    row = {"material_id": mid, "name": IMC_NAMES[mid],
           VEND: {"mechanical.tensile_strength": IMC_UTS}}
    if mid == 665:
        row[VEND]["mechanical.poisson_ratio"] = IMC_NU665
        row[REJ] = {"mechanical.youngs_modulus": IMC_E665}
    if mid in IMC_THERMAL_ABSENT:
        row[VEND]["thermal.conductivity"] = IMC_THERMAL_ABSENT[mid]
        row[VEND]["thermal.specific_heat"] = IMC_THERMAL_ABSENT[mid]
    V.append(row)

json.dump({"batch": "58차 TC", "verdicts": V},
          open("tc02_core_verdicts.json", "w"), ensure_ascii=False, indent=1)
print("재료", len(V), "· 칸", sum(len(r.get(VEND, {})) + len(r.get(REJ, {})) for r in V))
