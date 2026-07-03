# DB 마이그레이션 (Alembic)

스키마 변경을 버전 관리한다. `env.py`가 `app.db.Base` 메타데이터와
`settings.database_url`(env `MATERIALTWIN_DATABASE_URL`)을 단일 진실원천으로 쓴다.

## 개발/테스트 (SQLite, 기본)
`app.db.init_db()`가 `create_all()`로 그린필드 스키마를 즉시 만든다(빠름). 마이그레이션 불필요.

## 운영 (영속 볼륨·Postgres)
데이터가 배포 간 유지되므로 반드시 마이그레이션으로 스키마를 진화시킨다.

```bash
cd backend
# 최신 스키마로 업그레이드
alembic upgrade head
# 모델 변경 후 새 마이그레이션 생성
alembic revision --autogenerate -m "add xxx"
# 기존 create_all DB를 alembic 관리로 편입(1회)
alembic stamp head
```

## Postgres 전환
```bash
pip install -e ".[postgres]"   # psycopg 설치
export MATERIALTWIN_DATABASE_URL="postgresql+psycopg://user:pw@host:5432/db"
alembic upgrade head
```
SQLite 전용 PRAGMA(FK/WAL)는 `app.db`가 dialect로 자동 스킵한다. JSON·DateTime(tz)·FK CASCADE는
양 DB에서 동일 동작함을 `tests/test_postgres_compat.py`가 실 Postgres로 검증한다.

## 드리프트 가드
`tests/test_migrations.py`가 `alembic check`로 모델↔마이그레이션 불일치를 CI에서 차단한다.
컬럼을 추가하고 마이그레이션을 안 만들면 테스트가 실패한다.
