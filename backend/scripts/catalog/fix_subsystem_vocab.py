#!/usr/bin/env python3
# 계통 어휘가 갈라 놓은 재료를 합치고 범위 밖 재료를 표시한다 — 43차 EA 가 근거를 댄 정정이다.
#
# 왜 필요한가
#   `subsystem` 은 화면의 계통 필터를 만드는 축인데, **같은 모듈의 부품이 다른 값에 들어가**
#   필터가 부품을 나눠 버렸다. 실측으로 확인한 자리가 셋이다.
#     · 193 보이스코일선(`audio`) 과 83~85 진동판 필름(`speaker`) — 같은 스피커 모듈이다
#     · 197 압연동박(`pcb`) 과 261 압연동박(`fpcb`) — 같은 것이 두 값에 있다
#     · 122 TSV 구리(`packaging`) 와 176 TSV 배리어(`soc`) — 같은 공정 재료다
#   그리고 `soc`(10종)에는 SoC 가 하나도 없다. 전부 웨이퍼레벨 패키징 유전체·범프다 —
#   이름이 내용과 다르면 화면에서 못 찾는다. `wlp` 로 고친다.
#
# 왜 이 스크립트인가
#   병합기(`_materialtwin_merge.py`)는 삽입만 하지만 `CURATION_KEYS`(role·subsystem)만은
#   기존 재료에도 반영한다. 그러니 dev 에서 한 번 고치면 cae00 으로 따라간다.
#
# 한 번 더 돌려도 안전하다(멱등).
from __future__ import annotations

import json
import os
import sqlite3
import sys

DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR", "var/data"), "materialtwin.db")

# ── ① 계통 어휘 — 갈라져 있던 것을 합친다 ────────────────────────────────────
SUB: dict[int, tuple[str, str]] = {}
for i in (60, 83, 84, 85, 153, 193, 267):
    SUB[i] = ("acoustics", "스피커·음향 모듈 부품 — audio/speaker/acoustics 3분할을 합쳤다")
SUB[261] = ("pcb", "연성 동박적층판용 압연동박 — 197 RA 동박과 같은데 fpcb 로 갈려 있었다")
for i in (160, 161, 176, 430, 547, 548, 549, 1358, 1359, 1360):
    SUB[i] = ("wlp", "웨이퍼레벨 패키징(RDL 유전체·범프·TSV) — 옛 soc 는 이름이 내용과 달랐다")
SUB[122] = ("wlp", "TSV 도체 — 176 TSV 배리어와 같은 공정 재료인데 계통이 갈려 있었다")
_LAM = {94: "220 Isola 370HR", 98: "198 High-Tg FR-4 프리프레그",
        121: "229 두산 DS-7402 CCL", 145: "204 솔더마스크 PSR"}
for i, prod in _LAM.items():
    SUB[i] = ("pcb", f"적층판 계열 클래스 대표값 — 제품판({prod})이 pcb 에 있다")

# ── ② role — 다른 산업의 실제 제품이다(브리프 193) ──────────────────────────
# **GPO-3(2377~2379)는 넣지 않았다.** 낙하 모델의 Glastic 부품 근거라 범위 안이다
# (`docs/drop_materials.k` 298~309행). 442 Lexan FR25A 도 뺐다 — 난연 PC 필름은
# 전자 절연재로 정당하고, PV 백시트는 그 필름의 한 용도일 뿐이다.
OOS: dict[int, str] = {
    **{i: "치과 수복용 레진 시멘트" for i in (1246, 1247, 1248)},
    **{i: "경피흡수 의약 전달용 실리콘 PSA" for i in (1176, 1177)},
    **{i: "태양광 모듈 백시트" for i in (439, 440, 441)},
    **{i: "발전·압력용기 구조재" for i in (1353, 2263, 2265, 2289, 2358, 2359, 2360)},
    **{i: "로켓 추진기관 재료" for i in (817, 818)},
    **{i: "특수효과·몰드용 실리콘/우레탄" for i in
       (406, 407, 408, 409, 410, 411, 413, 414, 415, 416, 417)},
    449: "기체분리 막모듈",
    1674: "로 단열 블랭킷",
    419: "건축 구조 글레이징 실런트",
    **{i: "식품·의약 포장 배리어 필름" for i in (462, 463, 464, 465, 466, 467)},
}
# ── ③ role — 실험실 배합·표면 상태 그릇이다(브리프 115·116) ─────────────────
EVI: dict[int, str] = {
    420: "note 가 스스로 lab formulation 이라 밝힌다",
    433: "이름에 배합비(Versalink P-1000 : Isonate 143L = 4:1)가 박혀 있다",
    1289: "저자가 직접 합성해 측정한 기준물이다",
    1704: "표면 처리 상태 그릇이다 — 벌크 Al2024-T3 는 id 15 에 있다",
}


def main() -> int:
    if not os.path.exists(DB):
        print(f"DB 가 없다: {DB} — MATERIALTWIN_DATA_DIR 를 확인하라", file=sys.stderr)
        return 1
    c = sqlite3.connect(DB, timeout=60)
    c.execute("pragma busy_timeout=60000")

    def patch(mid: int, **kw) -> bool:
        row = c.execute("select attributes,name from material where id=?", (mid,)).fetchone()
        if row is None:
            print(f"  · id {mid} 없음 — 건너뛴다")
            return False
        a = json.loads(row[0]) if row[0] else {}
        if all(a.get(k) == v for k, v in kw.items()):
            return False                                    # 이미 같다(멱등)
        a.update(kw)
        c.execute("update material set attributes=? where id=?",
                  (json.dumps(a, ensure_ascii=False), mid))
        return True

    n_sub = sum(patch(m, subsystem=v, subsystem_basis=w) for m, (v, w) in SUB.items())
    n_oos = sum(patch(m, role="out_of_scope", role_reason=w) for m, w in OOS.items())
    n_evi = sum(patch(m, role="evidence", role_reason=w) for m, w in EVI.items())
    c.commit()
    print(f"계통 재배치 {n_sub} · out_of_scope {n_oos} · evidence {n_evi}")

    print("\n── 계통 분포(role=product)")
    for s, k in c.execute(
            "select coalesce(json_extract(attributes,'$.subsystem'),'(태그없음)') s, count(*) "
            "from material where json_extract(attributes,'$.role')='product' "
            "group by 1 order by 2 desc"):
        print(f"  {s:<14}{k:>5}")
    print("\n── role 분포")
    for r, k in c.execute(
            "select coalesce(json_extract(attributes,'$.role'),'(없음)'), count(*) "
            "from material group by 1 order by 2 desc"):
        print(f"  {r:<14}{k:>5}")
    c.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
