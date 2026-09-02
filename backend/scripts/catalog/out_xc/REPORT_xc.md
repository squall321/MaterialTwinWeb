<!-- 62차 XC — 열물성 쌍(비열·열전도율)의 1차 파동 t4 118칸 표적 처리 결과 -->

# 62차 XC — 아직 어떤 문서와도 대조된 적 없던 열물성 118칸

기준 — 2026-09-02 · 라이브 DB(`MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web`).
**병렬 배치가 같은 DB 를 친다**(브리프 640) — 아래 수치는 전부 이 배치가 손댄 목록 기준이다.
스냅샷은 `VACUUM INTO` 로 떴다(브리프 647).

## 1. 표적의 이동

| | 61차 WD 감사 | 62차 XC 시작 | 62차 XC 마감 |
|---|---:|---:|---:|
| t4 단독 대표 칸 | 272 → 267 | 267 | **259** |
| 그중 1차 파동 문구만 단 칸 | **118** | 115 | **107** |
| 그 107 중 **이번에 문서를 열어 부재를 확정한 칸** | — | — | **62** |
| **아직 어떤 문서와도 대조 안 된 칸** | 118 | 115 | **45** |

- 값으로 닫은 **8칸**(재료 6종) · 부재로 확정한 **62칸**(재료 43종) = **70칸**을 문서에 대 봤다.
- **선언 62칸 = DB 확인 62칸**, **값 선언 8행 = DB 확인 8행**(브리프 610 의 대조).

## 2. 넣은 값 여덟 — 전부 이미 인용된 문서 안에 있었다(새 문서 조달 0)

| 재료 | 칸 | 값 | tier | 문서 · 위치 | 종전 t4 |
|---|---|---:|---|---|---:|
| 62 Thermal Pad Silicone Soft 1.5 W/mK | 비열 | 1000 J/(kg·K) | t3 | Bergquist GAP PAD TGP 1500 TDS `Heat Capacity, ASTM E1269, J/g-K 1.0` | 1100 |
| 63 Thermal Pad Silicone Medium 3.0 W/mK | 비열 | 1000 | t1 | Bergquist GAP PAD TGP 3000 TDS 같은 블록 | 1000 |
| 86 IGZO Oxide Semiconductor | 비열 | 426 | t3 | Nanomaterials 11(6) 1547 본문 재인용 `[32,37]` | 400 |
| 191 NiCr Thin-Film Resistor | 비열 | 460 @20 °C | t3 | Kanthal Nikrothal 80/20 Cb `Specific heat capacity` 12점 표 | 450 |
| 191 NiCr Thin-Film Resistor | 열전도율 | 15 @20 °C | t3 | 같은 시트 `Thermal conductivity` 12점 표 | 12 |
| 192 MLCC Termination (Cu/Ni/Sn) | 비열 | 385 @20 °C | t3 | Kanthal C11000 ETP `Specific heat capacity` | 385 |
| 192 MLCC Termination (Cu/Ni/Sn) | 열전도율 | 388 @100 °C | t3 | 같은 시트 `Thermal conductivity` | 200 |
| 155 Ultra-Thin Glass (UTG) | 열전도율 | 1.0 @90 °C | t3 | SCHOTT 박판유리 브로슈어 각주 `approx. 1 W/(m·K) for all glass types` | 1.0 |

**t4 는 한 줄도 지우지 않았다.** 온도 조건이 없는 자리는 전부 `temperature_note` 에 *원문 미인쇄* 와 그 근거를 적었다.

### 2.1 항등식 검산 `k = alpha·rho·Cp` — 값을 만드는 데 쓰지 않았다

| 재료 | 세 값의 출처 | alpha 계산 | 판정 |
|---|---|---:|---|
| 192 MLCC 단자 | **셋 다 같은 C11000 시트** | 388/(8890×385) = **1.134e-4 m²/s** | 순동 교과서값 1.11e-4 와 **2% 안**. 자기무결성 검사(브리프 603) |
| 191 NiCr | **셋 다 같은 Nikrothal 시트** | 15/(8300×460) = **3.93e-6** | Ni-Cr 합금 통용대역 3~4e-6 안 |
| 62 Thermal Pad Soft | 셋 다 같은 TGP 1500 시트 | 1.5/(2100×1000) = **7.14e-7** | 충전 실리콘 TIM 대역 5e-7~1e-6 |
| 63 Thermal Pad Medium | 셋 다 같은 TGP 3000 시트 | 3.0/(3200×1000) = **9.38e-7** | 같은 대역. k 가 2배인데 rho·Cp 는 1.5배라 62 와 정합 |
| 86 IGZO | rho·Cp 는 재인용, k 는 같은 논문 실측 | 1.65/(5860×426) = **6.61e-7** | 비정질 산화물 박막 대역 |

**역산은 없다.** 86 IGZO 는 저자가 k 를 열반사로 직접 재고 Cp 를 포논기체모형 `k=(1/3)Cv·v·l` 의 **입력**으로 인용했다 —
인과 방향이 Cp → 모형이지 k → Cp 가 아니다(61차 WD 가 세운 경계 안쪽).

**단위 병기열 자기검산도 넷 걸었다.** Kanthal 은 SI 옆에 영미 단위를 같이 찍는다 —
0.46 kJ/(kg·K)→0.11 Btu/(lb·°F) ✔ · 15 W/(m·K)→8.7 Btu/(h·ft·°F) ✔ ·
0.385→0.09 ✔ · 388→224 ✔. 네 쌍 다 맞아 열 배정과 단위 환산이 동시에 닫힌다.

## 3. 부재를 확정한 62칸(재료 43종) — 벤더 시트 약 160장을 열었다

전부 `attributes.core_absent_from_vendor_sheet` 에 `{물성키: 사유}` 로 박았고, **사유마다 연 문서를 전부 이름으로 적었다**(브리프 627③).

가장 큰 표본 넷.

- **93 Underfill Epoxy(비열)** — 언더필 TDS **15장**(Henkel LOCTITE ECCOBOND 9 · NAMICS 2 · Panacol · Shin-Etsu SMC · Hysol GR920). **15장 전부 열전도율은 찍고 비열 0건.**
- **144 Conductive Silver Epoxy(비열)** — 은 충전 다이어태치 TDS **25장**(LOCTITE ABLESTIK 18 · EPO-TEK H20E 계열 3 · Panacol · NAMICS). **25장 전부 같은 모양.**
- **175 Die Attach Film(비열)** — DAF TDS **11장**(Resonac FH/HR · Henkel CDF/ATB · AI Technology). 같은 모양.
- **177 Low-Loss PCB Laminate(비열)** — Panasonic MEGTRON 4장 + Isola 2장. **Panasonic 은 UA 를 빼야 200 을 준다**(브리프 634) — UA 를 붙인 채 침묵을 부재로 읽었으면 여섯 장을 통째로 못 열 뻔했다.

나머지 39종 — 42~46 3M OCA 5종 · 47 467MP · 51/52 VHB · 53 PE 폼 · 54/65/66 PORON · 55 tesa 76565 ·
57 3M 8805 계열 · 58 실리콘 가스켓 · 60/61 Sorbothane · 67 ISODAMP C-1002 · 69 NBR · 70 3M 112 시리즈 ·
74 OKP · 82 FINEMET · 94/98/121 적층판·프리프레그 · 117/118/186 Ossila 유기반도체 · 119 EMI 차폐 ·
139 Teflon AF/OPTOOL · 140 LOCA · 145 Taiyo PSR-4000 · 153 GORE ePTFE · 154 EMI 패브릭 가스켓 ·
158 OSP · 160 HD MicroSystems PBO · 169 LDS PC · 180 LiTaO3 · 187 NCA.

**연 범위는 그 N장이지 그 벤더/그 군 전체가 아니다** — 사유 문장마다 그 한 줄을 박았다(브리프 627).

### 3.1 방향이 한쪽으로만 갈린다

이번 표본에서 **`열전도율은 찍고 비열은 안 찍는` 서식은 흔한데(언더필·다이어태치·DAF·PORON·적층판·VHB 통합 TDS),
반대(비열은 찍고 열전도율은 안 찍는) 서식은 하나도 없었다** — 61차 WD 가 찾은 SCHOTT AS 87 eco 한 장이 유일한 반례로 남는다.
**`Cp` 가 없다고 `k` 도 없다고 넘기면 찍혀 있는 열을 안 열게 된다.**

### 3.2 애그리게이터만 숫자를 찍은 세 자리 — 전부 넣지 않았다

- **94 FR4 · 121 CCL** — Anhui Hongxin 편찬 페이지가 `Specific heat capacity: approximately 1.0–1.1 J/(g·K)`. **구간 + `approximately`**(브리프 616). 벤더 시트 7장은 0건이다.
- **115 Microlens Resin** — Tangram `Plastics Data File - PMMA` 가 `Specific Heat 1.25 - 1.7 kJ/kg/°C`. **36% 폭 구간**이고 협회 자료파일이라 부재 판정도 안 박았다.
- **85 PEN Film** — lookpolymers 재편찬만 있어 61차 WD 대로 **부재를 선언하지 않았다.**

## 4. 61차 WD 신고 넷 — 확인 결과(고치지 않았다)

1. **재료 156·182 λ 행의 `"temperature": "20 degC"`** — **확인.** pv5543(156, N-LASF9 0.79) · pv5555(156, N-SF57 0.99) · pv5579(182, P-SK57 1.01) 셋이다.
   **보강 증거** — 같은 배치가 같은 파동에서 넣은 **OHARA 행 둘(pv5567 · pv5591)에는 이 키가 아예 없다**(`detail: "OHARA S-LAH79, k"`). 한 배치 안에서 규약이 갈렸다.
   **확대 발견** — 구식 문자열 키 `conditions.temperature` 를 쓰는 행이 **DB 전체에 2,255행**이고 값이 `ambient`·`room temperature`·`RT`·`298.15`·`300`·`300 K`·`20 degC` 로 제각각이다. 52차 NA 의 `temperature_c` 정규화가 이 키를 안 봤다. **신고만 한다.**
2. **출처 3384 의 제목** — **확인, 그리고 제3자로 독립 확인했다.** Crossref `10.1038/srep38595` 가 돌려주는 것은
   제목 `Tailoring thermal conductivity via three-dimensional porous alumina` · 제1저자 `Abad` · 2016 · Scientific Reports 다.
   DB 제목은 `Rodriguez et al., 'Thermal conductivity of 3D ordered anodic aluminium oxide membranes'` 이고 **`authors`·`year` 컬럼이 둘 다 NULL** 이다. DOI 만 맞다.
3. **재료 270 의 두 편찬표** — **확인.** `thermal.conductivity` pv7076 = 0.28(AZoM/Granta, notes 에 `Original range 0.28-0.30`) ·
   `thermal.specific_heat` pv7075 = 1650(같은 표, `Original range 1650-1700`). 둘 다 **구간의 하한을 취한 t4** 다.
   같은 재료 인장강도 행(pv20887)의 notes 가 matmake 폴리우레탄 표를 인용하는데 그 표는 0.21 / 1800 을 찍는다 — **k 는 33% 갈린다.**
   **어느 칸에도 갈린다는 사실이 없다.** 덧붙여 **두 t4 자체가 §616 의 구간값**이다.
4. **재료 85 PEN Film** — **확인.** 출처 265·266 의 URL 이 `lookpolymers.com/...` 다(MatWeb 계열 재편찬). WD 가 부재를 선언하지 않은 것이 옳다.
   **DuPont Teijin 원본 TDS 조달은 실패했다** — 막힌 문의 네 항목은 `BRIEF_DRAFT.md` 마지막 절에 적었다.

## 5. 남은 것

- **45칸**이 여전히 어떤 문서와도 대조된 적이 없다. 그 대부분은 **벤더가 특정되지 않은 제네릭 클래스**(예: 87 CPI · 89 ITO · 95 ABF · 106 BaTiO3 · 126 EUV 레지스트 · 127 HfO2 · 142 QDEF · 143 ACF · 162 RuO2 · 163 NTC · 164 ZnO 바리스터 · 181 ScAlN · 184 LTPS · 190 분말코어 · 193 CCAW · 198 프리프레그 · 203 EMI 필름 · 204 PSR)이고, **논문 축으로 가야 열린다.**
- **127 HfO2** — Panzer 2009(이 재료 열전도율의 출처)는 본문 verbatim *"The HfO2 heat capacity and other required thermal properties were taken from the literature [19]."* 라고만 적고 값을 안 찍는다. **[19] 를 여는 것이 이 칸의 다음 한 걸음이다.**
- **181 ScAlN** — 이 재료 열전도율의 출처(arXiv 2102 AlScN TDTR)는 체적열용량 `C` 를 식에만 쓰고 인쇄값이 없다.
- **93 Underfill** — Abbasi 2017 이 Hot Disk 로 비열을 쟀다고 초록이 밝히지만 **인쇄값이 없고 Fig.11 에만 있다**(앞 배치가 이미 규칙 3 으로 기각했고 그 판정이 열전도율 행 notes 에 적혀 있다). 그림 판독 파동의 표적이다.
- **191 NiCr** — 넣은 것은 **벌크 Ni80Cr20** 값이다. 박막 열전도율은 경계산란으로 낮아질 수 있으므로 **3-omega·TDTR 로 NiCr 박막을 잰 논문**이 이 칸의 진짜 표적이다(조건의 `grade_scope` 에 그렇게 적었다).

## 6. 검사

- `integrity_check.py` — **신규 위반 0.** 배치 전후 출력 diff 가 `물성값 42122 → 42130` 한 줄뿐이다(+8 = 이 배치가 넣은 행 수와 정확히 일치).
- `verdicts_check.py` — **이상 0개.** 신고 1건(재료 582)은 이 배치 것이 아니다.
- `pytest -q` — **366 passed, 1 skipped**(기준선 그대로).
