# 58차 TB 작업 기록 — packaging 솔더 합금 코어 빈칸

라이브 DB `MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web` 로만 읽고 썼다.

## 산출물

| 파일 | 무엇 |
|---|---|
| `tb01_solder_core.json` | 값 27행 / 재료 9종. `ingest_agent_json.py --apply` 로 적재 완료(거부 0) |
| `tb02_core_verdicts.json` | 판정 / 재료 22종. `apply_core_verdicts.py --apply` 로 적재 완료 |
| `BRIEF_DRAFT.md` | 브리프 초안 11건 |

## 결과 — `subsystem='packaging'` · `role='product'`

```
적재 직전  116종 · 812칸 · 채움 407 (50.1%) · V1 21 · V2 232 · V6 3 · V3 0 · V4 24 · V5 125
적재 직후  116종 · 812칸 · 채움 407 (50.1%) · V1 21 · V2 254 · V6 7 · V3 0 · V4 24 · V5  99
```

**주의 — 위 "적재 직전" 은 57차 SA 가 넘긴 192 가 아니다.** 같은 라이브 DB 에 다른 배치가 동시에 쓰고 있어
내가 시작할 때 192 였던 V5 가 값 적재 직전에 이미 125 였다. **내 몫만 떼어 세면 이렇다.**

- **값으로 닫은 코어 칸 10** — 2677(밀도·CTE·인장) 3 · 966(CTE·비열) 2 · 574(CTE·인장) 2 ·
  572(인장) 1 · 578(인장) 1 · 582(CTE) 1. 전부 적재 후 DB 조회로 확인했다.
- **판정으로 닫은 칸 26** — V2 22 · V6 4. **선언 26 = 집계 증가 26**(V2 232→254 · V6 3→7 · V5 125→99)로
  §610 의 대조를 통과했다.
- **솔더 갈래(재료 29종)만 따로 세면 V5 122 → 86 이다.** 아홉 종이 0 으로 닫혔다 —
  574 SAC405 · 584 SAC387 · 577 60Sn40Pb · 578 62Sn36Pb2Ag · 579 Sn-3.5Ag · 583 Indium ·
  576 92.5Pb5Sn2.5Ag · 962 Sn63Pb37 · 966 Sn0.7Cu · 2677 SACX0307.
- 그 밖 넣은 비코어 값 17행 — 연신율 3 · 비커스/브리넬 경도 3 · 융점 5 · 항복강도 1 · 체적저항률 1 등.

## 검사

- `integrity_check.py` — **이상 1개**(`물성값 0인 재료 2` = 기존 시험 잔재 2종). 신규 위반 0. 기준선과 같다.
- `verdicts_check.py` — **이상 0개**. 신고 1건(재료 229 Doosan DS-7402)은 54차 PC 가 만든 기존 어긋남이다.
- `pytest -q` — **366 passed, 1 skipped**. 기준선과 같다.

## 실제로 연 문서 (§127) — 새 문 11장

**ALPHA(MacDermid) 계열 7장**
1. ALPHA Vaculoy SACX 0307,0300 HASL TDS (SM956-1, Rev 2/15/08) ← **적재 출처 4765**
2. ALPHA SACX PLUS 0307,0300 TDS (Issue 22 May 2023) — 1과 같은 표를 다시 인쇄. 재인용이라 미적재
3. ALPHA VACULOY Sn99.3Cu0.7 Solid Solder TB (17 Dec 2021) ← **적재 출처 4766**
4. ALPHA SOLDER SPHERES TDS (Issue 25 May 2020) ← **적재 출처 4769**. 등급 확정의 열쇠
5. ALPHA SACX Plus 0807, 0800 Solid Solder TB (13 Mar 2020) — 비열 반증용
6. ALPHA SnCX Plus 07, 00 TDS (05 Aug 2022) — 비열 반증용
7. ALPHA Sn60Pb40 Plus Solid Solder TB (06 Dec 2019) — Wiedemann-Franz 확인용

**그 밖 4장**
8. Kester `TECHNICAL DATA ON SOFT SOLDERS`(Alloy Properties, Knowledge Base) — 영률 기각 근거
9. AIM Solder `ALLOY INFORMATION` ← **적재 출처 4767**
10. Duong 2021, JST ETSD 31(5) 075-080, DOI 10.51316/jst.154.etsd.2021.31.5.11 ← **적재 출처 4768**
11. Kapp Alloy 등급 페이지 4장(SAC305/0307/387/405) — 물결표 값 반증

**다시 연 기존 문서 4장(§602·506)** — The Solder Connection 2023(출처 3641) ·
ALPHA VACULOY SAC300~405 TDS(출처 4652) · Indalloy 2006(출처 4753) · Guangzhou Xianyi 편람(출처 3678) ·
Ibrahiem 2019(출처 3480) · Wang 1998(출처 3456) · Jian-Chun Liu 2014(출처 3457) · Darveaux 2011(출처 3616).

받아 둔 사본은 `/home/koopark/claude/MaterialTwinWeb/.agent_work/w58tb/` 에 있다.

## 결정과 이유

- **Indalloy·Solder Connection 두 표에 행이 없다는 전제는 맞았다.** 아홉 표를 전수로 훑어 재확인했다.
  SAC107·SAC205·97.5Pb2.5Sn 은 아홉 표 전부에 행이 없다. SACX0307 만 전용 TDS 가 있었다.
- **SACX0307 의 등급 확정은 ALPHA SOLDER SPHERES TDS 로 했다** — 제품 TDS 는 Bi 를 안 밝히고
  "2 minor elements" 라고만 쓴다. 스피어 TDS 합금표가 `Sn 98.9 / Ag 0.3 / Cu 0.7 / Bi 0.1` 로 찍어
  재료 2677 의 조성과 글자 단위로 맞았다.
- **비열 0.17 J/kg·C 는 기각했다**(V6) — 단위가 인쇄 자체로 틀렸고, 가장 너그러운 해석 170 J/(kg·K)도
  Kopp-Neumann 229.0 보다 26% 낮으며, 같은 제조사 형제 등급 넷이 0.214~0.236 이다.
- **62Sn36Pb2Ag 영률(Kester 3.41e6 psi = 23.51 GPa)은 기각했다**(V6) — Reuss 하한 31.2 보다 25% 아래.
  같은 열의 Sn60Pb40 은 하한과 0.1% 안에서 겹치고 Sn40Pb60·Sn30Pb70 은 10% 아래라, 이 행만 이상치다.
- **97.5Pb2.5Sn 영률(Wang 1998 24.13 GPa)은 기각했다**(V6) — **Voigt 상한 18.9 보다 28% 위**다.
  게다가 논문 자신이 Tensile 행이 Shear 행의 포아송비 환산임을 밝힌다(비 2.6931 = 2(1+0.3465)).
- **Sn-8Zn-3Bi 의 인장강도는 기각했다**(V6) — Duong 2021 의 36.8/47.8 MPa 는 Cu/솔더/Cu **접합체** 값이고
  저자가 계면 파단임을 밝힌다. 같은 논문의 CTE 는 벌크 봉재 시편이라 넣었다(§141 칸 단위 판정).
- **ALPHA Sn99.3Cu0.7 의 열전도율 60.5 W/(m·K)는 안 넣었다** — 같은 표의 저항률에서
  Wiedemann-Franz 로 60.7 이 나와 0.3% 안이고, 같은 제조사 Sn60Pb40 Plus 도 같은 관계를 만족한다(환산값이다).
- **Kapp Alloy 의 물결표 값은 안 넣었다** — SAC0307 `~40 MPa` 가 두 독립 벤더의 29.4/29.5 와 36% 어긋난다.
- **Depiver 2021 Table 1·2 는 안 썼다** — Table 1 은 The Solder Connection 형 벤더표의 재인용([61,62])이고
  kgf/cm² 값이 글자까지 같다. Table 2 는 FE 입력표(§3)이며 SAC305 ν 0.40 · SAC405 ν 0.42 로 계열 밖이다.
- **포아송비 판정 15칸은 표 열셋을 전수로 확인해 박았다.** 열이 하나도 없다.
- **아무것도 지우지 않았다.** 자유 키 `core_doors_tried` 는 집계가 안 읽으므로 그 칸은 그대로 V5 로 센다 —
  아직 표적인 것이 맞고, 남긴 이유는 다음 파동이 같은 아홉 표를 다시 훑지 않게 하는 것뿐이다.

## 신고 — 공유 도구를 고쳐야 열리는 것 (§468 이라 손대지 않았다)

1. **빈칸 갈래가 하나 더 필요하다 — "값이 형제 키에 있다".**
   솔더 여섯 종(572·573·574·575·586·2677)의 `mechanical.tensile_strength` 가 비었는데
   `mechanical.tensile_strength_at_rate` 에 2~160행이 이미 있다. 575 는 `youngs_modulus_at_rate` 도 160행이다.
   `coverage_report.CORE7` 이 `_at_rate` 계열을 안 보므로 이 칸은 영원히 V5 로 센다.
   자리 제안 `attributes.core_value_at_sibling_key`(이번에 재료 586 에 시범으로 박았다. `core_` 접두어라 운영까지 간다).
2. **57차 SA 가 신고한 V4 전파 문제는 그대로다** — `identification_status`·`anonymised_code` 가
   병합기 `CURATION_KEYS` 밖이다.

## 다음 표적 — 솔더 갈래에 남은 것

| 재료 | 남은 V5 | 다음 문 |
|---|---:|---|
| 986 SAC107 | 7 | 벤더 아홉 표 전부에 행 없음. **Sn-1.0Ag-0.7Cu 를 직접 잰 논문**(Si3N4·SnO2·MWCNT 첨가 연구의 기준시편)이 유일한 길 |
| 965 SAC125Ni | 6 | ALPHA 스피어 TDS 는 조성·융점만. Nihon Superior · Senju · Nihon Handa 일본어 등급 페이지, iNEMI Pb-Free Alloy Characterization 보고서 |
| 580 97.5Pb2.5Sn | 6 | 다섯 편찬표에 행 없음. Indium Corporation 고연 등급별 제품 페이지 · 5N Plus · 다이본딩 프리폼 벤더 |
| 575 SAC-Q | 6 | 상표 CYCLOMAX. **조성이 갈린다** — Lall 3.4Ag/3.4Bi 대 CapLinq LINQALLOY SACQ 4.0Ag/3.0Bi/0.05Ni. 등급을 못 닫으면 붙이지 마라(§22·586) |
| 573 SAC205 | 6 | **상용 등급이 아니다.** 벤더가 아니라 논문(Basit 2015 · Chen 2020 · Cai 2010 후속) |
| 581 Sn-9Zn-2.5Bi-0.5In-0.01P | 7 | 논문 개발합금. Jian-Chun Liu 연구실 후속 논문 |
| 586 SAC(307)-2In | 6 | 논문 개발합금. 원문에 밀도·CTE·k·Cp 표가 없음을 전문으로 확인했다. 인장강도 칸은 형제 키에 값이 있다(신고 1) |
| 582 Sn-8Zn-3Bi | 5 | CTE 닫음. 벌크 시편 인장·밀도·k·Cp 는 다른 논문 필요 |
| 585 Sn0.3Ag0.7Cu | 3 | E·CTE·k 는 아직 문이 없다. **ALPHA SACX0307 시트는 이 재료가 아니다**(Bi 0.1 도핑 등급 = 재료 2677) |
| 572 SAC105 | 1 | CTE 만 남음. **ALPHA VACULOY SAC 100,105 Solid Solder TB** — 403 이고 Wayback 스냅샷도 없다 |
