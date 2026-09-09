# Park 2011 언더필 UF-B 의 인장완화 Prony 13항 + 장기계수를 원문 Table 1 그대로 JSON 으로 만든다.
import json, pathlib

SRC = {"kind": "journal",
       "title": "Thermal fracture toughness measurement for underfill during temperature change",
       "authors": "Seungbae Park, Claudius Feger",
       "year": 2011,
       "publisher": "Microelectronics Reliability 51 (2011) 685-691",
       "doi": None, "url": None,
       "local_path": "/data/paper_patent_corpus/cae_papers/10_underfill_stress/"
                     "Park - 2011 - Thermal fracture toughness measurement for underfill during temperature change.pdf"}

NEWMAT = {"name": "Underfill UF-B, commercial capillary underfill, Tg 100 C "
                  "(Park & Feger 2011 thermal-SENT characterisation)",
          "category": "composite",
          "attributes": {"role": "evidence",
                         "role_reason": "원문이 'two commercial underfill materials' 라고만 하고 "
                                        "등급명을 밝히지 않는다. 식별자는 Tg 100 °C 와 논문 내 코드 'UF-B' 뿐",
                         "role_confidence": "medium",
                         "material_class": "flip-chip capillary underfill encapsulant",
                         "subsystem": "packaging",
                         "subsystem_basis": "플립칩 언더필 봉지재다.",
                         "process": "as received commercial underfill; DMA relaxation over ~200 C in 10 C steps"}}

# ── Table 1 원문 verbatim — **PDF 페이지 이미지로 부호를 확인했다.** ─────────
# docling·pdftotext 는 이 표의 마이너스 부호를 전부 잃는다(log rho 1~5 와 E10·E11·E13).
LOGTAU = [-13, -10, -7, -4, -2, 0, 1, 2, 3, 4, 5, 6, 7]
E_MPA  = [1360, 925.9, 1415, 946.0, 1919, 1836, 2019, 1032, 41.25, -0.22, -0.29, 2.38, -0.08]
E_INF_MPA = 91.6
assert len(LOGTAU) == len(E_MPA) == 13
E0 = E_INF_MPA + sum(E_MPA)          # 유리상(순간) 인장완화계수

SET = "park2011_ufb_tensile_13term"
NOTE = (f"Table 1 `Prony series coefficients of relaxation modulus of UF-B`, 원문 식 verbatim "
        f"E(t) = E_inf + sum_(m=1..13) E_m exp(-t/rho_m). 기준온도는 UF-B 의 Tg 인 **100 °C** 다"
        f"(본문: 'For the reference temperatures for both underfills their Tg's were chosen'). "
        f"검산 — E(0) = E_inf + sum E_m = {E_INF_MPA} + {sum(E_MPA):.2f} = {E0:.1f} MPa ≈ {E0/1000:.1f} GPa 로 "
        f"실리카 충전 언더필의 유리상 탄성률 대역과 맞는다. "
        f"**E_10 · E_11 · E_13 이 음수다(-0.22 / -0.29 / -0.08 MPa) — 제약 없는 적합의 산물이며 "
        f"원문에 그렇게 인쇄돼 있다.** docling 과 pdftotext 는 이 표의 마이너스 부호를 "
        f"(log rho 1~5 까지 포함해) 전부 잃으므로 **70차 FD 가 PDF 4쪽을 300 dpi 로 그려 눈으로 확인했다** "
        f"— 크롭은 out_fd/park2011_t1-4.png 다. "
        f"이동인자는 WLF 도 Arrhenius 도 아니다 — 마스터커브가 유리전이 위아래를 모두 담아 선형성이 깨져서 "
        f"저자가 s = 1/T - 1/T_M 에 대한 **5차 다항식** log aT = A5 s^5 + ... + A1 s 를 썼다"
        f"(A1~A5 = 1.54e4, 1.81e6, 1.92e10, 1.45e13, 3.22e15 — 다만 PDF 텍스트에서 곱셈기호·부호가 "
        f"뭉개져 부호를 확정하지 못했고, **우리 DB 에 다항 이동함수 키가 없어 등록하지 않았다**). "
        f"Prony 적합값이므로 method=computed, 표 인쇄값이므로 tier1.")

props = []
for i, (lt, e) in enumerate(zip(LOGTAU, E_MPA), start=1):
    base = {"term_index": i, "prony_terms_total": 13, "set_id": SET,
            "model": "generalized_maxwell", "series": "tensile", "relaxation_mode": "tensile (uniaxial)",
            "reference_temperature_c": 100.0, "reference_temperature_k": 373.15,
            "source_data": "DMA relaxation moduli over ~200 C in 10 C steps, TTS master curve (Fig. 4)"}
    props.append({"key": "mechanical.prony_tensile_modulus", "value": e * 1e6, "unit": "Pa",
                  "method": "computed", "tier": 1,
                  "conditions": dict(base, term=f"E{i}",
                                     printed_value_mpa=e),
                  "notes": f"E_{i} = {e} MPa 를 Pa 로 환산했다(x1e6). " + NOTE})
    props.append({"key": "mechanical.prony_relaxation_time", "value": float(10.0 ** lt), "unit": "s",
                  "method": "computed", "tier": 1,
                  "conditions": dict(base, term=f"rho{i}",
                                     printed_as="log rho_m (s)", printed_value_log10=lt),
                  "notes": f"원문은 완화시간을 상용로그로 인쇄한다 — `log rho_{i} = {lt}` 이므로 "
                           f"rho_{i} = 1e{lt} s 다. " + NOTE})

props.append({"key": "mechanical.prony_long_term_modulus", "value": E_INF_MPA * 1e6, "unit": "Pa",
              "method": "computed", "tier": 1,
              "conditions": {"set_id": SET, "term": "E_inf", "model": "generalized_maxwell",
                             "series": "tensile", "relaxation_mode": "tensile (uniaxial)",
                             "reference_temperature_c": 100.0, "reference_temperature_k": 373.15,
                             "printed_value_mpa": E_INF_MPA,
                             "basis": "급수 밖 평형항이라 항번호가 없는 것이 맞다"},
              "notes": f"Table 1 마지막 행 `∞ | 91.6` — 장기(평형) 인장완화계수 E_inf = 91.6 MPa. " + NOTE})

doc = {"batch": "70차 FD",
       "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("fd04_park2011_ufb_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{out.name}: {len(props)}행  (E0 = {E0:.1f} MPa)")
