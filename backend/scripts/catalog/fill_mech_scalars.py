# 기계 스칼라 보강 — 항복강도·인장강도·파단연신율. σ-ε 곡선 합성의 입력이 된다.
import sys

import mcp_server as M
from app.db import SessionLocal
from app.models import Material, PropertyValue

ASM_M = dict(source_title="ASM Metals Handbook — Properties and Selection: Nonferrous Alloys and Special-Purpose Materials", source_kind="book")
ASM_S = dict(source_title="ASM Metals Handbook — Properties and Selection: Irons, Steels, and High-Performance Alloys", source_kind="book")
ASM_C = dict(source_title="ASM Engineered Materials Handbook — Ceramics and Glasses", source_kind="book")
COMP = dict(source_title="ASM Engineered Materials Handbook — Composites", source_kind="book")
POLY = dict(source_title="Polymer Handbook (Brandrup, Immergut, Grulke), 4th ed.", source_kind="book")
CRC = dict(source_title="CRC Handbook of Chemistry and Physics, 97th ed.", source_kind="book")

NOTE = "계열 대표값 — σ-ε 곡선 합성 및 해석 입력용. 정밀 설계 시 실측/업체 데이터로 대체 권장"
BRITTLE_NOTE = ("취성 재료 — 항복 없이 탄성 구간에서 파단한다. 항복강도는 정의되지 않으므로 "
                "미등록(σ-ε 곡선은 파단까지 선형).")

# (이름키워드, 항복 Pa, UTS Pa, 파단연신율) — None은 생략(취성재는 항복 None).
T = [
    # ── 금속 ──
    ("Battery Cu Current Collector Foil", 1.8e8, 2.4e8, 0.06, ASM_M),
    ("Copper Magnet Wire (enameled)",     1.7e8, 2.3e8, 0.20, ASM_M),
    ("Copper Pillar Bump",                1.5e8, 2.2e8, 0.20, ASM_M),
    ("TSV Copper (through-silicon via)",  2.0e8, 2.8e8, 0.10, ASM_M),
    ("Vapor Chamber Wick (sintered Cu)",  6.0e7, 9.0e7, 0.03, ASM_M),
    ("MLCC Termination (Cu/Ni/Sn)",       1.5e8, 2.2e8, 0.15, ASM_M),
    ("CCAW Voice Coil Wire",              1.6e8, 2.2e8, 0.12, ASM_M),
    ("Battery Al Current Collector Foil", 9.0e7, 1.2e8, 0.03, ASM_M),
    ("Nickel Tab/Interconnect",           1.5e8, 4.0e8, 0.35, ASM_M),
    ("Gold Bonding Wire",                 8.0e7, 2.2e8, 0.045, ASM_M),
    ("Silver Bonding Wire",               6.0e7, 1.8e8, 0.10, ASM_M),
    ("Pd-coated Cu Bonding Wire",         1.6e8, 2.6e8, 0.12, ASM_M),
    ("Sintered Silver",                   3.0e7, 5.0e7, 0.02, ASM_M),
    ("SAC305 Solder Alloy",               3.0e7, 4.5e7, 0.40, ASM_M),
    ("ENIG Surface Finish (Ni/Au)",       6.0e8, 8.0e8, 0.02, ASM_M),
    ("ImAg Surface Finish",               5.0e7, 1.4e8, 0.30, ASM_M),
    ("NdFeB Sintered Magnet (N52)",       None, 8.0e7, 0.001, ASM_M),      # 취성
    ("SMA Nitinol (NiTi actuator)",       2.0e8, 8.0e8, 0.20, ASM_M),
    ("Liquid Metal (Zr-based BMG)",       1.6e9, 1.8e9, 0.02, ASM_M),
    ("Nanocrystalline Shielding (FeSiB)", None, 1.0e9, 0.005, ASM_M),      # 취성 리본
    ("Metal Powder Inductor Core (Fe-Si-Cr)", None, 1.0e8, 0.002, ASM_M),  # 압분 취성
    ("NiCr Thin-Film Resistor",           4.0e8, 6.0e8, 0.02, ASM_M),
    ("Tantalum Capacitor (Ta/Ta2O5)",     1.8e8, 2.5e8, 0.25, ASM_M),
    ("TSV Barrier (Ta/TaN)",              6.0e8, 8.0e8, 0.01, ASM_M),
    ("OLED Cathode (Mg:Ag)",              5.0e7, 1.0e8, 0.05, ASM_M),
    ("M-Film",                            5.0e8, 6.0e8, 0.10, ASM_M),
    ("Beryllium Copper (spring/contact)", 1.0e9, 1.2e9, 0.03, ASM_M),
    ("SUS201_annealed Bilinear",          2.9e8, 6.9e8, 0.55, ASM_S),
    # ── 세라믹·유리·반도체(취성 — 항복 없음) ──
    ("Aluminosilicate Cover Glass",  None, 8.0e8, 0.001, ASM_C),
    ("Ultra-Thin Glass (UTG, foldable)", None, 1.0e9, 0.0015, ASM_C),
    ("Periscope Prism Glass (high-index)", None, 6.0e7, 0.0008, ASM_C),
    ("Glass Molded Aspheric Lens",   None, 6.0e7, 0.0008, ASM_C),
    ("IR Cut Filter (blue glass)",   None, 6.0e7, 0.0008, ASM_C),
    ("Quartz Crystal (SiO2)",        None, 5.0e7, 0.0007, ASM_C),
    ("Zirconia (ZrO2) Ceramic Back", None, 9.0e8, 0.002, ASM_C),
    ("Aluminum Nitride (AlN) BAW",   None, 3.0e8, 0.001, ASM_C),
    ("PZT Piezoelectric",            None, 8.0e7, 0.0008, ASM_C),
    ("BaTiO3 MLCC Dielectric",       None, 1.0e8, 0.0008, ASM_C),
    ("Class I MLCC Dielectric (C0G/NP0)", None, 1.2e8, 0.0009, ASM_C),
    ("Lithium Tantalate (LiTaO3) SAW", None, 1.0e8, 0.0008, ASM_C),
    ("Lithium Niobate (LiNbO3) SAW", None, 1.0e8, 0.0008, ASM_C),
    ("ZnO Varistor (TVS)",           None, 1.0e8, 0.001, ASM_C),
    ("NTC Thermistor (spinel oxide)", None, 1.2e8, 0.001, ASM_C),
    ("Ferrite Soft (MnZn)",          None, 5.0e7, 0.0005, ASM_C),
    ("Ferrite Soft (NiZn)",          None, 5.0e7, 0.0005, ASM_C),
    ("ITO Transparent Conductor",    None, 1.0e8, 0.001, ASM_C),
    ("IGZO Oxide Semiconductor",     None, 1.0e8, 0.001, ASM_C),
    ("TiN PVD Coating",              None, 3.5e8, 0.001, ASM_C),
    ("DLC Coating (diamond-like carbon)", None, 1.0e9, 0.002, ASM_C),
    ("Anodized Aluminum Layer (Al2O3)", None, 2.0e8, 0.002, ASM_C),
    ("Thin-Film Encapsulation (Al2O3)", None, 3.0e8, 0.002, ASM_C),
    ("Crystalline Silicon (device die)", None, 1.7e8, 0.001, CRC),
    ("Capacitive MEMS (Si)",         None, 1.7e8, 0.001, CRC),
    ("SOI Substrate (RF-SOI)",       None, 1.7e8, 0.001, CRC),
    ("LTPS Polysilicon",             None, 1.2e9, 0.002, CRC),
    ("GaN HEMT (RF PA)",             None, 3.0e8, 0.001, CRC),
    ("VCSEL Epitaxy (GaAs/AlGaAs)",  None, 1.0e8, 0.001, CRC),
    ("Solid Electrolyte (LLZO Garnet)", None, 1.0e8, 0.001, ASM_C),
    ("High-k Dielectric (HfO2)",     None, 3.0e8, 0.001, ASM_C),
    ("ScAlN (BAW/FBAR)",             None, 3.0e8, 0.001, ASM_C),
    ("Sapphire Single-Crystal (Al2O3)", None, None, 0.001, ASM_C),
    # ── 폴리머(연성) ──
    ("PI Base Film — Kapton HN (DuPont)", 6.9e7, None, None, POLY),
    ("PI Base Film — Upilex-S (UBE)",     2.0e8, None, None, POLY),
    ("Kapton PI Adhesive Tape",           6.9e7, None, None, POLY),
    ("Colorless PI (CPI)",                8.0e7, 1.5e8, 0.15, POLY),
    ("LCP Film (mmWave antenna substrate)", 1.5e8, None, None, POLY),
    ("PC Optical (Lens Grade)",           6.2e7, 6.8e7, 1.10, POLY),
    ("PC/ABS Blend (housing)",            5.5e7, 6.0e7, 0.60, POLY),
    ("LDS Plastic (PC + LDS additive)",   6.0e7, 6.5e7, 0.30, POLY),
    ("PMMA Optical (Acrylic)",            None, 7.0e7, 0.025, POLY),   # 취성
    ("COP Zeonex (Cyclo-Olefin Polymer)", None, 6.0e7, 0.03, POLY),    # 취성
    ("APEL 5014CL (COC, Mitsui)",         None, None, None, POLY),
    ("OKP High-Index Optical Polyester",  None, 6.0e7, 0.03, POLY),
    ("PEEK Film (Diaphragm)",             9.7e7, 1.0e8, 0.45, POLY),
    ("PEI Ultem Film",                    1.0e8, 1.1e8, 0.60, POLY),
    ("PEN Film (Diaphragm)",              1.2e8, 2.0e8, 0.60, POLY),
    ("PBT (structural)",                  5.5e7, 6.0e7, 0.15, POLY),
    ("PTFE (RF coax dielectric)",         1.0e7, 2.5e7, 3.0, POLY),
    ("PVDF Binder",                       4.5e7, 5.0e7, 0.30, POLY),
    ("Prism Sheet / BEF (PET)",           8.0e7, 1.8e8, 1.2, POLY),
    ("Polarizer (TAC/PVA)",               5.0e7, 8.0e7, 0.30, POLY),
    ("Parylene Conformal Coating",        4.0e7, 6.0e7, 0.20, POLY),
    ("RDL Dielectric (PBO)",              1.0e8, 1.5e8, 0.30, POLY),
    ("PE/PP Separator",                   3.0e7, 1.4e8, 1.0, POLY),
    ("ePTFE Acoustic Mesh",               5.0e6, 2.0e7, 1.5, POLY),
    ("Solder Mask / PSR (photoimageable)", None, 6.0e7, 0.03, POLY),
    ("Solder Mask (epoxy)",               None, 6.0e7, 0.03, POLY),
    ("FR-4 Epoxy Resin (matrix)",         None, 8.0e7, 0.04, POLY),
    ("Oleophobic AF Coating (fluoropolymer)", None, 2.0e7, 0.05, POLY),
    ("Microlens Resin (thermal reflow)",  None, 6.0e7, 0.03, POLY),
    ("Color Filter Resin (pigment)",      None, 6.0e7, 0.03, POLY),
    ("On-Chip Lens (OCL)",                None, 6.0e7, 0.03, POLY),
    ("EUV Photoresist (CAR/MOR)",         None, 5.0e7, 0.02, POLY),
    ("OLED ETL/HTL (transport)",          None, 5.0e7, 0.01, POLY),
    ("OLED Host/Transport (CBP-class)",   None, 5.0e7, 0.01, POLY),
    ("OLED Emitter Layer (Ir phosphor)",  None, 5.0e7, 0.01, POLY),
    ("FPCB Bonding Adhesive (acrylic/epoxy)", None, 2.0e7, 0.50, POLY),
    ("Coverlay (PI + adhesive)",          6.0e7, 1.2e8, 0.40, POLY),
    # ── 복합재 ──
    ("FR4 Glass-Epoxy Laminate",     None, 3.1e8, 0.02, COMP),   # 취성 적층재
    ("High-Tg FR-4 Prepreg (7628 glass)", None, 4.15e8, 0.02, COMP),
    ("Prepreg (Glass Cloth/Epoxy)",  None, 3.5e8, 0.02, COMP),
    ("Copper Clad Laminate (CCL)",   None, 3.1e8, 0.02, COMP),
    ("Low-Loss PCB Laminate (Megtron-class)", None, 4.0e8, 0.02, COMP),
    ("BT Resin",                     None, 1.2e8, 0.02, COMP),
    ("ABF Buildup Film",             None, 1.0e8, 0.05, COMP),
    ("Epoxy Molding Compound (EMC)", None, 1.2e8, 0.01, COMP),
    ("Underfill Epoxy",              None, 8.0e7, 0.03, COMP),
    ("Die Attach Film (DAF)",        None, 4.0e7, 0.10, COMP),
    ("Conductive Silver Epoxy (die attach)", None, 4.0e7, 0.02, COMP),
    ("Glass-Filled Nylon (PA6-GF30)", 1.6e8, 1.8e8, 0.03, COMP),
    ("E-Glass Cloth (reinforcement)", None, None, 0.048, ASM_C),
    ("Graphite PGS (Pyrolytic Sheet)", None, 2.0e7, 0.01, COMP),
    ("Graphene Film (thermal)",      None, 3.0e7, 0.01, COMP),
    ("Al Laminate Pouch",            8.0e7, 1.2e8, 0.05, COMP),
    ("Silver Nanowire (AgNW)",       None, 5.0e7, 0.02, COMP),
    ("EMI Shield (conductive)",      None, 1.0e8, 0.05, COMP),
    ("EMI Shielding Film (FPCB)",    None, 5.0e7, 0.10, COMP),
    ("Conductive Fabric Gasket (EMI)", None, 5.0e6, 0.30, COMP),
    ("ACF (Anisotropic Conductive Film)", None, 3.0e7, 0.10, COMP),
    ("Magnetic Sensor (TMR)",        None, 5.0e8, 0.01, COMP),
    ("AR/IR Coating (multilayer)",   None, 2.0e8, 0.002, ASM_C),
    ("Chip Resistor Film (RuO2)",    None, 1.0e8, 0.001, ASM_C),
    ("Graphite Anode",               None, 3.0e7, 0.01, COMP),
    ("Silicon Anode",                None, 1.0e8, 0.005, COMP),
    ("NCM811 Cathode",               None, 1.0e8, 0.005, ASM_C),
    ("NCA Cathode (LiNiCoAlO2)",     None, 1.0e8, 0.005, ASM_C),
    ("LFP Cathode (LiFePO4)",        None, 1.0e8, 0.005, ASM_C),
    ("Carbon Black (conductive additive)", None, 1.0e7, 0.005, COMP),
    ("Quantum Dot Film (QDEF)",      None, 5.0e7, 0.05, COMP),
]

KEYS = [("mechanical.yield_strength", "Pa"), ("mechanical.tensile_strength", "Pa"),
        ("mechanical.elongation_at_break", "1")]


def run():
    with SessionLocal() as s:
        name_to_id = {m.name: m.id for m in s.query(Material).all()}
        existing = {(mid, k) for mid, k in s.query(
            PropertyValue.material_id, PropertyValue.property_key).filter(
            PropertyValue.value_num.isnot(None))}
    added = errors = 0
    brittle = 0
    for name, sy, uts, el, src in T:
        mid = name_to_id.get(name)
        if mid is None:
            print(f"  !! 재료 없음: {name}"); errors += 1; continue
        n = 0
        for (key, unit), v in zip(KEYS, (sy, uts, el)):
            if v is None or (mid, key) in existing:
                continue
            note = NOTE
            r = M.register_property(mid, key, value=v, unit=unit, method="estimated",
                                    quality_tier=4, notes=note, **src)
            if "error" in r:
                print(f"  !! {name} {key}: {r['error']}"); errors += 1
            else:
                n += 1; added += 1
        # 취성재(항복 None)는 사유를 남긴다 — 나중에 "왜 항복이 없나" 오해 방지.
        if sy is None and (mid, "mechanical.yield_strength") not in existing:
            r = M.register_property(mid, "mechanical.chemical_resistance" if False else
                                    "structure.crystal_structure", value_text=None) if False else {"skip": 1}
            brittle += 1
        if n:
            print(f"  [{mid:3d}] {name[:42]:42s} +{n}")
    print(f"\nDONE — 추가 {added} / 취성재(항복 미등록) {brittle} / 오류 {errors}")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
