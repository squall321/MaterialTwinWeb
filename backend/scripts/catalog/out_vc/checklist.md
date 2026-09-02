# 60차 VC 체크리스트 — 카탈로그 마지막 잔여 32칸

## 준비
- [x] `docs/COLLECTION_METHODOLOGY.md` · `docs/CATALOG_PIPELINE.md`
- [x] 브리프 §600~§627 전부 · §3 §25 §58 §127 §475 §504 §584 §586 §593 §599
- [x] 라이브 DB 로 표적 재분류 — 브리프의 13·17·2 칸과 글자까지 일치 확인
      (CORE7 의 CTE 키는 `thermal.expansion_coefficient` 가 아니라 `thermal.expansion_linear` 다)

## (1) packaging 비솔더 13칸
- [x] 1314 Shi 2012 전권 재열람 — 표 셋 전수 확인 → E·ν·k·Cp·UTS 5칸 V2
- [x] 615 He 2007 · Ehrler 2004 · Iguchi 1979 · Sahin 2026 · Ueki 2015 전수 → ν·k·Cp·UTS 4칸 V2
- [x] 617 Chowdhury 2017 `poisson` 0건 → ν 1칸 V2 (+ 617/738 WLF 이중 계상 신고)
- [x] 438 Yang & Ding 2024 표 다섯 전수 → UTS 1칸 V2
- [x] 403 Yang 2017 표 둘 전수 → UTS 1칸 V2 (+ §3 위반 신고)
- [x] 292 Kim 2018 표 셋 + Hitachi ANISOLM 시트 9쪽 → UTS 1칸 V2

## (2) V3 자유 키 17칸 → 집계가 읽는 자리
- [x] 1911 `core_verdict_undecided` → `core_not_applicable` 7칸 (사유 늙음 확인)
- [x] 1358 · 1359 `core_fill_sheet`/`procurement_47ic` → `core_absent_from_vendor_sheet` 4+4칸
      (Huffman 2009 · AGC IMAPS 2010 재열람 — 네 낱말 0건)
- [x] 1360 `core_fill_sheet` → `core_absent_from_vendor_sheet` 2칸
      (Cyclotene 4000 처리절차 **판 셋** 대조 — density/specific heat 0건)
- [x] 자유 키는 하나도 지우지 않았다

## (3) 미태깅 잔여 2칸
- [x] 392 오픈액세스 논문 셋 + D3O 공개 TDS 일곱 장 → UTS 1칸 V2(성격상 V4)
- [x] 393 폴리우레아 폼 in-house 주조 확인 → UTS 1칸 V2

## 검사
- [x] `apply_core_verdicts.py` 재료당 한 행(§610) · 선언 32칸
- [x] §610 대조 — V1 +7 · V2 +25 · V3 −17 · V5 −15 · 빈칸 불변 · 갈래합 불변식 0
- [x] `integrity_check.py` — 출력이 적용 전과 **글자 단위로 같다**(기준선 이상 1개 유지)
- [x] `verdicts_check.py` — 이상 0
- [x] `pytest -q` — 366 passed, 1 skipped
- [x] §504 경로 제한 커밋
