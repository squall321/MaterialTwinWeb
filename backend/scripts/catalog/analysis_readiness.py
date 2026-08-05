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
# 율속 의존을 표현하는 경로는 넷이다 — 어느 하나만 있어도 카드가 만들어진다.
#   Cowper-Symonds 2상수 · DIF · 율속별 항복강도(LCSR 곡선 원자료) · Johnson-Cook C
RATE = ('mechanical.cowper_symonds_c', 'mechanical.cowper_symonds_p',
        'mechanical.dynamic_increase_factor', 'mechanical.yield_strength_at_rate',
        'mechanical.johnson_cook_c')
PRONY = ('mechanical.prony_relaxation_time', 'mechanical.prony_tensile_modulus',
         'mechanical.prony_shear_modulus', 'mechanical.prony_relative_modulus')
MOIST = ('physical.water_vapor_transmission', 'physical.gas_permeability_h2o',
         'physical.diffusion_coefficient', 'chemical.water_absorption_24h')
WET = ('physical.contact_angle_water', 'physical.surface_energy')

# 벤딩·결로는 전 재료가 대상이 아니다. 벌크 금속에 층두께를 요구하면 척도가 왜곡된다.
FILMISH = ('film', 'tape', 'oca', 'ocr', 'psa', 'adhesive', 'coating',
           'laminate', 'foil', 'sheet', 'pi base', 'foam', '폼')

# 소성·파괴 입력은 두 경로 중 하나면 된다.
#   (a) 항복강도 — 연성 금속·무충전 폴리머
#   (b) 인장강도 + 파단연신율 — 항복점이 없는 재료(GF 강화 등급·취성 필름·세라믹)
# **(b)를 결측으로 세면 안 된다.** 유리섬유 강화 등급은 항복을 재지 않는 것이 정상이고
# BASF 등 제조사가 ISO 527 행에 "Stress at break (v=5 mm/min)*"로 그렇게 명시한다.
# 실제로 이 구분 없이 세면 146종이 부당하게 결측으로 잡혔다.
PLAS_YIELD = ("mechanical.yield_strength",)
PLAS_BRITTLE = ("mechanical.tensile_strength", "mechanical.elongation_at_break")


def has_plasticity(ks: set) -> bool:
    """소성·파괴 카드를 만들 수 있는가 — 항복강도 또는 (인장강도+연신율)."""
    return PLAS_YIELD[0] in ks or all(k in ks for k in PLAS_BRITTLE)


# (이름, 전체필수, [택일군], 대상필터)
# 결로의 습기 물성은 흡습·투습하는 재료에만 요구한다. 금속·세라믹은 표면 결로만 보면 되므로
# 여기에 투습도를 요구하면 없는 결함을 만들어낸다.
ANALYSES = {
    "구조":   ([E, NU, RHO], [PLAS], None),
    "벤딩":   ([E, NU, RHO], [PRONY + (G,)], "film"),
    "낙하":   ([E, NU, RHO], [PLAS_YIELD + PLAS_BRITTLE, RATE], None),
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
        # 낙하의 소성군은 '항복 OR (인장 AND 연신)'이라 단순 any()로는 못 센다.
        def _grp_ok(ks, grp):
            if set(grp) == set(PLAS_YIELD + PLAS_BRITTLE):
                return has_plasticity(ks)
            return any(k in ks for k in grp)
        ready = [m for m in full if all(_grp_ok(own[m], grp) for grp in anyof)]
        n = len(tgt)
        print(f"\n══ {name}  대상 {n}종")
        print(f"   필수 완비 {len(full):3d} ({len(full)*100//n:2d}%)"
              + (f"   → 선택군까지 {len(ready):3d} ({len(ready)*100//n:2d}%)" if anyof else ""))
        for k in must:
            miss = sum(1 for m in tgt if k not in own[m])
            if miss:
                print(f"     없음 {miss:3d}종  {k}")
        for grp in anyof:
            miss = [m for m in full if not _grp_ok(own[m], grp)]
            if miss:
                print(f"     택일군 전무 {len(miss):3d}종  ({' | '.join(g.split('.', 1)[1] for g in grp)})")
                print(f"        카테고리 {dict(Counter(mat[m][1] for m in miss))}")

    # 벤딩은 물성 **보유**와 카드 **생성**이 다르다. Prony 항이 아무리 많아도 τ와 항번호가
    # 짝을 이루지 않으면 곡선이 안 되고, VHB 4910처럼 한 재료에 경쟁 모델이 7개 섞여 있기도 하다.
    # 실제 생성기를 돌려 세지 않으면 지표가 준비도를 부풀린다(낙하 지표에서 같은 일이 있었다).
    if not only or only == "벤딩":
        try:
            import os
            os.environ.setdefault("MATERIALTWIN_DATABASE_URL", f"sqlite:///{DB}")
            sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
            from app.db import SessionLocal
            from app.dyna_export import K_PR_TAU, build_cards, prony_series
            from app.models import PropertyValue
            with SessionLocal() as s:
                ids = sorted({m for (m,) in s.query(PropertyValue.material_id)
                              .filter(PropertyValue.property_key == K_PR_TAU).distinct()})
                # 세트가 일관된 것과 **카드가 실제로 나오는 것**은 다르다.
                # 076은 Prony 항 외에 밀도와 BULK도 요구하므로, 세트만 세면 준비도가 부풀려진다.
                coherent = [m for m in ids if (prony_series(s, m) or {}).get("terms")]
                res = build_cards(s, ids, card="mechanical")
                made = [x for x in res.get("materials", [])
                        if any("076" in c for c in x.get("cards", []))]
                blocked = Counter()
                for x in res.get("skipped", []):
                    blocked[(x.get("reason") or "")[:52]] += 1
            print("\n══ 벤딩 — 물성 보유 vs 카드 생성")
            print(f"   Prony 보유 {len(ids)}종 → 세트가 일관된 것 {len(coherent)}종"
                  f" → **실제 *MAT_076 덱이 나오는 것 {len(made)}종**")
            for why, n_ in blocked.most_common():
                print(f"     {n_:2d}종  {why}")
        except Exception as e:                       # 앱 임포트가 안 되는 환경에서도 나머지는 돌아야 한다
            print(f"\n══ 벤딩 카드 생성 점검 건너뜀 ({type(e).__name__})")

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
