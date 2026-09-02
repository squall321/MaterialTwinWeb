<!-- 59차 UD — 계통 태그 없는 제품 84종·코어 빈칸 249칸 작업 체크리스트 -->
# 59차 UD 체크리스트

## 0. 읽기
- [x] `docs/COLLECTION_METHODOLOGY.md` · `docs/CATALOG_PIPELINE.md`
- [x] 브리프 §600~§627 전수 · §3 §22 §25 §58 §127 §193 §475 §479 §504 §505 §582~§586 §599 §603 §608~§610
- [x] 57차 SC 산출물 전수(`out_sc/sc04`·`sc05`)
- [x] 기준선 대조 — `subsystem_core()` 의 `(태깅 없음)` 이 84종·249칸·V1 14 V2 59 V3 14 V4 14 V5 148 로 지시서와 글자까지 같다

## 1. out_of_scope 17종 판정
- [x] 기존 `role='out_of_scope'` 67종을 전수로 읽어 경계를 잡았다(§193)
- [x] Uddeholm 13종 — **실행**. 선례는 406~417 Smooth-On 몰드용 실리콘이다(금형을 만드는 재료는 이미 격자 밖)
- [x] 364 Intertape AC778 — **실행**. 선례는 2426~2429 MLCC 테이프캐스팅 바인더다(완제 부품에 남지 않는다)
- [x] EPE 387·388·389 — **실행하지 않는다.** 근거는 `context-notes.md` 와 보고문
- [x] 검산 — 이 실행이 빼는 빈칸은 **19칸뿐**이다(전부 이미 V2). 지시서의 "빈칸이 크게 준다" 는 사실과 다르다(§505)

## 2. "읽을 시트가 존재하지 않는다" 14칸
- [x] §626 대로 조달 전에 `corpus_index.py search` 를 먼저 걸었다
- [x] 587 SY-14M-III — **Cheng 2019 가 코퍼스에 있다.** 벌크 접착제 인장시험을 직접 했고 E·UTS 가 Fig.8 에 있다
- [x] 587 E·UTS 2칸 — Fig.8 픽셀 디지타이즈로 **채웠다**(축 눈금 두 벌로 교차 캘리브레이션)
- [x] 587 나머지 5칸 + 1110 7칸 = **12칸에 `core_no_public_document` 를 박았다**(`core_` 접두어 — §608 전파)
- [x] 집계 반영 요청을 보고문에 적었다(`coverage_report.py` 는 다른 배치가 쓰고 있어 건드리지 않았다)

## 3. V5 148칸 분해(§582)
- [x] 32종의 출처 문서를 전부 열었다(코퍼스 md + 표 파일 + 벤더 TDS)
- [x] 2417 Thermocomp MEV-1006 — Lee 2010 TABLE III 에서 **코어 6칸**을 캤다(§602)
- [x] 2266 GlidCop AL-15 — 벤더 TDS(No.700A)에서 **코어 3칸**을 캤다
- [x] V2 134칸 · V6 2칸 · V4 1칸 · 남은 V5 2칸
- [x] 선언 칸 수 대조(§610) — 아래 4번

## 4. 검산
- [x] 판정 적용 뒤 `subsystem_core()` 재집계와 선언 수 대조(§610)
- [x] `integrity_check.py` 신규 위반 0
- [x] `verdicts_check.py` 이상 0
- [x] `pytest -q` 366 passed · 1 skipped

## 5. 산출
- [x] `ud01_out_of_scope.json` · `ud02_values.json` · `ud03_core_verdicts.json` · `ud04_v5_split.md`
- [x] `BRIEF_DRAFT.md`(번호 비움)
- [x] 커밋은 `git commit -F - -- <경로>` 경로 제한(§504)
