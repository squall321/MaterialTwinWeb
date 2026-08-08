# 데이터 허브 물성 내보내기 — 체크리스트

목표 — AIDataHub가 재료 이름만이 아니라 **물성값·조건·tier·출처까지** 받게 한다.

## 배경 (현황 진단 결과)

| 항목 | HEAXHub | AIDataHub |
|---|---|---|
| 재료 544종 | 있음 | 523종 (21종 누락) |
| 물성값 15,295건 | 있음 | **0건** |
| 출처 1,835건 | 있음 | **0건** |

원인 둘.
1. 허브가 긁는 `/api/materials`는 목록만 돌려준다. `attributes`가 `{"source":"mcp"}` 한 줄이라
   `content_extra_fields: [attributes]`로 보존할 수치가 없다.
2. 허브의 `_fetch_page`는 응답에서 `next_cursor` / `cursor` / `meta.next_offset`을 찾는데
   현 API는 `{items,total,page,size}`만 준다 → **1페이지(100건)에서 멈춘다.**
   `sync_runs.fetched_count`가 매 실행 100으로 고정된 것이 그 증거다.

## 작업

- [x] 1. `GET /api/materials/export` 추가 — 재료 + 전체 물성값 + 출처
      → 검증: `size=100`으로 6페이지 순회해 544종이 다 나오고 마지막만 `next_cursor: null`
- [x] 2. 응답에 `next_cursor` 포함 (다음 page 번호 문자열, 마지막이면 null)
      → 검증: 허브 `_fetch_page` 규약과 일치 — `body["next_cursor"]`
- [x] 3. `body` 텍스트 렌더 — 물성명·값·단위·조건·tier·출처를 한 문자열로
      → 검증: 응답 문자열에 '열전도율'과 수치가 들어 있다
- [x] 4. N+1 회피 — 페이지 내 재료의 물성·출처를 한 번에 적재
      → 검증: 100종 응답이 2초 이내
- [x] 5. 회귀 테스트 추가
      → 검증: `pytest` 통과
- [x] 6. `AIDataHub/config/sync_sources.yml` 갱신
      (`list_endpoint`, `body_field: body`, `content_extra_fields: [properties, sources]`)
      → 검증: yaml 파싱 + 허브 재기동
- [x] 7. MaterialTwin 재배포
      → 검증: `/api/materials/export?page=1&size=2`가 라이브에서 200
- [x] 8. 동기화 트리거 후 확인
      → 검증: `records` 544건, `content::text ilike '%youngs_modulus%'` > 0

## 성공 기준

허브의 `records` 테이블에서 아무 재료 하나를 열었을 때
**물성값·단위·측정조건·tier·출처 URL이 다 보인다.** 근거를 허브에서 되짚을 수 있어야 한다.

## 결과 (2026-08-08 완료)

| 항목 | 전 | 후 |
|---|---|---|
| `sync_runs.fetched_count` | 100 (고정) | **544** |
| 허브 레코드 | 523 | **544** (+ 잔재 5건 소프트 삭제) |
| 허브 물성값 | **0** | **15,295** |
| 문서 본문 | 빈 문자열 | 물성 목록 텍스트 |

전문검색 실측 — '열전도율' 319건, 'tier1' 496건, '열전도율 + through-thickness' 조합 검색도 걸린다.
MaterialTwin DB(544종 15,295건)와 허브가 정확히 일치한다.

### 덤으로 발견한 것 — 허브에 tombstone 구현이 없다

`sync_runs.tombstoned_count` 컬럼은 있는데 `sync_svc`에 쓰는 코드가 없다. 상류에서 삭제된
재료가 허브에 영원히 남는다. 실제로 5건이 남아 있었다 — MaterialTwin의 중복 정리(앞선 파동에서
Ti_Grade2 중복, FR-4 계열 정리 등)로 삭제된 재료 id 223·242·243·249·404이다.

이번에는 `records.deleted_at`으로 소프트 삭제했다(허브 조회가 `deleted_at is null`을 거르므로
유효하다). 근본 해결은 허브 쪽 작업이라 여기서는 손대지 않았다 —
**주기적 full ID set 비교**가 sync_svc 문서에 옵션으로 적혀 있으나 미구현이다.
