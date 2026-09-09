# Raghavan 2011 PSR(솔더레지스트) 정규화 전단 Prony 10항을 원문 Table I 그대로 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "journal",
       "title": "Methodology to Predict Substrate Warpage and Different Techniques to Achieve "
                "Substrate Warpage Targets",
       "authors": "Vijay Raghavan et al.",
       "year": 2011,
       "publisher": "IEEE Transactions on Components, Packaging and Manufacturing Technology, "
                    "vol. 1, no. 7, pp. 1064-1071",
       "doi": None, "url": None,
       "local_path": "/data/paper_patent_corpus/expert_papers/06_pcb/"
                     "Raghavan - 2011 - Methodology to Predict Substrate Warpage and Different Techniques "
                     "to Achieve Substrate Warpage Targets.pdf"}

NEWMAT = {"name": "Photosensitive solder resist (PSR) dielectric, epoxy-based, UV 40 mW/cm2 5-7 min + "
                  "170 C / 30 min full cure, Tg 115 C (Raghavan 2011)",
          "category": "polymer",
          "attributes": {"role": "evidence",
                         "role_reason": "원문이 제조사·등급을 밝히지 않고 'epoxy-based dielectric material' "
                                        "라고만 부른다. 공정(UV 노광 + 170 C/30 min)만 특정된다",
                         "role_confidence": "medium",
                         "material_class": "photoimageable solder resist (PSR) dielectric",
                         "subsystem": "pcb",
                         "subsystem_basis": "FR4 코어 위 30 um 솔더레지스트층이다.",
                         "process": "UV exposure 40 mW/cm^2 for 5-7 min, then oven cure 170 C / 30 min "
                                    "(full cure confirmed by DSC exotherm disappearance and DMA Tg saturation)"}}

# ── Table I 원문 verbatim(PDF 대조 완료) ────────────────────────────────────
TAU = [1.00e-10, 2.06e-9, 1.38e-8, 1.00e-6, 1.00e-5, 1.00e-4, 2.14e-3, 2.74e-2, 1.28e0, 5.13e2]
G   = [0.09, 0.01, 0.08, 0.10, 0.02, 0.15, 0.18, 0.16, 0.17, 0.02]
assert len(TAU) == len(G) == 10
SG = sum(G)
assert SG <= 1.0, SG

SET = "raghavan2011_psr_shear_10term"
NOTE = (f"Table I `PRONY SERIES COEFFICIENTS FOR PSR MATERIAL`, 10 Maxwell 요소, T_ref = 110 °C. "
        f"10개 g 합 = {SG:.2f} <= 1 (검산) — 남는 g_inf = {1-SG:.2f} 가 평형항이다. "
        f"원문 식 verbatim: g(t) = g_inf + sum g_i exp(-t/tau_i), g_inf = G_inf/G_0, G(t) = G_0 g(t) "
        f"— 즉 g_i 는 **유리상 전단탄성률 G_0 로 정규화된 무차원 가중치**다(열 머리글도 "
        f"'Normalized shear relaxation modulus weight factors (gi)'). "
        f"**G_0 자체는 논문에 인쇄되지 않는다** — 이 급수를 쓰려면 G_0 를 따로 구해야 한다. "
        f"시험은 10 x 6 x 0.045 mm 완전경화 시편의 응력완화 + TTS, 이동인자는 WLF 형태 "
        f"log(aT) = -C1(T-T0)/(C2+(T-T0)) 를 썼다고 밝히지만 **C1·C2 수치는 인쇄하지 않는다"
        f"(Fig. 3 그림뿐)**. PSR 의 Tg 는 본문에 115 °C 로 적혀 있다. "
        f"Prony 적합값이므로 method=computed, 표 인쇄값이므로 tier1.")

props = []
for i, (t, g) in enumerate(zip(TAU, G), start=1):
    base = {"term_index": i, "prony_terms_total": 10, "set_id": SET,
            "model": "generalized_maxwell", "series": "shear", "relaxation_mode": "shear",
            "reference_temperature_c": 110.0, "reference_temperature_k": 383.15,
            "normalisation": "g_i = G_i / G_0 (glassy shear modulus); G_0 NOT printed in the source",
            "source_data": "shear stress relaxation + time-temperature superposition, TA Instruments DMA"}
    props.append({"key": "mechanical.prony_relative_modulus", "value": g, "unit": "1",
                  "method": "computed", "tier": 1,
                  "conditions": dict(base, term=f"g{i}"), "notes": NOTE})
    props.append({"key": "mechanical.prony_relaxation_time", "value": t, "unit": "s",
                  "method": "computed", "tier": 1,
                  "conditions": dict(base, term=f"tau{i}"),
                  "notes": f"Table I 완화시간 tau_{i} (열 머리글 'Relaxation time, (τi) (s)'). " + NOTE})

doc = {"batch": "70차 FD",
       "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("fd03_raghavan2011_psr_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {len(props)}행  (Σg={SG:.2f}, g_inf={1-SG:.2f})")
