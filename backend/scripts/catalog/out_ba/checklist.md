# 66차 BA 체크리스트 — 포아송비 한 칸만 남은 재료 64종

- [x] 표적 재확인 — `role=product` · ρ·E 있고 ν 없는 재료 **64종**(라이브 DB 직접 질의)
- [x] 65차 AA 산출물(`out_aa/`) 읽기 — 어느 클래스가 왜 클래스 중앙값을 못 만들었는지
- [x] 65차 AB 산출물(`out_ab/`) 읽기 — 하드페라이트 25등급 밀도·영률 선례
- [x] **§626 — 조달 전 `corpus_index.py search`** (MMPDS · MIL-HDBK-5 · ASM Handbook · Polymer Handbook · CRC Handbook)
      → 다섯 다 **인용만 걸리고 원권은 코퍼스에 없다**. `find -iname "*handbook*"` 도 0건
- [x] **§659 전수 통과** — 표적 64종이 쓰는 출처 64건 중 로컬 파일 18건을 전부 텍스트화해 `poisson` grep
      → **2/18 (11%)** 적중(Eclipse 페라이트 시트 · Perkins 2009)
- [x] **§669 수확률 판정 후 문의 종류를 바꿈** — 제품 TDS 가 아니라 **벤더 설계가이드·응용노트**
- [x] 조달 — DuPont Delrin Design Guide Module III · Solvay Torlon PAI Design Guide · Indium Corporation Application Note
      (셋 다 200 · PDF · `poisson` 적중). 코퍼스 `standards_appnotes/` 에 사본 보관(§626④)
- [x] 조달 실패 확인 — 갭패드 벤더 9장 · Rogers LCP 2장 · EPO-TEK 2장 · GPO-3 4장 · Röchling 독일어 TDS · SABIC Noryl 가이드 = **0건**
- [x] **§43 역산 금지 준수** — E·G 로 ν 를 만들지 않았다
- [x] **기각 판정 재확인** — 재료 2293(90Pb10Sn)의 `core_rejected_printed_value` 를 읽고 Perkins 0.282 를 **넣지 않았다**
- [x] `core_not_applicable` 칸 건드리지 않음
- [x] 적재 JSON 작성 — `ba01`(25행 t4) · `ba02`(3행 t2)
- [x] **사본 리허설** — `VACUUM INTO` 스냅샷에 `--apply` → 카드 612 → 640, integrity/verdicts diff 0
- [x] 라이브 백업 `materialtwin.db.pre-w66ba-20260907-105050Z`(VACUUM INTO)
- [x] 라이브 적재 — `[APPLY] ok 28`
- [x] `integrity_check.py` — 이상 1개(기존 잔재, 전후 동일) · 신규 위반 0
- [x] `verdicts_check.py` — 이상 0개(전후 동일)
- [x] `pytest -q` — **515 passed, 1 skipped**(기준선 유지)
- [x] §657 주입 지문 자기검사
- [x] 교훈 초안 `BRIEF_DRAFT.md`
