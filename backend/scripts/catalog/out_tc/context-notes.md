# 58차 TC 작업 기록 — packaging 잔여 셋(언더필 5종 · EMC 3종 · Cu-Al IMC 5종)

라이브 DB `MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web` 로만 읽고 썼다.

## 산출물

| 파일 | 무엇 |
|---|---|
| `tc01_emc_core.json` | 값 1행 — EMC 739 포아송비. `ingest_agent_json.py --apply` 완료 |
| `tc03_cual_imc_cte.json` | 값 5행 — Cu-Al IMC 다섯 상 CTE. 적재 완료 |
| `tc04_cual2_thermal.json` | 값 3행 — CuAl2 비열·열전도율·열확산율(신규 출처 Nazarahari 2026). 적재 완료 |
| `tc02_make_verdicts.py` | 판정 JSON 생성기(사유 문장이 여기 산다) |
| `tc02_core_verdicts.json` | 판정 49칸 / 재료 13종. `apply_core_verdicts.py --apply` 완료 |
| `BRIEF_DRAFT.md` | 브리프 초안 8건(번호 비움) |

받아 둔 사본 — `/home/koopark/claude/MaterialTwinWeb/.agent_work/w58tc/`
(논문 md·PDF · 400 dpi 렌더 · `vendor_uf/` 벤더 시트 20장 · `imc/` Nazarahari 2026 PDF + Drozdov 학위논문 · DB 스냅샷).

## 표적 57칸의 처리

| 갈래 | 칸 | 값 | 판정 |
|---|---:|---:|---:|
| 언더필 5종(1352·1369·1676~1678) | 25 | 0 | 25 |
| EMC 3종(964·739·1368) | 16 | 1 | 15 |
| Cu-Al IMC 5종(664~668) | 16 | 7 | 7 |
| **합계** | **57** | **8** | **49** |

`subsystem='packaging'` · `role='product'` 집계(같은 시각 다른 배치도 돌고 있어 값 칸은 겹친다).

```
스냅샷  116종 · 812칸 · 채움 389 (47.9%) · V1 21 · V2 184 · V6 2 · V4 24 · V5 192
적재후  116종 · 812칸 · 채움 407 (50.1%) · V1 21 · V2 184 · V6 2 · V4 24 · V5 174   ← 채움 +18 중 내 몫 8
판정후  116종 · 812칸 · 채움 407 (50.1%) · V1 21 · V2 232 · V6 3 · V4 24 · V5 125
```

**§610 대조 — 선언 49칸(V2 48 · V6 1) = 집계 증가(V2 +48 · V6 +1 · V5 −49).** 어긋남 0.

## 검사

- `integrity_check.py` — 스냅샷 대비 **신규 위반 0**(항목별 출력이 글자까지 같고 마지막 집계 줄만 다르다). 이상 1개는 기존 시험 잔재 2종.
- `verdicts_check.py` — **이상 0개**. 신고 1건은 54차 PC 가 만든 기존 어긋남(재료 229).
- `pytest -q` — **366 passed, 1 skipped**.

## 인계가 틀린 것 — 여섯 편이 전부 로컬에 있었다

57차 SA 의 다음 표적 표가 Kaltenpoth 2001 · Zhang(Qun) 2000 · Katsurayama 2008 · **Kouters 2013** ·
Chiu 2011 · Lau 2018 을 *"로컬에 없다 · 조달해라"* 로 넘겼다. **여섯 편 전부 `/data/paper_patent_corpus` 에 있다**
(Kouters 는 원본 PDF 까지). 원인은 이 여섯 `source.local_path` 가 전부 `NULL` 인 것이다 —
그 칸은 적재한 배치가 채우는 칸이지 코퍼스 색인이 아니다. 브리프 초안 1번.

**`source.local_path` 는 고치지 않았다**(출처 행 정정은 이 배치의 권한 밖이다). 대신 판정 사유마다 코퍼스 경로를 박았다.

## 결정과 이유

- **Kouters Table 1 의 CTE 열은 살렸다.** 본문의 *"the thermal expansion … is of a factor of ten in error"* 가
  자기 표가 아니라 **원출처 Wulff 를 가리킨다**는 것을 Drozdov 2007 학위논문 p.13 Table 2(Wulff 전재)로 확인했다 —
  그쪽 값이 정확히 1/10 이고, 순물질 행(Al 23.5 · Cu 17.3 대 교과서 23.1 · 16.5~17.0)이 어느 쪽이 옳은지 가른다.
  2차 인용이고 1차(Wulff EPTC 2004 · Rabkin 1970) 조달에 실패했으므로 **t3**.
- **같은 표의 밀도 열은 안 썼다.** CuAl 을 2.7 로 인쇄하는데 바로 위 Al 행 2.70 의 복제이고
  같은 논문 Table 4 실측 5.31 과 어긋난다(§141 — 어긋난 칸만 버린다).
- **CuAl2 의 비열·열전도율은 Nazarahari 2026(CC-BY)에서 넣고 Cu4Al3 은 안 넣었다.**
  Theta 행은 본문이 `Al2Cu (θ)` 로 상을 명시하고 밀도 4.23 이 카탈로그의 Kouters 실측 4.27 과 0.9% 안이라 동정이 닫힌다.
  Zeta 행은 조성이 Cu4Al3 구간 안이지만 그 논문이 `ζ2 (Al9Cu11.5)` 로 부르고 **다섯 시편 중 그것만 ζ1+η2 이상혼합**이다.
  Theta 도 결정립계 Al4Cu9 석출물이 있어 **t3** 로 두고 조건에 박았다.
  표의 자기검산 — `k = cp·alpha·rho` 가 다섯 행 전부 0.8% 안에서 재현되고 Cp/Dulong-Petit 가 0.83~0.91 이다.
- **열전도율 62.0 대 126 W/mK 이견을 신고했다.** Zhang 2023 종설(PMC10144406)이 Al2Cu 를 126 이라 적지만
  1차 둘(Gunduz & Hunt 1985 · Ocak 2010)이 유료라 못 열었다. 인쇄값 62.0 을 t3 로 넣고 이견을 notes 에 적었다.
- **EMC 739 의 포아송비 0.35 를 t3 로 넣었다.** Chiu 2009 Table 3 의 맨 칸은 §3 대상이지만
  Chiu 2011 **본문**이 유도를 적어 둔다(K = 26.7 GPa 가정 + 완화계수). 같은 논문 TABLE IV 의 E0 = 24 GPa 로
  `nu = (3K−E)/(6K) = 0.3502` → 인쇄 0.35 와 두 자리 일치. 고무상 0.493 은 넣지 않았다(선택기에 regime 축이 없다).
- **언더필 25칸은 한 칸도 못 채웠다.** 벤더 시트 20장을 열어 ν·비열·인장강도가 **0/20** 임을 확인했고
  (Chhanda 2012 의 서술을 권위가 아니라 검산 대상으로 다뤘다), 밀도·열전도율은 갈래가 찍는데도
  **이 등급들에 붙일 문서가 없다**. `Lamics` 는 존재한 적 없는 도메인이고 NAMICS 의 오기로 보이지만
  등급(`-3`)이 어느 NAMICS 문서에도 없고 영률이 22% 어긋나 **빌리지 않았다**.
- **아무것도 지우거나 합치지 않았다.**

## 신고 — 다음 파동이 판단할 것

1. **재료 1352 와 1369 는 같은 언더필이다.** 두 논문이 같은 표(408 K · 26 · 110 · 9.0 GPa · 75 MPa)를
   각주까지 글자 단위로 같게 인쇄하고, 저자·소속이 겹치며 뒤 논문이 앞 논문을 인용한다.
   이름을 밝힌 것은 Kaltenpoth 뿐이라 1369 의 `trade name not printed` 는 `U-8437-3` 이다.
   **1369 의 빈칸 5개는 미채굴이 아니라 중복이다.** 병합은 조정자 판단.
2. **같은 인쇄값 75 MPa 를 두 배치가 다르게 처리했다.** 1352 는 `interface.cohesive_strength` t2 로 넣었고,
   1369 의 attributes 는 *"not transferable to this taxonomy … no matching key exists"* 라 적혀 있다.
   **같은 표의 같은 칸이다 — 한쪽이 틀렸다.**
3. **재료 665 의 이름 `CuAl (gamma)` 가 틀렸다.** 원문 Table 2 는 이 상을 `η`, Drozdov 는 `η2` 로 인쇄한다.
   `γ` 는 Cu9Al4(재료 668)의 기호다. 추출본이 `η`→`g`, `γ`→`c` 로 뭉갠 것이 이름에 굳었다. 이름은 안 건드렸다(자연키).
4. **`source.local_path` 가 비어 있는 출처 여섯이 코퍼스에 있다**(위 인계 절). 채워 두면 다음 파동이 안 헤맨다.
5. **Rabkin 1970(DOI 10.1007/BF00803820)이 열리면 다섯 상의 인장강도·미소경도·저항률·CTE 가 한꺼번에 닫힌다.**
   Springer 유료. 도서관 경유가 유일한 길로 보인다.
