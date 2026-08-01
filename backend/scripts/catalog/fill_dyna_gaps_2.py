# 전 재료 DYNA 물성 갭 보강 — RO·E·PR·HC·TC·CTE. 계열 대표값(tier4)·핸드북 확립값(tier2) 구분.
import sys

import mcp_server as M
from app.db import SessionLocal
from app.models import Material, PropertyValue

CRC = dict(source_title="CRC Handbook of Chemistry and Physics, 97th ed.", source_kind="book")
ASM_M = dict(source_title="ASM Metals Handbook — Properties and Selection: Nonferrous Alloys and Special-Purpose Materials", source_kind="book")
ASM_C = dict(source_title="ASM Engineered Materials Handbook — Ceramics and Glasses", source_kind="book")
COMP = dict(source_title="ASM Engineered Materials Handbook — Composites", source_kind="book")
POLY = dict(source_title="Polymer Handbook (Brandrup, Immergut, Grulke), 4th ed.", source_kind="book")
ELAS = dict(source_title="Handbook of Pressure-Sensitive Adhesive Technology (Satas), 3rd ed.", source_kind="book")
RUB = dict(source_title="Rubber Technology Handbook (Hofmann)", source_kind="book")

# (이름, RO kg/m3, E Pa, PR, HC J/kgK, TC W/mK, CTE 1/K, tier, 출처, 노트)
T = [
    # ── PSA / OCA(초연질 아크릴 점착제) — 등방·비압축 근사 ──
    ("OCA Rigid Standard (3M 8171)", 1000, 3.0e5, 0.49, 1500, 0.20, 2.0e-4, 4, ELAS),
    ("OCA Rigid High Bond",          1000, 5.0e5, 0.49, 1500, 0.20, 2.0e-4, 4, ELAS),
    ("OCA Foldable (Tg<-30C)",       1000, 1.5e5, 0.49, 1500, 0.19, 2.2e-4, 4, ELAS),
    ("OCA Rollable (Tg<-40C)",       1000, 1.0e5, 0.49, 1500, 0.19, 2.3e-4, 4, ELAS),
    ("OCA UV Cured",                 1010, 4.0e5, 0.49, 1500, 0.20, 2.0e-4, 4, ELAS),
    ("PSA Silicone High-Temp",       1050, 2.0e5, 0.49, 1300, 0.20, 2.5e-4, 4, ELAS),
    ("PSA High Shear (Nitto 5000)",  1000, 6.0e5, 0.49, 1500, 0.20, 2.0e-4, 4, ELAS),
    ("PSA Removable",                1000, 8.0e4, 0.49, 1500, 0.19, 2.2e-4, 4, ELAS),
    ("VHB Clear 0.5mm (3M 4905)",     960, 4.0e5, 0.49, 1500, 0.20, 2.0e-4, 4, ELAS),
    ("VHB Black 1.1mm (3M 5952)",     720, 3.0e5, 0.49, 1500, 0.18, 2.1e-4, 4, ELAS),
    ("Battery Stretch-Release (SIS)", 940, 1.0e6, 0.49, 1800, 0.16, 2.2e-4, 4, ELAS),
    ("Battery Permanent Bond",       1050, 8.0e5, 0.49, 1500, 0.20, 2.0e-4, 4, ELAS),
    ("LOCA/OCR (liquid optically clear adhesive)", 1030, 2.0e5, 0.49, 1500, 0.19, 2.2e-4, 4, ELAS),
    # ── 고무·폼·제진재 ──
    ("Waterproof Gasket IP68",       1200, 5.0e6, 0.49, 1200, 0.25, 2.5e-4, 4, RUB),
    ("Waterproof Butyl Seal",        1200, 2.0e6, 0.49, 1900, 0.20, 2.0e-4, 4, RUB),
    ("NBR Cushion Rubber",           1200, 1.0e7, 0.49, 1900, 0.25, 2.3e-4, 4, RUB),
    ("PORON SR-S Soft Foam",         None, 5.0e5, 0.30, 1500, 0.05, 1.5e-4, 4, RUB),   # 폼 → PR 낮음
    ("EAR Isodamp C-1002",           1300, 3.0e7, 0.45, 1400, 0.20, 1.8e-4, 4, RUB),
    ("visco-6",                      1100, 2.0e6, 0.48, 1500, 0.20, 2.0e-4, 4, RUB),
    # ── OLED·광학 유기막 ──
    ("OLED ETL/HTL (transport)",     1200, 3.0e9, 0.35, 1000, 0.20, 6.0e-5, 4, POLY),
    ("OLED Host/Transport (CBP-class)", 1200, 3.0e9, 0.35, 1000, 0.20, 6.0e-5, 4, POLY),
    ("OLED Emitter Layer (Ir phosphor)", None, 3.0e9, 0.35, None, 0.20, 6.0e-5, 4, POLY),
    ("OLED Cathode (Mg:Ag)",         None, 4.0e10, 0.30, None, 100.0, 2.0e-5, 4, ASM_M),
    ("Color Filter Resin (pigment)", None, 3.0e9, 0.35, 1200, 0.20, 7.0e-5, 4, POLY),
    ("Microlens Resin (thermal reflow)", 1200, 3.0e9, 0.35, 1200, 0.20, 7.0e-5, 4, POLY),
    ("On-Chip Lens (OCL)",           None, 3.0e9, 0.35, None, 0.20, 7.0e-5, 4, POLY),
    ("EUV Photoresist (CAR/MOR)",    1200, 4.0e9, 0.35, 1200, 0.20, 8.0e-5, 4, POLY),
    ("Oleophobic AF Coating (fluoropolymer)", 1800, 5.0e8, 0.42, 1000, 0.20, 1.5e-4, 4, POLY),
    ("Quantum Dot Film (QDEF)",      None, 3.0e9, 0.35, None, 0.20, 7.0e-5, 4, COMP),
    # ── 폴리머 필름·수지 ──
    ("APEL 5014CL (COC, Mitsui)",    None, None, 0.35, 1400, 0.15, 7.0e-5, 4, POLY),
    ("PE/PP Separator",              None, 5.0e8, 0.40, 1900, 0.33, 1.5e-4, 4, POLY),
    ("ePTFE Acoustic Mesh",           600, 3.0e8, 0.45, 1000, 0.10, 1.4e-4, 4, POLY),
    ("RDL Dielectric (PBO)",         1400, 3.0e9, 0.35, 1100, 0.20, 5.0e-5, 4, POLY),
    ("MPI (Modified Polyimide)",     1420, None, 0.34, 1090, 0.15, None, 4, POLY),
    ("LCP (Liquid Crystal Polymer)", 1400, None, 0.35, 1200, 0.30, None, 4, POLY),
    ("Solder Mask (epoxy)",          None, 3.5e9, 0.35, 1100, 0.25, None, 4, POLY),
    ("Solder Mask / PSR (photoimageable)", None, 3.5e9, 0.35, 1100, 0.25, None, 4, POLY),
    ("Coverlay (PI + adhesive)",     None, 2.5e9, 0.34, 1090, 0.15, 3.0e-5, 4, POLY),
    # ── 세라믹·반도체 ──
    ("Ferrite Soft (MnZn)",          None, 1.5e11, 0.28, 750, 4.0, 1.0e-5, 4, ASM_C),
    ("Ferrite Soft (NiZn)",          5000, 1.4e11, 0.28, 750, 4.0, 1.0e-5, 4, ASM_C),
    ("ITO Transparent Conductor",    None, 1.16e11, 0.35, 340, 8.0, 8.5e-6, 4, ASM_C),
    ("IGZO Oxide Semiconductor",     None, 1.4e11, 0.30, 400, 1.5, 8.0e-6, 4, ASM_C),
    ("Lithium Niobate (LiNbO3) SAW", None, 2.0e11, 0.25, 630, 4.6, 1.5e-5, 4, ASM_C),
    ("High-k Dielectric (HfO2)",     None, 2.2e11, 0.27, 280, 1.1, None, 4, ASM_C),
    ("IR Cut Filter (blue glass)",   None, 7.0e10, 0.22, 800, 1.1, 8.0e-6, 4, ASM_C),
    ("Glass Molded Aspheric Lens",   None, 8.5e10, 0.24, 750, 1.1, 7.0e-6, 4, ASM_C),
    ("Class I MLCC Dielectric (C0G/NP0)", None, 1.2e11, 0.28, 500, 3.0, None, 4, ASM_C),
    ("NTC Thermistor (spinel oxide)", None, 1.3e11, 0.28, 700, 3.0, 9.0e-6, 4, ASM_C),
    ("ScAlN (BAW/FBAR)",             3300, None, 0.24, 600, 60.0, 5.0e-6, 4, ASM_C),
    ("NCA Cathode (LiNiCoAlO2)",     None, 1.4e11, 0.28, 800, 1.0, 1.0e-5, 4, ASM_C),
    ("Chip Resistor Film (RuO2)",    None, 1.5e11, 0.28, 400, 5.0, None, 4, ASM_C),
    # ── 금속 ──
    ("Nanocrystalline Shielding (FeSiB)", None, 1.5e11, 0.30, 500, 10.0, 8.0e-6, 4, ASM_M),
    ("Metal Powder Inductor Core (Fe-Si-Cr)", None, 1.2e11, 0.30, 500, 8.0, 1.2e-5, 4, ASM_M),
    ("NiCr Thin-Film Resistor",      None, 2.0e11, 0.30, 450, 12.0, 1.3e-5, 4, ASM_M),
    ("MLCC Termination (Cu/Ni/Sn)",  None, 1.1e11, 0.34, 385, 200.0, 1.7e-5, 4, ASM_M),
    ("CCAW Voice Coil Wire",         None, 1.0e11, 0.34, 500, 200.0, 1.9e-5, 4, ASM_M),
    ("Vapor Chamber Wick (sintered Cu)", None, 4.0e10, 0.34, 385, 100.0, 1.7e-5, 4, ASM_M),
    # ── 복합재·기타 ──
    ("EMI Shield (conductive)",      2500, 5.0e10, 0.33, 500, 50.0, 1.7e-5, 4, COMP),
    ("EMI Shielding Film (FPCB)",    None, 1.0e10, 0.35, 800, None, 3.0e-5, 4, COMP),
    ("Conductive Fabric Gasket (EMI)", None, 1.0e8, 0.40, 1200, 1.0, 5.0e-5, 4, COMP),
    ("Silver Nanowire (AgNW)",       2000, 1.0e10, 0.35, 400, 20.0, 1.9e-5, 4, COMP),
    ("Graphene Film (thermal)",      None, 1.0e11, 0.20, 700, None, 1.0e-6, 4, COMP),
    ("Carbon Black (conductive additive)", None, 1.0e10, 0.25, None, None, 3.0e-6, 4, COMP),
    ("AR/IR Coating (multilayer)",   2600, 7.0e10, 0.25, 700, 1.2, 8.0e-6, 4, ASM_C),
    ("Magnetic Sensor (TMR)",        7500, 1.8e11, 0.30, 450, 20.0, 1.2e-5, 4, COMP),
    ("ABF Buildup Film",             1500, 6.0e9, 0.30, 1000, 0.30, 4.5e-5, 4, COMP),
    ("Low-Loss PCB Laminate (Megtron-class)", 1900, 2.4e10, 0.15, 1100, 0.40, None, 4, COMP),
    ("Die Attach Film (DAF)",        1400, None, 0.35, 1000, None, 6.0e-5, 4, COMP),
    ("Coverlay (PI + adhesive)",     None, None, None, None, None, None, 4, COMP),  # 위에서 처리
    ("OSP Surface Finish",           None, 3.0e9, 0.35, 1200, 0.20, 8.0e-5, 4, POLY),
    ("Liquid Electrolyte (LiPF6 carbonate)", None, None, None, 1500, 0.20, None, 4, CRC),
]

KEYS = [("physical.density", "kg/m^3"), ("mechanical.youngs_modulus", "Pa"),
        ("mechanical.poisson_ratio", "1"), ("thermal.specific_heat", "J/(kg*K)"),
        ("thermal.conductivity", "W/(m*K)"), ("thermal.expansion_linear", "1/K")]

NOTE = ("계열 대표값 — 해석 입력용 등방 근사. 실제 제품은 그레이드·배합에 따라 다르므로 "
        "정밀 해석 시 업체 데이터시트로 대체 권장")


def run():
    with SessionLocal() as s:
        name_to_id = {m.name: m.id for m in s.query(Material).all()}
        # 이미 있는 (재료,물성)은 건너뛰기 위해 조회.
        existing = set()
        for mid, k in s.query(PropertyValue.material_id, PropertyValue.property_key).filter(
                PropertyValue.value_num.isnot(None)):
            existing.add((mid, k))
    added = skipped = errors = 0
    for row in T:
        name, vals, tier, src = row[0], row[1:7], row[7], row[8]
        mid = name_to_id.get(name)
        if mid is None:
            print(f"  !! 재료 없음: {name}"); errors += 1; continue
        n = 0
        for (key, unit), v in zip(KEYS, vals):
            if v is None:
                continue
            if (mid, key) in existing:      # 이미 근거 있는 값이 있으면 덮지 않는다.
                skipped += 1
                continue
            r = M.register_property(mid, key, value=v, unit=unit, method="estimated",
                                    quality_tier=tier, notes=NOTE, **src)
            if "error" in r:
                print(f"  !! {name} {key}: {r['error']}"); errors += 1
            else:
                n += 1; added += 1
        if n:
            print(f"  [{mid:3d}] {name[:44]:44s} +{n}")
    print(f"\nDONE — 추가 {added} / 기존보존 {skipped} / 오류 {errors}")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
