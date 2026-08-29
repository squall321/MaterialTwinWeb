"""54차 PB — **출처가 딴 문서를 가리키는 값 70행**을 옳은 출처로 옮긴다. 한 행도 지우지 않는다(§565).

§578 이 세운 벽 그대로다 — 출처 행의 메타는 못 고친다(묘비를 적을 칸이 없고, 자연키 밖에
적으면 운영에 안 가고 자연키 안에 적으면 운영에 새 행이 생긴다). **그래서 출처를 고치는 대신
값을 옮긴다.** §579 의 분기 ⑤ 가 그 이동을 운영까지 나른다.

## 인계 검증(§479·505 — 인계는 언제나 검증 대상이다)

넷을 다 재현했고 **셋은 맞았고 하나는 뒤집혔다**(뒤집힌 것은 아래 `안 고친 것`).

| 인계 | 재측 |
|---|---|
| Uddeholm src4593 의 60행이 딴 시트를 인용한다 (Corrax 6·Impax 12·Orvar 10·Unimax 10·Vidar 22) | **같다.** 6+12+10+10+22 = 60, 재료·행수까지 일치 |
| 재료576 의 열전도율 26 W/(m·K) 가 3641 인데 3678 이어야 한다 | **같다.** 행 자신의 notes 가 그렇게 적고 URL 이 3678 의 URL 이다 |
| 틀린 DOI 다섯(src3280·2779·3119·4419·273) | **같다.** Crossref 전수 재조회로 다섯 다 확인 |
| src2919 는 URL·DOI 가 둘 다 딴 논문 | **같고, 더 있다** — 같은 논문이 **올바른 DOI 로 이미 카탈로그에 있다**(src2828) |

### ① Uddeholm — **조건이 스스로 시트를 짚는다**

60행의 `conditions.figure` 가 판(edition)과 발행월을 verbatim 으로 인쇄한다. 그것이 지문이다.

```
재료2390 Corrax          Ed.15(11.2025) p.3 `Toughness` 표          → Corrax Ed.15 (11.2025)
재료2393 Impax Supreme   Ed.7(09.2011) p.4 `Impact energy, J (Charpy V)` → Impax Ed.7 (09.2011)
재료2394 Orvar Supreme   Ed.13(06.2021) p.5·p.7                      → Orvar Ed.13 (06.2021)
재료2420 Vidar Superior  Ed.4(09.2013) p.4·p.6·p.7                   → Vidar Ed.4 (09.2013)
재료2421 Unimax          Ed.8(01.2021) p.4                           → Unimax Ed.8 (01.2021)
```

**원본 PDF 로 교차확인했다.** `pdftotext -layout` 전수 —
- Corrax Ed.15 p.3 `Toughness` 표가 `ST-2 direction 15 / 7 / 4` · `LT-2 direction 100 / 23 / 4` 를
  인쇄한다. DB 의 6행과 **여섯 값이 그대로다.**
- `Impact energy, J (Charpy V)` 는 **Impax 시트에만** 있고, `Charpy U specimens` 는 **Vidar 시트에만** 있다.
- **단수·복수가 갈린다** — Vidar 는 `EFFECT OF TESTING TEMPERATURE**S**`, Unimax·Orvar 는 단수다.
  DB 조건이 그 단복수까지 시트와 일치한다.
- Dievar 시트 전문에 `Corrax` 가 **0회**다.

그리고 다섯 시트가 이미 출처로 있고, **각 시트 밑에 그 재료의 다른 물성이 이미 들어 있다**
(Corrax 6·Impax 7·Orvar 10·Vidar 10·Unimax 10키). 옮길 자리가 원래부터 그 시트다.

### ② 재료576 — 행의 notes 가 스스로 출처를 밝힌다

`thermal.conductivity 26 W/(m·K)` 의 notes verbatim — *"**이 행만 출처가 Xianyi 다** —
Solder Connection 표는 이 합금의 열전도율을 `-`(미인쇄)로 둔다"*. 그리고 그 notes 가 인쇄한
Xianyi 문서 URL 이 **src3678 의 url 과 글자까지 같다.**

**카탈로그 안에서 닫힌다** — 같은 재료의 밀도 행(출처 3641)이 Solder Connection 행을
`'Pb92.5Sn05Ag2.5 | 287 / 296 | 11.02 | 0.2 | **-** | 295 | - | -'` 로 verbatim 인용하는데
다섯째 칸(Thermal Conductivity)이 `-` 다. 그리고 같은 Xianyi 행에서 온 CTE(2.4e-5 /K)는
**이미 3678 을 가리키고 있다.** 이 한 행만 남아 있었다.

### ③ src2919 — 틀린 DOI 를 고치는 대신 **이미 있는 옳은 출처로 옮긴다**

Crossref·EuropePMC 재조회 —
- `10.1038/s41598-023-46330-6` = *Whole-lake acoustic telemetry to evaluate survival of stocked
  juvenile fish* (Koeberle et al.). **딴 논문이다.**
- URL 의 `MED/37932378` = *X-ray reflectivity study of the heat shock protein Hsp70…*
  (`10.1038/s41598-023-46066-3`). **또 딴 논문이다.**
- 제목으로 Crossref 를 치면 참값은 `10.1038/s41598-023-46078-z`(Sci Rep 2023, Zhang/Chen/Xie).

**그 DOI 가 이미 카탈로그에 있다 — src2828, 제목이 글자까지 같다.** 즉 이건 "틀린 DOI" 이기
전에 **출처 중복**이고, 53차 OA 의 일곱 지문이 못 잡은 것이다(DOI·URL 이 둘 다 틀려서
어느 지문에도 안 걸린다). 두 출처의 값은 **같은 Table 2 의 다른 열**이라 상보적이다 —
2828 은 무충전 `PEEK9` 열 5행(재료83), 2919 는 `30%SGFR-PEEK` 열 8행(재료298).

**DOI 칸은 안 고친다**(§578) — 고치면 운영에 새 출처 행이 생긴다. 참조가 0 이 될 뿐이다(§565).

### ④ src3119 — 같은 모양이고, OA 가 남긴 이유가 열어 보니 닫힌다

`10.1021/acsomega.9b00825` = *Liposomal Nanovesicles…*(Crossref). 참값 `…8b01979` 는
**src2875 가 이미 갖고 있다**(URL 도 같은 PMC6644085 fullTextXML).

OA 는 *"남길 쪽 제목이 `Table 1 (columns 'phi_fl', 'tau_PF /ns', 'tau_DF /us')` 로 표를 지목해서
합치면 3119 의 1행이 'Table 1 에서 왔다' 고 주장하게 된다"* 는 이유로 **의심에 남겼다.**
그 1행을 열어 보니 — notes verbatim *"Table 1 'Photophysical Properties of Acridane-Oxadiazole
Emitters', 행 'DMAC-DPO, toluene', 열 머리글 tau_PF^e/ns = 7.0"* 이다.
**그 표, 그 열이다.** 주장이 참이 되므로 옮긴다.

## 안 고친 것 — 검증에서 뒤집혔다

**틀린 DOI 넷(src3280·2779·4419·273)은 그대로 둔다.** Crossref 로 다섯 다 확인했지만,
그 넷은 **53차 OA 가 이미 합쳐서 참조가 0** 이고, 참값 DOI 는 **살아남은 출처가 이미 갖고 있다**
(`source.doi` 는 UNIQUE 다 — 옮겨 적을 수 없다). 남은 선택지는 `NULL` 로 비우는 것뿐인데
그건 자연키를 바꾸므로 **운영에 빈 껍데기 출처가 하나 더 생긴다**(§578). 값이 하나도
안 걸린 죽은 행의 DOI 를 지우자고 운영에 행을 늘리지 않는다. 위험은 남는다 —
`10.3390/ma15207112`·`10.1016/j.jallcom.2021.160204`·`10.1016/j.eurpolymj.2007.06.017` 은
**실재하는 딴 논문의 DOI** 라, 나중에 그 논문을 적재하면 `UNIQUE(doi)` 로 이 껍데기에 붙는다.
`docs/source_duplicates.json` 에 적어 넘긴다.

## 병합 예행 — 60행 중 **4행이 분기 ⑤ 를 못 탄다**(보고, 안 고쳤다)

`find_source_moved_row` 는 값으로 안 갈리면 **조건을 사전으로 대조**하는데(§579),
`base` 에서 `moved_from_source` 를 **src 쪽에서만** 벗기고 dst 쪽 `d` 는 그대로 둔다.
그래서 **두 번 옮긴 행**(OA 가 4593→4571, 이 배치가 4571→제품시트)은 운영 조건에 표시가
남아 있어 사전 대조가 언제나 어긋난다. 값으로 갈리는 56행은 멀쩡하고, 값이 겹치는 4행
(재료2390 의 4.0 J 둘 · 재료2420 의 23.2 J 둘)만 걸린다.

**고치지 않았다** — 같은 파동의 54차 PA 가 `_materialtwin_merge.py` 를 만지고 있다(§553).
고침은 한 줄이다: `find_source_moved_row` 의 사전 대조에서 dst 쪽도
`{k: v for k, v in d.items() if k != SOURCE_MOVE_MARKER}` 로 벗기면 된다.

Revision ID: e6f7a8b9c0d1
Revises: d5e6f7a8b9c0
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "e6f7a8b9c0d1"
down_revision = "d5e6f7a8b9c0"
branch_labels = None
depends_on = None

MARK = "moved_from_source"
MOVED_AT = "2026-08-29"
BY = "54차 PB"

# 병합기(`_materialtwin_merge.SOURCE_NATURAL_KEY`)와 **같은 목록이어야 한다** —
# 한쪽만 바뀌면 분기 ⑤ 가 조용히 죽는다.
NATURAL_KEY = ("kind", "doi", "isbn", "url", "title", "publisher", "license")

_UD_API = "https://www.uddeholm.com/app/uploads/sites/216/productdb/api/"
_DIEVAR = ("datasheet", None, _UD_API + "tech_uddeholm-dievar_en.pdf",
           "Uddeholm Dievar — product datasheet, Edition 15 (10.2025)")

# (옛 출처 손잡이, 새 출처 손잡이, 재료 이름 또는 None, 물성키 또는 None, 사유)
#   · 재료 이름을 주면 그 재료의 행만 옮긴다(§535 — id 가 아니라 자연키).
#   · None 이면 그 출처의 **모든 행**을 옮긴다.
# 손잡이는 `(kind, doi, url, title)` 이고 **여러 행이 걸리면 그 군은 통째로 건너뛴다**(§536).
PLAN: list[tuple[tuple, tuple, str | None, str | None, str]] = [
    # ── ① Uddeholm — 다섯 제품 60행 ────────────────────────────────────────
    (_DIEVAR,
     ("datasheet", None, _UD_API + "tech-uddeholm-corrax_en.pdf",
      "Uddeholm Corrax — product datasheet, Edition 15 (11.2025)"),
     "Uddeholm Corrax precipitation-hardening stainless mould steel", None,
     "조건의 `figure` 가 `Ed.15(11.2025) p.3 Toughness 표` 를 짚는다 = Corrax 시트의 판이다"
     "(Dievar 는 Ed.15 10.2025). 원문 대조 — Corrax p.3 `Charpy-V (J)` 표가 "
     "`ST-2 direction 15 / 7 / 4` · `LT-2 direction 100 / 23 / 4` 로 여섯 값을 그대로 인쇄한다. "
     "Dievar 시트 전문에 `Corrax` 는 0회다"),

    (_DIEVAR,
     ("datasheet", None, _UD_API + "tech_uddeholm-impax-supreme_en.pdf",
      "Uddeholm Impax Supreme — product datasheet, Edition 7 (09.2011)"),
     "Uddeholm Impax Supreme prehardened mould steel (AISI P20 modified)", None,
     "조건의 `figure` 가 `Ed.7(09.2011) p.4 Impact energy, J (Charpy V) 그래프` 를 짚는다. "
     "그 캡션 문자열은 Uddeholm 시트 다섯 장 중 **Impax Supreme 에만** 있다(전수 대조)"),

    (_DIEVAR,
     ("datasheet", None, _UD_API + "tech_uddeholm-orvar-supreme_en.pdf",
      "Uddeholm Orvar Supreme — product datasheet, Edition 13 (06.2021)"),
     "Uddeholm Orvar Supreme hot-work tool steel "
     "(Superior ESR AISI H13, NADCA#207 Grade B)", None,
     "조건의 `figure` 가 `Ed.13(06.2021) p.5 EFFECT OF TESTING TEMPERATURE ON IMPACT ENERGY` 와 "
     "`p.7 APPROXIMATE IMPACT STRENGTH AT DIFFERENT TEMPERING TEMPERATURES` 를 짚는다. "
     "두 캡션이 Orvar 시트 본문에 verbatim 으로 있다(**단수** TEMPERATURE — Vidar 는 복수다)"),

    (_DIEVAR,
     ("datasheet", None, _UD_API + "tech_uddeholm-vidar-superior_en.pdf",
      "Uddeholm Vidar Superior — product datasheet, Edition 4 (09.2013)"),
     "Uddeholm Vidar Superior hot-work tool steel "
     "(AISI H11 modified, X36 CrMoV5-1 / W.-Nr. 1.2340)", None,
     "조건의 `figure` 가 `Ed.4(09.2013)` 의 세 그림을 짚는다 — "
     "`EFFECT OF TESTING TEMPERATURE**S** ON IMPACT ENERGY`(복수)·"
     "`APPROXIMATE IMPACT ENERGY AT DIFFERENT TEMPERING TEMPERATURES`·"
     "`Charpy U specimens, short transverse direction`. 셋 다 Vidar 시트에만 있다"),

    (_DIEVAR,
     ("datasheet", None, _UD_API + "tech_uddeholm-unimax_en.pdf",
      "Uddeholm Unimax — product datasheet, Edition 8 (01.2021)"),
     "Uddeholm Unimax ESR-remelted Cr-Mo-V tool steel", None,
     "조건의 `figure` 가 `Ed.8(01.2021) p.4 EFFECT OF TESTING TEMPERATURE ON IMPACT ENERGY` 를 "
     "짚는다. 그 판·쪽·캡션이 Unimax 시트와 일치한다"),

    # ── ② 재료576 — 행이 스스로 밝힌 출처 한 칸 ─────────────────────────────
    (("datasheet", None,
      "https://www.solderconnection.com/wp-content/uploads/2023/03/"
      "Solder-Alloy-Technical-Specifications.pdf",
      "Solder Alloy Technical Specification (The Solder Connection Ltd)"),
     ("datasheet", None,
      "https://pub-mediabox-storage.rxweb-prd.com/exhibitor/document/"
      "exh-8820eafd-de18-413d-b843-442e7c5b8ae6/fc18cbef-336a-4c7d-a71e-4170b3e3c1ea.pdf",
      "Guangzhou Xianyi Electronic Technology Co., Ltd. — Product Manual, Leading Brand of "
      "Semiconductor Microassembly Interconnecting Materials, 'List of Common Solders' "
      "(Soft Solders), pp. 3-5"),
     "92.5Pb5Sn2.5Ag Solder Alloy", "thermal.conductivity",
     "행의 notes 자신이 *'이 행만 출처가 Xianyi 다 — Solder Connection 표는 이 합금의 "
     "열전도율을 -(미인쇄)로 둔다'* 라고 적고, 그 notes 가 인쇄한 URL 이 옮겨 갈 출처의 url 과 "
     "글자까지 같다. 같은 재료의 밀도 행이 Solder Connection 행을 "
     "`'… | 11.02 | 0.2 | - | 295 | - | -'` 로 verbatim 인용하는데 열전도율 칸이 `-` 다. "
     "같은 Xianyi 행에서 온 CTE 2.4e-5 /K 는 이미 이 출처를 가리킨다"),

    # ── ③ src2919 → 같은 논문의 올바른 DOI 출처 ────────────────────────────
    (("journal", "10.1038/s41598-023-46330-6",
      "https://europepmc.org/article/MED/37932378",
      "Compression properties and constitutive model of short glass fiber reinforced "
      "poly-ether-ether-ketone (PEEK)"),
     ("journal", "10.1038/s41598-023-46078-z",
      "https://pmc.ncbi.nlm.nih.gov/articles/PMC10628305/",
      "Compression properties and constitutive model of short glass fiber reinforced "
      "poly-ether-ether-ketone (PEEK)"),
     None, None,
     "옛 출처는 DOI 도 URL 도 딴 논문이다 — DOI `10.1038/s41598-023-46330-6` 는 어류 음향 "
     "텔레메트리(Koeberle), URL 의 `MED/37932378` 은 Hsp70 X선 반사(`…46066-3`)다. "
     "제목으로 Crossref 를 치면 참값이 `10.1038/s41598-023-46078-z` 이고 **그 DOI 를 가진 "
     "출처가 이미 카탈로그에 있다**(제목 verbatim 동일). 두 출처의 값은 같은 Table 2 의 다른 "
     "열이라 상보적이다 — 남길 쪽 5행은 무충전 `PEEK9`, 옮길 8행은 `30%SGFR-PEEK` 열이다"),

    # ── ④ src3119 → 같은 논문의 올바른 DOI 출처 ────────────────────────────
    (("journal", "10.1021/acsomega.9b00825",
      "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6644085/fullTextXML",
      "Cooper et al., Control of Singlet Emission Energy in a Diphenyloxadiazole Containing "
      "Fluorophore Leading To Thermally Activated Delayed Fluorescence"),
     ("journal", "10.1021/acsomega.8b01979",
      "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC6644085/fullTextXML",
      "Cooper et al., Control of Singlet Emission Energy in a Diphenyloxadiazole Containing "
      "Fluorophore Leading To Thermally Activated Delayed Fluorescence, ACS Omega 3 (2018), "
      "Table 1 (columns 'phi_fl', 'tau_PF /ns', 'tau_DF /us') and body text"),
     None, None,
     "옛 출처의 DOI `10.1021/acsomega.9b00825` 는 리포솜 나노베시클 논문이다(Crossref). "
     "참값 `…8b01979` 를 가진 출처가 이미 있고 URL 도 같은 PMC6644085 fullTextXML 이다. "
     "53차 OA 가 *'남길 쪽 제목이 Table 1 을 지목해서 합치면 옮긴 행이 Table 1 에서 왔다고 "
     "주장하게 된다'* 며 의심에 남겼는데, 그 1행의 notes 가 "
     "*'Table 1 …, 열 머리글 tau_PF^e/ns = 7.0'* 이라 **그 표 그 열이 맞다**"),
]


def _load(cond) -> dict:
    try:
        d = json.loads(cond) if cond else {}
    except (TypeError, ValueError):
        d = {}
    return d if isinstance(d, dict) else {}


def _dump(d) -> str:
    return json.dumps(d, ensure_ascii=False)


def _find_source(conn, handle):
    """`(kind, doi, url, title)` 로 출처 한 행을 찾는다. **유일하지 않으면 None**(§536)."""
    kind, doi, url, title = handle
    rows = conn.execute(sa.text(
        "select id from source where kind = :k and doi is :d and url is :u and title is :t"),
        {"k": kind, "d": doi, "u": url, "t": title}).fetchall()
    return rows[0][0] if len(rows) == 1 else None


def _find_material(conn, name):
    rows = conn.execute(sa.text("select id from material where name = :n"),
                        {"n": name}).fetchall()
    return rows[0][0] if len(rows) == 1 else None


def _natural_key(conn, sid: int) -> dict:
    row = conn.execute(sa.text(
        "select " + ", ".join(NATURAL_KEY) + " from source where id = :i"), {"i": sid}).fetchone()
    return dict(zip(NATURAL_KEY, row))


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if not insp.has_table("source") or not insp.has_table("property_value"):
        return
    for old_h, new_h, mat_name, key, reason in PLAN:
        old = _find_source(conn, old_h)
        new = _find_source(conn, new_h)
        if old is None or new is None or old == new:
            continue                    # 옛 리비전 운영 DB — 이 출처가 아직 없다
        where = ["source_id = :s"]
        args: dict = {"s": old}
        if mat_name is not None:
            mid = _find_material(conn, mat_name)
            if mid is None:
                continue                # 재료가 없거나 이름이 유일하지 않다 — 손대지 않는다
            where.append("material_id = :m")
            args["m"] = mid
        if key is not None:
            where.append("property_key = :k")
            args["k"] = key
        marker = _natural_key(conn, old)
        for pid, cond in conn.execute(sa.text(
                "select id, conditions from property_value where " + " and ".join(where)),
                args).fetchall():
            d = _load(cond)
            prev = d.get(MARK)
            note = f"[{BY} {MOVED_AT}] {reason}"
            if isinstance(prev, dict):
                # **§573 — 앞 이동의 사유를 지우지 말고 이 사유 문장 안에 담는다.**
                # 칸을 새로 만들면 행마다 조건 수가 달라져 §548 을 못 지킨다.
                if prev.get("title") == marker.get("title") and prev.get("url") == marker.get("url"):
                    continue            # 멱등 — 이미 이 이동을 했다
                note += f". 앞선 이동: {prev.get('note') or '(사유 없음)'}"
            m = dict(marker)
            m["note"] = note
            # **바꾸는 조건 칸에는 되돌리기 표시를 남긴다**(§521). 앞 파동이 이 표시를 안 남긴 것은
            # 그때는 칸을 **새로** 달았기 때문이고(되돌릴 옛 값이 없다), 이 배치는 **이미 있는 칸을
            # 덮어쓴다.** 표시가 없으면 병합기의 정정 전파(③)가 운영행을 못 찾는다 —
            # `prior_conditions` 가 조건을 정정 전으로 되돌려 대조하는데, 이 칸만 되돌려지지 않아
            # 사전이 언제나 어긋난다. 값으로 안 갈리는 행(같은 재료·키에 같은 값이 둘)에서 실제로
            # 걸렸다: 실측 4행(재료2390 의 4.0 J 둘 · 2420 의 23.2 J 둘)이 miss 였고,
            # 이 표시를 남기니 0 이 됐다. `null` 은 "정정 전에는 이 칸이 없었다" 는 뜻이다(§558 ②).
            d[MARK + "_before_correction"] = prev if isinstance(prev, dict) else None
            d[MARK] = m                 # 기존 칸은 순서까지 그대로 두고 표시만 갱신한다
            conn.execute(sa.text(
                "update property_value set source_id = :n, conditions = :c where id = :i"),
                {"n": new, "c": _dump(d), "i": pid})
        # **옛 출처 행은 지우지 않는다**(§565). 참조가 0 이 될 뿐이다.


def downgrade() -> None:
    """표시가 가리키는 옛 출처로 되돌린다 — **행을 지우지 않는다.**

    이 배치의 표시만 되돌린다(`note` 가 `[54차 PB …]` 로 시작하는 것). 앞선 이동의 표시는
    사유 문장 안에만 있어 복원할 수 없으므로, 되돌린 뒤 표시를 지우지 않고 **앞 이동의
    사유를 남긴 채** 옛 출처를 가리키게 둔다 — 53차 OA 의 되돌리기가 그 다음을 맡는다.
    """
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    for pid, cond in conn.execute(sa.text(
            "select id, conditions from property_value where conditions like :p"),
            {"p": '%"' + MARK + '"%'}).fetchall():
        d = _load(cond)
        m = d.get(MARK)
        if not isinstance(m, dict) or not str(m.get("note", "")).startswith(f"[{BY} "):
            continue
        rows = conn.execute(sa.text(
            "select id from source where "
            + " and ".join(f"{c} is :{c}" for c in NATURAL_KEY)),
            {c: m.get(c) for c in NATURAL_KEY}).fetchall()
        if len(rows) != 1:
            continue                    # 옛 출처를 특정 못 하면 손대지 않는다
        # 되돌리기 표시가 **옛 값 그 자체**라 앞 이동의 표시까지 정확히 복원된다.
        prev = d.pop(MARK + "_before_correction", None)
        if isinstance(prev, dict):
            d[MARK] = prev
        else:
            d.pop(MARK, None)
        conn.execute(sa.text(
            "update property_value set source_id = :s, conditions = :c where id = :i"),
            {"s": rows[0][0], "c": _dump(d) if d else None, "i": pid})
