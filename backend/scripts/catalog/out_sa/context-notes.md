# 57차 SA 작업 기록 — packaging 계통 코어 빈칸

라이브 DB `MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web` 로만 읽고 썼다.

## 산출물

| 파일 | 무엇 |
|---|---|
| `sa01_solder_core.json` | 값 20행 / 재료 9종. `ingest_agent_json.py --apply` 로 적재 완료 |
| `sa02_make_verdicts.py` | 판정 JSON 생성기(사유 문장이 여기 산다) |
| `sa02_core_verdicts.json` | 판정 207칸 / 재료 44종. `apply_core_verdicts.py --apply` 로 적재 완료 |
| `BRIEF_DRAFT.md` | 브리프 초안 14건 |

## 결과 — `subsystem='packaging'` · `role='product'`

```
전  116종 · 812칸 · 채움 369 (45.4%) · V1 0 · V2 0 · V3 35 · V4 24 · V6 0 · V5 384
후  116종 · 812칸 · 채움 389 (47.9%) · V1 21 · V2 184 · V3 0 · V4 24 · V6 2 · V5 192
```

- 값으로 준 것 **20칸**, 문서를 열어 닫은 것 **205칸**, 자유 키에서 옮긴 것 **35칸**.
- 검사 — `integrity_check.py` 이상 1개(기존 시험 잔재 2종, 신규 위반 0) · `verdicts_check.py` 이상 0개
  (신고 1건은 54차 PC 가 만든 기존 어긋남) · `pytest -q` **366 passed, 1 skipped**.

## 실제로 연 문서 (§127)

**벤더 문서 10장** — NEG Powder Glass 카탈로그(Ref. 2410-19E, 로컬 보관본) ·
Henkel LOCTITE ECCOBOND FP4527 / FP4526 · Henkel LOCTITE ABLESTIK 965-1L / 2025D ·
EPO-TEK 353ND / H20E · Koki S3X48-M500 / S3X70-M500C(이미지 전용 PDF, 200 dpi + tesseract).
**편찬표 2장** — Indium Corporation Indalloy alloy chart(2006, Wayback) ·
The Solder Connection Solder Alloy Technical Specification(2023).
**논문 10편** — Fujishima 2017 · Narahashi 2010 · Kasahara 2016 · Horiki 2011 · Wei 2016 ·
Chhanda 2012 · Hohlfelder 2001 · Chiu 2009 · Chiu 2018 · Chowdhury 2017/2019 · Wang 1993.

받아 둔 사본은 `/home/koopark/claude/MaterialTwinWeb/.agent_work/w57sa/` 에 있다.

## 결정과 이유

- **Indalloy 편찬표는 `pdftotext -bbox-layout` 의 단어 x좌표로 읽었다.** `-layout` 텍스트는 행마다
  들여쓰기가 최대 11자 밀려(조성 열의 원소 수가 다르다) 비열 SOLID/LIQUID 두 열이 뒤바뀐다.
- **열전도율 열은 @85 °C, 선팽창 열은 @20 °C 라 조건을 그대로 박았다** — 편찬표 머리글에 인쇄돼 있다.
- **Sn96.5Ag3.5 의 열전도율은 Indalloy 33 대 Solder Connection 55 로 갈린다.** 제조사 자사 표를
  골랐고(§129), 갈린 사실과 상대값을 notes 에 적었다. 같은 행의 밀도(7.50 대 7.37)도 갈려 밀도는 안 썼다.
- **92.5Pb5Sn2.5Ag 의 영률과 Wang 1993 의 인장탄성률은 기각하고 `core_rejected_printed_value` 에 적었다.**
- **V3 35칸(재료 616 · 2305~2308)은 성격상 V4 인데** V4 를 정하는 `identification_status` 가 병합기의
  CURATION 접두어 밖이라 운영에 안 간다. 전파되는 `core_absent_from_vendor_sheet` 에 적고
  사유 문장에 "성격상 V4" 를 못박았다(브리프 초안 2).
- **아무것도 지우지 않았다.** 자유 키 `core_fill_sheet` 는 그대로 두고 읽는 칸을 더했을 뿐이다
  (분류기가 V2 를 자유 키보다 먼저 보므로 지울 필요가 없다).

## 다음 표적 — 남은 192칸

| 갈래 | 칸 | 어디서 열리나 |
|---|---:|---|
| 포아송비 39칸 | 39 | **§6 이 표적에서 내린 물성이다.** 측정법이 명시된 것만 넣어라 |
| 솔더 합금 (SAC107·SAC125Ni·SAC205·SAC-Q·SACX0307·SAC(307)-2In·Sn-Zn-Bi 2종·97.5Pb2.5Sn) | 약 60 | Indalloy 2006 표와 Solder Connection 표에 **행이 없다**. ALPHA VACULOY·Almit·Nihon Superior 시트를 열어야 한다. **`SAC0107` ≠ `SAC107`(브리프 초안 10)** |
| 언더필 5종 (1352 Lamics U-8437-3 · 1369 · 1676~1678 Katsurayama) | 25 | 원문이 로컬에 없다. Kaltenpoth 2001 · Zhang 2000 · Katsurayama 2008 을 받아야 한다 |
| Cu-Al 금속간화합물 5종 (664~668) | 16 | Kouters 2013(Elsevier)이 로컬에 없다. 열어서 CTE·인장강도 부재를 확정하거나 캐라 |
| EMC 3종 (964 Chiu 2020 · 739 Chiu 2009+2011 · 1368 Lau 2018) | 16 | 739 는 두 번째 출처 Chiu 2011(IEEE TDMR)이 로컬에 없어 판정을 못 했다 |
| BT 적층판 615 · 1314 · 2346 · 292 · 403 · 438 등 | 나머지 | 출처가 여럿이라 전수로 열어야 한다 |

**셋을 섞지 마라**(§584) — 위 갈래 중 "시트를 열었는데 없다"는 하나도 없다. 전부 **아직 아무도 안 열어 본 것**이다.
