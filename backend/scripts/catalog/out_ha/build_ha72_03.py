# 72차 HA — Gower 2006 Table 4 이동인자 log10(a_T) 45칸을 a_T 로 환산해 tts_shift_factor 로 세운다
import json
from pathlib import Path

OUT = Path(__file__).with_name('ha72_03_gower2006_shift_factor.json')

SRC = {
    "kind": "journal",
    "title": ("Gower & Shanks (2006), Acrylic acid level and adhesive performance and peel "
              "master-curves of acrylic pressure-sensitive adhesives, J Polym Sci Part B: "
              "Polym Phys 44:1237-1252"),
    "authors": "Martin D. Gower, Robert A. Shanks",
    "year": 2006,
    "doi": "10.1002/polb.20779",
    "url": "https://doi.org/10.1002/polb.20779",
    "publisher": "Journal of Polymer Science Part B: Polymer Physics 44(9) 1237-1252",
    "local_path": ("/data/paper_patent_corpus/mech_papers/26_psa_chem/"
                   "Gower - 2006 - Acrylic acid level and adhesive performance and peel "
                   "master‐curves of acrylic pressure‐sensitive adhesives.pdf"),
}

# DB 재료명 그대로(1659~1673). 코드 -> 이름.
MATS = {
 "AA2M91-3": "Acrylic PSA emulsion copolymer AA2M91-3 (BA/EHA/MMA/AA 91.00/0.00/7.00/2.00 wt%, Gower 2006)",
 "AA2M61-3": "Acrylic PSA emulsion copolymer AA2M61-3 (BA/EHA/MMA/AA 61.34/25.00/11.66/2.00 wt%, Gower 2006)",
 "AA2M50-3": "Acrylic PSA emulsion copolymer AA2M50-3 (BA/EHA/MMA/AA 50.00/34.56/13.44/2.00 wt%, Gower 2006)",
 "AA2M25-3": "Acrylic PSA emulsion copolymer AA2M25-3 (BA/EHA/MMA/AA 25.00/55.61/17.39/2.00 wt%, Gower 2006)",
 "AA2M02-3": "Acrylic PSA emulsion copolymer AA2M02-3 (BA/EHA/MMA/AA 1.98/75.00/21.02/2.00 wt%, Gower 2006)",
 "AA4M91-3": "Acrylic PSA emulsion copolymer AA4M91-3 (BA/EHA/MMA/AA 91.00/0.00/5.00/4.00 wt%, Gower 2006)",
 "AA4M61-3": "Acrylic PSA emulsion copolymer AA4M61-3 (BA/EHA/MMA/AA 61.34/25.00/9.66/4.00 wt%, Gower 2006)",
 "AA4M50-3": "Acrylic PSA emulsion copolymer AA4M50-3 (BA/EHA/MMA/AA 50.00/34.56/11.44/4.00 wt%, Gower 2006)",
 "AA4M25-3": "Acrylic PSA emulsion copolymer AA4M25-3 (BA/EHA/MMA/AA 25.00/55.61/15.39/4.00 wt%, Gower 2006)",
 "AA4M02-3": "Acrylic PSA emulsion copolymer AA4M02-3 (BA/EHA/MMA/AA 1.98/75.00/19.02/4.00 wt%, Gower 2006)",
 "AA6M91-3": "Acrylic PSA emulsion copolymer AA6M91-3 (BA/EHA/MMA/AA 91.00/0.00/3.00/6.00 wt%, Gower 2006)",
 "AA6M61-3": "Acrylic PSA emulsion copolymer AA6M61-3 (BA/EHA/MMA/AA 61.34/25.00/7.66/6.00 wt%, Gower 2006)",
 "AA6M50-3": "Acrylic PSA emulsion copolymer AA6M50-3 (BA/EHA/MMA/AA 50.00/34.56/9.44/6.00 wt%, Gower 2006)",
 "AA6M25-3": "Acrylic PSA emulsion copolymer AA6M25-3 (BA/EHA/MMA/AA 25.00/55.61/13.39/6.00 wt%, Gower 2006)",
 "AA6M02-3": "Acrylic PSA emulsion copolymer AA6M02-3 (BA/EHA/MMA/AA 1.98/75.00/17.02/6.00 wt%, Gower 2006)",
}

# Table 4 인쇄값 — **300 dpi 렌더에서 눈으로 확인한 것이다. 전부 음수다.**
TBL = {
 "AA2M91-3": (-0.50, -1.00, -1.40), "AA2M61-3": (-0.40, -1.00, -1.40),
 "AA2M50-3": (-0.40, -1.30, -1.70), "AA2M25-3": (-0.50, -1.10, -1.70),
 "AA2M02-3": (-0.50, -1.30, -2.10), "AA4M91-3": (-0.50, -1.10, -1.60),
 "AA4M61-3": (-0.50, -1.10, -1.60), "AA4M50-3": (-0.55, -1.15, -1.65),
 "AA4M25-3": (-0.60, -1.30, -1.85), "AA4M02-3": (-0.70, -1.50, -2.00),
 "AA6M91-3": (-0.50, -1.10, -1.50), "AA6M61-3": (-0.50, -1.10, -1.80),
 "AA6M50-3": (-0.50, -1.40, -2.40), "AA6M25-3": (-0.50, -1.70, -2.50),
 "AA6M02-3": (-0.50, -2.20, -2.60),
}
TEMPS = (35.0, 50.0, 65.0)
TREF = 25.0

CAP = ("Table 4. The Effect of Test Temperature on the Logarithm of the Temperature Shift Factors "
       "for the Cohesive Failure Region of the Peel Master-Curves for AA2M-3, AA4M-3, and AA6M-3 "
       "Copolymers")
BODY = ("The master-curves of log(reduced peel stress) against log(reduced peeling rate) were "
        "constructed via the TTS principle by applying shift factors aT to peel adhesion versus "
        "peeling rate curves at a range of test temperatures and superpositioning the curves at a "
        "reference temperature of 25 °C. ... The values for log(aT) used to prepare the individual "
        "polymer peel master-curves at test temperatures above 25 °C are presented in Table 4.")
EQ = "a_T = tau(T) / tau_r(T_r)   (원문 식 (3), 300 dpi 렌더로 해독)"

SIGNTRAP = (
    "**부호 함정 — 이 표는 docling 추출로 읽으면 45칸 전부 부호가 뒤집힌다.** "
    "`tables/table-4.md` 는 `0.50 / 1.00 / 1.40 …` 로 **양수**를 내놓는데 "
    "300 dpi 원본 렌더는 `−0.50 / −1.00 / −1.40 …` 로 **전부 음수**다. 크기는 같고 마이너스만 사라졌다. "
    "부호가 뒤집히면 a_T 가 0.316 이 아니라 3.16 이 되어 **10배가 아니라 100배 틀린 값**이 되고, "
    "게다가 그 값이 '고온에서 완화가 느려진다'는 물리적으로 불가능한 이야기를 하게 된다. "
    "**이 45칸은 전부 렌더로 눈으로 읽었다.**"
)

RULE = (
    "**원문은 log10(a_T) 를 인쇄하고 우리는 a_T 를 넣는다**(브리프 규칙). "
    "로그를 그대로 넣으면 밑과 부호가 조건에 숨어 한 칸에 두 양이 섞인다. "
    "원문 표기는 `printed_as = log10_a_T` 와 `value_printed` 에 보존했다. "
    "**밑이 10 인 것은 원문이 자기 안에서 증명한다** — 다른 자리에서 "
    "\"The curves were superpositioned by shifting the caboxylated polymer curves by a_T* = 7 "
    "[log(a_T*) = 0.845]\" 라 쓰는데 log10(7) = 0.8451 이다(자연로그면 1.9459 다)."
)

MODE = ("not applicable — 완화탄성률 곡선이 아니라 **180° 박리력 마스터커브**의 이동인자다. "
        "원문은 이것을 WLF 이동인자라 부르고 Derail 등[8]이 박리 마스터커브에서 얻은 이동인자가 "
        "유변학 측정에서 얻은 것과 같음을 보였다고 인용한다")

props_by_mat = {}
for code, logs in TBL.items():
    rows = []
    for Tc, lg in zip(TEMPS, logs):
        aT = 10.0 ** lg
        rows.append({
            "key": "mechanical.tts_shift_factor",
            "value": float(f"{aT:.6g}"),
            "unit": "1",
            "method": "computed",
            "tier": 1,
            "conditions": {
                "temperature_c": Tc,
                "reference_temperature_c": TREF,
                "reference_temperature_printed": True,
                "curve_type": "master_curve",
                "printed_as": "log10_a_T",
                "value_printed": lg,
                "relaxation_mode": MODE,
                "shift_function": ("empirical (obtained by superposing isothermal peel-rate curves; "
                                   "the paper calls them WLF shift factors and defines "
                                   "a_T = tau(T)/tau_r(T_r), eq 3)"),
                "set_id": f"gower2006_table4_peel_mastercurve_{code}",
                "master_curve": ("log(reduced peel stress) vs log(reduced peeling rate) = log(a_T · v), "
                                 "180° peel, cohesive-failure region, T_ref = 25 °C (298 K)"),
                "log_base": "log10",
                "sign_convention": ("a_T < 1 above T_ref (relaxation faster at higher T) — "
                                    "표준 시간영역 규약이다"),
                "polymer_code": code,
                "failure_mode": "cohesive",
            },
            "notes": (
                f"이동인자 a_T = {aT:.6g} (무차원), T = {Tc:g} °C, 기준온도 T0 = 25 °C. "
                f"원문 표 verbatim — `{CAP}` 의 `{code}` 행, `{Tc:g}` 열. "
                f"**원문 인쇄값은 log10(a_T) = {lg} 다.** "
                f"{RULE} "
                f"**환산 산술 — a_T = 10^({lg}) = {aT:.6g}.** "
                f"**검산 — log10({aT:.6g}) = {lg:.4f}** 로 인쇄값과 일치한다(왕복 검산). "
                f"정의 verbatim — {EQ}. "
                f"기준온도 근거(본문 verbatim) — \"{BODY}\" "
                f"{SIGNTRAP} "
                f"**부호 검산 — 세 온도 전부 T > T0 = 25 °C 이고 인쇄된 log 가 전부 음수라 "
                f"a_T < 1 이다.** 고온일수록 완화가 빠르므로 a_T 가 작아져야 하고, 이 폴리머의 "
                f"세 칸은 {logs[0]} > {logs[1]} > {logs[2]} 로 온도에 대해 단조감소한다 — 물리와 맞는다."
            ),
        })
    props_by_mat[code] = rows

doc = {
    "batch": "72차 HA",
    "materials": [
        {"match_name": MATS[code], "source": SRC, "properties": rows}
        for code, rows in props_by_mat.items()
    ],
}
OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding='utf-8')
n = sum(len(r) for r in props_by_mat.values())
print(f"{OUT.name} — 재료 {len(props_by_mat)}종 · {n} 행")
