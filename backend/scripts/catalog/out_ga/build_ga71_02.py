# Moisture Sensitivity 책 16장(van Driel 외)의 molding compound B 인장 Prony 15항·WLF·Tg·CTE 를 JSON 으로 만든다.
import json, math, pathlib

SRC = {"kind": "book",
       "title": "Industrial Applications of Moisture-Related Reliability Problems (Chapter 16 of "
                "`Moisture Sensitivity of Plastic Packages of IC Devices`)",
       "authors": "W.D. van Driel, D.G. Yang, C.A. Yuan, G.Q. Zhang",
       "year": 2010,
       "doi": "10.1007/978-1-4419-5719-1_16",
       "url": "https://doi.org/10.1007/978-1-4419-5719-1_16",
       "publisher": "Springer US, in: X.J. Fan, E. Suhir (eds.), Moisture Sensitivity of Plastic Packages "
                    "of IC Devices, pp. 411-431",
       "local_path": "/data/paper_patent_corpus/snowball_papers/from_rel/"
                     "2010 - Moisture Sensitivity of Plastic Packages of IC Devices.pdf"}

NEWMAT = {"name": "Epoxy molding compound `compound B`, thin large-body BGA overmould, Tg 189 C, "
                  "CTE 17/62 ppm/K (Moisture Sensitivity of Plastic Packages Ch.16, van Driel 2010)",
          "category": "composite",
          "attributes": {"role": "evidence",
                         "role_reason": "원문이 세 후보를 `compound A / B / C` 로만 부르고 제조사·등급을 밝히지 않는다. "
                                        "특정되는 것은 Tg 189 °C, CTE 17/62 ppm/K, 그리고 HAST 에서 "
                                        "'just within qualification limits' 였다는 것뿐이다",
                         "role_confidence": "medium",
                         "material_class": "epoxy molding compound (EMC), BGA overmould",
                         "subsystem": "packaging",
                         "subsystem_basis": "얇고 큰 BGA 패키지의 오버몰드 봉지재다.",
                         "glass_transition_c": 189,
                         "process": "transfer moulded BGA overmould; HAST 130 C / 85 % RH / 96 h 로 평가"}}

# ── Table 16.2 `Relaxation times and corresponding Prony coefficients of molding compound B` (PDF 421쪽) ──
# **PDF 421쪽을 350 dpi 로 그려 15항 전부를 눈으로 대조했다** (ga71_t162_crop.png).
# 지수의 마이너스 부호(1.00E-32 ~ 1.00E-02)가 렌더에도 그대로 있다 — 추출과 완전 일치.
TAU = [1.00e-32, 1.00e-26, 1.00e-20, 1.00e-14, 1.00e-08, 1.00e-02, 1.00e+04, 1.00e+09,
       3.16e+12, 3.16e+14, 1.00e+16, 1.00e+17, 3.16e+18, 3.16e+20, 1.00e+23]
E_MPA = [8.66e2, 9.63e2, 8.54e2, 7.74e2, 7.46e2, 7.94e2, 8.80e2, 9.57e2,
         1.11e3, 2.90e3, 2.75e3, 8.14e3, 4.54e3, 1.26e3, 4.88e2]
TREF_C, C1, C2 = 25.0, 73.79, 298.15
TG_C, CTE_GLASSY, CTE_RUBBERY = 189.0, 17e-6, 62e-6

assert len(TAU) == len(E_MPA) == 15
SUM_E = sum(E_MPA)          # MPa

SET = "moisturebook2010_ch16_compoundB_tensile_15term"


def log_aT(T):
    return -C1 * (T - TREF_C) / (C2 + T - TREF_C)


# 이동인자로 tau 범위가 설명되는지 본다 — WLF 검산 대신 쓸 수 있는 유일한 자기일관성 검사다.
SPAN_LO, SPAN_HI = log_aT(TG_C), log_aT(-40.0)
DECADES_TAU = math.log10(TAU[-1] / TAU[0])

CHECK = (f"**검산 1 — 순간계수.** 원문이 E_inf 를 인쇄하지 않으므로 급수만으로 얻는 것은 "
         f"E(0) - E_inf = sum E_n = {SUM_E:.0f} MPa = {SUM_E/1000:.1f} GPa 다. "
         f"고충전 EMC 의 유리상 인장계수 대역(Chae 2010 의 20.9 GPa, Chiu 2015 의 kappa_g 14 GPa)과 "
         f"같은 자릿수라 표를 잘못 읽지 않았음을 뒷받침한다. **E_inf 가 없으므로 E(0) 를 확정할 수는 없다.** "
         f"**검산 2 — 완화시간 범위와 WLF 의 자기일관성.** tau 가 1e-32 ~ 1e23 s 로 "
         f"{DECADES_TAU:.0f} 십년 치를 덮는데, 인쇄된 WLF(C1={C1}, C2={C2}, T_ref={TREF_C:.0f} °C)를 "
         f"쓰면 log a_T 가 T=Tg({TG_C:.0f} °C)에서 {SPAN_LO:.1f}, T=-40 °C 에서 {SPAN_HI:+.1f} 로 "
         f"약 {SPAN_HI-SPAN_LO:.0f} 십년을 움직인다 — 축 길이가 서로 맞는다. "
         f"**원문이 이동인자표를 인쇄하지 않아 값 대 값 대조는 불가능하다.**")

CAVEAT = ("**tau 를 실제 시간으로 읽지 마라 — 환산시간 축의 수치 적합 결과다.** "
          "1e-32 s 는 물리적 완화시간이 아니라 마스터커브를 55 십년에 걸쳐 덮으려고 놓은 격자점이다. "
          "19차에 Chiu 2018 이 같은 이유로 1e-22·1e-25 항을 적재기 범위검사에 잘렸다 — "
          "이번 값은 전부 적재기 허용범위(1e-40 ~ 1e40) 안에 있음을 확인했다.")

COMMON = ("재료는 원문이 등급명을 밝히지 않은 BGA 오버몰드용 에폭시 몰딩컴파운드 `compound B` 다. "
          "DMA 로 온도·시간 의존 물성을 재고 시간-온도 중첩으로 마스터커브를 만든 뒤 "
          "**일반화 Maxwell 모형**을 맞췄으며 이동인자는 WLF 다 — 본문 verbatim: "
          "*\"A generalized Maxwell model is used to describe their viscoelastic behaviors, and the shift "
          "factor is described by the WLF equation. Table 16.2 lists the relaxation times and the "
          "corresponding Prony coefficients for the molding compound B. The reference temperature is "
          "chosen as 25 °C, and the constants C1 and C2 for the WLF equation are determined to be 73.79 "
          "and 298.15, respectively.\"* 적합 결과라 method=computed, 표 인쇄값이므로 tier1. "
          + CHECK + " " + CAVEAT)

props = []


def add(key, value, unit, method, cond, notes):
    props.append({"key": key, "value": value, "unit": unit, "method": method,
                  "tier": 1, "conditions": cond, "notes": notes})


def base(i):
    return {"prony_term": i, "prony_terms_total": 15, "term_index": i, "set_id": SET,
            "model": "generalized_maxwell", "series": "tensile",
            "relaxation_mode": "tensile (DMA master curve, generalized Maxwell fit)",
            "reference_temperature_c": TREF_C,
            "reference_temperature_k": TREF_C + 273.15,
            "shift_function": "WLF",
            "normalisation": "none — E_n 이 절대 인장계수(MPa)로 인쇄돼 있다",
            "time_axis": "reduced time (WLF-shifted)",
            "source_data": "DMA + time-temperature superposition master curve"}


for i, (t, e) in enumerate(zip(TAU, E_MPA), start=1):
    n = (f"Table 16.2 `Relaxation times and corresponding Prony coefficients of molding compound B`, "
         f"15항 중 {i}번. **기준온도는 인쇄돼 있다 — 본문이 T_ref = 25 °C 로 못박는다.** " + COMMON)
    add("mechanical.prony_tensile_modulus", e * 1e6, "Pa", "computed",
        dict(base(i), term=f"E{i}", printed_value_mpa=e),
        f"E_{i} = {e:.2E} MPa 를 Pa 로 환산했다(x1e6). 열 머리글 `Coefficients E n (MPa)`. " + n)
    add("mechanical.prony_relaxation_time", t, "s", "computed",
        dict(base(i), term=f"tau{i}"),
        f"완화시간 tau_{i} = {t:.2E} s. 열 머리글 `Relaxation times τ n (s)`. " + n)

for nm, val, unit, note in [
        ("mechanical.wlf_c1", C1, "1",
         "16.2.2 절 본문 `the constants C1 and C2 for the WLF equation are determined to be 73.79 and "
         "298.15` 중 C1 = 73.79 (무차원)."),
        ("mechanical.wlf_c2", C2, "K",
         "같은 문장의 C2 = 298.15. **원문이 C2 의 단위를 명시하지 않는다** — WLF 의 C2 는 온도차이므로 "
         "K 와 °C 로 읽었을 때 값이 같다(온도 간격). DB 단위 K 에 그대로 넣었다. "
         "값이 298.15 로 0 °C 의 켈빈값과 정확히 같은 것이 눈에 걸리지만 인쇄값이라 그대로 옮겼다.")]:
    add(nm, val, unit, "computed",
        {"set_id": SET, "model": "WLF", "reference_temperature_c": TREF_C,
         "reference_temperature_k": TREF_C + 273.15,
         "applies_to": SET,
         "checksum_vs_printed_shift_factors": "NOT_POSSIBLE — 원문이 a_T 표를 인쇄하지 않는다"},
        note + " " + COMMON)

add("thermal.glass_transition", TG_C + 273.15, "K", "measured",
    {"method_detail": "DMTA/TMA", "printed_value_c": TG_C},
    "Table 16.1 `Material properties` 의 compound B 열 `Tg (°C) : 189` -> 462.15 K. "
    "**PDF 420쪽 350 dpi 렌더로 확인했다**(ga71_t161_crop.png). " + COMMON)

CTE_NOTE = (
    "**원문의 CTE1/CTE2 라벨이 통상 규약과 반대다 — 어느 쪽이 유리상인지는 표의 배치와 물리로 정했다.** "
    "Table 16.1 의 행 순서는 인쇄 그대로 `CTE2 -> Tg -> CTE1` 이다(PDF 420쪽 렌더 확인, "
    "ga71_t161_crop.png). 즉 Tg 행을 사이에 두고 위가 저온측, 아래가 고온측인 배치다. "
    "값도 그 읽기만 가능하다 — A(11/35) · B(17/62) · C(6/35) · 기판 z(51/239) 네 열 모두 "
    "`CTE2 < CTE1` 이고, 에폭시의 열팽창은 Tg 를 지나며 **반드시 커지므로** "
    "CTE2 = 유리상(Tg 아래) · CTE1 = 고무상(Tg 위) 외의 해석은 물리적으로 불가능하다. "
    "**인쇄된 라벨 자체는 conditions.printed_label 에 그대로 남겼다** — 다음 배치가 원문을 "
    "다시 열지 않고도 우리가 무엇을 정했는지 알 수 있게.")

add("thermal.expansion_linear", CTE_GLASSY, "1/K", "measured",
    {"branch": "below Tg (glassy, alpha1 in the usual convention)",
     "printed_label": "CTE2", "printed_value_ppm_per_K": 17,
     "temperature_range_c": "< 189 (Tg)", "method_detail": "TMA",
     "branch_basis": "표의 행 배치(CTE2 행이 Tg 행 위) + 에폭시 CTE 는 Tg 를 지나며 증가한다는 물리"},
    "Table 16.1 compound B 열 `CTE2 (ppm/K) : 17` -> 17e-6 1/K. " + CTE_NOTE + " " + COMMON)

add("thermal.expansion_linear", CTE_RUBBERY, "1/K", "measured",
    {"branch": "above Tg (rubbery, alpha2 in the usual convention)",
     "printed_label": "CTE1", "printed_value_ppm_per_K": 62,
     "temperature_range_c": "> 189 (Tg)", "method_detail": "TMA",
     "branch_basis": "표의 행 배치(CTE1 행이 Tg 행 아래) + 에폭시 CTE 는 Tg 를 지나며 증가한다는 물리"},
    "Table 16.1 compound B 열 `CTE1 (ppm/K) : 62` -> 62e-6 1/K. " + CTE_NOTE + " " + COMMON)

doc = {"batch": "71차 GA", "materials": [{"new_material": NEWMAT, "source": SRC, "properties": props}]}
out = pathlib.Path(__file__).with_name("ga71_02_moisturebook2010_compoundB_prony.json")
out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{out.name}: {len(props)} 행,  sum E_n = {SUM_E:.0f} MPa = {SUM_E/1000:.1f} GPa,  "
      f"tau {DECADES_TAU:.0f} decades vs WLF {SPAN_HI-SPAN_LO:.0f} decades")
