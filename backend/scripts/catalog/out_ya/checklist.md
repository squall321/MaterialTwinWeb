# 63차 YA 체크리스트 — `conditions.temperature` 두 갈래 정리

목표. **값을 한 칸도 안 바꾸고** 구식 문자열 키 `conditions.temperature` 2,255행을 정리한다.
성공 판정은 셋이다 — ① `integrity_check` 출력이 정정 전후로 **글자까지 같다** ② `verdicts_check`
이상 0 ③ `pytest` 기준선(366) + 새 시험이 전부 통과한다.

## 조사
- [x] 라이브 census — 표기 **142종 · 2,255행**(지시서의 133종은 그 사이 늘었다)
- [x] 이 키를 읽는 코드 전수 — `_temp_distance`(대표값) · `_COND_SHOW`(카드 태그) ·
      `tie_verdicts.temp_c`(동률) · 프런트 `formatConditions` · `integrity_check`(`$.temperature_k`)
- [x] `_rep_rank` 다섯째 자리(`_condition_axis_count`)가 `_before_correction` 을 안 센다는 것 확인 →
      **이 배치는 조건 칸 수를 안 바꾼다**(§548 의 사고가 구조적으로 안 난다)
- [x] 숫자가 든 149행을 **전수로 열어** `detail`·`notes` 로 시험온도인지 갈랐다 → `candidates_raw.txt`

## (1) 숫자 이관
- [x] 단위 확인 후 환산 — °C/K/F → K. 원값·배율을 정정 사유에 남겼다
- [x] **86행은 시험온도가 아니라 안 옮겼다** — 등급명 23 · 공정온도 18 · 구간 끝 17 ·
      값 자신의 재기재/승온율 15 · 다른 축 혼재 11 (`migrate_temperature_ya.SKIP` 에 pv 번호까지)
- [x] 맨 숫자 17행 — 8행은 옆 칸 `temperature_unit: "K"` 가, 9행은 `.15` 환산상수 지문이 단위를 답한다
- [x] **둘 다 가진 41행 대조 — 어긋난 행 0**(숫자 32행은 소수 둘째자리까지 일치, 나머지 9행은 진술)
- [x] 절대영도 이하 2행 신고(옮기지 않았다) — pv5595 `-343 K` · pv5596 `-573 K`
- [x] `temperature_before_correction` 보존(§594) — 적재기가 자동으로 남긴다
- [x] 이관 **75행** 적용(97행 중 22행은 정정을 못 남겨 뺐다)

## (2) 어휘 접기
- [x] `app/temperature_vocab.py` — 머리절 규율로 `room temperature` · `not reported` 둘로 접는다
- [x] 원문은 안 지운다 — `temperature_before_correction` 이 지킨다
- [x] 접기 **1,402행** 적용 → 진술 표기 88종이 2종으로(막힌 90행만 옛 표기가 남는다)
- [x] 접을 수 없는 4종 53행은 손대지 않았다(NTP · ISO 291 코드 · `hot or cold` · 구간 서술)

## 검사
- [x] 스냅샷은 `VACUUM INTO`(§647) — `cp` 안 썼다
- [x] **스냅샷 사본에 먼저 `--apply`** 하고 검사 diff 를 본 뒤 라이브 적용(62차 XA 의 수)
- [x] `integrity_check` 전후 **byte-identical**(`integrity_diff.txt` 0줄) · `이상 1개`는 기존 잔재
- [x] `verdicts_check` diff 없음 · `이상 0개`
- [x] `pytest -q` → **512 passed, 1 skipped**(기준선 366 + 새 시험 146)
- [x] `verify_readers_ya.py` — 조건 칸 수 바뀐 행 **0** · `_temp_distance` 바뀐 행 **75**(이관분 그대로) ·
      카드 온도 태그 **+75 · 사라진 것 0** · **대표행이 바뀐 군 7(값이 실제로 달라지는 것 5)**
- [x] §665 — 적재 직후 자기 행 `method` 재확인. `method_before_correction` 표시 **0행**
- [x] `value_duplicates` 전후 동일(47/445/1420) — 접기가 새 중복을 드러내지도 만들지도 않았다

## 산출
- [x] `out_ya/BRIEF_DRAFT.md`(번호 비움) · `checklist.md` · `context-notes.md`
- [x] 커밋 넷 — 모듈 / 시험 / 이관 / 접기. §504 경로 제한 · §656 메시지 파일에 `ya`
