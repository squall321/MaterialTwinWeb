#!/usr/bin/env python3
# 74차 JC — 두산전자 CCL 70종 코어7 빈칸 127칸의 부재 판정을 2026-09-13 실사로 재검증해 유효기간을 갱신한다.
#
# 이 배치는 **값을 하나도 넣지 않는다.** 70종의 빈칸이 이미 전부 판정돼 있었고
# (54·56·59·68·69·71차), 유일한 값 후보(DS-9000 `Tensile modulus 50~70 MPa`)는
# 56차 RC 가 이미 열어 보고 기각한 자리였다. 74차는 그 판정들이 **아직 유효한지**를
# 문서 지문으로 확인하고 그 사실을 판정문에 덧붙인다(73차 IB 의 유효기간 갱신과 같은 갈래).
#
# 입력(같은 디렉터리):
#   pp_grid.json  — 제품 상세표 24행을 rowspan 을 펴서 만든 격자(en/kr, 2026-09-13 재취득)
#   tds_rows.json — 전제품 TDS v9 표에 행이 있는 등급(55) / 없는 등급(15)
#   slugs.json    — material_id → 제품 페이지 슬러그
#
# 출력:
#   jc74_01_revalidation.json      — 기존 판정문에 **덧붙인** 재검증 각주(덮어쓰기가 아니다) + 69차 EB 낱칸 회수
#   jc74_02_flat_verdict_repair.json — 두산 밖 32재료의 같은 낱칸 사고 회수(제안)
from __future__ import annotations

import json
import os
import re
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = "74차 JC"
DB = os.path.join(os.environ.get("MATERIALTWIN_DATA_DIR",
                  "/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web"), "materialtwin.db")
CORE7 = ["physical.density", "mechanical.youngs_modulus", "mechanical.poisson_ratio",
         "thermal.expansion_linear", "thermal.conductivity", "thermal.specific_heat",
         "mechanical.tensile_strength"]
VERDICT_KEYS = ("core_absent_from_vendor_sheet", "core_not_applicable",
                "core_no_public_document", "core_rejected_printed_value")

grid = json.load(open(os.path.join(HERE, "pp_grid.json")))
tdsj = json.load(open(os.path.join(HERE, "tds_rows.json")))
NAME = tdsj["names"]
NO_TDS = set(tdsj["no_mech"])

# ── 74차 JC 가 실제로 다시 연 것. 판정문 끝에 이 한 문단을 덧붙인다. ─────────────────
STAMP_HEAD = (
    "\n\n**[74차 JC · 2026-09-13 재검증 — 문서 지문이 그대로라 이 판정은 아직 유효하다]** "
    "두산의 공개 제품문서 면(面)이 셋뿐이라는 것을 이번에 링크 단위로 확정했다. "
    "① 전제품 TDS v9(`/download/product/kr/CCL_All_Properties_PDF_240930_v9.pdf`)를 라이브에서 다시 받아 "
    "코퍼스 사본과 **md5 가 같았다(`fd8d4c084ceda37d438cecddd3965221`, 300,464 B)** — v9 가 아직 현행이고 v10 은 없다. "
    "② 제품 상세 70쪽을 en·kr 두 판으로 다시 받아 24행 표를 rowspan 까지 펴서 대조했다 — "
    "**두 판이 다 열리는 65등급에서 값이 다른 칸이 0개**다(71차 EB 가 한 등급에서 본 '언어판이 같다'가 전 등급·전 행에서 성립한다). "
    "DS-9000 쪽은 2026-09-01 코퍼스 사본과도 md5 가 같았다(`4aa45f9d1784a1c596cee4d58b089b7c`). "
    "③ 사이트 전체(제품 상세 70 · CCL 검색목록 · 기술지원 3쪽 · 솔루션 · What-is, en/kr)에서 "
    "**제품문서 링크는 그 TDS 한 파일뿐**이었고, 현행 `/download/pdf/catalog/<등급>.pdf` 는 전 등급 404 다. "
    "옛 경로도 닫혔다 — web.archive CDX 로 `doosanelectronics.com`(보존 PDF 28건)과 `dse.co.kr`(86건)을 전수로 훑으니 "
    "카탈로그 PDF 는 `DS-1202`·`DS-7409`·`DS-7209A`·`DS-7402` 넷뿐이고 그중 셋은 우리 70종 밖 세대다. "
    "④ 코퍼스 29,846편 전문에서 두산 등급명이 나오는 논문은 2편뿐이다 — "
    "Lee 2017(FPCB actuator)이 *'double-sided flexible copper clad laminate (Doosan Electronic, DSflex-600)'* 로 "
    "재료만 밝히고, Park 2017 은 참고문헌에 DS-7409HGB 프리프레그 카탈로그 URL 만 적는다. **둘 다 물성을 재지 않았다.**")

CP_CLAUSE = (
    " ⓐ **비열** — TDS v9 [Thermal] 표의 열을 200 dpi 렌더로 눈 대조했다: "
    "Tg(DMA 2.4.24.4 / DMA 2.4.24.2 / TMA 2.4.24C / DSC 2.4.25C) · Td(TGA 2.3.40) · T-288(2.4.24.1) · "
    "CTE(X a1 · Y a1 · Z a1 · Z a2) · Thermal Conductivity(**ASTM E 1461** · ASTM D 5470) · "
    "Max. Operating Temperature(UL 796) · Z Expansion(2.4.24.5). 비열 열이 없다. "
    "**주목할 것 하나** — 두산은 열전도율을 ASTM E 1461(레이저 플래시)로 잰다. 그 방법은 열확산계수 α 를 재고 "
    "k = α·ρ·Cp 로 환산하므로 **사내에는 Cp 가 반드시 있다.** 그런데 α 도 Cp 도 인쇄하지 않는다 — "
    "즉 역산할 재료가 하나도 없다(§43 역산 금지 이전에 산술 자체가 성립하지 않는다). "
    "표 층도 두드렸다: `corpus_index.py tables --want thermal.specific_heat` 이 비열 표를 가진 논문 220편을 세지만 "
    "두산 등급을 잰 것은 0편이다.")

TENSILE_CLAUSE_BLANK = (
    " ⓑ **인장강도** — 59차 UA 가 적은 '제품 페이지가 행을 인쇄하되 값 칸이 비어 있다'가 2026-09-13 현재도 글자 그대로 맞다. "
    "원시 HTML 에서 확인한 모양은 `<td colspan=2 rowspan=2>Tensile Strength</td>` 아래 "
    "`As Received | IPC-TM-650 2.4.18.3 | MPa | <td></td>` 와 `- | IPC-TM-650 2.4.19C | MPa | <td></td>` 두 줄이다 — "
    "**벤더가 시험법과 단위까지 찍어 놓고 값만 비운 것**이라 '이 시험이 이 등급에 해당하지 않는다'가 아니라 "
    "'해당하지만 공표하지 않는다'는 뜻이다. 70종 중 이 모양은 11등급이고 나머지는 행 자체가 없다.")

TENSILE_CLAUSE_ABSENT = (
    " ⓑ **인장강도** — TDS v9 [Mechanical] 표의 인장강도 두 열(`As Received / 2.4.18.3 / MPa` 와 `- / 2.4.19C / MPa`)에 "
    "값이 찍힌 것은 70종 중 **열두 등급뿐**이고(DS-7402BS (DF) 200~230 · DS-7402BS (DFM) 220~240 · "
    "DS-8402H BS (DFL) 180~220 [2.4.19C] / DSflex-600 220 · 600P 180 · 600U 390 · 600D 290 · 600UY 185 · "
    "600UF (DS) 280 · 600UK (SS) 280 · DSflex-900 300 · DS-9530 4.5 [2.4.18.3]) **그 열두 칸은 이미 적재돼 있다.** "
    "이 등급은 그 열둘에 들지 않는다. `Flexural Strength`(2.4.4B)는 TDS 에서 따로 인쇄되는 다른 열이라 옮기지 않았다.")

OTHER_CLAUSE = {
    "physical.density":
        " ⓒ **밀도** — 제품 상세표 24행에 `Density` 행이 없고(있는 등급은 `Density | - | - | g/cm3 | 값` 꼴로 찍힌다) "
        "SDS 9절 갈래는 69·71차가 이미 닫았다. 이번 재검증에서 DSR-1000 BS(2023-12-20) `N. Specific gravity  No data available`, "
        "DS-7409S (N) BS 영문(2024-04-04) 같은 행, 국문(2021-05-20) `하. 비중  자료없음` 을 다시 열어 확인했다.",
    "thermal.conductivity":
        " ⓒ **열전도율** — 이 등급의 [Thermal] 행은 Td·T-288·CTE(X·Y) 넷뿐이고 "
        "`Thermal conductivity (ASTM E 1461 / ASTM D 5470)` 행이 실리지 않았다. 형제 등급 값을 옮기지 않았다.",
    "mechanical.youngs_modulus":
        " ⓒ **영률** — DST-9000 계열 셋은 TDS v9 [Mechanical] 에서 필 강도 한 칸만 찍히고 "
        "영률·굽힘강도·저장탄성률·인장강도·포아송비가 전부 비어 있다. 알루미늄 베이스 방열 기판이라 "
        "두산이 이 계열의 기계 물성표를 공표하지 않는다. SDS 9절 서식에는 영률 항목 자체가 없다.",
    "mechanical.poisson_ratio":
        " ⓒ **포아송비** — 제품 상세표·TDS 두 곳 다 이 등급에서 비어 있다(59차 UA 의 판정이 그대로 유효하다).",
    "thermal.expansion_linear":
        " ⓒ **CTE** — 이 등급의 [Thermal] 행에 해당 열이 실리지 않았다.",
}

NO_TDS_CLAUSE = (
    " 이 등급은 **TDS v9 표에 행 자체가 없는 15등급** 중 하나다(v9 는 70종 중 55종만 싣는다) — "
    "제품 상세 쪽이 이 등급의 유일한 물성 문서이고, 그 24행 표가 곧 벤더가 공표한 전부다.")

# DS-9000 인장강도 — 56차 RC 의 기각을 뒤집지 않는다. 다음 파동에 넘길 검산만 덧붙인다.
DS9000_ADDENDUM = (
    "\n\n**[74차 JC — 56차 RC 의 기각을 유지한다. 다만 그 칸이 왜 아까운지는 수로 남긴다]** "
    "74차가 같은 행을 다시 열었다(en·kr 두 판이 글자 단위로 같다): "
    "`Tensile modulus | 50~70 | MPa | As received | IPC-TM-650 2.4.18.3`. "
    "**RC 의 결론에 동의한다 — 라벨이 modulus 인 것을 strength 로 옮기면 그것은 우리가 만든 값이다(§443·454).** "
    "그래도 다음 파동이 같은 자리를 처음부터 다시 재지 않도록 검산 셋을 적어 둔다. "
    "① 단위가 MPa 다 — 같은 표가 `Young's modulus | 2~5 | GPa` 를 **따로** 찍으므로 이 행이 정말 모듈러스라면 "
    "같은 쪽에서 같은 물성이 50배 어긋난다. "
    "② 시험법 `IPC-TM-650 2.4.18.3` 은 영률 행과 **같고**, TDS v9 [Mechanical] 에서 이 시험법이 머리로 달린 열은 "
    "`Young's Modulus (GPa)` 와 `Tensile Strength (MPa)` 둘뿐이다 — 단위가 MPa 인 쪽은 인장강도 열이다. "
    "③ 자릿수 검산 — 같은 표가 `Elongation | 2~3 | % | 2.4.19C` 를 찍는다. 거의 선형인 재료의 파단응력 상한은 "
    "E·e = (2~5 GPa)x(0.02~0.03) = 40~150 MPa 이고 50~70 MPa 이 그 안에 든다. 모듈러스로 읽으면 어떤 검산도 통과하지 못한다. "
    "**즉 이 칸은 '값이 없다'가 아니라 '벤더 인쇄가 틀렸을 가능성이 높다'는 칸이다.** "
    "다음 파동이 할 일은 값을 만드는 것이 아니라 **벤더 확인**이다 — "
    "`/en/contact/inquiry?category=1` 이 열려 있고, 이 등급은 공개 SDS 색인 120제품에 없어서 다른 경로가 없다.")


def pp_tensile_state(mid: str) -> str:
    rows = [r for r in grid[mid]["en"]["grid"]
            if len(r) >= 7 and re.match(r"^tensile strength$", r[1], re.I)]
    if not rows:
        return "absent"
    return "value" if any(r[6].strip() for r in rows) else "blank"


FLAT_NOTE = (
    "\n\n**[74차 JC — 69차 EB 의 판정문을 제자리로 옮겨 붙였다]** "
    "아래는 이 재료의 `attributes` 최상위에 `key`/`verdict`/`reason` **세 낱칸으로 흩어져 있던** 판정문이다. "
    "브리프 §4 의 예시 서식 `{\"material_id\":…, \"key\":…, \"verdict\":…, \"reason\":…}` 을 그대로 제출하면 "
    "`apply_core_verdicts.py` 가 `key`·`verdict`·`reason`·`source_url` 을 **각각 재료 속성 이름으로** 쓴다 "
    "(그 도구가 기대하는 것은 `{\"<판정키>\": {\"<물성키>\": \"<사유>\"}}` 다). "
    "이 사고로 106개 재료가 그 낱칸을 달고 있었고 그중 69개가 두산이다(인장강도 46 · 비열 23). "
    "두산 69건은 다행히 제대로 된 자리에도 판정이 따로 있어 집계는 멀쩡했지만, "
    "**그 자리에만 있던 20칸은 집계가 못 봤다**(§593). 아래 본문을 잃지 않도록 여기 합친다.\n\n")

BRIEF_FIX = ("**브리프 §4 의 예시를 고쳐야 한다** — `{\"batch\":…, \"verdicts\":["
             "{\"material_id\":2483, \"name\":…, \"core_absent_from_vendor_sheet\":"
             "{\"thermal.specific_heat\":\"<사유>\"}}]}` 가 맞는 모양이다.")

STRAY = ("key", "verdict", "reason", "source_url")


def main() -> None:
    c = sqlite3.connect("file:" + DB + "?mode=ro", uri=True)
    have: dict[int, set] = {}
    for m, k in c.execute("select distinct material_id,property_key from property_value"):
        have.setdefault(m, set()).add(k)
    attrs = {i: (n, json.loads(a or "{}"))
             for i, n, a in c.execute("select id,name,attributes from material")}

    out, stats = [], {"칸": 0, "재검증": 0, "판정 없던 칸": 0, "낱칸 회수": 0}
    for mid in sorted(grid, key=int):
        m = int(mid)
        name, at = attrs[m]
        cur = {}
        for vk in VERDICT_KEYS:
            v = at.get(vk)
            if isinstance(v, dict):
                for kk in v:
                    cur[kk] = (vk, v[kk])
        rec: dict[str, dict] = {}
        for p in CORE7:
            if p in have.get(m, ()):
                continue
            stats["칸"] += 1
            if p not in cur:
                stats["판정 없던 칸"] += 1
                continue
            vk, old = cur[p]
            body = STAMP_HEAD
            if p == "thermal.specific_heat":
                body += CP_CLAUSE
            elif p == "mechanical.tensile_strength":
                body += (TENSILE_CLAUSE_BLANK if pp_tensile_state(mid) == "blank"
                         else TENSILE_CLAUSE_ABSENT)
            elif p in OTHER_CLAUSE:
                body += OTHER_CLAUSE[p]
            if mid in NO_TDS:
                body += NO_TDS_CLAUSE
            if m == 2480 and p == "mechanical.tensile_strength":
                body += DS9000_ADDENDUM
            rec.setdefault(vk, {})[p] = old + body
            stats["재검증"] += 1
        # 69차 EB 의 판정문이 `key`/`verdict`/`reason` 낱칸으로 흩어져 있으면 제자리로 합친다.
        if at.get("key") and at.get("verdict") in VERDICT_KEYS and at.get("reason"):
            k, vk2, rsn = at["key"], at["verdict"], at["reason"]
            if k not in have.get(m, ()) and rsn.strip() not in rec.get(vk2, {}).get(k, ""):
                base = rec.get(vk2, {}).get(k) or cur.get(k, (None, ""))[1]
                rec.setdefault(vk2, {})[k] = (base or "") + FLAT_NOTE + rsn
                stats["낱칸 회수"] += 1
            for s in STRAY:
                if s in at:
                    rec[s] = None
        if rec:
            row = {"material_id": m, "name": name}
            row.update(rec)
            out.append(row)

    json.dump({"batch": BATCH + " — 부재 판정 재검증(덧붙임) + 69차 EB 낱칸 판정문 회수",
               "note": BRIEF_FIX, "verdicts": out},
              open(os.path.join(HERE, "jc74_01_revalidation.json"), "w"),
              ensure_ascii=False, indent=1)
    print("두산 재료", len(out), stats)

    # ── 두산 밖 37건 — 같은 낱칸 사고. 표적 밖이라 따로 낸다(적용은 사람이 고른다). ──
    other, ost = [], {"회수": 0, "어휘 밖이라 손대지 않음": 0}
    for i, (nm, at2) in attrs.items():
        if str(i) in grid or not at2.get("key"):
            continue
        k, vk2, rsn = at2.get("key"), at2.get("verdict"), at2.get("reason") or ""
        row = {"material_id": i, "name": nm}
        if vk2 in VERDICT_KEYS and rsn.strip() and k not in have.get(i, ()):
            old = at2.get(vk2)
            base = old.get(k, "") if isinstance(old, dict) else ""
            if rsn.strip() not in base:
                row[vk2] = {k: (base + FLAT_NOTE + rsn) if base else rsn}
                ost["회수"] += 1
        else:
            ost["어휘 밖이라 손대지 않음"] += 1
            continue
        for s in STRAY:
            if s in at2:
                row[s] = None
        other.append(row)
    json.dump({"batch": BATCH + " — 두산 밖 낱칸 판정문 회수(제안)",
               "note": BRIEF_FIX, "verdicts": other},
              open(os.path.join(HERE, "jc74_02_flat_verdict_repair.json"), "w"),
              ensure_ascii=False, indent=1)
    print("두산 밖", len(other), ost)


if __name__ == "__main__":
    main()
