# 물성 카탈로그 파이프라인 — 논문·시트 한 줄이 해석 카드 한 칸이 되기까지

**무엇이 무엇으로 변환되는가.** 코퍼스의 md 파일 한 줄과 벤더 PDF의 표 한 칸이 어떤 도구를
거쳐 DB 행이 되고, 어떤 관문이 무엇을 거부하고, 어느 화면·카드 칸에 실리고,
그것이 어떻게 운영 DB까지 가는가. 이 문서 한 장이 그 전 구간을 잇는다.

- **이 문서의 자리** — `docs/COLLECTION_METHODOLOGY.md` 는 **왜·어떻게 판단하는가**(등급 체계·
  우선순위·지표·함정)를 다룬다. 이 문서는 **파이프라인**이다 — 파일·함수·표·컬럼 이름으로만 쓴다.
  판단 기준이 궁금하면 방법론을, "이 값이 어디서 왔고 어디로 가나"가 궁금하면 이 문서를 봐라.
- **수치 기준일** — 2026-09-01. 전부 라이브 DB에서 직접 뽑았고 **모든 수에 재현 질의를 붙였다.**
- **DB** — `/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db`
- 경위의 1차 사료 — `docs/PROPERTY_DATA_HISTORY.md` · 지시서 정본 — `docs/COLLECTION_BRIEF.md` ·
  함정 대장 — `docs/COLLECTION_BRIEF_CORPUS.md`(599절)

---

## 0. 한 장 요약 — 전 구간

```
 ┌── 원천 ─────────────────┐   ┌── 선별 ────────────┐   ┌── 채굴 ──┐
 │ /data/paper_patent_corpus│   │ corpus_index.py    │   │ 배치 에이전트 │
 │   /structured  20,692편  ├──▶│ mined_index.py     ├──▶│ (파동당 2~4) │
 │ 벤더 PDF/웹 데이터시트     │   │ scan_targets.py    │   │           │
 │ 논문 그래프 이미지         │   │  ↑ 기채굴 · 기폐기   │   └─────┬─────┘
 └──────────────────────────┘   └──────┬─────────────┘         │
        │ extract_datasheet.py         │                       │ JSON
        │ digitize_curve.py            ▼                       ▼
        │                    _verdicts/discarded.jsonl   backend/scripts/catalog/out_XX/*.json
        │                    (폐기 대장 · append-only)     {"materials":[…]} · {"corrections":[…]}
        │                                                      │
        └──────────────────────────────────────────────────────┤
                                                               ▼
                                              ┌──────────────────────────────┐
                                              │ ingest_agent_json.py         │ ◀── 거부
                                              │  ① 기채굴 경고                │  no_source · bad_key
                                              │  ② 출처 유무                  │  bad_unit · out_of_range
                                              │  ③ 키·단위·범위·퍼센트          │  pct_suspect · cond_clash
                                              │  ④ 조건 충돌                  │  kept_better · visc_order
                                              │  ⑤ tier1 보존                │  mat_fail(행 유실)
                                              │  ⑥ corrections(정정 선언)      │  corr_* 8종
                                              └───────────┬──────────────────┘
                                    mcp_server.register_property
                                    app/acquire/store.upsert_source / upsert_property_value
                                                          ▼
                     ┌────────────────────────────────────────────────────────┐
                     │  SQLite  material · property_definition · source ·      │
                     │          property_value(41,396행)                       │
                     └───┬──────────────────┬─────────────────┬───────────────┘
                         │                  │                 │
        ┌────────────────▼──┐   ┌───────────▼────────┐   ┌────▼────────────────────┐
        │ 검사              │   │ 대표값 선택          │   │ 정리·판정                │
        │ integrity_check   │   │ catalog_compare     │   │ tie_verdicts.py         │
        │  50항목+주의6      │   │  ._rep_rank         │   │ correction_reach.py     │
        │ coverage_report   │   │  ._tie_key          │   │ normalize_condition_keys│
        │ value_duplicates  │   │  .representative_*  │   │ value/source_duplicates │
        │ source_duplicates │   │ catalog_alternatives│   │ normalize_tiers.py      │
        └───────────────────┘   └──────────┬──────────┘   └─────────┬───────────────┘
                                           │                        │ corrections JSON
                                           ▼                        └──▶ 적재기로 되돌아감
        ┌──────────────────────────────────────────────────────────────────┐
        │ 소비면                                                            │
        │  app/dyna_export.py  build_cards()  → *MAT_001/024/006/076/THERMAL │
        │  app/routers/catalog.py  /api/catalog/{summary,materials,compare,  │
        │                            ashby,dyna,coverage}                    │
        │  frontend/src/routes/catalog*.tsx                                  │
        │  mcp_server.py  export_dyna_cards · compare_materials · …          │
        └──────────────────────────────┬───────────────────────────────────┘
                                       │ appdata-to-drive.sh (tar → Drive)
                                       ▼
        ┌──────────────────────────────────────────────────────────────────┐
        │ 운영 전파  HEAXHub/deploy/apptainer/appdata-merge-from-drive.sh     │
        │            → _materialtwin_merge.py  (자연키 + id 재매핑, 비파괴)    │
        │  ① 전역 유일 식별자  ② 자연키  ②-b 판정  ③ 정정  ④ 이동  ⑤ 출처 병합   │
        └──────────────────────────────────────────────────────────────────┘
```

---

## 1. 원천 — 값은 세 곳에서만 온다

| 원천 | 실제 경로 | 도구 | DB에 남는 흔적 |
|---|---|---|---|
| 논문·특허 전문 코퍼스 | `/data/paper_patent_corpus/structured/` (md 전문) | `corpus_index.py` (FTS5) | `source.kind='journal'` · `source.local_path` |
| 벤더 데이터시트 | 웹/PDF (로컬 보관 시 `local_path`) | `backend/scripts/catalog/extract_datasheet.py` | `source.kind='datasheet'` · `source.publisher` |
| 논문·시트의 **그래프** | 이미지 캡처 | `backend/scripts/catalog/digitize_curve.py` | `property_value.method='digitized'` |

- **코퍼스 색인** — `corpus_index.py` 가 `/data/paper_patent_corpus/_index/corpus_fts.db` 에 FTS5 색인을
  만든다. 제목으로 중복을 제거한 뒤 **20,692편**이 색인돼 있다.
  의미검색이 아니라 어휘검색인 이유는 파일 머리말이 밝힌다 — 찾는 것이 "비슷한 주제"가 아니라
  **인쇄된 숫자**(`kJ/mol`·`365 nm`·`Table 3`)이기 때문이다.
- **디지타이즈는 measured 가 아니다.** `method='digitized'` 는 `property_value` 의 CHECK 제약에
  별도 어휘로 박혀 있다(`app/models.py:300`). 인쇄된 숫자가 아니라 **그림에서 읽은 값**이라
  실측과 섞이면 안 된다.
- **텍스트 레이어가 없는 PDF** 는 `extract_datasheet.py --ocr` 이 자동 폴백한다
  (Illustrator로 만든 이미지 전용 브로슈어).

```bash
# 코퍼스 색인 편수
python3 -c "import sqlite3;print(sqlite3.connect('file:/data/paper_patent_corpus/_index/corpus_fts.db?mode=ro',uri=True).execute('select count(*) from doc').fetchone())"
```

---

## 2. 선별 — 이미 캔 것과 이미 버린 것을 먼저 뺀다

| 도구 | 파일 | 무엇을 하나 |
|---|---|---|
| 기채굴 조회 | `backend/scripts/catalog/mined_index.py` | DOI·`local_path` 디렉터리·정규화 제목·인용키(`Tsai 2013`)·재료명 **다섯 축**으로 이미 캔 논문을 찾는다 |
| 표적 선별 | `backend/scripts/catalog/scan_targets.py` | 코퍼스에서 후보를 뽑되 **기채굴**과 **기폐기**를 둘 다 거른다 |
| 폐기 대장 | `/data/paper_patent_corpus/_index/_verdicts/discarded.jsonl` | 버린 논문 한 편당 한 줄(`title`·`wave`·`verdict`·`reason`·`path`) |
| 대장 점검 | `backend/scripts/catalog/verdicts_check.py` | 대장이 헛돌거나 멀쩡한 논문을 지우고 있지 않은지 |

### 대장이 append-only 인 이유

- **행이 0인 논문은 기채굴 조회로 영영 안 걸린다.** 열어 보고 "쓸 값이 없다"고 판정해 버리면
  DB에 아무 흔적이 안 남는다 — 다음 파동이 같은 논문을 열어 같은 이유로 다시 버린다.
  조회의 문제가 아니라 **기록**의 문제라 대장이 따로 있다.
- **여러 배치가 동시에 쓴다.** read-modify-write 로 쓰면 병렬 파동이 서로를 덮는다.
  그래서 `>>` 로만 덧붙인다.
- **거짓 폐기는 논문을 잃는다.** 그래서 대조는 `scan_targets.norm_full()` 로 **자르지 않은 전체 제목**이
  정확히 맞을 때만 건다. 조회용 `norm_title()` 은 45자에서 자르는데, 그 창을 폐기에 쓰면
  접두가 겹치는 자매논문이 함께 사라진다.

현재 대장은 **98줄**이다.

```bash
wc -l /data/paper_patent_corpus/_index/_verdicts/discarded.jsonl
python3 backend/scripts/catalog/verdicts_check.py
```

---

## 3. 채굴 산출 — 배치가 내놓는 것은 JSON 하나뿐이다

배치(파동별 에이전트)는 DB를 직접 건드리지 않는다. `backend/scripts/catalog/out_XX/` 에
JSON을 떨어뜨리고 끝난다. 문서 형태는 둘이고, 한 파일에 섞여도 된다.

**① 값 문서 — `materials` 배열**

```jsonc
{"materials": [{
  "match_name": "SAC107 Solder Alloy",          // 기존 재료명(정확일치). 없으면 new_material
  "source": {"kind": "journal", "doi": "10.1007/s11664-017-5374-3",
             "title": "...", "authors": "...", "year": 2017,
             "publisher": "Springer (Journal of Electronic Materials)",
             "local_path": "/data/paper_patent_corpus/structured/rel_papers/..."},
  "properties": [{
    "key": "thermal.melting_point", "value": 492.35, "unit": "K",
    "method": "measured", "tier": 1,
    "conditions": {"phase_boundary": "solidus (DSC onset on heating)",
                   "test_method": "DSC, 10 K/min heating, N2", "temperature_c_printed": 219.2},
    "notes": "Table I ... 표 내부 검산: T end - T onset = 230.8 - 219.2 = 11.6 ..."}]}]}
```

**② 정정 문서 — `corrections` 배열**(§4.6)

`load()` 는 `materials` 도 `corrections` 도 없는 파일을 **건너뛴다** — 배치가 산출 디렉터리에
표적 목록·키 제안 같은 것을 같이 두기 때문이다(`ingest_agent_json.py:732`).
`property_keys.json`·`materials.json` 은 이름으로 제외한다.

위 스니펫의 출처는 `backend/scripts/catalog/out_ga/sac107_sac205.json` 이다(45차 GA 산출).
저장소에 커밋된 실물 예 — `backend/scripts/catalog/out_fd/fd02_fa_cover_glass.json`(값) ·
`backend/scripts/catalog/out_pb/pb01_tie_reverdicts.json`(정정).
산출 디렉터리는 파동마다 `out_<파동코드>/` 로 늘어난다(현재 커밋된 것 62파일).

---

## 4. 적재기 — 이 파이프라인의 유일한 쓰기 문

`backend/scripts/catalog/ingest_agent_json.py` · **드라이런이 기본이고 `--apply` 라야 쓴다.**

```bash
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  python3 backend/scripts/catalog/ingest_agent_json.py backend/scripts/catalog/out_XX/          # 드라이런
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/ingest_agent_json.py out_XX/ --apply  # 적용
```

적재기는 맨 먼저 **어느 DB를 치는지 찍는다**(`[DB] <url> 재료 N종 · 정의 M종`).
`MATERIALTWIN_DATA_DIR` 을 빼먹으면 저장소 기본 DB(`backend/var/data`)를 쳐서 헛돈다.

### 4.1 관문 — 무엇을 거부하나

| # | 관문 | 통계 키 | 거부 조건 | 코드 |
|---:|---|---|---|---|
| 0 | 기채굴 경고 | — | 이 DOI/경로/제목이 이미 3행 이상 캐졌다. **막지 않고 경고만** 한다(조건 다른 행은 정당) | `mined_index.look` |
| 1 | 출처 | `no_source` | `url`·`doi`·`title` 이 **셋 다** 없으면 그 항목 전체를 버린다 | `:816` |
| 2 | 재료 지정 | `no_mat` / `mat_fail` | `match_name` 도 `new_material.name` 도 없다 / 재료명 200자 초과(`material.name` VARCHAR(200)) | `:826` · `:834`,`:847` |
| 3 | 물성키 | `bad_key` | `property_definition` 에 없는 key | `:884` |
| 4 | 단위 | `bad_unit` | `unit_key(unit) != unit_key(definition.si_unit)` | `:917` |
| 5 | 물리 범위 | `out_of_range` | `RANGE[key]` 밖 | `:922` |
| 6 | 퍼센트 오입력 | `pct_suspect` | `PCT_SUSPECT` 5키가 1.0 초과 | `:926` |
| 7 | 조건 충돌 | `cond_clash` | 같은 (재료·키·출처·조건)인데 값이 다르다 — 뒤엣것이 앞엣것을 덮어 측정 하나가 사라진다 | `:933` |
| 8 | 상위 등급 보존 | `kept_better` | 같은 (재료·키·**조건**)에 tier1이 이미 있다. **조건이 다르면 통과**시킨다(별개 측정) | `:941` |
| 9 | 점도 순서 | `visc_order` | 한 유리 안에서 `viscosity_reference_temperature` 순서가 뒤집혔다 → 그 항목의 점도 행 **전체**를 버린다 | `viscosity_order_violations` · `:875` |

- **`no_source` 는 항목 단위다** — 출처가 없으면 그 항목의 물성 전부가 사라진다.
  나머지는 행 단위다.
- **조용한 유실은 요약 밖으로 끌어낸다.** `mat_fail`·`skipped_rows` 가 0이 아니면 마지막에
  경고 한 줄을 따로 낸다. 무결성 검사는 **들어오지 않은 행**을 볼 수 없어서 여기가 유일한 방어선이다.

### 4.2 `RANGE` — 범위 가드가 "물리"인 이유와 하한 0 규칙

`RANGE` 는 자릿수·단위 오입력만 막는다. **인쇄된 값을 막지 않는다.**
그 원칙을 지키느라 하한을 내린 사고가 코드 주석에 일곱 번 기록돼 있다 —
Prony 상·하한(17·19차) · `peel_strength` 0.5 → 0(21차 Q2, `0.00 N/cm` 는 "접착이 안 됐다"는 실측) ·
`tack`/`static_shear_holding`(21차 S2) · `lap_shear_strength` 1e4 → 0(21차 T1) ·
`poisson_ratio` 0.0 → **-1.0**(42차 DA, 열분해흑연 basal 면이 실제로 음수) ·
`thermal.conductivity` 3000 → 5e4(43차 EC, 베이퍼챔버 유효 11,914.9 W/(m·K)).

> **새 키는 하한 0(물리적으로 음수가 되는 것만 음수)으로 시작한다.
> 단위 오입력은 범위가 아니라 조건·notes 대조와 검사기의 물리 검산으로 잡는다.**

무차원 물성은 가드가 단위를 하나도 못 잡는다 — `poisson_ratio`·`lankford_r_value`·
`monotonic_strain_hardening_exponent` 는 자릿수 사고만 본다.

### 4.3 정규화 — 버리지 않고 옮긴다

| 함수 | 하는 일 |
|---|---|
| `norm_cat()` | `Material.category` 를 고정 어휘 7종으로(`polymer`·`composite`·`ceramic`·`metal`·`molecular`·`rubber`·`foam`) |
| `norm_kind()` | `source.kind` 를 CHECK 어휘 8종으로 |
| `norm_method()` | `method` 를 고정 어휘로. **시험법 서술은 버리지 않고** `conditions.test_method` 로 옮긴다 |
| `force_computed_if_midpoint()` | notes가 "구간 중앙값"을 주장하면 `method` 를 `computed` 로 강제하고 `conditions.method_before_correction` 에 옛 값을 남긴다 |
| `pick_tier()` / `norm_tier()` | tier를 1~5로 |
| `pick_publisher()` | 데이터시트면 업체명을 `source.publisher` 에 1급으로 |
| `as_cond()` / `cond_sig()` | 조건을 dict로. 서술 문자열이면 **그 문자열 자체를 서명으로 쓴다**(빈 서명으로 뭉개면 다른 측정이 같은 조건으로 판정돼 덮어쓰기가 난다) |

### 4.4 실제 쓰기 — 두 함수

적재기는 SQL을 직접 쓰지 않고 `mcp_server.register_property()` 를 부른다. 그 안에서 둘이 돈다.

- `app/acquire/store.upsert_source()` — 출처 dedup 우선순위 **doi > content_hash > url**,
  식별자가 하나도 없을 때만 (title, kind) 로. 빈 문자열은 `None` 으로 정규화한다
  (`doi=''` 가 저장되면 UNIQUE 제약에 걸려 두 번째 무DOI 출처부터 적재가 통째로 죽는다).
- `app/acquire/store.upsert_property_value()` — **(재료·키·출처·조건)에 멱등**.
  같으면 갱신, 다르면 삽입. 이 넷이 사실상의 자연키다.

### 4.5 tier 재판정

`backend/scripts/catalog/normalize_tiers.py --apply` 가 tier를 **"문서 종류"가 아니라
"값의 성격"** 으로 다시 판정한다. `NOT_A_DIRECT_MEASUREMENT` 정규식(계열·클래스·추정·
digitized·midpoint·`class value`…)에 하나라도 걸리면 승격하지 않는다.
`grade_scope` 는 양방향으로 쓰이므로 존재만 보고 일괄 강등하지 않는다.

### 4.6 정정 — 적재기가 기존 행을 고칠 수 있는 **유일한** 길

`corrections` 배열로 **정정임을 선언**했을 때만 일어난다. **암묵적 정정은 없다.**

```jsonc
{"corrections": [{
  "target": {"property_value_id": 1499},                       // 또는 재료+키+조건+값으로 유일하게
  "reason": "왜 고치는지 — 10자 미만이면 거부",
  "evidence": "등급을 **올릴** 때만 추가로 요구",
  "by": "55차 QC",
  "set": {"quality_tier": 4, "conditions": {...}, "notes": "..."}}]}
```

| 거부 사유 | 통계 키 |
|---|---|
| 대상 미지정 | `corr_no_target` |
| 사유 10자 미만 | `corr_no_reason` |
| 대상 0건 | `corr_no_match` |
| **대상 2건 이상** — 어느 행인지 우리가 고르면 그건 우리 판정이 된다 | `corr_multi_match` |
| `set` 이 비었다 / 이미 그 값이다 | `corr_no_change` |
| 정정 불가 칸(`property_key`·`material_id`) · 단위·범위·퍼센트 가드 · 등급 상향 규율 | `corr_rejected` |
| 정정하면 다른 행과 (재료·키·출처·조건)이 같아진다 | `corr_would_duplicate` |

- **고칠 수 있는 칸** — `CORRECTABLE = {value, value_text, unit, method, quality_tier, conditions, notes}`.
  `property_key`·`material_id` 는 정정이 아니라 **이동**이라 여기 없다(§6.3).
- **새 값은 삽입과 같은 가드를 통과해야 한다.** 정정이 우회로가 되면 안 된다.
- **등급 상향은 더 엄격하다**(`check_tier_upgrade`) — `evidence` 를 사유와 별도로 요구하고,
  t1으로 올리려면 `method` 가 `measured`·`digitized` 여야 한다.
- **되돌리기 표시** — 바뀐 칸마다 `<칸>_before_correction` 을 조건에 남기고
  `correction_reason`·`corrected_by`(+`correction_evidence`)를 붙인다.
  **이 표시가 병합기가 운영 행을 찾는 열쇠다**(§7.3).
- **정정은 삽입이 다 끝난 뒤에 돈다** — 같은 파일이 새 행을 넣고 옛 행을 고칠 수 있다.
- **이름 공간 충돌 방어** — 조건 칸 이름이 컬럼 이름(`value`·`unit`·`method`·`tier`·`notes`)과
  겹치면 `conditions.` 접두어를 붙인다. 안 붙이면 병합기가 조건 칸의 표시를 **컬럼의 옛 값**으로
  읽어 정정을 못 찾는다(52차 NA 실측 483행).

---

## 5. DB — 표 넷이 전부다

```
material ──1:N── property_value ──N:1── source
                      │
                      └──N:1── property_definition (key 참조. id 참조 아님)
```

| 표 | 자연키(병합기 기준) | 비고 |
|---|---|---|
| `material` | `name` | `material_code` 는 다수 NULL이라 못 쓴다. `attributes` JSON에 `role`·`subsystem`·판정 키 |
| `property_definition` | `key` | UNIQUE·NULL 0. `app/property_taxonomy.py` 가 정의 원본 |
| `source` | `kind, doi, isbn, url, title, publisher, license` | `authors`·`year` 는 **나중에 채워지는 보강 필드**라 자연키에서 뺐다 |
| `property_value` | `material_id, property_key, value_num, value_text, unit, conditions, method, source_id` | **정정이 바꾸는 칸이 전부 자연키 안에 있다** — §7의 모든 복잡성이 여기서 나온다 |

`property_value` 의 어휘 제약(`app/models.py`) —
`method IN ('measured','handbook','datasheet','computed','estimated','digitized')` ·
`quality_tier BETWEEN 1 AND 5`.
`conditions` 는 `JSON(none_as_null=True)` 다 — 이게 없으면 파이썬 `None` 이 문자열 `'null'` 로
저장돼 조건 조회가 전부 빗나간다. 그리고 `app/db.py:_json_dumps` 가 `ensure_ascii=False` 로
저장한다 — 한글이 `\uXXXX` 로 escape되면 한국어 정규식 검색이 반쪽만 본다.

### 조건 안에 사는 것 — 측정 조건과 **살림살이**

`conditions` 에는 세 종류가 섞여 산다. 조건을 세거나 읽는 코드는 뒤 둘을 반드시 걷어내야 한다.

| 갈래 | 예 | 걷어내는 함수 |
|---|---|---|
| 실질 조건축 | `temperature_k` · `direction` · `frequency_hz` · `grade` | — |
| 되돌리기·사유 | `*_before_correction` · `correction_reason` · `corrected_by` | `coverage_report.is_housekeeping_cond()` · `catalog_alternatives._is_bookkeeping()` |
| 판정·계보 | `verdict_*` · `moved_from_material` · `moved_from_source` · `direction_verbatim` | 〃 |

**판정을 조건에 적으면 그 판정이 조건축으로 세어진다** — 대표값 순위의 5번째 자리가
`len(conditions)` 라서, 한 군의 일부 행에만 칸을 더하면 **대표값이 뒤집힌다.**
`tests/test_rep_rank.py` 가 이것을 양방향으로 못박아 두었다.

---

## 6. DB 안에서 값을 고치는 세 갈래

값은 넣기만 하는 게 아니다. 세 갈래로 고치는데, **세 갈래 모두 자연키의 어느 칸을 건드리므로
병합기에 대응 분기가 하나씩 있다.**

| 갈래 | 무엇이 바뀌나 | 조건에 남는 표시 | 병합기 분기 |
|---|---|---|---|
| **정정** | `value_num`·`unit`·`method`·`tier`·`conditions`·`notes` | `<칸>_before_correction` + `correction_reason` | ③ |
| **판정** | `conditions` 에 `verdict_*` 칸만 더한다. 값은 한 칸도 안 바꾼다 | `verdict_tie_axis` · `verdict_tie_note` | ②-b |
| **이동** | `material_id`(값 이동) 또는 `source_id`(출처 병합) | `moved_from_material` · `moved_from_source` | ④ · ⑤ |

### 6.1 판정 — `tie_verdicts.py`

`backend/scripts/catalog/tie_verdicts.py` 가 **대표값 동률**(선택기가 못 가른 것)을 세고,
왜 갈렸는지 분류하고, 그 분류를 `corrections` 선언으로 낸다.
**값을 고치지도 버리지도 않는다** — `conditions` 에 두 칸만 더한다.

규율 둘이 코드 머리말에 박혀 있다.
① **한 군의 모든 행에 같은 수의 칸**을 더해라(안 그러면 `_rep_rank` 5번째 자리가 뒤집힌다).
② **전파 불가능한 군은 건너뛰어라** — `gen` 이 자동으로 뺀다.

### 6.2 정정 도달성 — `correction_reach.py`

`backend/scripts/catalog/correction_reach.py` 는 **병합기의 정정 분기와 같은 자로**
"이 정정이 운영까지 갈 수 있는 행인가"를 미리 잰다. `reachable()` 은 그 분기의 거울이고,
둘이 어긋나면 예행에서 `correction_misses` 로 즉시 드러난다.

> **"dev 에서 고친 것이 운영에 가는가" 가 모든 정리의 합격 조건이다**(§464·522·536·579).
> 이 도구가 그 질문을 정리 **전에** 대신 한다.

### 6.3 이동 — 묘비 규약

값을 다른 재료로 옮기면 원 재료가 물성 0행이 된다. 그래서 **묘비**를 세운다.

```jsonc
"merge_verdict": "moved",
"merge_moved_to": "S45C_medium_carbon Bilinear",     // ← id 가 아니라 **이름**이다
"merge_moved_keys": ["mechanical.fatigue_strength_coefficient", "..."],
"merge_reason": "...", "merge_moved_at": "2026-08-28"
```

**`merge_moved_to` 에 id를 적으면 안 된다.** id는 정수 autoincrement라 dev와 운영에서
같은 id가 다른 행일 수 있고, `merge_` 접두어는 큐레이션이라 dev 값이 운영에 그대로 덮인다.
**이름이 재료의 자연키다.** 검사기가 `json_type(...) <> 'text'` 로 정수 표기를 위반으로 잡는다.

검사기 세 항목이 묘비를 지킨다 — `물성값 0인 재료`(묘비는 면제) ·
`묘비 선언이 깨졌다`(반쪽 선언·존재하지 않는 대상) · `묘비가 옮겼다는 키가 대상에 없다`(값이 사라졌다).

---

## 7. 병합기 — dev 에서 고친 것이 운영에 가는가

```
dev(라이브 DB) ──appdata-to-drive.sh──▶ Drive: app-data/latest/app-data.tar.gz
                                            │
      cae00 운영 ◀──appdata-merge-from-drive.sh──┘
                        └─▶ python3 _materialtwin_merge.py <dev.db> <운영.db>
```

`HEAXHub/deploy/apptainer/_materialtwin_merge.py` — **비파괴**다. 운영 기존 행은 유지하고,
자연키로 대응행을 찾아 없으면 INSERT(새 id) + 자식 FK 재매핑한다.
merge 직전에 운영 DB를 `*.pre-merge-<UTC>` 로 자동 백업한다.

### 7.1 대응행을 찾는 순서

| 단계 | 축 | 왜 |
|---|---|---|
| ① | `UNIQUE_FIRST` — `source` 의 `doi`/`isbn`/`content_hash` | 그 자체가 전역 유일 식별자다. 제목·URL은 나중에 교정되는 표시 정보라 자연키로만 보면 같은 문헌을 놓치고 UNIQUE에 걸려 병합이 죽는다 |
| ② | 표별 자연키(`PLAN`) | 기본 경로 |
| ②-c | **출처 병합 선언 행은 조회축을 옛 `source_id` 로 바꾼다** | ③·④·⑤가 전부 `source_id` 로 좁히는데 병합이 바꾼 칸이 바로 그것이다 |
| ②-b | 자연키 − `verdict_*` | 판정 한 칸이 붙으면 `conditions` 가 자연키 안이라 못 찾는다. 빼고 찾아 **판정만 얹는다** |
| ③ | 정정 전 값 (`*_before_correction` 으로 복원) | 자연키가 값·조건·method를 포함하는데 정정이 바로 그 칸들을 바꾼다 |
| ④ | 옛 재료 이름 (`moved_from_material`) | 자연키가 `material_id` 를 포함한다 |
| ⑤ | 옛 출처의 자연키 (`moved_from_source`) | 자연키가 `source_id` 를 포함한다 |

- **③·④·⑤ 모두 못 찾으면 값을 버리지 않고 삽입한다** — 운영에 아직 없는 값일 수 있고,
  값을 버리는 쪽이 더 위험하다. 다만 **조용히 넘기지 않는다** —
  `correction_misses`·`move_misses`·`source_move_misses`·`verdict_misses` 로 크게 보고한다.
- **유일하지 않으면 갱신하지 않는다.** 어느 행인지 병합기가 고르면 그건 병합기의 판정이 된다.
- **②가 ③보다 먼저 도는 순서라 재병합에 멱등하다** — 이미 전파된 정정은 ②에서 걸린다.
- **조건 텍스트로는 대조하지 않는다.** JSON 직렬화가 양쪽에서 글자까지 같으리라 기대할 수 없다.
  대신 옛 `value_num`/`value_text`(+정정이 실제로 바꾼 옛 unit·method)로 좁히고,
  §579 이후로는 **조건을 사전으로 파싱해** 대조한다(`prior_conditions`·`_condition_core`).

### 7.2 큐레이션 전파 — 재료 `attributes`

병합기는 삽입만 하므로 **이미 있는 재료의 attributes 는 원래 영원히 안 갔다**
(43차 EA가 계통 태그 346종을 붙였는데 전파 0건). 그래서 **판정 계열 키만** 예외로 반영한다.

```python
CURATION_KEYS = {"role","role_reason","role_basis","role_confidence","subsystem","subsystem_basis"}
CURATION_PREFIXES = ("core_", "merge_", "same_alloy_", "verdict_")
```

- **판정은 값과 다르다** — "이게 제품인가 시편인가"·"같은 재료인가"는 출처에서 나오는 게 아니라
  dev에서 사람이 정한다. 정본이 한쪽뿐이라 dev를 정본으로 반영한다.
- **지우지는 않는다.** dev에 없는 키는 운영 값을 그대로 둔다.
- **접두어를 좁게 유지하는 이유** — 명세(두께·조성 같은 것)가 섞이면 병합이 값을 덮는다.
  **배치가 판정 키를 만들 때는 이 접두어를 써라.**
- 반대로 `instrument` 의 `owned`·`owner_name`·`owner_contact` 는 **현장이 정본**이라
  덮지 않고 `ownership_diffs` 로 다르다는 사실만 드러낸다.

### 7.3 삭제는 없다

**병합은 비파괴다. dev에서 지운 행은 운영에 그대로 남고 되돌아오지도 않는다.**
그래서 값 정리는 **삭제가 아니라 표시**여야 한다 — `value_duplicates.py`·`source_duplicates.py`
둘 다 한 행도 지우지 않고 찾아서 부류로 가르기만 한다.
(옛 `dedupe_values.py`·`merge_duplicate_sources.py` 는 지운다. 쓰지 마라.)

### 7.4 표를 새로 만들면 `PLAN` 에 넣어라

`PLAN` 에 없는 표는 통째로 안 간다. 실제로 두 번 났다 —
카탈로그 3표(`property_definition`·`source`·`property_value`)가 빠져 운영이 **재료 548건인데
물성값·출처가 전부 0** 이었고, `instrument`·`instrument_capability` 750행이 통째로 안 갔다.
운영에 표가 아예 없으면 `[skip]` 로 몇 행이 안 갔는지 말한다(배포 순서상 merge가 앱 기동보다 먼저라
새 표는 첫 배포에서 반드시 이 가지로 빠진다).

---

## 8. 검사 — 배포 전 관문

### 8.1 무결성 — `integrity_check.py`

```bash
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  python3 backend/scripts/catalog/integrity_check.py     # 0이 아니면 배포 금지, exit 1
```

**DB 경로를 박아 두지 않는다** — 환경변수를 읽어야 적용 전 백업과 적용 후 라이브를 각각 쳐서
diff를 뜰 수 있다. 53차 OB가 그걸 시도했는데 두 출력이 글자까지 같았다(둘 다 라이브를 쳤다).
**검사기가 스냅샷을 못 치면 배치는 자기가 무엇을 깼는지 모른다.**

항목 구성 — **SQL 45 + 파이썬 5 = 50항목**, 그리고 **주의 6블록**.
(파일 머리말의 "37항목 + 주의 1항목"과 방법론 부록 B의 "37항목"은 **낡았다.** 아래 명령으로 센다.)

```bash
grep -c '^    ("' backend/scripts/catalog/integrity_check.py   # 45  (SQL)
grep -c 'bad += 1 if'  backend/scripts/catalog/integrity_check.py # 5  (파이썬)
grep -c '\[주의\]'      backend/scripts/catalog/integrity_check.py # 6  (주의 블록)
```

무엇을 보나 — 갈래로 묶으면 여섯이다.

| 갈래 | 항목 예 |
|---|---|
| 참조·필수 | 출처 없는 값 · 끊어진 출처 참조 · 정의 없는 물성키 · 고아 시편 · 값·텍스트 모두 없음 · 제목 없는 출처 · journal인데 DOI 없음 |
| 어휘·형식 | 단위가 정의와 다름 · tier 범위 밖 · method 어휘 밖 · 출처 kind 어휘 밖 · category 어휘 밖 · 조건이 dict 아님 |
| 조건 필수 | 초탄성인데 model 없음 · 파장 없는 광학값(tier<4) · 온도가 값인데 시험온도 조건 · 확산계수에 온도 없음 · 노화 유지율 조건 불완전 · 파장이 가시광 밖 |
| 세트 정합 | Prony 항번호/항수 · Basquin·Coffin-Manson·Morrow·Darveaux·Stromeyer 쌍 · 항번호 없는 다항 상수 · LCSR 가로축 비단조 |
| 물리 검산 | Mooney-Rivlin G0 음수(Drucker) · **(BH)max ≤ Br²/(4μ₀)** · 점도 기준점 순서 역전 · 비금속인데 비열이 금속급 |
| 등급·근거 | tier4인데 실측·핸드북 · 우리 추정인데 tier4 아님 · 가정값인데 근거 출처 없음 · 중앙값인데 실측 표기 · datasheet인데 식별자도 실측도 없음 |
| 묘비 | 물성값 0인 재료 · 묘비 선언이 깨졌다 · 묘비가 옮겼다는 키가 대상에 없다 |

**주의 6블록은 결함이 아니다**(`bad` 에 안 센다). 방향을 지어내 검사를 통과시키는 것도,
아는 위험을 안 알리는 것도 안 되기 때문이다.

| 주의 | 현재 | 왜 결함이 아닌가 |
|---|---:|---|
| 열적 이방성 재료인데 k에 방향이 없다 | 132건 | 원문에 방향이 없으면 지어내지 않는다. 해석에서 등방으로 쓰지 말 것 |
| 소자 유효 k를 재료 k 키에 담았다 | 4종 | 인쇄값이고 소자 해석에는 정당하다. **재료로 비교·순위·카드추출하면 틀린다** |
| 같은 출처에 1차값이 완전히 같은 재료쌍 | 14건 | 중복 적재일 수도, 등급 다른 대리값일 수도 있다. **자동 삭제 금지** |
| Tg 위 CTE > 1000 ppm/K 인데 표식 없음 | 0건 | TMA 프로브 침강 인공산물일 수 있다 |
| 항복 > 인장 | 21종 | 물리적으로 불가능하나 자동 판정 못 한다(조건·출처가 갈린다). 사람이 볼 목록 |
| 계통 판정이 안 된 재료 | 0건 | 값 결함이 아니라 **조사 사각지대**다 |

### 8.2 커버리지 — `coverage_report.py`

```bash
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/coverage_report.py
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/coverage_report.py --json
```

지표 정의·구조적 부재 선언·반례 검증이 전부 이 파일에 있다.
**격자 밖 재료를 뺀다** — `role='evidence'`(근거 재료) · `role='out_of_scope'`.
`role` 이 아예 없으면 **조용히 product 로 센다**(그래서 검사기가 `role` 없음을 주의로 낸다).

### 8.3 중복 — 지우지 않고 가른다

```bash
python3 backend/scripts/catalog/value_duplicates.py    # 물성값
python3 backend/scripts/catalog/source_duplicates.py   # 출처
```

- **출처가 값보다 앞이다.** 값 중복 검출의 묶음 키에 `source_id` 가 들어 있어서,
  같은 시트가 출처 두 행으로 들어오면 값 중복 검출이 통째로 눈을 감는다.
- **`local_path` 단독은 지문이 아니다** — Doosan CCL 편찬 PDF 한 경로가 55개 제품 페이지 출처에
  찍혀 있다. 같은 경로 **+ 같은 정규화 제목**일 때만 지문으로 쓴다.
- **URL 쿼리를 떼지 마라** — `azom.com/properties.aspx?ArticleID=…` 은 쿼리로 페이지가 갈린다.
  떼었다가 1,014행 오탐이 났다.

---

## 9. 대표값 선택기 — 한 재료·한 물성에 행이 여럿일 때

`backend/app/catalog_compare.py`

```python
def _rep_rank(pv) -> tuple:
    primary = (_wavelength_distance(pv.conditions) if key.startswith("optical.")
               else _temp_distance(pv.conditions))
    return (1 if is_non_solid(pv.conditions) else 0,   # ① 고체 우선(용융값 뒤로)
            pv.quality_tier or 9,                      # ② 신뢰등급
            0 if pv.value_num is not None else 1,      # ③ 수치 보유
            primary,                                   # ④ 지배 조건 근접(광학=파장, 그 외=온도)
            _condition_axis_count(pv.conditions),      # ⑤ 조건 적음
            pv.id)                                     # ⑥ 적재 순서
```

- **`method` 는 일부러 안 본다**(50차 LA). 이 DB에서 `method` 는 품질 축이 아니다 —
  같은 `midpoint_of_range` 행 211개가 computed 124·measured 63·handbook 24로 갈려 있어
  계보가 같은 행이 라벨만으로 순위가 갈린다. 넣어 보니 26쌍이 뒤집혔고 개선은 2건뿐이었다.
- **`_tie_key()` = `_rep_rank()[:-1]`** — 이게 같은 두 행은 **선택기가 못 가른다.**
  `representative_ties()` 가 그런 행을 찾아 **드러낸다**(자동으로 고르지 않는다).
- **순위를 더 만들지 않는다.** 축을 더 넣어 보니(method·온도축) 개선보다 개악이 많았다.
  대신 어느 쪽을 쓸지는 해석자가 정하게 화면·카드·API에 후보를 노출한다.
- `_TIE_REL_TOL = 0.01` — 반올림 쌍둥이(7.85 대 7.8)까지 세면 소음이 된다.

소비자 — `representative_numeric()`(값만) · `representative_rows()`(행 전체, **프로비넌스는
반드시 대표로 뽑힌 그 행의 출처를 쓴다**) · `property_ranking()` · `build_comparison()` ·
`scatter_dataset()`(Ashby).

동률·대안을 화면 payload로 만드는 것은 `backend/app/catalog_alternatives.py` —
`index_from_rows()` · `tie_info()` · `separated_by()` · `condition_diff()` ·
`annotate_comparison()` · `annotate_ranking()` · `annotate_scatter()`.

---

## 10. 소비면 — 값이 실제로 어디에 실리나

### 10.1 LS-DYNA 카드 — `app/dyna_export.py:build_cards()`

| 카드 | 필요한 값 | 자동 선택 조건 |
|---|---|---|
| `*MAT_GENERAL_VISCOELASTIC` (076) | 밀도 + 카탈로그 Prony 다항 세트 + K0(또는 G0·ν, E·ν로 유도) | 문헌 Prony 세트가 있으면 **최우선** |
| `*MAT_VISCOELASTIC` (006) | 밀도 + 업로드된 완화시험 Prony 단일항 | 업로드 시험이 있을 때 |
| `*MAT_PIECEWISE_LINEAR_PLASTICITY` (024) | 밀도 + E + (SIGY 또는 UTS+연신) | 소성 입력이 있을 때 |
| `*MAT_ELASTIC` (001) | **밀도 + E** (PR 없으면 0.3, 점탄성계는 0.45 폴백) | 그 외 |
| `*MAT_THERMAL_ISOTROPIC` | **밀도 + 비열 + 열전도율** | `card='thermal'`/`'both'` |
| `*DEFINE_CURVE` (CTE·LCSR) | CTE(PART 단위라 PID 필요) · `yield_strength_at_rate` | 있으면 추가 |

필수 물성이 없으면 **조용히 기본값으로 채우지 않고** `skipped` 에 사유와 함께 보고한다.
Prony가 있는데 밀도만 없으면 *"076은 영률을 쓰지 않으니 **밀도만** 채우면 바로 나온다"* 라고
정확히 말한다.

카드가 드러내는 것 — 자동으로 고르지 않고 **주석으로 낸다**.

- `$   ※ PR 의 다른 방향 후보 — in-plane -0.1 #38167` (`direction_options`)
- `$   **주의: 방향이 섞였다** — E 는 in-plane, PR 은 through-thickness 에서 뽑혔다` (`_direction_clash`)
- `$   **주의: 대표값이 동률이다** — … 적재 순서로 골랐다 (진 쪽 …)` (`_tie_note`)
- `$   ※ 후보 지정 — …` (`choices={물성키: "#4711"|"direction=in-plane"}`, `resolve_choice`)
- 각 값 아래 `<- [n] 출처` + 덱 끝의 번호 매긴 참고문헌(`_prov_tag`·`refs`)
- **용융 상태 값은 열 카드에서 끊는다**(`is_non_solid`) — 사출 충전 해석용이라 고체 열해석
  입력이 아닌데 수치대가 비슷해 조용히 틀린다.

### 10.2 API — `app/routers/catalog.py` (`/api/catalog`)

| 엔드포인트 | 내는 것 |
|---|---|
| `GET /summary` | 재료·정의·값 수, 계통·등급·도메인 패싯 |
| `GET /materials` | 목록·필터·패싯 |
| `GET /materials/{mid}` | **모든 행**을 도메인별로. 행마다 `representative`·`n_candidates`·`tie`·`separated_by` |
| `GET /definitions` · `/axes` · `/coverage` | 물성 정의 264종 · Ashby 축 · 커버리지 |
| `GET /compare` | 대표값 매트릭스 + 칸마다 후보 수·대안·동률(`annotate_comparison`) |
| `GET /ashby` | 산점도 데이터셋 |
| `POST /dyna/match` · `POST /dyna/build` · `GET /dyna` | 재료 해석·카드 덱 생성 |
| `GET /materials/{mid}/curve` | 합성 σ-ε 곡선 |

화면 — `frontend/src/routes/catalog.tsx` · `catalog-material.tsx` · `catalog-compare.tsx` ·
`catalog-ashby.tsx` · `catalog-dyna.tsx`.

MCP — `backend/mcp_server.py` 의 `list_materials` · `get_material_properties` ·
`compare_materials` · `search_catalog_property` · `export_dyna_cards` · `plot_ashby` 등.
**MCP 서버는 `MATERIALTWIN_DATA_DIR` 이 가리키는 DB를 본다** — 기본 폴백은 저장소 개발 DB라
카탈로그 쓰기에 쓰면 엉뚱한 DB에 쓴다.

---

## 11. 실례 하나 — 재료 2361을 끝까지 따라간다

**왜 이 행인가** — 방향이 갈리고, 원문 PDF가 부호 글리프를 잃었고, 범위 가드를 실제로 바꿨고,
동률 판정이 붙었고, 조건 어휘 통일 정정을 두 번 받았고, 카드에서 경고 셋을 낸다.
한 행이 이 파이프라인의 관문 대부분을 지난다.

### ① 원천

```
/data/paper_patent_corpus/structured/mech_papers/12_graphite_thermal/
  Yao - 2003 - Developing rapid heating and cooling systems using pyrolytic graphite/
  └─ ….md          ← source.local_path 에 이 경로가 그대로 들어간다
```

### ② 출처 행 (`source` 4543)

| 칸 | 값 |
|---|---|
| `kind` | `journal` |
| `doi` | `10.1016/S1359-4311(02)00191-6` |
| `title` | Developing rapid heating and cooling systems using pyrolytic graphite |
| `authors` / `year` | Yao / 2003 |
| `local_path` | 위 md 경로 |

### ③ 값 두 행 — 같은 표, 같은 칸, 방향만 다르다

Yao 2003 **Table 1 `Poisson ratio` 행**의 두 열이 두 행이 됐다.

| | pv **38166** | pv **38167** |
|---|---|---|
| `property_key` | `mechanical.poisson_ratio` | 같음 |
| `value_num` / `unit` | **0.3** / `1` | **-0.1** / `1` |
| `method` / `quality_tier` | `measured` / **3** | 같음 |
| `source_id` | 4543 | 4543 |
| `conditions.direction` | `through-thickness` | `in-plane` |
| `conditions.direction_verbatim` | `through-thickness / c-axis (z)` | `in-plane / basal plane (x, y)` |
| `conditions.class_value` | `true` | 같음 |
| `conditions.grade_scope` | `class value — 'PG' 일반값(Minerals Technologies 자료)` | 같음 |

**등급이 3인 이유가 행 안에 적혀 있다** — 본문이 *"Typical properties … listed in Table 1 [6]"* 이고
`[6] = Material data from Minerals Technologies Inc.` 다. 즉 **벤더 자료의 2차 인용**이라 tier3다.

**-0.1의 부호를 확정한 근거 셋**(notes verbatim) —
① docling 셀 bbox 폭 17.06 pt로 같은 행 `0.3`(11.39 pt)보다 넓어 앞에 글자가 하나 더 있다.
② 같은 표 CTE 행이 `0 : 5 \x02 10 \x00 6` 처럼 지수 부호를 통째로 잃었다(이 PDF는 부호 글리프가 깨진다).
③ 제조사 MINTEQ Pyroid HT 기술자료가 XY(basal) **-0.18** · Z 0.20을 인쇄한다.

### ④ 관문 통과 — 하한 가드를 실제로 바꾼 행

이 값이 **적재기의 `RANGE` 를 바꿨다.**

```python
# [2026-08-19 · 42차 DA] 하한 0.0 → -1.0. **인쇄된 값을 범위 가드가 막는 사고 — 여섯 번째다**
# 열분해흑연(PG)의 basal 면은 실제로 음수이고, 제조사 시트(MINTEQ Pyroid HT)가 XY -0.18 을 인쇄한다.
"mechanical.poisson_ratio": (-1.0, 0.5),
```

같은 재료의 열전도율 두 행(346 · 1.73 W/(m·K))은 **다른 검산**을 통과했다 —
초록 verbatim *"a factor of 200 in thermal conductivity difference"* 이고 346/1.73 = 200.0이다.
전기저항률 두 행도 0.003/2.5e-6 = 1200.0으로 *"a factor of 1200"* 을 정확히 재현한다.

### ⑤ 판정 — 51차 MA가 동률을 박았다

두 행 다 `quality_tier=3` · 같은 조건 수 · 온도 거리 같음 → **`_tie_key` 가 같다.**
선택기가 못 가른다. 그래서 두 행 **모두**에 같은 수의 칸이 붙었다.

```
verdict_tie_axis : "51차 MA — 다른조건 — 방향"
verdict_tie_note : "[51차 MA 동률 판정] 축이 다르므로 **둘 다 대표다** — 어느 쪽을 쓸지는
                    해석자가 정한다. 이 행이 대표로 뽑혀 있다. 이 행 = 0.3 1
                    [direction=\"through-thickness / c-axis (z)\"]. 동률 경쟁행 = -0.1 1
                    [direction=\"in-plane / basal plane (x, y)\"]. 갈린 조건키 = direction."
```

### ⑥ 정정 — 52차 NA가 조건 어휘를 통일했다

`direction` 값이 `"through-thickness / c-axis (z)"` 라는 자유서술이었다.
정규값과 원문을 갈랐다 — `direction` 은 어휘로, 원문은 `direction_verbatim` 으로.

```
direction_before_correction : "through-thickness / c-axis (z)"
direction_verbatim          : "through-thickness / c-axis (z)"
correction_reason           : "조건 어휘 통일(브리프 547·551) — 값·단위·등급·method·출처는
                               그대로다. direction 정규화 → through-thickness
                               | 앞 정정 사유(51차 MA): 대표값 동률 판정 …"
corrected_by                : "52차 NA"
```

**앞 정정의 사유가 지워지지 않았다** — 칸을 늘리지 않고 그 칸 안에 `|` 로 쌓았다.
이 `*_before_correction` 표시가 병합기 분기 ③의 열쇠다.

### ⑦ 대표값 — 방향이 갈리는 카드가 나온다

`build_cards(db, [2361], card='both')` 의 실제 출력을 줄여 옮긴다.

```
$ --- MID 1: Pyrolytic graphite (PG), bulk CVD as-deposited (Minerals Technologies  ---
$   RO  2.2000e-9 tonne/mm^3 (= 2200 kg/m^3)   <- [1] Developing rapid heating and cooling…
$   E   20000 MPa   <- [1] …  (in-plane)
$   PR  0.3         <- [1] …  (through-thickness)
$   **주의: 방향이 섞였다** — E 는 `in-plane`, PR 은 `through-thickness` 에서 뽑혔다.
$     등방 카드는 한 방향의 짝으로만 성립한다. 이방성 재료면 *MAT_ORTHOTROPIC 계열을 …
$   ※ PR 의 다른 방향 후보 — `in-plane` -0.1 #38167
$   **주의: 대표값이 동률이다** — PR 는 순위가 같은 후보 2개에서 적재 순서로 골랐다 (진 쪽 -0.1 #38167)
*MAT_ELASTIC_TITLE
         1 2.2000e-9     20000       0.3       0.0       0.0       0.0
$   TC  346 tonne*mm/(s^3*K)   <- [1] …  (in-plane)
$   ※ TC 의 다른 방향 후보 — `through-thickness` 1.73 #35344
$   ※ CTE 의 다른 방향 후보 — `through-thickness` 6.5000e-6 #35346
*MAT_THERMAL_ISOTROPIC_TITLE
```

**카드가 선다. 그리고 무엇이 위험한지 세 줄로 말한다.**
`-0.1`을 `20 GPa`(basal E)와 짝지으면 auxetic 카드가 되는데, 그 경고가 pv38167의 notes에도
이미 적혀 있다. 값을 지어내지도, 위험을 감추지도 않는 것이 이 파이프라인의 계약이다.

```bash
# 이 실례 재현
python3 - <<'PY'
import sqlite3
c=sqlite3.connect('file:/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db?mode=ro',uri=True)
for r in c.execute("select id,property_key,value_num,unit,method,quality_tier,source_id,conditions,notes"
                   " from property_value where material_id=2361 order by property_key"): print(r,"\n")
PY
cd backend && MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web python3 -c "
from app.db import SessionLocal; from app.dyna_export import build_cards
with SessionLocal() as s: print(build_cards(s,[2361],card='both')['keyword'])"
```

---

## 12. 현황 — 지금 무엇이 얼마나 있는가

전부 라이브 DB(`/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db`)
직접 조회다. 아래 `SQL:` 은 그대로 붙여 재현할 수 있다.

### 12.1 총량

| | 수 | 질의 |
|---|---:|---|
| 재료 | **2,654** | `select count(*) from material` |
| 물성값 | **41,396** | `select count(*) from property_value` |
| 출처 | **2,945** | `select count(*) from source` |
| 물성 정의 | **264** (값이 붙은 것 262) | `select count(*) from property_definition` / `select count(distinct property_key) from property_value` |
| 값이 하나도 없는 정의 | 2 (`chemical.hydrolysis_rate_constant` · `mechanical.hardness_martens`) | `select key from property_definition where key not in (select distinct property_key from property_value)` |

### 12.2 재료 — 역할·계통·계통수

```sql
select json_extract(attributes,'$.role') r, count(*) from material group by 1 order by 2 desc;
```
| role | 종 | 뜻 |
|---|---:|---|
| `evidence` | **1,723** | 근거 재료 — 커버리지 격자 **밖** |
| `product` | **864** | 격자 안. 모든 커버리지 지표의 모수 |
| `out_of_scope` | **67** | 도메인 밖 제품 |

```sql
select category, count(*) from material group by 1 order by 2 desc;
```
polymer 805 · composite 736 · ceramic 535 · metal 320 · **molecular 172** · rubber 57 · foam 29.

```sql
select json_extract(attributes,'$.subsystem') s, count(*) from material group by 1 order by 2 desc;
```
pcb 182 · housing 160 · packaging 115 · display 79 · thermal 69 · camera 41 · magnetics 39 ·
battery 37 · rf 24 · passive 17 · acoustics 15 · semiconductor 13 · wlp 11 · coating 7 ·
sensor 6 · emi 3 · **NULL 1,836**.
NULL 1,836 중 대부분은 격자 밖 근거 재료다 — **`role='product'` 인데 계통이 없는 것은 85종**이다.
```sql
select count(*) from material
 where json_extract(attributes,'$.role')='product'
   and coalesce(json_extract(attributes,'$.subsystem'),'')='';   -- 85
```

### 12.3 값 — 등급·방법·출처

```sql
select quality_tier, count(*) from property_value group by 1 order by 1;
select method, count(*) from property_value group by 1 order by 2 desc;
select kind, count(*) from source group by 1 order by 2 desc;
```

| tier | 행 | | method | 행 | | source.kind | 행 |
|---:|---:|---|---|---:|---|---|---:|
| 1 | **25,414** | | `measured` | 28,815 | | journal | 1,265 |
| 2 | 3,554 | | `estimated` | 4,409 | | datasheet | 1,113 |
| 3 | 7,932 | | `computed` | 3,733 | | database | 313 |
| 4 | 4,496 | | `handbook` | 3,613 | | other 123 · book 77 | |
| 5 | 0 | | `digitized` | **826** | | standard 27 · web 26 · computed 1 | |

- 출처 없는 값 **0행**(`select count(*) from property_value where source_id is null`).
- 문자값(`value_text`) 841행 — UL94 등급 같은 범주형.

### 12.4 해석 격자 — 커버리지

```bash
MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web \
  python3 backend/scripts/catalog/coverage_report.py
```

**격자 밖 1,790종 제외**(evidence 1,723 + out_of_scope 67) → 모수 **864종**.

| 해석 | 대상 | 칸 | 셀채움 | 실측기반 | 재료준비 | 구조적부재 |
|---|---:|---:|---:|---:|---:|---:|
| 구조·강성 | 864 | 2,592 | 69.8% | 52.7% | 58.4% | 6 |
| 낙하·충격 | 864 | 4,320 | 63.8% | 42.0% | 45.9% | 60 |
| 열전달·방열 | 864 | 2,592 | 66.4% | 52.5% | 55.1% | 13 |
| 열응력·워피지 | 864 | 3,456 | 71.9% | 55.9% | 56.7% | 8 |
| 폴더블 벤딩 | 321 | 1,284 | 67.2% | 46.5% | 50.5% | 0 |
| 결로(표면) | 864 | 3,456 | 62.1% | 49.2% | 48.4% | 24 |
| 결로(투습) | 542 | 2,168 | 69.4% | 51.3% | 53.9% | 3 |
| 초탄성(실링·완충) | 36 | 72 | 94.4% | 73.6% | 91.7% | 0 |
| 접착·박리 | 321 | 642 | 70.7% | 60.1% | 53.3% | 30 |
| 전기·EMI | 864 | 864 | 71.8% | 64.6% | 71.8% | 3 |
| 피로·수명 | 540 | 1,620 | 55.1% | 50.3% | 23.1% | 81 |
| 산소소광-발광체 | 7 | 7 | 28.6% | 28.6% | 28.6% | 0 |
| 산소확산-매트릭스 | 54 | 54 | 68.5% | 53.7% | 68.5% | 4 |
| **합계** | | **23,127** | **66.4%** | **50.7%** | | **232** |

- 채운 칸 **15,358** / 23,127. 실측기반과의 차 15.7%p(3,632칸)가 **가정값이 만든 착시**다.
- 구조적 부재 232칸(1.0%)을 뺀 **유효채움 67.0%** — 남은 일은 7,769칸이 아니라 **7,566칸**이다.

### 12.5 빈칸의 네(다섯) 갈래 분해 — §582

**채움률만 내면 "더 캐면 된다"로 읽힌다.** 코어 7물성(밀도·E·ν·CTE·k·cp·인장강도) ×
`role='product'` 864종 = **6,048칸**을 갈랐다.

```bash
cd backend && python3 -c "
import sys; sys.path.insert(0,'scripts/catalog')
from coverage_report import subsystem_core
r=subsystem_core('/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db')
print(r['total'])
for x in r['rows']: print(x)"
```

| 계통 | 재료 | 칸 | 채움 | % | V1 해당없음 | V2 벤더부재 | V3 자유키 | V4 등급미확정 | **V5 진짜 남은 것** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| coating | 7 | 49 | 49 | 100.0 | 0 | 0 | 0 | 0 | **0** |
| rf | 24 | 168 | 161 | 95.8 | 0 | 0 | 0 | 0 | 7 |
| emi | 3 | 21 | 20 | 95.2 | 0 | 0 | 0 | 0 | 1 |
| passive | 11 | 77 | 70 | 90.9 | 0 | 0 | 7 | 0 | **0** |
| wlp | 11 | 77 | 67 | 87.0 | 0 | 0 | 10 | 0 | **0** |
| housing | 160 | 1,120 | 972 | 86.8 | 0 | 0 | 55 | 0 | 93 |
| sensor | 5 | 35 | 28 | 80.0 | 0 | 0 | 0 | 0 | 7 |
| acoustics | 15 | 105 | 83 | 79.0 | 0 | 0 | 0 | 0 | 22 |
| camera | 41 | 287 | 215 | 74.9 | 0 | 0 | 0 | 0 | 72 |
| semiconductor | 13 | 91 | 64 | 70.3 | 0 | 0 | 26 | 0 | 1 |
| pcb | 178 | 1,246 | 862 | 69.2 | 1 | 69 | 6 | 0 | 308 |
| display | 79 | 553 | 371 | 67.1 | 63 | 0 | 7 | 0 | 112 |
| thermal | 42 | 294 | 184 | 62.6 | 0 | 0 | 0 | 0 | 110 |
| (계통 미태깅) | 85 | 595 | 340 | 57.1 | 0 | 0 | 72 | 0 | 183 |
| battery | 36 | 252 | 130 | 51.6 | 46 | 0 | 0 | 0 | 76 |
| packaging | 115 | 805 | 361 | 44.8 | 0 | 0 | 35 | 24 | 385 |
| **magnetics** | 39 | 273 | 98 | **35.9** | 0 | 0 | **168** | 0 | **7** |
| **합계** | **864** | **6,048** | **4,075** | **67.4** | **110** | **69** | **386** | **24** | **1,384** |

읽는 법 —

- **빈칸 1,973 중 진짜 표적은 1,384(70%)뿐이다.** 나머지 589는 이미 판정이 끝났다.
- **채움률이 가장 낮은 계통이 표적이 아니다.** magnetics는 35.9%로 꼴찌인데 빈칸 273-98=175 중
  **168이 V3** — 하드페라이트 25등급이 코어를 비운 것이고, 그 재료를 만든 배치가
  `attributes.grade_table_scope` 에 *"등급별이 아니라 소결 하드페라이트 공통값이라 복제하지 않았다"*
  라고 이미 적어 두었다. **채굴 잔여는 7칸이다.**
- **V3(386칸)는 판정이 적혀는 있는데 집계가 못 읽는 자리에 있다**(§593).
  다음 파동이 또 표적으로 센다. 집계가 읽는 칸은 `core_not_applicable`(V1)·
  `core_absent_from_vendor_sheet`(V2) 둘뿐이다. **판정을 남길 때 이 칸에 남겨라.**

### 12.6 카드가 서는 재료 수

`build_cards()` 의 최소 요건으로 직접 셌다.

```sql
-- 기계 카드(*MAT_ELASTIC 최소) = 밀도 + 영률
select count(*) from (select material_id from property_value
  where property_key in ('physical.density','mechanical.youngs_modulus') and value_num is not null
  group by material_id having count(distinct property_key)=2);                       -- 741
-- 열 카드 = 밀도 + 비열 + 열전도율
select count(*) from (select material_id from property_value
  where property_key in ('physical.density','thermal.specific_heat','thermal.conductivity')
    and value_num is not null group by material_id having count(distinct property_key)=3); -- 601
```

| 카드 | 전 재료 | `role='product'` 만 |
|---|---:|---:|
| 기계(최소 `*MAT_ELASTIC`) | **741종** | **577종** |
| 열(`*MAT_THERMAL_ISOTROPIC`) | **601종** | **476종** |

`role='product'` 한정은 이렇게 센다.

```sql
select count(*) from (
  select v.material_id from property_value v join material m on m.id = v.material_id
   where json_extract(m.attributes,'$.role') = 'product'
     and v.property_key in ('physical.density','mechanical.youngs_modulus')
     and v.value_num is not null
   group by v.material_id having count(distinct v.property_key) = 2);   -- 577
```

**격자 모수 864종 중 기계 카드가 서는 것은 577종(66.8%)** 이다.
§12.4의 「구조·강성 재료준비 58.4%(505종)」보다 큰 이유는, 카드 최소 요건이
밀도 + E 뿐이고 포아송비는 0.3으로 폴백하기 때문이다 — **카드가 선다는 것과
그 카드를 믿을 수 있다는 것은 다른 말이다.**

### 12.7 정정·판정·이동이 실제로 쓰인 양

```sql
select count(*) from property_value where conditions like '%correction_reason%';        -- 22,754
select json_extract(conditions,'$.corrected_by') b, count(*) from property_value
 where conditions like '%corrected_by%' group by 1 order by 2 desc;
select count(*) from property_value where conditions like '%verdict_tie%';              -- 10,907
select count(*) from property_value where conditions like '%moved_from_material%';      --      2
select count(*) from property_value where conditions like '%moved_from_source%';        --    203
select count(*) from material where json_extract(attributes,'$.merge_verdict')='moved'; --      1
```

| 파동 | 정정 행 |
|---|---:|
| 52차 NA | 9,800 |
| 53차 OB | 5,996 |
| 54차 PA | 4,217 |
| 52차 NC | 2,167 |
| 51차 MA | 463 · 54차 PB 73 · 49차 KB 36 · 48차 JA 2 |

**정정 22,754행 중 값을 바꾼 것은 36행뿐이다**
(`conditions like '%"value_before_correction"%'`) — 나머지는 조건 어휘 통일과 판정이다.
**값·등급·method·출처를 한 칸도 안 고치는 정리가 이 경로의 주된 쓰임이다.**

### 12.8 무결성 — 지금 상태

```bash
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/integrity_check.py; echo $?
```
**이상 1개** — `물성값 0인 재료 2`. 주의는 4블록이 발화한다(§8.1 표).

---

## 13. 아직 안 되는 것 — 정직하게

### 13.1 대표값 선택기가 조건축을 못 본다

```bash
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/tie_verdicts.py census
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/tie_verdicts.py classify
```

```
(재료,키) 쌍 20,058 · 후보 둘 이상 6,339
1·2위가 id 로만 갈림 3,988 · 그중 값이 10% 초과 2,516
동률군(1위와 순위가 완전히 같은 경쟁행 보유) 3,972
  · 1위 대 **모든** 경쟁행 중 하나라도 10% 초과 → 2,862   ← 판정 대상은 이쪽이다
```

| 부류 | 전체 | 10%초과 | 카드8키&10% |
|---|---:|---:|---:|
| 다른조건 | 2,498 | 1,762 | 522 |
| 다른항 | 1,026 | 879 | 12 |
| 산포범위 | 234 | 149 | 59 |
| 의견차 | 57 | 15 | 3 |
| 조건미기재 | 48 | 12 | 6 |
| 키표기흔들림 | 38 | 12 | 6 |
| 반복시편 | 32 | 15 | 5 |
| 서술차이 | 19 | 7 | 3 |
| 서술축 | 16 | 11 | 4 |
| 같은출처중복 | 4 | 0 | 0 |
| **합** | **3,972** | **2,862** | **620** |

- **동률군의 62.9%(2,498/3,972)가 `다른조건`** — 행이 같은 게 아니라 **선택기에 그 축이 없다.**
  갈라야 할 축(방향 · 율속 · 열처리 · `term`/`set_id`)이 `_rep_rank` 에 없다.
  구분할 조건조차 없어 진짜 "적재 순서"인 것은 그보다 훨씬 적다.
- **브리프 §546의 "88%(3,213/3,642)" 는 51차 MB 분류기 기준이라 지금 수와 직접 비교되지 않는다.**
  분류기가 그 뒤로 고쳐졌다(§599). 위 표가 현재 분류기의 라이브 값이다.
- **순위를 더 만들지 않는 것이 결론이다** — 축을 넣어 보니 개선보다 개악이 많았다.
  대신 화면·카드·API가 후보를 드러낸다.

### 13.2 판정 416군이 경로 때문에 막혀 있다

```bash
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/tie_verdicts.py gen /tmp/tie.json --all --skip-judged
# → 군 422 → 판정 6군 · 정정 선언 12건 · 전파 불가로 뺀 군 416
```

막는 이유 두 갈래(군 단위) —

| 사유 | 군 | 왜 |
|---|---:|---|
| 같은 (출처, 값) 행이 둘 이상 | 387 | 병합기가 옛 행을 특정 못 한다 → 운영에 **새 행**이 생긴다(§522가 경고한 그 사고) |
| 옛 `*_before_correction` **컬럼 표시** | 19 | 병합기가 그것을 컬럼의 옛 값으로 읽어 `where method=<가드 이전 값>` 으로 찾는다 → 0건 |
| 둘 다 | 10 | |

**남은 것은 판정이 아니라 중복이다.** 판정을 더 짜내는 것보다 중복을 지우는 쪽이 표적을 더 연다.

같은 벽이 조건 어휘 통일에도 있다.

```bash
MATERIALTWIN_DATA_DIR=... python3 backend/scripts/catalog/correction_reach.py plan
# 통일 대상 238행 / 막힘 71군 276행 (조건 대조를 넣어도 0군만 열림)
#   134행 — 옛 컬럼 표시 `method_before_correction` 가 탐색축을 틀리게 만든다
```

### 13.3 중복 적재가 남아 있다

```bash
python3 backend/scripts/catalog/value_duplicates.py
python3 backend/scripts/catalog/source_duplicates.py
```

| 값 중복 부류 | 군 | 행 | 여분행 |
|---|---:|---:|---:|
| `certain` | 47 | 97 | 50 |
| `suspect` | 445 | 912 | 467 |
| `repeat` | 1,400 | 3,363 | 1,963 |

| 출처 중복 지문 | 군 | 출처행 | 걸린 물성값 |
|---|---:|---:|---:|
| `local_path`(단독) | 6 | 65 | **1,811** |
| `title` | 26 | 52 | 569 |
| `title+year+publisher` | 17 | 34 | 295 |
| `local_path+title` | 5 | 10 | 162 |
| `docnum`(벤더 문서번호) | 5 | 12 | 143 |
| `url` | 7 | 14 | 110 |
| `doi` | 3 | 6 | 10 |
| `content_hash` | 0 | 0 | 0 |

`local_path` 단독은 **혼자서는 지문이 아니다**(같은 편찬 PDF가 55개 제품 페이지에 찍힌다).
자연키 유일성 자체는 온전하다 — 2,945/2,945.

**그리고 지울 수 없다.** 병합은 비파괴라 dev에서 지운 행은 운영에 그대로 남는다(§7.3).
정리는 **표시**여야 한다.

### 13.4 죽은 출처의 틀린 DOI 는 못 고친다

합쳐서 참조가 0이 된 출처 넷(src 3280·2779·4419·273)의 DOI가 틀렸는데 고칠 길이 없다.
참값은 살아남은 출처가 이미 갖고 있고 `source.doi` 는 UNIQUE다.
`NULL` 로 비우면 자연키가 바뀌어 **운영에 껍데기가 하나 더 생긴다**(§578).

```sql
select id, doi, (select count(*) from property_value v where v.source_id=s.id) n
  from source s
 where title in (select title from source where id in (3280,2779,4419,273))
 order by title, id;
```
| 제목 | 살아남은 행 | 죽은 껍데기 |
|---|---|---|
| CoMn2O4 Nanoparticles Decorated on 2D MoS2 Frame … | 4347 `10.1016/j.est.2021.102302` (12행) | **4419** `10.1016/j.jallcom.2021.160204` (0행) |
| Influence of Loading Directions on Dynamic Compressive … | 2915 `10.3390/ma15207047` (6행) | **2779** `10.3390/ma15207112` (0행) |
| Numerical Simulation Study on Factors Influencing Anti-Explosion … | 2541 `10.3390/ma15113880` (26행) | **3280** `10.3390/ma15103880` (0행) |
| Preparation and properties of a high temperature, flexible … | — | **273** `10.1016/j.eurpolymj.2007.06.017` (0행) |

**남는 위험** — 죽은 껍데기의 DOI 중 **실재하는 딴 논문을 가리키는 것이 있고**(§597),
적재기의 `upsert_source()` 가 출처를 `doi` 로 **최우선** 조회한다. 나중에 그 논문을 적재하면
**죽은 껍데기에 값이 붙는다.** 출처 메타 정정 경로가 생기면 첫 표적이 여기다.
(값 정정 경로는 `property_value` 전용이고 `source` 를 못 고친다.)

### 13.5 검사기의 「물성값 0인 재료 2」는 MCP 시험 잔재다

```sql
select id,name from material where id not in (select distinct material_id from property_value);
-- 2290  Carbon Steel 45 (Kwofie 2007 …)   ← 묘비(merge_verdict='moved'). 검사에서 면제된다
-- 2649  업로드시험강
-- 2650  삭제확인강
```

세 종이 물성 0행인데 검사기가 세는 것은 **2**다 — 2290은 묘비라 면제된다.
남은 `업로드시험강`·`삭제확인강` 두 종은 **MCP 도구 시험이 남긴 재료**이지 데이터 결함이 아니다.
그런데 병합은 비파괴라 dev에서 지워도 운영에 남는다(§7.3) — 그래서 검사기의 「이상 1개」가
계속 떠 있다. **이 한 줄은 알고 넘기는 것이고, 값 결함이 아니다.**

### 13.6 그 밖에

- **문서와 코드의 항목 수가 어긋난다.** `integrity_check.py` 머리말과
  `COLLECTION_METHODOLOGY.md` 부록 B는 "37항목"이라 적었지만 실제는 **50항목 + 주의 6**이다.
  이 문서 §8.1의 명령으로 매번 세라.
- **`role` 이 없으면 커버리지가 조용히 product로 센다.** 지금은 0종이지만 새 재료가 들어올 때마다
  재발할 수 있어 검사기 주의가 지킨다.
- **소자 유효 열전도율이 재료 키에 산다**(4종). 이름만으로도 값만으로도 못 가르고, 둘을 겹쳐야
  갈린다. 검사기 주의로만 방어한다 — Ashby·비교·카드에서 재료로 섞이면 틀린다.

---

## 부록 A — 재현 명령 한 묶음

```bash
export LIVE=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web

# 검사
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/integrity_check.py       # 0이 아니면 배포 금지
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/coverage_report.py
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/coverage_report.py --json
python3 backend/scripts/catalog/value_duplicates.py
python3 backend/scripts/catalog/source_duplicates.py
python3 backend/scripts/catalog/verdicts_check.py
python3 backend/scripts/catalog/analysis_readiness.py    # 주의 — 이 파일은 DB 경로가 박혀 있다(라이브 고정)

# 적재
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/ingest_agent_json.py out_XX/          # 드라이런
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/ingest_agent_json.py out_XX/ --apply
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/normalize_tiers.py --apply

# 동률·정정
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/tie_verdicts.py census
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/tie_verdicts.py classify
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/tie_verdicts.py gen out.json --all --skip-judged
MATERIALTWIN_DATA_DIR=$LIVE python3 backend/scripts/catalog/correction_reach.py plan

# 선별
python3 backend/scripts/catalog/corpus_index.py search "<FTS 질의>" -n 20
python3 backend/scripts/catalog/mined_index.py --doi <doi> | --title "<제목>"
python3 backend/scripts/catalog/scan_targets.py

# 문서·리포트 재생성
python3 backend/scripts/catalog/build_coverage_docx.py
python3 backend/scripts/catalog/build_stats_xlsx.py
python3 backend/scripts/catalog/build_overview_html.py

# 시험
cd backend && python3 -m pytest -q        # 366 passed, 1 skipped
```

**DB를 쓰는 경로는 셋뿐이다** — `ingest_agent_json.py --apply` ·
`normalize_tiers.py --apply` · 마이그레이션. 나머지는 전부 읽기다.
그리고 운영으로 나가는 경로는 `_materialtwin_merge.py` 하나다.

## 부록 B — 파일 지도

| 파일 | 역할 |
|---|---|
| `/data/paper_patent_corpus/structured/` | 논문·특허 전문 코퍼스(md) |
| `/data/paper_patent_corpus/_index/corpus_fts.db` | FTS5 어휘 색인 20,692편 |
| `/data/paper_patent_corpus/_index/_verdicts/discarded.jsonl` | 폐기 대장 **append-only** |
| `backend/scripts/catalog/corpus_index.py` | 코퍼스 색인·검색 |
| `backend/scripts/catalog/mined_index.py` | 기채굴 조회(다섯 축) |
| `backend/scripts/catalog/scan_targets.py` | 표적 선별(기채굴·기폐기 제외) |
| `backend/scripts/catalog/verdicts_check.py` | 대장 건강 점검 |
| `backend/scripts/catalog/extract_datasheet.py` | PDF/URL → 물성 텍스트(OCR 폴백) |
| `backend/scripts/catalog/digitize_curve.py` | 그래프 이미지 → 좌표 |
| `backend/scripts/catalog/ingest_agent_json.py` | **적재기** — 관문 9 + 정정 경로 |
| `backend/scripts/catalog/normalize_tiers.py` | tier 재판정("값의 성격") |
| `backend/scripts/catalog/normalize_condition_keys.py` | 조건 키 어휘 통일 |
| `backend/scripts/catalog/tie_verdicts.py` | 동률 census·분류·판정 선언 생성 |
| `backend/scripts/catalog/correction_reach.py` | 정정이 운영까지 가는가(병합기의 거울) |
| `backend/scripts/catalog/integrity_check.py` | 무결성 50항목 + 주의 6 |
| `backend/scripts/catalog/coverage_report.py` | 지표·구조적 부재·계통별 빈칸 분해 |
| `backend/scripts/catalog/value_duplicates.py` · `source_duplicates.py` | 중복 검출(**지우지 않는다**) |
| `backend/scripts/catalog/analysis_readiness.py` | 해석별 재료 준비도 |
| `backend/app/property_taxonomy.py` | 물성 정의 원본 |
| `backend/app/models.py` | `material`·`source`·`property_definition`·`property_value` |
| `backend/app/acquire/store.py` | `upsert_source` · `upsert_property_value`(멱등 적재) |
| `backend/app/catalog_compare.py` | **대표값 선택기** `_rep_rank`·`_tie_key`·`representative_*` |
| `backend/app/catalog_alternatives.py` | 대안·동률 payload(`tie_info`·`separated_by`) |
| `backend/app/dyna_export.py` | **카드 생성** `build_cards()`·`candidate_rows`·`resolve_choice` |
| `backend/app/routers/catalog.py` | `/api/catalog/*` |
| `backend/mcp_server.py` | MCP 도구(`register_property`·`export_dyna_cards` 등) |
| `frontend/src/routes/catalog*.tsx` | 카탈로그 화면 |
| `HEAXHub/deploy/apptainer/_materialtwin_merge.py` | **병합기** — 자연키·큐레이션·정정/판정/이동 |
| `HEAXHub/deploy/apptainer/appdata-merge-from-drive.sh` | 운영 병합 진입점(백업 후 실행) |
| `HEAXHub/deploy/apptainer/appdata-to-drive.sh` | dev 스냅샷 → Drive |
| `docs/COLLECTION_METHODOLOGY.md` | **왜·어떻게 판단하나**(이 문서의 짝) |
| `docs/COLLECTION_BRIEF.md` · `COLLECTION_BRIEF_CORPUS.md` | 지시서 정본 · 함정 대장 599절 |
| `docs/PROPERTY_DATA_HISTORY.md` | 경위의 1차 사료 |
| `docs/BLOCKED_SOURCES.md` | 막힌 경로 대장 |
