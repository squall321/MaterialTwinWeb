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
