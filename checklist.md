# MaterialTwinWeb 체크리스트

> [PLAN.md](PLAN.md) Phase 1(기초 인장 MVP) 기준. 완료 시 `[x]`. 상세 근거는 [context-notes.md](context-notes.md).

## Phase 0 — 프로젝트 초기화
- [x] `fastapi-react` 템플릿 내용을 메인 폴더로 복사 (backend/, frontend/, .portal/)
- [x] 이름 메타데이터 변경 (pyproject `materialtwin-web`, package.json, manifest `materialtwin_web`, index.html 타이틀)
- [x] git 초기화 + remote 등록 (push는 gh 인증 후 사람이 진행)
- [x] PLAN.md / checklist.md / context-notes.md 생성
- [ ] **D1** `.portal/manifest.yaml` 영속 볼륨 선언 가능 여부 확인 (HEAXHub 런처) — 운영 배포 전 필수
- [ ] **D2** testXpert 샘플 파일 2~3개 확보 — ZwickText 파서 확정 전 필수

## Phase 1 — 백엔드 골격
- [ ] `app/config.py` pydantic-settings (DATABASE_URL, DATA_DIR=`./var/data`, MAX_UPLOAD_MB)
- [ ] `app/db.py` engine/SessionLocal/Base/get_db + **PRAGMA foreign_keys=ON** 리스너
- [ ] `app/models.py` 5테이블 (material/specimen/test/raw_curve_ref/processed_result) + CHECK 제약
- [ ] `app/schemas.py` Pydantic v2 DTO
- [ ] `app/units.py` SI 정규화/표시변환 단일 모듈
- [ ] `app/main.py` 얇은 create_app() 으로 교체 (인메모리 `_tasks` 스캐폴드 삭제, StaticFiles 마운트 유지)
- [ ] `app/routers/` (health, materials, specimens, uploads, properties) + `api_router`
- [ ] pyproject 의존성 추가 (sqlalchemy, numpy, pandas, pyarrow, pydantic-settings, python-multipart, charset-normalizer, pyyaml)
- [ ] `init_db()` create_all() 동작 확인

## Phase 1 — 파서 서브시스템
- [ ] `app/parsing/base.py` dataclass(ParseResult/ParsedSpecimen/ColumnSpec/ParseIssue) + ParserBase (parse()=graceful, 예외 금지)
- [ ] `app/parsing/registry.py` sniff 점수 디스패치
- [ ] `app/parsing/column_map.py` ColumnRole + resolve_columns()
- [ ] `app/parsing/validate.py` 물리 검증
- [ ] `app/parsing/parsers/generic_csv.py`
- [ ] `app/parsing/parsers/zwick_textxpert.py` (structure 휴리스틱은 스텁+TODO, 샘플 확보 전 "완성" 금지)
- [ ] `app/parsing/config/column_aliases.yaml`
- [ ] 합성 픽스처 단위테스트 (독일식 소수점/`;`/움라우트/단위행)

## Phase 1 — 적재 & 곡선 저장
- [ ] `app/curve_store.py` Parquet(zstd) I/O + LTTB 다운샘플
- [ ] `app/ingest.py` 업로드→파서→units 정규화→검증→DB적재→Parquet 저장 (파일 먼저 fsync→DB 커밋)
- [ ] 곡선 경로 `DATA_DIR/curves/{material_id}/{test_id}.parquet`, DB엔 상대경로만
- [ ] 삭제 시 파일 앱레이어 정리 (CASCADE는 파일 못 지움)
- [ ] **양 DB FK CASCADE 테스트** (SQLite)

## Phase 1 — 물성 계산 (analysis.py, numpy만)
- [ ] 영률 E (toe보정 ON, 절편포함 회귀, R²≥0.99 거부, 고정구간+수동조정, params에 구간·R² 반환)
- [ ] 0.2% offset Rp0.2 (offset 직선 교점, 취성 null+플래그)
- [ ] UTS(Rm), 균일연신율 Ag, 파단연신율 A, 단면감소율 Z(Af 있을 때)
- [ ] Hollomon n/K (log-log 회귀)
- [ ] strain_source 결정 (extensometer 우선 / crosshead 플래그)

## Phase 1 — 프론트엔드
- [ ] 의존성 설치 (echarts, TanStack Router/Query, react-hook-form+zod, sonner, shadcn 핵심, tailwind, @fontsource/inter)
- [ ] `router.tsx` createHashHistory + 라우트
- [ ] `api/client.ts` request<T>() 상대경로 캡슐화 + `api/uploads.ts` FormData 전용 헬퍼
- [ ] `/upload` 4단계 마법사 (Dropzone, ParserDetectBadge, ColumnMapper, SpecimenMetaForm, RawPreviewChart)
- [ ] `/materials` 재료 라이브러리
- [ ] `/materials/$id` StressStrainChart(ECharts) + PropertyTable + brush 영률 구간 picker
- [ ] markPoint(UTS/Rp0.2)는 서버 풀해상도 인덱스 좌표 사용 (다운샘플 argmax 금지)
- [ ] `vite.config.ts` manualChunks로 echarts 분리, `base:"./"` 유지
- [ ] self-host 폰트 (CDN 금지)

## Phase 1 — 통합 검증 (완료기준)
- [ ] 합성 CSV 업로드 → 곡선 표시 → 물성 테이블 표시 E2E
- [ ] brush로 E 재계산 동작
- [ ] `pnpm build` 후 서브경로(`ROOT_PATH=/apps/materialtwin_web`) 마운트 스모크 테스트 (자산 상대경로 확인)
- [ ] `/api/health` 200
