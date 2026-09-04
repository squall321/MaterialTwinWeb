# 63차 YC — 표적 (2) 출처 제목이 실제보다 강해 보이는 자리

`integrity_check.py` 의 주의 **「식별자가 제목뿐이라 다시 열 수 없는 출처: 91건 · 값 1,736행」**
을 전수로 훑어 셋으로 갈랐다. 재현 질의는 검사기와 같다.

```sql
select s.id, s.title, count(v.id) n, min(v.quality_tier)
  from source s join property_value v on v.source_id = s.id
 where coalesce(s.doi,'')='' and coalesce(s.url,'')='' and coalesce(s.local_path,'')=''
 group by s.id order by n desc;      -- 91건 · 1,736행
```

## 0. 먼저 전체 그림 — 이 91건은 '핸드북' 이 아니라 **가정값의 창고**다

| 갈래 | 출처 | 값행 | t1 | t2 | t3 | **t4** | `assumption:true` |
|---|---:|---:|---:|---:|---:|---:|---:|
| **A 정당한 참고문헌·규격** | 22 | 1,283 | 0 | 244 | 17 | **1,022** | 1,019 |
| **B 제목·종류를 고쳐야 한다** | 39 | 325 | 55 | 48 | 2 | **220** | 220 |
| **C 출처로 성립하지 않는다** | 30 | 128 | 0 | 7 | 0 | **121** | 121 |
| 계 | **91** | **1,736** | 55 | 299 | 19 | **1,363(78.5%)** | 1,360 |

**§661 이 출처 972 하나에서 본 것이 91건 전체의 성질이다** — 1,736행 중 **1,363행(78.5%)이
t4 가정값**이고 그중 1,360행이 `assumption: true` 다. 즉 이 출처들은 대부분 *"핸드북에서 읽었다"*
가 아니라 *"클래스 기본값을 부으면서 그럴듯한 책 이름을 적었다"* 이고, 다음 파동이
**출처 문자열만 보고 "이미 핸드북 값이 있다" 고 읽어 표적을 놓친다.**

**표적 (1)과 여기서 만난다** — 취성재 파단연신율 t4 **40칸이 전부** 이 91건 안이다
(701 ASM Ceramics & Glasses 31 · 689 CRC 6 · 770 ASM Composites 3).

---

## 1. 갈래 A — 정당하다(제목이 식별자다). **22건 · 1,283행**

핸드북과 규격은 **제목+판이 곧 인용**이라 DOI·URL 이 없는 것 자체는 결함이 아니다.
남는 결함은 **판·권·쪽이 없어 그 값을 다시 찾을 수 없다**는 것이고, 그것은 §598 의 자리다
(*"값이 어느 시트에서 왔는지 행이 스스로 적어 둔다"* — 여기서는 안 적어 두었다).

| 출처 | kind | 값행 | 등급 | 제목(DB 문자열 그대로) |
|---:|---|---:|---|---|
| 853 | book | 391 | t2–t4 | Polymer Handbook (Brandrup, Immergut, Grulke), 4th ed. |
| 701 | book | 192 | t2–t4 | ASM Engineered Materials Handbook — Ceramics and Glasses |
| 760 | book | 148 | t2–t4 | ASM Metals Handbook — Properties and Selection: Nonferrous Alloys and Special-Purpose Materials |
| 770 | book | 136 | t4–t4 | ASM Engineered Materials Handbook — Composites |
| 971 | book | 119 | t4–t4 | Rubber Technology Handbook (Hofmann) |
| 905 | book | 87 | t4–t4 | Handbook of Pressure-Sensitive Adhesive Technology (Satas), 3rd ed. |
| 689 | book | 84 | t2–t4 | CRC Handbook of Chemistry and Physics, 97th ed. |
| 2303 | book | 25 | t2–t4 | Galvanic Series of Metals in Seawater — corrosion potential (volts DC ref. Ag/AgCl), Ref. ABYC |
| 549 | book | 21 | t2–t2 | ASM Handbook Vol.2 — Copper and Copper Alloys |
| 791 | book | 18 | t2–t2 | ASM Metals Handbook — Properties and Selection: Irons, Steels, and High-Performance Alloys |
| 643 | standard | 11 | t2–t4 | IPC-4204 — Flexible Metal-Clad Dielectrics |
| 550 | standard | 10 | t2–t2 | IPC-4562A — Metal Foil for Printed Board Applications |
| 577 | standard | 9 | t2–t2 | IPC-4101 — Base Materials (Laminate/Prepreg) Spec |
| 632 | book | 5 | t2–t2 | ASM Handbook — Precious Metals (Au/Ag) properties |
| 624 | standard | 5 | t2–t4 | IPC-4552B — Electroless Ni/Immersion Au (ENIG) Specification |
| 712 | standard | 5 | t2–t4 | MIL-A-8625F — Anodic Coatings for Aluminum and Aluminum Alloys |
| 660 | standard | 4 | t2–t2 | IPC-4101 base material spec |
| 639 | standard | 4 | t2–t4 | IPC-4555 — Organic Solderability Preservative (OSP) Specification |
| 628 | book | 3 | t2–t2 | ASM Handbook Vol.2 — Nickel, Cobalt and Their Alloys |
| 699 | standard | 3 | t2–t4 | EIA-198 / IEC 60384-21 — Class I (C0G/NP0) Ceramic Dielectric Specification |
| 637 | standard | 2 | t2–t4 | IPC-4553A — Immersion Silver (ImAg) Specification |
| 707 | standard | 1 | t2–t2 | IEC 60115-1 — Fixed resistors for electronic equipment |

**손대지 마라. 채워라.** `source.isbn` 은 자연키 안이지만 **지금 전부 NULL 이라 채우면
자연키가 바뀐다** — 병합기가 새 출처를 만든다(§578·597 과 같은 벽). 그러니 ISBN 은 넣지 말고
**쪽·표 번호는 값 쪽 `conditions.figure`·`source_detail` 에 넣어라**(§598 이 Uddeholm 60행을
다섯 시트로 가른 그 칸이다). 그 칸은 값의 조건이라 정정 경로(③)로 운영까지 간다.

- **701 · 770 · 971 · 905 는 t4 비율이 100% 에 가깝다.** 핸드북을 실제로 열었다면
  쪽 번호가 남았을 것이다. **표적으로 세울 때는 "핸드북 값" 이 아니라 "클래스 가정" 으로 세라**(§660).
- **660 은 577 과 같은 규격(IPC-4101)이 두 줄로 들어와 있다.** 제목 표기만 다르다
  (`IPC-4101 — Base Materials (Laminate/Prepreg) Spec` 대 `IPC-4101 base material spec`).
  **합치지 마라 — 자연키가 바뀐다.** `source_duplicates.py` 의 표본으로 넘긴다.

---

## 2. 갈래 B — 제목·종류를 고쳐야 한다. **39건 · 325행**

실재하는 문서를 가리키는데 **문자열이 그 문서를 특정하지 못한다.** 넷으로 더 갈린다.

| 출처 | kind | 값행 | 등급 | 제목(DB 문자열 그대로) |
|---:|---|---:|---|---|
| 972 | book | 201 | t4–t4 | Handbook of Infrared Radiation — emissivity tables (Touloukian TPRC Data Series) |
| 4513 | other | 12 | t1–t2 | Non-Conductive Films (NCFs) with Multi-Functional Epoxies and Silica Fillers for Reliable Flip Chip on Organic Board Assemblies |
| 588 | book | 6 | t2–t3 | Fiberglass & E-glass properties (Nittobo/AGY handbook) |
| 524 | datasheet | 6 | t1–t1 | DuPont Kapton HN datasheet |
| 174 | database | 6 | t2–t2 | AZoM/MatWeb: Stainless Steel Grade 316L (UNS S31603) |
| 168 | database | 6 | t2–t2 | AZoM/MatWeb: Stainless Steel Grade 316 (UNS S31600) |
| 162 | database | 6 | t2–t2 | AZoM/MatWeb: Stainless Steel Grade 304L (UNS S30403) |
| 156 | database | 6 | t2–t2 | AZoM/MatWeb: Stainless Steel Grade 301 (UNS S30100) |
| 149 | database | 6 | t2–t2 | AZoM/MatWeb: Stainless Steel Grade 201 (UNS S20100) |
| 719 | datasheet | 5 | t1–t1 | Toray Lumirror PET film technical datasheet |
| 676 | datasheet | 5 | t1–t4 | Kuraray Vecstar LCP film datasheet |
| 733 | datasheet | 5 | t1–t4 | Toyo Ink color filter photoresist technical datasheet |
| 740 | datasheet | 5 | t1–t4 | JSR microlens (OCL) photoresist material technical datasheet |
| 229 | datasheet | 4 | t1–t4 | Industrialization and application development of cyclo-olefin polymer (Yamazaki, J. Mol. Catal. A 213 (2004) 81-87) |
| 751 | datasheet | 4 | t1–t4 | Laird conductive fabric-over-foam EMI gasket technical datasheet |
| 755 | datasheet | 4 | t1–t4 | 3M 9871 high-temperature silicone adhesive transfer tape technical data |
| 759 | datasheet | 4 | t1–t4 | 3M removable repositionable adhesive technical data |
| 725 | datasheet | 4 | t1–t4 | Dexerials ACF (anisotropic conductive film) technical datasheet |
| 618 | datasheet | 3 | t1–t1 | Taiyo PSR-4000(DMA) |
| 203 | database | 3 | t2–t2 | M-Film 사양 (Ti 합금 필름) |
| 537 | datasheet | 2 | t1–t1 | UBE Upilex-S datasheet |
| 655 | datasheet | 2 | t1–t1 | Panasonic Megtron 6 (R-5775) datasheet |
| 657 | datasheet | 2 | t1–t1 | Panasonic Megtron 6 datasheet (DSC) |
| 710 | datasheet | 2 | t1–t1 | Murata NCP series NTC thermistor datasheet |
| 729 | datasheet | 2 | t1–t1 | Daikin Optool DSX anti-fingerprint coating datasheet |
| 663 | standard | 1 | t2–t2 | IPC-4101 prepreg gel time (typ. 100–200 s @171℃) |
| 322 | database | 1 | t2–t2 | Temperature-responsive microspheres-coated separator for thermal shutdown protection of lithium ion batteries (Ji 2015) |
| 387 | other | 1 | t4–t4 | Ongayi et al. (2012) High sensitivity chemically amplified EUV resists through enhanced EUV absorption, Proc. SPIE Vol. 8322, 83220T |
| 542 | other | 1 | t3–t3 | BPDA-PDA PI Tg(문헌) |
| 529 | other | 1 | t4–t4 | PMDA-ODA PI Tg (문헌) |
| 535 | datasheet | 1 | t1–t1 | DuPont Kapton HN 25µm |
| 530 | datasheet | 1 | t1–t1 | DuPont Kapton HN(TGA) |
| 543 | datasheet | 1 | t1–t1 | UBE Upilex-S(TGA) |
| 580 | datasheet | 1 | t1–t1 | Shengyi S1000H(DSC) |
| 581 | datasheet | 1 | t1–t1 | Shengyi high-Tg(Td, TGA) |
| 658 | datasheet | 1 | t1–t1 | Panasonic Megtron 6 datasheet (TGA) |
| 696 | datasheet | 1 | t1–t1 | Imerys ENSACO 260G conductive carbon black datasheet |
| 202 | database | 1 | t2–t2 | MatWeb: Titanium Grade 4 (CP), annealed |
| 200 | database | 1 | t2–t2 | MatWeb: Titanium Ti-3Al-2.5V (Grade 9), annealed |

### B-1. 두 문헌을 한 줄에 붙였다 — 2건

- **972 (201행, 전부 t4)** — §661 이 신고한 그것이다. `Handbook of Infrared Radiation` 과
  Touloukian *Thermophysical Properties of Matter* TPRC Data Series 는 **다른 책**이고 권·쪽도 없다.
- **588 (6행)** — `Fiberglass & E-glass properties (Nittobo/AGY handbook)` 은 **두 벤더**를 붙였다.
  §638 이 밝힌 대로 두 벤더는 같은 축을 다르게 찍는다 — 어느 쪽인지 모르면 그 값의 등급을 못 정한다.

### B-2. 논문인데 `kind` 와 식별자가 어긋난다 — 4건

| 출처 | 지금 | 실제 | 할 일 |
|---|---|---|---|
| 4513 | `other`, 식별자 0, **t1 12행** | 논문 제목이 통째로 들어 있다(NCF/flip-chip 신뢰성) | `kind='journal'` + DOI 조회. **t1 12행을 받치는데 다시 못 연다** — 이 91건에서 가장 급하다 |
| 229 | `datasheet` | 제목에 **완전한 인용**이 들어 있다(`Yamazaki, J. Mol. Catal. A 213 (2004) 81-87`) | `kind='journal'` + DOI |
| 322 | `database`, publisher=RSC | 논문(`Ji 2015`) | `kind='journal'` + DOI |
| 387 | `other`, publisher=`Dow Electronic Materials (SPIE)` | `Proc. SPIE 8322, 83220T` — 완전한 인용 | `kind='journal'`/`other` 유지 + DOI |

### B-3. 벤더 시트·DB 페이지인데 URL·판·발행년이 없다 — 30건

- **데이터시트 22건** — 524·719·676·618·537·535·530·543·580·581·655·657·658·696·710·729·733·740·751·755·759·725.
  **t1 이 55행**으로 이 갈래에 몰려 있다. 실재하는 시트이므로 **§626 대로 먼저 코퍼스에
  `ls | grep` 을 걸고**, 없으면 조달해 `local_path`·`url` 을 채워라 — 그 두 칸은 아래 §4 대로
  **자연키 안이라** 채우면 새 출처가 생긴다. **그래서 이 갈래는 "고친다" 가 아니라
  "새 출처로 다시 적재하고 옛 행을 `moved_from_source` 로 옮긴다" 가 옳다**(53차 OA 의 경로).
- **DB 페이지 8건** — AZoM/MatWeb 6 + MatWeb 2 + `M-Film 사양` 1(203, 제목이 한국어 서술이라
  어느 페이지인지 못 찾는다).
- **한 시트가 측정법별로 쪼개져 있다** — `DuPont Kapton HN datasheet`(524) · `DuPont Kapton HN 25µm`(535) ·
  `DuPont Kapton HN(TGA)`(530) 셋이 같은 시트일 공산이 크다. Megtron 6 도 셋(655·657·658),
  Upilex-S 도 둘(537·543), Shengyi 도 둘(580·581). **합치기 전에 §611 을 걸어라** —
  같은 시트의 다른 표일 수도 있다.

### B-4. "문헌" 이라고만 적었다 — 2건

- **542** `BPDA-PDA PI Tg(문헌)` (t3) · **529** `PMDA-ODA PI Tg (문헌)` (t4).
  **제목이 값의 이름 + "(문헌)" 이다.** 어느 문헌인지 없어 t3 의 근거가 없다. 갈래 C 와 갈래 B 의 경계인데,
  *"문헌"* 이라고 주장한 이상 그 문헌을 대야 하므로 B 에 둔다.

### B-5. 규격 + 값이 한 제목에 있다 — 1건

- **663** `IPC-4101 prepreg gel time (typ. 100–200 s @171℃)`. 규격 번호는 식별자인데 **값이 제목에 들어와**
  다른 IPC-4101 행(577·660)과 다른 출처가 됐다. 값은 `conditions` 로 내리고 제목은 규격만 남기는 것이 옳다 —
  **다만 자연키가 바뀐다**(§4).

---

## 3. 갈래 C — 출처로 성립하지 않는다. **30건 · 128행**

**문서가 아니다.** 제목이 우리 판단·클래스 라벨이고, 그중 일곱은 **스스로 그렇다고 적어 두었다**
(`[상한 라벨]`·`[추정 라벨]`·`[범위 라벨] … 측정값이 아니다`).

| 출처 | kind | 값행 | 등급 | 제목(DB 문자열 그대로) |
|---:|---|---:|---|---|
| 1046 | other | 76 | t4–t4 | [상한 라벨] ASTM E595 저아웃가싱 합격기준(TML≤1.0%·CVCM≤0.10%) — 이 재료들의 측정값이 아니다 |
| 105 | other | 5 | t4–t4 | Acrylic class water absorption (ASTM D570) |
| 613 | other | 4 | t4–t4 | [추정 라벨] 금속층 포함 복합 추정 — 벤더 데이터시트에서 읽은 값이 아니다 |
| 607 | other | 4 | t4–t4 | [추정 라벨] 아크릴/에폭시 접착 복합 추정 — 벤더 데이터시트에서 읽은 값이 아니다 |
| 617 | other | 3 | t4–t4 | [추정 라벨] PSR 계열 추정 — 벤더 데이터시트에서 읽은 값이 아니다 |
| 110 | other | 3 | t4–t4 | Acrylic class dielectric constant |
| 109 | other | 3 | t4–t4 | Acrylic PSA class density |
| 602 | other | 2 | t4–t4 | [추정 라벨] PI+접착 복합 추정 — 벤더 데이터시트에서 읽은 값이 아니다 |
| 552 | other | 2 | t4–t4 | [추정 라벨] IPC-4562A class-typical 추정 — 규격 문서에서 읽은 값이 아니다 |
| 104 | other | 2 | t4–t4 | Acrylic polymer class dielectric constant |
| 103 | other | 2 | t4–t4 | Acrylic PSA/OCA class representative density |
| 143 | other | 2 | t4–t4 | 점탄성 제진재 대표물성(Sorbothane 클래스) |
| 138 | other | 2 | t4–t4 | 연질 PU 폼 물성(문헌 클래스) |
| 600 | book | 2 | t2–t2 | epoxy 경화물 |
| 665 | other | 1 | t4–t4 | [범위 라벨] IPC-4101 규격 수지함량(RC) 허용범위 — 특정 제품의 측정값이 아니다 |
| 148 | other | 1 | t4–t4 | 점탄성 제진 아이솔레이터 대표물성(Sorbothane 클래스) |
| 147 | other | 1 | t4–t4 | 점탄성 제진 아이솔레이터 대표물성(Sorbothane/EAR 클래스) |
| 146 | other | 1 | t4–t4 | 점탄성 제진 마운트 대표물성(Sorbothane 클래스) |
| 145 | other | 1 | t4–t4 | 점탄성 제진 마운트 대표물성(Sorbothane/EAR 클래스) |
| 142 | other | 1 | t4–t4 | 점탄성 제진재 대표물성(Sorbothane/EAR 클래스) |
| 141 | other | 1 | t4–t4 | 등가근사: 3M 8810 계열 열전도 테이프급 |
| 139 | other | 1 | t4–t4 | PU 폼 물성(문헌 클래스) |
| 137 | other | 1 | t4–t4 | 점탄성 연질 PU 폼 물성(문헌 클래스) |
| 509 | other | 1 | t4–t4 | Equivalent approximation from bulk silver (Ag-dominant Mg:Ag cathode) |
| 599 | book | 1 | t2–t2 | epoxy Df |
| 598 | book | 1 | t2–t2 | epoxy Dk |
| 597 | book | 1 | t2–t2 | neat epoxy CTE |
| 596 | book | 1 | t2–t2 | 표준 FR-4 수지 Tg |
| 595 | book | 1 | t2–t2 | FR-4 epoxy 경화물(핸드북) |
| 594 | book | 1 | t4–t4 | E-glass softening ~846℃ |

**이것들은 §661 이 요구한 정직함을 이미 갖추고 있다** — *"가정값을 대량으로 부을 때 출처에
적을 것은 '그럴듯한 책 이름' 이 아니라 '이것은 클래스 기본값이다' 다."* 라벨 일곱은 그 규율의 **모범**이고,
`Acrylic class …`·`점탄성 제진재 대표물성(Sorbothane 클래스)`·`등가근사: 3M 8810 계열 …`·
`Equivalent approximation from bulk silver` 도 같은 부류다.

**문제는 나머지 일곱이다** — `epoxy 경화물`(600) · `epoxy Dk`(598) · `epoxy Df`(599) ·
`neat epoxy CTE`(597) · `표준 FR-4 수지 Tg`(596) · `FR-4 epoxy 경화물(핸드북)`(595) ·
`E-glass softening ~846℃`(594). **제목이 물성 이름인데 `kind='book'` 이고 등급이 t2 다.**
`kind` 와 등급이 "책에서 읽었다" 고 말하는데 어느 책인지 없다 — **C 안에서 유일하게 정직하지 않은 줄**이다.
(594 는 이미 다른 결함으로도 표시돼 있다 — pv1500 의 `conditions.internal_contradiction` 이
*"제목의 846 ℃ 와 값 1113 K(=840 ℃)가 6 ℃ 어긋나고, 어느 쪽이든 연화점이지 최대사용온도가 아니다"* 라고 적어 두었다.)

**할 일 — 지우지 말고 정직하게 다시 이름 붙여라.** 갈래 C 는 `kind='computed'` 가 맞다
(출처 2576 이 이미 그 kind 를 쓴다). 이름은 `[클래스 가정] …` 으로 통일하면 다음 파동이
**출처 문자열 한 줄로** 이 값들이 문서에서 온 것이 아님을 안다. **다만 `kind`·`title` 은
자연키 안이다**(§4) — 그래서 이것도 "고침" 이 아니라 "새 출처 + 이동" 이다.

---

## 4. 왜 제목을 안 고쳤나 — 병합기를 먼저 쳐 봤다(§578·597 의 확인)

`source` 의 자연키는 다음 일곱이다(`_materialtwin_merge.py` `PLAN`).

```
["kind", "doi", "isbn", "url", "title", "publisher", "license"]
```

**제목·kind·publisher·url·isbn 은 전부 그 안이다.** 하나만 고쳐도 자연키가 바뀌어
병합기가 운영에서 대응행을 못 찾고 **새 출처를 만든다.** 그러면 `source_id` 가 바뀐
`property_value` 도 자연키가 깨져 **그 출처의 값 전부가 운영에 사본으로 들어간다**
(972 면 201행, 853 이면 391행).

**빠져나갈 길은 둘뿐이고 둘 다 이 배치의 몫이 아니다.**

1. **`UNIQUE_FIRST` 축이 있는 출처는 안전하다** — `source` 는 `doi`·`isbn`·`content_hash` 로 **먼저** 찾는다.
   그런데 **이 91건은 정의상 셋이 다 비어 있다.** 그래서 이 91건에는 이 길이 없다.
2. **`conditions.moved_from_source` 로 옮긴다**(53차 OA · 분기 ⑤). 새 출처를 만들고 그 출처의
   **모든 값 행**에 옛 출처의 자연키 전체를 표시로 남긴다. 972 는 201행, 853 은 391행이다 —
   **마이그레이션 한 벌이고 표적 (2)만으로 한 파동이다.**

### 그리고 채워도 안전한 칸이 둘 있다 — `authors`·`year`

병합기가 2026-08-18 에 **자연키에서 뺐다**(주석 verbatim: *"`authors`·`year` 를 자연키에서 뺐다 …
**가변 보강 필드는 자연키에 넣지 마라**"*). 그래서 이 둘은 채워도 **새 출처가 안 생긴다.**

**그런데 운영에 전파되지도 않는다.** 병합기는 `material.attributes` 와 `property_value` 만
기존 행에 얹고, **`source` 는 매칭되면 한 칸도 안 건드린다**(비파괴 약속). 즉
`authors`·`year` 보강은 **dev 전용 개선**이다(§464 의 여섯 번째 얼굴).

→ **고칠 자리를 적어 둔다**(§468 — 이 배치는 안 고쳤다). `source` 도 `material` 처럼
**보강 전용 화이트리스트**(`authors`·`year`·`local_path` 중 자연키 밖의 것)를 두고
매칭된 운영 행의 **빈 칸만 채우는** 분기 하나면 된다. 덮어쓰지 않고 `IS NULL` 일 때만 채우면
비파괴 약속을 안 깬다.

---

## 5. 출처 3384 — 제3자 확인 결과(62차 XC 신고의 재검증, §653)

XC 의 신고를 그대로 옮기지 않고 **다시 쳤다.** Crossref 와 Europe PMC 둘 다 같은 답을 준다.

```
DOI 10.1038/srep38595
Crossref     title  "Tailoring thermal conductivity via three-dimensional porous alumina"
             authors Begoña Abad · Jon Maiz · Alejandra Ruiz-Clavijo · Olga Caballero-Calero
                     · Marisol Martin-Gonzalez        container Scientific Reports   year 2016
Europe PMC   "Tailoring thermal conductivity via three-dimensional porous alumina."
             Abad B, Maiz J, Ruiz-Clavijo A, Caballero-Calero O, Martin-Gonzalez M.
             Sci Rep 6:38595 (2016)  PMID 27934930 · PMC5146943
```

DB 의 제목은 `Rodriguez et al., 'Thermal conductivity of 3D ordered anodic aluminium oxide
membranes', Scientific Reports 6:38595` 다 — **제1저자도 제목도 다르고 권·쪽·DOI 만 맞다.**
`authors`·`year` 는 NULL 이다. 값 2행(재료 151 의 열전도율·비열 t3)의 귀속은 DOI 로 지켜지지만
**제목 검색으로는 영영 안 걸린다**(§596).

**할 일 — `authors`·`year` 를 채워라(자연키 밖이라 안전하다). `title` 은 고치지 마라.**
3384 는 DOI 가 있어 `UNIQUE_FIRST` 로 매칭되므로 제목을 고쳐도 병합은 안 깨지지만,
**운영에 반영되지도 않는다**(§4). 제목 정정은 §4 의 보강 분기가 생긴 뒤에 한 번에 하는 것이 맞다.

---

## 6. 출처 2576 — 제목이 스스로를 배신하는 자리(62차 XD 신고의 검산)

```
source 2576  kind=computed  url=https://github.com/squall321/MaterialTwinWeb  publisher=MaterialTwinWeb
title  "MaterialTwinWeb 클래스 가정 — 카탈로그 내 동일 클래스 실측값의 중앙값"
값 151행 · 전부 t4 (영률 92 · 포아송비 59)
```

**전수로 세었다 — 92행 중 89행이 제목과 다르다.**

| 무엇 | 행 | notes 가 말하는 근거 |
|---|---:|---|
| 포아송비 59행 | 59 | **제목대로다** — `카탈로그 내 '<클래스>' **실측** N건의 중앙값 …(범위·IQR)` 로 모집단·분산까지 적혀 있다 |
| 영률 3행 | 3 | **제목대로다** — 재료 443·444·445 는 *"tier1 으로 등록된 Henkel Hysol 17개 등급의 25 ℃ 굴곡탄성률(10.98–23.9 GPa)의 중앙값"* |
| **영률 89행** | **89** | **제목과 다르다** — 모집단이 실측이 아니라 **다른 t4 칸 하나**다. verbatim 예 — *"카탈로그 내 'PSA Acrylic General (3M 467MP)' 항목의 0.30 MPa(**tier4**, Satas PSA 핸드북 아크릴 PSA 계열값)를 **옮긴 가정값**이다"* · *"'Foam PE General' 3.0 MPa(**tier4**)와 … 대역이 근거다"* · *"OLED … 세 항목의 3.0 GPa(**tier4**, Polymer Handbook 4th ed.)"* |

**t4 위에 t4 다.** 그런데 세 번째 열의 `notes` 는 **하나같이 정직하다** — 스스로 `tier4` 라고 밝히고
어느 칸에서 옮겼는지까지 적는다. **틀린 것은 값도 사유도 아니라 출처 제목 한 줄**이고,
그 한 줄이 89행을 *"실측의 중앙값"* 으로 보이게 한다(§661 의 정확한 재현 — **출처 문자열이
실제보다 강해 보인다**).

**할 일 — 제목을 고치지 말고(위 §4) 행에 표식을 달아라.**
`conditions.verdict_class_transfer = "모집단이 실측이 아니라 t4 클래스값이다 — 출처 제목의 '실측값의 중앙값' 은
이 89행에는 해당하지 않는다"` 가 **병합기 분기 ②-b 로 운영까지 가는 유일한 경로**다
(`verdict_` 접두어여야 한다). 제목을 고치면 151행 전부가 운영에 사본으로 들어간다.

**그리고 이 89행은 §660 의 마지막 줄에 정확히 해당한다** — 대체 대상으로 세울 때 우선순위가
**가장 높다.** 포아송비 59행(실측 중앙값·범위·IQR 이 적혀 있다)은 §660 이 *"표적 아래로 내려라"*
라고 한 그 30칸의 확대판이라 **우선순위가 가장 낮다.** 같은 출처 안에서 두 갈래의 표적 우선순위가 정반대다.
