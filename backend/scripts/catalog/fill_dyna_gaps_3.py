# 잔여 68종 DYNA 물성 마무리 — 계열 대표값. 기존 근거값은 덮지 않는다.
import sys

import mcp_server as M
from app.db import SessionLocal
from app.models import Material, PropertyValue

CRC = dict(source_title="CRC Handbook of Chemistry and Physics, 97th ed.", source_kind="book")
ASM_M = dict(source_title="ASM Metals Handbook — Properties and Selection: Nonferrous Alloys and Special-Purpose Materials", source_kind="book")
ASM_S = dict(source_title="ASM Metals Handbook — Properties and Selection: Irons, Steels, and High-Performance Alloys", source_kind="book")
ASM_C = dict(source_title="ASM Engineered Materials Handbook — Ceramics and Glasses", source_kind="book")
COMP = dict(source_title="ASM Engineered Materials Handbook — Composites", source_kind="book")
POLY = dict(source_title="Polymer Handbook (Brandrup, Immergut, Grulke), 4th ed.", source_kind="book")
ELAS = dict(source_title="Handbook of Pressure-Sensitive Adhesive Technology (Satas), 3rd ed.", source_kind="book")
RUB = dict(source_title="Rubber Technology Handbook (Hofmann)", source_kind="book")

# (이름, RO, E, PR, HC, TC, CTE, tier, src)
T = [
    ("SUS201_annealed Bilinear",  None, None, None, 500, None, None, 2, ASM_S),
    # 점착·폼·실리콘 패드(초연질) — 등방 근사, PR≈0.49(비압축) / 폼은 낮음
    ("PSA Acrylic General (3M 467MP)", None, 3.0e5, 0.49, 1500, None, 2.0e-4, 4, ELAS),
    ("Thermal Interface Tape",    None, 5.0e5, 0.49, 1200, None, 2.0e-4, 4, ELAS),
    ("Foam PE General",           None, 3.0e6, 0.30, 1900, None, 1.5e-4, 4, RUB),
    ("Foam PU Impact Absorber",   None, 1.0e6, 0.30, 1500, None, 1.5e-4, 4, RUB),
    ("PORON 4701 Foam Gasket",    None, 5.0e5, 0.30, 1500, None, 1.5e-4, 4, RUB),
    ("Damping Speaker Mount",     None, 2.0e6, 0.48, 1500, None, 2.0e-4, 4, RUB),
    ("Damping Haptic Isolator",   None, 2.0e6, 0.48, 1500, None, 2.0e-4, 4, RUB),
    ("Thermal Pad Silicone Soft 1.5 W/mK",   None, 3.0e5, 0.49, 1100, None, 2.5e-4, 4, RUB),
    ("Thermal Pad Silicone Medium 3.0 W/mK", None, 8.0e5, 0.49, 1100, None, 2.5e-4, 4, RUB),
    ("Thermal Pad Silicone High 5.0 W/mK",   None, 1.5e6, 0.49, 1100, None, 2.5e-4, 4, RUB),
    # 광학·구조 폴리머
    ("COP Zeonex (Cyclo-Olefin Polymer)", None, None, None, None, 0.15, None, 4, POLY),
    ("APEL 5014CL (COC, Mitsui)", None, 2.4e9, None, None, None, None, 4, POLY),
    ("OKP High-Index Optical Polyester", None, 2.8e9, 0.36, 1300, 0.20, None, 4, POLY),
    ("PEEK Film (Diaphragm)",     None, None, None, None, 0.25, None, 2, POLY),
    ("PEI Ultem Film",            None, None, None, None, 0.22, 5.6e-5, 2, POLY),
    ("PEN Film (Diaphragm)",      None, None, None, None, 0.15, 2.0e-5, 4, POLY),
    ("Colorless PI (CPI)",        1400, None, 0.34, 1090, 0.15, None, 4, POLY),
    ("Polarizer (TAC/PVA)",       None, None, None, None, 0.20, 6.0e-5, 4, POLY),
    ("PBT (structural)",          None, None, None, None, 0.25, None, 2, POLY),
    ("LDS Plastic (PC + LDS additive)", None, None, None, None, 0.25, None, 4, POLY),
    ("Prism Sheet / BEF (PET)",   None, None, None, None, 0.24, 7.0e-5, 2, POLY),
    ("PVDF Binder",               None, None, None, None, 0.19, 1.3e-4, 2, POLY),
    ("Parylene Conformal Coating", None, None, None, None, None, 3.5e-5, 4, POLY),
    ("FR-4 Epoxy Resin (matrix)", None, None, None, None, 0.20, None, 2, POLY),
    ("FPCB Bonding Adhesive (acrylic/epoxy)", None, 1.0e9, 0.40, 1400, None, None, 4, POLY),
    # 복합재
    ("Epoxy Molding Compound (EMC)", None, None, None, None, 0.80, None, 4, COMP),
    ("Underfill Epoxy",           1600, None, 0.35, 1000, 0.50, None, 4, COMP),
    ("Prepreg (Glass Cloth/Epoxy)", 1900, None, 0.14, 1100, 0.35, None, 4, COMP),
    ("Conductive Silver Epoxy (die attach)", 3000, None, 0.35, 800, None, None, 4, COMP),
    ("Glass-Filled Nylon (PA6-GF30)", None, None, None, None, None, 3.0e-5, 4, COMP),
    ("Graphite PGS (Pyrolytic Sheet)", None, 1.0e10, 0.20, 700, None, 1.0e-6, 4, COMP),
    ("ACF (Anisotropic Conductive Film)", None, None, None, None, 0.40, 6.0e-5, 4, COMP),
    ("Carbon Black (conductive additive)", None, None, None, 850, None, None, 2, CRC),
    ("Quantum Dot Film (QDEF)",   None, None, None, 1400, None, None, 4, COMP),
    ("Copper Clad Laminate (CCL)", None, None, None, 1100, None, None, 4, COMP),
    ("Graphite Anode",            None, 1.0e10, 0.20, 710, None, None, 4, CRC),
    ("Silicon Anode",             None, None, None, None, None, 2.6e-6, 4, CRC),
    ("PE/PP Separator",            900, None, None, None, None, None, 4, POLY),
    # 세라믹·반도체
    ("Aluminosilicate Cover Glass", None, None, None, None, 1.0, None, 2, ASM_C),
    ("Ultra-Thin Glass (UTG, foldable)", None, None, None, None, 1.0, 8.0e-6, 4, ASM_C),
    ("Periscope Prism Glass (high-index)", None, None, None, None, 1.0, None, 4, ASM_C),
    ("Quartz Crystal (SiO2)",     None, None, None, None, 1.4, None, 2, ASM_C),
    ("Thin-Film Encapsulation (Al2O3)", None, None, None, None, 1.5, 7.0e-6, 4, ASM_C),
    ("Anodized Aluminum Layer (Al2O3)", None, 1.4e11, 0.24, 880, None, None, 4, ASM_C),
    ("BaTiO3 MLCC Dielectric",    None, None, None, None, 2.6, 1.0e-5, 4, ASM_C),
    ("PZT Piezoelectric",         None, None, None, None, 1.2, 4.0e-6, 4, ASM_C),
    ("ZnO Varistor (TVS)",        None, None, None, None, 20.0, None, 4, ASM_C),
    ("Lithium Tantalate (LiTaO3) SAW", None, None, None, None, 4.6, None, 4, ASM_C),
    ("Solid Electrolyte (LLZO Garnet)", None, None, None, None, 1.4, None, 4, ASM_C),
    ("NCM811 Cathode",            None, None, None, None, None, 1.0e-5, 4, ASM_C),
    ("DLC Coating (diamond-like carbon)", None, None, None, None, None, 2.3e-6, 4, ASM_C),
    ("TiN PVD Coating",           None, None, None, None, None, 9.4e-6, 4, ASM_C),
    ("2D Material (MoS2 monolayer)", None, None, None, None, None, 7.0e-6, 4, CRC),
    ("LTPS Polysilicon",          None, None, None, None, 30.0, 2.6e-6, 4, CRC),
    ("GaN HEMT (RF PA)",          None, 3.0e11, 0.25, 490, None, None, 2, CRC),
    ("E-Glass Cloth (reinforcement)", None, None, None, 800, 1.1, None, 2, ASM_C),
    ("OLED Emitter Layer (Ir phosphor)", None, None, None, 1000, None, None, 4, POLY),
    ("On-Chip Lens (OCL)",        None, None, None, 1200, None, None, 4, POLY),
    ("OLED Cathode (Mg:Ag)",      None, None, None, 1000, None, None, 4, CRC),
    # 금속
    ("Sintered Silver",           None, None, None, None, None, 1.97e-5, 4, CRC),
    ("Beryllium Copper (spring/contact)", None, None, None, None, None, 1.7e-5, 2, ASM_M),
    ("Liquid Metal (Zr-based BMG)", None, None, None, None, 5.0, None, 4, ASM_M),
    ("SMA Nitinol (NiTi actuator)", None, None, None, None, 18.0, None, 2, ASM_M),
    ("Tantalum Capacitor (Ta/Ta2O5)", None, None, None, None, 57.0, None, 2, CRC),
    ("Battery Al Current Collector Foil", None, 6.9e10, 0.33, 896, None, None, 2, ASM_M),
    ("ImAg Surface Finish",       None, 8.3e10, 0.37, 235, None, None, 2, CRC),
    ("Liquid Electrolyte (LiPF6 carbonate)", None, None, None, None, None, None, 4, CRC),
]

KEYS = [("physical.density", "kg/m^3"), ("mechanical.youngs_modulus", "Pa"),
        ("mechanical.poisson_ratio", "1"), ("thermal.specific_heat", "J/(kg*K)"),
        ("thermal.conductivity", "W/(m*K)"), ("thermal.expansion_linear", "1/K")]
NOTE = ("계열 대표값 — 해석 입력용 등방 근사. 실제 제품은 그레이드·배합에 따라 다르므로 "
        "정밀 해석 시 업체 데이터시트로 대체 권장")


def run():
    with SessionLocal() as s:
        name_to_id = {m.name: m.id for m in s.query(Material).all()}
        existing = {(mid, k) for mid, k in s.query(
            PropertyValue.material_id, PropertyValue.property_key).filter(
            PropertyValue.value_num.isnot(None))}
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
            if (mid, key) in existing:
                skipped += 1
                continue
            method = "handbook" if tier <= 2 else "estimated"
            r = M.register_property(mid, key, value=v, unit=unit, method=method,
                                    quality_tier=tier, notes=(None if tier <= 2 else NOTE), **src)
            if "error" in r:
                print(f"  !! {name} {key}: {r['error']}"); errors += 1
            else:
                n += 1; added += 1
        if n:
            print(f"  [{mid:3d}] {name[:42]:42s} +{n}")
    print(f"\nDONE — 추가 {added} / 기존보존 {skipped} / 오류 {errors}")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
