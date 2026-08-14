# 전방위 물성 taxonomy — property_definition 시드(열·전기·광/복사·화학·물리·음향·자기·유변·구조·기계).
"""화학·물리 물성 전 도메인의 정규 정의 레지스트리.

각 항목: (key, domain, name, symbol, unit, value_type, condition_axes, standard).
unit은 정규 저장 단위(무차원·범주형은 None). value_type 기본 'numeric'.
condition_axes는 이 물성이 의존하는 조건 축(property_value.conditions 키와 정합).
seed_property_definitions()로 멱등 upsert.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

# fmt: off
# (key, domain, name, symbol, unit, value_type, condition_axes, standard)
_DEFS: list[tuple] = [
    # ── 기계 (일부는 ProcessedResult와 중복 — 교차도메인 조회·외부 물성 병합용) ──────
    ("mechanical.youngs_modulus", "mechanical", "영률", "E", "Pa", "numeric", ["temperature_k"], "ASTM E111"),
    ("mechanical.yield_strength", "mechanical", "항복강도", "Rp0.2", "Pa", "numeric", ["temperature_k"], "ISO 6892"),
    ("mechanical.tensile_strength", "mechanical", "인장강도(UTS)", "Rm", "Pa", "numeric", ["temperature_k"], "ISO 6892"),
    ("mechanical.elongation_at_break", "mechanical", "파단연신율", "A", "1", "numeric", ["temperature_k"], "ISO 6892"),
    ("mechanical.poisson_ratio", "mechanical", "포아송비", "nu", "1", "numeric", ["temperature_k"], "ASTM E132"),
    ("mechanical.shear_modulus", "mechanical", "전단탄성계수", "G", "Pa", "numeric", ["temperature_k"], None),
    ("mechanical.bulk_modulus", "mechanical", "체적탄성계수", "K", "Pa", "numeric", ["temperature_k"], None),
    ("mechanical.hardness_vickers", "mechanical", "비커스 경도", "HV", "HV", "numeric", None, "ISO 6507"),
    ("mechanical.hardness_rockwell_c", "mechanical", "로크웰 경도 C", "HRC", "HRC", "numeric", None, "ISO 6508"),
    ("mechanical.hardness_shore_a", "mechanical", "쇼어 A 경도", "ShoreA", "ShoreA", "numeric", None, "ASTM D2240"),
    # Shore OO는 초연질(폼·겔·갭필러) 전용 척도다. **Shore A/OO/D는 상호 환산이 불가능하다** —
    # 규격이 압침 형상과 스프링 하중을 다르게 정의한다(ASTM D2240). 환산하면 우리가 만든 값이 된다.
    ("mechanical.hardness_shore_oo", "mechanical", "쇼어 OO 경도", None, "ShoreOO", "numeric",
     ["standard", "dwell_s", "temperature_c", "specimen_thickness_mm"], "ASTM D2240"),
    ("mechanical.fracture_toughness", "mechanical", "파괴인성", "K_IC", "Pa*m^0.5", "numeric", ["temperature_k"], "ASTM E399"),
    ("mechanical.fatigue_strength", "mechanical", "피로한도", "sigma_f", "Pa", "numeric", ["cycles"], None),
    ("mechanical.compressive_strength", "mechanical", "압축강도", None, "Pa", "numeric", ["temperature_k"], None),
    ("mechanical.flexural_modulus", "mechanical", "굽힘탄성계수", None, "Pa", "numeric", None, "ISO 178"),
    ("mechanical.flexural_strength", "mechanical", "굽힘강도", None, "Pa", "numeric", None, "ISO 178"),
    ("mechanical.impact_strength_izod", "mechanical", "아이조드 충격강도", None, "J/m", "numeric", ["temperature_k"], "ASTM D256"),
    ("mechanical.creep_rate", "mechanical", "정상상태 크리프율", None, "1/s", "numeric", ["stress_pa", "temperature_k"], None),
    # 변형률속도 의존 — LS-DYNA *MAT_024/*MAT_098이 그대로 받는 형식.
    # 테이프·접착제·폼은 충격 해석에서 이 항이 없으면 강성을 크게 과소평가한다.
    ("mechanical.cowper_symonds_c", "mechanical", "Cowper-Symonds C", "C", "1/s", "numeric",
     ["temperature_k"], None),
    ("mechanical.cowper_symonds_p", "mechanical", "Cowper-Symonds p", "p", "1", "numeric",
     ["temperature_k"], None),
    ("mechanical.dynamic_increase_factor", "mechanical", "동적증가계수(DIF)", "DIF", "1", "numeric",
     ["strain_rate_1/s", "temperature_k"], None),
    # 초탄성 상수 — VHB·폼테이프·OCA는 대변형에서 stiffening이 나므로 선형탄성으로는 못 푼다.
    # LS-DYNA *MAT_027(Mooney-Rivlin)·*MAT_077(Ogden/Yeoh)이 직접 받는 계수.
    # 모델별로 항 수가 달라 conditions.model과 term으로 구분한다(예: model="mooney_rivlin_5", term="C10").
    ("mechanical.hyperelastic_coefficient", "mechanical", "초탄성 계수", None, "Pa", "numeric",
     ["model", "term", "strain_rate_1/s", "temperature_k"], None),
    ("mechanical.hyperelastic_exponent", "mechanical", "초탄성 지수", None, "1", "numeric",
     ["model", "term", "temperature_k"], None),
    ("mechanical.incompressibility_d", "mechanical", "비압축 파라미터 D", "D", "1/Pa", "numeric",
     ["model", "term"], None),
    # Prony 급수 항 — 완화시험이 없어도 논문이 계수만 주는 경우가 많다.
    ("mechanical.prony_shear_modulus", "mechanical", "Prony 전단탄성률 항", "g_i", "Pa", "numeric",
     ["term", "temperature_k"], None),
    ("mechanical.prony_relaxation_time", "mechanical", "Prony 완화시간", "tau_i", "s", "numeric",
     ["term", "temperature_k"], None),
    # Prony 인장항은 영률이 아니다. youngs_modulus에 넣으면 대표값 선택이 완화항 하나를
    # 재료의 E로 집어 DYNA 카드가 통째로 틀어진다(실제로 53건이 그렇게 들어올 뻔했다).
    ("mechanical.prony_tensile_modulus", "mechanical", "Prony 인장완화 항", "E_i", "Pa", "numeric",
     ["term", "temperature_k"], None),
    # 상대완화계수 g_i는 무차원이라 Pa 키에 넣으면 단위가 거짓말이 된다.
    ("mechanical.prony_relative_modulus", "mechanical", "Prony 상대완화계수", "g_i", "1", "numeric",
     ["term", "temperature_k"], None),
    # 체적완화 항. 워피지·흡습 팽윤처럼 정수압 성분이 지배하는 문제에서 전단항만으로는 못 푼다.
    ("mechanical.prony_bulk_modulus", "mechanical", "Prony 체적탄성률 항", "K_i", "Pa", "numeric",
     ["term", "temperature_k"], None),
    # 논문마다 체적항을 절대값(K_i, Pa)으로 주기도 하고 비(k_i = K_i/K_0, 무차원)로 주기도 한다.
    # 비를 Pa 키에 넣으면 K_1 = 0.037 Pa가 된다. K_0을 곱해 절대값으로 바꾸는 것은 역산이다.
    ("mechanical.prony_relative_bulk_modulus", "mechanical", "Prony 상대 체적계수", "k_i", "1", "numeric",
     ["term", "temperature_k"], None),
    # 완전완화 후의 평형계수 E∞. **youngs_modulus에 넣으면 안 된다** — DynaVia의 E∞는 7.55 MPa,
    # 순간계수는 GPa급이다. 대표값으로 뽑히면 DYNA 카드의 E가 두 자릿수 틀어진다.
    ("mechanical.prony_long_term_modulus", "mechanical", "Prony 장기 평형계수", "E_inf", "Pa", "numeric",
     ["term", "temperature_k"], None),
    # ── 점소성 (율속·온도 의존 소성) ─────────────────────────────────────────────
    # 솔더·저융점 합금은 상온이 이미 T/Tm≈0.6이라 항상 크리프 영역에 있다. 정적 항복강도만으로
    # 고속 충격을 풀면 소성변형이 폭주해 요소가 뒤집힌다(negative volume). 아래 상수들이
    # *MAT_098/015(Johnson-Cook) · *MAT_224(표형) · Anand 점소성 카드의 입력이다.
    #
    # 계수는 모델·항마다 의미가 달라 conditions.model과 conditions.term이 반드시 있어야
    # 세트로 복원된다 — Prony·초탄성과 같은 규율이다.
    ("mechanical.johnson_cook_a", "mechanical", "Johnson-Cook A (초기항복)", "A", "Pa", "numeric",
     ["model", "temperature_k"], None),
    ("mechanical.johnson_cook_b", "mechanical", "Johnson-Cook B (경화계수)", "B", "Pa", "numeric",
     ["model", "temperature_k"], None),
    ("mechanical.johnson_cook_n", "mechanical", "Johnson-Cook n (경화지수)", "n", "1", "numeric",
     ["model"], None),
    # C가 율속항이다. 이게 없으면 Johnson-Cook을 써도 변형률속도 의존이 없는 것과 같다.
    ("mechanical.johnson_cook_c", "mechanical", "Johnson-Cook C (율속감도)", "C", "1", "numeric",
     ["model", "reference_strain_rate_s"], None),
    ("mechanical.johnson_cook_m", "mechanical", "Johnson-Cook m (온도연화지수)", "m", "1", "numeric",
     ["model", "reference_temperature_k", "melting_temperature_k"], None),
    # Anand 통합 점소성 — 솔더 표준 모델. 9상수가 한 세트라 term 없이는 못 쓴다.
    ("mechanical.anand_constant", "mechanical", "Anand 점소성 상수", None, "1", "numeric",
     ["model", "term", "temperature_k"], None),
    # Norton 정상상태 크리프 eps_dot = A * sigma^n. 지금은 노트 텍스트에만 있어 카드로 못 나간다.
    ("mechanical.norton_coefficient", "mechanical", "Norton 크리프 계수 A", "A", "1", "numeric",
     ["stress_unit", "temperature_k"], None),
    ("mechanical.norton_exponent", "mechanical", "Norton 크리프 지수 n", "n", "1", "numeric",
     ["temperature_k"], None),
    # 율속별 항복강도 — LS-DYNA LCSR(변형률속도 스케일 곡선)의 원자료.
    ("mechanical.yield_strength_at_rate", "mechanical", "변형률속도별 항복강도", None, "Pa", "numeric",
     ["strain_rate_s", "temperature_k"], None),
    # 율속 시험이 항복만 인쇄하는 건 아니다. 인장강도만 율속별로 준 문헌이 실제로 있었고
    # (Hiperco 50A Sandia 보고서의 UTS x 율속 20점), 담을 키가 없어 통째로 버렸다.
    # 항복이 그림뿐이고 UTS만 표로 인쇄되는 경우가 드물지 않다.
    ("mechanical.tensile_strength_at_rate", "mechanical", "변형률속도별 인장강도", None, "Pa", "numeric",
     ["strain_rate_s", "temperature_k"], None),
    # ── 피로·손상 ─────────────────────────────────────────────────────────────
    # 지금까지 fatigue_strength(단일 피로한도)만 있어 "무한수명 판정"밖에 못 했다.
    # 아래 계수쌍이 있어야 "몇 사이클에 깨지는가"를 답한다.
    #
    # Basquin σa = σf'(2Nf)^b — 고주기(응력 지배). 반복 낙하·진동 수명.
    ("mechanical.fatigue_strength_coefficient", "mechanical", "피로강도계수 σf'", "sigma_f", "Pa", "numeric",
     ["model", "stress_ratio_R", "temperature_k"], "ASTM E466"),
    ("mechanical.fatigue_strength_exponent", "mechanical", "피로강도지수 b", "b", "1", "numeric",
     ["model", "stress_ratio_R"], "ASTM E466"),
    # Coffin-Manson Δεp/2 = εf'(2Nf)^c — 저주기(변형률 지배). 온도사이클 솔더 균열.
    ("mechanical.fatigue_ductility_coefficient", "mechanical", "피로연성계수 εf'", "eps_f", "1", "numeric",
     ["model", "temperature_k"], "ASTM E606"),
    ("mechanical.fatigue_ductility_exponent", "mechanical", "피로연성지수 c", "c", "1", "numeric",
     ["model", "temperature_k"], "ASTM E606"),
    # Stromeyer형 (σ − σ∞)^m · N = C — **점근 응력이 있는** 응력-수명 회귀다.
    # Basquin은 N→∞에서 σ→0으로 가는데, 실제 여러 재료는 유한한 피로한도로 수렴한다.
    # 11차 금속 피로 배치가 Zr-BMG·베릴륨동에서 이 형태를 만났고, Basquin으로
    # 재매개화하려면 점근선을 0으로 놓아야 해서 **인쇄되지 않은 숫자를 만들게 된다.**
    # 세 값이 한 세트다 — 계수·지수 중 하나만 있으면 곡선이 서지 않는다.
    ("mechanical.fatigue_stromeyer_coefficient", "mechanical", "Stromeyer 계수 C", "C_st", "1", "numeric",
     ["model", "stress_ratio_R", "temperature_k"], None),
    ("mechanical.fatigue_stromeyer_exponent", "mechanical", "Stromeyer 지수 m", "m_st", "1", "numeric",
     ["model", "stress_ratio_R", "temperature_k"], None),
    ("mechanical.fatigue_stromeyer_asymptote", "mechanical", "Stromeyer 점근응력 σ∞", "sigma_inf", "Pa", "numeric",
     ["model", "stress_ratio_R", "temperature_k"], None),
    # Darveaux K1~K4 — 사이클당 비탄성 소성일 ΔW를 균열 개시·전파 사이클로 환산한다.
    # Anand로 계산한 ΔW가 이미 있어도 이 상수가 없으면 수명이 안 나온다.
    ("mechanical.darveaux_constant", "mechanical", "Darveaux 균열 상수", None, "1", "numeric",
     ["model", "term", "unit_of_term", "temperature_k"], None),
    # ── 배터리 스웰링 (전기화학-기계 연성) ──────────────────────────────────────
    # 인쇄 형태가 넷으로 갈려 키 하나로는 못 담는다(수집 에이전트 보고).
    #   A 사이클별 % 팽창 · B SOH별 절대두께 · C 부분몰부피 Ω · D 메커니즘 분류
    # B는 기존 layer_thickness + state_of_health 조건으로 충분하고, D는 셀 레벨이라 카탈로그 밖.
    # A와 C만 키를 만든다.
    #
    # ⚠ measure 축이 필수다 — 문헌이 "volume expansion"이라 쓰면서 실제로는 1D 딜라토미터로
    # 두께만 재는 경우가 흔하다. 체적변형률과 두께변형률을 섞으면 3배 틀린다.
    # 부호 규약: 팽창이 양수. 층상산화물 양극은 고SOC에서 수축하므로 음수가 정상이다.
    # scale 축은 수집 중에 필요성이 드러나 추가했다 — 흑연 격자 c축 14%와 전극층 10.5%가
    # 같은 measure="thickness"인데 1.3배 다르다. measure만으로는 구분이 안 된다.
    ("mechanical.swelling_strain", "mechanical", "충방전 팽창변형률", None, "1", "numeric",
     ["soc", "cycle", "reversibility", "measure", "scale", "temperature_k"], None),
    # 화학-기계 연성 구성식의 원형 — eps_swell = Omega * c / 3.
    # 흑연 Ω가 문헌 간 4배 차이(1.47e-6 vs 6.5e-6)라 논쟁 중이니 tier·출처를 반드시 남길 것.
    ("chemical.partial_molar_volume", "chemical", "부분몰부피", "Omega", "m^3/mol", "numeric",
     ["species", "soc", "form"], None),
    # Morrow 에너지 모델 N = (W/C)^(-1/m) — ΔW를 사이클로 환산하는 또 다른 경로.
    # Darveaux보다 데이터가 두껍고 요소 크기 의존성 논란이 적다. 계수·지수가 한 쌍이다.
    ("mechanical.morrow_energy_coefficient", "mechanical", "Morrow 에너지 계수", "C", "1", "numeric",
     ["model", "model_form", "unit_of_term", "temperature_k"], None),
    ("mechanical.morrow_energy_exponent", "mechanical", "Morrow 에너지 지수", "m", "1", "numeric",
     ["model", "model_form", "temperature_k"], None),
    # Dasgupta 에너지분할 — 크리프 성분과 순간소성 성분의 수명을 따로 피팅하고
    # 1/N = 1/N_pl + 1/N_cr 로 합친다. Morrow 와 **다른 모델**이라 키를 따로 둔다.
    # **C 는 분모에 있고 n 은 음수로 인쇄된다** — `ΔW = C·N^(−n)` 형태로 읽으면
    # 상수 규모가 자릿수로 틀린다. 그래서 `model_form` 을 필수 축으로 요구한다(브리프 66번).
    ("mechanical.energy_partitioning_constant", "mechanical", "에너지분할 상수", "C/n", "1", "numeric",
     ["model", "model_form", "term", "unit_of_term", "component", "temperature_k", "set_id"], None),
    # Johnson-Cook 파괴 D1~D5 — 삼축도·율속·온도 의존 파단변형률.
    # 지금은 총 파단연신율을 파괴 유효소성변형률로 근사하고 있다.
    ("mechanical.johnson_cook_damage", "mechanical", "Johnson-Cook 파괴상수", None, "1", "numeric",
     ["model", "term", "reference_strain_rate_s"], None),
    # ── 계면 파괴(응집영역) ────────────────────────────────────────────────────
    # 박리강도(peel)는 개시 판정만 된다. 전파를 보려면 파괴에너지가 필요하다.
    ("interface.cohesive_energy_mode1", "interface", "응집영역 파괴에너지 GIC", "G_IC", "J/m^2", "numeric",
     ["model", "temperature_k", "rate_mm_min"], "ASTM D5528"),
    ("interface.cohesive_energy_mode2", "interface", "응집영역 파괴에너지 GIIC", "G_IIC", "J/m^2", "numeric",
     ["model", "temperature_k", "rate_mm_min"], "ASTM D7905"),
    ("interface.cohesive_strength", "interface", "응집영역 최대 트랙션", "T_max", "Pa", "numeric",
     ["model", "mode", "temperature_k"], None),
    # ── 습기 ─────────────────────────────────────────────────────────────────
    # 85/85 후 낙하 같은 복합 시나리오의 끊어진 고리들.
    ("physical.hygroscopic_expansion", "physical", "흡습팽창계수 CHE", "beta", "m^3/kg", "numeric",
     ["temperature_k", "humidity_pct"], None),
    ("physical.moisture_saturation", "physical", "포화 수분농도 Csat", "C_sat", "mol/m^3", "numeric",
     ["temperature_k", "humidity_pct"], None),
    # 노화 후 유지율 — 조건(시간·온도·습도)이 없으면 아무 의미가 없다.
    ("mechanical.property_retention", "mechanical", "노화 후 물성 유지율", None, "1", "numeric",
     ["property", "aging_hours", "temperature_k", "humidity_pct",
      "radiant_exposure_mj_m2", "standard"], None),
    # 가속시험 ↔ 실사용 환산.
    ("chemical.activation_energy", "chemical", "Arrhenius 활성화에너지", "Ea", "J/mol", "numeric",
     ["mechanism", "temperature_range_k"], None),
    # ── 접촉·실링 ────────────────────────────────────────────────────────────
    ("mechanical.friction_coefficient", "mechanical", "마찰계수", "mu", "1", "numeric",
     ["mode", "counterface", "load_n", "temperature_k"], "ASTM D1894"),
    ("mechanical.compression_set", "mechanical", "압축영구변형", None, "1", "numeric",
     ["temperature_k", "duration_h", "compression_pct"], "ASTM D395"),
    # ── 열 ────────────────────────────────────────────────────────────────────
    ("thermal.conductivity", "thermal", "열전도율", "k", "W/(m*K)", "numeric", ["temperature_k"], "ASTM E1461"),
    ("thermal.specific_heat", "thermal", "비열", "cp", "J/(kg*K)", "numeric", ["temperature_k"], "ASTM E1269"),
    ("thermal.diffusivity", "thermal", "열확산율", "alpha", "m^2/s", "numeric", ["temperature_k"], "ASTM E1461"),
    ("thermal.expansion_linear", "thermal", "선팽창계수(CTE)", "CTE", "1/K", "numeric", ["temperature_k"], "ASTM E228"),
    ("thermal.melting_point", "thermal", "융점", "Tm", "K", "numeric", None, None),
    ("thermal.glass_transition", "thermal", "유리전이온도", "Tg", "K", "numeric", None, "ASTM E1356"),
    ("thermal.heat_deflection_temp", "thermal", "열변형온도(HDT)", "HDT", "K", "numeric", ["load_pa"], "ISO 75"),
    ("thermal.vicat_softening", "thermal", "비카트 연화온도", None, "K", "numeric", None, "ISO 306"),
    ("thermal.max_service_temp", "thermal", "최대 사용온도", None, "K", "numeric", None, None),
    ("thermal.min_service_temp", "thermal", "최소 사용온도", None, "K", "numeric", None, None),
    ("thermal.decomposition_temp", "thermal", "분해온도", "Td", "K", "numeric", None, "ASTM E1131"),
    ("thermal.flammability_loi", "thermal", "산소지수(LOI)", "LOI", "1", "numeric", None, "ISO 4589"),
    ("thermal.flammability_ul94", "thermal", "난연등급(UL94)", None, None, "categorical", ["thickness_m"], "UL 94"),
    ("thermal.latent_heat_fusion", "thermal", "융해잠열", None, "J/kg", "numeric", None, None),
    # ── 전기 ──────────────────────────────────────────────────────────────────
    ("electrical.resistivity_volume", "electrical", "체적저항률", "rho", "ohm*m", "numeric", ["temperature_k"], "ASTM D257"),
    ("electrical.conductivity", "electrical", "전기전도율", "sigma", "S/m", "numeric", ["temperature_k"], None),
    ("electrical.surface_resistivity", "electrical", "표면저항률", None, "ohm", "numeric", ["humidity_rh"], "ASTM D257"),
    ("electrical.dielectric_constant", "electrical", "유전율", "eps_r", "1", "numeric", ["frequency_hz"], "ASTM D150"),
    ("electrical.dielectric_strength", "electrical", "유전강도", None, "V/m", "numeric", ["thickness_m"], "ASTM D149"),
    ("electrical.dissipation_factor", "electrical", "손실계수", "tan_d", "1", "numeric", ["frequency_hz"], "ASTM D150"),
    ("electrical.comparative_tracking_index", "electrical", "비교트래킹지수(CTI)", "CTI", "V", "numeric", None, "IEC 60112"),
    ("electrical.band_gap", "electrical", "밴드갭", "Eg", "eV", "numeric", ["temperature_k"], None),
    ("electrical.piezoelectric_d33", "electrical", "압전상수 d33", "d33", "C/N", "numeric", None, None),
    # ── 광/복사 ────────────────────────────────────────────────────────────────
    ("optical.refractive_index", "optical", "굴절률", "n", "1", "numeric", ["wavelength_nm", "temperature_k"], None),
    ("optical.extinction_coefficient", "optical", "소광계수", "k", "1", "numeric", ["wavelength_nm"], None),
    ("optical.transmittance", "optical", "투과율", "T", "1", "numeric", ["wavelength_nm"], None),
    ("optical.reflectance", "optical", "반사율", "R", "1", "numeric", ["wavelength_nm"], None),
    # 어느 파장에서 투과가 기준치로 떨어지는가 — 기준 투과율을 조건에 안 적으면 값이 아니다.
    ("optical.uv_cutoff_wavelength", "optical", "UV 차단파장", "lambda_cut", "m", "numeric",
     ["transmittance_pct", "thickness_um"], None),
    ("optical.absorptance_solar", "optical", "태양흡수율", "alpha_s", "1", "numeric", None, "ASTM E903"),
    ("optical.emissivity_total", "optical", "전방사율", "eps", "1", "numeric", ["temperature_k"], "ASTM E408"),
    ("optical.emissivity_spectral", "optical", "분광방사율", None, "1", "numeric", ["wavelength_nm", "temperature_k"], None),
    ("optical.haze", "optical", "헤이즈", None, "1", "numeric", None, "ASTM D1003"),
    ("optical.gloss_60deg", "optical", "광택(60도)", None, "GU", "numeric", None, "ASTM D523"),
    ("optical.uv_resistance", "optical", "내자외선성", None, None, "categorical", None, None),
    # ── 화학/내구 ──────────────────────────────────────────────────────────────
    ("chemical.composition", "chemical", "화학조성", None, None, "categorical", None, None),
    ("chemical.corrosion_rate", "chemical", "부식률", None, "m/s", "numeric", ["environment", "temperature_k"], "ASTM G31"),
    ("chemical.oxidation_resistance", "chemical", "내산화성", None, None, "categorical", ["temperature_k"], None),
    ("chemical.chemical_resistance", "chemical", "내약품성", None, None, "categorical", ["reagent"], "ISO 175"),
    ("chemical.water_absorption_24h", "chemical", "수분흡수율(24h)", None, "1", "numeric", None, "ASTM D570"),
    ("chemical.water_absorption_saturation", "chemical", "포화수분흡수율", None, "1", "numeric", None, "ASTM D570"),
    ("chemical.moisture_absorption_equilibrium", "chemical", "평형흡습율", None, "1", "numeric", ["humidity_rh", "temperature_k"], None),
    # ── 내후성 계열. 정성 등급("excellent")만으로는 해석 입력이 안 된다.
    # 등급은 **노출 조건과 판정 기준을 함께 적어야** 다른 재료와 비교된다 —
    # UV는 램프가 다르면 시간이 비교되지 않으므로 조사량(MJ/m^2)이 1차 축이다.
    ("chemical.hydrolytic_stability", "chemical", "내가수분해성", None, None, "categorical",
     ["temperature_k", "humidity_pct", "duration_h", "criterion"], None),
    ("chemical.uv_ozone_resistance", "chemical", "내UV/오존성", None, None, "categorical",
     ["standard", "radiant_exposure_mj_m2", "duration_h", "criterion"], None),
    # 광열화·가수분해 속도상수 — 수명 예측의 본체다. 조건이 빠지면 자릿수가 통째로 달라진다.
    ("chemical.photodegradation_rate_constant", "chemical", "광열화 속도상수", "k_photo", "1/s", "numeric",
     ["wavelength_nm", "irradiance_w_m2", "temperature_k", "humidity_pct", "property"], None),
    ("chemical.hydrolysis_rate_constant", "chemical", "가수분해 속도상수", "k_hyd", "1/s", "numeric",
     ["temperature_k", "humidity_pct", "ph", "medium", "property"], None),
    # 시간이 아니라 **조사량**으로 적어야 램프가 달라도 비교된다(Pickett 2009).
    ("chemical.radiant_exposure_to_failure", "chemical", "판정도달 조사량", "H_fail", "J/m^2", "numeric",
     ["standard", "criterion", "wavelength_band_nm", "temperature_k"], None),
    ("chemical.outgassing_tml", "chemical", "아웃가싱 TML", "TML", "1", "numeric", None, "ASTM E595"),
    ("chemical.outgassing_cvcm", "chemical", "아웃가싱 CVCM", "CVCM", "1", "numeric", None, "ASTM E595"),
    ("chemical.ph_stability", "chemical", "pH 안정성", None, None, "categorical", None, None),
    ("chemical.galvanic_potential", "chemical", "갈바닉 전위", None, "V", "numeric", ["environment"], None),
    # ── 물리/수송/표면 ────────────────────────────────────────────────────────
    ("physical.density", "physical", "밀도", "rho", "kg/m^3", "numeric", ["temperature_k"], "ASTM D792"),
    ("physical.porosity", "physical", "기공률", None, "1", "numeric", None, None),
    ("physical.specific_surface_area", "physical", "비표면적", None, "m^2/kg", "numeric", None, "BET"),
    ("physical.water_vapor_transmission", "physical", "수증기투과율(WVTR)", "WVTR", "kg/(m^2*s)", "numeric", ["temperature_k", "humidity_rh"], "ASTM E96"),
    ("physical.gas_permeability_o2", "physical", "산소투과도", None, "mol/(m*s*Pa)", "numeric", ["temperature_k"], "ASTM D3985"),
    ("physical.gas_permeability_co2", "physical", "이산화탄소투과도", None, "mol/(m*s*Pa)", "numeric", ["temperature_k"], None),
    ("physical.gas_permeability_h2o", "physical", "수분투과도", None, "mol/(m*s*Pa)", "numeric", ["temperature_k"], None),
    ("physical.contact_angle_water", "physical", "물 접촉각", None, "deg", "numeric", None, None),
    ("physical.surface_energy", "physical", "표면에너지", None, "J/m^2", "numeric", None, None),
    ("physical.diffusion_coefficient", "physical", "확산계수", "D", "m^2/s", "numeric", ["species", "temperature_k"], None),
    # 투과도 P = D·S 이므로 확산계수만으로는 반응-확산 해석의 경계조건을 못 세운다.
    # 헨리 법칙 용해도(용존농도 = S·p)가 있어야 분압에서 막 내부 농도가 정해진다.
    ("physical.gas_solubility", "physical", "기체 용해도(헨리)", "S", "mol/(m^3*Pa)", "numeric",
     ["species", "temperature_k"], None),
    # ── 광물리(발광·소광) ─────────────────────────────────────────────────────
    # OLED 산소 소광 해석의 핵심. Stern-Volmer I0/I = 1 + k_q·tau0·[Q] 에서
    # tau0(무소광 여기수명)가 R/G/B 선택성을 결정한다 — 인광 us급 vs 형광 ns급.
    ("optical.excited_state_lifetime", "optical", "여기상태 수명", "tau_0", "s", "numeric",
     ["temperature_k", "matrix", "atmosphere"], None),
    # K_SV = k_q·tau0. 논문이 둘 중 어느 쪽을 인쇄하는지가 갈리므로 키를 나눈다.
    ("optical.stern_volmer_constant", "optical", "Stern-Volmer 소광상수", "K_SV", "1/Pa", "numeric",
     ["quencher", "temperature_k", "matrix"], None),
    ("optical.bimolecular_quenching_rate", "optical", "이분자 소광 속도상수", "k_q", "m^3/(mol*s)", "numeric",
     ["quencher", "temperature_k", "matrix"], None),
    ("optical.photoluminescence_quantum_yield", "optical", "광발광 양자수율", "PLQY", "1", "numeric",
     ["matrix", "atmosphere", "wavelength_nm"], None),
    # 소광 에너지가 3O2 -> 1O2 로 넘어가면 가역 소광이 비가역 광산화로 전이한다.
    # 가역 구간의 시한을 정하는 항이라 별도로 둔다.
    ("optical.singlet_oxygen_quantum_yield", "optical", "일중항 산소 양자수율", "Phi_Delta", "1", "numeric",
     ["matrix", "wavelength_nm"], None),
    # 광개시제 흡수대(365~405 nm)와 UV 리셋 액션 스펙트럼을 대조하는 데 쓴다.
    ("optical.molar_absorptivity", "optical", "몰흡광계수", "epsilon", "m^2/mol", "numeric",
     ["wavelength_nm", "solvent"], None),
    # ── 음향/제진 ──────────────────────────────────────────────────────────────
    ("acoustic.speed_of_sound", "acoustic", "음속", "c", "m/s", "numeric", ["temperature_k"], None),
    ("acoustic.impedance", "acoustic", "음향임피던스", "Z", "Pa*s/m", "numeric", None, None),
    ("acoustic.loss_factor", "acoustic", "제진 손실계수", "eta", "1", "numeric", ["frequency_hz", "temperature_k"], "ASTM E756"),
    ("acoustic.absorption_coefficient", "acoustic", "흡음계수", "alpha_a", "1", "numeric", ["frequency_hz"], "ISO 354"),
    # ── 자기 ──────────────────────────────────────────────────────────────────
    ("magnetic.relative_permeability", "magnetic", "비투자율", "mu_r", "1", "numeric", None, None),
    ("magnetic.saturation_magnetization", "magnetic", "포화자화", "Ms", "T", "numeric", ["temperature_k"], None),
    ("magnetic.coercivity", "magnetic", "보자력", "Hc", "A/m", "numeric", None, None),
    ("magnetic.remanence", "magnetic", "잔류자속밀도", "Br", "T", "numeric", None, None),
    ("magnetic.curie_temp", "magnetic", "큐리온도", "Tc", "K", "numeric", None, None),
    # ── 유변/가공 ──────────────────────────────────────────────────────────────
    ("rheological.melt_flow_index", "rheological", "용융흐름지수(MFI)", "MFI", "g/600s", "numeric", ["temperature_k", "load_kg"], "ISO 1133"),
    ("rheological.viscosity", "rheological", "점도", "eta", "Pa*s", "numeric", ["temperature_k", "shear_rate_1/s"], None),
    ("rheological.mold_shrinkage", "rheological", "성형수축률", None, "1", "numeric", None, "ISO 294-4"),
    ("rheological.gel_time", "rheological", "겔타임", None, "s", "numeric", ["temperature_k"], None),
    # ── 조성/구조 ──────────────────────────────────────────────────────────────
    ("structure.crystal_structure", "structure", "결정구조", None, None, "categorical", None, None),
    ("structure.grain_size", "structure", "결정립 크기", None, "m", "numeric", None, "ASTM E112"),
    ("structure.molecular_weight", "structure", "분자량(Mw)", "Mw", "kg/mol", "numeric", None, None),
    ("structure.crystallinity", "structure", "결정화도", None, "1", "numeric", None, None),
    ("structure.filler_content", "structure", "충전제 함량", None, "1", "numeric", None, None),
    # 도전입자·필러 입경. 결정립(grain_size)과 의미가 달라 별도 키로 둔다.
    ("structure.particle_diameter", "structure", "입자 직경", "d_p", "m", "numeric",
     ["particle_type"], None),
    # 코팅·도금·박막·계면반응층(IMC)의 두께. 유리 이온교환 깊이(mechanical.depth_of_layer)와
    # 의미가 달라 별도 키로 둔다.
    ("structure.layer_thickness", "structure", "층 두께", "t_layer", "m", "numeric",
     ["layer", "process"], None),
    # ── 접합·계면 (커버레이·테이프·CCL 선정의 핵심 지표. 기존엔 전용 키가 없어
    #    벤더 데이터시트 값이 notes 문자열에만 갇혀 있었다) ──────────────────────
    ("interface.peel_strength", "interface", "박리강도", None, "N/m", "numeric",
     ["temperature_k", "substrate", "angle_deg", "rate_mm/min"], "IPC-TM-650 2.4.9"),
    ("interface.lap_shear_strength", "interface", "중첩전단강도", None, "Pa", "numeric",
     ["temperature_k", "substrate"], "ASTM D1002"),
    ("interface.die_shear_strength", "interface", "다이쉬어 강도", None, "Pa", "numeric",
     ["temperature_k"], "MIL-STD-883 2019"),
    # PSA·테이프 선정은 박리력만으로 안 된다 — 초기 밀착(택)과 지속 하중(정적전단)이 함께 있어야
    # "잘 붙는데 흘러내리는" 조합을 걸러낼 수 있다.
    ("interface.tack", "interface", "택(초기점착력)", None, "N", "numeric",
     ["substrate", "rate_mm/min", "temperature_k"], "ASTM D6195 (loop) / D2979 (probe)"),
    ("interface.static_shear_holding", "interface", "정적전단 유지시간", None, "s", "numeric",
     ["load_kg", "area_mm2", "substrate", "temperature_k"], "ASTM D3654"),
    ("interface.wire_pull_strength", "interface", "와이어 풀 강도", None, "N", "numeric",
     ["wire_diameter_um", "loop_height_um"], "MIL-STD-883 2011"),
    ("mechanical.cure_shrinkage", "mechanical", "경화수축률", None, "1", "numeric",
     ["cure_schedule"], "ASTM D2566"),
    ("rheological.pot_life", "rheological", "가사시간(pot life)", None, "s", "numeric",
     ["temperature_k", "mix_ratio"], None),
    ("electrical.shielding_effectiveness", "electrical", "전자파 차폐효과", "SE", "dB", "numeric",
     ["frequency_hz", "thickness_m"], "ASTM D4935"),
    ("electrical.temperature_coefficient_resistance", "electrical", "저항온도계수(TCR)", "TCR",
     "1/K", "numeric", ["temperature_range_C"], "MIL-STD-202 Method 304"),
    ("thermal.thermal_resistance", "thermal", "열저항", "Rth", "K*m^2/W", "numeric",
     ["pressure_kPa", "thickness_m"], "ASTM D5470"),
    ("thermal.decomposition_time_t260", "thermal", "내열시간 T260", None, "s", "numeric",
     None, "IPC-TM-650 2.4.24.1"),
    # ── 광학 보강 ──────────────────────────────────────────────────────────────
    ("optical.abbe_number", "optical", "아베수", "nu_d", "1", "numeric", None, None),
    ("optical.birefringence", "optical", "복굴절", "dn", "1", "numeric",
     ["wavelength_nm"], None),
    # ── 화학강화 유리 (커버윈도우 강도 설계의 지배 인자) ──────────────────────
    ("mechanical.surface_compressive_stress", "mechanical", "표면압축응력(CS)", "CS", "Pa",
     "numeric", ["depth_um"], "ASTM C1422"),
    # 와이블 계수는 **재료 상수가 아니다.** 시편 수·시험 기하·유효면적·표면 이력에 종속된다 —
    # 같은 유리(Corning 2318)에서 강화 이력만 바뀌었는데 m이 2.68에서 32.95로 12배 움직였다.
    # 조건 없는 m은 값이 아니므로 축을 넓게 요구한다.
    # WLF 상수 — Prony 급수만으로는 기준온도에서만 쓸 수 있다. 마스터커브를 다른 온도로
    # 옮기려면 이 둘이 있어야 한다.
    #
    # **부호와 로그 밑이 논문마다 다르다.** 표준형은 log10 a_T = -C1(T-Tref)/(C2+T-Tref) 인데,
    # ln 을 쓰는 논문이 있고(그러면 C1이 2.303배로 보인다) 선두 마이너스를 식에 흡수한 논문도 있다.
    # 16차에 Jung 2019가 ln 을 쓰면서 자기 검산을 log10 기준 Ferry 규칙과 비교해 틀리는 것을 봤다.
    # 그래서 `log_base`와 `sign_convention`을 조건축으로 **요구한다** — 없으면 값이 아니다.
    ("mechanical.wlf_c1", "mechanical", "WLF 상수 C1", "C1", "1", "numeric",
     ["reference_temperature_k", "log_base", "sign_convention", "fit_r2"], None),
    ("mechanical.wlf_c2", "mechanical", "WLF 상수 C2", "C2", "K", "numeric",
     ["reference_temperature_k", "log_base", "sign_convention", "fit_r2"], None),
    # ── 구성모델 상수 다발. **항마다 단위가 달라** si_unit을 1로 두고
    # `conditions.term` 과 `unit_of_term` 에 정체를 적는다(darveaux_constant 선례).
    # 세트가 깨지면 곡선이 안 서므로 `set_id` 로 묶는다.
    #
    # Garofalo sinh: de/dt = A'[sinh(a*sigma)]^n exp(-Q/RT). 네 항의 단위가 1/s, 1/Pa, 무차원, J/mol.
    ("mechanical.garofalo_constant", "mechanical", "Garofalo sinh 크리프 상수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "component", "temperature_range_k",
      "stress_range_pa", "strain_rate_range_s", "set_id"], None),
    # 1차(천이) 크리프 상수. 2차(정상상태)와 다른 모델이다.
    ("mechanical.primary_creep_constant", "mechanical", "1차 크리프 상수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "temperature_range_k", "stress_range_pa", "set_id"], None),
    # Ramberg-Osgood: e = s/E + a(s/s0)^n. 항마다 단위가 다르다.
    ("mechanical.ramberg_osgood_constant", "mechanical", "Ramberg-Osgood 상수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "temperature_k", "set_id"], None),
    # 변형률 분해(SRRT/SRT). 성분마다 정체가 다르므로 term으로 가른다.
    ("mechanical.strain_partition_component", "mechanical", "변형률 분해 성분", None, "1", "numeric",
     ["term", "unit_of_term", "test_method", "strain_rate_s", "temperature_k", "set_id"], None),
    # 균열 개시·성장은 **모델 계수(darveaux_constant)가 아니라 그 모델의 출력 실측값**이다.
    ("mechanical.crack_initiation_cycles", "mechanical", "균열개시 사이클 수", "No", "1", "numeric",
     ["thermal_cycle_profile", "statistic", "solder_alloy", "negative_regression_intercept"], None),
    ("mechanical.crack_growth_rate", "mechanical", "균열성장률 da/dN", "da/dN", "m/cycle", "numeric",
     ["thermal_cycle_profile", "statistic", "solder_alloy"], None),
    # 경화 kinetics 다발(DiBenedetto λ·C3, Kamal k/m/n, Vogel ΔH 등).
    # **Vogel ΔH를 chemical.activation_energy 에 넣지 마라** — 660 kJ/mol이라 화학 Ea로 읽으면 틀린다.
    ("chemical.cure_model_constant", "chemical", "경화 모델 상수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "temperature_range_k", "set_id"], None),
    # 흡습 확산 모델 상수(전지수인자 D0 등). 확산계수 자체는 physical.diffusion_coefficient 다.
    ("physical.moisture_diffusion_constant", "physical", "흡습확산 모델 상수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "temperature_range_k", "set_id"], None),
    # secant CTE 다항식 계수. **계수를 대입해 CTE 값을 만들지 마라** —
    # 293 K 부근에서 항끼리 154~306배 상쇄돼 대입값의 유효숫자가 인쇄 자릿수보다 훨씬 적다.
    ("thermal.expansion_polynomial_coefficient", "thermal", "CTE 다항식 계수", None, "1", "numeric",
     ["term", "unit_of_term", "model", "reference_temperature_k",
      "temperature_range_k", "set_id"], None),
    ("mechanical.weibull_modulus", "mechanical", "와이블 계수 m", "m", "1", "numeric",
     ["strength_property", "test_geometry", "n_specimens", "stress_rate",
      "specimen_thickness_mm", "estimator", "surface_state"], "ASTM C1239"),
    # 마이어 경도는 **투영면적** 기준(H = P/(2a^2))이고 비커스 HV는 표면적 기준이다.
    # 둘의 비 2/1.8544 = 1.0785 를 우리가 곱하면 역산이므로 키를 따로 둔다.
    ("mechanical.hardness_meyer", "mechanical", "마이어 경도 H", "H", "Pa", "numeric",
     ["load_n", "dwell_s", "environment", "temperature_c"], None),
    ("mechanical.depth_of_layer", "mechanical", "이온교환 깊이(DOL)", "DOL", "m", "numeric",
     None, "ASTM C1422"),
]
# fmt: on


def all_definitions() -> list[dict]:
    """taxonomy를 dict 목록으로 반환."""
    keys = ("key", "domain", "name", "symbol", "si_unit", "value_type", "condition_axes", "test_standard")
    return [dict(zip(keys, row)) for row in _DEFS]


def seed_property_definitions(session: Session) -> dict:
    """property_definition을 멱등 upsert. 신규 삽입·기존 갱신 수를 반환."""
    from app.models import PropertyDefinition

    existing = {d.key: d for d in session.query(PropertyDefinition).all()}
    added = updated = 0
    for d in all_definitions():
        row = existing.get(d["key"])
        if row is None:
            session.add(PropertyDefinition(**d))
            added += 1
        else:
            changed = False
            for f in ("domain", "name", "symbol", "si_unit", "value_type",
                      "condition_axes", "test_standard"):
                if getattr(row, f) != d[f]:
                    setattr(row, f, d[f]); changed = True
            updated += changed
    session.commit()
    return {"added": added, "updated": updated, "total": len(_DEFS)}
