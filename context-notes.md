# MaterialTwinWeb 컨텍스트 노트

> 작업 중 내린 결정과 그 근거를 계속 누적한다. 다음 세션(사람/에이전트)이 결정을 다시 도출하지 않도록.

## 2026-06-25 — 프로젝트 시작 & 계획 수립

### 베이스 템플릿
- `fastapi-react` 폴더는 **디자인 패턴(템플릿)** 이다. git 커밋 대상이 아님 → `.gitignore`에 `fastapi-react/` 추가, 추적 해제됨. 디스크엔 보존.
- 템플릿 내용(backend/, frontend/, .portal/)을 메인 폴더로 복사해서 프로젝트를 시작했다.
- 깨면 안 되는 계약 3가지: ① entrypoint `app.main:app` 객체명/경로 불변, ② StaticFiles `/` 마운트는 항상 마지막·`/api/*`가 먼저, ③ 프론트는 상대경로 `fetch("api/...")` + Vite `base:"./"`.

### 요구사항 확정 (사용자 답변)
- 데이터 형식: CSV/TXT + Zwick zse/zsx(testXpert). 정확 스펙 미정 → **어댑터/파서 플러그인 패턴**.
- 물성 범위(단계적): 기본 인장 물성 → 진응력/진변형률 변환 → 구성방정식 피팅. **기초부터 우선**.
- DB: SQLAlchemy 추상화. SQLite 시작 → Postgres 설정만 바꿔 전환. 인증 초기엔 없음.

### 계획 수립 방법
- Workflow로 **5개 관점 병렬 설계(domain/arch/datamodel/ux/parser) → 3개 교차비판(gaps/overeng/feasibility) → 종합**. 9 에이전트, 약 463k 토큰.
- 결과를 [PLAN.md](PLAN.md)로 정리. 종합본의 메타문장만 제거하고 내용은 그대로.

### 종합에서 수렴된 핵심 결정 (왜 그렇게 정했나)
1. **과설계 차단**: 5개 설계안이 "2·3단계" 기능(피팅/진응력/통계/잡/Alembic/Postgres호환)을 1단계 골격에 미리 박는 공통 경향 → [overeng] 비판 수용해 **골격조차 안 만들고 JSON 확장 슬롯(`extra_metrics`/`attributes`)과 list 시그니처만 예약**.
2. **라우팅 = 해시(createHashHistory)**: StaticFiles(html=True)는 `/materials/42` deep-link를 index.html로 rewrite 안 함(실측). 빌드타임 슬러그 주입 없이 새로고침 안 깨지는 유일한 방법이 해시. ([ux]의 "형제앱 hash 검증" 근거는 사실 아님 → 폐기, 기술 근거로 대체.)
3. **곡선 저장 = Parquet 파일 + DB 포인터**: DB BLOB·점당1행 둘 다 탈락. 곡선은 한 덩어리로 읽는 컬럼 데이터라 pandas/numpy 직결·zstd 압축·DB 슬림이 유리. 경로는 DB에 **상대경로만**.
4. **단위 책임 단일화**: 파서는 원본 단위(mm/kN)+메타만 반환(자동변환 금지). SI 정규화는 `units.py`가 ingest 시 1회.
5. **테이블 명명 정본**: test(=TestRun), processed_result(=DerivedProperties), raw_curve_ref(=RawCurve)로 통일.
6. **물성 수치 함정 명시**: 영률 구간선택 ±10%·원점강제 −14% → toe보정 ON·절편포함 회귀·R²≥0.99 거부·brush 수동조정. Rp0.2는 E오차 추종(±4MPa)이라 E신뢰도 연동 경고. scipy 불필요(numpy만), 피팅은 Phase 3.

### 사람이 풀어야 할 2가지 (착수는 가능, 운영 전 필수)
- **D1 영속 볼륨**: manifest.yaml에 SIF 밖 쓰기가능 볼륨 선언 필요. 미해결 시 재시작마다 데이터 소실 → Parquet 전략 무효화. 개발은 `./var/data` 기본값으로 진행 가능.
- **D2 testXpert 샘플 2~3개**: 텍스트 export 레이아웃/다중시편 패턴/헤더 별칭/zse·zsx 내부구조 전부 막혀 있음. 없으면 GenericCsv+수동매핑으로 MVP 진행. ZwickText 휴리스틱 확정 전 필수.

### 미해결 / 보류
- `main.py`는 아직 템플릿 원본(인메모리 Task CRUD) 그대로다. Phase 1 백엔드 골격 착수 시 교체 예정 — 계획 확정 전 미리 짜면 어긋나서 의도적으로 보류함.
- git push 보류 (gh 미인증). 사람이 `gh auth login` 후 `git push -u origin main`.
- D5(FE 카드 타깃 MAT: *MAT_024 우선/*MAT_098)는 Phase 3 착수 전 확정.

## 2026-06-26 — 적대적 보증(§13) + 프리미엄 UX/UI(§14) 보강

### 방법
Workflow로 **적대적 공격(5) + 디자인 토너먼트(3) → 중립 심판(2) → 부록 종합(2)**, 12 에이전트 ~663k 토큰. 공격자가 실제로 합성 σ-ε 곡선을 측정(`scratchpad/verify.py`)하고 Starlette 0.50 소스·HEAXHub 런처 코드(`integration_launcher.py`, `stacks.yaml`)를 **직접 열람**해 검증 → 기존 계획의 "실측" 라벨이 사실은 LLM 추론이었음을 폭로하고, 일부는 합성측정으로 재확인.

### 본문에 반영한 치명/높음 (C-id, §13 부록이 SSOT)
- **C1【치명 최우선】** R²<0.99 **하드거부 폐기** → confidence 등급(high/ok/low)으로 강등, 값 항상 반환. 폴리머는 secant modulus 분기. (안 고치면 노이즈·폴리머에서 사용자가 물성을 영영 못 받음 = 제품 파괴.) §6.1·§9·§12 수정.
- **C2【치명】** SQLite 동시성 — 런처 단일 워커 내 동시 업로드가 `SQLITE_BUSY→500`. `journal_mode=WAL`+`busy_timeout=5000` 신설, Parquet 쓰기는 트랜잭션 밖. §4.5 수정.
- **C3【치명】** P1 완료기준에 **골든 픽스처 + 수치 정확도 게이트**(E ±2%, Rp0.2 ±2MPa, UTS ±0.5%). 기존엔 "동작함"뿐이라 E 틀려도 통과했음. §9 수정.
- **C4【높음】** 곡선 경로에서 가변 `material_id` 제거 → 불변 `test_id`만. atomic rename + 부팅 reaper. §4.4 수정.
- **C5【높음】** graceful 재정의: 파싱 성공 ≠ 계산 허가. 오매핑(단조성·채널상관·자릿수) 가드. sniff 절대임계 0.3 → 상대규칙.
- **C6【치명】** 런처는 `/apps/slug/`(trailing slash) 서빙 필수 — 없으면 첫 fetch가 `/apps/api/...`로 깨짐(RFC 3986). §3.1 계약 추가.
- **C7** D1 재기술: 런처가 추가 바인드 미지원(`cleanenv=True`) → "manifest만 고치면 됨"이 아니라 플랫폼 선결 과제.

### 생존(공격에도 안 무너져 유지) — 재확신
§6 "scipy 불필요(numpy만)", §4.4 Parquet+포인터 전략, LTTB 2000점. 합성측정 통과.

### 디자인 확정(§14)
- **다크 우선**, primary=calibration blue `#3B82F6`, accent=signal green `#34D399`, 딱 두 강조색.
- 토큰 SSOT = `index.css` CSS 변수(`:root`+`.light`), Okabe-Ito 색맹안전 8색, ECharts는 `getComputedStyle` 브리지로 색 주입(canvas는 CSS변수 못 읽음).
- 방향 A(정밀계측) 기반 + B(에디토리얼 서사·상태) + C(모션·접근성) 이식. framer-motion 없이 CSS/WAAPI.
- 무드: "어두운 계측 패널 위 데이터 발광, 발견의 서사, 바늘이 값에 꽂히듯 절제된 반응."

### 다음
사용자 지시로 **백엔드 전체를 백그라운드로 구현** 진행(범위=백엔드 전체, D1=./var/data 폴백, D2=합성 픽스처, ZwickText=wrapper 스텁).

## 2026-06-28 — 풀스택 Phase 1 완료 + Python 3.12 확정

- **프론트엔드 Phase 1 구현 완료**: §14 디자인시스템(다크 우선, calibration blue/signal green, Okabe-Ito), 3화면(/materials·/materials/$id·/upload 4단계 마법사), ECharts 곡선뷰어(brush 영률 재계산). 세션 2회 재시작으로 워크플로우 중단 → Screens 3개는 직접 작성. tsc 0·build 성공·서브경로 스모크 200 전부 통과. 커밋·push 완료.
- **서브경로 테스트 교훈**: `--root-path`만으로 테스트하면 404가 정상이다 — 실제론 Caddy가 prefix를 벗겨 `/`로 전달하므로 **루트(`/`) 서빙으로 검증**해야 한다. 해시 라우팅이라 deep-link는 `/#/...`로 서버엔 `/`만 도달(C6).
- **Python 3.12 확정**(유지보수성, 사용자 지시): 의존성이 시스템 python3(3.10)에만 있던 문제를 **`backend/.venv`(python3.12) 생성 + `pip install -e ".[test]"`로 해결**. `requires-python=">=3.12"`. **항상 `.venv/bin/python`으로 실행**(시스템 3.10엔 의존성 없음). test extra에 httpx 추가(starlette TestClient용). 3.12 venv에서 pytest 22개 전부 통과 확인.
- `.venv/`는 .gitignore 처리(커밋 안 함).

## 2026-06-28 — 브라우저 E2E 검증("띄워봐") + 실제 버그 2건 발견

uvicorn으로 띄우고 Playwright로 전 화면 + 업로드 E2E를 실측했다. **UI는 §14대로 완벽**(다크 테마·스텝퍼·드롭존·곡선 차트·confidence 배지·회귀 패널 전부 동작). 단, 합성 골든 CSV(kN·mm 단위)를 실제로 흘려보내며 **pytest가 못 잡은 진짜 버그 2건**을 잡았다.

### 🐞 BUG-1 【치명】 단위행 미파싱 → 물성 1000배 오차
- 증상: kN·mm CSV 업로드 시 E=0.00 GPa(정답 200), RM=1 MPa(정답 540), A%=18000(정답 18%). 정확히 1000배씩 어긋남.
- 근본 원인: 파서(zwick_textxpert/generic_csv)가 CSV **2행 단위행("s, kN, mm")을 ColumnSpec.unit으로 연결 못 함** → 모든 컬럼 `unit=None` 반환. ingest의 `_FORCE_FACTOR`(kN→1e3)·`_LEN_FACTOR`(mm→1e-3)가 None→1.0으로 처리되어 변환 안 됨.
- 왜 pytest 통과했나: 골든 픽스처 단위테스트는 이미 **SI(N·m)** 로 ingest를 직접 호출 → 단위행 파싱 경로를 안 탐. **단위 있는 raw CSV E2E 픽스처가 없었음**.
- 수정 방향: ① 파서 structure 단계에서 헤더 다음 행이 단위행이면 각 컬럼 unit으로 흡수(generic_csv·zwick 공통). ② 회귀 테스트: kN·mm·%·독일식 단위행 CSV → ingest → E/UTS가 SI로 정확. ③ 단위 추정 실패 시 ParseIssue(INFO)로 노출(§5.3 "FORCE 단위 자동변환 금지 → 사용자 확인"과 정합).

### 🐞 BUG-2 【낮음】 신규 재료 커밋 후 "재료 보기" 버튼 비활성
- 위치: `frontend/src/routes/upload.tsx` 결과 화면. `disabled={!meta.materialId}`인데 신규 재료 경로는 커밋 중 생성한 새 재료 id를 `meta.materialId`에 반영 안 해 항상 null → 버튼 영구 disabled.
- 수정 방향: commitMut에서 생성된 재료 id를 state(예: `committedMaterialId`)에 저장하고 그걸로 네비게이트·버튼 활성. (IngestResult엔 material_id가 없으니 createMaterial 반환 id를 따로 보관.)

### 검증된 것(정상)
업로드 4단계 마법사 전 단계, 파서 자동감지(zwick_textxpert 100%)+컬럼 역할 매핑(time/force/displacement), IssuePanel(WARN ambiguous_dispatch 노출), 재료 생성·시편 생성·곡선 Parquet 저장·곡선 차트 렌더·confidence='low' 배지·ISO 용어 테이블. 곡선 **형태**는 정확(탄성+멱법칙).

## 2026-06-30 — 버그 2건 수정 완료 + 브라우저 재검증

### ✅ BUG-1 해결
- `column_map.resolve_columns(headers, aliases, units=None)`에 **units 인자 추가** — 헤더 인라인 단위(`Force [kN]`)가 우선, 없으면 단위행 셀로 폴백. `_clean_unit`이 빈/숫자/8자 초과 토큰은 단위로 안 봄.
- `generic_csv.parse`가 header_idx~data_start 사이 **비수치행을 단위행으로 감지**(데이터에 가장 가까운 행) → resolve_columns에 전달. 흡수 시 INFO `units_from_unit_row`로 노출(§5.3 정합). zwick은 generic wrapper라 자동 수혜(C12).
- 회귀 테스트 2개: `test_unit_row_absorbed_into_columns`(파서 단위 흡수), `test_ingest_force_disp_units_si_normalized`(kN·mm raw → ingest → E/UTS SI 정확). 처음엔 둘 다 실패(E=1052 vs 2e11) → 수정 후 통과.
- 브라우저 재검증: E=200.0GPa, Rp0.2=275.6MPa, UTS=540.0MPa, A=18.0%, **confidence=high**. 1000배 오차 사라짐.

### ✅ BUG-2 해결
- `upload.tsx`: `commitMut.mutationFn`이 `{materialId, ingest}` 반환 → `onSuccess`에서 `committedMaterialId` state 저장. "재료 보기" 버튼이 `committedMaterialId`로 활성/네비게이트(신규 재료 포함). `resetWizard`도 초기화.
- 브라우저 재검증: 신규 재료 커밋 → 버튼 활성 → /materials/3 정확 이동.

### 함정 메모
브라우저가 같은 해시 번들을 **캐싱**해 수정 후에도 옛 동작이 보일 수 있다. 재검증 시 쿼리스트링(`?nocache=1`) 등으로 강제 리로드할 것. (번들 디컴파일로 `disabled:f==null` 로직 존재를 먼저 확인하면 캐시/코드 문제를 빨리 구분.)

전체 pytest **24개 통과**(3.12 .venv). UI는 framer-motion 없이 CSS 모션만으로 §14 충실 구현.

## 2026-07-09 — LS-DYNA 카드 단위계 전환 + Johnson-Cook 카드

### 왜
카드 2종의 단위계가 서로 달랐다(MAT_024=SI Pa, VISCOELASTIC=t/mm/s MPa) — 한 모델에 섞으면 단위 불일치. **ton·mm·s 기본**으로 통일해 둘 다 MPa 정합, 사용자 전환도 지원.

### 결정
- `app/unit_systems.py`(신규): 질량·길이·시간 기본단위 배율로 파생배율(f_stress=λτ²/α, f_density=λ³/α, f_rate=τ) 유도. 4계열 — **ton_mm_s(기본)**·kg_m_s(SI)·g_mm_ms·kg_mm_ms. 검증: steel E 2.07e11Pa→ton_mm_s 2.07e5MPa, ρ 7850→7.85e-9.
- **내부는 전부 SI 정규화**, 카드 생성 시점에만 단위계 변환. 점탄성 저장값은 t/mm/s라 호출부(properties·mcp)에서 ×1e6/×1e12로 SI 승격 후 카드함수(SI 입력)에 전달 → 두 카드가 동일 변환경로.
- **Johnson-Cook 카드는 *MAT_098(Simplified J-C)** 선택 — *MAT_015는 EOS 필요라 부적합. 자유 3파라미터 J-C 피팅은 A·B 상호식별 불가로 A가 음수 발산(비물리) → 카드용은 **A=측정 항복응력 고정**, B·n만 소성경화 적합(`fitting.johnson_cook_card_params`). 17-4PH 실측: A=1168, B=2319, n=0.514, R²=0.941(물리적).
- API: `card.k?units=&model=piecewise|johnson_cook`, `viscocard.k?units=`. 미지원 키 422. 파일명에 units·모델 태그(`test_10_MAT098_JC_ton_mm_s.k`).
- MCP `get_mat_card(test_id, units, model)`.
- 프런트: `UNIT_SYSTEMS`+`cardUrl(tid,units,model)`, FitPanel에 단위 Select+[*MAT_024][Johnson-Cook] 버튼, ViscoelasticView에 단위 Select.

### 안 한 것(정직)
**초탄성(고무) 카드 미지원** — 폴리머 데이터가 전부 완화시험(점탄성)이라 Ogden/Mooney용 응력-신장 데이터가 DB에 없음. 데이터 확보 후 과제.

### 검증
백엔드 pytest **70 passed, 1 skipped**(test_units.py 신규 12개 포함). 프런트 빌드 exit 0. 라이브: 4계열 단위 전환·JC·점탄성·422 모두 정합(β 50/s→g_mm_ms 0.05/ms, ρ 1100→0.0011g/mm³ 확인). showcase.html 카드도 ton·mm·s 반영.

## 2026-07-10 — UX 완성 + MCP 물성 등록(쓰기) 도구

### 진행 방식(ultracode)
정찰 4에이전트(UX 갭 20건·MCP 쓰기 경로·API 대조·테스트 관행) → 구현(백엔드 직접 + 프런트 4에이전트 병렬·파일 분리) → 적대적 리뷰 워크플로(3렌즈 리뷰 → 발견 13건 전부 반박 검증 → 13건 확정) → 전부 수정.

### MCP 쓰기 도구 7종 (mcp_server.py, 총 20도구)
- register_material / register_tensile_test(strain[]·stress_mpa[] → 시편 자동생성·곡선 Parquet·물성·4모델 피팅까지) / register_relaxation_test(모드A: G0·Ginf·beta Prony, 모드B: 실측 E(t) 곡선 → 3항 Prony 피팅 + 1항 등가 유도로 카드 경로 유지) / update_material / delete_material·delete_test(confirm=False면 미리보기 — 파괴적 액션 2단계) / recompute_properties(e_range 지정).
- 검증: 배열 길이·최소 20점·NaN·% 착오(카테고리별 strain 상한: rubber/foam 10, polymer 5, 금속 2), 저항복 자동 탄성창 보정(εy<0.0036 → [0.15εy,0.7εy], E 변화 0.5% 초과 시만 채택).
- 에러는 전부 한국어 {"error": ...} dict. IntegrityError rollback. write_curve 실패 시 시편까지 롤백(delete-orphan cascade).

### 적대적 리뷰가 잡은 실버그(전부 수정)
- **GI=0 카드 왜곡**: `p.get("GI") or 0.1`이 완전 완화(Ginf=0)를 0.1 MPa로 둔갑 — mcp+웹 viscocard 둘 다 None 검사로 교체. 회귀테스트 추가.
- **test_id 재사용 경합**: SQLite rowid 재사용으로 삭제 직후 타 프로세스가 같은 id에 곡선 쓰면 unlink가 산 파일 삭제 → Test에 sqlite_autoincrement + 마이그레이션 e1a9d40b77c1(라이브 DB는 stamp c7b6cca38dc2 후 upgrade — create_all DB엔 스탬프 필요).
- 비감쇠 곡선 ZeroDivision → error dict, 반쪽 e_range 조용한 무시 → 거부+e_range_used 반환, prony attributes 커밋을 곡선 저장 성공 뒤로 이동.
- 업로드 마법사: Stepper 뒤로가기 시 stale result 클리어(재등록 dead-end), 재시도 시 testId 재사용(remap 경로로 중복 test 방지 — remap은 기존 test 대체라 멱등), effectiveMapping이 '무시'(unknown)를 걸러내던 버그(백엔드는 unknown을 유효 role로 수용).
- EditForm category null → '미분류' 센티널(이름만 고쳐도 metal로 굳는 것 방지).

### UX 완성(정찰 20건 중 high/medium 전부)
- 차트 brush 실동작(takeGlobalCursor — 죽어 있던 드래그 회귀구간 선택) + 힌트 문구. 라이브 드래그로 ε 입력 갱신 확인.
- <a download> 3곳 → downloadFile 헬퍼(fetch+Blob, 422 시 한국어 토스트). errorMessage()로 영어 detail 한국어 변환.
- 404 전용 화면(비숫자 id 포함), specimensQ 에러≠빈 상태 분리, insights 5쿼리 에러+재시도, 점탄성 dead-end 안내, FitPanel 로딩/에러.
- 재료 편집/삭제 다이얼로그(삭제는 시편 수 고지+확인), 시험 valid 토글(이상치 제외/복원), 검색 URL 동기화+카테고리 칩+카운트+더보기, 라이트 테마 차트 대응, aria-pressed 일괄.
- **클라 네비 상태 유출 버그**(라이브 검증에서 발견): activeId/curveKind가 재료 간 유출 → 점탄성 빈 화면 + 완화시험에 kind=true 500. mid 변경 리셋 이펙트 + relaxation 시험 곡선쿼리 제외 + 백엔드 422 가드.
- classify(category=None) AttributeError(인사이트 5엔드포인트 500 유발) 수정 — MCP가 category 없이 등록해도 대시보드 생존.
- 재료/시편 삭제 시 Parquet 정리(웹+MCP), ?category= 서버 필터.

### 검증
pytest **87 passed 1 skipped**(test_mcp_write 17개 포함), vite build 클린. 라이브: MCP 등록(실DB) → 웹 상세에서 곡선·마커·회귀선 확인 → MCP 프로토콜(인메모리 클라이언트, 도구 20개) delete confirm 왕복 → DB 70종 원복. 편집 다이얼로그·valid 토글·brush 드래그·404·카테고리 필터 모두 브라우저 실조작 검증.

### 함정 메모
- mcp_server는 임포트 시점 env 고정 — 테스트는 tests/conftest.py mcp_env(env → cache_clear → app.db/models/curve_store reload → mcp_server reload) 순서 필수.
- 세션에 붙어 있는 MCP 서버 프로세스는 재시작해야 새 쓰기 도구가 보인다.

## 2026-07-10 — 자율 진화 루프 사이클 1~3

- **사이클1**: insights N+1 제거(141→1쿼리, 출력 70행 동등성 실측) + 파단연신 히스토그램 + Ashby 비강도·비강성 툴팁. c421469·3b8dac6.
- **사이클2**: 코드 스플리팅 — vendor(react/tanstack/ui) 분리로 앱 번들 578→151KB, echarts는 의도적 단일 청크(주석 명시). 브라우저 기동 검증. 03f61b4.
- **사이클3**: 업로드 마법사 E2E 실검증 — 골든 CSV 브라우저 실업로드 → zwick 감지 100% → 등록 → E=200.0GPa 정답 일치 → UI 삭제 다이얼로그로 정리(Parquet 정리 실전 확인). 5d2fb80.
- 남은 백로그: showcase 갱신, MCP prompts/resources, Postgres 실검증, SIF 패키징, 초탄성(데이터 대기).

## 2026-07-10 — 사이클 4: Postgres 실검증이 잡아낸 결함 2건

PG16 실인스턴스에 마이그레이션 체인→시드→서버→MCP 쓰기 전체 리허설. **PG에서만 드러난 실버그 2건 수정.**
- **CHECK 제약 미갱신**: c7b6cca38dc2가 nullable만 바꾸고 ck_test_strain_source에 'relaxation'을 안 넣음 — PG에서 점탄성 등록 전멸(SQLite는 개발 DB가 create_all 출신이라 가려짐. alembic check는 CHECK 드리프트 미감지). f4c2a91d55e0로 드롭·재생성. 함정: SQLite batch 재생성은 리플렉션이 AUTOINCREMENT를 못 잡아 e1a9d40b77c1 효과를 지움 → table_kwargs로 명시 유지 + 체인 끝 DDL 단언 테스트.
- **성긴 곡선 탄성회귀 붕괴**: 500점 곡선에서 기본창(0.0005~0.0025) 5점 중 2점이 소성 → E=1.04GPa(r²=0.81). register_tensile_test에 r²≥0.995 재시도 사다리(기본→0.0002~0.0015→0.0001~0.001) + 저항복 보정에 창 내 점수≥5·비율 0.5~2배 가드.
- 검증: PG에서 마이그레이션 4단계 클린 적용, 시드 5+3, MCP 등록(E=200.0)·GI=0 카드·recompute·delete 왕복, 웹서버 4엔드포인트 200. 라이브 SQLite도 헤드 동기화(70행 무결). pytest 89 passed.

## 2026-07-10 — 사이클 5·6

- **사이클5**: MCP 리소스 2종(guide: 단위규약·워크플로 / taxonomy: 라이브 분포) + 프롬프트 2종(find_material·register_test_data). 인메모리 프로토콜 왕복 테스트. 함정: conftest가 app.insights를 리로드 안 하면 taxonomy 리소스가 stale 모델 클래스로 매퍼 에러 — 리로드 체인에 추가. 6a63bc7.
- **사이클6**: 시연 영상 재녹화(48.8s — 카테고리 칩·brush 드래그·신뢰도 가드·편집·점탄성) + showcase에 MCP 등록 실출력 턴(DP980, E=207.0, JC R²=0.9986) 추가. 20도구 양방향 카피. 937382c.

## 2026-07-10 — 사이클 7: SIF 패키징 리허설(D1 해소)

fastapi_react 스택 레시피 그대로 재현: git archive 작업본 → pnpm install --frozen-lockfile(락파일 정합 ✓) → pnpm build(자산 상대경로 6/절대 0, C6 ✓) → 새 venv pip install -e backend → 런처 env만으로(PORT/ROOT_PATH/HEAX_DATA_DIR, MATERIALTWIN_* 없음) uvicorn 기동 → health·index 200 + 재료 생성 → **SQLite가 HEAX_DATA_DIR에 안착(D1 실증 해소)**. config.py에 HEAX_DATA_DIR 폴백 추가(MATERIALTWIN_DATA_DIR > HEAX_DATA_DIR > 개발 폴백). .portal/manifest.yaml v1.0.0으로 갱신(draft 해제·source git·MCP 서술). pytest 91 passed.
남은 백로그: 초탄성 카드(고무 단축인장 데이터 확보 대기)만 남음 — 전 항목 완료.

## 2026-07-10 — 사이클 8: 적대적 리뷰 라운드 2 (3에이전트)

백로그 소진 후 최근 변경(N+1·MCP 리소스·config 폴백·strain-source 마이그레이션·sparse 사다리)을 3개 병렬 리뷰어로 재검증. 확정 결함 3건(전부 수정):
- **MEDIUM** config.py: 빈 문자열 `MATERIALTWIN_DATA_DIR=""`가 pydantic에서 `PosixPath('.')`→CWD로 강제돼 방금 만든 HEAX_DATA_DIR 폴백을 조용히 우회. `str(data_dir) in ("",".")` + `not database_url` falsy 가드. test_config.py 5건 신규.
- **LOW** f4c2a91d55e0 PG downgrade의 `_CK_OLD`가 초기 스키마(IS NULL OR 접두 없음)와 텍스트 불일치 — 기능 등가지만 DDL 드리프트. 초기 스키마와 문자 일치시키고 PG에서 upgrade→downgrade 단계별 CHECK 텍스트 실대조.
- **LOW** material-detail: activeId 설정 effect가 paint 후 실행돼 점탄성 클라 네비 시 1프레임 빈 화면 — effectiveActiveId(첫 시편 즉시 폴백) 파생값 도입, 렌더 비교 5곳 교체.
리뷰어가 확인한 무결함: insights outerjoin(NULL 정렬 견고)·r² 사다리 가드·MCP 리소스·청크 분리·비물성 툴팁 단위·훅 규칙. pytest 96 passed.

## 2026-07-10 — 사이클 9: 적대적 리뷰 라운드 3 (파서·인제스트 + 수식·저장·프런트)

파서·인제스트 단독 에이전트 + 수식·저장·프런트 워크플로(find→verify)로 미검토 영역 전수. 확정 결함 8건 전부 수정.
파서·인제스트(4): remap 데이터 소실(HIGH)·N/mm² 등 미지단위 무음 오변환(MED~H)·고무 대변형 %오변환(HIGH~M)·compute_all 빈배열(LOW).
수식·저장·프런트(4): reaper cross-process 경합(HIGH, mtime 유예)·fit_prony E_inf=0 접힘(MED, 꼬리 선추정)·JC 초기값 미클램프(MED)·upload createdIds 중복재료(MED).
검증: pytest 108 passed, N/mm² 라이브 E=200GPa, 업로드 마법사 브라우저 렌더.

## 2026-07-11 — 사이클 10: 적대적 리뷰 라운드 4 (횡단 정합성)

웹↔MCP·단위 파이프라인·에러 일관성 3렌즈 워크플로. 확정 6건 전부 수정:
- **HIGH** mcp get_material이 Test.valid 미필터·valid 필드 미노출 → 웹에서 제외한 이상치를 LLM이 유효 물성으로 제시(웹·list_materials와 모순). valid/invalid_reason 노출 + guide 명시.
- **MED** 웹 material-detail 기본 활성 시편이 첫 시편의 invalid 대표시험일 수 있어 insights/mcp(유효 최소 test.id)와 갈림 — reps.find(valid) 우선 defaultActiveId.
- **MED** upload sniffMut.onError가 ApiError.message(영어) 토스트 — errorMessage(e)로 통일.
- **MED~LOW** mcp 에러 표기 혼재(영어·dict/list/str) — 읽기도구·get_mat_card·search·plot 전부 한국어화, get_curve/plot_curve read_curve FileNotFoundError 가드, search_by_property에 Test.valid 필터(웹 정합).
검증: pytest 110 passed(정합성 테스트 2건 추가), 프런트 빌드, 웹 상세(탄소성·점탄성) 브라우저 렌더 정상.
누적: 자율 루프 4라운드 적대적 리뷰로 실결함 30건 발견·수정(라운드1:13, 2:3, 3:8, 4:6).

## 2026-07-12 — 사이클 11: 적대적 리뷰 라운드 5 (동시성·스케일, 멀티프로세스 재현)

웹↔MCP 공유 SQLite에서 실제 멀티프로세스/스레드로 재현한 확정 6건 중 5건 수정(1건 성능은 보류).
- **MED** 웹 _load_curve TOCTOU(exists 후 read 사이 삭제)→500 — read를 FileNotFoundError/OSError 가드로 404(MCP는 이미 가드였음).
- **MED** 시편 라벨 경합: _next_label COUNT+1이 동시 등록에서 같은 S1 조용히 중복(UNIQUE 부재) — Specimen UNIQUE(material_id,label) + 마이그레이션 a72e1f3c8b90 + _add_specimen 재시도 헬퍼. **8-way 동시 등록 재현으로 S1~S8 유일 확인**(이전 S1×8).
- **MED** ProcessedResult 업서트(SELECT→INSERT) 경합: pr 없는 test 동시 재계산 시 test_id UNIQUE 위반 크래시 — commit을 try/except IntegrityError→rollback→재조회 UPDATE로(웹 compute_properties + MCP recompute_properties 양쪽).
- **MED** 저모듈러스(E<0.1GPa) _g 2자리 반올림 0.0→truthiness 필터 누락으로 property_space/family_stats vs property_stats 불일치 — is-not-None 필터 + _g 작은값 정밀도.
- **MED** MCP list_materials N+1(재료당 2쿼리)+limit 상한 없음 — 단일 outerjoin(insights와 동일 패턴)+limit≤200.
- 보류: 인사이트 5엔드포인트 각자 _material_rows(각 1쿼리로 이미 최적, 수천 재료 전엔 무의미, 결합은 프런트 변경 필요).
검증: pytest 112 passed, 마이그레이션 SQLite/PG 양쪽 클린+downgrade 왕복, 8-way 동시등록 재현.
누적: 5라운드 적대적 리뷰로 실결함 36건 발견(1:13,2:3,3:8,4:6,5:6), 35건 수정.
