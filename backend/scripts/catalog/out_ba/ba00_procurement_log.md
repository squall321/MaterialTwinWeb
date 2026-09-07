# 66차 BA 조달 기록 — 무엇을 실제로 손에 쥐었나

## 코퍼스 선검색(§626) — 원권은 **하나도 없다**
`corpus_index.py search` 로 `MMPDS` · `MIL-HDBK-5` · `"ASM Handbook"` · `"Polymer Handbook"` ·
`"CRC Handbook"` 다섯을 걸었다. **전부 논문 참고문헌의 인용만 걸리고 원권 전문은 없다.**
`find /data/paper_patent_corpus -iname "*handbook*"` 도 물성 핸드북 0건
(걸린 다섯은 지문인식·RFID·PSA·우주열제어 4장짜리다).
⚠ DB 출처 **853 `Polymer Handbook (Brandrup…) 4th ed.`** 는 쪽·표·URL·ISBN 이 하나도 없고
그 이름으로 실린 ν 39행 대부분이 `fill_dyna_gaps_1.py` 의 계열 대표값이다(§661 의 자리). **근거로 쓰지 않았다.**

## 열린 것 (200 · PDF · `poisson` 적중)

| 문서 | 크기 | 보관 경로 | 얻은 것 |
|---|---:|---|---|
| DuPont `Delrin® Design Guide — Module III`(H-57472, 95.1) | 442 KB | `standards_appnotes/poly/DuPont_Delrin_Acetal_Resin_Design_Guide_ModuleIII.pdf` | Delrin 500 ν 0.35 @23 °C |
| Solvay `Torlon® PAI Design Guide` v5.0 (R 07/2015) | 4.3 MB | `standards_appnotes/poly/Solvay_Torlon_PAI_Design_Guide_EN_227547.pdf` | Torlon 4301 ν 0.39 |
| Indium Corp. `Physical Constants of Pure Indium`(Form 97532 R7) | 146 KB | `standards_appnotes/mech/IndiumCorporation_Physical_Constants_of_Pure_Indium_APPNOTE-97532-R7-1.pdf` | 순수 In ν 0.4498 @20 °C |
| Eftekhari 2016 학위논문(OhioLINK `toledo1470388940`) | 10.4 MB | (미보관 — ν 0건이라 값이 안 나왔다) | **없음**. `poisson` 한 줄이 문헌고찰이다 |

`etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=<등록번호>&disposition=inline` — **경로는 살아 있다**(200).

## 이미 갖고 있던 출처 전수 통과(§659)
표적 64종이 쓰는 출처 **64건** 중 로컬 파일이 있는 **18건**을 전부 텍스트화해 `poisson` grep →
**2건 적중(11%)**. Eclipse 페라이트 시트(ν 0.28) · Perkins 2009(90Pb10Sn 0.282, **기각된 값이라 안 씀**).

## 열었으나 0건 — 다시 두드리지 마라

| 서식 | 장수 | 결과 |
|---|---:|---|
| Laird `T-flex 300 Series` TDS (RS 미러 2006판 · laird.com 2023-09판) | 2 | 0 |
| Henkel `BERGQUIST GAP PAD TGP` TDS (2400 · 1300U · A2000 · HC5000) | 4 | 0 |
| Parker Chomerics `THERM-A-GAP` (500 시리즈 TB-1016-1-07 · 974/G974/976) | 2 | 0 |
| Parker Chomerics `Thermal Interface Materials Catalog`(5.8 MB) | 1 | 0 |
| Rogers `ULTRALAM 3850HT` · `ULTRALAM 3908 Bondply` | 2 | 0 |
| `EPO-TEK 353ND` · `EPO-TEK H20E` TDS | 2 | 0 |
| GPO-3 — Boedeker `NEMA GPO-1/2/3` 규격표 · Attwater `GP03` · Gund `GPO3` · Röchling `Durostone UPM 203` 독일어 TDS(`querkontraktion` 도 0) | 4 | 0 |
| Celanese `Vectra LCP Short-Term Properties Guide`(LCP-026) | 1 | 0 |
| SABIC `NORYL Resin Injection Molding Guide` | 1 | 0 |
| Zoltek PANEX · Toho Tenax — 검색 결과에 ν 를 싣는 서식이 없다 | — | 0 |

**이 17장 중 상당수는 판정문(`core_absent_from_vendor_sheet`)이 이미 이름으로 적어 둔 문서다.**
다음 파동은 판정문을 먼저 읽어라 — BRIEF_DRAFT 첫 절이 그 교훈이다.

## 막힌 것
- `hi-tempfab.com`(Durostone Glastic FHT/SG-200) — **TLS 인증서 호스트명 불일치**로 curl 실패.
- `materialdatacenter.com` 의 `VECTRA A950RX` 페이지 — **404**(A950 페이지만 있다).
