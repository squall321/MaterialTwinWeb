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
- [ ] ColumnMapper(수동 컬럼 매핑 재파싱 UI) — sniff/IssuePanel은 됐으나 수동 매핑 폼은 D2 샘플 후

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
