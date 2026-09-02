<!-- 61차 WD — 열물성 쌍(비열·열전도율) t4 단독 대표 272칸 전수 감사 -->

# 61차 WD 감사 — `thermal.specific_heat` · `thermal.conductivity` 의 t4 단독 대표 272칸

기준 시각 — 2026-09-02, 라이브 DB(`MATERIALTWIN_DATA_DIR=/home/koopark/claude/HEAXHub/var/app_data/materialtwin_web`).
**병렬 배치가 같은 DB 를 친다.** 아래 수치는 전부 이 배치가 손댄 목록 기준이고, 총계 차이로 성과를 재지 않았다(브리프 640).

## 0. 표적의 모양

```sql
select m.id, pv.property_key
  from material m join property_value pv on pv.material_id = m.id
 where json_extract(m.attributes,'$.role') = 'product'
   and pv.property_key in ('thermal.specific_heat','thermal.conductivity')
 group by m.id, pv.property_key having min(pv.quality_tier) = 4;
```

- 272칸(비열 149 · 열전도율 123) · **재료 211종** · t4 행 **285행**(한 칸에 t4 가 둘인 경우가 13곳).
- 285행 **전부** `conditions.assumption = true` 이고 `method = 'estimated'` 다 — 무결성 검사의 두 표지는 깨진 데가 없다.

## 1. 온도 조건 — 63%가 조건 없이 앉아 있다

| 갈래 | 행 | 온도 조건 없음 |
|---|---:|---:|
| 1차 파동 일괄 문구 행 | 130 | **130 (100%)** |
| 그 밖의 행 | 155 | 50 (32%) |
| **합계** | **285** | **180 (63.2%)** |

**비열과 열전도율은 둘 다 온도 의존이므로 조건 없는 값은 해석 입력이 못 된다.**
그런데 갈래가 둘로 완전히 갈린다 — 1차 파동이 일괄로 부은 행은 **하나도 빠짐없이** 온도가 없고,
그 뒤 파동이 문서를 열고 넣은 행은 3분의 2가 온도를 갖는다. **온도 조건의 유무가 그 행이 문서를 거쳤는지를 가르는 지표다.**

## 2. 근거의 세기 — 118칸은 아직 아무 문서와도 대조된 적이 없다

t4 행의 `notes` 를 전수로 읽어 셋으로 갈랐다.

| 부류 | 행 | 무엇인가 |
|---|---:|---|
| **1차 파동 일괄 문구** | 130 | verbatim *"계열 대표값 — 해석 입력용 등방 근사. 실제 제품은 그레이드·배합에 따라 다르므로 정밀 해석 시 업체 데이터시트로 대체 권장"* 또는 *"복합재/적층재는 실제로 이방성 — 등방 해석용 면내 등가값"*. **어느 문서의 어느 표에서 왔는지 한 글자도 없다.** |
| Family approximation(영문) | 14 | 기재 폴리머를 밝히고 URL 까지 적는다. 근거가 있다. |
| 그 밖 | 141 | 대개 원문 verbatim·표 머리글·환산식·교차확인까지 적혀 있다. 이 카탈로그의 현재 수준이다. |

**칸 단위로 세면 272칸 중 118칸(43%)이 1차 파동 문구만 달고 있다** — 그 칸에 대해 문서를 연 배치가 아직 없다는 뜻이다.
브리프 618 이 battery 코어에서 관찰한 *"차 있는 칸 안에 모순이 숨는다"* 의 열물성판인데, 여기서는 모순이 아니라 **근거의 부재**다.

**이것이 다음 파동의 표적 목록이다.** 채움률로는 안 보인다 — 118칸은 전부 "차 있는 칸" 이다.

## 3. 이번 배치가 확인한 것

### 3.1 §602 로 닫힌 5칸 — 전부 **우리가 이미 인용한 문서** 안에 있었다

| 재료 | 칸 | 새 값 | tier | 어디에 있었나 |
|---|---|---:|---|---|
| 97 BT Resin | 비열 | 1000 J/(kg·K) | t1 | MGC CCL-HL832NX 표에서 **열전도율 바로 위 줄** |
| 112 Solid Electrolyte (LLZO Garnet) | 비열 | 618 | t1 (DSC) | Chalise 2023 본문 — **이 재료 열전도율 행의 notes 안에 이미 verbatim 으로 인용돼 있었다** |
| 151 Anodized Aluminum Layer (Al2O3) | 비열 | 885 | t3 | Abad/Rodriguez 2016 Table 1 — **이 재료 열전도율 행의 notes 가 표를 통째로 인용해 두었다** |
| 156 Periscope Prism Glass | 비열 | 530 · 660 | t1 | SCHOTT N-LASF9 · N-SF57 `Other Properties` — **λ 바로 위 줄의 `cp [J/(g·K)]`** |
| 182 Glass Molded Aspheric Lens | 비열 | 760 | t1 | SCHOTT P-SK57 같은 블록 |

세 건(97·112·151)은 **값이 우리 DB 의 notes 안에 이미 문장으로 들어 있었다**(브리프 635①).
두 건(156·182)은 같은 시트에서 λ·α·Tg 를 t1 으로 캐 가면서 **한 줄 위의 cp 만 남겼다**(브리프 602).

### 3.2 항등식 검산 `k = α · ρ · Cp`

- **112 LLZO** — 같은 시편의 세 인쇄값으로 α = 1.33 / (3894 × 618) = **5.53e-7 m²/s**. 산화물 소결체 대역이다.
- **151 AAO** — α = 0.38 / (1662 × 885) = **2.58e-7 m²/s**. 이 논문은 **광음향법이 ρ·Cp 를 입력으로 받아 k 를 낸다**고 본문이 밝히므로
  세 값은 구조적으로 정합하고, 그 때문에 **Cp 는 k 의 역산이 아니라 독립 실측 입력이다**(브리프 25 의 역산 금지선 안쪽).
- **어느 칸도 항등식으로 만들지 않았다.** 셋 다 인쇄값이다.

### 3.3 22차 감사의 보류가 실측으로 닫혔다 — 151

22차 B 는 151 의 t4 880 을 두고 *"Kyocera 소결 알루미나 13등급 대역 750~790 밖(+11~17%)이라 의심스럽다.
다만 양극산화막은 비정질·수화·다공이라 결합수가 Cp 를 실제로 올릴 수 있어 틀렸다고 단정할 수 없다"* 고 적고 판단을 보류했다.
**실측 885 는 그 보류를 지지한다**(t4 880 과 +0.6%). *소결 알루미나 값을 옮기면 안 된다* 던 그 경고가 옳았다.

### 3.4 부재를 확정한 23칸(재료 17종) — `core_absent_from_vendor_sheet`

문서를 실제로 열어 `grep -aci` 가 0 임을 확인한 칸만 담았다. 연 문서 범위를 사유마다 적었다(브리프 627③).

- **RF 적층판 9칸** — Isola I-Tera MT40 · Astra MT77 · Rogers RO4003C · RO4350B · RO4835 · CLTE-AT · Taconic TLX 시리즈 · Chukoh CGN-500 · CGS-500A.
  **아홉 장 전부 열전도율은 찍고 비열은 안 찍는다.** 이 카탈로그의 PTFE·세라믹 적층판 비열 960 J/(kg·K)은 전부
  Rogers **RT/duroid 5870-5880** 시트 한 장에서 옮겨 온 계열 대입값이다 — **같은 벤더 안에서도 서식이 갈린다**(브리프 628).
- **커버유리 6칸** — Corning Gorilla Glass Victus 2 · Victus · GG2 의 PI 시트에 열전도율도 비열도 없다.
  §127 이 인장강도에서 확인한 부재가 열물성에서 그대로 재현된다.
- **광학 폴리머 4칸** — ZEON ZEONEX 브로슈어 · 三井 APEL 브로슈어 둘 다 `thermal conductivity`·`specific heat`·`熱伝導`·`比熱` 0건.
- **필터유리 2칸** — SCHOTT BG60 · BG61 데이터시트에 λ 행도 cp 행도 없다.
- **UTG 1칸** — SCHOTT AS 87 eco 시트는 **비열은 찍고 열전도율은 안 찍는다**(그 비열 0.84 J/(g·K)는 이미 t1 으로 들어와 있다).
- **LCP 1칸** — Celanese VECTRA A950 CAMPUS 서식의 `Thermal properties` 블록은 융점·HDT·Vicat·CLTE 넷뿐이다.

## 4. 신고만 하고 손대지 않은 결함(브리프 565)

1. **재료 156·182 의 λ 행 조건 `"temperature": "20 degC"` 는 원문에 없는 값이다.**
   SCHOTT datasheet collection 의 `Other Properties` 블록은 `l [W/(m•K)] 0.790` 처럼 **온도 없이** 찍는다(같은 블록의 α 는 두 구간을 인쇄한다).
   같은 조건 칸이 **구식 표기 `temperature`(문자열)** 라 52차 NA 의 `temperature_c` 정규화도 안 걸렸다.
2. **출처 3384 의 제목이 논문의 제목이 아니다.** DB 제목은
   `Rodriguez et al., 'Thermal conductivity of 3D ordered anodic aluminium oxide membranes', Scientific Reports 6:38595` 인데
   원문의 `How to cite this article` 는 verbatim *"Abad, B. et al. **Tailoring thermal conductivity via three-dimensional porous alumina.** Sci. Rep. 6, 38595"* 다.
   **제1저자도 제목도 다르다.** DOI 는 맞으므로 값의 귀속은 안 깨지지만 제목 검색으로는 영영 안 걸린다(브리프 596).
3. **재료 270 `Matt Polyurethane Coating` 의 인장강도 행 notes 가 matmake 폴리우레탄 표를 통째로 인용하며
   `Thermal Conductivity 0.21 W/m*K` · `Specific Heat 1800 J/kg*K` 를 적어 두었다.**
   그런데 같은 재료의 두 칸에는 AZoM/Granta 표의 **하한** 0.28 · 1650 이 t4 로 앉아 있다.
   **두 편찬표가 같은 클래스에 서로 다른 값을 준다**(k 는 33% 차이). 어느 쪽도 이 제품의 실측이 아니라 둘 다 t4 이므로
   대표값은 안 바뀐다 — 그러나 **두 값이 갈린다는 사실이 어느 칸에도 적혀 있지 않다**(브리프 25 의 경계 사례).
4. **재료 85 `PEN Film (Diaphragm)`** — 이 재료가 쓰는 열물성 근거는 lookpolymers(MatWeb 계열 재편찬) 의
   Teonex Q51/Q83 페이지 두 장뿐이고 둘 다 `thermal conductivity`·`specific heat` 0건이다.
   **재편찬 페이지 0건으로 벤더 부재를 선언하지 않았다** — DuPont Teijin 자사 Teonex TDS 원본을 열어야 확정된다(브리프 630).
5. **재료 271 `Taconic TLY-5`** — 이 배치가 연 것은 **TLX 시리즈** 시트다. TLY-5 자신의 시트는 안 열었으므로 판정을 안 박았다.

## 5. 곁가지 — corning.com 의 상태코드 방언(브리프 634 의 세 번째 얼굴)

`https://www.corning.com/microsites/csm/gorillaglass/PI_Sheets/...` 는
UA 없는 `curl -sSL --compressed` 에 **403 · 486바이트**를 주고, 브라우저 UA 를 붙이면 **200 · 3.3 MB** 를 준다.
브리프 634 의 Panasonic 은 정확히 반대였다(UA 를 붙이면 침묵, 빼면 200).
**두 방언이 서로 반대이므로 "UA 를 붙여라"도 "UA 를 빼라"도 규칙이 못 된다 — 둘 다 쳐 봐야 한다.**
403 을 부재로 읽었으면 Victus·Victus 2 여섯 칸을 "문서가 없다" 로 잘못 판정할 뻔했다.

## 6. 남은 것

- **267칸**(비열 144 · 열전도율 123)이 여전히 t4 단독 대표다.
- **다음 배치의 첫 표적은 §2 의 118칸**이다 — 문서를 한 번도 안 거친 칸이고, 채움률·판정 검사 어디에도 안 보인다.
- 이 배치가 넣은 다섯 칸 중 **셋은 우리 DB 의 notes 안에 이미 값이 문장으로 들어 있었다.**
  브리프 635① 의 질의(`select ... from property_value where notes like '%<낱말>%'`)를 **물성 낱말**로도 걸어라 —
  등급명뿐 아니라 `specific heat`·`비열`·`比熱` 로 걸면 걸린다.
