#!/usr/bin/env python3
# 폐기 대장의 건강 상태를 점검한다 — `integrity_check.py` 의 대장 판.
#
# 왜 필요한가
#   대장은 **여러 배치가 동시에 쓰는 파일**이다. 37차 AV 가 짚었다 —
#   읽어서 고쳐 쓰는(read-modify-write) 방식이면 병렬 파동이 서로를 덮어쓴다.
#   그리고 대장이 조용히 망가지면 **두 방향으로 손해**다:
#     · 줄이 헛돌면 → 버린 논문을 다음 파동이 다시 연다(일 낭비)
#     · 줄이 잘못 걸리면 → **멀쩡한 논문이 표적에서 사라진다**(논문을 잃는다, 418번)
#
# **규칙: 대장은 append-only 다.** 새 줄은 `>>` 로 덧붙여라. 기존 줄을 고쳐야 하면
# 다른 파동이 도는 중이 아닌지 확인하고, 고친 뒤 이 점검기를 돌려라.
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from coverage_report import (VERDICT_ATTR_NA, VERDICT_ATTR_REJECT,  # noqa: E402
                             VERDICT_ATTR_VENDOR)
from mined_index import DB as MT_DB  # noqa: E402
from scan_targets import CORPUS, VERDICTS, norm_full  # noqa: E402

# 코어 빈칸 판정이 적히는 자리 셋 — `coverage_report.subsystem_core` 가 읽는 칸과 **같은 목록**이다.
# 여기에 이름을 다시 적지 않는다: 갈래를 늘렸는데 점검기가 옛 목록을 보면 새 갈래가 안 점검된다.
CORE_VERDICT_ATTRS = (VERDICT_ATTR_NA, VERDICT_ATTR_VENDOR, VERDICT_ATTR_REJECT)


def check_core_verdicts(mt: sqlite3.Connection) -> tuple[list[str], list[str]]:
    """`material.attributes` 의 코어 빈칸 판정이 집계가 읽을 수 있는 꼴인지 본다.

    이상으로 세는 것 둘.
      · **재료 단위 문자열 판정** — 집계는 그 재료의 코어 7칸을 통째로 덮는 것으로 읽는다.
        45차 GD 의 탄소 7종이 그렇게 사유 셋을 한 사유로 덮었고 재료 하나는 분류까지 틀려 있었다.
        판정은 언제나 `{물성키: 사유}` 여야 한다.
      · **물성 정의에 없는 키** — 오타면 그 칸은 영원히 V5 로 세어진다(§593 의 조용한 얼굴).

    경고로만 내는 것 하나.
      · **판정을 달았는데 그 칸에 값이 있다** — 선언과 데이터가 어긋난다. 값을 지우는 것이
        고침이 아니므로(§565) 여기서는 **신고만** 한다.
    """
    keys = {k for (k,) in mt.execute("select key from property_definition")}
    # 반례로 칠 값과 안 칠 값을 가른다.
    #
    # `core_absent_from_vendor_sheet` 는 **"이 등급에 대해 벤더 시트가 그 열을 안 찍는다"** 는
    # 주장이다. 그 칸에 t3 클래스 대표값이나 t4 가정값이 앉아 있는 것은 **주장을 반증하지 않는다** —
    # 그 값들은 애초에 벤더 시트에서 온 것이 아니다. 재료 229(Doosan DS-7402)가 이 자리다.
    # 선언문 자체가 "카탈로그의 유일한 Doosan 비열 행은 벤더값이 아니라 FE 해석 논문의 FR-4
    # 클래스값이다" 라고 적어 두었는데, 검사기가 tier 를 안 보고 세 파동 연속 같은 신고를 냈다.
    #
    # 그래서 판정 종류마다 반례의 문턱을 달리 둔다.
    #   · 벤더 시트 부재  → **tier1(그 제품에 대해 인쇄된 값)만** 반증한다.
    #   · 해당 없음       → 실측(tier≤3)이면 반증한다. 물리적으로 정의가 안 된다는 주장이니까.
    #   · 인쇄값 기각     → **실측(tier≤3)만** 반증한다. 65차에 문턱을 4에서 3으로 내렸다.
    #
    # 기각 판정의 뜻은 "원문이 인쇄한 이 값을 **그 등급의 값으로** 귀속시키지 않았다" 이지
    # "이 칸을 영원히 비워 두라" 가 아니다. 뒤에 같은 숫자가 `tier4 · assumption:true` 로
    # 들어오면 그건 원문의 주장을 되살린 게 아니라 **우리 가정으로 다시 세운 것**이라
    # 어긋남이 아니다. 65차 AB 가 Sr 페라이트 25등급에 Eclipse 공통값을 그렇게 넣었고
    # notes 가 "등급별이 아니라 소결 하드페라이트 공통값" 이라고 그대로 적는다.
    # 문턱을 4로 두면 그 50건이 경고를 채워 **진짜 어긋남(재료 582 의 t2)이 묻힌다.**
    COUNTER_TIER = {"core_absent_from_vendor_sheet": 1,
                    "core_no_public_document": 1,
                    "core_not_applicable": 3,
                    "core_rejected_printed_value": 3}
    have: dict[int, dict[str, int]] = {}
    for mid, k, t in mt.execute(
            "select material_id,property_key,quality_tier from property_value"):
        cur = have.setdefault(mid, {})
        cur[k] = min(cur.get(k, 9), t if t is not None else 9)
    bad, warn = [], []
    for mid, name, raw in mt.execute("select id,name,attributes from material"):
        try:
            a = json.loads(raw or "{}")
        except json.JSONDecodeError:
            bad.append(f"재료 {mid} — attributes JSON 파싱 실패")
            continue
        if not isinstance(a, dict):
            continue
        for attr in CORE_VERDICT_ATTRS:
            v = a.get(attr)
            if v is None:
                continue
            if not isinstance(v, dict):
                bad.append(f"재료 {mid} `{attr}` 가 dict 가 아니다({type(v).__name__}) — "
                           f"{str(name)[:44]}")
                continue
            for k in v:
                if k not in keys:
                    bad.append(f"재료 {mid} `{attr}` 의 `{k}` 는 물성 정의에 없다")
                t = have.get(mid, {}).get(k)
                if t is not None and t <= COUNTER_TIER.get(attr, 4):
                    warn.append(f"재료 {mid} `{attr}` 가 `{k}` 를 선언했는데 t{t} 값이 있다 — "
                                f"{str(name)[:44]}")
    return bad, warn


def main() -> int:
    lines = [ln for ln in VERDICTS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    recs, bad = [], []
    for i, ln in enumerate(lines, 1):
        try:
            recs.append((i, json.loads(ln)))
        except json.JSONDecodeError as e:
            bad.append(f"{i}행 JSON 파싱 실패 — {e}")

    # 코퍼스·DB 조회 준비
    cp = sqlite3.connect(CORPUS)
    corp = {norm_full(t): p for p, t in cp.execute(
        "select path,title from doc where title is not null")}
    paths = set(corp.values())
    mt = sqlite3.connect(MT_DB)
    agg = {r[0]: r[1] for r in mt.execute(
        "select source_id,count(*) from property_value where source_id is not null group by 1")}
    rows: dict[str, int] = {}
    for sid, t in mt.execute("select id,title from source where title is not null"):
        k = norm_full(t)
        rows[k] = max(rows.get(k, 0), agg.get(sid, 0))

    seen, stale, conflict, nopath = set(), [], [], []
    for i, r in recs:
        t = r.get("title")
        if not t:
            bad.append(f"{i}행 title 없음")
            continue
        k = norm_full(t)
        if k in seen:
            bad.append(f"{i}행 제목 중복 — {t[:56]}")
        seen.add(k)
        # ① DB 에 값이 있는데 폐기로 적혔나 — **가장 위험한 오류다**
        if rows.get(k, 0) > 2:
            conflict.append(f"{i}행 — DB 값 {rows[k]}행이 있다: {t[:56]}")
        # ② 코퍼스의 어떤 논문과도 안 걸리나
        p = r.get("path")
        if p and p in paths:
            continue
        if k in corp:
            nopath.append(i)
            continue
        if not r.get("not_in_corpus"):
            stale.append(f"{i}행 — 코퍼스에 안 걸린다: {t[:56]}")

    print(f"대장 {len(lines)}줄 · 파싱 {len(recs)}")
    print(f"  path 있는 줄 {sum(1 for _, r in recs if r.get('path'))} / {len(recs)}")
    for lbl, xs in (("**치명 — DB 에 값이 있는데 폐기다**(418번)", conflict),
                    ("형식 오류", bad),
                    ("코퍼스에 안 걸린다 — `path` 를 박아라(428번)", stale)):
        if xs:
            print(f"\n✗ {lbl} {len(xs)}건")
            for x in xs[:8]:
                print(f"    {x}")
    if nopath:
        print(f"\n· 제목으로는 걸리지만 `path` 가 없는 줄 {len(nopath)}개 — "
              f"제목 표기가 흔들리면 죽는다. 채워 두는 편이 안전하다")
    cv_bad, cv_warn = check_core_verdicts(mt)
    print(f"\n코어 빈칸 판정 — 읽는 자리 {len(CORE_VERDICT_ATTRS)}칸")
    if cv_bad:
        print(f"\n✗ **판정이 집계가 읽을 수 없는 꼴이다** {len(cv_bad)}건")
        for x in cv_bad[:8]:
            print(f"    {x}")
    if cv_warn:
        print(f"\n· 선언과 데이터가 어긋난다 {len(cv_warn)}건 — 신고만 한다(브리프 565)")
        for x in cv_warn[:8]:
            print(f"    {x}")

    n = len(conflict) + len(bad) + len(stale) + len(cv_bad)
    print(f"\n{'✔ 이상 0개' if n == 0 else f'✗ 이상 {n}개'}")
    return 1 if conflict or bad or cv_bad else 0


if __name__ == "__main__":
    sys.exit(main())
