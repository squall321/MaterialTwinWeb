<!-- 62차 XC 작업 체크리스트 -->
# 62차 XC — 열물성 t4 118칸

- [x] 61차 WD 산출물 `out_wd/AUDIT_thermal_t4.md` 정독
- [x] `docs/COLLECTION_METHODOLOGY.md` · `docs/CATALOG_PIPELINE.md` · 브리프 §600~§656 정독
- [x] 표적 재산출 — 라이브 DB 에서 t4 단독 대표 267칸 → 1차 파동 문구 115칸(재료 80종)
- [x] §635① notes 전문검색을 **물성 낱말**로 걸기(비열·比熱·specific heat·열전도·熱伝導) → 이 표적에서는 신규 0
- [x] 표적 80종이 쓰는 출처 550건 전수 추출 → URL 있는 467건 내려받기(UA 유·무 둘 다, §634)
- [x] PDF/HTML → 텍스트, 물성 낱말 grep, 칸 단위로 되매핑
- [x] 코퍼스 미해결 논문 해소(`corpus_fts.db` 제목 매칭 → 14편)
- [x] 적중 원문 확인 → 값 8행 확정(항등식·단위 병기열 검산 포함)
- [x] 0건 칸 → 부재 판정 62칸(재료 43종), 사유에 연 문서 전부 이름으로
- [x] WD 신고 넷 확인(고치지 않음)
- [x] 스냅샷 `VACUUM INTO`(§647) → 적재 → 판정 적용
- [x] 선언 대 집계 대조(§610) — 값 8/8 · 판정 62/62
- [x] `integrity_check.py` 신규 위반 0 · `verdicts_check.py` 이상 0 · `pytest -q` 366 passed 1 skipped
- [x] `BRIEF_DRAFT.md` · `REPORT_xc.md`
