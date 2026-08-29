"""53차 OA — 확실한 중복 **출처행** 20군을 합친다. 한 행도 지우지 않는다(§565).

§568 이 낸 자리다. 값 중복 검출의 묶음 키에 `source_id` 가 들어 있어서, **같은 시트가 출처
두 행으로 들어오면 중복 검출이 통째로 눈을 감는다.** 그래서 값보다 출처가 앞이다.

## 인계 검증(§479·505 — 인계는 언제나 검증 대상이다)

조정자의 실측 셋을 그대로 재현했다 — **셋 다 맞다.**

| 지문 | 인계 | 재측 |
|---|---|---|
| URL 전문 동일 | 7군 · 출처 14행 · 물성값 110 | 같다 |
| DOI 동일 | 3군 · 출처 6행 · 물성값 10 | 같다 |
| 정규화 제목 동일 | 26군 · 출처 52행 · 물성값 621 | 같다 |

**그런데 가장 큰 것으로 지목된 Uddeholm Dievar 쌍의 '92 + 96' 은 다시 읽어야 한다.**
src4593 의 96행은 Dievar 만이 아니라 **Corrax 6 · Impax Supreme 12 · Orvar Supreme 10 ·
Unimax 10 · Vidar Superior 22 · Dievar 36** 이다. 출처 **행**으로서는 4571 과 같은 문서다
(같은 `local_path`, 제목에 판까지 같다) — 그래서 합친다. 하지만 **60행은 다른 제품 시트의
값이 Dievar 시트를 인용하고 있다**. 이건 출처 중복이 아니라 별개 결함이고, 이 배치는
값을 한 칸도 안 고치므로 `docs/source_duplicates.json` 에 적어 넘긴다.
(합친 뒤에도 `conditions.moved_from_source` 로 그 60행을 그대로 짚을 수 있다.)

## 지문을 여럿 썼고, 하나는 혼자서 못 쓴다는 것을 실측으로 확인했다

```
DOI(대소문자 무시)      3군 ·   6행 ·   10값
URL 전문(쿼리 유지)      7군 ·  14행 ·  110값
정규화 제목             26군 ·  52행 ·  621값
content_hash            0군           ← 라이브 2,943행 **전부 NULL** 이라 지문이 못 된다
local_path + 제목        5군 ·  10행 ·  222값
제목+연도+발행처         17군 ·  34행 ·  295값
벤더 문서번호(EI/QE)      5군 ·  12행 ·  143값   ← 새로 판 지문
local_path 단독          6군 ·  65행 · 1860값   ← **오탐이다. 쓰지 마라**
```

`local_path` 단독이 왜 안 되나 — Doosan CCL 편찬 PDF **한 경로가 55개 제품 페이지 출처에
찍혀 있다.** 제품이 다르면 다른 문헌이다(§426). 그래서 `local_path + 정규화 제목` 으로만 쓴다.

## 부류 셋으로 갈랐다 — 손확인 결과

**확실 20군 · 출처 21행 · 물성값 193(여기서 합친다)** · **의심 23군(표시만, `docs/source_duplicates.json`)** ·
**정당하게 다른 문헌 25쌍 이상(건드리지 않는다)**.

갈라낸 축 — **판(edition)·등급·발표가 다르면 다른 문헌이다**(§426·196).

- **Andersson 3655/4493 은 합치지 않았다.** 값 12행이 자릿수까지 같고 `local_path` 도 같아서
  가장 확실해 보였는데, Crossref 로 두 DOI 를 다 열어 보니 **둘 다 실재하는 별개 문헌**이다 —
  `10.1016/j.msea.2004.10.043`(MSEA 2005)와 `10.1109/eptc.2003.1298763`(ICEPT 2003),
  저자 동일. **§196 그대로다.** 같은 표가 두 번 실렸을 뿐이고, 값이 같은 것은 §456 의
  "출처가 달라도 계보가 하나" 이지 출처 중복이 아니다.
- **Doosan 등급 접미**(DS-7409HG 대 (FQ)/(FU)/(IQ)/(KNF)/(LE)/(X)/(Z)/(ZL)/(ZS)/(ZU),
  DS-7402BS (DF)/(DFM), DS-7409DJG/(N), DS-7409DV (C)/(N), RAPIDON-10W/(N)) · **SCHOTT
  BG60/BG61** · **Corning Gorilla Glass Victus / Victus 2 / Glass 3** · **EMC EM-370(Z)/(5)** ·
  **Norland NOA 61/65** · **ATHAS poly(methyl)/poly(ethyl) acrylate** · **AccuDyne 폴리머별 5종**
  — 제목이 거의 같지만 다른 제품이다.
- **DuPont Kapton Summary of Properties(EI-10142) 세 행은 합치지 않았다.** 문서번호가 같은데도
  뺀 이유가 §426 이 아니다 — **그 문서 안의 '어느 표인가' 가 제목에만 있고 `conditions` 에는
  없다.** (3077 = Table 10 · 3227 = Table 2/3 · 3257 = Typical Thermal Properties)
  합치면 그 축이 사라진다. `docs/value_duplicates.json` 이 *"source_table·figure 를 주석으로
  취급하면 안 된다"* 고 못박은 바로 그 축이다.
- **ACS Omega Cooper 2875/3119 도 같은 이유로 뺐다.** URL 이 글자까지 같고(EuropePMC
  PMC6644085 fullTextXML) 3119 의 DOI 가 다른 논문이라 확실로 올릴 뻔했는데, 남길 쪽 제목이
  `Table 1 (columns 'phi_fl', 'tau_PF /ns', 'tau_DF /us') and body text` 로 **표를 지목**한다.
  합치면 3119 의 1행이 "Table 1 에서 왔다" 고 주장하게 된다 — 그건 우리가 만든 좁힘이다.

## 반대로, 판이 같다는 것을 **증명한** 지문이 새로 생겼다 — 벤더 문서번호

DuPont 은 Qnity 분사 뒤 같은 시트를 `EI-#####` 와 `QE-#####` 두 번호로 낸다. 번호가 같으면
같은 시트다 — 10172(EI/QE) · 10206(EI/QE) · 10207(EI/QE) 세 쌍이 그렇다. src1740 의 제목은
**스스로 `(EI-10172 / QE-10172)` 라고 두 번호를 적어 두었다.** §426 이 "판이 다르면 다른
문헌" 이라고 한 것의 뒷면이다 — **번호가 같으면 같은 문헌이다.**

## 틀린 DOI 다섯을 Crossref 로 잡았다(§15·108 의 출처판)

제목이 글자까지 같은데 DOI 가 다른 군이 여섯 있었다. 전부 열어 보니 **하나만 실재 별개 문헌**
(위 Andersson)이고 나머지 다섯은 **한쪽 DOI 가 엉뚱한 논문**이었다.

| 출처 | 적혀 있던 DOI | Crossref 가 돌려준 것 |
|---|---|---|
| src3280 | `10.3390/ma15103880` | **없는 DOI** (참은 `ma15113880`, 같은 PMC9181996) |
| src2779 | `10.3390/ma15207112` | 폐폴리에스터 활성탄 논문 (참은 `ma15207047`) |
| src3119 | `10.1021/acsomega.9b00825` | 리포솜 나노베시클 논문 (참은 `8b01979`) · **의심으로 남겼다**(아래) |
| src4419 | `10.1016/j.jallcom.2021.160204` | Pt/a-Ta2O5/TiN 저항변화 논문 (참은 `j.est.2021.102302`) |
| src273 | `10.1016/j.eurpolymj.2007.06.017` | 비닐 공중합체 논문 (참은 `2007.04.039`) |

**DOI 가 다르다고 다른 문헌이라고 단정하면 안 된다** — 확인해야 한다. `docs/source_duplicates.json`
의 옛 판(`제목이 같다고 같은 논문이 아니다`)이 src3/273 을 그 이유로 남겨 두었는데,
DOI 를 열어 보니 반대였다. **틀린 DOI 는 이 마이그레이션이 고치지 않는다**(값도 출처 메타도
건드리지 않는다 — 합칠 행은 그대로 남기고 참조만 옮긴다). 넘긴다.

## 규약 — §535 의 묘비를 출처에 **그대로는** 못 쓴다

§535 는 재료에서 *"판정 키에 id 를 적지 마라, 자연키(이름)를 적어라"* 였다. 출처에는 이름이 없다.
**병합기의 출처 자연키 `[kind, doi, isbn, url, title, publisher, license]` 가 그 자리다** —
라이브 2,943행에서 **2,943/2,943 완전 유일**이라 지문으로 쓸 수 있다(실측).

**그런데 묘비 자체는 출처 행에 못 세운다.** `source` 에는 `attributes` 같은 JSON 칸이 없고,
병합기는 자연키로 걸린 운영 행을 **그대로 둔다**(재료 `attributes`·장비 소유권만 예외).
즉 —
- 자연키 **밖** 칸(`authors`·`year`·`local_path`…)에 적으면 **운영에 영원히 안 간다**(§464).
- 자연키 **안** 칸(`title`…)에 적으면 **운영에 새 출처 행이 생긴다**(§522·536 의 얼굴).

→ 그래서 계보는 **옮긴 값 쪽에 남긴다.** `conditions.moved_from_source` 에 옛 출처의 자연키를
통째로 적는다. 이건 §536 의 `moved_from_material` 과 같은 모양이고 같은 이유다.
합칠 출처 행은 **지우지 않는다**(§565) — 참조가 0 이 될 뿐이다(라이브 4행 → 25행).

## 병합기를 고쳐야 했다 — `source_id` 재매핑만으로는 안 된다(예행으로 확인)

`property_value` 자연키에 `source_id` 가 있다. 이동이 바꾸는 칸이 바로 그것이다 —
§536 이 `material_id` 에서 만난 것의 **다섯 번째 얼굴**이다. 실측 예행 —

```
src=라이브(병합 후) 대 dst=병합 직전 백업(pre-w53oa-20260829-025038Z)
  고치기 전  property_value added **181** · correction_misses **65**
  고친 뒤    added 0 · matched 41383 · source_moves 103 · value_corrections 90
             · correction_misses 0 · verdict_misses 0 · source_move_misses 0 · fk_violations 0
  재병합     added 0 · source_moves 0          ← 자연키가 먼저라 멱등하다
```
(`source_moves` 와 `value_corrections` 의 갈림은 그 행이 정정을 함께 선언했는지에 달렸다 —
합은 언제나 옮긴 193행이다.)

`_materialtwin_merge.py` 에 분기 ⑤(`moved_from_source`)를 넣어 닫았다. 조회축 치환(②-c)도
같이 필요했다 — 옮긴 193행 중 **78행이 정정을, 9행이 판정을 함께 달고 있어서**
③·②-b 가 새 `source_id` 로 찾으면 전부 miss 로 뜬다.

## 대표값 — 표시 한 칸이 20군을 뒤집는다(§548 의 출처판, 고쳤다)

`_rep_rank` 5번째 자리가 조건 수라 **표시 한 칸이 순위를 바꾼다.** 실측 —

```
표시만 얹고 규칙 그대로   대표 변동 20군 · 그중 **값까지 바뀌는 것 6군**
                        (Zeonex 굴곡강도 120 → 115 MPa · 굴곡탄성률 2.40 → 2.24 GPa 등)
`moved_from_*` 를 조건 수에서 뺀 뒤  이동 전 라이브 변동 0군 · 표시 193행 얹어도 변동 0군
```

§563 이 값 중복군에서 "한쪽에만 더한다" 로 푼 길은 여기서 못 쓴다 — 옮기는 193행은 중복군이
아니라 DB 전역에 흩어져 있다. **표시는 조건이 아니다** 를 `catalog_compare._NOT_A_CONDITION`
에 박는 것이 옳은 길이고, `moved_from_material` 도 같이 넣었다(지금까지 2행뿐이라 안 드러났다).

Revision ID: d5e6f7a8b9c0
Revises: c7d8e9f0a1b2
"""
from __future__ import annotations

import json

import sqlalchemy as sa
from alembic import op

revision = "d5e6f7a8b9c0"
down_revision = "c7d8e9f0a1b2"
branch_labels = None
depends_on = None

MARK = "moved_from_source"
MOVED_AT = "2026-08-29"

# 병합기(`_materialtwin_merge.PLAN`)의 출처 자연키. 표시에 **전 칸을 다 적는다** —
# 빠진 칸을 "아무 값이나" 로 읽으면 운영에서 다른 출처를 잡는다.
NATURAL_KEY = ("kind", "doi", "isbn", "url", "title", "publisher", "license")

# 계획의 손잡이는 `(kind, doi, url, title)` 이다. 라이브 2,943행에서 **2,943/2,943 유일**이고,
# `(kind, title, url)` 만으로는 CoMn2O4 두 행이 겹친다(그 군이 바로 아래 계획에 있다).
# **여러 행이 걸리면 그 군은 통째로 건너뛴다** — 병합기가 고르면 그건 병합기의 판정이다(§536).
#
# (남길 출처, [합칠 출처…], 사유). 출처는 (kind, doi, url, title).
_UD = "Uddeholm Dievar — product datasheet, Edition 15 (10.2025)"
_QN = ("https://www.qnityelectronics.com/content/dam/electronics/amer/us/en/"
       "electronics/public/documents/en/")
_IOFFE = "https://www.ioffe.ru/SVA/NSM/Semicond/"
_ZEONEX = ("High Performance Optical Materials Cyclo Olefin Polymer ZEONEX "
           "(Obuchi et al., Proc. SPIE 6671, {}2007)")

PLAN: list[tuple[tuple, list[tuple], str]] = [
    (("datasheet", None,
      "https://www.uddeholm.com/app/uploads/sites/216/productdb/api/tech_uddeholm-dievar_en.pdf",
      _UD),
     [("datasheet", None, "https://www.uddeholm.com/", _UD)],
     "같은 local_path(Uddeholm_Dievar_Tech_Ed15_2025-10.pdf) · 제목에 판(Edition 15, 10.2025)"
     "까지 동일 · year·authors 동일. 합칠 쪽은 url 이 벤더 최상위이고 publisher 가 비어 있다"),

    (("datasheet", None, _QN + "QE-10172-Kapton-EN-A,EN-CandEN-ZData-Sheet.pdf",
      "Kapton® EN-A, EN-C and EN-Z Polyimide Film — Technical Data Sheet (QE-10172)"),
     [("datasheet", None, _QN + "EI-10172-Kapton-EN-A-C-Z-Data-Sheet.pdf",
       "DuPont™ Kapton® EN-A, EN-C and EN-Z Polyimide Film — Data Sheet (EI-10172 / QE-10172)")],
     "DuPont 문서번호 EI-10172 = QE-10172 — 합칠 행의 제목이 스스로 두 번호를 함께 선언한다. "
     "§568 이 지목한 Kapton 150EN-A pv3172 의 출처 갈림이 바로 이 쌍이다"),

    (("datasheet", None, _QN + "QE-10206-Kapton-HN-Data-Sheet.pdf",
      "DuPont Kapton HN Polyimide Film Technical Data Sheet (QE-10206)"),
     [("datasheet", None, _QN + "EI-10206-Kapton-HN-Data-Sheet.pdf",
       "DuPont Kapton HN Polyimide Film — Technical Data Sheet (EI-10206)")],
     "DuPont 문서번호 QE-10206 = EI-10206 · 같은 qnity 경로의 같은 시트"),

    (("datasheet", None,
      "https://www.pp.qnityelectronics.com/content/dam/electronics/amer/us/en/electronics/"
      "public/documents/en/EI-10207-Kapton-HPP-ST-Data-Sheet.pdf",
      "DuPont™ Kapton® HPP-ST Polyimide Film — Data Sheet (EI-10207 / QE-10207)"),
     [("datasheet", None, _QN + "EI-10207-Kapton-HPP-ST-Data-Sheet.pdf",
       "Kapton® HPP-ST Polyimide Film — Technical Data Sheet (QE-10207, 04/26)")],
     "문서번호 EI-10207 / QE-10207 · **URL 파일명이 같다**(EI-10207-Kapton-HPP-ST-Data-Sheet.pdf), "
     "서브도메인만 pp. 가 붙고 안 붙는다"),

    (("datasheet", None,
      "https://www.qnityelectronics.com/content/dam/electronics/amer/us/en/electronics/"
      "public/documents/en/EI-10118-Pyralux-LF-CL-Data-Sheet.pdf",
      "DuPont Pyralux LF Acrylic-Based Coverlay - Flexible Circuit Materials data sheet (EI-10118)"),
     [("datasheet", None,
       "https://insulectro.com/wp-content/uploads/2021/09/EI-10118-Pyralux-LF-CL-Data-Sheet.pdf",
       "DuPont Pyralux LF Acrylic-Based Coverlay Flexible Circuit Materials Data Sheet (EI-10118)")],
     "문서번호 EI-10118 · **URL 파일명이 같다**(EI-10118-Pyralux-LF-CL-Data-Sheet.pdf). "
     "남기는 쪽이 벤더 자기 호스트다"),

    (("journal", "10.3390/ma15113880", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9181996/",
      "Numerical Simulation Study on Factors Influencing Anti-Explosion Performance of Steel "
      "Structure Protective Doors under Chemical Explosion Conditions"),
     [("journal", "10.3390/ma15103880",
       "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9181996/fullTextXML",
       "Numerical Simulation Study on Factors Influencing Anti-Explosion Performance of Steel "
       "Structure Protective Doors under Chemical Explosion Conditions")],
     "같은 PMC9181996(EuropePMC 가 이 PMC 의 DOI 로 ma15113880 을 돌려준다) · "
     "합칠 쪽 DOI `10.3390/ma15103880` 은 **Crossref 에 없는 DOI** 다"),

    (("journal", "10.3390/ma15207047",
      "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9605540/fullTextXML",
      "Influence of Loading Directions on Dynamic Compressive Properties of Mill-Annealed "
      "Ti-6Al-4V Thick Plate"),
     [("journal", "10.3390/ma15207112", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9605540/",
       "Influence of Loading Directions on Dynamic Compressive Properties of Mill-Annealed "
       "Ti-6Al-4V Thick Plate")],
     "같은 PMC9605540 · 합칠 쪽 DOI `10.3390/ma15207112` 는 **다른 논문**"
     "(폐폴리에스터 활성탄 열분해·흡착)이다"),

    (("journal", "10.3390/polym12102327",
      "https://res.mdpi.com/d_attachment/polymers/polymers-12-02327/article_deploy/"
      "polymers-12-02327.pdf",
      "Reliability-Based Evaluation of the Suitability of Polymers for Additive Manufacturing "
      "Intended to Injection Molding — Table 4 'Analysis of parameters related to materials "
      "processability [48,56-67]'"),
     [("other", None,
       "https://res.mdpi.com/d_attachment/polymers/polymers-12-02327/article_deploy/"
       "polymers-12-02327.pdf",
       "Reliability-Based Evaluation of the Suitability of Polymers for Additive Manufacturing "
       "Intended to Injection Molding — Table 4 'Analysis of parameters related to materials "
       "processability [48,56-67]'")],
     "URL 전문 동일 · 제목도 표 이름까지 동일 · 합칠 쪽은 kind 가 other 이고 DOI 가 없다"),

    (("journal", "10.3390/ma18102261", "https://doi.org/10.3390/ma18102261",
      "Probing Phase Transitions and Interfacial Reorganization in TAPC/CBP/BPhen Organic "
      "Light-Emitting Diode Stacks by In Situ Ellipsometry"),
     [("database", None, "https://doi.org/10.3390/ma18102261",
       "Probing Phase Transitions in TAPC/CBP/BPhen OLED Stacks by In Situ Ellipsometry")],
     "URL 전문 동일(같은 DOI 링크) · 합칠 쪽은 제목 축약본이고 DOI 칸이 비어 있다"),

    (("journal", "10.1109/JMEMS.2009.2039697", "https://doi.org/10.1109/JMEMS.2009.2039697",
      "What is the Young's Modulus of Silicon?"),
     [("database", None, "https://ieeexplore.ieee.org/document/5430873",
       "What is the Young's Modulus of Silicon?")],
     "Crossref 가 이 DOI 의 전문 링크로 `arnumber=5430873` 을 명시한다 = 합칠 쪽의 "
     "ieeexplore/document/5430873. 제목도 동일"),

    (("journal", "10.1117/12.749910", "https://doi.org/10.1117/12.749910",
      _ZEONEX.format("66711I, ")),
     [("datasheet", None, None, _ZEONEX.format("66711I, ")),
      ("datasheet", None, None, _ZEONEX.format(""))],
     "제목이 인용문 그대로다(Obuchi et al., Proc. SPIE 6671, 66711I, 2007) · 합칠 두 행은 "
     "DOI·URL·local_path 가 **전무**하다(§185 의 '식별자가 하나도 없을 때만 제목으로 합친다')"),

    (("journal", "10.1016/j.est.2021.102302", None,
      "CoMn2O4 Nanoparticles Decorated on 2D MoS2 Frame: A Synergetic Energy Storage Composite "
      "Material for Sustainable Supercapacitor Application"),
     [("journal", "10.1016/j.jallcom.2021.160204", None,
       "CoMn2O4 Nanoparticles Decorated on 2D MoS2 Frame: A Synergetic Energy Storage Composite "
       "Material for Sustainable Supercapacitor Application")],
     "제목 verbatim 동일 · 합칠 쪽 DOI 는 **다른 논문**(Pt/a-Ta2O5/TiN 저항변화 소자)이다. "
     "값도 같은 세 시료의 서로 다른 물성(격자상수·기공 대 BET·기공부피)이라 상보적이다"),

    (("journal", "10.1016/j.eurpolymj.2007.04.039", None,
      "Preparation and properties of a high temperature, flexible and colorless ITO coated "
      "polyimide substrate"),
     [("journal", "10.1016/j.eurpolymj.2007.06.017",
       "https://doi.org/10.1016/j.eurpolymj.2007.06.017",
       "Preparation and properties of a high temperature, flexible and colorless ITO coated "
       "polyimide substrate (Li 2007)")],
     "제목 동일 · 합칠 쪽 DOI 는 **다른 논문**(N-비닐프탈이미드 공중합체, Chikhaoui-Grioune)이다. "
     "옛 `docs/source_duplicates.json` 이 'DOI 가 다르니 다른 논문' 으로 남겨 둔 쌍인데 "
     "열어 보니 반대였다"),

    (("datasheet", None,
      "https://www.nitto.com/us/en/others/products/file/datasheet/NBE_SWT_10+R_EN.pdf",
      "Nitto Semiconductor Wafer Processing Tape SWT 10+R datasheet (Jan 2019)"),
     [("datasheet", None,
       "https://www-origin.nitto.com/us/en/others/products/file/datasheet/NBE_SWT_10+R_EN.pdf",
       "Nitto Semiconductor Wafer Processing Tape SWT 10+R datasheet (Jan 2019)")],
     "URL 이 `www` / `www-origin` 서브도메인만 다르다(경로·파일명 동일) · 제목에 판(Jan 2019)까지 동일"),

    (("database", None, "https://www.ioffe.ru/SVA/NSM/Semicond/AlN/mechanic.html",
      "NSM Archive - Aluminium Nitride (AlN) - Mechanical properties"),
     [("database", None, "http://www.ioffe.ru/SVA/NSM/Semicond/AlN/mechanic.html",
       "Aluminium Nitride (AlN) - Mechanical properties, elastic constants, lattice vibrations "
       "(Ioffe Institute NSM Archive)")],
     "URL 이 http/https 만 다른 같은 페이지다"),

    (("database", None, _IOFFE + "Si/mechanic.html",
      "NSM Archive - Silicon (Si) - Mechanical properties"),
     [("database", None, "http://www.ioffe.ru/SVA/NSM/Semicond/Si/mechanic.html",
       "Silicon - Mechanical properties, elastic constants, lattice vibrations "
       "(Ioffe Institute NSM Archive)")],
     "URL 이 http/https 만 다른 같은 페이지다"),

    (("database", None, "http://www.ioffe.ru/SVA/NSM/Semicond/GaAs/basic.html",
      "GaAs - Basic Parameters at 300 K (NSM Archive)"),
     [("book", None, _IOFFE + "GaAs/basic.html",
       "NSM Archive - Gallium Arsenide (GaAs) - Basic Parameters")],
     "URL 이 http/https 만 다른 같은 페이지다. 남기는 쪽이 kind=database 이고 publisher 가 차 있다 "
     "— 합칠 쪽은 kind 가 book 으로 잘못 적혀 있다"),

    (("journal", "10.1007/BF02692566", "https://doi.org/10.1007/BF02692566",
      "Creep-constitutive behavior of Sn-3.8Ag-0.7Cu solder using an internal stress approach"),
     [("journal", "10.1007/bf02692566", "https://doi.org/10.1007/bf02692566",
       "Creep-constitutive behavior of Sn-3.8Ag-0.7Cu solder using an internal stress approach")],
     "DOI 가 대소문자만 다르다 — DOI 는 규격상 대소문자를 구분하지 않는다 · local_path 동일"),

    (("journal", "10.4028/www.scientific.net/MSF.926.73",
      "https://doi.org/10.4028/www.scientific.net/MSF.926.73",
      "Parylene-Coated Cellulose Nanofiber Films with Improved Oxygen Barrier and Water Resistance"),
     [("journal", "10.4028/www.scientific.net/msf.926.73", None,
       "Parylene-Coated Cellulose Nanofiber Films with Improved Oxygen Barrier and Water "
       "Resistance")],
     "DOI 가 대소문자만 다르다 · local_path 동일"),

    (("journal", "10.1007/BF01133338", "https://doi.org/10.1007/BF01133338",
      "Creep-fatigue interaction in eutectic lead-tin solder alloy"),
     [("journal", "10.1007/bf01133338", None,
       "Creep-fatigue interaction in eutectic lead-tin solder alloy")],
     "DOI 가 대소문자만 다르다 · local_path 동일"),
]


def _load(cond) -> dict:
    try:
        d = json.loads(cond) if cond else {}
    except (TypeError, ValueError):
        d = {}
    return d if isinstance(d, dict) else {}


def _dump(d) -> str:
    return json.dumps(d, ensure_ascii=False)


def _find(conn, handle) -> tuple | None:
    """`(kind, doi, url, title)` 로 출처 한 행을 찾는다. **유일하지 않으면 None**(§536)."""
    kind, doi, url, title = handle
    rows = conn.execute(sa.text(
        "select id from source where kind = :k and doi is :d and url is :u and title is :t"),
        {"k": kind, "d": doi, "u": url, "t": title}).fetchall()
    return rows[0] if len(rows) == 1 else None


def _natural_key(conn, sid: int) -> dict:
    row = conn.execute(sa.text(
        "select " + ", ".join(NATURAL_KEY) + " from source where id = :i"), {"i": sid}).fetchone()
    return dict(zip(NATURAL_KEY, row))


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if not insp.has_table("source") or not insp.has_table("property_value"):
        return
    has_instrument = insp.has_table("instrument")
    for keep_h, drop_hs, reason in PLAN:
        keep = _find(conn, keep_h)
        if not keep:
            continue                    # 옛 리비전 운영 DB — 이 출처가 아직 없다
        for drop_h in drop_hs:
            drop = _find(conn, drop_h)
            if not drop or drop[0] == keep[0]:
                continue
            marker = _natural_key(conn, drop[0])
            marker["note"] = f"[53차 OA {MOVED_AT}] {reason}"
            for pid, cond in conn.execute(sa.text(
                    "select id, conditions from property_value where source_id = :s"),
                    {"s": drop[0]}).fetchall():
                d = _load(cond)
                if MARK in d:
                    continue            # 멱등 — 이미 옮겼다
                d[MARK] = marker        # 기존 칸은 순서까지 그대로 두고 표시만 뒤에 붙인다
                conn.execute(sa.text(
                    "update property_value set source_id = :k, conditions = :c where id = :i"),
                    {"k": keep[0], "c": _dump(d), "i": pid})
            # 장비 참조 — 라이브 실측 0건이지만 표를 놓치면 FK 계보가 끊긴다(병합기 머리말의 교훈).
            if has_instrument:
                conn.execute(sa.text(
                    "update instrument set source_id = :k where source_id = :d"),
                    {"k": keep[0], "d": drop[0]})
            # **합칠 출처 행은 지우지 않는다**(§565). 참조가 0 이 될 뿐이다.


def downgrade() -> None:
    """표시가 남아 있는 행만 되돌린다 — **행을 지우지 않는다.**"""
    conn = op.get_bind()
    if not sa.inspect(conn).has_table("property_value"):
        return
    for pid, cond in conn.execute(sa.text(
            "select id, conditions from property_value where conditions like :p"),
            {"p": '%"' + MARK + '"%'}).fetchall():
        d = _load(cond)
        marker = d.get(MARK)
        if not isinstance(marker, dict):
            continue
        rows = conn.execute(sa.text(
            "select id from source where "
            + " and ".join(f"{c} is :{c}" for c in NATURAL_KEY)),
            {c: marker.get(c) for c in NATURAL_KEY}).fetchall()
        if len(rows) != 1:
            continue                    # 옛 출처를 특정 못 하면 손대지 않는다
        d.pop(MARK, None)
        conn.execute(sa.text(
            "update property_value set source_id = :s, conditions = :c where id = :i"),
            {"s": rows[0][0], "c": _dump(d) if d else None, "i": pid})
