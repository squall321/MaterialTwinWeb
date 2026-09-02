# 62차 XB — 결정과 근거

## 1. 표적은 123 이 아니라 110 이다
WB 가 12종에 값을 넣어 t4 단독 대표가 197 → 186 이 됐다. W-A 43 · W-B 35 를 빼면 **110종**이 남는다.
WB 의 표는 43+35+123=201(=t4 행 전수)로 세었고 197 은 그 시점의 단독 대표 수다 — 두 수의 출처가 다르다.

## 2. 키 배정 — `optical.emissivity_total` 의 시험규격이 ASTM E408 이다
`property_definition` 이 이 키에 **ASTM E408**(Total Normal Emittance, inspection-meter)을 적어 두었다.
NASA RP-1121 의 ε_n 은 Gier-Dunkle DB-100 휴대형 emissometer 로 잰 **total normal emittance** 이고
보고서 본문이 verbatim `The following formulas are used for computing total normal emittance`
라고 적는다 — **이 키가 맞다.** 52차 NA 는 그것을 `optical.emissivity_spectral` 에 넣었다(분광이 아니다).
**지우지 않았다. 신고만 하고 옳은 키에 옆으로 넣었다.**

## 3. 무수식 계열명을 등급에 옮기는 선을 어디에 긋나
WB 의 선을 그대로 썼다 — *"표의 무수식 `Aluminum` 은 순알루미늄이고 Al1100 은 같은 물질이다.
6061·5083 에 옮기면 우리가 만든 값이다."*
- 넣는다 — 표가 등급을 이름으로 찍거나(`316, 301, 347` · `24ST, 75ST`), 무수식 이름이 그 재료의
  물질과 같을 때(무수식 `Steel` = 탄소강 → SPCC · S45C · `Plastics, Opaque any color` · `Glass, Smooth`).
- 안 넣는다 — `Stainless Steel`(무수식) → SUS201/410/420/430 · `Dow Metal` → AZ31B/AZ91D/ZK60A ·
  `Titanium`(무수식) → Ti Grade 1/2/4 · `Aluminum`(무수식) → 6063/5052/3003/7050.
- SCM440 은 뺐다 — 이름이 저합금강이고 표에 `Alloyed` 행이 따로 있다.

## 4. 유리는 값을 넣되 카비앗을 박는다
같은 Mikron 표가 `Glass, Smooth 0-200 °C 0.95` 옆에 `Fused Quartz 320 °C 0.75` ·
`Nonex 0.82` · `Covex D 0.76` · `Pyrex 0-300 0.90` 을 찍는다. **조성과 온도가 둘 다 값을 움직인다.**
우리 대역(0~200 °C)에서는 표가 조성을 안 가르므로 무수식 행을 쓰되, 표 자신이 0.75~0.95 를
찍는다는 사실을 notes 에 박았다. 코팅·흡수유리(137 IR-cut)와 직물(199 E-glass)은 뺐다.

## 5. Inconel 718 표 배정은 원문 문장이 닫았다
BNL-52579 Table 4 는 OCR 이 머리글을 통째로 깼다. 배정을 닫은 것은 본문 두 문장이다 —
`(in only one case, EMIS-003, the measured value is 0.84)` 이고 Table 3 이 EMIS-003 을
**30분·1000 °C** 로 지정하는데 Table 4 의 그 칸이 정확히 0.84 다. 열평균도 본문 서술을 재현한다
(1000 °C → 0.86 · 1100 °C → 0.897 · 1142 °C → 0.903, 본문 *"increases … 1000 to 1100 … little
additional increase … to 1142"*). §603 의 표 자신의 항등식이다.
**200 °C 끝값은 안 넣었다** — 본문이 0.20, 결론이 0.24 로 스스로 어긋난다(§631·§141).

## 6. PGS 쌍둥이는 tier2 로 넣었다
재료 108(두께 미지정 일반 PGS)과 277(100 µm 등급)은 같은 제품군이다(§586 catalog twin).
Nagano 2000 의 측정은 **100 µm 시편**이므로 108 에는 tier1 이 아니라 **tier2 + `grade_scope`** 로 넣었다.

## 7. 조달로 못 연 문
- **Touloukian & DeWitt TPRC Vol.7** — DTIC `apps.dtic.mil/sti/tr/pdf/ADA951941.pdf` 가
  **200 인데 본문이 `Under Maintenance` HTML 545 바이트**다(§438·§634 의 새 방언). Internet Archive
  advancedsearch 는 `title:(thermal radiative properties) AND creator:(Touloukian)` 에 numFound 0.
- **Hunnewell 2017**(SS316L 전반구 방사율) · **Tanda & Misale 2006**(Anticorodal 6063 = Al6063 계열,
  as-received/sandblasted/anodized 75~365 °C) · **Keller 2015** — 전부 유료벽. tandfonline 은 403.
  Sandia 부록 C 가 이 셋을 **표적 등급 이름째로** 가리킨다 — 다음 파동의 가장 짧은 길이다.
