# 포아송비 결측을 '가정값'으로 채운다 — 측정값인 척하지 않고 가정임을 데이터에 새긴다.
#
# 사용: fill_assumed_poisson.py [--apply]
#
# 배경: 포아송비 166종 누락이 구조·벤딩·낙하·열응력을 동시에 막는다. 그런데 이건 수집으로
# 풀리지 않는다 — ISO 10350-1 / CAMPUS 항목 체계에 포아송비가 없어서 엔지니어링 열가소성
# 수지 TDS가 통째로 막힌다(BLOCKED_SOURCES I장). 그래서 가정값을 넣되 조건을 지킨다.
#
# 원칙:
#   1. 가정의 근거는 **카탈로그 안의 실측값**이거나 **DB에 이미 인용된 문헌**이어야 한다.
#      외부에서 기억으로 가져오지 않는다.
#   2. tier4 · method='estimated' · conditions.assumption=true 로 새긴다. 대표값 선택에서
#      실측값에 항상 밀리고, 나중에 실측이 들어오면 자동으로 대체된다.
#   3. 클래스가 균질할 때만 건다. 실측 4건 미만이거나 IQR이 넓으면 비워 둔다.
#   4. 고무·점착층에 ν=0.5를 쓰지 않는다 — 체적잠김으로 해석이 터진다.
import argparse
import json
import sqlite3
import statistics as st
from collections import defaultdict

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
NU = 'mechanical.poisson_ratio'
MIN_N = 4          # 클래스 실측 최소 건수
MAX_IQR = 0.07     # 클래스 산포 상한
# 산포가 극히 좁으면 표본이 적어도 클래스 균질성이 증명된다.
# (PI 필름은 실측 3건이 전부 0.340으로 일치한다 — 등급이 달라도 값이 같다는 뜻이다)
TIGHT_N, TIGHT_IQR = 3, 0.02


def subclass(nm: str, cat: str) -> str:
    n = nm.lower()
    if any(w in n for w in ('laminate', 'fr-4', 'fr4', 'ccl', 'bt resin', 'prepreg', 'rf-',
                            'duroid', 'megtron', 'ultralam', 'i-tera', 'astra', 'iteq',
                            'taconic', 'tu-', 's1000', 'np-155')):
        return "직물유리 적층판"
    if any(w in n for w in ('foam', 'poron', 'sponge', 'microcellular', 'epe ')) or cat == 'foam':
        return "폼"
    if cat == 'rubber' or any(w in n for w in ('silicone', 'ecoflex', 'dragon skin', 'rubber',
                                               'pdms', 'sylgard', 'rtv', 'platsil', 'body double',
                                               'sorta', 'rebound')):
        return "고무·엘라스토머"
    if any(w in n for w in ('oca', 'ocr', 'psa', 'adhesive', 'tape', 'vhb', 'tesa',
                            'arclear', 'duplocoll', 'avery')):
        return "점착·접착층"
    if any(w in n for w in ('pi base', 'kapton', 'upilex', 'apical', 'taimide', 'polyimide', 'cpi')):
        return "PI 필름"
    if cat == 'polymer' and any(w in n for w in ('gf', 'glass', 'filled', 'amodel', 'grivory',
                                                 'stanyl', 'ultramid', 'valox', 'ryton')):
        return "유리충전 수지"
    if cat == 'polymer':
        return "무충전 수지"
    if cat == 'ceramic':
        return "세라믹·유리"
    if cat == 'metal':
        return "금속"
    return f"기타({cat})"


# 카탈로그 실측이 부족하지만 **DB에 이미 인용된 문헌**으로 근거가 있는 클래스.
# (source_title, 값) — 그 문헌을 쓰는 기존 행이 실제로 있는지 실행 시 확인한다.
LITERATURE = {
    "고무·엘라스토머": (0.49, "Rubber Technology Handbook (Hofmann)",
                  "비압축성 근접. 0.5는 체적잠김을 일으키므로 0.49를 쓴다"),
    "점착·접착층":    (0.49, "Towards the optimal design of optically clear adhesives",
                  "아크릴·실리콘 점착층은 비압축성 근접. 3M VHB 4910 TDS 실측 0.49와도 일치"),
    "폼":          (0.30, "Rubber Technology Handbook (Hofmann)",
                  "셀 구조에 따라 실제로는 0~0.4로 넓다 — 정밀 해석에는 부적합한 등방 근사"),
}
# 방향이 의미 있는 클래스는 조건에 명시한다.
DIRECTION = {"직물유리 적층판": "in-plane (nu12) — 두께방향 nu13은 값이 다르다"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    c = sqlite3.connect(DB)

    mats = {i: (n, cat) for i, n, cat in c.execute("select id,name,category from material")}
    measured, lack = defaultdict(list), defaultdict(list)
    for mid, (nm, cat) in mats.items():
        sc = subclass(nm, cat)
        rows = c.execute(f"""select value_num, quality_tier from property_value
            where material_id=? and property_key='{NU}' and value_num is not null""", (mid,)).fetchall()
        if not rows:
            lack[sc].append(mid)
            continue
        measured[sc].extend(v for v, t in rows if t <= 2)     # 실측·핸드북만 근거로

    plan = {}
    for sc in sorted(set(measured) | set(lack)):
        if not lack[sc]:
            continue
        vs = sorted(measured[sc])
        if len(vs) >= TIGHT_N:
            q1, q3 = st.quantiles(vs, n=4)[0], st.quantiles(vs, n=4)[2]
            iqr = q3 - q1
            if (len(vs) >= MIN_N and iqr <= MAX_IQR) or (len(vs) >= TIGHT_N and iqr <= TIGHT_IQR):
                plan[sc] = (round(st.median(vs), 3), "catalog", len(vs), iqr, vs[0], vs[-1])
                continue
            # 카탈로그 실측으로는 못 세우지만 문헌 근거가 따로 있으면 그쪽으로 넘어간다.
            # (점착·접착층은 실측 3건이 0.34~0.49로 흩어져 있지만, DB에 이미 인용된
            #  OCA 최적설계 논문 근거가 22건 있고 3M VHB 실측 0.49와도 맞는다)
            print(f"  카탈로그 근거 불가 {sc}: 실측 {len(vs)}건 · IQR {iqr:.3f}"
                  f"{' → 문헌 근거로 전환' if sc in LITERATURE else ' · 문헌 근거도 없음 → 비워 둔다'}")
            if sc not in LITERATURE:
                continue
        if sc in LITERATURE:
            val, src_title, why = LITERATURE[sc]
            sid = c.execute("select id from source where title like ? limit 1",
                            (src_title[:40] + "%",)).fetchone()
            if sid:
                plan[sc] = (val, "literature", sid[0], why, None, None)
                continue
            print(f"  건너뜀 {sc}: 근거 문헌 '{src_title}'이 DB에 없다")
            continue
        print(f"  건너뜀 {sc}: 실측 {len(vs)}건(<{MIN_N}) · 인용 가능한 문헌 근거 없음 → 비워 둔다")

    # 카탈로그 유래 가정에 붙일 출처 행(계산 출처).
    cat_src = c.execute("select id from source where title=?",
                        ("MaterialTwinWeb 클래스 가정 — 카탈로그 내 동일 클래스 실측값의 중앙값",)).fetchone()
    if not cat_src and args.apply:
        c.execute("""insert into source(kind, title, publisher, url)
            values('computed','MaterialTwinWeb 클래스 가정 — 카탈로그 내 동일 클래스 실측값의 중앙값',
                   'MaterialTwinWeb','https://github.com/squall321/MaterialTwinWeb')""")
        cat_src = (c.execute("select last_insert_rowid()").fetchone()[0],)

    total = 0
    print()
    for sc, (val, kind, a, b, lo, hi) in sorted(plan.items()):
        ids = lack[sc]
        if kind == "catalog":
            note = (f"[가정] 측정값이 아니다. 카탈로그 내 '{sc}' 클래스 실측 {a}건의 중앙값 {val} "
                    f"(범위 {lo}~{hi}, IQR {b:.3f})을 해석 입력용으로 채운 것이다. "
                    f"해당 제품의 실측값이 확보되면 그 값이 대표값이 된다.")
            sid = cat_src[0] if cat_src else None
        else:
            note = (f"[가정] 측정값이 아니다. DB에 이미 인용된 문헌 근거를 같은 클래스에 확장한 값 {val}. "
                    f"{b}. 해당 제품의 실측값이 확보되면 그 값이 대표값이 된다.")
            sid = a
        cond = {"assumption": True, "class": sc, "basis": kind}
        if sc in DIRECTION:
            cond["direction"] = DIRECTION[sc]
        print(f"  {sc:16s} ν={val:<6.3f} {kind:10s} → {len(ids):3d}종")
        total += len(ids)
        if args.apply:
            for mid in ids:
                c.execute(f"""insert into property_value(material_id, property_key, value_num, unit,
                    quality_tier, method, source_id, conditions, notes)
                    values(?, '{NU}', ?, '1', 4, 'estimated', ?, ?, ?)""",
                          (mid, val, sid, json.dumps(cond, ensure_ascii=False), note))
    if args.apply:
        c.commit()
    left = c.execute(f"""select count(*) from material m where not exists(
        select 1 from property_value where material_id=m.id and property_key='{NU}')""").fetchone()[0]
    print(f"\n{'[APPLY]' if args.apply else '[DRY-RUN]'} 가정값 {total}건 / 적용 후 결측 {left}종")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
