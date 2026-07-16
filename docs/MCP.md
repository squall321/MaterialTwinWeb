<!-- MaterialTwin MCP 서버 레퍼런스 — LLM이 물성 DB를 조회·등록하는 도구/리소스/프롬프트 명세. -->
# MaterialTwin MCP 서버

LLM(Claude 등)이 MaterialTwin 물성 DB를 자연어로 **조회·등록·수정·삭제**하도록 노출하는 MCP 서버. **두 가지 트랜스포트**로 동일한 도구를 제공하며, 웹 API와 동일한 DB·계산 경로를 공유한다.

- **엔트리**: `backend/mcp_server.py` (FastMCP `"materialtwin"`)
- **stdio**: `.mcp.json` → `backend/.venv/bin/python backend/mcp_server.py` (개인 Claude, 전체 신뢰 → 도구 20 전부)
- **streamable HTTP**: 웹앱 `app.main`이 `/mcp`에 마운트(리다이렉트 없는 exact 경로). 배포 시 HEAXHub 게이트웨이가 manifest `mcp.expose`로 `/apps/materialtwin_web/mcp`를 자동 흡수 → 포털 챗·개인 Claude에서 페더레이션.
  - 등록 예) `claude mcp add --transport http materialtwin <포털베이스>/apps/materialtwin_web/mcp`
- **데이터**: 웹과 동일한 SQLite(`var/data/materialtwin.db`) + 곡선 Parquet
- **노출**: 도구 20(HTTP 기본 18 — 아래 *삭제 게이팅*) · 리소스 2 · 프롬프트 2 (프로토콜 왕복 검증 완료)

## 삭제 게이팅(페더레이션 안전)

게이트웨이는 툴 레벨 ACL이 없으므로 서버가 직접 가시성을 건다. **HTTP(app.main)는 `MATERIALTWIN_MCP_ALLOW_DELETE=0`을 기본 주입**해 `delete_material`/`delete_test`를 **미노출**(중앙 게이트웨이에는 18종). 개인 stdio는 전체 20종. HTTP에서도 삭제를 열려면 `MATERIALTWIN_MCP_ALLOW_DELETE=1` 명시.

## 단위 규약
- 입력 곡선: `strain` 무차원(% 아님), `stress_mpa` MPa. 완화는 `time_s`[s]·`modulus_mpa` MPa.
- Prony 파라미터: `G0`/`Ginf` MPa, `beta` 1/s (LS-DYNA ton·mm·s 관례).
- LS-DYNA 카드 단위계: `ton_mm_s`(기본, MPa) · `kg_m_s`(SI) · `g_mm_ms` · `kg_mm_ms`.
- 오류 표기: dict 도구는 `{"error": "한국어"}`, 카드 텍스트 도구는 `"error: 한국어"`, 이미지 도구는 한국어 예외.

## 도구 (20)

### 조회 (13)
| 도구 | 역할 |
|---|---|
| `list_materials(category, query, limit≤200)` | 재료 목록 + 대표 물성(단일 outerjoin) |
| `get_material(material_id)` | 재료 상세 + 시편·시험(각 시험의 `valid` 플래그 포함) |
| `get_curve(test_id, kind, max_points)` | 곡선 포인트(nominal·true·relaxation, LTTB 다운샘플) |
| `get_fits(test_id)` | 구성방정식 피팅(Hollomon/Swift/Voce/JC)·R²·파라미터 |
| `get_mat_card(test_id, units, model)` | LS-DYNA 카드 텍스트(*MAT_024·*MAT_098·*MAT_VISCOELASTIC). PR 필드는 `attributes.nu`(0<nu<0.5)면 그 값, 아니면 0.3 |
| `search_by_property(prop, min, max, limit)` | UTS/yield/E 범위 검색(유효 시험만) |
| `find_materials_in_property_range(E, UTS 범위)` | Ashby 물성박스 검색(AX) |
| `database_summary()` | 총계·카테고리별·시험유형별·피팅 수 |
| `material_taxonomy()` | 재료 분류 체계·계열 분포 |
| `property_distribution()` | 물성 히스토그램 통계 |
| `coverage_gaps()` | 커버리지 갭(rich/sparse/missing) |
| `plot_curve(test_id, kind)` | 곡선 PNG 이미지(matplotlib) |
| `plot_ashby()` | Ashby E–UTS 물성공간 PNG |

### 등록·수정·삭제 (7 — HTTP 기본은 삭제 2종 미노출)
| 도구 | 역할 |
|---|---|
| `register_material(name, category, material_code, description, attributes)` | 새 재료 등록. `attributes`(dict)로 nu·G_MPa 등 수동 상수 저장 |
| `register_tensile_test(material_id, strain[], stress_mpa[], …, orientation)` | 인장곡선 등록 → 시편 자동생성·물성·구성방정식 4모델 피팅까지. `orientation`(예: RD/TD/0/90)은 이방성·적층 해석용 |
| `register_relaxation_test(material_id, G0/Ginf/beta 또는 time_s/modulus_mpa, …)` | 점탄성 완화 등록(Prony 파라미터 또는 실측 곡선) |
| `update_material(material_id, …, attributes)` | 재료 메타데이터 부분 수정. `attributes`는 기존 값에 얕은 병합(nu·G_MPa 등) |
| `delete_material(material_id, confirm)` | 재료+하위 삭제(confirm=False면 미리보기). *HTTP 기본 미노출* |
| `delete_test(test_id, confirm)` | 시험 1건 삭제(confirm 2단계). *HTTP 기본 미노출* |
| `recompute_properties(test_id, e_min, e_max)` | 탄성 회귀창 지정 물성 재계산 |

단축 인장은 포아송비·전단탄성계수를 산출하지 못한다(단일 축 응력). `register_material`/`update_material`의 `attributes`에 `nu`(포아송비)·`G_MPa`(전단) 등을 수동 저장하면 `get_material`이 노출하고, `nu`는 LS-DYNA 카드 PR 필드에 반영된다.

**등록 검증**: 곡선 최소 20점·NaN 금지·카테고리별 strain 상한(금속 2.0 / polymer 5 / rubber·foam 10)·저항복 자동 탄성창 보정. 모든 오류는 한국어.

## 리소스 (2)
- `materialtwin://guide` — 단위 규약·워크플로·주의(LLM이 사용법을 스스로 발견).
- `materialtwin://taxonomy` — 재료 분류 체계 + 현재 DB 분포(라이브).

## 프롬프트 (2)
- `find_material(requirements)` — 요구조건→물성범위 번역→후보→비교→카드 도출 절차.
- `register_test_data(description)` — 인장/완화 자동판별→등록→검토→카드 절차.

## 견고성 (5라운드 적대적 리뷰로 확보)
- 웹↔MCP 대표 시험 선택·`valid` 플래그·단위·에러 메시지 **정합**(제외한 이상치를 LLM이 유효물성으로 오인하지 않음).
- 동시성: 시편 라벨 UNIQUE+재시도(8-way 동시등록 검증), ProcessedResult 업서트 경합 가드, 곡선 read TOCTOU 가드.
- GI=0(완전 완화) 카드 왜곡·fit_prony E∞ 접힘·JC 초기값 발산 등 수치 결함 수정.

## 시연
`docs/showcase.html` — LLM이 MCP로 재료 검색→곡선→피팅→LS-DYNA 카드→등록까지 하는 실제 대화 예시(실출력 임베드).
