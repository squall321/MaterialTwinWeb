# Chae 2010 EMC 의 인장완화 Prony 두 세트(Table I 21항 · Table II 18항)와 WLF 상수를 표 그대로 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "journal",
       "title": "Characterization of the Viscoelasticity of Molding Compounds in the Time Domain",
       "authors": "S.-H. Chae, J.-H. Zhao, D. R. Edwards, P. S. Ho",
       "year": 2010,
       "doi": "10.1007/s11664-010-1078-7",
       "url": "https://doi.org/10.1007/s11664-010-1078-7",
       "publisher": "Journal of Electronic Materials, vol. 39, no. 4, pp. 419-425",
       "local_path": "/data/paper_patent_corpus/snowball_papers/from_cae/"
                     "Chae - 2010 - Characterization of the Viscoelasticity of Molding Compounds in the Time Domain.pdf"}

NEWMAT = {"name": "Epoxy molding compound, 87 wt% filler, transfer moulded 175 C / 90 s + PMC 175 C / 4 h, "
                  "Tg 120-140 C (Chae 2010 time-domain relaxation characterisation)",
          "category": "composite",
          "attributes": {"role": "evidence",
                         "role_reason": "원문이 'an epoxy-based molding compound with a filler content of "
                                        "87 wt.%' 라고만 하고 제조사·등급을 밝히지 않는다",
                         "role_confidence": "medium",
                         "material_class": "epoxy molding compound (EMC), high filler content",
                         "subsystem": "packaging",
                         "subsystem_basis": "트랜스퍼 몰딩 봉지재다.",
                         "filler_content_wt_pct": 87,
                         "process": "transfer moulded at 175 C with 90 s in-mould cure, post-mould cured "
                                    "175 C / 4 h; bar tensile specimens 127 x 12.7 x 3.17 mm"}}

# ── Table I — Approach I(마스터커브를 먼저 만들고 ANSYS 가 Prony 적합), T_ref = 110 °C ──
# PDF 5쪽을 250 dpi 로 그려 눈으로 확인했다(chae_t1-5.png · chae_t1c-5.png).
T1_TAU = [1.6e-8, 2.8e-7, 4.4e-6, 5.4e-5, 6.2e-4, 6.0e-3, 4.1e-2, 2.7e-1, 1.7, 1.2e1,
          4.8e1, 2.5e2, 2.2e3, 1.5e4, 1.0e5, 8.6e5, 1.1e7, 9.8e7, 1.0e9, 1.0e10, 1.0e11]
T1_E   = [522, 483, 522, 589, 817, 984, 1143, 1938, 2082, 2663,
          2265, 2295, 2155, 720, 408, 300, 145, 94, 96, 34, 71]
T1_EINF = 530
# ── Table II — Approach II(ANSYS 가 Prony 와 WLF 를 동시에 적합), T_ref = 120 °C ──
# PDF 6쪽 확인(chae_t2-6.png · chae_t2b-6.png).
T2_TAU = [1.6e-12, 2.2e-11, 4.6e-10, 9.2e-9, 2.2e-7, 3.5e-6, 8.3e-5, 2.0e-3, 2.0e-2,
          2.2e-1, 3.8, 1.0e1, 9.9e1, 1.0e3, 1.0e4, 1.0e5, 1.0e6, 1.0e7]
T2_E   = [516, 274, 438, 306, 524, 774, 981, 1282, 1209,
          3704, 6188, 1757, 1758, 335, 169, 108, 40, 72]
T2_EINF = 504

assert len(T1_TAU) == len(T1_E) == 21
assert len(T2_TAU) == len(T2_E) == 18
E0_1 = T1_EINF + sum(T1_E)
E0_2 = T2_EINF + sum(T2_E)

COMMON = ("재료는 논문이 등급명을 밝히지 않은 87 wt% 충전 에폭시 몰딩컴파운드다(175 °C 트랜스퍼 몰딩 90 s + "
          "175 °C 4 h 후경화, DMA·TMA 기준 Tg 120~140 °C). 응력완화 시험은 변형률 제어 전기기계식 시험기로 "
          "20~150 °C 에서 했고, Prony 적합은 ANSYS 곡선적합 루틴이 했다 -> method=computed, 표 인쇄값이므로 tier1. "
          f"**교차검산 — 두 접근의 순간계수가 맞는다.** Approach I: E(0) = {T1_EINF} + {sum(T1_E)} = {E0_1} MPa, "
          f"Approach II: E(0) = {T2_EINF} + {sum(T2_E)} = {E0_2} MPa — 차이 {abs(E0_1-E0_2)} MPa "
          f"({abs(E0_1-E0_2)/E0_1*100:.2f} %). 87 wt% 충전 EMC 의 유리상 탄성률 대역과 맞는다. "
          "docling 과 pdftotext 는 이 논문의 곱셈기호(x)를 숫자 9 로, 지수 부호를 공백으로 뭉갠다 "
          "— **70차 FD 가 PDF 5·6쪽을 250 dpi 로 그려 눈으로 확인했다**(크롭은 out_fd/chae_t1*.png · chae_t2*.png).")

props = []
def add(key, value, unit, cond, notes):
    props.append({"key": key, "value": value, "unit": unit, "method": "computed",
                  "tier": 1, "conditions": cond, "notes": notes})

def emit(set_id, tref_c, taus, es, einf, label, extra_note):
    n = len(taus)
    note = (f"{label}, T_ref = {tref_c} °C, {n}항. 원문 식은 "
            f"E(t) = E_inf + sum_k E_k exp(-t/tau_k) 다. " + extra_note + " " + COMMON)
    for i, (t, e) in enumerate(zip(taus, es), start=1):
        base = {"term_index": i, "prony_terms_total": n, "set_id": set_id,
                "model": "generalized_maxwell", "series": "tensile",
                "relaxation_mode": "tensile (uniaxial)",
                "reference_temperature_c": float(tref_c),
                "reference_temperature_k": float(tref_c) + 273.15,
                "source_data": "uniaxial stress relaxation, strain control, 20-150 C; ANSYS Prony curve fit"}
        add("mechanical.prony_tensile_modulus", e * 1e6, "Pa",
            dict(base, term=f"E{i}", printed_value_mpa=e),
            f"E_{i} = {e} MPa 를 Pa 로 환산했다(x1e6). " + note)
        add("mechanical.prony_relaxation_time", t, "s",
            dict(base, term=f"tau{i}"),
            f"완화시간 tau_{i} (열 머리글 'τk (s)'). " + note)
    add("mechanical.prony_long_term_modulus", einf * 1e6, "Pa",
        {"set_id": set_id, "term": "E_inf", "model": "generalized_maxwell", "series": "tensile",
         "relaxation_mode": "tensile (uniaxial)", "reference_temperature_c": float(tref_c),
         "reference_temperature_k": float(tref_c) + 273.15, "printed_value_mpa": einf,
         "basis": "급수 밖 평형항이라 항번호가 없는 것이 맞다"},
        f"표 첫 행 `∞ | – | {einf}` — 장기(평형) 인장완화계수. " + note)

emit("chae2010_tableI_21term_tref110", 110, T1_TAU, T1_E, T1_EINF,
     "Table I `Prony pairs for the master curve shown in Fig. 3 with a reference temperature of 110°C`",
     "**Approach I** — 이동인자로 먼저 마스터커브를 만들고 그 커브에만 ANSYS 가 Prony 를 맞춘 세트다. "
     "이 세트의 이동함수는 WLF 도 Arrhenius 도 아니다 — 원문 Fig. 4 가 셋을 비교하는데 "
     "'either the WLF or Arrhenius equation alone did not fit the data very well' 이라 "
     "다항식을 썼고 **그 계수는 인쇄되지 않는다.**")

emit("chae2010_tableII_18term_tref120", 120, T2_TAU, T2_E, T2_EINF,
     "Table II `Prony pairs for the master curve in Fig. 6a which was determined together with WLF constants "
     "by ANSYS with a reference temperature of 120°C`",
     "**Approach II** — 온도별 원자료를 그대로 ANSYS 에 넣어 Prony 와 WLF 를 **동시에** 맞춘 세트다. "
     "짝이 되는 WLF 상수는 같은 출처로 따로 등록했다(set_id=chae2010_wlf_approachII).")

# ── WLF — 저자 스스로 부적합하다고 적은 값이다. 그대로 남기되 못 박아 둔다 ──
WLF_NOTE = ("본문 verbatim: 'The WLF constants were determined to be C1 = 2.01 × 10^11 and C2 = 1.51 × 10^12 "
            "with a reference temperature of T0 = 120°C. **These large numbers resulted in an almost linear "
            "result, as shown in Fig. 6b. This is attributed to the fact that the WLF equation alone could not "
            "describe this material's temperature-dependent behavior properly.**' "
            "— **저자 스스로 이 WLF 가 이 재료를 설명하지 못한다고 적었다.** C2 = 1.51e12 K 는 물리적 온도가 아니라 "
            "적합이 퇴화하며 나온 큰 수이고, C1/C2 비(0.1331)만 살아남아 log aT 가 (T-T0) 에 거의 선형이 된다. "
            "표 인쇄값이라 tier1 로 남기되 **이 상수로 마스터커브를 옮기지 마라** — Approach II 의 Prony 세트를 "
            "쓸 때는 원문 Fig. 6b 의 이동인자를 보라. " + COMMON)
for key, val, unit in (("mechanical.wlf_c1", 2.01e11, "1"), ("mechanical.wlf_c2", 1.51e12, "K")):
    add(key, val, unit,
        {"set_id": "chae2010_wlf_approachII", "reference_temperature_c": 120.0,
         "reference_temperature_k": 393.15, "log_base": "log10",
         "applies_to_sets": ["chae2010_tableII_18term_tref120"],
         "fitted_by": "ANSYS viscoelastic curve-fitting routine, simultaneously with the Prony pairs",
         "usable_for_shifting": False,
         "authors_own_verdict": "the WLF equation alone could not describe this material's "
                                "temperature-dependent behavior properly (원문 본문)",
         "c1_over_c2": 2.01e11 / 1.51e12},
        WLF_NOTE)

doc = {"batch": "70차 FD",
       "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("fd70_05_chae2010_emc_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {len(props)}행  (E0_I={E0_1} MPa, E0_II={E0_2} MPa, 차 {abs(E0_1-E0_2)})")
