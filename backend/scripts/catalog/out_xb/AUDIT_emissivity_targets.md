# 62차 XB — 전방사율 `optical.emissivity_total` 진짜 대체 대상을 전수로 두드렸다

기준 DB — `/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web/materialtwin.db`
스냅샷 — sqlite `backup` API(§647). 적용 직전 물성값 42,130 · 이 키 262행 · 출처 3,012.

## 1. 표적은 123 이 아니라 110 이었다

61차 WB 가 12종에 23행을 넣어 **t4 단독 대표가 197 → 186** 이 됐다.
WB 의 갈래표(W-A 43 · W-B 35 · W-C 123 = 201)는 **t4 행 전수**를 센 것이고 197 은 그 시점의
단독 대표 수다 — 두 수의 모집단이 다르다. 라이브에서 다시 세면

```
t4 행                     201
t4 를 가진 재료           201종
그중 tier<=3 도 가진 것    22종   ← WB 가 넣은 12종 포함
t4 단독 대표              186종
  − W-A(박막·스택)         43
  − W-B(자유표면 없음)      35
  = **W-C 진짜 대체 대상   110종**
```

## 2. 방법 — 61차 WC 의 경로를 그대로 썼다. 그리고 그 경로가 이 물성에서 얼마나 얇은지 쟀다

```
표적 110종이 쓰는 출처(source 조인, distinct)        872건
  local_path 가 채워진 것                             77 (8.8%)  ← §626 그대로다
  URL 이 있는 것                                     756
  아무 손잡이도 없는 것(url·doi·local_path 전무)       65
내려받은 파일                                        740  (PDF 269 · HTML 340 · XML 46 · TXT 49)
  200                                                668 · 403 42 · 429 14 · 404 5 · 502 5 · 410 1
3 KB 미만(사실상 실패)                                65 → Crossref·원URL 로 재시도, 33건 회복
`emissiv|emittanc|방사율|放射率` grep                 **적중 6건**
```

**872건에서 6건이다(0.7%).** 그중 표적 재료를 이름으로 찍는 행이 있는 것은 **NASA RP-1121 하나**다.
나머지 다섯은 SUS316 반사율(NASA-CR-150250) · Type 321 스테인리스 분광방사율(NASA MEMO 4-9-59W) ·
OCA 논문 본문의 낱말 한 번 · EuropePMC XML 둘이다.

코퍼스도 같이 쳤다 — FTS 로 `emissivity OR emittance OR emissive` 에 걸리는 코퍼스 문서가 528편인데
표적 110종의 출처 872건과 제목이 겹치는 것은 **2편**(Huang 2020 · Wang 2021)이고 둘 다 낱말 한 번이다.

> **이것이 이 파동의 가장 큰 발견이다 — 이 물성은 "우리가 이미 가진 문서" 안에 거의 없다.**
> 코어 물성(밀도·탄성계수·열전도율)에서는 §602 의 재개봉이 매번 값을 냈다. 전방사율은 다르다.
> 벤더 시트도 논문도 이 열을 안 찍는다. **이 물성의 문은 논문이 아니라 편찬표와 국립연구소 보고서다.**

## 3. 그래서 §649 로 갔다 — 가진 문서 셋을 전권으로 다시 열었다

| 문서 | 앞 파동이 본 것 | 이번에 더 읽은 것 |
|---|---|---|
| **Mikron 편찬표**(출처 4814) | WB 가 Al1100·황동·인청동·텅스텐 12행 | 표 전권 10쪽 — 아래 §4 |
| **NASA RP-1121**(출처 2111) | 52차 NA 가 α_s·ε_n 을 **다른 키에** 23행 | `ε_n` 이 무엇인지 정의절을 읽었다 — §5 |
| **SAND2018-13271**(출처 4813) | WB 가 Table 2-6·2-7·3-1 에서 10행 | Table 3-1 의 선언 · **부록 C** — §6 |

## 4. Mikron 편찬표 — WB 가 두고 간 행 셋 갈래

### 4.1 표가 등급을 이름으로 찍는 행이 있었다

`Paint, Lacquers, Varnishes` 절의 `Clear Silicone Vehicle Coating 0.001-0.150"thick` 블록이
**우리 등급을 그대로 인쇄한다.**

```
On mild steels ...................... 260 ....... 0.660
On stainless steels 316, 301, 347 ... 260 ....... 0.680, 0.750, 0.750
On Dow Metal ........................ 260 ....... 0.740
On Al Alloys, 24ST, 75ST ............ 260 ....... 0.770, 0.820
```

`-bbox-layout` 으로 열을 확인했다(§606) — `316,`(x=195) `301,`(x=217) `347`(x=240) 셋에
`0.680` `0.750`(x=475) `0.750`(x=506) 셋이 순서대로 대응하고, `24ST,`(x=169) `75ST`(x=198) 에
`0.770` `0.820`(x=475) 이 대응한다. **개수가 정확히 맞아 배정이 닫힌다.**
→ SUS316 0.68 · SUS301 0.75 · SPCC 0.66 · Al2024-T3 0.77(24ST = 2024 의 구 Alcoa 표기).

### 4.2 함정 — 같은 표에서 `316` 이 등급이 아니라 온도인 행이 있다

```
Stainless Steel 303 .................. 316 ....... 0.74
     Oxidized ........................ 1093 ...... 0.87
```

bbox 로 재면 `303`(x=159) 이 재료 열이고 **`316` 은 TEMPERATURE °C 열**이다.
**등급으로 읽으면 SUS316 에 0.74 를 넣게 된다 — §4.1 의 0.68 과 같은 표에서 8% 어긋난 오답이 된다.**

### 4.3 무수식 계열행은 어디까지 옮기나 — WB 의 선을 그대로 썼다

WB 의 문장이 정본이다 — *"표의 무수식 `Aluminum` 은 순알루미늄이고 Al1100 은 같은 물질이다.
6061·5083 에 옮기면 우리가 만든 값이다."*

| 옮긴 것 | 근거 | 안 옮긴 것 | 근거 |
|---|---|---|---|
| `Steel` 블록 → SPCC · S45C | 무합금 탄소강. 이 블록은 **등급축이 아예 없고 표면상태로만** 갈린다 | → SCM440 | 이름이 Cr-Mo 저합금강이고 표에 `Alloyed` 행이 따로 있다 |
| `Plastics, Opaque any color 25 °C 0.950` → EMC·PA6-GF30·PC/ABS·PBT·LDS PC | 표가 **스스로 색·조성 무관을 선언한 행**이다 | → 투명 필름·테이프·OCA | `Opaque` 가 조건이다. 기존 t4 notes 자신이 *"0.1 mm 필름 ~0.15"* 라고 두께 의존을 적어 두었다 |
| `Glass, Smooth 0-200 °C 0.95` → 커버글라스·UTG·프리즘글라스·몰드렌즈 | 매끈한 벌크 규산염 유리 자유표면 | → E-glass 직물 · IR-cut 필터 | 직조면과 코팅 스택이라 조건축이 다르다 |
| — | — | `Dow Metal 232-400 °C 0.24-0.20` → AZ31B·AZ91D·ZK60A | 마그네슘을 이름으로 찍지만 **등급을 안 찍는다** |
| — | — | `Tin / Unoxidized 25 °C 0.05` → SAC305 | 순주석 행이고 SAC305 는 3.5% 합금이다 |

**유리에는 카비앗을 같이 박았다.** 같은 표가 `Fused Quartz 320 °C 0.75` · `Covex D 0.76` ·
`Nonex 0.82` · `Pyrex 0-300 0.90` 을 따로 찍는다 — **'유리' 라는 낱말도 값을 정하지 않는다.**
다만 우리 대역(0~200 °C)에서는 표가 조성을 안 가르고 0.95 한 값만 준다.

### 4.4 카본블랙 모순의 답이 같은 표에 있었다

```
Carbon / Soot applied to solid ....... 50-1000 ... 0.96
Carbon / Lamp, Black, water glass .... 20-400 .... 0.96
Carbon / Candle Soot ................. 97-271 .... 0.952
Paint  / Lamp Black .................. 0-100 ..... 0.95
```

**넷이 0.95~0.96 으로 모이고 t4 0.2 만 방향이 반대다.** 0.96 을 옆에 넣고 t4 는 그대로 뒀다.

## 5. NASA RP-1121 의 `ε_n` 은 분광값이 아니다 — 키가 어긋나 있었다(신고, 삭제 안 함)

보고서 `Normal Emittance (ε_n)` 절 verbatim —

> **`The following formulas are used for computing total normal emittance, ε_n`**
> `The Gier-Dunkle portable emissometer, model DB-100 … gives a single integrated value of emittance.`
> `Spectral reflectance measurements were made over the wavelength region from 5 to 35 micrometers.
>  This region contains approximately 90 percent of the energy of a 300 K blackbody radiator.`

**적분식이 5~35 µm 분광반사율을 300 K Planck 함수로 가중적분한다 — 파장이 사라진 total 값이다.**
그리고 이 카탈로그의 `property_definition` 이 `optical.emissivity_total` 의 시험규격으로 적어 둔 것이
**ASTM E408 — Total Normal Emittance of Surfaces Using Inspection-Meter Techniques** 다.
DB-100 inspection emissometer 가 정확히 그 방법이다. **이 표의 옳은 자리는 이 키다.**

52차 NA 는 그것을 `optical.emissivity_spectral` 에 넣었다(재료 3·41·151·179·194, 5행).
**한 행도 지우지 않았고**, 이번 표적인 재료 179 에만 옳은 키로 옆에 넣었다.

| 재료 179 Beryllium Copper | 값 | 표면상태 | 출처 표 |
|---|---:|---|---|
| 무처리 맨면 | **0.03** | plain (uncoated) | p.11 `METALS AND CONVERSION COATINGS` |
| Pyramil Black 변환피막 | **0.72** | Pyramil Black on Beryllium Copper | p.7 `BLACK COATINGS` |

**한 재료 안에서 표면처리 하나로 24배다**(§586 의 가장 선명한 실례). 기존 t4 는 0.05 이고 조건이 없다.

## 6. SAND2018-13271 을 다시 열었더니 두 가지가 더 있었다

### 6.1 Table 3-1 이 스스로 등급 교환가능성을 선언한다

> **`Note: Treat SS304, SS304L and 17-4PH SS emissivities as interchangeable`**
> 결론절 verbatim: `No significant difference was identified for emissivity trends with SS304/304L
> and 17-4PH SS, so it is recommended that their emissivity data be treated as interchangeable.`

**§611 의 자리다 — 문서가 스스로 선언하면 그것은 우리의 계열 대입이 아니다.**
다만 이 선언은 **그 세 등급까지**이고 SUS316/430/410/420/201/301 로는 안 넘어간다.

### 6.2 부록 C 가 다음 파동의 표적을 **등급 이름째로** 찍어 두었다(§648)

`Table C-1: Recent literature measurements of metallic total hemispherical emissivity` 는
우리 등급 넷을 정확히 가리킨다.

| 우리 재료 | 부록 C 가 가리키는 문헌 | 표면상태축 |
|---|---|---|
| **6 SUS316L** · 5 SUS316 | Hunnewell et al. 2017, *Nuclear Technology* 198(3) 293-305 `10.1080/00295450.2017.1311120` | as-received · sandblasted(3단계) · graphite-coated · oxidized(700 °C) |
| **20·21 Al6063-T5/T6** | Tanda & Misale 2006, *ASME J. Heat Transfer* 128(3) 302-306 | **`Anticorodal 6063 (98% to 99% Al)`** as-received · sandblasted · anodized, 75~365 °C |
| **36 S45C** | Fu & Tan 2012 · Fu et al. 2012 | **`#45 Steel`** as-received, 225~1000 °C |
| **40 Inconel 718** | Greene et al. 2000 · Keller et al. 2015 · Tanda & Misale 2006 | as-rolled · oxidized · sandblasted · graphite-coated |

**넷 중 하나가 이번에 열렸다** — Greene et al. 2000 의 원 보고서 **BNL-52579**(OSTI 750781)가
공개돼 있다. 나머지 셋은 유료벽이다(tandfonline 403 · ASME Digital Collection).

## 7. BNL-52579 — 표 배정을 닫은 것은 원문 문장이다(§603)

Table 4 는 OCR 이 머리글을 통째로 깼다(`1 lodO)Iida,tion :;;raty-e ( ori4,`). 닫은 것은 셋이다.

1. **본문이 한 셀을 이름으로 짚는다** — verbatim `(in only one case, EMIS-003, the measured value
   is 0.84)` 이고 Table 3 이 EMIS-003 을 **30분 · 1000 °C** 로 지정하는데 Table 4 의 그 칸이 0.84 다.
2. **열평균이 본문 서술을 재현한다** — 1000 °C 열 (0.86+0.84+0.88)/3 = **0.860** · 1100 °C 열
   (0.90+0.90+0.89)/3 = **0.897** · 1142 °C 열 (0.89+0.91+0.91)/3 = **0.903**. 본문 verbatim
   *"increases … from 1000°C to 1100°C, but … little additional increase, if any, … to 1142°C"* ✔
3. **결론의 구간이 표를 감싼다** — verbatim `the emissivity increased … in the approximate range
   from 0.85 to 0.90`, 실제 9칸이 0.84~0.91 ✔

```
                산화온도 1000 °C   1100 °C   1142 °C     (측정 표면온도 1000 °C 에서의 최대 방사율)
   산화 15분        0.86     0.90     0.89
   산화 30분        0.84     0.90     0.91
   산화 60분        0.88     0.89     0.91
   무산화(as-rolled)                                      0.33
```

**200 °C 끝값은 안 넣었다 — 원문이 스스로 어긋난다**(§631·§141).
본문은 verbatim `approximately 0.20 at a surface temperature of 200°C` 인데
결론 1 은 verbatim `increased from approximately 0.24 to 0.33 over 200 ≤ T ≤ 1000°C` 다.
**1000 °C 의 0.33 은 세 문장이 일치하므로 그것만 넣고 200 °C 칸만 버렸다.**

## 8. 넣은 값 — 34행 · 재료 18종 · 전부 표면상태 + 온도

| 출처 | 성격 | 행 | 재료 |
|---|---|---:|---|
| **BNL-52579** Greene 1999 (OSTI 750781) | 국립연구소 진공 열량법 **전반구** 방사율 | 10 | Inconel 718 |
| **Mikron 편찬표**(Transmetra 배포, 출처 4814) | 표면상태별 전방사율 | 20 | SUS316·SUS301·SPCC·S45C·Al2024·유리 4종·불투명 플라스틱 5종·카본블랙 |
| **NASA RP-1121**(출처 2111) | GSFC total normal emittance (ASTM E408 계열) | 2 | Beryllium Copper |
| **Nagano 2000**(출처 4663) | 진공 구형용기 과도 열량법 전반구 방사율 | 2 | Graphite PGS (쌍둥이 계보 tier2) |

**모든 행에 표면상태와 온도가 있다.** 값 범위 0.03~0.96 — 전부 0 ≤ ε ≤ 1 안이다.

## 9. 모순 여섯 — 확인하고 조건·notes 에 못박았다. 하나도 안 지웠다

| 재료 | t4 | 처리 |
|---|---:|---|
| **108 Graphite PGS** | 0.95 | **옳은 값을 옆에 넣었다** — 같은 제품(쌍둥이 재료 277)의 Nagano 2000 실측 0.22(173 K)·0.32(373 K)를 tier2 로. α/ε = 0.72/0.32 ≈ 2.3 이라 반금속 표면에서 정상이고 **같은 문서의 태양흡수율 칸이 방향을 지지한다**(§617) |
| **147 Carbon Black** | 0.2 | **옳은 값을 옆에 넣었다** — Mikron `Soot applied to solid 50-1000 °C 0.96`. 같은 표의 램프블랙·촛불수트 셋이 0.95~0.96 으로 모인다 |
| 152 Graphene Film | 0.95 | **대체값 못 찾았다.** PGS 와 같은 부류지만 **CVD 그래핀 필름과 흑연화 PI 시트는 다른 제품이라 안 옮겼다**(§586). 이 재료의 출처 전수 grep 0건 |
| 89 ITO | 0.85 | 방향이 반대일 공산이 크나 **단정 안 했다** — 막두께·캐리어농도가 정한다(W-A). 조건축이 표면상태가 아님을 못박았다 |
| 111 Liquid Electrolyte | 0.95 | 밀봉 셀 안의 액체 — **부재가 아니라 해당 없음 성격**이다(§607). §618 이 같은 재료의 포아송비에서 같은 모순을 이미 신고했다 |
| 125 MoS2 단층 | 0.65 | 단층 방사율은 기판 없이 정의되지 않는다 |

여섯 다 `conditions.t4_contradiction` 과 notes 에 사유가 박혔다 — **`t4_contradiction` 이 이 카탈로그에
처음 생긴 자리다.** 채움률도 판정 검사도 t4 를 안 보므로(§618) 이 모순은 어떤 경보에도 안 걸린다.

## 10. 문서축 부재 판정 — 93종

값이 안 든 93종에 `attributes.core_absent_from_vendor_sheet["optical.emissivity_total"]` 을 달았다.
사유문에 **닫힌 축과 안 닫힌 축을 갈라 적었다**(§627) — *"이 재료의 값을 받치는 출처 N건을 전수로
열었고 0건이다. 닫힌 것은 문서축이고 조달축은 안 닫혔다."*
그리고 §648 대로 **다음 문의 정확한 주소**를 같이 적었다(아래 §11).
재료마다 특별한 사정이 있는 12종(SCM440·Mg 3종·Al6063 2종·SUS316L·Inconel625·SAC305·E-glass·
IR-cut·그래핀필름)에는 **그 재료만의 문장을 덧붙였다**(§600 — 형제로 묶은 사유는 형제만큼만 맞다).

## 11. 못 연 문 — 네 가지를 다 적는다(§648)

- **Touloukian & DeWitt TPRC Vol.7/8 원권** — 이 물성의 **가장 큰 단일 문**이다. SAND2018-13271 이
  우리가 못 넣은 값들의 출처로 이 두 권을 지목한다(`polished Al 6061 0.04~0.051` ·
  `sandblasted 0.41` · `polished SS18-8` · `oxidized SS303` · `sandblasted and oxidized SS304L`).
  - (a) 정확한 URL — `https://apps.dtic.mil/sti/tr/pdf/ADA951941.pdf`
  - (b) 시도한 조합 — `/sti/tr/pdf/` · `/sti/pdfs/` · `/sti/citations/` 셋 다 **200 인데 본문이
    545 바이트 `<title>Under Maintenance</title>` HTML** 이다. UA 유무 무관.
  - (c) 대조군 — 같은 호스트의 다른 경로도 같은 응답이라 **파일이 아니라 사이트 정책**이다.
  - (d) 미러 — Internet Archive advancedsearch `title:(thermal radiative properties) AND
    creator:(Touloukian)` numFound **0**. OSTI 5305606/5303494 는 서지만 있고 전문이 없다.
- **Hunnewell 2017**(SS316L) — tandfonline 403. 같은 연구실 후속 OSTI 1463106 을 받았는데
  **SS316L 방사율을 그림으로만 싣는다**(Figure 18~21). 픽셀 판독이 남은 길이다.
- **Tanda & Misale 2006**(Anticorodal 6063) — ASME Digital Collection 유료벽. **표적 등급 이름이
  그대로 인쇄된 유일한 문헌**이라 값어치가 가장 크다.
- **Keller 2015**(Inconel 718) — Elsevier 유료벽. 다만 BNL-52579 로 이 재료는 이미 닫혔다.

## 12. 검사

```
integrity_check.py   스냅샷 대 라이브 diff — **신규 위반 0** (이상 1개 → 1개, 같은 줄)
verdicts_check.py    이상 0개 (기존 신고 1건은 재료 582, 이 파동과 무관)
pytest -q            366 passed, 1 skipped  (기준선 그대로)
선언 대 집계(§610)   선언 34행 → 내가 손댄 18종의 이 키 행 18 → 52 (+34) ·
                     그중 tier<=3 0 → 34 (전부 이번 것) ✔
                     **t4 행 201 → 201 — 한 행도 안 지웠다**
                     새 출처 3012 → 3013 (+1, BNL-52579 만. Mikron·RP-1121·Nagano 는 재사용)
                     판정 선언 93종 → 집계 93종 ✔
                     t4 단독 대표 186 → 168 (−18 = W-C 17 + W-B 의 147 카본블랙)
                     **W-C 표적 110 → 93**
```

**병렬 배치가 같은 DB 를 친다(§640)** — 그래서 전체 총계가 아니라 **내가 손댄 재료 18종**에서 쟀다.
스냅샷은 `sqlite3 .backup` 으로 떴다(§647 — `cp` 는 WAL 을 안 가져온다).
