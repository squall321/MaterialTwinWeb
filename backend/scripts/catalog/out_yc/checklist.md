# 63차 YC 체크리스트

- [x] `docs/COLLECTION_METHODOLOGY.md` · `docs/CATALOG_PIPELINE.md` · `docs/COLLECTION_BRIEF_CORPUS.md` §600~§666 및 §3 §25 §468 §504 §505 §565 §578 §582 §584 §593 §594 §597 §610 읽기
- [x] 라이브 DB 스냅샷 (`VACUUM INTO`, §647) — `snap_yc_pre.db`

## 표적 (1) 해당 없음인데 차 있는 칸
- [x] `attributes.core_not_applicable` 전수 × 그 키의 값 유무 → **0건**(선언 키는 전부 빈칸)
- [x] `verdicts_check.py` 를 열어 "빈칸에만 걸린다" 는 전제 검증 → **틀렸다**(`COUNTER_TIER` 가 차 있는 칸을 본다)
- [x] 41,963행 `notes`+`conditions` 산문 전수 스캔(물성 별칭 20 × 물리부재 구문, 문서부재 어휘 제외) → 후보 46쌍 → 손확인 **2건**
- [x] `conditions.t4_contradiction` / `internal_contradiction` 전수 → 6건(표시 있음) + 2건(값 모순, 표적 아님)
- [x] 원형 표적 전수 — 취성재 파단연신율 40칸 · 분말 12종 · 액체 1종 · 소자 53종 목록화
- [x] 무엇을 해야 하는가 판단 3안 비교 후 결론 → `YC01_filled_na_audit.md` §3
- [x] **값은 한 칸도 안 지우고 안 고쳤다**

## 표적 (2) 출처 제목이 실제보다 강해 보이는 자리
- [x] 91건 전수 추출(검사기와 같은 질의) · 1,736행 · 등급 분포
- [x] 셋으로 가름 A 22 / B 39 / C 30 (합 91 검산 통과)
- [x] 출처 972 확인 — 두 문헌 합침, 201행 전부 t4
- [x] 출처 2576 전수 검산 — 영률 92행 중 **89행이 제목과 다른 모집단**(t4 위의 t4)
- [x] 출처 3384 제3자 재확인 — Crossref + Europe PMC 둘 다 `Abad, B. et al.` 2016
- [x] `source.doi` UNIQUE 와 병합기 자연키 영향 확인 → **제목 정정은 사본을 만든다. 안 고쳤다**
- [x] `authors`·`year` 는 자연키 밖이나 **운영 전파 경로가 없음**을 확인 → 고칠 자리만 적음
- [x] 산출 `YC02_noid_sources_triage.md` · `yc02_noid_triage.json`

## 표적 (3) 키 오분류 5행
- [x] 원문 PDF 직접 열기(`pdftotext -layout`) · 정의절·기호표·기기 절 verbatim 확보
- [x] 값 5개를 원문 표 행 라벨과 글자 대조
- [x] `property_definition` 의 `test_standard`(ASTM E408)·`condition_axes` 교차 확인
- [x] 마이그레이션 작성 `b3c4d5e6f7a8_move_w63yc_rp1121_normal_emittance.py`
- [x] 리비전 충돌 회피(`c3d4e5f6a7b8` 는 이미 쓰임 → `b3c4d5e6f7a8`), head 단일 확인
- [x] **사본에 먼저 적용** → diff 5행 · 추가 0 · 삭제 0
- [x] 대표값 전후 대조(§610) — 변동 2건 모두 개선 방향임을 확인
- [x] 중복 한 쌍(pv6690 대 pv43892)에 52차 NB 규약 표시
- [x] `downgrade` 왕복 → 원본과 다른 행 **0**
- [x] 라이브 적용(`VACUUM INTO` 로 적용 직전 스냅샷 먼저)
- [x] 라이브 diff — 내 적용으로 바뀐 행 정확히 5

## 검사
- [x] `integrity_check.py` — 스냅샷 대 적용후 diff **0줄**, 총계 "이상 1개"(기존 잔재)
- [x] `verdicts_check.py` — ✔ 이상 0개
- [x] `pytest -q` — 512 passed, 1 skipped
- [x] 공유 도구 셋(`coverage_report.py`·`verdicts_check.py`·`integrity_check.py`) **한 줄도 안 고침**
- [x] `build_overview_html.py` · `docs/물성카탈로그_현황.html` · `docs/COLLECTION_BRIEF_CORPUS.md` **안 건드림**

## 커밋
- [x] §504 경로 제한 커밋 · 커밋 메시지 파일 이름에 `yc`
- [x] `BRIEF_DRAFT.md`(번호 비움)
