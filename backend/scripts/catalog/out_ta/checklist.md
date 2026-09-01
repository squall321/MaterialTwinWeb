# 58차 TA 체크리스트

## 일 1 — magnetics 를 닫는다
- [x] `subsystem='magnetics'` 기준선 측정 — V3 168 · V5 7 · 빈칸 175 / 273
- [x] 자유 키 판정 전수 읽기 — `grade_table_scope` 24종(2651~2674), 2675 는 판정 없음
- [x] 사유가 지금도 맞는지 원문으로 확인 — Eclipse PDF 전문(§599·§127)
- [x] 옳은 자리 결정 — 7키 전부 `core_rejected_printed_value`(V6)
- [x] 판정 JSON 작성(한 재료 한 행, §610)
- [x] `apply_core_verdicts.py` 예행 → 적용
- [x] 선언 칸 수 대 집계 칸 수 대조(§610)
- [x] V5 7칸(재료 2675)이 캘 수 있는지 확인

## 일 2 — 막힌 키
- [x] `mechanical.elastic_compliance` [1/Pa] — Park 1997 s33^E 4행
- [x] `physical.density_model_constant` [1] — Landesfeind 2019 SI 9행
- [x] `electrical.arc_resistance` [s] — ASTM D 495 2행
- [x] 콘칼로리미터 ASTM E 1354 세트 4키 — 5행
- [x] `property_taxonomy.py` · 마이그레이션 · RANGE 가드
- [x] 값 적재 JSON 작성 · 예행 · 적용

## 검산
- [x] `integrity_check.py` 신규 위반 0
- [x] `verdicts_check.py` 이상 0
- [x] `pytest -q` 366 passed / 1 skipped
- [x] 마이그레이션 upgrade/downgrade 왕복
