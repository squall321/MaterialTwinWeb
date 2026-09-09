# 72차 HA — Memon 2020 Fig.8a 정규화 응력완화계수 65점을 relaxation_modulus_normalized 첫 손님으로 세운다
import json
from pathlib import Path

SP = Path('/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/'
          '27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/memon_fig8a_final.json')
OUT = Path(__file__).with_name('ha72_02_memon2020_relaxation_normalized.json')
CSV = Path(__file__).with_name('ha72_02_memon2020_fig8a.csv')

D = json.loads(SP.read_text())
CAL, META, TAU, PTS = D['calibration'], D['meta'], D['tau_1_over_e_s'], D['points']

NAME = ("Disulfide epoxy vitrimer BGPDS/MHHPA, cured (bis(4-glycidyloxyphenyl)disulfide + "
        "methyl hexahydrophthalic anhydride, 2M4EI catalyst, Tg 116 C, Memon 2020)")
assert len(NAME) <= 200, len(NAME)

SRC = {
    "kind": "journal",
    "title": ("Welding and reprocessing of disulfide-containing thermoset epoxy resin "
              "exhibiting behavior reminiscent of a thermoplastic"),
    "authors": "Hafeezullah Memon, Yi Wei",
    "year": 2020,
    "doi": "10.1002/app.49541",
    "url": "https://doi.org/10.1002/app.49541",
    "publisher": "Journal of Applied Polymer Science (Wiley)",
    "local_path": ("/data/paper_patent_corpus/mech_papers/24_epoxy_cure_chem/"
                   "Memon - 2020 - Welding and reprocessing of disulfide‐containing thermoset "
                   "epoxy resin exhibiting behavior reminiscent of a thermoplastic.pdf"),
}

MEAS = ("The relaxation modulus was recorded as a function of time at different temperatures "
        "from 70 to 130 °C on circular specimens with a diameter of 25 mm and a thickness of "
        "2 mm, prestrained by 0.5% torsional load on a strain-controlled rheometer ARES "
        "(TA Instruments) under parallel-plate geometry.")
CAP = ("FIGURE 8 Rheological studies of cured resin at six different temperatures between 80 and "
       "130 °C. (a) Normalized stress-relaxation modulus versus time")

# 세 앵커 — 이 값들이 판독을 검산한다
ANCHOR = (
    "**앵커 검산 셋을 통과했다.** "
    "① 원문 verbatim — \"The relaxation times (tau*) thus obtained decreased from longer than 1 hr "
    "at 80 °C to 440 s at 130 °C\" 이고 원문의 정의는 \"the time required to reach 63.3% of the "
    "initial relaxation modulus was considered as the relaxation time\" 다. 우리 곡선에서 "
    "130 °C · t = 440 s 의 G/G0 = 0.3699 로 **1/e = 0.3679 에 0.0021 차이로 떨어진다** "
    "— 즉 원문이 실제로 쓴 기준은 '초기값의 63.3 %' 가 아니라 '63.2 % 만큼 감쇠(= 1/e 로 하강)' 다. "
    "축 보정이 맞다는 증거이자 원문 문구의 오기를 잡은 것이다. "
    "② 우리 곡선에서 G/G0 = 1/e 도달 시각을 여섯 온도 전부에서 읽으면 "
    "80/90/100/110/120/130 °C = 4327/2841/1906/1214/747/460 s 이고, "
    "130 °C 의 460 s 는 인쇄된 440 s 와 4.5 % 차이, 80 °C 의 4327 s = 1.20 hr 는 원문의 "
    "\"longer than 1 hr\" 를 만족한다. "
    "③ 그 여섯 점을 아레니우스로 맞추면 **Ea = 52.9 kJ/mol · R² = 0.994** 가 나오고, "
    "원문이 인쇄한 값은 **Ea = 53.3 kJ/mol · R² = 0.985**(Fig. 8b)다 — 0.8 % 차이다. "
    "여섯 곡선 전부가 독립적으로 검산된 셈이다."
)

RULE = (
    "**기준온도가 없는데 넣었다 — 이 곡선이 마스터커브가 아니기 때문이다.** "
    "Fig. 8a 는 시간-온도 중첩으로 조립한 마스터커브가 아니라 **여섯 온도에서 각각 따로 잰 "
    "등온 완화곡선 여섯 벌**이다(원문 캡션이 \"at six different temperatures between 80 and 130 °C\" "
    "라고 못박는다). 단일온도 곡선은 그 곡선이 성립하는 온도가 곧 자기 자신이라 T0 가 필요 없다. "
    "그래서 `curve_type = single_temperature` · `reference_temperature_printed = false` 를 달았다. "
    "반대로 71차 GA 가 막은 Baek 2008 은 마스터커브인데 T0 가 인쇄돼 있지 않아 못 넣었다 — "
    "**마스터커브는 T0 없이 뜻이 없고 단일온도 모형은 T0 가 필요 없다**는 규칙의 두 사례다."
)

CALN = (
    f"**판독 방법과 오차.** 400/600 dpi 렌더에서 색상으로 여섯 곡선을 분리하고 열마다 중앙값을 "
    f"잡았다. 축 보정은 자동 검출한 눈금 픽셀만 썼다(보간한 눈금 없음) — "
    f"세로 눈금 6개(1.0~0.0), 가로 눈금 5개(0~6000 s). "
    f"**보정 잔차는 세로 최대 {CAL['y_resid_max']} G/G0 · 가로 최대 {CAL['x_resid_max']} s** 다. "
    f"파선의 빈 열은 인접 열 사이 선형보간으로 메웠고 **틈이 30 px(169 s)를 넘으면 그 점을 버렸다**. "
    f"**t = 0 직후의 급강하 구간은 읽지 않았다** — 곡선이 거의 수직이라 한 열의 중앙값이 값이 아니다. "
    f"곡선마다 열 안 세로 퍼짐이 25 px(0.030 G/G0) 아래로 떨어진 뒤부터 읽었다."
)

props, csv_rows = [], ["temperature_c,time_s,g_normalized,gap_px"]
for T in sorted(PTS, key=lambda s: int(s)):
    Tc = float(T)
    m = META[T]
    tau = TAU.get(T)
    for p in PTS[T]:
        csv_rows.append(f"{Tc:g},{p['time_s']},{p['g']},{p['gap_px']}")
        props.append({
            "key": "mechanical.relaxation_modulus_normalized",
            "value": p['g'],
            "unit": "1",
            "method": "digitized",
            "tier": 1,
            "conditions": {
                "time_s": float(p['time_s']),
                "temperature_c": Tc,
                "reference_temperature_printed": False,
                "curve_type": "single_temperature",
                "relaxation_mode": "shear",
                "strain_pct": 0.5,
                "normalisation": ("g(t) = G(t)/G(0); 원문 세로축 라벨은 `G/G'` 인데 캡션이 "
                                  "\"Normalized stress-relaxation modulus\" 라 밝히고 t→0 에서 1 로 "
                                  "수렴하므로 G' 는 초기(순간) 완화계수 G(0) 를 가리킨다. "
                                  "**G(0) 의 절대값은 원문에 인쇄되지 않는다** — 이 곡선만으로 "
                                  "Pa 단위 G(t) 를 되살릴 수 없다"),
                "source_figure": "Fig. 8a",
                "read_from_t_s": m['read_from_t_s'],
                "curve_last_t_s": m['t_last_s'],
                "interpolated_gap_px": p['gap_px'],
                "instrument": ("strain-controlled rheometer ARES (TA Instruments), parallel-plate, "
                               "disc 25 mm dia x 2 mm"),
                "test_method": "isothermal torsional stress relaxation, 0.5 % prestrain",
                "tau_1_over_e_s": tau,
                "material_state": "cured (post-cure DSC showed no residual exotherm); Tg = 116 °C",
                "above_or_below_tg": "below Tg" if Tc < 116 else "above Tg",
            },
            "notes": (
                f"정규화 응력완화계수 g(t) = G(t)/G(0) = {p['g']} (무차원), "
                f"t = {p['time_s']} s, T = {Tc:g} °C. "
                f"원문 그림 캡션 verbatim — `{CAP}`. "
                f"측정 조건 verbatim — \"{MEAS}\" "
                f"{RULE} "
                f"{CALN} "
                f"이 온도의 완화시간(우리 곡선에서 g = 1/e 도달) = {tau} s. "
                f"{ANCHOR} "
                f"**Tg = 116 °C 이므로 80~110 °C 는 유리상 아래, 120·130 °C 는 Tg 위다** "
                f"— 이 재료는 비트리머라 Tg 아래에서도 이황화 결합 교환으로 완화한다"
                f"(원문이 밝힌 위상동결전이온도 T_v = 28 °C). "
                f"**G(0) 절대값이 없으므로 이 행만으로 Pa 단위 완화계수를 만들 수 없다.**"
            ),
        })

doc = {
    "batch": "72차 HA",
    "materials": [{
        "new_material": {
            "name": NAME,
            "category": "polymer",
            "attributes": {
                "role": "evidence",
                "role_reason": ("연구실에서 합성한 이황화 비트리머 에폭시다 — 상용 등급이 아니고 "
                                "제조사·품번이 없다. 단량체(BGPDS)까지 저자가 직접 합성했다"),
                "role_confidence": "high",
                "material_class": "disulfide-containing epoxy vitrimer (covalent adaptable network)",
                "process": ("BGPDS:MHHPA:2M4EI = 180:168:3 (에폭시:무수물 몰비 1:1), "
                            "DCM 제거 후 진공탈포. **경화조건이 원문 두 곳에서 다르게 인쇄돼 있다** — "
                            "§2.4 는 120 °C 1 h / 140 °C 2 h / 160 °C 1 h, §3.1 은 DSC 근거로 "
                            "90 °C 2 h / 140 °C 2 h / 170 °C 2 h 다. 어느 쪽이 실제인지 "
                            "우리가 고르지 않고 둘 다 남긴다"),
                "notes": ("Tg 116 °C · 25 °C 저장탄성률 2,443 MPa · 위상동결전이온도 28 °C · "
                          "이황화 교환 활성화에너지 53.3 kJ/mol (전부 원문 인쇄값)"),
            },
        },
        "source": SRC,
        "properties": props,
    }],
}

OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
CSV.write_text("\n".join(csv_rows) + "\n", encoding='utf-8')
print(f"{OUT.name} — {len(props)} 행 · {CSV.name} — {len(csv_rows)-1} 점")
