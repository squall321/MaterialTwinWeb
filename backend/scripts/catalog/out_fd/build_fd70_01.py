# Chowdhury 2019 Table 2(DMA 7쌍)·Table 6/7(완화 17쌍) Prony 항과 미등록 WLF 상수를 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "journal",
       "title": "Characterization of Viscoelastic Response of Underfill Materials",
       "doi": "10.1109/itherm.2019.8756500",
       "url": "https://doi.org/10.1109/itherm.2019.8756500",
       "authors": "Promod R. Chowdhury, Jeffrey C. Suhling, Pradeep Lall",
       "year": 2019,
       "publisher": "IEEE (18th ITherm)",
       "local_path": "/data/paper_patent_corpus/structured/cae_papers/10_underfill_stress/"
                     "Chowdhury - 2019 - Characterization of Viscoelastic Response of Underfill Materials/"
                     "Chowdhury - 2019 - Characterization of Viscoelastic Response of Underfill Materials.md"}

MAT = ("Underfill encapsulant, silica-filled epoxy (commercial capillary underfill, "
       "Auburn CAVE3 viscoelastic characterisation, Chowdhury 2019)")

# ── 원문 표 verbatim ────────────────────────────────────────────────────────
# Table 2 — DMA 마스터커브에 맞춘 7쌍. 전단·체적 열이 인쇄값 그대로 동일하다(PDF 대조 완료).
T2_ALPHA = [2.85e-1, 1.82e-1, 1.18e-1, 9.60e-2, 9.19e-2, 1.05e-1, 3.65e-2]
T2_TAU   = [1.67e-1, 2.77e-3, 2.64e-3, 2.22e-14, 2.22e-14, 2.07e0, 5.92e1]
# Table 6(전단)·Table 7(체적) — 응력완화 17쌍. 두 표의 숫자가 완전히 동일하다(PDF 대조 완료).
T67_TAU   = [2.71e-5, 4.41e-4, 2.20e-3, 1.00e-2, 6.60e-2, 9.59e-1, 1.63e1, 9.30e1, 1.00e5,
             1.00e6, 1.00e9, 1.00e10, 1.00e12, 1.00e14, 1.00e15, 1.00e16, 1.00e17]
T67_ALPHA = [2.04e-2, 5.08e-1, 3.82e-2, 2.35e-2, 1.82e-2, 3.93e-3, 4.40e-3, 1.14e-3, 1.83e-3,
             3.92e-4, 5.62e-54, 8.49e-10, 5.58e-4, 2.88e-3, 1.82e-4, 3.35e-4, 3.58e-4]

assert len(T2_ALPHA) == len(T2_TAU) == 7
assert len(T67_TAU) == len(T67_ALPHA) == 17
S2, S67 = sum(T2_ALPHA), sum(T67_ALPHA)
assert S2 < 1.0 and S67 < 1.0, (S2, S67)

COMMON = (
 "Chowdhury 2019 는 측정한 1축 완화계수 E(t) 에 **상수 포아송비 nu=0.2989~0.30**"
 "(80x8x2 mm 시편, 축·횡 스트레인게이지)을 곱해 G=E/2(1+nu), K=E/3(1-2nu) 로 전단·체적을 만들었다. "
 "nu 가 상수이므로 정규화 급수는 수학적으로 동일해져 alpha_i^K == alpha_i^G, tau_i^K == tau_i^G 가 된다 "
 "— 인쇄된 전단 열과 체적 열이 같은 것은 표 중복 아티팩트가 아니라 이 구성의 결과다(PDF 원문 대조 완료). "
 "재료는 논문이 이름을 밝히지 않은 상용 실리카 충전 에폭시 capillary underfill 이다. "
 "Prony 적합은 ANSYS 가 했다 -> method=computed, 인쇄값이므로 tier1.")

props = []

def add(key, value, unit, cond, notes):
    props.append({"key": key, "value": value, "unit": unit,
                  "method": "computed", "tier": 1, "conditions": cond, "notes": notes})

# ── Set A — Table 2, DMA 7쌍 ───────────────────────────────────────────────
SET_A = "chowdhury2019_table2_7pair_dma"
A_NOTE = (f"Table 2 (`Table 2 - Calculated Prony constants for Shear and Bulk Response`), "
          f"**DMA** 마스터커브에서 얻은 7쌍, T_ref=120.0 C. 7개 alpha 합 = {S2:.4f} <= 1 (검산). "
          f"이 세트는 응력완화가 아니라 **DMA(TA RSA3, 0.1-10 Hz, 60-160 C, 인장 모드)** 데이터에서 나왔고 "
          f"Fig.34 에서 검증된다. **주의 — 항이 tau 오름차순이 아니다**(tau1=1.67e-1 > tau2=2.77e-3) 이고 "
          f"tau4=tau5=2.22e-14 s 로 두 항이 완전히 겹친다(적합 아티팩트). 인쇄값 그대로 옮긴다. " + COMMON)

for i, (a, t) in enumerate(zip(T2_ALPHA, T2_TAU), start=1):
    base = {"term_index": i, "prony_terms_total": 7, "set_id": SET_A,
            "model": "generalized_maxwell", "reference_temperature_c": 120.0,
            "reference_temperature_k": 393.15,
            "source_data": "DMA frequency sweep (TA Instruments RSA3, tensile mode, 0.1-10 Hz, 60-160 C), "
                           "storage-modulus master curve shifted to T_ref = 120 C"}
    add("mechanical.prony_relative_modulus", a, "1",
        dict(base, term=f"alpha{i}", series="shear", relaxation_mode="shear"), A_NOTE)
    add("mechanical.prony_relaxation_time", t, "s",
        dict(base, term=f"tau{i}", series="shear", relaxation_mode="shear"),
        f"Table 2 전단 완화시간 tau_{i} (열 머리글 'Ĳ {i} = ... ', 초). " + A_NOTE)
    add("mechanical.prony_relative_bulk_modulus", a, "1",
        dict(base, term=f"alpha{i}", series="volumetric", relaxation_mode="volumetric (bulk)",
             tau_shared_with="series=shear — 원문 체적 열의 tau 가 전단 열과 글자 그대로 같다"), A_NOTE)

# ── Set B — Table 6(전단)/Table 7(체적), 응력완화 17쌍 ────────────────────
SET_B = "chowdhury2019_table6_7_17pair_relaxation"
B_NOTE = (f"Table 6(`Calculated 17 prony pairs from Stress relaxation tests`, 전단)과 "
          f"Table 7(같은 제목, 체적) — **응력완화** 시험에서 얻은 17쌍, T_ref=120 C. "
          f"17개 alpha 합 = {S67:.4f} <= 1 (검산). 두 표의 숫자는 완전히 동일하다(PDF 대조 완료). "
          f"저자가 '17 prony pairs predicted the behavior fairly well' 이라며 Fig.36-40 에서 "
          f"-55/25/85/100 C 크리프까지 이 세트로 재현한다 — 논문이 권장하는 세트다. "
          f"alpha11=5.62e-54, alpha12=8.49e-10 은 사실상 0 인 인쇄값이며 그대로 옮긴다. " + COMMON)

for i, (t, a) in enumerate(zip(T67_TAU, T67_ALPHA), start=1):
    base = {"term_index": i, "prony_terms_total": 17, "set_id": SET_B,
            "model": "generalized_maxwell", "reference_temperature_c": 120.0,
            "reference_temperature_k": 393.15,
            "source_data": "uniaxial stress relaxation at 100/110/120/130/140 C, strain 1% "
                           "(micro tension-torsion tester), master curve shifted to T_ref = 120 C"}
    add("mechanical.prony_relative_modulus", a, "1",
        dict(base, term=f"alpha{i}", series="shear", relaxation_mode="shear"), B_NOTE)
    add("mechanical.prony_relaxation_time", t, "s",
        dict(base, term=f"tau{i}", series="shear", relaxation_mode="shear"),
        f"Table 6 전단 완화시간 tau_{i} (열 머리글 'Ĳi (sec)'). " + B_NOTE)
    add("mechanical.prony_relative_bulk_modulus", a, "1",
        dict(base, term=f"alpha{i}", series="volumetric", relaxation_mode="volumetric (bulk)",
             tau_shared_with="series=shear — Table 7 의 tau 열이 Table 6 과 글자 그대로 같다"), B_NOTE)

# ── WLF — 세 세트분. 인쇄값이지만 원문 Table 3 의 이동인자를 재현하지 못한다 ──
def wlf_note(label, c1, c2, table3_pred):
    return (f"{label} 의 시프트 함수 상수(표 머리글 'Constants for Shift Function "
            f"(Williams-Landel-Ferry (WLF) Equation)', T_ref = 120 C). **논문은 WLF 식을 인쇄하지 않는다.** "
            f"52차 NA 가 같은 논문 Table 2 의 양수 상수(C1=+14.76, C2=+91.52)를 원문 Table 1 이동인자로 "
            f"되맞춰 log10 a_T = -C1(T-Tref)/(C2+T-Tref) 규약을 확정했다. **그 규약으로 이 음수 상수는 "
            f"원문 Table 3 의 이동인자를 재현하지 못한다** — 100/110/130/140 C 에서 인쇄값 "
            f"log10 a = 2.7 / 1.7 / -1.0 / -1.5 인데 이 상수로는 {table3_pred} 가 나온다. "
            f"부호를 뒤집어도(log10 a = +C1·dT/(C2+dT)) 맞지 않는다. 표에 인쇄된 값이므로 tier1 로 그대로 "
            f"남기되 **이 상수만으로 마스터커브를 다른 온도로 옮기면 안 된다** — 옮길 때는 원문 Table 3 의 "
            f"이동인자표를 직접 써라(우리 DB 에는 이동인자 키가 없다). "
            f"표 옆의 안내문 'It is Recommended That Glass Transition Temperature Should be Used as "
            f"Reference Temperature (Tref=Tg) / Calculated Using Stress Relaxation Test Data From Ansys' "
            f"가 이 상수가 ANSYS 곡선적합 출력임을 밝힌다.")

WLF_SETS = [
    ("chowdhury2019_table4_7pair_relaxation", "Table 4 (응력완화 7쌍)", -13.66, -54.47),
    ("chowdhury2019_table5_13pair_relaxation", "Table 5 (응력완화 13쌍)", -12.28, -44.93),
    (SET_B, "Table 6/7 (응력완화 17쌍)", -12.20, -44.42),
]
def wlf_pred(c1, c2, dT):          # log10 a_T = -C1*dT/(C2+dT)
    return -c1 * dT / (c2 + dT)
for sid, label, c1, c2 in WLF_SETS:
    pred = " / ".join(f"{wlf_pred(c1, c2, d):+.2f}" for d in (-20, -10, +10, +20))
    cond = {"set_id": sid, "reference_temperature_c": 120.0, "reference_temperature_k": 393.15,
            "log_base": "log10",
            "equation_verbatim": "NOT PRINTED - 논문은 WLF 식을 쓰지 않는다. 표 머리글만 "
                                 "'Constants for Shift Function (Williams-Landel-Ferry (WLF) Equation)' 이다",
            "equation_assumed": "log10(a_T) = -C1*(T-Tref)/(C2+(T-Tref))  (52차 NA 가 같은 논문 Table 1·2 로 확정한 규약)",
            "checksum_vs_printed_shift_factors": "FAILED - 원문 Table 3 을 재현하지 못한다",
            "usable_for_shifting": False,
            "shift_factor_table_available_in_source": "Table 3 (100/110/120/130/140 C)"}
    add("mechanical.wlf_c1", c1, "1", cond, wlf_note(label, c1, c2, pred))
    add("mechanical.wlf_c2", c2, "K", dict(cond), wlf_note(label, c1, c2, pred))

doc = {"batch": "70차 FD",
       "materials": [{"match_name": MAT, "source": SRC, "properties": props}]}

out = pathlib.Path(__file__).with_name("fd01_chowdhury2019_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {len(props)}행  (T2 alpha합={S2:.4f}, T6/7 alpha합={S67:.4f})")
