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
- 기존 인메모리 `/api/tasks` 스캐폴드(`_tasks`)는 `main.py` 교체 시 **삭제**한다.

### 3.2 라우팅 전략 — 단일 결정 (비판 [feasibility] A-1 충돌 수렴)
**결정: `base:"./"` 유지 + TanStack Router `createHashHistory()` (해시 라우팅).**
근거: 이 템플릿의 `StaticFiles(html=True)` 서빙 모델은 `/materials/42` 같은 deep-link를 index.html로 rewrite하지 않아(Starlette 실측), 빌드타임 슬러그 주입 없이 deep-link 새로고침이 깨지지 않는 유일한 방법이 해시 라우팅이다. ([ux]가 인용한 "hash가 형제앱 검증됨"은 사실이 아니므로 그 근거 문구는 폐기하고, 위 기술적 근거로 대체한다.)

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

- 경로: `DATA_DIR/curves/{material_id}/{test_id}.parquet`, 컬럼 = time, force_N, disp_m, extenso_strain, eng_stress_Pa, eng_strain.
- 트랜잭션: "파일 먼저 쓰고 fsync → DB 커밋", 실패 시 파일 정리. 삭제는 DB 먼저, 파일은 앱 레이어에서 명시 삭제(FK CASCADE가 파일은 못 지움 — [feasibility] B-1).
- inline_json은 100점 미만 소형/픽스처 폴백.

### 4.5 SQLite→Postgres 호환 핵심 규칙
- **PRAGMA foreign_keys=ON** 연결마다 강제(`event.listens_for(Engine,"connect")`). 빠지면 CASCADE 침묵 실패 → 환경별 삭제 비결정성([feasibility] B-1). **양 DB CASCADE 테스트 작성.**
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

### 6.1 Phase 1 알고리즘 (수치 함정 실측 검증됨 — [feasibility] D)

**영률 E** ([feasibility] D-1/D-2 실측: 구간 선택 ±10%, 원점강제 −14%):
1. **Toe(발끝) 보정 기본 ON**: 선형구간 직선을 ε축 외삽 → 절편 ε0 제거 → 원점 이동 (ASTM E8).
2. 구간 선택: Phase 1은 **고정 변형률 구간(예: 0.0005~0.0025) + UI brush 수동조정**. auto 슬라이딩윈도우는 Phase 4로 미룸([overeng] B8).
3. **반드시 절편 포함 회귀**(`polyfit deg=1`), 원점 강제 절대 금지.
4. **R²<0.99 자동 거부** → 수동 전환 유도. 구간 점수 ≥5 강제.
5. 사용구간·R²·점수를 `processed_result.params`에 **항상 반환**(추적성).
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
| **P1: 기초 인장 MVP** | material/specimen/test/raw_curve_ref/processed_result 5테이블, GenericCsv+ZwickText 파서, E/Rp0.2/UTS/A% 계산, /upload·/materials·/materials/$id 3화면, ECharts 곡선뷰어+brush 회귀 | 합성 CSV 업로드→곡선 표시→물성 테이블 표시, brush로 E 재계산, 양 DB(SQLite) FK CASCADE 테스트 통과, SIF 빌드·서브경로 서빙 동작 |
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
**Phase 3+**: scipy(피팅), alembic(마이그레이션), psycopg[binary](Postgres), kaitai-struct(바이너리). cp312 휠 모두 제공 확인 → SIF 컴파일 불필요. lockfile/해시 고정 권장.

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
| 치명 | **영속 볼륨 미선언** → 재시작 데이터 소실, Parquet 전략 무효화 | manifest 볼륨 선언(D1). 미해결 시 곡선을 한시적 DB BLOB로 폴백할 결정 경로 확보 |
| 치명 | **라우팅 전략 충돌**([arch] HashRouter vs [ux] hash history vs 형제앱 History) + StaticFiles는 deep-link rewrite 안 함(실측) | `base:"./"` + TanStack `createHashHistory()` 단일 확정(§3.2). "hash 형제앱 검증" 문구 폐기 |
| 치명 | **SQLite FK CASCADE 침묵 실패** → 환경별 삭제 비결정성, 고아 Parquet | PRAGMA foreign_keys=ON 강제 + 양 DB CASCADE 테스트 + 파일은 앱레이어 삭제 |
| 높음 | **JSON 컬럼 검색** → SQLite/PG 쿼리 분기 | 검색·정렬 키 정규 컬럼 승격, JSON에 WHERE/ORDER BY 금지 |
| 높음 | **파서 휴리스틱 재작업** — 첫 실데이터에서 거의 확실 | 인터페이스·파이프라인·graceful만 동결, structure는 스텁+합성 픽스처 테스트, MVP=GenericCsv+수동매핑 |
| 높음 | **영률 변동** — 구간 ±10%, 원점강제 −14%(실측) | toe보정 기본 ON, 절편포함 회귀, R²≥0.99 거부, brush 수동조정, 사용구간·R² 항상 반환 |
| 중 | **0.2% offset이 E오차 추종**(±4MPa) | E신뢰도 연동 경고, 첫 안정 교점 규칙, 평활은 표시용·원본보존 |
| 중 | **단위 경계**(파서 mm/kN ↔ DB m/N/Pa) | units.py 단일 모듈이 ingest 시 1회 정규화, 파서는 원본+메타만 |
| 중 | **tz naive/aware 혼용**(SQLite 통과, PG 에러) | 입력 경계 UTC aware 강제, func.now() |
| 중 | **다운로드 비ASCII 파일명, LTTB가 마커 죽임** | filename*=UTF-8'', 마커는 풀해상도 인덱스로 계산 후 오버레이 |
| 낮음 | **SIF 용량**(pyarrow/pandas +200MB) | manylinux 휠 컴파일 불필요. scipy는 Phase 3 optional extra로 분리 |

---

**핵심 단일 메시지**: P1은 5테이블·동기계산·2파서·3화면으로 얇게 시작하고, 확장은 JSON 슬롯과 list 시그니처로만 예약한다. 착수 전 **라우팅 1개 확정(완료: hash)**, **영속 볼륨(D1)**·**testXpert 샘플(D2)** 두 항목만 사람이 풀면 된다.
