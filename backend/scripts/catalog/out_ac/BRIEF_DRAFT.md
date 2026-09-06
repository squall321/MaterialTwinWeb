# 65차 AC 교훈 초안 (번호는 비워 둔다)

## §___. **유료벽 뒤의 자매 저널논문 대신 같은 저자의 학위논문을 먼저 열어라 — 등급도 값도 거기 있다**(§672·§602·§620 의 실행)

46차 HD 가 Eftekhari 2016(IJF)의 세 시편에 대해 *"등급 코드가 없다 — 자매논문 [15] Compos. Part B 97 이 조달 대상"* 이라고
넘겼고, 47차 IC 가 그 DOI 를 Unpaywall·OpenAlex·academia.edu·기관 리포지터리로 전부 두드려 **Elsevier 유료로 접근 부재를 확정**했다.
확정은 옳았다. **틀린 것은 표적이었다.**

같은 저자의 **학위논문**(Eftekhari, *Creep, Fatigue, and Their Interaction at Elevated Temperatures in Thermoplastic
Composites*, University of Toledo 2016)이 OhioLINK ETD 에 **무료 PDF 10.4 MB** 로 있다. 그 안에서
- Table 3-1 의 마지막 행 `Full name and company` 가 **상품코드를 인쇄한다** — `[P-40TC-8100] -ASAHI KASEI` ·
  `[P6-30FG-0600] -ASAHI KASEI` · `[SE1GFN2] - Sabic`. **다섯 파동(46·47·60차) 동안 "원리적으로 못 닫는다" 던 등급이 한 줄로 닫혔다.**
- Table 4-1 이 저자 자신의 인장시험 **elastic modulus 36행**(3재료 x 3온도 x 2정의 x 2반복)을 인쇄한다.

**규율 — 유료벽에 막히면 그 논문의 저자·연도가 아니라 *저자의 학위*를 검색해라.** 저널논문은 학위논문의 한 장(章)이고,
북미 학위논문은 OhioLINK·ProQuest Open·기관 ETD 에 **원문 그대로** 올라간다. 접근 경로도 한 줄이다 —
`https://etd.ohiolink.edu/acprod/odb_etd/ws/send_file/send?accession=<accession>&disposition=inline`.
등록번호는 웹검색으로 나오고(`rave.ohiolink.edu/etdc/view?acc_num=…` 이 그 자리다), 실패하면 `Document not found or is embargoed` 한 줄이 온다.

**그리고 학위논문은 저널논문보다 *더* 많이 인쇄한다.** 저널판은 지면 때문에 재료절을 상표명까지만 줄이는데,
학위논문의 재료 장은 **TDS 편찬표와 상품코드**를 통째로 싣는다. 우리가 다섯 파동 동안 찾던 것이 정확히 그 표다.

**동일 시편 확인은 숫자로 닫는다(§632).** 학위논문 Table 3-2 의 Tm/Tg 가 이미 DB 에 든 IJF 값과 같고
(PP-T 165/11 · PP-G 165/23 · PPE/PS 325/135 degC), Table 4-1 의 85 degC 인장강도가 IJF Table 2 의
모델상수 `S_u` 와 맞는다(PP-T 13.8 · PPE/PS 46.3·46.8 평균 46.55 대 46.5). 저자·지도교수·시편이 같으므로 동정이 닫힌다.

---

## §___. **부재 판정을 뒤집는 것은 "더 두드린 것" 이 아니라 "다른 종류의 문을 연 것" 이다**(§669 의 뒷면)

65차 AC 의 표적 41칸은 재료 14종이었고 **14종 전부가 `identification_status` 가 '미식별' 인 클래스값 레코드**였다.
§669 의 수확률 계산대로라면 이 축은 "이 물성이 여기 없다" 여야 하고, 실제로 11종은 그랬다.
갈린 것은 세 종뿐인데 **그 셋에서만 문의 종류가 달랐다** — 나머지 열하나는 원 논문이 유일한 1차 문서이고
저자가 시편을 익명화했지만(Palaniappan) 또는 벤더를 안 밝혔지만(Ehrler·Low·Erlat), 셋은 **저자가 학위논문에서
같은 시편의 상품코드를 인쇄해 두었다.**

**수확률을 재기 전에 표적의 종류를 갈라라.** "등급 미확정"에는 두 부류가 있다.
1. **원문이 벤더를 안 밝혔다** — 조달로 못 닫는다(Ehrler 의 `FR-4` · Low 의 `optical grade` · Palaniappan 의 익명 A~D).
2. **원문이 상표명까지만 줄였다** — **저자의 다른 문서가 코드를 갖고 있을 수 있다**(Thermylene · Noryl · Hostaform).
   2번은 `trade_name` 이 `attributes` 에 이미 적혀 있다는 것이 지문이다. 한 줄 질의로 갈린다.

---

## §___. **`identification_status` 를 뒤집으면 집계 갈래가 함께 움직인다 — 뒤집기 전에 그 재료의 나머지 코어 칸을 세라**(§610 의 확장)

`coverage_report.subsystem_core()` 의 `elif` 사슬은 `identification_status` 가 `미식별` 로 시작하면 **V4(등급 미확정)** 로 센다.
등급을 닫으면 그 재료의 **모든** 빈 코어 칸이 V4 에서 내려온다 — V2 판정이 붙은 칸은 V2 로, 아무것도 안 붙은 칸은
`core_fill_sheet` 같은 자유 키가 있으면 V3, 없으면 **V5(진짜 남은 것)** 로 떨어진다.

65차 AC 에서 실측 — 세 재료의 코어 21칸이 이렇게 갈렸다.

| | 전 | 후 |
|---|---:|---:|
| 채움 | 0 | **6**(밀도 3 · 영률 3) |
| V2 | 0 | **3**(포아송비) |
| V4 | 21 | 0 |
| V3 | 0 | **12**(CTE·열전도율·비열·인장강도 x 3 — `core_fill_sheet` 가 있어서 V5 가 아니다) |

**규율 둘.**
- **등급을 닫는 파동은 그 재료의 `core_fill_sheet`(또는 다른 자유 판정 키)도 같이 고쳐라.** 그 텍스트는 대개
  *"코어 0/7, 등급 미확정으로 의도적 공백"* 이라고 적혀 있어 **닫는 순간 거짓이 된다**(§618 — 차 있는 칸 안의 모순).
  고칠 때 **그 시트가 실제로 인쇄하는 행 목록**을 적어 두면 그 12칸이 다음 파동의 즉시 표적이 된다(§648).
- **선언한 칸과 집계 이동을 대조할 때 V4 감소분은 내 판정 수보다 크다.** 65차 AC 는 판정 35 · 채움 6 인데
  V4 는 53 이 줄었다(35 + 6 + 12). **차이가 12 라는 것을 미리 적지 않으면 이 대조가 거짓 경보를 낸다.**

---

## §___. **CAMPUS/ISO 10350 단일점 물성표에는 포아송비 행이 없다 — 등급을 닫아도 그 칸은 안 열린다**(§675·§613 의 고분자판)

65차 AC 가 등급을 닫고 세 벤더 시트를 실제로 열었는데 **포아송비는 세 시트 어디에도 없었다.**

| 시트 | 인쇄행 |
|---|---|
| Thermylene P-40TC-8100 (CAMPUS/MDC) | MFI · 인장강도 · 굽힘탄성률 · 굽힘강도 · Charpy · HDT · 밀도 — **일곱 줄** |
| Thermylene P6-30FG-0600 (CAMPUS/MDC) | 같은 일곱 줄 |
| NORYL SE1GFN2 (SABIC Material Finder, Americas·Asia·Europe **세 블록 전부**) | 기계·충격·열·물리·전기 다섯 절, `poisson` 적중 **0건** |

**서식이 정한 부재다.** CAMPUS 의 근거 규격인 ISO 10350-1 의 단일점 물성 목록에 포아송비가 없고,
북미 벤더 TDS 도 ASTM D638/D790/D792 를 찍지 ASTM E132 를 안 찍는다.
**등급 미확정과 물성 부재는 다른 축이다(§643)** — 등급을 닫으면 밀도·인장강도·굽힘탄성률은 즉시 열리지만
포아송비는 안 열린다. 사출 열가소성수지의 포아송비를 캐려면 **시트가 아니라 초음파 탄성상수 논문이나
벤더의 CAE 물성세트**(SABIC 은 Material Finder 밖 별도 채널로 낸다)를 표적으로 잡아야 한다.

---

## §___. **지역판이 다르면 같은 등급도 다른 값을 찍는다 — 원 논문이 인용한 규격이 어느 지역판인지를 말한다**(§638 의 실행)

SABIC `NORYL Resin SE1GFN2` 한 등급이 Material Finder 안에서 세 블록으로 갈린다.

| 지역 | 비중 | 인장탄성률 |
|---|---|---|
| Americas | **1.23**(ASTM D792) | 7100 MPa(ASTM D638, 5 mm/min) |
| Asia | 1.23(ASTM D792) | 6400 MPa(ISO 527, 1 mm/min) |
| Europe | **1.25**(ASTM D792) · 1.25 g/cm³(ISO 1183) | 5500 MPa(ISO 527, 1 mm/min) |

Eftekhari 학위논문 Table 3-1 의 PPE/PS 열은 **ASTM 규격만** 인용한다(D638 106 MPa · D790 5.7 GPa · D792 1.23).
Americas 블록의 세 값(106 MPa · 5720 MPa · 1.23)과 **셋 다 맞는다.** 규격 계열이 지역판을 특정한 것이다.
**규율 — 벤더가 지역판을 갈라 찍으면 `test_standard` 가 어느 판인지의 지문이다.** ISO 만 인용한 논문에 ASTM 판을,
ASTM 만 인용한 논문에 ISO 판을 붙이면 §586 의 "이름이 세대를 숨긴다" 를 지역으로 반복하게 된다.

---

## §___. **`Young` 도 `density` 도 자기 그림자를 찾는다 — 65차 AC 의 오탐 실측**(§667 의 재현)

표적 재료 14종이 쓰는 출처 여섯 편을 전권으로 걸었을 때 낱말 적중과 그 정체.

| 적중 | 어디 | 실제 정체 |
|---|---|---|
| `Young` x2 (Palaniappan 1999) | 저자 약력 | `Outstanding **Young** Engineer Award` |
| `densit` x2 (Low 2005) | 본문 | 박막 결정립의 **조밀도**(`higher density film`) |
| `densit` x1 (Eftekhari IJF) | 본문 | `strain energy **density** range` |
| `densit` x2 (Erlat 2003·1999) | 본문 | **결함밀도** `700 mm^-2 density` |
| `Modulus`·`Specific Gravity` (Ehrler 2002 Table V) | 표 | **보강섬유**(Thermount·E-Glass·S-Glass·Quartz)이지 적층판이 아니다 |

**여섯 편 전권에서 표적 물성의 진짜 적중은 0건이었다.** 표적이 `density`·`modulus` 처럼 흔한 낱말일수록
정규식은 **읽을 이유**만 주고 값은 안 준다 — 적중 수로 성과를 예고하지 마라(§659).
그리고 **Ehrler 의 표 V 는 §602 의 '옆 표' 가 오히려 함정인 자리**다. 옆 표를 봤더니 열은 맞는데 **주어가 달랐다.**
