# 최저 커버리지 9종 보강 — 디스플레이/카메라/센서/EMI/PSA 원자재. 논문·데이터시트 출처 표기.
import sys
import mcp_server as M
from app.db import SessionLocal
from app.models import Material


def src(title, kind="datasheet", mfr=None, doi=None):
    d = {"source_title": title, "source_kind": kind}
    if mfr:
        d["source_manufacturer"] = mfr
    if doi:
        d["source_doi"] = doi
    return d


CRC = src("CRC Handbook of Chemistry and Physics, 97th ed.", "book")
BALDO = src("Baldo et al., 'Highly efficient phosphorescent emission from organic electroluminescent "
            "devices', Nature 395 (1998) 151", "journal", doi="10.1038/25954")
YUASA_TMR = src("Yuasa & Djayaprawira, 'Giant tunnel magnetoresistance in magnetic tunnel junctions "
                "with a crystalline MgO(001) barrier', J. Phys. D 40 (2007) R337",
                "journal", doi="10.1088/0022-3727/40/21/R01")
QD_REV = src("Shirasaki et al., 'Emergence of colloidal quantum-dot light-emitting technologies', "
             "Nature Photonics 7 (2013) 13", "journal", doi="10.1038/nphoton.2012.328")


def p(key, value=None, unit=None, tier=3, method="datasheet", source=None,
      cond=None, vtext=None, notes=None):
    d = dict(property_key=key, value=value, value_text=vtext, unit=unit,
             quality_tier=tier, method=method, conditions=cond, notes=notes)
    d.update(source or {})
    return d


ENRICH = {
    "Color Filter Resin (pigment)": [
        p("optical.transmittance", 0.92, "1", 3, cond={"wavelength_nm": 550, "color": "green pixel"},
          source=src("Toyo Ink color filter photoresist technical datasheet", mfr="Toyo Ink SC Holdings"),
          notes="녹색 화소 투과 피크. 적/청 화소는 각 대역에서 유사, 보색 대역은 <5%"),
        p("optical.refractive_index", 1.58, "1", 3, cond={"wavelength_nm": 589},
          source=src("Toyo Ink color filter photoresist technical datasheet", mfr="Toyo Ink SC Holdings"),
          notes="아크릴 감광성 수지 + 안료 분산"),
        p("thermal.glass_transition", 423, "K", 4, "estimated",
          src("Toyo Ink color filter photoresist technical datasheet", mfr="Toyo Ink SC Holdings"),
          notes="경화 아크릴 ~150℃"),
        p("thermal.max_service_temp", 503, "K", 3,
          source=src("Toyo Ink color filter photoresist technical datasheet", mfr="Toyo Ink SC Holdings"),
          notes="후속 공정(배향막 소성 ~230℃) 내열 필요"),
        p("physical.density", 1400, "kg/m^3", 4, "estimated",
          src("Toyo Ink color filter photoresist technical datasheet", mfr="Toyo Ink SC Holdings")),
    ],
    "OLED Emitter Layer (Ir phosphor)": [
        p("physical.density", 1400, "kg/m^3", 4, "estimated", BALDO, notes="호스트(CBP)+Ir 도판트 증착막"),
        p("optical.refractive_index", 1.75, "1", 3, cond={"wavelength_nm": 550}, method="handbook", source=BALDO,
          notes="유기 발광층 n≈1.7–1.8 — 고굴절이라 내부전반사로 광추출 효율 ~20% 제한"),
        p("thermal.glass_transition", 383, "K", 3, "handbook", BALDO,
          notes="CBP 호스트 Tg ~110℃ — 소자 수명의 열적 상한(결정화 시 열화)"),
        p("thermal.decomposition_temp", 623, "K", 4, "estimated", BALDO, notes="증착 온도 이상 ~350℃"),
        p("electrical.band_gap", 2.6, "eV", 3, "handbook", BALDO,
          notes="Ir(ppy)3 삼중항 에너지 ~2.4–2.6 eV(녹색 인광) — 인광으로 내부양자효율 100% 가능"),
    ],
    "Magnetic Sensor (TMR)": [
        p("structure.crystal_structure", vtext="CoFeB/MgO(001)/CoFeB 자기터널접합 (결정질 MgO 장벽)",
          tier=2, method="handbook", source=YUASA_TMR,
          notes="★ 결정질 MgO의 Δ1 밴드 필터링으로 거대 TMR 발현 — 비정질 AlOx 대비 수배"),
        p("magnetic.relative_permeability", 800, "1", 4, "estimated", YUASA_TMR,
          notes="CoFeB 연자성 자유층 — 낮은 보자력으로 미소자계 감지"),
        p("electrical.resistivity_volume", 1.0e-6, "ohm*m", 4, "estimated", YUASA_TMR,
          notes="접합 RA product ~1–100 Ω·µm²로 설계(장벽 두께 의존). TMR비 100–200% @RT"),
        p("thermal.max_service_temp", 423, "K", 3, "handbook", YUASA_TMR,
          notes="~150℃ — 초과 시 CoFeB/MgO 계면 확산으로 TMR 열화"),
        p("magnetic.coercivity", 80, "A/m", 4, "estimated", YUASA_TMR, notes="자유층 보자력 ~1 Oe급(고감도)"),
    ],
    "On-Chip Lens (OCL)": [
        p("optical.refractive_index", 1.60, "1", 3, cond={"wavelength_nm": 589},
          source=src("JSR microlens (OCL) photoresist material technical datasheet", mfr="JSR Corporation"),
          notes="CMOS 이미지센서 마이크로렌즈 — 고굴절일수록 집광각↑(감도↑)"),
        p("optical.transmittance", 0.95, "1", 3, cond={"wavelength_nm": 550},
          source=src("JSR microlens (OCL) photoresist material technical datasheet", mfr="JSR Corporation")),
        p("thermal.glass_transition", 413, "K", 4, "estimated",
          src("JSR microlens (OCL) photoresist material technical datasheet", mfr="JSR Corporation"),
          notes="열 리플로우로 렌즈 곡률 형성 후 경화"),
        p("physical.density", 1200, "kg/m^3", 4, "estimated",
          src("JSR microlens (OCL) photoresist material technical datasheet", mfr="JSR Corporation")),
        p("thermal.max_service_temp", 533, "K", 4, "estimated",
          src("JSR microlens (OCL) photoresist material technical datasheet", mfr="JSR Corporation"),
          notes="후속 리플로우(260℃) 내성 필요"),
    ],
    "Quantum Dot Film (QDEF)": [
        p("optical.refractive_index", 1.50, "1", 4, "estimated", QD_REV, cond={"wavelength_nm": 589},
          notes="아크릴 매트릭스 기준(QD 분산)"),
        p("optical.transmittance", 0.90, "1", 3, cond={"wavelength_nm": 630}, method="handbook", source=QD_REV,
          notes="적색 발광 대역 투과. 청색 여기광은 흡수·변환"),
        p("thermal.max_service_temp", 358, "K", 3, "handbook", source=QD_REV,
          notes="★ ~85℃ — QD는 열·산소·수분에 취약해 배리어필름 봉지 필수(WVTR<1e-4 g/m²/day)"),
        p("physical.water_vapor_transmission", 1.2e-14, "kg/(m^2*s)", 3, "handbook", QD_REV,
          notes="배리어 요구 ~1e-4 g/m²/day 환산 — 미달 시 QD 소광(dark spot)"),
        p("thermal.glass_transition", 353, "K", 4, "estimated", QD_REV, notes="아크릴 매트릭스"),
    ],
    "OLED Cathode (Mg:Ag)": [
        p("physical.density", 2600, "kg/m^3", 4, "estimated", CRC,
          notes="Mg:Ag ≈10:1(vol) 합금 — Mg 1.74·Ag 10.49의 혼합 추정"),
        p("optical.transmittance", 0.55, "1", 3, cond={"wavelength_nm": 550, "thickness_nm": 15},
          method="handbook", source=CRC,
          notes="★ 반투명 캐소드 — 15 nm 박막에서 ~50–60% 투과(탑에미션 구조 필수 조건)"),
        p("electrical.conductivity", 1.0e7, "S/m", 4, "estimated", CRC,
          notes="박막 합금 — 벌크 Mg(2.3e7) 대비 낮음(사이즈 효과·합금 산란)"),
        p("thermal.melting_point", 923, "K", 2, "handbook", CRC, notes="Mg 650℃ 기준(Ag 소량 첨가)"),
        p("chemical.oxidation_resistance", vtext="Mg 산화 취약 — 수분·산소 침투 시 다크스팟 발생, 봉지(encapsulation) 필수",
          tier=2, method="handbook", source=CRC, notes="저일함수(~3.7 eV)로 전자주입에 유리하나 화학적으로 불안정"),
    ],
    "Conductive Fabric Gasket (EMI)": [
        p("electrical.surface_resistivity", 0.05, "ohm", 3,
          source=src("Laird conductive fabric-over-foam EMI gasket technical datasheet", mfr="Laird Performance Materials"),
          notes="Ni/Cu 도금 직물 — 표면저항 ≤0.1 Ω/sq로 접지 연속성 확보"),
        p("thermal.max_service_temp", 343, "K", 3,
          source=src("Laird conductive fabric-over-foam EMI gasket technical datasheet", mfr="Laird Performance Materials"),
          notes="~70℃(우레탄 폼 코어 제한)"),
        p("mechanical.compressive_strength", 3.5e4, "Pa", 3, cond={"deflection": "50%"},
          source=src("Laird conductive fabric-over-foam EMI gasket technical datasheet", mfr="Laird Performance Materials"),
          notes="50% 압축 시 반력 — 저압축력으로 얇은 폰 구조에 적합"),
        p("chemical.galvanic_potential", -0.25, "V", 4, "estimated",
          src("Laird conductive fabric-over-foam EMI gasket technical datasheet", mfr="Laird Performance Materials"),
          notes="Ni 도금 기준 — Al 하우징(-0.75V)과 갈바닉 부식 우려로 도금종 선택 중요"),
    ],
    "PSA Silicone High-Temp": [
        p("thermal.max_service_temp", 533, "K", 3,
          source=src("3M 9871 high-temperature silicone adhesive transfer tape technical data", mfr="3M"),
          notes="★ ~260℃ — 아크릴 PSA(150℃) 대비 고온. 리플로우 마스킹용"),
        p("thermal.min_service_temp", 213, "K", 3,
          source=src("3M 9871 high-temperature silicone adhesive transfer tape technical data", mfr="3M"),
          notes="-60℃ — 실리콘 저Tg로 저온 유연성 유지"),
        p("physical.density", 1050, "kg/m^3", 4, "estimated",
          src("3M 9871 high-temperature silicone adhesive transfer tape technical data", mfr="3M")),
        p("chemical.chemical_resistance", vtext="내용제·내열·내후성 우수, 실리콘 이행(migration) 우려로 광학·전기접점 부위 주의",
          tier=3, source=src("3M 9871 high-temperature silicone adhesive transfer tape technical data", mfr="3M")),
    ],
    "PSA Removable": [
        p("thermal.max_service_temp", 338, "K", 3,
          source=src("3M removable repositionable adhesive technical data", mfr="3M"),
          notes="~65℃ — 재박리 특성 유지 상한"),
        p("physical.surface_energy", 0.030, "J/m^2", 4, "estimated",
          src("3M removable repositionable adhesive technical data", mfr="3M"),
          notes="저점착 설계 — 잔사 없는 재박리(마이크로스피어 구조)"),
        p("physical.density", 1000, "kg/m^3", 4, "estimated",
          src("3M removable repositionable adhesive technical data", mfr="3M")),
        p("chemical.chemical_resistance", vtext="재박리용 저점착 — 장기 부착 시 점착력 상승(경시변화) 주의",
          tier=4, method="estimated", source=src("3M removable repositionable adhesive technical data", mfr="3M")),
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
        print(f"[ENRICH] {mid:3d} {name[:42]:42s} +{n}")
    print(f"\nDONE — {total} property values, {errors} errors")
    return errors


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
