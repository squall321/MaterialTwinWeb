# 63차 YD 체크리스트

- [x] 라이브 DB(`MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web`)에서
      다섯 출처(3104·689·760·2836·22)가 덮는 재료·t4 격자를 뽑는다 → 검증: 지시서의 t4 수(191·130·78·112·134)가 재현되나
      → 결과 198·128·76·112·134 (DB 가 62차 이후 움직인 만큼의 편차, 격자 정의 일치)
- [x] 다섯 편을 전권으로 연다 → 검증: 표를 전수로 세었나
      - 3104 표 3개(전권 md + PDF, 코퍼스) · 2836 표 30개(188쪽 PDF 내려받음) · 22 표 7개(5쪽 PDF 내려받음)
      - 689·760 **열 수 없음** — 식별자 전무 · 코퍼스/디스크/웹 모두 부재
- [x] 문서에 있는 열 × 그 문서가 덮는 재료 격자로 빈칸·t4 를 처리한다
- [x] §658 을 형제 키(`*_at_rate`)까지 넓혀 돌린다 → 검증: 준정적 행이 있는 t4 를 다 찾았나
- [x] 400 dpi 렌더로 인쇄값을 확인한다(§603) — 2836 WLF 식·Table 5.7·5.9 · 2898 Appendix B 9행 · 3357 Table 1 · 22 전기표
- [x] JSON 을 `out_yd/` 에 쓴다 → 드라이런 통과 24행·거부 0
- [x] `VACUUM INTO` 스냅샷을 뜨고 사본에 먼저 `--apply` → diff 24행 신규·0행 삭제·기존 행 해시 불변·새 출처 0
- [x] 사본에서 `integrity_check.py`(이상 1개, 적용 전과 동일) · `verdicts_check.py`(이상 0) · `pytest -q`(512 passed, 1 skipped)
- [x] 라이브에 `--apply` → 42185 → 42209행
- [x] 라이브 재검사: integrity 이상 1개(불변) · verdicts 이상 0
- [x] 적재 직후 자기 행의 `method` 를 다시 읽는다(§451) → 24행 전부 `measured`, 중앙값 가드에 안 걸림
- [x] `BRIEF_DRAFT.md`(번호 미부여) 작성
- [x] `§504` 경로 제한 커밋(`backend/scripts/catalog/out_yd/` 만)
