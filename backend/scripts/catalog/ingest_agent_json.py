#!/usr/bin/env python
# 에이전트가 수집한 데이터시트 JSON을 검증 후 카탈로그에 등록. 근거(출처·조건) 없는 값은 거부.
#
# 사용:
#   ingest_agent_json.py <dir|file...> [--apply]
#
# 검증 항목(하나라도 어기면 그 값은 건너뛰고 사유를 보고):
#   · property_key가 taxonomy에 존재하는가
#   · 단위가 정의 단위와 일치하는가
#   · 출처(url/doi/title)가 있는가 — 근거 없는 값은 저장 금지
#   · 물리적으로 가능한 범위인가(음수 밀도, PR 범위, 비율>1 등)
#   · 기존에 더 신뢰도 높은 값(tier 낮음)이 있으면 덮지 않는가
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import mcp_server as M  # noqa: E402
from app.db import SessionLocal  # noqa: E402
from app.models import Material, PropertyDefinition, PropertyValue  # noqa: E402

# 물리적으로 불가능한 값 차단(키 → (최소, 최대)).
RANGE = {
    "physical.density": (1.0, 25000.0),
    "mechanical.youngs_modulus": (1e3, 1.5e12),
    # [2026-08-28 · 46차 HA] 율속별 영률. **상한은 youngs_modulus 와 같게 두고 하한은 0 이다.**
    # 인쇄된 값을 하한 가드가 막은 사고가 일곱 번 났다(브리프 150·161 — Prony 두 번,
    # peel_strength, tack/static_shear_holding, lap/die_shear_strength, 포아송비, 열전도율).
    # 그때마다 결론이 같았다 — **새 키는 하한 0 으로 시작해라.** 율속 모듈러스는 특히 그렇다:
    # Tg 위 고무상에서 값이 두 자릿수 kPa 로 떨어지고(같은 논문 Fig7 의 130 °C 가 2.52 GPa 인데
    # 폼·엘라스토머 율속 계열은 1e5 Pa 대다), MPa 원값 오입력을 잡겠다고 1e3 을 두면
    # 그 대역을 통째로 자른다. 단위 오입력은 조건·notes 대조로 잡는다.
    "mechanical.youngs_modulus_at_rate": (0.0, 1.5e12),
    # [2026-08-19 · 42차 DA] 하한 0.0 → -1.0. **인쇄된 값을 범위 가드가 막는 사고 — 여섯 번째다**
    # (17·19차 Prony 상·하한, 21차 peel_strength·tack, 40차 인쇄된 0, 그리고 여기).
    # 포아송비는 **무차원이라 하한 0 이 단위 오입력을 하나도 못 잡는다** — 막는 것은 auxetic 재료뿐이다.
    # 열분해흑연(PG)의 basal 면은 실제로 음수이고, 제조사 시트(MINTEQ Pyroid HT)가 XY -0.18 을 인쇄한다.
    # 하한은 등방 탄성의 열역학 한계인 -1.0 으로 둔다.
    "mechanical.poisson_ratio": (-1.0, 0.5),
    "mechanical.tensile_strength": (1e3, 1e11),
    "mechanical.yield_strength": (1e3, 1e11),
    # 인장항복·인장강도와 같은 응력 갈래라 같은 가드를 쓴다. 하한 1e3 은 MPa 원값을
    # Pa 로 넣는 오입력을 잡는다(358 MPa 를 358 로 넣으면 걸린다).
    # 접착 갈래와 달리 **인쇄된 0 이 나올 수 없는 물성**이라 하한 0 규칙(161번)이 아니다 —
    # 전단강도 0 인 벌크재는 재료가 아니다.
    "mechanical.shear_strength": (1e3, 1e11),
    "mechanical.compressive_yield_strength": (1e3, 1e11),
    "mechanical.elongation_at_break": (0.0, 20.0),
    # 단면감소율·항복연신율은 **무차원 비율**이다. 원문이 예외 없이 % 로 인쇄하므로
    # 35 · 10.5 를 그대로 넣는 사고가 잦다 — 상한 1.0 이 그것을 잡는다.
    # 단면감소율의 물리 상한도 1 이다(파단면 면적이 음수가 될 수는 없다).
    # **하한은 0 이다** — 넥킹이 전혀 없는 취성재의 인쇄된 `0` 은 값이다(브리프 161번).
    "mechanical.reduction_of_area": (0.0, 1.0),
    "mechanical.elongation_at_yield": (0.0, 1.0),
    # [2026-08-19 · 43차 EC] 상한 3000 → 5e4. **인쇄된 값을 범위 가드가 막는 사고 — 일곱 번째다**
    # (17·19차 Prony, 21차 peel_strength·tack, 40차 인쇄된 0, 42차 DA 포아송비 하한, 그리고 여기).
    # 3000 W/(m·K) 는 **재료 상한으로도 낮다** — 동위원소 정제 다이아몬드가 3320, 단층 그래핀 면내가
    # 3000~5300 이다. 게다가 방열 갈래는 **소자 유효열전도율**을 같은 키에 담는다 —
    # Yang 2021 의 200 µm 베이퍼챔버가 면내 유효 11,914.9 W/(m·K) 를 인쇄하고(23.91 W/cm² 열유속),
    # 같은 논문의 3834.6 도 함께 걸렸다. 소자값은 조건과 notes 로 갈리지 가드로 막을 것이 아니다(브리프 455).
    # 상한 5e4 는 mW/(m·K) 원값 오입력(1000배)을 여전히 잡는다.
    "thermal.conductivity": (0.0, 5e4),
    "thermal.specific_heat": (10.0, 5000.0),
    "thermal.expansion_linear": (-1e-4, 5e-3),
    # MnZn 페라이트는 저주파에서 입계 효과로 겉보기 유전율이 1e5대까지 간다(TDK N48 = 140e3 @10 kHz).
    # CCTO·릴랙서 강유전체는 1e6도 나온다. 1e5로 막으면 정상값을 버린다 — 실제로 버렸다.
    "electrical.dielectric_constant": (1.0, 1e7),
    # 굴절률은 대역이 넓다. 금속·금속성 질화물(TiN 0.79 @633nm)은 가시광에서 n<1이고,
    # 실리콘은 400 nm에서 5.6까지 오른다. EUV·X선은 n=1−δ<1이다.
    # 좁게 잡으면 정상값을 버린다 — 실제로 c-Si와 TiN이 걸렸다.
    "optical.refractive_index": (0.01, 10.0),
    "optical.transmittance": (0.0, 1.0),
    "optical.haze": (0.0, 1.0),
    "optical.emissivity_total": (0.0, 1.0),
    "chemical.water_absorption_24h": (0.0, 1.0),
    "chemical.water_absorption_saturation": (0.0, 1.0),
    # 아래는 단위 오입력이 잦은 신규 키 — 범위 자체가 단위 검산 역할을 한다.
    # [2026-08-15 · 21차 Q2] 하한을 0.5 → 0 으로 내린다.
    # 하한 0.5 N/m 는 "N/mm 로 넣으면 1000배 작아진다"를 잡으려던 것인데,
    # **측정된 0 을 함께 잘랐다.** Park 2014 의 `0.00 N/cm` 는 단위 오입력이 아니라
    # "접착이 아예 안 됐다"는 실측이고, 그건 값이다.
    # 19차에 Prony 꼬리를 세 번 자른 것과 같은 함정 — **물리적으로 가능한 값을 범위로 막지 마라.**
    # 단위 오입력은 범위가 아니라 조건·notes 대조로 잡는다.
    "interface.peel_strength": (0.0, 5e5),              # N/m (N/mm로 넣으면 1000배 작아짐)
    # [2026-08-15 · 21차 T1] 하한 1e4 → 0. **이 사고가 다섯 번째다**
    # (17·19차 Prony, 21차 Q2 peel_strength 0.5, S2 tack/holding, 그리고 여기).
    # Rebholz 2016 결과절 verbatim — *"VL did not bond on zirconia (0 MPa)"* 라 실측이다.
    # **새 키는 하한 0 으로 시작해라.** 단위 오입력은 조건·notes 대조로 잡는다.
    "interface.lap_shear_strength": (0.0, 1e9),
    "interface.die_shear_strength": (0.0, 1e9),   # 인쇄된 0 = 접합 실패. 위와 같은 이유
    "physical.surface_energy": (1e-3, 1.0),   # J/m^2. mN/m 원값(15 등)이면 걸린다
    "electrical.shielding_effectiveness": (0.0, 150.0),
    "electrical.temperature_coefficient_resistance": (-1e-2, 1e-2),  # ppm/K 원값이면 걸린다
    # [76차] TCDk — **음수가 정상이다**(RO3010 −395 ppm/℃ = −3.95e-4). 하한 0 이면 인쇄값을
    # 막는다(42차 DA). ±1e-3 은 실측 최대 |395 ppm| 의 2.5배라 여유가 있고, ppm 원값 −395 를
    # 1/K 칸에 그대로 넣는 오입력은 잡는다.
    "electrical.temperature_coefficient_dielectric_constant": (-1e-3, 1e-3),
    "thermal.thermal_resistance": (1e-6, 1.0),
    # 옛 `thermal.decomposition_time_t260` 의 가드를 그대로 옮겼다(39차 BA의 키 통합).
    "thermal.time_to_delamination": (1.0, 1e5),         # s (시간 단위면 걸린다)
    # 구간 총 팽창률은 **비율**이다. 원문이 % 로 인쇄하므로 2.46 을 그대로 넣는 사고가 잦다 —
    # 상한 1.0 이 그것을 잡는다(cure_shrinkage 와 같은 가드).
    "thermal.expansion_total": (0.0, 1.0),
    "optical.abbe_number": (10.0, 120.0),
    "optical.birefringence": (-1.0, 1.0),   # 음의 1축 결정(사파이어 등)은 Δn<0
    "mechanical.surface_compressive_stress": (1e6, 5e9),  # Pa (MPa 원값이면 걸린다)
    "mechanical.depth_of_layer": (1e-9, 1e-3),            # m (µm 원값이면 걸린다)
    # [2026-08-15 · 21차 S2] 하한 1e-3 → 0. **인쇄된 0 은 값이다.**
    # Athawale 1995 가 택·유지시간을 `0` 으로 인쇄한다 — "붙지 않았다"는 실측이다.
    # **이 사고가 네 번째다**(17·19차 Prony 상·하한, 21차 peel_strength 하한 0.5).
    # 단위 오입력(gf 원값)은 범위가 아니라 조건·notes 대조로 잡아라.
    "interface.tack": (0.0, 1e3),                         # N (gf 원값이면 걸린다)
    "interface.static_shear_holding": (0.0, 1e8),         # s. 인쇄된 0 = 즉시 미끄러짐. 폼 양면테이프는 5,000 h(1.8e7 s)도 나온다
    "interface.wire_pull_strength": (1e-4, 1e2),          # N (gf 원값이면 걸린다)
    "mechanical.cure_shrinkage": (0.0, 0.5),              # 비율 (% 원값이면 걸린다)
    "rheological.pot_life": (1.0, 1e7),                   # s (분 단위면 걸린다)
    # 초탄성 계수는 음수도 정상이다(Mooney-Rivlin C10<0). 자릿수만 본다.
    "mechanical.hyperelastic_coefficient": (-1e9, 1e9),
    # 모델마다 의미가 달라(Ogden alpha 1~80, 8-chain N은 10^2~10^5) 좁은 범위 가드는 무의미하다.
    # 무차원이라 단위 오입력도 못 잡는다 — 자릿수 사고만 막는다.
    "mechanical.hyperelastic_exponent": (-1e6, 1e6),
    "mechanical.prony_shear_modulus": (1.0, 1e11),
    # 마스터커브는 WLF 시프트로 아래로 1e-16 s, 위로 1e14 s(≈3백만 년)까지 간다.
    # 물리적 완화시간이 아니라 시간·온도 등가로 확장한 피팅 파라미터라 양쪽을 넓게 둔다.
    # **Prony 완화시간은 물리적 완화시간이 아니라 마스터커브를 덮는 피팅 항이다.**
    # 상한도 하한도 급수를 자른다. 17차에 상한 1e16이 31항을, 19차에 하한 1e-20이 2항을,
    # 그리고 상한 1e21이 Springer ECA의 32~35항을 잘랐다. **세 번 같은 사고가 났다.**
    # 피팅 항에 물리적 범위검사를 걸면 안 된다 — 범위를 아주 넓게 두고 세트 정합성으로 검사한다.
    # (19차 잔재)
    # 10^-22·10^-25 두 항이 하한 1e-20에 걸려 조용히 빠졌고, 가중치는 17항인데
    # 완화시간만 15항인 반쪽 세트가 남았다. 무결성 검사는 '들어오지 않은 행'을 못 본다.
    # TTS로 20 decade를 덮는 급수는 1e17~1e19 s 항을 정상적으로 포함한다(Springer 2020·Chiu 2018).
    # 상한을 1e16으로 두면 **급수의 꼬리가 잘려 세트가 못 쓰게 된다** — 17차에 31항이 잘렸다.
    "mechanical.prony_relaxation_time": (1e-40, 1e40),
    # ── 43차 EE 신규 키 ──────────────────────────────────────────────────────
    # **하한은 전부 0(또는 물리적으로 음수가 되는 것만 음수)으로 시작한다** —
    # 인쇄된 값을 범위 가드가 막은 사고가 여섯 번 났다(브리프 150·161). 단위 오입력은
    # 범위가 아니라 조건·notes 대조와 검사기의 물리 검산으로 잡는다.
    #
    # (BH)max 는 J/m^3 다. kJ/m^3 원값(414)이나 MGOe 원값(52)을 그대로 넣으면
    # 상한이 아니라 **integrity_check 의 (BH)max <= Br^2/(4*mu0) 검산**이 잡는다 —
    # 자릿수가 세 자리 작아지면 그 부등식은 오히려 통과하므로, 여기 상한은 자릿수 사고만 본다.
    # 상한 1e6 J/m^3 = 1000 kJ/m^3 — 알려진 어떤 영구자석도 500 kJ/m^3 을 못 넘는다.
    "magnetic.energy_product_max": (0.0, 1e6),
    "mechanical.puncture_strength": (0.0, 1e5),          # N (gf 원값이면 자릿수로 걸린다)
    # 양수 = 수축. 가열로 늘어나는 필름이 있어 하한이 음수다. 상한 1 은 % 원값(3.0)을 잡는다.
    "thermal.heat_shrinkage": (-1.0, 1.0),
    "physical.air_permeability_gurley": (0.0, 1e6),      # s
    # 부호가 음수인 수지가 있다(폴리스티렌). cm^2/dyne 원값이면 정확히 10 배 작아지는데
    # 범위로는 못 잡는다 — 자릿수만 본다(PC 7.2e-11 · PMMA 6.0e-12 · 유리 2~3e-12).
    "optical.stress_optical_coefficient": (-1e-7, 1e-7),
    "interface.tensile_adhesion_strength": (0.0, 1e9),   # Pa. lap_shear 와 같은 가드
    "mechanical.lankford_r_value": (0.0, 20.0),          # 무차원. Mg 합금이 5 대까지 간다
    "thermal.dilatometric_softening_point": (200.0, 3000.0),   # K (섭씨 원값이면 걸린다)
    "mechanical.abrasion_factor": (0.0, 1e4),            # BSC7 = 100 기준 상대값
    "mechanical.hardness_ball_indentation": (1e3, 1e11),  # Pa (N/mm^2 원값이면 걸린다)
    # ── 44차 FD 신규 키 ──────────────────────────────────────────────────────
    # 점도 기준온도는 K 다. **섭씨 원값이면 걸린다** — 이 갈래는 원문이 예외 없이 °C 로
    # 인쇄하므로(467~1700 °C) 환산을 빼먹는 사고가 정확히 여기서 난다.
    # 하한 300 K 는 상온 아래를 막고, 상한 3000 K 는 석영(작업점 ~2200 K)까지 통과시킨다.
    "thermal.viscosity_reference_temperature": (300.0, 3000.0),
    # ── 45차 GC 신규 키 ──────────────────────────────────────────────────────
    # 중량감소율은 **비율**이다. 원문이 예외 없이 % 로 인쇄하므로(43 -> 0.43) 그대로 넣는
    # 사고가 여기서 난다 — 상한 1.0 이 그것을 잡고, 그 1.0 은 물리 상한이기도 하다
    # (가진 것보다 더 잃을 수는 없다). **하한은 음수다** — 알칼리 환경에서 재석출로
    # 질량이 느는 경우가 실재한다(AGY 본문). 좁게 잡아 인쇄값을 막지 않는다(§150·161).
    "chemical.durability_mass_loss_fraction": (-1.0, 1.0),
    # 단위면적당 감소량은 kg/m^2 다. 시트가 mg/cm^2 로 인쇄하므로 x1e-2 해야 하는데,
    # 원값을 그대로 넣으면 100 배가 된다. 상한 1e2 kg/m^2 = 10 g/cm^2 는 유리를 4 cm
    # 두께로 녹인 양이라 물리적으로 불가능하고, 큰 칸(120 mg/cm^2)의 원값 오입력을 잡는다.
    # 작은 칸(0.8)은 범위로 못 잡힌다 — 그건 조건·notes 대조가 잡을 몫이다.
    "chemical.durability_mass_loss_per_area": (-1.0, 1e2),
    # ── 47차 ID 신규 키 ──────────────────────────────────────────────────────
    # **하한은 전부 0(물리적으로 음수가 되는 것만 음수)이다** — 인쇄된 값을 하한 가드가 막은
    # 사고가 일곱 번 났다(브리프 150·161). 단위 오입력은 조건·notes 대조로 잡는다.
    #
    # 단조 경화지수는 무차원이라 **가드가 단위를 못 잡는다** — 자릿수만 본다.
    # 상한 5.0 은 `0.77` 을 `77` 로 넣는 퍼센트 사고를 잡고, 하한 -1.0 은 연화(음의 지수)를
    # 인쇄하는 모델을 통과시킨다. 형제 `cyclic_*` 에는 가드가 없다 —
    # 새로 좁게 걸어 옛 값을 소급으로 막지 않으려고 이쪽만 넣는다.
    "mechanical.monotonic_strain_hardening_exponent": (-1.0, 5.0),
    # 소성 파단변형률은 **무차원 비율**이다(% 를 100 으로 나눈다). 상한은 `elongation_at_break`
    # 와 같은 20.0(2000 %) — 소성분이 총 연신을 넘을 수 없으니 형제보다 넓힐 이유가 없다.
    # **하한은 0 이다** — 소성변형 없이 깨지는 취성재의 인쇄된 `0` 은 값이다(§161).
    "mechanical.plastic_strain_at_break": (0.0, 20.0),
    # 압축탄성계수는 Pa 다. 상한은 `youngs_modulus` 와 같게 두고 **하한은 0** 이다 —
    # 46차 HA 가 율속 모듈러스에서 짚은 그대로다. 폼·겔의 압축계수는 두 자릿수 kPa 대라
    # MPa 원값을 잡겠다고 1e3 을 두면 그 대역을 통째로 자른다.
    "mechanical.compressive_modulus": (0.0, 1.5e12),
    # 지정 변형률 응력은 Pa 다. 상한은 `tensile_strength` 와 같은 1e11.
    # **하한은 0** — psi 원값(100)을 잡겠다고 1e3 을 두면 실제로 kPa 대인 연질 SBC 를 자른다
    # (Kraton D1161 의 300 % 모듈러스가 100 psi = 6.9e5 Pa 인데, 더 연한 등급은 더 내려간다).
    "mechanical.tensile_stress_at_strain": (0.0, 1e11),
    # ── 58차 TA 신규 키 ──────────────────────────────────────────────────────
    # **하한은 전부 0 이다** — 인쇄된 값을 하한 가드가 막은 사고가 일곱 번 났다(브리프 150·161).
    #
    # 탄성 컴플라이언스는 1/Pa 다. **상한이 여기서 실제로 일을 한다** — 원문이 `10^-12 m^2/N`
    # 배수로 인쇄하는데 추출에서 지수 부호가 죽는 갈래라(브리프 9), 배수를 안 곱한 `7.4` 가
    # 그대로 들어오는 것이 이 키의 대표적 사고다. 상한 1e-3 은 E = 1 kPa 에 해당해
    # 가장 무른 겔까지 통과시키면서 `7.4` 는 잡는다.
    "mechanical.elastic_compliance": (0.0, 1e-3),
    # 내아크성은 초다. ASTM D 495 는 420 초에서 시험을 끝내는 것이 관행이라 상한을 넉넉히
    # 1e4 로 둔다. **하한 0** — 즉시 트래킹되는 시편의 인쇄된 값을 막지 않는다.
    "electrical.arc_resistance": (0.0, 1e4),
    # 콘칼로리미터 넷. 착화시간은 초(무염 시편은 인쇄된 상한이 없어 1e5).
    "thermal.time_to_ignition": (0.0, 1e5),
    # 열방출률은 W/m^2 다. **kW/m^2 원값 오입력을 하한으로 잡을 수 없다** — 168.6 도 물리적으로
    # 가능한 값이라 0.1686 kW/m^2 짜리 재료와 구별이 안 된다. 그건 조건·notes 대조가 잡을 몫이다.
    # 상한 1e8(= 100 MW/m^2)은 어떤 콘칼로리미터도 못 내는 값이라 자릿수 사고만 잡는다.
    "thermal.heat_release_rate": (0.0, 1e8),
    # 유효연소열은 J/kg. 상한 1e9 는 수소(1.4e8 J/kg)의 일곱 배라 순수 자릿수 가드다.
    "thermal.heat_of_combustion": (0.0, 1e9),
    # 평균 연기소멸면적은 m^2/kg. 그을음이 많은 방향족 수지가 1,000 m^2/kg 대까지 간다.
    "thermal.smoke_extinction_area": (0.0, 1e5),
    #
    # **`physical.density_model_constant` 에는 가드를 걸지 않았다.** 형제 모델상수 키
    # (`viscosity_model_constant`·`moisture_diffusion_constant`·`cure_model_constant`)가 전부 무가드다 —
    # 항마다 단위와 부호가 달라 한 범위로 묶을 수 없다(Landesfeind p3 는 -1.35e-3 로 음수다).
    # 좁게 새로 걸면 형제와 규약이 갈린다(브리프 612).
}
# Material.category도 고정 어휘 — 에이전트 표기를 매핑한다.
# **`molecular` 은 48차 JC 가 열었다.** Ashby 구조재 계통수 여섯에는 *분자로 특성화되는*
# 기능재의 집이 없었다 — OLED 발광체·호스트·전하수송체, 사이클로메탈화 Ir/Pt/Pd/Cu 착체,
# 포르피린 색소, 분자결정. 물성이 HOMO/LUMO·삼중항·PLQY·발광파장이지 E·sigma 가 아니다.
# 172종이 `polymer`(164)·`composite`(10) 에 들어 있었다(migration a5b6c7d8e9f0).
#
# **경계** — 레코드가 *분자*를 말하면 `molecular`, *층/필름*을 말하면 그 층의 벌크 어휘다.
# `OLED Emitter Layer` 처럼 E·인장·밀도를 가진 균질층 대표값은 `polymer` 로 남는다.
# 원소 탄소(흑연·CNT·그래핀·카본블랙·탄소섬유)는 `ceramic` 이다 — 단상이라 복합재가 아니고,
# Ashby 계통수가 탄소를 두는 자리다. **`carbon` 이라는 값은 만들지 않았다**(§419).
# 어휘를 늘리면 세 곳을 같이 고쳐야 한다(§466) — 여기 · `integrity_check` · 프런트 선택지.
CAT_OK = {"metal", "polymer", "rubber", "composite", "ceramic", "foam", "molecular"}
CAT_MAP = {"ceramics": "ceramic", "glass": "ceramic", "semiconductor": "ceramic",
           "organic": "polymer", "plastic": "polymer", "resin": "polymer",
           "elastomer": "rubber", "alloy": "metal", "adhesive": "polymer",
           "film": "polymer", "laminate": "composite", "liquid": "polymer",
           # `organic` 은 여기 못 넣는다 — 유기 고분자도 organic 이라 뜻이 갈린다.
           "small_molecule": "molecular", "organometallic": "molecular",
           "molecule": "molecular", "complex": "molecular", "dye": "molecular",
           "carbon": "ceramic", "graphite": "ceramic"}


def norm_cat(c: str | None) -> str:
    c = (c or "composite").strip().lower()
    return c if c in CAT_OK else CAT_MAP.get(c, "composite")


# Source.kind는 DB 제약(ck_source_kind)이 있는 고정 어휘 — 에이전트 표기를 매핑한다.
KIND_OK = {"journal", "book", "database", "datasheet", "computed", "standard", "web",
           "patent", "other"}
KIND_MAP = {"paper": "journal", "article": "journal", "publication": "journal",
            "handbook": "book", "textbook": "book", "spec": "standard",
            "specification": "standard", "brochure": "datasheet",
            "technical_data": "datasheet", "tds": "datasheet", "catalog": "datasheet",
            "website": "web", "webpage": "web", "report": "other",
            # 67차까지 특허가 "other" 로 떨어졌다 — 오버코트·실링재의 정체를 특허로만
            # 확정했는데 kind 로 되찾을 수 없었다. 어휘를 늘렸으니 그대로 통과시킨다.
            "patents": "patent", "patent_application": "patent", "특허": "patent"}


def norm_kind(k: str | None) -> str:
    k = (k or "datasheet").strip().lower()
    return k if k in KIND_OK else KIND_MAP.get(k, "other")


def pick_publisher(src: dict) -> str | None:
    """출처의 발행처. `publisher` 와 `manufacturer` 둘 다 받는다.

    45차 GB 가 짚었다 — 로더가 `manufacturer` 만 읽는데, 배치 지시문은 `publisher` 라 적으라
    했다. **그래서 JSON 에 적어도 조용히 사라졌다.** DB 컬럼 이름이 `source.publisher` 라
    배치가 그쪽을 쓰는 것이 자연스럽고, MCP 인자 이름이 `source_manufacturer` 라 그쪽도 맞다.
    어느 쪽이 옳으냐를 정하는 대신 **둘 다 받는다** — 이 갈림이 값을 버리게 둘 이유가 없다.
    실측(2026-08-22) — datasheet 출처 1,100건 중 434건이 publisher 가 비어 있다.
    """
    for k in ("publisher", "manufacturer"):
        v = src.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


# 비율 물성인데 1을 넘으면 퍼센트 오입력 의심(엘라스토머 연신율은 예외로 20까지 허용).
PCT_SUSPECT = {"chemical.water_absorption_24h", "chemical.water_absorption_saturation",
               "optical.transmittance", "optical.haze", "optical.emissivity_total"}


# method는 고정 어휘다. 에이전트가 시험법 서술("wire tensile test")을 넣는 일이 잦은데,
# 그 서술은 버리기 아까우므로 conditions.test_method로 옮기고 method는 어휘로 정규화한다.
METHOD_OK = {"measured", "handbook", "computed", "estimated"}
METHOD_MAP = {"datasheet": "measured", "experiment": "measured", "experimental": "measured",
              "test": "measured", "derived": "computed", "calculated": "computed",
              "simulated": "computed", "simulation": "computed", "estimate": "estimated",
              "typical": "measured", "spec": "measured", "book": "handbook",
              "literature": "handbook", "database": "handbook",
              # 피팅·가정은 측정이 아니다. 'assumed'가 measured로 들어가면 논문이 "측정하지 않았다"고
              # 밝힌 값이 실측으로 둔갑한다(SAC305 Johnson-Cook m=1.0이 실제로 그렇게 들어왔다).
              "fitted": "computed", "fit": "computed", "inverse": "computed",
              "assumed": "estimated", "assumption": "estimated",
              # **그림에서 읽은 값은 실측이 아니다.** 조건에 남겨도 method 가 measured 면
              # 인쇄 실측과 구별이 안 된다(40차 BF).
              "digitized": "digitized", "digitised": "digitized", "graph": "digitized",
              "curve": "digitized", "readoff": "digitized"}


# **구간의 중앙값은 계산값이다** — notes 가 그렇게 밝히면 method 를 강제로 computed 로 내린다.
# 41차에 실측했다: 중앙값 표기 379행 중 210행이 measured/handbook 이었다(브리프 451).
# 검사기로 사후에 잡으면 배치가 도는 동안 계속 쌓인다 — **적재 단계에서 막는 것이 맞다.**
_MIDPOINT = re.compile(r"중간값|중앙값|midpoint of|mid-?point of")
# **부정문이 오탐을 낸다 — 브리프 451 을 지킨 배치가 오히려 벌을 받았다**(43차 EE).
# 451 을 읽은 배치는 근거에 "구간의 중앙값은 만들지 않았다" 라고 적는다. 그 한 줄 때문에
# **인쇄된 상·하한 실측이 computed 로 강등됐다** — EE 가 자기 행 7개에서 발견했고,
# 거슬러 보니 ED-3 의 Y30H-1 Br 상단 `0.40 T`(인쇄된 구간 상단)도 같은 이유로 computed 였다.
# 즉 이 가드는 **자기를 지킨 배치만 골라 틀리게 만든다.**
# 매치 뒤 24자 안에 부정어가 있으면 그 매치는 주장이 아니다. 부정 아닌 매치가 하나라도
# 있어야 강등한다. 놓친 것은 integrity_check 의 같은 판정이 파동 끝에 잡는다
# (**오탐은 아무도 못 잡지만 오미는 검사기가 잡는다** — 그래서 이 방향이 맞다).
# **부정어의 위치가 언어마다 반대다** — 한국어는 뒤("중앙값은 만들지 **않았다**"),
# 영어는 앞("we did **not** take the midpoint of"). 양쪽을 다 봐야 한다.
_MID_NEG_AFTER = re.compile(r"않|아니|없|금지")
_MID_NEG_BEFORE = re.compile(r"not |no |never |n't |without ", re.I)


def asserts_midpoint(notes) -> bool:
    """notes 가 '이 값이 구간의 중앙값이다' 라고 **주장**하면 True. 부정문은 세지 않는다."""
    s = str(notes or "")
    return any(not _MID_NEG_AFTER.search(s[m.end():m.end() + 24])
               and not _MID_NEG_BEFORE.search(s[max(0, m.start() - 24):m.start()])
               for m in _MIDPOINT.finditer(s))


def force_computed_if_midpoint(method: str, notes) -> tuple[str, bool]:
    """중앙값이면 (computed, True). 그 외에는 그대로."""
    if method in ("measured", "handbook") and asserts_midpoint(notes):
        return "computed", True
    return method, False


VISCOSITY_KEY = "thermal.viscosity_reference_temperature"


def viscosity_order_violations(props: list) -> list:
    """한 재료 항목 안의 점도 기준온도가 물리 순서를 어기는지 본다(브리프 431).

    유리의 점도는 온도가 오르면 **단조로 내려간다.** 그래서 지정 점도가 높을수록
    그 점도에 도달하는 온도는 낮다 — 변형점(10^14.5) < 서냉점(10^13) <
    리틀턴 연화점(10^7.6) < 작업점(10^4). 한 유리 안에서 이 순서가 뒤집히면
    **열 배정이 틀린 것**이지 값이 아니다(EAGLE XG 는 669 < 722 < 972 로 성립한다).

    반환은 위반 쌍의 설명 문자열 목록. 비어 있으면 통과다.
    **검사기로 잡을 것을 적재기로 막는다**(브리프 455) — 사후 검사는 이미 들어온 것만 본다.
    """
    pts = []
    for pr in props:
        if pr.get("key") != VISCOSITY_KEY or pr.get("value") is None:
            continue
        cond = as_cond(pr.get("conditions"))
        lg = cond.get("viscosity_log10_poise")
        if lg is None:
            continue
        try:
            pts.append((float(lg), float(pr["value"])))
        except (TypeError, ValueError):
            continue
    out = []
    for i, (lg_a, t_a) in enumerate(pts):
        for lg_b, t_b in pts[i + 1:]:
            if lg_a == lg_b:
                continue
            hi, lo = ((lg_a, t_a), (lg_b, t_b)) if lg_a > lg_b else ((lg_b, t_b), (lg_a, t_a))
            if hi[1] >= lo[1]:
                out.append(f"log10eta {hi[0]} 에서 {hi[1]:.2f} K 인데 "
                           f"log10eta {lo[0]} 에서 {lo[1]:.2f} K — 점도가 높은 쪽이 더 뜨겁다")
    return out


def norm_method(raw) -> tuple[str, str | None]:
    """(정규화된 method, 원문 서술 또는 None)."""
    s = (str(raw) if raw is not None else "").strip()
    if not s:
        return "measured", None
    low = s.lower()
    if low in METHOD_OK:
        return low, None
    if low in METHOD_MAP:
        return METHOD_MAP[low], None
    # 자유 서술 — 계산임을 밝히면 computed, 아니면 측정으로 보고 서술은 보존한다.
    m = "computed" if re.search(r"comput|calcul|simulat|derived|추정|계산", low) else "measured"
    return m, s


def norm_tier(raw) -> int:
    """'tier3' · '3' · 3 을 모두 받는다. 범위 밖은 3(데이터시트급)으로."""
    m = re.search(r"[1-5]", str(raw if raw is not None else 3))
    return int(m.group(0)) if m else 3


def pick_notes(pr: dict) -> str | None:
    """`note`와 `notes`를 둘 다 받는다.

    브리프의 출력 예시는 `notes`인데 로더는 `note`만 읽고 있었다. 근거 문구가 조용히
    사라졌다 — 최근 인제스트분의 37%가 notes 없이 들어갔다. 값은 남고 "왜 그 값인가"만
    없어지는 유실이라 무결성 검사에도 안 걸린다. 오탈자 하나가 이 카탈로그에서 가장
    값진 부분(열 머리글 확인·환산 과정·등급 불일치 사유)을 지우고 있었다.

    `uncertainty`도 register_property가 받지 않으니 ± 값은 notes 본문에 넣어야 산다.
    """
    for k in ("note", "notes"):
        v = pr.get(k)
        if v:
            return str(v)
    return None


def pick_tier(pr: dict) -> int:
    """신뢰등급을 읽는다 — `tier`와 `quality_tier`를 **둘 다** 받는다.

    예전엔 `tier`만 봤다. DB 컬럼명이 quality_tier라 산출 형식 예시도 그쪽을 쓰고 있었고,
    그래서 tier1로 적어 보낸 값이 조용히 tier3으로 떨어졌다 — 실측이 데이터시트급으로
    강등되면 대표값 선택이 뒤집히고, tier4로 적은 가정값은 정합성 검사를 위반한다.
    """
    for k in ("tier", "quality_tier"):
        if pr.get(k) is not None:
            return norm_tier(pr[k])
    return 3


def as_cond(raw) -> dict:
    """조건을 dict로. 서술 문자열이면 detail 필드에 담는다."""
    if isinstance(raw, dict):
        return dict(raw)
    if isinstance(raw, str) and raw.strip():
        try:
            d = json.loads(raw)
            return dict(d) if isinstance(d, dict) else {"detail": raw.strip()}
        except Exception:
            return {"detail": raw.strip()}
    return {}


def unit_key(u: str) -> tuple:
    """단위를 비교 가능한 형태로. 곱 순서만 다른 표기를 같게 본다.

    `m^2*K/W`와 `K*m^2/W`는 같은 단위인데 문자열 비교로는 다르다고 나온다.
    분자·분모를 각각 정렬한 다중집합으로 비교하므로 기호가 다르면(mN/m vs J/m^2)
    여전히 걸린다 — 실제 단위 오입력을 잡는 기능은 그대로 남는다.
    """
    s = (u or "").replace(" ", "")
    num, _, den = s.partition("/")
    split = lambda p: tuple(sorted(t for t in p.replace("(", "").replace(")", "").split("*") if t))
    return (split(num), split(den))


def cond_sig(cond) -> str:
    """조건을 비교 가능한 서명으로. 표기 순서·타입 차이를 흡수한다.

    조건이 서술 문자열로 오는 경우가 잦은데(에이전트가 dict 대신 문장을 넣는다),
    이때 빈 서명으로 뭉개면 서로 다른 측정이 같은 조건으로 판정돼 덮어쓰기가 난다.
    """
    if isinstance(cond, str):
        s = cond.strip()
        try:
            cond = json.loads(s)
        except Exception:
            return s          # 서술 문자열 자체를 서명으로 쓴다
    if not isinstance(cond, dict) or not cond:
        return ""
    return json.dumps({k: str(v) for k, v in sorted(cond.items())}, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
# 명시적 정정 경로 (48차 JA) — **적재기가 기존 행을 고칠 수 있는 유일한 길**
# ══════════════════════════════════════════════════════════════════════════════
# 브리프 314 가 남긴 제약이다 — *"적재기는 UPDATE 를 못 한다"*. 그래서 배치가 **이미 든 값이
# 틀렸음을 증명해도** notes 나 브리프에 적어 두고 지나갔다(47차 IB 의 Cai Fig.14 93행,
# 44차 FC 의 재료 199 두 행, 46차 HC 의 2290 세트). 한 파동에만 세 번 걸렸다.
#
# **"덮어쓰지 않는다" 는 보호장치를 없애지 않는다.** 같은 재료·같은 키에 값이 또 오면
# 지금처럼 삽입하거나 건너뛴다 — 그 경로는 손대지 않았다. 정정은 JSON 이 **`corrections`
# 배열로 정정임을 선언**했을 때만 일어난다. 암묵적 정정은 없다.
#
# 선언 형식 ────────────────────────────────────────────────────────────────────
#   {"corrections": [
#     {"target": {"property_value_id": 1499},          ← 행 id 로 못박거나
#      "target": {"material_id": 199, "property_key": "electrical.dielectric_constant",
#                 "conditions": null, "value": 6.6},   ← 재료+키+조건으로 유일하게 걸거나
#      "reason": "왜 고치는지 — 없으면 거부한다",
#      "evidence": "등급을 올릴 때만 추가로 요구한다",
#      "set": {"quality_tier": 4, "conditions": {...}, "notes": "..."}}]}
#
# 거부 조건 ────────────────────────────────────────────────────────────────────
#   · 대상 미지정 · 대상 0건 · **대상 2건 이상**(어느 행인지 우리가 고르면 그건 우리 판정이다)
#   · 사유 없음(10자 미만) · 고칠 것 없음 · 정정 불가 필드(아래)
#   · 새 값이 단위·범위·퍼센트 가드를 못 넘음 — **삽입과 같은 가드를 통과해야 한다**
#   · 정정 후 같은 (재료·키·출처·조건) 행이 이미 있음(중복 생성 방지)
#
# 되돌리기 ─────────────────────────────────────────────────────────────────────
#   옛 값을 지우지 않는다. 바뀐 칸마다 `<칸>_before_correction` 을 조건에 남긴다.
#   선례 — 43차 EE 의 `method_restored`, 44차 FD 의 `tier_before_correction`·
#   `wavelength_nm_before_correction`. 그리고 `correction_reason`·`corrected_by` 로
#   **왜·누가**를 값과 함께 남긴다. 이게 있어야 병합기가 운영 행을 찾을 수 있다(아래 참조).

# 정정할 수 있는 칸. **`property_key` 와 `material_id` 는 여기 없다** —
# 그건 정정이 아니라 **이동**이고, 물성 0행이 되는 재료를 검사기가 어떻게 볼지(묘비 규약)가
# 먼저 정해져야 한다(46차 HC 의 2290→36). 이동 경로는 이 배치에서 만들지 않는다.
CORRECTABLE = {"value", "value_text", "unit", "method", "quality_tier", "conditions", "notes"}
# 되돌리기 표시가 **컬럼용과 조건칸용으로 같은 이름 공간**을 쓴다. 이 이름들이 조건 칸으로도
# 쓰이면(라이브에 `conditions.method` 가 639행 있다) 병합기가 조건 칸의 표시를 컬럼의 옛 값으로
# 읽는다 — 그러면 정정을 못 찾고 운영에 새 행을 만든다(52차 NA 실측 483행).
COLUMN_MARKER_NAMES = {"value", "value_text", "unit", "method", "tier", "notes"}
# 정정 사유는 한 줄이라도 문장이어야 한다. "수정"·"fix" 한 단어는 사유가 아니다.
REASON_MIN = 10


def _num_eq(a, b) -> bool:
    """부동소수 비교. 인쇄 자릿수 차이가 아니라 **같은 수인가**만 본다."""
    if a is None or b is None:
        return a is b
    a, b = float(a), float(b)
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def match_targets(s, tgt: dict, by_name: dict) -> list:
    """정정 대상 행을 찾는다. 주어진 축을 전부 AND 로 건다.

    **여러 행에 걸리면 부르는 쪽이 거부한다** — 여기서는 걸린 것을 다 돌려준다.
    """
    from app.models import Source          # 지역 임포트: 이 함수만 쓴다
    if tgt.get("property_value_id") is not None:
        return s.query(PropertyValue).filter(
            PropertyValue.id == int(tgt["property_value_id"])).all()

    q = s.query(PropertyValue)
    mid = tgt.get("material_id")
    if mid is None and tgt.get("material_name"):
        mid = by_name.get(tgt["material_name"])
        if mid is None:
            return []                       # 이름이 DB 에 없으면 대상 0건이다
    if mid is not None:
        q = q.filter(PropertyValue.material_id == int(mid))
    if tgt.get("property_key"):
        q = q.filter(PropertyValue.property_key == tgt["property_key"])
    if tgt.get("source_id") is not None:
        q = q.filter(PropertyValue.source_id == int(tgt["source_id"]))
    if tgt.get("method"):
        q = q.filter(PropertyValue.method == tgt["method"])
    if tgt.get("quality_tier") is not None:
        q = q.filter(PropertyValue.quality_tier == int(tgt["quality_tier"]))
    rows = q.all()

    # 출처를 doi·url·title 로 좁힌다(출처 id 를 모르는 배치가 대부분이다).
    for fld, col in (("source_doi", "doi"), ("source_url", "url"), ("source_title", "title")):
        want = tgt.get(fld)
        if not want:
            continue
        ids = {r[0] for r in s.query(Source.id).filter(getattr(Source, col) == want).all()}
        rows = [pv for pv in rows if pv.source_id in ids]

    # 조건은 **키가 있으면**(값이 null 이어도) 건다 — "조건이 비어 있는 행" 을 못박기 위해서다.
    if "conditions" in tgt:
        want = cond_sig(tgt["conditions"])
        rows = [pv for pv in rows if cond_sig(pv.conditions) == want]
    if "value" in tgt and tgt["value"] is not None:
        rows = [pv for pv in rows if _num_eq(pv.value_num, tgt["value"])]
    if "value_text" in tgt and tgt["value_text"] is not None:
        rows = [pv for pv in rows if (pv.value_text or "") == str(tgt["value_text"])]
    return rows


def plan_correction(pv, setv: dict, defs: dict) -> tuple[dict, dict, list]:
    """(바뀔 칸, 조건에 남길 되돌리기 표시, 거부사유 목록).

    바뀌지 않는 칸은 결과에 담지 않는다 — "고칠 것이 없는 정정" 을 거부하기 위해서다.
    """
    bad: list[str] = []
    unknown = set(setv) - CORRECTABLE
    if unknown:
        # `property_key`·`material_id` 를 여기서 잡는다. 이동은 정정이 아니다.
        bad.append(f"정정할 수 없는 칸 {sorted(unknown)} — 키·재료 이동은 이 경로가 아니다"
                   f"(묘비 규약이 먼저다)")
    chg: dict = {}
    back: dict = {}

    if "value" in setv and not _num_eq(pv.value_num, setv["value"]):
        chg["value_num"] = None if setv["value"] is None else float(setv["value"])
        back["value_before_correction"] = pv.value_num
    if "value_text" in setv and (pv.value_text or None) != (setv["value_text"] or None):
        chg["value_text"] = setv["value_text"]
        back["value_text_before_correction"] = pv.value_text
    if "unit" in setv and (pv.unit or None) != (setv["unit"] or None):
        chg["unit"] = setv["unit"]
        back["unit_before_correction"] = pv.unit
    if "method" in setv:
        meth, detail = norm_method(setv["method"])
        if detail:
            bad.append(f"method 는 어휘여야 한다 — '{setv['method']}' 는 서술이다")
        elif meth != pv.method:
            chg["method"] = meth
            back["method_before_correction"] = pv.method
    if "quality_tier" in setv:
        t = norm_tier(setv["quality_tier"])
        if t != pv.quality_tier:
            chg["quality_tier"] = t
            back["tier_before_correction"] = pv.quality_tier
    if "notes" in setv and (pv.notes or None) != (setv["notes"] or None):
        chg["notes"] = setv["notes"]
        back["notes_before_correction"] = pv.notes

    if "conditions" in setv:
        old = as_cond(pv.conditions)
        new = as_cond(setv["conditions"])
        if cond_sig(old) != cond_sig(new):
            # **바뀐 조건 칸마다 개별로 남긴다**(44차 FD 의 `wavelength_nm_before_correction`).
            # 통째로 문자열에 말아 넣으면 grep 이 안 되고 되돌리기가 눈으로 안 읽힌다.
            #
            # 52차 NA 가 여기서 결함 둘을 만났다. 둘 다 **병합기가 정정을 못 알아보고 운영에
            # 새 행을 만든다** — §522 가 막으려던 바로 그 사고다(실측 574행).
            #   ① `old.get(k) != new.get(k)` 는 **"칸이 없다" 와 "칸이 null 이다" 를 못 가른다.**
            #      값이 null 인 칸의 이름만 바꾸면 표시가 **하나도 안 남고**, 표시가 없으면
            #      `correction_prior` 가 None 을 돌려 정정 전파 분기가 아예 안 돈다(91행).
            #      → 있고 없음(`k in`)을 먼저 본다.
            #   ② 조건 칸 이름이 **컬럼 이름과 같으면 표시가 충돌한다.** `conditions.method`
            #      를 고치면 `method_before_correction` 이 남는데, 병합기는 그것을 **컬럼**
            #      `method` 의 옛 값으로 읽어 `where method='DMA tan-delta'` 로 찾는다 —
            #      0건이라 정정이 통째로 miss 가 된다(483행).
            #      → 겹치는 이름만 `conditions.` 로 네임스페이스를 붙인다. 병합기는 그 접두어를
            #        모르므로 컬럼으로 오독하지 않고, 되돌리기 정보는 그대로 남는다.
            for k in set(old) | set(new):
                if k.endswith("_before_correction") or k in ("correction_reason", "corrected_by"):
                    continue
                if (k in old) != (k in new) or old.get(k) != new.get(k):
                    nm = f"conditions.{k}" if k in COLUMN_MARKER_NAMES else k
                    back[f"{nm}_before_correction"] = old.get(k)
            chg["conditions"] = new
    # 새 값이 삽입과 **같은 가드**를 통과하는지 본다. 정정이 우회로가 되면 안 된다.
    v = chg.get("value_num", pv.value_num)
    key = pv.property_key
    d = defs.get(key)
    u = chg.get("unit", pv.unit)
    if v is not None and d is not None and d.si_unit and u and unit_key(u) != unit_key(d.si_unit):
        bad.append(f"단위 불일치 {u} ≠ {d.si_unit}")
    lo, hi = RANGE.get(key, (None, None))
    if v is not None and lo is not None and not (lo <= float(v) <= hi):
        bad.append(f"범위 밖 {v} (허용 {lo}~{hi})")
    if v is not None and key in PCT_SUSPECT and float(v) > 1.0:
        bad.append(f"퍼센트 오입력 의심 {v} (비율이어야 함)")
    return chg, back, bad


def check_tier_upgrade(pv, chg: dict, corr: dict) -> list:
    """등급을 **올리는**(숫자가 작아지는) 정정은 더 엄격하다.

    등급은 "이 값을 얼마나 믿을 수 있나" 이고, 올린다는 것은 **근거가 더 세졌다**는 주장이다.
    사유만으로는 안 된다 — 무엇이 근거를 세게 만들었는지가 있어야 한다.

    · 상향이면 `evidence` 를 따로 요구한다(사유와 별개다. 사유는 '왜 고치나', 근거는 '무엇이 그것을 증명하나').
    · **t1 로 올리려면 method 가 `measured`·`digitized` 여야 한다** — 브리프 3번이
      *"측정 방법이 적힌 값만 tier1이다"* 라 못박았다. handbook·computed·estimated 를 t1 로
      올리는 것은 등급 체계를 무의미하게 만든다.
    """
    if "quality_tier" not in chg or chg["quality_tier"] >= pv.quality_tier:
        return []
    bad = []
    ev = str(corr.get("evidence") or "").strip()
    if len(ev) < REASON_MIN:
        bad.append(f"등급 상향(t{pv.quality_tier}→t{chg['quality_tier']})인데 `evidence` 가 없다 "
                   f"— 무엇이 근거를 세게 만들었는지를 사유와 별도로 적어라")
    if chg["quality_tier"] == 1 and chg.get("method", pv.method) not in ("measured", "digitized"):
        bad.append(f"t1 로 올리려면 method 가 measured·digitized 여야 한다 "
                   f"(지금 {chg.get('method', pv.method)}) — 브리프 3번")
    return bad


def apply_corrections(docs: list, apply: bool) -> dict:
    """선언된 정정을 검증하고(그리고 `--apply` 면) 적용한다. 통계 dict 를 돌려준다."""
    st = {"corr_ok": 0, "corr_no_target": 0, "corr_no_reason": 0, "corr_no_match": 0,
          "corr_multi_match": 0, "corr_no_change": 0, "corr_rejected": 0,
          "corr_would_duplicate": 0}
    todo = [(f, c) for f, doc in docs for c in (doc.get("corrections") or [])]
    if not todo:
        return st
    print(f"\n{'=' * 70}\n정정 선언 {len(todo)}건 — "
          f"{'적용한다' if apply else '**드라이런: 무엇을 고칠지만 출력한다**'}")
    with SessionLocal() as s:
        defs = {d.key: d for d in s.query(PropertyDefinition).all()}
        by_name = {m.name: m.id for m in s.query(Material).all()}
        for fname, corr in todo:
            tgt = corr.get("target") or {}
            head = f"  [{fname}]"
            if not isinstance(tgt, dict) or not tgt:
                st["corr_no_target"] += 1
                print(f"{head} ✗ 대상 미지정 — 행 id 또는 재료+키+조건으로 못박아라")
                continue
            reason = str(corr.get("reason") or "").strip()
            if len(reason) < REASON_MIN:
                st["corr_no_reason"] += 1
                print(f"{head} ✗ 사유 없음 — 왜 고치는지가 값과 함께 남아야 한다 (target={tgt})")
                continue
            rows = match_targets(s, tgt, by_name)
            if not rows:
                st["corr_no_match"] += 1
                print(f"{head} ✗ 대상 0건 — {tgt}")
                continue
            if len(rows) > 1:
                st["corr_multi_match"] += 1
                print(f"{head} ✗ 대상 {len(rows)}건에 걸린다(id {[r.id for r in rows][:8]}) — "
                      f"어느 행인지 우리가 고르면 그건 우리 판정이다. 조건을 더 걸어 유일하게 만들어라")
                continue
            pv = rows[0]
            setv = corr.get("set")
            if not isinstance(setv, dict) or not setv:
                st["corr_no_change"] += 1
                print(f"{head} ✗ pv{pv.id}: `set` 이 비었다")
                continue
            chg, back, bad = plan_correction(pv, setv, defs)
            bad += check_tier_upgrade(pv, chg, corr)
            if bad:
                st["corr_rejected"] += 1
                print(f"{head} ✗ pv{pv.id} 거부 — " + " / ".join(bad))
                continue
            if not chg:
                st["corr_no_change"] += 1
                print(f"{head} · pv{pv.id}: 이미 그 값이다 — 고칠 것이 없다")
                continue
            # 정정 결과가 같은 (재료·키·출처·조건) 의 다른 행과 겹치면 중복이 된다.
            new_sig = cond_sig(chg.get("conditions", as_cond(pv.conditions)))
            twin = [o for o in s.query(PropertyValue).filter(
                        PropertyValue.material_id == pv.material_id,
                        PropertyValue.property_key == pv.property_key).all()
                    if o.id != pv.id and o.source_id == pv.source_id
                    and cond_sig(o.conditions) == new_sig]
            if twin:
                st["corr_would_duplicate"] += 1
                print(f"{head} ✗ pv{pv.id}: 정정하면 pv{twin[0].id} 와 "
                      f"(재료·키·출처·조건)이 같아진다 — 중복이 된다")
                continue

            shown = {k: (getattr(pv, k) if k != "conditions" else pv.conditions) for k in chg}
            print(f"{head} {'✔' if apply else '(dry)'} pv{pv.id} "
                  f"[{pv.material_id}] {pv.property_key}")
            for k, v in chg.items():
                print(f"       {k}: {str(shown[k])[:90]} → {str(v)[:90]}")
            print(f"       사유: {reason[:160]}")
            if apply:
                cond = dict(chg.get("conditions", as_cond(pv.conditions)))
                cond.update(back)
                cond["correction_reason"] = reason
                cond["corrected_by"] = str(corr.get("by") or "unspecified")
                if corr.get("evidence"):
                    cond["correction_evidence"] = str(corr["evidence"])
                for k, v in chg.items():
                    if k != "conditions":
                        setattr(pv, k, v)
                pv.conditions = cond
                s.flush()
            st["corr_ok"] += 1
        if apply:
            s.commit()
    return st


def load(paths: list[str]) -> list[tuple[str, dict]]:
    out = []
    for p in paths:
        pp = Path(p)
        files = sorted(pp.glob("*.json")) if pp.is_dir() else [pp]
        for f in files:
            if f.name in ("property_keys.json", "materials.json"):
                continue
            try:
                doc = json.loads(f.read_text())
            except Exception as e:
                print(f"  ✗ {f.name}: JSON 파싱 실패 {e}")
                continue
            # **배치가 산출 디렉터리에 값 JSON 아닌 것을 같이 둔다.**
            # 23차에 `targets_v2.json` · `key_proposal.json` · `next_targets.json` 이 섞여 있었고,
            # 디렉터리째 넘기면 로더가 통째로 죽을 뻔했다. 값 문서만 골라 쓰고 나머지는 건너뛴다.
            # 48차 JA — **정정 전용 문서**는 `materials` 가 없어도 값 문서다.
            if not (isinstance(doc, dict) and (isinstance(doc.get("materials"), list)
                                               or isinstance(doc.get("corrections"), list))):
                print(f"  · {f.name}: 값 문서가 아니다(`materials`·`corrections` 배열 없음) — 건너뛴다")
                continue
            out.append((f.name, doc))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    with SessionLocal() as s:
        # **어느 DB를 치는지 먼저 찍는다.** MATERIALTWIN_DATA_DIR 을 빼먹고 돌리면
        # 저장소 기본 DB를 쳐서 '재료 미지정'이 무더기로 뜬다 — 19차 I6이 그렇게 한 번 헛돌았다.
        _url = str(s.get_bind().url)
        defs = {d.key: d for d in s.query(PropertyDefinition).all()}
        by_name = {m.name: m.id for m in s.query(Material).all()}
        print(f"[DB] {_url}\n     재료 {len(by_name)}종 · 정의 {len(defs)}종")
        existing = {}
        # 같은 (재료, 물성)이라도 조건이 다르면 별개 측정이므로, 조건 집합도 함께 들고 있는다.
        existing_cond: dict[tuple[int, str], set[str]] = {}
        for mid, k, t, cond in s.query(PropertyValue.material_id, PropertyValue.property_key,
                                       PropertyValue.quality_tier,
                                       PropertyValue.conditions).all():
            existing[(mid, k)] = min(existing.get((mid, k), 9), t)
            existing_cond.setdefault((mid, k), set()).add(cond_sig(cond))

    stats = {"ok": 0, "no_source": 0, "bad_key": 0, "bad_unit": 0, "out_of_range": 0,
             "pct_suspect": 0, "kept_better": 0, "new_mat": 0, "no_mat": 0, "cond_clash": 0,
             "mat_fail": 0, "skipped_rows": 0, "visc_order": 0}
    # 적재는 (재료·물성·출처·조건)에 멱등이다. 조건이 같은데 값이 다르면 나중 것이
    # 앞의 것을 조용히 덮어 측정 하나가 사라진다(3M 112P02/112P05가 그렇게 사라졌다).
    seen_cond: dict[tuple, float] = {}
    # **기채굴 조회는 지시로 안 지켜진다.** 34차 AG·AI·AJ 가 세 파동 연속으로 도구의 낡은 사본을
    # 돌려 이미 채굴한 논문을 놓쳤다(Tsai 2013 21행 · Vitry 2008 8행 · Kuang 2016 3행).
    # **적재기는 우회할 수 없으므로 여기서 한 번 더 친다** — 막지는 않고 경고만 한다
    # (같은 논문의 다른 조건 행은 정당하게 늘어난다).
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        import sqlite3 as _sq
        from mined_index import DB as _MI_DB, build as _mi_build, look as _mi_look
        _mi = _mi_build(_sq.connect(_MI_DB))
    except Exception as _e:                      # 도구가 없어도 적재는 계속돼야 한다
        _mi = None
        print(f"  · 기채굴 조회 건너뜀({str(_e)[:60]})")
    _warned: set = set()

    docs = load(a.paths)
    for fname, doc in docs:
        print(f"\n=== {fname} ===")
        for entry in doc.get("materials", []):
            src = entry.get("source") or {}
            # 이 논문이 이미 채굴됐는지 — DOI·경로·제목·인용키·재료명 다섯 축으로 본다.
            if _mi is not None:
                _k = (src.get("doi") or "", src.get("title") or "")
                if _k not in _warned:
                    _warned.add(_k)
                    _p = _mi_look(_mi, doi=src.get("doi"), path=src.get("local_path"),
                                  title=src.get("title"))
                    if _p and (_p.get("rows") or 0) >= 3:
                        print(f"  ⚠ **이미 채굴된 논문이다**({_p['matched_by']}, {_p['rows']}행"
                              f", 최소 tier{_p.get('min_tier')}) — {str(_p.get('title'))[:64]}")
                        print("     조건이 다른 행이면 정상이다. 같은 값을 다시 넣는 것이면 빼라.")
            if not (src.get("url") or src.get("doi") or src.get("title")):
                stats["no_source"] += len(entry.get("properties", []))
                print("  ✗ 출처 없음 — 항목 전체 건너뜀")
                continue
            name = entry.get("match_name")
            mid = by_name.get(name) if name else None
            if mid is None:
                nm = entry.get("new_material")
                if isinstance(nm, str):        # 이름만 문자열로 준 경우도 수용
                    nm = {"name": nm}
                if not nm or not nm.get("name"):
                    stats["no_mat"] += 1
                    print(f"  ✗ 재료 미지정: {name}")
                    continue
                if nm["name"] in by_name:
                    mid = by_name[nm["name"]]
                elif a.apply:
                    if len(nm["name"]) > 200:      # material.name 은 VARCHAR(200) 이다
                        n_lost = len(entry.get("properties", []))
                        stats["mat_fail"] += 1
                        stats["skipped_rows"] += n_lost
                        print(f"  ✗✗ 재료명이 {len(nm['name'])}자 — 200자 제한 초과, 물성 {n_lost}행 유실\n"
                              f"      {nm['name'][:90]}...")
                        continue
                    # **`attributes` 가 `new_material` 바깥에 오는 배치가 있다.**
                    # 안쪽만 보면 **역할 판정이 조용히 버려져** 근거 재료가 해석 격자에
                    # 들어간다(27차 V 에서 59종이 그렇게 들어가 커버리지가 7%p 내려앉았다).
                    attrs = {**(entry.get("attributes") or {}), **(nm.get("attributes") or {})}
                    r = M.register_material(name=nm["name"], category=norm_cat(nm.get("category") or entry.get("category")),
                                            attributes=attrs or None)
                    if "error" in r:
                        n_lost = len(entry.get("properties", []))
                        stats["mat_fail"] += 1
                        stats["skipped_rows"] += n_lost
                        print(f"  ✗✗ 재료 등록 실패 — 물성 {n_lost}행 유실 "
                              f"({len(nm['name'])}자) {nm['name'][:70]}: {r['error']}")
                        continue
                    mid = r["material_id"]
                    by_name[nm["name"]] = mid
                    stats["new_mat"] += 1
                    print(f"  + 신규 재료 [{mid}] {nm['name']}")
                else:
                    stats["new_mat"] += 1
                    print(f"  + (dry) 신규 재료 {nm['name']}")
                    # dry-run 가상 id. 이름마다 다른 값이어야 서로 다른 재료가
                    # 같은 것으로 판정돼 조건 충돌이 거짓으로 뜨지 않는다.
                    mid = -(abs(hash(nm["name"])) % 10**9 + 1)

            # **점도 기준온도는 한 유리 안에서 순서가 정해져 있다**(브리프 431).
            # 뒤집혀 있으면 그 항목의 점도 행 전체를 버린다 — 어느 칸이 틀렸는지
            # 우리가 고르면 그건 우리 값이 된다(브리프 443).
            _visc_bad = viscosity_order_violations(entry.get("properties", []))
            if _visc_bad:
                print(f"  ✗ 점도 기준점 순서 위반 — {name or (entry.get('new_material') or {}).get('name')}")
                for _m in _visc_bad:
                    print(f"      {_m}")

            for pr in entry.get("properties", []):
                key, val, unit = pr.get("key"), pr.get("value"), pr.get("unit")
                if key == VISCOSITY_KEY and _visc_bad:
                    stats["visc_order"] += 1
                    continue
                # 에이전트가 value_text 필드를 따로 쓰는 경우도 받는다.
                if pr.get("value_text") and (val is None or str(val).lower() in ("none", "null", "")):
                    val = pr["value_text"]
                if isinstance(unit, str) and unit.lower() in ("none", "null", ""):
                    unit = None
                d = defs.get(key)
                if d is None:
                    stats["bad_key"] += 1
                    print(f"    ✗ 미정의 key {key}")
                    continue
                if val is None:
                    continue
                # UL94 등급처럼 문자 값은 value_text로 저장(숫자 검증 건너뜀).
                is_text = isinstance(val, str)
                if is_text:
                    if a.apply:
                        meth, detail = norm_method(pr.get("method"))
                        meth0 = meth
                        meth, _mid = force_computed_if_midpoint(meth, pr.get("notes"))
                        cond = as_cond(pr.get("conditions"))
                        if _mid:
                            cond["method_before_correction"] = meth0
                        if detail:
                            cond["test_method"] = detail
                        r = M.register_property(
                            mid, key, value_text=val, method=meth,
                            quality_tier=pick_tier(pr),
                            conditions=cond or None, notes=pick_notes(pr),
                            source_title=src.get("title"), source_url=src.get("url"),
                            source_doi=src.get("doi"),
                            source_authors=src.get("authors"), source_year=src.get("year"),
                            source_local_path=src.get("local_path"),
                            source_kind=norm_kind(src.get("kind")),
                            source_manufacturer=pick_publisher(src))
                        if "error" in r:
                            print(f"    ✗ {key}: {r['error']}")
                            continue
                    stats["ok"] += 1
                    continue
                if d.si_unit and unit and unit_key(unit) != unit_key(d.si_unit):
                    stats["bad_unit"] += 1
                    print(f"    ✗ 단위 불일치 {key}: {unit} ≠ {d.si_unit}")
                    continue
                lo, hi = RANGE.get(key, (None, None))
                if lo is not None and not (lo <= float(val) <= hi):
                    stats["out_of_range"] += 1
                    print(f"    ✗ 범위 밖 {key}={val} (허용 {lo}~{hi})")
                    continue
                if key in PCT_SUSPECT and float(val) > 1.0:
                    stats["pct_suspect"] += 1
                    print(f"    ✗ 퍼센트 오입력 의심 {key}={val} (비율이어야 함)")
                    continue
                sig = (mid, key, src.get("doi") or src.get("url") or src.get("title"),
                       cond_sig(pr.get("conditions")))
                prev = seen_cond.get(sig)
                if prev is not None and abs(prev - float(val)) > 1e-12:
                    stats["cond_clash"] += 1
                    print(f"    ✗ 조건 충돌 {key}: {prev} vs {val} — 조건이 같아 뒤엣것이 앞엣것을 "
                          f"덮는다. 그레이드·방향 등 구분 조건을 conditions에 넣을 것")
                    continue
                seen_cond[sig] = float(val)
                # 기존 tier1 실측 보존 — 단 조건이 다르면 별개 측정이므로 통과시킨다.
                if (mid > 0 and existing.get((mid, key), 9) <= 1
                        and cond_sig(pr.get("conditions")) in existing_cond.get((mid, key), set())):
                    stats["kept_better"] += 1
                    continue
                if a.apply:
                    meth, detail = norm_method(pr.get("method"))
                    meth0 = meth
                    meth, _mid = force_computed_if_midpoint(meth, pr.get("notes"))
                    cond = as_cond(pr.get("conditions"))
                    # **강등했으면 표시를 남긴다** — 41차 CD 가 SQL 로 옮길 때 스스로 쓴 방식인데
                    # 적재기에는 없었다. 표시가 없으면 나중에 "가드가 내린 것"과 "배치가 그렇게
                    # 적어 보낸 것"을 구별할 수 없다(EE 가 기존 441행에서 그 벽을 만났다).
                    if _mid:
                        cond["method_before_correction"] = meth0
                    if detail:
                        cond["test_method"] = detail
                    r = M.register_property(
                        mid, key, value=float(val), unit=unit or d.si_unit,
                        method=meth, quality_tier=pick_tier(pr),
                        conditions=cond or None, notes=pick_notes(pr),
                        source_title=src.get("title"), source_url=src.get("url"),
                        source_doi=src.get("doi"),
                        source_authors=src.get("authors"), source_year=src.get("year"),
                            source_local_path=src.get("local_path"),
                        source_kind=norm_kind(src.get("kind")),
                        source_manufacturer=pick_publisher(src))
                    if "error" in r:
                        print(f"    ✗ {key}: {r['error']}")
                        continue
                stats["ok"] += 1
    # **정정은 삽입이 다 끝난 뒤에 돈다** — 같은 파일이 새 행을 넣고 옛 행을 고칠 수 있다.
    stats.update(apply_corrections(docs, a.apply))
    print(f"\n{'[APPLY]' if a.apply else '[DRY-RUN]'} " +
          " / ".join(f"{k} {v}" for k, v in stats.items() if v))
    # **조용한 유실을 요약 밖으로 끌어낸다.** 18차에 재료명이 202자라 등록이 거부되고
    # 물성 5행이 사라졌는데, print 한 줄이 정상 출력에 묻혀 아무도 못 봤다.
    # 무결성 검사는 '들어오지 않은 행'을 볼 수 없다 — 여기가 유일한 방어선이다.
    if stats["mat_fail"] or stats["skipped_rows"]:
        print(f"  ⚠ 재료 등록 실패 {stats['mat_fail']}건 때문에 물성 "
              f"{stats['skipped_rows']}행이 적재되지 않았다 — 위 ✗✗ 줄을 확인해라.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
