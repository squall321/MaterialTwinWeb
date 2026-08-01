<!-- 화·물리 물성 전방위 확장 전략 — taxonomy·프로비넌스 스키마·합법 소스 획득·추출 파이프라인. -->
# 물성 전방위 확장 전략 (Property Expansion)

기계 물성에 더해 **열·전기·광/복사·화학·물리/수송·음향·자기·유변·구조** 전 도메인의 화학·물리
물성을 **근거(출처) 있게** 채운다. 예: 흡습율·방사율·열전도율·유전율·투과도·부식률.

## 대전제

- **프로비넌스 우선** — 값마다 출처·측정조건·불확실도·신뢰등급이 붙는다. 근거 없는 값은 저장하지 않는다.
- **출처 합법성** — 합법 공개 소스만 사용한다(OpenAlex·Crossref·Unpaywall·Wikidata·PubChem·NIST·
  Materials Project·제조사 데이터시트). **논문의 수치값(사실)은 저작권 대상이 아니므로** 출처를 명시하면
  DB화는 정당하다. Sci-Hub/LibGen 대량 다운로드 스크래퍼는 만들지 않는다 — 파이프라인은 **사용자가
  정당하게 확보한 PDF를 `corpus/`에 넣으면 추출**하는 구조라 획득 경로와 추출 로직이 분리된다.
- **조건 의존성** — 비기계 물성은 온도·습도·주파수·파장·방위에 강하게 의존한다. 조건 없는 값은 무의미.

## 신뢰등급(quality_tier)

| tier | 의미 |
|---|---|
| 1 | 측정(1차문헌, 측정법·불확실도 포함) |
| 2 | 핸드북/권위 DB(ASM·NIST·CRC·Wikidata CC0) |
| 3 | 제조사 데이터시트 |
| 4 | 계산(DFT·경험식) |
| 5 | 추정/유추(플래그) |

## 데이터 구조 (구현됨)

- **`property_definition`** — 물성 사전(taxonomy). `key`=`domain.name`(예 `thermal.conductivity`)·
  정규단위·value_type·표준시험법·조건축. 부팅 시 `property_taxonomy.py`가 멱등 시드(현재 ~91 물성).
- **`source`** — 인용 레지스트리(DOI/ISBN/URL·license·local_path·content_hash). DOI/해시로 dedup.
- **`property_value`** — `material → property_key → value+unit+uncertainty+conditions(JSON)+
  method+quality_tier+source`. 한 물성에 출처·조건 다른 값 다수 공존.

## 획득 전략 (3경로)

1. **구조화 DB 커넥터**(무인증·값+출처 직접) — 순물질·표준재료에 강함.
   - ✅ **Wikidata**(`acquire/wikidata.py`) — 밀도·열전도율·융점·굴절률, SI 정규화(오단위 skip), CC0 출처.
   - ⬜ PubChem(화합물), Materials Project(DFT 무기결정), NIST WebBook/SRD.
2. **문헌 추출**(상용 합금·고분자 등 커넥터가 못 채우는 대상).
   - ⬜ OpenAlex/Crossref/Unpaywall로 재료×물성 논문 탐색 → `source` 적재 + OA PDF 링크.
   - ⬜ `corpus/`(DOI/해시 파일명·dedup)에 정당 확보 PDF 투입 → PDF/표 파싱 → **LLM 구조화 추출**
     (property_definition 스키마 강제, 값마다 출처·페이지·신뢰도) → 검증 게이트 → `property_value`.
3. **수동/에이전트 등록** — ✅ MCP `register_property`(출처 필수) — 개인 Claude/포털 챗이 직접 근거와 함께 입력.

## MCP 도구 (구현됨)

- `list_property_definitions(domain)` — 채울 수 있는 물성 taxonomy.
- `get_material_properties(material_id, domain)` — 수집값 + 프로비넌스(값·조건·등급·출처).
- `register_property(...)` — 근거(출처) 필수 물성 등록.

## 체계화(systematization)

- **source dedup** — DOI > content_hash > url. 재수집 멱등.
- **property_value 멱등** — (material, key, source, conditions) 동일 시 갱신, 아니면 삽입.
- **커버리지 매트릭스** — material × property → 채움/빈칸. "다음에 무엇을 찾을지" 자동 지시(⬜ UI).
- **해석 품질 주의** — 순진한 이름/부분문자열 매칭은 오매핑 위험(예: "SPCC강"→"pc"→polycarbonate).
  구조화 커넥터는 **큐레이션된 material→entity 매핑**을 쓰고, 애매하면 skip한다.

## 단계 (status)

- **Phase A ✅ (기반)** — 스키마 3테이블+마이그레이션(`888056f1c5b8`)·전방위 taxonomy 시드·store·
  Wikidata 커넥터·MCP 조회/등록·테스트. 파이프라인 end-to-end 실측 검증(Al 2700kg/m³·236W/mK·933K 등).
- **Phase B ⬜ (구조화 확대)** — PubChem·Materials Project·NIST 커넥터 + 큐레이션 material→entity 매핑.
- **Phase C ⬜ (문헌 추출)** — OpenAlex/Crossref 탐색 + `corpus/` + LLM 추출 + 검증 게이트.
- **Phase D ⬜ (운영)** — 커버리지 매트릭스 UI·웹 물성 탭·갭 기반 탐색 루프.

## 카탈로그 메타데이터 규약 (그레이드 단위 정합성)

재료를 "단단하게" — 실제 쓰는 재질과 1:1로 맞추고 추론이 되게 하려면 **그레이드 단위 + 업체
식별 + 구조화 메타데이터**가 필요하다.

- **그레이드 단위 등록** — 제품이 특정 그레이드를 쓰면(예: APEL 5014CL) 그 그레이드를 **별도 재료**로
  등록하고 그 제조사 데이터시트를 붙인다. 일반 클래스값은 그레이드 데이터시트가 없을 때만 폴백(tier4).
- **재료 메타데이터**(`Material.attributes` 표준 키, `app/material_metadata.py`): `manufacturer`·`grade`·
  `trade_name`·`material_class`·`process`·`application`·`subsystem`·`standard`·`composition`.
- **값 프로비넌스의 업체** — `Source.publisher`(= manufacturer)에 남긴다. `register_property`의
  `source_manufacturer`, 추출 시 `source_manufacturer`로 채운다.
- **추론 검색** — MCP `find_materials_by_metadata(manufacturer·material_class·subsystem·grade·process)` —
  "Mitsui 재료", "모든 COC 그레이드", "배터리 재료" 등 카탈로그 추론 지원.
