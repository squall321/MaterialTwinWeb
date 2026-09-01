<!-- 57차 SC 작업 중 내린 결정과 그 근거 — 다음 세션이 다시 유도하지 않도록 -->
# 57차 SC 컨텍스트 노트

## C1. 지시서의 전제가 틀렸다 — 85종은 이미 전수 판정돼 있었다
지시서는 *"85종을 하나씩 보고 근거를 갖고 배정해라"* 로 왔다. DB 를 먼저 쳤더니
**85종 전부**에 `attributes.verdict_subsystem`(`undetermined`|`not_applicable`)과
`subsystem_basis` 가 있었다. 만든 것은 **49차 KA**(커밋 `b53f334`) —
*"계통 태그 없던 203종을 훑는다 — 122종에 붙이고 85종은 사유를 남겼다"*.

내 일은 **배정이 아니라 검증**으로 바뀌었다(§479·505 — 인계는 언제나 검증 대상).
22계열로 묶어 재검토했고, 판정이 문서로 확인되지 않은 것 셋만 실제로 열었다.

## C2. `verdict_subsystem` 은 아무도 안 읽는다 — §593 의 계통판
KA 는 판정을 남겼는데 **`subsystem_core()` 는 `attributes.subsystem` 만 본다.**
그래서 85종이 `(태깅 없음)` 한 통에 그대로 남고, 화면은 `기타` 로 보여 주고,
**57차 조정자가 이 85종을 '미판정'으로 다시 셌다.** §593 이 코어 빈칸에서 말한 것이
계통 축에서 똑같이 재발했다 — 판정을 읽을 코드가 없으면 판정은 없는 것과 같다.

**제안(코드 변경은 하지 않았다)** — `subsystem_core()` 가 `(태깅 없음)` 을
`(계통 없음 — 판정)` / `(태깅 없음 — 미판정)` 둘로 갈라야 한다. 지금 이 한 줄이
파동마다 같은 85종을 표적으로 되돌려 보낸다.

## C3. 배정한 것은 하나뿐이고, 그 근거는 문서다
- **#371 DELO KATIOBOND 4670 → `packaging`.** TDS(2024-07-31) `Function` 란이
  `Fill for Dam&Fill` · `glob top` · `encapsulant / potting compound`,
  `Typical area of use` 가 `encapsulation of chip modules` 다. TIDB(Rev.42) 부제는
  `UV-curing encapsulant for Smart-Card technology`. **KA 가 '카메라용으로 알려져 있으나
  근거가 없다' 고 미룬 것을 열어 보니 카메라가 아니라 칩 봉지였다** — §127 의 정확한 사례다.
- **#372 KATIOBOND 4552** 는 같은 검사를 통과 못 했다. TDS `Function` 이
  `electronic adhesive`/`electronic encapsulant`, TIDB 가 `relays and switches` 다 — 범용이다.
- **#67 EAR Isodamp C-1002** 도 열었다. Product Bulletin 196 제목이
  `Aircraft Damping Composite` 이고 용도가 일반 제진·충격제어다. `undetermined` 확정.

**형제 이름으로 찍지 않았다** — 60(`Speaker Mount`)·61(`Haptic motor isolation`)이 갈린 것은
description 이 부품을 말했기 때문이고 67·70 에는 그 문장이 없다.

## C4. V3 72칸을 갈랐더니 세 갈래가 나왔다 — 그리고 자리가 하나 모자랐다
| 갈래 | 칸 | 옮긴 자리 |
|---|---:|---|
| 시트를 열어 부재 확인(§127) | 30 | `core_absent_from_vendor_sheet` |
| 대표 재료가 코어를 갖는다(중복 레코드) | 14 | `core_not_applicable` |
| 등급 미확정(§58) | 14 | `identification_status: "미식별 …"` |
| **읽을 시트가 존재하지 않는다** | **14** | **자리가 없다 — V3 로 남겼다** |

마지막 갈래가 #587 SY-14M-III(BIAM, 공개 TDS 없음)와 #1110 3M AF-130(단종, 현행 TDS 없음)이다.
V2 는 *"시트를 실제로 열어 그 열이 없음을 확인했다"* 인데 이쪽은 **열 시트가 없다.**
둘을 섞으면 §584 가 갈라 놓은 S3a 와 S3b 를 다시 붙이는 셈이라 옮기지 않았다.

조달도 해 봤다(§438·§22).
- AF-130 — 현행 3M 목록에는 **AF 130-2** 뿐이고 경화(최소 300 °F)·사용온도(−67~400 °F)가
  1987년 논문의 AF-130(177 °C/60 min, unmodified epoxy)과 다르다. **이름이 비슷한 딴 등급**이라
  대체하지 않았다(§22·586).
- SY-14M-III — 北京航空材料研究院 공개 문서가 검색·특허·논문 어디에도 없다.

## C5. `identification_status` 를 넣었는데 V4 로 안 갔다 — 분류기 순서 문제
`subsystem_core()` 의 갈래 판정 순서가 `V1 → V2 → V6 → **free(V3)** → grade_undet(V4)` 다.
2271·2272 는 `core_fill_sheet`(자유 키)를 **함께** 갖고 있어서, 읽을 수 있는 `identification_status`
를 새로 달았는데도 자유 키가 먼저 걸려 V3 로 세어진다.

**V3 의 뜻이 "판정은 있으나 집계가 못 읽음" 인데 이 둘은 이제 읽을 수 있다** — 분류기가 거짓을
인쇄한다. `grade_undet` 를 `free` 앞으로 옮기면 끝나지만, **57차 SB/SD 가 같은 파일을 동시에
고치고 있어서(§504) 건드리지 않고 신고만 한다.**

## C6. 채굴 — 시트를 열면 자유 키의 '없다' 가 뒤집힌다
- **#639 Fused Silica** — Heraeus HQS-SO 시트를 열었다. 열전도율 6행(20~950 °C)과
  인장강도 50 MPa 가 **한 페이지에 인쇄돼 있다.** 이 재료의 비열·CTE 가 이미 같은 표에서
  들어와 있었으므로(src3620) **아무도 그 옆 칸을 안 본 것**이다. 코어 2칸이 닫혔다.
- **#2391 Uddeholm Corrax for AM** — `relation_to_bar` 가 *"물리물성표는 봉재와 같은 숫자라
  중복이라 안 넣었다"* 였다. 원문 p.7 을 열어 보니 **그 페이지 전면이 `ADDITIVE MANUFACTURING`
  장**이고 `Physical data` 표 바로 아래가 `Mechanical data AM (Uddeholm Corrax for AM)` 이다.
  **시트가 AM 등급을 위해 그 표를 다시 인쇄한다** — 벤더의 AM 등급 선언이므로 옮겼다.
  숫자가 같은 이유도 시트가 밝힌다(`within the normal variation as the conventional material`).
  계보는 각 행 조건의 `same_as_bar_material: true` 로 남겼다. 코어 4칸이 닫혔다.
  **p.6 의 `Apparent 4.3 / Tap 4.7 / True density 7.61 g/cm3` 는 분말 특성이라 안 넣었다**(§241·245).

## C7. 못 캔 것과 그 이유
| 재료 | 남은 칸 | 왜 못 캤나 |
|---|---:|---|
| #2417 Thermocomp MEV-1006 (LNP) | 7 | `MEV-` 접두 자체가 현행 LNP 명명에 없다. 단종 등급이고 SABIC materialfinder·MatWeb 어디에도 없다 |
| #1658 Permabond ESP110 | 5 | Permabond 현행 목록에서 내려갔다(제품 URL 404). **검색이 Henkel `LOCTITE ESP110` 을 준다 — 딴 회사 딴 제품이다**(§475) |
| #2446·2447 PZN·PZN-8%PT | 14 | Park 1997 Table I 이 인쇄하는 것은 **탄성 컴플라이언스** `s33^E`(7.4·48·130 ×10⁻¹² m²/N)뿐이다. `E33 = 1/s33` 은 우리 산술이라 안 했다 |
| #2233·2283 무코팅 PET 기재 | 14 | 배리어 논문의 대조군이라 두께 말고는 아무것도 인쇄되지 않는다 |

**막힌 키 하나를 신고한다(§468)** — `mechanical.elastic_compliance`(1/Pa)가 없어서 Park 1997 의
`s33^E` 4행이 통째로 막힌다. 단결정 압전재는 컴플라이언스로 인쇄되는 것이 관행이다.

## C8. 병렬 파동이 같은 DB·같은 파일을 동시에 고치고 있었다(§504)
작업 중 **57차 SB/SD** 가 `coverage_report.py` 에 여섯째 갈래 `V6`(`core_rejected_printed_value`)를
넣고(커밋 `0bdcb06`) camera·acoustics·rf·sensor·battery 계통에 판정을 박았다.
**내 기준선(V5 1,078)과 종료값(931)의 차는 내 것이 아니다.** 보고에는 `(태깅 없음)` 줄만 쓴다.
커밋은 §504 대로 `-- backend/scripts/catalog/out_sc` 로 경로를 못박았다.

## C9. 결함 신고(고치지 않았다)
- **출처 중복** — `src4593`(`Uddeholm Dievar … Ed.15(10.2025)`, url=`https://www.uddeholm.com/`,
  publisher 비었음)이 `src4571` 과 **같은 `local_path`·같은 제목·같은 판**이다. §575 의 지문에 걸릴
  모양인데 남아 있다.
- **선언·데이터 불일치 1건**(`verdicts_check`) — 재료229 Doosan DS-7402 의
  `core_absent_from_vendor_sheet` 가 `thermal.specific_heat` 를 선언했는데 값이 있다. 내 것이 아니다.
- **물성값 0인 재료 3종** — 2290·2649·2650. 2026-08 생성분으로 내 것이 아니다.
