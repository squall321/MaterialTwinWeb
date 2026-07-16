<!-- MaterialTwin 프로젝트 개요·현황·구조 진입점. -->
# MaterialTwin

쯔윅(Zwick/Roell testXpert) 인장·완화 시험 데이터를 업로드받아 **물성 도출 → 구성방정식 피팅 → LS-DYNA 카드**까지 한 흐름으로 만들고, 그 DB 전체를 **LLM이 MCP로 직접 조회·등록**하는 재료 물성 플랫폼.

## 구성
- **backend/** — FastAPI + SQLAlchemy(SQLite↔Postgres) + Alembic. 단일 SIF로 프런트(`frontend/dist`)를 StaticFiles 서빙.
- **frontend/** — Vite + React + TypeScript, 상대경로·해시 라우팅(`/apps/<slug>/` 서브패스 대응), ECharts.
- **backend/mcp_server.py** — MCP(stdio) 서버. → [docs/MCP.md](docs/MCP.md)
- **scripts/drive-sync/** — Google Drive 데이터·SIF 동기화(손실 없는 병합). → [scripts/drive-sync/README.md](scripts/drive-sync/README.md)
- **docs/** — [intro.html](docs/intro.html)(비전) · [showcase.html](docs/showcase.html)(시연) · [MCP.md](docs/MCP.md)

## 기능 현황 (2026-07 기준)

| 영역 | 상태 |
|---|---|
| 인제스트 → 물성(E·Rp0.2·UTS·연신) | ✅ 골든 픽스처 ±2% 검증 |
| 진응력·넥킹(Considère) | ✅ |
| 구성방정식 피팅(Hollomon/Swift/Voce/Johnson-Cook) | ✅ |
| 점탄성 완화·Prony 급수 | ✅ |
| LS-DYNA 카드(*MAT_024·*MAT_098·*MAT_VISCOELASTIC, 4 단위계) | ✅ |
| 인사이트 대시보드(Ashby·계열 통계·커버리지·지식그래프) | ✅ |
| 업로드 마법사·재료 편집/삭제·시험 이상치 토글 | ✅ |
| **MCP 서버**(조회 13 · 등록 7 도구 + 리소스 2 + 프롬프트 2) | ✅ 프로토콜 왕복 검증 |
| Postgres 호환 | ✅ PG16 실검증 |
| SIF 패키징(HEAX_DATA_DIR 영속 볼륨) | ✅ 리허설 완료 |

**품질**: pytest **112 passed**, 프런트 빌드 클린, 마이그레이션 체인 upgrade↔downgrade 왕복·드리프트 없음.

**보류(외부 의존/후순위)**: 실 testXpert 바이너리(zse/zsx) 파서·초탄성(Ogden) 카드(실데이터 필요), 자동 E구간 선택·인증(설계상 후순위).

## 개발
```bash
# 백엔드(Python 3.12 .venv 필수 — 시스템 python은 3.10)
cd backend && .venv/bin/python -m pytest -q
MATERIALTWIN_DATA_DIR=$PWD/var/data \
  MATERIALTWIN_DATABASE_URL=sqlite:///$PWD/var/data/materialtwin.db \
  .venv/bin/python -m uvicorn app.main:app --port 17777

# 프런트
cd frontend && npm run build   # dist/ 를 백엔드가 서빙
```

## 견고성 이력
자율 하드닝 루프에서 5라운드 적대적 리뷰(파일별·물리·파서·횡단 정합성·동시성)로 실결함 **35건 발견·수정**. 상세는 [context-notes.md](context-notes.md)·[checklist.md](checklist.md).
