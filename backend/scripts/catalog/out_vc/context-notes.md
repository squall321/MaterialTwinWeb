# 60차 VC 맥락 기록

## 표적 수를 라이브에서 다시 센 것이 먼저였다
브리프의 13·17·2 를 그대로 믿지 않고 `coverage_report.subsystem_core()` 를 그대로 재현해 세었다.
처음엔 안 맞았는데(1314 가 6칸으로 나왔다) **CORE7 의 CTE 키를 `thermal.expansion_coefficient` 로 잘못 쓴 것**이었다.
실제 키는 `thermal.expansion_linear` 다(`coverage_report.py:29`). 고치니 13·17·2 가 글자까지 맞았다.
**집계를 재현할 수 없으면 그 뒤의 판정은 전부 허공에 뜬다** — 표적 수 대조가 첫 관문이다.

## 값을 하나도 안 넣었다 — 그 이유를 다 적었다
32칸 전부가 판정이다. 넣을 수 있었는데 안 넣은 자리가 셋 있고 셋 다 이유가 다르다.

1. **1314 의 영률·인장강도** — Shi 2012 Table 2 에 `flexural modulus 3,500 N/mm²` 와
   `flexural strength 120 N/mm²` 가 인쇄돼 있다. 굽힘은 인장이 아니다(브리프 141 의 갈래 규율).
2. **615 의 인장강도** — 이 재료의 피로계수 행이 조건에 `measured on IEC 60893 EPGC 203 …
   (UTS 418.45 MPa …), NOT on this product` 라고 이미 적어 두었다. 앞 배치가 그 값을 보고도
   안 옮긴 것이고, 그 판단이 옳다(브리프 147·616).
3. **617 의 포아송비** — Chowdhury 2019 가 스트레인게이지로 잰 `0.2989 ~ 0.30` 을 인쇄한다.
   그런데 그 논문은 재료를 `a typical underfill material` 로만 부르고 Tg·CTE·밀도 어느 축도 안 찍어
   617(Tg 137 °C, CTE α1 28 ppm/°C)과 같은 등급임을 닫을 대조축이 하나도 없다(브리프 51·586·620).
   그리고 그 값은 재료 **738** 에 이미 제자리로 들어가 있다.

## 617 ↔ 738 — 이중 계상 신고
`mechanical.wlf_c1 = 14.76` · `wlf_c2 = 91.52`(출처 Chowdhury 2019, src3525)가
**재료 617 과 738 에 똑같이 앉아 있다.** 같은 배치가 21초 간격(`2026-08-13 11:25:45` / `11:26:06`)으로 넣었다.
- 둘이 같은 언더필이면 738 이 617 의 중복 레코드다.
- 다르면 617 의 WLF 2행이 등급 이전이다.
어느 쪽이든 지금은 이중 계상이다(브리프 116·123·586). **병합·삭제는 이 배치의 권한이 아니라 신고만 한다.**
617 의 판정문 안에도 같은 신고를 박아 두었다.

## 403 — §3 위반 신고
Yang 2017(Materials 10(9) 1077) Table 1 **바로 앞 문장**이 verbatim 으로
`The Poisson ratio and CTE of the adhesive were assumed as constant values, because they have
little impact on the packaging stress [23]` 라고 적는다.
그런데 이 재료의 `mechanical.poisson_ratio 0.37` 과 `thermal.expansion_linear 6e-05` 가
**tier1 · method=measured** 로 그 출처에 걸려 있다. **해석 입력 가정값을 남의 t1 실측으로 세탁한 자리다**(§3).
값은 안 지웠다. 등급 정정은 정정 문서(`corrections`)의 일이다.

## 392 D3O — "벤더가 안 찍는다" 가 아니라 "등급을 못 고른다"
조달을 실제로 했다. D3O 공개 TDS 일곱 장에서 인장강도가 **등급마다 0.51 ~ 2.2 MPa(4.3배)** 로 갈린다.
그런데 원문(Smeets 2023)은 등급명을 안 밝히고 밀도만 397 kg/m³(본문은 395)로 찍는다.
D3O 전제품 편찬표(`Material Sheet Guide`)에는 **인장강도 열 자체가 없고** 밀도가 0.22~0.62 g/cm³ 로 널려 있는데
0.397 인 등급이 없다. 성격상 V4 이지만 V4 는 운영으로 전파되지 않으므로(§608)
전파되는 `core_absent_from_vendor_sheet` 에 적고 사유에 "성격상 V4" 를 못박았다 — 57차 SA 선례 그대로.

곁가지 — 기존 `mechanical.poisson_ratio 0.0` 행(D3O LITE D, 200~220 kg/m³)의 `grade_scope` 가
이미 `STRONG GRADE MISMATCH` 를 적어 두었고, 거기서 Zhao 2019(ACS Omega, 몰딩 D3O 0.41 g/cm³)라는
**조달 단서까지 남겨 두었다.** 그 논문을 열었더니 역시 압축시험뿐이었다.
**조건 필드에 적힌 반례·단서가 다음 파동의 조달 지도 노릇을 한다** — 브리프 598 의 실행판이다.

## 자유 키를 지우지 않았다
`core_verdict_undecided`(1911) · `core_fill_sheet`(1358·1359·1360) · `procurement_47ic` 는 그대로 뒀다.
집계가 읽는 칸으로 **복사**했을 뿐이다(브리프 623 — "집계가 읽는 자리" 와 "사람이 읽는 자리" 는 배타가 아니다).
`apply_core_verdicts.py` 는 `attributes` 를 키 단위로 병합하므로 다른 키를 건드리지 않는다.

## 병렬 배치 주의
`subsystem_core()` 전체 합계는 이번 파동 것만이 아니다. 우리 것은
packaging V5 99→86 · passive V3 7→V1 7 · wlp V3 10→V2 10 · (태깅 없음) V5 2→0 네 줄이다.
커밋은 §504 대로 경로 제한으로 했다.
