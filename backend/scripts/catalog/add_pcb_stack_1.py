# PCB/FPCB 원자재 스택을 근거와 함께 등록 — PI필름·동박(ED/RA)·커버레이·접착제·EMI필름·E글라스·에폭시·프리프레그·PSR.
import sys
import mcp_server as M
from app.db import SessionLocal
from app.models import Material

RT = {"temperature_C": 23}


def src(title, kind="datasheet", mfr=None):
    d = {"source_title": title, "source_kind": kind}
    if mfr:
        d["source_manufacturer"] = mfr
    return d


# 출처 프리셋.
ASM = src("ASM Handbook Vol.2 — Copper and Copper Alloys", "book")
IPC4562 = lambda mfr: src("IPC-4562A — Metal Foil for Printed Board Applications", "standard", mfr)  # noqa: E731
IPC4101 = lambda mfr: src("IPC-4101 — Base Materials (Laminate/Prepreg) Spec", "standard", mfr)  # noqa: E731
IPC4204 = lambda mfr: src("IPC-4204 — Flexible Metal-Clad Dielectrics", "standard", mfr)  # noqa: E731
GLASS_HB = src("Fiberglass & E-glass properties (Nittobo/AGY handbook)", "book")


def p(key, value=None, unit=None, tier=3, method="datasheet", source=None,
      cond=None, vtext=None, notes=None):
    d = dict(property_key=key, value=value, value_text=vtext, unit=unit,
             quality_tier=tier, method=method, conditions=cond, notes=notes)
    d.update(source or {})
    return d


# ─────────────────────────────────────────────────────────────────────────────
MATERIALS = [
    # 1) PI 베이스필름 — DuPont Kapton HN (범용 PMDA-ODA)
    dict(code="FPCB-PI-KAPTONHN", name="PI Base Film — Kapton HN (DuPont)", category="polymer",
         description="FPCB 베이스 유전체 — 범용 폴리이미드(PMDA-ODA) 필름. 연성기판 절연층.",
         attrs=dict(subsystem="pcb", material_class="polyimide film (PMDA-ODA)",
                    manufacturer="DuPont", grade="Kapton HN", process="cast PI film",
                    standard="IPC-4204", composition="PMDA-ODA polyimide"),
         props=[
             p("physical.density", 1420, "kg/m^3", 3, source=src("DuPont Kapton HN datasheet", mfr="DuPont")),
             p("mechanical.tensile_strength", 2.31e8, "Pa", 3, cond=RT, source=src("DuPont Kapton HN", mfr="DuPont"), notes="MD, 상온 ~231 MPa"),
             p("mechanical.youngs_modulus", 2.5e9, "Pa", 3, source=src("DuPont Kapton HN", mfr="DuPont"), notes="~2.5 GPa"),
             p("mechanical.elongation_at_break", 0.72, "1", 3, cond=RT, source=src("DuPont Kapton HN", mfr="DuPont"), notes="~72%"),
             p("thermal.expansion_linear", 2.0e-5, "1/K", 3, source=src("DuPont Kapton HN", mfr="DuPont"), notes="CTE ~20 ppm/K"),
             p("thermal.glass_transition", 658, "K", 4, source=src("PMDA-ODA PI Tg (문헌)", "journal"), notes="유사 Tg ~385℃(범용 PI는 뚜렷한 Tg 없음)"),
             p("thermal.decomposition_temp", 833, "K", 3, source=src("DuPont Kapton HN(TGA)", mfr="DuPont"), notes="~560℃"),
             p("thermal.max_service_temp", 673, "K", 3, source=src("DuPont Kapton HN", mfr="DuPont"), notes="단기 ~400℃, 장기 240–260℃"),
             p("thermal.conductivity", 0.12, "W/(m*K)", 3, source=src("DuPont Kapton HN", mfr="DuPont")),
             p("electrical.dielectric_constant", 3.4, "1", 3, cond={"frequency_hz": 1e3}, source=src("DuPont Kapton HN", mfr="DuPont"), notes="Dk @1 kHz"),
             p("electrical.dissipation_factor", 0.0018, "1", 3, cond={"frequency_hz": 1e3}, source=src("DuPont Kapton HN", mfr="DuPont")),
             p("electrical.dielectric_strength", 3.0e8, "V/m", 3, source=src("DuPont Kapton HN 25µm", mfr="DuPont"), notes="~300 kV/mm(25µm)"),
             p("chemical.water_absorption_24h", 0.018, "1", 3, source=src("DuPont Kapton HN", mfr="DuPont"), notes="흡습 ~1.8%(50%RH)"),
         ]),
    # 2) PI 베이스필름 — UBE Upilex-S (BPDA-PDA 고탄성·저CTE)
    dict(code="FPCB-PI-UPILEXS", name="PI Base Film — Upilex-S (UBE)", category="polymer",
         description="고급 FPCB/COF 베이스 — 바이페닐(BPDA-PDA) 폴리이미드. 고탄성·저CTE·저흡습.",
         attrs=dict(subsystem="pcb", material_class="polyimide film (BPDA-PDA, S-type)",
                    manufacturer="UBE Corporation", grade="Upilex-S", process="cast PI film",
                    standard="IPC-4204", composition="BPDA-PDA polyimide"),
         props=[
             p("physical.density", 1470, "kg/m^3", 3, source=src("UBE Upilex-S datasheet", mfr="UBE Corporation")),
             p("mechanical.tensile_strength", 5.2e8, "Pa", 3, cond=RT, source=src("UBE Upilex-S", mfr="UBE Corporation"), notes="~520 MPa(Kapton의 2배)"),
             p("mechanical.youngs_modulus", 9.1e9, "Pa", 3, source=src("UBE Upilex-S", mfr="UBE Corporation"), notes="★ ~9.1 GPa (Kapton 2.5의 3.6배) — 고탄성"),
             p("mechanical.elongation_at_break", 0.30, "1", 3, cond=RT, source=src("UBE Upilex-S", mfr="UBE Corporation"), notes="~30%"),
             p("thermal.expansion_linear", 1.2e-5, "1/K", 3, source=src("UBE Upilex-S", mfr="UBE Corporation"), notes="★ CTE ~12 ppm (Kapton 20 대비 저CTE) → Cu와 정합, 치수안정"),
             p("thermal.glass_transition", 773, "K", 4, source=src("BPDA-PDA PI Tg(문헌)", "journal"), notes="Tg >500℃(사실상 없음)"),
             p("thermal.decomposition_temp", 873, "K", 3, source=src("UBE Upilex-S(TGA)", mfr="UBE Corporation"), notes="~600℃"),
             p("thermal.max_service_temp", 673, "K", 3, source=src("UBE Upilex-S", mfr="UBE Corporation")),
             p("thermal.conductivity", 0.29, "W/(m*K)", 4, source=src("Upilex 계열 문헌값", "journal")),
             p("electrical.dielectric_constant", 3.5, "1", 3, cond={"frequency_hz": 1e6}, source=src("UBE Upilex-S", mfr="UBE Corporation"), notes="Dk @1 MHz"),
             p("electrical.dissipation_factor", 0.0013, "1", 3, cond={"frequency_hz": 1e6}, source=src("UBE Upilex-S", mfr="UBE Corporation")),
             p("chemical.water_absorption_24h", 0.013, "1", 3, source=src("UBE Upilex-S", mfr="UBE Corporation"), notes="~1.3%(Kapton보다 저흡습)"),
         ]),
    # 3) 전해동박 ED (rigid PCB)
    dict(code="PCB-CU-ED", name="전해동박 ED Copper Foil (HTE)", category="metal",
         description="rigid PCB 도체층 — 전착 동박, 주상정 구조. HTE(고온연신) 등급.",
         attrs=dict(subsystem="pcb", material_class="electrodeposited Cu foil (HTE)",
                    manufacturer="Mitsui Mining & Smelting", grade="HTE Class 3",
                    process="electrodeposition", standard="IPC-4562A", composition="Cu ≥99.8%"),
         props=[
             p("physical.density", 8920, "kg/m^3", 2, "handbook", ASM, notes="전착 동박(주상정)"),
             p("mechanical.tensile_strength", 3.30e8, "Pa", 3, cond=RT, source=IPC4562("Mitsui Mining & Smelting"), notes="HTE RT ~310–350 MPa. IPC 최소 ~207"),
             p("mechanical.elongation_at_break", 0.08, "1", 3, cond=RT, source=IPC4562("Mitsui Mining & Smelting"), notes="ED 주상정 → RA보다 낮음. HTE RT ~5–15%"),
             p("mechanical.yield_strength", 2.5e8, "Pa", 4, "estimated", src("IPC-4562A class-typical 추정", "standard"), cond=RT),
             p("mechanical.youngs_modulus", 1.15e11, "Pa", 2, "handbook", ASM),
             p("mechanical.hardness_vickers", 110, "HV", 4, "estimated", src("ED Cu foil class-typical")),
             p("mechanical.poisson_ratio", 0.34, "1", 2, "handbook", ASM),
             p("electrical.conductivity", 5.80e7, "S/m", 3, source=IPC4562("Mitsui Mining & Smelting"), notes="ED ~97–100% IACS"),
             p("electrical.resistivity_volume", 1.72e-8, "ohm*m", 2, "handbook", ASM),
             p("thermal.conductivity", 390, "W/(m*K)", 2, "handbook", ASM),
             p("thermal.expansion_linear", 1.70e-5, "1/K", 2, "handbook", ASM, notes="Cu ~17 ppm/K"),
             p("thermal.specific_heat", 385, "J/(kg*K)", 2, "handbook", ASM),
             p("thermal.melting_point", 1358, "K", 2, "handbook", ASM, notes="1085℃"),
             p("structure.crystal_structure", vtext="FCC (columnar/주상정)", tier=2, method="handbook", source=ASM, notes="전착 두께방향 주상정. 조도 Rz가 고주파 손실 좌우"),
         ]),
    # 4) 압연동박 RA (flex PCB)
    dict(code="PCB-CU-RA", name="압연동박 RA Copper Foil (annealed)", category="metal",
         description="flex PCB(FPCB) 도체층 — 압연+어닐 동박, 신장립. 굴곡피로 우수.",
         attrs=dict(subsystem="pcb", material_class="rolled-annealed Cu foil",
                    manufacturer="JX Advanced Metals", grade="RA annealed",
                    process="rolling + annealing", standard="IPC-4562A", composition="Cu ≥99.9%"),
         props=[
             p("physical.density", 8940, "kg/m^3", 2, "handbook", ASM, notes="압연 → 벌크 근접"),
             p("mechanical.tensile_strength", 2.20e8, "Pa", 3, cond=RT, source=IPC4562("JX Advanced Metals"), notes="어닐재 ~200–250 MPa(연질)"),
             p("mechanical.elongation_at_break", 0.20, "1", 3, cond=RT, source=IPC4562("JX Advanced Metals"), notes="★ 어닐 후 15–30% — ED(≤15%) 대비 높음. 굴곡피로(MIT) 수배 → FPCB 표준"),
             p("mechanical.yield_strength", 1.7e8, "Pa", 4, "estimated", src("IPC-4562A annealed 추정", "standard"), cond=RT),
             p("mechanical.youngs_modulus", 1.17e11, "Pa", 2, "handbook", ASM),
             p("mechanical.hardness_vickers", 75, "HV", 4, "estimated", src("RA annealed Cu foil class-typical")),
             p("mechanical.poisson_ratio", 0.34, "1", 2, "handbook", ASM),
             p("electrical.conductivity", 5.85e7, "S/m", 3, source=IPC4562("JX Advanced Metals"), notes="~100–101% IACS, ED보다 약간 우수"),
             p("electrical.resistivity_volume", 1.71e-8, "ohm*m", 2, "handbook", ASM),
             p("thermal.conductivity", 398, "W/(m*K)", 2, "handbook", ASM),
             p("thermal.expansion_linear", 1.70e-5, "1/K", 2, "handbook", ASM),
             p("thermal.specific_heat", 385, "J/(kg*K)", 2, "handbook", ASM),
             p("thermal.melting_point", 1358, "K", 2, "handbook", ASM),
             p("structure.crystal_structure", vtext="FCC (elongated/압연 신장립)", tier=2, method="handbook", source=ASM, notes="신장립 → 굴곡 시 균열전파 억제(FPCB 내굴곡성 근거)"),
         ]),
    # 5) 고Tg FR-4 프리프레그
    dict(code="PCB-PP-FR4HT", name="High-Tg FR-4 Prepreg (7628 glass)", category="composite",
         description="PCB 빌드업 접착층(B-stage) — 유리직물(7628)+에폭시, 고Tg 170℃.",
         attrs=dict(subsystem="pcb", material_class="high-Tg FR-4 prepreg (7628 glass)",
                    manufacturer="Shengyi Technology", grade="high-Tg 170°C",
                    process="B-stage glass-epoxy", standard="IPC-4101"),
         props=[
             p("physical.density", 1900, "kg/m^3", 3, source=IPC4101("Shengyi Technology")),
             p("electrical.dielectric_constant", 4.4, "1", 3, cond={"frequency_hz": 1e9}, source=IPC4101("Shengyi Technology"), notes="Dk @1 GHz"),
             p("electrical.dissipation_factor", 0.016, "1", 3, cond={"frequency_hz": 1e9}, source=IPC4101("Shengyi Technology"), notes="표준 FR-4(저손실 아님)"),
             p("thermal.glass_transition", 443, "K", 3, source=src("Shengyi S1000H(DSC)", mfr="Shengyi Technology"), notes="Tg ~170℃"),
             p("thermal.decomposition_temp", 618, "K", 3, source=src("Shengyi high-Tg(Td, TGA)", mfr="Shengyi Technology"), notes="~345℃"),
             p("thermal.expansion_linear", 1.4e-5, "1/K", 3, cond={"axis": "x-y", "below_Tg": True}, source=IPC4101("Shengyi Technology"), notes="면내 ~14 ppm. z축 Tg이하 ~50–60"),
             p("thermal.conductivity", 0.35, "W/(m*K)", 3, source=IPC4101("Shengyi Technology")),
             p("chemical.water_absorption_24h", 0.0012, "1", 3, source=IPC4101("Shengyi Technology"), notes="~0.12%"),
             p("thermal.flammability_ul94", vtext="V-0", tier=3, source=IPC4101("Shengyi Technology")),
             p("mechanical.flexural_strength", 4.15e8, "Pa", 3, source=IPC4101("Shengyi Technology"), notes="경화 라미네이트 ~415 MPa"),
             p("mechanical.youngs_modulus", 2.2e10, "Pa", 3, source=IPC4101("Shengyi Technology"), notes="면내 ~22 GPa"),
         ]),
    # 6) E-글라스 클로스(보강 원자재)
    dict(code="PCB-EGLASS", name="E-Glass Cloth (reinforcement)", category="ceramic",
         description="FR-4/프리프레그 보강 원자재 — E-유리 직물. 라미네이트 Dk·CTE·강성의 주 결정자.",
         attrs=dict(subsystem="pcb", material_class="E-glass fabric (reinforcement)",
                    manufacturer="Nittobo", process="woven glass cloth", composition="E-glass (Ca-Al-borosilicate)"),
         props=[
             p("physical.density", 2560, "kg/m^3", 2, "handbook", GLASS_HB),
             p("mechanical.youngs_modulus", 7.3e10, "Pa", 2, "handbook", GLASS_HB, notes="E-glass ~73 GPa"),
             p("mechanical.tensile_strength", 3.4e9, "Pa", 2, "handbook", GLASS_HB, notes="섬유 인장 ~3.4 GPa"),
             p("mechanical.poisson_ratio", 0.22, "1", 2, "handbook", GLASS_HB),
             p("thermal.expansion_linear", 5.0e-6, "1/K", 2, "handbook", GLASS_HB, notes="~5 ppm/K(저CTE) → 라미네이트 면내 CTE 억제"),
             p("electrical.dielectric_constant", 6.6, "1", 2, "handbook", GLASS_HB, notes="★ Dk ~6.6 — 수지(3.6)와 합쳐 FR-4 Dk 4.4 결정"),
             p("thermal.max_service_temp", 1113, "K", 3, source=src("E-glass softening ~846℃", "book"), notes="연화점 ~840℃"),
         ]),
    # 7) FR-4 에폭시 수지(매트릭스 원자재)
    dict(code="PCB-EPOXY-FR4", name="FR-4 Epoxy Resin (matrix)", category="polymer",
         description="FR-4 매트릭스 원자재 — 브롬화/DGEBA 에폭시 수지(경화물). 라미네이트 수지상.",
         attrs=dict(subsystem="pcb", material_class="FR-4 epoxy resin (DGEBA + FR)",
                    manufacturer="Kukdo Chemical", process="thermoset cure", composition="brominated DGEBA epoxy"),
         props=[
             p("physical.density", 1200, "kg/m^3", 3, source=src("FR-4 epoxy 경화물(핸드북)", "book")),
             p("thermal.glass_transition", 403, "K", 3, source=src("표준 FR-4 수지 Tg", "book"), notes="표준 ~130℃(고Tg 등급은 170)"),
             p("thermal.expansion_linear", 6.0e-5, "1/K", 3, source=src("neat epoxy CTE", "book"), notes="순수 수지 ~60 ppm(글라스가 억제 전)"),
             p("electrical.dielectric_constant", 3.6, "1", 3, cond={"frequency_hz": 1e9}, source=src("epoxy Dk", "book"), notes="수지 단독 ~3.6 → 글라스와 합쳐 4.4"),
             p("electrical.dissipation_factor", 0.025, "1", 3, cond={"frequency_hz": 1e9}, source=src("epoxy Df", "book")),
             p("mechanical.tensile_strength", 8.0e7, "Pa", 3, source=src("epoxy 경화물", "book"), notes="~80 MPa"),
             p("mechanical.youngs_modulus", 3.4e9, "Pa", 3, source=src("epoxy 경화물", "book"), notes="~3.4 GPa"),
         ]),
    # 8) 커버레이(FPCB 보호층)
    dict(code="FPCB-COVERLAY", name="Coverlay (PI + adhesive)", category="composite",
         description="FPCB 보호 커버레이 — PI필름 + 접착제(아크릴/에폭시). 회로 위 라미네이션.",
         attrs=dict(subsystem="pcb", material_class="coverlay (PI + acrylic/epoxy adhesive)",
                    manufacturer="Nikkan Industries", grade="CISV series", process="PI + B-stage adhesive"),
         props=[
             p("physical.density", 1500, "kg/m^3", 4, "estimated", src("PI+접착 복합 추정")),
             p("thermal.max_service_temp", 423, "K", 4, "estimated", src("접착제 제한 온도 추정"), notes="접착제(아크릴)가 상한 결정 ~150℃"),
             p("electrical.dielectric_constant", 3.5, "1", 4, "estimated", src("PI+접착 복합 추정"), cond={"frequency_hz": 1e6}),
             p("electrical.dissipation_factor", 0.02, "1", 4, "estimated", src("접착제 지배 Df 추정")),
             p("chemical.water_absorption_24h", 0.02, "1", 4, "estimated", src("복합 추정")),
         ]),
    # 9) FPCB 본딩 접착제(본딩시트)
    dict(code="FPCB-ADHESIVE", name="FPCB Bonding Adhesive (acrylic/epoxy)", category="polymer",
         description="FPCB 층간 접착 원자재 — 아크릴/에폭시 본딩시트(B-stage). FCCL 3층·커버레이 접착.",
         attrs=dict(subsystem="pcb", material_class="FPCB bonding adhesive (acrylic/epoxy)",
                    manufacturer="DuPont", grade="Pyralux bonding", process="B-stage thermoset"),
         props=[
             p("physical.density", 1300, "kg/m^3", 4, "estimated", src("아크릴/에폭시 접착 추정")),
             p("thermal.glass_transition", 333, "K", 4, "estimated", src("아크릴 접착 Tg 추정"), notes="아크릴계 저Tg ~60℃"),
             p("thermal.expansion_linear", 1.2e-4, "1/K", 4, "estimated", src("접착제 고CTE 추정"), notes="~120 ppm(고CTE, 굴곡 신뢰성 이슈)"),
             p("electrical.dielectric_constant", 3.5, "1", 4, "estimated", src("접착제 Dk 추정"), cond={"frequency_hz": 1e6}),
             p("electrical.dissipation_factor", 0.03, "1", 4, "estimated", src("접착제 Df 추정")),
             p("thermal.conductivity", 0.2, "W/(m*K)", 4, "estimated", src("폴리머 접착 추정")),
         ]),
    # 10) EMI 차폐필름 (사용자 명시)
    dict(code="FPCB-EMI-FILM", name="EMI Shielding Film (FPCB)", category="composite",
         description="FPCB 전자파 차폐필름 — 절연PI + 금속(Ag/Cu) 차폐층 + 이방도전 접착제. 회로 위 라미네이션.",
         attrs=dict(subsystem="pcb", material_class="EMI shielding film (Ag/Cu + conductive adhesive)",
                    manufacturer="Tatsuta Electric Wire & Cable", grade="SF-PC series",
                    process="metal shield + isotropic/anisotropic conductive adhesive"),
         props=[
             p("physical.density", 2500, "kg/m^3", 4, "estimated", src("금속층 포함 복합 추정")),
             p("thermal.max_service_temp", 423, "K", 4, "estimated", src("접착층 제한 추정"), notes="~150℃"),
             p("electrical.surface_resistivity", 0.05, "ohm", 4, "estimated", src("차폐/도전층 추정"), notes="도전층 저저항(그라운드 접속), 이방도전 접착으로 z접속. 차폐효과 SE ~40–90 dB(1 MHz–1 GHz, Ag/Cu 도전층의 흡수·반사 손실) — SE(dB)는 스칼라 물성이 아니라 여기 참고로만 기록"),
             p("thermal.conductivity", 0.5, "W/(m*K)", 4, "estimated", src("금속 함유 복합 추정")),
         ]),
    # 11) 솔더마스크 PSR (감광성 솔더레지스트)
    dict(code="PCB-PSR", name="Solder Mask / PSR (photoimageable)", category="polymer",
         description="PCB 솔더마스크 원자재 — 감광성 솔더레지스트(PSR). 회로 절연·솔더 정의.",
         attrs=dict(subsystem="pcb", material_class="photoimageable solder resist (PSR)",
                    manufacturer="Taiyo Ink", grade="PSR-4000 series", process="LPI photoimageable"),
         props=[
             p("physical.density", 1300, "kg/m^3", 4, "estimated", src("PSR 경화물 추정")),
             p("thermal.glass_transition", 423, "K", 3, source=src("Taiyo PSR-4000(DMA)", mfr="Taiyo Ink"), notes="Tg ~120–150℃"),
             p("electrical.dielectric_constant", 3.9, "1", 3, cond={"frequency_hz": 1e6}, source=src("Taiyo PSR-4000", mfr="Taiyo Ink"), notes="Dk @1 MHz"),
             p("electrical.dissipation_factor", 0.02, "1", 4, "estimated", src("PSR Df 추정")),
             p("electrical.comparative_tracking_index", 200, "V", 4, "estimated", src("PSR CTI 추정"), notes="CTI ≥175–250 V급"),
             p("thermal.expansion_linear", 6.0e-5, "1/K", 4, "estimated", src("PSR CTE 추정")),
             p("thermal.flammability_ul94", vtext="V-0", tier=3, source=src("Taiyo PSR-4000", mfr="Taiyo Ink")),
         ]),
]


def ensure_material(code, name, category, description, attrs):
    with SessionLocal() as s:
        m = s.query(Material).filter(Material.material_code == code).one_or_none()
        if m:
            return m.id, False
    r = M.register_material(name=name, category=category, material_code=code,
                            description=description, attributes=attrs)
    if "error" in r:
        print(f"  !! register_material {code}: {r['error']}"); return None, False
    return r["material_id"], True


def run():
    total_props = 0
    errors = 0
    for m in MATERIALS:
        mid, created = ensure_material(m["code"], m["name"], m["category"], m["description"], m["attrs"])
        if mid is None:
            errors += 1; continue
        n_ok = 0
        for pr in m["props"]:
            pr = dict(pr)
            key = pr.pop("property_key")
            r = M.register_property(mid, key, **pr)
            if "error" in r:
                print(f"  !! {m['code']} {key}: {r['error']}"); errors += 1
            else:
                n_ok += 1; total_props += 1
        print(f"[{'NEW' if created else 'EXIST'}] {mid:3d} {m['code']:18s} props+{n_ok}")
    print(f"\nDONE — {len(MATERIALS)} materials, {total_props} property values, {errors} errors")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
