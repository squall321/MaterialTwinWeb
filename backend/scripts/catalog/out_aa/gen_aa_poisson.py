# 65차 AA — 판정된 포아송비 빈칸에 '카탈로그 내 같은 클래스 실측 중앙값'을 t4 가정으로 세운다.
# 표적: role=product · mechanical.poisson_ratio 빈칸 · core_* 판정이 이미 있는 칸(core_not_applicable 제외).
# 근거는 하나뿐이다 — 우리 DB 안의 tier<=3 비-estimated 값. 외부 기억은 쓰지 않는다(§43 역산도 하지 않는다).
import json
import re
import sqlite3
import statistics as st
from collections import defaultdict

DB = '/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db'
NU = 'mechanical.poisson_ratio'
# 값을 세울 수 있는 판정 둘. `core_rejected_printed_value` 는 **뺐다** —
# 인쇄값을 기각해 놓은 칸에 숫자를 되돌리면 verdicts_check 가 등급을 가리지 않고
# 「선언과 데이터가 어긋난다」로 잡는다(그 검사기 주석이 그렇게 못박아 두었다).
# 특히 Sr 페라이트 25등급은 우리 클래스 근거 자체가 **기각된 바로 그 표의 그 값**이라
# 순환이다. `core_not_applicable` 은 브리프 규칙 2 로 애초에 제외다.
VERDICT_KEYS = ('core_absent_from_vendor_sheet', 'core_no_public_document')
BLOCK_KEYS = ('core_not_applicable', 'core_rejected_printed_value')


def cls(name: str, cat: str) -> str | None:
    """좁은 클래스 이름. 이름·조성을 읽는다 — category 만 보지 않는다."""
    n = name.lower()

    # ---- 이름으로 먼저 갈리는 것(카테고리가 polymer/composite 로 갈려 있어도 같은 물건이다) ----
    if not re.search(r'copper clad|copper-clad|적층판', n):
        if re.search(r'underfill|언더필|encapsulant|molding compound|봉지재|'
                     r'buildup film|build-up film|molding film', n):
            if re.search(r'unfilled|filler 0 wt|substrate laminate', n):
                return None
            return '실리카·무기 충전 에폭시 봉지재'
        if re.search(r'\babf\b', n):
            return '실리카·무기 충전 에폭시 봉지재'

    # PET 필름·시트 — 코팅 배리어 필름도 기재가 PET 이면 같은 클래스다.
    if re.search(r'\bpet\b|polyethylene terephthalate|mylar|melinex|ertalyte', n) \
            and not re.search(r'copper clad|적층판|prepreg|prism sheet', n):
        return 'PET 필름·시트'
    # 유리섬유 충전 열가소성 수지 — 충전 등급은 무충전 등급과 별개 클래스다.
    if re.search(r'-gf\d|-gf\b|gf\d{2}|glass-reinforced|glass filled|glass-filled|'
                 r'short e-glass|short-glass|pp/gf', n) \
            and not re.search(r'laminate|prepreg|적층판|lamina\b|udl|cloth|'
                              r'silicone|gap pad|gap filler', n):
        return '유리섬유 충전 열가소성 수지'

    # ---- 금속 -------------------------------------------------------------
    if cat == 'metal':
        if 'solder' in n or '솔더' in n:
            # Pb 주체·In·Ga 는 Sn 계와 탄성이 다르다. 이 클래스는 Sn 주체만이다.
            # Pb 주체(Pb 80% 이상)·In·Ga 는 Sn 계와 탄성이 다르다. 이 클래스는 Sn 주체만이다.
            if re.search(r'(?:^|\s)(?:8\d|9\d)(?:\.\d+)?pb|indium|99\.99% in', n):
                return None
            if re.search(r'sac|sn-?\d|sn\d|snag|sncu|sn63|3\.5ag|0\.7cu|60sn|62sn', n):
                return 'Sn 주체 솔더 합금'
            return None
        if 'zinc' in n or n.startswith('za-'):
            return None
        if re.search(r'\bal\s?\d{3,4}|alumini|aluminum|adc12|aa\d{4}|en aw|^\d{4}[a-z]?-t\d|'
                     r'6082|7003|2017a|7075-t651', n):
            return '알루미늄 전신·주조 합금'
        if 'intermetallic' in n:
            return None
        if re.search(r'copper|bronze|brass|glidcop|동박|c1\d{4}|c2\d{4}|c3\d{4}|c5\d{4}|cusn', n):
            return '구리·구리합금'
        if re.search(r'\bmg[ _]|magnesium|\baz\d{2}|\bam\d{2}|\bae4\d|zk60', n):
            return '마그네슘 합금'
        return None

    # ---- 세라믹·유리 -------------------------------------------------------
    if cat == 'ceramic':
        if 'ferrite magnet' in n or 'sr ferrite' in n:
            return 'Sr 페라이트 소결 자석'
        if re.search(r'sealing glass|frit|봉착', n):
            return None                       # 저온 봉착 프릿 — 중금속 붕산염이라 별개다
        if re.search(r'alkali-free|eagle xg|lotus nxt|willow glass|astra glass|'
                     r'\boa-\d|an100|an635', n):
            return '알칼리프리 디스플레이 유리 기판'
        if re.search(r'quartz|fused silica|vitreous silica|spectrosil', n):
            return None                       # 100% SiO2 — 다성분 유리와 조성이 다르다
        if re.search(r'glass-ceramic|glass ceramic|fluorrichterite|disilicate|cmas', n):
            return None
        if re.search(r'optical glass|prism|aspheric|lens|filter glass|l-lah|l-bal|p-sf|p-pk', n):
            return None
        if re.search(r'lead silicate|barium borosilicate|lanthanum|titania|fluorophosphate', n):
            return None
        if re.search(r'glass fibre|glass fiber|glass cloth|gorilla|dragontrail|xensation|'
                     r'soda-lime|sodalime|aluminosilicate|borosilicate|ultra-thin glass|utg|'
                     r'as 87|as87|e-glass|s-glass|d-glass|c-glass|a-glass|r-glass|ar-glass|'
                     r'ecrglas|ne-glass|t-glass|\bl2? glass|l-hdi', n):
            return '다성분 규산염 유리'
        return None

    # ---- 폴리머 -----------------------------------------------------------
    if cat == 'polymer':
        if re.search(r'kapton|upilex|apical|taimide|polyimide|\bpi base|\bbcb\b', n):
            return None
        if re.search(r'-gf\d|gf\d{2}|glass-reinforced|glass filled', n):
            return None                       # 충전 등급은 무충전 클래스에 못 넣는다
        if re.search(r'psa|점착|tape|adhesive|접착', n):
            return None
        if re.search(r'zeonex|zeonor|topas', n):
            return '무충전 비결정 열가소성 수지'
        if re.search(r'pmma|acrylic|lexan|makrolon|polycarbonate|ultem|okp|'
                     r'polyethersulphone|polyethersulfone|^pc \(|pc \(sabic|pc optical', n):
            return '무충전 비결정 열가소성 수지'
        return None

    # ---- 복합재 -----------------------------------------------------------
    if cat == 'composite':
        if 'dsflex' in n or 'flexible copper clad' in n:
            return '연성 동박적층판(PI 기반)'
        if re.search(r'ptfe|duroid|taconic|tlx|tly|rf-35|tsm-ds3|clte|ro3003|ro4350|chukoh', n):
            return 'PTFE·세라믹 충전 RF 적층판'
        if re.search(r'carbon-fiber|carbon fibre|cfrp|aramid|thermount', n):
            return None
        if re.search(r'copper clad|\bccl\b|laminate|prepreg|적층판|fr-?4|bt resin|megtron|iteq|'
                     r'isola|nelco|nan ya|shengyi|tu-8|tu-9|thunderclad|s1000|np-155|'
                     r'i-tera|astra mt|rapidon|getek|elite material|panasonic r-1', n):
            if re.search(r'pouch|barrier|pmma/abs|gpo-3|glass-mat', n):
                return None
            return '강성 직물유리 적층판(에폭시·BT·PPO)'
        return None
    return None


# 같은 벤더 제품 계열이 실측 형제를 둘 이상 가지면 그 계열 중앙값이 더 좁은 근거다.
FAMILY = (
    ('DSF-900',    r'doosan dsf-900'),
    ('DS-7402',    r'doosan ds-7402'),
    ('DS-7409HG',  r'doosan ds-7409hg'),
    ('DS-7409(HG 외)', r'doosan ds-7409(?!hg)'),
    ('DS-8402',    r'doosan ds-8402'),
    ('DS-8502',    r'doosan ds-8502'),
    ('PC-GF',      r'\(pc-gf'),
    ('PA-GF',      r'pa6-gf|pa66-gf|pa-6,6|pa mxd6'),
)


def family(name: str) -> str | None:
    n = name.lower()
    for key, pat in FAMILY:
        if re.search(pat, n):
            return key
    return None


def band(rows, src):
    vs = [v for _, v in rows]
    q = st.quantiles(vs, n=4) if len(vs) >= 4 else None
    ss = set()
    for mid, _ in rows:
        ss |= src.get(mid, set())
    return dict(n=len(vs), med=round(st.median(vs), 4), lo=min(vs), hi=max(vs),
                iqr=round(q[2] - q[0], 4) if q else None, nsrc=len(ss),
                mats=[m for m, _ in rows])


def load():
    c = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    mats = {}
    for i, nm, cat, attrs in c.execute("select id,name,category,attributes from material"):
        try:
            a = json.loads(attrs or '{}') or {}
        except Exception:
            a = {}
        mats[i] = (nm, cat or '', a)
    own = defaultdict(set)
    for mid, k in c.execute("select material_id, property_key from property_value"):
        own[mid].add(k)
    per_mat, src = defaultdict(list), defaultdict(set)
    for mid, v, sid in c.execute(
            "select material_id, value_num, source_id from property_value "
            "where property_key=? and quality_tier<=3 and method<>'estimated' "
            "and value_num is not null", (NU,)):
        per_mat[mid].append(v)
        src[mid].add(sid)
    return mats, own, {m: round(st.median(v), 4) for m, v in per_mat.items()}, src


def plan():
    mats, own, med, src = load()
    ev, evf = defaultdict(list), defaultdict(list)
    for mid, v in med.items():
        nm, cat, _ = mats[mid]
        k = cls(nm, cat)
        if not k:
            continue
        ev[k].append((mid, v))
        f = family(nm)
        if f:
            evf[f].append((mid, v))

    tgt, unassigned = defaultdict(list), []
    for mid, (nm, cat, a) in mats.items():
        if a.get('role') != 'product' or NU in own[mid]:
            continue
        if any(NU in (a.get(bk) or []) for bk in BLOCK_KEYS):
            continue
        if not any(NU in (a.get(vk) or []) for vk in VERDICT_KEYS):
            continue
        k = cls(nm, cat)
        if not k:
            unassigned.append((mid, cat, nm))
            continue
        f = family(nm)
        # 계열은 **상위 클래스보다 좁을 때만** 쓴다 — 형제 둘이라도 흩어져 있으면 근거가 아니다.
        ok = False
        if f and len(evf[f]) >= 2:
            fv = [v for _, v in evf[f]]
            ok = (max(fv) - min(fv)) <= 0.05
        tgt[((f if ok else k), k)].append(mid)

    stats = {k: band(rows, src) for k, rows in ev.items()}
    stats.update({k: band(rows, src) for k, rows in evf.items() if len(rows) >= 2})
    return mats, own, ev, evf, tgt, stats, unassigned


if __name__ == '__main__':
    mats, own, ev, evf, tgt, stats, unassigned = plan()
    print(f"{'근거 클래스':26s} {'N':>3s} {'출처':>3s} {'중앙값':>7s} {'min~max':>13s} {'IQR':>7s} {'표적':>4s}  상위클래스")
    tot = 0
    for (basis, k), ids in sorted(tgt.items()):
        s = stats.get(basis)
        tot += len(ids)
        print(f"{basis:26s} {s['n']:3d} {s['nsrc']:3d} {s['med']:7.4f} {s['lo']:6.3f}~{s['hi']:<6.3f} "
              f"{str(s['iqr']):>7s} {len(ids):4d}  {k}")
    print(f"\n배정 {tot}칸 · 미배정 {len(unassigned)}칸")


# ---------------------------------------------------------------------------
# 적재 JSON 생성
# ---------------------------------------------------------------------------
from decimal import Decimal, ROUND_HALF_UP   # noqa: E402

SOURCE = {"kind": "computed",
          "title": "MaterialTwinWeb 클래스 가정 — 카탈로그 내 동일 클래스 실측값의 중앙값",
          "publisher": "MaterialTwinWeb",
          "url": "https://github.com/squall321/MaterialTwinWeb"}

LAMINATE = ('강성 직물유리 적층판(에폭시·BT·PPO)', '연성 동박적층판(PI 기반)',
            'PTFE·세라믹 충전 RF 적층판')

CLASS_NOTE = {
    'Sr 페라이트 소결 자석':
        "근거 3종은 서로 다른 세 측정이 아니라 **같은 문서**(Eclipse Magnetics `Ferrite Magnets/"
        "Ceramic Magnets Datasheet`, 출처 2371)의 `Physical Characteristics (Typical)` 표가 준 "
        "소결 하드페라이트 **공통값** 0.28 을 이미 t3 으로 든 형제 등급 셋이다. 58차 TA 가 "
        "그 표를 등급에 귀속시키지 않기로 판정했고 그 판정은 그대로 참이다 — 그래서 이 행은 "
        "등급 고유값이 아니라 클래스값임을 t4·assumption 으로 표시해 세운다(58차 TA 가 "
        "「계보를 따를지는 다음 파동의 판단」이라 적어 둔 자리다).",
    'Sn 주체 솔더 합금':
        "참고대역(금속 0.27~0.35)을 조금 넘는데 Sn·Pb 자체가 ν 가 높은 금속이라 그렇다 — "
        "카탈로그의 솔더 실측 세 건이 0.35~0.37 로 모여 있다. Pb 주체 솔더(92.5Pb·97.5Pb·90Pb)와 "
        "인듐 솔더는 이 클래스에 넣지 않았다.",
    '다성분 규산염 유리':
        "유리섬유는 조성에 따라 ν 가 갈린다 — 카탈로그 안에서도 붕규산 0.195 부터 S 유리 0.23 까지 "
        "퍼져 있어 이 가정은 그 폭을 안고 있다. 100% SiO2 인 석영섬유(0.16)는 조성이 달라 "
        "클래스에서 뺐다.",
    '유리섬유 충전 열가소성 수지':
        "참고대역(유리충전 수지 0.30~0.38)의 위쪽을 넘는데, 카탈로그의 유리충전 등급값이 "
        "벤더 시트(CAMPUS 계열)에서 온 것이고 0.38~0.44 에 모여 있어서다.",
    '실리카·무기 충전 에폭시 봉지재':
        "충전율이 폭을 만든다 — 고충전 드라이필름 0.25 부터 89 wt% 실리카 EMC 0.371 까지다.",
    'PC-GF':
        "근거 3종이 모두 SABIC LEXAN 한 시트에서 왔다(출처 1건) — 표본 수보다 출처 수가 근거의 "
        "세기다(§678).",
    '연성 동박적층판(PI 기반)':
        "근거 14종이 모두 0.34 로 같고 카탈로그의 PI 필름 실측 대역(0.34)과도 일치한다.",
}


def r3(x):
    return float(Decimal(str(x)).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP))


def emit(path):
    mats, own, ev, evf, tgt, stats, unassigned = plan()
    pool = {**{k: v for k, v in ev.items()}, **{k: v for k, v in evf.items()}}
    out, rows = [], []
    for (basis, k), ids in sorted(tgt.items()):
        s = stats[basis]
        val = r3(s['med'])
        span = f"{s['lo']}~{s['hi']}"
        iqr = f" · IQR {s['iqr']}" if s['iqr'] is not None else ""
        sample = sorted(pool[basis], key=lambda x: x[1])
        ex = ' · '.join(f"{mats[m][0][:44]} {v}" for m, v in
                        (sample[0], sample[len(sample) // 2], sample[-1]))
        extra = CLASS_NOTE.get(basis) or CLASS_NOTE.get(k) or ""
        for mid in sorted(ids):
            nm, cat, a = mats[mid]
            verdict = next(vk for vk in VERDICT_KEYS if NU in (a.get(vk) or []))
            cond = {"assumption": True, "class": basis, "basis": "catalog_class_median",
                    "class_n": s['n'], "class_range": span, "prior_verdict": verdict}
            if k in LAMINATE:
                cond["direction"] = "in-plane (nu12) — 두께방향 nu13 은 값이 다르다"
            notes = (
                f"[가정] 이 재료 자신을 잰 값이 아니다. 카탈로그 안 '{basis}' 클래스에서 "
                f"tier 3 이하이면서 estimated 가 아닌 포아송비를 가진 재료 {s['n']}종"
                f"(출처 {s['nsrc']}건)의 중앙값 {val} 을 해석 입력용으로 세웠다. "
                f"그 {s['n']}종의 분포는 최소 {s['lo']} · 최대 {s['hi']}{iqr} 다. "
                f"근거 재료 예 — {ex}. "
                + (extra + " " if extra else "")
                + f"앞 판정 `{verdict}` 은 그대로 참이다 — 벤더·원문은 여전히 이 재료의 "
                  f"포아송비를 인쇄하지 않으며, 이 값은 인쇄값이 아니라 우리 카탈로그 "
                  f"실측군의 중앙값이다(§676 — 판정은 서식에 대해 참이고 값은 그 옆에 선다). "
                  f"§43 대로 E·G 에서 역산하지 않았다. 이 제품 자신의 실측이 들어오면 "
                  f"그 값이 대표값이 된다.")
            out.append({"match_name": nm, "source": SOURCE,
                        "properties": [{"key": NU, "value": val, "unit": "1",
                                        "method": "estimated", "tier": 4,
                                        "conditions": cond, "notes": notes}]})
            rows.append((basis, k, mid, nm, val))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({"materials": out}, f, ensure_ascii=False, indent=1)
    return rows, stats, unassigned, mats
