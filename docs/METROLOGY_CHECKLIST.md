# 시험장비 편입 체크리스트

## 1. 스키마
- [x] `Instrument` · `InstrumentCapability` 모델 추가 → 검증: `python3 -c "from app.models import Instrument"`
- [x] alembic 마이그레이션 생성·적용 → 검증: `integrity_check.py` 이상 0
- [x] 무결성 점검에 장비 규칙 추가 → 검증: 규칙이 목록에 뜨고 0 이 나온다

## 2. 적재 도구
- [x] `ingest_instrument_json.py` — 배치 산출 JSON 을 적재(dry-run 기본) → 검증: dry-run 이 오류 0
- [x] 카탈로그 PDF 를 `source(kind='datasheet')` 로 dedup 등록 → 검증: 80편에 출처 80건 이하(시리즈 합본 있음)

## 3. 데이터 추출 (배치)
- [x] 공통 지시문 `METROLOGY_PREAMBLE.md` 작성 → 검증: 규율 8개가 다 들어갔다
- [x] thermal 9편 · mechanical 16편 추출 → 검증: dry-run 통과
- [x] surface 15편 · chemical 12편 추출 → 검증: dry-run 통과
- [x] particle 9 · optical 5 · electrical 4 · ndt 4 · reliability 6 추출 → 검증: dry-run 통과
- [x] `property_key` 매핑 검수 — 애매한 것은 안 잇는다 → 검증: 매핑된 키가 전부 `property_definition` 에 있다

## 4. API
- [x] `GET /api/metrology/instruments` (분류·물성 필터)
- [x] `GET /api/metrology/by-property/{key}` — 기법별로 묶은 장비 목록
- [x] `GET /api/metrology/coverage` — **잴 장비가 없는 물성** 목록
- [x] 검증: `pytest` 통과 + 각 엔드포인트 스모크 테스트

## 5. 화면
- [x] `/metrology` 라우트 + 사이드 내비 항목
- [x] 물성 선택 → 기법 → 장비 표(측정범위·온도범위·규격)
- [x] 물성 카탈로그 빈 칸에서 넘어오는 링크
- [x] 검증: `npm run build` 통과

## 6. 마무리
- [x] `PROPERTY_DATA_HISTORY.md` 에 장이 하나 추가
- [x] 산출물 4종 재생성
- [ ] 라이브 재배포 — **AIDataHub 는 `/api/export/materials` 로 당겨 가는 구조라 밀 게 없다.**
      다만 새 라우터·화면은 재배포해야 라이브에 뜬다(DB 는 이미 라이브를 직접 쓰고 있다).
- [x] 커밋
