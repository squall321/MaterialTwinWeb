# 해석 종류별 재료 준비도 점검 — 어떤 해석이 되고 무엇이 막는지 재료 단위로 센다.
# 사용: .venv/bin/python scripts/catalog/analysis_readiness.py [해석이름]
import sqlite3
import sys
from collections import defaultdict, Counter

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'

E, NU, G, K = ('mechanical.youngs_modulus', 'mechanical.poisson_ratio',
               'mechanical.shear_modulus', 'mechanical.bulk_modulus')
RHO = 'physical.density'
PLAS = ('mechanical.yield_strength', 'mechanical.tensile_strength', 'mechanical.elongation_at_break')
RATE = ('mechanical.cowper_symonds_c', 'mechanical.cowper_symonds_p',
        'mechanical.dynamic_increase_factor')
PRONY = ('mechanical.prony_relaxation_time', 'mechanical.prony_tensile_modulus',
         'mechanical.prony_shear_modulus', 'mechanical.prony_relative_modulus')
MOIST = ('physical.water_vapor_transmission', 'physical.gas_permeability_h2o',
         'physical.diffusion_coefficient', 'chemical.water_absorption_24h')
WET = ('physical.contact_angle_water', 'physical.surface_energy')

# 벤딩·결로는 전 재료가 대상이 아니다. 벌크 금속에 층두께를 요구하면 척도가 왜곡된다.
FILMISH = ('film', 'tape', 'oca', 'ocr', 'psa', 'adhesive', 'coating',
           'laminate', 'foil', 'sheet', 'pi base', 'foam', '폼')

# (이름, 전체필수, [택일군], 대상필터)
# 결로의 습기 물성은 흡습·투습하는 재료에만 요구한다. 금속·세라믹은 표면 결로만 보면 되므로
# 여기에 투습도를 요구하면 없는 결함을 만들어낸다.
ANALYSES = {
    "구조":   ([E, NU, RHO], [PLAS], None),
    "벤딩":   ([E, NU, RHO], [PRONY + (G,)], "film"),
    "낙하":   ([E, NU, RHO] + list(PLAS), [RATE], None),
    "열전달": (['thermal.conductivity', 'thermal.specific_heat', RHO], [], None),
    "열응력": (['thermal.expansion_linear', E, NU, RHO], [], None),
    "결로(표면)":  (['thermal.conductivity', 'thermal.specific_heat', RHO], [WET], None),
    "결로(투습)":  (['thermal.conductivity', 'thermal.specific_heat', RHO], [MOIST], "absorbent"),
}


def load():
    c = sqlite3.connect(DB)
    mat = {i: (n, cat) for i, n, cat in c.execute("select id, name, category from material")}
    own = defaultdict(set)
    for mid, k in c.execute("select material_id, property_key from property_value"):
        own[mid].add(k)
    return mat, own


def scope(mat, filt):
    if filt == "film":
        return [m for m in mat if any(w in mat[m][0].lower() for w in FILMISH)]
    if filt == "absorbent":     # 흡습·투습하는 재료만 — 금속·세라믹 제외
        return [m for m in mat if mat[m][1] in ('polymer', 'composite', 'rubber', 'foam')]
    return list(mat)


def main():
    mat, own = load()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for name, (must, anyof, filt) in ANALYSES.items():
        if only and only != name:
            continue
        tgt = scope(mat, filt)
        full = [m for m in tgt if all(k in own[m] for k in must)]
        ready = [m for m in full if all(any(k in own[m] for k in grp) for grp in anyof)]
        n = len(tgt)
        print(f"\n══ {name}  대상 {n}종")
        print(f"   필수 완비 {len(full):3d} ({len(full)*100//n:2d}%)"
              + (f"   → 선택군까지 {len(ready):3d} ({len(ready)*100//n:2d}%)" if anyof else ""))
        for k in must:
            miss = sum(1 for m in tgt if k not in own[m])
            if miss:
                print(f"     없음 {miss:3d}종  {k}")
        for grp in anyof:
            miss = [m for m in full if not any(k in own[m] for k in grp)]
            if miss:
                print(f"     택일군 전무 {len(miss):3d}종  ({' | '.join(g.split('.', 1)[1] for g in grp)})")
                print(f"        카테고리 {dict(Counter(mat[m][1] for m in miss))}")

    # 포아송비는 4개 해석을 동시에 막는다 — 계산으로 회수되는 양을 따로 본다.
    no_nu = [m for m in mat if NU not in own[m]]
    calc = [m for m in no_nu if (E in own[m] and G in own[m]) or (E in own[m] and K in own[m])]
    print(f"\n══ 교차 병목")
    print(f"   포아송비 없음 {len(no_nu)}종 (구조·벤딩·낙하·열응력 동시 차단)")
    print(f"     등방관계로 계산 가능 {len(calc)}종 / 신규 수집 필요 {len(no_nu)-len(calc)}종")
    print(f"     수집 필요분 {dict(Counter(mat[m][1] for m in no_nu if m not in calc))}")
    no_rho = [m for m in mat if RHO not in own[m]]
    print(f"   밀도 없음 {len(no_rho)}종 (동해석 전부 차단) {dict(Counter(mat[m][1] for m in no_rho))}")


if __name__ == "__main__":
    main()
