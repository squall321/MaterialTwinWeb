# 원자재 보강 — 배터리 활물질·디스플레이 광학필름·수동소자 세라믹·코팅. 논문/핸드북/규격 출처 표기.
import sys
import mcp_server as M
from app.db import SessionLocal
from app.models import Material

RT = {"temperature_C": 23}


def src(title, kind="datasheet", mfr=None, doi=None, url=None):
    d = {"source_title": title, "source_kind": kind}
    if mfr:
        d["source_manufacturer"] = mfr
    if doi:
        d["source_doi"] = doi
    if url:
        d["source_url"] = url
    return d


# ── 실제 문헌 출처(검증 가능한 DOI 보유) ─────────────────────────────────────
NOH2013 = src("Noh et al., 'Comparison of the structural and electrochemical properties of "
              "layered Li[NixCoyMnz]O2 (x=1/3,0.5,0.6,0.7,0.8,0.85)', J. Power Sources 233 (2013) 121",
              "journal", doi="10.1016/j.jpowsour.2013.01.063")
BAK2014 = src("Bak et al., 'Structural Changes and Thermal Stability of Charged LiNixMnyCozO2 "
              "Cathode Materials', ACS Appl. Mater. Interfaces 6 (2014) 22594",
              "journal", doi="10.1021/am506712c")
CRC = src("CRC Handbook of Chemistry and Physics, 97th ed.", "book")
ASM_CER = src("ASM Engineered Materials Handbook — Ceramics and Glasses", "book")
KELLY_DLC = src("Robertson, 'Diamond-like amorphous carbon', Mater. Sci. Eng. R 37 (2002) 129",
                "journal", doi="10.1016/S0927-796X(02)00005-0")
MIL_A_8625 = src("MIL-A-8625F — Anodic Coatings for Aluminum and Aluminum Alloys", "standard")
EIA_198 = src("EIA-198 / IEC 60384-21 — Class I (C0G/NP0) Ceramic Dielectric Specification", "standard")


def p(key, value=None, unit=None, tier=3, method="datasheet", source=None,
      cond=None, vtext=None, notes=None):
    d = dict(property_key=key, value=value, value_text=vtext, unit=unit,
             quality_tier=tier, method=method, conditions=cond, notes=notes)
    d.update(source or {})
    return d


ENRICH = {
    # ── 배터리 활물질 ────────────────────────────────────────────────────────
    "NCM811 Cathode": [
        p("physical.density", 4800, "kg/m^3", 3, "handbook", NOH2013, notes="LiNi0.8Co0.1Mn0.1O2 결정밀도 ~4.8 g/cc"),
        p("structure.crystal_structure", vtext="층상 α-NaFeO2형 (R-3m, hexagonal)", tier=3, method="handbook", source=NOH2013,
          notes="Ni-rich 층상구조 — Li층/전이금속층 교대. Ni2+/Li+ 양이온 혼합(cation mixing)이 용량열화 원인"),
        p("thermal.decomposition_temp", 493, "K", 3, "measured", BAK2014,
          cond={"state": "charged (delithiated)", "SOC": "100%"},
          notes="★ 충전상태 NCM811 산소방출 개시 ~220℃ — Ni 함량↑일수록 개시온도↓(열폭주 안전성 핵심)"),
        p("electrical.conductivity", 1.0e-2, "S/m", 4, "estimated", NOH2013,
          notes="NCM811 전자전도도 ~1e-4 S/cm — 도전재(카본블랙) 필수인 이유"),
        p("thermal.conductivity", 1.0, "W/(m*K)", 4, "estimated", BAK2014, notes="양극 활물질층 유효 열전도 ~1 W/mK(저열전도 → 셀 내부 열축적)"),
        p("mechanical.youngs_modulus", 1.4e11, "Pa", 4, "estimated", NOH2013, notes="층상 산화물 나노압입 ~130–150 GPa"),
    ],
    "NCA Cathode (LiNiCoAlO2)": [
        p("physical.density", 4750, "kg/m^3", 3, "handbook", NOH2013, notes="LiNi0.8Co0.15Al0.05O2 ~4.75 g/cc"),
        p("structure.crystal_structure", vtext="층상 α-NaFeO2형 (R-3m)", tier=3, method="handbook", source=NOH2013,
          notes="Al 도핑이 층상구조 안정화 — NCM 대비 구조 안정성↑"),
        p("thermal.decomposition_temp", 483, "K", 4, "estimated", BAK2014, cond={"state": "charged (delithiated)"},
          notes="충전상태 산소방출 ~210℃(Ni-rich 계열 공통 경향)"),
        p("electrical.conductivity", 1.0e-2, "S/m", 4, "estimated", NOH2013),
    ],
    "Graphite Anode": [
        p("physical.density", 2260, "kg/m^3", 2, "handbook", CRC, notes="흑연 이론밀도 2.26 g/cc"),
        p("structure.crystal_structure", vtext="육방정 흑연 (P6_3/mmc, AB 적층)", tier=2, method="handbook", source=CRC,
          notes="층간 3.35 Å — Li+ 인터칼레이션으로 LiC6 형성(이론용량 372 mAh/g)"),
        p("electrical.conductivity", 2.0e5, "S/m", 2, "handbook", CRC, cond={"axis": "in-plane (a-b)"},
          notes="면내 전도 우수, c축은 ~1e3배 낮은 이방성"),
        p("thermal.conductivity", 150, "W/(m*K)", 2, "handbook", CRC, cond={"axis": "in-plane (a-b)"},
          notes="면내 ~150 W/mK. 전극 복합체 유효값은 ~1–2 W/mK로 급감"),
        p("thermal.expansion_linear", 2.0e-5, "1/K", 2, "handbook", CRC, cond={"axis": "c-axis"},
          notes="c축 ~20 ppm/K(면내는 ~1 ppm으로 이방성 큼)"),
        p("thermal.melting_point", 3900, "K", 2, "handbook", CRC, notes="승화(~3650℃) — 사실상 용융 없음"),
    ],
    "Carbon Black (conductive additive)": [
        p("electrical.conductivity", 1.0e3, "S/m", 3, "handbook", CRC,
          notes="도전재용 카본블랙 압축분말 전도도 — 활물질(1e-2) 대비 1e5배로 전자경로 형성"),
        p("physical.specific_surface_area", 6.2e4, "m^2/kg", 3, source=src("Imerys ENSACO 260G conductive carbon black datasheet", mfr="Imerys Graphite & Carbon"),
          notes="BET ~62 m²/g — 고비표면적이 소량으로 도전망 형성 가능케 함"),
        p("structure.crystal_structure", vtext="준결정 터보스트래틱 탄소(aggregate 구조)", tier=3, method="handbook", source=CRC),
        p("thermal.conductivity", 0.2, "W/(m*K)", 4, "estimated", CRC, cond={"form": "loose powder"}, notes="분말 벌크 기준(공극 지배)"),
    ],
    # ── 수동소자 세라믹 ──────────────────────────────────────────────────────
    "Class I MLCC Dielectric (C0G/NP0)": [
        p("electrical.dielectric_constant", 45, "1", 3, cond={"frequency_hz": 1e6}, source=EIA_198,
          notes="Class I(C0G) 유전율 ~20–90 — X7R(2000+) 대비 매우 낮지만 온도·전압 안정"),
        p("electrical.dissipation_factor", 0.0005, "1", 3, cond={"frequency_hz": 1e6}, source=EIA_198,
          notes="★ Df ≤0.001 (Q>1000) — RF·타이밍 회로용. X7R(0.025) 대비 초저손실"),
        p("thermal.expansion_linear", 1.0e-5, "1/K", 4, "estimated", ASM_CER, notes="페로브스카이트/티탄산염계 ~10 ppm/K"),
        p("physical.density", 5700, "kg/m^3", 4, "estimated", ASM_CER, notes="CaZrO3/티탄산염계 유전체"),
        p("electrical.dielectric_strength", 2.0e7, "V/m", 4, "estimated", EIA_198, notes="Class I 세라믹 절연내력 ~20 kV/mm"),
    ],
    "Chip Resistor Film (RuO2)": [
        p("electrical.resistivity_volume", 3.5e-7, "ohm*m", 3, "handbook", ASM_CER,
          notes="RuO2 벌크 비저항 ~35 µΩ·cm(금속성 산화물) — 후막 저항체는 글라스 배합으로 조정"),
        p("physical.density", 6970, "kg/m^3", 2, "handbook", CRC, notes="RuO2 6.97 g/cc"),
        p("thermal.expansion_linear", 6.5e-6, "1/K", 4, "estimated", ASM_CER, notes="알루미나 기판(7 ppm)과 정합"),
        p("thermal.max_service_temp", 428, "K", 3, source=src("IEC 60115-1 — Fixed resistors for electronic equipment", "standard"),
          notes="칩저항 정격 상한 155℃(디레이팅 개시 70℃)"),
    ],
    "NTC Thermistor (spinel oxide)": [
        p("structure.crystal_structure", vtext="스피넬 (Mn,Ni,Co)3O4 (Fd-3m)", tier=3, method="handbook", source=ASM_CER,
          notes="전이금속 스피넬 — hopping 전도로 큰 음의 온도계수 발생"),
        p("physical.density", 5000, "kg/m^3", 4, "estimated", ASM_CER),
        p("electrical.resistivity_volume", 100, "ohm*m", 3, cond={"temperature_C": 25},
          source=src("Murata NCP series NTC thermistor datasheet", mfr="Murata", ),
          notes="25℃ 기준. B상수 ~3400–4500 K로 온도에 지수적 감소(R=R25·exp(B(1/T−1/T25)))"),
        p("thermal.max_service_temp", 398, "K", 3, source=src("Murata NCP series NTC thermistor datasheet", mfr="Murata"),
          notes="동작 상한 ~125℃"),
    ],
    # ── 코팅 ────────────────────────────────────────────────────────────────
    "Anodized Aluminum Layer (Al2O3)": [
        p("physical.density", 3200, "kg/m^3", 3, "handbook", MIL_A_8625,
          notes="양극산화 비정질/수화 알루미나 — 벌크 α-Al2O3(3.97)보다 낮음(기공·수화)"),
        p("mechanical.hardness_vickers", 400, "HV", 3, source=MIL_A_8625,
          notes="Type II 황산욕 ~300–500 HV(경질양극산화 Type III는 400–600)"),
        p("electrical.dielectric_strength", 2.5e7, "V/m", 3, source=MIL_A_8625, notes="~25 kV/mm — 절연층 역할"),
        p("thermal.conductivity", 1.5, "W/(m*K)", 4, "estimated", MIL_A_8625,
          notes="다공성 양극산화층 — 벌크 알루미나(30) 대비 급감, 방열 저해 요인"),
        p("thermal.expansion_linear", 5.4e-6, "1/K", 3, "handbook", ASM_CER,
          notes="Al 모재(23 ppm)와 큰 차이 → 열충격 시 크랙 발생 원인"),
        p("chemical.corrosion_rate", 1.0e-13, "m/s", 4, "estimated", MIL_A_8625, notes="봉공처리 시 내식성 우수(염수분무 336h+)"),
    ],
    "DLC Coating (diamond-like carbon)": [
        p("mechanical.hardness_vickers", 2000, "HV", 3, "handbook", KELLY_DLC,
          notes="ta-C(수소프리) 20–80 GPa ≈ 2000–8000 HV. a-C:H는 10–20 GPa"),
        p("physical.density", 2800, "kg/m^3", 3, "handbook", KELLY_DLC, notes="sp3 분율에 따라 2.0–3.0 g/cc"),
        p("mechanical.youngs_modulus", 2.0e11, "Pa", 3, "handbook", KELLY_DLC, notes="ta-C ~200–700 GPa(sp3 의존)"),
        p("thermal.max_service_temp", 623, "K", 3, "handbook", KELLY_DLC,
          notes="~350℃ 초과 시 sp3→sp2 흑연화로 경도 급락"),
        p("optical.refractive_index", 2.4, "1", 3, "handbook", KELLY_DLC, cond={"wavelength_nm": 550},
          notes="다이아몬드(2.42)에 근접 — 적외선 창 코팅에도 사용"),
        p("thermal.conductivity", 10, "W/(m*K)", 4, "estimated", KELLY_DLC, notes="비정질이라 다이아몬드(2000)보다 훨씬 낮음"),
    ],
    # ── 디스플레이/패키지 광학·접합 ─────────────────────────────────────────
    "Prism Sheet / BEF (PET)": [
        p("physical.density", 1380, "kg/m^3", 3, source=src("Toray Lumirror PET film technical datasheet", mfr="Toray Industries"),
          notes="PET 베이스 필름"),
        p("optical.refractive_index", 1.65, "1", 3, cond={"wavelength_nm": 589}, source=src("Toray Lumirror PET film technical datasheet", mfr="Toray Industries"),
          notes="PET n≈1.65. 프리즘 수지층은 n≈1.56 — 굴절률 차로 축상휘도 상승(BEF 원리)"),
        p("mechanical.youngs_modulus", 4.0e9, "Pa", 3, source=src("Toray Lumirror PET film technical datasheet", mfr="Toray Industries")),
        p("thermal.glass_transition", 351, "K", 2, "handbook", CRC, notes="PET Tg ~78℃"),
        p("thermal.max_service_temp", 423, "K", 3, source=src("Toray Lumirror PET film technical datasheet", mfr="Toray Industries"), notes="~150℃"),
        p("optical.transmittance", 0.89, "1", 3, cond={"wavelength_nm": 550}, source=src("Toray Lumirror PET film technical datasheet", mfr="Toray Industries")),
    ],
    "ACF (Anisotropic Conductive Film)": [
        p("physical.density", 1300, "kg/m^3", 4, "estimated", src("Dexerials ACF (anisotropic conductive film) technical datasheet", mfr="Dexerials"),
          notes="에폭시 바인더 + Ni/Au 도금 수지입자"),
        p("electrical.resistivity_volume", 1.0e-3, "ohm*m", 3, cond={"axis": "z (compressed)"},
          source=src("Dexerials ACF (anisotropic conductive film) technical datasheet", mfr="Dexerials"),
          notes="★ 이방성 — 압착된 z축은 도전(접속저항 mΩ급), 면내(x-y)는 절연(>1e10 Ω·m). 미세피치 COG/FOG 접합 원리"),
        p("thermal.glass_transition", 393, "K", 4, "estimated", src("Dexerials ACF (anisotropic conductive film) technical datasheet", mfr="Dexerials"),
          notes="경화 에폭시 Tg ~120℃"),
        p("thermal.max_service_temp", 358, "K", 4, "estimated", src("Dexerials ACF (anisotropic conductive film) technical datasheet", mfr="Dexerials"),
          notes="장기 신뢰성 상한 ~85℃(85℃/85%RH 시험 기준)"),
    ],
    "Oleophobic AF Coating (fluoropolymer)": [
        p("physical.contact_angle_water", 112, "deg", 3, source=src("Daikin Optool DSX anti-fingerprint coating datasheet", mfr="Daikin Industries"),
          notes="★ 물 접촉각 ~110–115° — 발수·발유로 지문 저감(AF 코팅 핵심 지표)"),
        p("physical.surface_energy", 0.012, "J/m^2", 3, source=src("Daikin Optool DSX anti-fingerprint coating datasheet", mfr="Daikin Industries"),
          notes="~12 mN/m — 퍼플루오로폴리에테르(PFPE) 실란의 초저표면에너지"),
        p("optical.transmittance", 0.99, "1", 3, cond={"wavelength_nm": 550}, source=src("Daikin Optool DSX anti-fingerprint coating datasheet", mfr="Daikin Industries"),
          notes="나노미터 두께 단분자막 — 광학 영향 거의 없음"),
        p("thermal.max_service_temp", 473, "K", 4, "estimated", src("Daikin Optool DSX anti-fingerprint coating datasheet", mfr="Daikin Industries")),
    ],
}


def run():
    total = errors = 0
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
    print(f"\nDONE — {total} property values, {errors} errors")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
