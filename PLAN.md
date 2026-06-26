# MaterialTwinWeb — 마스터 계획서

> 쯔윅(Zwick/Roell) testXpert 인장시험 데이터를 업로드받아 DB화하고, 재료 물성을 수려하게 구축·관리하는 웹 플랫폼. 본 문서는 5개 설계안과 3개 교차 비판을 종합한 단일 실행 계획이다. 베이스 템플릿의 **상대경로 / 단일 SIF / SQLite** 철학을 모든 결정의 상위 제약으로 둔다.

---

## 1. 프로젝트 개요 & 목표 & 범위

### 1.1 목표
인장시험 원시 데이터(CSV/TXT, 추후 Zwick 바이너리)를 업로드 → 파싱 → 검증 → 곡선 저장 → 기본 물성(E, Rp0.2, UTS, 연신율) 산출 → 수려한 차트/테이블로 표시·관리한다. ASTM E8/E8M, ISO 6892-1 용어와 정합한다.

### 1.2 범위 결정 원칙
교차 비판([overeng])의 핵심 지적을 수용한다. 5개 설계안은 도메인 이해도는 높으나 **자기들이 "2·3단계"라 라벨링한 것(피팅·진응력·통계·잡 시스템·Alembic·Postgres 호환층)을 1단계 스키마·라우터·의존성에 골격으로 미리 박는** 공통 과설계가 있다. 따라서 **골격조차 만들지 않고, 확장 슬롯(JSON `extra_metrics`/`attributes` 컬럼, list 반환 시그니처)만 남긴다.**

### 1.3 Phase 1 MVP 범위 (명확히)

| 영역 | Phase 1 IN | 로드맵 후반 OUT |
|---|---|---|
| 테이블 | `material`, `specimen`, `test`, `raw_curve_ref`, `processed_result`(test와 1:1, 계산 파라미터는 JSON 1칸) | `analysis_run`, `aggregate_result`, `constitutive_fit`, `upload_batch`, `upload_file`, `jobs` |
| 계산 | E(고정구간+수동조정+toe보정), Rp0.2, UTS, A%, Ag, Z(Af 있을 때), Hollomon n/K | auto E구간선택, 진응력/Considère/Bridgman, Swift/Voce/JC 피팅, 대표곡선/통계 |
| 파서 | GenericCsvParser, ZwickTextExportParser(텍스트만) | zse/zsx 바이너리, 별칭 학습루프, 재파싱 엔드포인트 |
| 백엔드 의존성 | numpy, pandas, pyarrow, sqlalchemy, pydantic-settings, python-multipart, charset-normalizer, pyyaml | scipy, alembic, psycopg, kaitai-struct |
| 인프라 | `create_all()`, PRAGMA FK ON, plain JSON 컬럼 | Alembic, JSONB variant, Postgres 호환층, 백그라운드 잡, sha256/보상트랜잭션 |
| 프론트 화면 | `/upload`, `/materials/$id`(곡선+물성테이블), `/materials` 목록 | `/compare`, `/dashboard` 히스토그램, `/export`(피팅), `/settings` |
| 프론트 의존성 | echarts(core+line), react-hook-form+zod, sonner, shadcn 핵심, TanStack Query, TanStack Router(hash) | framer-motion, zustand, cmdk, @fontsource/jetbrains-mono, lazy 고해상 재요청 |

---

## 2. 사용자 시나리오 (핵심 워크플로우)

### 2.1 워크플로우 A — 단일 시편 업로드 → 물성 확인 (주 시나리오)
1. 사용자가 `/upload`에서 testXpert CSV 파일을 드래그앤드롭한다.
2. 클라이언트가 첫 ~50줄을 읽어 인코딩/구분자를 1차 추정, 서버 `POST api/uploads/sniff`로 파서 후보·신뢰도를 받는다.
3. "testXpert 텍스트 감지됨" 또는 "일반 CSV — 컬럼 매핑 필요" 배지가 뜬다. 미인식이면 `ColumnMapper`로 time/force/displacement/strain 컬럼과 단위를 사용자가 지정한다.
4. 시편 메타 폼(형상 라디오: 평판→w0·t0·L0 / 봉상→d0·L0, 재료명·시험속도·온도)을 채운다. A0 자동계산 미리보기가 뜬다.
5. 힘-변위 raw 미리보기 차트 확인 후 "커밋" → 시편 생성 + 업로드 + 파싱 + 곡선 Parquet 저장.
6. `/materials/$id`로 이동, 공칭 응력-변형률 곡선 + 물성 테이블(E, Rp0.2, UTS, A%)이 표시된다.
7. 사용자가 차트에서 brush로 영률 회귀구간을 드래그 조정 → 실시간 E·R² 미리보기 → 확정 시 서버 재계산·영속.

### 2.2 워크플로우 B — 반복 시편(repeat) 묶음 업로드
1. 한 재료의 여러 시편 파일을 한꺼번에 드롭한다.
2. "한 재료의 repeat로 묶기" 토글 + 공통 메타 일괄 적용(파일별 override 가능).
3. 각 파일이 개별 시편/시험으로 적재된다.
4. `/materials/$id`에서 모든 시편 곡선이 오버레이로 표시되고, 물성 테이블에 시편별 행이 쌓인다. (평균±σ 통계는 Phase 3.)

---

## 3. 시스템 아키텍처

### 3.1 깨면 안 되는 템플릿 계약 (검증 완료)
- `backend/app/main.py`의 `app` 객체가 entrypoint. 모듈 경로/객체명 변경 불가 (`uvicorn app.main:app --root-path $ROOT_PATH`).
- `StaticFiles(html=True)`를 `/`에 **항상 마지막** 마운트. 모든 `/api/*` 라우트는 그 앞에 등록.
- `pyproject.toml`의 `include = ["app*"]` → 새 백엔드 코드는 전부 `app/` 하위.
- 프론트 fetch는 선행 슬래시 없는 상대경로(`fetch("api/...")`), Vite `base: "./"`.
- **런처/Caddy는 앱을 반드시 `/apps/<slug>/`(trailing slash)로 서빙**해야 한다(★C6). 슬래시 없으면 첫 로드 상대 fetch가 `/apps/api/...`로 깨짐(slug 증발, RFC 3986). 스모크 테스트에 슬래시 없는 진입 케이스 1개 포함(§9).
- 기존 인메모리 `/api/tasks` 스캐폴드(`_tasks`)는 `main.py` 교체 시 **삭제**한다.

### 3.2 라우팅 전략 — 단일 결정 (비판 [feasibility] A-1 충돌 수렴)
**결정: `base:"./"` 유지 + TanStack Router `createHashHistory()` (해시 라우팅).**
근거: 이 템플릿의 `StaticFiles(html=True)` 서빙 모델은 `/materials/42` 같은 deep-link를 index.html로 rewrite하지 않아(Starlette 실측), **빌드타임 슬러그 주입 없이 deep-link 404와 상대경로 깨짐을 동시에 회피하는 가장 단순한 방법**이 해시 라우팅이다(★C11 — "유일한 방법"은 과장이라 완화). 해시는 `document.baseURI`의 path를 동결하므로 라우트가 깊어져도 `fetch("api/...")`가 항상 앱 베이스로 풀린다(history면 `…/materials/api/…`로 깨짐 — 실측 확인).
**대가(★C11)**: SEO는 사내 도구라 무관. 분석 도구는 클라 라우터 이벤트로 수동 계측. URL에 `#` 노출은 수용. — ([ux]가 인용한 "hash가 형제앱 검증됨"은 사실이 아니므로 폐기.)

### 3.3 백엔드 디렉터리 트리 (Phase 1 — 얕은 분해)
모듈 과립도 과설계([overeng] D-14)를 피해, 파일이 기능보다 먼저 생기지 않게 얕게 시작한다.

```
backend/
├─ pyproject.toml
└─ app/
   ├─ __init__.py
   ├─ main.py                  # 얇은 create_app(): 라우터 include + StaticFiles 마운트만
   ├─ config.py                # pydantic-settings: DATABASE_URL, DATA_DIR, MAX_UPLOAD_MB
   ├─ db.py                    # engine/SessionLocal/Base/get_db + PRAGMA foreign_keys=ON 리스너
   ├─ models.py                # 5개 ORM 테이블 (커지면 models/ 패키지로 분리)
   ├─ schemas.py               # Pydantic v2 DTO
   ├─ units.py                 # SI 정규화/표시변환 단일 모듈 (★ 단위 책임 단일화)
   ├─ analysis.py              # 순수 계산 함수 모음 (E, Rp0.2, UTS, A%, n/K)
   ├─ ingest.py                # 업로드→파서→검증→DB적재→곡선저장 오케스트레이션
   ├─ curve_store.py           # Parquet I/O + LTTB 다운샘플
   ├─ routers/
   │   ├─ __init__.py          # api_router = APIRouter(); 하위 include
   │   ├─ health.py
   │   ├─ materials.py
   │   ├─ specimens.py
   │   ├─ uploads.py           # sniff / 업로드 / 수동매핑
   │   └─ properties.py
   └─ parsing/
       ├─ __init__.py
       ├─ base.py              # dataclass(ParseResult/ParsedSpecimen/ColumnSpec/ParseIssue) + ParserBase
       ├─ registry.py          # sniff 점수 디스패치
       ├─ column_map.py        # ColumnRole, resolve_columns()
       ├─ validate.py          # 물리 검증
       ├─ parsers/
       │   ├─ generic_csv.py
       │   └─ zwick_textxpert.py
       └─ config/column_aliases.yaml
```

`main.py` 최종 형태 (얇음, 계약 유지):
```python
def create_app() -> FastAPI:
    app = FastAPI(title="MaterialTwinWeb", version="0.1.0")
    init_db()                          # create_all()
    app.include_router(api_router)     # 모든 /api/* (StaticFiles보다 먼저!)
    dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")
    return app

app = create_app()                     # entrypoint 객체명/경로 불변
```

### 3.4 프론트엔드 디렉터리 트리 (Phase 1)
```
frontend/src/
├─ main.tsx                    # RouterProvider (hash history)
├─ router.tsx                  # createHashHistory + 라우트 정의
├─ api/
│   ├─ client.ts               # request<T>() 헬퍼 (상대경로 캡슐화)
│   ├─ uploads.ts              # uploadFiles(): FormData 전용 (Content-Type 미지정)
│   ├─ materials.ts
│   └─ curves.ts
├─ routes/
│   ├─ upload.tsx              # 4단계 마법사
│   ├─ materials.tsx           # 재료 목록
│   └─ material-detail.tsx     # 곡선뷰어 + 물성테이블
├─ components/
│   ├─ ui/                     # shadcn 복사본 (핵심 프리미티브만)
│   ├─ StressStrainChart.tsx   # ECharts core+line
│   ├─ PropertyTable.tsx       # tabular-nums
│   └─ EmptyState.tsx
└─ lib/units.ts                # 표시 단위 변환
```

### 3.5 데이터 저장 위치 (SIF 전략 준수)
- DB(SQLite 파일)와 곡선 Parquet은 **SIF 이미지 밖 쓰기가능 볼륨** `DATA_DIR`(env `MATERIALTWIN_DATA_DIR`, 미설정 시 `./var/data`)에 둔다.
- 파일 경로는 DB에 **상대경로만** 저장(절대경로 금지 — 배포 이동/SIF 패키징 대비).
- ⚠️ **`.portal/manifest.yaml`에 영속 볼륨 선언이 필요하다** — 현재 manifest엔 cpu/memory/gpu만 있고 볼륨이 없다. 미해결 시 재시작마다 데이터 소실 (§11 D1, §12 R1).

---

## 4. 데이터 모델

### 4.1 엔티티 관계 (Phase 1)
```
material 1──N specimen 1──N test 1──1 raw_curve_ref (Parquet 포인터)
                                  └──1 processed_result (산출 물성, 파라미터 JSON)
```
- `specimen↔test`는 **스키마 1:N, UI 기본 1:1** (재시험 대비, 비용 거의 없음. [domain] 결정 #1 확정).
- 곡선은 **test가 소유** (`raw_curve_ref.test_id`). UI에서 specimen→대표 test 선택(1:1이면 자동).

### 4.2 명명 정본 (비판 [gaps] A1 수렴)
테이블/엔티티 명을 [datamodel] 기준으로 통일한다. 5개 설계안의 다른 명칭은 아래로 매핑.

| 정본 테이블 | [domain] 엔티티 | [arch] 파일 |
|---|---|---|
| `test` | TestRun | test.py |
| `processed_result` | DerivedProperties | processed_result.py |
| `raw_curve_ref` | RawCurve | raw_curve_ref.py |
| `processed_result.params`(JSON) | ProcessingConfig | — |

### 4.3 스키마 (Phase 1, SI 단위 + 컬럼 접미사)
전 컬럼 SI 저장: force=N, length=m, area=m², stress=Pa, strain=무차원(접미사 없음), temp=K, time=s.

**`material`**

| 컬럼 | 타입 | 제약 | 단위/설명 |
|---|---|---|---|
| id | Integer | PK | |
| name | String(200) | NOT NULL | "AL6061-T6" |
| material_code | String(100) | UNIQUE, nullable | 검색 대상 → 정규 컬럼 |
| category | String(50) | nullable | metal/polymer/composite |
| description | Text | nullable | |
| attributes | JSON | default {} | 자유 메타 (검색 금지) |
| created_at / updated_at | DateTime(tz) | NOT NULL, func.now() | UTC aware 강제 |

**`specimen`**

| 컬럼 | 타입 | 제약 | 단위 |
|---|---|---|---|
| id | Integer | PK | |
| material_id | Integer | FK→material, NOT NULL, ON DELETE CASCADE | |
| label | String(100) | NOT NULL | |
| geometry_type | String(20) | NOT NULL, CHECK in('flat','round') | |
| gauge_length_m | Float | NOT NULL, >0 | L0, m |
| width_m / thickness_m | Float | nullable, >0 | flat: w0/t0, m |
| diameter_m | Float | nullable, >0 | round: d0, m |
| area0_m2 | Float | NOT NULL, >0 | A0 (입력 시 확정, 불일치 reject) |
| orientation | String(20) | nullable | RD/TD/45 |
| standard | String(30) | nullable | ASTM E8M / ISO 6892-1 |

CHECK: `(geometry_type='flat' AND width_m IS NOT NULL AND thickness_m IS NOT NULL) OR (geometry_type='round' AND diameter_m IS NOT NULL)`.

**`test`**

| 컬럼 | 타입 | 제약 | 단위 |
|---|---|---|---|
| id | Integer | PK | |
| specimen_id | Integer | FK→specimen, NOT NULL, CASCADE | |
| test_type | String(30) | NOT NULL, default 'tensile' | |
| machine / software | String(100) | nullable | "Zwick Z050" / "testXpert III" |
| source_format | String(20) | nullable | 파서 키 (감사용, upload_file 대체) |
| strain_source | String(20) | NOT NULL, CHECK in('extensometer','crosshead') | |
| test_speed_m_s | Float | nullable | m/s |
| temperature_k | Float | nullable | K |
| tested_at | DateTime(tz) | nullable | UTC 정규화 |
| valid | Boolean | NOT NULL, default true | 이상치 배제 |
| invalid_reason | String(200) | nullable | |

**`raw_curve_ref`** (1:1 with test)

| 컬럼 | 타입 | 제약 | 설명 |
|---|---|---|---|
| id | Integer | PK | |
| test_id | Integer | FK→test, UNIQUE, NOT NULL, CASCADE | |
| storage | String(20) | NOT NULL, default 'parquet_fs' | parquet_fs / inline_json(폴백) |
| file_path | String(500) | nullable | DATA_DIR 상대경로 |
| n_points | Integer | NOT NULL | |
| channels | JSON | NOT NULL | `[{name,unit_si}]` |
| inline_data | JSON | nullable | storage='inline_json'일 때 |

**`processed_result`** (1:1 with test)

| 컬럼 | 타입 | 단위 |
|---|---|---|
| id | Integer PK | |
| test_id | Integer FK→test, UNIQUE, NOT NULL, CASCADE | |
| youngs_modulus_pa | Float, nullable | Pa |
| yield_strength_pa | Float, nullable | Pa (0.2% offset) |
| uts_pa | Float, nullable | Pa |
| uniform_elongation | Float, nullable | 무차원 |
| fracture_elongation | Float, nullable | 무차원 |
| reduction_of_area | Float, nullable | 무차원 |
| strain_hardening_n | Float, nullable | n |
| strength_coeff_k_pa | Float, nullable | Pa |
| params | JSON, NOT NULL | E구간[ε_lo,ε_hi], offset, toe, R², 사용점수 (★ 추적성) |
| extra_metrics | JSON, nullable | 진응력 등 확장 슬롯 |
| computed_at | DateTime(tz) | |

> **재계산 = 덮어쓰기**. 분석 이력 버저닝(`analysis_run`)은 Phase 3로 미룸([overeng] A1). 연신율/단면감소율은 **무차원 저장**, % 변환은 표시 레이어([gaps] B2).

### 4.4 곡선 저장 방식 결정
**파일시스템 + Parquet(zstd) + DB는 경로/메타만.** (3개 설계안 합의)

| 후보 | 채택 | 근거 |
|---|---|---|
| DB BLOB | ✗ | 수만 점×다채널 → SQLite 비대, 컬럼 연산 불가 |
| 점당 1행 테이블 | ✗ | 수천만 행, 인덱스/조인 폭발 |
| **Parquet 파일 + DB 포인터** | **✓** | 곡선은 "한 덩어리로 읽고 분석"하는 컬럼 데이터. pandas/numpy 직결, zstd 5~10× 압축, DB 슬림 → SQLite→Postgres 이행 가벼움 |

- 경로(★C4): `DATA_DIR/curves/{test_id}.parquet`(샤딩 시 `curves/{test_id//1000}/{test_id}.parquet`). **불변 키 test_id만 사용**(§4.1 "곡선은 test가 소유"와 일치). material_id는 가변 외래관계라 경로에서 제거 → 시편 이동 = DB UPDATE 1건, 파일 손 안 댐. 컬럼 = time, force_N, disp_m, extenso_strain, eng_stress_Pa, eng_strain.
- 쓰기 프로토콜(★C4): `{test_id}.parquet.tmp.{uuid}` 쓰기 → fsync → **atomic rename** → 마지막에 짧게 INSERT+커밋. 크래시(restart_policy on_failure) 시 `.tmp.*`는 항상 고아로 식별 가능. `finally` 정리는 크래시엔 안 돌므로 정리 책임을 **부팅 reaper**로 이관.
- **부팅 정합성 스윕(reaper, ★C4)**: `init_db()` 직후 `curves/` 스캔 — DB 포인터 없는 `.parquet`/`.tmp.*`는 삭제(또는 quarantine), 파일 없는 DB 포인터는 `raw_curve_ref.storage='missing'` 마킹(침묵 500 방지).
- 삭제는 DB 먼저, 파일은 앱 레이어에서 명시 삭제(FK CASCADE가 파일은 못 지움 — [feasibility] B-1).
- inline_json은 100점 미만 소형/픽스처 폴백.

### 4.5 SQLite→Postgres 호환 핵심 규칙
- **PRAGMA foreign_keys=ON** 연결마다 강제(`event.listens_for(Engine,"connect")`). 빠지면 CASCADE 침묵 실패 → 환경별 삭제 비결정성([feasibility] B-1). **양 DB CASCADE 테스트 작성.**
- **동시성 PRAGMA(연결마다, ★C2 치명)**: `PRAGMA journal_mode=WAL` + `PRAGMA busy_timeout=5000`(또는 SQLAlchemy `connect_args={"timeout": 5}`). 런처가 단일 워커로 기동(`--workers` 없음)하므로 위협은 프로세스 간 락이 아니라 **단일 프로세스 내 동시 업로드**(§2.2 워크플로우 B)다. 기본 `journal_mode=DELETE`+`busy_timeout=0`이면 즉시 `SQLITE_BUSY`→500. WAL로 읽기-쓰기 동시성 확보(업로드 중 GET curve 안 막힘), busy_timeout으로 짧은 경합을 500 대신 대기로 흡수.
- **Parquet 쓰기(느린 I/O)는 DB 트랜잭션 밖**에서 끝낸 뒤 마지막에 짧게 INSERT+커밋(라이터 점유 최소화, §4.4 쓰기 프로토콜과 일치).
- **WAL은 로컬 블록 스토리지 가정** — DATA_DIR이 NFS면 `-wal/-shm` 사이드카가 깨짐(§11 D1에서 볼륨 종류 확인 필수). 멀티워커 도입 시 단일 워커 전제 재검토.
- **JSON 컬럼에 WHERE/ORDER BY 금지.** 검색·정렬 후보 키(material_code, 대표 UTS/E)는 정규 컬럼으로 승격([feasibility] B-2).
- DateTime은 **입력 경계에서 UTC aware 강제**, `func.now()` server_default([feasibility] B-3).
- plain `JSON` 컬럼 사용. `with_variant(JSONB)`·Postgres 호환층은 전환 시점으로 미룸([overeng] D-13).

---

## 5. 파서 서브시스템 설계

### 5.1 5단계 파이프라인 + 어댑터 플러그인
```
bytes → [1.detect] → [2.decode] → [3.structure] → [4.map] → [5.validate] → ParseResult
         (sniff)      (encoding)    (header/table)  (columns)  (physics)
```
파서별 구현은 1~3단계만 다르고, 4·5단계(매핑·검증)는 전 파서 공유. 미지 형식 폴백 시 어느 단계가 깨졌는지 경계로 자명해진다.

### 5.2 핵심 결정 (유지)
- **`parse()`는 예외를 던지지 않는다.** 모든 실패를 `ParseIssue(level=ERROR)`로 수집해 graceful 반환 → 다중 파일 업로드 UX 보호. API는 ParseResult를 200+이슈목록(422 의미)으로 변환.
- **미지 형식**: sniff 최고점 < 0.3 → GenericCsvParser best-effort → `needs_manual_mapping=True` + `raw_preview`(앞 50줄) 반환 → 프론트 수동 매핑 UI.
- **재파싱은 4·5단계만** 재실행(RawTable 캐시). Phase 1은 수동 매핑 재파싱(`POST api/uploads/{id}/mapping`)만.

### 5.3 쯔윅 함정 대응 (구현 체크리스트)
- [ ] **독일식 소수점 콤마**: delimiter(`;`/`\t`/`,`)와 decimal_sep(`.`/`,`)을 **동시** 추정(한 표본 블록으로). `;` 보이면 소수는 `,` 확률 높음.
- [ ] **인코딩**: BOM 우선 → charset-normalizer → latin-1/cp1252 폴백. 움라우트(`ä/ö/ü`)·`mm²`·`°` 깨짐을 인코딩 오판 신호로.
- [ ] **`Standardweg`(crosshead) ≠ `Verlängerung`(신율계)** 구분 → ColumnRole DISPLACEMENT vs EXTENSION. 영률 정확도 직결.
- [ ] **FORCE 단위 N/kN 자동변환 금지** → 추정은 INFO 이슈로 노출, 사용자 확인(10배 오류 방지).
- [ ] **STRAIN % vs 무차원** 모호성 → 값 범위로 추정, INFO 노출.
- [ ] 다중 시편 (수평 접미 / 수직 블록 / 파일분리) 3패턴 분기 → `parse()`는 `specimens: list` 반환.
- [ ] 별칭은 코드가 아닌 `column_aliases.yaml` 외부화(새 헤더 무배포 흡수).

### 5.4 ColumnRole → strain_source 매핑 ([gaps] B3 보완)
ingest에서: EXTENSION 또는 STRAIN 존재 → `strain_source='extensometer'` 우선, DISPLACEMENT만 → `'crosshead'`.

### 5.5 단위 책임 경계 ([gaps] B1, [feasibility] C-2 수렴)
**파서는 원본 단위 그대로(mm/kN) + 단위 메타만 반환(자동변환 금지 원칙 존중). SI 정규화(→m/N/Pa)는 `app/units.py` 단일 모듈이 ingest 시 1회 수행.** 파서의 `inferred_unit`/`channels[].unit_si`가 이 모듈 입력으로 연결된다.

### 5.6 zse/zsx 바이너리 — Phase 1은 0단계만
`sniff()`로 인식만, `parse()`는 `ERROR(code="zwick_binary_unsupported", hint="testXpert에서 CSV/TXT로 export 후 업로드")` 반환. 역공학은 샘플 확보 후 후순위([overeng] A5).

### 5.7 샘플 필요 지점 (§11 D2와 연동)
| 지점 | 미확정 사항 | 필요 샘플 |
|---|---|---|
| 텍스트 export 레이아웃 | 메타블록 형식, 단위행 위치, delimiter 기본값 | testXpert TXT/CSV 2~3개 |
| 다중 시편 패턴 | 수평/수직/파일분리 | 시편 ≥3개 묶음 1개 |
| 헤더 별칭 실측 | 정확한 컬럼명 문자열 | 위 샘플 헤더행 |
| zse/zsx 내부 구조 | ZIP/XML/binary | 각 포맷 실물 1개 (최우선) |

> **안전한 진행법**: 인터페이스(dataclass)·파이프라인 경계·`parse()=graceful`은 샘플 무관하게 **지금 동결·구현**. structure 휴리스틱(단위행 탐지 등)은 스텁+TODO로 두고 **합성 픽스처 단위테스트**(독일식 소수점/`;`/움라우트/단위행)로 회귀 안전망 확보. "완성" 마킹 금지([feasibility] C-1).

---

## 6. 물성 계산 명세

전제: `σ_nom[i]=force[i]/A0`, `ε_nom[i]=extenso_strain[i]`(신율계) 또는 `disp[i]/L0`(crosshead). `analysis.py`는 순수 함수(numpy만, **scipy 불필요**).

### 6.1 Phase 1 알고리즘 (수치 함정 — [feasibility] D, ★C13 단일 수치는 "전형적 예시값")

> ★C13: 아래 ±수치는 적대적 합성측정으로 방향·자릿수는 확인됐으나 toe 크기·노이즈·항복무릎 형상에 의존하는 **예시값**이다(단일 실측 아님). **결론(원점강제 금지·toe보정 ON 등)은 전부 유지**한다.

**영률 E** (예시: 정상구간 산포 ~3%, toe/항복 침범 시 최대 ±10%; 원점강제 시 toe 절편 존재하면 수~수십% 저평가):
1. **Toe(발끝) 보정 기본 ON**: 선형구간 직선을 ε축 외삽 → 절편 ε0 제거 → 원점 이동 (ASTM E8).
2. 구간 선택: Phase 1은 **고정 변형률 구간(예: 0.0005~0.0025) + UI brush 수동조정**. auto 슬라이딩윈도우는 Phase 4로 미룸([overeng] B8).
3. **반드시 절편 포함 회귀**(`polyfit deg=1`), 원점 강제 절대 금지.
4. **R²는 거부 트리거가 아니라 신뢰도 등급(★C1 치명)**: ≥0.999 → `confidence='high'`, ≥0.99 → `'ok'`, <0.99 → `'low'`. **값은 항상 반환**하되 `processed_result.params.confidence`에 등급을 동봉하고, `'low'`는 UI 경고 배지로 노출(**거부하지 않음** — 노이즈 실데이터·폴리머에서 사용자가 물성을 영영 못 받는 결함 방지). ※ "구간 점수 ≥5"는 정의 없는 마법숫자라 **삭제**.
   - 4a. **폴리머 분기(★C1)**: `category='polymer'`는 명확한 선형구간이 없어 E를 **secant modulus**(예: 0.05~0.25% 할선) 또는 1% offset으로 분기 산출.
5. 사용구간·R²·confidence 등급을 `processed_result.params`에 **항상 반환**(추적성).
6. crosshead 소스 → 머신 컴플라이언스로 저평가 → **신뢰도 낮음 플래그**(보정은 Phase 2).

**0.2% offset 항복 Rp0.2** ([feasibility] D-3: E오차 ±10%→Rp0.2 ±4MPa):
1. Offset 직선 `σ=E·(ε−0.002)`.
2. 곡선과 첫 교점(부호변화 +→−, 이후 N점 연속 음수=안정 교점) → 선형보간으로 정확 교점.
3. 교점 없음(취성) → null + 플래그. E 신뢰도와 연동 경고.
4. 명확한 항복점(mild steel) → ReH/ReL 별도 산출 병기.

**UTS(Rm)**: 평활 후 max(σ_nom), 끝단 노이즈는 마지막 5% 제외 옵션, 파단 급강하와 구분.

**연신율·단면감소율**:
| 물성 | 정의 | 비고 |
|---|---|---|
| Ag/Agt(균일) | Rm 시점 변형률 | crosshead면 부정확 플래그 |
| A(파단) | (Lf−L0)/L0 또는 파단점 ε | 파단 자동검출(force −90% 급락)은 WARNING으로 사용자 확인 |
| Z(단면감소) | (A0−Af)/A0 | Af 미입력 시 null |

**Hollomon n, K**: log-log 선형회귀(numpy). scipy 불요.

**평활**: savgol는 계산 전 적용하되 **원본 보존**(다운샘플/평활은 표시·탐색용, 산출은 params로 추적).

### 6.2 Phase 2 개요 — 진응력 변환
`ε_true=ln(1+ε_nom)`, `σ_true=σ_nom·(1+ε_nom)` (넥킹 전 유효). Considère 넥킹 개시 `dσ_true/dε_true=σ_true`. Bridgman 보정은 R/a 측정 필요 → 기초는 균일구간까지만([domain] 결정 #4). `extra_metrics` JSON 슬롯에 저장(스키마 변경 0).

### 6.3 Phase 3 개요 — 구성방정식 피팅
소성변형률 `ε_pl=ε_true−σ_true/E`. 비선형 최소제곱(scipy `curve_fit`) → `constitutive_fit` 저장 → FE 카드 생성.

| 모델 | 수식 | 비고 |
|---|---|---|
| Hollomon | σ=K·εpⁿ | |
| Swift | σ=K·(ε0+εp)ⁿ | 금속 성형 표준 |
| Voce | σ=A−(A−σ0)·exp(−B·εp) | 포화형 |
| Johnson-Cook | σ=(A+B·εpⁿ)(1+C·ln ε̇*)(1−T*ᵐ) | 다변형률·다온도 → 재료 단위 피팅 |

FE 카드: LS-DYNA `*MAT_024`(piecewise) 우선, JC는 `*MAT_098`([domain] 결정 #5 — Phase 3 착수 전 확정 필요).

### 6.4 표준 용어 정합
DB 내부는 ISO 기호(Rp0.2, Rm, A, Z, So/L0)를 정규명으로, ASTM명은 alias. UI 토글로 전환.

| 개념 | ASTM E8 | ISO 6892-1 | DB 필드 |
|---|---|---|---|
| 영률 | E | E | youngs_modulus_pa |
| 0.2% offset | YS | Rp0.2 | yield_strength_pa |
| 인장강도 | UTS | Rm | uts_pa |
| 파단연신율 | A | A | fracture_elongation |
| 단면감소율 | RA | Z | reduction_of_area |
| 변형경화지수 | n (E646) | n | strain_hardening_n |

---

## 7. API 엔드포인트 목록 (Phase 1)

전부 `/api/` 접두사, `api_router`로 묶여 StaticFiles 앞 include. 업로드 플로우는 [gaps] A4 수렴: 마법사가 "시편 생성 → 그 sid로 업로드" 2-step을 프론트가 오케스트레이션.

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/health` | 헬스체크 |
| GET | `/api/materials?q&page&size` | 재료 목록(요약 포함) |
| POST | `/api/materials` | 재료 생성 |
| GET | `/api/materials/{mid}` | 재료 상세 |
| PATCH | `/api/materials/{mid}` | 재료 수정 |
| DELETE | `/api/materials/{mid}` | 삭제(cascade) |
| GET | `/api/materials/{mid}/specimens` | 시편 목록 |
| POST | `/api/materials/{mid}/specimens` | 시편 생성 |
| GET/PATCH/DELETE | `/api/specimens/{sid}` | 시편 상세/수정/삭제 |
| POST | `/api/uploads/sniff` | 파서 후보·신뢰도 (multipart, 미커밋) |
| GET | `/api/parsers` | 등록 파서 목록(hint UI) |
| POST | `/api/specimens/{sid}/uploads` | 원본 업로드→파싱→적재 (multipart) |
| POST | `/api/uploads/{id}/mapping` | 수동 매핑 재파싱(4·5단계만) |
| GET | `/api/specimens/{sid}/tests` | 시편의 시험 목록 |
| GET | `/api/tests/{tid}` | 시험 상세(파서 진단 포함) |
| PATCH | `/api/tests/{tid}` | valid/invalid_reason 토글 ([gaps] C2) |
| DELETE | `/api/tests/{tid}` | 삭제(곡선·raw 동반 정리) |
| GET | `/api/tests/{tid}/curve?kind=nominal&max_points` | 곡선 포인트(LTTB 다운샘플) — **곡선 소유자는 test** ([gaps] A3) |
| GET | `/api/tests/{tid}/curve.csv` | 곡선 CSV 다운로드 |
| POST | `/api/tests/{tid}/properties:compute` | 기본 물성 계산(동기) — 회귀구간/offset 옵션 |
| GET | `/api/tests/{tid}/properties` | 계산된 물성 조회 |

> 모든 계산은 **동기**(numpy 수십 ms). 백그라운드 잡 시스템(`jobs` 테이블/폴링)은 피팅·통계 도입 시 Phase 3에서 추가([overeng] B6). `analysis-runs`/`fits`/`card`/`aggregate` 엔드포인트는 Phase 3.

---

## 8. 프론트엔드 / UX 설계

### 8.1 화면 (Phase 1: 3개)
| route(#) | 화면 | 핵심 컴포넌트 |
|---|---|---|
| `/upload` | 4단계 마법사 | Dropzone, ParserDetectBadge, ColumnMapper, SpecimenMetaForm, RawPreviewChart |
| `/materials` | 재료 라이브러리 | MaterialFilterBar, MaterialCard, DataTable |
| `/materials/$id` | 곡선 뷰어 + 물성 | StressStrainChart, PropertyTable, RegressionRangePicker, SpecimenLegendPanel |

미룸(Phase 3+): `/compare`, `/dashboard` 히스토그램, `/export`(피팅), `/settings`.

### 8.2 업로드 4단계 마법사
`[1 Drop] → [2 Detect & Map] → [3 Specimen Meta] → [4 Preview & Commit]`. 미리보기 전까지 미커밋(클라 파싱 우선). 형상 라디오에 따라 동적 필드(평판 w0·t0·L0 / 봉상 d0·L0). 진행상태는 useState/hook(Phase 1은 Zustand 불요 — [overeng] C10).

### 8.3 곡선 시각화 — ECharts
**ECharts(`echarts/core` + LineChart + Grid/Tooltip/DataZoom/MarkLine/MarkPoint/BrushComponent만 import).** Canvas `large` 모드로 수만 점, `markPoint`(UTS/Rp0.2), `markLine`(회귀선), `brush`(영률 구간 선택) 내장. recharts(SVG 폭발)·plotly(번들 3MB) 탈락.

- **시그니처 인터랙션**: brush로 [ε1,ε2] 선택 → **클라 실시간 선형회귀 미리보기**(E·R²) → 확정 시 `POST api/tests/{tid}/properties:compute`로 서버 재계산·영속. **저장되는 건 서버 확정값만, 클라는 프리뷰**([gaps] E1).
- **다운샘플**: 서버 LTTB ~2000점(물성 산출은 풀해상도). **markPoint(UTS/Rp0.2)는 풀해상도 인덱스로 서버가 계산해 좌표 동봉** — 다운샘플 배열에서 argmax 금지([feasibility] D-5).

### 8.4 디자인 시스템
- **shadcn/ui(Radix+Tailwind+CVA)** 소스 복사 — 토큰 완전 장악.
- 색: 엔지니어링 계측 톤(calibration blue primary, signal green accent, 색맹 안전 chart 팔레트), 다크 기본.
- 타이포: UI=Inter, **수치/카드=monospace + `tabular-nums`**(Phase 1은 시스템 mono로 시작, jetbrains-mono는 미룸 — [overeng] C10).
- 폰트 self-host(@fontsource/inter) — CDN 의존 금지(SIF 오프라인).

### 8.5 상태관리 / 데이터패칭
| 영역 | 도구 |
|---|---|
| 서버 상태 | TanStack Query (`queryFn`은 상대경로 `fetch("api/...")`) |
| 클라 UI 상태 | useState/hook (Phase 1) — Zustand는 비교트레이 생기는 Phase 3 |
| 폼 | react-hook-form + zod |
| 토스트 | Sonner |
| 라우팅 | TanStack Router (createHashHistory) |

### 8.6 상대경로/다운로드 준수
- 모든 fetch·다운로드 href는 **선행 슬래시 없는 상대경로**. 동적 경로 동일.
- **업로드는 별도 `uploadFiles` 헬퍼**(FormData를 body로, Content-Type 미지정 → 브라우저가 boundary 자동 설정). 기존 `request()`의 `application/json` 강제와 분리.
- 다운로드: `fetch(상대경로)→blob()→objectURL→임시 <a download>` + `URL.revokeObjectURL`. 백엔드는 `Content-Disposition: attachment; filename=...` + 비ASCII는 `filename*=UTF-8''<percent-encoded>`(RFC 5987) 동반([feasibility] A-2).
- `vite.config.ts`에 `manualChunks`로 echarts 별도 청크 분리. `base:"./"` 절대 불변. 빌드 후 `dist/index.html` 청크 상대경로(`./assets/...`)를 서브경로 마운트로 스모크 테스트([feasibility] A-3).

---

## 9. 단계별 로드맵

| Phase | 산출물 | 완료기준 |
|---|---|---|
| **P1: 기초 인장 MVP** | material/specimen/test/raw_curve_ref/processed_result 5테이블, GenericCsv+ZwickText(wrapper) 파서, E/Rp0.2/UTS/A% 계산, /upload(+IssuePanel)·/materials·/materials/$id 3화면, ECharts 곡선뷰어+brush 회귀, **σ-ε 골든 픽스처 1개**(선형+멱법칙) | **(★C3 검증 가능한 게이트로 강화)** ① [정확도] 골든 픽스처 업로드 → 반환 E ±2%, Rp0.2 ±2MPa, UTS ±0.5%(pytest assert). ② [brush] 구간 POST = numpy polyfit 직접계산 일치, low-confidence는 **거부 아니라 플래그**(★C1). ③ [graceful] 깨진 인코딩/콤마소수점/움라우트 픽스처 → parse() 예외 0건+ParseIssue 수집(★C5). ④ [서브경로] 빌드 자산 전부 `./assets/`(절대경로 grep 0), `/apps/test-slug/` deep-link 새로고침 200 + **슬래시 없는 진입 케이스 1개**(★C6). ⑤ [CASCADE] 양 DB FK CASCADE 통과. ⑥ [reaper] 부팅 스윕이 고아 `.parquet/.tmp` 삭제(★C4). |
| **P2: 진응력 + 측정 신뢰도** | true_stress 변환(`kind=true` 곡선), Considère 넥킹점, crosshead 컴플라이언스 보정 슬롯, auto E구간선택, 실 testXpert 샘플로 ZwickText 휴리스틱 확정 | 공칭↔진 토글 동작, 넥킹점 마커, 실샘플 파싱 통과 |
| **P3: 통계 + 피팅 + 카드** | analysis_run/aggregate_result/constitutive_fit/jobs 테이블, 대표곡선±σ, Swift/Voce/JC 피팅(scipy), LS-DYNA 카드 export, /compare·/dashboard·/export 화면, 백그라운드 잡 | 다시편 통계밴드, 피팅 R²/잔차, 카드 다운로드, 잡 폴링 |
| **P4: 운영화** | Alembic 도입, Postgres 전환 옵션(psycopg+JSONB variant), zse/zsx 바이너리 파서, 별칭 학습루프, 인증 슬롯 | Postgres 마이그레이션 무손실, 바이너리 파싱 |

---

## 10. 의존성 목록

### 백엔드 (Phase 1)
```toml
"fastapi>=0.110", "uvicorn[standard]>=0.27",   # 기존
"python-multipart>=0.0.9",     # 멀티파트 업로드
"pydantic-settings>=2.2",      # config env
"sqlalchemy>=2.0",             # ORM (SQLite↔PG 추상화)
"numpy>=1.26",                 # 곡선 벡터 연산
"pandas>=2.2",                 # Parquet I/O
"pyarrow>=15",                 # Parquet(zstd) 엔진
"charset-normalizer>=3",       # 인코딩 감지 ([gaps] E2)
"pyyaml>=6",                   # column_aliases.yaml ([gaps] E2)
```
**Phase 3+**: scipy(피팅), alembic(마이그레이션), psycopg[binary](Postgres), kaitai-struct(바이너리). manylinux 휠 제공 → SIF 컴파일 불필요. lockfile/해시 고정 권장.

> **실제 구현 환경(★정정)**: 로컬·테스트 인터프리터는 **Python 3.10**(의존성 설치 위치)이라 `pyproject.toml requires-python`을 `>=3.10`으로 맞춤(기존 계획의 ">=3.12"는 추정이었음). SIF 빌드가 3.12를 쓰면 다시 올린다. 위 의존성은 numpy/pandas/pyarrow/sqlalchemy/pydantic v2/pydantic-settings/python-multipart/charset-normalizer/pyyaml로 Phase 1에 실제 사용됨, pytest는 dev extra.

### 프론트엔드 (Phase 1)
```
@tanstack/react-router (hash), @tanstack/react-query,
echarts + echarts-for-react (core+line만 import),
tailwindcss + autoprefixer + postcss (dev),
tailwind-merge, clsx, class-variance-authority,
@radix-ui/react-* (dialog,dropdown,popover,tabs,tooltip,select,radio-group,switch,separator,scroll-area,slot,label),
lucide-react, react-hook-form + @hookform/resolvers + zod,
react-dropzone, sonner, @fontsource/inter
```
**미룸**: framer-motion, zustand, cmdk, @fontsource/jetbrains-mono. `.npmrc`(shamefully-hoist) 변경 불필요. `manualChunks`로 echarts 청크 분리.

---

## 11. 열린 질문 / 결정 필요 항목

| # | 항목 | 권장/상태 | 누가 |
|---|---|---|---|
| **D1** | **영속 볼륨(DATA_DIR)** — manifest.yaml에 SIF 밖 쓰기가능 볼륨 선언 필요. 미해결 시 재시작마다 데이터 소실. **곡선 Parquet 전략 전체가 여기 의존** | HEAXHub 런처 영속 마운트 지원 확인 후 manifest 수정. **최우선** | 사람 |
| **D2** | **testXpert 샘플 2~3개** — 텍스트 export 레이아웃·다중시편 패턴·헤더 별칭·zse/zsx 내부구조 전부 막힘 | 코딩 착수 전 확보. 없으면 GenericCsv+수동매핑으로 MVP 진행 | 사람 |
| D3 | crosshead 컴플라이언스 보정 시점 | Phase 2 (P1은 신뢰도 플래그만) | 확정 |
| D4 | Bridgman 넥킹 후 보정 범위 | 기초는 균일구간까지 (R/a 측정 시 확장) | 확정 |
| D5 | FE 카드 타깃 MAT | LS-DYNA *MAT_024 우선, JC *MAT_098 (Phase 3 착수 전) | 결정 필요 |
| D6 | material.current_run_id(대표값 포인터) | Phase 3에서 명시 컬럼 추가 권장 | Phase 3 |
| D7 | upload_batch(1파일→N시편 묶음) | 파서가 specimens:list 반환 → Phase 3에서 배치 테이블 | Phase 3 |

> D1·D2가 미해결이어도 P1 착수는 가능하다: D1은 개발용 `./var/data` 기본값으로, D2는 합성 픽스처+GenericCsv로 진행. 단 **운영 배포 전 D1 필수**, **ZwickText 휴리스틱 확정 전 D2 필수**.

---

## 12. 리스크와 완화책

| 등급 | 리스크 | 완화책 |
|---|---|---|
| 치명 | **R²<0.99 하드거부**(폐기됨) → 노이즈·폴리머에서 사용자가 물성 영영 못 받음(제품 파괴) | ★C1 거부 폐기 → confidence 등급(high/ok/low)으로 강등, 값 항상 반환, 폴리머 secant 분기. §6.1·§9 반영 |
| 치명 | **영속 볼륨 미선언**(★C7) → 재시작 데이터 소실, Parquet 전략 무효화. 런처가 추가 바인드 미지원(`cleanenv=True`, MATERIALTWIN_DATA_DIR 미주입 확인) | **플랫폼(런처) 선결 과제**(D1). config는 `./var/data` 폴백+기동 WARNING. 미해결 시 곡선 한시적 DB BLOB 폴백 경로 확보 |
| 치명 | **SQLite 동시성 SQLITE_BUSY→500**(★C2) — 단일 워커 내 동시 업로드(워크플로우 B) | PRAGMA journal_mode=WAL + busy_timeout=5000, Parquet 쓰기는 트랜잭션 밖, 단일 워커 전제 명문화 |
| 치명 | **라우팅 전략** + StaticFiles는 deep-link rewrite 안 함(실측) | `base:"./"` + TanStack `createHashHistory()` 단일 확정(§3.2). ★C6: 런처는 `/apps/slug/`(trailing slash) 서빙 필수(슬래시 없으면 첫 fetch가 `/apps/api/...`로 깨짐, RFC 3986) |
| 치명 | **SQLite FK CASCADE 침묵 실패** → 환경별 삭제 비결정성, 고아 Parquet | PRAGMA foreign_keys=ON 강제 + 양 DB CASCADE 테스트 + 파일은 앱레이어 삭제 + 부팅 reaper(★C4) |
| 높음 | **graceful이 오매핑을 성공으로 분류**(★C5) → 쓰레기 값이 물성으로 표시 | parse 성공≠계산 허가. confidence 낮거나 미해결 INFO면 processed_result 안 만들고 "확인 필요" 상태. validate에 오매핑 가드(단조성·채널상관·자릿수) |
| 높음 | **곡선 경로에 가변 material_id**(★C4) → 시편 이동 시 404·고아 | 경로는 불변 test_id만, atomic rename, 부팅 reaper |
| 높음 | **JSON 컬럼 검색** → SQLite/PG 쿼리 분기 | 검색·정렬 키 정규 컬럼 승격, JSON에 WHERE/ORDER BY 금지. params는 Pydantic+schema_version(★C10) |
| 높음 | **파서 휴리스틱 재작업** — 첫 실데이터에서 거의 확실 | 인터페이스·파이프라인·graceful만 동결, ZwickText는 GenericCsv+독일 별칭 wrapper로 축소(★C12), 다중시편 분기는 P1 제거(파일분리만), MVP=GenericCsv+수동매핑 |
| 높음 | **영률 변동** — 구간 ~3%(toe/항복 침범 시 ±10%), 원점강제 시 수~수십% 저평가(★C13 예시값) | toe보정 기본 ON, 절편포함 회귀, **R² confidence 등급(거부 아님)**, 폴리머 secant 분기, brush 수동조정, 사용구간·R² 항상 반환 |
| 중 | **0.2% offset이 E오차 추종**(offset 교점 곡선 기울기에 반비례, ★C13) | E신뢰도 연동 경고, 첫 안정 교점 규칙, 평활은 표시용·원본보존 |
| 중 | **단위 경계**(파서 mm/kN ↔ DB m/N/Pa) | units.py 단일 모듈이 ingest 시 1회 정규화, 파서는 원본+메타만 |
| 중 | **tz naive/aware 혼용**(SQLite 통과, PG 에러) | 입력 경계 UTC aware 강제, func.now() |
| 중 | **다운로드 비ASCII 파일명, LTTB가 마커 죽임** | filename*=UTF-8'', 마커는 풀해상도 인덱스로 계산 후 오버레이 |
| 낮음 | **SIF 용량**(pyarrow/pandas +200MB) | manylinux 휠 컴파일 불필요. scipy는 Phase 3 optional extra로 분리 |

---

**핵심 단일 메시지**: P1은 5테이블·동기계산·2파서·3화면으로 얇게 시작하고, 확장은 JSON 슬롯과 list 시그니처로만 예약한다. 착수 전 **라우팅 1개 확정(완료: hash)**, **영속 볼륨(D1)**·**testXpert 샘플(D2)** 두 항목만 사람이 풀면 된다.

---

## 13. 적대적 보증(Adversarial Hardening)

### 13.1 검증 방법
본 계획서의 §1~§12는 9개 에이전트(~463k 토큰)의 설계·교차비판 산물이며, 그 자체로는 **실측이 아니라 LLM 추론 산출물**이다(`.koo-llm-sessions/`에 측정 로그·픽스처 부재). 이 한계를 보정하기 위해, 표적 주장 5묶음(영률·라우팅·저장·파서·범위)에 대해 **"반박-기본값(refute-by-default)" 적대적 공격**을 가했다. 공격자는 합성 인장곡선을 직접 생성해 수치를 재측정하고(`scratchpad/verify.py`), Starlette 0.50.0 실소스(`staticfiles.py:109-149`)·`new URL(rel,base)` RFC 3986 동작·HEAXHub 런처 실코드(`integration_launcher.py:430-601`, `stacks.yaml:82`)를 직접 실행/열람해 "동작이 코드에 실제로 존재하는가"를 확인했다. 그 위에 **중립 심판(neutral referee)**이 각 공격을 재심해 정당/부분정당/과함으로 분류하고, "실측" 라벨이 붙었으나 출처가 텍스트뿐인 단일 숫자는 "전형적 예시값"으로 강등했다. 본 절은 그 재심 결과를 §1~§12에 반영하기 위한 확정 보강이다.

### 13.2 표적 주장 verdict 종합

| 표적 주장(원위치) | verdict | 근거(검증으로 확인된 사실) | 보강조치 |
|---|---|---|---|
| §6.1 R²<0.99 자동거부 (L315), §12 L508 | **반박(치명)** | 합성측정: 폴리머 노이즈 1%→R²=0.905→거부→영구 NULL, 금속 노이즈 2%→R²=0.982→거부. §1.1 "물성 산출" 목표와 정면 충돌 | C1 |
| §6.1 "구간 점수 ≥5 강제" (L315) | **반박** | 점수함수 정의가 PLAN 어디에도 없음(registry.py 스텁). L234 "사용점수"도 미정의. 분모 없는 마법숫자 | C1 |
| §4.5 SQLite 동시성 모델 (L253-257) | **반박(최우선급)** | §4.5가 `foreign_keys=ON`만 다룸. WAL·busy_timeout 0줄. 런처가 단일 워커(확인) → 단일 프로세스 내 동시 업로드(워크플로우 B)가 즉시 `SQLITE_BUSY`→500 | C2 |
| §9 P1 완료기준 (L446) | **반박(최우선)** | 5항목 중 CASCADE만 통과/실패 명확, 나머지 "표시/동작". E를 틀려도 P1 통과 — 정확도 게이트 0개 | C3 |
| §4.4 경로 `{material_id}/{test_id}` (L249) | **반박(1줄)** | test_id가 곡선 소유자(L148)인데 가변 material_id를 경로에 박음 → 자기모순. 시편 이동 시 곡선 404·CASCADE 증발 보장 | C4 |
| §4.4 트랜잭션 "실패 시 파일 정리" (L250) | **반박** | `finally` 블록은 크래시(restart_policy on_failure 확인) 시 안 돎 → 고아 Parquet 영구 잔존. reaper 없음 | C4 |
| §5.2 graceful "예외 안 던짐" (L271) | **반박(위험)** | delimiter 오인→컬럼 오매핑은 *실패가 아니라 성공으로 분류*됨 → 쓰레기 값이 물성 테이블에 그럴듯하게 표시. confidence 게이트 없음 | C5 |
| §5.2 sniff "< 0.3" (L272) | **반박** | 점수함수 미정의 → 0.3이 무슨 척도인지조차 불명. 분모 없는 임계값 | C5 |
| §3.1 계약에 trailing-slash 보장 (L50-55) | **반박** | RFC 3986: base가 `/apps/slug`(슬래시 無)면 첫 상대 fetch가 `/apps/api/...`로 깨져 slug 증발. 계약에 보장 없음 | C6 |
| §11 D1 "manifest 수정" (L487) | **반박** | 런처가 `(workspace,"/workspace")` 단일 바인드+`cleanenv=True`+`MATERIALTWIN_DATA_DIR` 미주입(확인). "manifest만 고치면 됨"이 아니라 런처가 추가 바인드 미지원 | C7 |
| §3.2 deep-link 상대경로 동작 (L57-59) | **조건부(생존)** | 해시가 `document.baseURI`의 path를 동결 → 라우트가 깊어져도 `fetch("api/...")`가 앱 베이스로 정확히 풀림(실측 확인). 단 "유일한 방법"은 과장, 대가 미기재 | C6, C11 |
| §2.2 "평균±σ는 Phase 3" (L44) | **조건부** | numpy 3줄·새 테이블 불요인데 scipy 피팅과 같은 P3 바구니. ASTM 관행상 단일시편 불신 → P1이 "시편 뷰어"에 머묾 | C8 |
| §8.1 컴포넌트 (L402-406) | **조건부** | graceful 파싱이 핵심인데 ParseIssue 렌더 UI(IssuePanel) 없음 → graceful 가치 미실현 | C9 |
| §4.3 params/extra_metrics raw JSON (L234-235) | **조건부** | 키 드리프트 무방비 + Alembic이 P4(L449) → P3 JSON 변경 시 수동 UPDATE. Pydantic+schema_version으로 차단(테이블·의존성 0) | C10 |
| §5.3 다중시편 3분기 (L281) | **조건부** | `specimens:list` 시그니처는 동결 OK, 분기 로직만 샘플 의존 환각. §5.3(자신감)/§5.7(자백) 톤 분열 | C12 |
| §6.1 "원점강제 −14%" (L311) | **조건부(생존)** | 측정 −17.5%, 방향·자릿수 맞음. 결론(원점강제 금지) 옳음. 단 toe 크기 의존 예시값을 "실측"으로 포장 | C13 |
| §6.1 "구간선택 ±10%" (L311) | **조건부** | 정상구간 산포 1~3%, ±10%는 toe/항복 침범 worst-case. 결론 유지, 조건 명시 필요 | C13 |
| §6.1 "Rp0.2 ±4MPa" (L319) | **조건부(생존)** | 기전(offset 직선 기울기=E 추종) 옳음. 숫자는 항복무릎 둔할수록 커지는 예시 | C13 |
| §8.3 ECharts large+brush+markPoint 동시 (L414) | **조건부** | large 자릿수는 타당하나 large+progressive와 brush 히트테스트 동시성 미검증. LTTB 2000점이면 large 거의 불필요 | C14 |
| §1.3 material_code UNIQUE 멀티유저 (L169) | **조건부(낮음)** | 멀티유저가 같은 코드 쓰면 두 번째 INSERT 차단. owner_id 슬롯 위치만 선결 | C15 |
| §6 "scipy 불필요(numpy만)" (L307) | **생존** | 합성측정 통과: E=polyfit, Rp0.2=부호변화+선형보간, UTS=max, n/K=log-log polyfit, toe=절편외삽 전부 numpy. 변경 불필요 | — |
| §8.3 LTTB ~2000점 (L417) | **생존** | 표준적. markPoint 풀해상도 인덱스 함정도 이미 차단(L417). 영률 프리뷰만 보강 | C14 |
| §4.4 Parquet+포인터 (L241-247) | **생존** | 곡선=한 덩어리 컬럼 데이터, zstd 압축, DB 슬림 — 방향 옳음. 단 경로 키만 수정 | C4 |
| §11 D1 차단성 (L487) | **생존(이미 인정)** | 계획이 §12 치명+§11 최우선으로 자인. 재확인 — 안 풀리면 위 전부 재시작마다 소실 | C7 |

**과함으로 기각(반영 안 함)**: "ZwickText를 통째로 빼라"(→C12 wrapper 축소가 정답), "D1을 P1 착수 차단으로 격상"(L495가 `./var/data`로 P1 진행 명시, C7 WARNING+스모크로 충분), "감사로그/빈상태 P1 필수"(공격 스스로 P1 보류 정당/이미 있음 판정).

### 13.3 치명/높음 보강 항목 (기존 문장 → 수정문)

#### C1 【치명·단일 최우선】 R²<0.99 하드거부 폐기 → 신뢰도 등급 + 항상 값 반환 + 재료군 분기
노이즈 있는 실데이터·폴리머에서 사용자가 물성을 영영 못 받게 만드는 유일한 "제품을 망가뜨리는" 결함.

§6.1 L315:
```
기존:  4. R²<0.99 자동 거부 → 수동 전환 유도. 구간 점수 ≥5 강제.
수정:  4. R²는 거부 트리거가 아니라 **신뢰도 등급**으로 강등한다.
          ≥0.999 → confidence='high', ≥0.99 → 'ok', <0.99 → 'low'.
          **값은 항상 반환하되 processed_result.params.confidence에 등급을 동봉**하고,
          'low'는 UI에서 경고 배지로 노출(거부하지 않음).
       4a. 폴리머(category='polymer')는 명확한 선형구간이 없으므로 E를
          secant modulus(예: 0.05~0.25% 구간 할선) 또는 1% offset으로 분기 산출.
       ※ "구간 점수 ≥5"는 점수함수가 PLAN 어디에도 정의되지 않은 마법숫자이므로 **삭제**.
```
§12 L508:
```
기존:  ... toe보정 기본 ON, 절편포함 회귀, R²≥0.99 거부, brush 수동조정 ...
수정:  ... toe보정 기본 ON, 절편포함 회귀, **R² 신뢰도 등급(거부 아님)**,
          **폴리머 secant 분기**, brush 수동조정 ...
```
§9 L446 brush 완료기준의 "R²<0.99 입력 시 거부" 전제도 "low-confidence 플래그 반환"으로 수정(C3과 연동).

#### C2 【치명】 SQLite 동시성 PRAGMA 신설 (§4.5)
런처는 `fastapi_react` 엔트리포인트를 `uvicorn app.main:app`(`--workers` 없음 = 단일 프로세스, `stacks.yaml:82`)로 실행한다. 따라서 위협은 프로세스 간 락이 아니라 **단일 프로세스 내 동시 업로드**(§2.2 워크플로우 B)이며, 기본 `journal_mode=DELETE`+`busy_timeout=0`에서 즉시 `SQLITE_BUSY`→500이 터진다.

§4.5에 항목 신설:
```
신설:  - **동시성 PRAGMA(연결마다)**: `PRAGMA journal_mode=WAL` + `PRAGMA busy_timeout=5000`
          (또는 SQLAlchemy `connect_args={"timeout": 5}`). 읽기-쓰기 동시성 확보로
          업로드 중 곡선 조회(GET curve)가 안 막히고, 짧은 쓰기 경합을 500 대신 대기로 흡수.
       - **단일 워커 전제 명문화**: 런처가 단일 프로세스로 기동(`--workers` 없음).
          멀티워커 도입 시 본 가정 재검토.
       - **Parquet 쓰기(느린 I/O)는 DB 트랜잭션 밖**에서 끝낸 뒤 마지막에 짧게 INSERT+커밋
          (라이터 점유 시간 최소화. C4 쓰기 프로토콜과 일치).
       - **WAL은 로컬 블록 스토리지 가정** — DATA_DIR이 NFS면 `-wal/-shm` 사이드카가 깨짐
          (§11 D1에서 볼륨 종류 확인 필수).
```

#### C3 【치명·최우선】 P1 완료기준에 골든 픽스처 + 수치 정확도 게이트
§6이 "±10%" 운운하나 완료기준에 정확도 게이트가 없어 E를 틀려도 P1이 통과한다. 골든 픽스처 1개가 없으면 §6 전체가 검증 불가능한 산문이다.

§9 L446:
```
기존:  합성 CSV 업로드→곡선 표시→물성 테이블 표시, brush로 E 재계산,
       양 DB(SQLite) FK CASCADE 테스트 통과, SIF 빌드·서브경로 서빙 동작
수정:  (P1 착수 첫날 산출물로 해석해 존재하는 σ-ε **골든 픽스처 1개**(선형+멱법칙)를 박는다.)
       - [정확도] 골든 픽스처 업로드 → API 반환 E가 해석값 **±2% 이내**,
         Rp0.2 **±2MPa**, UTS **±0.5%** (pytest assert).
       - [brush] 구간 [ε1,ε2] POST → 동일 구간 numpy polyfit 직접계산과 일치.
         low-confidence(R²<0.99) 입력 시 **거부가 아니라 confidence='low' 플래그 반환**(C1).
       - [graceful] 깨진 인코딩/콤마소수점/움라우트 픽스처 → parse() **예외 0건**,
         ParseIssue(level=ERROR) 수집(§5.2 계약을 테스트로).
       - [서브경로] 빌드 후 `dist/index.html` 자산 전부 `./assets/`(절대경로 grep 0개),
         `/apps/test-slug/` deep-link 새로고침 200, **슬래시 없는 진입(/apps/test-slug)** 케이스 1개(C6).
       - [CASCADE] 양 DB FK CASCADE 통과(기존 유지).
       - [reaper] 부팅 정합성 스윕이 고아 .parquet/.tmp 삭제(C4).
```

#### C4 【높음】 경로에서 material_id 제거 + atomic rename + 부팅 reaper
§4.4 L249:
```
기존:  경로: DATA_DIR/curves/{material_id}/{test_id}.parquet, 컬럼 = ...
수정:  경로: DATA_DIR/curves/{test_id}.parquet (샤딩 시 curves/{test_id//1000}/{test_id}.parquet).
       **불변 키 test_id만 사용**(L148 "곡선은 test가 소유"와 일치). material_id는 가변
       외래관계라 경로에서 제거 → 시편 이동 = DB UPDATE 1건, 파일 손 안 댐.
```
§4.4 L250:
```
기존:  트랜잭션: "파일 먼저 쓰고 fsync → DB 커밋", 실패 시 파일 정리.
수정:  쓰기 프로토콜: `{test_id}.parquet.tmp.{uuid}` 쓰기 → fsync → **atomic rename** → DB 커밋.
       크래시(restart_policy on_failure) 시 `.tmp.*`는 항상 고아로 식별 가능.
       finally 정리는 크래시엔 안 돌므로 정리 책임을 reaper로 이관.
```
§4.4 + §9 P1 완료기준에 추가:
```
신설:  **부팅 정합성 스윕(reaper)** — init_db() 직후 curves/ 스캔.
         · DB 포인터 없는 .parquet / .tmp.* → 삭제(또는 quarantine)
         · 파일 없는 DB 포인터 → raw_curve_ref.storage='missing' 마킹(침묵 500 방지)
```

#### C5 【높음】 graceful = "실패 수집 + 불확실은 계산 차단"으로 재정의 + sniff 0.3 제거
graceful의 진짜 위험은 실패를 삼키는 게 아니라 **실패(delimiter 오인→컬럼 오매핑)를 성공으로 분류**하는 것이다.

§5.2 L271:
```
기존:  - parse()는 예외를 던지지 않는다. 모든 실패를 ParseIssue(level=ERROR)로
       수집해 graceful 반환 → 다중 파일 업로드 UX 보호. ...
수정:  - parse()는 예외를 던지지 않되, **파싱 성공 ≠ 계산 허가**다.
       ParseResult에 `confidence`(구조 파싱 자신도) + ParseIssue(level=ERROR/WARN/INFO)를 분리.
       confidence가 낮거나 미해결 INFO(단위·strain% 모호)가 있으면 **processed_result를
       만들지 않고 "확인 필요" 상태**로 둔다(사용자가 단위·컬럼 확인해야 계산 풀림).
```
§5(validate, L268) 물리 일관성 가드 추가(R² 게이트는 계산단계라 별개):
```
신설:  - 오매핑 가드: 단조성(force가 disp처럼 단조증가만 하면 의심),
         채널 간 상관(force와 disp가 동일 신호면 컬럼 오매핑),
         자릿수(N인데 kN 오인 의심).
```
§5.2 L272:
```
기존:  - 미지 형식: sniff 최고점 < 0.3 → GenericCsvParser best-effort → ...
수정:  - 미지 형식: **절대 임계 대신 상대 규칙** — 1등 파서가 2등과 유의분리 안 되거나,
       어떤 파서도 필수 시그니처(헤더 인식 + 수치테이블 인식)를 충족 못 하면 → GenericCsv
       best-effort + needs_manual_mapping. (숫자 유지 시 `SNIFF_FALLBACK_THRESHOLD`를
       config화 + `# placeholder, D2 후 ROC 보정` 주석.)
```

#### C6 【높음】 §3.1 계약에 trailing-slash 보장 추가
해시가 `document.baseURI`의 path를 동결하므로 상대 fetch는 안전하지만, **첫 로드만은 앱 진입 URL이 `/apps/slug/`로 끝나야** 한다. `/apps/slug`(슬래시 無)면 base가 `/apps/`로 잡혀 `fetch("api/...")`가 `/apps/api/...`로 깨지며 slug가 증발한다(RFC 3986 실측).

§3.1에 계약 1줄 추가:
```
신설:  - **런처/Caddy는 앱을 반드시 `/apps/<slug>/`(trailing slash)로 서빙**해야 한다.
       슬래시 없으면 첫 로드 상대 fetch가 `/apps/api/...`로 깨짐(slug 증발, RFC 3986).
       스모크 테스트에 슬래시 없는 진입 케이스 1개 포함(C3).
```

#### C7 【높음】 §11 D1 재기술 — "manifest 볼륨"이 아니라 "런처 추가바인드 미지원"
런처는 `(workspace,"/workspace")` 단일 바인드 + `cleanenv=True` + `MATERIALTWIN_DATA_DIR` 미주입(`integration_launcher.py:430-456` 확인). `./var/data`는 SIF 읽기전용 이미지에서 쓰기 실패한다.

§11 D1 (L487):
```
기존:  HEAXHub 런처 영속 마운트 지원 확인 후 manifest 수정. 최우선
수정:  런처가 추가 데이터볼륨 바인드를 **현재 지원하지 않음**(단일 workspace 바인드 +
       cleanenv=True + MATERIALTWIN_DATA_DIR 미주입 확인) → "manifest만 고치면 됨"이 아니라
       **플랫폼 측(런처) 선결 과제**. 최우선 차단 요인.
```
§3.3 config.py 책임에 추가:
```
신설:  - DATA_DIR 미주입 시 `./var/data` 폴백하되 **기동 시 WARNING 로그**("개발 전용,
       배포 시 절대경로 주입 필수"). P1 완료기준에 "임의 절대 DATA_DIR 주입(SIF 시뮬레이션)
       스모크" 추가 → base 기준점 가정을 P1에서 동결.
```

### 13.4 계획에 반영 확정된 결정 변경 요약 (중·낮 보강 포함)

| ID | 변경 | 위치 | 등급 |
|---|---|---|---|
| C8 | 평균±σ 단순집계를 **P1.5로 승격**(피팅은 P3 유지). 단계 분기 기준을 "도메인 라벨"에서 **"새 테이블/의존성 필요 여부"**로 교체. `/materials/$id` PropertyTable에 재료단위 평균±σ 요약 행(시편별 4컬럼 numpy mean/std, on-the-fly, 새 테이블·화면·의존성 0) | §2.2 L44, §8.1, §9 | 중 |
| C9 | §8.1 `/upload` 컴포넌트에 **`IssuePanel`** 추가(ParseIssue level별 목록, 파일별 부분실패 표시, C5 계산게이트 상태 노출) | §8.1 L404 | 중 |
| C10 | `params`·`extra_metrics`를 **Pydantic 모델(`ProcessingParams`)로 직렬화 + `schema_version:int` 의무화**(raw dict 금지, 읽을 때 버전 분기 → P3 마이그레이션을 전수 UPDATE에서 lazy 변환으로). **계산용 params(계약 필수)와 자유메타 attributes(검색 금지)를 같은 등급으로 묶지 않음**. 새 테이블·의존성 0 | §4.3 L234-235 | 중 |
| C11 | §3.2 "유일한 방법"(L59) → **"빌드타임 슬러그 주입 없이 deep-link 404와 상대경로 깨짐을 동시에 회피하는 가장 단순한 방법"**. 바로 아래 "대가" 1단락 추가(SEO 무관(사내)/분석은 클라 라우터 이벤트 수동계측/`#` 노출 수용). §8.6에 1줄: "해시는 document.baseURI의 path를 동결하므로 라우트가 깊어져도 `fetch('api/...')`가 항상 앱 베이스로 풀림(history면 `…/materials/api/…`로 깨짐 — 실측)" | §3.2 L59, §8.6 | 중 |
| C12 | `specimens:list` 시그니처(길이1 고정)는 **동결**. 한 파일 내 다중시편 **분기 detect/split 로직만 P1에서 제거** → `ParseIssue(WARN,"multi-specimen-in-file not yet supported, split externally")`. 파일분리(N파일=N시편)만 지원. **ZwickText 파서를 독립 structure 휴리스틱 대신 "GenericCsv + 독일 별칭 프리셋"의 얇은 wrapper로 축소**. §5.3을 5.3a(보편사실: 콤마소수점·인코딩폴백 — 합성픽스처로 지금 테스트)와 5.3b(가정: 헤더문자열·단위행·메타블록 — `# ASSUMPTION, needs D2` 스텁, `column_aliases.yaml`은 형식만+엔트리 비움)로 분리 | §5.3 L275-282 | 중 |
| C13 | §6 "수치 함정 실측 검증됨"의 단일 숫자를 **"전형적 예시값"으로 라벨 강등**(결론은 전부 유지). 구간선택 → "정상구간 ~3%, toe/항복 침범 시 최대 ±10%"로 조건 명시. 원점강제 → "toe 절편 존재 시 수~수십% 저평가". Rp0.2 → "offset 교점에서의 곡선 기울기에 반비례(항복무릎 둔할수록 큼)". 토우 컷오프 자동 가드는 §6.1 L312 toe보정과 통합 | §6.1 L309-319, §12 L508 | 낮 |
| C14 | §8.3 `large` 모드를 **비인터랙티브 raw 미리보기 전용**으로 한정(인터랙티브 분석차트는 LTTB 다운샘플 경로). 영률 brush 프리뷰는 저변형률 구간 점밀도가 LTTB에서 희박 → 프리뷰 E에 **"근사" 라벨** 또는 클라가 풀해상도 슬라이스 요청 | §8.3 L414-417 | 낮 |
| C15 | §11에 **D8** 추가 — material_code UNIQUE(L169)가 멀티유저서 INSERT 차단 → P4 인증 전 **슬롯 위치만 결정**(nullable `owner_id` 예약 vs `(owner_id, material_code)` 복합 UNIQUE). P1 운영노트 1줄: "DATA_DIR 백업 = SQLite 파일 + curves/ 디렉터리 cp(자동화는 P4)" | §11, §12 | 낮 |

**우선순위 결론**: **C1(R² 하드거부 폐기)**이 단일 최우선 — 제품을 망가뜨리는 유일한 결함. 다음이 C2(WAL)·C3(정확도 게이트)·C4(material_id 경로)다. **C7+D1은 안 풀리면 위 전부가 재시작마다 소실되는 차단 전제**다. §6 "scipy 불필요", §4.4 Parquet 전략, LTTB 2000점은 적대적 공격에서 **생존**했으므로 그대로 유지한다.

---

## 14. 프리미엄 UX/UI 설계

> 본 섹션은 3개 디자인 방향(A 정밀계측 / B 에디토리얼 / C 모션)과 디자인 디렉터 확정 판정을 단일 명세로 수렴한 것이다. **구현자는 이 절을 그대로 따라 만든다.** 토큰의 단일 진실원천(SSOT)은 방향 A의 HEX→CSS변수 직접참조 체계이며, B는 그 토큰을 소비하는 레이아웃·서사·상태 규칙으로, C는 모션·접근성·성능 규칙으로만 들어온다. 베이스 제약(`base:"./"` 상대경로 / 단일 SIF / `@fontsource/inter` 오프라인 / ECharts core+line / shadcn+Tailwind / hash 라우팅, §3.2·§8.3~8.6·§10)을 한 줄도 깨지 않는다.

### 14.1 디자인 원칙 · 무드

**한 문장 비전**
> "어두운 계측 패널 위에서 데이터가 발광하고, 페이지는 발견의 서사로 읽히며, 모든 반응은 바늘이 값에 꽂히듯 절제되어 안착한다."

**레퍼런스 결**: Linear(절제된 다크 표면·1px ring elevation), Vercel/Stripe 대시보드(밀도와 여백의 균형), Observable(데이터 잉크 우선·발견의 서사), scientific instrument UI(tabular 수치판·바늘 안착 모션). 화려함이 아니라 **정밀 계측기기의 절제된 고급스러움**.

**5줄 헌법**

1. **데이터가 잉크, UI는 종이.** 크롬(테두리·그림자·배경)은 거의 보이지 않게. 잉크는 숫자·곡선·라벨에만 쓴다.
2. **위계는 타이포로, 구획은 여백으로.** 박스·구분선은 최후의 수단. 섹션은 overline 에이브라우 라벨로 연다.
3. **물성값은 "발견"이다.** 대표값은 크고 차분하게(metric 스케일), 단위·통계는 작게 곁들인다. 계측기 디스플레이의 결.
4. **딱 두 강조색.** primary(calibration blue `#3B82F6`)는 액션·포커스·회귀선, accent(signal green `#34D399`)는 확정(commit)·라이브 신호. 나머지는 무채색.
5. **숫자는 항상 `tabular-nums`.** 자릿수가 흔들리면 신뢰가 흔들린다. 모든 수치는 `.tnum` 클래스를 단다.

**다크 우선(dark-default).** 측정·물성 데이터를 종일 응시하는 전문가에게 발광형 데이터(어두운 캔버스 위 곡선·수치)가 눈 피로·집중에 유리하다(PLAN §8.4 명시). 라이트는 보고서/PDF/주광 환경용 **동등 변형**으로 보존하되 WCAG AA로 별도 튜닝한다(§14.7, §14.10).

---

### 14.2 디자인 토큰 (SSOT)

토큰은 모두 `frontend/src/index.css`의 `:root`(다크 기본)와 `.light`(라이트 오버라이드)에 CSS 변수로 선언하고, `tailwind.config.ts`가 이를 색/반경/폰트로 노출한다. shadcn은 `hsl()` 래핑 없이 이 변수를 직접 참조한다. **ECharts canvas는 CSS 변수를 못 읽으므로 §14.3의 `getComputedStyle` 브리지로 런타임 주입**한다.

#### 14.2.1 색 — 표면·경계·텍스트 (다크 기본)

| CSS 변수 | 다크 HEX | 용도 |
|---|---|---|
| `--bg-base` | `#0A0E14` | 앱 최하단 캔버스 (거의 흑, 청록 편향) |
| `--bg-surface` | `#0F141B` | 카드·패널 표면 (1단 elevation) |
| `--bg-surface-2` | `#161D27` | 중첩 패널·tooltip·popover (2단) |
| `--bg-inset` | `#070A0F` | 차트 플롯 영역·입력 필드 안쪽(움푹) |
| `--border-subtle` | `#1C2530` | 패널 경계 (저대비, 거의 안 보임) |
| `--border-default` | `#26303D` | 카드·divider 기본 |
| `--border-strong` | `#37424F` | hover·focus 외곽·축선 |
| `--text-primary` | `#E6EBF2` | 본문·수치 (순백 아님, 눈부심 완화) |
| `--text-secondary` | `#9AA7B8` | 라벨·캡션·축 눈금 텍스트 |
| `--text-tertiary` | `#5E6B7D` | 단위 접미·placeholder·overline |
| `--text-disabled` | `#3A4452` | 비활성 컨트롤 |

#### 14.2.2 색 — primary / accent / semantic (다크)

| CSS 변수 | 다크 HEX | 용도 |
|---|---|---|
| `--primary` | `#3B82F6` | calibration blue — 회귀선·주 액션·링크·포커스 |
| `--primary-hover` | `#5C9AFF` | hover/active 밝기 상승 |
| `--primary-muted` | `#1A2B45` | primary 배경 채움(선택 행·탭) |
| `--primary-fg` | `#0A0E14` | primary 버튼 위 텍스트 |
| `--accent` | `#34D399` | signal green — 확정(commit)·라이브 신호·R²≥0.99 |
| `--accent-hover` | `#5EEAB0` | |
| `--accent-muted` | `#0F2B22` | accent 배경 채움 |
| `--success` | `#22C55E` | 검증 통과·유효 시편 |
| `--warning` | `#F0A92C` | crosshead 신뢰도·INFO 이슈·R²<0.99 |
| `--danger` | `#EF4444` | reject·파단·ERROR 이슈 |
| `--info` | `#38BDF8` | 안내 배지 |
| `--focus-ring` | `#3B82F6` | 키보드 포커스 (outline) |

#### 14.2.3 색 — 라이트 토큰 (보고서/주광용, WCAG AA 튜닝)

| CSS 변수 | 라이트 HEX | 비고 |
|---|---|---|
| `--bg-base` | `#F4F6F9` | 차가운 종이 |
| `--bg-surface` | `#FFFFFF` | |
| `--bg-surface-2` | `#FBFCFE` | |
| `--bg-inset` | `#F0F3F7` | 차트 플롯 영역 |
| `--border-subtle` | `#E6EAF0` | |
| `--border-default` | `#D4DAE3` | |
| `--border-strong` | `#B4BDCA` | |
| `--text-primary` | `#16202C` | 순흑 아님 (대비 14:1) |
| `--text-secondary` | `#46566A` | 본문 대비 7:1 이상 (AA 보정) |
| `--text-tertiary` | `#697789` | 단위·캡션 4.6:1 (AA 본문 통과 — faint 금지) |
| `--primary` | `#2563EB` | 라이트에선 한 단계 진하게 (흰 배경 대비 4.5:1+) |
| `--primary-hover` | `#1D4ED8` | |
| `--accent` | `#0F9D6B` | 흰 배경 대비 AA |
| `--warning` | `#B7791F` | |
| `--danger` | `#DC2626` | |

> 라이트는 **`--text-tertiary`도 본문 4.5:1을 넘기도록** 한 단계 진하게 했다(A·B 공통 자가비판 수용 — faint 보조색으로 핵심 정보를 표기 금지, §14.10 D-a).

#### 14.2.4 색 — 차트 색맹안전 8색 팔레트 (Okabe–Ito 보정)

인접 색은 protanopia/deuteranopia에서도 명도차로 분리된다. primary blue 회귀선·마커와 겹치지 않게 순서를 배치한다.

| # | 이름 | 다크 HEX | 라이트 HEX |
|---|---|---|---|
| 1 | sky | `#56B4E9` | `#1B7FC4` |
| 2 | orange | `#E69F00` | `#C77F00` |
| 3 | teal-green | `#009E73` | `#00805C` |
| 4 | vermilion | `#FF6B57` | `#D94A36` |
| 5 | violet | `#B07AFF` | `#7C4DD6` |
| 6 | yellow | `#F0E442` | `#9A8E00` |
| 7 | rose | `#E37BB0` | `#C13C82` |
| 8 | steel | `#7D93A8` | `#5A6F84` |

> CSS 변수: `--chart-1`…`--chart-8`. **8개 초과 시 색 재사용 + dash 패턴(`[6,4]`)으로 2차 분리** — 색만으로 늘리지 않는다(색맹 안전 유지). 다중 시편 구분은 **색 + 선 스타일 이중 인코딩**.

#### 14.2.5 색 — 차트 구조 토큰

| CSS 변수 | 다크 HEX | 라이트 HEX | 용도 |
|---|---|---|---|
| `--chart-grid` | `#18212C` | `#E9EDF3` | 주 그리드선 (거의 안 보임) |
| `--chart-grid-minor` | `#10171F` | `#F1F4F8` | 보조 그리드 |
| `--chart-axis` | `#3A4654` | `#AEB8C6` | 축선·눈금 틱 |
| `--chart-crosshair` | `#5C9AFF` | `#2563EB` | 십자선 |
| `--chart-regression` | `#3B82F6` | `#2563EB` | 영률 회귀선 |
| `--chart-marker-uts` | `#34D399` | `#0F9D6B` | UTS 마커 (accent green) |
| `--chart-marker-yield` | `#F0A92C` | `#B7791F` | Rp0.2 마커 (warning amber) |
| `--chart-brush-fill` | `rgba(59,130,246,0.10)` | `rgba(37,99,235,0.08)` | brush 선택 영역 채움 |
| `--chart-brush-stroke` | `rgba(92,154,255,0.45)` | `rgba(37,99,235,0.40)` | brush 핸들·경계 |
| `--chart-toe-ghost` | `rgba(154,167,184,0.25)` | `rgba(70,86,106,0.22)` | toe 보정 전 원본 고스트 곡선 |

#### 14.2.6 타이포그래피

**폰트 스택** (Inter self-host, CDN 금지 — SIF 오프라인):
```css
--font-ui:   "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
--font-mono: "Inter", ui-monospace, "SF Mono", "Cascadia Mono", Menlo, monospace;
```
JetBrains Mono는 Phase 1 미룸(PLAN §8.4) → Inter의 `tabular-nums` + feature로 계측기 표시판을 구현. **수치 표시 클래스 `.tnum`은 모든 숫자 셀에 강제**:
```css
.tnum{
  font-variant-numeric: tabular-nums;
  font-feature-settings:'tnum' 1,'cv01' 1,'cv02' 1,'ss01' 1;  /* 곧은 1·열린 4·곧은 6/9 */
  letter-spacing:.01em;
}
```

**타입 스케일** (16px base, rem). 웨이트는 400/500/600만 사용(700 거의 안 씀 — 절제):

| 토큰 | rem | px | line-height | letter-spacing | weight | 용도 |
|---|---|---|---|---|---|---|
| `text-overline` | 0.6875 | 11 | 1.3 | +0.08em UPPERCASE | 600 | **섹션 에이브라우 라벨** (B 이식) |
| `text-2xs` | 0.6875 | 11 | 1.45 | +0.04em | 400 | 축 눈금·단위 접미·테이블 캡션 |
| `text-xs` | 0.75 | 12 | 1.5 | +0.02em | 400 | 보조 라벨·배지·tooltip 보조 |
| `text-sm` | 0.8125 | 13 | 1.54 | +0.005em | 400 | 폼 라벨·테이블 셀 |
| `text-base` | 0.875 | 14 | 1.57 | 0 | 400 | 기본 본문 (UI 밀도↑로 14px 기준) |
| `text-md` | 1.0 | 16 | 1.5 | −0.005em | 500 | 강조 본문·카드 제목 |
| `text-lg` | 1.25 | 20 | 1.4 | −0.01em | 600 | 섹션 헤딩 |
| `text-xl` | 1.5 | 24 | 1.33 | −0.015em | 600 | 페이지 타이틀(재료명) |
| `text-2xl` | 1.875 | 30 | 1.27 | −0.02em | 600 | 대시보드 헤더 |
| `metric-sm` | 1.125 | 18 | 1.2 | +0.01em | 500 | 인라인 물성값 (`.tnum`) |
| `metric-md` | 1.625 | 26 | 1.15 | +0.01em | 500 | 카드 KPI E·Rp0.2·UTS (`.tnum`) |
| `metric-lg` | 2.25 | 36 | 1.05 | +0.005em | 500 | 단일 강조 수치 (`.tnum`) |

> **단위 위계**: 수치는 `metric-*` + 500 weight + `--text-primary`. 단위 접미(`MPa`,`GPa`,`%`)는 한 단계 작게 + 400 + `--text-tertiary` → 값과 단위가 한 시선에 "68.9 GPa"로 읽히되 단위가 물러난다. 이 대비가 계측기 인상의 80%.

#### 14.2.7 공간 · radius · elevation

**Spacing scale** (4px 기반, 8px 리듬):
```css
--sp-0:0;   --sp-1:2px;  --sp-2:4px;  --sp-3:6px;  --sp-4:8px;  --sp-5:12px;
--sp-6:16px; --sp-7:20px; --sp-8:24px; --sp-9:32px; --sp-10:40px;
--sp-11:48px; --sp-12:64px; --sp-14:96px;
```
밀도 우선: 컴포넌트 내부 패딩 `--sp-4`~`--sp-6`(8~16px), 패널 간 갭 `--sp-8`(24px), **섹션 간(층 사이) `--sp-12`(64px)** — 발견의 서사가 호흡하는 간격(§14.6 R4).

**Radius** (작게 — 정밀·기계적 인상, 큰 둥근 모서리 금지):
```css
--radius-xs:3px; --radius-sm:4px; --radius-md:6px; --radius-lg:8px; --radius-full:9999px;
```
기본 컨트롤/카드 `--radius-md`(6px), 차트 패널·테이블 `--radius-lg`(8px), 배지·태그 `--radius-sm`.

**Elevation** — 경계가 elevation의 주 언어. 다크에선 그림자가 약하므로 **1px ring + inner highlight**로 깊이를 만든다(Linear/scientific UI의 "유리 패널" 결):
```css
--elev-0: none;
--elev-1: 0 0 0 1px var(--border-default),
          0 1px 2px rgba(0,0,0,0.40);                /* 카드 */
--elev-2: 0 0 0 1px var(--border-default),
          0 4px 12px -2px rgba(0,0,0,0.55),
          inset 0 1px 0 rgba(255,255,255,0.03);      /* popover·tooltip (상단 하이라이트) */
--elev-3: 0 0 0 1px var(--border-strong),
          0 12px 32px -8px rgba(0,0,0,0.70);         /* dialog·command */
--inset-well: inset 0 1px 2px rgba(0,0,0,0.45),
              inset 0 0 0 1px var(--border-subtle);  /* 입력·차트 plot well */
```
> **hover로 그림자를 변화시킬 땐 `box-shadow` 직접 트랜지션 금지** → 정적 그림자를 가진 `::before` 가상요소의 `opacity` 크로스페이드로 우회(§14.5, 60fps 보장).

#### 14.2.8 모션 토큰 (C 이식)

```css
:root{
  /* duration — 거리·정보량이 클수록 느리게 */
  --mo-dur-instant: 90ms;    /* active press, 토글 노브, checkbox tick */
  --mo-dur-fast:    130ms;   /* hover, focus 등장, 툴팁, 배지 */
  --mo-dur-base:    220ms;   /* 패널 전환, 마법사 step 슬라이드, 다이얼로그 */
  --mo-dur-slow:    360ms;   /* 차트 곡선 draw-in, 진행바 단계 채움 */
  --mo-dur-deliberate: 560ms;/* (P1 제한: A0 등 입력→환산 미리보기 전용. E값 카운트업 미사용) */

  /* easing */
  --mo-ease-out:      cubic-bezier(0.16, 1, 0.3, 1);   /* 진입/전환 기본 — 끝이 길게 안착 */
  --mo-ease-inout:    cubic-bezier(0.65, 0, 0.35, 1);  /* 위치 이동·슬라이드 (대칭) */
  --mo-ease-in:       cubic-bezier(0.4, 0, 1, 1);      /* 퇴장 — 빠르게 사라짐 */
  --mo-ease-snap:     cubic-bezier(0.5, 0, 0, 1);      /* "바늘 안착" — 끝에서 떨림 없이 정지 */
  --mo-ease-emphasis: cubic-bezier(0.34, 1.2, 0.64, 1);/* 확정 배지·체크 — 극미세 오버슈트 */
}
```
**금지 곡선**: `ease`(흐물거림), 큰 오버슈트 bounce(>10%, 장난감), `linear`(곡선 draw-in·카운트업만 예외). 계측 톤의 핵심은 `--mo-ease-snap`(값에 꽂히는 결).

#### 14.2.9 Tailwind 브리지 (발췌)

```ts
// tailwind.config.ts — CSS 변수를 색/반경/폰트로 노출
colors:{
  base:'var(--bg-base)', surface:'var(--bg-surface)', 'surface-2':'var(--bg-surface-2)',
  inset:'var(--bg-inset)', primary:'var(--primary)', accent:'var(--accent)',
  border:'var(--border-default)', muted:'var(--text-secondary)',
  success:'var(--success)', warning:'var(--warning)', danger:'var(--danger)',
},
borderRadius:{ sm:'4px', md:'6px', lg:'8px' },
fontFamily:{ sans:['Inter','sans-serif'] },
```

---

### 14.3 핵심 화면 3개 — 레이아웃 · 위계

공통 셸: 좌측 256px 고정 사이드(collapsed 56px) + 우측 콘텐츠 `max-width:1180px`, gutter `clamp(1.25rem,5vw,4rem)`. **본문 텍스트는 `68ch`로 제한, 데이터(차트·테이블)는 풀폭** 활용(§14.6 R6). 섹션은 **OverlineLabel 에이브라우 + 우측 섹션전용 컨트롤**로 연다(박스 헤더 금지).

#### 14.3.1 `/upload` — 4단계 마법사

```
┌─ container 1180px, gutter clamp ──────────────────────────────────────┐
│                                                                       │
│   ①━━━━━━━② ─────── ③ ─────── ④        ← WizardStepper (수평)         │
│  Drop    Detect    Specimen  Preview                                  │
│  ✓done   ●active   ○         ○                                        │
│  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔   │
│                                                                       │
│   STEP 2 OF 4   (text-overline, text-tertiary)                        │
│   Detect & map columns          (text-lg)                             │
│   testXpert 텍스트가 감지되었습니다. 컬럼 매핑을 확인하세요.            │ ← muted 1줄
│                                                                       │
│   … 한 번에 한 단계만, content 폭 760px 중앙 …                         │
│                                                                       │
│   ─────────────────────────────────────────────────────────────────  │
│            [ ‹ 이전 ]                         [ 다음 › ]               │ ← 하단 고정 네비
└───────────────────────────────────────────────────────────────────────┘
```
**컴포넌트 위계**: `WizardLayout > WizardStepper`(✓/●/○ 상태, 완료 단계만 클릭 되돌아가기, 앞 단계 점프 금지) `> StepHeader`(overline `STEP n OF 4` + `text-lg` 제목 + muted 안내) `> StepBody`(단계별 특화) `> WizardNav`(이전/다음, 자동진행 금지 — 전문가는 확인 없이 넘어가는 걸 싫어함).

- **Step 1 Drop**: `Dropzone`(큰 점선 영역, hover 시 `--primary-muted` 배경 + primary 점선) → 드롭 즉시 `FileChip` 리스트 + 클라 인코딩/구분자 1차 추정 배지.
- **Step 2 Detect**: `ParserDetectBadge`("testXpert 감지 · 신뢰도 0.92" success / "일반 CSV · 매핑 필요" warning) + `ColumnMapper`(추정 결과 미리 채움, 미인식 컬럼만 강조 — 빈 폼 강요 금지).
- **Step 3 Meta**: `SpecimenMetaForm`(형상 라디오 flat/round에 따라 필드 부드럽게 교체) + 우측 `A₀ = 19.6 mm²` 라이브 미리보기(mono `.tnum`, muted — 입력→환산 220ms 카운트업 허용).
- **Step 4 Preview**: 좌측 raw 미리보기 차트(force-disp), 우측 적재 메타 요약, `[커밋]` primary 큰 버튼.

#### 14.3.2 `/materials` — 재료 라이브러리

```
┌─ container 1180px ────────────────────────────────────────────────────┐
│  MATERIALS   (text-overline)                          [+ 업로드]       │
│  재료 라이브러리   (text-xl)                                           │
│                                                                       │
│  [ 검색 q… ]                              [comfortable ⇄ compact]      │ ← MaterialFilterBar + 밀도토글
│                                                                       │
│  ── 카드 그리드(3열, md↓ 2열) 또는 DataTable 토글 ──                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                   │
│  │ AL6061-T6    │ │ S355J2       │ │ Ti-6Al-4V    │  ← MaterialCard   │
│  │ metal · 3 sp │ │ metal · 1 sp │ │ metal · 2 sp │    hover translateY│
│  │ E 68.9 GPa   │ │ E 210 GPa    │ │ E 114 GPa    │    -2px           │
│  │ Rm 310 MPa   │ │ Rm 470 MPa   │ │ Rm 950 MPa   │                   │
│  └──────────────┘ └──────────────┘ └──────────────┘                   │
└───────────────────────────────────────────────────────────────────────┘
```
**컴포넌트 위계**: `MaterialsLayout > SectionHeader`(overline + 우측 `[+ 업로드]`) `> MaterialFilterBar`(검색 + 밀도토글) `> MaterialGrid`(카드 진입 stagger 30ms, 상한 10개) | `DataTable`(헤어라인·zebra, `.tnum` 수치 우정렬). 빈 상태는 `EmptyState`(§14.6).

#### 14.3.3 `/materials/$id` — 곡선 뷰어 + 물성 (발견의 서사)

위→아래 4층: **헤더(맥락) → 발견(물성 띠) → 증거(곡선) → 원장(시편 테이블)**. 층 사이 `--sp-12`(64px).

```
┌─ container 1180px ────────────────────────────────────────────────────┐
│  ‹ 재료 라이브러리                                       [edit] [⋯]    │
│  TENSILE · ASTM E8M   (text-overline)                                 │
│  AL6061-T6   (text-xl)                                   ◷ 3 specimens │
│  Aluminum alloy · AL-6061-T6 · metal   (text-sm muted)                │
│                                                                       │
│  ░░░░░░░░░░░░░░░░░░░░░░ sp-12 (64px) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                                       │
│  KEY PROPERTIES   (text-overline)                                     │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐        │ ← StatBand
│  │ YOUNG'S MOD. │ YIELD Rp0.2  │ UTS  Rm      │ ELONG.  A    │        │   (한 계기판 띠,
│  │ 68.9         │ 276          │ 310          │ 12.4         │        │    헤어라인 분리)
│  │ GPa  E       │ MPa  Rp0.2   │ MPa  Rm      │ %   A        │        │   metric-md 수치
│  │ ░ R² 0.998   │ ░ offset .2% │ ░ n=0.07     │ ░ at fract.  │        │   text-2xs 마이크로
│  └──────────────┴──────────────┴──────────────┴──────────────┘        │
│                                                                       │
│  ░░░░░░░░░░░░░░░░░░░░░░ sp-12 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                                       │
│  STRESS–STRAIN  (overline)        [nominal ▾][ISO ⇄ ASTM][⤓ csv]      │
│  ┌─────────────────────────────────────────────┬───────────────────┐ │
│  │   σ          ╱‾‾‾‾●UTS                       │ SPECIMENS         │ │ ← StressStrainChart
│  │   │       ╱╱                                 │ ● S1  68.9 GPa ◉  │ │   72% / 28%
│  │   │    ╱╱  ●Rp0.2                            │ ● S2  67.4 GPa    │ │
│  │   │  ╱╱ ┊regression E 68.9 R² .998           │ ◌ S3  69.1 GPa ○  │ │ ← SpecimenLegendPanel
│  │   └──────────────────── ε                    │ ───── REGRESSION  │ │   (미니 원장)
│  │   [ ━━━ DataZoom slider ━━━ ]                 │ E 67.4  R² .997   │ │   brush 라이브 프리뷰
│  └─────────────────────────────────────────────┴───────────────────┘ │
│                    (md↓ 세로 스택)                                     │
│                                                                       │
│  ░░░░░░░░░░░░░░░░░░░░░░ sp-12 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                                       │
│  TEST RECORDS  (overline)                              + 시편 추가     │
│  Specimen  Geom  E(GPa)  Rp0.2  UTS   A%   R²    strain    valid       │ ← DataTable
│  ──────────────────────────────────────────────────────────────────   │   (.tnum, 헤어라인)
│  S1 ●      flat  68.9   276    310   12.4  .998  extenso   ✓           │
│  S3 ●      flat  69.1   279    312   12.8  .997  crosshd   ⚠ low-conf  │
└───────────────────────────────────────────────────────────────────────┘
```
**컴포넌트 위계**: `MaterialDetailLayout > DetailHeader`(백링크 + overline + `text-xl` 재료명 + 우측 메타/액션) `> StatBand`(4×`PropertyCard`) `> SectionHeader[STRESS–STRAIN]`(우측 nominal/단위토글/csv) `> { StressStrainChart(72%) | SpecimenLegendPanel(28%) }` `> SectionHeader[TEST RECORDS] > DataTable(density)`.

**PropertyCard 스펙** (B2 이식 — null 물성 명시는 전문가 신뢰의 핵심):
- props: `label, value, unit, symbol, micro[], confidence('ok'|'low'|'none')`.
- `value` → `metric-md` + `--text-primary`, `unit/symbol` → `text-2xs` + `--text-tertiary`, `micro` → `text-2xs .tnum` + `--text-tertiary`.
- `confidence='none'`(취성 등 Rp0.2 없음) → value `—` + micro에 사유(`no stable offset crossing`). **빈 카드를 숨기지 않고 "측정 안 됨"을 명시.**
- `confidence='low'`(R²<0.99·crosshead) → micro에 `⚠ low-confidence`(`--warning`) 행 추가, **value 숫자 색은 중립 유지**(데이터는 비난하지 않음).
- 4개 카드는 개별 박스가 아니라 **하나의 계기판 띠**(`StatBand`, `--bg-surface`, `--radius-lg`)를 `--border-subtle` 좌측 1px로 나눈 것.

**SpecimenLegendPanel 스펙** (B3 이식 — 상호작용 미니 원장):
- 색점(`--chart-1..8`) + 라벨 + 대표E + 가시성토글. **라벨 텍스트가 1차 식별자, 색은 보조**(색맹 안전).
- 행 hover → 해당 곡선 강조(타 시리즈 opacity 0.25로 `--mo-dur-base`). 토글 off → 점 비우고 곡선 숨김.
- brush 드래그 중 라이브 회귀 프리뷰(E·R²·ε구간)는 `--text-secondary`(muted), `apply` 확정 시에만 `--text-primary`로 진해짐 — 클라는 프리뷰, 영속은 서버(PLAN §8.3 정합).

---

### 14.4 응력-변형률 차트 — 시각 스펙 (ECharts 옵션)

**데이터 잉크 최대화**: 축 박스 4면 닫지 않음(좌·하만), 그리드 hairline 점선, 곡선 채움 없는 1.75px 선(평활 금지 — 진짜 데이터). markPoint(UTS/Rp0.2) 좌표는 **서버가 풀해상도 인덱스로 계산해 동봉**(PLAN §8.3, 다운샘플 argmax 금지).

**테마 브리지** (ECharts canvas는 CSS 변수를 못 읽음 → 런타임 주입 + 테마 전환 추종):
```ts
// CSS 변수를 읽어 옵션에 주입. data-theme 변경 시 MutationObserver로 setOption 재호출
const css = (v:string)=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const T = {
  inset:css('--bg-inset'), grid:css('--chart-grid'), gridMinor:css('--chart-grid-minor'),
  axis:css('--chart-axis'), text2:css('--text-secondary'), text3:css('--text-tertiary'),
  primary:css('--primary'), primaryHover:css('--primary-hover'),
  crosshair:css('--chart-crosshair'), surface2:css('--bg-surface-2'),
  border:css('--border-default'), markUts:css('--chart-marker-uts'),
  markYield:css('--chart-marker-yield'), series1:css('--chart-1'),
};
const numCss = "'tnum' 1,'cv01' 1,'cv02' 1";
```

```ts
const option: echarts.EChartsCoreOption = {
  animationDuration: 360,                    // --mo-dur-slow (곡선 draw-in)
  animationEasing: 'cubicOut',
  backgroundColor: 'transparent',
  textStyle: { fontFamily: 'Inter, sans-serif' },
  grid: { left: 64, right: 22, top: 22, bottom: 52, containLabel: false },

  xAxis: {
    type: 'value', name: 'Strain  ε', nameLocation: 'middle', nameGap: 32,
    nameTextStyle: { color: T.text3, fontSize: 11, fontWeight: 500 }, min: 0,
    axisLine:  { lineStyle: { color: T.axis, width: 1 } },
    axisTick:  { show: true, length: 3, lineStyle: { color: T.axis } },
    axisLabel: { color: T.text2, fontSize: 11, fontWeight: 500,
                 formatter: (v:number)=>v.toFixed(3) },
    splitLine: { show: true, lineStyle: { color: T.grid, width: 1, type: [2,4] } },
    minorTick: { show: true, splitNumber: 2, length: 2, lineStyle: { color: T.axis } },
    minorSplitLine: { show: true, lineStyle: { color: T.gridMinor, width: 1 } },
  },
  yAxis: {
    type: 'value', name: 'Stress  σ  (MPa)', nameLocation: 'end', nameGap: 12,
    nameTextStyle: { color: T.text3, fontSize: 11, fontWeight: 500, align: 'left' },
    axisLine: { show: false }, axisTick: { show: false },      // 좌측 박스선 생략 → 데이터잉크↓
    axisLabel: { color: T.text2, fontSize: 11, fontWeight: 500,
                 formatter: (v:number)=>v.toFixed(0), margin: 12 },
    splitLine: { show: true, lineStyle: { color: T.grid, width: 1, type: [2,4] } },
    minorSplitLine: { show: true, lineStyle: { color: T.gridMinor, width: 1 } },
  },

  axisPointer: {                              // crosshair + readout 칩
    show: true, link: [{ xAxisIndex: 'all' }], snap: true, triggerTooltip: true,
    lineStyle: { color: T.crosshair, width: 1, type: [3,3], opacity: 0.55 },
    label: { backgroundColor: T.surface2, borderColor: T.border, borderWidth: 1,
             color: '#E6EBF2', fontSize: 11, padding: [3,6], borderRadius: 4, shadowBlur: 0 },
  },
  tooltip: {
    trigger: 'axis', confine: true,
    backgroundColor: T.surface2, borderColor: T.border, borderWidth: 1, padding: [8,10],
    extraCssText: 'border-radius:6px;box-shadow:0 4px 12px -2px rgba(0,0,0,.55);',
    textStyle: { color: '#E6EBF2', fontSize: 12 },
    formatter: (p:any)=>{ const a=Array.isArray(p)?p[0]:p; const [eps,sig]=a.data;
      return `<div style="font-feature-settings:${numCss};letter-spacing:.01em">
        <span style="display:inline-block;width:7px;height:7px;border-radius:1px;background:${T.series1};margin-right:6px"></span>
        <b>${a.seriesName}</b><br/>
        <span style="color:${T.text2}">ε</span>&nbsp;${eps.toFixed(4)}<br/>
        <span style="color:${T.text2}">σ</span>&nbsp;${sig.toFixed(1)} <span style="color:${T.text3}">MPa</span>
      </div>`; },
  },

  brush: {                                    // 영률 회귀구간 가로 선택
    toolbox: [], xAxisIndex: 0, brushType: 'lineX', brushMode: 'single',
    transformable: true, throttleType: 'debounce', throttleDelay: 60,
    brushStyle: { color: css('--chart-brush-fill'),
                  borderColor: css('--chart-brush-stroke'), borderWidth: 1 },
    outOfBrush: { colorAlpha: 0.28 },         // 구간 밖 곡선 흐리게 → 선택 강조
  },
  dataZoom: [
    { type: 'inside', filterMode: 'none', zoomOnMouseWheel: 'shift' },
    { type: 'slider', height: 16, bottom: 6, filterMode: 'none',
      backgroundColor: 'transparent', borderColor: T.border,
      fillerColor: css('--chart-brush-fill'),
      handleStyle: { color: T.primary, borderColor: T.primaryHover },
      moveHandleSize: 4, dataBackground: { lineStyle: { color: T.axis, width: 1 }, areaStyle: { opacity: 0 } },
      textStyle: { color: T.text3, fontSize: 10 } },
  ],

  series: [{
    name: 'AL6061-T6 · S1', type: 'line', data: curve,    // [[ε,σ],…] LTTB ~2000pt
    showSymbol: false, smooth: false,                      // 평활 금지(진짜 데이터)
    sampling: 'lttb', large: true, largeThreshold: 2000,
    lineStyle: { color: T.series1, width: 1.75, cap: 'round', join: 'round' },
    emphasis: { focus: 'series', lineStyle: { width: 2.25 } },
    markLine: {                                            // 회귀선 (서버 확정 양 끝점)
      silent: true, symbol: 'none',
      lineStyle: { color: T.primary, width: 1.25, type: [5,4], opacity: 0.9 },
      label: { show: true, position: 'insideEndTop', color: T.primaryHover,
               fontSize: 11, fontWeight: 500,
               formatter: `E ${E_GPa.toFixed(1)} GPa · R² ${R2.toFixed(4)}` },
      data: [[ {coord: regP0}, {coord: regP1} ]],
    },
    markPoint: {                                           // UTS / Rp0.2 (서버 풀해상도 좌표)
      symbolSize: 1,
      label: { show: true, position: 'top', distance: 8, color: '#E6EBF2',
               fontSize: 11, fontWeight: 500, backgroundColor: T.surface2,
               borderColor: T.border, borderWidth: 1, padding: [3,6], borderRadius: 4 },
      data: [
        { name:'UTS', coord: utsCoord, symbol:'diamond', symbolSize: 9,
          itemStyle:{ color:'transparent', borderColor: T.markUts, borderWidth: 1.75 },
          label:{ formatter:`Rm ${uts_MPa.toFixed(0)} MPa` } },
        { name:'Rp0.2', coord: rpCoord, symbol:'circle', symbolSize: 7,
          itemStyle:{ color: T.markYield, borderColor: T.inset, borderWidth: 1.5 },
          label:{ formatter:`Rp0.2 ${rp_MPa.toFixed(0)} MPa` } },
      ],
    },
  }, {
    name:'offset', type:'line', data: offsetLine,          // 0.2% offset 보조선 E·(ε−0.002)
    showSymbol: false, silent: true,
    lineStyle:{ color: T.markYield, width: 1, type: [2,3], opacity: 0.55 },
    tooltip:{ show: false },
  }],
};
```
> 다중 시편 오버레이는 `series[i].lineStyle.color = css('--chart-'+((i%8)+1))`, 8개 초과 시 `type:[6,4]` dash로 2차 분리. 시리즈 진입은 시편당 70ms stagger. markLine/markPoint는 "활성 시편"에만 표시(레전드 토글). 성능: `large:true`, 화면 ≤2000점, brush 드래그 중 회귀선 series만 부분 `setOption`(전체 머지 금지) — PLAN §8.3·§14.7 정합.

---

### 14.5 시그니처 인터랙션 · 핵심 모션 스펙

#### 14.5.1 시그니처 — 영률 brush 구간 선택

목표: 곡선 위 탄성구간을 드래그하는 순간 **손끝에서 영률이 계산되는** 계측 감각. 서버 왕복 없이 클라 실시간 회귀(PLAN §6.1, §8.3). **P1은 카운트업 미사용** — 계측기처럼 깜빡임 없이 또렷이 갱신하는 **80ms opacity micro-fade**가 정본(디렉터 결정 3 — C의 560ms 카운트업은 마찰 위험으로 기각, A0 입력→환산만 220ms 허용).

발생 순서:
1. **진입**: "Pick E range" 클릭 → 차트가 `--mo-dur-base`(220ms)간 채도 −12%로 가라앉고(`outOfBrush`), 0.0005~0.0025 기본 구간에 brush 밴드가 좌→우 sweep 후 정착(`--mo-ease-out`).
2. **드래그 중 라이브 회귀**: `throttleDelay:60ms` debounce, 구간 내 점 `polyfit(1)` 클라 계산(2k점 부분집합, <2ms). 밴드 안 회귀 직선이 즉시 그려지고, **선 색이 R²에 따라 보간**: `R²≥0.99 → --accent`(green) / `0.97~0.99 → --primary`(blue) / `<0.97 → --warning`(amber). 손끝에서 색이 변하는 게 핵심 피드백.
3. **부동 readout 칩**: 밴드 상단에 `E 70.3 GPa · R² 0.9994 · n=24`(`.tnum`). 값 갱신은 **80ms opacity micro-fade만** (count-roll 없음).
4. **품질 경고**: 점수<5 또는 R²<0.97이면 밴드 경계 amber 고정 강조 + 칩 `· n<5 부족`(거부 아님, 안내).
5. **toe 고스트**: toe 보정 ON 시 보정 전 원본 곡선이 `--chart-toe-ghost`(25% alpha) 잔상으로 남아 외삽 절편 제거를 시각화.
6. **확정**: `Enter`/"Commit E" → 밴드 180ms accent green flash(box-shadow ring 펄스 1회) → 회귀선이 markLine으로 승격, `POST api/tests/{tid}/properties:compute`. 성공 시 Sonner `E 70.3 GPa 확정` + 물성 테이블 해당 행 120ms 배경 highlight 후 페이드. 실패 시 danger ring 1회 + 롤백.
7. **키보드 대안**: brush 불가 사용자를 위해 ε구간 **숫자 입력 2칸**으로도 조정(동일 compute 경로). 핸들 `←/→` 1px·`Shift+←/→` 격자(0.0005) 이동, `aria-valuenow`에 ε 노출.

#### 14.5.2 핵심 모션 CSS 스펙

**합성 전용 규칙(불변)**: `transform`/`opacity`/`clip-path`/`stroke-dashoffset`만 애니메이트. `width/height/top/left/margin/box-shadow` 직접 트랜지션 금지. `will-change`는 인터랙션 직전 JS 부여·종료 즉시 해제.

```css
/* 드롭존: dragover 글로우 (box-shadow는 가상요소 opacity로) */
.dropzone{ border:1.5px dashed var(--border-default);
  transition: border-color var(--mo-dur-fast) var(--mo-ease-out),
              background  var(--mo-dur-fast) var(--mo-ease-out),
              transform   var(--mo-dur-base) var(--mo-ease-snap); }
.dropzone[data-state="dragover"]{ border-color:var(--primary);
  background:var(--primary-muted); transform:scale(1.008); }     /* 0.8% — "장이 열림" */
.dropzone::after{ content:""; position:absolute; inset:-1px; border-radius:inherit;
  box-shadow:0 0 0 1px var(--primary), 0 0 24px -4px var(--primary);
  opacity:0; transition:opacity var(--mo-dur-fast) var(--mo-ease-out); pointer-events:none; }
.dropzone[data-state="dragover"]::after{ opacity:1; }

/* 업로드 진행: 단계 dot + 연결선 채움 (scaleX) */
.pipe-step__dot{ transition: background var(--mo-dur-fast) var(--mo-ease-out),
                             transform var(--mo-dur-base) var(--mo-ease-emphasis); }
.pipe-step[data-state="active"] .pipe-step__dot{ background:var(--primary); transform:scale(1.15); }
.pipe-step[data-state="done"]   .pipe-step__dot{ background:var(--accent); transform:scale(1); }
.pipe-connector__fill{ transform:scaleX(0); transform-origin:left;
  transition:transform var(--mo-dur-slow) var(--mo-ease-inout); }
.pipe-step[data-state="done"] + .pipe-connector .pipe-connector__fill{ transform:scaleX(1); }

/* 곡선 draw-in: ECharts 내장 (animationDuration 360 cubicOut, §14.4) */
/* markLine/markPoint는 곡선 draw 완료 후 진입, 재계산 시 분석선만 220ms snap 이동(곡선 정지) */

/* 토스트(Sonner) 진입/퇴장 */
[data-sonner-toast]{ transition: transform var(--mo-dur-base) var(--mo-ease-out),
                                 opacity var(--mo-dur-base) var(--mo-ease-out); }
[data-sonner-toast][data-removed="true"]{ transition-duration:var(--mo-dur-fast);
  transition-timing-function:var(--mo-ease-in); }   /* 퇴장은 빠르게 */

/* 마법사 단계 전환: 종이 넘김 (key 변경으로 마운트, framer-motion 미사용) */
.step-enter{ opacity:0; transform:translateX(8px); }
.step-enter-active{ opacity:1; transform:none;
  transition: opacity var(--mo-dur-base) var(--mo-ease-out),
              transform var(--mo-dur-base) var(--mo-ease-out); }
```
> 토스트는 **성공·임시 피드백 전용**. 에러는 토스트로 휘발시키지 않고 인라인 영속(§14.6). 진행 파이프라인 "최소표시 180ms 큐잉"·E값 560ms 카운트업은 P1 기각(디렉터 결정 3·C5).

---

### 14.6 상태 디자인 · 마이크로피드백

#### 14.6.1 빈 상태 — "초대"이지 "사과"가 아니다

중앙 760px 폭, 넉넉한 상단 여백, 얇은 1.5px 라인 아이콘(`--text-tertiary`) + 한 문장 + 단일 1차 액션. **상황별 카피 구분**(같은 컴포넌트, 다른 의미):
- 재료 0개(`/materials`) → "라이브러리 시작" + `[데이터 업로드]`.
- 시편은 있으나 물성 미계산 → "계산을 실행하세요" + `[compute]`.
- 한국어 카피는 **마침표로 종결**(콜론 금지 — 사용자 전역 규칙).

```
        ◜ ◞   ← 빈 곡선 축 라인 글리프 (faint)
   아직 측정 데이터가 없습니다.            ← text-lg, --text-primary
   인장시험 CSV를 업로드하면 곡선과         ← text-base, --text-secondary, max 44ch 중앙
   물성이 여기 나타납니다.
        [ 데이터 업로드 ]                   ← primary 버튼
     또는  샘플 데이터 보기                 ← text-sm 링크 (2차)
```

#### 14.6.2 로딩 스켈레톤 — 레이아웃 보존 + 절제된 시머

스피너 대신 실제 콘텐츠 형상 스켈레톤(레이아웃 시프트 0). **차트는 축을 먼저 렌더**(계측 다이얼이 켜지는 느낌) → 곡선 영역만 시머. 200ms 이내 응답이면 스켈레톤 생략(깜빡임 방지, TanStack Query `placeholderData` + 지연 표시).
```css
.skeleton{ background:linear-gradient(100deg,
    var(--bg-surface) 30%, var(--border-default) 50%, var(--bg-surface) 70%);
  background-size:200% 100%; border-radius:var(--radius-sm);
  animation:shimmer 1.4s var(--mo-ease-inout) infinite; }
@keyframes shimmer{ to{ background-position:-200% 0; } }
@media (prefers-reduced-motion: reduce){
  .skeleton{ animation:none; background:var(--bg-surface); } }
```
변형: `SkeletonStatBand`(overline 짧은 바 + hero 큰 바 + 마이크로), `SkeletonChart`(축 즉시 + 영역 시머), `SkeletonTable(n행)`.

#### 14.6.3 에러 상태 — 진단적, 비난하지 않음

graceful 파서(PLAN §5.2)이므로 에러는 대부분 "이슈 목록"이다. `IssueList`로 **인라인·등급별·실행가능**하게(토스트로 휘발 금지 — 전문가는 다시 읽어야 함).
```
┌──────────────────────────────────────────────────┐
│ ⚠ 3 issues found · 진행 가능        (warning 톤)   │
│  ⛔ ERROR  force 컬럼을 찾지 못했습니다.            │ danger · 차단 · [매핑 열기]
│  ⚠ WARN   strain이 % 단위로 추정됩니다.            │ warning · [확인] [수정]
│  ⓘ INFO   독일식 소수점 감지 → 자동 처리됨.         │ info · 안내만
└──────────────────────────────────────────────────┘
```
- **등급 = 색 + 아이콘 + 차단여부**. ERROR만 커밋 차단, WARN/INFO는 통과시키되 확인 유도(PLAN의 "자동변환 금지·INFO 노출" 철학과 정합).
- 인라인 에러 펼침은 `height` 금지 → `grid-template-rows:0fr→1fr` 트랜지션(레이아웃 안전) `--mo-dur-base` + opacity.
- 전역 크래시(500)는 760px 중앙에 "예상치 못한 오류" + `[다시 시도]` + 접을 수 있는 기술 상세(`<details>`, mono).

#### 14.6.4 마이크로피드백 매트릭스

| 요소 | hover | active(press) | focus-visible |
|---|---|---|---|
| Button (primary) | bg 4% 밝게, `--mo-dur-fast` | `scale(0.97)` `--mo-dur-instant` `--mo-ease-snap` | outline 2px + offset 2px, 즉시 |
| Button (ghost) | bg `--bg-surface-2` 페이드 130ms | `scale(0.98)` | outline |
| DataTable row | bg 3% + 좌측 2px primary bar `scaleY 0→1` 130ms | — | row inset ring |
| MaterialCard | `translateY(-2px)` + `::before` 그림자 opacity 220ms | `translateY(0) scale(0.995)` | outline |
| Checkbox/Switch | 노브 색 130ms | 노브 `scale(0.9)` 90ms | outline |
| 차트 legend 항목 | 해당 시리즈 강조(타 시리즈 opacity 0.35, 220ms) | — | outline |

> `scale(0.97)` press가 "물리적이되 가벼운" 결의 핵심(0.95는 장난감, 0.99는 무반응). release 시 90ms로 복원. transform-origin center.

---

### 14.7 접근성 체크리스트 (WCAG AA — 필수 게이트)

- [ ] **대비**: 텍스트 4.5:1, 큰 텍스트·UI 컴포넌트·차트 선 3:1 이상(다크·라이트 양쪽 실측). 라이트 `--text-tertiary`도 본문 4.5:1 통과(§14.2.3). **faint 보조색으로 핵심 정보 표기 금지.**
- [ ] **색 단독 금지**: valid/invalid(`test.valid`)·R²·이슈 등급은 **색 + 아이콘 + 텍스트** 다중 인코딩. R²≥0.99 green은 ✓ 병기, 다중 시편은 색 + 선 스타일 이중 인코딩.
- [ ] **prefers-reduced-motion 전역 차단**:
```css
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{ animation-duration:.01ms !important; animation-iteration-count:1 !important;
    transition-duration:.01ms !important; scroll-behavior:auto !important; } }
```
  의미 있는 상태 변화는 모션 대신 즉시 적용(투명도/색 유지, 이동/scale만 제거). ECharts `animation:false`. JS 모션(WAAPI/rAF, A0 카운트업 포함)은 `matchMedia('(prefers-reduced-motion: reduce)').matches` 가드 후 최종값 즉시 적용.
- [ ] **focus 링** — `:focus-visible` 한정, 즉시(트랜지션 없음), 대비 3:1:
```css
:where(button,a,[role=button],input,select,[tabindex]):focus-visible{
  outline:2px solid var(--focus-ring); outline-offset:2px; border-radius:inherit; }
:focus:not(:focus-visible){ outline:none; }
```
- [ ] **키보드 전 플로우 완주**: 업로드→매핑→커밋→brush 회귀(ε 숫자입력 2칸 대안)까지 마우스 없이. 마법사 `←/→`·`Enter`, 각 step `role="tabpanel"`+`aria-current`, 포커스는 새 step 첫 필드로. DataTable 화살표 행 이동·`Enter` 상세 진입. 다이얼로그 focus trap·`Esc`·트리거 포커스 복귀.
- [ ] **발작 안전**: 깜빡임 3회/초 초과 없음(처리 중 pulse 1.1s = 0.9Hz 안전), 무한 모션은 처리 중에만·종료 시 정지.
- [ ] **tabular-nums**: 카운트업/라이브 갱신 중 자릿수 폭 흔들림 없음(`.tnum` 강제).

---

### 14.8 추가 프론트 의존성 · 자산 결정 · Phase 1 제약 준수

**폰트 self-host** (PLAN §8.4, §10): `@fontsource/inter`만 추가(CDN 금지 — SIF 오프라인). `main.tsx`에서 `import "@fontsource/inter/400.css"`…`/600.css` + `/variable` 임포트. `@fontsource/jetbrains-mono`는 미룸 — 수치는 Inter `.tnum` feature로 충분.

**Phase 1 제약 준수 확인**:
- [ ] **framer-motion 미사용** — 모든 모션은 CSS `transition`/`@keyframes` + WAAPI(`element.animate()`) + ECharts 내장만. 마법사 전환·스켈레톤·brush 모션 전부 CSS로 구현, 번들 추가 0(PLAN §10 미룸 목록 준수).
- [ ] **zustand/cmdk 미사용** — 마법사 진행상태는 useState/hook(PLAN §8.2).
- [ ] **ECharts core+line only** — `echarts/core` + `LineChart` + `Grid/Tooltip/AxisPointer/MarkLine/MarkPoint/DataZoom/Brush` 컴포넌트만 import(§14.4). `manualChunks`로 별도 청크(PLAN §8.6).
- [ ] **상대경로·hash 라우팅 불변** — 모든 fetch/다운로드는 선행 슬래시 없는 상대경로, `base:"./"` 불변, `createHashHistory()`(PLAN §3.2, §8.6). 디자인 토큰·모션은 순수 클라이언트라 이 제약과 무관.
- [ ] **신규 추가 의존성**: `@fontsource/inter`(폰트), `react-dropzone`(Dropzone), `sonner`(토스트), `tailwindcss`+`tailwind-merge`+`clsx`+`class-variance-authority`(스타일) — 전부 PLAN §10 Phase 1 목록 내. **신규 디자인 전용 의존성 0**(애니메이션 라이브러리 도입 없음).

**미해결 보정사항(§14.10 연동)**: 라이트 토큰은 §14.2.3에서 1차 AA 튜닝했으나, 다크 그리드 저대비의 주광/프로젝터·인쇄(PDF) 환경 실측 검증이 남는다 — 구현 시 실제 대비비 측정 후 토큰 미세조정(A·B 공통 자가비판 수용).
