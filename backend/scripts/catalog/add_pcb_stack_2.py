# PCB 2차 보강 — 기존 얇은 재료(ENIG/ImAg/OSP/MPI/LCP/Megtron) 물성 채우기 + HVLP동박·LCP필름 신규.
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


ASM = src("ASM Handbook Vol.2 — Copper and Copper Alloys", "book")
ASM_NI = src("ASM Handbook Vol.2 — Nickel, Cobalt and Their Alloys", "book")
ASM_PM = src("ASM Handbook — Precious Metals (Au/Ag) properties", "book")
IPC4552 = lambda mfr=None: src("IPC-4552B — Electroless Ni/Immersion Au (ENIG) Specification", "standard", mfr)  # noqa: E731
IPC4553 = lambda mfr=None: src("IPC-4553A — Immersion Silver (ImAg) Specification", "standard", mfr)  # noqa: E731
IPC4555 = lambda mfr=None: src("IPC-4555 — Organic Solderability Preservative (OSP) Specification", "standard", mfr)  # noqa: E731
IPC4562 = lambda mfr: src("IPC-4562A — Metal Foil for Printed Board Applications", "standard", mfr)  # noqa: E731
IPC4204 = lambda mfr: src("IPC-4204 — Flexible Metal-Clad Dielectrics", "standard", mfr)  # noqa: E731


def p(key, value=None, unit=None, tier=3, method="datasheet", source=None,
      cond=None, vtext=None, notes=None):
    d = dict(property_key=key, value=value, value_text=vtext, unit=unit,
             quality_tier=tier, method=method, conditions=cond, notes=notes)
    d.update(source or {})
    return d


# ── 기존 재료 보강 (code 없이 이름으로 매칭) ────────────────────────────────
ENRICH = {
    # ENIG 표면처리 (Ni-P 하지 + Au 침적)
    "ENIG Surface Finish (Ni/Au)": [
        p("physical.density", 8400, "kg/m^3", 3, source=IPC4552(), notes="Ni-P(8.4) 주도, Au 박층(0.05–0.1µm)"),
        p("mechanical.hardness_vickers", 550, "HV", 3, source=IPC4552(), notes="무전해 Ni-P(8–10%P) as-plated ~500–600 HV"),
        p("electrical.resistivity_volume", 6.0e-7, "ohm*m", 3, source=IPC4552(), notes="Ni-P 비정질 ~60 µΩ·cm (순Ni 7의 ~9배) — 고주파 손실 원인"),
        p("thermal.conductivity", 7.0, "W/(m*K)", 4, "estimated", IPC4552(), notes="비정질 Ni-P ~5–9 W/mK(순Ni 90 대비 급감)"),
        p("mechanical.youngs_modulus", 1.9e11, "Pa", 2, "handbook", ASM_NI, notes="Ni-P ~190 GPa"),
        p("thermal.expansion_linear", 1.3e-5, "1/K", 2, "handbook", ASM_NI, notes="Ni ~13 ppm/K"),
        p("chemical.corrosion_rate", 1.0e-12, "m/s", 4, "estimated", IPC4552(), notes="Au 캡이 Ni 산화 차단 — 부식률 극저(정성)"),
        p("thermal.melting_point", 1728, "K", 2, "handbook", ASM_NI, notes="Ni 1455℃"),
    ],
    # ImAg 표면처리
    "ImAg Surface Finish": [
        p("physical.density", 10490, "kg/m^3", 2, "handbook", ASM_PM, notes="Ag 10.49 g/cc"),
        p("electrical.conductivity", 6.30e7, "S/m", 2, "handbook", ASM_PM, notes="★ Ag 최고 전도(63 MS/m) — ENIG Ni-P 대비 고주파 손실 유리"),
        p("thermal.conductivity", 429, "W/(m*K)", 2, "handbook", ASM_PM, notes="Ag 429 W/mK(금속 최고)"),
        p("thermal.melting_point", 1235, "K", 2, "handbook", ASM_PM, notes="962℃"),
        p("thermal.expansion_linear", 1.97e-5, "1/K", 2, "handbook", ASM_PM),
        p("mechanical.hardness_vickers", 60, "HV", 4, "estimated", IPC4553(), notes="침적 Ag 연질 박막"),
        p("chemical.chemical_resistance", vtext="황(S)·염소 분위기에서 변색(tarnish) 취약 — creep corrosion 우려", tier=3, source=IPC4553(), notes="ImAg 대표 약점. 보관·포장 관리 필요"),
    ],
    # OSP (유기 솔더러빌리티 보존제) — 초박막 유기층
    "OSP Surface Finish": [
        p("physical.density", 1200, "kg/m^3", 4, "estimated", IPC4555(), notes="아졸계 유기막(서브미크론) 추정"),
        p("thermal.max_service_temp", 533, "K", 3, source=IPC4555(), notes="리플로우(~260℃) 다회 통과 견딤이 요구조건"),
        p("chemical.chemical_resistance", vtext="다회 리플로우 시 열화 — 통상 2–3회 리플로우 한계", tier=3, source=IPC4555(), notes="OSP 대표 한계(다층 실장 시 고려)"),
        p("structure.filler_content", 0.0, "1", 4, "estimated", IPC4555(), notes="순수 유기 아졸 막(무충전)"),
    ],
    # MPI (Modified Polyimide) — 5G 저손실 연성기판
    "MPI (Modified Polyimide)": [
        p("electrical.dielectric_constant", 3.2, "1", 3, cond={"frequency_hz": 1e10}, source=IPC4204("BestPCBs (aggregator)"), notes="Dk @10 GHz — 5G mmWave 대역"),
        p("electrical.dissipation_factor", 0.004, "1", 3, cond={"frequency_hz": 1e10}, source=IPC4204("BestPCBs (aggregator)"), notes="★ Df @10 GHz ~0.004 — 일반 PI(0.01+) 대비 저손실이나 LCP(0.002)보다는 높음"),
        p("chemical.water_absorption_24h", 0.008, "1", 3, source=IPC4204("BestPCBs (aggregator)"), notes="~0.8% — LCP(0.04%)보다 흡습 큼(고습 시 Df 상승)"),
        p("thermal.expansion_linear", 1.8e-5, "1/K", 4, "estimated", IPC4204("BestPCBs (aggregator)"), notes="개질 PI ~18 ppm/K"),
        p("mechanical.youngs_modulus", 3.5e9, "Pa", 4, "estimated", IPC4204("BestPCBs (aggregator)"), notes="개질 PI ~3.5 GPa"),
        p("thermal.max_service_temp", 573, "K", 4, "estimated", IPC4204("BestPCBs (aggregator)"), notes="~300℃"),
    ],
    # LCP — 저손실·초저흡습 연성기판
    "LCP (Liquid Crystal Polymer)": [
        p("electrical.dissipation_factor", 0.002, "1", 3, cond={"frequency_hz": 1e10}, source=IPC4204("Murata"), notes="★ Df @10 GHz ~0.002 — mmWave 안테나 기판 표준"),
        p("electrical.dielectric_constant", 3.0, "1", 3, cond={"frequency_hz": 1e10}, source=IPC4204("Murata"), notes="Dk @10 GHz ~3.0(저Dk·안정)"),
        p("thermal.expansion_linear", 1.7e-5, "1/K", 3, source=IPC4204("Murata"), notes="Cu(17 ppm)와 정합 설계 가능 — 치수안정"),
        p("mechanical.youngs_modulus", 2.3e9, "Pa", 3, source=IPC4204("Murata")),
        p("mechanical.tensile_strength", 2.0e8, "Pa", 3, cond=RT, source=IPC4204("Murata")),
        p("thermal.melting_point", 553, "K", 3, source=IPC4204("Murata"), notes="~280℃(열가소성 — 접착제 없이 융착 가능)"),
    ],
    # Megtron급 저손실 라미네이트
    "Low-Loss PCB Laminate (Megtron-class)": [
        p("electrical.dissipation_factor", 0.002, "1", 3, cond={"frequency_hz": 1.2e10},
          source=src("Panasonic Megtron 6 (R-5775) datasheet", mfr="Panasonic Corporation, Electronic Materials Business Division"),
          notes="★ Df @12 GHz ~0.002 — 표준 FR-4(0.016) 대비 1/8 손실"),
        p("electrical.dielectric_constant", 3.7, "1", 3, cond={"frequency_hz": 1.2e10},
          source=src("Panasonic Megtron 6 (R-5775) datasheet", mfr="Panasonic Corporation, Electronic Materials Business Division"),
          notes="Dk @12 GHz ~3.7(FR-4 4.4보다 낮아 전파지연↓)"),
        p("thermal.glass_transition", 458, "K", 3,
          source=src("Panasonic Megtron 6 datasheet (DSC)", mfr="Panasonic Corporation, Electronic Materials Business Division"),
          notes="Tg ~185℃"),
        p("thermal.decomposition_temp", 683, "K", 3,
          source=src("Panasonic Megtron 6 datasheet (TGA)", mfr="Panasonic Corporation, Electronic Materials Business Division"),
          notes="Td ~410℃"),
        p("chemical.water_absorption_24h", 0.0008, "1", 3,
          source=src("Panasonic Megtron 6 datasheet", mfr="Panasonic Corporation, Electronic Materials Business Division"),
          notes="~0.08%(저흡습 → 고주파 Df 안정)"),
    ],
    # 기존 CCL·프리프레그·FR4 보강
    "Copper Clad Laminate (CCL)": [
        p("electrical.dissipation_factor", 0.016, "1", 3, cond={"frequency_hz": 1e9}, source=src("IPC-4101 base material spec", "standard"), notes="표준 FR-4 CCL Df @1 GHz"),
        p("mechanical.flexural_strength", 4.0e8, "Pa", 3, source=src("IPC-4101 base material spec", "standard")),
        p("thermal.glass_transition", 413, "K", 3, source=src("IPC-4101 base material spec", "standard"), notes="표준 Tg ~140℃"),
    ],
    "Prepreg (Glass Cloth/Epoxy)": [
        p("rheological.gel_time", 150, "s", 3, source=src("IPC-4101 prepreg gel time (typ. 100–200 s @171℃)", "standard"), cond={"temperature_C": 171}, notes="B-stage 겔타임 — 라미네이션 공정창 결정"),
        p("electrical.dissipation_factor", 0.018, "1", 3, cond={"frequency_hz": 1e9}, source=src("IPC-4101 base material spec", "standard")),
        p("structure.filler_content", 0.45, "1", 4, "estimated", src("IPC-4101 resin content 기준", "standard"), notes="수지함량(RC) ~45–55% → 글라스 45–55%"),
    ],
}

# ── 신규 재료 ────────────────────────────────────────────────────────────────
NEW = [
    # HVLP(저조도) 동박 — 5G/고속 신호 표피효과 손실 억제
    dict(code="PCB-CU-HVLP", name="HVLP Low-Profile Copper Foil (5G)", category="metal",
         description="고속·고주파 PCB 도체 — 초저조도(HVLP/VLP) 전해동박. 표피효과 손실 억제.",
         attrs=dict(subsystem="pcb", material_class="HVLP/VLP low-profile ED Cu foil",
                    manufacturer="Mitsui Mining & Smelting", grade="HVLP (Rz<1.5µm)",
                    process="electrodeposition + surface treatment", standard="IPC-4562A",
                    composition="Cu ≥99.8%"),
         props=[
             p("physical.density", 8920, "kg/m^3", 2, "handbook", ASM),
             p("mechanical.tensile_strength", 3.5e8, "Pa", 3, cond=RT, source=IPC4562("Mitsui Mining & Smelting"), notes="HVLP ~330–380 MPa"),
             p("mechanical.elongation_at_break", 0.06, "1", 3, cond=RT, source=IPC4562("Mitsui Mining & Smelting"), notes="저조도 처리 → 연신 다소 낮음"),
             p("mechanical.youngs_modulus", 1.15e11, "Pa", 2, "handbook", ASM),
             p("electrical.conductivity", 5.85e7, "S/m", 3, source=IPC4562("Mitsui Mining & Smelting"), notes="★ 저조도(Rz<1.5µm) → 표피효과 경로 짧아 삽입손실 감소(10 GHz+ 유리)"),
             p("electrical.resistivity_volume", 1.71e-8, "ohm*m", 2, "handbook", ASM),
             p("thermal.conductivity", 390, "W/(m*K)", 2, "handbook", ASM),
             p("thermal.expansion_linear", 1.70e-5, "1/K", 2, "handbook", ASM),
             p("thermal.melting_point", 1358, "K", 2, "handbook", ASM),
             p("structure.crystal_structure", vtext="FCC (fine-grain, 저조도 표면처리 Rz<1.5µm)", tier=3, source=IPC4562("Mitsui Mining & Smelting"), notes="ED HTE(Rz 4–7µm) 대비 조도 1/3 이하"),
         ]),
    # LCP 필름(원자재) — mmWave 안테나 기판
    dict(code="FPCB-LCP-FILM", name="LCP Film (mmWave antenna substrate)", category="polymer",
         description="mmWave 안테나/고속 FPC 베이스 — 액정폴리머 필름. 초저흡습·저손실.",
         attrs=dict(subsystem="pcb", material_class="liquid crystal polymer film",
                    manufacturer="Kuraray", grade="Vecstar CT-Z", process="extruded LCP film",
                    standard="IPC-4204", composition="thermotropic LCP (aromatic polyester)"),
         props=[
             p("physical.density", 1400, "kg/m^3", 3, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray")),
             p("electrical.dielectric_constant", 3.0, "1", 3, cond={"frequency_hz": 1e10}, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray"), notes="Dk @10 GHz"),
             p("electrical.dissipation_factor", 0.002, "1", 3, cond={"frequency_hz": 1e10}, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray"), notes="★ Df @10 GHz ~0.002 — PI(0.01) 대비 1/5"),
             p("chemical.water_absorption_24h", 0.0004, "1", 3, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray"), notes="★ ~0.04% — PI(1.8%)의 1/45. 고습에서도 Df 안정(mmWave 핵심)"),
             p("mechanical.tensile_strength", 2.7e8, "Pa", 3, cond=RT, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray")),
             p("mechanical.youngs_modulus", 4.5e9, "Pa", 3, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray")),
             p("mechanical.elongation_at_break", 0.05, "1", 3, cond=RT, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray")),
             p("thermal.expansion_linear", 1.8e-5, "1/K", 3, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray"), notes="Cu 정합 조절 가능"),
             p("thermal.melting_point", 608, "K", 3, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray"), notes="~335℃ — 열가소성 융착 접합(접착제 불요)"),
             p("thermal.max_service_temp", 523, "K", 3, source=src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray")),
             p("thermal.conductivity", 0.2, "W/(m*K)", 4, "estimated", src("Kuraray Vecstar LCP film datasheet", mfr="Kuraray")),
         ]),
]


def run():
    total = errors = 0
    # 1) 기존 재료 보강.
    with SessionLocal() as s:
        name_to_id = {m.name: m.id for m in s.query(Material).all()}
    for name, props in ENRICH.items():
        mid = name_to_id.get(name)
        if mid is None:
            print(f"  !! 재료 없음: {name}"); errors += 1; continue
        n = 0
        for pr in props:
            pr = dict(pr); key = pr.pop("property_key")
            r = M.register_property(mid, key, **pr)
            if "error" in r:
                print(f"  !! {name} {key}: {r['error']}"); errors += 1
            else:
                n += 1; total += 1
        print(f"[ENRICH] {mid:3d} {name[:44]:44s} +{n}")
    # 2) 신규 재료.
    for m in NEW:
        with SessionLocal() as s:
            ex = s.query(Material).filter(Material.material_code == m["code"]).one_or_none()
            mid = ex.id if ex else None
        if mid is None:
            r = M.register_material(name=m["name"], category=m["category"], material_code=m["code"],
                                    description=m["description"], attributes=m["attrs"])
            if "error" in r:
                print(f"  !! {m['code']}: {r['error']}"); errors += 1; continue
            mid = r["material_id"]
        n = 0
        for pr in m["props"]:
            pr = dict(pr); key = pr.pop("property_key")
            r = M.register_property(mid, key, **pr)
            if "error" in r:
                print(f"  !! {m['code']} {key}: {r['error']}"); errors += 1
            else:
                n += 1; total += 1
        print(f"[NEW]    {mid:3d} {m['code']:18s} +{n}")
    print(f"\nDONE — {total} property values, {errors} errors")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
