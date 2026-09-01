<!-- 57차 SC — 계통 태깅 없는 제품 재료 85종의 코어 빈칸 255칸 작업 체크리스트 -->
# 57차 SC 체크리스트

## 0. 사전 확인
- [x] 라이브 DB 확인 (`/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db`)
- [x] 인계 수치 직접 검증 — 85종 · 255칸 · V3 72 · V5 183 (`coverage_report.subsystem_core()`) → 넷 다 맞다
- [x] §25 §50 §127 §129 §131 §193 §438 §475 §504 §505 §565 §582~§584 §593~§599 정독

## 1. 계통 태깅
- [x] 85종 전수 `attributes` 열람 → **49차 KA 가 이미 전수 판정했고 `verdict_subsystem`+`subsystem_basis` 에 사유가 있다**
- [x] 판정 22계열로 묶어 재검증
- [x] 애매한 것은 벤더 문서를 실제로 열어 확인(§127) — DELO 4670/4552 · Aearo ISODAMP C-1002
- [x] 근거가 선 것만 배정 — #371 DELO KATIOBOND 4670 → `packaging`
- [x] out_of_scope 후보 목록화(직접 바꾸지 않는다)
- [x] 새 어휘 필요 여부 판단

## 2. §582 분해 · 판정을 읽는 자리로
- [x] V3 72칸 계열 분해 → V2 30 · V1 14 · V4 14 · 미결 14
- [x] V5 183칸 중 **자유 키에 이미 판정이 있는 29칸** 발굴(`*_absence`·`relation_to_bar`)
- [x] `apply_core_verdicts.py` 입력 JSON 작성 → 드라이런 → `--apply`

## 3. 채굴
- [x] #639 Fused Silica — Heraeus HQS-SO 시트 열어 열전도율 6행 + 인장강도 1행
- [x] #2391 Corrax for AM — Ed.15 p.7 AM 절 `Physical data` 표에서 밀도·E 3행·CTE 2행·k 2행
- [x] 못 캔 것과 그 이유 기록

## 4. 검산
- [x] `integrity_check.py` 신규 위반 0
- [x] `verdicts_check.py` 이상 0
- [x] `pytest -q` 366 passed / 1 skipped
- [x] `coverage_report.subsystem_core()` 재실행 — V5 감소 확인

## 5. 산출
- [x] `out_sc/` JSON · 보고 · `BRIEF_DRAFT.md`
- [x] §504 경로 제한 커밋
