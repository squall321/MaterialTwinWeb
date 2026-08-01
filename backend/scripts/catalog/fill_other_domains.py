# DYNA 외 물성 보강 — 흡습률·방사율·아웃가싱·융해잠열·피로한도·성형수축 등. 계열 규칙 기반.
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
IR = dict(source_title="Handbook of Infrared Radiation — emissivity tables (Touloukian TPRC Data Series)", source_kind="book")
ASTM_E595 = dict(source_title="ASTM E595 — Total Mass Loss and Collected Volatile Condensable Materials from Outgassing in a Vacuum Environment", source_kind="standard")

NOTE_CLASS = ("계열 대표값 — 실제 제품은 그레이드·배합에 따라 다르므로 정밀 설계 시 "
              "업체 데이터시트로 대체 권장")

# ── 계열별 규칙: category(또는 이름 키워드) → {물성키: (값, 단위, tier, 출처)} ──
# 흡습률(24h, 무차원 비율)·전방사율·아웃가싱은 계열 특성이 뚜렷해 대표값 부여가 타당.
POLYMER_MOIST = {          # 흡습률 계열 기본값(폴리머 세부는 아래 BY_NAME이 우선)
    "acrylic": 0.004, "epoxy": 0.002, "silicone": 0.001, "pi": 0.018,
    "pet": 0.0005, "ptfe": 0.0001, "pe": 0.0001, "pc": 0.0015, "default": 0.003,
}

# 이름 키워드 → 흡습률(24h) 개별값.
MOIST_BY_KEYWORD = [
    ("PTFE", 0.0001), ("ePTFE", 0.0002), ("PE/PP", 0.0001), ("Polyethylene", 0.0001),
    ("PEN", 0.0004), ("PET", 0.0005), ("Prism Sheet", 0.0005),
    ("Silicone", 0.001), ("Thermal Pad", 0.001), ("PSA Silicone", 0.001),
    ("Epoxy", 0.002), ("EMC", 0.002), ("Underfill", 0.002), ("Solder Mask", 0.0015),
    ("Prepreg", 0.0012), ("DAF", 0.002), ("Silver Epoxy", 0.002),
    ("PI", 0.018), ("Polyimide", 0.018), ("CPI", 0.015), ("PBO", 0.010),
    ("PEI", 0.0025), ("Ultem", 0.0025), ("PC", 0.0015), ("LDS", 0.0015),
    ("Nylon", 0.017), ("PA6", 0.017), ("PVDF", 0.0004),
    ("OCA", 0.004), ("PSA", 0.004), ("LOCA", 0.004), ("Bond", 0.004), ("Tape", 0.004),
    ("NBR", 0.005), ("PORON", 0.005), ("Foam", 0.005), ("Damping", 0.004),
    ("Isodamp", 0.004), ("Gasket", 0.003), ("Fabric", 0.008),
    ("APEL", 0.0001), ("COC", 0.0001), ("Polarizer", 0.030), ("TAC", 0.030),
    ("Resin", 0.003), ("Photoresist", 0.003), ("OLED", 0.001), ("OCL", 0.003),
    ("Coating", 0.002), ("AgNW", 0.003), ("EMI", 0.003), ("ACF", 0.003),
    ("Graphene", 0.0005), ("Graphite", 0.0005), ("Carbon", 0.001), ("Anode", 0.001),
    ("QDEF", 0.003), ("Pouch", 0.002), ("OSP", 0.005), ("RuO2", 0.0005),
    ("TMR", 0.0005), ("AR/IR", 0.0005),
]

# 전방사율(0~1) — 열해석 복사 경계조건. 계열별 대표값.
EMISS = {
    "metal_polished": 0.05, "metal_oxidized": 0.30, "metal_coated": 0.85,
    "ceramic": 0.85, "polymer": 0.90, "composite": 0.88, "semiconductor": 0.65,
}
EMISS_BY_KEYWORD = [
    ("Anodized", 0.85), ("Coating", 0.85), ("Graphite", 0.95), ("Graphene", 0.95),
    ("Copper", 0.05), ("동박", 0.05), ("Silver", 0.03), ("Gold", 0.02),
    ("Aluminum", 0.09), ("Al6061", 0.09), ("Al1050", 0.09), ("Al7", 0.09),
    ("SUS", 0.28), ("Steel", 0.28), ("Nickel", 0.12), ("Ni", 0.12),
    ("Solder", 0.35), ("SAC305", 0.35), ("Tungsten", 0.05), ("Ti", 0.20),
    ("Mg_", 0.12), ("Brass", 0.06), ("Bronze", 0.08), ("Nitinol", 0.20),
]

# 아웃가싱(ASTM E595) — 폴리머·접착제 계열. TML/CVCM(무차원 비율).
OUTGAS = [
    ("Silicone", 0.005, 0.0005), ("Epoxy", 0.008, 0.0008), ("Acrylic", 0.010, 0.001),
    ("PSA", 0.010, 0.001), ("OCA", 0.010, 0.001), ("PI", 0.005, 0.0002),
    ("Polyimide", 0.005, 0.0002), ("PTFE", 0.001, 0.0001), ("Foam", 0.015, 0.0015),
]

# 융해잠열(J/kg) — 금속 상변화(솔더 리플로우 해석).
LATENT = [("SAC305", 5.5e4), ("Solder", 5.5e4), ("Copper", 2.05e5), ("동박", 2.05e5),
          ("Aluminum", 3.97e5), ("Al6061", 3.97e5), ("Silver", 1.05e5), ("Gold", 6.4e4),
          ("Nickel", 2.91e5), ("Tungsten", 1.92e5), ("Liquid Metal", 4.0e4)]

# 피로한도(Pa) — 구조 금속(진동·낙하 반복하중).
FATIGUE = [("SUS304", 2.4e8), ("SUS316", 2.4e8), ("SUS201", 2.5e8), ("SUS301", 2.6e8),
           ("SUS410", 2.8e8), ("SUS420", 3.0e8), ("SUS430", 2.6e8), ("SUS_17-4PH", 6.0e8),
           ("Al6061", 9.7e7), ("Al7", 1.6e8), ("Al1050", 3.5e7), ("Al5052", 1.2e8),
           ("Ti6Al4V", 5.1e8), ("Ti_Grade", 2.0e8), ("Mg_AZ31B", 1.0e8), ("Mg_AZ91D", 8.0e7),
           ("SPCC", 1.7e8), ("S45C", 2.8e8), ("SCM440", 4.5e8), ("Beryllium Copper", 2.6e8),
           ("Phosphor_Bronze", 2.0e8), ("Cartridge_Brass", 1.3e8), ("Inconel", 3.5e8)]

# 성형수축률(무차원) — 사출 성형 플라스틱.
SHRINK = [("PC", 0.006), ("PC/ABS", 0.006), ("LDS", 0.006), ("PBT", 0.018),
          ("Nylon", 0.012), ("PA6", 0.012), ("PEEK", 0.013), ("PEI", 0.006),
          ("Ultem", 0.006), ("APEL", 0.005), ("COC", 0.005), ("PMMA", 0.005),
          ("LCP", 0.002), ("PPS", 0.003), ("EMC", 0.002)]


def kw_match(name, table):
    """이름에 키워드가 포함되면 값 반환(긴 키워드 우선)."""
    n = name.lower()
    best = None
    for kw, *vals in sorted(table, key=lambda x: -len(x[0])):
        if kw.lower() in n:
            best = vals if len(vals) > 1 else vals[0]
            break
    return best


def run():
    with SessionLocal() as s:
        mats = [(m.id, m.name, m.category or "") for m in s.query(Material).all()]
        existing = {(mid, k) for mid, k in s.query(
            PropertyValue.material_id, PropertyValue.property_key).filter(
            PropertyValue.value_num.isnot(None))}
    added = errors = 0

    def put(mid, key, val, unit, tier, src, note=NOTE_CLASS):
        nonlocal added, errors
        if val is None or (mid, key) in existing:
            return 0
        r = M.register_property(mid, key, value=val, unit=unit,
                                method=("handbook" if tier <= 2 else "estimated"),
                                quality_tier=tier, notes=note, **src)
        if "error" in r:
            print(f"  !! {mid} {key}: {r['error']}"); errors += 1; return 0
        added += 1
        return 1

    for mid, name, cat in mats:
        n = 0
        # ① 흡습률 — 폴리머·복합재·유기물.
        if cat in ("polymer", "composite", "organic"):
            v = kw_match(name, MOIST_BY_KEYWORD) or POLYMER_MOIST["default"]
            n += put(mid, "chemical.water_absorption_24h", v, "1", 4, POLY)
            # 포화흡습률 ≈ 24h의 2~3배(계열 경험칙).
            n += put(mid, "chemical.water_absorption_saturation", round(v * 2.5, 6), "1", 4, POLY)
        # ② 전방사율 — 전 재료(열복사 경계조건).
        e = kw_match(name, EMISS_BY_KEYWORD)
        if e is None:
            e = {"metal": 0.15, "ceramic": 0.85, "polymer": 0.90, "composite": 0.88,
                 "organic": 0.90, "semiconductor": 0.65, "liquid": 0.95}.get(cat, 0.85)
        n += put(mid, "optical.emissivity_total", e, "1", 4, IR)
        # ③ 아웃가싱 — 폴리머·접착제(카메라 포깅·진공 신뢰성).
        og = kw_match(name, OUTGAS)
        if og and cat in ("polymer", "composite", "organic"):
            n += put(mid, "chemical.outgassing_tml", og[0], "1", 4, ASTM_E595)
            n += put(mid, "chemical.outgassing_cvcm", og[1], "1", 4, ASTM_E595)
        # ④ 융해잠열 — 금속.
        lat = kw_match(name, LATENT)
        if lat and cat == "metal":
            n += put(mid, "thermal.latent_heat_fusion", lat, "J/kg", 2, CRC, None)
        # ⑤ 피로한도 — 구조 금속.
        fat = kw_match(name, FATIGUE)
        if fat and cat == "metal":
            n += put(mid, "mechanical.fatigue_strength", fat, "Pa", 2,
                     ASM_S if "SUS" in name or "S45C" in name or "SCM" in name or "SPCC" in name else ASM_M,
                     "회전굽힘/축하중 10^7 사이클 기준 피로한도")
        # ⑥ 성형수축률 — 사출 플라스틱.
        shr = kw_match(name, SHRINK)
        if shr and cat in ("polymer", "composite"):
            n += put(mid, "rheological.mold_shrinkage", shr, "1", 4, POLY)
        if n:
            print(f"  [{mid:3d}] {name[:42]:42s} +{n}")
    print(f"\nDONE — 추가 {added} / 오류 {errors}")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
