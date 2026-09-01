# 58차 TD 체크리스트 — housing 계통

## 준비
- [x] `docs/COLLECTION_METHODOLOGY.md` · `docs/CATALOG_PIPELINE.md` 읽기
- [x] `docs/COLLECTION_BRIEF_CORPUS.md` §600~§625 전독 + §6 §25 §50 §58 §127 §129 §438 §504 §505 §582 §584 §593 §599
- [x] 라이브 DB 로 housing 분해 재현 — 160종 · 빈칸 148 · V1 0 / V2 0 / V3 55 / V4 0 / V5 93 (지시서와 일치)
- [x] 빈칸 있는 재료 49종 목록화 · 계열로 분류(테이프 20 · 금속 9 · 폴리머 10 · 계보 4 · 기타 6)

## (1) V3 55칸을 집계가 읽는 자리로
- [x] 자유 키 사유 10종 전수 재독 → **넷이 늙어 있었다**(2290 · 2316/2317/2318 의 `single_property_exception`)
- [x] 740 KGK-200A50 7칸 → V2 (일본어 카탈로그 전수 판정 유지)
- [x] 1785 AE44 as-cast ν → V2 (NADCA 에 AE**42** 만 있고 AE44 열이 없음을 이 파동에 확인)
- [x] 1786/87/88 AE44 시효점 21칸 → V1 계보 + `catalog_twin`(1785)
- [x] 2274 Noryl 7칸 → V4 (`identification_status` 로 이동 — 57차 SA 이후 `CURATION_KEYS` 에 있어 운영까지 간다)
- [x] 2290 강 45 7칸 → V1 계보 + `catalog_twin`(36). **판정 늙음 신고** — "병합 후보다" 는 이미 병합됐다
- [x] 2316 Hostaform 5칸 → V4
- [x] 2317 Delrin 500 5칸 → V2 · 2318 Torlon 4301 2칸 → V2
- [x] 2316/2317/2318 `single_property_exception` 늙은 문장 정정(원문은 `_before_correction` 에 보존)

## (2) V5 93칸 분해
- [x] 점착테이프 20종 벤더 문서 18장 조달 + 전권 낱말검색 → UTS 20칸 V2
- [x] 폴리머 시트 재독(Stanyl·Celanex·Ertalyte·Vectra·Victrex) → 20칸 V2
- [x] 금속 시트 조달(Nedal 6082 · Alcoa 6013 · Nedal 7003 재독 · Smiths 2017A) → 10칸 V2
- [x] 계보 판정 2종(1364 7075-T651 → 23 · 2432 Type 316 → 5) → 12칸 V1
- [x] §602 옆 칸 검사 — NADCA Zn 표에서 비열·열전도율, NADCA Mg 표에서 ν 둘 → **4칸 채움**
- [x] Nedal 6082 물리물성 표 → 밀도·CTE·열전도율 **3칸 채움**(4행)
- [x] Baek 2008 Table 2 고상/용융 밀도 쌍 검산 → 밀도 **1칸 채움**, 나머지 4칸 V6
- [x] Zinc HF CTE 단위쌍 불일치 → V6 (400 dpi 렌더 + 2015 판 대조)
- [x] 남은 18칸에 `core_next_target` 으로 다음 한 걸음 못박기(V5 로 남긴다)

## 검산
- [x] Zinc HF — 65.3 BTU/ft·hr·°F × 1.7307 = 113.0 W/(m·K) · α = k/(ρ·Cp) = 4.25e-5 (순 Zn 4.17e-5)
- [x] Zinc HF 비열 — 조성 혼합칙 0.955×390 + 0.045×900 = 413 대 인쇄 403 (2.5%)
- [x] Mg ν 0.35 — G = E/(2(1+ν)) = 45/2.7 = 16.7 GPa (Mg 통용 16.5~17)
- [x] 6082 — α = k/(ρ·Cp) = 170/(2700×900) = 7.0e-5 m²/s
- [x] Baek 필름 밀도 — 고상 1054.1 / 용융 943.9 → 체적수축 10.5% (ABS 통용 10~12%)
- [x] §438 검사 — 받은 문서마다 등급 문자열 카운트. Aalco 2017A 경로에서 **실제로 걸렸다**

## 검사
- [x] `integrity_check.py` — 신규 위반 0 (물성값 0인 재료 2 는 타 배치의 시험 재료 2649·2650)
- [x] `verdicts_check.py` — 이상 0
- [x] `pytest -q` — 366 passed, 1 skipped (기준선 일치)
- [x] §610 — 선언 칸 수 대 집계 칸 수 대조: filled +8 · V1 40 · V2 65 · V6 5 · V4 12 · V5 18 = 140 ✔
