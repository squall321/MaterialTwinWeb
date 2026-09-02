# 60차 VA 작업 기록 — packaging 상용 솔더 등급

라이브 DB `MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web` 로만 읽고 썼다.
명령은 전부 `backend/` 에서 돌렸다.

## 표적

58차 TB 가 넘긴 `subsystem='packaging'` 솔더 잔여 — 재료 아홉(986·965·580·575·573·586·963·585·572) **44칸**.
(지시서는 "약 40칸" 이라 했고 집계로 세니 44칸이었다.)

각 재료의 `attributes.core_doors_tried` 를 먼저 읽어 TB 가 훑은 표 아홉을 다시 열지 않았다.

## 산출물

| 파일 | 무엇 |
|---|---|
| `va01_almit_sac.json` | 값 12행 / 재료 2종(963·962). 적재 완료(거부 0) |
| `va03_linqalloy_sac125n.json` | 값 6행 / 재료 1종(965). 적재 완료(거부 0) |
| `va04_indium_directory.json` | 값 2행 / 재료 2종(585·963). 적재 완료(거부 0) |
| `va02_core_verdicts.json` | 판정 29칸 / 재료 6종(585·575·573·586·965·580). 적재 완료 |
| `va05_senju_sac107.json` | 값 2행 / 재료 1종(986). 적재 완료(거부 0) |
| `va06_core_verdicts_2.json` | 판정 8칸 / 재료 2종(986·572). 적재 완료 |
| `BRIEF_DRAFT.md` | 브리프 초안 |

## 결과 — `subsystem='packaging'` · `role='product'`

라이브 DB 에 다른 배치가 동시에 쓰고 있어 전체 스냅샷은 계속 움직였다. **내 몫만 떼어 세면 이렇다.**

| 단계 | 채운 칸 | V5 |
|---|---:|---:|
| va01 적재 직전 | 407 | 86 |
| va01 적재 직후 | **412** | **83** |
| va03·va04 적재 직전 | 413 | 41 |
| va03·va04 적재 직후 | **417** | **37** |
| va02 판정 직전 | 417 | 37 |
| va02 판정 직후 | 417 | **8** |
| va05 적재 직후 | 417 | 8 |
| va06 판정 직후 | 417 | **0** |

- **값으로 닫은 코어 칸 9** — 963(포아송비·CTE·열전도율·인장) 4 · 962(포아송비) 1 · 965(밀도·영률·인장) 3 · 585(영률) 1.
- **판정으로 닫은 칸 37** — V2 36 · V6 1. **§610 대조를 두 번 다 통과했다**:
  va02 선언 29 = 증가 29(V2 297→325 · V6 9→10 · V5 37→8) · va06 선언 8 = 증가 8(V2 325→333 · V5 8→0).
- **그 밖 넣은 비코어 값 10행** — 항복강도 1 · 연신율 2 · 융점 5 · 비커스경도 1 · 밀도(독립확인) 1.
- **표적 아홉 종의 44칸을 전부 닫았다. `subsystem='packaging'` 의 V5 가 0 이 됐다.**
  마지막 여덟은 986 SAC107 7칸(V2 — 千住가 파는 등급이나 물성 열이 없다)과
  572 SAC105 의 CTE 1칸(`core_no_public_document` — 문서가 특정됐는데 못 받는다)이다.

## 가장 큰 것 — 이미 DB 에 있던 출처의 옆 칸(§602)

**Almit(日本アルミット) `Difference Between Various Sn/Ag/Cu Solder Compositions`(2005-06-29)** 은 이미
출처 4658 로 DB 에 있었다. 앞 파동이 **비열 행 하나만** 가져가 재료 91·962·963 세 종에 3행을 넣었다.
그 문서의 p.13 `Chart 2. Mechanical Properties Test Results (n=3)` 는 **네 합금 × 열넷**을 찍는다 —
액상선·고상선·인장강도·항복점·연신율·가공경화계수·영률·**포아송비**·비중·비열·열전도율(25 C)·
'열전도율(60 C)'·'열전도율(100 C)'·CTE(20-60C / 20-100C).

시험시료는 `Sn-3.9Ag-0.6Cu (SAC396, iNEMI recommended)` · `Sn-3.5Ag-0.7Cu (SAC357)` ·
`Sn-3.0Ag-0.5Cu (SAC305, JEITA recommended)` · 기준 `63Sn-37Pb (Eutectic Solder)` 넷이다.

- **재료 963 SAC396** — 남은 V5 셋(CTE·열전도율·인장강도)이 전부 닫혔고, V2 로 판정돼 있던 포아송비도
  값으로 닫혔다. **코어 빈칸 4 → 0.**
- **재료 962 Sn63Pb37** — 마지막 빈칸이던 포아송비가 닫혔다. **1 → 0.**
- 그 밖 넣은 비코어 값 — 항복강도 31.3 MPa · 연신율 40.6% · 융점(고상선 217 / 액상선 218 C) · 영률 52 GPa(초음파) ·
  밀도 7.4(벤더 자기 측정, 기존 t3 편찬표값을 독립 확인).

## 이 표 한 장에서 나온 검산 셋

1. **이름이 틀린 행 둘을 항등식이 갈랐다.** `Thermal Conductivity (%) 60C` · `(%) 100C` 두 행의 값은
   열전도율이 아니라 **열팽창률(%)** 이다 — 같은 표의 CTE 행과 `CTE × ΔT` 로 **인쇄된 일곱 칸이 전부 재현된다**
   (21.4e-6×40 = 0.0856 대 0.085 · 21.5e-6×40 = 0.086 대 0.086 · 21.8e-6×80 = 0.1744 대 0.174 ·
   21.7e-6×80 = 0.1736 대 0.173 · 기준열 21.6e-6×40 = 0.0864 대 0.086 · ×80 = 0.1728 대 0.173).
   CTE 20-60C 가 `---` 인 SAC305 열은 60C 행도 `---` 다. 목차(p.6)가 평가항목을
   `5) Coefficient of Thermal Expansion / Thermal Expansion ratio` 로 적어 팽창률 행의 존재를 뒷받침한다.
   400 dpi 렌더로 행 머리글이 실제로 `Thermal Conductivity (%)` 임을 확인했다 — 추출 손상이 아니라 원문 오식이다.
2. **단위 `%` 가 오식인 열전도율 25 C 행은 기준합금 행이 척도를 고정한다.** 63Sn-37Pb 52.8 이
   The Solder Connection 2023 의 50 W/(m·K)와 5.6% 안이다. 상대비 해석(순 Cu 대비 → 245 · 순 Sn 대비 → 40.7)은
   기준열을 못 맞춘다. **W/(m·K)로 읽을 때만 닫히므로 그렇게 읽었다.**
3. **영률 52 GPa 는 혼합물 상한 위인데 기각하지 않았다.** Voigt 상한이 교과서 순물질값으로 51.3,
   편찬표 준정적값(순 Sn 42.1)으로 43.6 이다. **같은 표의 기준열 63Sn-37Pb 40 GPa 이 같은 편차를 재현한다**
   (교과서 Voigt 40.7 과 1.7% 안 · 편찬표 Voigt 35.5 보다 13% 위). 열이 초음파 동적 탄성률이라
   준정적값보다 계통적으로 13~19% 높다 — **두 행이 같은 방향·같은 크기로 어긋나는 것은 오식이 아니다.**
   기존 t1 영률 18.075 GPa(Zhang 2004, TMM 제하기울기)와는 `conditions.modulus_type` 으로 갈라 두었다.

## tier 를 2로 맞춘 이유(§612)

같은 표에서 온 앞 파동의 비열 행이 `tier 2 · measured` 다. 한 재료 안에서 같은 문서에서 온 칸들이
두 규약으로 갈리면 안 되므로 새 행도 전부 `tier 2 · measured` 로 맞췄다.

## 새로 연 문서

**값이 나온 것**
0. CAPLINQ `LINQALLOY SAC125N` — SAC125N Solder Spheres TDS v1.0
   — https://www.krayden.com/products/709/files/5859 (CapLinq 제품 페이지가 krayden.com 으로 301 이동했고 문서는 `/products/709/files/<id>` 에 있다.
   옛 `caplinq.com/index.php?option=com_filecabinet...` 링크는 404 이고 Wayback 에도 없다)
   ← **재료 965 의 밀도·영률·인장·연신·경도·고상선이 여기서 나왔다.** CTE·비열·포아송비 행은 없다
0b. 같은 제품의 `LINQALLOY SAC125N SDS`(Version 01) — https://www.krayden.com/products/709/files/5927
0c. Indium Corporation `SOLDER ALLOY DIRECTORY` Form 97720-A4-R9(2025-03, 16쪽)
   — https://web.archive.org/web/20260104191151id_/https://www.indium.com/wp-content/uploads/2025/03/Solder-Alloy-Directory-97720-A4-R9.pdf
   (현행 사이트에서 내려갔다) ← **재료 585 의 영률이 여기서 나왔다.** 2006 편찬표에 없던 저Ag SAC 행(258 SAC105 · 263 SAC0307 · 252 SAC396)이 새 판에 생겼다
1. Almit Ltd. `Difference Between Various Sn/Ag/Cu Solder Compositions`(2005-06-29, PowerPoint→PDF 14쪽)
   — https://www.almit.com/dloads/Agents/SAC%20Alloy%20Comparison.pdf ← **출처 4658(기존). `local_path`·`publisher` 를 이번에 채웠다(§626 규율 4)**

**열었으나 그 열이 없던 것(부재 확정)**
2. Alpha-Fry™ EGS SAC0107, SAC0307, SAC0807, SAC0100, SAC0300, SAC0800 TDS (SM1138-1, Rev. 07/30/2013)
   — alphaassembly.com Wayback `TDSEGS_SAC0107_SAC0307_SAC0100_SAC0300WWESM113802040114.pdf`. 조성 규격표뿐, 물성표 없음
3. AIM Solder `SAC0307 LEAD-FREE SOLDER ALLOY` TDS (Document Rev # NF1)
   — https://www.aimalloys.com/sites/default/files/tds_alloy_sac0307.pdf. 조성·융점 두 표뿐
4. Nathan Trotter `SAC 0307 Lead-Free Solder` TDS (2024-10)
   — https://nathantrotter.com/wp-content/uploads/2024/10/NT-SAC0307-Solder-Bar.pdf.
   `Physical Properties` 가 융점·밀도 0.265 lbs/in³·비중 7.33·경도 HV 14.1·**비열 0.17**·리플로/웨이브 온도뿐
5. DYFENCO/KNK `SAC0307-1688 (Sn/0.3Ag/0.7Cu)` 솔더와이어 TDS
   — https://knk.com.vn/wp-content/uploads/2022/01/TDS-SAC0307-1688-DY-E.pdf. `3.2 Physical Characteristic` 은 융점·비중 7.3 두 칸
6. CAPLINQ/Krayden `LINQALLOY SACQ` TDS v1.0 + SDS(Version 01, 인쇄 2024-05-02)
   — https://www.krayden.com/products/5503/files/3177 · `/5320`
7. CAPLINQ/Krayden `LINQALLOY SAC405` TDS + SDS — `/products/263/files/5858` · `/4728`(형제 등급 대조용)
8. CAPLINQ/Krayden `SAC125N | PbFree Solder Spheres` 제품 페이지(현행) 및 CapLinq 구판 Wayback — 조성·융점만
9. Indium Corporation `Master Solder Alloy Properties Table`(2004-03-04, 5쪽) — Indalloy 2006 편찬표와 **다른 판**.
   — https://ncsx.pppl.gov/NCSX_Engineering/ModCoil_TF-Coil_VVSA_Fab/Jobs1451_1459_1408/017-%20MC%20Joint%20Concerns/Indium%20alloy%20properties%20IndiumAmerica.pdf
   97.5Pb2.5Sn·SAC105·SAC107·SAC205 행 **없음**(가장 가까운 것은 Indalloy 171 = 95Pb5Sn, 165 = 97.5Pb1.5Ag1Sn)
10. iNEMI Pb-Free Alloy Characterization Project Report Part II (Sweatman, SMTAI 2012)
    — https://thor.inemi.org/webdownload/Pres/SMTAI_2012/Pb-Free_Alloy/LF1-3_Sweatman.pdf. 합금 15종을 싣되 **물성표가 없다**(특성수명뿐)
11. Ning-Cheng Lee `Low Cost High Reliability Solder Materials`(IEEE CPMT, 2017-02-23) — 물성표 없음
12. JEITA `Standardization Activity of 2nd Generation Lead-Free Solder Paste` — SAC107 의 고상선 217 / 액상선 224 C 와
    젖음시간만 인쇄. 코어 물성 없음
13. Osterman `Modeling Temperature Cycle Fatigue Life of Select SAC alloys`(CALCE, SMTAI 2018) — 기판·패키지 CTE 뿐
14. Electronics Cooling `Thermal Conductivity of Solders`(2006) — SAC 계열을 `approximately 60 W/mK` 라는 **계열 구간**으로만 쓴다(§616)

15. 千住金属工業(Senju Metal Industry, SMIC) `鉛フリーはんだ合金 一覧表 / List of Lead-free Solder Alloys`(2020-04-09 카탈로그, 7 MB)
    — https://www.senju.com/ja/download/pdf/2020_SMIC_FA_cata_0409.pdf
    ← **재료 986 SAC107 의 등급 존재를 확정한 문서다**: `M771 | Sn-1.0Ag-0.7Cu | 217 | 219 | 224 | BAR·CORE·BALL·PASTE·PREFORM`.
    **그러나 이 카탈로그는 물성 열이 하나도 없다**(전권에서 密度·比重·熱膨張·熱伝導·ヤング·ポアソン·引張 낱말이 사실상 0건).
    같은 표에 `M34 = Sn-1.0Ag-0.5Cu`(SAC105) · `M35 = Sn-0.3Ag-0.7Cu`(SAC0307) · `M40 = Sn-1.0Ag-0.7Cu-Bi-In`(딴 등급)도 있다
16. TOPLINE `BGA Solder Ball Alloys` — https://www.topline.tv/BGA_SolderBall.html.
    `Ref. | Composition | Solidus | Liquidus | Density gm/cc` 네 열뿐이고 CTE 열이 없다.
    SAC105 `Sn98.5 Ag1.0 Cu0.5 | 215 | 227 | 7.350` 은 있으나 **SAC107·SAC205 행이 없다**
17. INVACU `Properties of solder alloys` — https://invacu.com/solder-alloys.
    SAC105 행의 여섯 값이 The Solder Connection 2023 과 **글자 단위로 같아 같은 표의 재게재**다(§456) — 새 값 없음
18. Harima MULTiCORE `Solder Material Solutions` 브로슈어 — `SOLDER ALLOY PROPERTIES` 표(융점·밀도·비저항·열전도율).
    SAC0307·SAC305·SAC387 등은 있고 **SAC105·SAC107·SAC205 행이 없으며 CTE 열 자체가 없다**
19. Qualitek `SAC Solder Bar` TDS Rev. E 01/17 — `Coefficient of Thermal Expansion Pure Sn= 23.5` 로 **순 Sn 값만** 찍는다(등급값 아님)
20. Balver Zinn `SCAN-Ge 071` PDS(SnCu0.7Ag1.0NiGe) — Ag 1.0 / Cu 0.7 이지만 **Ni·Ge 도핑 등급**이라 SAC107 이 아니다. 융점·조성만
21. NIST `Database for Solder Properties with Emphasis on New Lead-free Solders` v4(140쪽)
    — https://www.metallurgy.nist.gov/solder/NIST_LeadfreeSolder_v4.pdf. CTE 표(Table 1.23~1.26 · 2.2.19)가 **근공정 SnAgCu 뿐**이고 저Ag 계열이 없다
22. EasySpheres SAC105 SDS(Version 2.4, 2023-04-22) — 9항이 융점·상대밀도를 포함해 **전 항목 `Not Available`**
23. Interflux `TD Lead-free alloys` · Canfield `SAC Alloys` · Kester 무연 바 솔더 페이지 · Shenmao 2019 카탈로그 · MG Chemicals TDS-4900 — SAC105/107/205 행 또는 물성 열 없음

**다시 연 기존 문서** — The Solder Connection 2023(출처 3641) · Indalloy 2006(출처 4753) ·
Kester Technical Data on Soft Solders · AIM Alloy Information(출처 4767) · Darveaux 1992(출처 3556) ·
Chen 2020(출처 3634) · Basit 2015(출처 3452) · Cai 2010(출처 4729) · Lall 2018(출처 3454) · Amagai 2002 · Coyle 2015 · Sun 2017(출처 4728)

받아 둔 사본은 `/home/koopark/claude/MaterialTwinWeb/.agent_work/w60va/` 에 있다.

## 결정과 이유

- **`SAC0107` 함정을 다시 확인했다**(§621). Solder Connection 표뿐 아니라 **ALPHA(Alpha-Fry) EGS 시트도**
  `SAC0107 (Sn99.2Ag0.1Cu0.7)` 로 앞 두 자리를 Ag 의 소수점 이하로 쓴다. 재료 986 SAC107 은 Ag 1.0 이라 딴 합금이다.
  Coyle 2015(iNEMI)의 합금표는 반대로 `Sn-1.0Ag-0.7Cu → SAC107` 로 **통용 약칭**을 쓴다 —
  **한 이름이 문서마다 다른 조성을 가리키므로 조성 열로만 골라야 한다.**
- **SAC-Q 는 등급이 안 닫힌다.** CAPLINQ/Krayden `LINQALLOY SACQ` TDS 의 조성은
  `Ag 3.90–4.10 / Cu 0.45–0.55 / Ni 0.04–0.06 / Bi 2.50–3.50` 이고 Lall 2018 TABLE 1 의 EDX 는
  `Sn 92.7 / Ag 3.4 / Cu 0.5 / Bi 3.4` 다(Ni 없음). **Ag 가 18% 다르다** — 붙이지 않았다(§22·586).
- **LINQALLOY SACQ TDS 의 `Young's Modulus 128.4 GPa` 는 기각했다**(V6). Voigt 상한 50.8 GPa 의 2.5배다.
  같은 벤더의 형제 등급 `LINQALLOY SAC405` TDS 가 같은 표 구성으로 `49 GPa` 를 찍어 **한 칸짜리 오식**임이 드러난다.
- **LINQALLOY 계열의 열전도율 열은 안 썼다.** SAC405 74 · SACQ 70.8 W/(m·K)인데 순 Sn(66.6)보다 높고
  The Solder Connection SAC405 62 · Almit 실측 SAC396 61.1 과 19% 어긋난다.
- **Nathan Trotter SAC0307 의 비열 `0.17` 은 넣지 않았다.** 58차 TB 가 ALPHA 두 판에서 같은 값을 기각한 그 값이다
  (Kopp-Neumann 229 J/(kg·K) 보다 26% 낮고, 같은 제조사 형제 등급이 0.214~0.236). **벤더가 셋으로 늘었을 뿐 독립 확인이 아니다.**
- **Amagai 2002 Table 1 은 안 썼다** — 캡션은 `... Sn3.5Ag0.75Cu and Sn1.0Ag0.5Cu` 인데 표의 넷째 열 머리글은
  `Sn2.0Ag0.5Cu` 다. 같은 논문의 Table 2·3 은 넷째를 `Sn1.0Ag0.5Cu` 로 쓴다 — **자기모순이라 양쪽을 다 버렸다**(§25).
- **Chen 2020 Table III 는 안 썼다** — `Elastic Material Properties used for FEA modeling` 이고 줄이
  Copper·Board·Mold·Die·Die attach·BGA sub 여섯이라 **솔더 줄이 아예 없다**(§3).
- **CAPLINQ LINQALLOY SAC125N 의 SDS 9항은 형제 제품에서 복제됐다.** SDS 는 `Melting Point 211-216 °C` 와
  `Specific Gravity 7.48` 을 찍는데 **그 둘이 같은 벤더의 LINQALLOY SACQ 값과 글자까지 같다**(SACQ TDS 융점 211/216 · SDS SG 7.48).
  같은 제품의 TDS 는 217/225 와 7.33 이다. **§601 은 SDS 9항이 TDS 에 없는 밀도를 찍는다고 했는데, 이것은 그 반대 사례다** —
  SDS 9항이 형제 제품에서 복제되면 자기 TDS 와 어긋난다. 밀도는 조성 혼합칙(7.324)이 TDS 쪽을 지지해 TDS 를 썼다.
- **SAC125Ni 의 액상선은 안 넣었다** — 같은 벤더가 세 값을 인쇄한다(TDS 225 · 제품 페이지 219 · ALPHA 스피어 TDS 228).
  벤더가 자기 문서 안에서 갈리므로 못 고른다(§25). 고상선 217 은 셋이 같아 넣었다.
- **LINQALLOY 계열 TDS 의 열전도율 열은 통째로 안 썼다** — SAC125N 67 · SAC405 74 · SACQ 70.8 W/(m·K)로
  **셋 다 순 Sn 의 66.6 보다 높다.** 희박 Sn 합금이 순 Sn 보다 열전도율이 높을 수 없다. 같은 표의 비저항 13 µΩ·cm 에
  Wiedemann-Franz 를 넣으면 55.9(순 Sn 의 WF 오차 보정해도 58.7)이라 14% 어긋난다. 재료 965 의 이 칸은 V6 로 냈다.
- **LINQALLOY 표의 비저항 열은 복제됐다** — SACQ 13.0 · SAC405 13 · SAC125N 13 으로 세 등급이 같다. 안 넣었다.
- **Indium `Solder Alloy Directory` R9(2025)는 2006 편찬표와 다른 문서다.** 2006 판에 없던 저Ag SAC 행이 새로 생겼다
  (258 = 98.5Sn/1Ag/0.5Cu · 263 = 99Sn/0.3Ag/0.7Cu · 268 = 98.5Sn/0.5Ag/1Cu). **§615 의 반대 방향** —
  신판이 구판보다 적게 찍는 것이 보통인데 이 계열은 새 등급이 생기면서 행이 늘었다.
  열 배정은 §606 대로 `-bbox-layout` x좌표로 했다(영률 x=519 · 전단 x=481 · 인장 x=448 · CTE x=419 ·
  열전도율@20C x=386 · 열전도율@85C x=353 · %IACS x=317 · 전기전도율 x=279 · 밀도 x=245).
- **R9 영률 열의 두 칸은 기각했다** — 258행 SAC105 `2.1`(14.5 GPa) · 246행 SAC405 `2.6`(17.9 GPa).
  같은 열의 이웃 행이 전부 4.8~7.7(33~53 GPa)이고 순 Sn 행이 6.1(42.1 GPa, 교과서값)이라 세 배 낮다.
  **두 재료 다 영률 칸이 이미 차 있어 표적이 아니므로 판정을 박지 않았다** — 다음 파동을 위해 여기와 va04 notes 에 적어 둔다.
- **R9 의 SAC105 열전도율 0.43 W/(cm·°C) = 43 W/(m·K)는 안 넣었다** — 재료 572 의 이 칸은 이미
  The Solder Connection 2023 의 60 W/(m·K)로 차 있고 둘이 28% 갈린다. 닫지 못했으므로 정정하지 않고 신고만 한다.
- **R9 의 SAC0307 인장 6882 psi = 47.4 MPa 도 안 넣었다** — 재료 585 의 이 칸은 The Solder Connection 의
  300 kgf/cm² = 29.42 MPa 로 차 있고 ALPHA Vaculoy SACX0307 29.5 와 맞는다. **세 값이 29.4 / ~40(Kapp 물결표) / 47.4 로
  갈리는데 닫지 못했다** — 신고만 한다.
- **986 SAC107 은 상용 등급이다 — 그런데 파는 벤더가 물성을 안 찍는다.** 千住金属 카탈로그의 `M771` 이
  이 조성을 바·와이어·볼·페이스트·프리폼 다섯 형태로 판다고 인쇄한다. 58차 TB 가 '아홉 표 전부에 행 없음' 으로
  넘긴 전제는 맞았으나 **결론("상용 등급이 아닐 수 있다")은 틀렸다.** 그래도 코어 일곱은 V2 다 —
  물성 열이 있는 표 스물한 장 전부에 이 조성의 행이 없다. **남은 문은 논문이다.**
- **572 SAC105 의 CTE 는 `core_no_public_document` 로 냈다**(V2 로 세어진다). 문이 하나로 특정됐고
  형제 시트가 그 열의 존재를 증명하는데(SAC300~405 TB 의 `TCE (Range 20 to 100 ºC)`) 파일을 못 받는다 —
  403 여섯 조합 · Wayback 캡처 0 · 유통사 미러 넷 0. **"벤더가 안 찍는다" 가 아니므로 V2 사유를 쓰면 거짓이 된다.**
- **아무것도 지우지 않았다.**

## 신고 — 손대지 않은 것

1. **`verdicts_check.py` 가 새 어긋남 1건을 낸다** — `재료 582 core_rejected_printed_value 가
   mechanical.tensile_strength 를 선언했는데 t2 값이 있다`. 58차 TB 마감 시점의 신고는 재료 229 하나였다.
   내가 만든 것이 아니다(내 작업 시작 시점 스냅샷에 이미 582 의 인장 칸이 차 있었다). 같은 라이브 DB 에
   동시에 쓰는 다른 배치의 결과로 보인다. **신고만 한다**(§565).
2. **58차 TB 의 신고 1(빈칸 갈래 "값이 형제 키에 있다")은 그대로다.** 이번에도 573·575·586 세 종에서
   같은 모양을 만났고, 집계가 `_at_rate` 를 안 보므로 §608 의 57차 SA 선례대로
   전파되는 `core_absent_from_vendor_sheet` 에 적고 사유에 성격을 못박았다. 공유 도구는 고치지 않았다(§468).
3. **57차 SA 가 신고한 V4 전파 문제(`identification_status`·`anonymised_code` 가 병합기 `CURATION_KEYS` 밖)도 그대로다.**
   재료 575 가 정확히 그 자리라 같은 우회로를 썼다.

## 다음 표적 — 솔더 갈래에 남은 것

`subsystem='packaging'` 의 V5 는 0 이다. **표적은 판정 밖에 있다.**

| 재료 | 무엇이 남았나 | 다음 문 |
|---|---|---|
| **572 SAC105** | CTE 한 칸. `core_no_public_document` 로 세었으나 **다시 조달할 가치가 가장 큰 자리다** | `https://www.macdermidalpha.com/sites/default/files/2021-11/ALPHA-VACULOY-SAC-100,-105-Solid-Solder-EN-24Sep20-TB.pdf` 한 장. 유통사·대리점 사본이 유일한 길이다(hisco·hilpert·ams-electronics·gluespec 넷은 이미 확인) |
| **986 SAC107** | 코어 일곱 전부. 벤더 스물한 문이 닫혔다 | **논문뿐이다.** 이 조성을 기준시편으로 쓰는 나노입자 첨가 연구(SnO2·SiC·Fe2O3·MWCNT·TiO2·ZrO2)가 여럿인데 코퍼스에 있는 Sun 2017·Xiong 2018 은 DSC·IMC 만 싣는다. Gu(Fe2O3) · El-Daly(SiC) 계열 원논문 조달이 다음 자리다 |
| 573 SAC205 · 586 SAC(307)-2In | 코어 여섯씩 | 벤더가 아니라 논문. 573 은 컨소시엄 평가 합금(초안 13 의 ③), 586 은 논문 개발합금(④) |
| 575 SAC-Q | 코어 여섯 | **등급을 먼저 닫아라.** Lall 2018 EDX(Ag 3.4/Bi 3.4)와 CAPLINQ LINQALLOY SACQ(Ag 4.0/Bi 3.0/Ni 0.05)가 다르다. ALPHA CYCLOMAX 원 TDS 나 Witkin 2013(Sn-3.4Ag-1.0Cu-3.3Bi)이 남은 문이다 |
| 580 97.5Pb2.5Sn | 코어 여섯 | 벤더 목록·표준 열여덟이 닫혔다. 1990년대 플립칩 시험합금이라 **Darveaux 계열 원논문의 부록**이 유일하게 남은 자리다 |
| 585 SAC0307 | CTE·열전도율·비열 | 등급 전용 TDS 넉 장이 안 찍는다. Indium R9 도 그 두 열이 비어 있다 |
| 965 SAC125Ni | CTE·비열·포아송비 | LINQALLOY TDS·SDS·ALPHA 스피어 TDS 가 안 찍는다 |

### 다음 파동에 바로 쓸 수 있는 것

- **§602 를 표적 선정에 먼저 걸어라.** 이 배치가 닫은 코어 아홉 칸 중 다섯이 **이미 DB 에 있던 출처 한 장**에서 나왔다.
  새로 연 문 열셋에서 나온 코어 칸은 넷이다.
- **Almit 시험보고서(출처 4658)에는 아직 안 가져온 열이 남아 있다** — `Sn-3.5Ag-0.7Cu`(SAC357) 열 전체다.
  카탈로그에 이 조성의 일반 등급 레코드가 없고 재료 1679~1681(IDEALS project, Harrison 2001)은
  **특정 연구과제의 용해물**이라 옮기면 §123·140·623 위반이다. **일반 SAC357 재료를 새로 세울지가 먼저 결정할 일이다.**
- **CAPLINQ/Krayden `/products/<id>/files/<id>` 는 새로 열린 문서 창고다.** 솔더 스피어 라인 전체
  (`linq-sac105` · `linq-sac305` · `linq-sac405` · `linq-sacq` · `linq-sac125n` · `linqalloy-sp-*`)에 TDS·SDS 가 붙어 있고
  **caplinq.com 쪽 링크는 404 이며 Wayback 에도 없다.** krayden.com 으로만 받힌다.
