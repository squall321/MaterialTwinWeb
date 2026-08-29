# 52차 NA — 조건 어휘 통일 · 작업 노트

**값은 한 행도 안 고쳤다.** 라이브 41,368행 전수 대조에서
`value_num`·`value_text`·`unit`·`method`·`quality_tier`·`source_id`·`notes` 가 바뀐 행 **0**.

## 정본을 고른 규칙 (다수결이 아니다)
1. **코드가 읽는 이름**이 하나뿐이면 그것 — `_DESCRIPTIVE_COND`·`_RATE_COND`·`_COND_SHOW`·
   `_temp_distance`·프런트 `formatConditions` 를 전수로 봤다.
2. 없으면 **taxonomy `condition_axes`** 가 선언한 이름(조건축을 어휘로 선언하는 곳은 거기 하나뿐, 171종).
3. 둘 다 없고 **대소문자만 다르면** taxonomy 관례(171종 중 166종이 전부 소문자).
4. 그래도 안 갈리면 행수 다수.

`_COND_SHOW` 이 `temperature_C` 만 읽고 `temperature_c` 를 빠뜨린 것은 **선택이 아니라 누락**이다
(같은 목록이 `temperature_K`·`temperature_k` 는 둘 다 읽는다). 그래서 규칙 ①의 제약으로 세지 않고
같이 고쳤다 — 5,171행이 카드 태그에서 안 보이고 있었다.

## 이 배치가 만난 결함 셋 (전부 고쳤고 시험으로 못박았다)
- **적재기** — 값이 `null` 인 조건 칸의 이름만 바꾸면 `<칸>_before_correction` 이 **하나도 안 남는다**
  (`old.get(k) != new.get(k)` 가 "없다" 와 "null 이다" 를 못 가른다). 표시가 없으면 병합기의
  정정 전파 분기가 아예 안 돈다 — 예행에서 91행이 운영에 새 행이 됐다.
- **적재기** — 조건 칸 이름이 컬럼 이름과 겹치면 표시가 충돌한다. `conditions.method` 를 고치면
  `method_before_correction` 이 남는데 병합기는 그것을 **컬럼 `method` 의 옛 값**으로 읽는다
  (`where method='DMA tan-delta'` → 0건). 예행에서 483행이 miss 였다. 겹치는 이름만
  `conditions.` 로 네임스페이스를 붙였다.
- **선택기** — `_rep_rank` 5번째 자리가 `len(conditions)` 인데 **되돌리기 표시까지 세고 있었다.**
  정정이 바꾸는 칸 수가 행마다 다르면 표시 수도 달라져 대표값이 뒤집힌다(첫 적용에서 102군).
  표시(`*_before_correction`·`correction_reason`·`corrected_by`)를 조건 수에서 뺐다.
  전수 재측 — 양쪽에 걸면 변동 **0**, 정정 전 라이브에 걸면 **1군**(재료140 LOCA 점도, 손확인).
  **`verdict_*` 는 안 뺐다** — 빼면 재료255 가 뒤집히고, 52차 NB 의 중복 표시 규약이 그 셈에 기대고 있다.

## 안 합친 쌍
`normalize_condition_keys.NOT_MERGED` 에 사유와 함께 있다. 요약 — 환산이 필요한 것(`thickness` ↔
`thickness_um`, C ↔ K, mil ↔ mm), 층이 다른 것(`method_detail` ↔ `test_method`, 242행 공존),
축이 다른 것(`condition` ↔ `conditioning`, `type` ↔ `test_type`, `test` ↔ `test_method`),
그리고 `axis` 의 그래프축 서술 약 320행.

## 예행
`src=라이브(정정 후)` 대 `dst=정정 직전 백업(pre-w52na-20260829-014041Z)` —
`property_value added 0 · matched 41368` · `value_corrections 12049` · `correction_misses 0` ·
`fk_violations 0`. 재병합도 `added 0 · corrections 0` 으로 멱등하다.
