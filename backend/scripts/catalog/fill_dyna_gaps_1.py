# DYNA 카드 누락 물성 보강 — 포아송비(PR)·비열(HC). 핸드북 근거, 추정은 tier4로 정직 표기.
import sys

import mcp_server as M
from app.db import SessionLocal
from app.models import Material

CRC = dict(source_title="CRC Handbook of Chemistry and Physics, 97th ed.", source_kind="book")
ASM_M = dict(source_title="ASM Metals Handbook — Properties and Selection: Nonferrous Alloys and Special-Purpose Materials", source_kind="book")
ASM_S = dict(source_title="ASM Metals Handbook — Properties and Selection: Irons, Steels, and High-Performance Alloys", source_kind="book")
ASM_C = dict(source_title="ASM Engineered Materials Handbook — Ceramics and Glasses", source_kind="book")
POLY = dict(source_title="Polymer Handbook (Brandrup, Immergut, Grulke), 4th ed.", source_kind="book")
COMP = dict(source_title="ASM Engineered Materials Handbook — Composites", source_kind="book")

# (재료명, 포아송비, 비열 J/(kg*K), 등급, 출처) — None은 해당 물성 생략.
# tier2=핸드북 확립값(순물질·표준합금), tier4=계열 대표값 추정(블렌드·복합재·박막).
ROWS = [
    # ── 금속(핸드북 확립값) ──
    ("Battery Cu Current Collector Foil", 0.34, 385, 2, ASM_M),
    ("HVLP Low-Profile Copper Foil (5G)", 0.34, 385, 2, ASM_M),
    ("Copper Magnet Wire (enameled)",     0.34, 385, 2, ASM_M),
    ("Copper Pillar Bump",                0.34, 385, 2, ASM_M),
    ("TSV Copper (through-silicon via)",  0.34, 385, 2, ASM_M),
    ("Copper Clad Laminate (CCL)",        0.18, None, 4, COMP),   # 유리-에폭시 면내
    ("Beryllium Copper (spring/contact)", 0.30, 420, 2, ASM_M),
    ("Gold Bonding Wire",                 0.44, 129, 2, CRC),
    ("Pd-coated Cu Bonding Wire",         0.34, 385, 2, ASM_M),
    ("Silver Bonding Wire",               0.37, 235, 2, CRC),
    ("Sintered Silver",                   0.37, 235, 4, CRC),     # 다공성 → 핸드북 은 기준 근사
    ("Nickel Tab/Interconnect",           0.31, 440, 2, ASM_M),
    ("ENIG Surface Finish (Ni/Au)",       0.31, 440, 4, ASM_M),
    ("SAC305 Solder Alloy",               0.36, 220, 2, ASM_M),
    ("Tantalum Capacitor (Ta/Ta2O5)",     0.34, 140, 2, CRC),
    ("TSV Barrier (Ta/TaN)",              0.34, 140, 4, CRC),
    ("SPCC_mild_steel Bilinear",          0.29, 486, 2, ASM_S),
    ("SUS_17-4PH_H900 Bilinear",          0.27, 460, 2, ASM_S),
    ("NdFeB Sintered Magnet (N52)",       0.24, 440, 4, ASM_M),
    ("SMA Nitinol (NiTi actuator)",       0.33, 470, 2, ASM_M),
    ("Liquid Metal (Zr-based BMG)",       0.37, 400, 4, ASM_M),
    ("M-Film",                            0.34, 520, 4, ASM_M),   # Ti 합금 필름
    # ── 세라믹·반도체(핸드북) ──
    ("Crystalline Silicon (device die)",  0.28, 700, 2, CRC),
    ("Capacitive MEMS (Si)",              0.28, 700, 2, CRC),
    ("SOI Substrate (RF-SOI)",            0.28, 700, 4, CRC),
    ("LTPS Polysilicon",                  0.28, 700, 4, CRC),
    ("Sapphire Single-Crystal (Al2O3)",   0.25, 761, 2, ASM_C),
    ("Thin-Film Encapsulation (Al2O3)",   0.24, 880, 4, ASM_C),
    ("Aluminum Nitride (AlN) BAW",        0.24, 740, 2, ASM_C),
    ("Piezo MEMS (AlN thin-film)",        0.24, 740, 4, ASM_C),
    ("Quartz Crystal (SiO2)",             0.17, 740, 2, ASM_C),
    ("Aluminosilicate Cover Glass",       0.22, 800, 2, ASM_C),
    ("Ultra-Thin Glass (UTG, foldable)",  0.22, 800, 4, ASM_C),
    ("Periscope Prism Glass (high-index)", 0.23, 700, 4, ASM_C),
    ("Zirconia (ZrO2) Ceramic Back",      0.30, 400, 2, ASM_C),
    ("PZT Piezoelectric",                 0.31, 350, 2, ASM_C),
    ("BaTiO3 MLCC Dielectric",            0.30, 434, 2, ASM_C),
    ("Lithium Tantalate (LiTaO3) SAW",    0.25, 424, 4, ASM_C),
    ("ZnO Varistor (TVS)",                0.36, 494, 4, ASM_C),
    ("TiN PVD Coating",                   0.25, 600, 4, ASM_C),
    ("DLC Coating (diamond-like carbon)", 0.22, 700, 4, ASM_C),
    ("VCSEL Epitaxy (GaAs/AlGaAs)",       0.31, 330, 2, CRC),
    ("2D Material (MoS2 monolayer)",      0.25, 373, 4, CRC),
    ("LFP Cathode (LiFePO4)",             0.28, 1000, 4, ASM_C),
    ("NCM811 Cathode",                    0.28, 800, 4, ASM_C),
    ("Solid Electrolyte (LLZO Garnet)",   0.26, 600, 4, ASM_C),
    ("Silicon Anode",                     0.28, 700, 4, CRC),
    # ── 폴리머(핸드북·계열 대표) ──
    ("Kapton PI Adhesive Tape",           0.34, 1090, 2, POLY),
    ("PI Base Film — Kapton HN (DuPont)", 0.34, 1090, 2, POLY),
    ("PI Base Film — Upilex-S (UBE)",     0.34, 1130, 4, POLY),
    ("LCP Film (mmWave antenna substrate)", 0.35, 1200, 4, POLY),
    ("PC Optical (Lens Grade)",           0.37, 1200, 2, POLY),
    ("PC/ABS Blend (housing)",            0.36, 1300, 4, POLY),
    ("LDS Plastic (PC + LDS additive)",   0.36, 1200, 4, POLY),
    ("PMMA Optical (Acrylic)",            0.35, 1470, 2, POLY),
    ("COP Zeonex (Cyclo-Olefin Polymer)", 0.35, 1400, 4, POLY),
    ("PEEK Film (Diaphragm)",             0.38, 1340, 2, POLY),
    ("PEI Ultem Film",                    0.36, 1300, 2, POLY),
    ("PEN Film (Diaphragm)",              0.38, 1200, 4, POLY),
    ("PBT (structural)",                  0.38, 1300, 2, POLY),
    ("PTFE (RF coax dielectric)",         0.46, 1000, 2, POLY),
    ("PVDF Binder",                       0.38, 1400, 2, POLY),
    ("Prism Sheet / BEF (PET)",           0.40, 1200, 2, POLY),
    ("Parylene Conformal Coating",        0.40, 1000, 4, POLY),
    ("Polarizer (TAC/PVA)",               0.37, 1400, 4, POLY),
    ("FR-4 Epoxy Resin (matrix)",         0.35, 1100, 2, POLY),
    # ── 복합재(계열 대표 — 이방성이라 등방 근사임을 노트에 명시) ──
    ("FR4 Glass-Epoxy Laminate",          0.14, 1100, 4, COMP),
    ("High-Tg FR-4 Prepreg (7628 glass)", 0.14, 1100, 4, COMP),
    ("BT Resin",                          0.20, 1100, 4, COMP),
    ("Epoxy Molding Compound (EMC)",      0.25, 900, 4, COMP),
    ("Glass-Filled Nylon (PA6-GF30)",     0.35, 1300, 4, COMP),
    ("Al Laminate Pouch",                 0.33, 900, 4, COMP),
    ("ACF (Anisotropic Conductive Film)", 0.35, 1200, 4, COMP),
]

ISO_NOTE = "복합재/적층재는 실제로 이방성 — 등방 해석용 면내 등가값(카드 PR/HC 입력 목적)"


def run():
    with SessionLocal() as s:
        name_to_id = {m.name: m.id for m in s.query(Material).all()}
    added = errors = 0
    for name, nu, hc, tier, src in ROWS:
        mid = name_to_id.get(name)
        if mid is None:
            print(f"  !! 재료 없음: {name}"); errors += 1; continue
        method = "handbook" if tier <= 2 else "estimated"
        note_iso = ISO_NOTE if src is COMP else None
        n = 0
        if nu is not None:
            r = M.register_property(mid, "mechanical.poisson_ratio", value=nu, unit="1",
                                    method=method, quality_tier=tier, notes=note_iso, **src)
            if "error" in r: print(f"  !! {name} PR: {r['error']}"); errors += 1
            else: n += 1
        if hc is not None:
            r = M.register_property(mid, "thermal.specific_heat", value=hc, unit="J/(kg*K)",
                                    method=method, quality_tier=tier, notes=note_iso, **src)
            if "error" in r: print(f"  !! {name} HC: {r['error']}"); errors += 1
            else: n += 1
        added += n
        print(f"  [{mid:3d}] {name[:42]:42s} +{n} (tier{tier})")
    print(f"\nDONE — {added} property values, {errors} errors")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
