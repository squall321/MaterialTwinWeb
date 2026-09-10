# Kenner 1995 Fig.2 마스터커브 3벌 → mechanical.relaxation_modulus JSON 생성기
# (좌표는 scratchpad 의 ic73_extract.py 가 900 dpi 렌더에서 뽑은 값을 리터럴로 박았다)
import json, math

SRC = {
    "kind": "journal",
    "title": ("Viscoelastic Characterization of an Epoxy-Based Molding Compound "
              "(MRS Proceedings 390, 97-102, 1995)"),
    "doi": "10.1557/proc-390-97",
    "url": "https://doi.org/10.1557/proc-390-97",
    "year": 1995,
    "authors": "V. H. Kenner, M. R. Julian, C. H. Popelar, M. K. Chengalva",
    "publisher": "Materials Research Society",
    "local_path": ("/data/paper_patent_corpus/pkg_papers/10_emc_filler_lowstress/"
                   "Kenner - 1995 - Viscoelastic Characterization of an Epoxy-Based Molding Compound.pdf"),
}

MAT = ("Epoxy molding compound MP7100 (silica-filled epoxy, Tg 110 C, "
       "Nitto-Denko, Kenner 1995 OSU)")

# --- Fig.2 판독값: {변형률: [(log t, log10 E[MPa]), ...]} ---
FIG2 = {
 0.25: [(-9,4.3246),(-8,4.3249),(-7,4.3252),(-6,4.3162),(-5,4.3072),(-4,4.2888),
        (-3,4.2756),(-2,4.2573),(-1,4.2213),(0,4.1687),(1,4.1005),(2,3.9920),
        (3,3.8533),(4,3.6825),(5,3.4983),(6,3.3586),(7,3.2335),(8,3.1395),(9,3.0777)],
 0.5:  [(-9,4.2312),(-8,4.2273),(-7,4.2225),(-6,4.2051),(-5,4.1806),(-4,4.1487),
        (-3,4.1065),(-2,4.0674),(-1,4.0138),(0,3.9394),(1,3.8609),(2,3.7586),
        (3,3.6459),(4,3.5031),(5,3.3261),(6,3.2052),(7,3.1091),(8,3.0441),(9,2.9885)],
 1.0:  [(0,3.4726),(1,3.4730),(2,3.4692),(3,3.4301),(4,3.3060),(5,3.1778),
        (6,3.0620),(7,2.9878),(8,2.9342),(9,2.8890),(10,2.8375)],
}
# 원문이 인쇄한 영시간계수(Prony 적합) — 곡선 좌측 끝의 검산 앵커
ZERO_TIME_MPA = {0.25: 21.4e3, 0.5: 17.3e3, 1.0: 3.0e3}
# 곡선이 실제로 시작하는 환산시간(밴드 좌측 끝)
LEFT_END_LOGT = {0.25: -9.28, 0.5: -9.31, 1.0: -0.26}

COMMON = {
    "temperature_c": 100,
    "reference_temperature_c": 100,
    "relaxation_mode": "tensile",
    "curve_type": "master_curve",
    "reference_temperature_printed": True,
}

AXIS = ("Fig.2 축 좌표계 — 가로 `Log t (sec)` 환산시간 -10~15(주눈금 6개 검출, 직선회귀 잔차 최대 0.21 px), "
        "세로 `Log E (MPa)` 2.5~5.0(주눈금 6개, 잔차 최대 2.6 px = 0.005 decade). "
        "900 dpi 렌더에서 곡선 밴드(실선 + Prony 적합 원형 마커)의 상·하 끝 중점을 곡선값으로 잡았다 — "
        "마커가 곡선 위에 중심을 두므로 밴드 중심이 곡선이다. "
        "판독틀은 상·하 프레임선을 x 마다 재어 기울어짐(1400 px 에 4 px)을 보정했다.")

props = []
for strain, pts in FIG2.items():
    zt = ZERO_TIME_MPA[strain]
    for lt, le in pts:
        E_pa = (10.0 ** le) * 1e6
        note = (
            f"Kenner 1995 Fig.2 `Master Stress Relaxation Curves for MP7100 Molding Compound at 100 C` "
            f"의 세 마스터커브 중 원문이 `e_o = {strain}%` 로 표기한 곡선을 디지타이즈. "
            f"판독값 log10(E/MPa) = {le:.4f} → E = {10**le:.1f} MPa = {E_pa:.4g} Pa, "
            f"환산시간 log t = {lt:+d} → t = {10.0**lt:.6g} s. "
            + AXIS + " "
            f"검산① 원문 본문이 인쇄한 이 곡선의 영시간계수 = {zt:.6g} MPa "
            f"(log10 = {math.log10(zt):.4f}); 곡선 좌측 끝(log t = {LEFT_END_LOGT[strain]:.2f})에서 "
            f"우리 판독값과의 차이는 세 곡선 각각 -1.3 / -1.6 / -1.0 % 다(원문이 밝힌 완화계수 정확도는 +-4 %). "
            f"검산② 이 문서 Fig.1(0.5 % 변형률 등온 완화곡선)의 100 C 곡선을 따로 디지타이즈해 "
            f"0.5 % 마스터커브와 대조했다 — 기준온도가 100 C 이므로 a_T = 1 이라 둘이 같아야 한다. "
            f"log t = 1/1.5/2/2.5/3/3.5 에서 차이 0.014/0.012/0.022/0.030/0.040/0.031 decade 로 일치한다. "
            f"이 곡선은 시간-온도 중첩으로 조립한 마스터커브다(원문: `all shifting was arbitrarily effected "
            f"relative to the 100 C relaxation curve`) — 기준온도 100 C 가 그림 표제에 인쇄돼 있다. "
            f"E(0) 절대값은 별도 행(time_s = 0)으로 넣었다."
        )
        props.append({
            "key": "mechanical.relaxation_modulus", "value": E_pa, "unit": "Pa",
            "method": "digitized", "tier": 1,
            "conditions": {**COMMON, "time_s": 10.0 ** lt, "strain_pct": strain,
                           "reduced_time": True, "log10_time_s_printed_axis": lt},
            "notes": note,
        })

# 원문이 본문에 인쇄한 영시간계수 3개 (Prony 적합에서 나온 값이므로 computed / tier2)
for strain, zt in ZERO_TIME_MPA.items():
    props.append({
        "key": "mechanical.relaxation_modulus", "value": zt * 1e6, "unit": "Pa",
        "method": "computed", "tier": 2,
        "conditions": {**COMMON, "time_s": 0.0, "strain_pct": strain,
                       "reduced_time": True, "value_kind": "zero_time_modulus_of_prony_fit"},
        "notes": (
            f"원문 본문 verbatim — `the zero-time modulus associated with the Prony fit of the 0.25% "
            f"relaxation curve, 21.4 x 10^3 MPa, compares to an initial modulus of 21.8 x 10^3 MPa observed "
            f"in a constant strain rate tensile test ... The zero-time relaxation moduli values for the Prony "
            f"fits to the 0.5% and 1.0% relaxation curves are 17.3 x 10^3 MPa and 3.0 x 10^3 MPa, "
            f"respectively.` 이 행은 e_o = {strain}% 곡선의 값 {zt:.6g} MPa = {zt*1e6:.4g} Pa 다. "
            f"**인쇄된 절대값이지만 Prony 적합의 t->0 극한이라 measured 가 아니라 computed 로 적는다.** "
            f"원문 자신이 이 값을 `데이터의 단시간 절단(short-time truncation)` 때문에 실제 순간계수보다 "
            f"낮다고 밝힌다 — 특히 1.0 % 곡선은 환산시간 log t = -0.26 에서야 시작한다. "
            f"이 세 값이 Fig.2 좌측 끝 판독의 검산 앵커다(차이 -1.3 / -1.6 / -1.0 %)."
        ),
    })

# 원문이 인쇄한 정속변형률 인장시험 초기기울기 2개
for T_c, E_mpa in [(24, 21.8e3), (150, 1.4e3)]:
    props.append({
        "key": "mechanical.youngs_modulus_at_rate", "value": E_mpa * 1e6, "unit": "Pa",
        "method": "measured", "tier": 1,
        "conditions": {"temperature_c": T_c, "strain_rate_s": 1e-4,
                       "test_standard": "ASTM D638-91 type IV"},
        "notes": (
            f"원문 본문 verbatim — `the initial slope of the stress-strain curve for 24 C and a strain rate "
            f"of 10-4 s-1 is 21.8x10 3 MPa; at a temperature of 150 C and the same strain rate, the initial "
            f"slope of the stress-strain curve is l.4x103 MPa.`(Fig.4). 이 행은 {T_c} C · 1e-4 /s 의 "
            f"{E_mpa:.6g} MPa = {E_mpa*1e6:.4g} Pa 다. 시편은 ASTM D638-91 type IV 도그본, "
            f"시험부 6.35 x 3.18 mm, 175 C 5 h 후경화. **Fig.4 를 디지타이즈한 것이 아니라 본문 인쇄값이다.**"
        ),
    })

# 원문이 인쇄한 Tg
props.append({
    "key": "thermal.glass_transition", "value": 110.0 + 273.15, "unit": "K",
    "method": "estimated", "tier": 2,
    "conditions": {"determined_from": "relaxation_modulus_vs_temperature_at_100_s",
                   "value_printed_c": 110},
    "notes": (
        "원문 verbatim — `It is observed from Figure 1 by examining the relaxation modulus as a function of "
        "temperature at a given time (e.g., at 100 s) that the greatest rate of change with respect to "
        "temperature occurs at approximately 110 C. This was taken to give an estimate of the glass "
        "transition temperature for the molding compound.` Fig.3 이 `T = Tg = 110 C` 로 축 위에 다시 "
        "인쇄한다. 110 C = 383.15 K. **DSC/TMA 가 아니라 완화곡선의 온도의존성에서 읽은 값이라 "
        "원문이 스스로 `estimate` 라 부른다 — 그래서 tier 2 다.**"
    ),
})

doc = {"batch": "73차 IC", "materials": [{
    "match_name": MAT,
    "new_material": {"name": MAT, "category": "composite", "attributes": {
        "role": "evidence",
        "manufacturer_printed_verbatim": "Nitto-Dinko",
        "manufacturer_note": ("원문은 `manufactured by Nitto-Dinko` 라 인쇄한다 — Nitto-Denko(닛토덴코)의 "
                              "오식으로 보고 재료명에는 Nitto-Denko 를 쓰되 인쇄 철자를 여기 그대로 남긴다. "
                              "우리가 값을 고친 것이 아니라 제조사 표기를 기록한 것이다."),
        "grade": "MP7100",
        "composition_printed": "epoxy-based, highly filled with silica particles (further details not available)",
        "post_mold_cure": "175 C, 5 h",
        "specimen": "ASTM D638-91 type IV dog bone, 6.35 x 3.18 mm gage section, supplied by Intel",
        "notes": ("Kenner 1995(MRS Proc. 390, 97-102) 의 비선형 점탄성 특성화 대상. "
                  "응력완화 3벌(0.25/0.5/1.0 % 변형률, 24~150 C)과 정속변형률 인장(1e-4/1e-5/1e-6 /s). "
                  "완화계수가 변형률에 의존한다 — 즉 비선형 점탄성이다."),
    }},
    "source": SRC,
    "properties": props,
}]}

with open("/home/koopark/claude/MaterialTwinWeb/backend/scripts/catalog/out_ic/"
          "ic73_01_kenner1995_relaxation_modulus.json", "w") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)

# --- 자체검산 ---
n_dig = sum(1 for p in props if p["method"] == "digitized")
assert n_dig == 49, n_dig
assert len(props) == 49 + 3 + 2 + 1, len(props)
for strain, pts in FIG2.items():
    v = [le for _, le in pts]
    inc = [(pts[i][0], v[i], v[i+1]) for i in range(len(v)-1) if v[i+1] > v[i] + 1e-9]
    print(f"  e_o={strain}%: {len(pts)}점, 단조감소 위반 {len(inc)} {inc}")
for strain, zt in ZERO_TIME_MPA.items():
    le0 = FIG2[strain][0][1]
    print(f"  앵커 e_o={strain}%: 판독 {10**le0:.0f} MPa vs 인쇄 {zt:.0f} MPa "
          f"→ {100*(10**le0/zt - 1):+.1f} %")
print(f"총 {len(props)} 행 (디지타이즈 {n_dig} + 인쇄 영시간계수 3 + 인쇄 초기기울기 2 + Tg 1)")
