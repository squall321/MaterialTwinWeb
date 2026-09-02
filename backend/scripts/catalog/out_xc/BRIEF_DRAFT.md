<!-- 62차 XC 교훈 초안 — 절 번호는 조정자가 붙인다(브리프 496·504) -->

## ___. **1차 파동의 t4 가 옳은 값을 옳은 근거 없이 부어 놓았을 수 있다 — 그래서 '값이 안 바뀐 채움' 이 진짜 성과다**

62차 XC 가 61차 WD 의 표적 118칸(재조회 시점 115칸)을 쳤다. 여덟 칸을 인쇄값으로 닫았는데
**여덟 중 셋은 숫자가 종전 t4 와 사실상 같았다.**

| 재료 | 칸 | 종전 t4(근거 문구뿐) | 이번 인쇄값 | 차이 |
|---|---|---:|---:|---|
| 192 MLCC Termination | 비열 | 385 (ASM Metals Handbook) | **385** (Kanthal C11000 ETP 시트) | **0%** |
| 155 UTG | 열전도율 | 1.0 (ASM Ceramics Handbook) | **1.0 @90 °C** (SCHOTT 박판유리 브로슈어) | **0%** |
| 191 NiCr 박막저항 | 비열 | 450 (ASM Metals Handbook) | **460 @20 °C** (Kanthal Nikrothal 80/20 Cb) | −2.2% |

**값이 안 바뀌었으니 성과가 없다고 읽으면 안 된다.** 바뀐 것은 넷이다 — **출처가 표를 특정하고**,
**온도 조건이 생기고**, **단위 병기열로 자기검산이 서고**, **다음 파동이 같은 칸을 표적으로 다시 세지 않는다.**
반대로 재료 192 의 열전도율은 t4 200 대 인쇄값 388 로 **두 배 가까이 갈렸는데**, 갈린 이유가 §475 다 —
t4 는 Cu/Ni/Sn **3층 적층**을 어림한 값이고 인쇄값은 **Cu 하지전극 층**의 값이다. 둘 다 살려 두고 조건에 그 차이를 적었다.

**규율 — 근거 없는 t4 를 교체할 때 성과 지표는 값의 변화량이 아니라 "그 칸이 이제 어느 표를 가리키는가" 다.**
값이 같아도 채운 것이고, 값이 갈리면 **왜 갈리는지가 새 정보**다.

---

## ___. **§602 는 열물성에서 배가된다 — 밀도를 캐 간 시트가 비열·열전도율을 같은 블록에 찍는다**

62차 XC 가 닫은 여덟 칸 중 **일곱 칸이 그 재료가 이미 값을 받고 있는 시트 안에 있었다.** 새 문서 조달 0 이다.

| 재료 | 앞 배치가 그 시트에서 가져간 것 | 남기고 간 것 |
|---|---|---|
| 191 NiCr | Nikrothal 80/20 Cb 시트에서 밀도·체적저항률·전기전도율·인장강도 **4행** | 같은 시트의 **비열 12점 표 · 열전도율 12점 표 전체** |
| 192 MLCC 단자 | C11000 ETP 시트에서 밀도·전기전도율·체적저항률 **3행** | 같은 시트의 **비열 1행 · 열전도율 1행** |
| 62 Thermal Pad Soft | GAP PAD TGP 1500 TDS 에서 밀도·열전도율·최고사용온도·유전율·열저항 **5행** | 같은 `Physical Properties` 블록의 **`Heat Capacity, ASTM E1269, J/g-K 1.0`** |
| 63 Thermal Pad Medium | GAP PAD TGP 3000 TDS 에서 열전도율·밀도·최고사용온도 **3행** | 같은 블록의 **Heat Capacity** |
| 86 IGZO | 논문에서 열전도율 1.65 **1행** | 같은 본문의 **비열 426 J/(kg·K)**(재인용) |

**왜 하필 열물성인가.** `k = alpha·rho·Cp` 때문에 벤더도 논문도 이 넷을 **한 표·한 블록에** 인쇄한다.
그런데 파동은 물성 키 하나를 표적으로 잡고 가므로(브리프 649) **한 블록에서 한 행만 뜯어 온다.**
밀도를 캔 배치는 밀도 파동이었고, 열전도율을 캔 배치는 열전도율 파동이었다.

**규율 — 열물성 빈칸의 첫 질의는 코퍼스 검색이 아니라 이것이다.**
```sql
select distinct s.id, s.title from property_value pv join source s on s.id = pv.source_id
 where pv.material_id = ? and pv.property_key like 'thermal.%' or pv.property_key = 'physical.density';
```
**밀도 행의 출처가 열물성 빈칸의 1순위 표적이다** — `k = alpha·rho·Cp` 를 인쇄하는 표는 rho 도 같이 찍는다.

---

## ___. **부재는 벤더가 아니라 서식이 정하고, 열물성에서는 그 경계가 '열전도율은 찍고 비열은 안 찍는다' 로 거의 항상 같은 방향이다**

62차 XC 가 벤더 데이터시트 **약 160장**을 열어 43종 62칸의 부재를 확정했다.
**한 방향의 비대칭이 서식군을 가로질러 반복된다.**

| 서식군 | 연 장수 | 열전도율 | 비열 |
|---|---:|---|---|
| 언더필 TDS(Henkel ECCOBOND · NAMICS · Panacol · Shin-Etsu SMC · Hysol) | 15 | **찍는다** | **0건** |
| 은 충전 다이어태치 TDS(LOCTITE ABLESTIK · EPO-TEK · Panacol · NAMICS) | 25 | **찍는다** | **0건** |
| 다이어태치 필름 TDS(Resonac · Henkel CDF/ATB · AI Technology) | 11 | **찍는다** | **0건** |
| Rogers PORON 미세발포 PU 시트 | 6 | **찍는다**(ASTM C518) | **0건** |
| 3M VHB / 전사테이프 TDS | 9 | 통합 TDS 가 찍는다 | **0건** |
| Isola/Shengyi/Panasonic 적층판 시트 | 9 | **찍는다** | **0건** |
| Ossila 유기반도체 공급자 시트 | 6 | 0건 | **0건** |
| 3M OCA / LOCA / 감쇠재 / 가스켓 / ePTFE 벤트 / EMI 가스켓 / OSP | 30+ | 0건 | **0건** |

**둘이 함께 없는 서식은 흔하고, 비열만 없는 서식도 흔한데, 열전도율만 없고 비열은 있는 서식은 이번 표본에 하나도 없었다**
(61차 WD 가 찾은 SCHOTT AS 87 eco 한 장이 유일한 반례다).
이유는 용도다 — **열전도율은 카탈로그 선택 파라미터이고 비열은 해석 입력이다.** 벤더는 파는 데 쓰는 숫자를 찍는다.

**규율 — 열물성 부재를 예측할 때 `k` 와 `Cp` 를 대칭으로 보지 마라.** `k` 가 있는 서식에서 `Cp` 를 기대하는 것은
근거가 있지만(같은 블록이다), `Cp` 가 없다고 `k` 도 없다고 넘기면 **찍혀 있는 열을 안 열게 된다.**

---

## ___. **판정은 서식 단위라 같은 벤더의 다른 서식이 그 판정을 뒤집을 수 있다 — 그리고 뒤집는 쪽도 '연 문서의 범위' 를 적어야 한다**(§627·653 의 짝)

61차 WD 가 재료 155(UTG)의 열전도율에 `core_absent_from_vendor_sheet` 를 박았다 —
*"SCHOTT AS 87 eco 시트와 PGO 제품 페이지 두 장을 열어 확인했다. `Thermal Properties` 블록은 CTE·비열·Tg·점도 넷뿐이고 열전도율 행이 없다."*
**그 판정은 지금도 참이다.** 그런데 같은 벤더의 **다른 서식**이 그 행을 찍는다.

> SCHOTT `Main properties of SCHOTT glass`(박판유리 브로슈어, ENGLISH 07/2026) 각주 verbatim —
> *"The thermal conductivity λ at ϑ = 90 °C is approx. 1 W/(m · K) **for all glass types**."*
> 그 브로슈어의 표에 **AS 87 neo** 행이 있고, 그 행의 CTE 8.7 · Tg 621 · rho 2.46 · E 73.3 · nD 1.5040 이
> 우리 DB 의 **AS 87 eco** t1 다섯 행과 한 자리도 안 틀리고 같다.

- **판정이 틀린 것이 아니라 범위가 좁았던 것이다.** WD 는 §627③ 대로 연 문서를 사유에 적어 두었고, 그래서
  이 배치가 **무엇이 아직 안 열렸는지**를 알 수 있었다. 사유에 "SCHOTT 는 안 찍는다" 라고만 적혀 있었으면 안 열었다.
- **뒤집는 쪽도 범위를 적어야 한다.** 같은 문장을 재료 137(SCHOTT BG60/BG61 필터유리)에는 **쓰지 않았다** —
  `for all glass types` 의 목록은 박판유리 아홉 종이고 필터유리는 거기 없다. 넓히면 §627 이 경고한 확대해석이다.
- 숫자 다섯 개가 일치해도 **eco 와 neo 의 동일성은 단정하지 않았다**(브리프 632). t3 로 두고 조건에 그 사실을 적었다.

**규율 — 부재 판정을 닫을 때는 지우지 말고 옆에 값을 넣되, 그 값의 조건에 "앞 판정은 어느 서식에 대해 참인가" 를 적어라.**
그러면 두 문장이 서로를 죽이지 않고 **서식 지도**가 된다.

---

## ___. **애그리게이터가 유일하게 숫자를 찍은 칸은 채움이 아니라 두 번째 부재다**(§616 의 열물성판)

62차 XC 가 연 문서 중 **숫자를 찍은 것이 편찬 페이지뿐인 칸**이 셋 있었고 **셋 다 넣지 않았다.**

| 재료 | 편찬 페이지가 찍은 것 | 왜 안 넣었나 |
|---|---|---|
| 94 FR4 · 121 CCL | Anhui Hongxin `FR4 PCB Material` 페이지 — `Specific heat capacity: approximately 1.0–1.1 J/(g·K)` | **구간 + `approximately`.** 같은 재료의 벤더 시트 일곱 장(Shengyi·Isola×3·Panasonic·Chang Chun)은 전부 0건이다 |
| 115 Microlens Resin | Tangram `Plastics Data File - PMMA` — `Specific Heat 1.25 - 1.7 kJ/kg/°C` | 구간이 **36% 폭**이다. 협회 자료파일이지 벤더 시트가 아니다 |
| 85 PEN Film | lookpolymers Teonex Q51/Q83 페이지 | **재편찬 페이지다**(61차 WD 가 이미 짚었다) — 원 TDS 를 못 열었으므로 부재도 선언 못 한다 |

**세 자리가 서로 다르다.** ①은 구간이라 값이 아니고(§616), ②는 구간에 더해 문서 종류가 벤더가 아니고,
③은 숫자가 아예 없는데 **문서 종류 때문에 부재 선언도 막힌다**(§630).
**애그리게이터를 만났을 때 물어야 하는 것은 "쓸 수 있나" 가 아니라 "이 자리는 셋 중 어디인가" 다** — 답이 다르면 다음 파동의 행동이 다르다.

---

## ___. **막힌 문 — DuPont Teijin Teonex 원본 TDS**(§648 의 서식대로)

61차 WD 가 재료 85 `PEN Film (Diaphragm)` 의 열전도율을 두고 *"DuPont Teijin 자사 Teonex TDS 원본을 열어야 확정된다"* 로 넘겼다. 열지 못했다.

- **(a) 정확한 대상** — DB 출처 265·266 은 제목이 `DuPont Teijin Films Teonex Q51/Q83 ... Datasheet` 인데
  **URL 이 `lookpolymers.com/polymer_DuPont-Teijin-Films-Teonex-Q51-Polyester-Film-48-Gauge.php`** 다(MatWeb 계열 재편찬).
  원본은 `dupontteijinfilms.com/FilmEnterprise/Datasheet.asp?ID=<n>&Version=US` 서식이다(Wayback CDX 로 확인).
- **(b) 시도한 조합** — `dupontteijinfilms.com/wp-content/uploads/...` 404(UA 유무 둘 다) ·
  `teijinfilmsolutions.com` · `teijinfilm.com` 연결 타임아웃(30 s, UA 유무 둘 다) ·
  `europe.dupontteijinfilms.com/media/2276/dtf_teonex__hv_brochure_2014.pdf` 404.
- **(c) 같은 폴더의 대조군** — `dupontteijinfilms.com` 루트는 UA 를 붙이면 **200 · 14 KB** 를 준다. 사이트는 살아 있고 경로만 죽었다.
- **(d) 미러 탐색 범위** — Wayback CDX 로 `Teonex` 를 걸어 47줄을 받았고 그 안에 `FilmEnterprise/Datasheet.asp?ID=...` 계열이 있다.
  **그런데 두 번째 CDX 질의부터 web.archive.org 가 429 → 연결 거부로 바뀌었다**(같은 세션에서 두 번 친 것뿐이다).
  **다음 파동은 CDX 질의를 아껴 쓰고, 한 번에 `filter=original:.*Datasheet.asp.*` 로 ID 목록을 통째로 받아 저장해라.**
- 코퍼스 디스크에도 없다(`find /data/paper_patent_corpus -iname '*teonex*' -o -iname '*teijin*'` 0건, §635③).

---

## ___. **`conditions.temperature`(구식 문자열 키)가 2,255행 남아 있다 — 52차 NA 의 정규화가 이 키를 안 봤다**(61차 WD 신고 1의 확대)

61차 WD 가 재료 156·182 의 SCHOTT λ 행 조건 `"temperature": "20 degC"` 를 *원문에 없는 값*으로 신고하며
*"구식 문자열 키라 정규화도 안 걸렸다"* 고 적었다. **세어 보니 그 키를 쓰는 행이 2,255행이다.**

값의 모양이 제각각이라 조건 조회가 반쪽만 본다 — `ambient` · `room temperature` · `RT` ·
`298.15` · `300` · `300 K` · `20 degC` 가 한 키 안에 섞여 있다.
**같은 배치가 같은 SCHOTT 표에서 넣은 OHARA 행들은 이 키가 아예 없다**(`detail: "OHARA S-LAH79, k"`) —
한 배치 안에서도 규약이 갈렸다는 뜻이고, WD 의 "원문에 없는 값" 이라는 판단을 뒷받침한다.

**신고만 한다**(브리프 565). 고치는 쪽은 정리 파동이고, 고칠 때 **문자열을 버리지 말고
`temperature_c` + `temperature_verbatim` 으로 갈라야 한다**(`ambient`·`RT` 는 숫자로 못 접는다).
