#!/usr/bin/env python
# 신뢰등급을 실제 운용 기준으로 정규화 — "문서 종류"가 아니라 "값의 성격"으로 tier를 맞춘다.
#
# 사용: normalize_tiers.py [--apply]
#
# 배경: 이 DB의 tier1은 "특정 재료에 대해 문서에 인쇄된 실제 시험값"을 뜻해 왔다
# (tier1 1,662건이 벤더 TDS 유래, 235건이 논문 유래). 그런데 8단계 수집에서
# 에이전트에게 "데이터시트 → tier3"으로 지시하는 바람에 method=measured인데 tier3인
# 행이 대량 생겼다. 대표값 선택이 최저 tier를 고르므로 조회 결과가 갈린다.
#
# 규칙(문서 종류가 아니라 값의 성격으로 판정):
#   승격 tier3 → tier1 : method=measured 이고, 벤더가 자기 제품에 대해 인쇄한 값이거나
#                        논문이 그 재료를 직접 측정한 값
#   유지 tier3         : 계열/클래스 대표값, 2차 인용(남의 값을 표로 옮긴 것),
#                        좌표 추출값, 조건 추정값 — 노트·조건의 표지로 판별
#   격하 → computed/4  : 시뮬레이션·제일원리 논문 값, 저자가 "가정"한 값
from __future__ import annotations

import argparse
import re
import sqlite3
from collections import Counter
import sys

DB = "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db"

# 특정 재료의 실측치가 아님을 시사하는 표지. 하나라도 걸리면 승격하지 않는다.
NOT_A_DIRECT_MEASUREMENT = re.compile(
    r"계열|클래스|등가근사|대표값|추정|유사|proxy|representative|inferred|"
    r"미표기|미기재|not stated|not labelled|가정|assum|유도|derived|디지타이즈|digitiz|"
    r"상당재|equivalent|midpoint|중앙값|대체값|not available|매핑|근사",
    re.I)
# 논문 자체가 계산·시뮬레이션인 경우 — measured 표기 자체가 틀렸다.
COMPUTATIONAL = re.compile(
    r"simulat|modeling|modelling|first-principles|ab initio|\bDFT\b", re.I)
# 단, 계산과 실험을 함께 한 논문이 많다("Experiments and first-principles modeling").
# 노트가 측정임을 밝히면 제목보다 노트를 믿는다 — 실측을 계산으로 깎으면 손해가 크다.
MEASURED_HINT = re.compile(
    r"측정|실측|실험|nanoindentation|experiment|measured|관측", re.I)
# 남의 값을 비교표로 옮긴 것(그 논문의 측정이 아님). "Same paper reports"처럼
# 같은 논문의 다른 값을 가리키는 표현과 구분해야 하므로 저자·DB 이름을 근거로 삼는다.
SECONDARY_CITATION = re.compile(
    r"Ioffe|Weitzel|\bDing \d{4}\b|accepted range|비교표|본문 인용값", re.I)

# 개별 판정이 필요한 행 — 위 규칙으로는 잡히지 않거나, 잡히더라도 사유가 다르다.
# (id, 새 tier, 새 method 또는 None, 새 value 또는 None, 노트에 덧붙일 사유)
MANUAL = [
    (3851, 3, None, None,
     "[정규화] 여러 분리막의 중앙값이라 특정 제품 실측이 아님 — tier3."),
    (3893, 4, "computed", None,
     "[정규화] 저자가 계산을 위해 '가정'한 밀도 — 측정값이 아니므로 computed/tier4."),
    (3896, 3, None, None,
     "[정규화] 균일연신율(uniform elongation)이라 파단연신율보다 낮다 — 하한으로만 사용할 것."),
    (4773, 3, None, None,
     "[정규화] 원문이 '≈25~26 (근사)'로 준 값 — 단일 실측치가 아님."),
    (4776, 3, None, 5100.0,
     "[정규화] 원문 범위 5.1~5.2 g/cm3의 중앙값이었다. 규칙대로 하한 5.1로 정정."),
    (1384, 3, None, None,
     "[정규화] 논문이 제일원리와 실험을 병행해 이 값의 출처가 계산인지 측정인지 단정 불가 — tier3 유지."),
    (1411, 3, None, None,
     "[정규화] 나노인덴테이션과 마이크로역학 시뮬레이션을 병행한 논문 — 치밀 입자 기준값이라 tier3 유지."),
]
MANUAL_IDS = {row[0] for row in MANUAL}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    c = sqlite3.connect(DB)
    rows = c.execute("""select pv.id, s.kind, s.title, coalesce(pv.notes,''),
            coalesce(pv.conditions,''), m.name, pv.property_key
        from property_value pv join source s on s.id=pv.source_id
        join material m on m.id=pv.material_id
        where pv.quality_tier=3 and pv.method='measured'""").fetchall()

    promote, keep, to_computed = [], [], []
    for rid, kind, title, notes, cond, mat, key in rows:
        if rid in MANUAL_IDS:      # 개별 판정 대상은 자동 분류에서 제외
            continue
        blob = notes + " " + cond
        if COMPUTATIONAL.search(title) and not MEASURED_HINT.search(notes):
            to_computed.append((rid, mat, key, title))
        elif NOT_A_DIRECT_MEASUREMENT.search(blob):
            keep.append((rid, mat, key, "클래스·대표·추정 표지"))
        elif SECONDARY_CITATION.search(notes):
            keep.append((rid, mat, key, "2차 인용(비교표)"))
        elif kind in ("datasheet", "journal"):
            promote.append((rid, mat, key, kind))
        else:
            keep.append((rid, mat, key, f"2차 출처({kind})"))

    print(f"검토 대상 {len(rows)}건 (tier3 · method=measured)")
    print(f"  → tier1 승격      {len(promote)}  {dict(Counter(p[3] for p in promote))}")
    print(f"  → tier3 유지      {len(keep)}  {dict(Counter(k[3] for k in keep))}")
    print(f"  → computed/tier4  {len(to_computed)}")
    for rid, mat, key, title in to_computed:
        print(f"      #{rid} {mat[:28]:28s} {key[:28]:28s} {title[:44]}")
    print(f"  개별 판정         {len(MANUAL)}건")

    if not a.apply:
        print("\n[DRY-RUN] --apply 로 실제 반영")
        return 0

    for rid, *_ in promote:
        c.execute("update property_value set quality_tier=1 where id=?", (rid,))
    for rid, *_ in to_computed:
        c.execute("""update property_value set quality_tier=4, method='computed',
            notes=trim(coalesce(notes,'')||' [정규화] 시뮬레이션·제일원리 논문 값이라 실측이 아님.')
            where id=?""", (rid,))
    for rid, tier, method, value, why in MANUAL:
        c.execute("update property_value set quality_tier=? where id=?", (tier, rid))
        if method:
            c.execute("update property_value set method=? where id=?", (method, rid))
        if value is not None:
            c.execute("update property_value set value_num=? where id=?", (value, rid))
        # 재실행해도 같은 사유가 중복으로 붙지 않게 한다.
        c.execute("""update property_value set notes=trim(coalesce(notes,'')||' '||?)
            where id=? and coalesce(notes,'') not like ?""", (why, rid, f"%{why}%"))
    # 2차 패스 — method='datasheet'는 방법이 아니라 출처 종류다. 값의 성격으로 다시 매긴다.
    # (measured/handbook/computed/estimated 만 방법 어휘로 쓴다)
    ds = c.execute("""select pv.id, coalesce(pv.notes,''), coalesce(pv.conditions,''), s.kind
        from property_value pv join source s on s.id=pv.source_id
        where pv.method='datasheet'""").fetchall()
    remap = Counter()
    for rid, notes, cond, kind in ds:
        if NOT_A_DIRECT_MEASUREMENT.search(notes + " " + cond):
            method, tier = "estimated", 4        # 계열·등가근사
        elif kind == "datasheet":
            method, tier = "measured", 1         # 벤더가 자기 제품에 인쇄한 시험값
        elif kind in ("standard", "book"):
            method, tier = "handbook", 2
        elif kind == "database":
            method, tier = "handbook", 3         # 2차 DB
        else:
            method, tier = "measured", 3
        remap[(method, tier)] += 1
        c.execute("update property_value set method=?, quality_tier=? where id=?",
                  (method, tier, rid))
    print(f"  method='datasheet' 재분류 {len(ds)}건 → {dict(remap)}")

    # 3차 패스 — method와 tier가 서로 모순인 칸을 정리한다.
    # measured@tier2  : 논문이 남의 문헌값을 인용한 것(시뮬레이션 입력표 등) → handbook·tier3
    # measured@tier4  : "등가근사·클래스 대표" → estimated
    # handbook@tier4  : 1차 자료 없이 업계 취합·클래스 근사한 것 → estimated
    # computed@tier3  : 그래프 디지타이즈(원 데이터는 벤더 실측, 좌표 오차만 얹힘) → 그대로 둔다
    fix = Counter()
    for rid, in c.execute("select id from property_value where method='measured' and quality_tier=2"):
        c.execute("""update property_value set method='handbook', quality_tier=3,
            notes=trim(coalesce(notes,'')||' [정규화] 논문이 인용한 문헌값이라 그 논문의 측정이 아님.')
            where id=?""", (rid,))
        fix["measured@2 → handbook@3"] += 1
    for rid, in c.execute("""select id from property_value
            where method in ('measured','handbook') and quality_tier=4"""):
        c.execute("update property_value set method='estimated' where id=?", (rid,))
        fix["measured/handbook@4 → estimated@4"] += 1
    print(f"  모순 칸 정리 → {dict(fix)}")

    # 출처 메타 오기 정정(제목의 업체와 publisher가 다름).
    c.execute("update source set publisher='Sorbothane, Inc.' where id=40")

    c.commit()
    print("\n[APPLIED]")
    for label, sql in (("tier1", "quality_tier=1"), ("tier2", "quality_tier=2"),
                       ("tier3", "quality_tier=3"), ("tier4", "quality_tier=4")):
        n = c.execute(f"select count(*) from property_value where {sql}").fetchone()[0]
        print(f"  {label} {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
