# MaterialTwinWeb 체크리스트

> [PLAN.md](PLAN.md) Phase 1(기초 인장 MVP) 기준. 완료 시 `[x]`. 상세 근거는 [context-notes.md](context-notes.md).

## Phase 0 — 프로젝트 초기화
- [x] `fastapi-react` 템플릿 내용을 메인 폴더로 복사 (backend/, frontend/, .portal/)
- [x] 이름 메타데이터 변경 (pyproject `materialtwin-web`, package.json, manifest `materialtwin_web`, index.html 타이틀)
- [x] git 초기화 + remote 등록 (push는 gh 인증 후 사람이 진행)
- [x] PLAN.md / checklist.md / context-notes.md 생성
- [x] 적대적 보증(§13) + 프리미엄 UX/UI(§14) 부록 작성, 치명/높음(C1~C6,C11) 본문 반영
- [ ] **D1** 영속 볼륨 — ★C7: 런처가 추가 바인드 미지원(`cleanenv=True`). 플랫폼 선결 과제. 개발은 `./var/data` 폴백 + 기동 WARNING
- [ ] **D2** testXpert 샘플 파일 2~3개 확보 — ZwickText는 그 전까지 GenericCsv+독일별칭 wrapper(★C12)

## Phase 1 — 백엔드 골격
- [x] `app/config.py` pydantic-settings (DATABASE_URL, DATA_DIR=`./var/data`, MAX_UPLOAD_MB) + **DATA_DIR 미주입 시 폴백 WARNING 로그**(★C7)
- [x] `app/db.py` engine/SessionLocal/Base/get_db + **PRAGMA foreign_keys=ON** + **journal_mode=WAL + busy_timeout=5000**(★C2 치명)
- [x] `app/models.py` 5테이블 (material/specimen/test/raw_curve_ref/processed_result) + CHECK 제약. material에 nullable `owner_id` 슬롯만 예약(★C15 D8)
- [x] `app/schemas.py` Pydantic v2 DTO
- [x] `app/units.py` SI 정규화/표시변환 단일 모듈
- [x] `app/main.py` 얇은 create_app() 으로 교체 (인메모리 `_tasks` 스캐폴드 삭제, StaticFiles 마운트 유지)
- [x] `app/routers/` (health, materials, specimens, uploads, properties) + `api_router`
- [x] pyproject 의존성 추가 (sqlalchemy, numpy, pandas, pyarrow, pydantic-settings, python-multipart, charset-normalizer, pyyaml)
- [x] `init_db()` create_all() 동작 확인

## Phase 1 — 파서 서브시스템
- [x] `app/parsing/base.py` dataclass(ParseResult+**confidence**/ParsedSpecimen/ColumnSpec/ParseIssue) + ParserBase. **parse 성공 ≠ 계산 허가**(★C5): confidence 낮거나 미해결 INFO면 "확인 필요" 상태
- [x] `app/parsing/registry.py` sniff — **절대 임계(0.3) 대신 상대 규칙**(1등이 2등과 유의분리/필수 시그니처 충족, ★C5). 상수 쓰면 config화+placeholder 주석
- [x] `app/parsing/column_map.py` ColumnRole + resolve_columns()
- [x] `app/parsing/validate.py` 물리 검증 + **오매핑 가드**(단조성·채널 상관·자릿수, ★C5)
- [x] `app/parsing/parsers/generic_csv.py`
- [x] `app/parsing/parsers/zwick_textxpert.py` — **GenericCsv+독일별칭 프리셋 wrapper로 축소**(★C12). 다중시편 분기 P1 제거(파일분리만), 5.3b 헤더/단위행은 `# ASSUMPTION, needs D2` 스텁
- [x] `app/parsing/config/column_aliases.yaml` (형식만 + 엔트리 비움, D2 후 채움)
- [x] 합성 픽스처 단위테스트 (독일식 소수점/`;`/움라우트/단위행, parse 예외 0건)

## Phase 1 — 적재 & 곡선 저장
- [x] `app/curve_store.py` Parquet(zstd) I/O + LTTB 다운샘플
- [x] `app/ingest.py` 업로드→파서→units 정규화→검증→DB적재→Parquet 저장. **Parquet 쓰기는 DB 트랜잭션 밖**(★C2)
- [x] 곡선 경로 **`DATA_DIR/curves/{test_id}.parquet`**(불변 키만, ★C4), DB엔 상대경로만
- [x] 쓰기 프로토콜 `.tmp.{uuid}` → fsync → **atomic rename** → INSERT 커밋(★C4)
- [x] **부팅 reaper** — `init_db()` 직후 고아 `.parquet/.tmp` 삭제, 파일 없는 포인터 `storage='missing'` 마킹(★C4)
- [x] 삭제 시 파일 앱레이어 정리 (CASCADE는 파일 못 지움)
- [x] **양 DB FK CASCADE 테스트** (SQLite)

## Phase 1 — 물성 계산 (analysis.py, numpy만)
- [x] **σ-ε 골든 픽스처 1개**(선형+멱법칙) 작성 — 정확도 게이트의 기준(★C3)
- [x] 영률 E (toe보정 ON, 절편포함 회귀, **R² confidence 등급 high/ok/low — 거부 아님**, 고정구간+수동조정, params에 구간·R²·confidence 반환)(★C1)
- [x] **폴리머 분기**: `category='polymer'`는 secant modulus(0.05~0.25%) 또는 1% offset(★C1)
- [x] 0.2% offset Rp0.2 (offset 직선 교점, 취성 null+플래그)
- [x] UTS(Rm), 균일연신율 Ag, 파단연신율 A, 단면감소율 Z(Af 있을 때)
- [x] Hollomon n/K (log-log 회귀)
- [x] strain_source 결정 (extensometer 우선 / crosshead 플래그)
- [x] `ProcessingParams` Pydantic 모델 + `schema_version:int`(raw dict 금지, ★C10)

## Phase 1 — 프론트엔드 (디자인 시스템은 §14 SSOT 준수)
- [x] 의존성 설치 (echarts, TanStack Router/Query, react-hook-form+zod, sonner, shadcn 핵심, tailwind, @fontsource/inter)
- [x] **디자인 토큰**(§14.2): `index.css` `:root`(다크 기본)+`.light` CSS 변수, Okabe-Ito 차트 8색, tailwind.config 연결
- [x] `router.tsx` createHashHistory + 라우트
- [x] `api/client.ts` request 헬퍼(상대경로 캡슐화) + `api/uploads.ts` FormData 전용 헬퍼
- [x] `/upload` 4단계 마법사 (Dropzone, ParserDetectBadge, SpecimenMetaForm, A0 자동계산, Preview) + **IssuePanel**(★C9)
- [x] `/materials` 재료 라이브러리 (검색·생성 다이얼로그)
- [x] `/materials/$id` StressStrainChart(ECharts §14.4) + PropertyTable + brush 영률 picker + **재료단위 평균±σ 요약 행**(★C8)
- [x] markPoint(UTS/Rp0.2)는 서버 물성 스칼라 기반 좌표 사용 (다운샘플 argmax 금지)
- [x] **ECharts CSS변수 브리지**(getComputedStyle 런타임 주입, §14.3), large는 raw 미리보기 전용(★C14)
- [x] **모션**(§14.5): CSS transition/WAAPI만(framer-motion 미사용), prefers-reduced-motion 대응(§14.7)
- [x] `vite.config.ts` manualChunks로 echarts 분리, `base:"./"` 유지
- [x] self-host 폰트 (CDN 금지)
- [x] ColumnMapper(수동 컬럼 매핑 재파싱 UI) — sniff 컬럼별 역할 재지정 → 커밋 시 remapUpload로 재파싱. 브라우저 검증

## Phase 2/3 — 진응력·구성방정식·통계·카드 (완료)
- [x] **진응력 변환**: `true_stress.py` ε_true=ln(1+ε)·σ_true=σ(1+ε), Considère 넥킹(dσ_true/dε_true=σ_true). `kind=true` 곡선 API. 브라우저: 넥킹 마커 ε_true=0.15(=n) 검증
- [x] **구성방정식 피팅**: `fitting.py` Hollomon/Swift/Voce/JC(scipy curve_fit, graceful). constitutive_fit 테이블. Hollomon K=700MPa·n=0.15 R²=1.0 복원
- [x] **재료 통계**: `/materials/{mid}/stats` 평균±σ(numpy on-the-fly, 새 테이블 0, C8)
- [x] **LS-DYNA 카드**: `cards.py` *MAT_024 + *DEFINE_CURVE, `card.k` export(RFC 5987)
- [x] 프론트: 공칭↔진 토글, 넥킹 마커, FitPanel(피팅 계산·모델별 R²·카드 다운로드)
- [x] pytest 34개 통과(진응력·넥킹·Hollomon 복원·카드·통계·API), tsc/build 통과
- [ ] auto E구간선택 — Phase 4로 미룸 / crosshead 컴플라이언스 보정 — 신뢰도 플래그만(P2 슬롯)

## Phase 1 — 통합 검증 (완료기준, ★C3 게이트)
- [x] [정확도] 골든 픽스처 → E ±2%, Rp0.2 ±2MPa, UTS ±0.5% (pytest assert) — test_analysis_accuracy 통과
- [x] [brush] 구간 POST = numpy polyfit 일치, low-confidence는 거부 아닌 플래그 — test_api 통과
- [x] [graceful] 깨진 인코딩/콤마소수점/움라우트 → parse 예외 0건 + ParseIssue 수집 — test_parsing 통과
- [x] [서브경로] 자산 전부 `./assets/`(절대경로 grep 0) ✅, uvicorn 루트 서빙 GET / ·/api/health ·자산 ·POST material 전부 200/201 ✅. 해시 라우팅이라 deep-link는 `/#/...`로 서버엔 `/`만 도달(C6 충족)
- [x] [reaper] 부팅 스윕 고아 파일 삭제 — test_ingest 통과
- [x] `/api/health` 200 (test_api) | [ ] WCAG AA 대비 실측 스폿체크(§14.7) — 브라우저 실행 시
- [x] **pytest 22개 전부 통과 (python3.12 .venv)**
- [x] **브라우저 E2E 실측**(Playwright): 3화면 렌더·업로드 4단계 마법사 끝까지·곡선 차트·confidence 배지 동작 확인

## Phase 1 — 발견 버그 (브라우저 E2E에서, context-notes 상세)
- [x] **BUG-1【치명】** 단위행 미파싱 → 물성 1000배 오차. **수정**: resolve_columns에 units 인자 추가, generic_csv가 헤더-데이터 사이 비수치행을 단위행으로 흡수(인라인 단위 우선·폴백), INFO `units_from_unit_row` 노출. 회귀 테스트 2개 추가. 브라우저 재검증: E=200GPa·Rp0.2=276MPa·UTS=540MPa·confidence=high ✅
- [x] **BUG-2【낮음】** upload.tsx 신규 재료 "재료 보기" disabled. **수정**: commitMut가 {materialId,ingest} 반환→committedMaterialId state 저장, 버튼이 그걸로 활성/네비게이트. 브라우저 재검증: 신규재료 커밋→버튼 활성→/materials/3 이동 ✅

## Phase 4 — 운영화 (부분 완료)
- [x] **Alembic 마이그레이션**: `migrations/`(env.py는 Base+settings 단일소스), 초기 마이그레이션(6테이블 autogenerate). SQLite·Postgres 양쪽 upgrade/downgrade 검증
- [x] **모델↔마이그레이션 드리프트 가드**: `alembic check`를 pytest로(`test_migrations.py`). 컬럼 추가 후 마이그레이션 누락 시 실패
- [x] **Postgres 실구동 호환성**: `psycopg` 옵셔널 의존성, 실 PG16에 전체 플로우(JSON 왕복·DateTime tz·ingest E±2%·FK CASCADE) 통과(`test_postgres_compat.py`, MTW_TEST_POSTGRES_URL 게이트)
- [x] 개발=create_all(빠름) / 운영=`alembic upgrade head`. `migrations/README.md`에 전환 절차
- [x] pytest 38개+1스킵(SQLite), PG 포함 시 39개 통과
- [ ] **zse/zsx 바이너리 파서** — D2 실샘플 없이 불가(보류)
- [ ] 별칭 학습루프 / 인증(owner_id 슬롯만 존재) — 후순위

## 자율 진화 백로그 (2026-07-10 — 우선순위순, 루프가 위에서부터 소비)

- [x] insights.py N+1 제거 — _material_rows를 outerjoin 1쿼리로, property_stats 내부 재사용 (재료 70개에 엔드포인트당 ~140쿼리)
- [x] Ashby 차트 비강도(σ/ρ)·비강성(E/ρ) 툴팁 노출 + AshbyPoint 타입 선언 (백엔드는 이미 반환)
- [x] 인사이트 elong_pct 히스토그램 렌더 (데이터 수신만 하고 미표시)
- [x] 프런트 코드 스플리팅 — echarts 청크 분리로 500kB 경고 해소 (manualChunks)
- [x] 업로드 마법사 E2E 회귀: 골든 CSV로 브라우저 실업로드 → 물성 확인 (Playwright)
- [x] showcase.html·demo.mp4 갱신 — 새 기능(편집·삭제·카테고리 필터·brush·MCP 등록) 반영
- [x] MCP prompts/resources 노출 검토 — LLM이 도구 사용법을 스스로 발견하게
- [x] Postgres 실인스턴스 검증 (mtw_test 계정 존재 — test_postgres_compat 참고)
- [x] 단일 SIF 패키징 + /apps/<slug>/ 서브패스 배포 리허설
- [ ] 초탄성(Ogden/Mooney) 카드 — 고무 단축인장 데이터 확보 후

규칙: 한 사이클 = 항목 1개 구현 → 검증(pytest·build·필요시 브라우저) → 시맨틱 커밋·푸시 → 체크 표시 → context-notes 기록. 검증 실패 상태로 커밋 금지.

### 적대적 리뷰 라운드 2 발견 (2026-07-10 — 3에이전트, 전부 해결)
- [x] config.py 빈 문자열 MATERIALTWIN_DATA_DIR=""가 CWD로 새어 HEAX 폴백 우회 (MEDIUM) — falsy 가드 + test_config.py 5건
- [x] 마이그레이션 f4c2a91d55e0 PG downgrade _CK_OLD 텍스트 비대칭 (LOW) — 초기 스키마와 문자 일치, PG 실검증
- [x] material-detail 점탄성 클라 네비 activeId-null 1프레임 플리커 (LOW) — effectiveActiveId 파생 폴백

### 적대적 리뷰 라운드 3 — 파서·인제스트 (2026-07-10, 재현 검증, 전부 해결)
- [x] remap_upload 재적재 전 커밋삭제로 비가역 데이터 소실 (HIGH) — 새 적재 성공(valid) 후에만 원본 교체, 실패 시 원본 보존+422
- [x] N/mm²(=MPa, Zwick/DIN 표준) 등 미지 단위 1e6배 무음 오변환 (MEDIUM~HIGH) — 단위맵 확장(N/mm²·μm U+03BC·cm·MN) + 미지단위 WARN 보고
- [x] 무단위 대변형(고무 비 2.0)을 %로 오변환해 100배 축소 (HIGH~MED) — 카테고리별 임계(대변형 15) + INFO 보고
- [x] compute_all 빈 배열 ValueError (LOW) — 진입부 graceful 가드

### 적대적 리뷰 라운드 3 — 수식·저장·프런트 (2026-07-10, 재현 검증, 전부 해결)
- [x] reaper가 in-flight 적재의 미커밋 곡선을 오삭제(cross-process 경합, HIGH) — mtime 유예기간(기본 600s) 가드
- [x] fit_prony n_terms=3 고정 τ가 t.max에 닿아 E_inf=0으로 접힘(모든 시드 점탄성, MED) — E_inf 꼬리 선추정+초과분 적합, E_inf 오차 0%
- [x] johnson_cook_card_params 초기값 미클램프로 비멱법칙 경화 시 curve_fit 실패→완전소성 카드(MED) — p0 경계 클램프
- [x] upload.tsx createdIds reset[meta,file]이 materialId까지 초기화→중복 재료(MED) — 재료 정체성/시편 이펙트 분리

### 적대적 리뷰 라운드 4 — 횡단 정합성 (2026-07-11, 재현 검증, 전부 해결)
- [x] mcp get_material이 valid 미필터·미노출 → LLM이 제외 이상치를 유효물성으로 오인(HIGH) — valid/invalid_reason 노출, guide 명시
- [x] 웹 기본 대표 시편이 invalid 시험일 수 있어 insights·mcp와 갈림(MED) — valid 우선 defaultActiveId
- [x] upload sniffMut.onError가 영어 원문 토스트(MED) — errorMessage(e)
- [x] mcp 읽기·카드·검색·plot 에러가 영어·모양 불일치(MED~LOW) — 한국어 통일 + get_curve/plot_curve read_curve 가드 + search_by_property valid 필터

### 적대적 리뷰 라운드 5 — 동시성·스케일 (2026-07-12, 멀티프로세스 재현, 전부 해결)
- [x] 웹 _load_curve TOCTOU: 동시 delete↔read에서 FileNotFoundError→HTTP 500(MED) — read 가드로 404
- [x] 시편 라벨 경합: 동시 등록이 같은 S1 조용히 중복(MED) — UNIQUE(material_id,label)+_add_specimen 재시도, 8-way 재현 검증
- [x] ProcessedResult 업서트 경합: pr 없는 test 동시 재계산 IntegrityError 크래시(MED) — commit try/except rollback→UPDATE (웹+MCP)
- [x] 저모듈러스(E<10MPa) truthiness 필터 누락으로 대시보드 수치 불일치(MED) — is-not-None 필터 + _g 정밀도
- [x] MCP list_materials N+1 + limit 상한 없음(MED) — 단일 outerjoin + limit≤200
- [~] 인사이트 5엔드포인트 각자 _material_rows 풀스캔(MED, 성능) — N+1 이미 제거로 각 1쿼리, 대규모(수천)에서만 유의미. 결합 엔드포인트는 API+프런트 변경 필요라 보류.

### Google Drive 데이터·SIF 동기화 (2026-07-16, 손실 없는 병합, 실 Drive 검증)
- [x] app/sync.py — 이식가능 번들 export(안정키 material_code/name·test content-hash) + 병합 import(union, 삭제 없음)
- [x] python -m app.sync CLI + pytest 4(멱등·운영추가보존·신규추가·시험복원)
- [x] scripts/drive-sync/ — sync-to-drive(번들+SIF·retain·sha256)·sync-from-drive(pull→병합)·PROJECT.conf·_common.sh
- [x] SIF: sha256+버전명+LATEST+retain, 덮어쓰기 없이 .bak 보존
- [x] 실 Drive 라운드트립: 운영DB(1종)→Drive pull 병합→71종(70추가+운영전용강 보존 True)

### HEAXHub 포털 배포 복구 (2026-07-16)
- [x] 근본원인: port_allocator가 OS 점유 미확인으로 9100(node_exporter) 배정 → socket bind 검사로 점유 포트 스킵 (HEAXHub 커밋 59c666e)
- [x] 구 스키마 볼륨 DB 재생성 + 포트 9118 재배정 + caddy 등록 (백엔드 재시작 없이 launcher 재호출)
- [x] Drive 병합으로 70종 시드 → 포털에서 조회·인사이트·곡선 전부 렌더 검증
- [x] (후속) 앱 부팅 create_all→alembic 관리(빈DB create_all+stamp head, 버전DB upgrade head) — 구버전 볼륨 자동 마이그레이션, 배포 볼륨 stamp head

### 43차 EE — 물성키 열 개를 열고 버려졌던 값 52행을 넣는다 (2026-08-19)
- [x] 도메인 어휘 확인 — `magnetic.*` 5키에 (BH)max 없음 · 246개 정의 전수 대조로 열 자리 확정
- [x] taxonomy 10키 추가(`app/property_taxonomy.py`) → 246 → 256, 시드 멱등 검증
- [x] 적재기 범위 가드 10개(`ingest_agent_json.py`) — 하한 0 원칙(브리프 161)
- [x] Alembic `f7a8b9c0d1e2` — 정의 행 삽입, 전제 없음(b2c3d4e5f6a7 함정 회피)
- [x] `integrity_check` 에 (BH)max ≤ Br²/(4µ₀) 상시 검사 추가(브리프 431·339 반올림 구간)
- [x] 값 52행 적재 — (BH)max 24 · 분리막 6 · 광학 13 · 전지계면 7 · 짝 Br 2
- [x] 물리 상한 검산 — NdFeB 16칸 + 페라이트 7칸 전부 통과(비 0.90~0.97), MGOe 병기 검산 ±1%
- [x] **로더 결함 발견·수정** — 451 중앙값 가드가 부정문("만들지 않았다")에 걸려 실측을 강등
- [x] `integrity_check` 중앙값 항목을 SQL → 파이썬(적재기와 같은 판정), 옛 SQL 이 놓친 1건 교정
- [x] 마이그레이션 예행 4종 — 운영head 사본·구버전(w40) 사본·멱등 재적용·downgrade 양방향
- [x] `integrity_check` 이상 0 · `verdicts_check` 이상 0 · `pytest` 190 passed
- [ ] (인계) SmCo 421·422 · Alnico 423 의 (BH)max — Recoma·ChenYang 시트가 손에 없어 미적재
- [ ] (인계) 하드페라이트 나머지 ~20등급 · PC 광학등급 — **재료가 없다.** 새 재료 승인 필요
- [ ] (인계) 중앙값 가드가 강등했을 수 있는 기존 441행 — 표시가 없어 되돌릴 수 없다

### 45차 GC — 화학 내구성 두 키를 열고, 하드페라이트 등급 25종을 세운다 (2026-08-28)
- [x] 브리프 필수 절 통독(0·1·2·129·140·145·225·339·419·429·431·443·451·453·456·468·470·471·478~482)
- [x] ① AGY 내구성표 원본 재확인 — attributes 에 없어 원본 PDF 를 렌더로 다시 읽었다(§479·33·128)
- [x] ① NEG 봉지 프릿 내산성표 원본 재확인 — 12칸, 나머지 두 열은 전부 `-`
- [x] ① 키 둘 신설 — `durability_mass_loss_fraction`[1] · `durability_mass_loss_per_area`[kg/m²]
- [x] ① taxonomy · 적재기 범위 가드(하한 음수) · Alembic `c0d1e2f3a4b5`
- [x] ② Eclipse 페라이트 등급표 3장 전사 + 렌더 대조 4회(§88)
- [x] ② 중복 조회 — 등급명 41개 전수, 걸린 것은 기존 424·425·2533 셋뿐(§435)
- [x] ② 물리 상한 — 25종 중 24종 통과(비 0.75~0.99). **Y28H-2 는 위반이라 Br·BHmax 를 안 넣었다**
- [x] ② MGOe · kG · kOe 왕복 검산 — C1 HcJ 8% 어긋남(버림) · C7·C10 끝자리(병기 칸만 버림)
- [x] ①② 값 적재 — 278행 · 신규 재료 25종
- [x] 마이그레이션 예행 4종 — 운영 head 사본 · 멱등 재적용 · 빈 DB 전체 사슬 · downgrade 양방향
- [x] `integrity_check` 신규 위반 0 · `verdicts_check` 이상 0 · `pytest` 193 passed
- [x] ③ SmCo 421·422 · Alnico 423 (BH)max — **조달 성공.** 11행 추가(짝 칸 포함)
- [ ] (인계) 물성값 0인 재료 2종(2649 업로드시험강 · 2650 삭제확인강, 2026-08-22 MCP 수동세션 잔재)
      — 내 배치가 만든 것이 아니라 지우지 않았다. `integrity_check` 이상 1개는 이것 하나다
- [ ] (인계) Y28H-2 의 Br·BHmax — GB/T 3217 원본이나 다른 벤더 시트로 다시 열어야 한다
- [ ] (인계) 미국규격 C11·C12 는 등급표에 행이 없다(대조표에만 나온다) — 값 없음

## 46차 HD — 코어 채우기 ② (2026-08-28)

- [x] 브리프 0·1·2·5·8·51·58·117·127·129·131·140·145·195·410·429·435·438·443·451·454·456·468 읽기
- [x] 표적 15종의 현재 코어 7물성 상태를 DB 로 확인(전부 0/7)
- [x] 벤더 시트를 **실제로 열기**(§127) — FM 300 · FM 73 · Meridian · Imerys SDS/SFG15 TDS · KGK 200A · ANISOLM AC-7206U · Shengyi S1170G
- [x] 등급이 안 닫히는 것(2271·2272·2274·2316) 판정 — 원문 verbatim 으로 근거 기록
- [x] 접근 부재(1098·1358·1359) 판정 + 1차 출처 DOI/서지 특정(§145)
- [x] 해당 없음 vs 부재 구분(2028·2029·2030 분말)
- [x] `ingest_agent_json.py --apply` — 47행, 거부 0
- [x] 채운 재료의 `attributes.core_fill_sheet` 에 결과를 **덧붙이기**(지우지 않음), 15종
- [x] 2316 의 낡은 `single_property_exception` 에 해소 표시(§89)
- [x] `integrity_check.py` 신규 위반 0 · `verdicts_check.py` 이상 0 · `pytest -q` 193 passed
- [x] 브리프 교훈 497~503 기록

## 47차 ID — 키 넷 개설 + 대기 값 적재 (2026-08-28)

- [x] 브리프 0·1·2·66·69·93·129·145·419·429·431·453·468·470·471·478·479·482·487·504·505 읽기
- [x] **인계 검증**(§479·505) — 넷 다 DB·원문으로 다시 셌다
  - [x] ① `n` 4행(1105 Dexter 0.77 · 1106/1107/1108 Zymet 0.62) — 인계 4행과 **일치**
  - [x] ② `ε_pl` 4행(0.5 / 1.5 / 1.5 / 1.5 %) — 인계 4행과 **일치**(인계문의 "3행" 정정이 옳았다)
  - [x] ③ 압축탄성계수 — 인계 **1행** → 실측 **6행**(신규 2 + 이관 4). §507 로 남겼다
  - [x] ④ 300 % 모듈러스 — 카탈로그 대상 2행 확인(2341 D1102 · 2342 D1161)
- [x] 원문 재확인 — Hohlfelder 2001 TABLE I · Solvay Torlon TDS · Rogers CLTE-AT · Kraton 4문서
- [x] BCB-hard 행(n 0.68 · ε_pl 5.7 %)이 카탈로그에 없음을 확인 — 1360 은 Cyclotene **4000 계열**(다른 논문)
- [x] 키 넷의 이름·조건축을 **각자의 형제 키**에 맞춤(§487) — 넷을 억지로 한 어휘로 묶지 않았다
- [x] ④ 축 이름을 DB census 로 결정 — `strain_pct`(172행 사용 중), 새 어휘 안 만듦(§419·509)
- [x] 범위 가드 넷 추가 — **하한 전부 0(무차원 지수만 −1)**(§150·161)
- [x] 이관 매처를 전 재료에 돌리고 좁힘(§480) — 후보 42행 → 채택 4행, 오탐 0. 남긴 둘 특정
- [x] 마이그레이션 `f3a4b5c6d7e8` — 현재 head `e2f3a4b5c6d7` 위에 얹음(전제 없음, §482)
- [x] 예행 3종 — 옛 운영 사본(`888056f1c5b8`) · 현재 운영 사본(`e2f3a4b5c6d7`) · downgrade 왕복
- [x] 운영 DB 적용 + `ingest_agent_json.py --apply` **12행 · 거부 0**(총 16행, 이관 4 포함)
- [x] 2318·2341·2342 의 낡은 "키가 없어 못 넣었다" 표시에 해소 표기(§89)
- [x] `integrity_check` **신규 위반 0**(기존 `물성값 0인 재료 2` 만) · `verdicts_check` 이상 0 · `pytest -q` 193 passed
- [x] 브리프 교훈 507~510 기록
- [ ] (인계) **Hohlfelder 2001 TABLE I `BCB-hard` 행 6칸이 그대로 막혀 있다** — 재료가 없다.
      Dow Cyclotene 3022, hard cure 250 °C/1 h(≈98 % 가교): σ_ys 48 · σ_UTS 90 MPa · E 2.9 GPa ·
      **n 0.68** · **ε_pl 5.7 %** · K_Ic 0.36 MPa·m^0.5. 재료를 세우는 것은 채굴이라 이 배치가 안 했다
- [ ] (인계) 재료 435 는 이제 `youngs_modulus` 가 0행이다 — 압축계수만 가진 재료다.
      Sandia OSTI 1213488 에 인장 탄성계수 열이 있는지 확인하면 §470 의 짝이 닫힌다
- [ ] (인계) 폼·엘라스토머 37행은 옮기지 않았다(§507) — 그쪽을 정리하려면 **키가 아니라
      `youngs_modulus` 의 오염 조사**가 먼저다(47차 IA 가 같은 자리에서 66행을 셌다)

## 53차 OC — packaging 코어 7물성 채굴 (2026-08-29)

- [x] 브리프 0·1·2·5·8·51·58·117·127·129·131·140·145·195·410·429·431·435·438·443·451·454·456·467·468·479·505·559·561 읽기
- [x] **조정자 실측 검증**(§479·505) — `subsystem='packaging'` 전수 재집계.
      인계 `재료 112 · 5,891행 · 코어 44%` → 실측 **재료 115 · 5,955행 · 코어 43.6%**(같은 파동 병렬 배치의 증분)
- [x] 재료별 빈 코어 칸 전수 census + 계열별 결손표 작성
- [x] **`attributes.core_fill_sheet` 확인**(45차 GD 인계) — packaging 5종 전부 **"없음"**.
      616(등급·공급사 미인쇄) · 2305~2308(Palaniappan 2000 A/B/C/D 익명, §58) — **열 문서가 없다**
- [x] 벤더 시트 **실제로 열기**(§127) — EPO-TEK 353ND(Rev XXIX)·H20E(Rev VIII/IX/XVIII 셋) ·
      Henkel LOCTITE ECCOBOND FP4526(2014-12)·FP4527(2018-11)·ABLESTIK 2025D(2014-04)·965-1L(2014-10) ·
      NEG Powder Glass 카탈로그(표 1·2) · Solder Connection 편찬표 · Xianyi Product Manual · Zymet X6-82-5LV
- [x] §506 행 단위 재조회 — 이미 쓴 벤더표에서 **안 옮긴 칸**을 찾았다(SAC105 k · Xianyi CTE 열)
- [x] §138 경계 적용 — CTE·열전도율은 옮기고 **솔더 인장강도·연신 열은 옮기지 않았다**
- [x] §133 적용 — Sn96.5Ag3.5 열전도율(55 대 33)·FP4526 CTE(25 대 33) 모순 처리
- [x] `ingest_agent_json.py --apply` **15행 · 거부 0** (코어 칸 +10)
- [x] `integrity_check.py` 신규 위반 0(기존 `물성값 0인 재료 2` 만) · `verdicts_check.py` 이상 0 · `pytest -q` **350 passed**
- [ ] (인계) NEG 분말유리 `Softening point` 10칸 — **키는 열렸는데 여전히 못 넣는다.**
      `thermal.viscosity_reference_temperature` 는 `viscosity_log10_poise` 가 조건축인데
      NEG 카탈로그는 점도값도 시험법도 안 찍는다. 분말유리 연화점은 DTA 흡열피크지 리틀턴점이 아니다 —
      log η 7.6 을 우리가 배정하면 그건 우리 값이다(§10). **재료 2634~2643 의 낡은 notes 를 갱신해야 한다(§89)**
- [ ] (인계) **재료 576 열전도율 26 W/(m·K) 의 `source_id` 가 3641(Solder Connection)인데
      그 행의 notes 자신이 "이 행만 출처가 Xianyi 다"라고 적는다.** Solder Connection 표는 이 합금 k 를 `-` 로 둔다.
      정정 경로(`corrections`)가 `source_id` 를 못 고친다 — 로더에 없는 필드다
- [ ] (인계) NEG 카탈로그 표 2 의 **LS-3075 행이 카탈로그에 없다**(형제 5종은 있다).
      `Application` 이 `Alkali-free glass` 라 display 계통일 수 있어 packaging 배치가 계통을 정하지 않았다
- [ ] (인계) FP4527 시트의 코어 밖 값 — 굽힘강도 17,000 psi · 굽힘탄성계수 10.3 GPa ·
      `Modulus @ 23ºC` 5.5 GPa · 파단연신 1.39 % · 선수축 0.135 %
