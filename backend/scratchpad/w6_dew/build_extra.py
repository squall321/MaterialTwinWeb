# 2차 배치(배터리 전극/금속) 항목을 F_dew.json에 덧붙이는 스크립트
import json, os

OUT = "/tmp/claude-1000/-home-koopark-claude-MaterialTwinWeb/27fcb5b7-c986-41ba-966a-c49b295b3f3a/scratchpad/w6parts/F_dew.json"
TGT = "/home/koopark/claude/MaterialTwinWeb/.agent_work/targets/g_dew.txt"
names = {}
for line in open(TGT, encoding="utf-8"):
    if line.startswith("#"):
        continue
    p = line.rstrip("\n").split("\t")
    if len(p) >= 4:
        names[int(p[0])] = p[1]

d = json.load(open(OUT, encoding="utf-8"))

S_SCIREP = {"title": "The impact of binder polarity on the properties of aqueously processed positive and negative electrodes for lithium-ion batteries",
            "kind": "journal", "url": "https://www.nature.com/articles/s41598-025-93813-9.pdf",
            "doi": "10.1038/s41598-025-93813-9", "year": 2025}
S_JES = {"title": "The Role of Surface Free Energy in Binder Distribution and Adhesion Strength of Aqueously Processed LiNi0.5Mn1.5O4 Cathodes (Weber et al., J. Electrochem. Soc. 171 040523)",
         "kind": "journal", "url": "https://iopscience.iop.org/article/10.1149/1945-7111/ad3a24/pdf",
         "doi": "10.1149/1945-7111/ad3a24", "year": 2024}
S_METAL = {"title": "Wettability of Metal Surfaces Affected by Paint Layer Covering (Materials 15 (2022) 1830)",
           "kind": "journal", "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8912038/fullTextXML",
           "doi": "10.3390/ma15051830", "year": 2022}
S_SUS = {"title": "Surface Analysis of Stainless Steel Electrodes Cleaned by Atmospheric Pressure Plasma (Materials 17 (2024) 3621)",
         "kind": "journal", "url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11278598/fullTextXML",
         "doi": "10.3390/ma17143621", "year": 2024}

extra = []

extra.append((100, S_SCIREP, [{
    "key": "physical.surface_energy", "value": 0.0481, "unit": "J/m^2", "tier": 1,
    "method": "Owens-Wendt-Rabel-Kaelble (OWRK) from contact angles with diiodomethane, DMSO and ethylene glycol",
    "conditions": {"method_detail": "Washburn / sessile drop 접촉각(DIM, DMSO, EG) -> OWRK; dispersive 45.7, polar 2.4 mJ/m^2, 상대극성 5.0%",
                   "reported_uncertainty": "+-1.8 mJ/m^2",
                   "surface_treatment": "천연흑연 음극 활물질 분말 (MechanoCap 1P1, H.C. Carbon) — 무처리",
                   "temperature": "not reported"},
    "notes": "Table 2 'SFE of different anode materials' 의 Graphite 행, 첫 열 gammaS = 48.1 +- 1.8 mJ/m^2. 인접 열은 gammaS^d 45.7 / gammaS^p 2.4로 45.7+2.4=48.1이 되어 열 대응을 검산했다. Table 1의 C65/CMC/LNMO/Al CC 행에 붙은 [1] 재인용 표시가 Graphite 행에는 없어 이 논문 자체 측정이다. **탐침 액체에 물이 없다** — 표면에너지라 접촉각 항목은 넣지 않았다."}]))

extra.append((147, S_JES, [
    {"key": "physical.surface_energy", "value": 0.0317, "unit": "J/m^2", "tier": 1,
     "method": "Owens-Wendt-Rabel-Kaelble (OWRK) from Washburn capillary-rise contact angles",
     "conditions": {"method_detail": "Washburn(모세관 상승) 접촉각 -> OWRK; dispersive 28.6, polar 3.1 mJ/m^2",
                    "reported_uncertainty": "+-1.2 mJ/m^2",
                    "surface_treatment": "C-NERGY SUPER C65 (Imerys Graphite & Carbon) 분말, BET 비표면적 62 m^2/g, 무처리 분말층",
                    "temperature": "not reported"},
     "notes": "Table IV 'Surface free energy...' 의 C65 행, gammaS = 31.7 +- 1.2 mJ/m^2 (gammaS^d 28.6 + gammaS^p 3.1 = 31.7 검산 통과). 이 논문이 1차 출처다(Sci Rep 2025 논문은 이 값을 [1] 재인용한다). 대상 재료 147에 이미 붙어 있는 TIMCAL C-NERGY SUPER C65 데이터시트와 등급이 정확히 일치한다."},
    {"key": "physical.contact_angle_water", "value": 89.6, "unit": "deg", "tier": 1,
     "method": "Washburn capillary-rise (powder bed)",
     "conditions": {"test_liquid": "water",
                    "angle_type": "Washburn capillary-rise effective contact angle on a packed powder bed (sessile drop이 아니다)",
                    "method_detail": "n-hexane으로 구한 모세관 상수 1.7e-5 사용, n = 3",
                    "reported_uncertainty": "+-0.4 deg",
                    "surface_treatment": "C-NERGY SUPER C65 분말, 무처리",
                    "temperature": "not reported"},
     "notes": "Table III 'Contact angle measurements of electrode components' 의 C65 행 'Water' 열 = 89.6 +- 0.4도. 인접 'DIM' 열 64.4도, 'DMSO' 열 38.7도와 헷갈리지 않도록 열 머리글을 다시 읽었다. Method 열이 WB(Washburn)이라 분말층 유효 접촉각이다."}]))

extra.append((398, S_SCIREP, [{
    "key": "physical.surface_energy", "value": 0.0406, "unit": "J/m^2", "tier": 3,
    "method": "Owens-Wendt-Rabel-Kaelble (OWRK) from contact angles with diiodomethane, DMSO and ethylene glycol",
    "conditions": {"method_detail": "sessile drop 접촉각(DIM, DMSO, EG) -> OWRK; dispersive 39.2, polar 1.4 mJ/m^2, 상대극성 3.5%",
                   "reported_uncertainty": "+-0.7 mJ/m^2",
                   "surface_treatment": "SBR 바인더 라텍스 (TRD 2001, JSR Micro)로 캐스팅한 필름, 무처리",
                   "temperature": "not reported",
                   "grade_scope": "class value - 논문 시편은 리튬전지 음극용 SBR 바인더 라텍스 필름이다. 대상은 카본블랙 충전·가황된 벌크 SBR 고무라 표면에 배합제(왁스·오일)가 블룸할 수 있다"},
    "notes": "Table 2의 SBR 행, gammaS = 40.6 +- 0.7 (39.2 + 1.4 = 40.6 검산 통과). Table 1/2에서 [1] 재인용 표시가 없는 자체 측정 행이다."}]))

extra.append((37, S_METAL, [
    {"key": "physical.contact_angle_water", "value": 64.0, "unit": "deg", "tier": 3,
     "method": "static equilibrium (Young) water contact angle, sessile drop",
     "conditions": {"test_liquid": "water (gamma_LV = 71.7 mN/m at 23 C)", "angle_type": "static equilibrium (Theta_Y)",
                    "surface_treatment": "brass reference — 도료를 바르지 않은 세정 상태의 황동 기준면",
                    "temperature_c": 23,
                    "grade_scope": "class value - 논문의 황동은 등급 미명시 CuZn 황동이다. 대상은 C26000(70/30 카트리지 황동)이다"},
     "notes": "Table 2 'Static equilibrium contact angles, theta_eq, and corresponding gamma_SV' 의 'brass ref.' 행, Theta_Y^a 열 = 64.0 (1). 같은 표의 도장면 행(brass (w) 79.1, (b) 77.8, (r) 73.4, (cs) 72.3)은 도료 표면이라 배제했다. 같은 행이 이미 DB의 C36000 황동에 tier3으로 들어가 있다."},
    {"key": "physical.surface_energy", "value": 0.0439, "unit": "J/m^2", "tier": 3,
     "method": "gamma_SV = 1/2 * gamma_LV * (1 + cos theta_eq)",
     "conditions": {"probe_liquid": "water (gamma_LV = 71.7 mN/m at 23 C)", "temperature_c": 23,
                    "surface_treatment": "brass reference — 도장하지 않은 세정 황동 기준면",
                    "grade_scope": "class value - 등급 미명시 CuZn 황동 기준면. 대상은 C26000 카트리지 황동이다"},
     "notes": "Table 2의 'brass ref.' 행 gamma_SV^a 열 = 43.9 (1.7) mJ/m^2. 인접 gamma_SV^b 52.9 / gamma_SV^c 53.2는 접촉각 이력(CAH)에서 유도한 다른 정의라 섞지 않았다."}]))

for mid, gs in [(39, "class value - 논문 기준면은 순동(Cu ref.)이다. 대상은 C51000 인청동(Cu-Sn-P)으로 합금원소가 다르다"),
                (179, "class value - 논문 기준면은 순동(Cu ref.)이다. 대상은 베릴륨동(Cu-Be)이다")]:
    extra.append((mid, S_METAL, [
        {"key": "physical.contact_angle_water", "value": 70.2, "unit": "deg", "tier": 3,
         "method": "static equilibrium (Young) water contact angle, sessile drop",
         "conditions": {"test_liquid": "water (gamma_LV = 71.7 mN/m at 23 C)", "angle_type": "static equilibrium (Theta_Y)",
                        "surface_treatment": "Cu reference — 도장하지 않은 세정 구리 기준면", "temperature_c": 23,
                        "grade_scope": gs},
         "notes": "Table 2의 'Cu ref.' 행 Theta_Y^a 열 = 70.2 (1)도. 도장면 행(Cu (w) 81.6, (b) 83.9, (r) 70.8, (cs) 79.9)은 도료 표면이라 배제했다. DB의 압연동박 79.0도·소결동 70.1도와 같은 대역이다."},
        {"key": "physical.surface_energy", "value": 0.0390, "unit": "J/m^2", "tier": 3,
         "method": "gamma_SV = 1/2 * gamma_LV * (1 + cos theta_eq)",
         "conditions": {"probe_liquid": "water (gamma_LV = 71.7 mN/m at 23 C)", "temperature_c": 23,
                        "surface_treatment": "Cu reference — 도장하지 않은 세정 구리 기준면", "grade_scope": gs},
         "notes": "Table 2의 'Cu ref.' 행 gamma_SV^a 열 = 39.0 (1.6) mJ/m^2. 금속의 진공 표면에너지(~1000 mJ/m^2)가 아니라 젖음 대역의 고체 표면장력이다."}]))

extra.append((12, S_METAL, [
    {"key": "physical.contact_angle_water", "value": 68.0, "unit": "deg", "tier": 3,
     "method": "static equilibrium (Young) water contact angle, sessile drop",
     "conditions": {"test_liquid": "water (gamma_LV = 71.7 mN/m at 23 C)", "angle_type": "static equilibrium (Theta_Y)",
                    "surface_treatment": "Fe reference — 도장하지 않은 세정 철 기준면", "temperature_c": 23,
                    "grade_scope": "class value - 논문 기준면은 순철(Fe ref.)이다. 대상은 SCM440 Cr-Mo 저합금강이다. 표면 산화막 상태가 지배하므로 열처리·연마 이력이 다르면 크게 벗어난다"},
     "notes": "Table 2의 'Fe ref.' 행 Theta_Y^a 열 = 68.0 (1)도. 도장면 행은 배제했다. DB의 SPCC 연강 60.0도와 같은 대역이다. 스테인리스강(부동태 Cr 산화막)에는 쓰지 않았다 — 표면 화학이 다른 계통이다."},
    {"key": "physical.surface_energy", "value": 0.0422, "unit": "J/m^2", "tier": 3,
     "method": "gamma_SV = 1/2 * gamma_LV * (1 + cos theta_eq)",
     "conditions": {"probe_liquid": "water (gamma_LV = 71.7 mN/m at 23 C)", "temperature_c": 23,
                    "surface_treatment": "Fe reference — 도장하지 않은 세정 철 기준면",
                    "grade_scope": "class value - 순철 기준면. 대상은 SCM440 Cr-Mo 저합금강이다"},
     "notes": "Table 2의 'Fe ref.' 행 gamma_SV^a 열 = 42.2 (1.6) mJ/m^2."}]))

extra.append((1, S_SUS, [{
    "key": "physical.contact_angle_water", "value": 70.76, "unit": "deg", "tier": 3,
    "method": "sessile drop water contact angle",
    "conditions": {"test_liquid": "water", "angle_type": "static (sessile drop)",
                   "surface_treatment": "304 스테인리스강 전극, 99% 공업용 알코올로 세정한 **플라즈마 미처리** 기준면",
                   "grade_scope": "class value - 논문 시편은 SUS304(오스테나이트계)다. 대상 SUS201은 Ni 일부를 Mn으로 치환한 같은 오스테나이트 계열이다"},
    "notes": "초록·본문·결론에 세 번 인쇄된 값 — 'the water contact angle decreased from 70.76 deg to a minimum of 29.31 deg'. **29.31도는 대기압 플라즈마 세정 직후 값이라 서비스 상태가 아니다 — 넣지 않았다.** 표면 탄소 오염이 62.95% -> 37.68%로 줄어드는 것이 원인이라고 논문이 밝힌다. 표면 이력이 값을 지배하는 대표 사례다."}]))

# merge
for mid, src, props in extra:
    d["materials"].append({"match_name": names[mid], "source": src, "properties": props})

json.dump(d, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("entries", len(d["materials"]))
